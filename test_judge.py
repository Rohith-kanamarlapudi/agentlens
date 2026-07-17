from agentlens.judge import DeepSeekJudge

judge = DeepSeekJudge()

result = judge.judge(
    prompt="What is 2 + 2?",
    answer="4",
)

print(result)