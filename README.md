# AgentLens

Framework-agnostic evaluation and observability framework for AI agents.

AgentLens helps developers trace, evaluate, benchmark, and monitor AI agents with minimal code changes.

## Features

- Agent execution tracing
- Nested span visualization
- Tool call tracking
- SQLite trace storage
- Rule-based evaluation
- DeepSeek LLM-as-a-Judge
- Regression detection
- FastAPI dashboard
- CLI runner
- GitHub Actions CI quality gates

## Tech Stack

- Python 3.10+
- Pydantic v2
- SQLite
- FastAPI
- Click
- DeepSeek API
- Pytest

## Project Architecture

See [architecture.md](architecture.md).

## Installation

```bash
pip install -e .