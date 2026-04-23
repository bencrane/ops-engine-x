# Trigger.dev — ops-engine-x scheduled events

This directory holds the Trigger.dev task definitions for the `ops-engine-x`
Trigger.dev project (`proj_dkjfnsdgwksztgjlqzlr`). **Every task is identical
in shape**: it fires on cron and tells ops-engine-x to dispatch a named
event. All routing (which target service, which path, which bearer token)
is resolved server-side by ops-engine-x through its `scheduled_events`
registry.

Trigger.dev never calls a target service directly. It never holds a target
service's bearer token. Adding a new scheduled event never requires adding
a new environment variable here.

## Architecture

```
  Trigger.dev (cloud)                   ops-engine-x                            target service
  ───────────────────                   ─────────────────────                   ────────────────
  <event_id>-task                       POST /internal/scheduler/tick           POST <target_path>
  cron fires             ─POST─────▶    {event_id, trigger_run_id}   ─POST──▶   Bearer ${svc_token}
                                        • lookup scheduled_events                <work>
                                        • resolve target_service                 ─outcome─▶
                                        • POST target
                                        • insert scheduler_runs
                         ◀─TickResult─  ←───────summary────────────────────────
```

Key properties:

- **One source of truth for routing.** `scheduled_events` (in ops-engine-x's Supabase) maps `event_id → (target_service, target_path, enabled)`. Operators can disable or re-point a schedule with a SQL update; no Trigger.dev redeploy required.
- **Target-service credentials never leave ops-engine-x.** `SERX_AUTH_TOKEN`, `SERX_API_BASE_URL`, and their future siblings live in ops-engine-x's Doppler. Adding a new target service = one row in `app/service_registry.py` + two secrets in Doppler.
- **ops-engine-x owns the run log.** Every dispatch (success or failure) appends a row to `scheduler_runs` in-process. No extra HTTP call, no best-effort fallback.
- **Trigger.dev is pure timing.** Each task = `id + cron + fireScheduledEvent(id, ctx.run.id)`. Nothing else.

## Key files

| File | Role |
|---|---|
| [`../../trigger.config.ts`](../../trigger.config.ts) | Trigger.dev project config (project id, runtime, retries, task dir) |
| [`lib/fire-scheduled-event.ts`](./lib/fire-scheduled-event.ts) | Reusable helper every task calls. POSTs to ops-engine-x's tick endpoint, throws on dispatcher or target failures so Trigger.dev marks the run errored. |
| [`serx-dispatch-due-preframes.ts`](./serx-dispatch-due-preframes.ts) | First production task. Cron `0 */6 * * *`. Fires event `serx.dispatch_due_preframes`. |

Server-side (ops-engine-x):

| File | Role |
|---|---|
| [`../../app/scheduled_events.py`](../../app/scheduled_events.py) | CRUD on the `scheduled_events` registry |
| [`../../app/scheduler_runs.py`](../../app/scheduler_runs.py) | CRUD on the `scheduler_runs` log |
| [`../../app/service_registry.py`](../../app/service_registry.py) | Slug (`serx`, future `oex`) → (base URL env var, auth token env var) |
| [`../../app/main.py`](../../app/main.py) | `POST /internal/scheduler/tick` dispatcher; `GET|PUT|DELETE /scheduled-events/*` CRUD; `GET /internal/scheduler/runs` inspection |

Supabase migrations (applied via Supabase MCP):

- `create_scheduler_runs` — append-only run log.
- `create_scheduled_events` — event registry.

## Environment variables

### Trigger.dev dashboard (per environment: dev / staging / prod)

Only two. Target-service credentials do NOT live here anymore.

| Variable | Purpose |
|---|---|
| `OPEX_API_URL` | Base URL of ops-engine-x, e.g. `https://api.opsengine.run`. |
| `OPEX_AUTH_TOKEN` | Bearer matching `OPEX_AUTH_TOKEN` in `ops-engine-x/prd` Doppler. |

### ops-engine-x Doppler (`ops-engine-x/prd`)

Target-service credentials live here. The dispatcher reads them through
`app/service_registry.py`.

| Variable | Purpose |
|---|---|
| `SERX_API_BASE_URL` | e.g. `https://api.serviceengine.xyz` |
| `SERX_AUTH_TOKEN` | serx-api's inbound bearer |

Future targets (`oex`, etc.) follow the same `<SLUG>_API_BASE_URL` /
`<SLUG>_AUTH_TOKEN` pattern.

## Registering a new scheduled event

1. Pick an `event_id`, format `<service>.<verb_noun>` — e.g. `oex.sweep_stale_suppressions`.
2. `PUT /scheduled-events/{event_id}` with `{target_service, target_path, cron?, description?, enabled}`.
3. Create a Trigger.dev task file (~15 lines) in this directory whose `id` matches the `event_id` and whose `run:` calls `fireScheduledEvent("<event_id>", ctx.run.id)`.
4. `npx trigger.dev@latest deploy`.

If the target service is new, first add it to `app/service_registry.py` and
add its two secrets (`<SLUG>_API_BASE_URL`, `<SLUG>_AUTH_TOKEN`) to
ops-engine-x's Doppler. Redeploy ops-engine-x once, never again for that
service.

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

Via HTTP:

```bash
# recent runs, any event
curl -H "Authorization: Bearer $OPEX_AUTH_TOKEN" \
  "https://api.opsengine.run/internal/scheduler/runs?limit=20"

# last 10 failures of the serx preframe dispatcher
curl -H "Authorization: Bearer $OPEX_AUTH_TOKEN" \
  "https://api.opsengine.run/internal/scheduler/runs?task_id=serx.dispatch_due_preframes&ok=false&limit=10"
```

Or query `public.scheduler_runs` directly in Supabase. Trigger.dev's own
dashboard still shows the canonical run log with stdout/stack traces;
`scheduler_runs` is the SQL-queryable summary for ops/observability.
