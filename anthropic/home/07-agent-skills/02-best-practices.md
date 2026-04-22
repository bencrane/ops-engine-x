# Skill authoring best practices

Learn how to write effective Skills that Claude can discover and use successfully.

Good Skills are concise, well-structured, and tested with real usage. This guide provides practical authoring decisions to help you write Skills that Claude can discover and use effectively.

For conceptual background on how Skills work, see the Skills overview.

## Core principles

### Concise is key

The context window is a public good. Your Skill shares the context window with everything else Claude needs to know, including:
- The system prompt
- Conversation history
- Other Skills' metadata
- Your actual request

Not every token in your Skill has an immediate cost. At startup, only the metadata (name and description) from all Skills is pre-loaded. Claude reads SKILL.md only when the Skill becomes relevant, and reads additional files only as needed. However, being concise in SKILL.md still matters: once Claude loads it, every token competes with conversation history and other context.

### Default assumption: Claude is already very smart

Only add context Claude doesn't already have. Challenge each piece of information:
- "Does Claude really need this explanation?"
- "Can I assume Claude knows this?"
- "Does this paragraph justify its token cost?"

### Set appropriate degrees of freedom

Match the level of specificity to the task's fragility and variability.

**High freedom (text-based instructions):** Use when multiple approaches are valid, decisions depend on context, heuristics guide the approach.

**Medium freedom (pseudocode or scripts with parameters):** Use when a preferred pattern exists, some variation is acceptable, configuration affects behavior.

**Low freedom (specific scripts, few or no parameters):** Use when operations are fragile and error-prone, consistency is critical, a specific sequence must be followed.

### Test with all models you plan to use

Skills act as additions to models, so effectiveness depends on the underlying model. Test your Skill with all the models you plan to use it with.

Testing considerations by model:
- **Claude Haiku (fast, economical):** Does the Skill provide enough guidance?
- **Claude Sonnet (balanced):** Is the Skill clear and efficient?
- **Claude Opus (powerful reasoning):** Does the Skill avoid over-explaining?

## Skill structure

### Naming conventions

Use consistent naming patterns to make Skills easier to reference and discuss. Consider using gerund form (verb + -ing) for Skill names.

Remember that the name field must use lowercase letters, numbers, and hyphens only.

Good naming examples (gerund form):
- processing-pdfs
- analyzing-spreadsheets
- managing-databases
- testing-code
- writing-documentation

### Writing effective descriptions

The description field enables Skill discovery and should include both what the Skill does and when to use it.

Always write in third person. The description is injected into the system prompt, and inconsistent point-of-view can cause discovery problems.

Each Skill has exactly one description field. The description is critical for skill selection: Claude uses it to choose the right Skill from potentially 100+ available Skills.

Effective examples:

- **PDF Processing skill:** `description: Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.`
- **Excel Analysis skill:** `description: Analyze Excel spreadsheets, create pivot tables, generate charts. Use when analyzing Excel files, spreadsheets, tabular data, or .xlsx files.`

## Progressive disclosure patterns

SKILL.md serves as an overview that points Claude to detailed materials as needed, like a table of contents in an onboarding guide.

Practical guidance:
- Keep SKILL.md body under 500 lines for optimal performance
- Split content into separate files when approaching this limit
- Use patterns to organize instructions, code, and resources effectively

### Pattern 1: High-level guide with references

```markdown
---
name: pdf-processing
description: Extracts text and tables from PDF files, fills forms, and merges documents.
---

# PDF Processing

## Quick start
Extract text with pdfplumber:
...

## Advanced features
**Form filling**: See [FORMS.md](FORMS.md) for complete guide
**API reference**: See [REFERENCE.md](REFERENCE.md) for all methods
```

### Pattern 2: Domain-specific organization

For Skills with multiple domains, organize content by domain to avoid loading irrelevant context.

### Pattern 3: Conditional details

Show basic content, link to advanced content that Claude reads only when needed.

### Avoid deeply nested references

Keep references one level deep from SKILL.md. All reference files should link directly from SKILL.md.

### Structure longer reference files with table of contents

For reference files longer than 100 lines, include a table of contents at the top.

## Workflows and feedback loops

### Use workflows for complex tasks

Break complex operations into clear, sequential steps. For particularly complex workflows, provide a checklist that Claude can copy into its response and check off as it progresses.

### Implement feedback loops

Common pattern: Run validator -> fix errors -> repeat. This pattern greatly improves output quality.

## Content guidelines

### Avoid time-sensitive information

Don't include information that will become outdated. Use "old patterns" sections for deprecated approaches.

### Use consistent terminology

Choose one term and use it throughout the Skill. Consistency helps Claude understand and follow instructions.

## Common patterns

### Template pattern

Provide templates for output format. Match the level of strictness to your needs.

### Examples pattern

For Skills where output quality depends on seeing examples, provide input/output pairs just like in regular prompting.

### Conditional workflow pattern

Guide Claude through decision points with clear branching logic.

## Evaluation and iteration

### Build evaluations first

Create evaluations BEFORE writing extensive documentation. This ensures your Skill solves real problems rather than documenting imagined ones.

Evaluation-driven development:
1. Identify gaps: Run Claude on representative tasks without a Skill
2. Create evaluations: Build three scenarios that test these gaps
3. Establish baseline: Measure Claude's performance without the Skill
4. Write minimal instructions: Create just enough content to address the gaps
5. Iterate: Execute evaluations, compare against baseline, and refine

### Develop Skills iteratively with Claude

Work with one instance of Claude ("Claude A") to create a Skill that is used by other instances ("Claude B"). Claude A helps you design and refine instructions, while Claude B tests them in real tasks.

### Observe how Claude navigates Skills

Pay attention to how Claude actually uses them in practice. Watch for unexpected exploration paths, missed connections, overreliance on certain sections, and ignored content.

## Anti-patterns to avoid

- **Avoid Windows-style paths:** Always use forward slashes in file paths
- **Avoid offering too many options:** Provide a default with an escape hatch

## Advanced: Skills with executable code

### Solve, don't punt

When writing scripts for Skills, handle error conditions rather than punting to Claude.

### Provide utility scripts

Pre-made scripts are more reliable than generated code, save tokens, save time, and ensure consistency across uses.

### Use visual analysis

When inputs can be rendered as images, have Claude analyze them visually.

### Create verifiable intermediate outputs

Use the "plan-validate-execute" pattern to catch errors early.

### Package dependencies

Skills run in the code execution environment with platform-specific limitations:
- **claude.ai:** Can install packages from npm and PyPI
- **Claude API:** Has no network access and no runtime package installation

### Runtime environment

Skills run in a code execution environment with filesystem access, bash commands, and code execution capabilities.

### MCP tool references

If your Skill uses MCP tools, always use fully qualified tool names: `ServerName:tool_name`.

## Checklist for effective Skills

### Core quality
- Description is specific and includes key terms
- SKILL.md body is under 500 lines
- No time-sensitive information
- Consistent terminology throughout
- Progressive disclosure used appropriately

### Code and scripts
- Scripts solve problems rather than punt to Claude
- Error handling is explicit and helpful
- Required packages listed and verified as available
- Validation/verification steps for critical operations

### Testing
- At least three evaluations created
- Tested with Haiku, Sonnet, and Opus
- Tested with real usage scenarios
