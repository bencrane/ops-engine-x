# Agent SDK reference - Python

Complete API reference for the Python Agent SDK, including all functions, types, and classes.

## Installation

```bash
pip install claude-agent-sdk
```

## Choosing between query() and ClaudeSDKClient

| Feature | query() | ClaudeSDKClient |
|---|---|---|
| Session | Creates new session each time | Reuses same session |
| Conversation | Single exchange | Multiple exchanges in same context |
| Connection | Managed automatically | Manual control |
| Streaming Input | Supported | Supported |
| Interrupts | Not supported | Supported |
| Hooks | Supported | Supported |
| Custom Tools | Supported | Supported |
| Continue Chat | New session each time | Maintains conversation |
| Use Case | One-off tasks | Continuous conversations |

## Functions

### query()

Creates a new session for each interaction. Returns an async iterator that yields messages.

```python
async def query(
    *,
    prompt: str | AsyncIterable[dict[str, Any]],
    options: ClaudeAgentOptions | None = None,
    transport: Transport | None = None
) -> AsyncIterator[Message]
```

| Parameter | Type | Description |
|---|---|---|
| prompt | str \| AsyncIterable[dict] | The input prompt or async iterable for streaming |
| options | ClaudeAgentOptions \| None | Optional configuration object |
| transport | Transport \| None | Optional custom transport |

### tool()

Decorator for defining MCP tools with type safety.

```python
def tool(
    name: str,
    description: str,
    input_schema: type | dict[str, Any],
    annotations: ToolAnnotations | None = None
) -> Callable
```

Input schema options:

- **Simple type mapping**: `{"text": str, "count": int, "enabled": bool}`
- **JSON Schema format**: `{"type": "object", "properties": {...}, "required": [...]}`

```python
from claude_agent_sdk import tool
from typing import Any

@tool("greet", "Greet a user", {"name": str})
async def greet(args: dict[str, Any]) -> dict[str, Any]:
    return {"content": [{"type": "text", "text": f"Hello, {args['name']}!"}]}
```

### create_sdk_mcp_server()

Create an in-process MCP server.

```python
def create_sdk_mcp_server(
    name: str,
    version: str = "1.0.0",
    tools: list[SdkMcpTool[Any]] | None = None
) -> McpSdkServerConfig
```

### list_sessions()

Lists past sessions with metadata. Synchronous.

```python
def list_sessions(
    directory: str | None = None,
    limit: int | None = None,
    include_worktrees: bool = True
) -> list[SDKSessionInfo]
```

### get_session_messages()

Retrieves messages from a past session. Synchronous.

```python
def get_session_messages(
    session_id: str,
    directory: str | None = None,
    limit: int | None = None,
    offset: int = 0
) -> list[SessionMessage]
```

## Classes

### ClaudeSDKClient

Maintains a conversation session across multiple exchanges.

```python
class ClaudeSDKClient:
    def __init__(self, options: ClaudeAgentOptions | None = None, transport: Transport | None = None)
    async def connect(self, prompt: str | AsyncIterable[dict] | None = None) -> None
    async def query(self, prompt: str | AsyncIterable[dict], session_id: str = "default") -> None
    async def receive_messages(self) -> AsyncIterator[Message]
    async def receive_response(self) -> AsyncIterator[Message]
    async def interrupt(self) -> None
    async def set_permission_mode(self, mode: str) -> None
    async def set_model(self, model: str | None = None) -> None
    async def rewind_files(self, user_message_id: str) -> None
    async def get_mcp_status(self) -> list[McpServerStatus]
    async def add_mcp_server(self, name: str, config: McpServerConfig) -> None
    async def remove_mcp_server(self, name: str) -> None
    async def disconnect(self) -> None
```

Context manager support:

```python
async with ClaudeSDKClient() as client:
    await client.query("Hello Claude")
    async for message in client.receive_response():
        print(message)
```

> **Important**: When iterating over messages, avoid using `break` to exit early as this can cause asyncio cleanup issues.

> **Buffer behavior after interrupt**: interrupt() sends a stop signal but does not clear the message buffer. You must drain messages with receive_response() before reading the response to a new query.

## Types

### ClaudeAgentOptions

Configuration for query() and ClaudeSDKClient. Key properties:

| Property | Type | Default | Description |
|---|---|---|---|
| allowed_tools | list[str] | [] | Tools to auto-approve |
| disallowed_tools | list[str] | [] | Tools to always deny |
| agents | dict[str, AgentDefinition] | None | Programmatically define subagents |
| can_use_tool | CanUseTool \| None | None | Custom permission function |
| cwd | str | os.getcwd() | Current working directory |
| effort | str | 'high' | Controls effort ('low', 'medium', 'high', 'max') |
| enable_file_checkpointing | bool | False | Enable file change tracking |
| env | dict[str, str \| None] | os.environ | Environment variables |
| hooks | dict[str, list[HookMatcher]] | {} | Hook callbacks |
| include_partial_messages | bool | False | Include streaming events |
| max_budget_usd | float \| None | None | Maximum budget in USD |
| max_turns | int \| None | None | Maximum agentic turns |
| mcp_servers | dict[str, McpServerConfig] | {} | MCP server configurations |
| model | str \| None | Default | Claude model to use |
| output_format | dict | None | Structured output format |
| permission_mode | str | 'default' | Permission mode |
| plugins | list[SdkPluginConfig] | [] | Load custom plugins |
| resume | str \| None | None | Session ID to resume |
| setting_sources | list[str] | [] | Which filesystem settings to load |
| system_prompt | str \| dict | None | System prompt configuration |
| sandbox | SandboxSettings \| None | None | Sandbox behavior configuration |

