# Directive: Bootstrap managed-agents-x-api DB from Anthropic ground truth

## Context
You are working in `/Users/benjamincrane/managed-agents-x-api` — a FastAPI backend service that will become the system-of-record for Claude Managed Agents. A separate frontend app will use this backend to view and edit agent configs (system prompts, tools, MCP servers, etc.). Currently all ground truth lives in Anthropic's Managed Agents platform. Your job is to pull it into our Supabase DB so the DB becomes authoritative going forward.

## Environment
- **Doppler project** for this repo: `managed-agents-x-api` (config `dev`) — already scoped via `doppler configure`. Run anything that needs secrets through `doppler run -- <cmd>`.
- **Secrets available** in Doppler: `ANTHROPIC_API_KEY`, `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_ANON_KEY`, `SUPABASE_DB_URL`, `SUPABASE_PROJECT_REF`.
- **Supabase project**: `managed-agents-x-api`, ref `imfwppinnfbptqdyraod`, Postgres 17, `public` schema is empty.
- **Supabase MCP** is available in your session — use `apply_migration` for DDL and `execute_sql` for ad-hoc. Project id: `imfwppinnfbptqdyraod`.

## Canonical Anthropic docs (read first — do not guess API shapes)
The `anthropic/` folder has been added to this repo at the root. It contains the authoritative reference for the Anthropic API and Managed Agents platform. Read these before designing the schema or writing any API calls:

- `anthropic/MANAGED_AGENTS_CANONICAL.md` — canonical overview of how Managed Agents work.
- `anthropic/MANAGED_AGENTS_CANONICAL_DIRECTIVE.md` — canonical directive-style reference.
- `anthropic/ANTHROPIC_API_CANONICAL.md` — canonical Anthropic API reference.
- `anthropic/managed-agents/` — subfolder with endpoint-level detail for Managed Agents (list agents, get agent, system prompt, tools, MCP server bindings, credential vault ids, environments, versions, etc.).
- `anthropic/api-reference/`, `anthropic/home/`, `anthropic/00-general/` — supporting reference material.

Use these docs to determine the exact endpoint paths, request/response shapes, auth headers, pagination, and all the fields you will need to pull per agent. **Do not** rely on training-data memory of the Anthropic API — the canonical files in this repo are the source of truth.

## What to build

### 1. Schema (your call)
Design the tables. You are expected to make strong engineering decisions here — do not ask for permission on schema shape. Constraints you must satisfy:
- Capture the **full ground truth** of each managed agent as it exists on Anthropic today: at minimum system prompt, model, tool config, MCP server connections including **credential vault ids**, environment, and any agent-level metadata Anthropic exposes (discover the full field set from `anthropic/managed-agents/`).
- Support **immutable version history** of system prompts and config — every edit going forward creates a new version; rollback = promote old version, never mutate.
- Track which version is **currently active / deployed** per agent.
- Store the **raw Anthropic API response** per version snapshot (jsonb) so we can forensically compare later even if our normalized columns miss a field.
- Distinguish **source of a version** (pulled from Anthropic vs. edited in our UI) and support a later **drift-detection** reconcile job.
- Audit trail for deployments (who/when/status/error).

Apply migrations via the Supabase MCP against project `imfwppinnfbptqdyraod`. Use sensible RLS defaults (service-role-only for now; the frontend will go through this backend, not directly to Supabase).

### 2. Sync code
Build the initial-backfill sync inside this FastAPI app (`app/` directory — follow the existing project structure and conventions; read `AGENTS.md` and `README.md` first). It must:
- List all managed agents on Anthropic using `ANTHROPIC_API_KEY` from Doppler (endpoint and request shape per `anthropic/managed-agents/`).
- For each agent, fetch full config including system prompt, model, tools, MCP server bindings with credential vault ids, environment, and every other field the canonical docs document.
- Upsert into your `agents` table keyed on Anthropic's agent id.
- Insert a new version row with `source='anthropic_pull'`, the normalized fields, and the raw response snapshot.
- Set that version as the active version.
- Be **idempotent** — re-running must not duplicate rows; it should detect unchanged agents and skip, and create a new version only when something actually changed.
- Log a summary at the end: agents seen, created, updated, unchanged.

Expose it as both a CLI entrypoint (`python -m app.sync` or similar — your call) **and** an authenticated FastAPI endpoint (e.g. `POST /admin/sync/anthropic`) so we can trigger it from the frontend later.

### 3. Verification
- Run the sync end-to-end via `doppler run -- <cmd>`.
- Query the DB via the Supabase MCP and confirm row counts match Anthropic's agent count, active_version is set on every row, and at least one sample agent's system prompt in the DB matches what's on Anthropic.
- Run it a second time and confirm idempotency (no new versions created when nothing changed).

## Out of scope
- UI edit / deploy flow (next directive).
- Drift reconcile job (next directive) — but leave room for it in the schema.
- Frontend auth model.

## Deliverable
- Migration(s) applied to `imfwppinnfbptqdyraod`.
- Sync module in `app/` with tests where it matters.
- Short write-up in your final message: table list with one-line purpose each, the endpoint/CLI command, and the verification output (agent count, sample diff check, second-run idempotency proof).
