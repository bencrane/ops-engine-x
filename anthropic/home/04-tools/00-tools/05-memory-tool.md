# Memory tool

The memory tool enables Claude to store and retrieve information across conversations through a memory file directory. Claude can create, read, update, and delete files that persist between sessions, allowing it to build knowledge over time without keeping everything in the context window.

The memory tool operates client-side: you control where and how the data is stored through your own infrastructure.

This feature is eligible for Zero Data Retention (ZDR).

## Supported models

Available on Claude Opus 4.6, Opus 4.5, Opus 4.1, Opus 4, Sonnet 4.6, Sonnet 4.5, Sonnet 4, and Haiku 4.5.

## How it works

When enabled, Claude automatically checks its memory directory before starting tasks. Claude can create, read, update, and delete files in the /memories directory, then reference those memories in future conversations.

Since this is a client-side tool, your application executes memory operations locally.

## Basic usage

```shell
curl https://api.anthropic.com/v1/messages \
  --header "x-api-key: $ANTHROPIC_API_KEY" \
  --header "anthropic-version: 2023-06-01" \
  --header "content-type: application/json" \
  --data '{
    "model": "claude-opus-4-6",
    "max_tokens": 2048,
    "messages": [{"role": "user", "content": "Help me debug this Python function..."}],
    "tools": [{"type": "memory_20250818", "name": "memory"}]
  }'
```

## Tool commands

### view

Shows directory contents or file contents with optional line ranges.

```json
{"command": "view", "path": "/memories", "view_range": [1, 10]}
```

### create

Create a new file.

```json
{"command": "create", "path": "/memories/notes.txt", "file_text": "Meeting notes:\n- Discussed timeline\n"}
```

### str_replace

Replace text in a file.

```json
{"command": "str_replace", "path": "/memories/preferences.txt", "old_str": "Favorite color: blue", "new_str": "Favorite color: green"}
```

### insert

Insert text at a specific line.

```json
{"command": "insert", "path": "/memories/todo.txt", "insert_line": 2, "insert_text": "- Review docs\n"}
```

### delete

Delete a file or directory (recursively).

```json
{"command": "delete", "path": "/memories/old_file.txt"}
```

### rename

Rename or move a file/directory.

```json
{"command": "rename", "old_path": "/memories/draft.txt", "new_path": "/memories/final.txt"}
```

## Security considerations

- **Path traversal protection**: Validate all paths start with /memories, resolve canonical paths, reject traversal patterns like ../
- **Sensitive information**: Claude usually refuses to write sensitive info, but consider implementing stricter validation
- **File storage size**: Track sizes and prevent files from growing too large
- **Memory expiration**: Consider clearing files not accessed in extended time

## Using with Context Editing

The memory tool can be combined with context editing, which clears old tool results when conversation context grows beyond a threshold. Claude preserves important information to memory files before results are cleared.

## Using with Compaction

Memory can be paired with compaction (server-side summarization). For long-running workflows, use both: compaction keeps active context manageable, and memory persists important information across compaction boundaries.

## Multi-session software development pattern

For long-running projects spanning multiple sessions:

1. **Initializer session**: Set up progress log, feature checklist, and initialization scripts
2. **Subsequent sessions**: Read memory artifacts to recover full project state
3. **End-of-session update**: Update progress log with what was completed and what remains

Key principle: Work on one feature at a time and only mark complete after end-to-end verification.
