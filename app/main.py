"""FastAPI entrypoint for ops-engine-x.

ops-engine-x is the operational-heartbeat service: event routing from
domain-service webhook ingests to downstream targets (today: managed agents
via Anthropic; later: a managed-agents gateway and non-agent HTTP targets),
plus the admin surface for the routing table.

The app must start successfully with zero secrets configured. Any feature
that requires a secret reads it lazily via `app.config.require(...)`.

Inbound auth is `OPEX_AUTH_TOKEN` (bearer), checked via
`app.deps.require_opex_auth`. Some handlers below are preserved verbatim for
extraction into the future `managed-agents-x-api` repo — they will fail at
call time without `ANTHROPIC_API_KEY`, which is intentional (this project's
Doppler does not hold that secret).
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

import httpx
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

import json

from app import agent_defaults as agent_defaults_store
from app import event_routes as event_routes_store
from app import scheduler_runs as scheduler_runs_store
from app.anthropic_client import create_session, get_agent, list_agents, send_user_message
from app.config import settings
from app.deps import require_admin_token, require_opex_auth
from app.sync import sync_from_anthropic


class AgentDefaultsPayload(BaseModel):
    environment_id: str = Field(..., min_length=1)
    vault_ids: list[str] = Field(default_factory=list)
    task_instruction: str | None = Field(
        default=None,
        description=(
            "Optional per-agent kickoff preamble prepended to the user.message "
            "sent when /sessions/from-event fires. Use this to give the agent "
            "a short, durable job description that sits above the event payload."
        ),
    )


class AgentDefaults(BaseModel):
    agent_id: str
    environment_id: str
    vault_ids: list[str]
    task_instruction: str | None = None


class AgentDefaultsList(BaseModel):
    data: list[AgentDefaults]
    count: int


class DeleteResult(BaseModel):
    deleted: bool


class EventRef(BaseModel):
    store: str = Field(..., min_length=1, description="Caller-side table/store name, e.g. 'oex_webhook_events'")
    id: str = Field(..., min_length=1, description="UUID of the row holding the raw payload")


class FromEventPayload(BaseModel):
    source: str = Field(..., min_length=1, description="e.g. 'emailbison', 'cal.com'")
    event_name: str = Field(..., min_length=1, description="e.g. 'lead_replied', 'BOOKING_CREATED'")
    event_ref: EventRef = Field(..., description="Pointer to the stored raw payload in the caller's DB")
    title: str | None = Field(default=None, description="Optional session title override")


class FromEventResult(BaseModel):
    session_id: str
    agent_id: str
    environment_id: str
    vault_ids: list[str]
    status: str


class EventRoute(BaseModel):
    source: str
    event_name: str
    agent_id: str
    enabled: bool


class EventRoutePayload(BaseModel):
    agent_id: str = Field(..., min_length=1)
    enabled: bool = True


class EventRouteList(BaseModel):
    data: list[EventRoute]
    count: int


class SchedulerRunPayload(BaseModel):
    """Incoming log row from a Trigger.dev scheduled task."""

    task_id: str = Field(..., min_length=1, description="Trigger.dev task id, e.g. 'serx:scheduler-tick'.")
    target_url: str = Field(..., min_length=1, description="The URL the tick POSTed to.")
    started_at: datetime
    finished_at: datetime
    duration_ms: int = Field(..., ge=0)
    ok: bool
    http_status: int | None = Field(default=None, ge=100, le=599)
    summary: Any | None = Field(
        default=None,
        description="Response body from the target (any JSON value). Truncated client-side if oversized.",
    )
    error: str | None = Field(
        default=None,
        description="Short human-readable reason the run was not ok. Required when ok=false and no http_status was received.",
    )
    trigger_run_id: str | None = Field(
        default=None,
        description="Trigger.dev run id, for cross-linking to the Trigger.dev dashboard.",
    )


class SchedulerRun(BaseModel):
    id: str
    task_id: str
    target_url: str
    started_at: datetime
    finished_at: datetime
    duration_ms: int
    ok: bool
    http_status: int | None = None
    summary: Any | None = None
    error: str | None = None
    trigger_run_id: str | None = None
    created_at: datetime


class SchedulerRunList(BaseModel):
    data: list[SchedulerRun]
    count: int


app = FastAPI(
    title="ops-engine-x",
    version="0.1.0",
    description=(
        "Operational-heartbeat service. Routes events from domain-service webhook "
        "ingests to downstream targets (managed agents today; managed-agents-x-api "
        "and non-agent HTTP targets later). All non-public routes require a bearer "
        "OPEX_AUTH_TOKEN."
    ),
)


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness probe. Must stay dumb: no DB, no upstream calls, no secret checks."""
    return {"status": "ok"}


