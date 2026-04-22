# Anthropic API — Canonical Reference

> **Purpose:** The definitive Anthropic API reference for all Claude integrations — real-time voice agents, asset generation, chat interfaces, and tool-augmented workflows. Every parameter, response shape, and constraint is documented with exact values and working code examples.
>
> **Base URL:** `https://api.anthropic.com`
> **Required Header:** `anthropic-version: 2023-06-01`
> **Auth Header:** `x-api-key: $ANTHROPIC_API_KEY`

---

## 1. Models Inventory

### Latest Models

| Model | API ID | Alias | Context Window | Max Output | Input $/MTok | Output $/MTok | Speed | Best For |
|-------|--------|-------|---------------|------------|-------------|--------------|-------|----------|
| **Claude Opus 4.6** | `claude-opus-4-6` | `claude-opus-4-6` | 1M tokens | 128k tokens | $5 | $25 | Moderate | Deep reasoning, complex agents, advanced coding, multi-hour research, step-change vision |
| **Claude Sonnet 4.6** | `claude-sonnet-4-6` | `claude-sonnet-4-6` | 1M tokens | 64k tokens | $3 | $15 | Fast | Code generation, data analysis, content creation, agentic tool use |
| **Claude Haiku 4.5** | `claude-haiku-4-5-20251001` | `claude-haiku-4-5` | 200k tokens | 64k tokens | $1 | $5 | Fastest | Real-time applications, high-volume processing, cost-sensitive, sub-agent tasks |

### Additional Active Models

| Model | API ID | Context Window | Max Output | Input $/MTok | Output $/MTok |
|-------|--------|---------------|------------|-------------|--------------|
| Claude Opus 4.5 | `claude-opus-4-5-20250520` | 1M tokens | 128k tokens | $5 | $25 |
| Claude Opus 4.1 | `claude-opus-4-1-20250415` | 200k tokens | 128k tokens | $15 | $75 |
| Claude Opus 4 | `claude-opus-4-20250514` | 200k tokens | 128k tokens | $15 | $75 |
| Claude Sonnet 4.5 | `claude-sonnet-4-5-20250514` | 1M tokens (beta w/ header) | 64k tokens | $3 | $15 |
| Claude Sonnet 4 | `claude-sonnet-4-20250514` | 1M tokens (beta w/ header) | 64k tokens | $3 | $15 |
| Claude Haiku 3.5 | `claude-3-5-haiku-20241022` | 200k tokens | 64k tokens | $0.80 | $4 |
| Claude Haiku 3 | `claude-3-haiku-20240307` | 200k tokens | 4k tokens | $0.25 | $1.25 |

### Third-Party Platform IDs

| Model | AWS Bedrock | GCP Vertex AI |
|-------|------------|---------------|
| Opus 4.6 | `anthropic.claude-opus-4-6-v1` | `claude-opus-4-6` |
| Sonnet 4.6 | `anthropic.claude-sonnet-4-6` | `claude-sonnet-4-6` |
| Haiku 4.5 | `anthropic.claude-haiku-4-5-20251001-v1:0` | `claude-haiku-4-5@20251001` |

### Model-Specific Behaviors & Limitations

- **Opus 4.6 does NOT support prefilling assistant messages.** Sending a prefilled last assistant message returns `400 invalid_request_error`. Use structured outputs, system prompt instructions, or `output_config.format` instead.
- **Extended thinking:** Supported on Opus 4.6, Sonnet 4.6, and Haiku 4.5.
- **Adaptive thinking:** Supported on Opus 4.6 and Sonnet 4.6 only (not Haiku 4.5).
- **Fast mode (beta):** Only available on Opus 4.6. Provides ~2.5x faster output at 6x pricing ($30/MTok input, $150/MTok output).
- **Knowledge cutoffs:** Opus 4.6 reliable through May 2025 (training data to Aug 2025). Sonnet 4.6 reliable through Aug 2025 (training data to Jan 2026). Haiku 4.5 reliable through Feb 2025 (training data to Jul 2025).

### Query Model Capabilities Programmatically

```bash
# List all models
curl https://api.anthropic.com/v1/models \
  -H 'anthropic-version: 2023-06-01' \
  -H "x-api-key: $ANTHROPIC_API_KEY"

# Get a specific model
curl https://api.anthropic.com/v1/models/claude-opus-4-6 \
  -H 'anthropic-version: 2023-06-01' \
  -H "x-api-key: $ANTHROPIC_API_KEY"
```

Response includes `max_input_tokens`, `max_tokens`, and a `capabilities` object with boolean support flags for: `batch`, `citations`, `code_execution`, `context_management`, `effort`, `image_input`, `pdf_input`, `structured_outputs`, `thinking`.

---

## 2. Messages API — Complete Specification

### Endpoint

```
POST /v1/messages
```

### Required Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `model` | `string` | Model ID (e.g., `"claude-opus-4-6"`, `"claude-sonnet-4-6"`) |
| `max_tokens` | `number` | Maximum output tokens. Min: 1. Max varies by model (Opus 4.6: 128000, Sonnet 4.6: 64000, Haiku 4.5: 64000) |
| `messages` | `array of MessageParam` | Input messages. Alternating `user`/`assistant` turns. Limit: 100,000 messages per request. |

### Optional Parameters

| Parameter | Type | Default | Valid Range / Values | Description |
|-----------|------|---------|---------------------|-------------|
| `system` | `string` or `array` | none | — | System prompt. Top-level field, NOT in messages array. |
| `temperature` | `number` | `1.0` | `0.0` to `1.0` | Randomness. Lower = more deterministic. |
| `top_p` | `number` | none | `0.0` to `1.0` | Nucleus sampling. Don't combine with `temperature`. |
| `top_k` | `number` | none | positive integer | Sample from top K tokens only. |
| `stop_sequences` | `array of string` | none | — | Custom stop strings. |
| `stream` | `boolean` | `false` | `true`/`false` | Enable SSE streaming. |
| `tools` | `array` | none | — | Tool definitions (see Section 4). |
| `tool_choice` | `object` | `{"type": "auto"}` | `auto`, `any`, `tool`, `none` | How to use tools. |
| `thinking` | `object` | none | `{"type": "enabled", "budget_tokens": N}` or `{"type": "adaptive"}` | Extended thinking config. |
| `reasoning_effort` | `string` | none | `"low"`, `"medium"`, `"high"`, `"max"` | Effort level for reasoning. |
| `metadata` | `object` | none | `{"user_id": "..."}` | Request metadata. |
| `service_tier` | `string` | none | `"auto"`, `"standard_only"` | Service tier selection. |
| `inference_geo` | `string` | `"global"` | `"us"`, `"global"` | Data residency. US-only adds 1.1x pricing multiplier on Opus 4.6+. |
| `output_config` | `object` | none | JSON schema or text format | Structured output config. |
| `mcp_servers` | `array` | none | — | MCP servers for tool use (beta). |

