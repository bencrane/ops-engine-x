"""CRUD helpers for the agent_defaults table.

Stores per-agent default session config (environment_id + vault_ids) used when
external triggers (e.g. cal.com bookings) spin up a session for an agent.
No FK to upstream Anthropic agents — orphans are fine and simply never resolve.
"""

from __future__ import annotations

from typing import TypedDict

from app.db import connect


class AgentDefaults(TypedDict):
    agent_id: str
    environment_id: str
    vault_ids: list[str]


def get(agent_id: str) -> AgentDefaults | None:
    with connect() as conn, conn.cursor() as cur:
        cur.execute(
            "select agent_id, environment_id, vault_ids from agent_defaults where agent_id = %s",
            (agent_id,),
        )
        row = cur.fetchone()
    if not row:
        return None
    return {"agent_id": row[0], "environment_id": row[1], "vault_ids": list(row[2] or [])}


def list_all() -> list[AgentDefaults]:
    with connect() as conn, conn.cursor() as cur:
        cur.execute("select agent_id, environment_id, vault_ids from agent_defaults order by agent_id")
        rows = cur.fetchall()
    return [
        {"agent_id": r[0], "environment_id": r[1], "vault_ids": list(r[2] or [])}
        for r in rows
    ]


def upsert(agent_id: str, environment_id: str, vault_ids: list[str]) -> AgentDefaults:
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                insert into agent_defaults (agent_id, environment_id, vault_ids)
                values (%s, %s, %s)
                on conflict (agent_id) do update set
                    environment_id = excluded.environment_id,
                    vault_ids = excluded.vault_ids,
                    updated_at = now()
                returning agent_id, environment_id, vault_ids
                """,
                (agent_id, environment_id, vault_ids),
            )
            row = cur.fetchone()
        conn.commit()
    return {"agent_id": row[0], "environment_id": row[1], "vault_ids": list(row[2] or [])}


def delete(agent_id: str) -> bool:
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("delete from agent_defaults where agent_id = %s", (agent_id,))
            deleted = cur.rowcount > 0
        conn.commit()
    return deleted
