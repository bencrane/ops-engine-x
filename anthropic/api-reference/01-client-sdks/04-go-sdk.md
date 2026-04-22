# Go SDK

Install and configure the Anthropic Go SDK with context-based cancellation and functional options.

The Anthropic Go library provides convenient access to the Anthropic REST API from applications written in Go.

For API feature documentation with code examples, see the API reference. This page covers Go-specific SDK features and configuration.

## Installation

```go
import (
    "github.com/anthropics/anthropic-sdk-go" // imported as anthropic
)
```

Or to pin the version:

```bash
go get -u 'github.com/anthropics/anthropic-sdk-go@v1.27.1'
```

## Requirements

This library requires Go 1.23+.

## Usage

```go
package main

import (
    "context"
    "fmt"
    "github.com/anthropics/anthropic-sdk-go"
    "github.com/anthropics/anthropic-sdk-go/option"
)

func main() {
    client := anthropic.NewClient(
        option.WithAPIKey("my-anthropic-api-key"), // defaults to os.LookupEnv("ANTHROPIC_API_KEY")
    )
    message, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
        MaxTokens: 1024,
        Messages: []anthropic.MessageParam{
            anthropic.NewUserMessage(anthropic.NewTextBlock("What is a quaternion?")),
        },
        Model: anthropic.ModelClaudeOpus4_6,
    })
    if err != nil {
        panic(err.Error())
    }
    fmt.Printf("%+v\n", message.Content)
}
```

## Request fields

The anthropic library uses the `omitzero` semantics from the Go 1.24+ `encoding/json` release for request fields.

- Required primitive fields (`int64`, `string`, etc.) feature the tag `` `json:"...,required"` ``. These fields are always serialized, even their zero values.
- Optional primitive types are wrapped in a `param.Opt[T]`. These fields can be set with the provided constructors, `anthropic.String(string)`, `anthropic.Int(int64)`, etc.
- Any `param.Opt[T]`, map, slice, struct or string enum uses the tag `` `json:"...,omitzero"` ``. Its zero value is considered omitted.

To send null instead of a `param.Opt[T]`, use `param.Null[T]()`. To send null instead of a struct T, use `param.NullStruct[T]()`.

### Request unions

Unions are represented as a struct with fields prefixed by "Of" for each of its variants, only one field can be non-zero. The non-zero field will be serialized.

### Deserializing params

Param types are designed for outgoing requests only. If you need to reconstruct params from raw JSON, call `UnmarshalJSON` to populate non-union fields, then use `param.SetJSON` to attach the raw bytes for correct re-serialization.

## Response objects

All fields in response structs are ordinary value types (not pointers or wrappers). Response structs also include a special JSON field containing metadata about each property.

To handle optional data, use the `.Valid()` method on the JSON field. `.Valid()` returns true if a field is not null, not present, or couldn't be marshaled.

### Response unions

In responses, unions are represented by a flattened struct containing all possible fields from each of the object variants. To convert it to a variant use the `.AsFooVariant()` method or the `.AsAny()` method.

## Error handling

When the API returns a non-success status code, the SDK returns an error with type `*anthropic.Error`. This contains the `StatusCode`, `*http.Request`, and `*http.Response` values of the request, as well as the JSON of the error body. The error also includes the `RequestID` from the response headers.

```go
_, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
    MaxTokens: 1024,
    Messages:  []anthropic.MessageParam{...},
    Model:     anthropic.ModelClaudeOpus4_6,
})
if err != nil {
    var apierr *anthropic.Error
    if errors.As(err, &apierr) {
        println("Request ID:", apierr.RequestID)
        println(string(apierr.DumpRequest(true)))
        println(string(apierr.DumpResponse(true)))
    }
    panic(err.Error())
}
```

## Retries

Certain errors will be automatically retried 2 times by default, with a short exponential backoff. The SDK retries connection errors, 408 Request Timeout, 409 Conflict, 429 Rate Limit, and >=500 Internal errors.

```go
client := anthropic.NewClient(
    option.WithMaxRetries(0), // default is 2
)
```

## Timeouts

Requests do not time out by default; use context to configure a timeout for a request lifecycle.

