"""EdDSA JWT verification against auth-engine-x's JWKS endpoint.

Modelled after outbound-engine-x's `src/auth/jwt.py`. JWKS URL, issuer, and
audience all come from env (`AUX_JWKS_URL`, `AUX_ISSUER`, `AUX_AUDIENCE`).
The JWKS set is cached for 5 minutes by `PyJWKClient`.
"""

from __future__ import annotations

import jwt
from jwt import PyJWKClient

from app.config import settings

_jwks_client = PyJWKClient(
    settings.aux_jwks_url,
    cache_jwk_set=True,
    lifespan=300,
)


def _decode_token(token: str, expected_type: str) -> dict | None:
    """Verify a JWT against the JWKS endpoint and check the `type` claim.

    Returns the payload dict on success, None on any verification failure
    (expired, bad signature, wrong issuer/audience, wrong type, etc.).
    """
    try:
        signing_key = _jwks_client.get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["EdDSA"],
            issuer=settings.aux_issuer,
            audience=settings.aux_audience,
            options={"require": ["exp", "sub", "type"]},
        )
        if payload.get("type") != expected_type:
            return None
        return payload
    except jwt.PyJWTError:
        return None


def decode_session_token(token: str) -> dict | None:
    """Decode and validate a session JWT (operator/user token)."""
    return _decode_token(token, "session")


def decode_m2m_token(token: str) -> dict | None:
    """Decode and validate an M2M JWT (service-to-service token)."""
    return _decode_token(token, "m2m")
