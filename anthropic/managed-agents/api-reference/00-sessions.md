# Sessions

## Create Session

**POST** `/v1/sessions`

Create a new session for an agent.

### Header Parameters

- `anthropic-beta`: optional array of AnthropicBeta

  Optional header to specify the beta version(s) you want to use.

  - `UnionMember0 = string`

  - `UnionMember1 = "message-batches-2024-09-24" | "prompt-caching-2024-07-31" | "computer-use-2024-10-22" | "computer-use-2025-01-24" | "pdfs-2024-09-25" | "token-counting-2024-11-01" | "token-efficient-tools-2025-02-19" | "output-128k-2025-02-19" | "files-api-2025-04-14" | "mcp-client-2025-04-04" | "mcp-client-2025-11-20" | "dev-full-thinking-2025-05-14" | "interleaved-thinking-2025-05-14" | "code-execution-2025-05-22" | "extended-cache-ttl-2025-04-11" | "context-1m-2025-08-07" | "context-management-2025-06-27" | "model-context-window-exceeded-2025-08-26" | "skills-2025-10-02" | "fast-mode-2026-02-01" | "output-300k-2026-03-24" | "advisor-tool-2026-03-01"`

### Body Parameters

- `agent`: string | BetaManagedAgentsAgentParams (required)

  Agent identifier. Accepts the `agent` ID string, which pins the latest version for the session, or an `agent` object with both id and version specified.

  - `UnionMember0 = string`

  - `BetaManagedAgentsAgentParams = object { id, type, version }`

    Specification for an Agent. Provide a specific `version` or use the short-form `agent="agent_id"` for the most recent version.

    - `id: string` - The `agent` ID.
    - `type: "agent"`
    - `version: optional number` - The specific `agent` version to use. Omit to use the latest version. Must be at least 1 if specified.

- `environment_id`: string (required)

  ID of the `environment` defining the container configuration for this session.

- `metadata`: optional map[string]

  Arbitrary key-value metadata attached to the session. Maximum 16 pairs, keys up to 64 chars, values up to 512 chars.

- `resources`: optional array of BetaManagedAgentsGitHubRepositoryResourceParams | BetaManagedAgentsFileResourceParams

  Resources (e.g. repositories, files) to mount into the session's container.

  - `BetaManagedAgentsGitHubRepositoryResourceParams = object { authorization_token, type, url, checkout, mount_path }`

    Mount a GitHub repository into the session's container.

    - `authorization_token: string` - GitHub authorization token used to clone the repository.
    - `type: "github_repository"`
    - `url: string` - Github URL of the repository.
    - `checkout: optional BetaManagedAgentsBranchCheckout | BetaManagedAgentsCommitCheckout` - Branch or commit to check out. Defaults to the repository's default branch.
      - `BetaManagedAgentsBranchCheckout = object { name: string, type: "branch" }` - Branch name to check out.
      - `BetaManagedAgentsCommitCheckout = object { sha: string, type: "commit" }` - Full commit SHA to check out.
    - `mount_path: optional string` - Mount path in the container. Defaults to `/workspace/<repo-name>`.

  - `BetaManagedAgentsFileResourceParams = object { file_id, type, mount_path }`

    Mount a file uploaded via the Files API into the session.

    - `file_id: string` - ID of a previously uploaded file.
    - `type: "file"`
    - `mount_path: optional string` - Mount path in the container. Defaults to `/mnt/session/uploads/<file_id>`.

- `title`: optional string

  Human-readable session title.

- `vault_ids`: optional array of string

  Vault IDs for stored credentials the agent can use during the session.

### Returns

`BetaManagedAgentsSession` - A Managed Agents `session`.

