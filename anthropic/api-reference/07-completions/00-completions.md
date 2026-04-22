# Completions

## Endpoints

- [Create a Text Completion](/07-completions/01-create-a-text-completion.md) - `POST /v1/complete`

## Models

## Completion Object

```
Completion = object { id, completion, model, stop_reason, type }
```

### Properties

#### id
`string`

Unique object identifier. The format and length of IDs may change over time.

#### completion
`string`

The resulting completion up to and excluding the stop sequences.

#### model
`Model`

The model that will complete your prompt. See models for additional details and options.

Accepts one of the following:

- `"claude-opus-4-6"` - Most intelligent model for building agents and coding
- `"claude-sonnet-4-6"` - Best combination of speed and intelligence
- `"claude-haiku-4-5"` - Fastest model with near-frontier intelligence
- `"claude-haiku-4-5-20251001"` - Fastest model with near-frontier intelligence
- `"claude-opus-4-5"` - Premium model combining maximum intelligence with practical performance
- `"claude-opus-4-5-20251101"` - Premium model combining maximum intelligence with practical performance
- `"claude-sonnet-4-5"` - High-performance model for agents and coding
- `"claude-sonnet-4-5-20250929"` - High-performance model for agents and coding
- `"claude-opus-4-1"` - Exceptional model for specialized complex tasks
- `"claude-opus-4-1-20250805"` - Exceptional model for specialized complex tasks
- `"claude-opus-4-0"` - Powerful model for complex tasks
- `"claude-opus-4-20250514"` - Powerful model for complex tasks
- `"claude-sonnet-4-0"` - High-performance model with extended thinking
- `"claude-sonnet-4-20250514"` - High-performance model with extended thinking
- `"claude-3-haiku-20240307"` - Fast and cost-effective model

#### stop_reason
`string`

The reason that we stopped. This may be one of the following values:

- `"stop_sequence"`: we reached a stop sequence — either provided by you via the `stop_sequences` parameter, or a stop sequence built into the model
- `"max_tokens"`: we exceeded `max_tokens_to_sample` or the model's maximum

#### type
`"completion"`

Object type. For Text Completions, this is always `"completion"`.
