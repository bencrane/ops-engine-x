# Trigger.dev — ops-engine-x scheduled events

This directory holds the Trigger.dev task definitions for the `ops-engine-x`
Trigger.dev project (`proj_dkjfnsdgwksztgjlqzlr`). **Every task is identical
in shape**: it fires on cron and tells ops-engine-x to dispatch a named
event. All routing (which target service, which path) is resolved
server-side by ops-engine-x through its `scheduled_events` registry.

Trigger.dev never calls a target service directly. It never holds a target
service's credentials. Adding a new scheduled event never requires adding
a new environment variable here.

## Architecture

```
  Trigger.dev (cloud)                   ops-engine-x                            target service
  ───────────────────                   ─────────────────────                   ────────────────
  <event_id>-task                       POST /internal/scheduler/tick           POST <target_path>
  cron fires             ─POST─────▶    {event_id, trigger_run_id}   ─POST──▶   Bearer <M2M JWT>
  Bearer <M2M JWT>                      • lookup scheduled_events                <work>
                                        • resolve target_service                 ─outcome─▶
                                        • POST target (M2MAuth)
                                        • insert scheduler_runs
                         ◀─TickResult─  ←───────summary────────────────────────
```

Both hops are M2M-authenticated against `auth-engine-x`'s JWKS:

- **Trigger.dev → ops-engine-x.** The Trigger.dev project mints its own
  short-lived M2M JWT via `auth-engine-x` (helper: [`lib/m2m.ts`](./lib/m2m.ts))
  and presents it on `/internal/scheduler/tick`.
- **ops-engine-x → target service.** ops-engine-x mints its own M2M JWT
  via `aux_m2m_client.M2MAuth` and presents it on the target route.

Static bearer tokens (`OPEX_AUTH_TOKEN`, `SERX_AUTH_TOKEN`, etc.) have
been removed end-to-end.

Key properties:

