# Beta - Delete a Message Batch

`DELETE /v1/messages/batches/{message_batch_id}`

Delete a Message Batch.

Message Batches can only be deleted once they've finished processing. If you'd like to delete an in-progress batch, you must first cancel it.

## Path Parameters

- **message_batch_id**: `string` — ID of the Message Batch.

## Header Parameters

- **anthropic-beta**: `array of AnthropicBeta` (optional) — Optional header to specify the beta version(s) you want to use.

## Returns

### BetaDeletedMessageBatch

`object { id, type }`

- **id**: `string` — ID of the Message Batch.
- **type**: `"message_batch_deleted"` — Deleted object type. For Message Batches, this is always "message_batch_deleted".

## Example Request

```bash
curl https://api.anthropic.com/v1/messages/batches/$MESSAGE_BATCH_ID?beta=true \
  -X DELETE \
  -H 'anthropic-version: 2023-06-01' \
  -H 'anthropic-beta: message-batches-2024-09-24' \
  -H "X-Api-Key: $ANTHROPIC_API_KEY"
```

## Response 200

```json
{
  "id": "msgbatch_013Zva2CMHLNnXjNJJKqJ2EF",
  "type": "message_batch_deleted"
}
```
