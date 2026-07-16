from agentlens import trace


@trace
def add(a: int, b: int) -> int:
    return a + b


@trace(name="division")
def divide(a: int, b: int):
    return a / b


print(add(2, 3))

try:
    divide(10, 0)
except ZeroDivisionError:
    print("Exception captured successfully.")