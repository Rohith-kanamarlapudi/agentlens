from agentlens.evaluator.baseline import load_baseline
from agentlens.evaluator.regression import compare_to_baseline

baseline = load_baseline("scenario_01")

new_result = {
    "score": 0.81,
    "passed": True,
    "tool_call_pattern": [
        "search",
        "summarize",
    ],
}

comparison = compare_to_baseline(
    new_result,
    baseline,
)

print(comparison)