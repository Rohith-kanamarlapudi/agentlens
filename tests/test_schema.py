from agentlens.evaluator import check_schema
from agentlens.models import ToolCall

call = ToolCall(
    name="search",
    inputs={
        "query": "AI Agents",
        "top_k": "5",  # Should be int
        "extra": True,
    },
)

errors = check_schema(
    call,
    {
        "query": str,
        "top_k": int,
    },
)

print(errors)