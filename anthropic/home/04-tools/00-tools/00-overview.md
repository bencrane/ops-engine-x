# Tool use with Claude

Claude is capable of interacting with tools and functions, allowing you to extend Claude's capabilities to perform a wider variety of tasks. Each tool defines a contract: you specify what operations are available and what they return; Claude decides when and how to call them. Tool access is one of the highest-leverage primitives you can give an agent. On benchmarks like LAB-Bench FigQA (scientific figure interpretation) and SWE-bench (real-world software engineering), adding even simple tools produces outsized capability gains, often surpassing human expert baselines.

Structured Outputs provides guaranteed schema validation for tool inputs. Add strict: true to your tool definitions to ensure Claude's tool calls always match your schema exactly, eliminating type mismatches or missing fields.

Here's an example of how to provide tools to Claude using the Messages API:

```shell
curl https://api.anthropic.com/v1/messages \
  -H "content-type: application/json" \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -d '{
    "model": "claude-opus-4-6",
    "max_tokens": 1024,
    "tools": [
      {
        "name": "get_weather",
        "description": "Get the current weather in a given location",
        "input_schema": {
          "type": "object",
          "properties": {
            "location": {
              "type": "string",
              "description": "The city and state, e.g. San Francisco, CA"
            }
          },
          "required": ["location"]
        }
      }
    ],
    "messages": [
      {
        "role": "user",
        "content": "What is the weather like in San Francisco?"
      }
    ]
  }'
```

## How tool use works

Claude supports two types of tools:

- **Client tools**: Tools that execute on your systems, which include:
  - User-defined custom tools that you create and implement
  - Anthropic-defined tools like computer use and text editor that require client implementation
- **Server tools**: Tools that execute on Anthropic's servers, like the web search and web fetch tools. These tools must be specified in the API request but don't require implementation on your part.

Anthropic-defined tools use versioned types (e.g., web_search_20250305, text_editor_20250124) to ensure compatibility across model versions.

### Client tools

Integrate client tools with Claude in these steps:

1. **Provide Claude with tools and a user prompt** - Define client tools with names, descriptions, and input schemas in your API request. Include a user prompt that might require these tools.
2. **Claude decides to use a tool** - Claude assesses if any tools can help with the user's query. If yes, Claude constructs a properly formatted tool use request. For client tools, the API response has a stop_reason of tool_use, signaling Claude's intent.
3. **Execute the tool and return results** - Extract the tool name and input from Claude's request. Execute the tool code on your system. Return the results in a new user message containing a tool_result content block.
4. **Claude uses tool result to formulate a response** - Claude analyzes the tool results to craft its final response to the original user prompt.

Note: Steps 3 and 4 are optional. For some workflows, Claude's tool use request (step 2) might be all you need, without sending results back to Claude.

### Server tools

Server tools follow a different workflow where Anthropic's servers handle tool execution in a loop:

1. **Provide Claude with tools and a user prompt** - Server tools, like web search and web fetch, have their own parameters. Include a user prompt that might require these tools.
2. **Claude executes the server tool** - Claude assesses if a server tool can help with the user's query. If yes, Claude executes the tool, and the results are automatically incorporated into Claude's response. The server runs a sampling loop that may execute multiple tool calls before returning a response.
3. **Claude uses the server tool result to formulate a response** - Claude analyzes the server tool results to craft its final response to the original user prompt.

The server-side sampling loop has a default limit of 10 iterations. If Claude reaches this limit while executing server tools, the API returns a response with stop_reason="pause_turn". When you receive pause_turn, continue the conversation by sending the response back to let Claude finish processing.

## Using MCP tools with Claude

If you're building an application that uses the Model Context Protocol (MCP), you can use tools from MCP servers directly with Claude's Messages API. MCP tool definitions use a schema format that's similar to Claude's tool format. You just need to rename inputSchema to input_schema.

### Converting MCP tools to Claude format

```python
from mcp import ClientSession

async def get_claude_tools(mcp_session: ClientSession):
    """Convert MCP tools to Claude's tool format."""
    mcp_tools = await mcp_session.list_tools()
    claude_tools = []
    for tool in mcp_tools.tools:
        claude_tools.append(
            {
                "name": tool.name,
                "description": tool.description or "",
                "input_schema": tool.inputSchema,
            }
        )
    return claude_tools
```

## Pricing

Tool use requests are priced based on:

- The total number of input tokens sent to the model (including in the tools parameter)
- The number of output tokens generated
- For server-side tools, additional usage-based pricing (e.g., web search charges per search performed)

The additional tokens from tool use come from:

- The tools parameter in API requests (tool names, descriptions, and schemas)
- tool_use content blocks in API requests and responses
- tool_result content blocks in API requests

When you use tools, a special system prompt for the model is automatically included which enables tool use. The number of tool use tokens required for each model are listed below:

| Model | Tool choice | Tool use system prompt token count |
|---|---|---|
| Claude Opus 4.6 | auto, none / any, tool | 346 tokens / 313 tokens |
| Claude Opus 4.5 | auto, none / any, tool | 346 tokens / 313 tokens |
| Claude Opus 4.1 | auto, none / any, tool | 346 tokens / 313 tokens |
| Claude Opus 4 | auto, none / any, tool | 346 tokens / 313 tokens |
| Claude Sonnet 4.6 | auto, none / any, tool | 346 tokens / 313 tokens |
| Claude Sonnet 4.5 | auto, none / any, tool | 346 tokens / 313 tokens |
| Claude Sonnet 4 | auto, none / any, tool | 346 tokens / 313 tokens |
| Claude Haiku 4.5 | auto, none / any, tool | 346 tokens / 313 tokens |
| Claude Haiku 3.5 | auto, none / any, tool | 264 tokens / 340 tokens |
