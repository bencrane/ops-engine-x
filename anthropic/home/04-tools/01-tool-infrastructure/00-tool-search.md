# Tool search

The tool search tool enables Claude to work with hundreds or thousands of tools by dynamically discovering and loading them on-demand. Instead of loading all tool definitions into the context window upfront, Claude searches your tool catalog and loads only the tools it needs.

This solves two problems:

- **Context bloat**: Tool definitions consume context budget. Tool search typically reduces this by over 85%.
- **Tool selection accuracy**: Degrades significantly past 30-50 tools. Tool search keeps accuracy high across thousands of tools.

Server-side tool search is not covered by ZDR. Custom client-side implementations are ZDR-eligible.

## How tool search works

Two variants available:

- **Regex** (tool_search_tool_regex_20251119): Claude constructs regex patterns
- **BM25** (tool_search_tool_bm25_20251119): Claude uses natural language queries

Flow:
1. Include tool search tool plus tools with `defer_loading: true`
2. Claude sees only the search tool and non-deferred tools initially
3. When Claude needs tools, it searches and gets 3-5 relevant tool_reference blocks
4. References are automatically expanded into full tool definitions
5. Claude selects and invokes discovered tools

## Quick start

```shell
curl https://api.anthropic.com/v1/messages \
  --header "x-api-key: $ANTHROPIC_API_KEY" \
  --header "anthropic-version: 2023-06-01" \
  --header "content-type: application/json" \
  --data '{
    "model": "claude-opus-4-6",
    "max_tokens": 2048,
    "messages": [{"role": "user", "content": "What is the weather in San Francisco?"}],
    "tools": [
      {"type": "tool_search_tool_regex_20251119", "name": "tool_search_tool_regex"},
      {"name": "get_weather", "description": "Get the weather at a specific location", "input_schema": {"type": "object", "properties": {"location": {"type": "string"}}, "required": ["location"]}, "defer_loading": true}
    ]
  }'
```

## Deferred tool loading

Mark tools with `defer_loading: true` for on-demand loading. Keep 3-5 most frequently used tools as non-deferred.

## MCP integration

Works with MCP servers via the "mcp-client-2025-11-20" beta header. Use `mcp_toolset` with `default_config` to defer loading MCP tools.

## Custom tool search implementation

Return `tool_reference` blocks from a custom tool for your own search logic (embeddings, semantic search, etc.). Every referenced tool must have a corresponding definition with `defer_loading: true`.

## Limits and best practices

- Maximum tools: 10,000
- Search results: 3-5 per search
- Pattern length: 200 characters max (regex)
- Model support: Sonnet 4.0+, Opus 4.0+ only (no Haiku)

### Optimization tips

- Keep 3-5 most frequent tools non-deferred
- Use consistent namespacing (e.g., github_, slack_)
- Write clear tool names and descriptions
- Add system prompt describing available tool categories
