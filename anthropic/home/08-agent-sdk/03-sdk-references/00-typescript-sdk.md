# Agent SDK reference - TypeScript

Complete API reference for the TypeScript Agent SDK, including all functions, types, and interfaces.

> Try the new V2 interface (preview): A simplified interface with send() and stream() patterns is now available, making multi-turn conversations easier. Learn more about the TypeScript V2 preview.

## Installation

```bash
npm install @anthropic-ai/claude-agent-sdk
```

## Functions

### query()

The primary function for interacting with Claude Code. Creates an async generator that streams messages as they arrive.

```typescript
function query({
  prompt,
  options
}: {
  prompt: string | AsyncIterable<SDKUserMessage>;
  options?: Options;
}): Query;
```

| Parameter | Type | Description |
|---|---|---|
| prompt | string \| AsyncIterable\<SDKUserMessage\> | The input prompt as a string or async iterable for streaming mode |
| options | Options | Optional configuration object (see Options type below) |

Returns a Query object that extends AsyncGenerator\<SDKMessage, void\> with additional methods.

### tool()

Creates a type-safe MCP tool definition for use with SDK MCP servers.

```typescript
function tool<Schema extends AnyZodRawShape>(
  name: string,
  description: string,
  inputSchema: Schema,
  handler: (args: InferShape<Schema>, extra: unknown) => Promise<CallToolResult>,
  extras?: { annotations?: ToolAnnotations }
): SdkMcpToolDefinition<Schema>;
```

| Parameter | Type | Description |
|---|---|---|
| name | string | The name of the tool |
| description | string | A description of what the tool does |
| inputSchema | Schema extends AnyZodRawShape | Zod schema defining the tool's input parameters |
| handler | (args, extra) => Promise\<CallToolResult\> | Async function that executes the tool logic |
| extras | { annotations?: ToolAnnotations } | Optional MCP tool annotations |

**ToolAnnotations** (re-exported from @modelcontextprotocol/sdk/types.js):

| Field | Type | Default | Description |
|---|---|---|---|
| title | string | undefined | Human-readable title for the tool |
| readOnlyHint | boolean | false | If true, the tool does not modify its environment |
| destructiveHint | boolean | true | If true, the tool may perform destructive updates |
| idempotentHint | boolean | false | If true, repeated calls with same arguments have no additional effect |
| openWorldHint | boolean | true | If true, the tool interacts with external entities |

### createSdkMcpServer()

Creates an MCP server instance that runs in the same process as your application.

```typescript
function createSdkMcpServer(options: {
  name: string;
  version?: string;
  tools?: Array<SdkMcpToolDefinition<any>>;
}): McpSdkServerConfigWithInstance;
```

### listSessions()

Discovers and lists past sessions with light metadata.

