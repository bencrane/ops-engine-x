# Agents API Reference

Source: https://platform.claude.com/docs/en/api/beta/agents

All agent endpoints require the `anthropic-beta: managed-agents-2026-04-01` header.

---

## Create Agent

**POST** `/v1/agents`

Creates a new Claude agent with specified configuration.

### Headers

| Header | Required | Description |
|--------|----------|-------------|
| `Content-Type` | Yes | `application/json` |
| `anthropic-version` | Yes | `2023-06-01` |
| `anthropic-beta` | Yes | `managed-agents-2026-04-01` |
| `X-Api-Key` | Yes | Your Anthropic API key |

### Request Body

#### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `model` | `BetaManagedAgentsModel \| BetaManagedAgentsModelConfigParams` | Model identifier (string) or configuration object. |
| `name` | `string` | Human-readable name for the agent. 1-256 characters. |

#### Optional Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `description` | `string` | Up to 2048 characters | Description of what the agent does. |
| `system` | `string` | Up to 100,000 characters | System prompt for the agent. |
| `metadata` | `map[string]` | Max 16 pairs, keys up to 64 chars, values up to 512 chars | Arbitrary key-value metadata. |
| `mcp_servers` | `array of BetaManagedAgentsURLMCPServerParams` | Maximum 20, names must be unique | MCP servers this agent connects to. |
| `skills` | `array of BetaManagedAgentsSkillParams` | Maximum 20 | Skills available to the agent. |
| `tools` | `array of (BetaManagedAgentsAgentToolset20260401Params \| BetaManagedAgentsMCPToolsetParams \| BetaManagedAgentsCustomToolParams)` | Maximum 128 tools across all toolsets | Tool configurations available to the agent. |

#### Model Parameter

The `model` field can be specified as a string or object.

**String format (BetaManagedAgentsModel):**

| Value | Description |
|-------|-------------|
| `"claude-opus-4-6"` | Most intelligent model for building agents and coding |
| `"claude-sonnet-4-6"` | Best combination of speed and intelligence |
| `"claude-haiku-4-5"` | Fastest model with near-frontier intelligence |
| `"claude-haiku-4-5-20251001"` | Fastest model with near-frontier intelligence |
| `"claude-opus-4-5"` | Premium model combining maximum intelligence with practical performance |
| `"claude-opus-4-5-20251101"` | Premium model combining maximum intelligence with practical performance |
| `"claude-sonnet-4-5"` | High-performance model for agents and coding |
| `"claude-sonnet-4-5-20250929"` | High-performance model for agents and coding |

**Object format (BetaManagedAgentsModelConfigParams):**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | `BetaManagedAgentsModel` | Yes | The model that will power your agent. |
| `speed` | `"standard" \| "fast"` | No | Inference speed mode. `"fast"` provides significantly faster output token generation at premium pricing. Not all models support `fast`; invalid combinations are rejected at create time. Default: `"standard"`. |

### Response — `BetaManagedAgentsAgent`

```json
{
  "id": "string",
  "type": "agent",
  "name": "string",
  "description": "string",
  "model": {
    "id": "string",
    "speed": "standard"
  },
  "system": "string",
  "tools": [],
  "skills": [],
  "mcp_servers": [],
  "metadata": {},
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "archived_at": null,
  "version": 1
}
```

### Example Request

```bash
curl https://api.anthropic.com/v1/agents \
    -H 'Content-Type: application/json' \
    -H 'anthropic-version: 2023-06-01' \
    -H 'anthropic-beta: managed-agents-2026-04-01' \
    -H "X-Api-Key: $ANTHROPIC_API_KEY" \
    -d '{
      "model": "claude-sonnet-4-6",
      "name": "My First Agent"
    }'
```

### Example Request — Full Configuration

