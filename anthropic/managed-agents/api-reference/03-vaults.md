# Vaults

API reference for Vault and Credential endpoints.

Source: https://platform.claude.com/docs/en/api/beta/vaults

---

## Vaults

### Create Vault

**POST** `/v1/vaults`

Create a new vault.

#### Header Parameters

- `anthropic-beta`: optional `array of AnthropicBeta`
  Optional header to specify the beta version(s) you want to use.

- `anthropic-version`: required `string`
  API version (e.g., `2023-06-01`).

- `x-api-key`: required `string`
  Your Anthropic API key.

#### Body Parameters

- `display_name`: required `string`
  Human-readable name for the vault. 1-255 characters.

- `metadata`: optional `map[string]`
  Arbitrary key-value metadata to attach to the vault. Maximum 16 pairs, keys up to 64 chars, values up to 512 chars.

#### Returns

`BetaManagedAgentsVault` object:

- `id`: `string` - Unique identifier for the vault.
- `archived_at`: `string` - A timestamp in RFC 3339 format.
- `created_at`: `string` - A timestamp in RFC 3339 format.
- `display_name`: `string` - Human-readable name for the vault.
- `metadata`: `map[string]` - Arbitrary key-value metadata attached to the vault.
- `type`: `"vault"`.
- `updated_at`: `string` - A timestamp in RFC 3339 format.

#### Example Request

```bash
curl https://api.anthropic.com/v1/vaults \
    -H 'Content-Type: application/json' \
    -H 'anthropic-version: 2023-06-01' \
    -H 'anthropic-beta: managed-agents-2026-04-01' \
    -H "X-Api-Key: $ANTHROPIC_API_KEY" \
    -d '{
          "display_name": "Example vault"
        }'
```

#### Example Response

```json
{
  "id": "vault_01abc123",
  "archived_at": null,
  "created_at": "2026-04-11T12:00:00Z",
  "display_name": "Example vault",
  "metadata": {},
  "type": "vault",
  "updated_at": "2026-04-11T12:00:00Z"
}
```

---

### List Vaults

**GET** `/v1/vaults`

List all vaults.

#### Query Parameters

- `include_archived`: optional `boolean`
  Whether to include archived vaults in the results.

- `limit`: optional `number`
  Maximum number of vaults to return per page. Defaults to 20, maximum 100.

- `page`: optional `string`
  Opaque pagination token from a previous `list_vaults` response.

#### Header Parameters

- `anthropic-beta`: optional `array of AnthropicBeta`
  Optional header to specify the beta version(s) you want to use.

#### Returns

- `data`: optional `array of BetaManagedAgentsVault`
  List of vaults. Each vault object contains:
  - `id`: `string` - Unique identifier for the vault.
  - `archived_at`: `string` - A timestamp in RFC 3339 format.
  - `created_at`: `string` - A timestamp in RFC 3339 format.
  - `display_name`: `string` - Human-readable name for the vault.
  - `metadata`: `map[string]` - Arbitrary key-value metadata attached to the vault.
  - `type`: `"vault"`.
  - `updated_at`: `string` - A timestamp in RFC 3339 format.

- `next_page`: optional `string`
  Pagination token for the next page, or null if no more results.

#### Example Request

```bash
curl https://api.anthropic.com/v1/vaults \
    -H 'anthropic-version: 2023-06-01' \
    -H 'anthropic-beta: managed-agents-2026-04-01' \
    -H "X-Api-Key: $ANTHROPIC_API_KEY"
```

#### Example Response

```json
{
  "data": [
    {
      "id": "vault_01abc123",
      "archived_at": null,
      "created_at": "2026-04-11T12:00:00Z",
      "display_name": "Example vault",
      "metadata": {},
      "type": "vault",
      "updated_at": "2026-04-11T12:00:00Z"
    }
  ],
  "next_page": null
}
```

---

### Get Vault

**GET** `/v1/vaults/{vault_id}`

Retrieve a single vault by ID.

#### Path Parameters

- `vault_id`: required `string`

#### Header Parameters

