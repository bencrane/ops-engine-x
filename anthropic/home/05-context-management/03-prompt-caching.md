# Prompt Caching

Prompt caching optimizes your API usage by allowing resuming from specific prefixes in your prompts. This significantly reduces processing time and costs for repetitive tasks or prompts with consistent elements.

Prompt caching stores KV cache representations and cryptographic hashes of cached content, but does not store the raw text of prompts or responses. This may be suitable for customers who require ZDR-type data retention commitments. See cache lifetime for details.

There are two ways to enable prompt caching:

- **Automatic caching:** Add a single `cache_control` field at the top level of your request. The system automatically applies the cache breakpoint to the last cacheable block and moves it forward as conversations grow. Best for multi-turn conversations where the growing message history should be cached automatically.
- **Explicit cache breakpoints:** Place `cache_control` directly on individual content blocks for fine-grained control over exactly what gets cached.

The simplest way to start is with automatic caching:

```shell
curl https://api.anthropic.com/v1/messages \
-H "content-type: application/json" \
-H "x-api-key: $ANTHROPIC_API_KEY" \
-H "anthropic-version: 2023-06-01" \
-d '{
"model": "claude-opus-4-6",
"max_tokens": 1024,
"cache_control": {"type": "ephemeral"},
"system": "You are an AI assistant tasked with analyzing literary works. Your goal is to provide insightful commentary on themes, characters, and writing style.",
"messages": [
{
"role": "user",
"content": "Analyze the major themes in Pride and Prejudice."
}
]
}'
```

With automatic caching, the system caches all content up to and including the last cacheable block. On subsequent requests with the same prefix, cached content is reused automatically.

## How prompt caching works

When you send a request with prompt caching enabled:

1. The system checks if a prompt prefix, up to a specified cache breakpoint, is already cached from a recent query.
2. If found, it uses the cached version, reducing processing time and costs.
3. Otherwise, it processes the full prompt and caches the prefix once the response begins.

This is especially useful for:
- Prompts with many examples
- Large amounts of context or background information
- Repetitive tasks with consistent instructions
- Long multi-turn conversations

By default, the cache has a 5-minute lifetime. The cache is refreshed for no additional cost each time the cached content is used.

> If you find that 5 minutes is too short, Anthropic also offers a 1-hour cache duration at additional cost. For more information, see 1-hour cache duration.

> **Prompt caching caches the full prefix** - Prompt caching references the entire prompt - tools, system, and messages (in that order) up to and including the block designated with `cache_control`.

## Pricing

Prompt caching introduces a new pricing structure. The table below shows the price per million tokens for each supported model:

| Model | Base Input Tokens | 5m Cache Writes | 1h Cache Writes | Cache Hits & Refreshes | Output Tokens |
|-------|------------------|-----------------|-----------------|----------------------|---------------|
| Claude Opus 4.6 | $5 / MTok | $6.25 / MTok | $10 / MTok | $0.50 / MTok | $25 / MTok |
| Claude Opus 4.5 | $5 / MTok | $6.25 / MTok | $10 / MTok | $0.50 / MTok | $25 / MTok |
| Claude Opus 4.1 | $15 / MTok | $18.75 / MTok | $30 / MTok | $1.50 / MTok | $75 / MTok |
| Claude Opus 4 | $15 / MTok | $18.75 / MTok | $30 / MTok | $1.50 / MTok | $75 / MTok |
| Claude Sonnet 4.6 | $3 / MTok | $3.75 / MTok | $6 / MTok | $0.30 / MTok | $15 / MTok |
| Claude Sonnet 4.5 | $3 / MTok | $3.75 / MTok | $6 / MTok | $0.30 / MTok | $15 / MTok |
| Claude Sonnet 4 | $3 / MTok | $3.75 / MTok | $6 / MTok | $0.30 / MTok | $15 / MTok |
| Claude Sonnet 3.7 (deprecated) | $3 / MTok | $3.75 / MTok | $6 / MTok | $0.30 / MTok | $15 / MTok |
| Claude Haiku 4.5 | $1 / MTok | $1.25 / MTok | $2 / MTok | $0.10 / MTok | $5 / MTok |
| Claude Haiku 3.5 | $0.80 / MTok | $1 / MTok | $1.6 / MTok | $0.08 / MTok | $4 / MTok |
| Claude Opus 3 (deprecated) | $15 / MTok | $18.75 / MTok | $30 / MTok | $1.50 / MTok | $75 / MTok |
| Claude Haiku 3 | $0.25 / MTok | $0.30 / MTok | $0.50 / MTok | $0.03 / MTok | $1.25 / MTok |

