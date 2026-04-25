"""FastAPI dependencies: inbound auth.

Two dependencies, two caller categories:

- `require_internal_bearer` — static bearer (`OPEX_INTERNAL_BEARER_TOKEN`)
  for service-to-service callers: SERX webhook ingest, OEX webhook ingest,
  Trigger.dev tasks. Direct string equality, no DB lookup.

- `get_current_auth` — EdDSA JWT verified against auth-engine-x's JWKS for
  operator-facing routes (admin status, event-route CRUD, scheduled-event
  CRUD, scheduler-runs query). Returns an `AuthContext` populated from the
  JWT claims.
"""

from __future__ import annotations

import secrets
from dataclasses import dataclass, field
from typing import Any

from fastapi import Header, HTTPException, status

from app.auth.jwt import decode_session_token
from app.config import settings


@dataclass(frozen=True)
class InternalContext:
    """Marker context for an authenticated internal service caller."""

    auth_method: str = "internal_bearer"


@dataclass(frozen=True)
class AuthContext:
    """Operator/JWT-authenticated caller context.

    OPEX is single-tenant by construction, so there's no `org_id` here.
    Whatever the JWT carries (sub, scopes, role, etc.) is exposed via
    `claims` for downstream use without baking schema assumptions in.
    """

    subject: str
    claims: dict[str, Any] = field(default_factory=dict)
    auth_method: str = "session_jwt"


def _extract_bearer(authorization: str | None) -> str | None:
    if not authorization:
        return None
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    return parts[1]


def require_internal_bearer(
    authorization: str | None = Header(default=None),
) -> InternalContext:
    """Static bearer gate for internal service-to-service callers.

    Validates `Authorization: Bearer <token>` against
    `OPEX_INTERNAL_BEARER_TOKEN`. The env var is required at startup
    (see `app.config._validate_startup_secrets`), so a 503 here means
    the value was unset between boot and request — almost always a
    deployment misconfiguration.
    """
    expected = settings.opex_internal_bearer_token
    if not expected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OPEX_INTERNAL_BEARER_TOKEN not configured (check Doppler).",
        )
    token = _extract_bearer(authorization)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token",
        )
    if not secrets.compare_digest(token, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    return InternalContext()


def get_current_auth(
    authorization: str | None = Header(default=None),
) -> AuthContext:
    """JWT gate for operator-facing routes.

    Verifies the bearer token as an EdDSA session JWT against
    auth-engine-x's JWKS (issuer, audience, exp, sub, type all
    enforced in `app.auth.jwt`).
    """
    token = _extract_bearer(authorization)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token",
        )
    payload = decode_session_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session token",
        )
    return AuthContext(subject=payload["sub"], claims=payload)
