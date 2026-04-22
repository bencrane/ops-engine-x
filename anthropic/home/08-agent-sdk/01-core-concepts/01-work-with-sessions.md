# Work with sessions

How sessions persist agent conversation history, and when to use continue, resume, and fork to return to a prior run.

A session is the conversation history the SDK accumulates while your agent works. It contains your prompt, every tool call the agent made, every tool result, and every response. The SDK writes it to disk automatically so you can return to it later.

Returning to a session means the agent has full context from before: files it already read, analysis it already performed, decisions it already made. You can ask a follow-up question, recover from an interruption, or branch off to try a different approach.

> Sessions persist the conversation, not the filesystem. To snapshot and revert file changes the agent made, use file checkpointing.

## Choose an approach

| What you're building | What to use |
|---------------------|-------------|
| One-shot task: single prompt, no follow-up | Nothing extra. One `query()` call handles it. |
| Multi-turn chat in one process | `ClaudeSDKClient` (Python) or `continue: true` (TypeScript) |
| Pick up where you left off after a process restart | `continue_conversation=True` (Python) / `continue: true` (TypeScript) |
| Resume a specific past session | Capture the session ID and pass it to resume |
| Try an alternative approach without losing the original | Fork the session |
| Stateless task, don't want anything written to disk (TypeScript only) | Set `persistSession: false` |

## Continue, resume, and fork

- **Continue** finds the most recent session in the current directory. No ID tracking needed.
- **Resume** takes a specific session ID. Required when you have multiple sessions.
- **Fork** creates a new session that starts with a copy of the original's history. The original stays unchanged.

## Automatic session management

### Python: ClaudeSDKClient

`ClaudeSDKClient` handles session IDs internally. Each call to `client.query()` automatically continues the same session.

```python
import asyncio
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions, AssistantMessage, ResultMessage, TextBlock

async def main():
    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Edit", "Glob", "Grep"],
    )
    async with ClaudeSDKClient(options=options) as client:
        await client.query("Analyze the auth module")
        async for message in client.receive_response():
            print_response(message)

        await client.query("Now refactor it to use JWT")
        async for message in client.receive_response():
            print_response(message)

asyncio.run(main())
```

### TypeScript: continue: true

Pass `continue: true` on each subsequent `query()` call and the SDK picks up the most recent session.

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

// First query: creates a new session
for await (const message of query({
    prompt: "Analyze the auth module",
    options: { allowedTools: ["Read", "Glob", "Grep"] }
})) { /* handle messages */ }

// Second query: continue: true resumes the most recent session
for await (const message of query({
    prompt: "Now refactor it to use JWT",
    options: { continue: true, allowedTools: ["Read", "Edit", "Write", "Glob", "Grep"] }
})) { /* handle messages */ }
```

## Capture the session ID

```python
async for message in query(
    prompt="Analyze the auth module and suggest improvements",
    options=ClaudeAgentOptions(allowed_tools=["Read", "Glob", "Grep"]),
):
    if isinstance(message, ResultMessage):
        session_id = message.session_id
        print(f"Session ID: {session_id}")
```

## Resume by ID

```python
async for message in query(
    prompt="Now implement the refactoring you suggested",
    options=ClaudeAgentOptions(
        resume=session_id,
        allowed_tools=["Read", "Edit", "Write", "Glob", "Grep"],
    ),
):
    if isinstance(message, ResultMessage) and message.subtype == "success":
        print(message.result)
```

## Fork to explore alternatives

Forking creates a new session that starts with a copy of the original's history but diverges from that point. The original stays unchanged.

```python
async for message in query(
    prompt="Instead of JWT, implement OAuth2 for the auth module",
    options=ClaudeAgentOptions(
        resume=session_id,
        fork_session=True,
    ),
):
    if isinstance(message, ResultMessage):
        forked_id = message.session_id
```

## Resume across hosts

Session files are local to the machine that created them. To resume on a different host:
- Move the session file and restore it to the same path on the new host
- Or capture results as application state and pass them into a fresh session's prompt