- `anthropic-beta`: optional `array of AnthropicBeta`
  Optional header to specify the beta version(s) you want to use.

#### Returns

`BetaManagedAgentsVault` object:

- `id`: `string` - Unique identifier for the vault.
- `archived_at`: `string` - A timestamp in RFC 3339 format.
- `created_at`: `string` - A timestamp in RFC 3339 format.
- `display_name`: `string` - Human-readable name for the vault.
- `metadata`: `map[string]` - Arbitrary key-value metadata attached to the vault.
- `type`: `"vault"`.
- `updated_at`: `string` - A timestamp in RFC 3339 format.

#### Example Request

```bash
curl https://api.anthropic.com/v1/vaults/$VAULT_ID \
    -H 'anthropic-version: 2023-06-01' \
    -H 'anthropic-beta: managed-agents-2026-04-01' \
    -H "X-Api-Key: $ANTHROPIC_API_KEY"
```

---

### Update Vault

**POST** `/v1/vaults/{vault_id}`

Update an existing vault.

#### Path Parameters

- `vault_id`: required `string`

#### Header Parameters

- `anthropic-beta`: optional `array of AnthropicBeta`
  Optional header to specify the beta version(s) you want to use.

#### Body Parameters

- `display_name`: optional `string`
  Updated human-readable name for the vault. 1-255 characters.

- `metadata`: optional `map[string]`
  Metadata patch. Set a key to a string to upsert it, or to null to delete it. Omitted keys are preserved.

#### Returns

`BetaManagedAgentsVault` object (same schema as Create Vault response).

#### Example Request

```bash
curl https://api.anthropic.com/v1/vaults/$VAULT_ID \
    -H 'Content-Type: application/json' \
    -H 'anthropic-version: 2023-06-01' \
    -H 'anthropic-beta: managed-agents-2026-04-01' \
    -H "X-Api-Key: $ANTHROPIC_API_KEY" \
    -d '{}'
```

---

### Delete Vault

**DELETE** `/v1/vaults/{vault_id}`

Permanently delete a vault.

#### Path Parameters

- `vault_id`: required `string`

#### Header Parameters

- `anthropic-beta`: optional `array of AnthropicBeta`
  Optional header to specify the beta version(s) you want to use.

#### Returns

`BetaManagedAgentsDeletedVault` object:

- `id`: `string` - Unique identifier of the deleted vault.
- `type`: `"vault_deleted"`.

#### Example Request

```bash
curl https://api.anthropic.com/v1/vaults/$VAULT_ID \
    -X DELETE \
    -H 'anthropic-version: 2023-06-01' \
    -H 'anthropic-beta: managed-agents-2026-04-01' \
    -H "X-Api-Key: $ANTHROPIC_API_KEY"
```

#### Example Response

```json
{
  "id": "vault_01abc123",
  "type": "vault_deleted"
}
```

---

### Archive Vault

**POST** `/v1/vaults/{vault_id}/archive`

Archive a vault (soft-delete, reversible).

#### Path Parameters

- `vault_id`: required `string`

#### Header Parameters

- `anthropic-beta`: optional `array of AnthropicBeta`
  Optional header to specify the beta version(s) you want to use.

#### Returns

`BetaManagedAgentsVault` object (same schema as Create Vault response, with `archived_at` populated).

#### Example Request

```bash
curl https://api.anthropic.com/v1/vaults/$VAULT_ID/archive \
    -X POST \
    -H 'anthropic-version: 2023-06-01' \
    -H 'anthropic-beta: managed-agents-2026-04-01' \
    -H "X-Api-Key: $ANTHROPIC_API_KEY"
```

---

## Credentials

### Create Credential

**POST** `/v1/vaults/{vault_id}/credentials`

Create a new credential within a vault.

#### Path Parameters

- `vault_id`: required `string`

#### Header Parameters

- `anthropic-beta`: optional `array of AnthropicBeta`
  Optional header to specify the beta version(s) you want to use.

#### Body Parameters

