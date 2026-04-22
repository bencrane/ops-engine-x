# C# SDK

Install and configure the Anthropic C# SDK for .NET applications with IChatClient integration.

The Anthropic C# SDK provides convenient access to the Anthropic REST API from applications written in C#.

The C# SDK is currently in beta. APIs may change between versions.

For API feature documentation with code examples, see the API reference. This page covers C#-specific SDK features and configuration.

As of version 10+, the `Anthropic` package is now the official Anthropic SDK for C#. Package versions 3.X and below were previously used for the tryAGI community-built SDK, which has moved to `tryAGI.Anthropic`.

## Installation

Install the package from NuGet:

```bash
dotnet add package Anthropic
```

## Requirements

This library requires .NET Standard 2.0 or later.

## Usage

```csharp
using System;
using Anthropic;
using Anthropic.Models.Messages;

AnthropicClient client = new();

MessageCreateParams parameters = new()
{
    MaxTokens = 1024,
    Messages =
    [
        new()
        {
            Role = Role.User,
            Content = "Hello, Claude",
        },
    ],
    Model = "claude-opus-4-6",
};

var message = await client.Messages.Create(parameters);
Console.WriteLine(message);
```

## Client configuration

Configure the client using environment variables:

```csharp
// Configured using the ANTHROPIC_API_KEY, ANTHROPIC_AUTH_TOKEN and ANTHROPIC_BASE_URL environment variables
AnthropicClient client = new();
```

Or manually:

```csharp
AnthropicClient client = new() { ApiKey = "my-anthropic-api-key" };
```

| Property | Environment variable | Required | Default value |
|---|---|---|---|
| ApiKey | ANTHROPIC_API_KEY | false | - |
| AuthToken | ANTHROPIC_AUTH_TOKEN | false | - |
| BaseUrl | ANTHROPIC_BASE_URL | true | "https://api.anthropic.com" |

### Modifying configuration

To temporarily use a modified client configuration while reusing the same connection and thread pools, call `WithOptions`:

```csharp
var message = await client
    .WithOptions(options =>
        options with
        {
            BaseUrl = "https://example.com",
            Timeout = TimeSpan.FromSeconds(42),
        }
    )
    .Messages.Create(parameters);
```

## Streaming

Streaming methods return `IAsyncEnumerable`:

```csharp
await foreach (var message in client.Messages.CreateStreaming(parameters))
{
    Console.WriteLine(message);
}
```

## Error handling

The SDK throws custom exception types:

| Status | Exception |
|---|---|
| 400 | AnthropicBadRequestException |
| 401 | AnthropicUnauthorizedException |
| 403 | AnthropicForbiddenException |
| 404 | AnthropicNotFoundException |
| 422 | AnthropicUnprocessableEntityException |
| 429 | AnthropicRateLimitException |
| 5xx | Anthropic5xxException |
| others | AnthropicUnexpectedStatusCodeException |

Additionally: `AnthropicSseException` for SSE streaming errors, `AnthropicIOException` for I/O errors, `AnthropicInvalidDataException` for data interpretation failures.

## Retries

The SDK automatically retries 2 times by default, with a short exponential backoff. Configure with:

```csharp
AnthropicClient client = new() { MaxRetries = 3 };
```

## Timeouts

Requests time out after 10 minutes by default.

```csharp
AnthropicClient client = new() { Timeout = TimeSpan.FromSeconds(42) };
```

## Pagination

### Auto-pagination

```csharp
var page = await client.Messages.Batches.List(parameters);
await foreach (var item in page.Paginate())
{
    Console.WriteLine(item);
}
```

### Manual pagination

```csharp
var page = await client.Messages.Batches.List();
while (true)
{
    foreach (var item in page.Items)
    {
        Console.WriteLine(item);
    }
    if (!page.HasNext()) break;
    page = await page.Next();
}
```

## Response validation

By default, the SDK does not throw on type mismatches. To enable upfront validation:

```csharp
var message = await client.Messages.Create(parameters);
message.Validate();

// Or configure at client level:
AnthropicClient client = new() { ResponseValidation = true };
```

## IChatClient integration

The SDK provides an implementation of the `IChatClient` interface from `Microsoft.Extensions.AI.Abstractions`. This enables use with other libraries that integrate with these core abstractions, including the MCP C# SDK:

```csharp
using Anthropic;
using Microsoft.Extensions.AI;
using ModelContextProtocol.Client;

IChatClient chatClient = client.AsIChatClient("claude-opus-4-6")
    .AsBuilder()
    .UseFunctionInvocation()
    .Build();

McpClient learningServer = await McpClient.CreateAsync(
    new HttpClientTransport(new() { Endpoint = new("https://learn.microsoft.com/api/mcp") }));
ChatOptions options = new() { Tools = [.. await learningServer.ListToolsAsync()] };
Console.WriteLine(await chatClient.GetResponseAsync("Tell me about IChatClient", options));
```

## Advanced usage

### Raw responses

Access response headers, status code, or the raw response body by prefixing with `WithRawResponse`:

```csharp
var response = await client.WithRawResponse.Messages.Create(parameters);
var statusCode = response.StatusCode;
var headers = response.Headers;
```

### Logging

Enable debug logging via environment variable:

```bash
export ANTHROPIC_LOG=debug
```

## Platform integrations

The C# SDK supports Bedrock and Foundry through separate NuGet packages:

- **Bedrock**: `Anthropic.Bedrock` - Uses `AnthropicBedrockClient`
- **Foundry**: `Anthropic.Foundry` - Uses `AnthropicFoundryClient`

## Semantic versioning

While this package is versioned as 10+, it's currently in beta. During the beta period, breaking changes may occur in minor or patch releases.

## Additional resources

- [GitHub repository](https://github.com/anthropics/anthropic-sdk-csharp)
- [NuGet package](https://www.nuget.org/packages/Anthropic)
- API reference
- Streaming guide
