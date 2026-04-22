"""Secret contract for the application.

This file is the canonical list of environment variables the app expects.
Values are injected at runtime by `doppler run --` (via the Doppler CLI in
the container) from the Doppler project `managed-agents-x-api`, config `prd`.

Design rule: every field must be tolerant of being missing at import time.
The app must boot and `/health` must return 200 even if Doppler is
unreachable or a variable is unset. Required secrets are validated lazily
at the call site that actually needs them (see `require()`).
"""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        extra="ignore",
    )

    anthropic_api_key: str | None = None
    supabase_url: str | None = None
    supabase_service_role_key: str | None = None
    supabase_anon_key: str | None = None
    supabase_db_url: str | None = None
    supabase_project_ref: str | None = None
    mag_auth_token: str | None = None


settings = Settings()


class MissingSecretError(RuntimeError):
    """Raised when a secret required by a code path is not configured."""


def require(name: str) -> str:
    """Fetch a required secret by attribute name, raising a clear error if unset.

    Use this at the call site of any feature that genuinely needs the secret,
    e.g. `api_key = require("anthropic_api_key")`. This keeps startup tolerant
    while failing loudly and clearly when a feature is exercised without its
    required configuration.
    """
    value = getattr(settings, name, None)
    if not value:
        raise MissingSecretError(
            f"Required secret '{name.upper()}' is not set. "
            "Confirm it exists in Doppler (project: managed-agents-x-api, "
            "config: prd) and that DOPPLER_TOKEN is valid."
        )
    return value
