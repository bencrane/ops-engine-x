# managed-agents-x-api — Repo Brief

> Onboarding brief for the agent starting work in the new (empty) `managed-agents-x-api` repo.
> Read this first, then ask the user which phase to start on.

---

## What you're building

**managed-agents-x-api** is a new FastAPI backend service that becomes the **product surface for managed agents** on this platform. It wraps Anthropic's managed-agents API and adds a product layer on top.

It has two consumer types:
1. **Frontend** (human-facing) — call this service to view, create, edit, version, and manage Claude managed agents. System prompt editors, tool configurators, draft/published lifecycle, version history, templates, A/B tests, agent analytics eventually live here.
2. **ops-engine-x** (system-to-system) — calls this service to **invoke agents** with task instructions in response to routed events. ops-engine-x does not call Anthropic directly; all Anthropic traffic flows through this service.

**You are NOT building:**
- Event routing. That's ops-engine-x's job. You just invoke whatever `agent_id` you're told, with whatever task instructions you're given.
- Scheduling / cron. That's ops-engine-x + Trigger.dev.
- Inbox watching, webhook ingest, workflow orchestration. All ops-engine-x.
- A source of truth for live agent configs — **Anthropic is the source of truth.** This service's DB (when added) stores only *product-layer metadata* (drafts, version snapshots, templates, A/B configs, analytics). Never the live agent config itself.

---

## Where this fits (target architecture)

```
Frontend ──────────────────→ api.managedagents.run ─────→ Anthropic API
                             (managed-agents-x-api:
                              this service)

Domain services:
serx-api, oex-api, etc. ─→ api.opsengine.run ───┬──→ managed-agents-x-api → Anthropic
                           (ops-engine-x:        │    (invocation gateway)
                            event routing, etc.) │
                                                 └──→ direct API calls to
                                                     non-agent targets
```

**Auth topology:**
- Frontend → managed-agents-x-api (user auth / API key — TBD)
- ops-engine-x → managed-agents-x-api (service-to-service token B)
- This service holds the Anthropic API key (the only place it lives)
- Domain services (serx, oex, etc.) are **never** authed directly to this service — they only know ops-engine-x exists

---

## Hold-the-line rules (do NOT violate)

1. **No routing logic here.** This service does not decide which agent to invoke for which event. It invokes whatever `agent_id` it's given. If you catch yourself building "if event_type is X, invoke agent Y" logic, stop — that belongs in ops-engine-x.
2. **Anthropic is source of truth for live agent configs.** Don't re-duplicate agent state. The DB (when added) stores only product-layer metadata.
3. **No ops-engine-x concerns.** No cron, no webhook ingest from external providers, no inbox watching. If it's operational plumbing, it belongs elsewhere.
4. **Separate the two consumer surfaces cleanly.** Frontend endpoints and internal (ops-engine-x) endpoints should be distinct — different auth, likely different route prefixes (e.g., `/agents/*` for frontend, `/internal/agents/*` for ops-engine-x). Frontend should never use internal endpoints; ops-engine-x should never use frontend endpoints.
5. **`-api` suffix means HTTP API.** This service is an API, hence `managed-agents-x-api`. (Naming TBD — see "Open decisions" below.)

---

## Infrastructure — already provisioned

- **Doppler project:** `managed-agents-x-api` already exists. It was originally the Doppler project for what is now `ops-engine-x`; it has been kept and reserved for this repo. Use it.
  - Anthropic API key should live here
  - Supabase credentials (if/when this service gets a DB) should live here
  - Service-to-service token shared with ops-engine-x for the internal invocation endpoint lives here
- **Custom domain target:** `api.managedagents.run` — currently pointing at the ops-engine-x Railway service during transition. When this new service is stood up and ready, DNS gets repointed to the new Railway service. Do NOT create a competing subdomain.

## Infrastructure — you'll set up

- **Railway service** for this new repo. Use the Dockerfile pattern from `ops-engine-x`.
- **Railway env var:** `DOPPLER_TOKEN` — generate a service token in the existing Doppler `managed-agents-x-api` project, set it as the only env var in Railway. The entrypoint runs `doppler run -- uvicorn ...`, which fetches secrets at container start.
- **Custom domain cutover** — after the service is feature-ready (parity with whatever ops-engine-x is currently serving on `api.managedagents.run`), repoint DNS. Coordinate with the user before the cutover.

---

## Reference repo — use `ops-engine-x` as a scaffolding pattern

The user will give you read access to `/Users/benjamincrane/ops-engine-x` (or its GitHub: `github.com/bencrane/ops-engine-x`). **This is your pattern reference, not a source to fork.** Recreate the scaffold fresh in this repo; don't wholesale copy.

