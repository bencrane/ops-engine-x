# Beta - Cancel a Message Batch

`POST /v1/messages/batches/{message_batch_id}/cancel`

Batches may be canceled any time before processing ends. Once cancellation is initiated, the batch enters a canceling state, at which time the system may complete any in-progress, non-interruptible requests before finalizing cancellation.

The number of canceled requests is specified in request_counts. To determine which requests were canceled, check the individual results within the batch. Note that cancellation may not result in any canceled requests if they were non-interruptible.

## Path Parameters

- **message_batch_id**: `string` — ID of the Message Batch.

## Header Parameters

- **anthropic-beta**: `array of AnthropicBeta` (optional) — Optional header to specify the beta version(s) you want to use.

## Returns

Returns a `BetaMessageBatch` object.

## Example Request

```bash
curl https://api.anthropic.com/v1/messages/batches/$MESSAGE_BATCH_ID/cancel?beta=true \
  -X POST \
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
