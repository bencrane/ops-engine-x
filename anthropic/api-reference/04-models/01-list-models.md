# List Models

`GET /v1/models`

List available models.

The Models API response can be used to determine which models are available for use in the API. More recently released models are listed first.

## Query Parameters

- **after_id**: `string` (optional) — ID of the object to use as a cursor for pagination. When provided, returns the page of results immediately after this object.
- **before_id**: `string` (optional) — ID of the object to use as a cursor for pagination. When provided, returns the page of results immediately before this object.
- **limit**: `number` (optional) — Number of items to return per page. Defaults to 20. Ranges from 1 to 1000.

## Header Parameters

- **anthropic-beta**: `array of AnthropicBeta` (optional) — Optional header to specify the beta version(s) you want to use.

## Returns

- **data**: `array of ModelInfo` — Array of model info objects.
  - **id**: `string` — Unique model identifier.
  - **capabilities**: `ModelCapabilities` — Model capability information.
  - **created_at**: `string` — RFC 3339 datetime string representing the time at which the model was released. May be set to an epoch value if the release date is unknown.
  - **display_name**: `string` — A human-readable name for the model.
  - **max_input_tokens**: `number` — Maximum input context window size in tokens for this model.
  - **max_tokens**: `number` — Maximum value for the max_tokens parameter when using this model.
  - **type**: `"model"` — Object type. For Models, this is always "model".
- **first_id**: `string` — First ID in the data list. Can be used as the before_id for the previous page.
- **has_more**: `boolean` — Indicates if there are more results in the requested page direction.
- **last_id**: `string` — Last ID in the data list. Can be used as the after_id for the next page.

## Example Request

```bash
curl https://api.anthropic.com/v1/models \
  -H 'anthropic-version: 2023-06-01' \
  -H "X-Api-Key: $ANTHROPIC_API_KEY"
```

## Response 200

```json
{
  "data": [
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
  ],
  "first_id": "first_id",
  "has_more": true,
  "last_id": "last_id"
}
```
