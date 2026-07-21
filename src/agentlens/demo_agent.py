from agentlens import trace

from agentlens.logging_config import get_logger
logger = get_logger(__name__)

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
    logger.info("%s", run_demo("hello agentlens"))