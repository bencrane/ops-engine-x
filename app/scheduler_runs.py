"""CRUD helpers for the scheduler_runs table.

Append-only log of every Trigger.dev scheduled-task tick dispatched by the
`ops-engine-x` Trigger.dev project. Rows are inserted by the task itself,
which POSTs to `/internal/scheduler/runs` after its outbound work POST
completes (successfully or not). ops-engine-x never generates ticks — it
only records them.

Design notes:
- `summary` is an arbitrary jsonb blob representing the target service's
  response body. The tick caps its size client-side; this module does not
  re-validate shape.
- `http_status` is nullable because a run can fail before a response is
  received (DNS failure, connect timeout, etc.), in which case only
  `error` will be set.
- There is no `updated_at` — rows are immutable by contract.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, TypedDict

from app.db import connect


class SchedulerRun(TypedDict):
    id: str
    task_id: str
    target_url: str
    started_at: datetime
    finished_at: datetime
    duration_ms: int
    ok: bool
    http_status: int | None
    summary: Any | None
    error: str | None
    trigger_run_id: str | None
    created_at: datetime


_COLS = (
    "id, task_id, target_url, started_at, finished_at, duration_ms, "
    "ok, http_status, summary, error, trigger_run_id, created_at"
)


def _row_to_dict(row: tuple) -> SchedulerRun:
    return {
        "id": str(row[0]),
        "task_id": row[1],
        "target_url": row[2],
        "started_at": row[3],
        "finished_at": row[4],
        "duration_ms": row[5],
        "ok": row[6],
        "http_status": row[7],
        "summary": row[8],
        "error": row[9],
        "trigger_run_id": row[10],
        "created_at": row[11],
    }


def insert(
    *,
    task_id: str,
    target_url: str,
    started_at: datetime,
    finished_at: datetime,
    duration_ms: int,
    ok: bool,
    http_status: int | None = None,
    summary: Any | None = None,
    error: str | None = None,
    trigger_run_id: str | None = None,
) -> SchedulerRun:
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                insert into scheduler_runs (
                    task_id, target_url, started_at, finished_at, duration_ms,
                    ok, http_status, summary, error, trigger_run_id
                )
                values (%s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s, %s)
                returning {_COLS}
                """,
                (
                    task_id,
                    target_url,
                    started_at,
                    finished_at,
                    duration_ms,
                    ok,
                    http_status,
                    # psycopg adapts dicts to jsonb via json.dumps; be explicit
                    # to keep non-dict payloads (list, str, int) working too.
                    _jsonb(summary),
                    error,
                    trigger_run_id,
                ),
            )
            row = cur.fetchone()
        conn.commit()
    assert row is not None
    return _row_to_dict(row)


def list_recent(
    *,
    task_id: str | None = None,
    ok: bool | None = None,
    limit: int = 50,
) -> list[SchedulerRun]:
    # Guard against pathological queries. The index is on (task_id, started_at)
    # so unfiltered scans are tolerable but we still cap.
    limit = max(1, min(limit, 500))
    clauses: list[str] = []
    params: list[Any] = []
    if task_id is not None:
        clauses.append("task_id = %s")
        params.append(task_id)
    if ok is not None:
        clauses.append("ok = %s")
        params.append(ok)
    where = f"where {' and '.join(clauses)}" if clauses else ""
    params.append(limit)
    with connect() as conn, conn.cursor() as cur:
        cur.execute(
            f"""
            select {_COLS}
            from scheduler_runs
            {where}
            order by started_at desc
            limit %s
            """,
            params,
        )
        rows = cur.fetchall()
    return [_row_to_dict(r) for r in rows]


def _jsonb(value: Any) -> str | None:
    """Serialize a Python value to a JSON string for the jsonb column.

    psycopg doesn't auto-adapt arbitrary Python objects to jsonb; we send a
    pre-serialized JSON string and cast with `%s::jsonb` in the SQL.
    """
    if value is None:
        return None
    import json

    return json.dumps(value, default=str)
