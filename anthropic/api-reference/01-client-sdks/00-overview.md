# Client SDKs

Official SDKs for building with the Claude API in Python, TypeScript, Java, Go, Ruby, C#, and PHP.

Anthropic provides official client SDKs in multiple languages to make it easier to work with the Claude API. Each SDK provides idiomatic interfaces, type safety, and built-in support for features like streaming, retries, and error handling.

- **Python**: Sync and async clients, Pydantic models
- **TypeScript**: Node.js, Deno, Bun, and browser support
- **Java**: Builder pattern, CompletableFuture async
- **Go**: Context-based cancellation, functional options
- **Ruby**: Sorbet types, streaming helpers
- **C#**: .NET Standard 2.0+, IChatClient integration
- **PHP**: Value objects, builder pattern

## Quick installation

**Python:**

```bash
pip install anthropic
```

## Quick start

**Python:**

```python
import anthropic

client = anthropic.Anthropic()

message = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello, Claude"}],
)
print(message.content)
```

## Platform support

All SDKs support multiple deployment options:

| Platform | Description |
|---|---|
| Claude API | Connect directly to Claude API endpoints |
| Amazon Bedrock | Use Claude through AWS |
| Google Vertex AI | Use Claude through Google Cloud |
| Microsoft Foundry | Use Claude through Microsoft Azure |

See individual SDK pages for platform-specific setup instructions.

## Beta features

Access beta features using the beta namespace in any SDK:

**Python:**

```python
message = client.beta.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello"}],
    betas=["feature-name"],
)
```

See Beta headers for available beta features.

## Requirements

| SDK | Minimum Version |
|---|---|
| Python | 3.9+ |
| TypeScript | 4.9+ (Node.js 20+) |
| Java | 8+ |
| Go | 1.23+ |
| Ruby | 3.2.0+ |
| C# | .NET Standard 2.0 |
| PHP | 8.1.0+ |

## GitHub repositories

- [anthropic-sdk-python](https://github.com/anthropics/anthropic-sdk-python)
- [anthropic-sdk-typescript](https://github.com/anthropics/anthropic-sdk-typescript)
- [anthropic-sdk-java](https://github.com/anthropics/anthropic-sdk-java)
- [anthropic-sdk-go](https://github.com/anthropics/anthropic-sdk-go)
- [anthropic-sdk-ruby](https://github.com/anthropics/anthropic-sdk-ruby)
- [anthropic-sdk-csharp](https://github.com/anthropics/anthropic-sdk-csharp)
- [anthropic-sdk-php](https://github.com/anthropics/anthropic-sdk-php)
