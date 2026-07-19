from agentlens.store import TraceStore

store = TraceStore()

row = store.conn.execute(
    """
    SELECT run_id
    FROM runs
    ORDER BY started_at DESC
    LIMIT 1
    """
).fetchone()

if row:
    print(row["run_id"])
else:
    raise SystemExit("No runs found.")