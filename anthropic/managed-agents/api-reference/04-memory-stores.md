# Memory Stores

API reference for Memory Store, Memory, and Memory Version endpoints.

Source: https://platform.claude.com/docs/en/api/beta/memory-stores

> **Note:** The Memory Stores API exists at the backend (endpoints return `401 Authentication` errors, not `404 Not Found`) but public documentation has not been published yet. The page at the source URL above returns a 404. The endpoints below are documented based on API endpoint probing and the patterns established by the other Managed Agents APIs (Vaults, Sessions, Agents, Environments), which all follow the same conventions. This file should be updated once official documentation is published.

---

## Confirmed Endpoints

The following endpoints were confirmed to exist via HTTP probing (all return `401 Authentication` with a valid `anthropic-version` and `anthropic-beta: managed-agents-2026-04-01` header, indicating they are real routes behind authentication):

### Memory Store Endpoints

| Method | Path | Operation |
|--------|------|-----------|
| **POST** | `/v1/memory_stores` | Create Memory Store |
| **GET** | `/v1/memory_stores` | List Memory Stores |
| **GET** | `/v1/memory_stores/{memory_store_id}` | Get Memory Store |
| **POST** | `/v1/memory_stores/{memory_store_id}` | Update Memory Store |
| **DELETE** | `/v1/memory_stores/{memory_store_id}` | Delete Memory Store |
| **POST** | `/v1/memory_stores/{memory_store_id}/archive` | Archive Memory Store |

### Memory Endpoints

| Method | Path | Operation |
|--------|------|-----------|
| **POST** | `/v1/memory_stores/{memory_store_id}/memories` | Write Memory |
| **GET** | `/v1/memory_stores/{memory_store_id}/memories` | List Memories |
| **GET** | `/v1/memory_stores/{memory_store_id}/memories/{memory_id}` | Get Memory |
| **POST** | `/v1/memory_stores/{memory_store_id}/memories/{memory_id}` | Update Memory |
| **DELETE** | `/v1/memory_stores/{memory_store_id}/memories/{memory_id}` | Delete Memory |

### Memory Version Endpoints

Memory Version endpoints (`/versions`, `/redact`) were probed and returned `404 page not found`, indicating they are **not yet implemented** at the API level.

---

## Expected Request Headers

Based on the managed agents API conventions:

- `anthropic-version`: required `string` (e.g., `2023-06-01`)
- `anthropic-beta`: required `string` - Must include `managed-agents-2026-04-01`
- `x-api-key`: required `string` - Your Anthropic API key
- `content-type`: `application/json` (for POST requests)

---

## Expected Patterns

Based on the Vaults, Agents, Sessions, and Environments APIs which all follow identical CRUD conventions:

### Create Memory Store

**POST** `/v1/memory_stores`

Expected to accept a JSON body with fields like `display_name` (or `name`) and optional `metadata`, and return a Memory Store object with `id`, `type`, `created_at`, `updated_at`, `archived_at`, and `metadata`.

```bash
curl https://api.anthropic.com/v1/memory_stores \
    -H 'Content-Type: application/json' \
    -H 'anthropic-version: 2023-06-01' \
    -H 'anthropic-beta: managed-agents-2026-04-01' \
    -H "X-Api-Key: $ANTHROPIC_API_KEY" \
    -d '{
          "display_name": "Project knowledge base"
        }'
```

### List Memory Stores

**GET** `/v1/memory_stores`

Expected query parameters (following Vaults pattern):
- `include_archived`: optional `boolean`
- `limit`: optional `number` (default 20, max 100)
- `page`: optional `string` (opaque pagination token)

```bash
curl https://api.anthropic.com/v1/memory_stores \
    -H 'anthropic-version: 2023-06-01' \
    -H 'anthropic-beta: managed-agents-2026-04-01' \
    -H "X-Api-Key: $ANTHROPIC_API_KEY"
```

### Get Memory Store

**GET** `/v1/memory_stores/{memory_store_id}`

```bash
curl https://api.anthropic.com/v1/memory_stores/$MEMORY_STORE_ID \
    -H 'anthropic-version: 2023-06-01' \
    -H 'anthropic-beta: managed-agents-2026-04-01' \
    -H "X-Api-Key: $ANTHROPIC_API_KEY"
```

### Update Memory Store

**POST** `/v1/memory_stores/{memory_store_id}`

