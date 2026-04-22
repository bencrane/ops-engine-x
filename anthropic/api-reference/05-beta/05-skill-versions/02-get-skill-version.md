# Beta - Get Skill Version

`GET /v1/skills/{skill_id}/versions/{version}`

Get a specific skill version.

## Path Parameters

- **skill_id**: `string` — Unique identifier for the skill.
- **version**: `string` — Version identifier for the skill. Each version is identified by a Unix epoch timestamp (e.g., "1759178010641129").

## Header Parameters

- **anthropic-beta**: `array of AnthropicBeta` (optional) — Optional header to specify the beta version(s) you want to use.

## Returns

- **id**: `string` — Unique identifier for the skill version.
- **created_at**: `string` — ISO 8601 timestamp of when the skill version was created.
- **description**: `string` — Description of the skill version. Extracted from the SKILL.md file.
- **directory**: `string` — Directory name of the skill version.
- **name**: `string` — Human-readable name of the skill version. Extracted from the SKILL.md file.
- **skill_id**: `string` — Identifier for the skill that this version belongs to.
- **type**: `string` — Object type. For Skill Versions, this is always "skill_version".
- **version**: `string` — Version identifier (Unix epoch timestamp).

## Example Request

```bash
curl https://api.anthropic.com/v1/skills/$SKILL_ID/versions/$VERSION?beta=true \
  -H 'anthropic-version: 2023-06-01' \
  -H 'anthropic-beta: skills-2025-10-02' \
  -H "X-Api-Key: $ANTHROPIC_API_KEY"
```

## Response 200

```json
{
  "id": "skillver_01JAbcdefghijklmnopqrstuvw",
  "created_at": "2024-10-30T23:58:27.427722Z",
  "description": "A custom skill for doing something useful",
  "directory": "my-skill",
  "name": "my-skill",
  "skill_id": "skill_01JAbcdefghijklmnopqrstuvw",
  "type": "skill_version",
  "version": "1759178010641129"
}
```
