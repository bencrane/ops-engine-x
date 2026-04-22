# List Message Batches

`GET /v1/messages/batches`

List all Message Batches within a Workspace. Most recently created batches are returned first.

## Query Parameters

| Parameter | Type | Description |
|---|---|---|
| `after_id` | optional string | ID of the object to use as a cursor for pagination. Returns the page of results immediately after this object. |
| `before_id` | optional string | ID of the object to use as a cursor for pagination. Returns the page of results immediately before this object. |
| `limit` | optional number | Number of items to return per page. Defaults to 20. Ranges from 1 to 1000. |

## Response

Returns a paginated list of `MessageBatch` objects:

| Field | Type | Description |
|---|---|---|
| `data` | array of MessageBatch | Array of message batch objects. |
| `first_id` | string | First ID in the data list. Can be used as the `before_id` for the previous page. |
| `last_id` | string | Last ID in the data list. Can be used as the `after_id` for the next page. |
| `has_more` | boolean | Indicates if there are more results in the requested page direction. |

## Example Request

```bash
curl https://api.anthropic.com/v1/messages/batches \
    -H 'anthropic-version: 2023-06-01' \
    -H "X-Api-Key: $ANTHROPIC_API_KEY"
```

## Example Response

```json
{
    "data": [
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
    ],
    "first_id": "first_id",
    "has_more": true,
    "last_id": "last_id"
}
```
