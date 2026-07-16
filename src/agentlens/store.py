from __future__ import annotations

import sqlite3
from pathlib import Path

DB_FILE = Path("agentlens.db")

SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS runs (
    run_id TEXT PRIMARY KEY,
    agent_name TEXT NOT NULL,
    status TEXT NOT NULL,
    started_at TEXT,
    ended_at TEXT
);

CREATE TABLE IF NOT EXISTS spans (
    span_id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    parent_id TEXT,
    name TEXT NOT NULL,
    started_at TEXT,
    ended_at TEXT,
    inputs TEXT,
    output TEXT,
    error TEXT,
    FOREIGN KEY(run_id) REFERENCES runs(run_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tool_calls (
    tool_id TEXT PRIMARY KEY,
    span_id TEXT NOT NULL,
    name TEXT NOT NULL,
    inputs TEXT,
    output TEXT,
    started_at TEXT,
    ended_at TEXT,
    error TEXT,
    FOREIGN KEY(span_id) REFERENCES spans(span_id) ON DELETE CASCADE
);
"""


def get_connection() -> sqlite3.Connection:
    """Return a SQLite connection."""

    return sqlite3.connect(DB_FILE)


def initialize_database() -> None:
    """Create all database tables if they don't exist."""

    with get_connection() as conn:
        conn.executescript(SCHEMA)
        conn.commit()