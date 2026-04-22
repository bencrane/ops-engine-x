# Beta - Delete File

`DELETE /v1/files/{file_id}`

Delete a file.

## Path Parameters

- **file_id**: `string` — ID of the File.

## Header Parameters

- **anthropic-beta**: `array of AnthropicBeta` (optional) — Optional header to specify the beta version(s) you want to use.

## Returns

### DeletedFile

`object { id, type }`

- **id**: `string` — ID of the deleted file.
- **type**: `"file_deleted"` (optional) — Deleted object type. For file deletion, this is always "file_deleted".

## Example Request

```bash
curl https://api.anthropic.com/v1/files/$FILE_ID?beta=true \
  -X DELETE \
  -H 'anthropic-version: 2023-06-01' \
  -H 'anthropic-beta: files-api-2025-04-14' \
  -H "X-Api-Key: $ANTHROPIC_API_KEY"
```

## Response 200

```json
{
  "id": "file_011CNha8iCJcU1wXNR6q4V8w",
  "type": "file_deleted"
}
```
