# Beta - Get Skill

`GET /v1/skills/{skill_id}`

Get a skill.

## Path Parameters

- **skill_id**: `string` — Unique identifier for the skill.

## Header Parameters

- **anthropic-beta**: `array of AnthropicBeta` (optional) — Optional header to specify the beta version(s) you want to use.

## Returns

- **id**: `string` — Unique identifier for the skill.
- **created_at**: `string` — ISO 8601 timestamp of when the skill was created.
- **display_title**: `string` — Display title for the skill.
- **latest_version**: `string` — The latest version identifier for the skill.
- **source**: `string` — Source of the skill ("custom" or "anthropic").
- **type**: `string` — Object type. For Skills, this is always "skill".
- **updated_at**: `string` — ISO 8601 timestamp of when the skill was last updated.

## Example Request

```bash
curl https://api.anthropic.com/v1/skills/$SKILL_ID?beta=true \
  -H 'anthropic-version: 2023-06-01' \
  -H 'anthropic-beta: skills-2025-10-02' \
  -H "X-Api-Key: $ANTHROPIC_API_KEY"
```

## Response 200

```json
{
  "id": "skill_01JAbcdefghijklmnopqrstuvw",
  "created_at": "2024-10-30T23:58:27.427722Z",
  "display_title": "My Custom Skill",
  "latest_version": "1759178010641129",
  "source": "custom",
  "type": "type",
  "updated_at": "2024-10-30T23:58:27.427722Z"
}
```
