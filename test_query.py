from agentlens.models import Run
from agentlens.store import TraceStore

store = TraceStore()

store.save_trace(Run(agent_name="planner"))
store.save_trace(Run(agent_name="planner"))
store.save_trace(Run(agent_name="executor"))

print("Run Count:", store.get_run_count())

print()

print("Agents:")
print(store.list_agent_names())

print()

print("Statuses:")
print(store.list_statuses())

print()

print("Planner Runs:")
for row in store.list_runs(agent_name="planner"):
    print(dict(row))

store.close()