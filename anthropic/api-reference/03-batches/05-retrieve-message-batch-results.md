# Retrieve Message Batch Results

`GET /v1/messages/batches/{message_batch_id}/results`

Streams the results of a Message Batch as a `.jsonl` file.

Each line in the file is a JSON object containing the result of a single request in the Message Batch. Results are not guaranteed to be in the same order as requests. Use the `custom_id` field to match results to requests.

## Path Parameters

| Parameter | Type | Description |
|---|---|---|
| `message_batch_id` | string | ID of the Message Batch. |

## Response

Returns a stream of JSONL where each line is a `MessageBatchIndividualResponse` object:

| Field | Type | Description |
|---|---|---|
| `custom_id` | string | Developer-provided ID matching the request. |
| `result` | object | Processing result for this request. |

### Result Types

The `result` field can be one of:

**MessageBatchSucceededResult** (`type: "succeeded"`):
- `message`: A full `Message` object (same as Create a Message response), including `id`, `content`, `model`, `stop_reason`, `usage`, etc.

**MessageBatchErroredResult** (`type: "errored"`):
- `error`: An `ErrorResponse` object containing the error type and message. Error types include: `invalid_request_error`, `authentication_error`, `billing_error`, `permission_error`, `not_found_error`, `rate_limit_error`, `timeout_error`, `api_error`, `overloaded_error`.

**MessageBatchCanceledResult** (`type: "canceled"`):
- No additional fields. The request was canceled before processing.

**MessageBatchExpiredResult** (`type: "expired"`):
- No additional fields. The request expired before processing completed.

## Example Request

```bash
curl https://api.anthropic.com/v1/messages/batches/$MESSAGE_BATCH_ID/results \
    -H 'anthropic-version: 2023-06-01' \
    -H "X-Api-Key: $ANTHROPIC_API_KEY"
```

## Example Response (JSONL)

Each line is a separate JSON object:

```json
{"custom_id":"my-first-request","result":{"type":"succeeded","message":{"id":"msg_01...","type":"message","role":"assistant","content":[{"type":"text","text":"Hello!"}],"model":"claude-opus-4-6","stop_reason":"end_turn","usage":{"input_tokens":12,"output_tokens":6}}}}
{"custom_id":"my-second-request","result":{"type":"succeeded","message":{"id":"msg_02...","type":"message","role":"assistant","content":[{"type":"text","text":"Hi again!"}],"model":"claude-opus-4-6","stop_reason":"end_turn","usage":{"input_tokens":14,"output_tokens":5}}}}
```

## Notes

- Results are streamed as JSONL, meaning each line is a complete, independent JSON object.
- Results may be returned in any order. Always use `custom_id` to match results to your original requests.
- The `message` field in succeeded results contains the full Message object, identical to what the standard Messages API would return.
- This endpoint is only available after the batch has finished processing (`processing_status` is "ended").