The table above reflects the following pricing multipliers for prompt caching:
- 5-minute cache write tokens are 1.25 times the base input tokens price
- 1-hour cache write tokens are 2 times the base input tokens price
- Cache read tokens are 0.1 times the base input tokens price

These multipliers stack with other pricing modifiers such as the Batch API discount, long context pricing, and data residency. See pricing for full details.

## Supported models

Prompt caching (both automatic and explicit) is currently supported on:
- Claude Opus 4.6
- Claude Opus 4.5
- Claude Opus 4.1
- Claude Opus 4
- Claude Sonnet 4.6
- Claude Sonnet 4.5
- Claude Sonnet 4
- Claude Sonnet 3.7 (deprecated)
- Claude Haiku 4.5
- Claude Haiku 3.5 (deprecated)
- Claude Haiku 3

## Automatic caching

Automatic caching is the simplest way to enable prompt caching. Instead of placing `cache_control` on individual content blocks, add a single `cache_control` field at the top level of your request body. The system automatically applies the cache breakpoint to the last cacheable block.

```shell
curl https://api.anthropic.com/v1/messages \
-H "content-type: application/json" \
-H "x-api-key: $ANTHROPIC_API_KEY" \
-H "anthropic-version: 2023-06-01" \
-d '{
"model": "claude-opus-4-6",
"max_tokens": 1024,
"cache_control": {"type": "ephemeral"},
"system": "You are a helpful assistant that remembers our conversation.",
"messages": [
{"role": "user", "content": "My name is Alex. I work on machine learning."},
{"role": "assistant", "content": "Nice to meet you, Alex! How can I help with your ML work today?"},
{"role": "user", "content": "What did I say I work on?"}
]
}'
```

### How automatic caching works in multi-turn conversations

With automatic caching, the cache point moves forward automatically as conversations grow. Each new request caches everything up to the last cacheable block, and previous content is read from cache.

| Request | Content | Cache behavior |
|---------|---------|---------------|
| Request 1 | System + User(1) + Asst(1) + User(2) <-- cache | Everything written to cache |
| Request 2 | System + User(1) + Asst(1) + User(2) + Asst(2) + User(3) <-- cache | System through User(2) read from cache; Asst(2) + User(3) written to cache |
| Request 3 | System + User(1) + Asst(1) + User(2) + Asst(2) + User(3) + Asst(3) + User(4) <-- cache | System through User(3) read from cache; Asst(3) + User(4) written to cache |

The cache breakpoint automatically moves to the last cacheable block in each request, so you don't need to update any `cache_control` markers as the conversation grows.

### TTL support

By default, automatic caching uses a 5-minute TTL. You can specify a 1-hour TTL at 2x the base input token price:

```json
{ "cache_control": { "type": "ephemeral", "ttl": "1h" } }
```

### Combining with block-level caching

Automatic caching is compatible with explicit cache breakpoints. When used together, the automatic cache breakpoint uses one of the 4 available breakpoint slots.

This lets you combine both approaches. For example, use explicit breakpoints to cache your system prompt and tools independently, while automatic caching handles the conversation:

```json
{
  "model": "claude-opus-4-6",
  "max_tokens": 1024,
  "cache_control": { "type": "ephemeral" },
  "system": [
    {
      "type": "text",
      "text": "You are a helpful assistant.",
      "cache_control": { "type": "ephemeral" }
    }
  ],
  "messages": [{ "role": "user", "content": "What are the key terms?" }]
}
```

### What stays the same

Automatic caching uses the same underlying caching infrastructure. Pricing, minimum token thresholds, context ordering requirements, and the 20-block lookback window all apply the same as with explicit breakpoints.

### Edge cases

- If the last block already has an explicit `cache_control` with the same TTL, automatic caching is a no-op.
- If the last block has an explicit `cache_control` with a different TTL, the API returns a 400 error.
- If 4 explicit block-level breakpoints already exist, the API returns a 400 error (no slots left for automatic caching).
- If the last block is not eligible as an automatic cache breakpoint target, the system silently walks backwards to find the nearest eligible block. If none is found, caching is skipped.

