# Beta - Retrieve Message Batch Results

`GET /v1/messages/batches/{message_batch_id}/results`

Streams the results of a Message Batch as a .jsonl file.

Each line in the file is a JSON object containing the result of a single request in the Message Batch. Results are not guaranteed to be in the same order as requests. Use the custom_id field to match results to requests.

## Path Parameters

- **message_batch_id**: `string` — ID of the Message Batch.

## Header Parameters

- **anthropic-beta**: `array of AnthropicBeta` (optional) — Optional header to specify the beta version(s) you want to use.

## Returns

### BetaMessageBatchIndividualResponse

`object { custom_id, result }`

This is a single line in the response .jsonl file and does not represent the response as a whole.

- **custom_id**: `string` — Developer-provided ID created for each request in a Message Batch. Useful for matching results to requests, as results may be given out of request order. Must be unique for each request within the Message Batch.
- **result**: `BetaMessageBatchResult` — Processing result for this request. Contains a Message output if processing was successful, an error response if processing failed, or the reason why processing was not attempted, such as cancellation or expiration.
  - Accepts one of the following:
    - `BetaMessageBatchSucceededResult { message, type }` — type: "succeeded"
    - `BetaMessageBatchErroredResult { error, type }` — type: "errored"
    - `BetaMessageBatchCanceledResult { type }` — type: "canceled"
    - `BetaMessageBatchExpiredResult { type }` — type: "expired"

## Example Request

```bash
curl https://api.anthropic.com/v1/messages/batches/$MESSAGE_BATCH_ID/results?beta=true \
  -H 'anthropic-version: 2023-06-01' \
  -H 'anthropic-beta: message-batches-2024-09-24' \
  -H "X-Api-Key: $ANTHROPIC_API_KEY"
```
