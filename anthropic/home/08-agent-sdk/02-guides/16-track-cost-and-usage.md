# Track cost and usage

Learn how to track token usage, deduplicate parallel tool calls, and calculate costs with the Claude Agent SDK.

The Claude Agent SDK provides detailed token usage information for each interaction with Claude. This guide explains how to properly track costs and understand usage reporting, especially when dealing with parallel tool uses and multi-step conversations.

## Understand token usage

The TypeScript and Python SDKs expose usage data at different levels of detail:

- **TypeScript** provides per-step token breakdowns on each assistant message, per-model cost via modelUsage, and a cumulative total on the result message.
- **Python** provides the accumulated total on the result message (total_cost_usd and usage dict). Per-step breakdowns are not available on individual assistant messages.

Cost tracking depends on understanding how the SDK scopes usage data:

- **query() call**: one invocation of the SDK's query() function. A single call can involve multiple steps. Each call produces one result message at the end.
- **Step**: a single request/response cycle within a query() call. In TypeScript, each step produces assistant messages with token usage.
- **Session**: a series of query() calls linked by a session ID (using the resume option). Each query() call within a session reports its own cost independently.

## Get the total cost of a query

The result message is the last message in every query() call. It includes total_cost_usd, the cumulative cost across all steps in that call.

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({ prompt: "Summarize this project" })) {
  if (message.type === "result") {
    console.log(`Total cost: $${message.total_cost_usd}`);
  }
}
```

## Track detailed usage in TypeScript

The TypeScript SDK exposes additional usage granularity that is not available in Python.

### Track per-step usage

Each assistant message contains a nested BetaMessage with an id and usage object with token counts. When Claude uses tools in parallel, multiple messages share the same id with identical usage data. Deduplicate by ID to avoid inflated totals.

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

const seenIds = new Set<string>();
let totalInputTokens = 0;
let totalOutputTokens = 0;

for await (const message of query({ prompt: "Summarize this project" })) {
  if (message.type === "assistant") {
    const msgId = message.message.id;
    if (!seenIds.has(msgId)) {
      seenIds.add(msgId);
      totalInputTokens += message.message.usage.input_tokens;
      totalOutputTokens += message.message.usage.output_tokens;
    }
  }
}

console.log(`Steps: ${seenIds.size}`);
console.log(`Input tokens: ${totalInputTokens}`);
console.log(`Output tokens: ${totalOutputTokens}`);
```

### Break down usage per model

The result message includes modelUsage, a map of model name to per-model token counts and cost. Useful when you run multiple models (e.g., Haiku for subagents and Opus for the main agent).

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({ prompt: "Summarize this project" })) {
  if (message.type !== "result") continue;

  for (const [modelName, usage] of Object.entries(message.modelUsage)) {
    console.log(`${modelName}: $${usage.costUSD.toFixed(4)}`);
    console.log(`  Input tokens: ${usage.inputTokens}`);
    console.log(`  Output tokens: ${usage.outputTokens}`);
    console.log(`  Cache read: ${usage.cacheReadInputTokens}`);
    console.log(`  Cache creation: ${usage.cacheCreationInputTokens}`);
  }
}
```

## Accumulate costs across multiple calls

Each query() call returns its own total_cost_usd. The SDK does not provide a session-level total, so accumulate the totals yourself:

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

let totalSpend = 0;

const prompts = [
  "Read the files in src/ and summarize the architecture",
  "List all exported functions in src/auth.ts"
];

for (const prompt of prompts) {
  for await (const message of query({ prompt })) {
    if (message.type === "result") {
      totalSpend += message.total_cost_usd ?? 0;
      console.log(`This call: $${message.total_cost_usd}`);
    }
  }
}

console.log(`Total spend: $${totalSpend.toFixed(4)}`);
```

## Handle errors, caching, and token discrepancies

### Resolve output token discrepancies

In rare cases, you might observe different output_tokens values for messages with the same ID. When this occurs:

- **Use the highest value**: the final message in a group typically contains the accurate total
- **Verify against total cost**: the total_cost_usd in the result message is authoritative
- **Report inconsistencies**: file issues at the Claude Code GitHub repository

### Track costs on failed conversations

Both success and error result messages include usage and total_cost_usd. If a conversation fails mid-way, you still consumed tokens up to the point of failure. Always read cost data from the result message regardless of its subtype.

### Track cache tokens

The Agent SDK automatically uses prompt caching to reduce costs on repeated content. The usage object includes two additional fields:

- **cache_creation_input_tokens**: tokens used to create new cache entries (charged at a higher rate)
- **cache_read_input_tokens**: tokens read from existing cache entries (charged at a reduced rate)

Track these separately from input_tokens to understand caching savings.

## Related documentation

- TypeScript SDK Reference - Complete API documentation
- Python SDK Reference - Complete API documentation
- SDK Overview - Getting started with the SDK
