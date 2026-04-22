# Environments

> **Beta** -- Requires header `anthropic-beta: managed-agents-2026-04-01`

Environments define the execution context for Claude Managed Agent sessions, including network access policies and pre-installed packages.

---

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/v1/environments` | Create Environment |
| GET | `/v1/environments` | List Environments |
| GET | `/v1/environments/{environment_id}` | Get Environment |
| POST | `/v1/environments/{environment_id}` | Update Environment |
| DELETE | `/v1/environments/{environment_id}` | Delete Environment |
| POST | `/v1/environments/{environment_id}/archive` | Archive Environment |

---

## Create Environment

```
POST /v1/environments
```

Create a new environment with the specified configuration.

### Header Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `anthropic-beta` | `array of AnthropicBeta` | Optional | Optional header to specify the beta version(s) you want to use. |

### Body Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | `string` | **Required** | Human-readable name for the environment |
| `config` | `BetaCloudConfigParams` | Optional | Request params for cloud environment configuration. Fields default to null; on update, omitted fields preserve the existing value. |
| `description` | `string` | Optional | Optional description of the environment |
| `metadata` | `map[string]` | Optional | User-provided metadata key-value pairs |

#### `config` (BetaCloudConfigParams)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | `"cloud"` | **Required** | Environment type |
| `networking` | `BetaUnrestrictedNetwork` or `BetaLimitedNetworkParams` | Optional | Network configuration policy. Omit on update to preserve the existing value. |
| `packages` | `BetaPackagesParams` | Optional | Specify packages (and optionally their versions) available in this environment. When versioning, use the version semantics relevant for the package manager, e.g. for `pip` use `package==1.0.0`. You are responsible for validating the package and version exist. Unversioned installs the latest. |

### Returns

`BetaEnvironment` -- Unified Environment resource for both cloud and BYOC environments.

### Example Request

```bash
curl https://api.anthropic.com/v1/environments \
    -H 'Content-Type: application/json' \
    -H 'anthropic-version: 2023-06-01' \
    -H 'anthropic-beta: managed-agents-2026-04-01' \
    -H "X-Api-Key: $ANTHROPIC_API_KEY" \
    -d '{
          "name": "python-data-analysis",
          "config": {
            "type": "cloud",
            "networking": {
              "type": "limited",
              "allow_package_managers": true,
              "allowed_hosts": [
                "api.example.com"
              ]
            },
            "packages": {
              "pip": [
                "pandas",
                "numpy"
              ]
            }
          }
        }'
```

---

## List Environments

```
GET /v1/environments
```

List environments with pagination support.

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `include_archived` | `boolean` | Optional | Include archived environments in the response |
| `limit` | `number` | Optional | Maximum number of environments to return |
| `page` | `string` | Optional | Opaque cursor from previous response for pagination. Pass the `next_page` value from the previous response. |

### Header Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `anthropic-beta` | `array of AnthropicBeta` | Optional | Optional header to specify the beta version(s) you want to use. |

### Returns

| Field | Type | Description |
|-------|------|-------------|
| `data` | `array of BetaEnvironment` | List of environments. |
| `next_page` | `string` | Token for fetching the next page of results. If `null`, there are no more results available. Pass this value to the `page` parameter in the next request. |

### Example Request

```bash
curl https://api.anthropic.com/v1/environments \
    -H 'anthropic-version: 2023-06-01' \
    -H 'anthropic-beta: managed-agents-2026-04-01' \
    -H "X-Api-Key: $ANTHROPIC_API_KEY"
```

---

## Get Environment

```
GET /v1/environments/{environment_id}
```

Retrieve a specific environment by ID.

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `environment_id` | `string` | **Required** | The environment identifier (e.g., `env_...`) |

### Header Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `anthropic-beta` | `array of AnthropicBeta` | Optional | Optional header to specify the beta version(s) you want to use. |

### Returns

`BetaEnvironment` -- Unified Environment resource for both cloud and BYOC environments.

### Example Request

```bash
curl https://api.anthropic.com/v1/environments/$ENVIRONMENT_ID \
    -H 'anthropic-version: 2023-06-01' \
    -H 'anthropic-beta: managed-agents-2026-04-01' \
    -H "X-Api-Key: $ANTHROPIC_API_KEY"
