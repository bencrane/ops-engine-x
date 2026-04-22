# Delete a Message Batch

`DELETE /v1/messages/batches/{message_batch_id}`

Delete a Message Batch.

Message Batches can only be deleted once they've finished processing. If you'd like to delete an in-progress batch, you must first cancel it.

## Path Parameters

| Parameter | Type | Description |
|---|---|---|
| `message_batch_id` | string | ID of the Message Batch. |

## Response

Returns a `DeletedMessageBatch` object:

| Field | Type | Description |
|---|---|---|
| `id` | string | ID of the Message Batch. |
| `type` | string | Always "message_batch_deleted". |

## Example Request

```bash
curl https://api.anthropic.com/v1/messages/batches/$MESSAGE_BATCH_ID \
    -X DELETE \
    -H 'anthropic-version: 2023-06-01' \
    -H "X-Api-Key: $ANTHROPIC_API_KEY"
```

## Example Response

```json
{
    "id": "msgbatch_013Zva2CMHLNnXjNJJKqJ2EF",
    "type": "message_batch_deleted"
}
```
