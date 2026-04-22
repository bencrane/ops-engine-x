# Create a Message Batch

`POST /v1/messages/batches`

Send a batch of Message creation requests.

The Message Batches API can be used to process multiple Messages API requests at once. Once a Message Batch is created, it begins processing immediately. Batches can take up to 24 hours to complete.

## Body Parameters

### Required Parameters

| Parameter | Type | Description |
|---|---|---|
| `requests` | array of object | List of requests for prompt completion. Each is an individual request to create a Message. |

Each request object contains:

| Field | Type | Description |
|---|---|---|
| `custom_id` | string | Developer-provided ID for each request. Must be unique within the batch. Max length: 64, min length: 1. |
| `params` | object | Messages API creation parameters for the individual request. Same parameters as the Create a Message endpoint (max_tokens, messages, model, etc.). |

## Response

Returns a `MessageBatch` object:

| Field | Type | Description |
|---|---|---|
| `id` | string | Unique object identifier for the batch (e.g., "msgbatch_013Zva2CMHLNnXjNJJKqJ2EF") |
| `type` | string | Always "message_batch" |
| `processing_status` | string | Processing status. Values: "in_progress", "canceling", "ended" |
| `request_counts` | object | Tallies of request statuses within the batch |
| `ended_at` | string or null | RFC 3339 datetime when processing ended |
| `created_at` | string | RFC 3339 datetime when the batch was created |
| `expires_at` | string | RFC 3339 datetime when the batch will expire (results no longer available) |
| `cancel_initiated_at` | string or null | RFC 3339 datetime when cancellation was initiated |
| `results_url` | string or null | URL to retrieve batch results (available when processing has ended) |

### Request Counts Object

| Field | Type | Description |
|---|---|---|
| `processing` | number | Number of requests still processing |
| `succeeded` | number | Number of requests that completed successfully |
| `errored` | number | Number of requests that encountered an error |
| `canceled` | number | Number of requests that were canceled |
| `expired` | number | Number of requests that expired |

## Example Request

```bash
curl https://api.anthropic.com/v1/messages/batches \
    --header "x-api-key: $ANTHROPIC_API_KEY" \
    --header "anthropic-version: 2023-06-01" \
    --header "content-type: application/json" \
    --data '{
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

## Example Response

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

## Notes

- The maximum request size for the Batch API is 256 MB.
- Each batch request uses the same parameters as the standard Messages API.
- Batches offer a 50% cost reduction compared to standard Messages API requests.
- Results may be returned out of order relative to the request order. Use `custom_id` to match results to requests.
