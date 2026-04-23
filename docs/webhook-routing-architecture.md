# Webhook → Managed-Agent Routing Architecture

**Status:** live as of 2026-04-23
**Owner service:** `ops-engine-x` (this repo), deployed at `api.opsengine.run`
**Upstream callers:** `oex-webhook-ingest`, `serx-webhook-ingest`
**Downstream (today):** Anthropic Managed Agents API (`/v1/sessions`), via the preserved-for-extraction code in `app/anthropic_client.py`.
**Downstream (future):** `managed-agents-x` (invocation gateway). When that service comes online, the Anthropic-calling code moves there and ops-engine-x calls the gateway instead. The contract for `POST /events/receive` described here does not change.

This document is the canonical reference for how third-party webhooks (Cal.com, EmailBison, etc.) get turned into running Claude Managed Agent sessions. Read this before modifying any of the moving parts.

---

## 1. Design principles

1. **Webhook-ingest apps are dumb.** They persist the raw payload, then POST a pointer to `ops-engine-x`. They do not resolve org_id, do not know which agent handles what, do not forward the full body.
2. **Routing is centralized.** A single `event_routes` table in this service maps `(source, event_name) → agent_id`. Ingest apps never hardcode agent IDs.
3. **Agents hydrate themselves.** The initial session message carries only an `event_ref` pointer. The agent's own MCP tool (e.g. `serx_get_webhook_event`, `oex_get_webhook_event`) fetches the raw payload from the caller's DB on demand.
4. **Canonical source names use underscores:** `emailbison`, `cal_com`. No dots, no hyphens, no abbreviations.
5. **Cal.com event names are UPPERCASE** (`BOOKING_CREATED`). EmailBison event names are lowercase (`lead_replied`). Match exactly what the provider sends.

---

## 2. End-to-end flow

```
Cal.com / EmailBison
        │  (webhook)
        ▼
┌───────────────────────────┐
│ {serx,oex}-webhook-ingest │  persists raw payload to its own DB
└────────────┬──────────────┘  (webhook_events_raw / oex_webhook_events)
             │
             │  POST /events/receive
             │  { source, event_name, event_ref: {store, id} }
             │  Bearer OPEX_AUTH_TOKEN
             ▼
┌───────────────────────────┐
│ ops-engine-x              │
│ 1. resolve event_route    │  (source, event_name) → agent_id
│ 2. load agent_defaults    │  agent_id → environment_id + vault_ids
│ 3. POST /v1/sessions      │  (Anthropic — preserved-for-extraction)
│ 4. POST .../events        │  initial user.message with event_ref
└────────────┬──────────────┘
             │
             ▼
      Anthropic runtime
      spawns agent session
             │
             ▼
      Agent calls its MCP:
      serx_get_webhook_event({event_id: event_ref.id})
      oex_get_webhook_event({event_id: event_ref.id})
      → does its work
```

---

## 3. The contract: `POST /events/receive`

**Route:** `POST /events/receive`
**Auth:** `Authorization: Bearer ${OPEX_AUTH_TOKEN}`
**Handler:** [app/main.py](app/main.py) (`receive_event`)

### Request body

```json
{
  "source": "cal_com",
  "event_name": "BOOKING_CREATED",
  "event_ref": {
    "store": "serx_webhook_events_raw",
    "id": "<uuid of the row that holds the raw payload>"
  },
  "title": "optional session title override"
}
```

Field rules:
- `source` — canonical lowercase_snake: `emailbison`, `cal_com`.
- `event_name` — provider-exact casing (`BOOKING_CREATED`, `lead_replied`).
- `event_ref.store` — the caller's table name. Callers pick their own; the agent's prompt says which store to expect.
- `event_ref.id` — UUID of the row holding the raw payload.
- Never send the raw payload itself.

### Response (201-style)

```json
{
  "session_id": "ses_...",
  "agent_id": "agent_...",
  "environment_id": "env_...",
  "vault_ids": ["vault_..."],
  "status": "running"
}
```

### Error codes

