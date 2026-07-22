from __future__ import annotations

import contextvars
import functools
import inspect
from datetime import datetime
from .store import TraceStore
from typing import Any, Callable

from .models import Run, Span

STORE = TraceStore()
# Context variable used to track nested spans
CURRENT_SPAN = contextvars.ContextVar(
    "current_span",
    default=None,
)

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
    """
    Recursively redact secrets from dictionaries, lists and tuples.
    """

    if isinstance(value, dict):
        return {
            key: (
                "***REDACTED***"
                if key.lower() in SECRET_KEYS
                else _redact(val)
            )
            for key, val in value.items()
        }

    if isinstance(value, list):
        return [_redact(v) for v in value]

    if isinstance(value, tuple):
        return tuple(_redact(v) for v in value)

    return value


def _emit(run: Run) -> None:
    """
    Persist one run into SQLite.
    """
    STORE.save_trace(run)


def trace(
    fn: Callable | None = None,
    *,
    name: str | None = None,
):
    """
    Trace synchronous and asynchronous functions.

    Usage
    -----

    @trace
    def foo():
        ...

    @trace(name="planner")
    def planner():
        ...
    """

    def decorator(func: Callable):

        # ==========================================================
        # Async wrapper
        # ==========================================================
        if inspect.iscoroutinefunction(func):

            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):

                run = Run(
                    agent_name=name or func.__name__,
                )

                parent_span = CURRENT_SPAN.get()

                span = Span(
                    name=name or func.__name__,
                    parent_id=parent_span,
                )

                span.inputs = _redact(
                    {
                        "args": args,
                        "kwargs": kwargs,
                    }
                )

                run.spans.append(span)

                token = CURRENT_SPAN.set(span.span_id)

                try:
                    result = await func(*args, **kwargs)

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

                    CURRENT_SPAN.reset(token)

                    _emit(run)

            return async_wrapper

        # ==========================================================
        # Sync wrapper
        # ==========================================================
        @functools.wraps(func)
        def wrapper(*args, **kwargs):

            run = Run(
                agent_name=name or func.__name__,
            )

            parent_span = CURRENT_SPAN.get()

            span = Span(
                name=name or func.__name__,
                parent_id=parent_span,
            )

            span.inputs = _redact(
                {
                    "args": args,
                    "kwargs": kwargs,
                }
            )

            run.spans.append(span)

            token = CURRENT_SPAN.set(span.span_id)

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

                CURRENT_SPAN.reset(token)

                _emit(run)

        return wrapper

    return decorator(fn) if fn else decorator