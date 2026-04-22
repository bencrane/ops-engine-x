# Beta - Create a Message Batch

`POST /v1/messages/batches`

Send a batch of Message creation requests.

The Message Batches API can be used to process multiple Messages API requests at once. Once a Message Batch is created, it begins processing immediately. Batches can take up to 24 hours to complete.

## Header Parameters

- **anthropic-beta**: `array of AnthropicBeta` (optional) — Optional header to specify the beta version(s) you want to use.

## Body Parameters (JSON)

- **requests**: `array of object { custom_id, params }` (required) — List of requests for prompt completion. Each is an individual request to create a Message.
  - **custom_id**: `string` — Developer-provided ID created for each request in a Message Batch. Useful for matching results to requests, as results may be given out of request order. Must be unique for each request within the Message Batch. maxLength: 64, minLength: 1.
  - **params**: `object` — Messages API creation parameters for the individual request. See the Messages API reference for full documentation on available parameters.
    - **max_tokens**: `number` — The maximum number of tokens to generate before stopping.
    - **messages**: `array of BetaMessageParam { content, role }` — Input messages.
    - **model**: `string` — The model that will complete your prompt.
    - And all other standard Messages API parameters (betas, citations, metadata, reasoning_effort, service_tier, stop_sequences, stream, system, temperature, thinking, tool_choice, tools, top_k, top_p, etc.)

## Returns

### BetaMessageBatch

`object { id, cancel_initiated_at, created_at, ended_at, expires_at, processing_status, request_counts, results_url, type }`

- **id**: `string` — Unique object identifier. Format: `msgbatch_`.
- **cancel_initiated_at**: `string` or `null` — RFC 3339 datetime string when cancellation was initiated, if applicable.
- **created_at**: `string` — RFC 3339 datetime string when the Message Batch was created.
- **ended_at**: `string` or `null` — RFC 3339 datetime string when processing ended.
- **expires_at**: `string` — RFC 3339 datetime string when the Message Batch will expire.
- **processing_status**: `"in_progress"` or `"canceling"` or `"ended"` — Processing status of the Message Batch.
- **request_counts**: `BetaRequestCounts` — Tallies of requests within the Message Batch by their status.
  - **canceled**: `number` — Number of requests that were canceled.
  - **errored**: `number` — Number of requests that encountered an error.
  - **expired**: `number` — Number of requests that expired.
  - **processing**: `number` — Number of requests currently being processed.
  - **succeeded**: `number` — Number of requests that completed successfully.
- **results_url**: `string` or `null` — URL to a .jsonl file containing the results of the Message Batch requests.
- **type**: `"message_batch"` — Object type. For Message Batches, this is always "message_batch".

## Example Request

```bash
curl https://api.anthropic.com/v1/messages/batches \
  -H "content-type: application/json" \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -d '{
    "requests": [
      {
        "custom_id": "my-first-request",
        "params": {
          "model": "claude-opus-4-6",
          "max_tokens": 1024,
          "messages": [
            {"role": "user", "content": "Hello, world"}
          ]
        }
      },
      {
        "custom_id": "my-second-request",
        "params": {
          "model": "claude-opus-4-6",
          "max_tokens": 1024,
          "messages": [
            {"role": "user", "content": "Hi again, friend"}
          ]
        }
      }
    ]
  }'
```

## Response 200

```json
{
  "id": "msgbatch_013Zva2CMHLNnXjNJJKqJ2EF",
  "type": "message_batch",
  "processing_status": "in_progress",
  "request_counts": {
    "processing": 2,
    "succeeded": 0,
    "errored": 0,
    "canceled": 0,
    "expired": 0
  },
  "ended_at": null,
  "created_at": "2024-09-24T18:37:24.100435Z",
  "expires_at": "2024-09-25T18:37:24.100435Z",
  "cancel_initiated_at": null,
  "results_url": null
}
```