- `id: string`
- `agent: BetaManagedAgentsSessionAgent` - Resolved `agent` definition for a `session`. Snapshot of the `agent` at `session` creation time.
  - `id: string`
  - `description: string`
  - `mcp_servers: array of BetaManagedAgentsMCPServerURLDefinition`
    - `name: string`
    - `type: "url"`
    - `url: string`
  - `model: BetaManagedAgentsModelConfig` - Model identifier and configuration.
    - `id: BetaManagedAgentsModel` - The model that will power your agent.
      - `"claude-opus-4-6"` - Most intelligent model for building agents and coding
      - `"claude-sonnet-4-6"` - Best combination of speed and intelligence
      - `"claude-haiku-4-5"` - Fastest model with near-frontier intelligence
      - `"claude-haiku-4-5-20251001"` - Fastest model with near-frontier intelligence
      - `"claude-opus-4-5"` - Premium model combining maximum intelligence with practical performance
      - `"claude-opus-4-5-20251101"` - Premium model combining maximum intelligence with practical performance
      - `"claude-sonnet-4-5"` - High-performance model for agents and coding
      - `"claude-sonnet-4-5-20250929"` - High-performance model for agents and coding
      - Or any other model string
    - `speed: optional "standard" | "fast"` - Inference speed mode. `fast` provides significantly faster output token generation at premium pricing. Not all models support `fast`; invalid combinations are rejected at create time.
  - `name: string`
  - `skills: array of BetaManagedAgentsAnthropicSkill | BetaManagedAgentsCustomSkill`
    - `BetaManagedAgentsAnthropicSkill = object { skill_id: string, type: "anthropic", version: string }` - A resolved Anthropic-managed skill.
    - `BetaManagedAgentsCustomSkill = object { skill_id: string, type: "custom", version: string }` - A resolved user-created custom skill.
  - `system: string`
  - `tools: array of BetaManagedAgentsAgentToolset20260401 | BetaManagedAgentsMCPToolset | BetaManagedAgentsCustomTool`
    - `BetaManagedAgentsAgentToolset20260401 = object { configs, default_config, type }`
      - `configs: array of BetaManagedAgentsAgentToolConfig`
        - `enabled: boolean`
        - `name: "bash" | "edit" | "read" | "write" | "glob" | "grep" | "web_fetch" | "web_search"` - Built-in agent tool identifier.
        - `permission_policy: BetaManagedAgentsAlwaysAllowPolicy | BetaManagedAgentsAlwaysAskPolicy` - Permission policy for tool execution.
          - `BetaManagedAgentsAlwaysAllowPolicy = object { type: "always_allow" }` - Tool calls are automatically approved without user confirmation.
          - `BetaManagedAgentsAlwaysAskPolicy = object { type: "always_ask" }` - Tool calls require user confirmation before execution.
      - `default_config: BetaManagedAgentsAgentToolsetDefaultConfig` - Resolved default configuration for agent tools.
        - `enabled: boolean`
        - `permission_policy: BetaManagedAgentsAlwaysAllowPolicy | BetaManagedAgentsAlwaysAskPolicy`
      - `type: "agent_toolset_20260401"`
    - `BetaManagedAgentsMCPToolset = object { configs, default_config, mcp_server_name, type }`
      - `configs: array of BetaManagedAgentsMCPToolConfig`
        - `enabled: boolean`
        - `name: string`
        - `permission_policy: BetaManagedAgentsAlwaysAllowPolicy | BetaManagedAgentsAlwaysAskPolicy`
      - `default_config: BetaManagedAgentsMCPToolsetDefaultConfig` - Resolved default configuration for all tools from an MCP server.
        - `enabled: boolean`
        - `permission_policy: BetaManagedAgentsAlwaysAllowPolicy | BetaManagedAgentsAlwaysAskPolicy`
      - `mcp_server_name: string`
      - `type: "mcp_toolset"`
    - `BetaManagedAgentsCustomTool = object { description, input_schema, name, type }` - A custom tool as returned in API responses.
      - `description: string`
      - `input_schema: BetaManagedAgentsCustomToolInputSchema` - JSON Schema for custom tool input parameters.
        - `properties: optional map[unknown]` - JSON Schema properties defining the tool's input parameters.
        - `required: optional array of string` - List of required property names.
        - `type: optional "object"` - Must be 'object' for tool input schemas.
      - `name: string`
      - `type: "custom"`
  - `type: "agent"`
  - `version: number`
- `archived_at: string` - A timestamp in RFC 3339 format
- `created_at: string` - A timestamp in RFC 3339 format
- `environment_id: string`
- `metadata: map[string]`
- `resources: array of BetaManagedAgentsSessionResource`
  - `BetaManagedAgentsGitHubRepositoryResource = object { id, created_at, mount_path, type, updated_at, url, checkout }`
    - `id: string`
    - `created_at: string` - A timestamp in RFC 3339 format
    - `mount_path: string`
    - `type: "github_repository"`
    - `updated_at: string` - A timestamp in RFC 3339 format
    - `url: string`
    - `checkout: optional BetaManagedAgentsBranchCheckout | BetaManagedAgentsCommitCheckout`
      - `BetaManagedAgentsBranchCheckout = object { name: string, type: "branch" }`
      - `BetaManagedAgentsCommitCheckout = object { sha: string, type: "commit" }`
  - `BetaManagedAgentsFileResource = object { id, created_at, file_id, mount_path, type, updated_at }`
    - `id: string`
    - `created_at: string` - A timestamp in RFC 3339 format
    - `file_id: string`
    - `mount_path: string`
    - `type: "file"`
    - `updated_at: string` - A timestamp in RFC 3339 format
- `stats: BetaManagedAgentsSessionStats` - Timing statistics for a session.
  - `active_seconds: optional number` - Cumulative time in seconds the session spent in running status. Excludes idle time.
  - `duration_seconds: optional number` - Elapsed time since session creation in seconds. For terminated sessions, frozen at the final update.
- `status: "rescheduling" | "running" | "idle" | "terminated"` - SessionStatus enum
- `title: string`
- `type: "session"`
- `updated_at: string` - A timestamp in RFC 3339 format
- `usage: BetaManagedAgentsSessionUsage` - Cumulative token usage for a session across all turns.
  - `cache_creation: optional BetaManagedAgentsCacheCreationUsage` - Prompt-cache creation token usage broken down by cache lifetime.
    - `ephemeral_1h_input_tokens: optional number` - Tokens used to create 1-hour ephemeral cache entries.
    - `ephemeral_5m_input_tokens: optional number` - Tokens used to create 5-minute ephemeral cache entries.
  - `cache_read_input_tokens: optional number` - Total tokens read from prompt cache.
  - `input_tokens: optional number` - Total input tokens consumed across all turns.
  - `output_tokens: optional number` - Total output tokens generated across all turns.
- `vault_ids: array of string` - Vault IDs attached to the session at creation. Empty when no vaults were supplied.

### Example

```bash
curl https://api.anthropic.com/v1/sessions \
    -H 'Content-Type: application/json' \
    -H 'anthropic-version: 2023-06-01' \
    -H 'anthropic-beta: managed-agents-2026-04-01' \
    -H "X-Api-Key: $ANTHROPIC_API_KEY" \
    -d '{
          "agent": "agent_011CZkYpogX7uDKUyvBTophP",
          "environment_id": "env_011CZkZ9X2dpNyB7HsEFoRfW"
        }'
```

---

## List Sessions

**GET** `/v1/sessions`

List all sessions with optional filtering.

### Query Parameters