```bash
curl https://api.anthropic.com/v1/agents \
    -H 'Content-Type: application/json' \
    -H 'anthropic-version: 2023-06-01' \
    -H 'anthropic-beta: managed-agents-2026-04-01' \
    -H "X-Api-Key: $ANTHROPIC_API_KEY" \
    -d '{
      "model": {
        "id": "claude-opus-4-6",
        "speed": "fast"
      },
      "name": "Advanced Agent",
      "description": "An advanced agent with multiple tools and skills",
      "system": "You are a helpful assistant...",
      "metadata": {
        "team": "engineering",
        "environment": "production"
      },
      "mcp_servers": [
        {
          "name": "my_mcp_server",
          "type": "url",
          "url": "http://localhost:3000"
        }
      ],
      "skills": [
        {
          "skill_id": "xlsx",
          "type": "anthropic"
        }
      ],
      "tools": [
        {
          "type": "agent_toolset_20260401",
          "default_config": {
            "enabled": true,
            "permission_policy": {
              "type": "always_allow"
            }
          },
          "configs": [
            {
              "name": "bash",
              "enabled": true,
              "permission_policy": {
                "type": "always_ask"
              }
            }
          ]
        }
      ]
    }'
```

---

## List Agents

**GET** `/v1/agents`

Retrieves a paginated list of agents.

### Headers

| Header | Required | Description |
|--------|----------|-------------|
| `anthropic-version` | Yes | `2023-06-01` |
| `anthropic-beta` | Yes | `managed-agents-2026-04-01` |
| `X-Api-Key` | Yes | Your Anthropic API key |

### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | `number` | 20 | Maximum results per page. Maximum 100. |
| `page` | `string` | — | Opaque pagination cursor from a previous response. |
| `include_archived` | `boolean` | `false` | Include archived agents in results. |
| `created_at[gte]` | `string` | — | Return agents created at or after this time (inclusive). RFC 3339 format. |
| `created_at[lte]` | `string` | — | Return agents created at or before this time (inclusive). RFC 3339 format. |

### Response

```json
{
  "data": [
    {
      "id": "string",
      "type": "agent",
      "name": "string",
      "description": "string",
      "model": {
        "id": "string",
        "speed": "standard"
      },
      "system": "string",
      "tools": [],
      "skills": [],
      "mcp_servers": [],
      "metadata": {},
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z",
      "archived_at": null,
      "version": 1
    }
  ],
  "next_page": "string or null"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `data` | `array of BetaManagedAgentsAgent` | List of agents. |
| `next_page` | `string \| null` | Opaque cursor for the next page. Null when no more results. |

### Example Request

```bash
curl https://api.anthropic.com/v1/agents \
    -H 'anthropic-version: 2023-06-01' \
    -H 'anthropic-beta: managed-agents-2026-04-01' \
    -H "X-Api-Key: $ANTHROPIC_API_KEY"
```

---

## Retrieve Agent

**GET** `/v1/agents/{agent_id}`

Retrieves a specific agent by ID. Optionally retrieves a specific version.

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `agent_id` | `string` | Yes | The agent ID. |

### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `version` | `number` | — | Agent version to retrieve. Omit for the most recent version. Must be at least 1 if specified. |

### Headers

| Header | Required | Description |
|--------|----------|-------------|
| `anthropic-version` | Yes | `2023-06-01` |
| `anthropic-beta` | Yes | `managed-agents-2026-04-01` |
| `X-Api-Key` | Yes | Your Anthropic API key |

### Response — `BetaManagedAgentsAgent`

```json
{
  "id": "string",
  "type": "agent",
  "name": "string",
  "description": "string",
  "model": {
    "id": "string",
    "speed": "standard"
  },
  "system": "string",
  "tools": [],
  "skills": [],
  "mcp_servers": [],
  "metadata": {},
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "archived_at": null,
  "version": 1
}
```

### Example Request

```bash
curl https://api.anthropic.com/v1/agents/$AGENT_ID \
    -H 'anthropic-version: 2023-06-01' \
    -H 'anthropic-beta: managed-agents-2026-04-01' \
    -H "X-Api-Key: $ANTHROPIC_API_KEY"
```

### Example Request — Specific Version

```bash
curl "https://api.anthropic.com/v1/agents/$AGENT_ID?version=2" \
    -H 'anthropic-version: 2023-06-01' \
    -H 'anthropic-beta: managed-agents-2026-04-01' \
    -H "X-Api-Key: $ANTHROPIC_API_KEY"
