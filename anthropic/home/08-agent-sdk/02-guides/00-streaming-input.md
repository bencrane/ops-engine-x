# Streaming Input

Understanding the two input modes for Claude Agent SDK and when to use each.

## Overview

The Claude Agent SDK supports two distinct input modes for interacting with agents:

- **Streaming Input Mode (Default & Recommended)** - A persistent, interactive session
- **Single Message Input** - One-shot queries that use session state and resuming

## Streaming Input Mode (Recommended)

Streaming input mode is the preferred way to use the Claude Agent SDK. It provides full access to the agent's capabilities and enables rich, interactive experiences.

It allows the agent to operate as a long lived process that takes in user input, handles interruptions, surfaces permission requests, and handles session management.

### Benefits

- **Image Uploads:** Attach images directly to messages for visual analysis
- **Queued Messages:** Send multiple messages that process sequentially, with ability to interrupt
- **Tool Integration:** Full access to all tools and custom MCP servers during the session
- **Hooks Support:** Use lifecycle hooks to customize behavior at various points
- **Real-time Feedback:** See responses as they're generated, not just final results
- **Context Persistence:** Maintain conversation context across multiple turns naturally

### Implementation Example

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";
import { readFile } from "fs/promises";

async function* generateMessages() {
    yield {
        type: "user" as const,
        message: {
            role: "user" as const,
            content: "Analyze this codebase for security issues"
        }
    };

    await new Promise((resolve) => setTimeout(resolve, 2000));

    yield {
        type: "user" as const,
        message: {
            role: "user" as const,
            content: [
                { type: "text", text: "Review this architecture diagram" },
                {
                    type: "image",
                    source: {
                        type: "base64",
                        media_type: "image/png",
                        data: await readFile("diagram.png", "base64")
                    }
                }
            ]
        }
    };
}

for await (const message of query({
    prompt: generateMessages(),
    options: { maxTurns: 10, allowedTools: ["Read", "Grep"] }
})) {
    if (message.type === "result") {
        console.log(message.result);
    }
}
```

## Single Message Input

### When to Use Single Message Input

Use single message input when:
- You need a one-shot response
- You do not need image attachments, hooks, etc.
- You need to operate in a stateless environment, such as a lambda function

### Limitations

Single message input mode does not support:
- Direct image attachments in messages
- Dynamic message queueing
- Real-time interruption
- Hook integration
- Natural multi-turn conversations

### Implementation Example

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({
    prompt: "Explain the authentication flow",
    options: { maxTurns: 1, allowedTools: ["Read", "Grep"] }
})) {
    if (message.type === "result") {
        console.log(message.result);
    }
}

// Continue conversation with session management
for await (const message of query({
    prompt: "Now explain the authorization process",
    options: { continue: true, maxTurns: 1 }
})) {
    if (message.type === "result") {
        console.log(message.result);
    }
}
```
