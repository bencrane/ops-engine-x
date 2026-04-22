# Beta - Download File

`GET /v1/files/{file_id}/content`

Download a file.

## Path Parameters

- **file_id**: `string` — ID of the File.

## Header Parameters

- **anthropic-beta**: `array of AnthropicBeta` (optional) — Optional header to specify the beta version(s) you want to use.

## Example Request

```bash
curl https://api.anthropic.com/v1/files/$FILE_ID/content?beta=true \
  -H 'anthropic-version: 2023-06-01' \
  -H 'anthropic-beta: files-api-2025-04-14' \
  -H "X-Api-Key: $ANTHROPIC_API_KEY"
```
