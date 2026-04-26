"""FastAPI entrypoint for ops-engine-x.

ops-engine-x is the operational-heartbeat service: it receives inbound
events from webhook-ingest callers, looks up a routing decision in its
`event_routes` table, and hands off to the right downstream service.
Today every route targets a managed agent, invoked via managed-agents-x.
Tomorrow other `target_kind`s (raw HTTP calls, Trigger.dev task runs,
etc.) plug into the same dispatch surface.

ops-engine-x never creates Anthropic sessions and never holds
`ANTHROPIC_API_KEY`. The session lifecycle and all agent-product state
(agent_defaults, system prompts, vaults, versions) live entirely in
managed-agents-x. This service's job is routing plumbing.

Inbound auth has two flavours, both verified against auth-engine-x's
JWKS by `aux_m2m_server`:

- Service-to-service callers (SERX/OEX webhook ingest, Trigger.dev tasks)
  present a short-lived M2M JWT and hit `require_m2m`.
- Operator-facing routes (admin status, event-route CRUD, scheduled-event
  CRUD, scheduler-runs query) require an EdDSA session JWT verified by
  `require_session`.

Inbound-auth env vars (`AUX_JWKS_URL`, `AUX_ISSUER`, `AUX_AUDIENCE`,
`AUX_API_BASE_URL`, `AUX_M2M_API_KEY`) are required at startup; the
process fails to boot if any are missing. Outbound credentials are uniform
— every call out uses a fresh M2M JWT from `aux_m2m_client.M2MAuth`, no
per-service bearers. Outbound base URLs are validated lazily at the call
site that needs them.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any, Literal

import httpx
from aux_m2m_client import M2MAuth, M2MTokenClient
from aux_m2m_server import require_m2m, require_session
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app import event_routes as event_routes_store
from app import scheduled_events as scheduled_events_store
from app import scheduler_runs as scheduler_runs_store
from app import service_registry
from app.config import MissingSecretError, settings


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


# --- Outbound auth (M2M) -----------------------------------------------------
#
# One process-wide token client + Auth pair. The token client caches a minted
# M2M JWT in memory and refreshes ~30s before expiry; M2MAuth attaches it to
# every outbound httpx request and retries once on a 401 (after invalidating
# the cache).
_m2m_token_client = M2MTokenClient(settings.to_m2m_config())
_m2m_auth = M2MAuth(_m2m_token_client)


app = FastAPI(
    title="ops-engine-x",
    version="0.3.0",
    description=(
        "Operational-heartbeat service. Receives events from domain-service "
        "webhook ingests and routes them to downstream targets (managed agents "
        "via managed-agents-x today; future non-agent targets plug in via the "
        "same event_routes registry). Internal routes require an M2M JWT; "
        "operator-facing routes require an auth-engine-x session JWT."
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


@app.get("/admin/status", dependencies=[Depends(require_session)])
def admin_status() -> dict[str, object]:
    """Authenticated diagnostic probe: reports which configured secrets Doppler
    has successfully injected. Values are never returned, only presence booleans.

    Useful immediately after a deploy or DOPPLER_TOKEN rotation to verify the
    process actually loaded what you expect. The outbound-services block is
    derived from `app.service_registry` so adding a new slug automatically
    surfaces its base-URL cred here.
    """
    outbound_services: dict[str, dict[str, bool]] = {}
    for slug in service_registry.registered_slugs():
        reg = service_registry._REGISTRY[slug]  # noqa: SLF001
        outbound_services[slug] = {
            reg.base_url_env.lower(): bool(getattr(settings, reg.base_url_env.lower(), None)),
        }
    return {
        "service": "ops-engine-x",
        "status": "ok",
        "secrets_loaded": {
            "aux_jwks_url": bool(settings.aux_jwks_url),
            "aux_issuer": bool(settings.aux_issuer),
            "aux_audience": bool(settings.aux_audience),
            "aux_api_base_url": bool(settings.aux_api_base_url),
            "aux_m2m_api_key": bool(settings.aux_m2m_api_key),
            "opex_db_url_pooled": bool(settings.opex_db_url_pooled),
        },
        "outbound_services": outbound_services,
    }


@app.post(
    "/events/receive",
    dependencies=[Depends(require_m2m)],
    response_model=None,
)
def receive_event(body: ReceiveEventPayload) -> JSONResponse:
    """Receive an inbound event from a webhook-ingest caller and dispatch.

    The caller sends `(source, event_name, event_ref)` \u2014 a pointer to the
    raw webhook payload stored in its own DB. ops-engine-x looks up the
    matching row in `event_routes` to resolve `agent_id`, then HTTP-forwards
    the event to managed-agents-x's invocation gateway. managed-agents-x
    owns agent_defaults lookup, Anthropic session creation, and kickoff
    message formatting.

    Error surface:
    - 404: no `event_route` for `(source, event_name)`.
    - 409: `event_route` exists but is disabled.
    - 500: `service_registry` has no `mag` slug (config bug).
    - 503: `MAGS_API_BASE_URL` not set in this project's Doppler.
    - 502: managed-agents-x unreachable (DNS, TCP, TLS, timeout).
    - Passthrough: any 2xx/4xx/5xx managed-agents-x returns, body verbatim.
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

    try:
        target = service_registry.resolve("mag")
    except KeyError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except MissingSecretError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    target_url = f"{target.base_url}/internal/agents/{agent_id}/invoke"

    try:
        with httpx.Client(timeout=60.0, auth=_m2m_auth) as client:
            resp = client.post(
                target_url,
                headers={"Content-Type": "application/json"},
                json={
                    "source":          body.source,
                    "event_name":      body.event_name,
                    "event_ref":       body.event_ref.model_dump(),
                    "title":           body.title,
                    "idempotency_key": body.event_ref.id,
                },
            )
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"managed-agents-x unreachable: {type(exc).__name__}: {exc}",
        ) from exc

    try:
        content: Any = resp.json()
    except ValueError:
        content = {"detail": resp.text or "Upstream managed-agents-x error"}
    return JSONResponse(status_code=resp.status_code, content=content)