```

---

## Update Environment

```
POST /v1/environments/{environment_id}
```

Update an existing environment's configuration.

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `environment_id` | `string` | **Required** | The environment identifier (e.g., `env_...`) |

### Header Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `anthropic-beta` | `array of AnthropicBeta` | Optional | Optional header to specify the beta version(s) you want to use. |

### Body Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `config` | `BetaCloudConfigParams` | Optional | Request params for cloud environment configuration. Fields default to null; on update, omitted fields preserve the existing value. |
| `description` | `string` | Optional | Updated description of the environment |
| `metadata` | `map[string]` | Optional | User-provided metadata key-value pairs. Set a value to null or empty string to delete the key. |
| `name` | `string` | Optional | Updated name for the environment |

### Returns

`BetaEnvironment` -- Unified Environment resource for both cloud and BYOC environments.

### Example Request

```bash
curl https://api.anthropic.com/v1/environments/$ENVIRONMENT_ID \
    -H 'Content-Type: application/json' \
    -H 'anthropic-version: 2023-06-01' \
    -H 'anthropic-beta: managed-agents-2026-04-01' \
    -H "X-Api-Key: $ANTHROPIC_API_KEY" \
    -d '{
          "config": {
            "type": "cloud",
            "networking": {
              "type": "limited",
              "allow_package_managers": true,
              "allowed_hosts": [
                "api.example.com"
              ]
            },
            "packages": {
              "pip": [
                "pandas",
                "numpy"
              ]
            }
          }
        }'
```

---

## Delete Environment

```
DELETE /v1/environments/{environment_id}
```

Delete an environment by ID. Returns a confirmation of the deletion.

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `environment_id` | `string` | **Required** | The environment identifier (e.g., `env_...`) |

### Header Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `anthropic-beta` | `array of AnthropicBeta` | Optional | Optional header to specify the beta version(s) you want to use. |

### Returns

`BetaEnvironmentDeleteResponse`

| Field | Type | Description |
|-------|------|-------------|
| `id` | `string` | Environment identifier |
| `type` | `"environment_deleted"` | The type of response |

### Example Request

```bash
curl https://api.anthropic.com/v1/environments/$ENVIRONMENT_ID \
    -X DELETE \
    -H 'anthropic-version: 2023-06-01' \
    -H 'anthropic-beta: managed-agents-2026-04-01' \
    -H "X-Api-Key: $ANTHROPIC_API_KEY"
```

---

## Archive Environment

```
POST /v1/environments/{environment_id}/archive
```

Archive an environment by ID. Archived environments cannot be used to create new sessions.

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `environment_id` | `string` | **Required** | The environment identifier (e.g., `env_...`) |

### Header Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `anthropic-beta` | `array of AnthropicBeta` | Optional | Optional header to specify the beta version(s) you want to use. |

### Returns

`BetaEnvironment` -- Unified Environment resource for both cloud and BYOC environments.

### Example Request

```bash
curl https://api.anthropic.com/v1/environments/$ENVIRONMENT_ID/archive \
    -X POST \
    -H 'anthropic-version: 2023-06-01' \
    -H 'anthropic-beta: managed-agents-2026-04-01' \
    -H "X-Api-Key: $ANTHROPIC_API_KEY"
