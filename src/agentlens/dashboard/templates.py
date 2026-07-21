from __future__ import annotations

from html import escape

from agentlens.models import Run


PASS_THRESHOLD = 0.7

_env = Environment(
    loader=FileSystemLoader(
        Path(__file__).parent / "templates"
    ),
    autoescape=True,
)
def render_report(
    run,
    eval_result,
    trend_labels,
    trend_scores,
) -> str:
    """
    Render the dashboard using the Jinja2 template.
    """

    return _env.get_template(
        "report.html.j2"
    ).render(
        run=run,
        eval_result=eval_result,
        trend_labels=trend_labels,
        trend_scores=trend_scores,
    )
def render_badges(dimensions: dict) -> str:
    """
    Render pass/fail badges for each rubric dimension.
    """

    if not dimensions:
        return "<p><i>No evaluation available.</i></p>"

    badges = []

    for name, result in dimensions.items():

        score = float(result.get("score", 0))

        passed = score >= PASS_THRESHOLD

        color = "#28a745" if passed else "#dc3545"

        badges.append(
            f"""
            <span
                style="
                    display:inline-block;
                    margin:4px;
                    padding:6px 12px;
                    border-radius:20px;
                    color:white;
                    background:{color};
                    font-size:14px;
                    font-weight:bold;
                ">
                {escape(name)}
                ({score:.2f})
            </span>
            """
        )

    return "".join(badges)


def render_timeline(
    run: Run,
    evaluation: dict | None = None,
) -> str:
    """
    Render a simple HTML report.
    """

    html = f"""
    <!DOCTYPE html>

    <html>

    <head>

        <title>AgentLens Dashboard</title>

    </head>

    <body style="font-family:Arial;padding:30px">

        <h1>{escape(run.agent_name)}</h1>

        <p>

            <b>Run ID</b><br>

            {run.run_id}

        </p>

        <p>

            <b>Status:</b>

            {run.status}

        </p>

        <hr>

    """

    if evaluation:

        html += "<h2>Evaluation</h2>"

        html += render_badges(
            evaluation.get("dimensions", {})
        )

        html += "<hr>"

    html += "<h2>Timeline</h2>"

    for span in run.spans:

        html += f"""
        <div
            style="
                border:1px solid #ddd;
                padding:15px;
                margin-bottom:15px;
                border-radius:8px;
            ">

            <h3>{escape(span.name)}</h3>

            <p><b>Span ID:</b> {span.span_id}</p>

            <p><b>Parent:</b> {span.parent_id}</p>

            <p><b>Started:</b> {span.started_at}</p>

            <p><b>Ended:</b> {span.ended_at}</p>

            <p><b>Error:</b> {escape(str(span.error))}</p>

        </div>
        """

    html += """
    </body>
    </html>
    """

    return html

from html import escape
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from agentlens.models import Run


def render_diff(current: Run, baseline: Run) -> str:
    """
    Render a simple comparison page between two runs.
    """

    current_spans = len(current.spans)
    baseline_spans = len(baseline.spans)

    current_tools = sum(
        len(span.tool_calls)
        for span in current.spans
    )

    baseline_tools = sum(
        len(span.tool_calls)
        for span in baseline.spans
    )

    return f"""
    <!DOCTYPE html>

    <html>

    <head>

        <title>Run Comparison</title>

        <style>

            body {{
                font-family: Arial;
                margin: 40px;
            }}

            table {{
                border-collapse: collapse;
                width: 100%;
            }}

            th, td {{
                border: 1px solid #ddd;
                padding: 10px;
                text-align: left;
            }}

            th {{
                background: #f4f4f4;
            }}

        </style>

    </head>

    <body>

        <h1>Run Comparison</h1>

        <table>

            <tr>
                <th>Metric</th>
                <th>Current</th>
                <th>Baseline</th>
            </tr>

            <tr>
                <td>Agent</td>
                <td>{escape(current.agent_name)}</td>
                <td>{escape(baseline.agent_name)}</td>
            </tr>

            <tr>
                <td>Status</td>
                <td>{current.status}</td>
                <td>{baseline.status}</td>
            </tr>

            <tr>
                <td>Spans</td>
                <td>{current_spans}</td>
                <td>{baseline_spans}</td>
            </tr>

            <tr>
                <td>Tool Calls</td>
                <td>{current_tools}</td>
                <td>{baseline_tools}</td>
            </tr>

        </table>

    </body>

    </html>
    """