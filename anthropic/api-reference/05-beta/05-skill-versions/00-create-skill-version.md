# Beta - Create Skill Version

`POST /v1/skills/{skill_id}/versions`

Create a new version of a skill.

## Path Parameters

- **skill_id**: `string` — Unique identifier for the skill.

## Header Parameters

- **anthropic-beta**: `array of AnthropicBeta` (optional) — Optional header to specify the beta version(s) you want to use.

## Body Parameters (Form Data)

- **files**: `array of string` (optional) — Files to upload for the skill. All files must be in the same top-level directory and must include a SKILL.md file at the root of that directory.

## Returns

- **id**: `string` — Unique identifier for the skill version.
- **created_at**: `string` — ISO 8601 timestamp of when the skill version was created.
- **description**: `string` — Description of the skill version. This is extracted from the SKILL.md file in the skill upload.
- **directory**: `string` — Directory name of the skill version. This is the top-level directory name that was extracted from the uploaded files.
- **name**: `string` — Human-readable name of the skill version. This is extracted from the SKILL.md file in the skill upload.
- **skill_id**: `string` — Identifier for the skill that this version belongs to.
- **type**: `string` — Object type. For Skill Versions, this is always "skill_version".
- **version**: `string` — Version identifier for the skill. Each version is identified by a Unix epoch timestamp (e.g., "1759178010641129").

## Example Request

```bash
curl https://api.anthropic.com/v1/skills/$SKILL_ID/versions?beta=true \
  -X POST \
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
