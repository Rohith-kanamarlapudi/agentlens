from __future__ import annotations

from typing import Any

from agentlens.models import ToolCall


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