"""FastAPI entrypoint for managed-agents-x-api.

The app must start successfully with zero secrets configured. Any feature
that requires a secret reads it lazily via `app.config.require(...)`.
"""

from __future__ import annotations

import httpx
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app import agent_defaults as agent_defaults_store
from app.anthropic_client import get_agent, list_agents
from app.config import settings
from app.deps import require_admin_token
from app.sync import sync_from_anthropic


class AgentDefaultsPayload(BaseModel):
    environment_id: str = Field(..., min_length=1)
    vault_ids: list[str] = Field(default_factory=list)


class AgentDefaults(BaseModel):
    agent_id: str
    environment_id: str
    vault_ids: list[str]


class AgentDefaultsList(BaseModel):
    data: list[AgentDefaults]
    count: int


class DeleteResult(BaseModel):
    deleted: bool


app = FastAPI(
    title="managed-agents-x-api",
    version="0.1.0",
    description=(
        "Backend service that owns the Anthropic Managed Agents API key and "
        "stores per-agent defaults (environment_id, vault_ids) for external triggers. "
        "All /agents* and /admin* routes require a bearer MAG_AUTH_TOKEN."
    ),
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/")
def root() -> dict[str, object]:
    return {
        "service": "managed-agents-x-api",
        "status": "ok",
        "secrets_loaded": {
            "anthropic_api_key": bool(settings.anthropic_api_key),
            "supabase_db_url": bool(settings.supabase_db_url),
            "mag_auth_token": bool(settings.mag_auth_token),
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
    row = agent_defaults_store.upsert(agent_id, payload.environment_id, payload.vault_ids)
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
