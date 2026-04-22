# PDF support

Process PDFs with Claude. Extract text, analyze charts, and understand visual content from your documents.

You can ask Claude about any text, pictures, charts, and tables in PDFs you provide. Some sample use cases:

- Analyzing financial reports and understanding charts/tables
- Extracting key information from legal documents
- Translation assistance for documents
- Converting document information into structured formats

## Before you begin

### Check PDF requirements

Claude works with any standard PDF. Ensure your request size meets these requirements:

| Requirement | Limit |
|---|---|
| Maximum request size | 32 MB (varies by platform) |
| Maximum pages per request | 600 (100 for models with a 200k-token context window) |
| Format | Standard PDF (no passwords/encryption) |

Both limits are on the entire request payload, including any other content sent alongside PDFs. For large PDFs, consider uploading with the Files API and referencing by file_id to keep request payloads small.

Dense PDFs (many small-font pages, complex tables, or heavy graphics) can fill the context window before reaching the page limit. Requests with large PDFs can also fail before reaching the page limit, even when using the Files API. Try splitting the document into sections; for large files, since each page is processed as an image, downsampling embedded images can also help.

Since PDF support relies on Claude's vision capabilities, it is subject to the same limitations and considerations as other vision tasks.

### Supported platforms and models

PDF support is currently supported via direct API access and Google Vertex AI. All active models support PDF processing.

PDF support is now available on Amazon Bedrock with the following considerations:

#### Amazon Bedrock PDF Support

When using PDF support through Amazon Bedrock's Converse API, there are two distinct document processing modes:

Important: To access Claude's full visual PDF understanding capabilities in the Converse API, you must enable citations. Without citations enabled, the API falls back to basic text extraction only.

**Document Processing Modes:**

- **Converse Document Chat** (Original mode - Text extraction only): Provides basic text extraction from PDFs. Cannot analyze images, charts, or visual layouts within PDFs. Uses approximately 1,000 tokens for a 3-page PDF. Automatically used when citations are not enabled.
- **Claude PDF Chat** (New mode - Full visual understanding): Provides complete visual analysis of PDFs. Can understand and analyze charts, graphs, images, and visual layouts. Processes each page as both text and image for comprehensive understanding. Uses approximately 7,000 tokens for a 3-page PDF. Requires citations to be enabled in the Converse API.

For non-PDF files like .csv, .xlsx, .docx, .md, or .txt files, see Working with other file formats.

## Process PDFs with Claude

### Send your first PDF request

You can provide PDFs to Claude in three ways:

- As a URL reference to a PDF hosted online
- As a base64-encoded PDF in document content blocks
- By a file_id from the Files API

#### Option 1: URL-based PDF document

```shell
curl https://api.anthropic.com/v1/messages \
  -H "content-type: application/json" \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -d '{
    "model": "claude-opus-4-6",
    "max_tokens": 1024,
    "messages": [{
      "role": "user",
      "content": [{
        "type": "document",
        "source": {
          "type": "url",
          "url": "https://assets.anthropic.com/m/1cd9d098ac3e6467/original/Claude-3-Model-Card-October-Addendum.pdf"
        }
      },
      {
        "type": "text",
        "text": "What are the key findings in this document?"
      }]
    }]
  }'
```

#### Option 2: Base64-encoded PDF document

If you need to send PDFs from your local system or when a URL isn't available, encode the PDF as base64 and include it in the request.

#### Option 3: Files API

For PDFs you'll use repeatedly, or when you want to avoid encoding overhead, use the Files API:

```shell
# First, upload your PDF to the Files API
curl -X POST https://api.anthropic.com/v1/files \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "anthropic-beta: files-api-2025-04-14" \
  -F "file=@document.pdf"

# Then use the returned file_id in your message
curl https://api.anthropic.com/v1/messages \
  -H "content-type: application/json" \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "anthropic-beta: files-api-2025-04-14" \
  -d '{
    "model": "claude-opus-4-6",
    "max_tokens": 1024,
    "messages": [{
      "role": "user",
      "content": [{
        "type": "document",
        "source": {
          "type": "file",
          "file_id": "file_abc123"
        }
      },
      {
        "type": "text",
        "text": "What are the key findings in this document?"
      }]
    }]
  }'
```

### How PDF support works

When you send a PDF to Claude, the following steps occur:

1. **The system extracts the contents of the document.** The system converts each page of the document into an image. The text from each page is extracted and provided alongside each page's image.
2. **Claude analyzes both the text and images** to better understand the document. Documents are provided as a combination of text and images for analysis. This allows users to ask for insights on visual elements of a PDF, such as charts, diagrams, and other non-textual content.
3. **Claude responds**, referencing the PDF's contents if relevant. Claude can reference both textual and visual content when it responds.

You can further improve performance by integrating PDF support with:

- **Prompt caching**: To improve performance for repeated analysis.
- **Batch processing**: For high-volume document processing.
- **Tool use**: To extract specific information from documents for use as tool inputs.

### Estimate your costs

The token count of a PDF file depends on the total text extracted from the document as well as the number of pages:

- **Text token costs**: Each page typically uses 1,500-3,000 tokens per page depending on content density. Standard API pricing applies with no additional PDF fees.
- **Image token costs**: Since each page is converted into an image, the same image-based cost calculations are applied.

You can use token counting to estimate costs for your specific PDFs.

## Optimize PDF processing

### Improve performance

Follow these best practices for optimal results:

- Place PDFs before text in your requests
- Use standard fonts
- Ensure text is clear and legible
- Rotate pages to proper upright orientation
- Use logical page numbers (from PDF viewer) in prompts
- Split large PDFs into chunks when needed
- Enable prompt caching for repeated analysis

### Scale your implementation

For high-volume processing, consider these approaches:

#### Use prompt caching

Cache PDFs to improve performance on repeated queries by adding `cache_control` with type `"ephemeral"` to your document block.

#### Process document batches

Use the Message Batches API for high-volume workflows to process multiple PDF analysis requests efficiently.