- `agent_id`: optional string - Filter sessions created with this agent ID.
- `agent_version`: optional number - Filter by agent version. Only applies when agent_id is also set.
- `created_at[gt]`: optional string - Return sessions created after this time (exclusive).
- `created_at[gte]`: optional string - Return sessions created at or after this time (inclusive).
- `created_at[lt]`: optional string - Return sessions created before this time (exclusive).
- `created_at[lte]`: optional string - Return sessions created at or before this time (inclusive).
- `include_archived`: optional boolean - When true, includes archived sessions. Default: false (exclude archived).
- `limit`: optional number - Maximum number of results to return.
- `order`: optional "asc" | "desc" - Sort direction for results, ordered by created_at. Defaults to desc (newest first).
- `page`: optional string - Opaque pagination cursor from a previous response's next_page.

### Header Parameters

- `anthropic-beta`: optional array of AnthropicBeta

  Optional header to specify the beta version(s) you want to use. (See Create Session for full list of beta values.)

### Returns

- `data`: optional array of BetaManagedAgentsSession - List of sessions. (See Create Session response for full session schema.)
- `next_page`: optional string - Opaque cursor for the next page. Null when no more results.

### Example

```bash
curl https://api.anthropic.com/v1/sessions \
    -H 'anthropic-version: 2023-06-01' \
    -H 'anthropic-beta: managed-agents-2026-04-01' \
    -H "X-Api-Key: $ANTHROPIC_API_KEY"
```

---

## Retrieve Session

**GET** `/v1/sessions/{session_id}`

Get a specific session by ID.

### Path Parameters

- `session_id`: string (required)

### Header Parameters

- `anthropic-beta`: optional array of AnthropicBeta

  Optional header to specify the beta version(s) you want to use. (See Create Session for full list of beta values.)

### Returns

`BetaManagedAgentsSession` - A Managed Agents `session`. (See Create Session response for full session schema.)

### Example

```bash
curl https://api.anthropic.com/v1/sessions/$SESSION_ID \
    -H 'anthropic-version: 2023-06-01' \
    -H 'anthropic-beta: managed-agents-2026-04-01' \
    -H "X-Api-Key: $ANTHROPIC_API_KEY"
```

---

## Update Session

**POST** `/v1/sessions/{session_id}`

Update an existing session.

### Path Parameters

- `session_id`: string (required)

### Header Parameters

- `anthropic-beta`: optional array of AnthropicBeta

  Optional header to specify the beta version(s) you want to use. (See Create Session for full list of beta values.)

### Body Parameters

- `metadata`: optional map[string] - Metadata patch. Set a key to a string to upsert it, or to null to delete it. Omit the field to preserve.
- `title`: optional string - Human-readable session title.
- `vault_ids`: optional array of string - Vault IDs (`vlt_*`) to attach to the session. Not yet supported; requests setting this field are rejected. Reserved for future use.

### Returns

`BetaManagedAgentsSession` - A Managed Agents `session`. (See Create Session response for full session schema.)

### Example

```bash
curl https://api.anthropic.com/v1/sessions/$SESSION_ID \
    -X POST \
    -H 'Content-Type: application/json' \
    -H 'anthropic-version: 2023-06-01' \
    -H 'anthropic-beta: managed-agents-2026-04-01' \
    -H "X-Api-Key: $ANTHROPIC_API_KEY" \
    -d '{
          "title": "Updated Session Title"
        }'
```

---

## Delete Session

**DELETE** `/v1/sessions/{session_id}`

Permanently delete a session.

### Path Parameters

- `session_id`: string (required)

### Header Parameters

- `anthropic-beta`: optional array of AnthropicBeta

  Optional header to specify the beta version(s) you want to use. (See Create Session for full list of beta values.)

### Returns

`BetaManagedAgentsDeletedSession` - Confirmation that a `session` has been permanently deleted.

- `id: string`
- `type: "session_deleted"`

### Example

```bash
curl https://api.anthropic.com/v1/sessions/$SESSION_ID \
    -X DELETE \
    -H 'anthropic-version: 2023-06-01' \
    -H 'anthropic-beta: managed-agents-2026-04-01' \
    -H "X-Api-Key: $ANTHROPIC_API_KEY"
```

---

## Archive Session

**POST** `/v1/sessions/{session_id}/archive`

Archive a session (marks it but keeps data).

### Path Parameters

- `session_id`: string (required)

### Header Parameters

- `anthropic-beta`: optional array of AnthropicBeta

  Optional header to specify the beta version(s) you want to use. (See Create Session for full list of beta values.)

### Returns

`BetaManagedAgentsSession` - A Managed Agents `session` with `archived_at` timestamp populated. (See Create Session response for full session schema.)

### Example

```bash
curl https://api.anthropic.com/v1/sessions/$SESSION_ID/archive \
    -X POST \
    -H 'anthropic-version: 2023-06-01' \
    -H 'anthropic-beta: managed-agents-2026-04-01' \
    -H "X-Api-Key: $ANTHROPIC_API_KEY"
```

---

# Events

## Send Events

**POST** `/v1/sessions/{session_id}/events`

Send events to a session.

### Path Parameters

- `session_id`: string (required)

### Header Parameters

- `anthropic-beta`: optional array of AnthropicBeta

  Optional header to specify the beta version(s) you want to use. (See Create Session for full list of beta values.)

### Body Parameters

