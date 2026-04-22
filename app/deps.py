"""FastAPI dependencies (secret validation, auth)."""

from __future__ import annotations

import secrets

from fastapi import Header, HTTPException, status

from app.config import settings


def require_admin_token(authorization: str | None = Header(default=None)) -> None:
    """Bearer-token gate for admin-only endpoints using MAG_AUTH_TOKEN from Doppler."""
    expected = settings.mag_auth_token
    if not expected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="MAG_AUTH_TOKEN not configured (check Doppler).",
        )
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    provided = authorization.split(" ", 1)[1].strip()
    if not secrets.compare_digest(provided, expected):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
