# Pricing

Learn about Anthropic's pricing structure for models and features.

This page provides detailed pricing information for Anthropic's models and features. All prices are in USD.

For the most current pricing information, please visit claude.com/pricing.

## Model pricing

The following table shows pricing for all Claude models across different usage tiers:

| Model | Base Input Tokens | 5m Cache Writes | 1h Cache Writes | Cache Hits & Refreshes | Output Tokens |
|-------|------------------|-----------------|-----------------|----------------------|---------------|
| Claude Opus 4.6 | $5 / MTok | $6.25 / MTok | $10 / MTok | $0.50 / MTok | $25 / MTok |
| Claude Opus 4.5 | $5 / MTok | $6.25 / MTok | $10 / MTok | $0.50 / MTok | $25 / MTok |
| Claude Opus 4.1 | $15 / MTok | $18.75 / MTok | $30 / MTok | $1.50 / MTok | $75 / MTok |
| Claude Opus 4 | $15 / MTok | $18.75 / MTok | $30 / MTok | $1.50 / MTok | $75 / MTok |
| Claude Sonnet 4.6 | $3 / MTok | $3.75 / MTok | $6 / MTok | $0.30 / MTok | $15 / MTok |
| Claude Sonnet 4.5 | $3 / MTok | $3.75 / MTok | $6 / MTok | $0.30 / MTok | $15 / MTok |
| Claude Sonnet 4 | $3 / MTok | $3.75 / MTok | $6 / MTok | $0.30 / MTok | $15 / MTok |
| Claude Sonnet 3.7 (deprecated) | $3 / MTok | $3.75 / MTok | $6 / MTok | $0.30 / MTok | $15 / MTok |
| Claude Haiku 4.5 | $1 / MTok | $1.25 / MTok | $2 / MTok | $0.10 / MTok | $5 / MTok |
| Claude Haiku 3.5 | $0.80 / MTok | $1 / MTok | $1.6 / MTok | $0.08 / MTok | $4 / MTok |
| Claude Opus 3 (deprecated) | $15 / MTok | $18.75 / MTok | $30 / MTok | $1.50 / MTok | $75 / MTok |
| Claude Haiku 3 | $0.25 / MTok | $0.30 / MTok | $0.50 / MTok | $0.03 / MTok | $1.25 / MTok |

MTok = Million tokens. The "Base Input Tokens" column shows standard input pricing, "Cache Writes" and "Cache Hits" are specific to prompt caching, and "Output Tokens" shows output pricing. See prompt caching pricing below for an explanation of the cache columns and pricing multipliers.

## Third-party platform pricing

Claude models are available on AWS Bedrock, Google Vertex AI, and Microsoft Foundry. For official pricing, visit:

- AWS Bedrock pricing
- Google Vertex AI pricing
- Microsoft Foundry pricing

### Regional endpoint pricing for Claude 4.5 models and beyond

Starting with Claude Sonnet 4.5 and Haiku 4.5, AWS Bedrock and Google Vertex AI offer two endpoint types:

- **Global endpoints:** Dynamic routing across regions for maximum availability
- **Regional endpoints:** Data routing guaranteed within specific geographic regions

Regional endpoints include a 10% premium over global endpoints. The Claude API (1P) is global by default and unaffected by this change.

> The Claude API is global-only (equivalent to the global endpoint offering and pricing from other providers).

Scope: This pricing structure applies to Claude Sonnet 4.5, Haiku 4.5, and all future models. Earlier models (Claude Sonnet 4, Opus 4, and prior releases) retain their existing pricing.

## Feature-specific pricing

### Prompt caching

Prompt caching reduces costs and latency by reusing previously processed portions of your prompt across API calls. Instead of reprocessing the same large system prompt, document, or conversation history on every request, the API reads from cache at a fraction of the standard input price.

There are two ways to enable prompt caching:

- **Automatic caching:** Add a single `cache_control` field at the top level of your request. The system automatically manages cache breakpoints as conversations grow. This is the recommended starting point for most use cases.
- **Explicit cache breakpoints:** Place `cache_control` directly on individual content blocks for fine-grained control over exactly what gets cached.

| Cache operation | Multiplier | Duration |
|----------------|------------|----------|
| 5-minute cache write | 1.25x base input price | Cache valid for 5 minutes |
| 1-hour cache write | 2x base input price | Cache valid for 1 hour |
| Cache read (hit) | 0.1x base input price | Same duration as the preceding write |

Cache write tokens are charged when content is first stored. Cache read tokens are charged when a subsequent request retrieves the cached content. A cache hit costs 10% of the standard input price, which means caching pays off after just one cache read for the 5-minute duration (1.25x write), or after two cache reads for the 1-hour duration (2x write).

These multipliers stack with other pricing modifiers, including the Batch API discount, long context pricing, and data residency.

### Data residency pricing

For Claude Opus 4.6 and newer models, specifying US-only inference via the `inference_geo` parameter incurs a 1.1x multiplier on all token pricing categories, including input tokens, output tokens, cache writes, and cache reads. Global routing (the default) uses standard pricing.

