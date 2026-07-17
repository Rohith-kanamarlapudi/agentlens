from __future__ import annotations

import json
from pathlib import Path


def load_baseline(
    scenario_id: str,
    directory: str | Path = "baselines",
) -> dict:
    """
    Load a baseline JSON for a scenario.
    """

    path = Path(directory) / f"{scenario_id}.json"

    if not path.exists():
        raise FileNotFoundError(
            f"Baseline '{scenario_id}' not found."
        )

    with path.open(
        "r",
        encoding="utf-8",
    ) as f