```bash
curl https://api.anthropic.com/v1/memory_stores/$MEMORY_STORE_ID \
    -H 'Content-Type: application/json' \
    -H 'anthropic-version: 2023-06-01' \
    -H 'anthropic-beta: managed-agents-2026-04-01' \
    -H "X-Api-Key: $ANTHROPIC_API_KEY" \
    -d '{
          "display_name": "Updated name"
        }'
```

### Delete Memory Store

**DELETE** `/v1/memory_stores/{memory_store_id}`

```bash
curl https://api.anthropic.com/v1/memory_stores/$MEMORY_STORE_ID \
    -X DELETE \
    -H 'anthropic-version: 2023-06-01' \
    -H 'anthropic-beta: managed-agents-2026-04-01' \
    -H "X-Api-Key: $ANTHROPIC_API_KEY"
```

### Archive Memory Store

**POST** `/v1/memory_stores/{memory_store_id}/archive`

```bash
curl https://api.anthropic.com/v1/memory_stores/$MEMORY_STORE_ID/archive \
    -X POST \
    -H 'anthropic-version: 2023-06-01' \
    -H 'anthropic-beta: managed-agents-2026-04-01' \
    -H "X-Api-Key: $ANTHROPIC_API_KEY"
```

### Write Memory

**POST** `/v1/memory_stores/{memory_store_id}/memories`

```bash
curl https://api.anthropic.com/v1/memory_stores/$MEMORY_STORE_ID/memories \
    -H 'Content-Type: application/json' \
    -H 'anthropic-version: 2023-06-01' \
    -H 'anthropic-beta: managed-agents-2026-04-01' \
    -H "X-Api-Key: $ANTHROPIC_API_KEY" \
    -d '{
          "content": "The user prefers Python over JavaScript for backend services."
        }'
```

### List Memories

**GET** `/v1/memory_stores/{memory_store_id}/memories`

```bash
curl https://api.anthropic.com/v1/memory_stores/$MEMORY_STORE_ID/memories \
    -H 'anthropic-version: 2023-06-01' \
    -H 'anthropic-beta: managed-agents-2026-04-01' \
    -H "X-Api-Key: $ANTHROPIC_API_KEY"
```

### Get Memory

**GET** `/v1/memory_stores/{memory_store_id}/memories/{memory_id}`

```bash
curl https://api.anthropic.com/v1/memory_stores/$MEMORY_STORE_ID/memories/$MEMORY_ID \
    -H 'anthropic-version: 2023-06-01' \
    -H 'anthropic-beta: managed-agents-2026-04-01' \
    -H "X-Api-Key: $ANTHROPIC_API_KEY"
```

### Update Memory

**POST** `/v1/memory_stores/{memory_store_id}/memories/{memory_id}`

```bash
curl https://api.anthropic.com/v1/memory_stores/$MEMORY_STORE_ID/memories/$MEMORY_ID \
    -H 'Content-Type: application/json' \
    -H 'anthropic-version: 2023-06-01' \
    -H 'anthropic-beta: managed-agents-2026-04-01' \
    -H "X-Api-Key: $ANTHROPIC_API_KEY" \
    -d '{}'
```

### Delete Memory

**DELETE** `/v1/memory_stores/{memory_store_id}/memories/{memory_id}`

```bash
curl https://api.anthropic.com/v1/memory_stores/$MEMORY_STORE_ID/memories/$MEMORY_ID \
    -X DELETE \
    -H 'anthropic-version: 2023-06-01' \
    -H 'anthropic-beta: managed-agents-2026-04-01' \
    -H "X-Api-Key: $ANTHROPIC_API_KEY"
```

---

## Memory Version Endpoints (Not Yet Available)

The following endpoints were probed and returned `404`, indicating they are not yet implemented:

- `GET /v1/memory_stores/{memory_store_id}/memories/{memory_id}/versions` - List Memory Versions
- `GET /v1/memory_stores/{memory_store_id}/memories/{memory_id}/versions/{version_id}` - Get Memory Version
- `POST /v1/memory_stores/{memory_store_id}/memories/{memory_id}/redact` - Redact Memory Version

---

## Status

- **API endpoints**: Memory Store and Memory CRUD endpoints exist and are routed (return 401 behind auth).
- **Memory Version endpoints**: Not yet routed (return 404).
- **SDK support**: Not present in `anthropic-sdk-python` or `anthropic-sdk-typescript` as of the current release.
- **OpenAPI spec**: Not included in the published Stainless-generated OpenAPI spec.
- **Documentation**: Not published at `platform.claude.com/docs/en/api/beta/memory-stores` or any variant URL.

This file should be replaced with full verbatim documentation once Anthropic publishes the Memory Stores API reference.