This applies to the Claude API (1P) only. Third-party platforms have their own regional pricing. Earlier models retain their existing pricing regardless of `inference_geo` settings.

### Fast mode pricing

Fast mode (beta: research preview) for Claude Opus 4.6 provides significantly faster output at premium pricing (6x standard rates). Fast mode pricing applies across the full context window, including requests over 200k input tokens. Currently supported on Opus 4.6:

| Input | Output |
|-------|--------|
| $30 / MTok | $150 / MTok |

Fast mode pricing stacks with other pricing modifiers:

- Prompt caching multipliers apply on top of fast mode pricing
- Data residency multipliers apply on top of fast mode pricing

Fast mode is not available with the Batch API.

### Batch processing

The Batch API allows asynchronous processing of large volumes of requests with a 50% discount on both input and output tokens.

| Model | Batch input | Batch output |
|-------|------------|-------------|
| Claude Opus 4.6 | $2.50 / MTok | $12.50 / MTok |
| Claude Opus 4.5 | $2.50 / MTok | $12.50 / MTok |
| Claude Opus 4.1 | $7.50 / MTok | $37.50 / MTok |
| Claude Opus 4 | $7.50 / MTok | $37.50 / MTok |
| Claude Sonnet 4.6 | $1.50 / MTok | $7.50 / MTok |
| Claude Sonnet 4.5 | $1.50 / MTok | $7.50 / MTok |
| Claude Sonnet 4 | $1.50 / MTok | $7.50 / MTok |
| Claude Sonnet 3.7 (deprecated) | $1.50 / MTok | $7.50 / MTok |
| Claude Haiku 4.5 | $0.50 / MTok | $2.50 / MTok |
| Claude Haiku 3.5 | $0.40 / MTok | $2 / MTok |
| Claude Opus 3 (deprecated) | $7.50 / MTok | $37.50 / MTok |
| Claude Haiku 3 | $0.125 / MTok | $0.625 / MTok |

### Long context pricing

Claude Opus 4.6 and Sonnet 4.6 include the full 1M token context window at standard pricing. (A 900k-token request is billed at the same per-token rate as a 9k-token request.) Prompt caching and batch processing discounts apply at standard rates across the full context window.

For Claude Sonnet 4.5 and Sonnet 4, the 1M token context window is in beta for organizations in usage tier 4 and organizations with custom rate limits. When the `context-1m-2025-08-07` beta header is included, requests that exceed 200k input tokens are automatically charged at premium long context rates:

| Model | ≤ 200k Input | ≤ 200k Output | > 200k Input | > 200k Output |
|-------|-------------|---------------|-------------|---------------|
| Claude Sonnet 4.5 / 4 | $3 / MTok | $15 / MTok | $6 / MTok | $22.50 / MTok |

Long context pricing for Sonnet 4.5 and Sonnet 4 stacks with other pricing modifiers:

- The Batch API 50% discount applies to long context pricing
- Prompt caching multipliers apply on top of long context pricing

> Even with the beta flag enabled, requests with fewer than 200k input tokens are charged at standard rates. If your request exceeds 200k input tokens, all tokens incur premium pricing. The 200k threshold is based solely on input tokens (including cache reads/writes). Output token count does not affect pricing tier selection, though output tokens are charged at the higher rate when the input threshold is exceeded.

### Tool use pricing

Tool use requests are priced based on:

- The total number of input tokens sent to the model (including in the `tools` parameter)
- The number of output tokens generated
- For server-side tools, additional usage-based pricing (e.g., web search charges per search performed)

Client-side tools are priced the same as any other Claude API request, while server-side tools may incur additional charges based on their specific usage.

The additional tokens from tool use come from:

- The `tools` parameter in API requests (tool names, descriptions, and schemas)
- `tool_use` content blocks in API requests and responses
- `tool_result` content blocks in API requests

When you use tools, a special system prompt for the model is automatically included which enables tool use. The number of tool use tokens required for each model are listed below:

| Model | Tool choice | Tool use system prompt token count |
|-------|------------|----------------------------------|
| Claude Opus 4.6 | auto, none / any, tool | 346 tokens / 313 tokens |
| Claude Opus 4.5 | auto, none / any, tool | 346 tokens / 313 tokens |
| Claude Opus 4.1 | auto, none / any, tool | 346 tokens / 313 tokens |
| Claude Opus 4 | auto, none / any, tool | 346 tokens / 313 tokens |
| Claude Sonnet 4.6 | auto, none / any, tool | 346 tokens / 313 tokens |
| Claude Sonnet 4.5 | auto, none / any, tool | 346 tokens / 313 tokens |
| Claude Sonnet 4 | auto, none / any, tool | 346 tokens / 313 tokens |
| Claude Sonnet 3.7 (deprecated) | auto, none / any, tool | 346 tokens / 313 tokens |
| Claude Haiku 4.5 | auto, none / any, tool | 346 tokens / 313 tokens |
| Claude Haiku 3.5 | auto, none / any, tool | 264 tokens / 340 tokens |
| Claude Opus 3 (deprecated) | auto, none / any, tool | 530 tokens / 281 tokens |
| Claude Sonnet 3 | auto, none / any, tool | 159 tokens / 235 tokens |
| Claude Haiku 3 | auto, none / any, tool | 264 tokens / 340 tokens |

