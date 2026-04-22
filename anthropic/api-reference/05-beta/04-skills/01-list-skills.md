# Beta - List Skills

`GET /v1/skills`

List skills.

## Query Parameters

- **limit**: `number` (optional) — Number of results to return per page. Maximum value is 100. Defaults to 20.
- **page**: `string` (optional) — Pagination token for fetching a specific page of results. Pass the value from a previous response's next_page field.
- **source**: `string` (optional) — Filter skills by source. Values: "custom" (user-created), "anthropic" (Anthropic-created).

## Header Parameters

- **anthropic-beta**: `array of AnthropicBeta` (optional) — Optional header to specify the beta version(s) you want to use.

## Returns

- **data**: `array of Skill` — List of skills.
  - **id**: `string` — Unique identifier for the skill.
  - **created_at**: `string` — ISO 8601 timestamp of when the skill was created.
  - **display_title**: `string` — Display title for the skill.
  - **latest_version**: `string` — The latest version identifier for the skill.
  - **source**: `string` — Source of the skill ("custom" or "anthropic").
  - **type**: `string` — Object type. For Skills, this is always "skill".
  - **updated_at**: `string` — ISO 8601 timestamp of when the skill was last updated.
- **has_more**: `boolean` — Whether there are more results available.
- **next_page**: `string` — Token for fetching the next page of results. If null, there are no more results.

## Example Request

```bash
curl https://api.anthropic.com/v1/skills?beta=true \
  -H 'anthropic-version: 2023-06-01' \
  -H 'anthropic-beta: skills-2025-10-02' \
  -H "X-Api-Key: $ANTHROPIC_API_KEY"
```

## Response 200

```json
{
  "data": [
    {
      "id": "skill_01JAbcdefghijklmnopqrstuvw",
      "created_at": "2024-10-30T23:58:27.427722Z",
      "display_title": "My Custom Skill",
      "latest_version": "1759178010641129",
      "source": "custom",
      "type": "type",
      "updated_at": "2024-10-30T23:58:27.427722Z"
    }
  ],
  "has_more": true,
  "next_page": "page_MjAyNS0wNS0xNFQwMDowMDowMFo="
}
```