> Automatic caching is available on the Claude API and Azure AI Foundry (preview). Support for Amazon Bedrock and Google Vertex AI is coming later.

## Explicit cache breakpoints

For more control over caching, you can place `cache_control` directly on individual content blocks. This is useful when you need to cache different sections that change at different frequencies, or need fine-grained control over exactly what gets cached.

### Structuring your prompt

Place static content (tool definitions, system instructions, context, examples) at the beginning of your prompt. Mark the end of the reusable content for caching using the `cache_control` parameter.

Cache prefixes are created in the following order: tools, system, then messages. This order forms a hierarchy where each level builds upon the previous ones.

### How automatic prefix checking works

You can use just one cache breakpoint at the end of your static content, and the system will automatically find the longest prefix that a prior request already wrote to the cache. Understanding how this works helps you optimize your caching strategy.

Three core principles:

1. **Cache writes happen only at your breakpoint.** Marking a block with `cache_control` writes exactly one cache entry: a hash of the prefix ending at that block. The system does not write entries for any earlier position. Because the hash is cumulative, covering everything up to and including the breakpoint, changing any block at or before the breakpoint produces a different hash on the next request.

2. **Cache reads look backward for entries that prior requests wrote.** On each request the system computes the prefix hash at your breakpoint and checks for a matching cache entry. If none exists, it walks backward one block at a time, checking whether the prefix hash at each earlier position matches something already in the cache. It is looking for prior writes, not for stable content.

3. **The lookback window is 20 blocks.** The system checks at most 20 positions per breakpoint, counting the breakpoint itself as the first. If the system finds no matching entry in that window, checking stops (or resumes from the next explicit breakpoint, if any).

#### Example: Lookback in a growing conversation

You append new blocks each turn and set `cache_control` on the final block of each request:

- **Turn 1:** 10 blocks, breakpoint on block 10. No prior cache entries exist. The system writes an entry at block 10.
- **Turn 2:** 15 blocks, breakpoint on block 15. Block 15 has no entry, so the system walks back to block 10 and finds the turn-1 entry. Cache hit at block 10; the system processes only blocks 11 through 15 fresh and writes a new entry at block 15.
- **Turn 3:** 35 blocks, breakpoint on block 35. The system checks 20 positions (blocks 35 through 16) and finds nothing. The turn-2 entry at block 15 is one position outside the window, so there is no cache hit. Adding a second breakpoint at block 15 starts a second lookback window there, which finds the turn-2 entry.

#### Common mistake: Breakpoint on content that changes every request

Your prompt has a large static system context (blocks 1 through 5) followed by a per-request block containing a timestamp and the user message (block 6). You set `cache_control` on block 6:

- **Request 1:** Cache write at block 6. The hash includes the timestamp.
- **Request 2:** The timestamp differs, so the prefix hash at block 6 differs. The lookback walks through blocks 5, 4, 3, 2, and 1, but the system never wrote an entry at any of those positions. No cache hit. You pay for a fresh cache write on every request and never get a read.

The lookback does not find stable content behind your breakpoint and cache it. It finds entries that prior requests already wrote, and writes happen only at breakpoints. Move `cache_control` to block 5, the last block that stays the same across requests, and every subsequent request reads the cached prefix.

**Key takeaway:** Place `cache_control` on the last block whose prefix is identical across the requests you want to share a cache. In a growing conversation the final block works as long as each turn adds fewer than 20 blocks: earlier content never changes, so the next request's lookback finds the prior write. For a prompt with a varying suffix (timestamps, per-request context, the incoming message), place the breakpoint at the end of the static prefix, not on the varying block.

### When to use multiple breakpoints

You can define up to 4 cache breakpoints if you want to:
- Cache different sections that change at different frequencies (for example, tools rarely change, but context updates daily)
- Have more control over exactly what gets cached
- Ensure a cache hit when a growing conversation pushes your breakpoint 20 or more blocks past the last cache write

> **Important limitation:** The lookback can only find entries that earlier requests already wrote. If a growing conversation pushes your breakpoint 20 or more blocks past the last write, the lookback window misses it. Add a second breakpoint closer to that position from the start so a write accumulates there before you need it.

### Understanding cache breakpoint costs