```go
ctx, cancel := context.WithTimeout(context.Background(), 5*time.Minute)
defer cancel()

client.Messages.New(ctx, params,
    option.WithRequestTimeout(20*time.Second), // per-retry timeout
)
```

## Long requests

Consider using the streaming Messages API for longer running requests. Avoid setting a large `MaxTokens` value without using streaming. The SDK will return an error if a non-streaming request is expected to be above roughly 10 minutes long.

## File uploads

Request parameters that correspond to file uploads in multipart requests are typed as `io.Reader`. Use `anthropic.File(reader io.Reader, filename string, contentType string)` to specify custom content-type:

```go
file, err := os.Open("/path/to/file.json")
anthropic.BetaFileUploadParams{
    File:  anthropic.File(file, "custom-name.json", "application/json"),
    Betas: []anthropic.AnthropicBeta{anthropic.AnthropicBetaFilesAPI2025_04_14},
}
```

## Pagination

Use `.ListAutoPaging()` methods to iterate through items across all pages:

```go
iter := client.Messages.Batches.ListAutoPaging(context.TODO(), anthropic.MessageBatchListParams{
    Limit: anthropic.Int(20),
})
for iter.Next() {
    messageBatch := iter.Current()
    fmt.Printf("%+v\n", messageBatch)
}
if err := iter.Err(); err != nil {
    panic(err.Error())
}
```

Or use `.List()` methods to fetch a single page:

```go
page, err := client.Messages.Batches.List(context.TODO(), anthropic.MessageBatchListParams{
    Limit: anthropic.Int(20),
})
for page != nil {
    for _, batch := range page.Data {
        fmt.Printf("%+v\n", batch)
    }
    page, err = page.GetNextPage()
}
```

## RequestOptions

This library uses the functional options pattern. Functions defined in the `option` package return a `RequestOption`, which is a closure that mutates a `RequestConfig`.

```go
client := anthropic.NewClient(
    option.WithHeader("X-Some-Header", "custom_header_info"),
)

client.Messages.New(context.TODO(), params,
    option.WithHeader("X-Some-Header", "some_other_custom_header_info"),
    option.WithJSONSet("some.json.path", map[string]string{"my": "object"}),
)
```

## HTTP client customization

### Middleware

The SDK provides `option.WithMiddleware`, which applies the given middleware to requests.

```go
client := anthropic.NewClient(
    option.WithMiddleware(func(req *http.Request, next option.MiddlewareNext) (res *http.Response, err error) {
        start := time.Now()
        LogReq(req)
        res, err = next(req)
        LogRes(res, err, time.Since(start))
        return res, err
    }),
)
```

You may also replace the default `http.Client` with `option.WithHTTPClient(client)`.

## Platform integrations

For detailed platform setup guides with code examples, see:

- Amazon Bedrock
- Google Vertex AI

The Go SDK supports Amazon Bedrock and Google Vertex AI through subpackages:

- **Bedrock**: `import "github.com/anthropics/anthropic-sdk-go/bedrock"` - Use `bedrock.WithLoadDefaultConfig(ctx)` or `bedrock.WithConfig(cfg)`
- **Vertex AI**: `import "github.com/anthropics/anthropic-sdk-go/vertex"` - Use `vertex.WithGoogleAuth(ctx, region, projectID)` or `vertex.WithCredentials(ctx, region, projectID, creds)`

## Advanced usage

### Accessing raw response data

Use `option.WithResponseInto()` request option to access raw HTTP response data:

```go
var response *http.Response
message, err := client.Messages.New(context.TODO(), params,
    option.WithResponseInto(&response),
)
fmt.Printf("Status Code: %d\n", response.StatusCode)
fmt.Printf("Headers: %+#v\n", response.Header)
```

### Making custom/undocumented requests

To make requests to undocumented endpoints, use `client.Get`, `client.Post`, and other HTTP verbs. To use undocumented parameters, use `option.WithQuerySet()` or `option.WithJSONSet()`. To access undocumented response properties, use `result.JSON.RawJSON()` or `result.JSON.ExtraFields()`.

## Semantic versioning

This package generally follows SemVer conventions, though certain backwards-incompatible changes may be released as minor versions.

## Additional resources

- [GitHub repository](https://github.com/anthropics/anthropic-sdk-go)
- Go package documentation
- API reference
- Streaming guide
