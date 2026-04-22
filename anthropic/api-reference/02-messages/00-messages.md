# Messages

The Messages API is the primary API for interacting with Claude models. It provides endpoints for creating messages and counting tokens.

## Endpoints

- **Create a Message**: `POST /v1/messages` - Send messages to Claude for conversational interactions
- **Count tokens in a Message**: `POST /v1/messages/count_tokens` - Count tokens in a message before sending

## Key Types

This section documents the complete type system used by the Messages API. The types below define the structure of requests and responses.

### Content Block Types

- **TextBlock** - Text content with optional citations
- **ImageBlock** - Base64-encoded image content (JPEG, PNG, GIF, WebP)
- **DocumentBlock** - PDF or file-based document content
- **ToolUseBlock** - Tool/function call with input parameters
- **ToolResultBlock** - Result returned from a tool call
- **ThinkingBlock** - Extended thinking/reasoning content
- **RedactedThinkingBlock** - Redacted thinking content
- **CodeExecutionToolResultBlock** - Code execution results
- **BashCodeExecutionToolResultBlock** - Bash code execution results
- **ContainerUploadBlock** - File uploaded to container
- **MCPToolUseBlock** - MCP tool use content
- **MCPToolResultBlock** - MCP tool result content
- **ServerToolUseBlock** - Server-side tool use (web search, code execution)
- **WebSearchToolResultBlock** - Web search results

### Source Types

- **Base64ImageSource** - Base64-encoded image with media type
- **Base64PDFSource** - Base64-encoded PDF document
- **FileSource** - Reference to an uploaded file by file_id
- **URLImageSource** - Image from a URL
- **URLPDFSource** - PDF from a URL
- **URLReference** - URL reference for content

### Tool Types

- **Tool** - Custom tool definition with JSON schema
- **CodeExecutionTool20250522** - Code execution tool
- **CodeExecutionTool20250825** - Code execution tool (updated)
- **CodeExecutionTool20260120** - Code execution tool with REPL persistence
- **WebSearchTool20250305** - Web search tool
- **MCPTool** - MCP server tool
- **TextEditor20250429** - Text editor tool
- **BashTool20250124** - Bash execution tool

### Message Types

- **Message** - Complete response message with content blocks, usage, and metadata
- **MessageParam** - Input message with role and content
- **ContentBlock** - Union type for all response content blocks
- **ContentBlockParam** - Union type for all input content blocks

### Configuration Types

- **CacheControlEphemeral** - Cache control with TTL (5m or 1h)
- **CitationsConfig** - Enable/disable citation generation
- **ThinkingConfig** - Configure extended thinking
- **Metadata** - Request metadata with user_id
- **ToolChoice** - Control tool selection behavior (auto, any, tool, none)

### Usage Types

- **Usage** - Token usage for a request (input_tokens, output_tokens)
- **CacheCreation** - Cache creation token counts
- **CacheReadInput** - Cache read token counts

### Streaming Event Types

- **RawMessageStartEvent** - Start of message stream
- **RawMessageDeltaEvent** - Message-level delta (stop_reason, usage)
- **RawMessageStopEvent** - End of message stream
- **RawContentBlockStartEvent** - Start of content block
- **RawContentBlockDeltaEvent** - Content block delta (text, tool input, thinking, citations)
- **RawContentBlockStopEvent** - End of content block

### Output Configuration

- **OutputConfig** - Configure output format and constraints
- **JsonSchemaFormat** - JSON schema for structured output
- **TextFormat** - Plain text output format

For complete type definitions and schemas, see the API reference at https://docs.anthropic.com/en/api/messages.
