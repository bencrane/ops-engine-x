"""FastAPI entrypoint for managed-agents-x-api.

The app must start successfully with zero secrets configured. Any feature
that requires a secret reads it lazily via `app.config.require(...)`.
"""

from __future__ import annotations

from fastapi import FastAPI

from app.config import settings

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
        },
    }