- `auth`: required - Authentication details for creating a credential. Accepts one of the following:

  **Option A: `BetaManagedAgentsMCPOAuthCreateParams`** - Parameters for creating an MCP OAuth credential.
  - `access_token`: required `string` - OAuth access token.
  - `mcp_server_url`: required `string` - URL of the MCP server this credential authenticates against.
  - `type`: required `"mcp_oauth"`.
  - `expires_at`: optional `string` - A timestamp in RFC 3339 format.
  - `refresh`: optional `BetaManagedAgentsMCPOAuthRefreshParams` - OAuth refresh token parameters.
    - `client_id`: required `string` - OAuth client ID.
    - `refresh_token`: required `string` - OAuth refresh token.
    - `token_endpoint`: required `string` - Token endpoint URL used to refresh the access token.
    - `token_endpoint_auth`: required - Token endpoint authentication method. One of:
      - `BetaManagedAgentsTokenEndpointAuthNoneParam`: `{ type: "none" }` - No client authentication.
      - `BetaManagedAgentsTokenEndpointAuthBasicParam`: `{ client_secret: string, type: "client_secret_basic" }` - HTTP Basic authentication.
      - `BetaManagedAgentsTokenEndpointAuthPostParam`: `{ client_secret: string, type: "client_secret_post" }` - POST body authentication.
    - `resource`: optional `string` - OAuth resource indicator.
    - `scope`: optional `string` - OAuth scope for the refresh request.

  **Option B: `BetaManagedAgentsStaticBearerCreateParams`** - Parameters for creating a static bearer token credential.
  - `token`: required `string` - Static bearer token value.
  - `mcp_server_url`: required `string` - URL of the MCP server this credential authenticates against.
  - `type`: required `"static_bearer"`.

- `display_name`: optional `string`
  Human-readable name for the credential. Up to 255 characters.

- `metadata`: optional `map[string]`
  Arbitrary key-value metadata to attach to the credential. Maximum 16 pairs, keys up to 64 chars, values up to 512 chars.

#### Returns

`BetaManagedAgentsCredential` object:

- `id`: `string` - Unique identifier for the credential.
- `archived_at`: `string` - A timestamp in RFC 3339 format.
- `auth`: one of:
  - `BetaManagedAgentsMCPOAuthAuthResponse`:
    - `mcp_server_url`: `string` - URL of the MCP server this credential authenticates against.
    - `type`: `"mcp_oauth"`.
    - `expires_at`: optional `string` - A timestamp in RFC 3339 format.
    - `refresh`: optional `BetaManagedAgentsMCPOAuthRefreshResponse`:
      - `client_id`: `string` - OAuth client ID.
      - `token_endpoint`: `string` - Token endpoint URL used to refresh the access token.
      - `token_endpoint_auth`: one of:
        - `{ type: "none" }` - No client authentication.
        - `{ type: "client_secret_basic" }` - HTTP Basic authentication.
        - `{ type: "client_secret_post" }` - POST body authentication.
      - `resource`: optional `string` - OAuth resource indicator.
      - `scope`: optional `string` - OAuth scope for the refresh request.
  - `BetaManagedAgentsStaticBearerAuthResponse`:
    - `mcp_server_url`: `string` - URL of the MCP server this credential authenticates against.
    - `type`: `"static_bearer"`.
- `created_at`: `string` - A timestamp in RFC 3339 format.
- `metadata`: `map[string]` - Arbitrary key-value metadata attached to the credential.
- `type`: `"vault_credential"`.
- `updated_at`: `string` - A timestamp in RFC 3339 format.
- `vault_id`: `string` - Identifier of the vault this credential belongs to.
- `display_name`: optional `string` - Human-readable name for the credential.

#### Example Request

```bash
curl https://api.anthropic.com/v1/vaults/$VAULT_ID/credentials \
    -H 'Content-Type: application/json' \
    -H 'anthropic-version: 2023-06-01' \
    -H 'anthropic-beta: managed-agents-2026-04-01' \
    -H "X-Api-Key: $ANTHROPIC_API_KEY" \
    -d '{
          "auth": {
            "token": "bearer_exampletoken",
            "mcp_server_url": "https://example-server.modelcontextprotocol.io/sse",
            "type": "static_bearer"
          }
        }'
```

