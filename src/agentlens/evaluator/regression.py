from __future__ import annotations

from typing import Any


def compare_to_baseline(
    new_result: dict[str, Any],
    baseline: dict[str, Any],
) -> dict[str, Any]:
    """
    Compare a new evaluation result against a stored baseline.
    """

    baseline_score = baseline["expected"]["score"]
    current_score = new_result["score"]

    score_drop = baseline_score - current_score

    baseline_pattern = baseline.get(
        "tool_call_pattern",
        [],
    )

    current_pattern = new_result.get(
        "tool_call_pattern",
        [],
    )

    pattern_changed = (
        baseline_pattern != current_pattern
    )

    baseline_passed = baseline["expected"]["passed"]
    current_passed = new_result.get(
        "passed",
        False,
    )

    return {
        "baseline_score": baseline_score,
        "current_score": current_score,
        "score_drop": round(score_drop, 4),
        "passed_before": baseline_passed,
        "passed_now": current_passed,
        "tool_pattern_changed": pattern_changed,
        "regression": (
            score_drop > 0
            or pattern_changed
            or (
                baseline_passed
                and not current_passed
            )
        ),
    }