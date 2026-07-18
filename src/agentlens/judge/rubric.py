from __future__ import annotations

from pathlib import Path

import yaml


def load_rubric(path: str | Path = "rubrics/default.yaml") -> dict:
    """
    Load an evaluation rubric from YAML.
    """

    path = Path(path)

    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)