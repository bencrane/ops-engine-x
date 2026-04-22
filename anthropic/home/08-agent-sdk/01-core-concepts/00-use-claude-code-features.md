# Use Claude Code features in the SDK

Load project instructions, skills, hooks, and other Claude Code features into your SDK agents.

The Agent SDK is built on the same foundation as Claude Code, which means your SDK agents have access to the same filesystem-based features: project instructions (CLAUDE.md and rules), skills, hooks, and more.

By default, the SDK loads no filesystem settings. Your agent runs in isolation mode with only what you pass programmatically. To load CLAUDE.md, skills, or filesystem hooks, set `settingSources` to tell the SDK where to look.

## Enable Claude Code features with settingSources

The setting sources option (`setting_sources` in Python, `settingSources` in TypeScript) controls which filesystem-based settings the SDK loads.

```python
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ResultMessage

async for message in query(
    prompt="Help me refactor the auth module",
    options=ClaudeAgentOptions(
        setting_sources=["user", "project"],
        allowed_tools=["Read", "Edit", "Bash"],
    ),
):
    if isinstance(message, AssistantMessage):
        for block in message.content:
            if hasattr(block, "text"):
                print(block.text)
    if isinstance(message, ResultMessage) and message.subtype == "success":
        print(f"\nResult: {message.result}")
```

| Source | What it loads | Location |
|--------|-------------|----------|
| "project" | Project CLAUDE.md, .claude/rules/*.md, project skills, project hooks, project settings.json | `<cwd>/.claude/` and parent directories |
| "user" | User CLAUDE.md, ~/.claude/rules/*.md, user skills, user settings | `~/.claude/` |
| "local" | CLAUDE.local.md (gitignored), .claude/settings.local.json | `<cwd>/` |

To match the full Claude Code CLI behavior, use `["user", "project", "local"]`.

## Project instructions (CLAUDE.md and rules)

CLAUDE.md files and `.claude/rules/*.md` files give your agent persistent context about your project. When `settingSources` includes "project", the SDK loads these files into context at session start.

### CLAUDE.md load locations

| Level | Location | When loaded |
|-------|----------|-------------|
| Project (root) | `<cwd>/CLAUDE.md` or `<cwd>/.claude/CLAUDE.md` | settingSources includes "project" |
| Project rules | `<cwd>/.claude/rules/*.md` | settingSources includes "project" |
| Project (parent dirs) | CLAUDE.md files in directories above cwd | settingSources includes "project" |
| Project (child dirs) | CLAUDE.md files in subdirectories of cwd | settingSources includes "project", loaded on demand |
| Local (gitignored) | `<cwd>/CLAUDE.local.md` | settingSources includes "local" |
| User | `~/.claude/CLAUDE.md` | settingSources includes "user" |
| User rules | `~/.claude/rules/*.md` | settingSources includes "user" |

## Skills

Skills are markdown files that give your agent specialized knowledge and invocable workflows. Unlike CLAUDE.md (which loads every session), skills load on demand.

```python
async for message in query(
    prompt="Review this PR using our code review checklist",
    options=ClaudeAgentOptions(
        setting_sources=["user", "project"],
        allowed_tools=["Skill", "Read", "Grep", "Glob"],
    ),
):
    if isinstance(message, ResultMessage) and message.subtype == "success":
        print(message.result)
```

Skills must be created as filesystem artifacts (`.claude/skills/<name>/SKILL.md`).

## Hooks

The SDK supports two ways to define hooks:

- **Filesystem hooks:** shell commands defined in settings.json, loaded when settingSources includes the relevant source
- **Programmatic hooks:** callback functions passed directly to `query()`

Both types execute during the same hook lifecycle.

```python
async def audit_bash(input_data, tool_use_id, context):
    command = input_data.get("tool_input", {}).get("command", "")
    if "rm -rf" in command:
        return {"decision": "block", "reason": "Destructive command blocked"}
    return {}

async for message in query(
    prompt="Refactor the auth module",
    options=ClaudeAgentOptions(
        setting_sources=["project"],
        hooks={
            "PreToolUse": [
                HookMatcher(matcher="Bash", hooks=[audit_bash]),
            ]
        },
    ),
):
    if isinstance(message, ResultMessage) and message.subtype == "success":
        print(message.result)
```

### When to use which hook type

| Hook type | Best for |
|-----------|----------|
| Filesystem (settings.json) | Sharing hooks between CLI and SDK sessions |
| Programmatic (callbacks) | Application-specific logic; returning structured decisions |

## Choose the right feature

| You want to... | Use | SDK surface |
|----------------|-----|-------------|
| Set project conventions | CLAUDE.md | settingSources: ["project"] |
| Give reference material loaded when relevant | Skills | settingSources + allowedTools: ["Skill"] |
| Run reusable workflows | User-invocable skills | settingSources + allowedTools: ["Skill"] |
| Delegate isolated subtasks | Subagents | agents parameter + allowedTools: ["Agent"] |
| Run deterministic logic on tool calls | Hooks | hooks parameter with callbacks |
| Give Claude structured tool access to external services | MCP | mcpServers parameter |
