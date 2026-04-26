# AGENTS.md

Instructions for AI coding agents working in this repository. Read this, [`README.md`](README.md), and [`HANDOFF.md`](HANDOFF.md) before writing code.

## Project shape

- Python 3.12, FastAPI, uvicorn.
- Deployed to Railway from the `Dockerfile` as `api.opsengine.run`.
- Secrets come from **Doppler only** (project `ops-engine-x`, config `prd`). Railway has exactly one environment variable: `DOPPLER_TOKEN`. The container entrypoint runs `doppler run -- uvicorn ...`, which fetches secrets and injects them into the process env before Python starts.
- There is no `.env` or `.env.example` in this repo, and you must not add one. The canonical list of secrets is `app/config.py` + the table in `README.md`.

## Scope rule (read HANDOFF.md first)

This service is **operational plumbing** — event routing, scheduled-job dispatch, inbox watchers, workflow orchestration. It is NOT the managed-agents product surface.

If a feature touches agent authoring, versioning, editing, drafts, templates, A/B tests, analytics, or the Anthropic API directly → it belongs in [`managed-agents-x`](https://api.managedagents.run), not here.

**Concrete consequences:**
- Do NOT add `ANTHROPIC_API_KEY` to this project's Doppler config.
- Do NOT add code that calls Anthropic. All Anthropic traffic flows through managed-agents-x.
- Do NOT add code that stores per-agent invocation state (environment_id, vault_ids, task_instruction, system prompt). That's managed-agents-x's `agent_defaults` concern.
- `event_routes` in this DB stores only `agent_id` pointers — never agent content.

## Auth rule

All inbound auth is verified against `auth-engine-x`'s JWKS via the shared
[`aux_m2m_server`](https://github.com/bencrane/aux-m2m-client-py) library.
Two flavours, two FastAPI deps — pick the right one for the caller:

- **Service-to-service callers** (SERX/OEX webhook ingest, Trigger.dev tasks)
  present a short-lived M2M JWT and use `require_m2m`.
- **Operator-facing routes** (admin status, event-route CRUD, scheduled-event
  CRUD, scheduler-runs query) require an EdDSA session JWT verified via
  `require_session`.

```python
from fastapi import Depends
from aux_m2m_server import require_m2m, require_session

@app.post("/internal/whatever", dependencies=[Depends(require_m2m)])
def internal_whatever(...): ...

@app.get("/admin/whatever", dependencies=[Depends(require_session)])
def admin_whatever(...): ...
```

Public routes are limited to `GET /health` and `GET /` (minimal identity).
Everything else is gated. **Never** add a static-bearer dep — there is no
`OPEX_INTERNAL_BEARER_TOKEN` / `OPEX_AUTH_TOKEN` anymore.

Outbound auth is uniform: every call to another AUX backend mints a fresh
M2M JWT via `aux_m2m_client.M2MAuth` using `AUX_M2M_API_KEY`. There are no
per-callee bearers (no `MAGS_AUTH_TOKEN`, no `SERX_AUTH_TOKEN`). Each
registered outbound service lives in [`app/service_registry.py`](app/service_registry.py)
as `(slug, base_url_env)` only.

## Rule 1: Two-tier secret contract — boot-required vs lazy

There are exactly **two tiers** of secrets in this project:

**Tier 1 — boot-required (`BaseAuthSettings`).** The five AUX_* env vars
(`AUX_JWKS_URL`, `AUX_ISSUER`, `AUX_AUDIENCE`, `AUX_API_BASE_URL`,
`AUX_M2M_API_KEY`) are required at process start. Pydantic raises
`ValidationError` if any is missing — that's intentional. The process
**should** fail to boot with a clear traceback rather than 503-ing every
authenticated request.

**Tier 2 — lazy/optional.** Everything else — DB DSNs, outbound base URLs,
reserved Supabase keys — is `str | None` on `Settings` and validated at
the call site that needs it (via `require()` or a `Depends()` factory).
`/health` must stay green even when these are unset.

Practical consequences:

- Tier-1 fields (the AUX_* set) live on `BaseAuthSettings` upstream — do
  not redeclare them in this repo's `Settings`. Inherit; don't shadow.
- Tier-2 fields must have a default (`None` for secrets, a safe default
  for non-secrets) so `Settings()` does not raise on their absence.
- Do **not** read tier-2 secrets at import time or at module load.
- Do **not** construct API clients that require tier-2 secrets as
  module-level globals.
- Tier-1 clients (`M2MTokenClient`, `M2MAuth`) **may** be module-level
  globals — they're guaranteed by tier-1 boot validation.

## Rule 2: Use lazy, validated reads for every required secret

**Never read a required secret via `settings.<name>` directly in production code paths.** Direct reads give you `None` silently and fail with a cryptic `NoneType` or downstream 401. Use one of the two patterns below so the failure mode is always a loud, Doppler-pointing error.

### Pattern A — FastAPI routes: `Depends()` factory (preferred for HTTP handlers)

For anything reached via an HTTP route, use a FastAPI dependency. This gives you a proper `503 Service Unavailable` with a clear message, and it's trivially overridable in tests. Pattern for a new secret-backed client:

```python
# app/deps.py
from fastapi import HTTPException
from app.config import settings

def get_some_client() -> SomeClient:
    if not settings.some_api_key:
        raise HTTPException(
            status_code=503,
            detail="SOME_API_KEY not configured (check Doppler prd).",
        )
    return SomeClient(api_key=settings.some_api_key)
```

### Pattern B — Everywhere else: `require()`

For non-route code paths — background workers, startup tasks, CLI entrypoints, library-style modules — use the `require()` helper from `app/config.py`. It raises `MissingSecretError` with a Doppler-pointing message.

```python
from app.config import require

def do_thing():
    token = require("some_secret")
    ...
```

### Do not do any of these

```python
from app.config import settings
client = SomeClient(key=settings.some_api_key)   # silent None, cryptic failure later

_client = SomeClient(key=settings.some_api_key)  # module-level, breaks boot tolerance

key = os.environ["SOME_API_KEY"]                 # bypasses the contract, KeyError at import
```

### Optional / best-effort reads

If a secret is genuinely optional (the feature degrades gracefully when it's absent), read it directly from `settings` and branch on truthiness:

```python
from app.config import settings

if settings.some_optional_webhook_url:
    post_webhook(settings.some_optional_webhook_url, payload)
```

Reserve `Depends()` / `require()` for secrets whose absence should be a hard error at call time.

## Rule 3: Adding a new secret

Every new secret must be added in three places, in this order:

1. **Doppler**: add the variable to the `prd` config of the `ops-engine-x` project. The human operator does this; mention it in your PR description so they know.
2. **`app/config.py`**: add a typed, optional field to `Settings` using lowercase snake_case. pydantic-settings maps it to the uppercase env var automatically (case-insensitive).
3. **`README.md`**: add a row to the secrets table (name, required/optional, notes).

Then read it with `require("your_new_secret")` at the call site.

Do **not**:

- Add it to a `.env.example` (there isn't one, and there shouldn't be).
- Set it in `railway.toml` or Railway's variables UI. `DOPPLER_TOKEN` is the only Railway variable, ever.
- Add `ANTHROPIC_API_KEY` — that secret lives in managed-agents-x's Doppler, not here.

## Rule 4: Don't touch the Doppler injection path

The following files implement the "Doppler is the only source of secrets" contract. Change them only with an explicit reason:

- `Dockerfile` — installs the Doppler CLI; must stay installed.
- `docker-entrypoint.sh` — runs `doppler run --` when `DOPPLER_TOKEN` is set, falls back to plain `uvicorn` otherwise so the container always boots. Do not remove the fallback; it is what lets `docker run` work locally without a token and preserves boot tolerance.
- `railway.toml` — Dockerfile builder + `/health` healthcheck. Do not switch to Nixpacks or move secrets into Railway variables.

## Rule 5: Verifying your change

Before opening a PR that touches config or a new integration:

1. Build and run the container with **no** env vars:
   ```bash
   docker build -t ops-engine-x:test .
   docker run --rm -p 8088:8080 ops-engine-x:test
   curl -f localhost:8088/health
   ```
   `/health` must return 200. The entrypoint will log that `DOPPLER_TOKEN` is not set; that is expected.

2. Hit `/` — it returns minimal identity info and must be 200.

3. With Doppler secrets injected locally, hit `GET /admin/status` with an operator session JWT (issued by `auth-engine-x`). It returns a `secrets_loaded` map showing which configured secrets are present.

4. If your change adds a route that calls a secret-backed service, verify that hitting it without the secret returns a clear `MissingSecretError` (500 with a readable message), not a `NoneType` traceback or a 401 from the upstream.

## Rule 6: Keep `/health` dumb

`/health` is the Railway healthcheck target. It must:

- Return 200 quickly.
- Not depend on any external service (no DB ping, no upstream call, no Doppler check).

Diagnostics that depend on secrets belong on `GET /admin/status` (authenticated). Readiness checks that depend on the DB belong on a new `/ready` if/when we need one.

---

_Last updated: 2026-04-25 (M2M cutover — replaced static bearers with EdDSA M2M JWTs minted by `auth-engine-x`; added two-tier secret contract)._
