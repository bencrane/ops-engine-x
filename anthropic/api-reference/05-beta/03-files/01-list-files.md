# Beta - List Files

`GET /v1/files`

List files.

## Query Parameters

- **after_id**: `string` (optional) — ID of the object to use as a cursor for pagination.
- **before_id**: `string` (optional) — ID of the object to use as a cursor for pagination.
- **limit**: `number` (optional) — Number of items to return per page. Defaults to 20. Ranges from 1 to 1000.

## Header Parameters

- **anthropic-beta**: `array of AnthropicBeta` (optional) — Optional header to specify the beta version(s) you want to use.

## Returns

- **data**: `array of FileMetadata` — List of file metadata objects.
- **first_id**: `string` (optional) — ID of the first file in this page of results.
- **has_more**: `boolean` (optional) — Whether there are more results available.
- **last_id**: `string` (optional) — ID of the last file in this page of results.

## Example Request

```bash
curl https://api.anthropic.com/v1/files?beta=true \
  -H 'anthropic-version: 2023-06-01' \
  -H 'anthropic-beta: files-api-2025-04-14' \
  -H "X-Api-Key: $ANTHROPIC_API_KEY"
```

## Response 200

```json
{
  "data": [
    {
      "id": "file_011CNha8iCJcU1wXNR6q4V8w",
      "created_at": "2025-04-15T18:37:24.100435Z",
      "filename": "document.pdf",
      "mime_type": "application/pdf",
      "size_bytes": 102400,
      "type": "file",
      "downloadable": false
    }
  ],
  "first_id": "file_011CNha8iCJcU1wXNR6q4V8w",
  "has_more": true,
  "last_id": "file_013Zva2CMHLNnXjNJJKqJ2EF"
}
```
