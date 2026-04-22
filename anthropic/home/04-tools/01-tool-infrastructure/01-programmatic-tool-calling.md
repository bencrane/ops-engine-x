# Programmatic tool calling

Programmatic tool calling allows Claude to write code that calls your tools programmatically within a code execution container, rather than requiring round trips through the model for each tool invocation. This reduces latency for multi-tool workflows and decreases token consumption by allowing Claude to filter or process data before it reaches the model's context window.

This feature requires the code execution tool. Not eligible for ZDR.

## Model compatibility

Available on Claude Opus 4.6, Sonnet 4.6, Sonnet 4.5, and Opus 4.5 with tool version code_execution_20260120. Available via Claude API and Microsoft Foundry.

## Quick start

```shell
curl https://api.anthropic.com/v1/messages \
  --header "x-api-key: $ANTHROPIC_API_KEY" \
  --header "anthropic-version: 2023-06-01" \
  --header "content-type: application/json" \
  --data '{
    "model": "claude-opus-4-6",
    "max_tokens": 4096,
    "messages": [{"role": "user", "content": "Query sales data for West, East, and Central regions"}],
    "tools": [
      {"type": "code_execution_20260120", "name": "code_execution"},
      {"name": "query_database", "description": "Execute a SQL query. Returns JSON rows.", "input_schema": {"type": "object", "properties": {"sql": {"type": "string"}}, "required": ["sql"]}, "allowed_callers": ["code_execution_20260120"]}
    ]
  }'
```

## How it works

1. Claude writes Python code that invokes tools as functions
2. Code runs in sandboxed container via code execution
3. When tool function is called, execution pauses and API returns a tool_use block
4. You provide the tool result, execution continues
5. Once complete, Claude receives final output

## Core concepts

### The allowed_callers field

- `["direct"]` - Only Claude can call directly (default)
- `["code_execution_20260120"]` - Only callable from code execution
- `["direct", "code_execution_20260120"]` - Both modes

### The caller field in responses

Every tool_use block includes a `caller` field indicating how it was invoked (direct or from code execution).

### Container lifecycle

Containers expire after ~4.5 minutes of inactivity. Reuse containers via the container ID.

## Advanced patterns

- **Batch processing**: Loop through items, call tools in sequence, aggregate results
- **Early termination**: Stop processing when success criteria met
- **Conditional tool selection**: Choose tools based on intermediate results
- **Data filtering**: Process large datasets, return only relevant items

## Token efficiency

- Tool results from programmatic calls are not added to Claude's context
- Intermediate processing happens in code
- Multiple tool calls in one execution reduces overhead
- 10 tools programmatically uses ~1/10th the tokens of 10 direct calls

## Constraints

- Not compatible with strict: true tools
- Cannot force via tool_choice
- disable_parallel_tool_use not supported
- MCP connector tools cannot be called programmatically (yet)
- When responding to programmatic tool calls, messages must contain only tool_result blocks (no text)

## Best practices

- Provide detailed output format descriptions in tool definitions
- Return structured data (JSON) for easy programmatic processing
- Reuse containers for related requests
- Use for 3+ dependent tool calls, large dataset processing, or parallel operations