- `events`: array of BetaManagedAgentsEventParams (required)

  Events to send to the `session`.

  - `BetaManagedAgentsUserMessageEventParams = object { content, type }`

    Parameters for sending a user message to the session.

    - `content`: array of BetaManagedAgentsTextBlock | BetaManagedAgentsImageBlock | BetaManagedAgentsDocumentBlock - Array of content blocks for the user message.
      - `BetaManagedAgentsTextBlock = object { text: string, type: "text" }` - Regular text content.
      - `BetaManagedAgentsImageBlock = object { source, type: "image" }` - Image content specified directly as base64 data or as a reference via a URL.
        - `source`: BetaManagedAgentsBase64ImageSource | BetaManagedAgentsURLImageSource | BetaManagedAgentsFileImageSource
          - `BetaManagedAgentsBase64ImageSource = object { data: string, media_type: string, type: "base64" }` - Base64-encoded image data. `media_type` is the MIME type (e.g., "image/png", "image/jpeg", "image/gif", "image/webp").
          - `BetaManagedAgentsURLImageSource = object { type: "url", url: string }` - Image referenced by URL.
          - `BetaManagedAgentsFileImageSource = object { file_id: string, type: "file" }` - Image referenced by file ID.
      - `BetaManagedAgentsDocumentBlock = object { source, type: "document", context, title }` - Document content, either specified directly as base64 data, as text, or as a reference via a URL.
        - `source`: BetaManagedAgentsBase64DocumentSource | BetaManagedAgentsPlainTextDocumentSource | BetaManagedAgentsURLDocumentSource | BetaManagedAgentsFileDocumentSource
          - `BetaManagedAgentsBase64DocumentSource = object { data: string, media_type: string, type: "base64" }` - Base64-encoded document data. `media_type` is the MIME type (e.g., "application/pdf").
          - `BetaManagedAgentsPlainTextDocumentSource = object { data: string, media_type: "text/plain", type: "text" }` - Plain text document content.
          - `BetaManagedAgentsURLDocumentSource = object { type: "url", url: string }` - Document referenced by URL.
          - `BetaManagedAgentsFileDocumentSource = object { file_id: string, type: "file" }` - Document referenced by file ID.
        - `context`: optional string - Additional context about the document for the model.
        - `title`: optional string - The title of the document.
    - `type`: "user.message"

  - `BetaManagedAgentsUserInterruptEventParams = object { type }`

    Parameters for sending an interrupt to pause the agent.

    - `type`: "user.interrupt"

  - `BetaManagedAgentsUserToolConfirmationEventParams = object { result, tool_use_id, type, deny_message }`

    Parameters for confirming or denying a tool execution request.

    - `result`: "allow" | "deny" - UserToolConfirmationResult enum.
    - `tool_use_id`: string - The id of the `agent.tool_use` or `agent.mcp_tool_use` event this result corresponds to, which can be found in the last `session.status_idle` event's `stop_reason.event_ids` field.
    - `type`: "user.tool_confirmation"
    - `deny_message`: optional string - Optional message providing context for a 'deny' decision. Only allowed when result is 'deny'.

  - `BetaManagedAgentsUserCustomToolResultEventParams = object { custom_tool_use_id, type, content, is_error }`

    Parameters for providing the result of a custom tool execution.

    - `custom_tool_use_id`: string - The id of the `agent.custom_tool_use` event this result corresponds to, which can be found in the last `session.status_idle` event's `stop_reason.event_ids` field.
    - `type`: "user.custom_tool_result"
    - `content`: optional array of BetaManagedAgentsTextBlock | BetaManagedAgentsImageBlock | BetaManagedAgentsDocumentBlock - The result content returned by the tool. (See content block schemas above.)
    - `is_error`: optional boolean - Whether the tool execution resulted in an error.

### Returns

`BetaManagedAgentsSendSessionEvents` - Events that were successfully sent to the session.

- `data`: optional array of BetaManagedAgentsUserMessageEvent | BetaManagedAgentsUserInterruptEvent | BetaManagedAgentsUserToolConfirmationEvent | BetaManagedAgentsUserCustomToolResultEvent

  Sent events. Each event includes:

  - `BetaManagedAgentsUserMessageEvent = object { id, content, type: "user.message", processed_at }`
    - `id`: string - Unique identifier for this event.
    - `content`: array of BetaManagedAgentsTextBlock | BetaManagedAgentsImageBlock | BetaManagedAgentsDocumentBlock
    - `type`: "user.message"
    - `processed_at`: optional string - A timestamp in RFC 3339 format

  - `BetaManagedAgentsUserInterruptEvent = object { id, type: "user.interrupt", processed_at }`
    - `id`: string - Unique identifier for this event.
    - `type`: "user.interrupt"
    - `processed_at`: optional string - A timestamp in RFC 3339 format

  - `BetaManagedAgentsUserToolConfirmationEvent = object { id, result, tool_use_id, type: "user.tool_confirmation", deny_message, processed_at }`
    - `id`: string - Unique identifier for this event.
    - `result`: "allow" | "deny"
    - `tool_use_id`: string
    - `type`: "user.tool_confirmation"
    - `deny_message`: optional string
    - `processed_at`: optional string - A timestamp in RFC 3339 format

  - `BetaManagedAgentsUserCustomToolResultEvent = object { id, custom_tool_use_id, type: "user.custom_tool_result", content, is_error, processed_at }`
    - `id`: string - Unique identifier for this event.
    - `custom_tool_use_id`: string
    - `type`: "user.custom_tool_result"
    - `content`: optional array of content blocks
    - `is_error`: optional boolean
    - `processed_at`: optional string - A timestamp in RFC 3339 format

### Example