Cache breakpoints themselves don't add any cost. You are only charged for:
- **Cache writes:** When new content is written to the cache (25% more than base input tokens for 5-minute TTL)
- **Cache reads:** When cached content is used (10% of base input token price)
- **Regular input tokens:** For any uncached content

Adding more `cache_control` breakpoints doesn't increase your costs - you still pay the same amount based on what content is actually cached and read. The breakpoints simply give you control over what sections can be cached independently.

## Caching strategies and considerations

### Cache limitations

The minimum cacheable prompt length is:
- 4096 tokens for Claude Opus 4.6, Claude Opus 4.5
- 2048 tokens for Claude Sonnet 4.6
- 1024 tokens for Claude Sonnet 4.5, Claude Opus 4.1, Claude Opus 4, Claude Sonnet 4, and Claude Sonnet 3.7 (deprecated)
- 4096 tokens for Claude Haiku 4.5
- 2048 tokens for Claude Haiku 3.5 (deprecated) and Claude Haiku 3

Shorter prompts cannot be cached, even if marked with `cache_control`. Any requests to cache fewer than this number of tokens will be processed without caching. To see if a prompt was cached, see the response usage fields.

For concurrent requests, note that a cache entry only becomes available after the first response begins. If you need cache hits for parallel requests, wait for the first response before sending subsequent requests.

Currently, "ephemeral" is the only supported cache type, which by default has a 5-minute lifetime.

### What can be cached

Most blocks in the request can be cached. This includes:
- **Tools:** Tool definitions in the tools array
- **System messages:** Content blocks in the system array
- **Text messages:** Content blocks in the messages.content array, for both user and assistant turns
- **Images & Documents:** Content blocks in the messages.content array, in user turns
- **Tool use and tool results:** Content blocks in the messages.content array, in both user and assistant turns

Each of these elements can be cached, either automatically or by marking them with `cache_control`.

### What cannot be cached

While most request blocks can be cached, there are some exceptions:
- Thinking blocks cannot be cached directly with `cache_control`. However, thinking blocks CAN be cached alongside other content when they appear in previous assistant turns. When cached this way, they DO count as input tokens when read from cache.
- Sub-content blocks (like citations) themselves cannot be cached directly. Instead, cache the top-level block.
- In the case of citations, the top-level document content blocks that serve as the source material for citations can be cached. This allows you to use prompt caching with citations effectively by caching the documents that citations will reference.
- Empty text blocks cannot be cached.

### What invalidates the cache

Modifications to cached content can invalidate some or all of the cache.

As described in Structuring your prompt, the cache follows the hierarchy: tools -> system -> messages. Changes at each level invalidate that level and all subsequent levels.

| What changes | Tools cache | System cache | Messages cache | Impact |
|-------------|-------------|--------------|----------------|--------|
| Tool definitions | Invalidated | Invalidated | Invalidated | Modifying tool definitions invalidates the entire cache |
| Web search toggle | Valid | Invalidated | Invalidated | Enabling/disabling web search modifies the system prompt |
| Citations toggle | Valid | Invalidated | Invalidated | Enabling/disabling citations modifies the system prompt |
| Speed setting | Valid | Invalidated | Invalidated | Switching between speed: "fast" and standard speed invalidates system and message caches |
| Tool choice | Valid | Valid | Invalidated | Changes to tool_choice parameter only affect message blocks |
| Images | Valid | Valid | Invalidated | Adding/removing images anywhere in the prompt affects message blocks |
| Thinking parameters | Valid | Valid | Invalidated | Changes to extended thinking settings affect message blocks |

### Tracking cache performance

Monitor cache performance using these API response fields, within usage in the response (or message_start event if streaming):

- `cache_creation_input_tokens`: Number of tokens written to the cache when creating a new entry.
- `cache_read_input_tokens`: Number of tokens retrieved from the cache for this request.
- `input_tokens`: Number of input tokens which were not read from or used to create a cache (that is, tokens after the last cache breakpoint).

> **Understanding the token breakdown:** The `input_tokens` field represents only the tokens that come after the last cache breakpoint in your request - not all the input tokens you sent. To calculate total input tokens: `total_input_tokens = cache_read_input_tokens + cache_creation_input_tokens + input_tokens`

### Caching with thinking blocks

When using extended thinking with prompt caching, thinking blocks have special behavior:

