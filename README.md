<div align="center">

# 🔍 AgentLens

### *Instrument any agent with one decorator. Get traces, evaluations, and regression gates for free.*

No black-box agent runs. No manual log-diving. No "did this PR make the agent worse?" guesswork.

Wrap any Python function with **`@trace`** and AgentLens captures every call, timing, and tool invocation — then scores it with a **rule engine + DeepSeek LLM-as-a-Judge**, compares it against a **golden baseline**, and gates your CI on the result.

**Framework-agnostic by design** — dogfooded against a real 6-agent LangGraph pipeline ([`playwright-ai-automation`](https://github.com/Rohith-kanamarlapudi/playwright-ai-automation)), not just its own test suite.

<br/>

[![AgentLens CI](https://github.com/Rohith-kanamarlapudi/agentlens/actions/workflows/agentlens.yml/badge.svg)](https://github.com/Rohith-kanamarlapudi/agentlens/actions/workflows/agentlens.yml)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white&style=for-the-badge)](https://www.python.org/)
[![Pydantic](https://img.shields.io/badge/Pydantic-v2-E92063?logo=pydantic&logoColor=white&style=for-the-badge)](https://docs.pydantic.dev/)
[![DeepSeek](https://img.shields.io/badge/DeepSeek-LLM--as--Judge-4D6BFE?style=for-the-badge)](https://www.deepseek.com/)
[![SQLite](https://img.shields.io/badge/SQLite-Trace%20Store-003B57?logo=sqlite&logoColor=white&style=for-the-badge)](https://www.sqlite.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

</div>

---

### 📌 Jump to

[What Is This](#-what-is-this) · [Pipeline](#-pipeline-at-a-glance) · [Key Features](#-key-features) · [Architecture](#️-architecture) · [Project Structure](#️-project-structure) · [Tech Stack](#️-tech-stack) · [Getting Started](#-getting-started) · [Usage Examples](#-usage-examples) · [Dogfooding Results](#-dogfooding-results) · [Roadmap](#️-roadmap) · [Contributing](#-contributing)

---

## 🧭 What Is This?

**AgentLens** is a framework-agnostic evaluation and observability toolkit for LLM agents. It solves a problem every multi-agent system runs into: once you have more than one agent handing work off to another, it becomes hard to know *what actually happened* inside a run, whether a change made things better or worse, and whether it's safe to merge.

AgentLens answers that with three layers working together:

1. **Tracing** — a single `@trace` decorator captures every function call, its inputs/outputs, timing, and nested tool calls, with known secret keys redacted automatically before anything touches disk.
2. **Evaluation** — a deterministic rule engine (schema checks, loop detection, budget limits) and a DeepSeek-powered LLM-as-a-Judge score every run against a YAML rubric, with judge results cached by trace hash so identical runs never get re-scored.
3. **Regression gating** — every scored run is compared against a golden baseline. A CLI (`agentlens run`) turns this into a CI-ready exit code, so a pull request that quietly makes an agent worse gets blocked automatically.

> **The bottom line:** decorate your agent functions, run `agentlens run scenarios/`, and get traces, scores, and a pass/fail gate — without writing a single custom logging or eval harness.

---

## ⚡ Pipeline at a Glance

```
   Your agent function
          │
          ▼
   ┌─────────────┐
   │  @trace SDK │   captures inputs, outputs, timing, nested tool calls
   │             │   redacts known secret keys before anything is written
   └──────┬──────┘
          ▼
   ┌─────────────────────┐
   │     Trace Store     │   JSONL (raw) ──► SQLite (queryable: runs · spans · tool_calls)
   └──────┬──────────────┘
          ▼
   ┌────────────────────────────────────────────────────────────┐
   │                      Evaluator                             │
   │                                                            │
   │   Rule Engine                     DeepSeek LLM-as-a-Judge  │
   │   • schema validation             • YAML rubric scoring    │
   │   • loop detection (3+ calls)     • cached by trace hash   │
   │   • timeout / cost budget         • retry w/ backoff       │
   └──────┬─────────────────────────────────────────────────────┘
          ▼
   ┌──────────────────────┐
   │ Regression Detector  │   new run vs. golden baseline
   └──────┬───────────────┘
          ▼
   CLI (`agentlens run`) ──► exit code ──► CI gate blocks the PR
```

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
| 🚀 | **CI/CD Ready** | GitHub Actions workflow included — a regressing PR is blocked automatically, the same way a failing unit test would be |

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

```env
DEEPSEEK_API_KEY=your_api_key_here
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_BASE_URL=https://api.deepseek.com
```

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

## 📄 License

MIT License — see [`LICENSE`](LICENSE) for details.

---

## 🙏 Acknowledgements

Built on top of [DeepSeek](https://www.deepseek.com/), the [OpenAI Python SDK](https://github.com/openai/openai-python), [Pydantic](https://docs.pydantic.dev/), [Click](https://click.palletsprojects.com/), SQLite, PyYAML, and [Tenacity](https://tenacity.readthedocs.io/).

<br/>

<div align="center">

**Rohith Kanamarlapudi** — [@Rohith-kanamarlapudi](https://github.com/Rohith-kanamarlapudi)

</div>