# Beta - Delete Skill

`DELETE /v1/skills/{skill_id}`

Delete a skill.

## Path Parameters

- **skill_id**: `string` — Unique identifier for the skill.

## Header Parameters

- **anthropic-beta**: `array of AnthropicBeta` (optional) — Optional header to specify the beta version(s) you want to use.

## Returns

- **id**: `string` — Unique identifier for the skill.
- **type**: `string` — Deleted object type. For Skills, this is always "skill_deleted".

## Example Request

```bash
curl https://api.anthropic.com/v1/skills/$SKILL_ID?beta=true \
  -X DELETE \
  -H 'anthropic-version: 2023-06-01' \
  -H 'anthropic-beta: skills-2025-10-02' \
  -H "X-Api-Key: $ANTHROPIC_API_KEY"
```

## Response 200

```json
{
  "id": "skill_01JAbcdefghijklmnopqrstuvw",
  "type": "skill_deleted"
}
```
