from agentlens.models import Run
from agentlens.store import TraceStore

store = TraceStore()

run = Run(agent_name="demo")

store.save_trace(run)

loaded = store.get_trace(run.run_id)

print(loaded)

store.close()