### Specific tool pricing

#### Bash tool

The bash tool adds 245 input tokens to your API calls. Additional tokens are consumed by command outputs (stdout/stderr), error messages, and large file contents.

#### Code execution tool

Code execution is free when used with web search or web fetch. When `web_search_20260209` or `web_fetch_20260209` is included in your API request, there are no additional charges for code execution tool calls beyond the standard input and output token costs.

When used without these tools, code execution is billed by execution time, tracked separately from token usage:

- Execution time has a minimum of 5 minutes
- Each organization receives 1,550 free hours of usage per month
- Additional usage beyond 1,550 hours is billed at $0.05 per hour, per container
- If files are included in the request, execution time is billed even if the tool is not invoked, due to files being preloaded onto the container

#### Text editor tool

The text editor tool uses the same pricing structure as other tools. Additional input tokens:

| Tool | Additional input tokens |
|------|----------------------|
| text_editor_20250429 (Claude 4.x) | 700 tokens |
| text_editor_20250124 (Claude Sonnet 3.7) | 700 tokens |

#### Web search tool

Web search is available on the Claude API for $10 per 1,000 searches, plus standard token costs for search-generated content. Web search results retrieved throughout a conversation are counted as input tokens. Each web search counts as one use, regardless of the number of results returned. If an error occurs during web search, the web search will not be billed.

#### Web fetch tool

The web fetch tool is available on the Claude API at no additional cost. You only pay standard token costs for the fetched content that becomes part of your conversation context.

To protect against inadvertently fetching large content that would consume excessive tokens, use the `max_content_tokens` parameter to set appropriate limits.

Example token usage for typical content:

- Average web page (10 kB): ~2,500 tokens
- Large documentation page (100 kB): ~25,000 tokens
- Research paper PDF (500 kB): ~125,000 tokens

#### Computer use tool

Computer use follows the standard tool use pricing. When using the computer use tool:

- System prompt overhead: The computer use beta adds 466-499 tokens to the system prompt
- Computer use tool token usage: 735 input tokens per tool definition (Claude 4.x and Claude Sonnet 3.7)
- Additional token consumption: Screenshot images (see Vision pricing) and tool execution results returned to Claude

## Agent use case pricing examples

### Customer support agent example

When building a customer support agent:

- Average ~3,700 tokens per conversation
- Using Claude Opus 4.6 at $5/MTok input, $25/MTok output
- Total cost: ~$37.00 per 10,000 tickets

### General agent workflow pricing

For more complex agent architectures with multiple steps:

- **Initial request processing:** Typical input 500-1,000 tokens, ~$0.003 per request
- **Memory and context retrieval:** Retrieved context 2,000-5,000 tokens, ~$0.015 per operation
- **Action planning and execution:** Planning 1,000-2,000 tokens, execution feedback 500-1,000, ~$0.045 per action

### Cost optimization strategies

- **Use appropriate models:** Choose Haiku for simple tasks, Sonnet for complex reasoning
- **Implement prompt caching:** Reduce costs for repeated context
- **Batch operations:** Use the Batch API for non-time-sensitive tasks
- **Monitor usage patterns:** Track token consumption to identify optimization opportunities

## Additional pricing considerations

### Rate limits

Rate limits vary by usage tier:

- **Tier 1:** Entry-level usage with basic limits
- **Tier 2:** Increased limits for growing applications
- **Tier 3:** Higher limits for established applications
- **Tier 4:** Maximum standard limits
- **Enterprise:** Custom limits available

### Volume discounts

- Standard tiers use the pricing shown above
- Enterprise customers can contact sales for custom pricing
- Academic and research discounts may be available

### Enterprise pricing

For enterprise customers with specific needs: custom rate limits, volume discounts, dedicated support, and custom terms. Contact the sales team at sales@anthropic.com or through the Claude Console.

### Billing and payment

- Billing is calculated monthly based on actual usage
- Payments are processed in USD
- Credit card and invoicing options available
- Usage tracking available in the Claude Console

## Frequently asked questions

**How is token usage calculated?**
Tokens are pieces of text that models process. As a rough estimate, 1 token is approximately 4 characters or 0.75 words in English. The exact count varies by language and content type.

**Are there free tiers or trials?**
New users receive a small amount of free credits to test the API. Contact sales for information about extended trials for enterprise evaluation.

**How do discounts stack?**
Batch API and prompt caching discounts can be combined. For example, using both features together provides significant cost savings compared to standard API calls.

**What payment methods are accepted?**
Major credit cards are accepted for standard accounts. Enterprise customers can arrange invoicing and other payment methods.

For additional questions about pricing, contact support@anthropic.com.
