# Web search tool

The web search tool gives Claude direct access to real-time web content, allowing it to answer questions with up-to-date information beyond its knowledge cutoff. Claude automatically cites sources from search results as part of its answer.

The latest web search tool version (web_search_20260209) supports dynamic filtering with Claude Opus 4.6 and Sonnet 4.6. Claude can write and execute code to filter search results before they reach the context window, keeping only relevant information and discarding the rest. This leads to more accurate responses while reducing token consumption. The previous tool version (web_search_20250305) remains available without dynamic filtering.

The basic web search tool (web_search_20250305) is eligible for Zero Data Retention (ZDR). The web_search_20260209 version with dynamic filtering is not ZDR-eligible by default because dynamic filtering relies on code execution internally. To use web_search_20260209 with ZDR, disable dynamic filtering by setting "allowed_callers": ["direct"] on the tool.

## Supported models

Web search is available on:

- Claude Opus 4.6 (claude-opus-4-6)
- Claude Opus 4.5 (claude-opus-4-5-20251101)
- Claude Opus 4.1 (claude-opus-4-1-20250805)
- Claude Opus 4 (claude-opus-4-20250514)
- Claude Sonnet 4.6 (claude-sonnet-4-6)
- Claude Sonnet 4.5 (claude-sonnet-4-5-20250929)
- Claude Sonnet 4 (claude-sonnet-4-20250514)
- Claude Sonnet 3.7 (deprecated) (claude-3-7-sonnet-20250219)
- Claude Haiku 4.5 (claude-haiku-4-5-20251001)
- Claude Haiku 3.5 (deprecated) (claude-3-5-haiku-latest)

## How web search works

When you add the web search tool to your API request:

1. Claude decides when to search based on the prompt.
2. The API executes the searches and provides Claude with the results. This process may repeat multiple times throughout a single request.
3. At the end of its turn, Claude provides a final response with cited sources.

## Dynamic filtering with Opus 4.6 and Sonnet 4.6

With the web_search_20260209 tool version, Claude can write and execute code to post-process query results. Instead of reasoning over full HTML files, Claude dynamically filters search results before loading them into context.

Dynamic filtering is particularly effective for:
- Searching through technical documentation
- Literature review and citation verification
- Technical research
- Response grounding and verification

Dynamic filtering requires the code execution tool to be enabled.

```shell
curl https://api.anthropic.com/v1/messages \
  --header "x-api-key: $ANTHROPIC_API_KEY" \
  --header "anthropic-version: 2023-06-01" \
  --header "content-type: application/json" \
  --data '{
    "model": "claude-opus-4-6",
    "max_tokens": 4096,
    "messages": [
      {
        "role": "user",
        "content": "Search for the current prices of AAPL and GOOGL, then calculate which has a better P/E ratio."
      }
    ],
    "tools": [{
      "type": "web_search_20260209",
      "name": "web_search"
    }]
  }'
```

## How to use web search

Your organization's administrator must enable web search in the Claude Console.

```shell
curl https://api.anthropic.com/v1/messages \
  --header "x-api-key: $ANTHROPIC_API_KEY" \
  --header "anthropic-version: 2023-06-01" \
  --header "content-type: application/json" \
  --data '{
    "model": "claude-opus-4-6",
    "max_tokens": 1024,
    "messages": [
      {
        "role": "user",
        "content": "What is the weather in NYC?"
      }
    ],
    "tools": [{
      "type": "web_search_20250305",
      "name": "web_search",
      "max_uses": 5
    }]
  }'
```

## Tool definition

The web search tool supports the following parameters:

```json
{
  "type": "web_search_20250305",
  "name": "web_search",
  "max_uses": 5,
  "allowed_domains": ["example.com", "trusteddomain.org"],
  "blocked_domains": ["untrustedsource.com"],
  "user_location": {
    "type": "approximate",
    "city": "San Francisco",
    "region": "California",
    "country": "US",
    "timezone": "America/Los_Angeles"
  }
}
```

### Max uses

The max_uses parameter limits the number of searches performed.

### Domain filtering

- Domains should not include the HTTP/HTTPS scheme
- Subdomains are automatically included
- Subpaths are supported
- You can use either allowed_domains or blocked_domains, but not both
- Wildcard support: Only one wildcard (*) allowed per domain entry, must appear after the domain part

### Localization

The user_location parameter allows you to localize search results based on a user's location.

## Response

Search results include:
- **url**: The URL of the source page
- **title**: The title of the source page
- **page_age**: When the site was last updated
- **encrypted_content**: Encrypted content that must be passed back in multi-turn conversations

### Citations

Citations are always enabled for web search, and each web_search_result_location includes:
- **url**: The URL of the cited source
- **title**: The title of the cited source
- **encrypted_index**: A reference for multi-turn conversations
- **cited_text**: Up to 150 characters of the cited content

The web search citation fields cited_text, title, and url do not count towards input or output token usage.

### Errors

Possible error codes:
- **too_many_requests**: Rate limit exceeded
- **invalid_input**: Invalid search query parameter
- **max_uses_exceeded**: Maximum web search tool uses exceeded
- **query_too_long**: Query exceeds maximum length
- **unavailable**: An internal error occurred

## Prompt caching

Web search works with prompt caching. Add at least one cache_control breakpoint in your request to enable caching.

## Streaming

With streaming enabled, you'll receive search events as part of the stream with a pause while the search executes.

## Batch requests

You can include the web search tool in the Messages Batches API, priced the same as regular Messages API requests.

## Usage and pricing

Web search is available on the Claude API for $10 per 1,000 searches, plus standard token costs for search-generated content. Each web search counts as one use, regardless of the number of results returned. If an error occurs during web search, the web search will not be billed.
