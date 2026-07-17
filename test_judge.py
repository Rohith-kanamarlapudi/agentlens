from agentlens.judge import DeepSeekJudge

judge = DeepSeekJudge()

result = judge.judge(
    prompt="What is the capital of France?",
    answer="Paris",
)

print(result)