# Handling stop reasons

When you make a request to the Messages API, Claude's response includes a `stop_reason` field that indicates why the model stopped generating its response. Understanding these values is crucial for building robust applications that handle different response types appropriately.

For details about `stop_reason` in the API response, see the Messages API reference.

## The stop_reason field

The `stop_reason` field is part of every successful Messages API response. Unlike errors, which indicate failures in processing your request, `stop_reason` tells you why Claude successfully completed its response generation.

Example response:

```json
{
  "id": "msg_01234",
  "type": "message",
  "role": "assistant",
  "content": [
    {
      "type": "text",
      "text": "Here's the answer to your question..."
    }
  ],
  "stop_reason": "end_turn",
  "stop_sequence": null,
  "usage": {
    "input_tokens": 100,
    "output_tokens": 50
  }
}
```

## Stop reason values

### end_turn

The most common stop reason. Indicates Claude finished its response naturally.

```python
from anthropic import Anthropic

client = Anthropic()
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello!"}],
)
if response.stop_reason == "end_turn":
    # Process the complete response
    print(response.content[0].text)
```

#### Empty responses with end_turn

Sometimes Claude returns an empty response (exactly 2-3 tokens with no content) with `stop_reason: "end_turn"`. This typically happens when Claude interprets that the assistant turn is complete, particularly after tool results.

Common causes:

- Adding text blocks immediately after tool results (Claude learns to expect the user to always insert text after tool results, so it ends its turn to follow the pattern)
- Sending Claude's completed response back without adding anything (Claude already decided it's done, so it will remain done)

How to prevent empty responses:

```python
# INCORRECT: Adding text immediately after tool_result
messages = [
    {"role": "user", "content": "Calculate the sum of 1234 and 5678"},
    {
        "role": "assistant",
        "content": [
            {
                "type": "tool_use",
                "id": "toolu_123",
                "name": "calculator",
                "input": {"operation": "add", "a": 1234, "b": 5678},
            }
        ],
    },
    {
        "role": "user",
        "content": [
            {"type": "tool_result", "tool_use_id": "toolu_123", "content": "6912"},
            {
                "type": "text",
                "text": "Here's the result",  # Don't add text after tool_result
            },
        ],
    },
]

# CORRECT: Send tool results directly without additional text
messages = [
    {"role": "user", "content": "Calculate the sum of 1234 and 5678"},
    {
        "role": "assistant",
        "content": [
            {
                "type": "tool_use",
                "id": "toolu_123",
                "name": "calculator",
                "input": {"operation": "add", "a": 1234, "b": 5678},
            }
        ],
    },
    {
        "role": "user",
        "content": [
            {"type": "tool_result", "tool_use_id": "toolu_123", "content": "6912"}
        ],
    },  # Just the tool_result, no additional text
]
```

Best practices:

- Never add text blocks immediately after tool results - This teaches Claude to expect user input after every tool use
- Don't retry empty responses without modification - Simply sending the empty response back won't help
- Use continuation prompts as a last resort - Only if the above fixes don't resolve the issue

### max_tokens

Claude stopped because it reached the `max_tokens` limit specified in your request.

```python
response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=10,
    messages=[{"role": "user", "content": "Explain quantum physics"}],
)
if response.stop_reason == "max_tokens":
    print("Response was cut off at token limit")
```

### stop_sequence

Claude encountered one of your custom stop sequences.

```python
response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    stop_sequences=["END", "STOP"],
    messages=[{"role": "user", "content": "Generate text until you say END"}],
)
if response.stop_reason == "stop_sequence":
    print(f"Stopped at sequence: {response.stop_sequence}")
```

### tool_use

Claude is calling a tool and expects you to execute it.

For most tool use implementations, we recommend using the tool runner which automatically handles tool execution, result formatting, and conversation management.

```python
from anthropic import Anthropic

client = Anthropic()

weather_tool = {
    "name": "get_weather",
    "description": "Get the current weather in a given location",
    "input_schema": {
        "type": "object",
        "properties": {
            "location": {"type": "string", "description": "City and state"},
        },
        "required": ["location"],
    },
}

def execute_tool(name, tool_input):
    """Execute a tool and return the result."""
    return f"Weather in {tool_input.get('location', 'unknown')}: 72°F"

response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    tools=[weather_tool],
    messages=[{"role": "user", "content": "What's the weather?"}],
)
if response.stop_reason == "tool_use":
    for content in response.content:
        if content.type == "tool_use":
            result = execute_tool(content.name, content.input)
```

### pause_turn

Returned when the server-side sampling loop reaches its iteration limit while executing server tools like web search or web fetch. The default limit is 10 iterations per request.

When this happens, the response may contain a `server_tool_use` block without a corresponding `server_tool_result`. To let Claude finish processing, continue the conversation by sending the response back as-is.

```python
response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    tools=[{"type": "web_search_20250305", "name": "web_search"}],
    messages=[{"role": "user", "content": "Search for latest AI news"}],
)
if response.stop_reason == "pause_turn":
    messages = [
        {"role": "user", "content": original_query},
        {"role": "assistant", "content": response.content},
    ]
    continuation = client.messages.create(
        model="claude-opus-4-6",
        messages=messages,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
    )
```

