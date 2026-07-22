<div align="center">

# 🔍 AgentLens

### *Instrument any agent with one decorator. Get traces, evaluations, and regression gates for free.*

No black-box agent runs. No manual log-diving. No "did this PR make the agent worse?" guesswork.

Wrap any Python function with **`@trace`** and AgentLens captures every call, timing, and tool invocation — then scores it with a **rule engine + DeepSeek LLM-as-a-Judge**, compares it against a **golden baseline**, and gates your CI on the result.

**Framework-agnostic by design** — dogfooded against a real 6-agent LangGraph pipeline ([`playwright-ai-automation`](https://github.com/Rohith-kanamarlapudi/playwright-ai-automation)), not just its own test suite.

<br/>

[![AgentLens CI](https://img.shields.io/github/actions/workflow/status/Rohith-kanamarlapudi/agentlens/agentlens.yml?style=for-the-badge&label=AgentLens%20CI&logo=github&logoColor=white&labelColor=333)](https://github.com/Rohith-kanamarlapudi/agentlens/actions/workflows/agentlens.yml)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white&style=for-the-badge)](https://www.python.org/)
[![Pydantic](https://img.shields.io/badge/Pydantic-V2-E92063?logo=pydantic&logoColor=white&style=for-the-badge)](https://docs.pydantic.dev/)
[![DeepSeek](https://img.shields.io/badge/DeepSeek-LLM--as--Judge-4D6BFE?style=for-the-badge)](https://www.deepseek.com/)
[![SQLite](https://img.shields.io/badge/SQLite-Trace%20Store-07405E?logo=sqlite&logoColor=white&style=for-the-badge)](https://www.sqlite.org/)

</div>

---

### 📌 Jump to

[What Is This](#-what-is-this) · [How It Works](#-how-it-works) · [Key Features](#-key-features) · [Architecture](#️-architecture) · [Project Structure](#️-project-structure) · [Tech Stack](#️-tech-stack) · [Getting Started](#-getting-started) · [Usage Examples](#-usage-examples) · [CI Integration](#-ci-integration) · [Dogfooding Results](#-dogfooding-results) · [Roadmap](#️-roadmap) · [FAQ](#-faq) · [Contributing](#-contributing) · [About](#-about)

---

## 🧭 What Is This?

**AgentLens** is a framework-agnostic evaluation and observability toolkit for LLM agents. It solves a problem every multi-agent system runs into: once you have more than one agent handing work off to another, it becomes hard to know *what actually happened* inside a run, whether a change made things better or worse, and whether it's safe to merge.

AgentLens answers that with three layers working together:

1. **Tracing** — a single `@trace` decorator captures every function call, its inputs/outputs, timing, and nested tool calls, with known secret keys redacted automatically before anything touches disk.
2. **Evaluation** — a deterministic rule engine (schema checks, loop detection, budget limits) and a DeepSeek-powered LLM-as-a-Judge score every run against a YAML rubric, with judge results cached by trace hash so identical runs never get re-scored.
3. **Regression gating** — every scored run is compared against a golden baseline. A CLI (`agentlens run`) turns this into a CI-ready exit code, so a pull request that quietly makes an agent worse gets blocked automatically.

> **The bottom line:** decorate your agent functions, run `agentlens run scenarios/`, and get traces, scores, and a pass/fail gate — without writing a single custom logging or eval harness.

---

## 🔬 How It Works

| Step | What happens |
|---|---|
| **1. Instrument** | Add `@trace` (or `@trace(name="...")`) above any agent function — sync or async, no other code changes |
| **2. Run your agent** | Every call is captured: inputs, output, timing, nested tool calls, errors — secrets redacted automatically |
| **3. Persist** | Traces stream to `traces.jsonl`, then migrate into a queryable SQLite store (`runs`, `spans`, `tool_calls`) |
| **4. Evaluate** | Deterministic rules run first (cheap, fast); a DeepSeek judge scores against a YAML rubric where judgment is genuinely needed |
| **5. Compare** | The scored run is diffed against a frozen golden baseline — score drops, new tool-call patterns, and cost spikes are all flagged |
| **6. Gate** | `agentlens run scenarios/ --fail-below 0.8` returns a CI-ready exit code — a regressing PR is blocked the same way a failing unit test would be |

---

## ✨ Key Features

| | Feature | What it does |
|---|---|---|
| 🔍 | **Agent Execution Tracing** | `@trace` decorator wraps any function — sync or async — with zero boilerplate |
| 🌳 | **Nested Span Tracking** | Multi-step agent calls (planner → tool → responder) show up as a proper parent/child tree |
| 🛠 | **Tool Call Capture** | Every tool invocation inside a traced run is recorded with its own inputs, outputs, and timing |
| 🔒 | **Automatic Secret Redaction** | Known secret keys (`api_key`, `token`, `authorization`, `password`) are stripped before serialization |
| 📄 | **JSONL Trace Logging** | Every call is appended as a structured JSON line — simple, append-only, human-readable |
| 🗄 | **SQLite Trace Store** | Traces persist losslessly to SQLite (`runs`, `spans`, `tool_calls`), queryable by agent, status, or date |
| 📊 | **Rule-Based Evaluation** | Schema validation, loop detection (3+ repeated calls), and timeout/cost budget checks — no LLM required |
| 🤖 | **DeepSeek LLM-as-a-Judge** | Rubric-driven scoring via the DeepSeek API, with `temperature=0` and structured JSON output for reproducibility |
| 📑 | **YAML Evaluation Rubrics** | Define scoring dimensions (task completion, groundedness, safety) in a human-editable YAML file |
| ⚡ | **Cached Judge Results** | Every judge call is cached by trace hash — an identical run is never scored twice |
| 🔄 | **Automatic Retry w/ Backoff** | Judge calls retry with exponential backoff, so a transient API blip never fails a CI run |
| 📈 | **Regression Detection** | New runs are diffed against a golden baseline — score drops, new tool-call patterns, and cost spikes are all flagged |
| 💾 | **Golden Baseline Comparison** | Freeze a known-good result per scenario; every future run is measured against it |
| 🖥 | **CLI Runner** | `agentlens run scenarios/ --fail-below 0.8` — one command, CI-ready exit code |
| 🧪 | **Scenario-Based Testing** | Fixed YAML prompts with expected outcomes turn agent evaluation into a real test suite |
| 🚀 | **CI/CD Ready** | GitHub Actions workflow included — a regressing PR is blocked automatically |

---

## 🏗️ Architecture

```
┌───────────────────────────────────────────────────────────────────┐
│                         Your Agent Code                           │
│         (LangGraph, CrewAI, plain functions — anything)           │
└──────────────────────────┬────────────────────────────────────────┘
                            │ @trace(name="...")
                            ▼
┌───────────────────────────────────────────────────────────────────┐
│                      agentlens.sdk                                │
│   trace() decorator ─► captures inputs/outputs/timing/errors      │
│   contextvars ─► tracks parent span for nested tool calls         │
│   _redact() ─► strips known secret keys before serialization      │
└──────────────────────────┬────────────────────────────────────────┘
                            │ structured JSON per call
                            ▼
┌───────────────────────────────────────────────────────────────────┐
│                      agentlens.store                              │
│   TraceStore ─► save_trace() / get_trace() / list_runs()          │
│   SQLite schema: runs · spans · tool_calls                        │
└──────────────────────────┬────────────────────────────────────────┘
                            │ Run (Pydantic model)
                            ▼
┌───────────────────────────────────────────────────────────────────┐
│                    agentlens.evaluator                            │
│                                                                   │
│   rules.py                          judge/                        │
│   • check_schema()                  • DeepSeek LLM-as-a-Judge     │
│   • check_loops()                   • rubric-driven YAML scoring  │
│   • check_budget()                  • cached by trace hash        │
│   • RuleCheckResult                 • retry w/ exponential backoff│
│                                                                   │
│   regression.py                                                   │
│   • compare_to_baseline() ─► score drop / new pattern / cost spike│
└──────────────────────────┬────────────────────────────────────────┘
                            │ EvalResult
                            ▼
┌───────────────────────────────────────────────────────────────────┐
│                      agentlens.cli                                │
│   agentlens run <scenarios_dir> --fail-below <threshold>          │
│   ─► terminal report ─► non-zero exit on regression               │
└──────────────────────────┬────────────────────────────────────────┘
                            ▼
                  GitHub Actions / any CI system
                  (PR blocked automatically on regression)
```

A deeper breakdown of every module, the trace lifecycle, and design decisions lives in [`architecture.md`](architecture.md).

---

## 🗂️ Project Structure

```
agentlens/
│
├── src/
│   └── agentlens/
│       ├── models.py           # Run, Span, ToolCall, EvalResult (Pydantic v2)
│       ├── sdk.py               # @trace decorator, redaction, JSONL emission
│       ├── store.py             # TraceStore — SQLite persistence + query API
│       ├── cli.py               # agentlens run <scenarios_dir> --fail-below
│       ├── utils.py             # shared helpers
│       ├── evaluator/
│       │   ├── rules.py         # schema validation, loop detection, budget checks
│       │   └── regression.py    # baseline comparison, regression flags
│       └── judge/
│           └── ...              # DeepSeek LLM-as-a-Judge, caching, retry
│
├── baselines/                   # golden baseline results per scenario
├── rubrics/                     # YAML evaluation rubrics (task_completion, groundedness, safety)
├── scenarios/                   # fixed YAML prompts + expected outcomes
├── scripts/                     # one-off tooling (e.g. trace migration)
├── tests/                       # full test suite
│
├── .github/workflows/           # CI — lint, type-check, scenario suite
├── architecture.md              # detailed architecture and design notes
├── CHANGELOG.md
├── pyproject.toml
└── README.md
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Language** | Python 3.10+ |
| **Data modeling** | Pydantic v2 — `Run`, `Span`, `ToolCall`, `EvalResult` |
| **Trace persistence** | SQLite — `runs`, `spans`, `tool_calls` tables |
| **LLM-as-a-Judge** | DeepSeek API (`deepseek-chat`) via the OpenAI-compatible SDK |
| **Rubric format** | YAML — human-editable scoring dimensions |
| **CLI** | Click |
| **Retry / resilience** | Tenacity — exponential backoff on judge calls |
| **Testing** | Pytest |
| **CI** | GitHub Actions |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- A [DeepSeek API key](https://platform.deepseek.com) — used for LLM-as-a-Judge scoring

### 1. Clone & Install

```bash
git clone https://github.com/Rohith-kanamarlapudi/agentlens.git
cd agentlens

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -e .
```

### 2. Configure

```bash
cp .env.example .env
```

| Variable | Purpose | Default |
|---|---|---|
| `DEEPSEEK_API_KEY` | Auth for LLM-as-a-Judge calls | *(required)* |
| `DEEPSEEK_MODEL` | Judge model | `deepseek-chat` |
| `DEEPSEEK_BASE_URL` | API base URL | `https://api.deepseek.com` |

### 3. Run

```bash
# Run every scenario in scenarios/
agentlens run scenarios

# Fail the run (and CI) if the average score drops below a threshold
agentlens run scenarios --fail-below 0.80

# CLI entry point not registered yet? Fall back to the module form:
python -m agentlens.cli run scenarios

# Run the test suite
pytest -q
```

---

## 💡 Usage Examples

### Trace any function

```python
from agentlens import trace

@trace
def add(a, b):
    return a + b

print(add(2, 3))
# A structured trace is captured automatically — no extra code required.
```

### Trace a multi-step agent

```python
from agentlens import trace

@trace(name="planner")
def plan(query):
    ...

@trace(name="tool_call")
def call_tool(action):
    ...  # captured as a nested child span of whichever traced function calls it
```

### Score a response with the DeepSeek judge

```python
from agentlens.judge import DeepSeekJudge

judge = DeepSeekJudge()

result = judge.judge_cached(
    prompt="What is Python?",
    answer="Python is a programming language.",
)

print(result)
```

---

## ⚙️ CI Integration

Drop this into `.github/workflows/agentlens.yml` to gate every pull request on agent quality:

```yaml
name: agentlens
on: [pull_request]
jobs:
  eval:
    runs-on: ubuntu-latest
    env:
      DEEPSEEK_API_KEY: ${{ secrets.DEEPSEEK_API_KEY }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - run: pip install -e .
      - run: agentlens run scenarios/ --fail-below 0.8
```

A pull request that regresses agent quality below the threshold fails this check automatically — no manual review step required to catch it.

---

## 🐕 Dogfooding Results

AgentLens was integrated into a real multi-agent system — [`playwright-ai-automation`](https://github.com/Rohith-kanamarlapudi/playwright-ai-automation), a 6-agent LangGraph pipeline that generates and self-heals Playwright test suites — to validate that the tracing and evaluation model holds up outside its own test suite.

| | Before | After |
|---|---|---|
| **Visibility** | No centralized view into individual agent execution | Full tracing across Strategy, Architecture, Code Gen, Review, Edge Cases, and Heal agents |
| **Evaluation** | Manual inspection of generated outputs | 6 representative evaluation scenarios covering real Playwright test generation workflows |
| **Result** | — | **6/6 scenarios passing**, average evaluation score **1.00** |
| **CLI robustness** | Scenario execution required every YAML to explicitly define a `scenario_id` | CLI made more robust — `scenario_id` is now inferred, reducing friction for new scenario authors |

---

## 🗺️ Roadmap

**Shipped ✅**

- [x] `@trace` decorator with nested span tracking and secret redaction
- [x] JSONL trace logging + SQLite trace store with a queryable API
- [x] Rule-based evaluator — schema validation, loop detection, budget checks
- [x] DeepSeek LLM-as-a-Judge with YAML rubrics, caching, and retry/backoff
- [x] Regression detection against golden baselines
- [x] CLI runner with CI-ready exit codes
- [x] GitHub Actions CI integration
- [x] Dogfooded end-to-end against a real 6-agent LangGraph pipeline

**Coming next 🔜**

- [ ] Interactive dashboard — run timeline, rubric badges, score-trend chart
- [ ] Static HTML evaluation reports (`agentlens export-html`)
- [ ] Performance analytics — per-agent latency and cost breakdowns
- [ ] Multi-model evaluation — pluggable judge backends beyond DeepSeek
- [ ] Native LangGraph and CrewAI integration helpers
- [ ] Auto-generated benchmark scenarios from recorded traces

---

## ❓ FAQ

**Does AgentLens require LangGraph or any specific agent framework?**
No. `@trace` wraps plain Python functions — it has no dependency on any orchestration framework, which is exactly what made dogfooding it against a LangGraph pipeline possible without modifying AgentLens itself.

**What happens if the DeepSeek API is unavailable?**
Judge calls retry with exponential backoff. Deterministic rule-based checks (schema, loops, budget) don't depend on the API at all, so a full evaluation run degrades gracefully rather than failing outright.

**Can I use a different LLM as the judge?**
Not yet natively — this is the top item under "Coming next." The judge interface is intentionally narrow so a second backend can be added without touching the rest of the pipeline.

**Is trace data safe to commit or share?**
Known secret keys are redacted automatically before a trace is written or sent anywhere. That said, treat `traces.jsonl` and the SQLite store like any other log output — review before sharing broadly.

---

## 🤝 Contributing

```bash
# 1. Fork the repository

# 2. Create a feature branch
git checkout -b feature/my-feature

# 3. Commit your changes
git commit -m "feat: add new feature"

# 4. Push
git push origin feature/my-feature

# 5. Open a Pull Request
```

---

## 🙏 Acknowledgements

Built on top of [DeepSeek](https://www.deepseek.com/), the [OpenAI Python SDK](https://github.com/openai/openai-python), [Pydantic](https://docs.pydantic.dev/), [Click](https://click.palletsprojects.com/), SQLite, PyYAML, and [Tenacity](https://tenacity.readthedocs.io/).

---

## 👤 About

<div align="center">

<br/>

### Built and maintained by

# Rohith Kanamarlapudi

*AI Agents Developer — building multi-agent systems, evaluation tooling, and the infrastructure that keeps them honest.*

[![GitHub](https://img.shields.io/badge/GitHub-Rohith--kanamarlapudi-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Rohith-kanamarlapudi)
[![playwright-ai-automation](https://img.shields.io/badge/Also%20check%20out-playwright--ai--automation-2EAD33?style=for-the-badge&logo=playwright&logoColor=white)](https://github.com/Rohith-kanamarlapudi/playwright-ai-automation)

<br/>

*If AgentLens helped you evaluate or debug an agent, a ⭐ on the repo goes a long way.*

</div>