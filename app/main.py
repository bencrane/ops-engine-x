"""FastAPI entrypoint for managed-agents-x-api.

The app must start successfully with zero secrets configured. Any feature
that requires a secret reads it lazily via `app.config.require(...)`.
"""

from __future__ import annotations

from fastapi import Depends, FastAPI

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
