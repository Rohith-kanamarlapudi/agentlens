from agentlens.evaluator import evaluate_run
from agentlens.models import Run

run = Run(
    agent_name="demo_agent",
)

result = evaluate_run(
    run=run,
    prompt="What is Python?",
    answer="Python is a programming language.",
)

print(result)