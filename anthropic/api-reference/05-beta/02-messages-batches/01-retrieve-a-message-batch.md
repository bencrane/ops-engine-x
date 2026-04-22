# Beta - Retrieve a Message Batch

`GET /v1/messages/batches/{message_batch_id}`

This endpoint is idempotent and can be used to poll for Message Batch completion. To access the results of a Message Batch, make a request to the results_url field in the response.

## Path Parameters

- **message_batch_id**: `string` — ID of the Message Batch.

## Header Parameters

- **anthropic-beta**: `array of AnthropicBeta` (optional) — Optional header to specify the beta version(s) you want to use.

## Returns

### BetaMessageBatch

`object { id, archived_at, cancel_initiated_at, created_at, ended_at, expires_at, processing_status, request_counts, results_url, type }`

- **id**: `string` — Unique object identifier. The format and length of IDs may change over time.
- **archived_at**: `string` — RFC 3339 datetime string representing the time at which the Message Batch was archived and its results became unavailable.
- **cancel_initiated_at**: `string` — RFC 3339 datetime string representing the time at which cancellation was initiated for the Message Batch.
- **created_at**: `string` — RFC 3339 datetime string representing the time at which the Message Batch was created.
- **ended_at**: `string` — RFC 3339 datetime string representing the time at which processing for the Message Batch ended. Processing ends when every request in a Message Batch has either succeeded, errored, canceled, or expired.
- **expires_at**: `string` — RFC 3339 datetime string representing the time at which the Message Batch will expire and end processing, which is 24 hours after creation.
- **processing_status**: `"in_progress"` or `"canceling"` or `"ended"` — Processing status of the Message Batch.
- **request_counts**: `BetaMessageBatchRequestCounts` — Tallies requests within the Message Batch, categorized by their status.
  - **canceled**: `number` — Number of requests that have been canceled.
  - **errored**: `number` — Number of requests that encountered an error.
  - **expired**: `number` — Number of requests that have expired.
  - **processing**: `number` — Number of requests that are processing.
  - **succeeded**: `number` — Number of requests that have completed successfully.
- **results_url**: `string` — URL to a .jsonl file containing the results of the Message Batch requests. Results in the file are not guaranteed to be in the same order as requests. Use the custom_id field to match results to requests.
- **type**: `"message_batch"` — Object type. For Message Batches, this is always "message_batch".

## Example Request

```bash
curl https://api.anthropic.com/v1/messages/batches/$MESSAGE_BATCH_ID?beta=true \
  -H 'anthropic-version: 2023-06-01' \
  -H 'anthropic-beta: message-batches-2024-09-24' \
  -H "X-Api-Key: $ANTHROPIC_API_KEY"
```

## Response 200

```json
{
  "id": "msgbatch_013Zva2CMHLNnXjNJJKqJ2EF",
  "archived_at": "2024-08-20T18:37:24.100435Z",
  "cancel_initiated_at": "2024-08-20T18:37:24.100435Z",
  "created_at": "2024-08-20T18:37:24.100435Z",
  "ended_at": "2024-08-20T18:37:24.100435Z",
  "expires_at": "2024-08-20T18:37:24.100435Z",
  "processing_status": "in_progress",
  "request_counts": {
    "canceled": 10,
    "errored": 30,
    "expired": 10,
    "processing": 100,
    "succeeded": 50
  },
  "results_url": "https://api.anthropic.com/v1/messages/batches/msgbatch_013Zva2CMHLNnXjNJJKqJ2EF/results",
  "type": "message_batch"
}
```