| Status | Meaning |
|--------|---------|
| 401 | Missing/invalid `OPEX_AUTH_TOKEN` |
| 404 | No `event_route` configured for `(source, event_name)` |
| 409 | `event_route` exists but is disabled, OR no `agent_defaults` for the resolved agent |
| 4xx/5xx passthrough | Upstream Anthropic error, body forwarded verbatim |
| 502 | Network error talking to Anthropic |

### What the agent receives

The API creates the Anthropic session with metadata:
```json
{
  "source": "cal_com",
  "event_name": "BOOKING_CREATED",
  "event_ref_store": "serx_webhook_events_raw",
  "event_ref_id": "<uuid>"
}
```

Then sends a single `user.message` with text:
```
source: cal_com
event_name: BOOKING_CREATED
event_ref: {"store": "serx_webhook_events_raw", "id": "<uuid>"}
```

The agent's system prompt tells it how to parse this and which MCP tool to call for hydration.

---

## 4. The `event_routes` table

**Location:** Supabase (same DB as `agent_defaults`).
**Schema:**

```sql
create table event_routes (
  source       text not null,
  event_name   text not null,
  agent_id     text not null,
  enabled      boolean not null default true,
  created_at   timestamptz not null default now(),
  updated_at   timestamptz not null default now(),
  primary key (source, event_name)
);
create index event_routes_agent_id_idx on event_routes (agent_id);
```

**CRUD module:** [app/event_routes.py](app/event_routes.py) — `resolve()`, `list_all()`, `upsert()`, `delete()`.

**Admin endpoints** (require `OPEX_AUTH_TOKEN`):
- `GET /event-routes` — list all
- `PUT /event-routes/{source}/{event_name}` — upsert `{agent_id, enabled}`
- `DELETE /event-routes/{source}/{event_name}`

### Current seeded routes

| source | event_name | agent | purpose |
|---|---|---|---|
| `emailbison` | `lead_replied` | inbox-orchestrator | tracked reply, classify + respond |
| `emailbison` | `lead_interested` | inbox-orchestrator | positive signal |
| `emailbison` | `untracked_reply_received` | inbox-orchestrator | out-of-sequence reply |
| `emailbison` | `lead_unsubscribed` | inbox-orchestrator | unsubscribe handling |
| `cal_com` | `BOOKING_CREATED` | new-booking-orchestrator | persist new booking |
| `cal_com` | `BOOKING_REQUESTED` | new-booking-orchestrator | pending approval booking |
| `cal_com` | `BOOKING_PAID` | new-booking-orchestrator | paid booking |
| `cal_com` | `BOOKING_RESCHEDULED` | rescheduled-booking-orchestrator | new uid, flip old → rescheduled |
| `cal_com` | `BOOKING_CANCELLED` | canceled-booking-orchestrator | status → cancelled |
| `cal_com` | `BOOKING_REJECTED` | canceled-booking-orchestrator | treat as cancel |
| `cal_com` | `AFTER_HOSTS_CAL_VIDEO_NO_SHOW` | canceled-booking-orchestrator | no-show |
| `cal_com` | `AFTER_GUESTS_CAL_VIDEO_NO_SHOW` | canceled-booking-orchestrator | no-show |

**Explicitly NOT routed:**
- `warmup_disabled_*` events — not orchestration-relevant.
- `email_bounced` — suppression list concern, handled elsewhere.

---

## 5. The `agent_defaults` table

**Purpose:** per-agent `environment_id`, `vault_ids`, and optional `task_instruction` that the session-creation step needs. Without defaults, `/events/receive` returns 409.

**Columns:** `agent_id` (PK), `environment_id`, `vault_ids text[]`, `task_instruction text` (nullable).

**Module:** [app/agent_defaults.py](app/agent_defaults.py).

**Admin endpoints:**
- `GET /agents/defaults`
- `GET /agents/{agent_id}/defaults`
- `PUT /agents/{agent_id}/defaults` — body `{environment_id, vault_ids, task_instruction?}`
- `DELETE /agents/{agent_id}/defaults`

Every agent referenced by an `event_route` MUST have a matching `agent_defaults` row.

