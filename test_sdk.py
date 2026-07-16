from agentlens import trace


@trace
def add(a, b):
    return a + b


add(10, 20)