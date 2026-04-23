"""Secret contract for the application.

This file is the canonical list of environment variables the app expects.
Values are injected at runtime by `doppler run --` (via the Doppler CLI in
the container) from the Doppler project `ops-engine-x`, config `prd`.

Design rule: every field must be tolerant of being missing at import time.
The app must boot and `/health` must return 200 even if Doppler is
unreachable or a variable is unset. Required secrets are validated lazily
at the call site that actually needs them (see `require()`).

Notes on a few specific fields:
- `opex_auth_token` is the inbound bearer token domain services use to
  authenticate into this service. It's the one secret the routing surface
  (`/events/receive`, `/event-routes/*`, `/admin/status`) treats as
  required.
- `anthropic_api_key` is **not** a secret this project is expected to hold.
  It is present on `Settings` only because the preserved-for-extraction
  code paths (`app/anthropic_client.py`, `app/sync.py`,
  `scripts/setup_orchestrator.py`, and the `/agents*` + `/admin/sync/anthropic`
  route handlers) still reference it. Those code paths will fail clearly via
  `require("anthropic_api_key")` until they are extracted into
  `managed-agents-x-api`. Do not add `ANTHROPIC_API_KEY` to this project's
  Doppler config.
"""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        extra="ignore",
    )

    opex_auth_token: str | None = None
    supabase_url: str | None = None
    supabase_service_role_key: str | None = None
    supabase_anon_key: str | None = None
    supabase_db_url: str | None = None
    supabase_project_ref: str | None = None

    # Outbound service credentials. Each downstream service ops-engine-x
    # dispatches to needs a matching pair here and an entry in
    # `app.service_registry`. Slugs currently registered: serx, oex.
    serx_api_url: str | None = None
    serx_auth_token: str | None = None
    oex_api_url: str | None = None
    oex_auth_token: str | None = None

    anthropic_api_key: str | None = None


settings = Settings()


class MissingSecretError(RuntimeError):
    """Raised when a secret required by a code path is not configured."""


def require(name: str) -> str:
    """Fetch a required secret by attribute name, raising a clear error if unset.

    Use this at the call site of any feature that genuinely needs the secret,
    e.g. `token = require("opex_auth_token")`. This keeps startup tolerant
    while failing loudly and clearly when a feature is exercised without its
    required configuration.
    """
    value = getattr(settings, name, None)
    if not value:
        raise MissingSecretError(
            f"Required secret '{name.upper()}' is not set. "
            "Confirm it exists in Doppler (project: ops-engine-x, "
            "config: prd) and that DOPPLER_TOKEN is valid."
        )
    return value