```typescript
function listSessions(options?: ListSessionsOptions): Promise<SDKSessionInfo[]>;
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| options.dir | string | undefined | Directory to list sessions for |
| options.limit | number | undefined | Maximum number of sessions to return |
| options.includeWorktrees | boolean | true | Include sessions from all worktree paths |

### getSessionMessages()

Reads user and assistant messages from a past session transcript.

```typescript
function getSessionMessages(
  sessionId: string,
  options?: GetSessionMessagesOptions
): Promise<SessionMessage[]>;
```

## Types

### Options

Configuration object for the query() function. Key properties:

| Property | Type | Default | Description |
|---|---|---|---|
| allowedTools | string[] | [] | Tools to auto-approve without prompting |
| disallowedTools | string[] | [] | Tools to always deny |
| agents | Record\<string, AgentDefinition\> | undefined | Programmatically define subagents |
| canUseTool | CanUseTool | undefined | Custom permission function for tool usage |
| cwd | string | process.cwd() | Current working directory |
| effort | 'low' \| 'medium' \| 'high' \| 'max' | 'high' | Controls how much effort Claude puts into its response |
| enableFileCheckpointing | boolean | false | Enable file change tracking for rewinding |
| env | Record\<string, string \| undefined\> | process.env | Environment variables |
| hooks | Partial\<Record\<HookEvent, HookCallbackMatcher[]\>\> | {} | Hook callbacks for events |
| includePartialMessages | boolean | false | Include partial message events |
| maxBudgetUsd | number | undefined | Maximum budget in USD for the query |
| maxTurns | number | undefined | Maximum agentic turns |
| mcpServers | Record\<string, McpServerConfig\> | {} | MCP server configurations |
| model | string | Default from CLI | Claude model to use |
| outputFormat | { type: 'json_schema', schema: JSONSchema } | undefined | Define output format for structured results |
| permissionMode | PermissionMode | 'default' | Permission mode for the session |
| plugins | SdkPluginConfig[] | [] | Load custom plugins from local paths |
| resume | string | undefined | Session ID to resume |
| settingSources | SettingSource[] | [] (no settings) | Control which filesystem settings to load |
| systemPrompt | string \| { type: 'preset'; preset: 'claude_code'; append?: string } | undefined | System prompt configuration |
| tools | string[] \| { type: 'preset'; preset: 'claude_code' } | undefined | Tool configuration |

### Query object

Interface returned by the query() function.

```typescript
interface Query extends AsyncGenerator<SDKMessage, void> {
  interrupt(): Promise<void>;
  rewindFiles(userMessageId: string, options?: { dryRun?: boolean }): Promise<RewindFilesResult>;
  setPermissionMode(mode: PermissionMode): Promise<void>;
  setModel(model?: string): Promise<void>;
  initializationResult(): Promise<SDKControlInitializeResponse>;
  supportedCommands(): Promise<SlashCommand[]>;
  supportedModels(): Promise<ModelInfo[]>;
  supportedAgents(): Promise<AgentInfo[]>;
  mcpServerStatus(): Promise<McpServerStatus[]>;
  accountInfo(): Promise<AccountInfo>;
  reconnectMcpServer(serverName: string): Promise<void>;
  toggleMcpServer(serverName: string, enabled: boolean): Promise<void>;
  setMcpServers(servers: Record<string, McpServerConfig>): Promise<McpSetServersResult>;
  streamInput(stream: AsyncIterable<SDKUserMessage>): Promise<void>;
  stopTask(taskId: string): Promise<void>;
  close(): void;
}
```

### AgentDefinition

Configuration for a subagent defined programmatically.

```typescript
type AgentDefinition = {
  description: string;
  tools?: string[];
  disallowedTools?: string[];
  prompt: string;
  model?: "sonnet" | "opus" | "haiku" | "inherit";
  mcpServers?: AgentMcpServerSpec[];
  skills?: string[];
  maxTurns?: number;
};
```

### PermissionMode

```typescript
type PermissionMode =
  | "default"          // Standard permission behavior
  | "acceptEdits"      // Auto-accept file edits
  | "bypassPermissions" // Bypass all permission checks
  | "plan"             // Planning mode - no execution
  | "dontAsk";         // Don't prompt, deny if not pre-approved
```

### CanUseTool

Custom permission function type for controlling tool usage.

```typescript
type CanUseTool = (
  toolName: string,
  input: Record<string, unknown>,
  options: {
    signal: AbortSignal;
    suggestions?: PermissionUpdate[];
    blockedPath?: string;
    decisionReason?: string;
    toolUseID: string;
    agentID?: string;
  }
) => Promise<PermissionResult>;
```

### PermissionResult

```typescript
type PermissionResult =
  | { behavior: "allow"; updatedInput?: Record<string, unknown>; updatedPermissions?: PermissionUpdate[]; }
  | { behavior: "deny"; message: string; interrupt?: boolean; };
