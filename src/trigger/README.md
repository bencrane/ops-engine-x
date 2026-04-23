# Trigger.dev — ops-engine-x scheduled jobs

This directory holds the Trigger.dev task definitions for the `ops-engine-x`
Trigger.dev project (`proj_dkjfnsdgwksztgjlqzlr`). The project is a
**multi-service scheduling umbrella**: individual tasks dispatch ticks to
whichever backend service owns the scheduled concern (serx-api today, oex-api
or ops-engine-x itself tomorrow). Trigger.dev stays dumb — it fires on cron,
POSTs, and logs. All business logic lives in the target service.

## Architecture

```
  Trigger.dev (cloud)                 Target backend                     ops-engine-x
  ─────────────────────               ───────────────────                 ───────────────
  <x>-scheduler-tick                  /internal/scheduler/<job>           /internal/scheduler/runs
  every <cron>           ─POST───▶    <service-specific work>  ─ok/err─▶  insert scheduler_runs row
                                      Bearer ${X_AUTH_TOKEN}              Bearer ${OPEX_AUTH_TOKEN}
```

- Each task POSTs `{}` to one internal endpoint on one backend service, with
  that service's bearer token.
- After the work POST returns (or errors), the task POSTs the outcome to
  `${OPEX_API_URL}/internal/scheduler/runs` with `OPEX_AUTH_TOKEN`.
  ops-engine-x appends one row to `public.scheduler_runs` per run.
- Adding a new scheduled event type within an existing target (e.g. a new
  variety of SERX-owned reminder) does **not** require a new Trigger.dev
  task. It only requires appending a new `EventConfig` in that service's
  dispatcher. The tick URL stays the same.
- Adding a scheduled job for a *new* target service (e.g. oex-api nightly
  sweep) = one new `*-scheduler-tick.ts` file in this dir + two new env
  vars (`<SERVICE>_API_URL`, `<SERVICE>_AUTH_TOKEN`) in the Trigger.dev
  dashboard. The helper below does the rest.

## Key files

| File | Role |
|---|---|
| [`../../trigger.config.ts`](../../trigger.config.ts) | Project config (project id, runtime, retries, task dir) |
| [`lib/tick-and-log.ts`](./lib/tick-and-log.ts) | Reusable helper. Every task calls `tickAndLog({...})` — it handles the work POST, truncates the response body to 8KB, logs the outcome to ops-engine-x, and throws on non-2xx so Trigger.dev marks the run as errored. |
| [`serx-scheduler-tick.ts`](./serx-scheduler-tick.ts) | The first production task. Cron `0 */6 * * *`. POSTs to `${SERX_API_URL}/api/internal/scheduler/dispatch-due-preframes`. |

Server-side (ops-engine-x):

| File | Role |
|---|---|
| [`../../app/main.py`](../../app/main.py) | `POST /internal/scheduler/runs` (insert) and `GET /internal/scheduler/runs` (list) |
| [`../../app/scheduler_runs.py`](../../app/scheduler_runs.py) | `scheduler_runs` table CRUD |

Supabase table `public.scheduler_runs` was created via the Supabase MCP
migration `create_scheduler_runs` (2026-04-23).

## Environment variables (Trigger.dev dashboard)

Set these in **Trigger.dev → Project → Environment variables**, per
environment (dev / staging / prod). The task runtime runs on Trigger.dev's
cloud and does not have access to your Doppler secrets — so Doppler is not
the source of truth here.

| Variable | Purpose |
|---|---|
| `OPEX_API_URL` | Base URL of ops-engine-x, e.g. `https://api.opsengine.run`. No trailing slash required. |
| `OPEX_AUTH_TOKEN` | Bearer token for ops-engine-x. Must match `OPEX_AUTH_TOKEN` in the `ops-engine-x/prd` Doppler config. |
| `SERX_API_URL` | Base URL of serx-api, e.g. `https://api.serviceengine.xyz`. No trailing slash required. |
| `SERX_AUTH_TOKEN` | Bearer token for serx-api's internal scheduler endpoint. |

Adding a new target service → add `<X>_API_URL` + `<X>_AUTH_TOKEN` to this
list and consume them in the new task file via `process.env`.

## Cron cadence

Each task owns its cron. Keep the cron string in a named constant at the
top of the task file (see `CRON_EVERY_6_HOURS` in `serx-scheduler-tick.ts`)
rather than inlining. Idempotency is owned server-side by the target
service — overlapping ticks are safe as long as the target protects
against duplicate dispatch (SERX uses a DB uniqueness index; other targets
should do the same before tightening cadence).

## Deploying

Trigger.dev deploys are out-of-band from Railway:

```bash
npx trigger.dev@latest deploy
```

Env vars are managed via the Trigger.dev dashboard or `npx trigger.dev env`.
Local iteration:

```bash
npx trigger.dev@latest dev
```

During `dev`, `process.env` values come from your shell / Trigger.dev's dev
environment — not from Doppler. See the Trigger.dev docs for how to seed
local-dev env vars.

## Inspecting runs

Query `public.scheduler_runs` via Supabase, or:

```bash
# recent runs, any task
curl -H "Authorization: Bearer $OPEX_AUTH_TOKEN" \
  "https://api.opsengine.run/internal/scheduler/runs?limit=20"

# last 10 failures of the serx tick
curl -H "Authorization: Bearer $OPEX_AUTH_TOKEN" \
  "https://api.opsengine.run/internal/scheduler/runs?task_id=serx:scheduler-tick&ok=false&limit=10"
```

Trigger.dev's own dashboard still shows the canonical run log (stdout,
stack traces, retries). `scheduler_runs` is the queryable-from-SQL summary
for ops/observability.
