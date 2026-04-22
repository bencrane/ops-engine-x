# Get a Model

`GET /v1/models/{model_id}`

Get a specific model.

The Models API response can be used to determine information about a specific model or resolve a model alias to a model ID.

## Path Parameters

- **model_id**: `string` — Model identifier or alias.

## Header Parameters

- **anthropic-beta**: `array of AnthropicBeta` (optional) — Optional header to specify the beta version(s) you want to use.

## Returns

### ModelInfo

`object { id, capabilities, created_at, display_name, max_input_tokens, max_tokens, type }`

- **id**: `string` — Unique model identifier.
- **capabilities**: `ModelCapabilities` — Model capability information.
  - **batch**: `CapabilitySupport { supported }` — Whether the model supports the Batch API.
  - **citations**: `CapabilitySupport { supported }` — Whether the model supports citation generation.
  - **code_execution**: `CapabilitySupport { supported }` — Whether the model supports code execution tools.
  - **context_management**: `ContextManagementCapability` — Context management support and available strategies.
  - **effort**: `EffortCapability` — Effort (reasoning_effort) support and available levels.
  - **image_input**: `CapabilitySupport { supported }` — Whether the model accepts image content blocks.
  - **pdf_input**: `CapabilitySupport { supported }` — Whether the model accepts PDF content blocks.
  - **structured_outputs**: `CapabilitySupport { supported }` — Whether the model supports structured output / JSON mode / strict tool schemas.
  - **thinking**: `ThinkingCapability { supported, types }` — Thinking capability and supported type configurations.
- **created_at**: `string` — RFC 3339 datetime string representing the time at which the model was released. May be set to an epoch value if the release date is unknown.
- **display_name**: `string` — A human-readable name for the model.
- **max_input_tokens**: `number` — Maximum input context window size in tokens for this model.
- **max_tokens**: `number` — Maximum value for the max_tokens parameter when using this model.
- **type**: `"model"` — Object type. For Models, this is always "model".

## Example Request

```bash
curl https://api.anthropic.com/v1/models/$MODEL_ID \
  -H 'anthropic-version: 2023-06-01' \
  -H "X-Api-Key: $ANTHROPIC_API_KEY"
```

## Response 200

```json
{
  "id": "claude-opus-4-6",
  "capabilities": {
    "batch": {
      "supported": true
    },
    "citations": {
      "supported": true
    },
    "code_execution": {
      "supported": true
    },
    "context_management": {
      "clear_thinking_20251015": {
        "supported": true
      },
      "clear_tool_uses_20250919": {
        "supported": true
      },
      "compact_20260112": {
        "supported": true
      },
      "supported": true
    },
    "effort": {
      "high": {
        "supported": true
      },
      "low": {
        "supported": true
      },
      "max": {
        "supported": true
      },
      "medium": {
        "supported": true
      },
      "supported": true
    },
    "image_input": {
      "supported": true
    },
    "pdf_input": {
      "supported": true
    },
    "structured_outputs": {
      "supported": true
    },
    "thinking": {
      "supported": true,
      "types": {
        "adaptive": {
          "supported": true
        },
        "enabled": {
          "supported": true
        }
      }
    }
  },
  "created_at": "2026-02-04T00:00:00Z",
  "display_name": "Claude Opus 4.6",
  "max_input_tokens": 0,
  "max_tokens": 0,
  "type": "model"
}
```