### AgentDefinition

```python
@dataclass
class AgentDefinition:
    description: str
    prompt: str
    tools: list[str] | None = None
    disallowed_tools: list[str] | None = None
    model: str | None = None  # "sonnet", "opus", "haiku", "inherit"
    max_turns: int | None = None
```

### PermissionMode

```python
PermissionMode = Literal["default", "acceptEdits", "bypassPermissions", "plan"]
```

### CanUseTool

```python
CanUseTool = Callable[
    [str, dict, ToolPermissionContext],
    Awaitable[PermissionResultAllow | PermissionResultDeny]
]
```

### PermissionResult types

```python
@dataclass
class PermissionResultAllow:
    updated_input: dict | None = None

@dataclass
class PermissionResultDeny:
    message: str = ""
    interrupt: bool = False
```

## Message Types

### Message (union type)

Key message types:

- **AssistantMessage**: Assistant response with content blocks (TextBlock, ToolUseBlock, etc.)
- **UserMessage**: User input message with uuid for checkpointing
- **ResultMessage**: Final result with total_cost_usd, usage, session_id, structured_output
- **SystemMessage**: System init with tools, mcp_servers, slash_commands
- **StreamEvent**: Raw streaming events (when include_partial_messages=True)

### ResultMessage

```python
@dataclass
class ResultMessage:
    type: str  # "result"
    subtype: str  # "success", "error_max_turns", "error_during_execution", etc.
    session_id: str
    result: str | None
    total_cost_usd: float
    usage: dict[str, int]
    is_error: bool
    duration_ms: int
    num_turns: int
    structured_output: Any | None = None
```

### Content Block Types

- **TextBlock**: `text: str`
- **ThinkingBlock**: `thinking: str`
- **ToolUseBlock**: `name: str, input: dict, id: str`
- **ToolResultBlock**: `tool_use_id: str, content: str | list`

## Hook Types

### HookEvent

```python
HookEvent = Literal[
    "PreToolUse", "PostToolUse", "PostToolUseFailure",
    "Notification", "UserPromptSubmit", "Stop",
    "SubagentStart", "SubagentStop", "PreCompact", "PermissionRequest"
]
```

> Note: SessionStart and SessionEnd are TypeScript-only as SDK callback hooks. In Python, they're only available as shell command hooks in settings files.

### HookMatcher

```python
@dataclass
class HookMatcher:
    matcher: str | None = None  # Regex pattern
    hooks: list[HookCallback] = field(default_factory=list)
    timeout: int = 60
```

### HookCallback

```python
HookCallback = Callable[
    [dict[str, Any], str | None, HookContext],
    Awaitable[dict[str, Any]]
]
```

## Tool Input/Output Types

Built-in tool schemas:

| Tool | Key Input Fields |
|---|---|
| Agent | description, prompt, subagent_type, model? |
| AskUserQuestion | questions[] with question, header, options, multiSelect |
| Bash | command, timeout?, description?, run_in_background? |
| Edit | file_path, old_string, new_string, replace_all? |
| Read | file_path, offset?, limit?, pages? |
| Write | file_path, content |
| Glob | pattern, path? |
| Grep | pattern, path?, glob?, output_mode?, multiline? |
| WebFetch | url, prompt |
| WebSearch | query, allowed_domains?, blocked_domains? |
| TodoWrite | todos[] with content, status, activeForm |
| NotebookEdit | notebook_path, new_source, cell_type?, edit_mode? |

## Sandbox Configuration

### SandboxSettings

```python
class SandboxSettings(TypedDict, total=False):
    enabled: bool                    # Enable sandbox mode
    autoAllowBashIfSandboxed: bool  # Auto-approve bash when sandboxed
    excludedCommands: list[str]      # Commands that bypass sandbox
    allowUnsandboxedCommands: bool   # Let model request unsandboxed execution
    network: SandboxNetworkConfig
    ignoreViolations: SandboxIgnoreViolations
```

> Filesystem and network access restrictions are NOT configured via sandbox settings. They are derived from permission rules (deny rules for Read, allow/deny rules for Edit, allow/deny rules for WebFetch).

## Error Types

- **CLINotFoundError**: Claude Code CLI not found
- **CLIConnectionError**: Connection to CLI process failed
- **ProcessError**: CLI process exited with non-zero code (has exit_code attribute)
- **CLIJSONDecodeError**: Failed to parse CLI response

```python
from claude_agent_sdk import query, CLINotFoundError, ProcessError, CLIJSONDecodeError

try:
    async for message in query(prompt="Hello"):
        print(message)
except CLINotFoundError:
    print("Claude Code CLI not found")
except ProcessError as e:
    print(f"Process failed with exit code: {e.exit_code}")
except CLIJSONDecodeError as e:
    print(f"Failed to parse response: {e}")
```

## See also

- SDK overview - General SDK concepts
- TypeScript SDK reference - TypeScript SDK documentation
- CLI reference - Command-line interface

For the complete and most up-to-date API reference, see the [Anthropic documentation](https://platform.claude.com/docs/en/agent-sdk/python).
