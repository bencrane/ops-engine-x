# Agent SDK overview

Build production AI agents with Claude Code as a library.

> The Claude Code SDK has been renamed to the Claude Agent SDK. If you're migrating from the old SDK, see the Migration Guide.

Build AI agents that autonomously read files, run commands, search the web, edit code, and more. The Agent SDK gives you the same tools, agent loop, and context management that power Claude Code, programmable in Python and TypeScript.

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions

async def main():
    async for message in query(
        prompt="Find and fix the bug in auth.py",
        options=ClaudeAgentOptions(allowed_tools=["Read", "Edit", "Bash"]),
    ):
        print(message)  # Claude reads the file, finds the bug, edits it

asyncio.run(main())
```

The Agent SDK includes built-in tools for reading files, running commands, and editing code, so your agent can start working immediately without you implementing tool execution.

## Get started

### 1. Install the SDK

**TypeScript:**
```
npm install @anthropic-ai/claude-agent-sdk
```

**Python:**
```
pip install claude-agent-sdk
```

### 2. Set your API key

Get an API key from the Console, then set it as an environment variable:

```
export ANTHROPIC_API_KEY=your-api-key
```

The SDK also supports authentication via third-party API providers:
- **Amazon Bedrock:** set `CLAUDE_CODE_USE_BEDROCK=1` environment variable and configure AWS credentials
- **Google Vertex AI:** set `CLAUDE_CODE_USE_VERTEX=1` environment variable and configure Google Cloud credentials
- **Microsoft Azure:** set `CLAUDE_CODE_USE_FOUNDRY=1` environment variable and configure Azure credentials

> Unless previously approved, Anthropic does not allow third party developers to offer claude.ai login or rate limits for their products, including agents built on the Claude Agent SDK. Please use the API key authentication methods described in this document instead.

### 3. Run your first agent

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions

async def main():
    async for message in query(
        prompt="What files are in this directory?",
        options=ClaudeAgentOptions(allowed_tools=["Bash", "Glob"]),
    ):
        if hasattr(message, "result"):
            print(message.result)

asyncio.run(main())
```

## Capabilities

Everything that makes Claude Code powerful is available in the SDK:

### Built-in tools

| Tool | What it does |
|------|-------------|
| Read | Read any file in the working directory |
| Write | Create new files |
| Edit | Make precise edits to existing files |
| Bash | Run terminal commands, scripts, git operations |
| Glob | Find files by pattern (**/*.ts, src/**/*.py) |
| Grep | Search file contents with regex |
| WebSearch | Search the web for current information |
| WebFetch | Fetch and parse web page content |
| AskUserQuestion | Ask the user clarifying questions with multiple choice options |

## Claude Code features

The SDK also supports Claude Code's filesystem-based configuration. To use these features, set `setting_sources=["project"]` (Python) or `settingSources: ['project']` (TypeScript) in your options.

| Feature | Description | Location |
|---------|-------------|----------|
| Skills | Specialized capabilities defined in Markdown | .claude/skills/SKILL.md |
| Slash commands | Custom commands for common tasks | .claude/commands/*.md |
| Memory | Project context and instructions | CLAUDE.md or .claude/CLAUDE.md |
| Plugins | Extend with custom commands, agents, and MCP servers | Programmatic via plugins option |

## Compare the Agent SDK to other Claude tools

The Anthropic Client SDK gives you direct API access: you send prompts and implement tool execution yourself. The Agent SDK gives you Claude with built-in tool execution.

```python
# Client SDK: You implement the tool loop
response = client.messages.create(...)
while response.stop_reason == "tool_use":
    result = your_tool_executor(response.tool_use)
    response = client.messages.create(tool_result=result, **params)

# Agent SDK: Claude handles tools autonomously
async for message in query(prompt="Fix the bug in auth.py"):
    print(message)
```

## Changelog

View the full changelog for SDK updates, bug fixes, and new features:
- TypeScript SDK: view CHANGELOG.md
- Python SDK: view CHANGELOG.md

## Reporting bugs

If you encounter bugs or issues with the Agent SDK:
- TypeScript SDK: report issues on GitHub
- Python SDK: report issues on GitHub

## Branding guidelines

For partners integrating the Claude Agent SDK, use of Claude branding is optional. When referencing Claude in your product:

**Allowed:**
- "Claude Agent" (preferred for dropdown menus)
- "Claude" (when within a menu already labeled "Agents")
- "{YourAgentName} Powered by Claude" (if you have an existing agent name)

**Not permitted:**
- "Claude Code" or "Claude Code Agent"
- Claude Code-branded ASCII art or visual elements that mimic Claude Code

## License and terms

Use of the Claude Agent SDK is governed by Anthropic's Commercial Terms of Service, including when you use it to power products and services that you make available to your own customers and end users, except to the extent a specific component or dependency is covered by a different license as indicated in that component's LICENSE file.
