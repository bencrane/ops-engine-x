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

from datetime import UTC, datetime
from typing import Any, Literal

import httpx
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

import json

from app import agent_defaults as agent_defaults_store
from app import event_routes as event_routes_store
from app import scheduled_events as scheduled_events_store
from app import scheduler_runs as scheduler_runs_store
from app import service_registry
from app.anthropic_client import create_session, get_agent, list_agents, send_user_message
from app.config import MissingSecretError, settings
from app.deps import require_admin_token, require_opex_auth
from app.sync import sync_from_anthropic


class AgentDefaultsPayload(BaseModel):
    environment_id: str = Field(..., min_length=1)
    vault_ids: list[str] = Field(default_factory=list)
    task_instruction: str | None = Field(
        default=None,
        description=(
            "Optional per-agent kickoff preamble prepended to the user.message "
            "sent when /events/receive fires. Use this to give the agent "
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


class ReceiveEventPayload(BaseModel):
    source: str = Field(..., min_length=1, description="e.g. 'emailbison', 'cal_com'")
    event_name: str = Field(..., min_length=1, description="e.g. 'lead_replied', 'BOOKING_CREATED'")
    event_ref: EventRef = Field(..., description="Pointer to the stored raw payload in the caller's DB")
    title: str | None = Field(default=None, description="Optional session title override")


class ReceiveEventResult(BaseModel):
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


class ScheduledEvent(BaseModel):
    event_id: str
    target_service: str
    target_path: str
    http_method: Literal["GET", "POST"] = "POST"
    enabled: bool
    description: str | None = None
    cron: str | None = None


class ScheduledEventPayload(BaseModel):
    target_service: str = Field(..., min_length=1, description="Registered service slug, e.g. 'serx'.")
    target_path: str = Field(..., pattern=r"^/", description="Path on the target service; must start with '/'.")
    http_method: Literal["GET", "POST"] = Field(
        default="POST",
        description=(
            "HTTP method the dispatcher uses to call the target. Defaults to POST "
            "(side-effectful scheduled work). Use GET for read-only polling, "
            "reachability probes, or targets that expose their trigger as GET."
        ),
    )
    enabled: bool = True
    description: str | None = None
    cron: str | None = Field(
        default=None,
        description="Cron string \u2014 informational only. Trigger.dev's task file owns the live cron.",
    )


class ScheduledEventList(BaseModel):
    data: list[ScheduledEvent]
    count: int


class TickRequest(BaseModel):
    event_id: str = Field(..., min_length=1)
    trigger_run_id: str | None = Field(
        default=None,
        description="Trigger.dev run id, stored on the scheduler_runs row for cross-linking.",
    )


class TickResult(BaseModel):
    event_id: str
    ok: bool
    http_status: int | None = None
    duration_ms: int
    summary: Any | None = None
    error: str | None = None
    scheduler_run_id: str


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
    process actually loaded what you expect. The outbound-services block is
    derived from `app.service_registry` so adding a new slug automatically
    surfaces its two creds here.
    """
    outbound_services: dict[str, dict[str, bool]] = {}
    for slug in service_registry.registered_slugs():
        reg = service_registry._REGISTRY[slug]  # noqa: SLF001
        outbound_services[slug] = {
            reg.base_url_env.lower(): bool(getattr(settings, reg.base_url_env.lower(), None)),
            reg.auth_token_env.lower(): bool(getattr(settings, reg.auth_token_env.lower(), None)),
        }
    return {
        "service": "ops-engine-x",
        "status": "ok",
        "secrets_loaded": {
            "opex_auth_token": bool(settings.opex_auth_token),
            "supabase_db_url": bool(settings.supabase_db_url),
        },
        "outbound_services": outbound_services,
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
    "/events/receive",
    dependencies=[Depends(require_opex_auth)],
    response_model=ReceiveEventResult,
)
def receive_event(body: ReceiveEventPayload) -> ReceiveEventResult:
    """Receive an inbound event from a webhook-ingest caller and dispatch.

    The caller sends `(source, event_name, event_ref)` \u2014 a pointer to the
    raw webhook payload stored in its own DB. ops-engine-x looks up the
    matching row in `event_routes`, resolves the target agent, and today
    fires the managed-agent session inline via the preserved-for-extraction
    Anthropic client. Post-extraction this handler shrinks to an HTTP call
    against managed-agents-x's invocation gateway; the endpoint's public
    contract does not change across that cutover.
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

    return ReceiveEventResult(
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
    "/internal/scheduler/tick",
    dependencies=[Depends(require_opex_auth)],
    response_model=TickResult,
)
def scheduler_tick(body: TickRequest) -> TickResult:
    """Fire a scheduled event.

    Called by the ops-engine-x Trigger.dev project when a cron task fires.
    Looks up `body.event_id` in `scheduled_events`, resolves the target
    service via `app.service_registry`, issues the configured HTTP call
    (GET or POST, per the row's `http_method`) to
    `{base_url}{target_path}` with the service's bearer token, appends a
    row to `scheduler_runs`, and returns the outcome.

    Method defaults to POST for existing rows and for the vast majority of
    scheduled work (side-effectful). GET is supported for polling /
    reachability-probe style events and for targets whose trigger endpoint
    happens to be GET.

    Always returns 200 on a successful *dispatcher* run \u2014 even if the
    target returned non-2xx or the request errored. Callers check `ok` to
    decide retries. Dispatcher-level failures (missing event, unknown
    service, missing credentials) return 4xx/5xx with no log row.
    """
    event = scheduled_events_store.get(body.event_id)
    if event is None:
        raise HTTPException(status_code=404, detail=f"No scheduled_event for event_id={body.event_id}")
    if not event["enabled"]:
        raise HTTPException(status_code=409, detail=f"scheduled_event {body.event_id} is disabled")

    try:
        target = service_registry.resolve(event["target_service"])
    except KeyError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except MissingSecretError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    target_url = f"{target.base_url}{event['target_path']}"
    method = event["http_method"]
    started_at = datetime.now(tz=UTC)
    http_status: int | None = None
    ok = False
    summary: Any | None = None
    error_text: str | None = None

    headers = {"Authorization": f"Bearer {target.auth_token}"}
    if method == "POST":
        headers["Content-Type"] = "application/json"

    try:
        with httpx.Client(timeout=60.0) as client:
            if method == "GET":
                resp = client.get(target_url, headers=headers)
            else:
                resp = client.post(target_url, headers=headers, json={})
        http_status = resp.status_code
        ok = resp.is_success
        summary = _parse_summary(resp.text)
        if not ok:
            error_text = f"HTTP {resp.status_code}"
    except httpx.HTTPError as exc:
        error_text = f"{type(exc).__name__}: {exc}"

    finished_at = datetime.now(tz=UTC)
    duration_ms = int((finished_at - started_at).total_seconds() * 1000)

    run = scheduler_runs_store.insert(
        task_id=event["event_id"],
        target_url=target_url,
        started_at=started_at,
        finished_at=finished_at,
        duration_ms=duration_ms,
        ok=ok,
        http_status=http_status,
        summary=summary,
        error=error_text,
        trigger_run_id=body.trigger_run_id,
    )

    return TickResult(
        event_id=event["event_id"],
        ok=ok,
        http_status=http_status,
        duration_ms=duration_ms,
        summary=summary,
        error=error_text,
        scheduler_run_id=run["id"],
    )


@app.get(
    "/internal/scheduler/runs",
    dependencies=[Depends(require_opex_auth)],
    response_model=SchedulerRunList,
)
def list_scheduler_runs(
    task_id: str | None = Query(default=None, description="Filter to a single task / event id."),
    ok: bool | None = Query(default=None, description="Filter to successes (true) or failures (false)."),
    limit: int = Query(default=50, ge=1, le=500),
) -> SchedulerRunList:
    rows = scheduler_runs_store.list_recent(task_id=task_id, ok=ok, limit=limit)
    return SchedulerRunList(data=[SchedulerRun(**r) for r in rows], count=len(rows))


@app.get(
    "/scheduled-events",
    dependencies=[Depends(require_opex_auth)],
    response_model=ScheduledEventList,
)
def list_scheduled_events() -> ScheduledEventList:
    rows = scheduled_events_store.list_all()
    return ScheduledEventList(data=[ScheduledEvent(**r) for r in rows], count=len(rows))


@app.get(
    "/scheduled-events/{event_id}",
    dependencies=[Depends(require_opex_auth)],
    response_model=ScheduledEvent,
)
def get_scheduled_event(event_id: str) -> ScheduledEvent:
    row = scheduled_events_store.get(event_id)
    if row is None:
        raise HTTPException(status_code=404, detail=f"No scheduled_event for event_id={event_id}")
    return ScheduledEvent(**row)


@app.put(
    "/scheduled-events/{event_id}",
    dependencies=[Depends(require_opex_auth)],
    response_model=ScheduledEvent,
)
def put_scheduled_event(event_id: str, payload: ScheduledEventPayload) -> ScheduledEvent:
    # Validate the slug is registered so operators can't set up an event
    # that will blow up at dispatch time.
    if payload.target_service not in service_registry.registered_slugs():
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unknown target_service '{payload.target_service}'. "
                f"Registered: {service_registry.registered_slugs()}."
            ),
        )
    row = scheduled_events_store.upsert(
        event_id,
        target_service=payload.target_service,
        target_path=payload.target_path,
        http_method=payload.http_method,
        enabled=payload.enabled,
        description=payload.description,
        cron=payload.cron,
    )
    return ScheduledEvent(**row)


@app.delete(
    "/scheduled-events/{event_id}",
    dependencies=[Depends(require_opex_auth)],
    response_model=DeleteResult,
)
def delete_scheduled_event(event_id: str) -> DeleteResult:
    deleted = scheduled_events_store.delete(event_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="No scheduled_event for that event_id")
    return DeleteResult(deleted=True)


def _parse_summary(raw: str) -> Any | None:
    """Parse a response body for storage in scheduler_runs.summary.

    Same contract as the trigger-side helper used to honour: valid JSON is
    stored as-is; otherwise the body is wrapped as {"raw_text": ...} and
    truncated to 8KB. Truncation here is a belt-and-suspenders cap on top
    of whatever the target service already returns.
    """
    max_bytes = 8 * 1024
    text = raw[:max_bytes] if len(raw) > max_bytes else raw
    if not text:
        return None
    try:
        return json.loads(text)
    except ValueError:
        return {"raw_text": text, "truncated": len(raw) > max_bytes}


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