### Messages Format

Each message: `{"role": "user"|"assistant", "content": string|array}`

Content can be a plain string (shorthand for single text block) or an array of content blocks:

```json
[
    {"role": "user", "content": "Hello, Claude"},
    {"role": "assistant", "content": "Hi! How can I help?"},
    {"role": "user", "content": "Explain LLMs."}
]
```

### Input Content Block Types

| Type | Fields | Use |
|------|--------|-----|
| `text` | `type`, `text`, optional `cache_control`, `citations` | Plain text |
| `image` | `type`, `source` (base64/url/file) | Image input |
| `document` | `type`, `source` (base64/url/file), optional `title`, `context`, `citations` | PDF/text documents |
| `tool_use` | `type`, `id`, `name`, `input` | Tool call (in assistant messages) |
| `tool_result` | `type`, `tool_use_id`, `content`, optional `is_error` | Tool result (in user messages) |
| `thinking` | `type`, `thinking`, `signature` | Thinking block passthrough |
| `redacted_thinking` | `type`, `data` | Redacted thinking passthrough |

### Full Request Example (All Fields)

```bash
curl https://api.anthropic.com/v1/messages \
    --header "x-api-key: $ANTHROPIC_API_KEY" \
    --header "anthropic-version: 2023-06-01" \
    --header "content-type: application/json" \
    --data '{
        "model": "claude-opus-4-6",
        "max_tokens": 4096,
        "system": "You are a helpful assistant specializing in weather data.",
        "temperature": 0.7,
        "top_p": 0.9,
        "stop_sequences": ["END"],
        "stream": false,
        "metadata": {"user_id": "user-123"},
        "messages": [
            {"role": "user", "content": "Hello, Claude"}
        ]
    }'
```

### Response Shape (Non-Streaming)

```json
{
    "id": "msg_01XFDUDYJgAACzvnptvVoYEL",
    "type": "message",
    "role": "assistant",
    "content": [
        {
            "type": "text",
            "text": "Hello! How can I assist you today?"
        }
    ],
    "model": "claude-opus-4-6",
    "stop_reason": "end_turn",
    "stop_sequence": null,
    "usage": {
        "input_tokens": 12,
        "output_tokens": 8,
        "cache_creation_input_tokens": 0,
        "cache_read_input_tokens": 0,
        "service_tier": "standard"
    }
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | `string` | Unique message ID (e.g., `"msg_01XFDUDYJgAACzvnptvVoYEL"`) |
| `type` | `string` | Always `"message"` |
| `role` | `string` | Always `"assistant"` |
| `content` | `array` | Array of content blocks: `text`, `tool_use`, `thinking`, `redacted_thinking`, `server_tool_use`, `web_search_tool_result`, `code_execution_tool_result`, `mcp_tool_use` |
| `model` | `string` | Model that handled the request |
| `stop_reason` | `string` | `"end_turn"` / `"max_tokens"` / `"stop_sequence"` / `"tool_use"` / `"refusal"` / `"pause_turn"` |
| `stop_sequence` | `string or null` | Which custom stop sequence was hit |
| `usage` | `object` | Token counts (see below) |

### Usage Object

| Field | Type | Description |
|-------|------|-------------|
| `input_tokens` | `number` | Tokens after last cache breakpoint |
| `output_tokens` | `number` | Output tokens generated |
| `cache_creation_input_tokens` | `number` | Tokens written to cache |
| `cache_read_input_tokens` | `number` | Tokens read from cache |
| `service_tier` | `string` | Service tier used |

**Total input tokens formula:** `total = cache_read_input_tokens + cache_creation_input_tokens + input_tokens`

---

## 3. Multi-Turn Conversation Format

### Role Alternation Rules

1. Messages must alternate between `user` and `assistant` roles.
2. The first message must be `user`.
3. Each `user` message can contain text, images, documents, and `tool_result` blocks.
4. Each `assistant` message can contain text, `tool_use`, and `thinking` blocks.

### Tool Use Conversation Flow

When the assistant responds with `tool_use`, the next `user` message MUST contain `tool_result` blocks:

```json
[
    {"role": "user", "content": "What's the weather in SF and NYC?"},
    {"role": "assistant", "content": [
        {"type": "text", "text": "I'll check both cities for you."},
        {"type": "tool_use", "id": "toolu_01A", "name": "get_weather", "input": {"location": "San Francisco, CA"}},
        {"type": "tool_use", "id": "toolu_01B", "name": "get_weather", "input": {"location": "New York, NY"}}
    ]},
    {"role": "user", "content": [
        {"type": "tool_result", "tool_use_id": "toolu_01A", "content": "72°F, sunny"},
        {"type": "tool_result", "tool_use_id": "toolu_01B", "content": "58°F, cloudy"}
    ]},
    {"role": "assistant", "content": [
        {"type": "text", "text": "San Francisco is 72°F and sunny. New York is 58°F and cloudy."}
    ]}
]
```

**Critical formatting rules:**
- `tool_result` blocks must immediately follow their corresponding `tool_use` blocks in the conversation.
- In user messages containing tool results, `tool_result` blocks must come FIRST, before any text blocks.

### Memory Management Near Context Limits

- Use the Token Counting API (`POST /v1/messages/count_tokens`) to check token usage before sending.
- Implement sliding window: drop oldest messages while preserving the system prompt and recent context.
- Use prompt caching to avoid re-processing repeated content (system prompts, documents).
- Use context management strategies (compaction) via the `context-management-2025-06-27` beta.
- For thinking blocks: previous assistant turn thinking blocks are ignored and do NOT count toward input tokens on subsequent turns.

---

## 4. Tool Use / Function Calling — Deep Dive

### Tool Definition Schema

```json
{
    "name": "get_weather",
    "description": "Get the current weather in a given location. Returns temperature, humidity, and conditions. Use when the user asks about weather in a specific city.",
    "input_schema": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "The city and state, e.g. San Francisco, CA"
            },
            "unit": {
                "type": "string",
                "enum": ["celsius", "fahrenheit"],
                "description": "Temperature unit"
            }
        },
        "required": ["location"]
    }
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | `string` | Yes | Must match `^[a-zA-Z0-9_-]{1,64}$` |
| `description` | `string` | Yes | Detailed plaintext description. Aim for 3-4+ sentences. |
| `input_schema` | `object` | Yes | JSON Schema defining expected parameters |
| `input_examples` | `array` | No | Example input objects (must validate against schema). Adds ~20-200 tokens each. |

