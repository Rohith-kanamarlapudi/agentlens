from __future__ import annotations

from datetime import datetime
from typing import Any


def build_report(
    run_id: str,
    rule_result: dict[str, Any],
    judge_result: dict[str, Any],
    regression: dict[str, Any],
) -> dict[str, Any]:
    """
    Build a unified evaluation report.
    """

    passed = (
        rule_result.get("passed", False)
        and judge_result.get("passed", False)
        and not regression.get("regression", False)
    )

    return {
        "run_id": run_id,
        "timestamp": datetime.utcnow().isoformat(),
        "passed": passed,
        "rule_result": rule_result,
        "judge_result": judge_result,
        "regression": regression,
    }