```bash
curl https://api.anthropic.com/v1/sessions/$SESSION_ID/events \
    -H 'Content-Type: application/json' \
    -H 'anthropic-version: 2023-06-01' \
    -H 'anthropic-beta: managed-agents-2026-04-01' \
    -H "X-Api-Key: $ANTHROPIC_API_KEY" \
    -d '{
          "events": [
            {
              "content": [
                {
                  "text": "Where is my order #1234?",
                  "type": "text"
                }
              ],
              "type": "user.message"
            }
          ]
        }'
```

---

## List Events

**GET** `/v1/sessions/{session_id}/events`

List events for a session conversation.

### Path Parameters

- `session_id`: string (required)

### Query Parameters

- `limit`: optional number - Maximum number of results to return.
- `order`: optional "asc" | "desc" - Sort direction for results, ordered by created_at. Defaults to asc (chronological).
- `page`: optional string - Opaque pagination cursor from a previous response's next_page.

### Header Parameters

- `anthropic-beta`: optional array of AnthropicBeta

  Optional header to specify the beta version(s) you want to use. (See Create Session for full list of beta values.)

### Returns

- `data`: optional array of BetaManagedAgentsSessionEvent - Events for the session, ordered by `created_at`.
- `next_page`: optional string - Opaque cursor for the next page. Null when no more results.

#### Event Types

- `BetaManagedAgentsUserMessageEvent = object { id, content, type: "user.message", processed_at }`

  A user message event in the session conversation.

  - `id`: string - Unique identifier for this event.
  - `content`: array of BetaManagedAgentsTextBlock | BetaManagedAgentsImageBlock | BetaManagedAgentsDocumentBlock - Array of content blocks comprising the user message. (See Send Events for full content block schemas.)
  - `type`: "user.message"
  - `processed_at`: optional string - A timestamp in RFC 3339 format

- `BetaManagedAgentsUserInterruptEvent = object { id, type: "user.interrupt", processed_at }`

  An interrupt event that pauses agent execution and returns control to the user.

  - `id`: string - Unique identifier for this event.
  - `type`: "user.interrupt"
  - `processed_at`: optional string - A timestamp in RFC 3339 format

- `BetaManagedAgentsUserToolConfirmationEvent = object { id, result, tool_use_id, type: "user.tool_confirmation", deny_message, processed_at }`

  A tool confirmation event that approves or denies a pending tool execution.

  - `id`: string - Unique identifier for this event.
  - `result`: "allow" | "deny" - UserToolConfirmationResult enum.
  - `tool_use_id`: string - The id of the `agent.tool_use` or `agent.mcp_tool_use` event this result corresponds to, which can be found in the last `session.status_idle` event's `stop_reason.event_ids` field.
  - `type`: "user.tool_confirmation"
  - `deny_message`: optional string - Optional message providing context for a 'deny' decision. Only allowed when result is 'deny'.
  - `processed_at`: optional string - A timestamp in RFC 3339 format

- `BetaManagedAgentsUserCustomToolResultEvent = object { id, custom_tool_use_id, type: "user.custom_tool_result", content, is_error, processed_at }`

  Event sent by the client providing the result of a custom tool execution.

  - `id`: string - Unique identifier for this event.
  - `custom_tool_use_id`: string - The id of the `agent.custom_tool_use` event this result corresponds to, which can be found in the last `session.status_idle` event's `stop_reason.event_ids` field.
  - `type`: "user.custom_tool_result"
  - `content`: optional array of BetaManagedAgentsTextBlock | BetaManagedAgentsImageBlock | BetaManagedAgentsDocumentBlock - The result content returned by the tool.
  - `is_error`: optional boolean - Whether the tool execution resulted in an error.
  - `processed_at`: optional string - A timestamp in RFC 3339 format

- `BetaManagedAgentsAgentCustomToolUseEvent = object { id, input, name, processed_at, type: "agent.custom_tool_use" }`

  Event emitted when the agent calls a custom tool. The session goes idle until the client sends a `user.custom_tool_result` event with the result.

  - `id`: string - Unique identifier for this event.
  - `input`: map[unknown] - Input parameters for the tool call.
  - `name`: string - Name of the custom tool being called.
  - `processed_at`: string - A timestamp in RFC 3339 format
  - `type`: "agent.custom_tool_use"

- `BetaManagedAgentsAgentMessageEvent = object { id, content, processed_at, type: "agent.message" }`

  An agent response event in the session conversation.

  - `id`: string - Unique identifier for this event.
  - `content`: array of BetaManagedAgentsTextBlock - Array of text blocks comprising the agent response.
    - `text`: string - The text content.
    - `type`: "text"
  - `processed_at`: string - A timestamp in RFC 3339 format
  - `type`: "agent.message"

- `BetaManagedAgentsAgentThinkingEvent = object { id, processed_at, type: "agent.thinking" }`

  Indicates the agent is making forward progress via extended thinking. A progress signal, not a content carrier.

  - `id`: string - Unique identifier for this event.
  - `processed_at`: string - A timestamp in RFC 3339 format
  - `type`: "agent.thinking"

- `BetaManagedAgentsAgentMCPToolUseEvent = object { id, input, mcp_server_name, name, processed_at, type: "agent.mcp_tool_use", evaluated_permission }`

  Event emitted when the agent invokes a tool provided by an MCP server.

  - `id`: string - Unique identifier for this event.
  - `input`: map[unknown] - Input parameters for the tool call.
  - `mcp_server_name`: string - Name of the MCP server providing the tool.
  - `name`: string - Name of the MCP tool being used.
  - `processed_at`: string - A timestamp in RFC 3339 format
  - `type`: "agent.mcp_tool_use"
  - `evaluated_permission`: optional "allow" | "ask" | "deny" - AgentEvaluatedPermission enum.

