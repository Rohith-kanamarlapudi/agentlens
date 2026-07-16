from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class ToolCall(BaseModel):
    """
    Represents a single tool invocation made by an agent.
    """

    tool_id: str = Field(default_factory=lambda: str(uuid4()))

    name: str

    inputs: dict[str, Any] = Field(default_factory=dict)

    output: Any | None = None

    started_at: datetime = Field(default_factory=datetime.utcnow)

    ended_at: datetime | None = None

    error: str | None = None


class Span(BaseModel):
    """
    Represents one traced execution span.
    """

    span_id: str = Field(default_factory=lambda: str(uuid4()))

    parent_id: str | None = None

    name: str

    started_at: datetime = Field(default_factory=datetime.utcnow)

    ended_at: datetime | None = None

    tool_calls: list[ToolCall] = Field(default_factory=list)


class Run(BaseModel):
    """
    Top-level execution of an AI agent.
    """

    run_id: str = Field(default_factory=lambda: str(uuid4()))

    agent_name: str

    started_at: datetime = Field(default_factory=datetime.utcnow)

    ended_at: datetime | None = None

    spans: list[Span] = Field(default_factory=list)

    status: str = "running"


class EvalResult(BaseModel):
    """
    Stores evaluation output for a completed run.
    """

    run_id: str

    passed: bool

    score: float | None = None

    reasons: list[str] = Field(default_factory=list)

    metadata: dict[str, Any] = Field(default_factory=dict)