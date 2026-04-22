# Java SDK

Install and configure the Anthropic Java SDK with builder patterns and async support.

The Anthropic Java SDK provides convenient access to the Anthropic REST API from applications written in Java. It uses the builder pattern for creating requests and supports both synchronous and asynchronous operations.

For API feature documentation with code examples, see the API reference. This page covers Java-specific SDK features and configuration.

## Installation

**Gradle:**

```groovy
implementation("com.anthropic:anthropic-java:2.18.0")
```

## Requirements

This library requires Java 8 or later.

## Quick start

```java
import com.anthropic.client.AnthropicClient;
import com.anthropic.client.okhttp.AnthropicOkHttpClient;
import com.anthropic.models.messages.Message;
import com.anthropic.models.messages.MessageCreateParams;
import com.anthropic.models.messages.Model;

// Configures using the `anthropic.apiKey`, `anthropic.authToken` and `anthropic.baseUrl` system properties
// Or configures using the `ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN` and `ANTHROPIC_BASE_URL` environment variables
AnthropicClient client = AnthropicOkHttpClient.fromEnv();

MessageCreateParams params = MessageCreateParams.builder()
    .maxTokens(1024L)
    .addUserMessage("Hello, Claude")
    .model(Model.CLAUDE_OPUS_4_6)
    .build();

Message message = client.messages().create(params);
```

## Client configuration

### API key setup

Configure the client using system properties or environment variables:

```java
AnthropicClient client = AnthropicOkHttpClient.fromEnv();
```

Or configure manually:

```java
AnthropicClient client = AnthropicOkHttpClient.builder()
    .apiKey("my-anthropic-api-key")
    .build();
```

Or use a combination of both approaches:

```java
AnthropicClient client = AnthropicOkHttpClient.builder()
    .fromEnv()
    .apiKey("my-anthropic-api-key")
    .build();
```

### Configuration options

| Setter | System property | Environment variable | Required | Default value |
|---|---|---|---|---|
| apiKey | anthropic.apiKey | ANTHROPIC_API_KEY | false | - |
| authToken | anthropic.authToken | ANTHROPIC_AUTH_TOKEN | false | - |
| baseUrl | anthropic.baseUrl | ANTHROPIC_BASE_URL | true | "https://api.anthropic.com" |

System properties take precedence over environment variables.

Don't create more than one client in the same application. Each client has a connection pool and thread pools, which are more efficient to share between requests.

### Modifying configuration

To temporarily use a modified client configuration while reusing the same connection and thread pools, call `withOptions()` on any client or service:

```java
AnthropicClient clientWithOptions = client.withOptions(optionsBuilder -> {
    optionsBuilder.baseUrl("https://example.com");
    optionsBuilder.maxRetries(42);
});
```

The `withOptions()` method does not affect the original client or service.

## Async usage

The default client is synchronous. To switch to asynchronous execution, call the `async()` method:

```java
AnthropicClient client = AnthropicOkHttpClient.fromEnv();

MessageCreateParams params = MessageCreateParams.builder()
    .maxTokens(1024L)
    .addUserMessage("Hello, Claude")
    .model(Model.CLAUDE_OPUS_4_6)
    .build();

CompletableFuture<Message> message = client.async().messages().create(params);
```

Or create an asynchronous client from the beginning:

```java
AnthropicClientAsync client = AnthropicOkHttpClientAsync.fromEnv();

CompletableFuture<Message> message = client.messages().create(params);
```

The asynchronous client supports the same options as the synchronous one, except most methods return `CompletableFuture`s.

## Streaming

### Synchronous streaming

These streaming methods return `StreamResponse` for synchronous clients:

```java
try (StreamResponse<RawMessageStreamEvent> streamResponse = client.messages().createStreaming(params)) {
    streamResponse.stream().forEach(chunk -> {
        System.out.println(chunk);
    });
    System.out.println("No more chunks!");
}
```

### Asynchronous streaming

For asynchronous clients, the method returns `AsyncStreamResponse`:

```java
client.async().messages().createStreaming(params).subscribe(chunk -> {
    System.out.println(chunk);
});

// If you need to handle errors or completion of the stream
client.async().messages().createStreaming(params).subscribe(new AsyncStreamResponse.Handler<>() {
    @Override
    public void onNext(RawMessageStreamEvent chunk) {
        System.out.println(chunk);
    }

    @Override
    public void onComplete(Optional<Throwable> error) {
        if (error.isPresent()) {
            System.out.println("Something went wrong!");
            throw new RuntimeException(error.get());
        } else {
            System.out.println("No more chunks!");
        }
    }
});
```

