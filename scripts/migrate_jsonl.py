from __future__ import annotations

import json
from pathlib import Path

from agentlens.models import Run
from agentlens.store import TraceStore

TRACE_FILE = Path("traces.jsonl")


def migrate_jsonl(trace_file: Path = TRACE_FILE) -> None:
    """
    Import every JSONL trace into SQLite.
    """

    if not trace_file.exists():
        print(f"{trace_file} not found.")
        return

    store = TraceStore()

    migrated = 0

    with trace_file.open("r", encoding="utf-8") as f:
        for line in f:

            line = line.strip()

            if not line:
                continue

            data = json.loads(line)

            run = Run.model_validate(data)

            store.save_trace(run)

            migrated += 1

    store.close()

    print(f"Migrated {migrated} trace(s).")


if __name__ == "__main__":
    migrate_jsonl()