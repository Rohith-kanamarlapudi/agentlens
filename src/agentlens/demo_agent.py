from agentlens import trace


@trace(name="planner")
def planner(query: str):
    return query.upper()


@trace(name="responder")
def responder(plan: str):
    return f"Response: {plan}"


def run_demo(query: str):
    plan = planner(query)
    return responder(plan)


if __name__ == "__main__":
    print(run_demo("hello agentlens"))