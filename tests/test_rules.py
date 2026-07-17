from datetime import timedelta

from agentlens.evaluator import run_rules
from agentlens.models import Run


def test_run_rules_returns_result():

    run = Run(agent_name="planner")

    run.ended_at = run.started_at + timedelta(seconds=45)

    result = run_rules(run)

    assert result.run_id == run.run_id
    assert result.passed is False
    assert len(result.reasons) > 0