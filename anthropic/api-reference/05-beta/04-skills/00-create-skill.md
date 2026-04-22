# Beta - Create Skill

`POST /v1/skills`

Create a skill.

## Header Parameters

- **anthropic-beta**: `array of AnthropicBeta` (optional) — Optional header to specify the beta version(s) you want to use.

## Body Parameters (Form Data)

- **display_title**: `string` (optional) — Display title for the skill. This is a human-readable label that is not included in the prompt sent to the model.
- **files**: `array of string` (optional) — Files to upload for the skill. All files must be in the same top-level directory and must include a SKILL.md file at the root of that directory.

## Returns

- **id**: `string` — Unique identifier for the skill.
- **created_at**: `string` — ISO 8601 timestamp of when the skill was created.
- **display_title**: `string` — Display title for the skill.
- **latest_version**: `string` — The latest version identifier for the skill.
- **source**: `string` — Source of the skill. Values: "custom" (created by a user), "anthropic" (created by Anthropic).
- **type**: `string` — Object type. For Skills, this is always "skill".
- **updated_at**: `string` — ISO 8601 timestamp of when the skill was last updated.

## Example Request

```bash
curl https://api.anthropic.com/v1/skills?beta=true \
  -X POST \
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
