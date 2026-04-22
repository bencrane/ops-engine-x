## Directive: Produce `MANAGED_AGENTS_CANONICAL.md`

### Objective

Read every file in `anthropic/managed-agents/` (including the `api-reference/` subfolder), then produce a single canonical reference document at `anthropic/MANAGED_AGENTS_CANONICAL.md`. This document must enable any AI agent reading it to accurately build, configure, modify, debug, and operate Anthropic Managed Agents — without needing to consult the source files.

### Source Files (read ALL of these, in order)

```
anthropic/managed-agents/00-overview.md
anthropic/managed-agents/01-quickstart.md
anthropic/managed-agents/02-agent-setup.md
anthropic/managed-agents/03-environments.md
anthropic/managed-agents/04-sessions.md
anthropic/managed-agents/05-events-and-streaming.md
anthropic/managed-agents/06-tools.md
anthropic/managed-agents/07-skills.md
anthropic/managed-agents/08-mcp-connector.md
anthropic/managed-agents/09-permission-policies.md
anthropic/managed-agents/10-vaults.md
anthropic/managed-agents/11-cloud-containers.md
anthropic/managed-agents/12-multi-agent.md
anthropic/managed-agents/13-define-outcomes.md
anthropic/managed-agents/14-memory.md
anthropic/managed-agents/api-reference/00-sessions.md
anthropic/managed-agents/api-reference/01-agents.md
anthropic/managed-agents/api-reference/02-environments.md
anthropic/managed-agents/api-reference/03-vaults.md
anthropic/managed-agents/api-reference/04-memory-stores.md
```

### Rules — Non-Negotiable

1. **Zero hallucination.** Every statement in the output must be directly derivable from the source files. Do not infer capabilities, guess at behaviors, or fill gaps with general knowledge. If the source docs are silent on something, do not cover it.

2. **Source attribution on every claim.** Every insight, parameter, constraint, guardrail, limitation, or behavioral note must include an inline source reference in the format:
   ```
   [Source: <filename>, "<section heading or context>"]
   ```
   Example: `Sessions are stateful and persist across reconnections. [Source: 04-sessions.md, "Session Lifecycle"]`

3. **No summarizing away critical detail.** If a source file specifies exact parameter names, enum values, default values, limits, error codes, or required headers — reproduce them exactly. This is a reference document, not a summary.

4. **Preserve all code examples.** If the source files contain code snippets that demonstrate setup, configuration, or API usage, include them in the canonical doc in the appropriate section. Attribute which file they came from.

5. **Call out non-obvious behavior explicitly.** Anything that could trip up a developer or AI agent — edge cases, ordering dependencies, silent failures, required-but-not-obvious configuration, version-specific behavior, mutual exclusions between features — must be surfaced in a dedicated "Gotchas & Guardrails" subsection within the relevant section AND collected into a top-level "Critical Gotchas" section at the end.

### Output Structure

Use this structure for `anthropic/MANAGED_AGENTS_CANONICAL.md`. Adapt section depth based on source material density, but do not skip any section.

```markdown
# Anthropic Managed Agents — Canonical Reference

> **Purpose:** [One-line statement of what this doc is and who it's for]
> **Source:** Synthesized from [N] source documents in `anthropic/managed-agents/`
> **Last generated:** [date]

---

## 1. Overview & Mental Model
What managed agents are, how they differ from raw API calls, the core
abstractions (agents, environments, sessions), and the high-level architecture.

## 2. Quickstart
Minimum viable setup from zero to a working agent. Include the exact
API calls / SDK usage, in order, with code.

## 3. Agent Setup & Configuration
How to create and configure an agent. All parameters, defaults,
and required vs. optional fields.

## 4. Environments
What environments are, how they relate to agents, configuration options,
lifecycle, and isolation guarantees.

## 5. Sessions
Session creation, lifecycle, state management, reconnection behavior,
expiration, and cleanup.

## 6. Events & Streaming
Event types, streaming protocol, SSE format, event ordering guarantees,
how to consume streams, and error/reconnection handling.

## 7. Tools
How to attach tools to agents, tool schemas, built-in vs. custom tools,
execution model, timeout behavior, and error handling.

## 8. Skills
What skills are, how they differ from tools, how to define and attach them,
and any interaction with tools.

## 9. MCP Connector
How to connect MCP servers to managed agents, configuration,
authentication, and limitations.

## 10. Permission Policies
Permission model, policy definition, default permissions,
how permissions interact with tools/skills/MCP, and escalation behavior.

## 11. Vaults (Secrets Management)
How to store and access secrets, vault types, access patterns from
within agent code, and security model.

## 12. Cloud Containers
What cloud containers are, when to use them, configuration,
resource limits, and networking.

## 13. Multi-Agent
How to set up multi-agent systems, agent-to-agent communication,
orchestration patterns, and limitations.

## 14. Defining Outcomes
How to define and measure agent outcomes, success criteria,
and evaluation.

## 15. Memory
Memory stores, persistence model, how agents read/write memory,
scope and isolation, and limits.

## 16. API Reference (Consolidated)
All API endpoints, request/response shapes, required headers,
auth, error codes, and rate limits. Organized by resource:
  - 16.1 Sessions API
  - 16.2 Agents API
  - 16.3 Environments API
  - 16.4 Vaults API
  - 16.5 Memory Stores API

## 17. Critical Gotchas & Guardrails
Collected from all sections — the non-obvious things that break,
the constraints that aren't where you'd expect them, the ordering
dependencies, the "you must do X before Y" rules. Each entry
attributed to its source.

## 18. Limitations & Known Constraints
Explicit limits (rate limits, size limits, feature gaps,
unsupported configurations) stated anywhere in the source docs.
```

### Style Guide

- **Tone:** Precise, technical, declarative. No marketing language, no "you can easily..." filler.
- **Format:** Use tables for parameter/field inventories. Use code blocks for all API calls, payloads, and configuration. Use blockquotes for direct quotes from source material when the exact wording matters.
- **Length:** As long as it needs to be. Completeness over brevity. This is a reference, not a blog post.
- **Cross-references:** When one section depends on concepts from another, use `(see Section N)` links.

### Quality Check Before Writing

After reading all source files and before writing the output, verify:
- [ ] You have read all 20 files completely (not just headers)
- [ ] You can attribute every planned section to specific source material
- [ ] You have identified at least 5 gotchas/guardrails from across the docs
- [ ] You have not invented any API endpoints, parameters, or behaviors

### Output Location

Write the completed document to:
```
anthropic/MANAGED_AGENTS_CANONICAL.md
```