- `BetaManagedAgentsAgentMCPToolResultEvent = object { id, mcp_tool_use_id, processed_at, type: "agent.mcp_tool_result", content, is_error }`

  Event representing the result of an MCP tool execution.

  - `id`: string - Unique identifier for this event.
  - `mcp_tool_use_id`: string - The id of the `agent.mcp_tool_use` event this result corresponds to.
  - `processed_at`: string - A timestamp in RFC 3339 format
  - `type`: "agent.mcp_tool_result"
  - `content`: optional array of BetaManagedAgentsTextBlock | BetaManagedAgentsImageBlock | BetaManagedAgentsDocumentBlock - The result content returned by the tool.
  - `is_error`: optional boolean - Whether the tool execution resulted in an error.

- `BetaManagedAgentsAgentToolUseEvent = object { id, input, name, processed_at, type: "agent.tool_use", evaluated_permission }`

  Event emitted when the agent invokes a built-in agent tool.

  - `id`: string - Unique identifier for this event.
  - `input`: map[unknown] - Input parameters for the tool call.
  - `name`: string - Name of the agent tool being used.
  - `processed_at`: string - A timestamp in RFC 3339 format
  - `type`: "agent.tool_use"
  - `evaluated_permission`: optional "allow" | "ask" | "deny" - AgentEvaluatedPermission enum.

- `BetaManagedAgentsAgentToolResultEvent = object { id, processed_at, tool_use_id, type: "agent.tool_result", content, is_error }`

  Event representing the result of an agent tool execution.

  - `id`: string - Unique identifier for this event.
  - `processed_at`: string - A timestamp in RFC 3339 format
  - `tool_use_id`: string - The id of the `agent.tool_use` event this result corresponds to.
  - `type`: "agent.tool_result"
  - `content`: optional array of BetaManagedAgentsTextBlock | BetaManagedAgentsImageBlock | BetaManagedAgentsDocumentBlock - The result content returned by the tool.
  - `is_error`: optional boolean - Whether the tool execution resulted in an error.

- `BetaManagedAgentsAgentThreadContextCompactedEvent = object { id, processed_at, type: "agent.thread_context_compacted" }`

  Indicates that context compaction (summarization) occurred during the session.

  - `id`: string - Unique identifier for this event.
  - `processed_at`: string - A timestamp in RFC 3339 format
  - `type`: "agent.thread_context_compacted"

- `BetaManagedAgentsSessionErrorEvent = object { id, error, processed_at, type: "session.error" }`

  An error event indicating a problem occurred during session execution.

  - `id`: string - Unique identifier for this event.
  - `error`: one of the following error types:
    - `BetaManagedAgentsUnknownError = object { message, retry_status, type: "unknown_error" }` - An unknown or unexpected error occurred during session execution. A fallback variant; clients that don't recognize a new error code can match on `retry_status` and `message` alone.
    - `BetaManagedAgentsModelOverloadedError = object { message, retry_status, type: "model_overloaded_error" }` - The model is currently overloaded. Emitted after automatic retries are exhausted.
    - `BetaManagedAgentsModelRateLimitedError = object { message, retry_status, type: "model_rate_limited_error" }` - The model request was rate-limited.
    - `BetaManagedAgentsModelRequestFailedError = object { message, retry_status, type: "model_request_failed_error" }` - A model request failed for a reason other than overload or rate-limiting.
    - `BetaManagedAgentsMCPConnectionFailedError = object { mcp_server_name, message, retry_status, type: "mcp_connection_failed_error" }` - Failed to connect to an MCP server. Includes `mcp_server_name: string`.
    - `BetaManagedAgentsMCPAuthenticationFailedError = object { mcp_server_name, message, retry_status, type: "mcp_authentication_failed_error" }` - Authentication to an MCP server failed. Includes `mcp_server_name: string`.
    - `BetaManagedAgentsBillingError = object { message, retry_status, type: "billing_error" }` - The caller's organization or workspace cannot make model requests -- out of credits or spend limit reached. Retrying with the same credentials will not succeed; the caller must resolve the billing state.

    All error types include:
    - `message`: string - Human-readable error description.
    - `retry_status`: BetaManagedAgentsRetryStatusRetrying | BetaManagedAgentsRetryStatusExhausted | BetaManagedAgentsRetryStatusTerminal - What the client should do next in response to this error.
      - `BetaManagedAgentsRetryStatusRetrying = object { type: "retrying" }` - The server is retrying automatically. Client should wait; the same error type may fire again as retrying, then once as exhausted when the retry budget runs out.
      - `BetaManagedAgentsRetryStatusExhausted = object { type: "exhausted" }` - This turn is dead; queued inputs are flushed and the session returns to idle. Client may send a new prompt.
      - `BetaManagedAgentsRetryStatusTerminal = object { type: "terminal" }` - The session encountered a terminal error and will transition to `terminated` state.
  - `processed_at`: string - A timestamp in RFC 3339 format
  - `type`: "session.error"

- `BetaManagedAgentsSessionStatusRescheduledEvent = object { id, processed_at, type: "session.status_rescheduled" }`

  Indicates the session is recovering from an error state and is rescheduled for execution.

  - `id`: string - Unique identifier for this event.
  - `processed_at`: string - A timestamp in RFC 3339 format
  - `type`: "session.status_rescheduled"

- `BetaManagedAgentsSessionStatusRunningEvent = object { id, processed_at, type: "session.status_running" }`

  Indicates the session is actively running and the agent is working.

  - `id`: string - Unique identifier for this event.
  - `processed_at`: string - A timestamp in RFC 3339 format
  - `type`: "session.status_running"

