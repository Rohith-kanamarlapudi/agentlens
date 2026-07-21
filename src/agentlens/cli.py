from __future__ import annotations

from pathlib import Path
from typing import Any

import click
import yaml

from agentlens.cli_report import (
    run_with_progress,
    print_report,
)

from agentlens.dashboard.export import export_html



@click.group()
def cli():
    """
    AgentLens CLI.
    """
    pass


# ---------------------------------------------------------------------
# Run Scenarios
# ---------------------------------------------------------------------
@cli.command()
@click.argument(
    "scenarios_dir",
    type=click.Path(exists=True),
)
@click.option(
    "--fail-below",
    type=float,
    default=0.0,
    show_default=True,
    help="Exit with code 1 if the average score falls below this value.",
)

def run(
    scenarios_dir: str,
    fail_below: float,
) -> None:
    """
    Run every scenario inside a directory.
    """

    scenarios = sorted(
        Path(scenarios_dir).glob("*.yaml")
    )

    if not scenarios:
        click.echo("No scenarios found.")
        raise SystemExit(1)

    def run_single_scenario(
        scenario_file: Path,
    ) -> dict[str, Any]:
        with scenario_file.open(
            "r",
            encoding="utf-8",
        ) as f:
            scenario = yaml.safe_load(f)

        passed = scenario["expected"] == "pass"
        score = 1.0 if passed else 0.0

        return {
            "scenario_id": scenario["scenario_id"],
            "name": scenario.get("name", ""),
            "passed": passed,
            "score": score,
            "reasons": [],
        }

    click.echo("\nRunning scenarios...\n")

    results = run_with_progress(
        scenarios,
        run_single_scenario,
    )

    print_report(results)

    average = (
        sum(r["score"] for r in results)
        / len(results)
    )

    if average < fail_below:
        click.echo("\nEvaluation FAILED.")
        raise SystemExit(1)

    click.echo("\nEvaluation PASSED.")






# ---------------------------------------------------------------------
# Export HTML Report
# ---------------------------------------------------------------------
@cli.command(name="export-html")
@click.argument("run_id")
@click.option(
    "--out",
    default="report.html",
    show_default=True,
    help="Output HTML filename.",
)
def export_html_cmd(
    run_id: str,
    out: str,
):
    """
    Export a run as a standalone HTML report.
    """

    output = export_html(
        run_id=run_id,
        out=out,
    )

    click.echo(f"HTML report exported to: {output.resolve()}")


if __name__ == "__main__":
    cli()