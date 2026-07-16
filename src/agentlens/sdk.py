from __future__ import annotations

import functools
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from .models import Run, Span


TRACE_FILE = Path("traces.jsonl")

# Keys that should never be written to disk
SECRET_KEYS = {
    "api_key",
    "apikey",
    "password",
    "secret",
    "token",
    "access_token",
    "authorization",
    "bearer",
}


def _redact(value: Any) -> Any:
    """Recursively redact secrets from dictionaries/lists."""

    if isinstance(value, dict):
        return {
            k: (
                "***REDACTED***"
                if k.lower() in SECRET_KEYS
                else _redact(v)
            )
            for k, v in value.items()
        }

    if isinstance(value, list):
        return [_redact(v) for v in value]

    if isinstance(value, tuple):
        return tuple(_redact(v) for v in value)

    return value


def _emit(run: Run) -> None:
    """Append one JSON trace per line."""

    TRACE_FILE.parent.mkdir(parents=True, exist_ok=True)

    with TRACE_FILE.open("a", encoding="utf-8") as f:
        f.write(run.model_dump_json())
        f.write("\n")


def trace(
    fn: Callable | None = None,
    *,
    name: str | None = None,
):
    """
    Usage:

    @trace
    def foo():
        ...

    @trace(name="planner")
    def bar():
        ...
    """

    def decorator(func: Callable):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):

            run = Run(
                agent_name=name or func.__name__,
            )

            span = Span(
                name=name or func.__name__,
            )

            span.inputs = _redact(
                {
                    "args": args,
                    "kwargs": kwargs,
                }
            )

            run.spans.append(span)

            try:
                result = func(*args, **kwargs)

                span.output = _redact(result)

                run.status = "success"

                return result

            except Exception as exc:

                span.error = str(exc)

                run.status = "failed"

                raise

            finally:

                now = datetime.utcnow()

                span.ended_at = now
                run.ended_at = now

                _emit(run)

        return wrapper

    return decorator(fn) if fn else decorator