# Quickstart

Get started with the Python or TypeScript Agent SDK to build AI agents that work autonomously.

Use the Agent SDK to build an AI agent that reads your code, finds bugs, and fixes them, all without manual intervention.

**What you'll do:**
- Set up a project with the Agent SDK
- Create a file with some buggy code
- Run an agent that finds and fixes the bugs automatically

## Prerequisites

- Node.js 18+ or Python 3.10+
- An Anthropic account

## Setup

### 1. Create a project folder

```bash
mkdir my-agent && cd my-agent
```

### 2. Install the SDK

**TypeScript:**
```bash
npm install @anthropic-ai/claude-agent-sdk
```

**Python (uv):**
```bash
uv add claude-agent-sdk
```

**Python (pip):**
```bash
pip install claude-agent-sdk
```

### 3. Set your API key

Get an API key from the Claude Console, then create a `.env` file in your project directory:

```
ANTHROPIC_API_KEY=your-api-key
```

The SDK also supports authentication via third-party API providers:
- **Amazon Bedrock:** set `CLAUDE_CODE_USE_BEDROCK=1` and configure AWS credentials
- **Google Vertex AI:** set `CLAUDE_CODE_USE_VERTEX=1` and configure Google Cloud credentials
- **Microsoft Azure:** set `CLAUDE_CODE_USE_FOUNDRY=1` and configure Azure credentials

## Create a buggy file

Create `utils.py` in the my-agent directory:

```python
def calculate_average(numbers):
    total = 0
    for num in numbers:
        total += num
    return total / len(numbers)

def get_user_name(user):
    return user["name"].upper()
```

This code has two bugs:
- `calculate_average([])` crashes with division by zero
- `get_user_name(None)` crashes with a TypeError

## Build an agent that finds and fixes bugs

Create `agent.py`:

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ResultMessage

async def main():
    async for message in query(
        prompt="Review utils.py for bugs that would cause crashes. Fix any issues you find.",
        options=ClaudeAgentOptions(
            allowed_tools=["Read", "Edit", "Glob"],
            permission_mode="acceptEdits",
        ),
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if hasattr(block, "text"):
                    print(block.text)
                elif hasattr(block, "name"):
                    print(f"Tool: {block.name}")
        elif isinstance(message, ResultMessage):
            print(f"Done: {message.subtype}")

asyncio.run(main())
```

This code has three main parts:
- **query:** the main entry point that creates the agentic loop
- **prompt:** what you want Claude to do
- **options:** configuration for the agent

## Run your agent

```bash
python agent.py
```

After running, check `utils.py`. You'll see defensive code handling empty lists and null users. Your agent autonomously:
1. Read utils.py to understand the code
2. Analyzed the logic and identified edge cases
3. Edited the file to add proper error handling

## Customize your agent

Add web search capability:
```python
options = ClaudeAgentOptions(
    allowed_tools=["Read", "Edit", "Glob", "WebSearch"],
    permission_mode="acceptEdits"
)
```

Give Claude a custom system prompt:
```python
options = ClaudeAgentOptions(
    allowed_tools=["Read", "Edit", "Glob"],
    permission_mode="acceptEdits",
    system_prompt="You are a senior Python developer. Always follow PEP 8 style guidelines.",
)
```

## Key concepts

**Tools control what your agent can do:**

| Tools | What the agent can do |
|-------|----------------------|
| Read, Glob, Grep | Read-only analysis |
| Read, Edit, Glob | Analyze and modify code |
| Read, Edit, Bash, Glob, Grep | Full automation |

**Permission modes control how much human oversight you want:**

| Mode | Behavior | Use case |
|------|----------|----------|
| acceptEdits | Auto-approves file edits, asks for other actions | Trusted development workflows |
| dontAsk (TypeScript only) | Denies anything not in allowedTools | Locked-down headless agents |
| bypassPermissions | Runs every tool without prompting | Sandboxed CI, fully trusted environments |
| default | Requires a canUseTool callback to handle approval | Custom approval flows |

## Next steps

- **Permissions:** control what your agent can do and when it needs approval
- **Hooks:** run custom code before or after tool calls
- **Sessions:** build multi-turn agents that maintain context
- **MCP servers:** connect to databases, browsers, APIs, and other external systems
- **Hosting:** deploy agents to Docker, cloud, and CI/CD
