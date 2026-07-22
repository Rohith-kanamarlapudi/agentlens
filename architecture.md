# AgentLens Architecture

This document describes how AgentLens is put together: the trace lifecycle from a decorated function call through to a CI pass/fail decision, the responsibility of each module, the data model, and the reasoning behind the key design decisions. For a higher-level feature overview, see [`README.md`](README.md).

---

## 1. Design goals

AgentLens is built around four constraints that shaped every decision below:

1. **Framework-agnostic.** `@trace` wraps a plain Python function. It has no dependency on LangGraph, CrewAI, or any other orchestration framework — which is what made it possible to dogfood against a real LangGraph pipeline (`playwright-ai-automation`) without modifying AgentLens itself.
2. **Zero-friction instrumentation.** Adding observability to an existing agent should be one decorator, not a rewrite. `@trace` and `@trace(name="...")` both work, on sync and async functions alike.
3. **Deterministic where possible, LLM-assisted where necessary.** Cheap, fast, deterministic checks (schema validation, loop detection, budget limits) run first and catch the majority of real failures. The LLM-as-a-Judge is reserved for judgment calls that genuinely need it — quality, safety, groundedness — and its results are cached and run at `temperature=0` so they're reproducible.
4. **CI is the real interface.** The dashboard and reports are conveniences. The thing that actually protects agent quality over time is a non-zero exit code on a regressing pull request.

---

## 2. High-level data flow

```
 1. Agent function runs
        │  wrapped in @trace
        ▼
 2. sdk.py captures the call
        │  inputs, output, timing, errors, redacted secrets
        ▼
 3. Trace written to traces.jsonl (append-only)
        │
        ▼
 4. store.py persists it into SQLite
        │  runs / spans / tool_calls tables
        ▼
 5. evaluator/rules.py runs deterministic checks
        │  schema, loops, budget
        ▼
 6. evaluator/judge/ scores it with DeepSeek (if a rubric applies)
        │  cached by trace hash, retried on transient failure
        ▼
 7. evaluator/regression.py compares the scored run to a golden baseline
        │
        ▼
 8. cli.py aggregates results across a scenario suite
        │  prints a report, computes an average score
        ▼
 9. Exit code 0 (pass) or 1 (fail) ──► CI blocks or allows the PR
```

Every arrow above is a real module boundary — each stage can be used independently. You can call `sdk.trace` without ever touching the evaluator; you can run the rule engine against a trace pulled from the store without invoking the judge; you can call the judge directly without going through the CLI.

---

## 3. Module responsibilities

### `agentlens/models.py` — the shared contract

Four Pydantic v2 models define the shape every other module reads and writes:

```python
class ToolCall(BaseModel):
    name: str
    inputs: dict[str, Any]
    output: Optional[Any] = None
    started_at: datetime
    ended_at: Optional[datetime] = None
    error: Optional[str] = None

class Span(BaseModel):
    span_id: str
    parent_id: Optional[str] = None
    tool_calls: list[ToolCall] = []

class Run(BaseModel):
    run_id: str
    agent_name: str
    spans: list[Span] = []
    status: str = "running"

class EvalResult(BaseModel):
    run_id: str
    passed: bool
    score: Optional[float] = None
    reasons: list[str] = []
```

Keeping these as the single source of truth means the SDK, the store, and the evaluator never pass around ad-hoc dicts — every function signature in the codebase is typed against one of these four models.

### `agentlens/sdk.py` — instrumentation

The `@trace` decorator is the only thing a developer needs to add to their own code. Internally it:

- Records `name`, redacted `inputs`, `started_at`/`ended_at`, and `output` or `error` around the wrapped call.
- Uses a `contextvars.ContextVar` to track the currently-executing span, so a tool call made *inside* another traced function is automatically recorded as a **child span** rather than a sibling — this is what makes multi-agent pipelines (planner → tool → responder) show up as a real tree instead of a flat list.
- Detects `inspect.iscoroutinefunction` and dispatches to an async-safe wrapper, so streaming/async agent frameworks don't silently lose span capture.
- Redacts known secret keys (`api_key`, `token`, `authorization`, `password`, and their case-insensitive variants) via `_redact()` before anything is serialized — this runs *before* the trace ever touches disk or an LLM prompt, not as a downstream cleanup step.
- Emits each call as one JSON line to `traces.jsonl`, tagged with a fresh `trace_id`.

### `agentlens/store.py` — persistence

`TraceStore` migrates the append-only JSONL log into a queryable SQLite database with three tables that mirror the Pydantic models one-to-one:

| Table | Columns | Purpose |
|---|---|---|
| `runs` | `run_id`, `agent_name`, `status`, `created_at` | One row per top-level agent invocation |
| `spans` | `span_id`, `run_id`, `parent_id` | The tree structure — `parent_id` is null for root spans |
| `tool_calls` | `id`, `span_id`, `name`, `inputs`, `output`, `error`, `started_at`, `ended_at` | The actual captured call data |

