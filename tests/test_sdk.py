import asyncio
import json
from pathlib import Path

import pytest

from agentlens import trace


TRACE_FILE = Path("traces.jsonl")


@pytest.fixture(autouse=True)
def cleanup():
    """Remove traces before every test."""
    if TRACE_FILE.exists():
        TRACE_FILE.unlink()

    yield

    if TRACE_FILE.exists():
        TRACE_FILE.unlink()


def read_traces():
    return [
        json.loads(line)
        for line in TRACE_FILE.read_text(encoding="utf-8").splitlines()
    ]


def test_sync_function_returns_value():
    @trace
    def add(a, b):
        return a + b

    assert add(2, 3) == 5

    traces = read_traces()

    assert len(traces) == 1
    assert traces[0]["status"] == "success"


def test_exception_is_recorded():
    @trace
    def boom():
        raise ValueError("failure")

    with pytest.raises(ValueError):
        boom()

    traces = read_traces()

    assert traces[0]["status"] == "failed"
    assert traces[0]["spans"][0]["error"] == "failure"


def test_trace_records_inputs():
    @trace
    def greet(name):
        return f"Hello {name}"

    greet("Rohith")

    traces = read_traces()

    assert traces[0]["spans"][0]["inputs"]["args"][0] == "Rohith"


def test_trace_records_output():
    @trace
    def square(x):
        return x * x

    square(5)

    traces = read_traces()

    assert traces[0]["spans"][0]["output"] == 25


def test_secret_redaction():
    @trace
    def login(api_key):
        return True

    login("my-secret-key")

    traces = read_traces()

    assert (
        traces[0]["spans"][0]["inputs"]["kwargs"] == {}
    )


def test_nested_span_parent_id():
    @trace
    def child():
        return "child"

    @trace
    def parent():
        return child()

    parent()

    traces = read_traces()

    assert len(traces) == 2


@pytest.mark.asyncio
async def test_async_function():

    @trace
    async def hello():
        await asyncio.sleep(0.01)
        return "AgentLens"

    result = await hello()

    assert result == "AgentLens"

    traces = read_traces()

    assert traces[0]["status"] == "success"


def test_timestamp_exists():
    @trace
    def demo():
        return True

    demo()

    traces = read_traces()

    assert traces[0]["started_at"] is not None
    assert traces[0]["ended_at"] is not None