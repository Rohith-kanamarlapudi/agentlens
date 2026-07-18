from __future__ import annotations

from pathlib import Path

import click
import yaml


@click.group()
def cli():
    """
    AgentLens CLI.
    """
    pass


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
    help="Exit with code 1 if the average expected score falls below this value.",
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

    total_score = 0.0

    click.echo("\nRunning scenarios...\n")

    for scenario_file in scenarios:

        with open(
            scenario_file,
            "r",
            encoding="utf-8",
        ) as f:
            scenario = yaml.safe_load(f)

        score = 1.0 if scenario["expected"] == "pass" else 0.0

        total_score += score

        click.echo(
            f"✓ {scenario['scenario_id']}"
            f" ({scenario['name']})"
        )

    average = total_score / len(scenarios)

    click.echo()
    click.echo(f"Average Score : {average:.2f}")

    if average < fail_below:
        click.echo("Evaluation FAILED.")
        raise SystemExit(1)

    click.echo("Evaluation PASSED.")


if __name__ == "__main__":
    cli()