`save_trace()` and `get_trace()` are designed as an exact round trip — a `Run` object saved and then retrieved should be indistinguishable from the original. `list_runs()` supports filtering by agent name, status, and date range, which is what the (planned) dashboard and any future `/runs` API would build on.

### `agentlens/evaluator/rules.py` — deterministic checks

Three checks run without any LLM call, in this order of cost:

1. **`check_schema()`** — validates each `ToolCall.inputs` against a declared signature; catches missing or wrong-typed arguments.
2. **`check_loops()`** — counts repeated tool-call names per run; **3 or more identical calls flags a loop.** This is the single highest-signal rule in the engine — it's what caught a real selector-retry loop during the `playwright-ai-automation` dogfood run.
3. **`check_budget()`** — flags runs that exceed a duration or estimated-cost threshold, so a runaway agent can't silently blow a CI time or spend budget.

All three roll up into one `RuleCheckResult(run_id, passed, reasons)`, which is the same shape the LLM judge's result eventually gets compared against.

### `agentlens/judge/` — DeepSeek LLM-as-a-Judge

For evaluation dimensions that genuinely require judgment — task completion, groundedness, safety — a rubric-driven judge call is made to DeepSeek:

- **Rubric format** is a plain YAML file (`rubrics/`) listing named dimensions with a human-readable description each. Non-engineers can edit this without touching code.
- **Structured output** is enforced via JSON-mode prompting, so the response is always `{"dimension": {"score": float, "justification": str}, ...}` — never free text that needs fragile parsing.
- **`temperature=0`** by design — the judge's job is repeatable measurement, not creative variation.
- **Caching by trace hash** (`hashlib.sha256` over the serialized `Run`) means an identical run is never re-scored, which matters both for cost and for keeping regression comparisons stable.
- **Retry with exponential backoff** (via Tenacity) wraps the judge call, so a transient DeepSeek API hiccup doesn't fail an entire CI run.

### `agentlens/evaluator/regression.py` — baseline comparison

A **golden baseline** is a frozen, known-good result per scenario (`baselines/`). `compare_to_baseline()` diffs a new result against it along three axes:

- **Score drop** — the rubric score fell below a configurable threshold.
- **New tool-call pattern** — the sequence of tools called changed, which is often the earliest signal of a regression, before the score itself moves.
- **Cost spike** — the run got meaningfully more expensive without a corresponding quality improvement.

Any one of these three flags the run as a regression.

### `agentlens/cli.py` — the CI-facing surface

`agentlens run <scenarios_dir> --fail-below <threshold>` is the command everything else exists to support:

1. Loads every `*.yaml` scenario in the target directory.
2. Runs each one, collecting an `EvalResult`.
3. Prints a per-scenario pass/fail report.
4. Computes the average score across the suite.
5. Exits non-zero if the average is below `--fail-below`.

That exit code is the entire integration surface with GitHub Actions (or any CI system) — no custom plugin or webhook is required, just a shell command in a workflow file.

---

## 4. Why these tradeoffs

**Why SQLite instead of Postgres/a hosted DB?** AgentLens is meant to be dropped into a project with zero external infrastructure. SQLite gives real SQL querying (`list_runs` filters) with no setup step, which matters for a tool whose adoption cost needs to be close to zero.

**Why JSONL as an intermediate format before SQLite?** Writing a JSON line per call is the cheapest possible operation on the hot path of a traced function — no schema, no locking, no transaction. The SQLite migration happens out-of-band, so instrumentation overhead stays negligible even in a tight agent loop.

**Why cache the judge by trace hash rather than by scenario ID?** Hashing the full trace (not just the scenario name) means the cache is correct even when the same scenario produces a different trace on a different code version — which is exactly the situation regression testing needs to distinguish.

**Why rule-based checks *before* the LLM judge, not after?** Loop detection and budget checks are both cheaper and more reliable than an LLM call for the failure modes they target. Running them first means a broken agent gets flagged without ever spending judge-call budget on a run that was never going to pass.

---

## 5. Extension points

- **New rule checks** — add a function to `evaluator/rules.py` and fold its result into `run_rules()`. No changes needed elsewhere.
- **New rubric dimensions** — add a `name`/`description` pair to any YAML file under `rubrics/`; no code change required.
- **A different judge backend** — `judge/` is the intended seam for the "multi-model evaluation" roadmap item; the judge interface (`judge_cached(prompt, answer) -> dict`) is deliberately narrow so a second implementation can sit alongside `DeepSeekJudge` without touching the rest of the pipeline.
- **A new orchestration framework to dogfood against** — since `@trace` has no framework dependency, instrumenting a new agent codebase is limited to importing the decorator and wrapping the relevant functions, as was done for the LangGraph-based `playwright-ai-automation` pipeline.