### Sending Tools in the Request

```bash
curl https://api.anthropic.com/v1/messages \
  -H "content-type: application/json" \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -d '{
    "model": "claude-opus-4-6",
    "max_tokens": 1024,
    "tools": [
      {
        "name": "get_weather",
        "description": "Get the current weather in a given location",
        "input_schema": {
          "type": "object",
          "properties": {
            "location": {"type": "string", "description": "City and state"}
          },
          "required": ["location"]
        }
      },
      {
        "name": "get_stock_price",
        "description": "Get the current stock price for a ticker symbol",
        "input_schema": {
          "type": "object",
          "properties": {
            "ticker": {"type": "string", "description": "Stock ticker symbol, e.g. AAPL"}
          },
          "required": ["ticker"]
        }
      }
    ],
    "messages": [{"role": "user", "content": "What is the weather in SF?"}]
  }'
```

### tool_choice Modes

| Mode | JSON Format | Behavior |
|------|------------|----------|
| `auto` | `{"type": "auto"}` | Claude decides whether to use tools. **Default when tools are provided.** |
| `any` | `{"type": "any"}` | Claude MUST use one of the provided tools. |
| `tool` | `{"type": "tool", "name": "get_weather"}` | Claude MUST use the specific named tool. |
| `none` | `{"type": "none"}` | Claude cannot use any tools. **Default when no tools provided.** |

**Extended thinking constraint:** When using extended thinking, only `auto` and `none` are supported. `any` and `tool` will return an error.

### How the Model Returns tool_use Content Blocks

When Claude decides to use a tool, the response has `stop_reason: "tool_use"` and contains `tool_use` blocks:

