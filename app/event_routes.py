"""CRUD helpers for the event_routes table.

Maps (source, event_name) -> agent_id so webhook-ingest callers can stay dumb
and ops-engine-x is the single source of truth for event routing. The schema
currently supports only agent targets; non-agent HTTP targets will require a
schema extension and are not implemented yet.
"""

from __future__ import annotations

from typing import TypedDict

from app.db import connect


class EventRoute(TypedDict):
    source: str
    event_name: str
    agent_id: str
    enabled: bool


def resolve(source: str, event_name: str) -> EventRoute | None:
    with connect() as conn, conn.cursor() as cur:
        cur.execute(
            """
            select source, event_name, agent_id, enabled
            from event_routes
            where source = %s and event_name = %s
            """,
            (source, event_name),
        )
        row = cur.fetchone()
    if not row:
        return None
    return {"source": row[0], "event_name": row[1], "agent_id": row[2], "enabled": row[3]}


def list_all() -> list[EventRoute]:
    with connect() as conn, conn.cursor() as cur:
        cur.execute(
            "select source, event_name, agent_id, enabled from event_routes order by source, event_name"
        )
        rows = cur.fetchall()
    return [
        {"source": r[0], "event_name": r[1], "agent_id": r[2], "enabled": r[3]}
        for r in rows
    ]


def upsert(source: str, event_name: str, agent_id: str, enabled: bool = True) -> EventRoute:
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                insert into event_routes (source, event_name, agent_id, enabled)
                values (%s, %s, %s, %s)
                on conflict (source, event_name) do update set
                    agent_id = excluded.agent_id,
                    enabled = excluded.enabled,
                    updated_at = now()
                returning source, event_name, agent_id, enabled
                """,
                (source, event_name, agent_id, enabled),
            )
            row = cur.fetchone()
        conn.commit()
    return {"source": row[0], "event_name": row[1], "agent_id": row[2], "enabled": row[3]}


def delete(source: str, event_name: str) -> bool:
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "delete from event_routes where source = %s and event_name = %s",
                (source, event_name),
            )
            deleted = cur.rowcount > 0
        conn.commit()
    return deleted
