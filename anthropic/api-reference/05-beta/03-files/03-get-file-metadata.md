# Beta - Get File Metadata

`GET /v1/files/{file_id}`

Get file metadata.

## Path Parameters

- **file_id**: `string` — ID of the File.

## Header Parameters

- **anthropic-beta**: `array of AnthropicBeta` (optional) — Optional header to specify the beta version(s) you want to use.

## Returns

### FileMetadata

`object { id, created_at, filename, mime_type, size_bytes, type, downloadable }`

- **id**: `string` — Unique object identifier.
- **created_at**: `string` — RFC 3339 datetime string representing when the file was created.
- **filename**: `string` — Original filename of the uploaded file.
- **mime_type**: `string` — MIME type of the file.
- **size_bytes**: `number` — Size of the file in bytes.
- **type**: `"file"` — Object type. For files, this is always "file".
- **downloadable**: `boolean` (optional) — Whether the file can be downloaded.

## Example Request

```bash
curl https://api.anthropic.com/v1/files/$FILE_ID?beta=true \
  -H 'anthropic-version: 2023-06-01' \
  -H 'anthropic-beta: files-api-2025-04-14' \
  -H "X-Api-Key: $ANTHROPIC_API_KEY"
```

## Response 200

```json
{
  "id": "file_011CNha8iCJcU1wXNR6q4V8w",
  "created_at": "2025-04-15T18:37:24.100435Z",
  "filename": "document.pdf",
  "mime_type": "application/pdf",
  "size_bytes": 102400,
  "type": "file",
  "downloadable": false
}
```
