# AgentLens

Framework-agnostic evaluation and observability framework for AI agents.

AgentLens helps developers trace, evaluate, benchmark, and monitor AI agents with minimal code changes.

---

# Features

- 🔍 Agent execution tracing
- 🌳 Nested span tracking
- 🛠 Tool call capture
- 🔒 Automatic secret redaction
- 📄 JSONL trace logging
- 🗄 SQLite trace storage
- 📊 Rule-based evaluation
- 🤖 DeepSeek LLM-as-a-Judge
- 📑 YAML-based evaluation rubrics
- 📈 Regression detection
- 💾 Golden baseline comparison
- ⚡ Cached judge results
- 🔄 Automatic retry with exponential backoff
- 🖥 CLI runner
- 🧪 Scenario-based testing
- 🚀 Ready for CI/CD integration

---

# Tech Stack

- Python 3.10+
- Pydantic v2
- SQLite
- Click
- PyYAML
- OpenAI SDK (DeepSeek Compatible)
- DeepSeek API
- Tenacity
- Pytest

---

# Project Structure

```
agentlens/
│
├── baselines/
├── rubrics/
├── scenarios/
├── scripts/
├── tests/
│
├── src/
│   └── agentlens/
│       ├── evaluator/
│       ├── judge/
│       ├── models.py
│       ├── sdk.py
│       ├── store.py
│       ├── cli.py
│       └── utils.py
│
├── architecture.md
├── pyproject.toml
└── README.md
```

---

# Architecture

```
Agent
   │
   ▼
@trace SDK
   │
   ▼
Trace Store
(JSONL / SQLite)
   │
   ▼
Rule Engine
   │
   ▼
DeepSeek Judge
   │
   ▼
Regression Engine
   │
   ▼
CLI / Dashboard / CI
```

For additional details see:

```
architecture.md
```

---

# Installation

Clone the repository

```bash
git clone <your-repository-url>

cd agentlens
```

Create a virtual environment

```bash
python -m venv .venv
```

Activate it

### Windows

```powershell
.venv\Scripts\activate
```

### Linux / macOS

```bash
source .venv/bin/activate
```

Install the project

```bash
pip install -e .
```

---

# Environment Variables

Create a `.env`

```env
DEEPSEEK_API_KEY=your_api_key_here
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_BASE_URL=https://api.deepseek.com
```

---

# Running the CLI

Run all evaluation scenarios

```bash
agentlens run scenarios
```

Fail the run if the average score is below a threshold

```bash
agentlens run scenarios --fail-below 0.80
```

If you haven't registered the CLI entry point yet, use:

```bash
python -m agentlens.cli run scenarios
```

---

# Running Tests

Run all tests

```bash
pytest
```

Run quietly

```bash
pytest -q
```

---

# Example

```python
from agentlens import trace


@trace
def add(a, b):
    return a + b


print(add(2, 3))
```

A trace will automatically be generated and stored.

---

# DeepSeek Judge Example

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

# Current Capabilities

✅ Execution tracing

✅ Nested spans

✅ Tool call tracking

✅ Secret redaction

✅ SQLite trace storage

✅ Rule engine

✅ YAML rubrics

✅ DeepSeek evaluation

✅ Judge result caching

✅ Automatic retry with exponential backoff

✅ Regression detection

✅ Golden baselines

✅ CLI runner

✅ Scenario testing

---

# Roadmap

- Interactive Dashboard
- HTML evaluation reports
- GitHub Actions integration
- Performance analytics
- Multi-model evaluation
- LangGraph support
- CrewAI support
- Auto-generated benchmarks

---

# Contributing

1. Fork the repository

2. Create a feature branch

```bash
git checkout -b feature/my-feature
```

3. Commit your changes

```bash
git commit -m "feat: add new feature"
```

4. Push

```bash
git push origin feature/my-feature
```

5. Open a Pull Request

---

# License

MIT License

---

# Acknowledgements

- DeepSeek
- OpenAI Python SDK
- Pydantic
- Click
- SQLite
- PyYAML
- Tenacity