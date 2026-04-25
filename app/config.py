"""Secret contract for the application.

This file is the canonical list of environment variables the app expects.
Values are injected at runtime by `doppler run --` (via the Doppler CLI in
the container) from the Doppler project `ops-engine-x`, config `prd`.

Auth contract (inbound):
- `OPEX_INTERNAL_BEARER_TOKEN` — static bearer for service-to-service
  callers (SERX webhook ingest, OEX webhook ingest, Trigger.dev tasks).
  Validated by `app.deps.require_internal_bearer`.
- `AUX_JWKS_URL`, `AUX_ISSUER`, `AUX_AUDIENCE` — auth-engine-x JWKS config
  used to verify operator-issued EdDSA JWTs on operator-facing routes.
  Validated by `app.deps.get_current_auth` via `app.auth.jwt`.

These four values are **required at startup**. The module raises
`MissingSecretError` on import if any are unset, so the process fails fast
and surfaces config gaps before traffic arrives. Optional outbound creds
remain `None`-tolerant and are validated lazily at the call site that
needs them (see `require()`).

Notes on a few specific fields:
- `mags_api_base_url` + `mags_auth_token` are the outbound credentials this
  service uses to call managed-agents-x's invocation gateway from
  `/events/receive`. Both are required at call time; registered in
  `app.service_registry` under slug `mag`.
- `ANTHROPIC_API_KEY` is **not** held by this project. All Anthropic
  traffic flows through managed-agents-x. Do not add it to this project's
  Doppler config.
"""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        extra="ignore",
    )

    # Inbound auth — required at startup (validated below).
    opex_internal_bearer_token: str | None = None
    aux_jwks_url: str | None = None
    aux_issuer: str | None = None
    aux_audience: str | None = None

    # Database / Supabase — optional at startup, required by code paths that use them.
    opex_supabase_url: str | None = None
    opex_supabase_service_role_key: str | None = None
    opex_supabase_anon_key: str | None = None
    opex_supabase_publishable_key: str | None = None
    opex_supabase_project_ref: str | None = None
    opex_db_url_direct: str | None = None
    opex_db_url_pooled: str | None = None

    # Outbound service credentials. Each downstream service ops-engine-x
    # dispatches to needs a matching pair here and an entry in
    # `app.service_registry`. Slugs currently registered: mag, serx, oex.
    # Outbound auth is still static-bearer; M2M JWT migration is a later phase.
    mags_api_base_url: str | None = None
    mags_auth_token: str | None = None
    serx_api_base_url: str | None = None
    serx_auth_token: str | None = None
    oex_api_base_url: str | None = None
    oex_auth_token: str | None = None


settings = Settings()


class MissingSecretError(RuntimeError):
    """Raised when a secret required by a code path is not configured."""


def require(name: str) -> str:
    """Fetch a required secret by attribute name, raising a clear error if unset.

    Use this at the call site of any feature that genuinely needs the secret,
    e.g. `token = require("mags_auth_token")`. Reserved for outbound creds and
    other lazily-validated secrets; inbound-auth secrets are validated at boot.
    """
    value = getattr(settings, name, None)
    if not value:
        raise MissingSecretError(
            f"Required secret '{name.upper()}' is not set. "
            "Confirm it exists in Doppler (project: ops-engine-x, "
            "config: prd) and that DOPPLER_TOKEN is valid."
        )
    return value


_REQUIRED_AT_STARTUP = (
    "opex_internal_bearer_token",
    "aux_jwks_url",
    "aux_issuer",
    "aux_audience",
)


def _validate_startup_secrets() -> None:
    missing = [name.upper() for name in _REQUIRED_AT_STARTUP if not getattr(settings, name, None)]
    if missing:
        raise MissingSecretError(
            "Required inbound-auth env vars are not set: "
            f"{', '.join(missing)}. Confirm they exist in Doppler "
            "(project: ops-engine-x, config: prd) and DOPPLER_TOKEN is valid."
        )


_validate_startup_secrets()