@app.get("/")
def root() -> dict[str, str]:
    """Minimal public identity endpoint. For diagnostics use GET /admin/status."""
    return {"service": "ops-engine-x", "status": "ok"}


@app.get("/admin/status", dependencies=[Depends(require_opex_auth)])
def admin_status() -> dict[str, object]:
    """Authenticated diagnostic probe: reports which configured secrets Doppler
    has successfully injected. Values are never returned, only presence booleans.

    Useful immediately after a deploy or DOPPLER_TOKEN rotation to verify the
    process actually loaded what you expect.
    """
    return {
        "service": "ops-engine-x",
        "status": "ok",
        "secrets_loaded": {
            "opex_auth_token": bool(settings.opex_auth_token),
            "supabase_db_url": bool(settings.supabase_db_url),
        },
    }


@app.post("/admin/sync/anthropic", dependencies=[Depends(require_admin_token)])
def admin_sync_anthropic() -> dict[str, object]:
    """Pull all managed agents from Anthropic and reconcile into the DB."""
    return sync_from_anthropic().as_dict()


def _passthrough_upstream_error(exc: httpx.HTTPStatusError) -> JSONResponse:
    try:
        body = exc.response.json()
    except ValueError:
        body = {"detail": exc.response.text or "Upstream Anthropic error"}
    return JSONResponse(status_code=exc.response.status_code, content=body)


@app.get(
    "/agents/defaults",
    dependencies=[Depends(require_admin_token)],
    response_model=AgentDefaultsList,
)
def list_agent_defaults() -> AgentDefaultsList:
    """List every agent_defaults row (frontend merges with /agents client-side)."""
    rows = agent_defaults_store.list_all()
    return AgentDefaultsList(data=[AgentDefaults(**r) for r in rows], count=len(rows))


@app.get(
    "/agents/{agent_id}/defaults",
    dependencies=[Depends(require_admin_token)],
    response_model=AgentDefaults,
)
def get_agent_defaults(agent_id: str) -> AgentDefaults:
    row = agent_defaults_store.get(agent_id)
    if row is None:
        raise HTTPException(status_code=404, detail="No defaults configured for this agent")
    return AgentDefaults(**row)


@app.put(
    "/agents/{agent_id}/defaults",
    dependencies=[Depends(require_admin_token)],
    response_model=AgentDefaults,
)
def put_agent_defaults(agent_id: str, payload: AgentDefaultsPayload) -> AgentDefaults:
    row = agent_defaults_store.upsert(
        agent_id,
        payload.environment_id,
        payload.vault_ids,
        payload.task_instruction,
    )
    return AgentDefaults(**row)


@app.delete(
    "/agents/{agent_id}/defaults",
    dependencies=[Depends(require_admin_token)],
    response_model=DeleteResult,
)
def delete_agent_defaults(agent_id: str) -> DeleteResult:
    deleted = agent_defaults_store.delete(agent_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="No defaults configured for this agent")
    return DeleteResult(deleted=True)


def _format_event_message(
    source: str,
    event_name: str,
    event_ref: EventRef,
    task_instruction: str | None = None,
) -> str:
    body = (
        f"source: {source}\n"
        f"event_name: {event_name}\n"
        f"event_ref: {json.dumps(event_ref.model_dump())}\n"
    )
    if task_instruction:
        return f"{task_instruction.rstrip()}\n\n{body}"
    return body


