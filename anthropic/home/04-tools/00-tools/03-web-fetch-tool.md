# Web fetch tool

The web fetch tool allows Claude to retrieve full content from specified web pages and PDF documents.

The latest web fetch tool version (web_fetch_20260209) supports dynamic filtering with Claude Opus 4.6 and Sonnet 4.6. Claude can write and execute code to filter fetched content before it reaches the context window, keeping only relevant information and discarding the rest. The previous tool version (web_fetch_20250910) remains available without dynamic filtering.

The basic web fetch tool (web_fetch_20250910) is eligible for Zero Data Retention (ZDR). The web_fetch_20260209 version with dynamic filtering is not ZDR-eligible by default because dynamic filtering relies on code execution internally. To use web_fetch_20260209 with ZDR, disable dynamic filtering by setting "allowed_callers": ["direct"] on the tool.

Enabling the web fetch tool in environments where Claude processes untrusted input alongside sensitive data poses data exfiltration risks. Claude is not allowed to dynamically construct URLs -- it can only fetch URLs explicitly provided by the user or from previous search/fetch results.

## Supported models

Web fetch is available on all active Claude models including Opus 4.6, Opus 4.5, Opus 4.1, Opus 4, Sonnet 4.6, Sonnet 4.5, Sonnet 4, Haiku 4.5, and deprecated models Sonnet 3.7 and Haiku 3.5.

## How web fetch works

1. Claude decides when to fetch content based on the prompt and available URLs.
2. The API retrieves the full text content from the specified URL.
3. For PDFs, automatic text extraction is performed.
4. Claude analyzes the fetched content and provides a response with optional citations.

The web fetch tool currently does not support websites dynamically rendered via JavaScript.

## Dynamic filtering with Opus 4.6 and Sonnet 4.6

With the web_fetch_20260209 tool version, Claude can write and execute code to filter the fetched content before loading it into context. Dynamic filtering requires the code execution tool to be enabled.

```shell
curl https://api.anthropic.com/v1/messages \
  --header "x-api-key: $ANTHROPIC_API_KEY" \
  --header "anthropic-version: 2023-06-01" \
  --header "content-type: application/json" \
  --data '{
    "model": "claude-opus-4-6",
    "max_tokens": 4096,
    "messages": [{"role": "user", "content": "Fetch the content at https://example.com/research-paper and extract the key findings."}],
    "tools": [{"type": "web_fetch_20260209", "name": "web_fetch"}]
  }'
```

## Tool definition

```json
{
  "type": "web_fetch_20250910",
  "name": "web_fetch",
  "max_uses": 10,
  "allowed_domains": ["example.com", "docs.example.com"],
  "blocked_domains": ["private.example.com"],
  "citations": {"enabled": true},
  "max_content_tokens": 100000
}
```

### Parameters

- **max_uses**: Limits number of web fetches performed. No default limit.
- **allowed_domains / blocked_domains**: Domain filtering. Cannot use both simultaneously.
- **citations**: Optional. Set enabled: true for Claude to cite specific passages.
- **max_content_tokens**: Limits content included in context. Approximate.

### Domain filtering

- Domains should not include HTTP/HTTPS scheme
- Subdomains are automatically included
- Subpaths are supported
- Be aware of Unicode homograph attacks in domain names

## Response

Fetch results include:
- **url**: The URL that was fetched
- **content**: A document block containing the fetched content
- **retrieved_at**: Timestamp when the content was retrieved

The web fetch tool caches results to improve performance. Content returned may not always reflect the latest version.

### Errors

Possible error codes: invalid_input, url_too_long, url_not_allowed, url_not_accessible, too_many_requests, unsupported_content_type, max_uses_exceeded, unavailable.

### URL validation

The web fetch tool can only fetch URLs that have previously appeared in the conversation context (user messages, tool results, or previous search/fetch results).

## Combined search and fetch

Web fetch works seamlessly with web search for comprehensive information gathering. Claude will search to find relevant articles, then fetch full content for detailed analysis.

## Prompt caching

Web fetch works with prompt caching. Add cache_control breakpoints in your request.

## Usage and pricing

The web fetch tool has no additional charges beyond standard token costs. Typical token usage:

- Average web page (10 kB): ~2,500 tokens
- Large documentation page (100 kB): ~25,000 tokens
- Research paper PDF (500 kB): ~125,000 tokens