```

---

## Update Agent

**POST** `/v1/agents/{agent_id}`

Updates an existing agent. Uses optimistic concurrency control with version numbers.

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `agent_id` | `string` | Yes | The agent ID. |

### Headers

| Header | Required | Description |
|--------|----------|-------------|
| `Content-Type` | Yes | `application/json` |
| `anthropic-version` | Yes | `2023-06-01` |
| `anthropic-beta` | Yes | `managed-agents-2026-04-01` |
| `X-Api-Key` | Yes | Your Anthropic API key |

### Request Body

#### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `version` | `number` | The agent's current version. Must match the server's current version to prevent concurrent overwrites. |

#### Optional Fields

| Field | Type | Constraints | Update Behavior |
|-------|------|-------------|-----------------|
| `name` | `string` | 1-256 characters | Cannot be cleared. Omit to preserve. |
| `description` | `string` | Up to 2048 characters | Omit to preserve. Send empty string or `null` to clear. |
| `model` | `BetaManagedAgentsModel \| BetaManagedAgentsModelConfigParams` | — | Cannot be cleared. Omit to preserve. |
| `system` | `string` | Up to 100,000 characters | Omit to preserve. Send empty string or `null` to clear. |
| `metadata` | `map[string]` | Max 16 pairs, keys up to 64 chars, values up to 512 chars | Patch-based: set a key to a string to upsert, set to `null` to delete. Omit to preserve. |
| `mcp_servers` | `array of BetaManagedAgentsURLMCPServerParams` | Maximum 20, unique names | Full replacement. Omit to preserve. Send empty array or `null` to clear. |
| `skills` | `array of BetaManagedAgentsSkillParams` | Maximum 20 | Full replacement. Omit to preserve. Send empty array or `null` to clear. |
| `tools` | `array of (BetaManagedAgentsAgentToolset20260401Params \| BetaManagedAgentsMCPToolsetParams \| BetaManagedAgentsCustomToolParams)` | Maximum 128 tools across all toolsets | Full replacement. Omit to preserve. Send empty array or `null` to clear. |

### Response — `BetaManagedAgentsAgent`

Returns the updated agent object with incremented version number.

### Example Request

```bash
curl https://api.anthropic.com/v1/agents/$AGENT_ID \
    -H 'Content-Type: application/json' \
    -H 'anthropic-version: 2023-06-01' \
    -H 'anthropic-beta: managed-agents-2026-04-01' \
    -H "X-Api-Key: $ANTHROPIC_API_KEY" \
    -d '{
      "version": 1,
      "name": "Updated Agent Name",
      "description": "Updated description"
    }'
```

---

## Archive Agent

**POST** `/v1/agents/{agent_id}/archive`

Archives an agent, marking it as inactive while preserving it for historical reference.

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `agent_id` | `string` | Yes | The agent ID. |

### Headers

| Header | Required | Description |
|--------|----------|-------------|
| `anthropic-version` | Yes | `2023-06-01` |
| `anthropic-beta` | Yes | `managed-agents-2026-04-01` |
| `X-Api-Key` | Yes | Your Anthropic API key |

### Response — `BetaManagedAgentsAgent`

Returns the archived agent object with `archived_at` timestamp populated.

```json
{
  "id": "string",
  "type": "agent",
  "name": "string",
  "description": "string",
  "model": {
    "id": "string",
    "speed": "standard"
  },
  "system": "string",
  "tools": [],
  "skills": [],
  "mcp_servers": [],
  "metadata": {},
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "archived_at": "2024-01-01T00:00:00Z",
  "version": 1
}
```

### Example Request

```bash
curl https://api.anthropic.com/v1/agents/$AGENT_ID/archive \
    -X POST \
    -H 'anthropic-version: 2023-06-01' \
    -H 'anthropic-beta: managed-agents-2026-04-01' \
    -H "X-Api-Key: $ANTHROPIC_API_KEY"
