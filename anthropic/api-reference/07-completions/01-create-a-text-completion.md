# Create a Text Completion

`POST /v1/complete`

[Legacy] Create a Text Completion.

The Text Completions API is a legacy API. We recommend using the Messages API going forward. Future models and features will not be compatible with Text Completions. See our migration guide for guidance in migrating from Text Completions to Messages.

## Header Parameters

### `anthropic-beta`
`optional array of AnthropicBeta`

Optional header to specify the beta version(s) you want to use.

Accepts one of the following:

- `"message-batches-2024-09-24"`
- `"prompt-caching-2024-07-31"`
- `"computer-use-2024-10-22"`
- `"computer-use-2025-01-24"`
- `"pdfs-2024-09-25"`
- `"token-counting-2024-11-01"`
- `"token-efficient-tools-2025-02-19"`
- `"output-128k-2025-02-19"`
- `"files-api-2025-04-14"`
- `"mcp-client-2025-04-04"`
- `"mcp-client-2025-11-20"`
- `"dev-full-thinking-2025-05-14"`
- `"interleaved-thinking-2025-05-14"`
- `"code-execution-2025-05-22"`
- `"extended-cache-ttl-2025-04-11"`
- `"context-1m-2025-08-07"`
- `"context-management-2025-06-27"`
- `"model-context-window-exceeded-2025-08-26"`
- `"skills-2025-10-02"`
- `"fast-mode-2026-02-01"`

## Body Parameters

### `max_tokens_to_sample`
`number` **required**

The maximum number of tokens to generate before stopping.

Note that our models may stop before reaching this maximum. This parameter only specifies the absolute maximum number of tokens to generate.

Minimum: `1`

### `model`
`Model` **required**

The model that will complete your prompt. See models for additional details and options.

Accepts one of the following:

- `"claude-opus-4-6"` - Most intelligent model for building agents and coding
- `"claude-sonnet-4-6"` - Best combination of speed and intelligence
- `"claude-haiku-4-5"` - Fastest model with near-frontier intelligence
- `"claude-haiku-4-5-20251001"` - Fastest model with near-frontier intelligence
- `"claude-opus-4-5"` - Premium model combining maximum intelligence with practical performance
- `"claude-opus-4-5-20251101"` - Premium model combining maximum intelligence with practical performance
- `"claude-sonnet-4-5"` - High-performance model for agents and coding
- `"claude-sonnet-4-5-20250929"` - High-performance model for agents and coding
- `"claude-opus-4-1"` - Exceptional model for specialized complex tasks
- `"claude-opus-4-1-20250805"` - Exceptional model for specialized complex tasks
- `"claude-opus-4-0"` - Powerful model for complex tasks
- `"claude-opus-4-20250514"` - Powerful model for complex tasks
- `"claude-sonnet-4-0"` - High-performance model with extended thinking
- `"claude-sonnet-4-20250514"` - High-performance model with extended thinking
- `"claude-3-haiku-20240307"` - Fast and cost-effective model

### `prompt`
`string` **required**

The prompt that you want Claude to complete.

For proper response generation you will need to format your prompt using alternating `\n\nHuman:` and `\n\nAssistant:` conversational turns. For example:

```
"\n\nHuman: {userQuestion}\n\nAssistant:"
```

See prompt validation and our guide to prompt design for more details.

Min length: `1`

### `metadata`
`optional Metadata`

An object describing metadata about the request.

#### `user_id`
`optional string`

An external identifier for the user who is associated with the request. This should be a uuid, hash value, or other opaque identifier. Anthropic may use this id to help detect abuse. Do not include any identifying information such as name, email address, or phone number.

Max length: `512`

### `stop_sequences`
`optional array of string`

Sequences that will cause the model to stop generating.

Our models stop on `"\n\nHuman:"`, and may include additional built-in stop sequences in the future. By providing the `stop_sequences` parameter, you may include additional strings that will cause the model to stop generating.

### `stream`
`optional boolean`

Whether to incrementally stream the response using server-sent events. See streaming for details.

### `temperature`
`optional number`

Amount of randomness injected into the response.

Defaults to `1.0`. Ranges from `0.0` to `1.0`. Use temperature closer to `0.0` for analytical / multiple choice, and closer to `1.0` for creative and generative tasks.

Note that even with temperature of `0.0`, the results will not be fully deterministic.

Minimum: `0`, Maximum: `1`

### `top_k`
`optional number`

Only sample from the top K options for each subsequent token.

Used to remove "long tail" low probability responses. Learn more technical details here. Recommended for advanced use cases only. You usually only need to use `temperature`.

Minimum: `0`

### `top_p`
`optional number`

Use nucleus sampling.

In nucleus sampling, we compute the cumulative distribution over all the options for each subsequent token in decreasing probability order and cut it off once it reaches a particular probability specified by `top_p`. You should either alter `temperature` or `top_p`, but not both.

Recommended for advanced use cases only. You usually only need to use `temperature`.

Minimum: `0`, Maximum: `1`

## Returns

A [Completion](/07-completions/00-completions.md) object.

### Example Request

```bash
curl https://api.anthropic.com/v1/complete \
  -H 'Content-Type: application/json' \
  -H 'anthropic-version: 2023-06-01' \
  -H "X-Api-Key: $ANTHROPIC_API_KEY" \
  --max-time 600 \
  -d '{
    "max_tokens_to_sample": 256,
    "model": "claude-opus-4-6",
    "prompt": "\n\nHuman: Hello, world!\n\nAssistant:"
  }'
```

### Example Response (200)

```json
{
  "id": "compl_018CKm6gsux7P8yMcwZbeCPw",
  "completion": " Hello! My name is Claude.",
  "model": "claude-2.1",
  "stop_reason": "stop_sequence",
  "type": "completion"
}
```
