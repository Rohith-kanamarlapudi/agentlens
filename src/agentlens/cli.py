from __future__ import annotations

from pathlib import Path
from typing import Any

import click
import yaml

from agentlens.dashboard.export import export_html


def print_report(results: list[dict[str, Any]]) -> None:
    """
    Print a clean evaluation report.
    """

    click.echo("\n" + "=" * 70)
    click.echo("AgentLens Evaluation Report")
    click.echo("=" * 70)

    passed = 0

    for result in results:

        mark = "PASS" if result["passed"] else "FAIL"

        if result["passed"]:
            passed += 1

        click.echo(
            f"[{mark:<4}] "
            f"{result['scenario_id']:<20} "
            f"Score: {result['score']:.2f}"
        )

        reasons = result.get("reasons", [])

        if reasons:
            for reason in reasons:
                click.echo(f"        • {reason}")

    total = len(results)

    average_score = (
        sum(r["score"] for r in results) / total
        if total
        else 0.0
    )

    click.echo("-" * 70)
    click.echo(f"Passed        : {passed}/{total}")
    click.echo(f"Failed        : {total - passed}/{total}")
    click.echo(f"Average Score : {average_score:.2f}")
    click.echo("=" * 70)


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
):
    """
    Run every scenario inside a directory.
    """

    scenarios = sorted(
        Path(scenarios_dir).glob("*.yaml")
    )

    if not scenarios:
        click.echo("No scenarios found.")
        raise SystemExit(1)

    results: list[dict[str, Any]] = []

    click.echo("\nRunning scenarios...\n")

    for scenario_file in scenarios:

        with scenario_file.open(
            "r",
            encoding="utf-8",
        ) as f:
            scenario = yaml.safe_load(f)

        # Temporary scoring until evaluator is connected
        passed = scenario["expected"] == "pass"
        score = 1.0 if passed else 0.0

        results.append(
            {
                "scenario_id": scenario["scenario_id"],
                "name": scenario.get("name", ""),
                "passed": passed,
                "score": score,
                "reasons": [],
            }
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