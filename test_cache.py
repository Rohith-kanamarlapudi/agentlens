from agentlens.judge import DeepSeekJudge

judge = DeepSeekJudge()

print("First call...")
result1 = judge.judge_cached(
    prompt="What is 2 + 2?",
    answer="4",
)

print(result1)

print()

print("Second call...")
result2 = judge.judge_cached(
    prompt="What is 2 + 2?",
    answer="4",
)

print(result2)

print()

print(result1 == result2)