```

---

## Models / Type Definitions

### BetaEnvironment

Unified Environment resource for both cloud and BYOC environments.

```
BetaEnvironment = object {
  id,
  archived_at,
  config,
  created_at,
  description,
  metadata,
  name,
  type,
  updated_at
}
```

| Field | Type | Description |
|-------|------|-------------|
| `id` | `string` | Environment identifier (e.g., `env_...`) |
| `archived_at` | `string` | RFC 3339 timestamp when environment was archived, or null if not archived |
| `config` | `BetaCloudConfig` | Cloud environment configuration. |
| `created_at` | `string` | RFC 3339 timestamp when environment was created |
| `description` | `string` | User-provided description for the environment |
| `metadata` | `map[string]` | User-provided metadata key-value pairs |
| `name` | `string` | Human-readable name for the environment |
| `type` | `"environment"` | The type of object (always `"environment"`) |
| `updated_at` | `string` | RFC 3339 timestamp when environment was last updated |

---

### BetaCloudConfig

Cloud environment configuration.

```
BetaCloudConfig = object {
  networking,
  packages,
  type
}
```

| Field | Type | Description |
|-------|------|-------------|
| `networking` | `BetaUnrestrictedNetwork` or `BetaLimitedNetwork` | Network configuration policy. |
| `packages` | `BetaPackages` | Package manager configuration. |
| `type` | `"cloud"` | Environment type |

---

### BetaCloudConfigParams

Request params for cloud environment configuration. Fields default to null; on update, omitted fields preserve the existing value.

```
BetaCloudConfigParams = object {
  type,
  networking,
  packages
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | `"cloud"` | **Required** | Environment type |
| `networking` | `BetaUnrestrictedNetwork` or `BetaLimitedNetworkParams` | Optional | Network configuration policy. Omit on update to preserve the existing value. |
| `packages` | `BetaPackagesParams` | Optional | Specify packages (and optionally their versions) available in this environment. When versioning, use the version semantics relevant for the package manager, e.g. for `pip` use `package==1.0.0`. You are responsible for validating the package and version exist. Unversioned installs the latest. |

---

### BetaUnrestrictedNetwork

Unrestricted network access.

```
BetaUnrestrictedNetwork = object {
  type
}
```

| Field | Type | Description |
|-------|------|-------------|
| `type` | `"unrestricted"` | Network policy type |

---

### BetaLimitedNetwork

Limited network access.

```
BetaLimitedNetwork = object {
  allow_mcp_servers,
  allow_package_managers,
  allowed_hosts,
  type
}
```

| Field | Type | Description |
|-------|------|-------------|
| `allow_mcp_servers` | `boolean` | Permits outbound access to MCP server endpoints configured on the agent, beyond those listed in the `allowed_hosts` array. |
| `allow_package_managers` | `boolean` | Permits outbound access to public package registries (PyPI, npm, etc.) beyond those listed in the `allowed_hosts` array. |
| `allowed_hosts` | `array of string` | Specifies domains the container can reach. |
| `type` | `"limited"` | Network policy type |

---

### BetaLimitedNetworkParams

Limited network request params. Fields default to null; on update, omitted fields preserve the existing value.

```
BetaLimitedNetworkParams = object {
  type,
  allow_mcp_servers,
  allow_package_managers,
  allowed_hosts
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | `"limited"` | **Required** | Network policy type |
| `allow_mcp_servers` | `boolean` | Optional | Permits outbound access to MCP server endpoints configured on the agent, beyond those listed in the `allowed_hosts` array. Defaults to `false`. |
| `allow_package_managers` | `boolean` | Optional | Permits outbound access to public package registries (PyPI, npm, etc.) beyond those listed in the `allowed_hosts` array. Defaults to `false`. |
| `allowed_hosts` | `array of string` | Optional | Specifies domains the container can reach. |

---

### BetaPackages

Packages (and their versions) available in this environment.

```
BetaPackages = object {
  apt,
  cargo,
  gem,
  go,
  npm,
  pip,
  type
}
```

| Field | Type | Description |
|-------|------|-------------|
| `apt` | `array of string` | Ubuntu/Debian packages to install |
| `cargo` | `array of string` | Rust packages to install |
| `gem` | `array of string` | Ruby packages to install |
| `go` | `array of string` | Go packages to install |
| `npm` | `array of string` | Node.js packages to install |
| `pip` | `array of string` | Python packages to install |
| `type` | `"packages"` (optional) | Package configuration type |

---

### BetaPackagesParams

Specify packages (and optionally their versions) available in this environment. When versioning, use the version semantics relevant for the package manager, e.g. for `pip` use `package==1.0.0`. You are responsible for validating the package and version exist. Unversioned installs the latest.

```
BetaPackagesParams = object {
  apt,
  cargo,
  gem,
  go,
  npm,
  pip,
  type
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `apt` | `array of string` | Optional | Ubuntu/Debian packages to install |
| `cargo` | `array of string` | Optional | Rust packages to install |
| `gem` | `array of string` | Optional | Ruby packages to install |
| `go` | `array of string` | Optional | Go packages to install |
| `npm` | `array of string` | Optional | Node.js packages to install |
| `pip` | `array of string` | Optional | Python packages to install |
| `type` | `"packages"` | Optional | Package configuration type |

---

### BetaEnvironmentDeleteResponse

Response after deleting an environment.

```
BetaEnvironmentDeleteResponse = object {
  id,
  type
}
```

| Field | Type | Description |
|-------|------|-------------|
| `id` | `string` | Environment identifier |
| `type` | `"environment_deleted"` | The type of response |

---

## AnthropicBeta Header Values

The `anthropic-beta` header accepts an array. Known values:

- `"message-batches-2024-09-24"`
- `"prompt-caching-2024-07-31"`
- `"computer-use-2024-10-22"`
- `"computer-use-2025-01-24"`
- `"pdfs-2024-09-25"`
- `"token-counting-2024-11-01"`
- `"token-efficient-tools-2025-02-19"`
- `"output-128k-2025-02-19"`
- `"files-api-2025-04-14"`
- `"mcp-client-2025-04-04"`
- `"mcp-client-2025-11-20"`
- `"dev-full-thinking-2025-05-14"`
- `"interleaved-thinking-2025-05-14"`
- `"code-execution-2025-05-22"`
- `"extended-cache-ttl-2025-04-11"`
- `"context-1m-2025-08-07"`
- `"context-management-2025-06-27"`
- `"model-context-window-exceeded-2025-08-26"`
- `"skills-2025-10-02"`
- `"fast-mode-2026-02-01"`
- `"output-300k-2026-03-24"`
- `"advisor-tool-2026-03-01"`