### Streaming with message accumulator

A `MessageAccumulator` can record the stream of events in the response as they are processed and accumulate a `Message` object similar to what would have been returned by the non-streaming API.

```java
MessageAccumulator messageAccumulator = MessageAccumulator.create();

try (StreamResponse<RawMessageStreamEvent> streamResponse =
        client.messages().createStreaming(createParams)) {
    streamResponse.stream()
        .peek(messageAccumulator::accumulate)
        .flatMap(event -> event.contentBlockDelta().stream())
        .flatMap(deltaEvent -> deltaEvent.delta().text().stream())
        .forEach(textDelta -> System.out.print(textDelta.text()));
}

Message message = messageAccumulator.message();
```

## Structured outputs

For complete structured outputs documentation including Java examples, see Structured Outputs.

## Tool use

Tool Use lets you integrate external tools and functions directly into the AI model's responses. The SDK can derive a tool and its parameters automatically from the structure of an arbitrary Java class.

### Defining tools with annotations

```java
@JsonClassDescription("Get the weather in a given location")
static class GetWeather {
    @JsonPropertyDescription("The city and state, e.g. San Francisco, CA")
    public String location;

    @JsonPropertyDescription("The unit of temperature")
    public Unit unit;

    public Weather execute() {
        // implementation
    }
}
```

### Calling tools

When your tool classes are defined, add them to the message parameters using `MessageCreateParams.addTool(Class<T>)` and then call them if requested:

```java
AnthropicClient client = AnthropicOkHttpClient.fromEnv();

MessageCreateParams.Builder createParamsBuilder = MessageCreateParams.builder()
    .model(Model.CLAUDE_OPUS_4_6)
    .maxTokens(2048)
    .addTool(GetWeather.class)
    .addUserMessage("What's the temperature in New York?");
```

### Tool name conversion

Tool names are derived from the camel case tool class names (e.g., `GetWeather`) and converted to snake case (e.g., `get_weather`). This conversion can be overridden using the `@JsonTypeName` annotation.

### Annotating tool classes

- `@JsonClassDescription` - Add a description to a tool class
- `@JsonTypeName` - Set the tool name
- `@JsonPropertyDescription` - Add a detailed description to a tool parameter
- `@JsonIgnore` - Exclude a public field from the generated JSON schema
- `@JsonProperty` - Include a non-public field in the generated JSON schema

## Message batches

The SDK provides support for the Message Batches API under the `client.messages().batches()` namespace. See the pagination section for how to iterate through batch results.

## File uploads

The SDK defines methods that accept files through the `MultipartField` interface:

```java
FileUploadParams params = FileUploadParams.builder()
    .file(
        MultipartField.<InputStream>builder()
            .value(Files.newInputStream(Paths.get("/path/to/file.pdf")))
            .contentType("application/pdf")
            .build()
    )
    .addBeta(AnthropicBeta.FILES_API_2025_04_14)
    .build();

FileMetadata fileMetadata = client.beta().files().upload(params);
```

## Error handling

The SDK throws custom unchecked exception types:

- **AnthropicServiceException** - Base class for HTTP errors
- **AnthropicIoException** - I/O networking errors
- **AnthropicRetryableException** - Generic error indicating a failure that could be retried
- **AnthropicInvalidDataException** - Failure to interpret successfully parsed data
- **AnthropicException** - Base class for all exceptions

### Status code mapping

| Status | Exception |
|---|---|
| 400 | BadRequestException |
| 401 | UnauthorizedException |
| 403 | PermissionDeniedException |
| 404 | NotFoundException |
| 422 | UnprocessableEntityException |
| 429 | RateLimitException |
| 5xx | InternalServerException |
| others | UnexpectedStatusCodeException |

```java
try {
    Message message = client.messages().create(params);
} catch (RateLimitException e) {
    System.out.println("Rate limited, retry after: " + e.headers());
} catch (UnauthorizedException e) {
    System.out.println("Invalid API key");
} catch (AnthropicServiceException e) {
    System.out.println("API error: " + e.statusCode());
} catch (AnthropicIoException e) {
    System.out.println("Network error: " + e.getMessage());
}
```

## Request IDs

When using raw responses, you can access the `request-id` response header using the `requestId()` method:

```java
HttpResponseFor<Message> message = client.messages().withRawResponse().create(params);
Optional<String> requestId = message.requestId();
```

## Retries

The SDK automatically retries 2 times by default, with a short exponential backoff between requests.

Only the following error types are retried: Connection errors, 408 Request Timeout, 409 Conflict, 429 Rate Limit, and 5xx Internal errors.