@app.get(
    "/event-routes",
    dependencies=[Depends(require_session)],
    response_model=EventRouteList,
)
def list_event_routes() -> EventRouteList:
    rows = event_routes_store.list_all()
    return EventRouteList(data=[EventRoute(**r) for r in rows], count=len(rows))


@app.put(
    "/event-routes/{source}/{event_name}",
    dependencies=[Depends(require_session)],
    response_model=EventRoute,
)
def put_event_route(source: str, event_name: str, payload: EventRoutePayload) -> EventRoute:
    row = event_routes_store.upsert(source, event_name, payload.agent_id, payload.enabled)
    return EventRoute(**row)


@app.delete(
    "/event-routes/{source}/{event_name}",
    dependencies=[Depends(require_session)],
    response_model=DeleteResult,
)
def delete_event_route(source: str, event_name: str) -> DeleteResult:
    deleted = event_routes_store.delete(source, event_name)
    if not deleted:
        raise HTTPException(status_code=404, detail="No event_route configured")
    return DeleteResult(deleted=True)


@app.post(
    "/internal/scheduler/tick",
    dependencies=[Depends(require_m2m)],
    response_model=TickResult,
)
def scheduler_tick(body: TickRequest) -> TickResult:
    """Fire a scheduled event.

    Called by the ops-engine-x Trigger.dev project when a cron task fires.
    Looks up `body.event_id` in `scheduled_events`, resolves the target
    service via `app.service_registry`, issues the configured HTTP call
    (GET or POST, per the row's `http_method`) to
    `{base_url}{target_path}` with a fresh M2M JWT (via M2MAuth), appends
    a row to `scheduler_runs`, and returns the outcome.

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

    headers: dict[str, str] = {}
    if method == "POST":
        headers["Content-Type"] = "application/json"

    try:
        with httpx.Client(timeout=60.0, auth=_m2m_auth) as client:
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
    dependencies=[Depends(require_session)],
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
    dependencies=[Depends(require_session)],
    response_model=ScheduledEventList,
)
def list_scheduled_events() -> ScheduledEventList:
    rows = scheduled_events_store.list_all()
    return ScheduledEventList(data=[ScheduledEvent(**r) for r in rows], count=len(rows))


@app.get(
    "/scheduled-events/{event_id}",
    dependencies=[Depends(require_session)],
    response_model=ScheduledEvent,
)
def get_scheduled_event(event_id: str) -> ScheduledEvent:
    row = scheduled_events_store.get(event_id)
    if row is None:
        raise HTTPException(status_code=404, detail=f"No scheduled_event for event_id={event_id}")
    return ScheduledEvent(**row)


@app.put(
    "/scheduled-events/{event_id}",
    dependencies=[Depends(require_session)],
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
    dependencies=[Depends(require_session)],
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
