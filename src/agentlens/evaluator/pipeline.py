from __future__ import annotations

from agentlens.evaluator.rules import run_rules
from agentlens.judge import DeepSeekJudge


def evaluate_run(
    run,
    prompt: str,
    answer: str,
):
    """
    Execute the complete evaluation pipeline.
    """

    rule_result = run_rules(run)

    judge = DeepSeekJudge()

    judge_result = judge.judge_cached(
        prompt=prompt,
        answer=answer,
    )

    return {
        "rules": rule_result,
        "judge": judge_result,
    }