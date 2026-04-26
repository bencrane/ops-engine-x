# ops-engine-x

**Operational heartbeat** — the routing, scheduling, and orchestration layer of the platform. Domain services (`serx-api`, `oex-api`, etc.) emit events here; ops-engine-x decides what each event triggers (a managed agent via `managed-agents-x` today; other target kinds plug in via the same registry later) and dispatches.

Deployed to Railway as `api.opsengine.run`. Secrets come from Doppler (project `ops-engine-x`).

## What this service is

- **Event routing** — `POST /events/receive` takes `(source, event_name, event_ref)` from a webhook-ingest app, looks up the row in `event_routes` to resolve an `agent_id`, and forwards the event to `managed-agents-x`'s invocation gateway (`POST /internal/agents/{agent_id}/invoke`).
- **Routing-table admin** — CRUD on `event_routes` for whoever manages the mapping (`GET|PUT|DELETE /event-routes/*`).
- **Scheduled dispatch** — `POST /internal/scheduler/tick` fires cron-driven events from the companion Trigger.dev project; rows live in `scheduled_events`, outcomes in `scheduler_runs`.
- **Health + diagnostics** — `GET /health` (public liveness), `GET /admin/status` (authenticated secret-load + outbound-creds probe).

## What this service is NOT

- **Not the managed-agents product surface.** CRUD on agent definitions, system prompts, versioning, drafts, templates, A/B tests, analytics all live in [`managed-agents-x`](https://api.managedagents.run).
- **Not a source of truth for agent configs.** Anthropic is, and `managed-agents-x` mirrors it. ops-engine-x stores only `agent_id` pointers in `event_routes`.
- **Not the Anthropic API key holder.** `ANTHROPIC_API_KEY` is not in this Doppler and no code here reads it.
- **Not a session creator.** ops-engine-x never calls Anthropic. All session lifecycle happens inside `managed-agents-x`.

## Architecture

- **Runtime**: Python 3.12, FastAPI, uvicorn.
- **Secrets**: Doppler (project `ops-engine-x`, config `prd`) is the single source of truth.
- **Deployment**: Railway builds the `Dockerfile`; the only Railway env var is `DOPPLER_TOKEN`.
- **Secret injection**: the container runs `doppler run -- uvicorn ...`, which fetches and injects all Doppler secrets at process start.

The app boots successfully with zero secrets configured. Any feature that needs a secret reads it lazily via `app.config.require("...")` or a FastAPI `Depends()` factory and fails clearly at call time if missing.

> **For AI agents working in this repo:** read [`AGENTS.md`](AGENTS.md) and [`HANDOFF.md`](HANDOFF.md) first. They codify the scope boundary and the secret-handling conventions.

## Secret contract

The canonical list of secrets lives in [`app/config.py`](app/config.py). No `.env` or `.env.example` is maintained in this repo — Doppler is the source of truth.

| Name | Required | Notes |
| ---- | -------- | ----- |
| `AUX_JWKS_URL` | required (boot) | JWKS endpoint of `auth-engine-x`. Used by `aux_m2m_server` to verify EdDSA JWTs (both operator session JWTs and M2M JWTs). Inherited from the `shared-services` Doppler base. |
| `AUX_ISSUER` | required (boot) | Expected `iss` claim on inbound JWTs. Inherited from `shared-services`. |
| `AUX_AUDIENCE` | required (boot) | Expected `aud` claim on inbound JWTs. Inherited from `shared-services`. |
| `AUX_API_BASE_URL` | required (boot) | `auth-engine-x` base URL. Used by `aux_m2m_client` to mint M2M JWTs for outbound calls. Inherited from `shared-services`. |
| `AUX_M2M_API_KEY` | required (boot) | This backend's own M2M API key (its identity in `auth-engine-x`). Caller-side credential for outbound calls to MAGS/SERX/OEX. **Specific to ops-engine-x** — not shared. |
| `OPEX_DB_URL_POOLED` | required (when DB code paths run) | Postgres DSN backing `event_routes`, `scheduled_events`, `scheduler_runs`. |
| `OPEX_DB_URL_DIRECT` | optional (reserved) | Direct Postgres connection string. Reserved for future migration scripts. |
| `MAGS_API_BASE_URL` | outbound | Base URL for `managed-agents-x` (e.g. `https://api.managedagents.run`). Required for `/events/receive` to dispatch to agent targets. |
| `SERX_API_BASE_URL` | outbound | Base URL for serx-api. Required whenever a `scheduled_events` row has `target_service='serx'`. |
| `OEX_API_BASE_URL` | outbound | Base URL for oex-api (e.g. `https://api.outboundengine.dev`). Required whenever a `scheduled_events` row has `target_service='oex'`. |
| `OPEX_SUPABASE_URL` | optional | Reserved for future use. |
| `OPEX_SUPABASE_SERVICE_ROLE_KEY` | optional | Reserved. |
| `OPEX_SUPABASE_ANON_KEY` | optional | Reserved. |
| `OPEX_SUPABASE_PROJECT_REF` | optional | Supabase project ref slug. |

Deliberately **not** in this project's Doppler:

- `OPEX_INTERNAL_BEARER_TOKEN` / `OPEX_AUTH_TOKEN` — **removed** during the M2M migration. Internal callers (SERX/OEX webhook ingest, Trigger.dev tasks) now mint short-lived EdDSA M2M JWTs via `auth-engine-x` instead of presenting a static shared secret.
- `MAGS_AUTH_TOKEN` / `SERX_INTERNAL_BEARER_TOKEN` / `OEX_AUTH_TOKEN` — **removed**. Outbound calls (ops-engine-x → MAGS/SERX/OEX) use `aux_m2m_client.M2MAuth` with `AUX_M2M_API_KEY`, not service-specific bearers.
- `ANTHROPIC_API_KEY` — held only by `managed-agents-x`. All Anthropic traffic flows through that service.

## Local development

Install the Doppler CLI once:

```bash
brew install dopplerhq/cli/doppler
doppler login
```

This directory is scoped to Doppler project `ops-engine-x`, config `prd` (see `doppler configure --all`). Your shell may, however, inherit `DOPPLER_TOKEN` / `DOPPLER_PROJECT` / `DOPPLER_CONFIG` / `DOPPLER_ENVIRONMENT` from a home-directory default (e.g. `sfdc-engine-x`). Those env vars override the per-directory scope, so a naive `doppler run` from this repo would silently hit the wrong project. Two ways to deal with it — pick one:

**Option A — use the wrapper (zero install, recommended):**

```bash
./scripts/doppler run -- uvicorn app.main:app --reload --port 8080
./scripts/doppler secrets
```

The wrapper strips the four shadowing env vars before exec'ing `doppler`.

**Option B — use direnv (auto-strips on `cd`):**

```bash
brew install direnv
echo 'eval "$(direnv hook zsh)"' >> ~/.zshrc  # or bash/fish equivalent
direnv allow .
# Now `doppler run -- ...` works directly inside this directory.
```

`.envrc` is already in the repo; it's inert if direnv isn't installed.

Install Python deps and run:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
./scripts/doppler run -- uvicorn app.main:app --reload --port 8080
```

Smoke test:

```bash
curl localhost:8080/health           # {"status":"ok"}
curl localhost:8080/                 # {"service":"ops-engine-x","status":"ok"}
curl -H "Authorization: Bearer $OPERATOR_JWT" localhost:8080/admin/status
# → secrets_loaded: {aux_jwks_url, aux_issuer, aux_audience, aux_api_base_url,
#                    aux_m2m_api_key, opex_db_url_pooled}
# → outbound_services: {mag, serx, oex} each reporting base-URL presence.
#
# /admin/status requires an operator session JWT from auth-engine-x.
# /events/receive and /internal/scheduler/tick require an M2M JWT (also
# from auth-engine-x); both verified by aux_m2m_server against the same
# JWKS endpoint.
```

## Railway deployment

1. Connect the GitHub repo to a Railway service.
2. In Doppler, generate a service token for the `ops-engine-x` project, `prd` config.
3. In Railway → Variables, set a single variable: `DOPPLER_TOKEN` = (that token).
4. Deploy. Railway builds the Dockerfile and runs the entrypoint.

`railway.toml` configures the Dockerfile build, `/health` healthcheck, and `on_failure` restart policy.

## Adding a new secret

1. Add it to the Doppler `prd` config of the `ops-engine-x` project.
2. Add a typed field to `Settings` in `app/config.py`.
3. At the call site that needs it, use `require("new_secret_name")` (or a FastAPI `Depends()` factory — see `AGENTS.md`).
4. Add a row to the secrets table above.
5. Redeploy (Railway will pick up the new value on next boot via `doppler run --`).

---

_Last updated: 2026-04-25 (M2M cutover — replaced static bearers with EdDSA M2M JWTs minted by `auth-engine-x`)._
