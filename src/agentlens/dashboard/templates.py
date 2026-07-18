from __future__ import annotations

from agentlens.models import Run


def render_timeline(run: Run) -> str:
    """
    Render a simple HTML timeline for a Run.
    """

    html = f"""
    <html>
    <head>
        <title>AgentLens Run</title>
    </head>

    <body>

    <h1>{run.agent_name}</h1>

    <p>Status: <b>{run.status}</b></p>

    <hr>

    """

    for span in run.spans:

        html += f"""
        <h3>{span.name}</h3>

        <ul>

            <li><b>Span ID:</b> {span.span_id}</li>

            <li><b>Parent:</b> {span.parent_id}</li>

            <li><b>Started:</b> {span.started_at}</li>

            <li><b>Ended:</b> {span.ended_at}</li>

            <li><b>Error:</b> {span.error}</li>

        </ul>

        <hr>
        """

    html += """
    </body>
    </html>
    """

    return html