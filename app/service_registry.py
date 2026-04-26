"""Registry of downstream services ops-engine-x can dispatch to.

Maps a short service slug (e.g. `serx`) to the Doppler env var name that
holds the service's public base URL. **Auth is uniform**: every outbound
call uses a fresh M2M JWT minted via `aux_m2m_client` from this backend's
own `AUX_M2M_API_KEY`. There is no per-service bearer token.

Adding a new service = one entry here + the base-URL secret in the
ops-engine-x Doppler config + the receiver-side backend must accept M2M
JWTs (i.e. its routes are guarded by `aux_m2m_server.require_m2m`).
Nothing else in the codebase needs to know about a new target.

Design:
- Values are indirected through env var names rather than read from
  `settings` directly so we can add services without touching `Settings`.
  Any new secret still needs a Settings field (per AGENTS.md), but the
  dispatcher layer itself stays agnostic.
- `resolve()` raises a clear `MissingSecretError` if the base URL env var
  is unset — same failure mode as `app.config.require()`.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.config import MissingSecretError, settings


@dataclass(frozen=True)
class ServiceRegistration:
    slug: str
    base_url_env: str


# The registry. Keep entries sorted by slug. Slugs are lowercase snake-case
# and never appear in user-facing URLs — they're the internal key used by
# scheduled_events.target_service (and future routing tables).
_REGISTRY: dict[str, ServiceRegistration] = {
    "mag": ServiceRegistration(slug="mag", base_url_env="MAGS_API_BASE_URL"),
    "oex": ServiceRegistration(slug="oex", base_url_env="OEX_API_BASE_URL"),
    "serx": ServiceRegistration(slug="serx", base_url_env="SERX_API_BASE_URL"),
    # "opex" (self-call) intentionally omitted until we actually need a
    # scheduled job that hits an ops-engine-x internal endpoint. When that
    # comes, prefer an in-process dispatch helper over HTTP loopback.
}


@dataclass(frozen=True)
class ResolvedService:
    slug: str
    base_url: str


def resolve(slug: str) -> ResolvedService:
    """Resolve a service slug to its live base URL.

    Raises `KeyError` if the slug is not registered (caller should map to a
    400-class HTTP error). Raises `MissingSecretError` if the slug is
    registered but its base-URL env var is unset (caller should map to 503).
    """
    reg = _REGISTRY.get(slug)
    if reg is None:
        raise KeyError(f"Unknown target_service slug '{slug}'. Registered: {sorted(_REGISTRY)}")
    base_url = _read_env(reg.base_url_env)
    if not base_url:
        raise MissingSecretError(
            f"Service '{slug}' base URL is not configured. "
            f"Set {reg.base_url_env} in Doppler (ops-engine-x/prd)."
        )
    return ResolvedService(slug=reg.slug, base_url=base_url.rstrip("/"))


def registered_slugs() -> list[str]:
    """List every registered service slug (for diagnostic endpoints)."""
    return sorted(_REGISTRY)


def _read_env(name: str) -> str | None:
    # pydantic-settings lowercases field names; look up case-insensitively.
    return getattr(settings, name.lower(), None)
