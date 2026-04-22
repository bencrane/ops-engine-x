# Using Agent Skills with the API

Learn how to use Agent Skills to extend Claude's capabilities through the API.

Agent Skills extend Claude's capabilities through organized folders of instructions, scripts, and resources. This guide shows you how to use both pre-built and custom Skills with the Claude API.

For complete API reference including request/response schemas and all parameters, see:
- Skill Management API Reference - CRUD operations for Skills
- Skill Versions API Reference - Version management

> This feature is in beta and is not eligible for Zero Data Retention (ZDR). Beta features are excluded from ZDR.

## Overview

Skills integrate with the Messages API through the code execution tool. Whether using pre-built Skills managed by Anthropic or custom Skills you've uploaded, the integration shape is identical: both require code execution and use the same container structure.

### Using Skills

You can use Skills from two sources:

| Aspect | Anthropic Skills | Custom Skills |
|--------|-----------------|---------------|
| Type value | anthropic | custom |
| Skill IDs | Short names: pptx, xlsx, docx, pdf | Generated: skill_01AbCdEfGhIjKlMnOpQrStUv |
| Version format | Date-based: 20251013 or latest | Epoch timestamp: 1759178010641129 or latest |
| Management | Pre-built and maintained by Anthropic | Upload and manage via Skills API |
| Availability | Available to all users | Private to your workspace |

## Prerequisites

To use Skills, you need:
- Claude API key from the Console
- Beta headers:
  - `code-execution-2025-08-25` - Enables code execution (required for Skills)
  - `skills-2025-10-02` - Enables Skills API
  - `files-api-2025-04-14` - For uploading/downloading files to/from container
- Code execution tool enabled in your requests

## Using Skills in Messages

### Container Parameter

Skills are specified using the `container` parameter in the Messages API. You can include up to 8 Skills per request.

```shell
curl https://api.anthropic.com/v1/messages \
-H "x-api-key: $ANTHROPIC_API_KEY" \
-H "anthropic-version: 2023-06-01" \
-H "anthropic-beta: code-execution-2025-08-25,skills-2025-10-02" \
-H "content-type: application/json" \
-d '{
"model": "claude-opus-4-6",
"max_tokens": 4096,
"container": {
"skills": [
  {
    "type": "anthropic",
    "skill_id": "pptx",
    "version": "latest"
  }
]
},
"messages": [{
"role": "user",
"content": "Create a presentation about renewable energy"
}],
"tools": [{
"type": "code_execution_20250825",
"name": "code_execution"
}]
}'
```

### Downloading Generated Files

When Skills create documents, they return `file_id` attributes in the response. Use the Files API to download these files.

### Multi-Turn Conversations

Reuse the same container across multiple messages by specifying the container ID:

```python
# First request creates container
response1 = client.beta.messages.create(
    model="claude-opus-4-6",
    max_tokens=4096,
    betas=["code-execution-2025-08-25", "skills-2025-10-02"],
    container={
        "skills": [{"type": "anthropic", "skill_id": "xlsx", "version": "latest"}]
    },
    messages=[{"role": "user", "content": "Analyze this sales data"}],
    tools=[{"type": "code_execution_20250825", "name": "code_execution"}],
)

# Continue conversation with same container
response2 = client.beta.messages.create(
    model="claude-opus-4-6",
    max_tokens=4096,
    betas=["code-execution-2025-08-25", "skills-2025-10-02"],
    container={
        "id": response1.container.id,
        "skills": [{"type": "anthropic", "skill_id": "xlsx", "version": "latest"}],
    },
    messages=messages,
    tools=[{"type": "code_execution_20250825", "name": "code_execution"}],
)
```

### Long-Running Operations

Skills may perform operations that require multiple turns. Handle `pause_turn` stop reasons by providing the response back in a subsequent request to let Claude continue.

### Using Multiple Skills

Combine multiple Skills in a single request (up to 8) to handle complex workflows.

## Managing Custom Skills

### Creating a Skill

Upload your custom Skill to make it available in your workspace:

```shell
curl -X POST "https://api.anthropic.com/v1/skills" \
-H "x-api-key: $ANTHROPIC_API_KEY" \
-H "anthropic-version: 2023-06-01" \
-H "anthropic-beta: skills-2025-10-02" \
-F "display_title=Financial Analysis" \
-F "files[]=@financial_skill/SKILL.md;filename=financial_skill/SKILL.md" \
-F "files[]=@financial_skill/analyze.py;filename=financial_skill/analyze.py"
```

Requirements:
- Must include a SKILL.md file at the top level
- All files must specify a common root directory in their paths
- Total upload size must be under 8 MB

### Listing Skills

```shell
# List all Skills
curl "https://api.anthropic.com/v1/skills" \
-H "x-api-key: $ANTHROPIC_API_KEY" \
-H "anthropic-version: 2023-06-01" \
-H "anthropic-beta: skills-2025-10-02"

# List only custom Skills
curl "https://api.anthropic.com/v1/skills?source=custom" \
-H "x-api-key: $ANTHROPIC_API_KEY" \
-H "anthropic-version: 2023-06-01" \
-H "anthropic-beta: skills-2025-10-02"
```

### Deleting a Skill

To delete a Skill, you must first delete all its versions.

### Versioning

Skills support versioning to manage updates safely:
- **Anthropic-Managed Skills:** Versions use date format (20251013)
- **Custom Skills:** Auto-generated epoch timestamps; use "latest" for most recent

## How Skills Are Loaded

When you specify Skills in a container:
1. **Metadata Discovery:** Claude sees metadata for each Skill in the system prompt
2. **File Loading:** Skill files are copied into the container at `/skills/{directory}/`
3. **Automatic Use:** Claude automatically loads and uses Skills when relevant
4. **Composition:** Multiple Skills compose together for complex workflows

## Limits and Constraints

### Request Limits
- Maximum Skills per request: 8
- Maximum Skill upload size: 8 MB (all files combined)

### Environment Constraints
- No network access - Cannot make external API calls
- No runtime package installation - Only pre-installed packages available
- Isolated environment - Each request gets a fresh container

## Best Practices

### Version Management Strategy
- **Production:** Pin to specific versions for stability
- **Development:** Use latest for active development

### Prompt Caching Considerations
Changing the Skills list in your container breaks the cache. Keep your Skills list consistent across requests for best caching performance.

### Error Handling
Handle Skill-related errors gracefully by catching `BadRequestError` and checking for skill-specific errors.
