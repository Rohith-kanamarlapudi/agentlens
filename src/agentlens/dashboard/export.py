from __future__ import annotations

import shutil
from pathlib import Path

from agentlens.dashboard.templates import render_report
from agentlens.store import TraceStore


def export_html(
    run_id: str,
    out: str | Path = "report.html",
) -> Path:
    """
    Export a run as a standalone HTML report.
    """

    store = TraceStore()

    run = store.get_trace(run_id)

    if run is None:
        raise ValueError(
            f"Run '{run_id}' not found."
        )

    html = render_report(
        run=run,
        eval_result={},
        trend_labels=[],
        trend_scores=[],
    )

    out = Path(out)

    out.write_text(
        html,
        encoding="utf-8",
    )

    # Copy dashboard.css beside the HTML report
    css_source = (
        Path(__file__).parent
        / "static"
        / "dashboard.css"
    )

    css_destination = (
        out.parent
        / "dashboard.css"
    )

    if css_source.exists():
        shutil.copy2(
            css_source,
            css_destination,
        )

    return out