# Beta - List Message Batches

`GET /v1/messages/batches`

List all Message Batches within a Workspace. Most recently created batches are returned first.

## Query Parameters

- **after_id**: `string` (optional) — ID of the object to use as a cursor for pagination. When provided, returns the page of results immediately after this object.
- **before_id**: `string` (optional) — ID of the object to use as a cursor for pagination. When provided, returns the page of results immediately before this object.
- **limit**: `number` (optional) — Number of items to return per page. Defaults to 20. Ranges from 1 to 1000.

## Header Parameters

- **anthropic-beta**: `array of AnthropicBeta` (optional) — Optional header to specify the beta version(s) you want to use.

## Returns

- **data**: `array of BetaMessageBatch` — Array of message batch objects.
- **first_id**: `string` — First ID in the data list. Can be used as the before_id for the previous page.
- **has_more**: `boolean` — Indicates if there are more results in the requested page direction.
- **last_id**: `string` — Last ID in the data list. Can be used as the after_id for the next page.

## Example Request

```bash
curl https://api.anthropic.com/v1/messages/batches?beta=true \
  -H 'anthropic-version: 2023-06-01' \
  -H 'anthropic-beta: message-batches-2024-09-24' \
  -H "X-Api-Key: $ANTHROPIC_API_KEY"
```

## Response 200

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
