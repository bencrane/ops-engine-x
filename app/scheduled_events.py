"""CRUD helpers for the scheduled_events table.

Maps event_id -> (target_service, target_path, enabled, description, cron).
Ops-engine-x's `/internal/scheduler/tick` dispatcher resolves an incoming
event_id through here, then through `app.service_registry` to get the
base URL + auth token, then POSTs to target_service + target_path.

See app/main.py for the dispatcher and app/service_registry.py for the
slug-to-credentials mapping.
"""

from __future__ import annotations

from typing import TypedDict

from app.db import connect


class ScheduledEvent(TypedDict):
    event_id: str
    target_service: str
    target_path: str
    enabled: bool
    description: str | None
    cron: str | None


_COLS = "event_id, target_service, target_path, enabled, description, cron"


def _row_to_dict(row: tuple) -> ScheduledEvent:
    return {
        "event_id": row[0],
        "target_service": row[1],
        "target_path": row[2],
        "enabled": row[3],
        "description": row[4],
        "cron": row[5],
    }


def get(event_id: str) -> ScheduledEvent | None:
    with connect() as conn, conn.cursor() as cur:
        cur.execute(
            f"select {_COLS} from scheduled_events where event_id = %s",
            (event_id,),
        )
        row = cur.fetchone()
    if not row:
        return None
    return _row_to_dict(row)


def list_all() -> list[ScheduledEvent]:
    with connect() as conn, conn.cursor() as cur:
        cur.execute(f"select {_COLS} from scheduled_events order by event_id")
        rows = cur.fetchall()
    return [_row_to_dict(r) for r in rows]


def upsert(
    event_id: str,
    *,
    target_service: str,
    target_path: str,
    enabled: bool = True,
    description: str | None = None,
    cron: str | None = None,
) -> ScheduledEvent:
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                insert into scheduled_events
                    (event_id, target_service, target_path, enabled, description, cron)
                values (%s, %s, %s, %s, %s, %s)
                on conflict (event_id) do update set
                    target_service = excluded.target_service,
                    target_path = excluded.target_path,
                    enabled = excluded.enabled,
                    description = excluded.description,
                    cron = excluded.cron,
                    updated_at = now()
                returning {_COLS}
                """,
                (event_id, target_service, target_path, enabled, description, cron),
            )
            row = cur.fetchone()
        conn.commit()
    assert row is not None
    return _row_to_dict(row)


def delete(event_id: str) -> bool:
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("delete from scheduled_events where event_id = %s", (event_id,))
            deleted = cur.rowcount > 0
        conn.commit()
    return deleted
