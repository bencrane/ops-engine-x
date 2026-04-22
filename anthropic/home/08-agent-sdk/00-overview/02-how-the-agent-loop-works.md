# How the agent loop works

Understand the message lifecycle, tool execution, context window, and architecture that power your SDK agents.

The Agent SDK lets you embed Claude Code's autonomous agent loop in your own applications. The SDK is a standalone package that gives you programmatic control over tools, permissions, cost limits, and output. You don't need the Claude Code CLI installed to use it.

## The loop at a glance

Every agent session follows the same cycle:

1. **Receive prompt.** Claude receives your prompt, along with the system prompt, tool definitions, and conversation history. The SDK yields a SystemMessage with subtype "init" containing session metadata.
2. **Evaluate and respond.** Claude evaluates the current state and determines how to proceed. It may respond with text, request one or more tool calls, or both. The SDK yields an AssistantMessage.
3. **Execute tools.** The SDK runs each requested tool and collects the results. Each set of tool results feeds back to Claude for the next decision.
4. **Repeat.** Steps 2 and 3 repeat as a cycle. Each full cycle is one turn. Claude continues calling tools and processing results until it produces a response with no tool calls.
5. **Return result.** The SDK yields a final AssistantMessage with the text response, followed by a ResultMessage with the final text, token usage, cost, and session ID.

## Turns and messages

A turn is one round trip inside the loop: Claude produces output that includes tool calls, the SDK executes those tools, and the results feed back to Claude automatically.

You can cap the loop with `max_turns` / `maxTurns`, which counts tool-use turns only. You can also use `max_budget_usd` / `maxBudgetUsd` to cap turns based on a spend threshold.

## Message types

| Type | Description |
|------|-------------|
| SystemMessage | Session lifecycle events ("init", "compact_boundary") |
| AssistantMessage | Emitted after each Claude response, contains text and tool call blocks |
| UserMessage | Emitted after each tool execution with tool result content |
| StreamEvent | Only emitted when partial messages are enabled, contains raw API streaming events |
| ResultMessage | The last message always, contains final text, token usage, cost, and session ID |

## Tool execution

### Built-in tools

| Category | Tools | What they do |
|----------|-------|-------------|
| File operations | Read, Edit, Write | Read, modify, and create files |
| Search | Glob, Grep | Find files by pattern, search content with regex |
| Execution | Bash | Run shell commands, scripts, git operations |
| Web | WebSearch, WebFetch | Search the web, fetch and parse pages |
| Discovery | ToolSearch | Dynamically find and load tools on-demand |
| Orchestration | Agent, Skill, AskUserQuestion, TodoWrite | Spawn subagents, invoke skills, ask the user, track tasks |

### Tool permissions

Three options work together to determine what runs:
- **allowed_tools / allowedTools** auto-approves listed tools
- **disallowed_tools / disallowedTools** blocks listed tools
- **permission_mode / permissionMode** controls what happens to tools not covered by rules

### Parallel tool execution

Read-only tools can run concurrently. Tools that modify state run sequentially to avoid conflicts.

## Control how the loop runs

### Turns and budget

| Option | What it controls | Default |
|--------|-----------------|---------|
| max_turns / maxTurns | Maximum tool-use round trips | No limit |
| max_budget_usd / maxBudgetUsd | Maximum cost before stopping | No limit |

### Effort level

| Level | Behavior | Good for |
|-------|----------|----------|
| "low" | Minimal reasoning, fast responses | File lookups, listing directories |
| "medium" | Balanced reasoning | Routine edits, standard tasks |
| "high" | Thorough analysis | Refactors, debugging |
| "max" | Maximum reasoning depth | Multi-step problems requiring deep analysis |

### Permission mode

| Mode | Behavior |
|------|----------|
| "default" | Tools not covered by allow rules trigger your approval callback |
| "acceptEdits" | Auto-approves file edits, other tools follow default rules |
| "plan" | No tool execution; Claude produces a plan for review |
| "dontAsk" (TypeScript only) | Never prompts. Pre-approved tools run, everything else denied |
| "bypassPermissions" | Runs all allowed tools without asking. Use only in isolated environments |

## The context window

Everything accumulates: system prompt, tool definitions, conversation history, tool inputs, and tool outputs. Content that stays the same across turns is automatically prompt cached.

### Automatic compaction

When the context window approaches its limit, the SDK automatically compacts the conversation: it summarizes older history to free space. The SDK emits a SystemMessage with subtype "compact_boundary" when this happens.

You can customize compaction behavior with:
- Summarization instructions in CLAUDE.md
- PreCompact hook
- Manual compaction via `/compact` prompt string

### Keep context efficient

- Use subagents for subtasks (each starts with a fresh conversation)
- Be selective with tools
- Watch MCP server costs
- Use lower effort for routine tasks

## Sessions and continuity

Each interaction creates or continues a session. Capture the session ID from `ResultMessage.session_id` to resume later. When you resume, the full context from previous turns is restored.

## Handle the result

| Result subtype | What happened | result field available? |
|---------------|---------------|----------------------|
| success | Claude finished the task normally | Yes |
| error_max_turns | Hit the maxTurns limit | No |
| error_max_budget_usd | Hit the maxBudgetUsd limit | No |
| error_during_execution | An error interrupted the loop | No |
| error_max_structured_output_retries | Structured output validation failed | No |

## Hooks

| Hook | When it fires | Common uses |
|------|--------------|-------------|
| PreToolUse | Before a tool executes | Validate inputs, block dangerous commands |
| PostToolUse | After a tool returns | Audit outputs, trigger side effects |
| UserPromptSubmit | When a prompt is sent | Inject additional context |
| Stop | When the agent finishes | Validate the result, save session state |
| SubagentStart / SubagentStop | When a subagent spawns or completes | Track parallel task results |
| PreCompact | Before context compaction | Archive full transcript |