```

---

## List Agent Versions

**GET** `/v1/agents/{agent_id}/versions`

Retrieves all versions of a specific agent.

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `agent_id` | `string` | Yes | The agent ID. |

### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | `number` | 20 | Maximum results per page. Maximum 100. |
| `page` | `string` | — | Opaque pagination cursor. |

### Headers

| Header | Required | Description |
|--------|----------|-------------|
| `anthropic-version` | Yes | `2023-06-01` |
| `anthropic-beta` | Yes | `managed-agents-2026-04-01` |
| `X-Api-Key` | Yes | Your Anthropic API key |

### Response

```json
{
  "data": [
    {
      "id": "string",
      "type": "agent",
      "name": "string",
      "description": "string",
      "model": {
        "id": "string",
        "speed": "standard"
      },
      "system": "string",
      "tools": [],
      "skills": [],
      "mcp_servers": [],
      "metadata": {},
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z",
      "archived_at": null,
      "version": 1
    }
  ],
  "next_page": "string or null"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `data` | `array of BetaManagedAgentsAgent` | Agent versions. |
| `next_page` | `string \| null` | Opaque cursor for the next page. |

### Example Request

```bash
curl https://api.anthropic.com/v1/agents/$AGENT_ID/versions \
    -H 'anthropic-version: 2023-06-01' \
    -H 'anthropic-beta: managed-agents-2026-04-01' \
    -H "X-Api-Key: $ANTHROPIC_API_KEY"
```

---

## Object Schemas

### BetaManagedAgentsAgent

The agent response object returned by all endpoints.

| Field | Type | Description |
|-------|------|-------------|
| `id` | `string` | Unique agent identifier. |
| `type` | `"agent"` | Fixed value indicating this is an agent object. |
| `name` | `string` | Human-readable name for the agent. 1-256 characters. |
| `description` | `string` | Description of what the agent does. Up to 2048 characters. |
| `model` | `BetaManagedAgentsModelConfig` | Model identifier and configuration. |
| `system` | `string` | System prompt for the agent. Up to 100,000 characters. |
| `tools` | `array` | Tool configurations available to the agent. Maximum 128 tools across all toolsets. |
| `skills` | `array` | Skills available to the agent. Maximum 20. |
| `mcp_servers` | `array of BetaManagedAgentsMCPServerURLDefinition` | MCP servers this agent connects to. Maximum 20, names must be unique. |
| `metadata` | `map[string]` | Arbitrary key-value metadata. Maximum 16 pairs, keys up to 64 chars, values up to 512 chars. |
| `created_at` | `string` | RFC 3339 timestamp of creation. |
| `updated_at` | `string` | RFC 3339 timestamp of last update. |
| `archived_at` | `string \| null` | RFC 3339 timestamp of archival, or null if not archived. |
| `version` | `number` | The agent's current version. Starts at 1, increments on each update. |

### BetaManagedAgentsModelConfig

| Field | Type | Description |
|-------|------|-------------|
| `id` | `BetaManagedAgentsModel` | The model that powers the agent. |
| `speed` | `"standard" \| "fast"` | Inference speed mode. `"fast"` provides significantly faster output token generation at premium pricing. Not all models support `fast`. |

### BetaManagedAgentsMCPServerURLDefinition

| Field | Type | Description |
|-------|------|-------------|
| `name` | `string` | Unique name for this server, referenced by mcp_toolset configurations. 1-255 characters. |
| `type` | `"url"` | Fixed value indicating URL-based MCP server connection. |
| `url` | `string` | Endpoint URL for the MCP server. |

### BetaManagedAgentsAnthropicSkill

| Field | Type | Description |
|-------|------|-------------|
| `skill_id` | `string` | Identifier of the Anthropic skill (e.g., `"xlsx"`). |
| `type` | `"anthropic"` | Fixed value indicating Anthropic-managed skill. |
| `version` | `string` | Version to pin (resolved from latest if omitted during creation). |

### BetaManagedAgentsCustomSkill

| Field | Type | Description |
|-------|------|-------------|
| `skill_id` | `string` | Tagged ID of the custom skill (e.g., `"skill_01XJ5..."`). |
| `type` | `"custom"` | Fixed value indicating user-created custom skill. |
| `version` | `string` | Version to pin (resolved from latest if omitted during creation). |

---

## Tool Schemas

### BetaManagedAgentsAgentToolset20260401

Built-in agent tools configuration.

| Field | Type | Description |
|-------|------|-------------|
| `type` | `"agent_toolset_20260401"` | Fixed value indicating built-in agent tools. |
| `configs` | `array of BetaManagedAgentsAgentToolConfig` | Per-tool configuration overrides. |
| `default_config` | `BetaManagedAgentsAgentToolsetDefaultConfig` | Default configuration for all tools in the toolset. |

#### BetaManagedAgentsAgentToolConfig

| Field | Type | Description |
|-------|------|-------------|
| `name` | `"bash" \| "edit" \| "read" \| "write" \| "glob" \| "grep" \| "web_fetch" \| "web_search"` | Built-in agent tool identifier. |
| `enabled` | `boolean` | Whether this tool is enabled and available to Claude. |
| `permission_policy` | `BetaManagedAgentsAlwaysAllowPolicy \| BetaManagedAgentsAlwaysAskPolicy` | Permission policy for tool execution. |

#### BetaManagedAgentsAgentToolsetDefaultConfig

| Field | Type | Description |
|-------|------|-------------|
| `enabled` | `boolean` | Whether tools are enabled and available by default. |
| `permission_policy` | `BetaManagedAgentsAlwaysAllowPolicy \| BetaManagedAgentsAlwaysAskPolicy` | Permission policy for tool execution. |

#### Available Built-in Tools

| Tool | Description |
|------|-------------|
| `bash` | Execute shell commands |
| `edit` | Edit file contents |
| `read` | Read file contents |
| `write` | Write file contents |
| `glob` | Pattern matching for files |
| `grep` | Search file contents |
| `web_fetch` | Fetch web content |
| `web_search` | Search the web |

### BetaManagedAgentsMCPToolset

Tools from a Model Context Protocol (MCP) server.

| Field | Type | Description |
|-------|------|-------------|
| `type` | `"mcp_toolset"` | Fixed value indicating MCP server tools. |
| `mcp_server_name` | `string` | Name of the MCP server. Must match a server name from the `mcp_servers` array. 1-255 characters. |
| `configs` | `array of BetaManagedAgentsMCPToolConfig` | Per-tool configuration overrides. |
| `default_config` | `BetaManagedAgentsMCPToolsetDefaultConfig` | Default configuration for all tools from the MCP server. |

#### BetaManagedAgentsMCPToolConfig

| Field | Type | Description |
|-------|------|-------------|
| `name` | `string` | Name of the MCP tool to configure. 1-128 characters. |
| `enabled` | `boolean` | Whether this tool is enabled. |
| `permission_policy` | `BetaManagedAgentsAlwaysAllowPolicy \| BetaManagedAgentsAlwaysAskPolicy` | Permission policy for tool execution. |

#### BetaManagedAgentsMCPToolsetDefaultConfig

| Field | Type | Description |
|-------|------|-------------|
| `enabled` | `boolean` | Whether tools are enabled by default. |
| `permission_policy` | `BetaManagedAgentsAlwaysAllowPolicy \| BetaManagedAgentsAlwaysAskPolicy` | Permission policy for tool execution. |

### BetaManagedAgentsCustomTool

Client-implemented tools that emit `agent.custom_tool_use` events.

| Field | Type | Description |
|-------|------|-------------|
| `type` | `"custom"` | Fixed value indicating custom tool. |
| `name` | `string` | Unique name for the tool. 1-128 characters. Letters, digits, underscores, and hyphens only. |
| `description` | `string` | Description of what the tool does, shown to the agent. 1-1024 characters. |
| `input_schema` | `BetaManagedAgentsCustomToolInputSchema` | JSON Schema for custom tool input parameters. |

#### BetaManagedAgentsCustomToolInputSchema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | `"object"` | No | Must be `"object"` for tool input schemas. |
| `properties` | `map[unknown]` | No | JSON Schema properties defining the tool's input parameters. |
| `required` | `array of string` | No | List of required property names. |

---

## Permission Policies

### BetaManagedAgentsAlwaysAllowPolicy

```json
{
  "type": "always_allow"
}
```

Tool calls are automatically approved without user confirmation.

### BetaManagedAgentsAlwaysAskPolicy

```json
{
  "type": "always_ask"
}
```

Tool calls require user confirmation before execution.

---

## Request Parameter Schemas (Create/Update)

### BetaManagedAgentsURLMCPServerParams

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | `string` | Yes | Unique name for this server. 1-255 characters. |
| `type` | `"url"` | Yes | Fixed value for URL-based connection. |
| `url` | `string` | Yes | Endpoint URL for the MCP server. |

### BetaManagedAgentsSkillParams

Union type of `BetaManagedAgentsAnthropicSkillParams` or `BetaManagedAgentsCustomSkillParams`.

#### BetaManagedAgentsAnthropicSkillParams

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `skill_id` | `string` | Yes | Identifier of the Anthropic skill (e.g., `"xlsx"`). |
| `type` | `"anthropic"` | Yes | Fixed value. |
| `version` | `string` | No | Version to pin. Defaults to latest if omitted. |

#### BetaManagedAgentsCustomSkillParams

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `skill_id` | `string` | Yes | Tagged ID of the custom skill (e.g., `"skill_01XJ5..."`). |
| `type` | `"custom"` | Yes | Fixed value. |
| `version` | `string` | No | Version to pin. Defaults to latest if omitted. |

### BetaManagedAgentsAgentToolset20260401Params

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | `"agent_toolset_20260401"` | Yes | Fixed value. |
| `configs` | `array of BetaManagedAgentsAgentToolConfigParams` | No | Per-tool configuration overrides. |
| `default_config` | `BetaManagedAgentsAgentToolsetDefaultConfigParams` | No | Default configuration for all tools in the toolset. |

#### BetaManagedAgentsAgentToolConfigParams

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | `"bash" \| "edit" \| "read" \| "write" \| "glob" \| "grep" \| "web_fetch" \| "web_search"` | Yes | Built-in agent tool identifier. |
| `enabled` | `boolean` | No | Whether this tool is enabled. Overrides `default_config`. |
| `permission_policy` | `BetaManagedAgentsAlwaysAllowPolicy \| BetaManagedAgentsAlwaysAskPolicy` | No | Permission policy for tool execution. |

#### BetaManagedAgentsAgentToolsetDefaultConfigParams

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `enabled` | `boolean` | No | Whether tools are enabled by default. Default: `true`. |
| `permission_policy` | `BetaManagedAgentsAlwaysAllowPolicy \| BetaManagedAgentsAlwaysAskPolicy` | No | Permission policy for tool execution. |

### BetaManagedAgentsMCPToolsetParams

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | `"mcp_toolset"` | Yes | Fixed value. |
| `mcp_server_name` | `string` | Yes | Name of the MCP server. Must match a name from the `mcp_servers` array. 1-255 characters. |
| `configs` | `array of BetaManagedAgentsMCPToolConfigParams` | No | Per-tool configuration overrides. |
| `default_config` | `BetaManagedAgentsMCPToolsetDefaultConfigParams` | No | Default configuration for all tools from the MCP server. |

#### BetaManagedAgentsMCPToolConfigParams

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | `string` | Yes | Name of the MCP tool to configure. 1-128 characters. |
| `enabled` | `boolean` | No | Whether this tool is enabled. Overrides `default_config`. |
| `permission_policy` | `BetaManagedAgentsAlwaysAllowPolicy \| BetaManagedAgentsAlwaysAskPolicy` | No | Permission policy for tool execution. |

#### BetaManagedAgentsMCPToolsetDefaultConfigParams

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `enabled` | `boolean` | No | Whether tools are enabled by default. Default: `true`. |
| `permission_policy` | `BetaManagedAgentsAlwaysAllowPolicy \| BetaManagedAgentsAlwaysAskPolicy` | No | Permission policy for tool execution. |

### BetaManagedAgentsCustomToolParams

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | `"custom"` | Yes | Fixed value. |
| `name` | `string` | Yes | Unique name for the tool. 1-128 characters. Letters, digits, underscores, and hyphens only. |
| `description` | `string` | Yes | Description of what the tool does. 1-1024 characters. |
| `input_schema` | `BetaManagedAgentsCustomToolInputSchema` | Yes | JSON Schema for custom tool input parameters. |

---

## Beta Header

All endpoints require the `anthropic-beta` header. Include the managed agents beta version:

```
anthropic-beta: managed-agents-2026-04-01
```

Supported beta versions:

| Beta Version | Description |
|-------------|-------------|
| `message-batches-2024-09-24` | Message batches |
| `prompt-caching-2024-07-31` | Prompt caching |
| `computer-use-2024-10-22` | Computer use |
| `computer-use-2025-01-24` | Computer use (updated) |
| `pdfs-2024-09-25` | PDF support |
| `token-counting-2024-11-01` | Token counting |
| `token-efficient-tools-2025-02-19` | Token efficient tools |
| `output-128k-2025-02-19` | 128k output |
| `files-api-2025-04-14` | Files API |
| `mcp-client-2025-04-04` | MCP client |
| `mcp-client-2025-11-20` | MCP client (updated) |
| `dev-full-thinking-2025-05-14` | Developer full thinking |
| `interleaved-thinking-2025-05-14` | Interleaved thinking |
| `code-execution-2025-05-22` | Code execution |
| `extended-cache-ttl-2025-04-11` | Extended cache TTL |
| `context-1m-2025-08-07` | 1M context |
| `context-management-2025-06-27` | Context management |
| `model-context-window-exceeded-2025-08-26` | Model context window exceeded |
| `skills-2025-10-02` | Skills |
| `fast-mode-2026-02-01` | Fast mode |
| `output-300k-2026-03-24` | 300k output |
| `advisor-tool-2026-03-01` | Advisor tool |

---

## Validation Constraints Summary

### Agent-Level Limits

| Constraint | Limit |
|------------|-------|
| Name length | 1-256 characters |
| Description length | Up to 2048 characters |
| System prompt length | Up to 100,000 characters |
| Metadata pairs | Maximum 16 |
| Metadata key length | Up to 64 characters |
| Metadata value length | Up to 512 characters |
| MCP servers | Maximum 20 |
| Skills | Maximum 20 |
| Tools (across all toolsets) | Maximum 128 |

### Tool-Level Limits

| Constraint | Limit |
|------------|-------|
| MCP server name | 1-255 characters, unique within array |
| MCP tool name | 1-128 characters |
| Custom tool name | 1-128 characters (letters, digits, underscores, hyphens) |
| Custom tool description | 1-1024 characters |

### Versioning

- Every agent starts at version 1.
- Each update increments the version.
- The `version` field in Update requests enables optimistic concurrency control. The provided version must match the server's current version.

### Update Semantics

| Field | Behavior |
|-------|----------|
| `name` | Cannot be cleared. Omit to preserve. |
| `model` | Cannot be cleared. Omit to preserve. |
| `description` | Omit to preserve. Empty string or `null` to clear. |
| `system` | Omit to preserve. Empty string or `null` to clear. |
| `metadata` | Patch-based: set key to string to upsert, set to `null` to delete. Omit to preserve. |
| `mcp_servers` | Full replacement. Omit to preserve. Empty array or `null` to clear. |
| `skills` | Full replacement. Omit to preserve. Empty array or `null` to clear. |
| `tools` | Full replacement. Omit to preserve. Empty array or `null` to clear. |

---

## Endpoints Summary

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/v1/agents` | Create Agent |
| `GET` | `/v1/agents` | List Agents |
| `GET` | `/v1/agents/{agent_id}` | Retrieve Agent (use `?version=N` for specific version) |
| `POST` | `/v1/agents/{agent_id}` | Update Agent |
| `POST` | `/v1/agents/{agent_id}/archive` | Archive Agent |
| `GET` | `/v1/agents/{agent_id}/versions` | List Agent Versions |
