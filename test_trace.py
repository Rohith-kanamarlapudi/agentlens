from agentlens import trace


@trace
def hello(name):
    return f"Hello {name}"


hello("Rohith")