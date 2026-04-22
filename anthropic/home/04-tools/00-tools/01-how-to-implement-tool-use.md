# How to implement tool use

## Choosing a model

- Use the latest Claude Opus (4.6) model for complex tools and ambiguous queries; it handles multiple tools better and seeks clarification when needed.
- Use Claude Haiku models for straightforward tools, but note they may infer missing parameters.
- If using Claude with tool use and extended thinking, refer to the extended thinking guide for more information.

## Specifying client tools

Client tools (both Anthropic-defined and user-defined) are specified in the tools top-level parameter of the API request. Each tool definition includes:

| Parameter | Description |
|---|---|
| name | The name of the tool. Must match the regex ^[a-zA-Z0-9_-]{1,64}$. |
| description | A detailed plaintext description of what the tool does, when it should be used, and how it behaves. |
| input_schema | A JSON Schema object defining the expected parameters for the tool. |
| input_examples | (Optional) An array of example input objects to help Claude understand how to use the tool. |

### Tool use system prompt

When you call the Claude API with the tools parameter, the API constructs a special system prompt from the tool definitions, tool configuration, and any user-specified system prompt.

### Best practices for tool definitions

To get the best performance out of Claude when using tools, follow these guidelines:

- **Provide extremely detailed descriptions.** This is by far the most important factor in tool performance. Your descriptions should explain every detail about the tool. Aim for at least 3-4 sentences per tool description, more if the tool is complex.
- **Prioritize descriptions, but consider using input_examples for complex tools.** Clear descriptions are most important, but for tools with complex inputs, nested objects, or format-sensitive parameters, you can use the input_examples field.
- **Consolidate related operations into fewer tools.** Rather than creating a separate tool for every action, group them into a single tool with an action parameter.
- **Use meaningful namespacing in tool names.** When your tools span multiple services or resources, prefix names with the service (e.g., github_list_prs, slack_send_message).
- **Design tool responses to return only high-signal information.** Return semantic, stable identifiers rather than opaque internal references, and include only the fields Claude needs to reason about its next step.

### Providing tool use examples

You can provide concrete examples of valid tool inputs to help Claude understand how to use your tools more effectively. Add an optional input_examples field to your tool definition with an array of example input objects. Each example must be valid according to the tool's input_schema.

Requirements and limitations:
- Schema validation - Each example must be valid according to the tool's input_schema. Invalid examples return a 400 error
- Not supported for server-side tools - Only user-defined tools can have input examples
- Token cost - Examples add to prompt tokens: ~20-50 tokens for simple examples, ~100-200 tokens for complex nested objects

## Tool runner (beta)

The tool runner provides an out-of-the-box solution for executing tools with Claude. Instead of manually handling tool calls, tool results, and conversation management, the tool runner automatically:

- Executes tools when Claude calls them
- Handles the request/response cycle
- Manages conversation state
- Provides type safety and validation

The tool runner is currently in beta and available in the Python, TypeScript, and Ruby SDKs. The tool runner supports automatic compaction, which generates summaries when token usage exceeds a threshold.

### Basic usage

Define tools using the SDK helpers, then use the tool runner to execute them:

```python
import anthropic
import json
from anthropic import beta_tool

client = anthropic.Anthropic()

@beta_tool
def get_weather(location: str, unit: str = "fahrenheit") -> str:
    """Get the current weather in a given location.
    Args:
        location: The city and state, e.g. San Francisco, CA
        unit: Temperature unit, either 'celsius' or 'fahrenheit'
    """
    return json.dumps({"temperature": "20°C", "condition": "Sunny"})

runner = client.beta.messages.tool_runner(
    model="claude-opus-4-6",
    max_tokens=1024,
    tools=[get_weather],
    messages=[{"role": "user", "content": "What's the weather like in Paris?"}],
)

for message in runner:
    print(message.content[0].text)
```

### Iterating over the tool runner

The tool runner is an iterable that yields messages from Claude. Each iteration, the runner checks if Claude requested a tool use. If so, it calls the tool and sends the result back automatically.

If you don't need intermediate messages, you can get the final message directly with `runner.until_done()`.

### Streaming

Enable streaming to receive events as they arrive:

```python
runner = client.beta.messages.tool_runner(
    model="claude-opus-4-6",
    max_tokens=1024,
    tools=[calculate_sum],
    messages=[{"role": "user", "content": "What is 15 + 27?"}],
    stream=True,
)

for message_stream in runner:
    for event in message_stream:
        print("event:", event)
```

## Controlling Claude's output

### Forcing tool use

You can force Claude to use a specific tool by specifying the tool in the tool_choice field:

- **auto** allows Claude to decide whether to call any provided tools or not. This is the default value when tools are provided.
- **any** tells Claude that it must use one of the provided tools, but doesn't force a particular tool.
- **tool** forces Claude to always use a particular tool.
- **none** prevents Claude from using any tools. This is the default value when no tools are provided.

When using extended thinking with tool use, tool_choice: {"type": "any"} and tool_choice: {"type": "tool", "name": "..."} are not supported and will result in an error. Only tool_choice: {"type": "auto"} (the default) and tool_choice: {"type": "none"} are compatible with extended thinking.

### JSON output

Tools do not necessarily need to be client functions. You can use tools anytime you want the model to return JSON output that follows a provided schema.

### Model responses with tools

When using tools, Claude will often comment on what it's doing or respond naturally to the user before invoking tools.

### Parallel tool use

By default, Claude may use multiple tools to answer a user query. You can disable this behavior by setting disable_parallel_tool_use=true.

## Handling tool use and tool result content blocks

### Handling results from client tools

The response will have a stop_reason of tool_use and one or more tool_use content blocks that include:

- **id**: A unique identifier for this particular tool use block.
- **name**: The name of the tool being used.
- **input**: An object containing the input being passed to the tool, conforming to the tool's input_schema.

When you receive a tool use response, you should:

1. Extract the name, id, and input from the tool_use block.
2. Run the actual tool in your codebase corresponding to that tool name.
3. Continue the conversation by sending a new message with the role of user, and a content block containing the tool_result type.

Important formatting requirements:
- Tool result blocks must immediately follow their corresponding tool use blocks in the message history.
- In the user message containing tool results, the tool_result blocks must come FIRST in the content array. Any text must come AFTER all tool results.

### Handling results from server tools

Claude executes the tool internally and incorporates the results directly into its response without requiring additional user interaction.

### Handling the max_tokens stop reason

If Claude's response is cut off due to hitting the max_tokens limit, and the truncated response contains an incomplete tool use block, you'll need to retry the request with a higher max_tokens value.

### Handling the pause_turn stop reason

When using server tools like web search, the API may return a pause_turn stop reason, indicating that the API has paused a long-running turn. Continue the conversation by passing the paused response back as-is in a subsequent request.

## Troubleshooting errors

Common error types when using tools with Claude include:
- Tool execution errors
- Invalid tool names
- search_quality_reflection tags
- Server tool errors
- Parallel tool calls not working
