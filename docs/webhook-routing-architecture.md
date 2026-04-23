# Webhook → Managed-Agent Routing Architecture

**Status:** live as of 2026-04-23
**Owner service:** `ops-engine-x` (this repo), deployed at `api.opsengine.run`
**Upstream callers:** `oex-webhook-ingest`, `serx-webhook-ingest`
**Downstream:** `managed-agents-x` (invocation gateway) at `api.managedagents.run`. All Anthropic traffic flows through that service; ops-engine-x does not call Anthropic directly.

This document is the canonical reference for how third-party webhooks (Cal.com, EmailBison, etc.) get turned into running Claude Managed Agent sessions from ops-engine-x's perspective. For what happens **inside** managed-agents-x (session lifecycle, `agent_defaults` lookup, kickoff-message formatting, Anthropic session creation), see that repo's docs.

---

## 1. Design principles

1. **Webhook-ingest apps are dumb.** They persist the raw payload, then POST a pointer to ops-engine-x. They do not resolve `org_id`, do not know which agent handles what, do not forward the full body.
2. **Routing is centralized.** A single `event_routes` table in this service maps `(source, event_name) → agent_id`. Ingest apps never hardcode agent IDs. ops-engine-x is the only service that owns this mapping.
3. **Agent-invocation state lives in managed-agents-x.** `environment_id`, `vault_ids`, `task_instruction`, agent system prompts, versions — none of that lives in ops-engine-x. ops-engine-x holds only `agent_id` strings.
4. **Agents hydrate themselves.** The initial session message (built by managed-agents-x) carries only an `event_ref` pointer. The agent's own MCP tool (e.g. `serx_get_webhook_event`, `oex_get_webhook_event`) fetches the raw payload from the caller's DB on demand.
5. **Canonical source names use underscores:** `emailbison`, `cal_com`. No dots, no hyphens, no abbreviations.
6. **Provider-native event-name casing.** Cal.com uses UPPERCASE (`BOOKING_CREATED`); EmailBison uses lowercase (`lead_replied`). Match exactly what the provider sends — never normalize.

---

## 2. End-to-end flow

```
Cal.com / EmailBison
        │  (webhook)
        ▼
┌───────────────────────────┐
│ {serx,oex}-webhook-ingest │  persists raw payload to its own DB
└────────────┬──────────────┘  (serx_webhook_events_raw / oex_webhook_events)
             │
             │  POST /events/receive
             │  { source, event_name, event_ref: {store, id} }
             │  Bearer OPEX_AUTH_TOKEN
             ▼
┌───────────────────────────┐
│ ops-engine-x              │
│ 1. resolve event_route    │  (source, event_name) → agent_id
│ 2. service_registry("mag")│  → (MAG_API_URL, MAG_AUTH_TOKEN)
│ 3. POST managed-agents-x  │  /internal/agents/{agent_id}/invoke
│ 4. passthrough response   │  status + body verbatim
└────────────┬──────────────┘
             │
             ▼
┌───────────────────────────┐
│ managed-agents-x          │
│ 1. load agent_defaults    │  agent_id → environment_id, vault_ids,
│                           │   task_instruction
│ 2. format kickoff text    │
│ 3. Anthropic /v1/sessions │  create session
│ 4. Anthropic .../events   │  send user.message with kickoff
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

## 3. The inbound contract: `POST /events/receive`

**Route:** `POST /events/receive`
**Auth:** `Authorization: Bearer ${OPEX_AUTH_TOKEN}`
**Handler:** [`app/main.py::receive_event`](../app/main.py)

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
- `source` — canonical `lowercase_snake`: `emailbison`, `cal_com`.
- `event_name` — provider-exact casing (`BOOKING_CREATED`, `lead_replied`).
- `event_ref.store` — the caller's table/collection name. Callers pick their own; the agent's system prompt + MCP know which store to expect for a given source.
- `event_ref.id` — UUID of the row holding the raw payload.
- Never send the raw payload itself.

### Response

ops-engine-x passes through whatever managed-agents-x returns. On success:

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

| Status | Source | Meaning |
|--------|--------|---------|
| 401 | ops-engine-x | Missing/invalid `OPEX_AUTH_TOKEN`. |
| 404 | ops-engine-x | No `event_route` configured for `(source, event_name)`. |
| 409 | ops-engine-x | `event_route` exists but is disabled. |
| 500 | ops-engine-x | `mag` slug missing from `service_registry` (config bug). |
| 503 | ops-engine-x | `MAG_API_URL` / `MAG_AUTH_TOKEN` not set in Doppler. |
| 502 | ops-engine-x | managed-agents-x unreachable (DNS, TCP, TLS, timeout). |
| any | managed-agents-x | Passthrough — status + body forwarded verbatim (e.g. 409 when no `agent_defaults` for the resolved agent, 4xx/5xx from Anthropic, etc.). |

---

## 4. The `event_routes` table

**Location:** ops-engine-x's Supabase, `public.event_routes`.

**Schema:**

```sql
create table event_routes (
  source       text        not null,
  event_name   text        not null,
  agent_id     text        not null,
  enabled      boolean     not null default true,
  created_at   timestamptz not null default now(),
  updated_at   timestamptz not null default now(),
  primary key (source, event_name)
);
create index event_routes_agent_id_idx on event_routes (agent_id);
```

**CRUD module:** [`app/event_routes.py`](../app/event_routes.py) — `resolve()`, `list_all()`, `upsert()`, `delete()`.

**Admin endpoints** (require `OPEX_AUTH_TOKEN`):
- `GET /event-routes` — list all.
- `PUT /event-routes/{source}/{event_name}` — upsert `{agent_id, enabled}`.
- `DELETE /event-routes/{source}/{event_name}`.

**Future generalization.** Today every route targets an agent. When the second target kind appears (raw HTTP call, Trigger.dev task run, etc.), extend the schema to `(source, event_name, target_kind, target_spec jsonb, enabled)` and branch in `receive_event` on `target_kind`. Don't pre-generalize — one row is cheaper than premature abstraction.

### Currently seeded routes

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

## 5. What each webhook-ingest app must do

### Common responsibilities

1. Receive raw webhook from provider.
2. Write full payload to the app's own `*_webhook_events_raw` (or equivalent) table. Store `source`, `event_name`, `payload`, and track dispatch state (e.g. `dispatch_status`, `dispatch_error`, `session_id`).
3. POST to `ops-engine-x /events/receive` (`https://api.opsengine.run/events/receive`):
   ```
   Authorization: Bearer ${OPEX_AUTH_TOKEN}
   Content-Type: application/json

   {
     "source":     "<canonical>",
     "event_name": "<provider-exact>",
     "event_ref":  { "store": "<this_app_table_name>", "id": "<row uuid>" }
   }
   ```
