# Search results

Enable natural citations for RAG applications by providing search results with source attribution.

Search result content blocks enable natural citations with proper source attribution, bringing web search-quality citations to your custom applications. This feature is particularly powerful for RAG (Retrieval-Augmented Generation) applications where you need Claude to cite sources accurately.

The search results feature is available on the following models:

- Claude Opus 4.6 (claude-opus-4-6)
- Claude Sonnet 4.6 (claude-sonnet-4-6)
- Claude Sonnet 4.5 (claude-sonnet-4-5-20250929)
- Claude Opus 4.5 (claude-opus-4-5-20251101)
- Claude Opus 4.1 (claude-opus-4-1-20250805)
- Claude Opus 4 (claude-opus-4-20250514)
- Claude Sonnet 4 (claude-sonnet-4-20250514)
- Claude Sonnet 3.7 (deprecated) (claude-3-7-sonnet-20250219)
- Claude Haiku 4.5 (claude-haiku-4-5-20251001)
- Claude Haiku 3.5 (deprecated) (claude-3-5-haiku-20241022)

## Key benefits

- **Natural citations** - Achieve the same citation quality as web search for any content
- **Flexible integration** - Use in tool returns for dynamic RAG or as top-level content for pre-fetched data
- **Proper source attribution** - Each result includes source and title information for clear attribution
- **No document workarounds needed** - Eliminates the need for document-based workarounds
- **Consistent citation format** - Matches the citation quality and format of Claude's web search functionality

## How it works

Search results can be provided in two ways:

1. **From tool calls** - Your custom tools return search results, enabling dynamic RAG applications
2. **As top-level content** - You provide search results directly in user messages for pre-fetched or cached content

In both cases, Claude can automatically cite information from the search results with proper source attribution.

## Search result schema

Search results use the following structure:

```json
{
  "type": "search_result",
  "source": "https://example.com/article",
  "title": "Article Title",
  "content": [
    {
      "type": "text",
      "text": "The actual content of the search result..."
    }
  ],
  "citations": {
    "enabled": true
  }
}
```

### Required fields

| Field | Type | Description |
|---|---|---|
| type | string | Must be "search_result" |
| source | string | The source URL or identifier for the content |
| title | string | A descriptive title for the search result |
| content | array | An array of text blocks containing the actual content |

### Optional fields

| Field | Type | Description |
|---|---|---|
| citations | object | Citation configuration with enabled boolean field |
| cache_control | object | Cache control settings (e.g., {"type": "ephemeral"}) |

Each item in the content array must be a text block with:
- type: Must be "text"
- text: The actual text content (non-empty string)

## Method 1: Search results from tool calls

The most powerful use case is returning search results from your custom tools. This enables dynamic RAG applications where tools fetch and return relevant content with automatic citations.

### Example: Knowledge base tool

```python
from anthropic.types import (
    MessageParam,
    TextBlockParam,
    SearchResultBlockParam,
    ToolResultBlockParam,
)

client = Anthropic()

# Define a knowledge base search tool
knowledge_base_tool = {
    "name": "search_knowledge_base",
    "description": "Search the company knowledge base for information",
    "input_schema": {
        "type": "object",
        "properties": {"query": {"type": "string", "description": "The search query"}},
        "required": ["query"],
    },
}

# Function to handle the tool call
def search_knowledge_base(query):
    return [
        SearchResultBlockParam(
            type="search_result",
            source="https://docs.company.com/product-guide",
            title="Product Configuration Guide",
            content=[
                TextBlockParam(
                    type="text",
                    text="To configure the product, navigate to Settings > Configuration. The default timeout is 30 seconds, but can be adjusted between 10-120 seconds based on your needs.",
                )
            ],
            citations={"enabled": True},
        ),
    ]
```

## Method 2: Search results as top-level content

You can also provide search results directly in user messages. This is useful for:

- Pre-fetched content from your search infrastructure
- Cached search results from previous queries
- Content from external search services
- Testing and development

### Example: Direct search results

```shell
curl https://api.anthropic.com/v1/messages \
  --header "x-api-key: $ANTHROPIC_API_KEY" \
  --header "anthropic-version: 2023-06-01" \
  --header "content-type: application/json" \
  --data \
'{
  "model": "claude-opus-4-6",
  "max_tokens": 1024,
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "search_result",
          "source": "https://docs.company.com/api-reference",
          "title": "API Reference - Authentication",
          "content": [
            {
              "type": "text",
              "text": "All API requests must include an API key in the Authorization header. Keys can be generated from the dashboard. Rate limits: 1000 requests per hour for standard tier, 10000 for premium."
            }
          ],
          "citations": {
            "enabled": true
          }
        },
        {
          "type": "text",
          "text": "Based on these search results, how do I authenticate API requests and what are the rate limits?"
        }
      ]
    }
  ]
}'
```

## Claude's response with citations

Regardless of how search results are provided, Claude automatically includes citations when using information from them:

```json
{
  "role": "assistant",
  "content": [
    {
      "type": "text",
      "text": "To authenticate API requests, you need to include an API key in the Authorization header",
      "citations": [
        {
          "type": "search_result_location",
          "source": "https://docs.company.com/api-reference",
          "title": "API Reference - Authentication",
          "cited_text": "All API requests must include an API key in the Authorization header",
          "search_result_index": 0,
          "start_block_index": 0,
          "end_block_index": 0
        }
      ]
    }
  ]
}
```

### Citation fields

| Field | Type | Description |
|---|---|---|
| type | string | Always "search_result_location" for search result citations |
| source | string | The source from the original search result |
| title | string or null | The title from the original search result |
| cited_text | string | The exact text being cited |
| search_result_index | integer | Index of the search result (0-based) |
| start_block_index | integer | Starting position in the content array |
| end_block_index | integer | Ending position in the content array |

### Multiple content blocks

Search results can contain multiple text blocks in the content array. Claude can cite specific blocks using the start_block_index and end_block_index fields.

## Advanced usage

### Combining both methods

You can use both tool-based and top-level search results in the same conversation.

### Combining with other content types

Both methods support mixing search results with other content types including images and plain text.

### Cache control

Add cache control for better performance:

```json
{
  "type": "search_result",
  "source": "https://docs.company.com/guide",
  "title": "User Guide",
  "content": [{ "type": "text", "text": "..." }],
  "cache_control": {
    "type": "ephemeral"
  }
}
```

### Citation control

By default, citations are disabled for search results. You can enable citations by explicitly setting the citations configuration:

```json
{
  "type": "search_result",
  "source": "https://docs.company.com/guide",
  "title": "User Guide",
  "content": [{ "type": "text", "text": "Important documentation..." }],
  "citations": {
    "enabled": true
  }
}
```

Citations are all-or-nothing: either all search results in a request must have citations enabled, or all must have them disabled. Mixing search results with different citation settings results in an error.

## Best practices

### For tool-based search (Method 1)
- **Dynamic content**: Use for real-time searches and dynamic RAG applications
- **Error handling**: Return appropriate messages when searches fail
- **Result limits**: Return only the most relevant results to avoid context overflow

### For top-level search (Method 2)
- **Pre-fetched content**: Use when you already have search results
- **Batch processing**: Ideal for processing multiple search results at once
- **Testing**: Great for testing citation behavior with known content

### General best practices
- Use clear, permanent source URLs
- Provide descriptive titles
- Break long content into logical text blocks
- Keep formatting consistent across your application

## Limitations

- Search result content blocks are available on Claude API, Amazon Bedrock, and Google Cloud's Vertex AI
- Only text content is supported within search results (no images or other media)
- The content array must contain at least one text block
