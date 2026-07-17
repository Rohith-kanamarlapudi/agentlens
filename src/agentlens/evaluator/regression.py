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
    
    


def flag_regression(
    comparison: dict,
    cost_delta: float = 0.0,
    score_threshold: float = 0.10,
    cost_threshold: float = 0.20,
) -> list[str]:
    """
    Generate regression warnings from a baseline comparison.

    Parameters
    ----------
    comparison
        Output from compare_to_baseline().

    cost_delta
        Fractional increase in cost relative to the baseline.

        Example:
            baseline = $0.50
            current  = $0.60

            cost_delta = (0.60 - 0.50) / 0.50 = 0.20
    """

    flags: list[str] = []

    if comparison["score_drop"] > score_threshold:
        flags.append(
            f"Score regressed "
            f"({comparison['score_drop']:.3f})"
        )

    if comparison["tool_pattern_changed"]:
        flags.append(
            "Tool-call pattern changed"
        )

    if (
        comparison["passed_before"]
        and not comparison["passed_now"]
    ):
        flags.append(
            "Scenario no longer passes"
        )

    if cost_delta > cost_threshold:
        flags.append(
            f"Cost increased by "
            f"{cost_delta:.1%}"
        )

    return flags