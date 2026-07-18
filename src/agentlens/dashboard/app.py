from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from agentlens.dashboard.templates import (
    render_diff,
    render_timeline,
)
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

    # Evaluation persistence is not implemented yet.
    # Later this can become:
    #
    # evaluation = store.get_evaluation(run_id)
    #
    evaluation = None

    return render_timeline(
        run=run,
        evaluation=evaluation,
    )


@app.get(
    "/compare/{run_id}/{baseline_id}",
    response_class=HTMLResponse,
)
def compare_runs(
    run_id: str,
    baseline_id: str,
):
    """
    Compare two stored runs.
    """

    current = store.get_trace(run_id)
    baseline = store.get_trace(baseline_id)

    if current is None:
        raise HTTPException(
            status_code=404,
            detail=f"Run '{run_id}' not found.",
        )

    if baseline is None:
        raise HTTPException(
            status_code=404,
            detail=f"Baseline '{baseline_id}' not found.",
        )

    return render_diff(
        current=current,
        baseline=baseline,
    )


@app.get("/health")
def health():
    """
    Health check endpoint.
    """
    return {
        "status": "ok",
        "service": "AgentLens Dashboard",
        "version": app.version,
    }