@app.post(
    "/sessions/from-event",
    dependencies=[Depends(require_opex_auth)],
    response_model=FromEventResult,
)
def create_session_from_event(body: FromEventPayload) -> FromEventResult:
    """Route (source, event_name) to an agent and fire a session.

    Webhook-ingest callers send a reference to their stored raw payload; the
    agent's system prompt tells it how to hydrate via the appropriate MCP tool.
    """
    route = event_routes_store.resolve(body.source, body.event_name)
    if route is None:
        raise HTTPException(
            status_code=404,
            detail=f"No event_route configured for ({body.source}, {body.event_name})",
        )
    if not route["enabled"]:
        raise HTTPException(
            status_code=409,
            detail=f"event_route for ({body.source}, {body.event_name}) is disabled",
        )

    agent_id = route["agent_id"]
    defaults = agent_defaults_store.get(agent_id)
    if defaults is None:
        raise HTTPException(
            status_code=409,
            detail=f"No agent_defaults configured for agent_id={agent_id}",
        )

    metadata = {
        "source": body.source,
        "event_name": body.event_name,
        "event_ref_store": body.event_ref.store,
        "event_ref_id": body.event_ref.id,
    }
    title = body.title or f"{body.source}:{body.event_name}"

    try:
        session = create_session(
            agent_id=agent_id,
            environment_id=defaults["environment_id"],
            vault_ids=defaults["vault_ids"],
            title=title,
            metadata=metadata,
        )
    except httpx.HTTPStatusError as exc:
        return _passthrough_upstream_error(exc)  # type: ignore[return-value]
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"create_session failed: {exc}") from exc

    try:
        send_user_message(
            session_id=session["id"],
            text=_format_event_message(
                body.source,
                body.event_name,
                body.event_ref,
                defaults.get("task_instruction"),
            ),
        )
    except httpx.HTTPStatusError as exc:
        return _passthrough_upstream_error(exc)  # type: ignore[return-value]
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502, detail=f"send_user_message failed: {exc}"
        ) from exc

    return FromEventResult(
        session_id=session["id"],
        agent_id=agent_id,
        environment_id=defaults["environment_id"],
        vault_ids=defaults["vault_ids"],
        status=session.get("status", "unknown"),
    )


@app.get(
    "/event-routes",
    dependencies=[Depends(require_opex_auth)],
    response_model=EventRouteList,
)
def list_event_routes() -> EventRouteList:
    rows = event_routes_store.list_all()
    return EventRouteList(data=[EventRoute(**r) for r in rows], count=len(rows))


@app.put(
    "/event-routes/{source}/{event_name}",
    dependencies=[Depends(require_opex_auth)],
    response_model=EventRoute,
)
def put_event_route(source: str, event_name: str, payload: EventRoutePayload) -> EventRoute:
    row = event_routes_store.upsert(source, event_name, payload.agent_id, payload.enabled)
    return EventRoute(**row)


@app.delete(
    "/event-routes/{source}/{event_name}",
    dependencies=[Depends(require_opex_auth)],
    response_model=DeleteResult,
)
def delete_event_route(source: str, event_name: str) -> DeleteResult:
    deleted = event_routes_store.delete(source, event_name)
    if not deleted:
        raise HTTPException(status_code=404, detail="No event_route configured")
    return DeleteResult(deleted=True)


@app.post(
    "/internal/scheduler/runs",
    dependencies=[Depends(require_opex_auth)],
    response_model=SchedulerRun,
    status_code=201,
)
def record_scheduler_run(body: SchedulerRunPayload) -> SchedulerRun:
    """Append a scheduler-run log row.

    Called by the ops-engine-x Trigger.dev project after every tick. The task
    itself owns the outbound work POST (to serx-api, oex-api, etc.) and then
    POSTs here with the outcome. ops-engine-x only records.
    """
    row = scheduler_runs_store.insert(
        task_id=body.task_id,
        target_url=body.target_url,
        started_at=body.started_at,
        finished_at=body.finished_at,
        duration_ms=body.duration_ms,
        ok=body.ok,
        http_status=body.http_status,
        summary=body.summary,
        error=body.error,
        trigger_run_id=body.trigger_run_id,
    )
    return SchedulerRun(**row)


@app.get(
    "/internal/scheduler/runs",
    dependencies=[Depends(require_opex_auth)],
    response_model=SchedulerRunList,
)
def list_scheduler_runs(
    task_id: str | None = Query(default=None, description="Filter to a single task id."),
    ok: bool | None = Query(default=None, description="Filter to successes (true) or failures (false)."),
    limit: int = Query(default=50, ge=1, le=500),
) -> SchedulerRunList:
    rows = scheduler_runs_store.list_recent(task_id=task_id, ok=ok, limit=limit)
    return SchedulerRunList(data=[SchedulerRun(**r) for r in rows], count=len(rows))


@app.get("/agents", dependencies=[Depends(require_admin_token)], response_model=None)
def get_agents() -> JSONResponse | dict[str, object]:
    """List all managed agents (live passthrough to Anthropic, paginated server-side)."""
    try:
        agents = list(list_agents())
    except httpx.HTTPStatusError as exc:
        return _passthrough_upstream_error(exc)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Upstream request failed: {exc}") from exc
    return {"data": agents, "count": len(agents)}


@app.get("/agents/{agent_id}", dependencies=[Depends(require_admin_token)], response_model=None)
def get_agent_by_id(agent_id: str) -> JSONResponse | dict:
    """Single agent (live passthrough to Anthropic)."""
    try:
        return get_agent(agent_id)
    except httpx.HTTPStatusError as exc:
        return _passthrough_upstream_error(exc)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Upstream request failed: {exc}") from exc