4. On 2xx: mark `dispatch_status='dispatched'`, store returned `session_id`.
5. On 404: mark `dispatch_status='no_route'`. Not an error — means the event is intentionally ignored.
6. On 409 / 5xx: log, mark `dispatch_status='failed'`, surface for retry. Any 5xx from the managed-agents-x side (passed through by ops-engine-x) is retryable; 4xx usually isn't.
7. Return 2xx to the provider regardless of downstream outcome. Don't let ops-engine-x failures cascade into provider-side webhook-retry storms.

### serx-webhook-ingest specifics

- **Source values:** always `cal_com`. (Not `cal`, not `cal.com`.)
- **Store value:** `serx_webhook_events_raw`.
- **Event names:** copy Cal.com's `triggerEvent` verbatim (UPPERCASE).
- **MCP for agents:** `serx-mcp` — must expose `serx_get_webhook_event({event_id})` that returns the row by its UUID.

### oex-webhook-ingest specifics

- **Source values:** `emailbison`.
- **Store value:** `oex_webhook_events`.
- **Event names:** copy EmailBison event name verbatim (lowercase).
- **MCP for agents:** `oex-mcp` — must expose `oex_get_webhook_event({event_id})`.

### Shared secret

Both ingest apps store `OPEX_AUTH_TOKEN` in their own Doppler (same value as ops-engine-x's Doppler `OPEX_AUTH_TOKEN`). When the value rotates, all three must rotate together.

---

## 6. Why this shape (design history)

Earlier iterations tried:
- **Sending the full payload to `/events/receive`.** Rejected — ingest apps already persist it; shipping it a second time wastes bandwidth and couples the router to payload schemas.
- **Having the ingest app pass `agent_id`.** Rejected — pushes routing knowledge into every caller. Centralizing in `event_routes` means we can re-point an event to a different agent with a SQL update, no redeploy.
- **Source named `cal.com` or `cal`.** Rejected — `.` is brittle (URL paths, query params); `cal` is ambiguous (Cal.com vs Google Calendar vs Apple Calendar). `cal_com` is explicit and path-safe.
- **Pre-resolving `org_id` in the ingest app.** Rejected — each agent already has the MCP access needed to resolve org from event_type. Keeping it in the agent means one fewer cross-service contract.
- **ops-engine-x creating Anthropic sessions inline.** Rejected — session lifecycle is a managed-agents-x concern. Delegating via `/internal/agents/{agent_id}/invoke` keeps `ANTHROPIC_API_KEY` in exactly one place and makes swapping agent providers a single-service change.
- **Putting the `(event → agent)` lookup in managed-agents-x.** Rejected — routing is ops-engine-x's whole job. managed-agents-x is "dumb about routing" by design: it invokes whatever `agent_id` it's told.

---

## 7. Key files in this repo

| File | Purpose |
|---|---|
| [`app/main.py`](../app/main.py) | FastAPI routes — `/events/receive`, `/event-routes/*`, `/scheduled-events/*`, `/internal/scheduler/*`, `/admin/status` |
| [`app/event_routes.py`](../app/event_routes.py) | `event_routes` CRUD module |
| [`app/service_registry.py`](../app/service_registry.py) | Slug (`mag`, `serx`, `oex`) → `(base_url_env, auth_token_env)` registry. `receive_event` + `scheduler_tick` both read through this. |
| [`app/deps.py`](../app/deps.py) | `require_opex_auth` bearer check |
| [`app/config.py`](../app/config.py) | Lazy secret loader |
