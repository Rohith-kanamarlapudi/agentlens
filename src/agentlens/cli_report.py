from __future__ import annotations

from typing import Any, Callable

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

console = Console()


def run_with_progress(
    files: list[Any],
    run_fn: Callable[[Any], dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Run scenarios while displaying a progress spinner.
    """

    results: list[dict[str, Any]] = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:

        task = progress.add_task(
            "Running scenarios...",
            total=len(files),
        )

        for scenario in files:
            results.append(run_fn(scenario))
            progress.update(task, advance=1)

    return results


def print_report(
    results: list[dict[str, Any]],
) -> None:
    """
    Display a colored evaluation table.
    """

    table = Table(title="AgentLens Evaluation Results")

    table.add_column("Scenario")
    table.add_column("Status")
    table.add_column("Score", justify="right")

    for result in results:

        color = "green" if result["passed"] else "red"

        table.add_row(
            result["scenario_id"],
            f"[{color}]{'PASS' if result['passed'] else 'FAIL'}[/{color}]",
            f"{result['score']:.2f}",
        )

    console.print(table)