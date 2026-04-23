# ops-engine-x

**Operational heartbeat** — the routing, scheduling, and orchestration layer of the platform. Domain services (serx-api, oex-api, etc.) emit events here; ops-engine-x decides what each event triggers (a managed agent today, a managed-agents-x-api invocation or a raw HTTP call later) and dispatches.

Deployed to Railway as `api.opsengine.run`. Secrets come from Doppler (project `ops-engine-x`).

## What this service is

- **Event routing** — `POST /sessions/from-event` takes `(source, event_name, event_ref)` from a webhook-ingest app, looks up the route in the `event_routes` table, and dispatches.
- **Routing-table admin** — CRUD on `event_routes` for whoever manages the mapping (`GET|PUT|DELETE /event-routes/*`).
- **Health + diagnostics** — `GET /health` (public liveness), `GET /admin/status` (authenticated secret-load probe).

## What this service is NOT

- Not a managed-agents product surface. CRUD on agent definitions, system prompts, versioning, drafts, templates, A/B tests, analytics — all of that belongs in the future `managed-agents-x-api` repo.
- Not a source of truth for agent configs. Anthropic is. ops-engine-x stores only pointers (`agent_id` strings) in its routing table.
- Not the Anthropic API key holder. **`ANTHROPIC_API_KEY` is not expected in this project's Doppler.**

Some route handlers in `app/main.py` (`/agents*`, `/agents/*/defaults`, `/admin/sync/anthropic`) and their supporting modules (`app/anthropic_client.py`, `app/sync.py`, `app/agent_defaults.py`, `scripts/setup_orchestrator.py`) are preserved verbatim for extraction into `managed-agents-x-api`. They will fail at call time without `ANTHROPIC_API_KEY` — that is the intended state. See `HANDOFF.md` for the full extraction plan.

## Architecture

- **Runtime**: Python 3.12, FastAPI, uvicorn
- **Secrets**: Doppler (project `ops-engine-x`, config `prd`) is the single source of truth
- **Deployment**: Railway builds the `Dockerfile`; the only Railway env var is `DOPPLER_TOKEN`
- **Secret injection**: the container runs `doppler run -- uvicorn ...`, which fetches and injects all Doppler secrets at process start

The app is designed to boot successfully even with zero secrets configured. Any feature that needs a secret reads it lazily via `app.config.require("...")` and fails clearly at call time if the secret is missing.

> **For AI agents working in this repo:** read [`AGENTS.md`](AGENTS.md) and [`HANDOFF.md`](HANDOFF.md) first. They codify the scope boundary, secret-handling conventions, and the "preserved for extraction" freeze on managed-agents code paths.

## Secret contract

The canonical list of secrets lives in [`app/config.py`](app/config.py). No `.env` or `.env.example` is maintained in this repo — Doppler is the source of truth.

Secrets this project **does** expect:

| Name | Required | Notes |
| ---- | -------- | ----- |
| `OPEX_AUTH_TOKEN` | required | Inbound bearer token domain services present when calling this service. Gates every non-public route. |
| `SUPABASE_DB_URL` | required | Postgres connection string backing `event_routes` (and the preserved-for-extraction `agent_defaults`). |
| `SERX_API_URL` | outbound | Base URL for serx-api. Required whenever a `scheduled_events` row has `target_service='serx'`. |
| `SERX_AUTH_TOKEN` | outbound | Bearer token ops-engine-x presents when calling serx-api. Paired with `SERX_API_URL`. |
| `OEX_API_URL` | outbound | Base URL for oex-api (e.g. `https://api.outboundengine.dev`). Required whenever a `scheduled_events` row has `target_service='oex'`. |
| `OEX_AUTH_TOKEN` | outbound | Bearer token ops-engine-x presents when calling oex-api. Paired with `OEX_API_URL`. |
| `SUPABASE_URL` | optional | Reserved for future use. |
| `SUPABASE_SERVICE_ROLE_KEY` | optional | Reserved. |
| `SUPABASE_ANON_KEY` | optional | Reserved. |
| `SUPABASE_PROJECT_REF` | optional | Supabase project ref slug. |

Secrets this project **does NOT expect** (deliberate):

- `ANTHROPIC_API_KEY` — lives in the future `managed-agents-x-api` Doppler config, not here.
- Any outbound service-to-service token (e.g. `MAG_AUTH_TOKEN`) — will be added when ops-engine-x has a reason to call that service. None today.

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
curl -H "Authorization: Bearer $OPEX_AUTH_TOKEN" localhost:8080/admin/status
# → secrets_loaded: {opex_auth_token: true, supabase_db_url: true}
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