- **One source of truth for routing.** `scheduled_events` (in ops-engine-x's Supabase) maps `event_id → (target_service, target_path, http_method, enabled)`. Operators can disable, re-point, or switch a schedule between GET/POST with a SQL update; no Trigger.dev redeploy required. `http_method` defaults to `POST` (the right default for side-effectful scheduled work); use `GET` for polling / reachability-probe style events.
- **Target-service base URLs never leave ops-engine-x.** `SERX_API_BASE_URL` and its siblings live in ops-engine-x's Doppler. Adding a new target service = one row in `app/service_registry.py` + one base-URL secret in Doppler. No bearer secrets to manage anywhere.
- **ops-engine-x owns the run log.** Every dispatch (success or failure) appends a row to `scheduler_runs` in-process. No extra HTTP call, no best-effort fallback.
- **Trigger.dev is pure timing.** Each task = `id + cron + fireScheduledEvent(id, ctx.run.id)`. Nothing else.

## Key files

| File | Role |
|---|---|
| [`../../trigger.config.ts`](../../trigger.config.ts) | Trigger.dev project config (project id, runtime, retries, task dir) |
| [`lib/m2m.ts`](./lib/m2m.ts) | TS-side M2M JWT minter — fetches a short-lived EdDSA JWT from `auth-engine-x`, caches it in-process, refreshes ~30s before expiry. |
| [`lib/fire-scheduled-event.ts`](./lib/fire-scheduled-event.ts) | Reusable helper every task calls. Mints an M2M JWT via `lib/m2m.ts`, POSTs to ops-engine-x's tick endpoint, throws on dispatcher or target failures so Trigger.dev marks the run errored. |
| [`serx-dispatch-due-preframes.ts`](./serx-dispatch-due-preframes.ts) | First production task. Cron `0 */6 * * *`. Fires event `serx.dispatch_due_preframes`. |
| [`oex-auth-me-probe.ts`](./oex-auth-me-probe.ts) | Daily reachability probe targeting oex-api `/api/auth/me`. |

Server-side (ops-engine-x):

| File | Role |
|---|---|
| [`../../app/scheduled_events.py`](../../app/scheduled_events.py) | CRUD on the `scheduled_events` registry |
| [`../../app/scheduler_runs.py`](../../app/scheduler_runs.py) | CRUD on the `scheduler_runs` log |
| [`../../app/service_registry.py`](../../app/service_registry.py) | Slug (`mag`, `serx`, `oex`) → base-URL env var. Auth is uniform M2M. |
| [`../../app/main.py`](../../app/main.py) | `POST /internal/scheduler/tick` dispatcher (M2M-guarded); `GET\|PUT\|DELETE /scheduled-events/*` CRUD; `GET /internal/scheduler/runs` inspection |

Supabase migrations (applied via Supabase MCP):

- `create_scheduler_runs` — append-only run log.
- `create_scheduled_events` — event registry.

## Environment variables

### Trigger.dev dashboard (per environment: dev / staging / prod)

| Variable | Purpose |
|---|---|
| `OPEX_API_URL` | Base URL of ops-engine-x, e.g. `https://api.opsengine.run`. |
| `AUX_API_BASE_URL` | `auth-engine-x` base URL — used by `lib/m2m.ts` to mint M2M JWTs. |
| `AUX_M2M_API_KEY` | This Trigger.dev project's M2M API key. Identity in `auth-engine-x`. |

`OPEX_AUTH_TOKEN` is **gone**. Every Trigger.dev → ops-engine-x request
mints a fresh M2M JWT.

### ops-engine-x Doppler (`ops-engine-x/prd`)

Outbound base URLs live here. The dispatcher reads them through
`app/service_registry.py`. Auth on outbound calls is uniform M2M
(`aux_m2m_client.M2MAuth` using `AUX_M2M_API_KEY`); there are no
per-service bearer secrets.

| Variable | Purpose |
|---|---|
| `MAGS_API_BASE_URL` | e.g. `https://api.managedagents.run` |
| `SERX_API_BASE_URL` | e.g. `https://api.serviceengine.xyz` |
| `OEX_API_BASE_URL`  | e.g. `https://api.outboundengine.dev` |

## Registering a new scheduled event

1. Pick an `event_id`, format `<service>.<verb_noun>` — e.g. `oex.sweep_stale_suppressions`.
2. `PUT /scheduled-events/{event_id}` with `{target_service, target_path, cron?, description?, enabled}`.
3. Create a Trigger.dev task file (~15 lines) in this directory whose `id` matches the `event_id` and whose `run:` calls `fireScheduledEvent("<event_id>", ctx.run.id)`.
4. `npx trigger.dev@latest deploy`.

If the target service is new, first add it to `app/service_registry.py`
and add its base-URL secret (`<SLUG>_API_BASE_URL`) to ops-engine-x's
Doppler. Redeploy ops-engine-x once, never again for that service. The
target service must accept M2M JWTs from this backend's identity (i.e.
its routes are guarded by `aux_m2m_server.require_m2m`).

## Cron cadence

Each task owns its cron. Keep the cron string in a named constant at the
top of the task file (see `CRON_EVERY_6_HOURS` in
`serx-dispatch-due-preframes.ts`). The `scheduled_events.cron` column is
**informational only** — Trigger.dev is the actual scheduler and the task
file is canonical. The column exists for operator inspection and drift
audits.

Idempotency of overlapping ticks is owned by the target service.

## Deploying & local dev

```bash
npx trigger.dev@latest deploy
npx trigger.dev@latest dev  # local iteration
```

Env vars during `dev` come from your shell / Trigger.dev's dev env — not
from Doppler.

## Inspecting runs

Via HTTP (note: `/internal/scheduler/runs` is operator-gated, not M2M):

```bash
# recent runs, any event
curl -H "Authorization: Bearer $OPERATOR_JWT" \
  "https://api.opsengine.run/internal/scheduler/runs?limit=20"

# last 10 failures of the serx preframe dispatcher
curl -H "Authorization: Bearer $OPERATOR_JWT" \
  "https://api.opsengine.run/internal/scheduler/runs?task_id=serx.dispatch_due_preframes&ok=false&limit=10"
```

Or query `public.scheduler_runs` directly in Supabase. Trigger.dev's own
dashboard still shows the canonical run log with stdout/stack traces;
`scheduler_runs` is the SQL-queryable summary for ops/observability.

---

_Last updated: 2026-04-25 (M2M cutover — Trigger.dev → ops-engine-x and ops-engine-x → targets both mint short-lived EdDSA JWTs; `OPEX_AUTH_TOKEN` and per-service bearers removed)._
