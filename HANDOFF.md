# ops-engine-x — Handoff & Roadmap

> Context snapshot for continuing work after a Cursor restart. Read this first.

---

## What this repo is (and isn't) becoming

**ops-engine-x** is the **operational heartbeat** of the platform. It's a FastAPI backend service deployed to Railway. Its scope is the *plumbing layer* of the system:

- **Event routing** — webhooks arrive from domain services (`serx-api`, `oex-api`, etc.) referencing events from providers (cal.com, signed-proposal provider, email, etc.); ops-engine looks up in its DB *which managed agent or API call* that event should be routed to, and dispatches.
- **Scheduled jobs** — the Trigger.dev project `ops-engine-x` (separate runtime, same conceptual umbrella) hosts cron/scheduled tasks. Inbox watchers, periodic checks, nightly sweeps, etc. Trigger.dev jobs call ops-engine-x's API when they need to do work that touches the platform.
- **Inbox watchers / observers** — future ongoing processes that monitor external systems and emit events into the routing table.
- **Workflow orchestration** — glue logic that sits between domain services and the things they need to trigger.

**It is NOT:**
- The managed-agents product surface (CRUD, system prompt editing, version history, drafts, A/B tests, templates, tool configurators). That work belongs in a separate, future repo: **`managed-agents-x-api`** (to be built — see roadmap).
- A source of truth for agent definitions. **Anthropic's managed-agents API is the source of truth for live agent configs.** ops-engine-x stores only *pointers* (agent_id strings) in its event routing table — never agent content.

---

## Target architecture (end state)

```
Frontend ──────────────────→ api.managedagents.run ─────→ Anthropic API
                             (managed-agents-x-api:                       
                              product surface —                           
                              CRUD, versioning, drafts,                   
                              templates, A/B, analytics)                  

Domain services:
serx-api, oex-api, etc. ─→ api.opsengine.run ───┬──→ managed-agents-x-api → Anthropic
                           (ops-engine-x:        │    (invocation gateway)
                            event routing,       │
                            cron, inbox,         └──→ direct API calls to
                            orchestration)            non-agent targets
```

