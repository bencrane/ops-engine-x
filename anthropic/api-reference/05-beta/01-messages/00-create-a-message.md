# Beta - Create a Message

`POST /v1/messages`

Send a structured list of input messages with text and/or image content, and the model will generate the next message in the conversation.

The Messages API can be used for either single queries or stateless multi-turn conversations.

## Header Parameters

- **anthropic-beta**: `array of AnthropicBeta` (optional) — Optional header to specify the beta version(s) you want to use.

## Body Parameters (JSON)

- **max_tokens**: `number` (required) — The maximum number of tokens to generate before stopping. Note that our models may stop before reaching this maximum. This parameter only specifies the absolute maximum number of tokens to generate. Different models have different maximum values for this parameter. See models for details. Minimum: 1.

- **messages**: `array of BetaMessageParam { content, role }` (required) — Input messages. Our models are trained to operate on alternating user and assistant conversational turns. When creating a new Message, you specify the prior conversational turns with the messages parameter, and the model then generates the next Message in the conversation. Consecutive user or assistant turns in your request will be combined into a single turn.

  Each input message must be an object with a role and content. You can specify a single user-role message, or you can include multiple user and assistant messages.

  If the final message uses the assistant role, the response content will continue immediately from the content in that message. This can be used to constrain part of the model's response.

  Example with a single user message:
  ```json
  [{"role": "user", "content": "Hello, Claude"}]
  ```

  Example with multiple conversational turns:
  ```json
  [
    {"role": "user", "content": "Hello there."},
    {"role": "assistant", "content": "Hi, I'm Claude. How can I help you?"},
    {"role": "user", "content": "Can you explain LLMs in plain English?"}
  ]
  ```

  Each input message content may be either a single string or an array of content blocks, where each block has a specific type. Using a string for content is shorthand for an array of one content block of type "text".

  Note that if you want to include a system prompt, you can use the top-level system parameter -- there is no "system" role for input messages in the Messages API.

  There is a limit of 100,000 messages in a single request.

  - **content**: `string` or `array of BetaContentBlockParam` — Accepts one of the following:
    - `string`
    - `array of BetaContentBlockParam` (BetaTextBlockParam, BetaImageBlockParam, BetaRequestDocumentBlock, BetaToolUseBlockParam, BetaToolResultBlockParam, BetaCodeExecutionToolResultBlockParam, BetaBashCodeExecutionToolResultBlockParam)
  - **role**: `"user"` or `"assistant"`

- **model**: `string` (required) — The model that will complete your prompt. See models for additional details and options.

- **betas**: `array of AnthropicBeta` (optional) — Optional beta version(s) you want to use.

- **citations**: `BetaCitationsConfigParam { enabled }` (optional) — Configuration for citation generation.
  - **enabled**: `boolean` (optional)

- **context_management**: `object` (optional) — Context management configuration with edits array.

- **metadata**: `BetaMetadata { user_id }` (optional) — An object describing metadata about the request.
  - **user_id**: `string` (optional) — An external identifier for the user who is associated with the request.

- **reasoning_effort**: `"low"` or `"medium"` or `"high"` or `"max"` (optional) — Defaults to "high". How much effort to spend on reasoning before responding.

- **service_tier**: `"auto"` or `"standard_only"` (optional) — Defaults to "auto". Determines whether to use Priority Tier.

- **stop_sequences**: `array of string` (optional) — Custom text sequences that will cause the model to stop generating.

- **stream**: `boolean` (optional) — Whether to incrementally stream the response using server-sent events.

- **system**: `string` or `array of BetaTextBlockParam` (optional) — System prompt. A system prompt is a way of providing context and instructions to Claude.

- **temperature**: `number` (optional) — Defaults to 1.0. Amount of randomness injected into the response. Ranges from 0.0 to 1.0.

- **thinking**: `BetaThinkingConfigEnabled` or `BetaThinkingConfigAdaptive` or `BetaThinkingConfigDisabled` (optional) — Configuration for enabling Claude's extended thinking.

- **tool_choice**: `BetaToolChoiceAuto` or `BetaToolChoiceAny` or `BetaToolChoiceTool` or `BetaToolChoiceNone` (optional) — How the model should use the provided tools.

- **tools**: `array of BetaTool` (optional) — Definitions of tools that the model may use.

- **top_k**: `number` (optional) — Only sample from the top K options for each subsequent token. Used to remove "long tail" low probability responses.

- **top_p**: `number` (optional) — Use nucleus sampling. We generally recommend altering temperature instead.

## Returns

### BetaMessage

`object { id, content, model, role, stop_reason, stop_sequence, type, usage }`

- **id**: `string` — Unique object identifier.
- **content**: `array of BetaContentBlock` — Content generated by the model. Array of content blocks, each of which has a type that determines its shape.
- **model**: `string` — The model that handled the request.
- **role**: `"assistant"` — Conversational role of the generated message. This will always be "assistant".
- **stop_reason**: `"end_turn"` or `"max_tokens"` or `"stop_sequence"` or `"tool_use"` or `"pause_turn"` or `null` — The reason that we stopped.
- **stop_sequence**: `string` or `null` — Which custom stop sequence was generated, if any.
- **type**: `"message"` — Object type. For Messages, this is always "message".
- **usage**: `BetaUsage` — Billing and rate-limit usage.
  - **cache_creation_input_tokens**: `number` — The number of input tokens used to create the cache entry.
  - **cache_read_input_tokens**: `number` — The number of input tokens read from the cache.
  - **input_tokens**: `number` — The number of input tokens which were used.
  - **output_tokens**: `number` — The number of output tokens which were used.
  - **service_tier**: `string` — The service tier used for this request.

## Example Request

```bash
curl https://api.anthropic.com/v1/messages \
  -H "content-type: application/json" \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -d '{
    "model": "claude-opus-4-6",
    "max_tokens": 1024,
    "messages": [
      {"role": "user", "content": "Hello, world"}
    ]
  }'
```

## Response 200

```json
{
  "id": "msg_01XFDUDYJgAACzvnptvVoYEL",
  "type": "message",
  "role": "assistant",
  "content": [
    {
      "type": "text",
      "text": "Hello! How can I help you today?"
    }
  ],
  "model": "claude-opus-4-6",
  "stop_reason": "end_turn",
  "stop_sequence": null,
  "usage": {
    "input_tokens": 25,
    "output_tokens": 13,
    "cache_creation_input_tokens": 0,
    "cache_read_input_tokens": 0
  }
}
```
