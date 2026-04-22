# Skills for enterprise

Governance, security review, evaluation, and organizational guidance for deploying Agent Skills at enterprise scale.

This guide is for enterprise admins and architects who need to govern Agent Skills across an organization. It covers how to vet, evaluate, deploy, and manage Skills at scale. For authoring guidance, see best practices. For architecture details, see the Skills overview.

## Security review and vetting

Deploying Skills in an enterprise requires answering two distinct questions:
1. Are Skills safe in general? See the security considerations section in the overview for platform-level security details.
2. How do I vet a specific Skill? Use the risk assessment and review checklist below.

### Risk tier assessment

Evaluate each Skill against these risk indicators before approving deployment:

| Risk indicator | What to look for | Concern level |
|---------------|-----------------|---------------|
| Code execution | Scripts in the Skill directory (*.py, *.sh, *.js) | High: scripts run with full environment access |
| Instruction manipulation | Directives to ignore safety rules, hide actions from users, or alter Claude's behavior conditionally | High: can bypass security controls |
| MCP server references | Instructions referencing MCP tools (ServerName:tool_name) | High: extends access beyond the Skill itself |
| Network access patterns | URLs, API endpoints, fetch, curl, or requests calls | High: potential data exfiltration vector |
| Hardcoded credentials | API keys, tokens, or passwords in Skill files or scripts | High: secrets exposed in Git history and context window |
| File system access scope | Paths outside the Skill directory, broad glob patterns, path traversal (../) | Medium: may access unintended data |
| Tool invocations | Instructions directing Claude to use bash, file operations, or other tools | Medium: review what operations are performed |

### Review checklist

Before deploying any Skill from a third party or internal contributor, complete these steps:

1. **Read all Skill directory content.** Review SKILL.md, all referenced markdown files, and any bundled scripts or resources.
2. **Verify script behavior matches stated purpose.** Run scripts in a sandboxed environment and confirm outputs align with the Skill's description.
3. **Check for adversarial instructions.** Look for directives that tell Claude to ignore safety rules, hide actions from users, exfiltrate data through responses, or alter behavior based on specific inputs.
4. **Check for external URL fetches or network calls.** Search scripts and instructions for network access patterns.
5. **Verify no hardcoded credentials.** Credentials should use environment variables or secure credential stores, never appear in Skill content.
6. **Identify tools and commands the Skill instructs Claude to invoke.** List all bash commands, file operations, and tool references.
7. **Confirm redirect destinations.** If the Skill references external URLs, verify they point to expected domains.
8. **Verify no data exfiltration patterns.** Look for instructions that read sensitive data and then write, send, or encode it for external transmission.

> Never deploy Skills from untrusted sources without a full audit. A malicious Skill can direct Claude to execute arbitrary code, access sensitive files, or transmit data externally.

## Evaluating Skills before deployment

Skills can degrade agent performance if they trigger incorrectly, conflict with other Skills, or provide poor instructions. Require evaluation before any production deployment.

### What to evaluate

| Dimension | What it measures | Example failure |
|-----------|-----------------|-----------------|
| Triggering accuracy | Does the Skill activate for the right queries? | Skill triggers on every spreadsheet mention |
| Isolation behavior | Does the Skill work correctly on its own? | Skill references files that don't exist |
| Coexistence | Does adding this Skill degrade other Skills? | New Skill's description steals triggers |
| Instruction following | Does Claude follow the Skill's instructions? | Claude skips validation steps |
| Output quality | Does the Skill produce correct, useful results? | Generated reports have formatting errors |

### Evaluation requirements

Require Skill authors to submit evaluation suites with 3-5 representative queries per Skill, covering cases where the Skill should trigger, should not trigger, and ambiguous edge cases. Require testing across the models your organization uses.

### Using evaluations for lifecycle decisions

- **Declining trigger accuracy:** Update the Skill's description or instructions
- **Coexistence conflicts:** Consolidate overlapping Skills or narrow descriptions
- **Consistently low output quality:** Rewrite instructions or add validation steps
- **Persistent failures across updates:** Deprecate the Skill

## Skill lifecycle management

1. **Plan** - Identify workflows that are repetitive, error-prone, or require specialized knowledge
2. **Create and review** - Ensure the Skill author follows best practices; require security review and evaluation suite
3. **Test** - Require evaluations in isolation and alongside existing Skills
4. **Deploy** - Upload via the Skills API for workspace-wide access; document in internal registry
5. **Monitor** - Track usage patterns, collect feedback, re-run evaluations periodically
6. **Iterate or deprecate** - Require full evaluation suite to pass before promoting new versions

## Organizing Skills at scale

### Recall limits

Limit the number of Skills loaded simultaneously to maintain reliable recall accuracy. Each Skill's metadata competes for attention in the system prompt. API requests support a maximum of 8 Skills per request.

### Start specific, consolidate later

Encourage teams to start with narrow, workflow-specific Skills. As patterns emerge, consolidate related Skills into role-based bundles.

### Naming and cataloging

Maintain an internal registry for each Skill with:
- **Purpose:** What workflow the Skill supports
- **Owner:** Team or individual responsible for maintenance
- **Version:** Current deployed version
- **Dependencies:** MCP servers, packages, or external services required
- **Evaluation status:** Last evaluation date and results

### Role-based bundles

Group Skills by organizational role:
- **Sales team:** CRM operations, pipeline reporting, proposal generation
- **Engineering:** Code review, deployment workflows, incident response
- **Finance:** Report generation, data validation, audit preparation

## Distribution and version control

### Source control

Store Skill directories in Git for history tracking, code review via pull requests, and rollback capability.

### API-based distribution

The Skills API provides workspace-scoped distribution. Skills uploaded via the API are available to all workspace members.

### Versioning strategy

- **Production:** Pin Skills to specific versions. Run the full evaluation suite before promoting a new version.
- **Development and testing:** Use latest versions to validate changes before production promotion.
- **Rollback plan:** Maintain the previous version as a fallback.
- **Integrity verification:** Compute checksums of reviewed Skills and verify them at deployment time.

### Cross-surface considerations

Custom Skills do not sync across surfaces. Skills uploaded to the API are not available on claude.ai or in Claude Code, and vice versa. Maintain Skill source files in Git as the single source of truth.
