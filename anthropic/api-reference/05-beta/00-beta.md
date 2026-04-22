# Beta

## Endpoints

### Beta Models
- **List Models** `GET /v1/models`
- **Get a Model** `GET /v1/models/{model_id}`

### Beta Messages
- **Create a Message** `POST /v1/messages`
- **Count tokens in a Message** `POST /v1/messages/count_tokens`

### Beta Files
- **Upload File** `POST /v1/files`
- **List Files** `GET /v1/files`
- **Download File** `GET /v1/files/{file_id}/content`
- **Get File Metadata** `GET /v1/files/{file_id}`
- **Delete File** `DELETE /v1/files/{file_id}`

### Beta Skills
- **Create Skill** `POST /v1/skills`
- **List Skills** `GET /v1/skills`
- **Get Skill** `GET /v1/skills/{skill_id}`
- **Delete Skill** `DELETE /v1/skills/{skill_id}`

### Beta Skill Versions
- **Create Skill Version** `POST /v1/skills/{skill_id}/versions`
- **List Skill Versions** `GET /v1/skills/{skill_id}/versions`
- **Get Skill Version** `GET /v1/skills/{skill_id}/versions/{version_id}`
- **Delete Skill Version** `DELETE /v1/skills/{skill_id}/versions/{version_id}`

## Models

### AnthropicBeta

Accepts one of the following:
- `string`
- `"message-batches-2024-09-24"`
- `"prompt-caching-2024-07-31"`
- `"computer-use-2024-10-22"`
- `"computer-use-2025-01-24"`
- `"pdfs-2024-09-25"`
- `"token-counting-2024-11-01"`
- `"token-efficient-tools-2025-02-19"`
- `"output-128k-2025-02-19"`
- `"files-api-2025-04-14"`
- `"mcp-client-2025-04-04"`
- `"mcp-client-2025-11-20"`
- `"dev-full-thinking-2025-05-14"`
- `"interleaved-thinking-2025-05-14"`
- `"code-execution-2025-05-22"`
- `"extended-cache-ttl-2025-04-11"`
- `"context-1m-2025-08-07"`
- `"context-management-2025-06-27"`
- `"model-context-window-exceeded-2025-08-26"`
- `"skills-2025-10-02"`
- `"fast-mode-2026-02-01"`

### BetaAPIError

`object { message, type }`

- **message**: `string`
- **type**: `"api_error"`

### BetaAuthenticationError

`object { message, type }`

- **message**: `string`
- **type**: `"authentication_error"`

### BetaBillingError

`object { message, type }`

- **message**: `string`
- **type**: `"billing_error"`

### BetaError

Accepts one of the following:
- `BetaInvalidRequestError { message, type }`
- `BetaAuthenticationError { message, type }`
- `BetaBillingError { message, type }`
- `BetaPermissionError { message, type }`
- `BetaNotFoundError { message, type }`
- `BetaRateLimitError { message, type }`
- `BetaGatewayTimeoutError { message, type }`
- `BetaAPIError { message, type }`
- `BetaOverloadedError { message, type }`

### BetaErrorResponse

`object { error, request_id, type }`

- **error**: `BetaError`
- **request_id**: `string`
- **type**: `"error"`

### BetaGatewayTimeoutError

`object { message, type }`

- **message**: `string`
- **type**: `"timeout_error"`

### BetaInvalidRequestError

`object { message, type }`

- **message**: `string`
- **type**: `"invalid_request_error"`

### BetaNotFoundError

`object { message, type }`

- **message**: `string`
- **type**: `"not_found_error"`

### BetaOverloadedError

`object { message, type }`

- **message**: `string`
- **type**: `"overloaded_error"`

### BetaPermissionError

`object { message, type }`

- **message**: `string`
- **type**: `"permission_error"`

### BetaRateLimitError

`object { message, type }`

- **message**: `string`
- **type**: `"rate_limit_error"`
