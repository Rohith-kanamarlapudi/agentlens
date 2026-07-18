from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from agentlens.dashboard.templates import render_timeline
from agentlens.store import TraceStore

app = FastAPI(
    title="AgentLens Dashboard",
)

store = TraceStore()


@app.get("/")
def home():
    return {
        "message": "AgentLens Dashboard",
    }


@app.get(
    "/runs/{run_id}",
    response_class=HTMLResponse,
)
def run_report(run_id: str):

    run = store.get_trace(run_id)

    if run is None:
        raise HTTPException(
            status_code=404,
            detail="Run not found",
        )

    return render_timeline(run)