#### Example Response

```json
{
  "id": "cred_01abc123",
  "archived_at": null,
  "auth": {
    "mcp_server_url": "https://example-server.modelcontextprotocol.io/sse",
    "type": "static_bearer"
  },
  "created_at": "2026-04-11T12:00:00Z",
  "metadata": {},
  "type": "vault_credential",
  "updated_at": "2026-04-11T12:00:00Z",
  "vault_id": "vault_01abc123",
  "display_name": null
}
```

---

### List Credentials

**GET** `/v1/vaults/{vault_id}/credentials`

List credentials in a vault.

#### Path Parameters

- `vault_id`: required `string`

#### Query Parameters

- `include_archived`: optional `boolean`
  Whether to include archived credentials in the results.

- `limit`: optional `number`
  Maximum number of credentials to return per page. Defaults to 20, maximum 100.

- `page`: optional `string`
  Opaque pagination token from a previous `list_credentials` response.

#### Header Parameters

- `anthropic-beta`: optional `array of AnthropicBeta`
  Optional header to specify the beta version(s) you want to use.

#### Returns

- `data`: optional `array of BetaManagedAgentsCredential`
  List of credentials. Each credential contains the same fields as the Create Credential response.

- `next_page`: optional `string`
  Pagination token for the next page, or null if no more results.

#### Example Request

```bash
curl https://api.anthropic.com/v1/vaults/$VAULT_ID/credentials \
    -H 'anthropic-version: 2023-06-01' \
    -H 'anthropic-beta: managed-agents-2026-04-01' \
    -H "X-Api-Key: $ANTHROPIC_API_KEY"
```

#### Example Response

```json
{
  "data": [
    {
      "id": "cred_01abc123",
      "archived_at": null,
      "auth": {
        "mcp_server_url": "https://example-server.modelcontextprotocol.io/sse",
        "type": "static_bearer"
      },
      "created_at": "2026-04-11T12:00:00Z",
      "metadata": {},
      "type": "vault_credential",
      "updated_at": "2026-04-11T12:00:00Z",
      "vault_id": "vault_01abc123",
      "display_name": null
    }
  ],
  "next_page": null
}
```

---

### Get Credential

**GET** `/v1/vaults/{vault_id}/credentials/{credential_id}`

Retrieve a single credential by ID.

#### Path Parameters

- `vault_id`: required `string`
- `credential_id`: required `string`

#### Header Parameters

- `anthropic-beta`: optional `array of AnthropicBeta`
  Optional header to specify the beta version(s) you want to use.

#### Returns

`BetaManagedAgentsCredential` object (same schema as Create Credential response).

#### Example Request

```bash
curl https://api.anthropic.com/v1/vaults/$VAULT_ID/credentials/$CREDENTIAL_ID \
    -H 'anthropic-version: 2023-06-01' \
    -H 'anthropic-beta: managed-agents-2026-04-01' \
    -H "X-Api-Key: $ANTHROPIC_API_KEY"
```

---

### Update Credential

**POST** `/v1/vaults/{vault_id}/credentials/{credential_id}`

Update an existing credential. The `mcp_server_url` is immutable.

#### Path Parameters

- `vault_id`: required `string`
- `credential_id`: required `string`

#### Header Parameters

- `anthropic-beta`: optional `array of AnthropicBeta`
  Optional header to specify the beta version(s) you want to use.

#### Body Parameters

