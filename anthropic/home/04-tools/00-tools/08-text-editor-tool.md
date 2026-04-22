# Text editor tool

Claude can use an Anthropic-defined text editor tool to view and modify text files, helping you debug, fix, and improve your code or other text documents.

## Model compatibility

| Model | Tool Version |
|---|---|
| Claude 4.x models | text_editor_20250728 |
| Claude Sonnet 3.7 (deprecated) | text_editor_20250124 |

The text_editor_20250728 tool for Claude 4 models does not include the undo_edit command.

## When to use the text editor tool

- **Code debugging**: Identify and fix bugs
- **Code refactoring**: Improve structure, readability, and performance
- **Documentation generation**: Add docstrings, comments, or README files
- **Test creation**: Create unit tests based on understanding of the implementation

## Use the text editor tool

```shell
curl https://api.anthropic.com/v1/messages \
  -H "content-type: application/json" \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -d '{
    "model": "claude-opus-4-6",
    "max_tokens": 1024,
    "tools": [{"type": "text_editor_20250728", "name": "str_replace_based_edit_tool", "max_characters": 10000}],
    "messages": [{"role": "user", "content": "There'\''s a syntax error in my primes.py file. Can you help me fix it?"}]
  }'
```

## Text editor tool commands

### view

Examine file contents or list directory contents. Supports optional view_range for specific line ranges.

Parameters: command, path, view_range (optional)

### str_replace

Replace a specific string in a file with new text. Must match exactly one location.

Parameters: command, path, old_str, new_str

### create

Create a new file with specified content.

Parameters: command, path, file_text

### insert

Insert text at a specific line number.

Parameters: command, path, insert_line, insert_text

### undo_edit

Revert the last edit (Claude Sonnet 3.7 only, not supported in Claude 4 models).

Parameters: command, path

## Implementation

The text editor tool is schema-less -- the schema is built into Claude's model. Your application must:

1. Handle file operations (read, write, modify)
2. Process tool calls based on command type
3. Implement security measures (path validation, backups)
4. Return results to Claude

### Security considerations

- Validate file paths to prevent directory traversal
- Create backups before making changes
- Implement permissions checks
- Handle errors gracefully

## Pricing and token usage

| Tool | Additional input tokens |
|---|---|
| text_editor_20250728 (Claude 4.x) | 700 tokens |
| text_editor_20250124 (Claude Sonnet 3.7) | 700 tokens |