```java
AnthropicClient client = AnthropicOkHttpClient.builder().fromEnv().maxRetries(4).build();
```

## Timeouts

Requests time out after 10 minutes by default. For methods that accept `maxTokens`, if you specify a large value and are not streaming, the default timeout will be calculated dynamically (up to 60 minutes).

```java
// Per-request timeout
Message message = client
    .messages()
    .create(params, RequestOptions.builder().timeout(Duration.ofSeconds(30)).build());

// Client-level default
AnthropicClient client = AnthropicOkHttpClient.builder()
    .fromEnv()
    .timeout(Duration.ofSeconds(30))
    .build();
```

## Long requests

Consider using streaming for longer running requests. Avoid setting a large `maxTokens` value without using streaming. The SDK periodically pings the API to keep the connection alive and reduce the impact of idle connection timeouts.

## Pagination

### Auto-pagination

```java
BatchListPage page = client.messages().batches().list();

// Process as an Iterable
for (MessageBatch batch : page.autoPager()) {
    System.out.println(batch);
}

// Process as a Stream
page.autoPager()
    .stream()
    .limit(50)
    .forEach(batch -> System.out.println(batch));
```

### Manual pagination

```java
BatchListPage page = client.messages().batches().list();
while (true) {
    for (MessageBatch batch : page.items()) {
        System.out.println(batch);
    }
    if (!page.hasNextPage()) {
        break;
    }
    page = page.nextPage();
}
```

## Type system

### Immutability and builders

Each class in the SDK has an associated builder for constructing it. Each class is immutable once constructed. If the class has an associated builder, then it has a `toBuilder()` method for making a modified copy.

```java
MessageCreateParams params = MessageCreateParams.builder()
    .maxTokens(1024L)
    .addUserMessage("Hello, Claude")
    .model(Model.CLAUDE_OPUS_4_6)
    .build();

// Create a modified copy using toBuilder()
MessageCreateParams modified = params.toBuilder().maxTokens(2048L).build();
```

### Undocumented parameters

To set undocumented parameters, call the `putAdditionalHeader`, `putAdditionalQueryParam`, or `putAdditionalBodyProperty` methods on any Params class.

### Response properties

To access undocumented response properties, call the `_additionalProperties()` method.

### Response validation

By default, the SDK does not throw an exception when the API returns a response that doesn't match the expected type. To check upfront, call `validate()`:

```java
Message message = client.messages().create(params).validate();
```

## HTTP client customization

### Proxy configuration

```java
AnthropicClient client = AnthropicOkHttpClient.builder()
    .fromEnv()
    .proxy(new Proxy(Proxy.Type.HTTP, new InetSocketAddress("https://example.com", 8080)))
    .build();
```

### Custom HTTP client

The SDK consists of three artifacts:

- **anthropic-java-core** - Contains core SDK logic, does not depend on OkHttp
- **anthropic-java-client-okhttp** - Depends on OkHttp
- **anthropic-java** - Depends on and exposes the APIs of both

## Platform integrations

For detailed platform setup guides with code examples, see:

- Amazon Bedrock
- Google Vertex AI
- Microsoft Foundry

The Java SDK supports Bedrock, Vertex AI, and Foundry through separate dependencies:

- **Bedrock**: `com.anthropic:anthropic-java-bedrock` - Uses `BedrockBackend`
- **Vertex AI**: `com.anthropic:anthropic-java-vertex` - Uses `VertexBackend`
- **Foundry**: `com.anthropic:anthropic-java-foundry` - Uses `FoundryBackend`

## Advanced usage

### Raw response access

```java
HttpResponseFor<Message> message = client.messages().withRawResponse().create(params);
int statusCode = message.statusCode();
Headers headers = message.headers();
```

### Logging

Enable logging by setting the `ANTHROPIC_LOG` environment variable to `info` or `debug`.

## Beta features

You can access most beta API features through the `beta()` method on the client.

```java
StructuredMessageCreateParams<BookList> createParams = MessageCreateParams.builder()
    .model(Model.CLAUDE_OPUS_4_6)
    .maxTokens(2048)
    .outputFormat(BookList.class)
    .addUserMessage("List some famous late twentieth century novels.")
    .build();

client.beta().messages().create(createParams);
```

## Semantic versioning

This package generally follows SemVer conventions, though certain backwards-incompatible changes may be released as minor versions.

## Additional resources

- [GitHub repository](https://github.com/anthropics/anthropic-sdk-java)
- Javadocs
- API reference
- Streaming guide
- Tool use guide