- `auth`: optional - Updated authentication details. Accepts one of the following:

  **Option A: `BetaManagedAgentsMCPOAuthUpdateParams`** - Parameters for updating an MCP OAuth credential. The `mcp_server_url` is immutable.
  - `type`: required `"mcp_oauth"`.
  - `access_token`: optional `string` - Updated OAuth access token.
  - `expires_at`: optional `string` - A timestamp in RFC 3339 format.
  - `refresh`: optional `BetaManagedAgentsMCPOAuthRefreshUpdateParams`:
    - `refresh_token`: optional `string` - Updated OAuth refresh token.
    - `scope`: optional `string` - Updated OAuth scope for the refresh request.
    - `token_endpoint_auth`: optional - Updated token endpoint authentication. One of:
      - `BetaManagedAgentsTokenEndpointAuthBasicUpdateParam`: `{ type: "client_secret_basic", client_secret: optional string }`.
      - `BetaManagedAgentsTokenEndpointAuthPostUpdateParam`: `{ type: "client_secret_post", client_secret: optional string }`.

  **Option B: `BetaManagedAgentsStaticBearerUpdateParams`** - Parameters for updating a static bearer token credential. The `mcp_server_url` is immutable.
  - `type`: required `"static_bearer"`.
  - `token`: optional `string` - Updated static bearer token value.

- `display_name`: optional `string`
  Updated human-readable name for the credential. 1-255 characters.

- `metadata`: optional `map[string]`
  Metadata patch. Set a key to a string to upsert it, or to null to delete it. Omitted keys are preserved.

#### Returns

`BetaManagedAgentsCredential` object (same schema as Create Credential response).

#### Example Request

```bash
curl https://api.anthropic.com/v1/vaults/$VAULT_ID/credentials/$CREDENTIAL_ID \
    -H 'Content-Type: application/json' \
    -H 'anthropic-version: 2023-06-01' \
    -H 'anthropic-beta: managed-agents-2026-04-01' \
    -H "X-Api-Key: $ANTHROPIC_API_KEY" \
    -d '{}'
```

---

### Delete Credential

**DELETE** `/v1/vaults/{vault_id}/credentials/{credential_id}`

Permanently delete a credential.

#### Path Parameters

- `vault_id`: required `string`
- `credential_id`: required `string`

#### Header Parameters

- `anthropic-beta`: optional `array of AnthropicBeta`
  Optional header to specify the beta version(s) you want to use.

#### Returns

`BetaManagedAgentsDeletedCredential` object:

- `id`: `string` - Unique identifier of the deleted credential.
- `type`: `"vault_credential_deleted"`.

#### Example Request

```bash
curl https://api.anthropic.com/v1/vaults/$VAULT_ID/credentials/$CREDENTIAL_ID \
    -X DELETE \
    -H 'anthropic-version: 2023-06-01' \
    -H 'anthropic-beta: managed-agents-2026-04-01' \
    -H "X-Api-Key: $ANTHROPIC_API_KEY"
```

#### Example Response

```json
{
  "id": "cred_01abc123",
  "type": "vault_credential_deleted"
}
```

---

### Archive Credential

**POST** `/v1/vaults/{vault_id}/credentials/{credential_id}/archive`

Archive a credential (soft-delete, reversible).

#### Path Parameters

- `vault_id`: required `string`
- `credential_id`: required `string`

#### Header Parameters

- `anthropic-beta`: optional `array of AnthropicBeta`
  Optional header to specify the beta version(s) you want to use.

#### Returns

`BetaManagedAgentsCredential` object (same schema as Create Credential response, with `archived_at` populated).

#### Example Request

```bash
curl https://api.anthropic.com/v1/vaults/$VAULT_ID/credentials/$CREDENTIAL_ID/archive \
    -X POST \
    -H 'anthropic-version: 2023-06-01' \
    -H 'anthropic-beta: managed-agents-2026-04-01' \
    -H "X-Api-Key: $ANTHROPIC_API_KEY"
```

---

## Domain Types

### BetaManagedAgentsVault

A vault that stores credentials for use by agents during sessions.

| Field | Type | Description |
|-------|------|-------------|
| `id` | `string` | Unique identifier for the vault. |
| `archived_at` | `string` | A timestamp in RFC 3339 format. |
| `created_at` | `string` | A timestamp in RFC 3339 format. |
| `display_name` | `string` | Human-readable name for the vault. |
| `metadata` | `map[string]` | Arbitrary key-value metadata attached to the vault. |
| `type` | `"vault"` | Object type discriminator. |
| `updated_at` | `string` | A timestamp in RFC 3339 format. |

### BetaManagedAgentsDeletedVault

