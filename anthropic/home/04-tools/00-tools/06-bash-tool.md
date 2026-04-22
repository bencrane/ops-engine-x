# Bash tool

The bash tool enables Claude to execute shell commands in a persistent bash session, allowing system operations, script execution, and command-line automation.

## Overview

The bash tool provides Claude with:
- Persistent bash session that maintains state
- Ability to run any shell command
- Access to environment variables and working directory
- Command chaining and scripting capabilities

## Model compatibility

The bash tool (bash_20250124) is available on all Claude 4 models and Sonnet 3.7 (deprecated).

## Quick start

```python
import anthropic

client = anthropic.Anthropic()
response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    tools=[{"type": "bash_20250124", "name": "bash"}],
    messages=[{"role": "user", "content": "List all Python files in the current directory."}],
)
```

## How it works

1. Claude determines what command to run
2. You execute the command in a bash shell
3. Return the output (stdout and stderr) to Claude
4. Session state persists between commands

### Parameters

| Parameter | Required | Description |
|---|---|---|
| command | Yes* | The bash command to run |
| restart | No | Set to true to restart the bash session |

*Required unless using restart

## Security

The bash tool provides direct system access. Essential safety measures:

- Run in isolated environments (Docker/VM)
- Implement command filtering and allowlists
- Set resource limits (CPU, memory, disk)
- Log all executed commands
- Use minimal user permissions

## Pricing

The bash tool adds 245 input tokens to your API calls.

## Common patterns

- **Development workflows**: pytest, npm build, git operations
- **File operations**: Processing data, searching files, creating backups
- **System tasks**: Checking resources, process management, environment setup

## Git-based checkpointing

Git serves as a structured recovery mechanism in long-running agent workflows:
1. Capture a baseline before agent work begins
2. Commit per feature as rollback points
3. Reconstruct state at session start via git log
4. Revert on failure with git checkout

## Limitations

- No interactive commands (vim, less, password prompts)
- No GUI applications
- Session persists within conversation, lost between API calls
- Large outputs may be truncated
- Results returned after completion (no streaming)

## Combining with other tools

Most powerful when combined with the text editor. If also using the code execution tool, Claude has two separate execution environments -- clarify the distinction in your system prompt.
