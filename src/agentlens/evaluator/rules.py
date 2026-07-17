from __future__ import annotations

from typing import Any

from agentlens.models import ToolCall
from collections import Counter

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