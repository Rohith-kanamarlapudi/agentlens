from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from agentlens.dashboard.templates import render_timeline
from agentlens.store import TraceStore

app = FastAPI(
    title="AgentLens Dashboard",
    description="Visualize AgentLens traces and evaluation results.",
    version="0.2.0",
)

store = TraceStore()


@app.get("/")
def home():
    """
    Dashboard home page.
    """
    return {
        "message": "AgentLens Dashboard",
        "docs": "/docs",
    }


@app.get(
    "/runs/{run_id}",
    response_class=HTMLResponse,
)
def run_report(run_id: str):
    """
    Display a trace report for a specific run.
    """

    run = store.get_trace(run_id)

    if run is None:
        raise HTTPException(
            status_code=404,
            detail=f"Run '{run_id}' not found.",
        )

    # ------------------------------------------------------------------
    # Evaluation results are not stored in SQLite yet.
    # Later replace this with something like:
    #
    # evaluation = store.get_evaluation(run_id)
    #
    # once evaluator persistence is implemented.
    # ------------------------------------------------------------------
    evaluation = None

    return render_timeline(
        run=run,
        evaluation=evaluation,
    )