Confirmation of a deleted vault.

| Field | Type | Description |
|-------|------|-------------|
| `id` | `string` | Unique identifier of the deleted vault. |
| `type` | `"vault_deleted"` | Object type discriminator. |

### BetaManagedAgentsCredential

A credential stored in a vault. Sensitive fields are never returned in responses.

| Field | Type | Description |
|-------|------|-------------|
| `id` | `string` | Unique identifier for the credential. |
| `archived_at` | `string` | A timestamp in RFC 3339 format. |
| `auth` | `BetaManagedAgentsMCPOAuthAuthResponse` or `BetaManagedAgentsStaticBearerAuthResponse` | Authentication details for a credential. |
| `created_at` | `string` | A timestamp in RFC 3339 format. |
| `metadata` | `map[string]` | Arbitrary key-value metadata attached to the credential. |
| `type` | `"vault_credential"` | Object type discriminator. |
| `updated_at` | `string` | A timestamp in RFC 3339 format. |
| `vault_id` | `string` | Identifier of the vault this credential belongs to. |
| `display_name` | optional `string` | Human-readable name for the credential. |

### BetaManagedAgentsDeletedCredential

Confirmation of a deleted credential.

| Field | Type | Description |
|-------|------|-------------|
| `id` | `string` | Unique identifier of the deleted credential. |
| `type` | `"vault_credential_deleted"` | Object type discriminator. |

### BetaManagedAgentsMCPOAuthAuthResponse

OAuth credential details for an MCP server.

| Field | Type | Description |
|-------|------|-------------|
| `mcp_server_url` | `string` | URL of the MCP server this credential authenticates against. |
| `type` | `"mcp_oauth"` | Auth type discriminator. |
| `expires_at` | optional `string` | A timestamp in RFC 3339 format. |
| `refresh` | optional `BetaManagedAgentsMCPOAuthRefreshResponse` | OAuth refresh token configuration returned in credential responses. |

### BetaManagedAgentsMCPOAuthCreateParams

Parameters for creating an MCP OAuth credential.

| Field | Type | Description |
|-------|------|-------------|
| `access_token` | `string` | OAuth access token. |
| `mcp_server_url` | `string` | URL of the MCP server this credential authenticates against. |
| `type` | `"mcp_oauth"` | Auth type discriminator. |
| `expires_at` | optional `string` | A timestamp in RFC 3339 format. |
| `refresh` | optional `BetaManagedAgentsMCPOAuthRefreshParams` | OAuth refresh token parameters for creating a credential with refresh support. |

### BetaManagedAgentsMCPOAuthRefreshParams

OAuth refresh token parameters for creating a credential with refresh support.

| Field | Type | Description |
|-------|------|-------------|
| `client_id` | `string` | OAuth client ID. |
| `refresh_token` | `string` | OAuth refresh token. |
| `token_endpoint` | `string` | Token endpoint URL used to refresh the access token. |
| `token_endpoint_auth` | `TokenEndpointAuthNoneParam` or `TokenEndpointAuthBasicParam` or `TokenEndpointAuthPostParam` | Token endpoint authentication method. |
| `resource` | optional `string` | OAuth resource indicator. |
| `scope` | optional `string` | OAuth scope for the refresh request. |

### BetaManagedAgentsMCPOAuthRefreshResponse

OAuth refresh token configuration returned in credential responses.

| Field | Type | Description |
|-------|------|-------------|
| `client_id` | `string` | OAuth client ID. |
| `token_endpoint` | `string` | Token endpoint URL used to refresh the access token. |
| `token_endpoint_auth` | `TokenEndpointAuthNoneResponse` or `TokenEndpointAuthBasicResponse` or `TokenEndpointAuthPostResponse` | Token endpoint authentication method. |
| `resource` | optional `string` | OAuth resource indicator. |
| `scope` | optional `string` | OAuth scope for the refresh request. |

### BetaManagedAgentsMCPOAuthRefreshUpdateParams

Parameters for updating OAuth refresh token configuration.