- **Automatic caching alongside other content:** While thinking blocks cannot be explicitly marked with `cache_control`, they get cached as part of the request content when you make subsequent API calls with tool results.
- **Input token counting:** When thinking blocks are read from cache, they count as input tokens in your usage metrics.
- **Cache invalidation patterns:**
  - Cache remains valid when only tool results are provided as user messages
  - Cache gets invalidated when non-tool-result user content is added, causing all previous thinking blocks to be stripped

### Cache storage and sharing

> Starting February 5, 2026, prompt caching will use workspace-level isolation instead of organization-level isolation.

- **Organization Isolation:** Caches are isolated between organizations. Different organizations never share caches, even if they use identical prompts.
- **Exact Matching:** Cache hits require 100% identical prompt segments, including all text and images up to and including the block marked with cache control.
- **Output Token Generation:** Prompt caching has no effect on output token generation. The response you receive will be identical to what you would get if prompt caching was not used.

## Best practices for effective caching

To optimize prompt caching performance:

1. Start with automatic caching for multi-turn conversations. It handles breakpoint management automatically.
2. Use explicit block-level breakpoints when you need to cache different sections with different change frequencies.
3. Cache stable, reusable content like system instructions, background information, large contexts, or frequent tool definitions.
4. Place cached content at the prompt's beginning for best performance.
5. Use cache breakpoints strategically to separate different cacheable prefix sections.
6. Place the breakpoint on the last block that stays identical across requests.
7. Regularly analyze cache hit rates and adjust your strategy as needed.

## Optimizing for different use cases

Tailor your prompt caching strategy to your scenario:

- **Conversational agents:** Reduce cost and latency for extended conversations, especially those with long instructions or uploaded documents.
- **Coding assistants:** Improve autocomplete and codebase Q&A by keeping relevant sections or a summarized version of the codebase in the prompt.
- **Large document processing:** Incorporate complete long-form material including images in your prompt without increasing response latency.
- **Detailed instruction sets:** Share extensive lists of instructions, procedures, and examples to fine-tune Claude's responses. Developers often include an example or two in the prompt, but with prompt caching you can get even better performance by including 20+ diverse examples of high quality answers.
- **Agentic tool use:** Enhance performance for scenarios involving multiple tool calls and iterative code changes, where each step typically requires a new API call.
- **Talk to books, papers, documentation, podcast transcripts, and other longform content:** Bring any knowledge base alive by embedding the entire document(s) into the prompt, and letting users ask it questions.

## Troubleshooting common issues

If experiencing unexpected behavior:

- Ensure cached sections are identical across calls. For explicit breakpoints, verify that `cache_control` markers are in the same locations
- Check that calls are made within the cache lifetime (5 minutes by default)
- Verify that `tool_choice` and image usage remain consistent between calls
- Validate that you are caching at least the minimum number of tokens
- Confirm your breakpoint is on a block that stays identical across requests
- Verify that the keys in your `tool_use` content blocks have stable ordering as some languages (for example, Swift, Go) randomize key order during JSON conversion, breaking caches

## 1-hour cache duration

If you find that 5 minutes is too short, Anthropic also offers a 1-hour cache duration at additional cost.

To use the extended cache, include `ttl` in the `cache_control` definition like this:

```json
"cache_control": {
  "type": "ephemeral",
  "ttl": "1h"
}
```

The response will include detailed cache information:

```json
{
  "usage": {
    "input_tokens": 2048,
    "cache_read_input_tokens": 1800,
    "cache_creation_input_tokens": 248,
    "output_tokens": 503,
    "cache_creation": {
      "ephemeral_5m_input_tokens": 456,
      "ephemeral_1h_input_tokens": 100
    }
  }
}
```

### When to use the 1-hour cache

If you have prompts that are used at a regular cadence (that is, system prompts that are used more frequently than every 5 minutes), continue to use the 5-minute cache, since this will continue to be refreshed at no additional charge.

The 1-hour cache is best used in the following scenarios:
- When you have prompts that are likely used less frequently than 5 minutes, but more frequently than every hour.
- When latency is important and your follow up prompts may be sent beyond 5 minutes.
- When you want to improve your rate limit utilization, since cache hits are not deducted against your rate limit.

### Mixing different TTLs

You can use both 1-hour and 5-minute cache controls in the same request, but with an important constraint: Cache entries with longer TTL must appear before shorter TTLs (that is, a 1-hour cache entry must appear before any 5-minute cache entries).