Your application should handle `pause_turn` in any agent loop that uses server tools. Simply add the assistant's response to your messages array and make another API request to let Claude continue.

### refusal

Claude refused to generate a response due to safety concerns.

```python
response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": "[Unsafe request]"}],
)
if response.stop_reason == "refusal":
    print("Claude was unable to process this request")
```

If you encounter refusal stop reasons frequently while using Claude Sonnet 4.5 or Opus 4.1, you can try updating your API calls to use Sonnet 4 (`claude-sonnet-4-20250514`), which has different usage restrictions.

### model_context_window_exceeded

Claude stopped because it reached the model's context window limit. This allows you to request the maximum possible tokens without knowing the exact input size.

```python
response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=64000,
    messages=[
        {"role": "user", "content": "Large input that uses most of context window..."}
    ],
)
if response.stop_reason == "model_context_window_exceeded":
    print("Response reached model's context window limit")
```

This stop reason is available by default in Sonnet 4.5 and newer models. For earlier models, use the beta header `model-context-window-exceeded-2025-08-26` to enable this behavior.

## Best practices for handling stop reasons

### 1. Always check stop_reason

```python
def handle_response(response):
    if response.stop_reason == "tool_use":
        return handle_tool_use(response)
    elif response.stop_reason == "max_tokens":
        return handle_truncation(response)
    elif response.stop_reason == "model_context_window_exceeded":
        return handle_context_limit(response)
    elif response.stop_reason == "pause_turn":
        return handle_pause(response)
    elif response.stop_reason == "refusal":
        return handle_refusal(response)
    else:
        return response.content[0].text
```

### 2. Handle truncated responses gracefully

```python
def handle_truncated_response(response):
    if response.stop_reason in ["max_tokens", "model_context_window_exceeded"]:
        if response.stop_reason == "max_tokens":
            message = "[Response truncated due to max_tokens limit]"
        else:
            message = "[Response truncated due to context window limit]"
        return f"{response.content[0].text}\n\n{message}"
```

### 3. Implement retry logic for pause_turn

```python
def handle_server_tool_conversation(client, user_query, tools, max_continuations=5):
    messages = [{"role": "user", "content": user_query}]
    for _ in range(max_continuations):
        response = client.messages.create(
            model="claude-opus-4-6", messages=messages, tools=tools
        )
        if response.stop_reason != "pause_turn":
            return response
        messages = [
            {"role": "user", "content": user_query},
            {"role": "assistant", "content": response.content},
        ]
    return response
```

## Stop reasons vs. errors

It's important to distinguish between `stop_reason` values and actual errors:

**Stop reasons (successful responses):**
- Part of the response body
- Indicate why generation stopped normally
- Response contains valid content

**Errors (failed requests):**
- HTTP status codes 4xx or 5xx
- Indicate request processing failures
- Response contains error details

```python
import anthropic
from anthropic import Anthropic

client = Anthropic()
try:
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[{"role": "user", "content": "Hello!"}],
    )
    if response.stop_reason == "max_tokens":
        print("Response was truncated")
except anthropic.APIError as e:
    if e.status_code == 429:
        print("Rate limit exceeded")
    elif e.status_code == 500:
        print("Server error")
```

## Streaming considerations

When using streaming, `stop_reason` is:

- `null` in the initial `message_start` event
- Provided in the `message_delta` event
- Not provided in any other events

```python
from anthropic import Anthropic

client = Anthropic()
with client.messages.stream(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello!"}],
) as stream:
    for event in stream:
        if event.type == "message_delta":
            stop_reason = event.delta.stop_reason
            if stop_reason:
                print(f"Stream ended with: {stop_reason}")
```

## Common patterns

### Handling tool use workflows

```python
def complete_tool_workflow(client, user_query, tools):
    messages = [{"role": "user", "content": user_query}]
    while True:
        response = client.messages.create(
            model="claude-opus-4-6", messages=messages, tools=tools
        )
        if response.stop_reason == "tool_use":
            tool_results = execute_tools(response.content)
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})
        else:
            return response
```

### Ensuring complete responses

```python
def get_complete_response(client, prompt, max_attempts=3):
    messages = [{"role": "user", "content": prompt}]
    full_response = ""
    for _ in range(max_attempts):
        response = client.messages.create(
            model="claude-opus-4-6", messages=messages, max_tokens=4096
        )
        full_response += response.content[0].text
        if response.stop_reason != "max_tokens":
            break
        messages = [
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": full_response},
            {"role": "user", "content": "Please continue from where you left off."},
        ]
    return full_response
```

### Getting maximum tokens without knowing input size

```python
def get_max_possible_tokens(client, prompt):
    response = client.messages.create(
        model="claude-opus-4-6",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=64000,
    )
    if response.stop_reason == "model_context_window_exceeded":
        print(f"Generated {response.usage.output_tokens} tokens (context limit reached)")
    elif response.stop_reason == "max_tokens":
        print(f"Generated {response.usage.output_tokens} tokens (max_tokens reached)")
    else:
        print(f"Generated {response.usage.output_tokens} tokens (natural completion)")
    return response.content[0].text
```

By properly handling `stop_reason` values, you can build more robust applications that gracefully handle different response scenarios and provide better user experiences.
