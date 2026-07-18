from agentlens.evaluator import check_loops
from agentlens.models import Span, ToolCall

span = Span(
    name="planner",
    tool_calls=[
        ToolCall(name="search", inputs={}),
        ToolCall(name="search", inputs={}),
        ToolCall(name="search", inputs={}),
        ToolCall(name="calculator", inputs={}),
    ],
)

warnings = check_loops([span])

print(warnings)