from agentlens.evaluator.regression import (
    compare_to_baseline,
    flag_regression,
)

baseline = {
    "expected": {
        "score": 0.92,
        "passed": True,
    },
    "tool_call_pattern": [
        "search",
        "summarize",
    ],
}

current = {
    "score": 0.75,
    "passed": False,
    "tool_call_pattern": [
        "search",
        "search",
    ],
}

comparison = compare_to_baseline(
    current,
    baseline,
)

flags = flag_regression(
    comparison,
    cost_delta=0.35,
)

print(comparison)
print()
print(flags)