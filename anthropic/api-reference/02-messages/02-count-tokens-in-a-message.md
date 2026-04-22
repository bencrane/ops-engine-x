# Count Tokens in a Message

`POST /v1/messages/count_tokens`

Count the number of tokens in a Message, including tools, images, and documents, without creating it.

The Token Count API can be used to count the number of tokens in a Message, including tools, images, and documents, without creating it.

## Body Parameters

### Required Parameters

| Parameter | Type | Description |
|---|---|---|
| `messages` | array of MessageParam | Input messages. Same format as the Create a Message endpoint. |
| `model` | string | The model to use for tokenization (e.g., "claude-opus-4-6"). |

### Optional Parameters

| Parameter | Type | Description |
|---|---|---|
| `system` | string or array | System prompt. |
| `thinking` | object | Configuration for extended thinking. |
| `tool_choice` | object | How the model should use the provided tools. |
| `tools` | array | Definitions of tools that the model may use. |
| `mcp_servers` | array | MCP servers to connect to for tool use. |

The `messages`, `system`, `tools`, `thinking`, `tool_choice`, and `mcp_servers` parameters accept the same format as the Create a Message endpoint.

## Response

Returns a token count object:

| Field | Type | Description |
|---|---|---|
| `input_tokens` | number | The total number of input tokens that would be used by this message. |

## Example Request

```bash
curl https://api.anthropic.com/v1/messages/count_tokens \
    --header "x-api-key: $ANTHROPIC_API_KEY" \
    --header "anthropic-version: 2023-06-01" \
    --header "content-type: application/json" \
    --data '{
        "model": "claude-opus-4-6",
        "messages": [
            {"role": "user", "content": "Hello, world"}
        ]
    }'
```

## Example Response

```json
{
    "input_tokens": 10
}
```

## Notes

- This endpoint uses the same tokenizer as the Messages API, so token counts will be accurate.
- Useful for estimating costs and managing rate limits before sending requests.
- The endpoint counts all input tokens including system prompts, messages, tool definitions, and any other content.
- Images and documents are counted according to the same token counting rules used by the Messages API.

For the complete parameter schemas, see the API reference at https://docs.anthropic.com/en/api/messages/count_tokens.