```

### McpServerConfig

```typescript
type McpServerConfig =
  | McpStdioServerConfig    // { type?: "stdio"; command: string; args?: string[]; env?: Record<string, string>; }
  | McpSSEServerConfig      // { type: "sse"; url: string; headers?: Record<string, string>; }
  | McpHttpServerConfig     // { type: "http"; url: string; headers?: Record<string, string>; }
  | McpSdkServerConfigWithInstance; // { type: "sdk"; name: string; instance: McpServer; }
```

### SettingSource

```typescript
type SettingSource = "user" | "project" | "local";
```

| Value | Description | Location |
|---|---|---|
| 'user' | Global user settings | ~/.claude/settings.json |
| 'project' | Shared project settings | .claude/settings.json |
| 'local' | Local project settings | .claude/settings.local.json |

## Message Types

### SDKMessage

Union type of all possible messages returned by the query.

Key message types:

- **SDKAssistantMessage** (`type: "assistant"`): Assistant response with nested BetaMessage
- **SDKUserMessage** (`type: "user"`): User input message
- **SDKResultMessage** (`type: "result"`): Final result with total_cost_usd, usage, modelUsage
- **SDKSystemMessage** (`type: "system"`, `subtype: "init"`): System initialization with tools, mcp_servers, slash_commands
- **SDKPartialAssistantMessage** (`type: "stream_event"`): Streaming partial message (when includePartialMessages is true)
- **SDKCompactBoundaryMessage** (`type: "system"`, `subtype: "compact_boundary"`): Conversation compaction boundary

### SDKResultMessage

```typescript
type SDKResultMessage =
  | { type: "result"; subtype: "success"; result: string; total_cost_usd: number; usage: NonNullableUsage; modelUsage: { [modelName: string]: ModelUsage }; structured_output?: unknown; /* ... */ }
  | { type: "result"; subtype: "error_max_turns" | "error_during_execution" | "error_max_budget_usd" | "error_max_structured_output_retries"; errors: string[]; /* ... */ };
```

## Hook Types

### HookEvent

```typescript
type HookEvent =
  | "PreToolUse" | "PostToolUse" | "PostToolUseFailure"
  | "Notification" | "UserPromptSubmit"
  | "SessionStart" | "SessionEnd" | "Stop"
  | "SubagentStart" | "SubagentStop"
  | "PreCompact" | "PermissionRequest"
  | "Setup" | "TeammateIdle" | "TaskCompleted"
  | "ConfigChange" | "WorktreeCreate" | "WorktreeRemove";
```

### HookCallback

```typescript
type HookCallback = (
  input: HookInput,
  toolUseID: string | undefined,
  options: { signal: AbortSignal }
) => Promise<HookJSONOutput>;
```

### HookCallbackMatcher

```typescript
interface HookCallbackMatcher {
  matcher?: string;
  hooks: HookCallback[];
  timeout?: number;
}
```

## Tool Input Types

Built-in tool input schemas (exported from @anthropic-ai/claude-agent-sdk):

| Tool | Input Type | Key Fields |
|---|---|---|
| Agent | AgentInput | description, prompt, subagent_type, model?, resume? |
| AskUserQuestion | AskUserQuestionInput | questions[] with question, header, options, multiSelect |
| Bash | BashInput | command, timeout?, description?, run_in_background? |
| Edit | FileEditInput | file_path, old_string, new_string, replace_all? |
| Read | FileReadInput | file_path, offset?, limit?, pages? |
| Write | FileWriteInput | file_path, content |
| Glob | GlobInput | pattern, path? |
| Grep | GrepInput | pattern, path?, glob?, output_mode?, multiline? |
| WebFetch | WebFetchInput | url, prompt |
| WebSearch | WebSearchInput | query, allowed_domains?, blocked_domains? |
| TodoWrite | TodoWriteInput | todos[] with content, status, activeForm |
| NotebookEdit | NotebookEditInput | notebook_path, new_source, cell_type?, edit_mode? |

For the complete and most up-to-date API reference, see the [Anthropic documentation](https://platform.claude.com/docs/en/agent-sdk/typescript).
