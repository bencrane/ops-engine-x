"""FastAPI entrypoint for managed-agents-x-api.

The app must start successfully with zero secrets configured. Any feature
that requires a secret reads it lazily via `app.config.require(...)`.
"""

from __future__ import annotations

import httpx
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import JSONResponse

from app.anthropic_client import get_agent, list_agents
from app.config import settings
from app.deps import require_admin_token
from app.sync import sync_from_anthropic

app = FastAPI(
    title="managed-agents-x-api",
    version="0.1.0",
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


@app.get("/agents", dependencies=[Depends(require_admin_token)])
def get_agents() -> JSONResponse | dict[str, object]:
    """List all managed agents (live passthrough to Anthropic, paginated server-side)."""
    try:
        agents = list(list_agents())
    except httpx.HTTPStatusError as exc:
        return _passthrough_upstream_error(exc)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Upstream request failed: {exc}") from exc
    return {"data": agents, "count": len(agents)}


@app.get("/agents/{agent_id}", dependencies=[Depends(require_admin_token)])
def get_agent_by_id(agent_id: str) -> JSONResponse | dict:
    """Single agent (live passthrough to Anthropic)."""
    try:
        return get_agent(agent_id)
    except httpx.HTTPStatusError as exc:
        return _passthrough_upstream_error(exc)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Upstream request failed: {exc}") from exc
