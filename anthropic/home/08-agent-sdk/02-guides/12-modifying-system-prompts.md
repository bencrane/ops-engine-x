# Modifying system prompts

Learn how to customize Claude's behavior by modifying system prompts using three approaches - output styles, systemPrompt with append, and custom system prompts.

System prompts define Claude's behavior, capabilities, and response style. The Claude Agent SDK provides three ways to customize system prompts: using output styles (persistent, file-based configurations), appending to Claude Code's prompt, or using a fully custom prompt.

## Understanding system prompts

A system prompt is the initial instruction set that shapes how Claude behaves throughout a conversation.

**Default behavior**: The Agent SDK uses a minimal system prompt by default. It contains only essential tool instructions but omits Claude Code's coding guidelines, response style, and project context. To include the full Claude Code system prompt, specify `systemPrompt: { preset: "claude_code" }` in TypeScript or `system_prompt={"type": "preset", "preset": "claude_code"}` in Python.

Claude Code's system prompt includes:

- Tool usage instructions and available tools
- Code style and formatting guidelines
- Response tone and verbosity settings
- Security and safety instructions
- Context about the current working directory and environment

## Methods of modification

### Method 1: CLAUDE.md files (project-level instructions)

CLAUDE.md files provide project-specific context and instructions that are automatically read by the Agent SDK when it runs in a directory. They serve as persistent "memory" for your project.

**Location and discovery:**

- Project-level: `CLAUDE.md` or `.claude/CLAUDE.md` in your working directory
- User-level: `~/.claude/CLAUDE.md` for global instructions across all projects

> **IMPORTANT**: The SDK only reads CLAUDE.md files when you explicitly configure settingSources (TypeScript) or setting_sources (Python). Include 'project' to load project-level CLAUDE.md. Include 'user' to load user-level CLAUDE.md. The claude_code system prompt preset does NOT automatically load CLAUDE.md - you must also specify setting sources.

**Example CLAUDE.md:**

```markdown
# Project Guidelines

## Code Style
- Use TypeScript strict mode
- Prefer functional components in React
- Always include JSDoc comments for public APIs

## Testing
- Run `npm test` before committing
- Maintain >80% code coverage
- Use jest for unit tests, playwright for E2E

## Commands
- Build: `npm run build`
- Dev server: `npm run dev`
- Type check: `npm run typecheck`
```

**Using CLAUDE.md with the SDK:**

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

const messages = [];
for await (const message of query({
  prompt: "Add a new React component for user profiles",
  options: {
    systemPrompt: {
      type: "preset",
      preset: "claude_code"
    },
    settingSources: ["project"] // Required to load CLAUDE.md from project
  }
})) {
  messages.push(message);
}
```

### Method 2: Output styles (persistent configurations)

Output styles are saved configurations that modify Claude's system prompt. They're stored as markdown files and can be reused across sessions and projects.

```typescript
import { writeFile, mkdir } from "fs/promises";
import { join } from "path";
import { homedir } from "os";

async function createOutputStyle(name: string, description: string, prompt: string) {
  const outputStylesDir = join(homedir(), ".claude", "output-styles");
  await mkdir(outputStylesDir, { recursive: true });

  const content = `---
name: ${name}
description: ${description}
---
${prompt}`;

  const filePath = join(outputStylesDir, `${name.toLowerCase().replace(/\s+/g, "-")}.md`);
  await writeFile(filePath, content, "utf-8");
}

await createOutputStyle(
  "Code Reviewer",
  "Thorough code review assistant",
  `You are an expert code reviewer.

For every code submission:
1. Check for bugs and security issues
2. Evaluate performance
3. Suggest improvements
4. Rate code quality (1-10)`
);
```

Once created, activate output styles via CLI (`/output-style [style-name]`) or settings (`.claude/settings.local.json`).

> Output styles are loaded when you include settingSources: ['user'] or settingSources: ['project'] in your options.

### Method 3: Using systemPrompt with append

You can use the Claude Code preset with an append property to add your custom instructions while preserving all built-in functionality.

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

const messages = [];
for await (const message of query({
  prompt: "Help me write a Python function to calculate fibonacci numbers",
  options: {
    systemPrompt: {
      type: "preset",
      preset: "claude_code",
      append: "Always include detailed docstrings and type hints in Python code."
    }
  }
})) {
  messages.push(message);
  if (message.type === "assistant") {
    console.log(message.message.content);
  }
}
```

### Method 4: Custom system prompts

You can provide a custom string as systemPrompt to replace the default entirely with your own instructions.

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

const customPrompt = `You are a Python coding specialist.

Follow these guidelines:
- Write clean, well-documented code
- Use type hints for all functions
- Include comprehensive docstrings
- Prefer functional programming patterns when appropriate
- Always explain your code choices`;

const messages = [];
for await (const message of query({
  prompt: "Create a data processing pipeline",
  options: {
    systemPrompt: customPrompt
  }
})) {
  messages.push(message);
  if (message.type === "assistant") {
    console.log(message.message.content);
  }
}
```

## Comparison of all four approaches

| Feature | CLAUDE.md | Output Styles | systemPrompt with append | Custom systemPrompt |
|---|---|---|---|---|
| Persistence | Per-project file | Saved as files | Session only | Session only |
| Reusability | Per-project | Across projects | Code duplication | Code duplication |
| Management | On filesystem | CLI + files | In code | In code |
| Default tools | Preserved | Preserved | Preserved | Lost (unless included) |
| Built-in safety | Maintained | Maintained | Maintained | Must be added |
| Environment context | Automatic | Automatic | Automatic | Must be provided |
| Customization level | Additions only | Replace default | Additions only | Complete control |
| Version control | With project | Yes | With code | With code |
| Scope | Project-specific | User or project | Code session | Code session |

## Use cases and best practices

### When to use CLAUDE.md

Best for: Project-specific coding standards, documenting project structure, listing common commands, team-shared context that should be version controlled.

> **Important**: To load CLAUDE.md files, you must explicitly set settingSources: ['project'] (TypeScript) or setting_sources=["project"] (Python).

### When to use output styles

Best for: Persistent behavior changes across sessions, team-shared configurations, specialized assistants (code reviewer, data scientist, DevOps).

### When to use systemPrompt with append

Best for: Adding specific coding standards, customizing output formatting, adding domain-specific knowledge, enhancing Claude Code's default behavior without losing tool instructions.

### When to use custom systemPrompt

Best for: Complete control over Claude's behavior, specialized single-session tasks, building specialized agents with unique behavior.

### Combining approaches

You can combine methods for maximum flexibility:

```typescript
import { query } from "@anthropic-ai/claude-agent-sdk";

const messages = [];
for await (const message of query({
  prompt: "Review this authentication module",
  options: {
    systemPrompt: {
      type: "preset",
      preset: "claude_code",
      append: `
For this review, prioritize:
- OAuth 2.0 compliance
- Token storage security
- Session management
`
    }
  }
})) {
  messages.push(message);
}
```

## See also

- Output styles - Complete output styles documentation
- TypeScript SDK guide - Complete SDK usage guide
- Configuration guide - General configuration options
