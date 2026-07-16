from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from .models import Run, Span, ToolCall

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


class TraceStore:
    def __init__(self, db_path: str | Path = DB_FILE):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)

    def save_trace(self, run: Run) -> None:
        """Persist a Run and all nested objects."""

        self.conn.execute(
            """
            INSERT OR REPLACE INTO runs
            (run_id, agent_name, status, started_at, ended_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                run.run_id,
                run.agent_name,
                run.status,
                run.started_at.isoformat() if run.started_at else None,
                run.ended_at.isoformat() if run.ended_at else None,
            ),
        )

        for span in run.spans:

            self.conn.execute(
                """
                INSERT OR REPLACE INTO spans
                (
                    span_id,
                    run_id,
                    parent_id,
                    name,
                    started_at,
                    ended_at,
                    inputs,
                    output,
                    error
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    span.span_id,
                    run.run_id,
                    span.parent_id,
                    span.name,
                    span.started_at.isoformat() if span.started_at else None,
                    span.ended_at.isoformat() if span.ended_at else None,
                    json.dumps(span.inputs),
                    json.dumps(span.output),
                    span.error,
                ),
            )

            for tc in span.tool_calls:

                self.conn.execute(
                    """
                    INSERT OR REPLACE INTO tool_calls
                    (
                        tool_id,
                        span_id,
                        name,
                        inputs,
                        output,
                        started_at,
                        ended_at,
                        error
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        tc.tool_id,
                        span.span_id,
                        tc.name,
                        json.dumps(tc.inputs),
                        json.dumps(tc.output),
                        tc.started_at.isoformat() if tc.started_at else None,
                        tc.ended_at.isoformat() if tc.ended_at else None,
                        tc.error,
                    ),
                )

        self.conn.commit()

    def get_trace(self, run_id: str) -> Run | None:
        """Load a Run from SQLite."""

        row = self.conn.execute(
            "SELECT * FROM runs WHERE run_id=?",
            (run_id,),
        ).fetchone()

        if row is None:
            return None

        run = Run(
            run_id=row["run_id"],
            agent_name=row["agent_name"],
            status=row["status"],
            started_at=row["started_at"] if row["started_at"] else None,
            ended_at=row["ended_at"] if row["ended_at"] else None,
            spans=[],
        )

        span_rows = self.conn.execute(
            "SELECT * FROM spans WHERE run_id=?",
            (run_id,),
        ).fetchall()

        for s in span_rows:

            span = Span(
                span_id=s["span_id"],
                parent_id=s["parent_id"],
                name=s["name"],
                started_at=s["started_at"],
                ended_at=s["ended_at"],
                inputs=json.loads(s["inputs"] or "{}"),
                output=json.loads(s["output"] or "null"),
                error=s["error"],
                tool_calls=[],
            )

            tool_rows = self.conn.execute(
                "SELECT * FROM tool_calls WHERE span_id=?",
                (span.span_id,),
            ).fetchall()

            for t in tool_rows:

                span.tool_calls.append(
                    ToolCall(
                        tool_id=t["tool_id"],
                        name=t["name"],
                        inputs=json.loads(t["inputs"] or "{}"),
                        output=json.loads(t["output"] or "null"),
                        started_at=t["started_at"],
                        ended_at=t["ended_at"],
                        error=t["error"],
                    )
                )

            run.spans.append(span)

        return run
    
    
    
    def list_runs(
        self,
        agent_name: str | None = None,
        status: str | None = None,
        since: str | None = None,
    ) -> list[sqlite3.Row]:
        """
        Return all runs matching the supplied filters.
        """

        query = "SELECT * FROM runs WHERE 1=1"
        params = []

        if agent_name:
            query += " AND agent_name = ?"
            params.append(agent_name)

        if status:
            query += " AND status = ?"
            params.append(status)

        if since:
            query += " AND started_at >= ?"
            params.append(since)

        query += " ORDER BY started_at DESC"

        return self.conn.execute(query, params).fetchall()

    def list_agent_names(self) -> list[str]:
        """
        Return all distinct agent names.
        """

        rows = self.conn.execute(
            """
            SELECT DISTINCT agent_name
            FROM runs
            ORDER BY agent_name
            """
        ).fetchall()

        return [row["agent_name"] for row in rows]

    def get_run_count(self) -> int:
        """
        Return the total number of stored runs.
        """

        row = self.conn.execute(
            "SELECT COUNT(*) AS count FROM runs"
        ).fetchone()

        return row["count"]

    def list_statuses(self) -> list[str]:
        """
        Return all distinct run statuses.
        """

        rows = self.conn.execute(
            """
            SELECT DISTINCT status
            FROM runs
            ORDER BY status
            """
        ).fetchall()

        return [row["status"] for row in rows]

    def delete_run(self, run_id: str) -> None:
        """
        Delete a run and all related spans/tool calls.
        """

        self.conn.execute(
            "DELETE FROM runs WHERE run_id=?",
            (run_id,),
        )

        self.conn.commit()



    def close(self):
        self.conn.close()