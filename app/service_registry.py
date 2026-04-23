"""Registry of downstream services ops-engine-x can dispatch to.

Maps a short service slug (e.g. `serx`) to the pair of Doppler env var names
that hold (a) the service's public base URL and (b) the bearer token used
to authenticate outbound calls to it.

Adding a new service = one entry here + the two secrets in the ops-engine-x
Doppler config. Nothing else in the codebase needs to know about a new
target. `POST /internal/scheduler/tick` and any future inbound-routing
dispatcher both read through this.

Design:
- Values are indirected through env var names rather than read from
  `settings` directly so we can add services without touching `Settings`.
  Any new secret still needs a Settings field (per AGENTS.md), but the
  dispatcher layer itself stays agnostic.
- `resolve()` raises a clear `MissingSecretError` if either env var is
  unset \u2014 same failure mode as `app.config.require()`.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.config import MissingSecretError, settings


@dataclass(frozen=True)
class ServiceRegistration:
    slug: str
    base_url_env: str
    auth_token_env: str


# The registry. Keep entries sorted by slug. Slugs are lowercase snake-case
# and never appear in user-facing URLs \u2014 they're the internal key used by
# scheduled_events.target_service (and future routing tables).
_REGISTRY: dict[str, ServiceRegistration] = {
    "serx": ServiceRegistration(
        slug="serx",
        base_url_env="SERX_API_URL",
        auth_token_env="SERX_AUTH_TOKEN",
    ),
    "oex": ServiceRegistration(
        slug="oex",
        base_url_env="OEX_API_URL",
        auth_token_env="OEX_AUTH_TOKEN",
    ),
    # "opex" (self-call) intentionally omitted until we actually need a
    # scheduled job that hits an ops-engine-x internal endpoint. When that
    # comes, prefer an in-process dispatch helper over HTTP loopback.
}


@dataclass(frozen=True)
class ResolvedService:
    slug: str
    base_url: str
    auth_token: str


def resolve(slug: str) -> ResolvedService:
    """Resolve a service slug to its live base URL + auth token.

    Raises `KeyError` if the slug is not registered (caller should map to a
    400-class HTTP error). Raises `MissingSecretError` if the slug is
    registered but one of its env vars is unset (caller should map to 503).
    """
    reg = _REGISTRY.get(slug)
    if reg is None:
        raise KeyError(f"Unknown target_service slug '{slug}'. Registered: {sorted(_REGISTRY)}")
    base_url = _read_env(reg.base_url_env)
    auth_token = _read_env(reg.auth_token_env)
    if not base_url:
        raise MissingSecretError(
            f"Service '{slug}' base URL is not configured. "
            f"Set {reg.base_url_env} in Doppler (ops-engine-x/prd)."
        )
    if not auth_token:
        raise MissingSecretError(
            f"Service '{slug}' auth token is not configured. "
            f"Set {reg.auth_token_env} in Doppler (ops-engine-x/prd)."
        )
    return ResolvedService(slug=reg.slug, base_url=base_url.rstrip("/"), auth_token=auth_token)


def registered_slugs() -> list[str]:
    """List every registered service slug (for diagnostic endpoints)."""
    return sorted(_REGISTRY)


def _read_env(name: str) -> str | None:
    # pydantic-settings lowercases field names; look up case-insensitively.
    return getattr(settings, name.lower(), None)