**What to pattern-match from ops-engine-x:**
- `Dockerfile` + `docker-entrypoint.sh` pattern (Doppler-wrapped entrypoint)
- `railway.toml` structure
- `app/main.py` FastAPI entrypoint + `/health` pattern
- `app/config.py` Doppler-aware config loading
- `.dockerignore`, `.gitignore`
- `requirements.txt` baseline deps
- `AGENTS.md` structure (adapt to this repo's scope)

**What to extract as actual code** (not just pattern):
- `app/anthropic_client.py` — the Anthropic managed-agents client wrapper. This is the core piece that moves from ops-engine-x into this repo. Port it cleanly.
- Any `/agents/*` routes in ops-engine-x that are actually about managing agents (CRUD, invocation, etc.) — these are the starting point for your endpoints. Port them, clean them up, split them into frontend-facing vs internal.
- Any agent-related schemas / pydantic models used by those routes.

**What to leave behind in ops-engine-x:**
- Anything about event routing, routing tables, webhook handlers from domain services.
- Anything about scheduling or cron.
- The webhook-ingest / `/events/*` routes.
- Any `event_routes` table logic.

**What Anthropic's API supports natively** — before designing schemas, read the Anthropic managed-agents docs in `ops-engine-x/anthropic/managed-agents/*`. Some product features you're thinking about (versioning, drafts) may have Anthropic primitives that shape the design. Don't reinvent what Anthropic already gives you.

---

## Roadmap — phased

### Phase 1 — MVP scaffold (start here)

1. **Scaffold the repo** — Dockerfile, entrypoint, railway.toml, FastAPI skeleton with `/health`, Doppler-aware config.
2. **Port the Anthropic client** from ops-engine-x.
3. **Two endpoint groups:**
   - `/agents/*` — frontend-facing (user auth) — at minimum: list agents, get agent by id, maybe update system prompt. Keep small; you're just wrapping Anthropic.
   - `/internal/agents/{id}/invoke` — called by ops-engine-x with service-to-service token. Accepts `(agent_id, task_instruction)` and invokes Anthropic. This is THE gateway endpoint.
4. **Auth setup:**
   - Internal routes: bearer token from Doppler.
   - Frontend routes: defer to user decision (TBD — may be reusing existing auth from ops-engine-x, or a separate scheme).
5. **Deploy to Railway.** Get it green. Do NOT cut `api.managedagents.run` DNS over yet.
6. **Coordinate cutover with user** — when ready, repoint `api.managedagents.run` from ops-engine-x → this service. Update ops-engine-x to call this service's internal endpoint instead of calling Anthropic directly.

**Version 1 can be stateless** — no DB required for MVP. This service just wraps Anthropic and adds an auth layer. Resist the urge to add a DB until you have a feature that genuinely requires one.

### Phase 2 — Product surface build-out (after Phase 1 is live)

7. **Add Supabase** when the first product feature requires it. Likely trigger: version history for system prompts, or draft/published lifecycle.
8. **Version snapshots** — capture system prompt + tool config snapshots over time. Rollback support.
9. **Drafts** — in-progress agent config not yet deployed to Anthropic.
10. **Templates** — library of agent templates for quick creation.
11. **A/B configs** — route a portion of invocations to variant B, measure.
12. **Analytics layer** — agent invocation metrics beyond what Anthropic returns.
13. **Tool configurators** — UI/API for managing which MCP tools an agent can use.

Build these **incrementally, driven by actual frontend needs.** Don't build a speculative feature palace.

---

## Integration — how ops-engine-x calls you

Expected contract (confirm with user / adjust as needed):

```
POST /internal/agents/{agent_id}/invoke
Authorization: Bearer <service-to-service token>
Content-Type: application/json

{
  "task_instruction": "...",
  "context": { ... optional structured context ... },
  "metadata": { "source_event_id": "...", "provider": "cal_com", ... }
}

→ 200 OK
{
  "session_id": "...",
  "status": "running" | "completed",
  ...
}
```

Exact shape to be negotiated with user and ops-engine-x agent. Key constraints:
- ops-engine-x passes `agent_id` (already resolved via its routing table) + task instructions + optional context
- This service handles the Anthropic session lifecycle
- Response includes enough for ops-engine-x to correlate back to the triggering event (session_id, any status)

---

## Open decisions (confirm with user before committing)

- **Repo name:** `managed-agents-x-api` (consistent with Doppler project name + `-api` convention) vs `managed-agents-x` (user has floated dropping `-api` broadly, but said "not yet"). **Default:** `managed-agents-x-api`. Confirm with user.
- **Frontend auth scheme** — API keys? User JWTs? Reuse something existing? TBD.
- **Service-to-service auth between ops-engine-x and this service** — bearer token is the obvious default. Confirm.
- **DB or no DB for MVP** — default is no DB. Confirm with user before adding Supabase in Phase 1.
- **Anthropic-native primitives** — read the docs in `ops-engine-x/anthropic/managed-agents/` and surface what Anthropic already gives you before designing competing schemas.

---

## For the first agent picking this up

1. Read this file.
2. Confirm with user: repo name, whether to start Phase 1 now, and whether you have read access to `/Users/benjamincrane/ops-engine-x` for reference.
3. Read `ops-engine-x/AGENTS.md` and `ops-engine-x/HANDOFF.md` to understand the broader system and decisions already made.
4. Read `ops-engine-x/anthropic/managed-agents/*` before designing schemas.
5. Start Phase 1, step 1 (scaffold). Do each step as a discrete, verifiable commit.
6. Do NOT build Phase 2 features without user go-ahead.
