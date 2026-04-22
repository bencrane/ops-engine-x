# Beta - Count Tokens in a Message

`POST /v1/messages/count_tokens`

Count the number of tokens in a Message.

The Token Count API can be used to count the number of tokens in a Message, including tools, images, and documents, without creating it.

## Header Parameters

- **anthropic-beta**: `array of AnthropicBeta` (optional) — Optional header to specify the beta version(s) you want to use.

## Body Parameters (JSON)

- **messages**: `array of BetaMessageParam { content, role }` (required) — Input messages. Our models are trained to operate on alternating user and assistant conversational turns.
  - **content**: `string` or `array of BetaContentBlockParam`
  - **role**: `"user"` or `"assistant"`

- **model**: `string` (required) — The model that will complete your prompt.

- **betas**: `array of AnthropicBeta` (optional) — Optional beta version(s) you want to use.

- **system**: `string` or `array of BetaTextBlockParam` (optional) — System prompt.

- **thinking**: `BetaThinkingConfigEnabled` or `BetaThinkingConfigAdaptive` or `BetaThinkingConfigDisabled` (optional) — Configuration for enabling Claude's extended thinking.

- **tool_choice**: `BetaToolChoiceAuto` or `BetaToolChoiceAny` or `BetaToolChoiceTool` or `BetaToolChoiceNone` (optional) — How the model should use the provided tools.

- **tools**: `array of BetaTool` (optional) — Definitions of tools that the model may use.

## Returns

### BetaTokenCountResponse

`object { input_tokens }`

- **input_tokens**: `number` — The total number of tokens across the provided list of messages, system prompt, and tools.

## Example Request

```bash
curl https://api.anthropic.com/v1/messages/count_tokens \
  -H "content-type: application/json" \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -d '{
    "model": "claude-opus-4-6",
    "messages": [
      {"role": "user", "content": "Hello, world"}
    ]
  }'
```

## Response 200

```json
{
  "input_tokens": 2095
}
```
