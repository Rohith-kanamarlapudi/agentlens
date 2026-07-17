from agentlens.evaluator.report import build_report

report = build_report(
    run_id="run_001",
    rule_result={
        "passed": True,
        "reasons": [],
    },
    judge_result={
        "passed": True,
        "score": 0.91,
    },
    regression={
        "regression": False,
        "score_drop": 0.01,
    },
)

print(report)