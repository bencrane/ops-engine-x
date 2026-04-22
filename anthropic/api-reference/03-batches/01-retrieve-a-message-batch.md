# Retrieve a Message Batch

`GET /v1/messages/batches/{message_batch_id}`

This endpoint is idempotent and can be used to poll for Message Batch completion. To access the results of a Message Batch, make a request to the `results_url` field in the response.

## Path Parameters

| Parameter | Type | Description |
|---|---|---|
| `message_batch_id` | string | ID of the Message Batch. |

## Response

Returns a `MessageBatch` object:

| Field | Type | Description |
|---|---|---|
| `id` | string | Unique object identifier. |
| `type` | string | Always "message_batch". |
| `processing_status` | string | Processing status: "in_progress", "canceling", or "ended". |
| `request_counts` | object | Tallies of request statuses within the batch. |
| `created_at` | string | RFC 3339 datetime when the batch was created. |
| `ended_at` | string or null | RFC 3339 datetime when processing ended. |
| `expires_at` | string | RFC 3339 datetime when the batch will expire (24 hours after creation). |
| `cancel_initiated_at` | string or null | RFC 3339 datetime when cancellation was initiated. |
| `archived_at` | string or null | RFC 3339 datetime when the batch was archived and results became unavailable. |
| `results_url` | string or null | URL to a .jsonl file containing the results. Available only once processing ends. |

## Example Request

```bash
curl https://api.anthropic.com/v1/messages/batches/$MESSAGE_BATCH_ID \
    -H 'anthropic-version: 2023-06-01' \
    -H "X-Api-Key: $ANTHROPIC_API_KEY"
```

## Example Response

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