- `BetaManagedAgentsSessionStatusIdleEvent = object { id, processed_at, stop_reason, type: "session.status_idle" }`

  Indicates the agent has paused and is awaiting user input.

  - `id`: string - Unique identifier for this event.
  - `processed_at`: string - A timestamp in RFC 3339 format
  - `stop_reason`: one of:
    - `BetaManagedAgentsSessionEndTurn = object { type: "end_turn" }` - The agent completed its turn naturally and is ready for the next user message.
    - `BetaManagedAgentsSessionRequiresAction = object { event_ids, type: "requires_action" }` - The agent is idle waiting on one or more blocking user-input events (tool confirmation, custom tool result, etc.). Resolving all of them transitions the session back to running.
      - `event_ids`: array of string - The ids of events the agent is blocked on. Resolving fewer than all re-emits `session.status_idle` with the remainder.
    - `BetaManagedAgentsSessionRetriesExhausted = object { type: "retries_exhausted" }` - The turn ended because the retry budget was exhausted (`max_iterations` hit or an error escalated to `retry_status: 'exhausted'`).
  - `type`: "session.status_idle"

- `BetaManagedAgentsSessionStatusTerminatedEvent = object { id, processed_at, type: "session.status_terminated" }`

  Indicates the session has terminated, either due to an error or completion.

  - `id`: string - Unique identifier for this event.
  - `processed_at`: string - A timestamp in RFC 3339 format
  - `type`: "session.status_terminated"

- `BetaManagedAgentsSpanModelRequestStartEvent = object { id, processed_at, type: "span.model_request_start" }`

  Emitted when a model request is initiated by the agent.

  - `id`: string - Unique identifier for this event.
  - `processed_at`: string - A timestamp in RFC 3339 format
  - `type`: "span.model_request_start"

- `BetaManagedAgentsSpanModelRequestEndEvent = object { id, is_error, model_request_start_id, model_usage, processed_at, type: "span.model_request_end" }`

  Emitted when a model request completes.

  - `id`: string - Unique identifier for this event.
  - `is_error`: boolean - Whether the model request resulted in an error.
  - `model_request_start_id`: string - The id of the corresponding `span.model_request_start` event.
  - `model_usage`: BetaManagedAgentsSpanModelUsage - Token usage for a single model request.
    - `cache_creation_input_tokens`: number - Tokens used to create prompt cache in this request.
    - `cache_read_input_tokens`: number - Tokens read from prompt cache in this request.
    - `input_tokens`: number - Input tokens consumed by this request.
    - `output_tokens`: number - Output tokens generated by this request.
    - `speed`: optional "standard" | "fast" - Inference speed mode.
  - `processed_at`: string - A timestamp in RFC 3339 format
  - `type`: "span.model_request_end"

- `BetaManagedAgentsSessionDeletedEvent = object { id, processed_at, type: "session.deleted" }`

  Emitted when a session has been deleted. Terminates any active event stream -- no further events will be emitted for this session.

  - `id`: string - Unique identifier for this event.
  - `processed_at`: string - A timestamp in RFC 3339 format
  - `type`: "session.deleted"

### Example

```bash
curl https://api.anthropic.com/v1/sessions/$SESSION_ID/events \
    -H 'anthropic-version: 2023-06-01' \
    -H 'anthropic-beta: managed-agents-2026-04-01' \
    -H "X-Api-Key: $ANTHROPIC_API_KEY"
```

---

## Stream Events

**GET** `/v1/sessions/{session_id}/events/stream`

Stream session events via Server-Sent Events (SSE).

### Path Parameters

- `session_id`: string (required)

### Header Parameters

- `anthropic-beta`: optional array of AnthropicBeta

  Optional header to specify the beta version(s) you want to use. (See Create Session for full list of beta values.)

### Returns

`BetaManagedAgentsStreamSessionEvents` - Server-sent events in the session stream.

The stream emits all the same event types as List Events (see above), including:

**User Events:**
- `user.message` - BetaManagedAgentsUserMessageEvent
- `user.interrupt` - BetaManagedAgentsUserInterruptEvent
- `user.tool_confirmation` - BetaManagedAgentsUserToolConfirmationEvent
- `user.custom_tool_result` - BetaManagedAgentsUserCustomToolResultEvent

**Agent Events:**
- `agent.custom_tool_use` - BetaManagedAgentsAgentCustomToolUseEvent
- `agent.message` - BetaManagedAgentsAgentMessageEvent
- `agent.thinking` - BetaManagedAgentsAgentThinkingEvent
- `agent.mcp_tool_use` - BetaManagedAgentsAgentMCPToolUseEvent
- `agent.mcp_tool_result` - BetaManagedAgentsAgentMCPToolResultEvent
- `agent.tool_use` - BetaManagedAgentsAgentToolUseEvent
- `agent.tool_result` - BetaManagedAgentsAgentToolResultEvent
- `agent.thread_context_compacted` - BetaManagedAgentsAgentThreadContextCompactedEvent

**Session Events:**
- `session.error` - BetaManagedAgentsSessionErrorEvent
- `session.status_rescheduled` - BetaManagedAgentsSessionStatusRescheduledEvent
- `session.status_running` - BetaManagedAgentsSessionStatusRunningEvent
- `session.status_idle` - BetaManagedAgentsSessionStatusIdleEvent
- `session.status_terminated` - BetaManagedAgentsSessionStatusTerminatedEvent
- `session.deleted` - BetaManagedAgentsSessionDeletedEvent

**Span Events:**
- `span.model_request_start` - BetaManagedAgentsSpanModelRequestStartEvent
- `span.model_request_end` - BetaManagedAgentsSpanModelRequestEndEvent