| Field | Type | Description |
|-------|------|-------------|
| `refresh_token` | optional `string` | Updated OAuth refresh token. |
| `scope` | optional `string` | Updated OAuth scope for the refresh request. |
| `token_endpoint_auth` | optional `TokenEndpointAuthBasicUpdateParam` or `TokenEndpointAuthPostUpdateParam` | Updated token endpoint authentication parameters. |

### BetaManagedAgentsMCPOAuthUpdateParams

Parameters for updating an MCP OAuth credential. The `mcp_server_url` is immutable.

| Field | Type | Description |
|-------|------|-------------|
| `type` | `"mcp_oauth"` | Auth type discriminator. |
| `access_token` | optional `string` | Updated OAuth access token. |
| `expires_at` | optional `string` | A timestamp in RFC 3339 format. |
| `refresh` | optional `BetaManagedAgentsMCPOAuthRefreshUpdateParams` | Parameters for updating OAuth refresh token configuration. |

### BetaManagedAgentsStaticBearerAuthResponse

Static bearer token credential details for an MCP server.

| Field | Type | Description |
|-------|------|-------------|
| `mcp_server_url` | `string` | URL of the MCP server this credential authenticates against. |
| `type` | `"static_bearer"` | Auth type discriminator. |

### BetaManagedAgentsStaticBearerCreateParams

Parameters for creating a static bearer token credential.

| Field | Type | Description |
|-------|------|-------------|
| `token` | `string` | Static bearer token value. |
| `mcp_server_url` | `string` | URL of the MCP server this credential authenticates against. |
| `type` | `"static_bearer"` | Auth type discriminator. |

### BetaManagedAgentsStaticBearerUpdateParams

Parameters for updating a static bearer token credential. The `mcp_server_url` is immutable.

| Field | Type | Description |
|-------|------|-------------|
| `type` | `"static_bearer"` | Auth type discriminator. |
| `token` | optional `string` | Updated static bearer token value. |

### BetaManagedAgentsTokenEndpointAuthNoneParam

Token endpoint requires no client authentication.

| Field | Type | Description |
|-------|------|-------------|
| `type` | `"none"` | Auth method discriminator. |

### BetaManagedAgentsTokenEndpointAuthNoneResponse

Token endpoint requires no client authentication.

| Field | Type | Description |
|-------|------|-------------|
| `type` | `"none"` | Auth method discriminator. |

### BetaManagedAgentsTokenEndpointAuthBasicParam

Token endpoint uses HTTP Basic authentication with client credentials.

| Field | Type | Description |
|-------|------|-------------|
| `client_secret` | `string` | OAuth client secret. |
| `type` | `"client_secret_basic"` | Auth method discriminator. |

### BetaManagedAgentsTokenEndpointAuthBasicResponse

Token endpoint uses HTTP Basic authentication with client credentials.

| Field | Type | Description |
|-------|------|-------------|
| `type` | `"client_secret_basic"` | Auth method discriminator. |

### BetaManagedAgentsTokenEndpointAuthBasicUpdateParam

Updated HTTP Basic authentication parameters for the token endpoint.

| Field | Type | Description |
|-------|------|-------------|
| `type` | `"client_secret_basic"` | Auth method discriminator. |
| `client_secret` | optional `string` | Updated OAuth client secret. |

### BetaManagedAgentsTokenEndpointAuthPostParam

Token endpoint uses POST body authentication with client credentials.

| Field | Type | Description |
|-------|------|-------------|
| `client_secret` | `string` | OAuth client secret. |
| `type` | `"client_secret_post"` | Auth method discriminator. |

### BetaManagedAgentsTokenEndpointAuthPostResponse

Token endpoint uses POST body authentication with client credentials.

| Field | Type | Description |
|-------|------|-------------|
| `type` | `"client_secret_post"` | Auth method discriminator. |

### BetaManagedAgentsTokenEndpointAuthPostUpdateParam

Updated POST body authentication parameters for the token endpoint.

| Field | Type | Description |
|-------|------|-------------|
| `type` | `"client_secret_post"` | Auth method discriminator. |
| `client_secret` | optional `string` | Updated OAuth client secret. |
