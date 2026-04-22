# TypeScript SDK V2 interface (preview)

Preview of the simplified V2 TypeScript Agent SDK, with session-based send/stream patterns for multi-turn conversations.

> The V2 interface is an unstable preview. APIs may change based on feedback before becoming stable. Some features like session forking are only available in the V1 SDK.

The V2 Claude Agent TypeScript SDK removes the need for async generators and yield coordination. This makes multi-turn conversations simpler. The API surface reduces to three concepts:

- **createSession() / resumeSession()**: Start or continue a conversation
- **session.send()**: Send a message
- **session.stream()**: Get the response

## Installation

The V2 interface is included in the existing SDK package:

```bash
npm install @anthropic-ai/claude-agent-sdk
```

## Quick start

### One-shot prompt

For simple single-turn queries, use `unstable_v2_prompt()`:

```typescript
import { unstable_v2_prompt } from "@anthropic-ai/claude-agent-sdk";

const result = await unstable_v2_prompt("What is 2 + 2?", {
  model: "claude-opus-4-6"
});

if (result.subtype === "success") {
  console.log(result.result);
}
```

### Basic session

For interactions beyond a single prompt, create a session. V2 separates sending and streaming into distinct steps:

```typescript
import { unstable_v2_createSession } from "@anthropic-ai/claude-agent-sdk";

await using session = unstable_v2_createSession({
  model: "claude-opus-4-6"
});

await session.send("Hello!");
for await (const msg of session.stream()) {
  if (msg.type === "assistant") {
    const text = msg.message.content
      .filter((block) => block.type === "text")
      .map((block) => block.text)
      .join("");
    console.log(text);
  }
}
```

### Multi-turn conversation

Sessions persist context across multiple exchanges. Call send() again on the same session:

```typescript
import { unstable_v2_createSession } from "@anthropic-ai/claude-agent-sdk";

await using session = unstable_v2_createSession({
  model: "claude-opus-4-6"
});

// Turn 1
await session.send("What is 5 + 3?");
for await (const msg of session.stream()) {
  if (msg.type === "assistant") {
    const text = msg.message.content
      .filter((block) => block.type === "text")
      .map((block) => block.text)
      .join("");
    console.log(text);
  }
}

// Turn 2
await session.send("Multiply that by 2");
for await (const msg of session.stream()) {
  if (msg.type === "assistant") {
    const text = msg.message.content
      .filter((block) => block.type === "text")
      .map((block) => block.text)
      .join("");
    console.log(text);
  }
}
```

### Session resume

Resume a session from a previous interaction using its ID:

```typescript
import {
  unstable_v2_createSession,
  unstable_v2_resumeSession,
  type SDKMessage
} from "@anthropic-ai/claude-agent-sdk";

function getAssistantText(msg: SDKMessage): string | null {
  if (msg.type !== "assistant") return null;
  return msg.message.content
    .filter((block) => block.type === "text")
    .map((block) => block.text)
    .join("");
}

// Create initial session
const session = unstable_v2_createSession({ model: "claude-opus-4-6" });

await session.send("Remember this number: 42");
let sessionId: string | undefined;
for await (const msg of session.stream()) {
  sessionId = msg.session_id;
  const text = getAssistantText(msg);
  if (text) console.log("Initial response:", text);
}
session.close();

// Later: resume the session
await using resumedSession = unstable_v2_resumeSession(sessionId!, {
  model: "claude-opus-4-6"
});

await resumedSession.send("What number did I ask you to remember?");
for await (const msg of resumedSession.stream()) {
  const text = getAssistantText(msg);
  if (text) console.log("Resumed response:", text);
}
```

### Cleanup

Sessions can be closed manually or automatically using `await using` (TypeScript 5.2+):

**Automatic cleanup (TypeScript 5.2+):**

```typescript
await using session = unstable_v2_createSession({ model: "claude-opus-4-6" });
// Session closes automatically when the block exits
```

**Manual cleanup:**

```typescript
const session = unstable_v2_createSession({ model: "claude-opus-4-6" });
// ... use the session ...
session.close();
```

## API reference

### unstable_v2_createSession()

Creates a new session for multi-turn conversations.

```typescript
function unstable_v2_createSession(options: {
  model: string;
  // Additional options supported
}): SDKSession;
```

### unstable_v2_resumeSession()

Resumes an existing session by ID.

```typescript
function unstable_v2_resumeSession(
  sessionId: string,
  options: {
    model: string;
    // Additional options supported
  }
): SDKSession;
```

### unstable_v2_prompt()

One-shot convenience function for single-turn queries.

```typescript
function unstable_v2_prompt(
  prompt: string,
  options: {
    model: string;
    // Additional options supported
  }
): Promise<SDKResultMessage>;
```

### SDKSession interface

```typescript
interface SDKSession {
  readonly sessionId: string;
  send(message: string | SDKUserMessage): Promise<void>;
  stream(): AsyncGenerator<SDKMessage, void>;
  close(): void;
}
```

## Feature availability

Not all V1 features are available in V2 yet. The following require using the V1 SDK:

- Session forking (forkSession option)
- Some advanced streaming input patterns

## See also

- TypeScript SDK reference (V1) - Full V1 SDK documentation
- SDK overview - General SDK concepts
- V2 examples on GitHub - Working code examples