```json
{
    "stop_reason": "tool_use",
    "content": [
        {
            "type": "text",
            "text": "I'll check the weather for you."
        },
        {
            "type": "tool_use",
            "id": "toolu_01D7FLrfh4GYq7yT1ULFeyMV",
            "name": "get_weather",
            "input": {"location": "San Francisco, CA"}
        }
    ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `id` | `string` | Unique identifier for this tool call (e.g., `"toolu_01D7FLrfh4GYq7yT1ULFeyMV"`) |
| `name` | `string` | Name of the tool being called |
| `input` | `object` | Input parameters conforming to the tool's `input_schema` |

### Constructing tool_result Messages

```json
{
    "role": "user",
    "content": [
        {
            "type": "tool_result",
            "tool_use_id": "toolu_01D7FLrfh4GYq7yT1ULFeyMV",
            "content": "72°F, sunny, humidity 45%"
        }
    ]
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `tool_use_id` | `string` | Yes | Must match the `id` from the `tool_use` block |
| `content` | `string` or `array` | Yes | Result from executing the tool |
| `is_error` | `boolean` | No | Set to `true` if the tool execution failed |

### Parallel Tool Calls

Yes, Claude can request multiple tools in one response. The response will contain multiple `tool_use` blocks. You must return ALL results in the next user message:

```json
{
    "role": "user",
    "content": [
        {"type": "tool_result", "tool_use_id": "toolu_01A", "content": "Result A"},
        {"type": "tool_result", "tool_use_id": "toolu_01B", "content": "Result B"}
    ]
}
```

Disable parallel tool use with `"disable_parallel_tool_use": true` in `tool_choice`.

### Error Handling for Tool Calls

When a tool call fails, send the error back with `is_error: true`:

```json
{
    "type": "tool_result",
    "tool_use_id": "toolu_01D7FLrfh4GYq7yT1ULFeyMV",
    "content": "Error: City not found. Please provide a valid city name.",
    "is_error": true
}
```

Claude will see the error and can retry with corrected input or inform the user.

### Best Practices for Tool Descriptions

1. **Provide extremely detailed descriptions** — 3-4+ sentences minimum per tool.
2. **Consolidate related operations** into fewer tools with an `action` parameter.
3. **Use meaningful namespacing** in tool names (e.g., `github_list_prs`, `slack_send_message`).
4. **Return only high-signal information** from tools — semantic identifiers, not opaque IDs.
5. **Add `strict: true`** for guaranteed schema validation (Structured Outputs).

### Tool Use Token Overhead

When tools are provided, a system prompt is automatically injected:

| Model | `auto`/`none` | `any`/`tool` |
|-------|--------------|-------------|
| Claude Opus 4.6, 4.5, 4.1, 4 | 346 tokens | 313 tokens |
| Claude Sonnet 4.6, 4.5, 4 | 346 tokens | 313 tokens |
| Claude Haiku 4.5 | 346 tokens | 313 tokens |
| Claude Haiku 3.5 | 264 tokens | 340 tokens |

### Full Working Python Example — Multi-Turn with Two Tool Calls

```python
import anthropic
import json

client = anthropic.Anthropic()  # Uses ANTHROPIC_API_KEY env var

# Define tools
tools = [
    {
        "name": "get_weather",
        "description": "Get the current weather in a given location. Returns temperature and conditions.",
        "input_schema": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "City and state, e.g. San Francisco, CA"}
            },
            "required": ["location"]
        }
    },
    {
        "name": "get_time",
        "description": "Get the current time in a given timezone.",
        "input_schema": {
            "type": "object",
            "properties": {
                "timezone": {"type": "string", "description": "IANA timezone, e.g. America/New_York"}
            },
            "required": ["timezone"]
        }
    }
]

# Simulated tool implementations
def execute_tool(name, input_data):
    if name == "get_weather":
        return json.dumps({"temperature": "72°F", "conditions": "sunny", "humidity": "45%"})
    elif name == "get_time":
        return json.dumps({"time": "2:30 PM", "timezone": input_data["timezone"]})
    return json.dumps({"error": "Unknown tool"})

# Start conversation
messages = [{"role": "user", "content": "What's the weather and current time in San Francisco?"}]

# First API call — Claude will request tool use
response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    tools=tools,
    messages=messages
)

# Process tool calls in a loop until Claude produces a final response
while response.stop_reason == "tool_use":
    # Add assistant message to history
    messages.append({"role": "assistant", "content": response.content})

    # Execute all tool calls and collect results
    tool_results = []
    for block in response.content:
        if block.type == "tool_use":
            result = execute_tool(block.name, block.input)
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": result
            })

    # Send tool results back
    messages.append({"role": "user", "content": tool_results})

    # Get next response
    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1024,
        tools=tools,
        messages=messages
    )

# Final text response
print(response.content[0].text)
print(f"Total tokens: {response.usage.input_tokens} in, {response.usage.output_tokens} out")
```

### Server Tools (Web Search, Code Execution, etc.)

Server tools execute on Anthropic's servers. You don't implement them — just specify them in the request. The API runs an internal sampling loop (max 10 iterations by default).

```json
{
    "tools": [
        {"type": "web_search_20250305", "name": "web_search"}
    ]
}
```

If the loop limit is reached, the response has `stop_reason: "pause_turn"`. Send the response back as-is to continue.

---

## 5. Streaming — Complete Protocol

### Enable Streaming

Set `"stream": true` in the request body. Response is returned as Server-Sent Events (SSE).

### SSE Event Types

| Event | Description | Data Shape |
|-------|-------------|-----------|
| `message_start` | Initial Message object with empty content | `{"type": "message_start", "message": {Message}}` |
| `content_block_start` | New content block begins | `{"type": "content_block_start", "index": N, "content_block": {type, ...}}` |
| `content_block_delta` | Incremental content update | `{"type": "content_block_delta", "index": N, "delta": {type-specific}}` |
| `content_block_stop` | Content block complete | `{"type": "content_block_stop", "index": N}` |
| `message_delta` | Message-level changes | `{"type": "message_delta", "delta": {"stop_reason": "...", "stop_sequence": ...}, "usage": {"output_tokens": N}}` |
| `message_stop` | End of stream | `{"type": "message_stop"}` |
| `ping` | Keep-alive | `{"type": "ping"}` |
| `error` | Error during stream | `{"type": "error", "error": {"type": "...", "message": "..."}}` |

### Delta Types

| Delta Type | Used In | Shape |
|-----------|---------|-------|
| `text_delta` | Text blocks | `{"type": "text_delta", "text": "chunk"}` |
| `input_json_delta` | Tool use blocks | `{"type": "input_json_delta", "partial_json": "{\"loc..."}` |
| `thinking_delta` | Thinking blocks | `{"type": "thinking_delta", "thinking": "reasoning..."}` |
| `signature_delta` | Thinking blocks (before stop) | `{"type": "signature_delta", "signature": "EqQB..."}` |

### Event Flow

```
message_start
  content_block_start (index=0, type=text)
    content_block_delta (text_delta)
    content_block_delta (text_delta)
    ...
  content_block_stop (index=0)
  content_block_start (index=1, type=tool_use)
    content_block_delta (input_json_delta)
    content_block_delta (input_json_delta)
    ...
  content_block_stop (index=1)
message_delta (stop_reason, usage)
message_stop
```

### How tool_use Blocks Stream

The `input` JSON streams incrementally as `input_json_delta` with `partial_json` strings. Accumulate all delta strings and parse the full JSON when you receive `content_block_stop`. Current models emit one complete key-value pair at a time, so there may be delays between events during tool input generation.

### Full Streaming Response Example

```
event: message_start
data: {"type": "message_start", "message": {"id": "msg_1nZdL29xx5MUA1yADyHTEsnR8uuvGzszyY", "type": "message", "role": "assistant", "content": [], "model": "claude-opus-4-6", "stop_reason": null, "stop_sequence": null, "usage": {"input_tokens": 25, "output_tokens": 1}}}

event: content_block_start
data: {"type": "content_block_start", "index": 0, "content_block": {"type": "text", "text": ""}}

event: ping
data: {"type": "ping"}

event: content_block_delta
data: {"type": "content_block_delta", "index": 0, "delta": {"type": "text_delta", "text": "Hello"}}

event: content_block_delta
data: {"type": "content_block_delta", "index": 0, "delta": {"type": "text_delta", "text": "!"}}

event: content_block_stop
data: {"type": "content_block_stop", "index": 0}

event: message_delta
data: {"type": "message_delta", "delta": {"stop_reason": "end_turn", "stop_sequence": null}, "usage": {"output_tokens": 15}}

event: message_stop
data: {"type": "message_stop"}
```

### Full Working Python Streaming Example with Tool Use

```python
import anthropic
import json

client = anthropic.Anthropic()

# Using the SDK streaming helper
with client.messages.stream(
    model="claude-opus-4-6",
    max_tokens=1024,
    tools=[{
        "name": "get_weather",
        "description": "Get the current weather in a given location",
        "input_schema": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "City and state"}
            },
            "required": ["location"]
        }
    }],
    messages=[{"role": "user", "content": "What's the weather in Boston?"}],
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)

    # Get the complete message after streaming
    message = stream.get_final_message()
    print(f"\nStop reason: {message.stop_reason}")
    print(f"Usage: {message.usage.input_tokens} in, {message.usage.output_tokens} out")

    # If tool_use, handle it
    if message.stop_reason == "tool_use":
        for block in message.content:
            if block.type == "tool_use":
                print(f"Tool call: {block.name}({block.input})")
```

### Low-Level Streaming (Raw SSE)

```python
stream = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello"}],
    stream=True,
)
for event in stream:
    if event.type == "content_block_delta":
        if event.delta.type == "text_delta":
            print(event.delta.text, end="", flush=True)
        elif event.delta.type == "input_json_delta":
            print(event.delta.partial_json, end="")
    elif event.type == "message_delta":
        print(f"\nStop: {event.delta.stop_reason}")
```

---

## 6. Vision / Multimodal

### Image Input

**Supported formats:** JPEG, PNG, GIF, WebP

**Size limits:**
- Maximum: 8000x8000 px (single image)
- If >20 images in one request: max 2000x2000 px each
- Up to 600 images per API request (100 for 200k-token context models)
- Request size limit: 32 MB

**Optimal sizing:** Resize to max 1568 px on the long edge (1.15 megapixels) for best latency without quality loss.

**Token calculation:** `tokens = (width_px * height_px) / 750`

| Image Size | Tokens | Cost (Sonnet 4.6 @ $3/MTok) |
|-----------|--------|------------------------------|
| 200x200 px | ~54 | ~$0.00016 |
| 1000x1000 px | ~1,334 | ~$0.004 |
| 1092x1092 px | ~1,590 | ~$0.0048 |

### Three Ways to Send Images

**Base64:**
```json
{
    "type": "image",
    "source": {
        "type": "base64",
        "media_type": "image/jpeg",
        "data": "<BASE64_DATA>"
    }
}
```

**URL:**
```json
{
    "type": "image",
    "source": {
        "type": "url",
        "url": "https://example.com/image.jpg"
    }
}
```

**Files API (best for multi-turn / repeated use):**
```json
{
    "type": "image",
    "source": {
        "type": "file",
        "file_id": "file_abc123"
    }
}
```

### PDF Input

**Limits:**
- Max request size: 32 MB
- Max pages per request: 600 (100 for 200k-token context models)
- Format: Standard PDF (no passwords/encryption)

**How it works:** Each page is converted to an image + extracted text. Token cost: ~1,500-3,000 tokens per page (text) + image tokens per page.

**Three ways to send PDFs:** URL, base64, or Files API — all use `"type": "document"` content block:

```json
{
    "type": "document",
    "source": {
        "type": "url",
        "url": "https://example.com/document.pdf"
    },
    "title": "Q4 Report",
    "context": "Annual financial report",
    "citations": {"enabled": true}
}
```

### Best Practices

- Place images/PDFs BEFORE text in the message content array.
- For multi-turn conversations, upload via Files API to avoid re-sending base64 on every turn.

---

## 7. System Prompts

### How They Work

System prompts go in the **top-level `system` field**, NOT in the `messages` array:

```json
{
    "model": "claude-opus-4-6",
    "max_tokens": 1024,
    "system": "You are a helpful weather assistant. Always provide temperatures in Fahrenheit.",
    "messages": [{"role": "user", "content": "Weather in Boston?"}]
}
```

### System Prompt as Array (for caching)

```json
{
    "system": [
        {
            "type": "text",
            "text": "You are a helpful assistant...",
            "cache_control": {"type": "ephemeral"}
        }
    ]
}
```

### System Prompt Interaction with Tools

When tools are provided, Anthropic injects an additional system prompt enabling tool use (346 or 313 tokens depending on `tool_choice`). This is prepended to your system prompt.

### Caching Behavior

System prompts are prime candidates for caching. Place `cache_control` on the system text block. The cached system prompt is reused across requests with identical content, reducing both cost and latency.

---

## 8. Rate Limits

### Spend Limits by Tier

| Tier | Credit Purchase Threshold | Max Single Purchase | Monthly Spend Limit |
|------|--------------------------|--------------------|--------------------|
| Tier 1 | $5 | $100 | $100 |
| Tier 2 | $40 | $500 | $500 |
| Tier 3 | $200 | $1,000 | $1,000 |
| Tier 4 | $400 | $200,000 | $200,000 |
| Monthly Invoicing | N/A | N/A | No limit |

### Rate Limits (Tier 1 — Messages API)

| Model | RPM | Input TPM (ITPM) | Output TPM (OTPM) |
|-------|-----|-------------------|-------------------|
| Claude Opus 4.x* | 50 | 30,000 | 8,000 |
| Claude Sonnet 4.x** | 50 | 30,000 | 8,000 |
| Claude Haiku 4.5 | 50 | 50,000 | 10,000 |
| Claude Haiku 3.5 (deprecated) | 50 | 50,000† | 10,000 |
| Claude Haiku 3 | 50 | 50,000† | 10,000 |

\* Opus limit shared across Opus 4.6, 4.5, 4.1, and 4.
\*\* Sonnet limit shared across Sonnet 4.6, 4.5, and 4.
† Cache read tokens count toward ITPM on these models.

**Cache-aware ITPM:** For most models (without †), only `input_tokens + cache_creation_input_tokens` count toward ITPM. `cache_read_input_tokens` do NOT count. With 80% cache hit rate, effective throughput is 5x the limit.

**OTPM:** Evaluated in real-time on actual output tokens. `max_tokens` parameter does NOT factor into OTPM calculation.

### Message Batches API Rate Limits

| Limit | All Tiers |
|-------|-----------|
| RPM | 50 |
| Max batch requests in queue | 100,000 |
| Max requests per batch | 100,000 |

### Fast Mode Rate Limits

Dedicated rate limits separate from standard Opus limits. Response includes `anthropic-fast-*` headers.

### Response Headers

| Header | Description |
|--------|-------------|
| `retry-after` | Seconds to wait before retrying |
| `anthropic-ratelimit-requests-limit` | Max RPM |
| `anthropic-ratelimit-requests-remaining` | Remaining requests |
| `anthropic-ratelimit-requests-reset` | RFC 3339 reset time |
| `anthropic-ratelimit-input-tokens-limit` | Max ITPM |
| `anthropic-ratelimit-input-tokens-remaining` | Remaining input tokens (nearest 1000) |
| `anthropic-ratelimit-input-tokens-reset` | RFC 3339 reset time |
| `anthropic-ratelimit-output-tokens-limit` | Max OTPM |
| `anthropic-ratelimit-output-tokens-remaining` | Remaining output tokens (nearest 1000) |
| `anthropic-ratelimit-output-tokens-reset` | RFC 3339 reset time |

The API uses **token bucket algorithm** — capacity refills continuously, not on fixed intervals.

---

## 9. Error Handling

### Error Types

| HTTP Status | Error Type | Description |
|------------|-----------|-------------|
| 400 | `invalid_request_error` | Bad format or content |
| 401 | `authentication_error` | Invalid API key |
| 402 | `billing_error` | Payment issue |
| 403 | `permission_error` | Insufficient permissions |
| 404 | `not_found_error` | Resource not found |
| 413 | `request_too_large` | Exceeds max request size |
| 429 | `rate_limit_error` | Rate limit exceeded |
| 500 | `api_error` | Internal Anthropic error |
| 529 | `overloaded_error` | API temporarily overloaded |

### Request Size Limits

| Endpoint | Max Size |
|----------|---------|
| Messages API | 32 MB |
| Token Counting API | 32 MB |
| Batch API | 256 MB |
| Files API | 500 MB |

### Error Response Shape

```json
{
    "type": "error",
    "error": {
        "type": "not_found_error",
        "message": "The requested resource could not be found."
    },
    "request_id": "req_011CSHoEeqs5C35K2UUqR7Fy"
}
```

Every response includes a `request-id` header for support debugging.

### Handling Each Error Programmatically

```python
import anthropic

try:
    message = client.messages.create(...)
except anthropic.APIConnectionError as e:
    print("Server unreachable:", e.__cause__)
except anthropic.RateLimitError as e:
    print("429 — back off. Retry-after:", e.response.headers.get("retry-after"))
except anthropic.BadRequestError as e:
    print("400 — invalid request:", e.message)
except anthropic.AuthenticationError as e:
    print("401 — check API key")
except anthropic.PermissionDeniedError as e:
    print("403 — insufficient permissions")
except anthropic.NotFoundError as e:
    print("404 — resource not found")
except anthropic.InternalServerError as e:
    print("500+ — Anthropic internal error, retry")
except anthropic.APIStatusError as e:
    print(f"Other error: {e.status_code} — {e.response}")
```

---

## 10. Python SDK

### Installation

```bash
pip install anthropic

# With platform extras
pip install anthropic[bedrock]    # AWS Bedrock
pip install anthropic[vertex]     # Google Vertex AI
pip install anthropic[aiohttp]    # Better async performance
```

Requires Python 3.9+.

### Client Initialization

```python
from anthropic import Anthropic, AsyncAnthropic

# Sync client (reads ANTHROPIC_API_KEY from env)
client = Anthropic()

# Explicit API key
client = Anthropic(api_key="sk-ant-...")

# Async client
async_client = AsyncAnthropic()
```

### Basic Call

```python
message = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello, Claude"}],
)
print(message.content[0].text)
print(f"Usage: {message.usage}")  # Usage(input_tokens=12, output_tokens=8)
```

### Streaming Call

```python
# High-level streaming helper (context manager)
with client.messages.stream(
    model="claude-opus-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello"}],
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)

    # Get complete message after streaming
    message = stream.get_final_message()

# Low-level streaming (raw events)
stream = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello"}],
    stream=True,
)
for event in stream:
    print(event.type)
```

### Tool Use Call

```python
from anthropic import Anthropic, beta_tool
import json

client = Anthropic()

@beta_tool
def get_weather(location: str) -> str:
    """Get the weather for a given location.
    Args:
        location: The city and state, e.g. San Francisco, CA
    """
    return json.dumps({"temperature": "68°F", "condition": "Sunny"})

# Automatic tool execution with tool_runner
runner = client.beta.messages.tool_runner(
    model="claude-opus-4-6",
    max_tokens=1024,
    tools=[get_weather],
    messages=[{"role": "user", "content": "What's the weather in SF?"}],
)
for message in runner:
    print(message.content[0].text)
```

### Error Handling

```python
try:
    message = client.messages.create(...)
except anthropic.APIConnectionError as e:
    print("Server unreachable")
except anthropic.RateLimitError as e:
    print("429 rate limited")
except anthropic.APIStatusError as e:
    print(f"Error {e.status_code}: {e.response}")
```

### Retry Configuration

Default: 2 retries with exponential backoff. Auto-retries on: connection errors, 408, 409, 429, >=500.

```python
client = Anthropic(max_retries=5)  # Global
client.with_options(max_retries=0).messages.create(...)  # Per-request
```

### Timeout Configuration

Default: 10 minutes. The SDK throws `ValueError` if a non-streaming request is expected to exceed ~10 minutes.

```python
import httpx
client = Anthropic(timeout=20.0)  # 20 seconds
client = Anthropic(timeout=httpx.Timeout(60.0, read=5.0, write=10.0, connect=2.0))
```

### Request IDs

```python
message = client.messages.create(...)
print(message._request_id)  # req_018EeWyXxfu5pfWkrYcMdjWG
```

### Platform Integrations

```python
from anthropic import AnthropicBedrock, AnthropicVertex, AnthropicFoundry

# AWS Bedrock
bedrock_client = AnthropicBedrock()

# Google Vertex AI
vertex_client = AnthropicVertex()

# Microsoft Foundry
foundry_client = AnthropicFoundry()
```

---

## 11. Batch API

### Create a Batch

```
POST /v1/messages/batches
```

```python
batch = client.messages.batches.create(
    requests=[
        {
            "custom_id": "request-001",
            "params": {
                "model": "claude-opus-4-6",
                "max_tokens": 1024,
                "messages": [{"role": "user", "content": "Hello"}],
            },
        },
        {
            "custom_id": "request-002",
            "params": {
                "model": "claude-opus-4-6",
                "max_tokens": 1024,
                "messages": [{"role": "user", "content": "Hi again"}],
            },
        },
    ]
)
print(batch.id)  # msgbatch_013Zva...
```

### Batch Pricing — 50% Discount

| Model | Batch Input | Batch Output |
|-------|-----------|-------------|
| Opus 4.6 | $2.50/MTok | $12.50/MTok |
| Sonnet 4.6 | $1.50/MTok | $7.50/MTok |
| Haiku 4.5 | $0.50/MTok | $2.50/MTok |

### Batch Lifecycle

- Max request size: 256 MB
- Max requests per batch: 100,000
- Processing: up to 24 hours
- States: `in_progress` → `canceling` → `ended`
- Results expire 24 hours after creation

### Poll for Results

```python
batch = client.messages.batches.retrieve("msgbatch_013Zva...")

if batch.processing_status == "ended":
    for entry in client.messages.batches.results(batch.id):
        if entry.result.type == "succeeded":
            print(f"{entry.custom_id}: {entry.result.message.content[0].text}")
        elif entry.result.type == "errored":
            print(f"{entry.custom_id}: ERROR - {entry.result.error}")
```

### Result Types

| Type | Description |
|------|-------------|
| `succeeded` | Contains full `Message` object |
| `errored` | Contains `ErrorResponse` |
| `canceled` | Request was canceled |
| `expired` | Request expired before processing |

Results are JSONL (one JSON per line). Order is NOT guaranteed — use `custom_id` to match.

---

## 12. Token Counting

### Endpoint

```
POST /v1/messages/count_tokens
```

### Usage

```python
count = client.messages.count_tokens(
    model="claude-opus-4-6",
    messages=[{"role": "user", "content": "Hello, world"}],
)
print(count.input_tokens)  # 10
```

Accepts the same parameters as Create a Message: `messages`, `model`, `system`, `tools`, `thinking`, `tool_choice`, `mcp_servers`.

### Response

```json
{"input_tokens": 10}
```

### Key Details

- Free to use (no token charges)
- Subject to RPM limits: Tier 1 = 100, Tier 2 = 2,000, Tier 3 = 4,000, Tier 4 = 8,000 RPM
- Token counting and message creation have **separate independent rate limits**
- Counts all input tokens: system + messages + tools + images + documents
- Thinking blocks from previous assistant turns are **ignored** and don't count
- Token count is an estimate; actual usage may vary by a small amount

---

## 13. Prompt Caching

### How It Works

Cache frequently reused content (system prompts, documents, tool definitions) to avoid re-processing.

### Automatic Caching

```json
{
    "model": "claude-opus-4-6",
    "max_tokens": 1024,
    "system": [{"type": "text", "text": "Long system prompt...", "cache_control": {"type": "ephemeral"}}],
    "messages": [{"role": "user", "content": "Question"}]
}
```

### Pricing

| Operation | Multiplier | Duration |
|-----------|-----------|----------|
| 5-minute cache write | 1.25x base input | 5 minutes |
| 1-hour cache write | 2.0x base input | 1 hour |
| Cache read (hit) | 0.10x base input | Same as write |

Cache pays for itself after 1 read (5-min) or 2 reads (1-hour).

### 1-Hour Extended Cache

```json
"cache_control": {"type": "ephemeral", "ttl": "1h"}
```

1-hour entries must appear before 5-minute entries in the request.

---

## 14. Extended Thinking & Effort

### Extended Thinking

Enable step-by-step reasoning visible in the response:

```python
response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=20000,
    thinking={"type": "enabled", "budget_tokens": 16000},
    messages=[{"role": "user", "content": "Prove there are infinitely many primes."}],
)
for block in response.content:
    if block.type == "thinking":
        print("THINKING:", block.thinking[:200])
    elif block.type == "text":
        print("ANSWER:", block.text)
```

### Adaptive Thinking

Auto-decides whether to think based on query complexity (Opus 4.6 and Sonnet 4.6 only):

```json
"thinking": {"type": "adaptive"}
```

### Reasoning Effort

Control reasoning depth without thinking blocks:

```json
"reasoning_effort": "low"   // quick, minimal reasoning
"reasoning_effort": "medium"
"reasoning_effort": "high"
"reasoning_effort": "max"   // deepest reasoning
```

---

## 15. Structured Outputs

Force Claude to return valid JSON matching a schema:

```json
{
    "model": "claude-opus-4-6",
    "max_tokens": 1024,
    "output_config": {
        "format": {
            "type": "json_schema",
            "json_schema": {
                "name": "weather_response",
                "schema": {
                    "type": "object",
                    "properties": {
                        "city": {"type": "string"},
                        "temperature": {"type": "number"},
                        "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
                    },
                    "required": ["city", "temperature", "unit"]
                }
            }
        }
    },
    "messages": [{"role": "user", "content": "Weather in Paris"}]
}
```

Add `strict: true` to tool definitions for guaranteed schema validation of tool inputs.

---

## 16. Files API (Beta)

**Beta header required:** `anthropic-beta: files-api-2025-04-14`

### Upload

```bash
curl -X POST https://api.anthropic.com/v1/files \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "anthropic-beta: files-api-2025-04-14" \
  -F "file=@document.pdf"
```

### Use in Messages

```json
{"type": "document", "source": {"type": "file", "file_id": "file_011CNha..."}}
```

### Limits

- Max file size: 500 MB
- Total storage: 500 GB per organization
- File operations are free; content used in messages billed as input tokens
- Rate limit: ~100 RPM during beta
- Files scoped to workspace; persist until deleted

---

## 17. Key Decisions for Our Stack

### For Real-Time Voice (Vapi Integration)

| Setting | Value | Rationale |
|---------|-------|-----------|
| Model | `claude-sonnet-4-6` | Best speed/intelligence balance; fast latency |
| `max_tokens` | `256`–`512` | Voice responses must be short |
| `stream` | `true` | **Required** — stream tokens to Vapi for real-time TTS |
| `temperature` | `0.7` | Natural conversational variation |
| Tools | Yes — keep tool count low (≤5) | Minimize latency from tool overhead |
| For maximum speed | Consider `claude-haiku-4-5` | Fastest model, lowest cost, still strong reasoning |

### For Asset Generation (PaidEdge)

| Setting | Value | Rationale |
|---------|-------|-----------|
| Model | `claude-opus-4-6` | Highest quality output for creative/analytical content |
| `max_tokens` | `4096`–`16384` | Assets need room; adjust per asset type |
| `temperature` | `0.8`–`1.0` | Higher creativity for content generation |
| `stream` | `false` or `true` | Non-streaming for batch; streaming for interactive |
| Structured outputs | Use `output_config` with JSON schema | Ensure parseable, consistent output format |
| For cost optimization | Use Batch API (50% off) for non-urgent generation | $2.50/MTok input, $12.50/MTok output |

### For Chat Interfaces

| Setting | Value | Rationale |
|---------|-------|-----------|
| Model | `claude-sonnet-4-6` | Good balance of quality and speed for interactive chat |
| `max_tokens` | `2048`–`4096` | Reasonable for conversational responses |
| `stream` | `true` | **Always stream** for responsive UX |
| `temperature` | `0.7`–`1.0` | Natural conversational tone |
| System prompt | Cache with `cache_control` | Saves cost on every turn of multi-turn conversations |
| Extended thinking | `{"type": "adaptive"}` on Sonnet 4.6 | Automatically engages for complex queries |

### For Tool-Heavy Workflows

| Setting | Value | Rationale |
|---------|-------|-----------|
| Model | `claude-opus-4-6` | Best tool-use quality; handles complex multi-tool scenarios, seeks clarification |
| `tool_choice` | `{"type": "auto"}` | Let Claude decide when to use tools |
| Parallel tools | Enabled by default | Claude can request multiple tools at once |
| `max_tokens` | `4096`+ | Tool-use responses include JSON blocks that consume tokens |
| Descriptions | 3-4+ sentences per tool | Single most important factor for tool-use accuracy |
| For simpler tools | `claude-sonnet-4-6` works well | Faster, cheaper; but may infer missing params |
| `strict: true` | On tool `input_schema` | Guarantees schema-valid tool inputs |

### Cost Comparison Matrix (Per 1M Input + 1M Output Tokens)

| Model | Standard | Batch (50% off) | With 80% Cache Hit |
|-------|----------|------------------|--------------------|
| Opus 4.6 | $30 | $15 | ~$8.50 |
| Sonnet 4.6 | $18 | $9 | ~$5.10 |
| Haiku 4.5 | $6 | $3 | ~$1.70 |

---

## Appendix A: Complete Pricing Reference

### Standard Pricing

| Model | Input | Output | 5m Cache Write | 1h Cache Write | Cache Read |
|-------|-------|--------|---------------|---------------|------------|
| Opus 4.6 | $5/MTok | $25/MTok | $6.25/MTok | $10/MTok | $0.50/MTok |
| Opus 4.5 | $5/MTok | $25/MTok | $6.25/MTok | $10/MTok | $0.50/MTok |
| Opus 4.1 | $15/MTok | $75/MTok | $18.75/MTok | $30/MTok | $1.50/MTok |
| Opus 4 | $15/MTok | $75/MTok | $18.75/MTok | $30/MTok | $1.50/MTok |
| Sonnet 4.6 | $3/MTok | $15/MTok | $3.75/MTok | $6/MTok | $0.30/MTok |
| Sonnet 4.5 | $3/MTok | $15/MTok | $3.75/MTok | $6/MTok | $0.30/MTok |
| Sonnet 4 | $3/MTok | $15/MTok | $3.75/MTok | $6/MTok | $0.30/MTok |
| Haiku 4.5 | $1/MTok | $5/MTok | $1.25/MTok | $2/MTok | $0.10/MTok |
| Haiku 3.5 | $0.80/MTok | $4/MTok | $1/MTok | $1.60/MTok | $0.08/MTok |
| Haiku 3 | $0.25/MTok | $1.25/MTok | $0.30/MTok | $0.50/MTok | $0.03/MTok |

### Additional Pricing

| Feature | Price |
|---------|-------|
| Web search | $10 per 1,000 searches + standard token costs |
| Web fetch | Free (standard token costs only) |
| Code execution (w/ web tools) | Free |
| Code execution (standalone) | $0.05/hr after 1,550 free hrs/mo; 5-min minimum |
| Fast mode (Opus 4.6) | $30/MTok input, $150/MTok output (6x standard) |
| Data residency (US-only, Opus 4.6+) | 1.1x multiplier on all token pricing |
| Long context (Sonnet 4.5/4, >200k) | 2x input, 1.5x output |

---

## Appendix B: Beta Headers Reference

| Beta Feature | Header Value |
|-------------|-------------|
| Files API | `files-api-2025-04-14` |
| MCP Connector | `mcp-client-2025-11-20` |
| Prompt Caching | `prompt-caching-2024-07-31` |
| Computer Use | `computer-use-2025-01-24` |
| Token Counting | `token-counting-2024-11-01` |
| Code Execution | `code-execution-2025-05-22` |
| 1M Context (Sonnet 4.5/4) | `context-1m-2025-08-07` |
| Context Management | `context-management-2025-06-27` |
| Extended Cache TTL | `extended-cache-ttl-2025-04-11` |
| Skills API | `skills-2025-10-02` |
| Fast Mode | `fast-mode-2026-02-01` |
| Output 128k | `output-128k-2025-02-19` |
| Token-Efficient Tools | `token-efficient-tools-2025-02-19` |
| PDFs | `pdfs-2024-09-25` |
| Message Batches | `message-batches-2024-09-24` |

---

## Appendix C: MCP Connector (Beta)

Connect to remote MCP servers directly from the Messages API without implementing an MCP client.

**Header:** `anthropic-beta: mcp-client-2025-11-20`

```json
{
    "model": "claude-opus-4-6",
    "max_tokens": 1024,
    "mcp_servers": [
        {
            "type": "url",
            "url": "https://my-mcp-server.example.com/mcp",
            "name": "my-server",
            "tool_configuration": {
                "enabled": true
            }
        }
    ],
    "messages": [{"role": "user", "content": "Query my database"}]
}
```

**Limitations:** Only tool calls supported (not resources/prompts). Server must be publicly exposed via HTTP. Not supported on Bedrock/Vertex.

---

## Appendix D: Admin API

The Admin API (`/v1/organizations/*`) provides programmatic management. Requires admin API key.

| Resource | Endpoints |
|----------|----------|
| Organizations | `GET /v1/organizations/me` |
| Invites | CRUD at `/v1/organizations/invites` |
| Users | CRUD at `/v1/organizations/users` |
| Workspaces | CRUD at `/v1/organizations/workspaces` |
| Workspace Members | CRUD at `/v1/organizations/workspaces/{id}/members` |
| API Keys | List/Get/Update at `/v1/organizations/api_keys` |
| Usage Reports | `GET /v1/organizations/usage` (messages, Claude Code) |
| Cost Reports | `GET /v1/organizations/costs` |