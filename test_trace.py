from agentlens import trace


@trace
def greet(name):
    return f"Hello {name}"


greet("Rohith")