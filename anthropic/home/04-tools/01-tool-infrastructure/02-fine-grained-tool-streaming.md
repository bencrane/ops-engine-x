# Fine-grained tool streaming

Fine-grained tool streaming is generally available on all models and all platforms, with no beta header required. It enables streaming of tool use parameter values without buffering or JSON validation, reducing the latency to begin receiving large parameters.

When using fine-grained tool streaming, you may potentially receive invalid or partial JSON inputs. Make sure to account for these edge cases in your code.

## How to use fine-grained tool streaming

To use it, set `eager_input_streaming` to true on any tool where you want fine-grained streaming enabled, and enable streaming on your request.

```shell
curl https://api.anthropic.com/v1/messages \
  -H "content-type: application/json" \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -d '{
    "model": "claude-opus-4-6",
    "max_tokens": 65536,
    "tools": [
      {
        "name": "make_file",
        "description": "Write text to a file",
        "eager_input_streaming": true,
        "input_schema": {
          "type": "object",
          "properties": {
            "filename": {
              "type": "string",
              "description": "The filename to write text to"
            },
            "lines_of_text": {
              "type": "array",
              "description": "An array of lines of text to write to the file"
            }
          },
          "required": ["filename", "lines_of_text"]
        }
      }
    ],
    "messages": [
      {
        "role": "user",
        "content": "Can you write a long poem and make a file called poem.txt?"
      }
    ],
    "stream": true
  }'
```

With fine-grained tool streaming, tool use chunks start streaming faster and are often longer with fewer word breaks due to differences in chunking behavior.

Example comparison:

Without fine-grained streaming (15s delay):
```
Chunk 1: '{"'
Chunk 2: 'query": "Ty'
Chunk 3: 'peScri'
...
```

With fine-grained streaming (3s delay):
```
Chunk 1: '{"query": "TypeScript 5.0 5.1 5.2 5.3'
Chunk 2: ' new features comparison'
```

Because fine-grained streaming sends parameters without buffering or JSON validation, there is no guarantee that the resulting stream will complete in a valid JSON string. If the stop reason max_tokens is reached, the stream may end midway through a parameter. You generally have to write specific support to handle when max_tokens is reached.

## Handling invalid JSON in tool responses

When using fine-grained tool streaming, you may receive invalid or incomplete JSON. If you need to pass this back to the model in an error response block, wrap it in a JSON object:

```json
{
  "INVALID_JSON": "<your invalid json string>"
}
```

This helps the model understand the content is invalid JSON while preserving the original data for debugging. Make sure to properly escape quotes or special characters in the invalid JSON string.
