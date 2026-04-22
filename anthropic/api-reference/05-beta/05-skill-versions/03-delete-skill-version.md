# Beta - Delete Skill Version

`DELETE /v1/skills/{skill_id}/versions/{version}`

Delete a skill version.

## Path Parameters

- **skill_id**: `string` — Unique identifier for the skill.
- **version**: `string` — Version identifier for the skill. Each version is identified by a Unix epoch timestamp (e.g., "1759178010641129").

## Header Parameters

- **anthropic-beta**: `array of AnthropicBeta` (optional) — Optional header to specify the beta version(s) you want to use.

## Returns

- **id**: `string` — Version identifier for the skill.
- **type**: `string` — Deleted object type. For Skill Versions, this is always "skill_version_deleted".

## Example Request

```bash
curl https://api.anthropic.com/v1/skills/$SKILL_ID/versions/$VERSION?beta=true \
  -X DELETE \
  -H 'anthropic-version: 2023-06-01' \
  -H 'anthropic-beta: skills-2025-10-02' \
  -H "X-Api-Key: $ANTHROPIC_API_KEY"
```

## Response 200

```json
{
  "id": "1759178010641129",
  "type": "skill_version_deleted"
}
```
