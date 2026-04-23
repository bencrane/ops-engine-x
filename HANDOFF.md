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
- **Railway:** old service that served `api.managedagents.run` has been deleted. The active service is `api.opsengine.run` only. `api.managedagents.run` DNS is free and will be repointed to the new managed-agents-x-api service when it comes online.
- **Domain service callers** (`serx-webhook-ingest`, `oex-webhook-ingest`) have been updated to use `OPEX_AUTH_TOKEN` and point at `api.opsengine.run`.
- **Naming convention decided:** `-api` suffix = HTTP API service; no suffix = other runtime shape (job runner, daemon). Trigger.dev project is `ops-engine-x` (no `-api`). `-x` is an internal namespace token, never appears in user-facing URLs.

## Preserved for extraction (do NOT modify)

The following code and endpoints currently live in this repo but belong conceptually to the future `managed-agents-x-api` service. They are preserved verbatim so the agent building that repo can extract them cleanly. Do not delete, refactor, rename, or grow them here:

- `app/anthropic_client.py` — Anthropic managed-agents HTTP client.
- `app/sync.py` — reconciles Anthropic agent state into local DB.
- `app/agent_defaults.py` — `agent_defaults` table CRUD (per-agent `environment_id`, `vault_ids`, `task_instruction`).
- `scripts/setup_orchestrator.py` — one-shot orchestrator-agent creation script.
- `DIRECTIVE_BOOTSTRAP_DB.md`, `MANAGED-AGENTS-BRIEF.md` — handoff artifacts for the future repo.
- The `anthropic/` reference folder (Anthropic's own docs).
- Route handlers in `app/main.py`: `GET /agents`, `GET /agents/{agent_id}`, `GET|PUT|DELETE /agents/{agent_id}/defaults`, `GET /agents/defaults`, `POST /admin/sync/anthropic`.

At runtime, these endpoints will return clear errors (missing `ANTHROPIC_API_KEY`) — that is expected. Do not add `ANTHROPIC_API_KEY` to this project's Doppler to "fix" it. The fix is extraction into `managed-agents-x-api`.

---

## Roadmap — ordered work

### Phase 1 — Finish the rename cleanly (IN PROGRESS / MOSTLY DONE)

1. **Doppler secrets migration — DONE.** `ops-engine-x/prd` populated with `OPEX_AUTH_TOKEN`, `SUPABASE_DB_URL`, and related Supabase keys. `ANTHROPIC_API_KEY` intentionally excluded.
2. **Railway `DOPPLER_TOKEN` — DONE.** Service token for `ops-engine-x/prd` is in Railway.
3. **Source code sweep — DONE (this pass).** Files updated:
   - `app/config.py` — secret field renamed `mag_auth_token` → `opex_auth_token`, `anthropic_api_key` kept but no longer documented as expected (preserved-for-extraction code still references it and will fail clearly at call time).
   - `app/deps.py` — `require_admin_token` validates `OPEX_AUTH_TOKEN`.
   - `app/main.py` — service title + `/` payload updated; `/` slimmed; authenticated `GET /admin/status` added with secrets-loaded probe; `/agents*` + `/admin/sync/anthropic` + `/agents/*/defaults` handlers left intact per preservation rule.
   - `app/event_routes.py` — module docstring updated to reflect ops-engine-x scope.
   - `docker-entrypoint.sh` — header comment updated.
   - `docs/webhook-routing-architecture.md` — rewritten to use `ops-engine-x` + `OPEX_AUTH_TOKEN`.
   - `README.md`, `AGENTS.md` — scope reframed from "managed-agents backend" to "operational heartbeat / event routing".
   - **Not touched** (preservation rule): `anthropic/**`, `app/anthropic_client.py`, `app/sync.py`, `app/agent_defaults.py`, `scripts/setup_orchestrator.py`, `DIRECTIVE_BOOTSTRAP_DB.md`, `MANAGED-AGENTS-BRIEF.md`. These carry stale `managed-agents-x-api` references intentionally — they are extraction hand-off artifacts.
4. **Caller cutover — DONE.** Domain services re-pointed at `api.opsengine.run` with the new `OPEX_AUTH_TOKEN`.
5. **GitHub repo description** — still says `"managed-agents-x-api"`; update when convenient.

### Phase 2 — Clean up stale data model (SOON)

6. **Delete stale agent-definition tables** in ops-engine-x's Supabase DB.
   - Anthropic is the source of truth for agent configs.
   - These tables are currently stale and actively misleading.
   - What stays in ops-engine-x's DB re: agents: **only an `event_routes` (or similar) table mapping `(event_type, provider) → target` where target is either an `agent_id` string or an external API call spec.**
   - Any system prompts, tool configs, agent metadata currently in this DB: delete.
7. **Inventory the Anthropic-calling code** in this repo (`app/anthropic_client.py`, any `/agents` endpoints, `agent_defaults.py`, etc.) and mark it as "to be extracted." Do NOT extract yet. Do NOT build more of it here.

### Phase 3 — Build managed-agents-x-api (WHEN READY)

8. **Sanity-check Anthropic's API** for what it supports natively. Read `anthropic/managed-agents/` docs in this repo before designing the managed-agents-x-api data model. Some product features (versioning, drafts) may have Anthropic primitives that shape the design.
9. **Create new `managed-agents-x-api` repo.** Minimal first version: thin wrapper around Anthropic + start of product surface (CRUD, maybe version snapshots).
10. **Reuse the existing Doppler project `managed-agents-x-api`** for this new repo.
11. **Deploy to Railway.** Repoint `api.managedagents.run` DNS from ops-engine-x's Railway service to the new service.
12. **Extract Anthropic-calling code** from ops-engine-x → new repo.
13. **Update ops-engine-x** to call `managed-agents-x-api` (via service-to-service token) for agent invocations, instead of calling Anthropic directly.
14. **Build out product features** (versioning, drafts, templates, A/B tests, tool configurators, analytics) in `managed-agents-x-api`.

### Phase 4 — Layer in trigger.dev (PARALLEL TO PHASE 3)

15. **Set up Trigger.dev project `ops-engine-x`** (no `-api` — not an API).
16. Write scheduled job definitions (inbox watchers, periodic checks, etc.) that call ops-engine-x's API over HTTP.
17. Use ops-engine-x's Doppler project for any secrets Trigger.dev jobs need.

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

## Open questions / decisions deferred

- **Exact schema for the event_routes table** — not yet designed. Needs to handle both agent targets and non-agent API call targets cleanly.
- **Service-to-service auth mechanism** — JWT? Static bearer tokens stored in Doppler? TBD when we build the first cross-service call.
- **Whether `managed-agents-x-api` repo name keeps the dashes or goes to `managedagents-x-api`** — defer until repo creation; Doppler project already uses dashed form.
- **Observability/logging** stack — not set up yet across services.

---

## For the next agent picking this up

Start here:
1. Read this file.
2. Read `AGENTS.md` for repo-level conventions.
3. Ask the user which Phase 1 step they want to tackle first. Recommended order: Doppler migration → token rotation → source code sweep → README/AGENTS reframe → GitHub description. Do each as a discrete, verifiable step.
4. Do not proactively start Phase 2+ work without the user's go-ahead.
