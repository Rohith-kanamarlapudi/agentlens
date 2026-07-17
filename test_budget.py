from datetime import timedelta

from agentlens.evaluator import check_budget
from agentlens.models import Run

run = Run(agent_name="planner")

run.ended_at = run.started_at + timedelta(seconds=45)

issues = check_budget(
    run,
    max_seconds=30,
)

print(issues)