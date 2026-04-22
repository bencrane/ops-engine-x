# Agent Skills in the SDK

Extend Claude with specialized capabilities using Agent Skills in the Claude Agent SDK.

## Overview

Agent Skills extend Claude with specialized capabilities that Claude autonomously invokes when relevant. Skills are packaged as SKILL.md files containing instructions, descriptions, and optional supporting resources.

For comprehensive information about Skills, including benefits, architecture, and authoring guidelines, see the Agent Skills overview.

## How Skills Work with the SDK

When using the Claude Agent SDK, Skills are:

- **Defined as filesystem artifacts**: Created as SKILL.md files in specific directories (.claude/skills/)
- **Loaded from filesystem**: Skills are loaded from configured filesystem locations. You must specify settingSources (TypeScript) or setting_sources (Python) to load Skills from the filesystem
- **Automatically discovered**: Once filesystem settings are loaded, Skill metadata is discovered at startup from user and project directories; full content loaded when triggered
- **Model-invoked**: Claude autonomously chooses when to use them based on context
- **Enabled via allowed_tools**: Add "Skill" to your allowed_tools to enable Skills

> Unlike subagents (which can be defined programmatically), Skills must be created as filesystem artifacts. The SDK does not provide a programmatic API for registering Skills.

> **Default behavior**: By default, the SDK does not load any filesystem settings. To use Skills, you must explicitly configure settingSources: ['user', 'project'] (TypeScript) or setting_sources=["user", "project"] (Python) in your options.

## Using Skills with the SDK

To use Skills with the SDK, you need to:

1. Include "Skill" in your allowed_tools configuration
2. Configure settingSources/setting_sources to load Skills from the filesystem

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions

async def main():
    options = ClaudeAgentOptions(
        cwd="/path/to/project",  # Project with .claude/skills/
        setting_sources=["user", "project"],  # Load Skills from filesystem
        allowed_tools=["Skill", "Read", "Write", "Bash"],  # Enable Skill tool
    )

    async for message in query(
        prompt="Help me process this PDF document", options=options
    ):
        print(message)

asyncio.run(main())
```

## Skill Locations

Skills are loaded from filesystem directories based on your settingSources/setting_sources configuration:

- **Project Skills** (`.claude/skills/`): Shared with your team via git - loaded when setting_sources includes "project"
- **User Skills** (`~/.claude/skills/`): Personal Skills across all projects - loaded when setting_sources includes "user"
- **Plugin Skills**: Bundled with installed Claude Code plugins

## Creating Skills

Skills are defined as directories containing a SKILL.md file with YAML frontmatter and Markdown content. The description field determines when Claude invokes your Skill.

Example directory structure:

```
.claude/skills/processing-pdfs/
  SKILL.md
```

For complete guidance on creating Skills, see:
- Agent Skills in Claude Code: Complete guide with examples
- Agent Skills Best Practices: Authoring guidelines and naming conventions

## Tool Restrictions

> The allowed-tools frontmatter field in SKILL.md is only supported when using Claude Code CLI directly. It does not apply when using Skills through the SDK.

To control tool access for Skills in SDK applications, use allowedTools to pre-approve specific tools:

```python
options = ClaudeAgentOptions(
    setting_sources=["user", "project"],
    allowed_tools=["Skill", "Read", "Grep", "Glob"],
)

async for message in query(prompt="Analyze the codebase structure", options=options):
    print(message)
```

## Discovering Available Skills

To see which Skills are available in your SDK application, simply ask Claude:

```python
options = ClaudeAgentOptions(
    setting_sources=["user", "project"],
    allowed_tools=["Skill"],
)

async for message in query(prompt="What Skills are available?", options=options):
    print(message)
```

## Testing Skills

Test Skills by asking questions that match their descriptions:

```python
options = ClaudeAgentOptions(
    cwd="/path/to/project",
    setting_sources=["user", "project"],
    allowed_tools=["Skill", "Read", "Bash"],
)

async for message in query(prompt="Extract text from invoice.pdf", options=options):
    print(message)
```

## Troubleshooting

### Skills Not Found

**Check settingSources configuration**: Skills are only loaded when you explicitly configure settingSources/setting_sources. This is the most common issue:

```python
# Wrong - Skills won't be loaded
options = ClaudeAgentOptions(allowed_tools=["Skill"])

# Correct - Skills will be loaded
options = ClaudeAgentOptions(
    setting_sources=["user", "project"],  # Required to load Skills
    allowed_tools=["Skill"],
)
```

**Check working directory**: The SDK loads Skills relative to the cwd option:

```python
options = ClaudeAgentOptions(
    cwd="/path/to/project",  # Must contain .claude/skills/
    setting_sources=["user", "project"],
    allowed_tools=["Skill"],
)
```

**Verify filesystem location**:

```bash
# Check project Skills
ls .claude/skills/*/SKILL.md

# Check personal Skills
ls ~/.claude/skills/*/SKILL.md
```

### Skill Not Being Used

- Check the Skill tool is enabled: Confirm "Skill" is in your allowedTools
- Check the description: Ensure it's specific and includes relevant keywords

## Related Documentation

### Skills Guides

- Agent Skills in Claude Code: Complete Skills guide
- Agent Skills Overview: Conceptual overview, benefits, and architecture
- Agent Skills Best Practices: Authoring guidelines
- Agent Skills Cookbook: Example Skills and templates

### SDK Resources

- Subagents in the SDK: Similar filesystem-based agents with programmatic options
- Slash Commands in the SDK: User-invoked commands
- TypeScript SDK Reference: Complete API documentation
- Python SDK Reference: Complete API documentation