**Auth topology:**
- Frontend → managed-agents-x-api (user auth / API key)
- Domain services → ops-engine-x, authenticated with **`OPEX_AUTH_TOKEN`** (inbound bearer — the credential that grants access *into* ops-engine-x)
- ops-engine-x → managed-agents-x-api (service-to-service token, named after the callee when it's introduced — e.g. `MAG_AUTH_TOKEN` for the managed-agents gateway)
- ops-engine-x → any other downstream service it may need to call — same pattern: a separate token per callee, named after the callee, stored in ops-engine-x's Doppler config
- Only managed-agents-x-api holds the Anthropic API key. **ops-engine-x does NOT expect `ANTHROPIC_API_KEY` in its Doppler config.** The Anthropic-calling code currently in this repo (see "Preserved for extraction" below) is frozen and will be extracted into managed-agents-x-api when that repo is built.
- Domain services are **never** authed directly to managed-agents-x-api — they only know ops-engine-x exists

**Token naming convention:** a token is named after the service it grants access *to*. `OPEX_AUTH_TOKEN` grants inbound access to ops-engine-x; `MAG_AUTH_TOKEN` (future) grants ops-engine-x access to managed-agents-x-api. This keeps direction unambiguous even when a single Doppler config holds tokens in opposite roles.

**Property this gives you:** domain services are completely decoupled from agent infrastructure. They emit events; they don't know if an event triggers an agent, a cron, or an HTTP call to something else. If you swap Anthropic for another provider, only `managed-agents-x-api` changes.

---

## Current state (what is already done)

- **GitHub repo:** renamed `managed-agents-x-api` → `ops-engine-x`. Remote URL updated locally.
- **Local directory:** `/Users/benjamincrane/ops-engine-x`. Doppler CLI is scoped here to `ops-engine-x/prd` (see `doppler configure --all`). Note: the shell's `DOPPLER_TOKEN`/`DOPPLER_PROJECT`/`DOPPLER_CONFIG` env vars (autoloaded for another project) will shadow the directory scope — strip them when running Doppler commands for this repo.
- **Doppler:** new project `ops-engine-x` created and populated (`OPEX_AUTH_TOKEN`, `SUPABASE_DB_URL`, `SUPABASE_*`). Old project `managed-agents-x-api` still exists and is reserved for the future `managed-agents-x-api` repo — do NOT delete it. **`ANTHROPIC_API_KEY` is intentionally NOT in the `ops-engine-x` Doppler config.**
- **Railway:** the active service is `api.opsengine.run` only. `api.managedagents.run` is no longer pointed at this project — that DNS record has been moved off ops-engine-x and now belongs to the new `managed-agents-x` service, which has been stood up in its own Railway project with its own Doppler project.
- **Domain service callers** (`serx-webhook-ingest`, `oex-webhook-ingest`) have been updated to use `OPEX_AUTH_TOKEN` and point at `api.opsengine.run`.
- **Naming convention decided:** `-api` suffix = HTTP API service; no suffix = other runtime shape (job runner, daemon). Trigger.dev project is `ops-engine-x` (no `-api`). `-x` is an internal namespace token, never appears in user-facing URLs.

## Extraction status — DONE

All Anthropic / managed-agents code has been extracted out of this repo and into [`managed-agents-x`](https://api.managedagents.run). The code that used to live here (`app/anthropic_client.py`, `app/sync.py`, `app/agent_defaults.py`, `scripts/setup_orchestrator.py`, `/agents*` route handlers, `/admin/sync/anthropic`) is gone. The `agents`, `agent_versions`, and `agent_defaults` tables have been dropped from this project's Supabase DB.

`POST /events/receive` is wired to HTTP-forward agent-kind events to `managed-agents-x`'s invocation gateway (`POST /internal/agents/{agent_id}/invoke`) via the `mag` entry in `app/service_registry.py`.

---

## Completed milestones

### Phase 1 — Rename to ops-engine-x (DONE)

- Doppler project `ops-engine-x` populated; `managed-agents-x-api` Doppler kept and repurposed as the managed-agents-x project's Doppler.
- Railway service running at `api.opsengine.run`, only env var is `DOPPLER_TOKEN`.
- Source code sweep: scope reframed from "managed-agents backend" to "operational heartbeat / event routing." Auth token renamed `MAG_AUTH_TOKEN` → `OPEX_AUTH_TOKEN`. Inbound auth standardized on `require_opex_auth`.
- Domain service callers (`serx-webhook-ingest`, `oex-webhook-ingest`) re-pointed at `api.opsengine.run` with `OPEX_AUTH_TOKEN`.

### Phase 2 — Stale data model cleanup (DONE)

- `agents`, `agent_versions`, `agent_defaults` tables dropped from this project's Supabase DB.
- What stays in this DB: `event_routes` (routing decisions), `scheduled_events` (cron registry), `scheduler_runs` (cron dispatch log).

### Phase 3 — Build managed-agents-x (DONE)

- New repo deployed to Railway, reachable at `api.managedagents.run`.
- Its own Doppler project holds `ANTHROPIC_API_KEY`, Supabase creds, and `MAG_AUTH_TOKEN` (inbound).
- Anthropic client, `agent_defaults` CRUD, sync, and the `setup_orchestrator` scaffolder all live in managed-agents-x now.
- Invocation gateway endpoint live: `POST /internal/agents/{agent_id}/invoke`. Accepts `(source, event_name, event_ref, title?, idempotency_key?)`, does its own `agent_defaults` lookup, formats kickoff, creates Anthropic session, returns session metadata.

### Phase 4 — Scheduled dispatch via Trigger.dev (DONE for initial tasks)

- Trigger.dev project `ops-engine-x` active. Tasks call `POST /internal/scheduler/tick` on ops-engine-x with `(event_id, trigger_run_id)`. ops-engine-x resolves `scheduled_events[event_id]` → `service_registry.resolve(target_service)` → HTTP call → `scheduler_runs` log row.
- Live tasks: `serx.dispatch_due_preframes` (every 6 hours), `oex.auth_me_probe` (daily reachability/auth check).
- Scheduler now supports both GET and POST dispatch (`http_method` column on `scheduled_events`, default POST).

---

## Hold-the-line rules (do NOT violate)

1. **No new managed-agents product features in ops-engine-x.** If a feature request touches agent authoring, versioning, editing, templates, etc. — it either gets stubbed minimally here or waits for the new `managed-agents-x-api` repo. Don't dig the hole deeper.
2. **Do not modify the preserved extraction code.** The files listed under "Preserved for extraction" are frozen. Don't refactor them, don't rename their symbols, don't update their stale `managed-agents-x-api` references. They ship as-is into the future repo.
3. **ops-engine-x does not expect `ANTHROPIC_API_KEY`.** Do not add it to this project's Doppler. Any endpoint that needs it (the preserved extraction endpoints) will return a clear error at call time — that is the correct state until extraction.
4. **ops-engine-x's DB never stores agent content.** Only pointers (`agent_id` strings), routing rules, cron state, event logs. The `agent_defaults` table is an extraction artifact and moves to `managed-agents-x-api`.
5. **Neither domain services nor the frontend call the wrong backend.** Domain services → ops-engine-x only. Frontend → managed-agents-x-api only. ops-engine-x → managed-agents-x-api (not the other way).
6. **managed-agents-x-api will be dumb about routing.** Routing decisions live in ops-engine-x. managed-agents-x-api just invokes whatever `agent_id` it's told.
7. **Anthropic is source of truth for live agent configs.** Don't re-duplicate agent state. managed-agents-x-api's DB stores only product-layer metadata (drafts, versions, templates, A/B, analytics) — never the live config itself.
8. **Subdomains name capabilities, not umbrellas.** `api.opsengine.run`, `docs.opsengine.run`, etc. Never `x.opsengine.run`. The apex `opsengine.run` is free for future marketing/landing/redirect use.
9. **`-api` suffix means HTTP API.** Trigger.dev projects, workers, daemons do NOT get `-api`. If you catch yourself naming a non-API service with `-api`, stop.
10. **Token-naming convention.** A token's name reflects the service it grants access *to*, not the service holding it. Inbound-to-ops-engine-x = `OPEX_AUTH_TOKEN`. Outbound-from-ops-engine-x to service X = `X_AUTH_TOKEN` (e.g. `MAG_AUTH_TOKEN` when calling managed-agents-x-api, `SERX_AUTH_TOKEN` when calling serx-api).
11. **Every routing decision lives in ops-engine-x.** No caller (webhook-ingest, Trigger.dev task, future fan-out source) ever hardcodes a target service URL or carries a target service's bearer token. Callers tell ops-engine-x *what happened* (inbound webhook: `(source, event_name, event_ref)`; scheduled tick: `event_id`); ops-engine-x looks up the target in a routing table and makes the outbound call itself. Trade-off: one extra HTTP hop (~100–300ms) per dispatch. Benefit: routing changes are SQL updates, not redeploys; outbound credentials live only in ops-engine-x's Doppler; every dispatch is auto-logged in one queryable place.
12. **ops-engine-x never touches another service's database.** Dispatch targets are always internal HTTP endpoints on the owning service (e.g. `https://api.serviceengine.xyz/api/internal/scheduler/dispatch-due-preframes`). Domain services own their data; ops-engine-x only knows their public API surface and holds the bearer token to call it.

---

## Open threads

- **`event_routes` generalization.** Today the table is `(source, event_name, agent_id, enabled)` — 100% of routes target an agent. When the second target kind appears (raw HTTP call, Trigger.dev task run, etc.), generalize to `(source, event_name, target_kind, target_spec jsonb, enabled)` and branch in `receive_event` on `target_kind`. Don't pre-generalize.
- **Idempotency on the receiver side.** ops-engine-x currently passes `idempotency_key = event_ref.id` downstream. If webhook-ingest providers re-send the same webhook (retries, replay), managed-agents-x's invocation_log de-dupes. ops-engine-x itself does no idempotency check today — if needed, add one at the `event_routes` lookup.
- **Observability.** No centralized logging/tracing stack yet. Today's inspection is `/internal/scheduler/runs` for scheduled dispatches and Trigger.dev's run log for its side. Inbound `/events/receive` calls have no persistent audit trail — if that becomes needed, add an `events_received` table.
- **GitHub repo description** still says `"managed-agents-x-api"` — cosmetic, update when convenient.
- **Docs trim.** `docs/webhook-routing-architecture.md` predates the extraction and still describes parts of the system that now live in managed-agents-x (orchestrator system prompts, agent wake-up behavior, MCP hydration). Worth pruning to just the ops-engine-x concern (inbound contract + routing) once someone has an hour.

---

## For the next agent picking this up

Start here:
1. Read this file.
2. Read `AGENTS.md` for repo-level conventions.
3. Ask the user what they want to tackle. The extraction is done; remaining work is operational (add a new source, a new target_kind, a new scheduled task) or quality-of-life (observability, docs trim).