See the List Events section above for the complete schema of each event type.

### Example

```bash
curl https://api.anthropic.com/v1/sessions/$SESSION_ID/events/stream \
    -H 'anthropic-version: 2023-06-01' \
    -H 'anthropic-beta: managed-agents-2026-04-01' \
    -H "X-Api-Key: $ANTHROPIC_API_KEY"
```

---

# Domain Types

## BetaManagedAgentsAgentParams

Specification for an Agent. Provide a specific `version` or use the short-form `agent="agent_id"` for the most recent version.

- `id`: string - The `agent` ID.
- `type`: "agent"
- `version`: optional number - The specific `agent` version to use. Omit to use the latest version. Must be at least 1 if specified.

## BetaManagedAgentsBranchCheckout

- `name`: string - Branch name to check out.
- `type`: "branch"

## BetaManagedAgentsCommitCheckout

- `sha`: string - Full commit SHA to check out.
- `type`: "commit"

## BetaManagedAgentsCacheCreationUsage

Prompt-cache creation token usage broken down by cache lifetime.

- `ephemeral_1h_input_tokens`: optional number - Tokens used to create 1-hour ephemeral cache entries.
- `ephemeral_5m_input_tokens`: optional number - Tokens used to create 5-minute ephemeral cache entries.

## BetaManagedAgentsDeletedSession

Confirmation that a `session` has been permanently deleted.

- `id`: string
- `type`: "session_deleted"

## BetaManagedAgentsFileResourceParams

Mount a file uploaded via the Files API into the session.

- `file_id`: string - ID of a previously uploaded file.
- `type`: "file"
- `mount_path`: optional string - Mount path in the container. Defaults to `/mnt/session/uploads/<file_id>`.

## BetaManagedAgentsGitHubRepositoryResourceParams

Mount a GitHub repository into the session's container.

- `authorization_token`: string - GitHub authorization token used to clone the repository.
- `type`: "github_repository"
- `url`: string - Github URL of the repository.
- `checkout`: optional BetaManagedAgentsBranchCheckout | BetaManagedAgentsCommitCheckout - Branch or commit to check out. Defaults to the repository's default branch.
- `mount_path`: optional string - Mount path in the container. Defaults to `/workspace/<repo-name>`.

## BetaManagedAgentsSession

A Managed Agents `session`. See Create Session response for full schema.

## BetaManagedAgentsSessionAgent

Resolved `agent` definition for a `session`. Snapshot of the `agent` at `session` creation time. See Create Session response for full schema.

## BetaManagedAgentsSessionStats

Timing statistics for a session.

- `active_seconds`: optional number - Cumulative time in seconds the session spent in running status. Excludes idle time.
- `duration_seconds`: optional number - Elapsed time since session creation in seconds. For terminated sessions, frozen at the final update.

## BetaManagedAgentsSessionUsage

Cumulative token usage for a session across all turns.

- `cache_creation`: optional BetaManagedAgentsCacheCreationUsage - Prompt-cache creation token usage broken down by cache lifetime.
- `cache_read_input_tokens`: optional number - Total tokens read from prompt cache.
- `input_tokens`: optional number - Total input tokens consumed across all turns.
- `output_tokens`: optional number - Total output tokens generated across all turns.

## BetaManagedAgentsSpanModelUsage

Token usage for a single model request.

- `cache_creation_input_tokens`: number - Tokens used to create prompt cache in this request.
- `cache_read_input_tokens`: number - Tokens read from prompt cache in this request.
- `input_tokens`: number - Input tokens consumed by this request.
- `output_tokens`: number - Output tokens generated by this request.
- `speed`: optional "standard" | "fast" - Inference speed mode.

## Error Types

- `BetaManagedAgentsUnknownError` - type: "unknown_error"
- `BetaManagedAgentsModelOverloadedError` - type: "model_overloaded_error"
- `BetaManagedAgentsModelRateLimitedError` - type: "model_rate_limited_error"
- `BetaManagedAgentsModelRequestFailedError` - type: "model_request_failed_error"
- `BetaManagedAgentsMCPConnectionFailedError` - type: "mcp_connection_failed_error" (includes `mcp_server_name`)
- `BetaManagedAgentsMCPAuthenticationFailedError` - type: "mcp_authentication_failed_error" (includes `mcp_server_name`)
- `BetaManagedAgentsBillingError` - type: "billing_error"

All error types include `message: string` and `retry_status` with one of:
- `BetaManagedAgentsRetryStatusRetrying { type: "retrying" }` - The server is retrying automatically.
- `BetaManagedAgentsRetryStatusExhausted { type: "exhausted" }` - This turn is dead; session returns to idle.
- `BetaManagedAgentsRetryStatusTerminal { type: "terminal" }` - Session will transition to `terminated` state.

## Permission Policies

- `BetaManagedAgentsAlwaysAllowPolicy = object { type: "always_allow" }` - Tool calls are automatically approved without user confirmation.
- `BetaManagedAgentsAlwaysAskPolicy = object { type: "always_ask" }` - Tool calls require user confirmation before execution.

## Stop Reasons

- `BetaManagedAgentsSessionEndTurn = object { type: "end_turn" }` - The agent completed its turn naturally and is ready for the next user message.
- `BetaManagedAgentsSessionRequiresAction = object { event_ids: array of string, type: "requires_action" }` - The agent is idle waiting on one or more blocking user-input events.
- `BetaManagedAgentsSessionRetriesExhausted = object { type: "retries_exhausted" }` - The turn ended because the retry budget was exhausted.