### `task_instruction`

An optional durable kickoff preamble prepended to the user.message the agent receives. When set, the initial message becomes:

```
<task_instruction>

source: <source>
event_name: <event_name>
event_ref: {...}
```

Use this for a short, stable task framing ("You are the new-booking-orchestrator. Persist the booking to SERX. Do nothing else.") that complements the system prompt. Leave null to send just the event block.

---

## 6. The four orchestrator agents

All four were created against `claude-sonnet-4-6` on Anthropic managed infra and are editable in Console UI. System prompts are the source of truth for behavior; this doc only describes what each is for.

### 6.1 inbox-orchestrator
- **Agent ID:** (see Anthropic Console; pulled from `agent_defaults`)
- **Triggered by:** `emailbison/*` events
- **MCP:** `emailbison` (official hosted), plus whatever oex-mcp additions are required for reply action recording
- **Status:** system prompt pending — waiting on oex agent's playbook spec

### 6.2 new-booking-orchestrator
- **Agent ID:** `agent_011CaKVUQQ1uBt14rAZAfdAe`
- **Triggered by:** `cal_com/BOOKING_CREATED` (+ REQUESTED, PAID)
- **MCP:** serx-mcp
- **System prompt version:** v4 (pushed 2026-04-22)
- **Directive source:** `/Users/benjamincrane/# new-booking-orchestrator — SERX DB write directive.md`

Steps: fetch raw payload → resolve org → append `serx_create_booking_event` audit row → `serx_create_meeting_from_cal_event` (idempotent) → enrich primary attendee via `serx_upsert_contact`.

### 6.3 rescheduled-booking-orchestrator
- **Agent ID:** `agent_011CaKYudXLy6opfnsgZH5T3`
- **Triggered by:** `cal_com/BOOKING_RESCHEDULED`
- **MCP:** serx-mcp
- **System prompt version:** v2 (pushed 2026-04-22)

Key subtlety: Cal.com does NOT mutate in place. The webhook carries a **new** `uid`/`id` plus `rescheduledFromUid` for the old booking. `serx_create_meeting_from_cal_event` handles the flip atomically when passed `rescheduled_from_uid`.

### 6.4 canceled-booking-orchestrator
- **Agent ID:** `agent_011CaKYuiC9XGxkWRjMUQrAF`
- **Triggered by:** `cal_com/BOOKING_CANCELLED` (+ REJECTED, NO_SHOW variants)
- **MCP:** serx-mcp
- **System prompt version:** v2 (pushed 2026-04-22)

Cancellation reuses the original uid. Agent looks up existing meeting via `serx_get_meeting_by_cal_uid`, falls back to `serx_get_meeting_by_cal_booking_id`, then `serx_update_meeting({status: "cancelled"})`. Never creates a meeting on cancel.

---

## 7. What each webhook-ingest app must do

### Common responsibilities
1. Receive raw webhook from provider.
2. Write full payload to the app's own `*_webhook_events_raw` table. Store `source`, `event_name`, `payload`, and track dispatch state (e.g. `dispatch_status`, `dispatch_error`).
3. POST to `ops-engine-x /events/receive` (`https://api.opsengine.run/events/receive`):
   ```
   Authorization: Bearer ${OPEX_AUTH_TOKEN}
   Content-Type: application/json

   {
     "source": "<canonical>",
     "event_name": "<provider-exact>",
     "event_ref": { "store": "<this_app_table_name>", "id": "<row uuid>" }
   }
   ```
4. On 2xx: mark the row `dispatch_status='dispatched'`, store returned `session_id`.
5. On 404 (no route): mark `dispatch_status='no_route'`. Not an error — means the event is intentionally ignored.
6. On 409 / 5xx: log, mark `dispatch_status='failed'`, surface for retry.

### serx-webhook-ingest specifics
- **Source values:** always `cal_com`. (Not `cal`, not `cal.com`.)
- **Store value:** `serx_webhook_events_raw`
- **Event names:** copy Cal.com's `triggerEvent` verbatim (UPPERCASE).
- **MCP for agents:** `serx-mcp` — must expose `serx_get_webhook_event({event_id})` that returns the row by its UUID.

