from __future__ import annotations

from typing import Any

from agentlens.models import ToolCall
from collections import Counter
from datetime import datetime

from agentlens.models import Run

from agentlens.models import Span   

def check_schema(
    call: ToolCall,
    signature: dict[str, type],
) -> list[str]:
    """
    Validate a ToolCall against an expected schema.

    Example:
        signature = {
            "query": str,
            "top_k": int,
        }
    """

    errors: list[str] = []

    # Check for missing or incorrect types
    for field, expected_type in signature.items():

        if field not in call.inputs:
            errors.append(f"Missing required argument: '{field}'")
            continue

        value = call.inputs[field]

        if not isinstance(value, expected_type):
            errors.append(
                f"Argument '{field}' expected "
                f"{expected_type.__name__}, "
                f"got {type(value).__name__}"
            )

    # Check for unexpected arguments
    for field in call.inputs:

        if field not in signature:
            errors.append(
                f"Unexpected argument: '{field}'"
            )

    return errors

def check_loops(
    spans: list[Span],
    threshold: int = 3,
) -> list[str]:
    """
    Detect repeated tool calls.

    If the same tool is invoked 'threshold' or more times,
    return a warning.
    """

    tool_names = [
        tool.name
        for span in spans
        for tool in span.tool_calls
    ]

    counts = Counter(tool_names)

    warnings = []

    for tool_name, count in counts.items():

        if count >= threshold:

            warnings.append(
                f"Tool '{tool_name}' was called {count} times."
            )

    return warnings



def _run_duration(run: Run) -> float:
    """
    Return the total execution time of a run in seconds.
    """

    if run.started_at is None or run.ended_at is None:
        return 0.0

    return (run.ended_at - run.started_at).total_seconds()


def _estimate_cost(
    run: Run,
    input_cost_per_1m: float = 0.14,
    output_cost_per_1m: float = 0.28,
) -> float:
    """
    Estimate DeepSeek API cost.

    Since token usage isn't tracked yet, this estimates using
    character count as a placeholder. Replace this with real
    token accounting later.
    """

    prompt_chars = 0
    completion_chars = 0

    for span in run.spans:

        prompt_chars += len(str(span.inputs))
        completion_chars += len(str(span.output))

        for tool in span.tool_calls:
            prompt_chars += len(str(tool.inputs))
            completion_chars += len(str(tool.output))

    # Rough approximation:
    # 1 token ≈ 4 characters
    prompt_tokens = prompt_chars / 4
    completion_tokens = completion_chars / 4

    cost = (
        (prompt_tokens / 1_000_000) * input_cost_per_1m
        + (completion_tokens / 1_000_000) * output_cost_per_1m
    )

    return round(cost, 6)


def check_budget(
    run: Run,
    max_seconds: float = 30.0,
    max_cost: float = 0.50,
) -> list[str]:
    """
    Check runtime and estimated API cost.
    """

    issues = []

    duration = _run_duration(run)

    if duration > max_seconds:
        issues.append(
            f"Run exceeded time budget ({duration:.2f}s > {max_seconds}s)"
        )

    cost = _estimate_cost(run)

    if cost > max_cost:
        issues.append(
            f"Estimated cost ${cost:.6f} exceeds budget ${max_cost:.2f}"
        )

    return issues