### oex-webhook-ingest specifics
- **Source values:** `emailbison`
- **Store value:** `oex_webhook_events`
- **Event names:** copy EmailBison event name verbatim (lowercase).
- **MCP for agents:** `oex-mcp` — must expose `oex_get_webhook_event({event_id})`.

### Shared secret
Both ingest apps store `OPEX_AUTH_TOKEN` in their own Doppler (same value as `ops-engine-x/prd OPEX_AUTH_TOKEN`). When the value rotates, all three must rotate together.

---

## 8. What agents must do on wake-up

The initial message the agent sees is exactly:
```
source: <source>
event_name: <event_name>
event_ref: {"store": "...", "id": "<uuid>"}
```

Every orchestrator system prompt tells the agent to:
1. Call the appropriate hydration tool (`serx_get_webhook_event` / `oex_get_webhook_event`) with `event_ref.id`.
2. Extract fields from the returned payload. For Cal.com, the real booking object lives at `payload.payload` (Cal's nested envelope).
3. Resolve `org_id` via its own MCP (e.g. `serx_resolve_org_from_event_type({event_type_id})`). The ingest layer does NOT pass `org_id`.
4. Never write back to `*_webhook_events_raw`. Dispatch state is owned by the ingest app.

---

## 9. Why this shape (design history)

Earlier iterations tried:
- **Sending the full payload to `/events/receive`.** Rejected — ingest apps already persist it; shipping it a second time wastes bandwidth and couples the router to payload schemas.
- **Having the ingest app pass `agent_id`.** Rejected — that pushes routing knowledge into every caller. Centralizing it in `event_routes` means we can re-point an event to a different agent without redeploying ingest services.
- **Source named `cal.com` or `cal`.** Rejected — `.` is brittle in some contexts (URL paths, query params); `cal` is ambiguous (Cal.com vs Google Calendar vs Apple Calendar). `cal_com` is explicit and path-safe.
- **Pre-resolving `org_id` in the ingest app.** Rejected — each agent already has the MCP access needed to resolve org from event_type. Keeping it in the agent means one fewer cross-service contract.

---

## 10. Key files in this repo

| File | Purpose |
|---|---|
| [app/main.py](app/main.py) | FastAPI routes — `/events/receive`, `/event-routes/*`, `/agents/*/defaults` |
| [app/event_routes.py](app/event_routes.py) | `event_routes` CRUD module |
| [app/agent_defaults.py](app/agent_defaults.py) | `agent_defaults` CRUD module |
| [app/anthropic_client.py](app/anthropic_client.py) | `create_session`, `send_user_message`, `get_agent`, `list_agents` |
| [app/sync.py](app/sync.py) | Reconcile from Anthropic into local DB |
| [app/deps.py](app/deps.py) | `require_opex_auth` bearer check (also exported as `require_admin_token` for the preserved-for-extraction handlers) |
| [app/config.py](app/config.py) | Lazy secret loader |
| [scripts/setup_orchestrator.py](scripts/setup_orchestrator.py) | One-shot creation of the four orchestrator agents |

---

## 11. Open work (as of 2026-04-22)

- **inbox-orchestrator system prompt** — awaiting oex agent's playbook spec.
- **oex-mcp additions** — `get_webhook_event`, `get_campaign_assets`, `record_reply_action` — external directive handed to oex team.
- **oex-webhook-ingest + serx-webhook-ingest** — implement the dispatch described in §7. Directives already handed off.
- **Legacy Railway inbox-agent** — to be torn down once inbox-orchestrator is verified handling production traffic.
- **serx-mcp verification** — the booking prompts assume `serx_create_meeting_from_cal_event`, `serx_get_meeting_by_cal_uid`, `serx_get_meeting_by_cal_booking_id`, `serx_update_meeting`, `serx_upsert_contact`, `serx_resolve_org_from_event_type`, `serx_create_booking_event`, `serx_get_webhook_event` all exist. Confirm before first prod dispatch.
