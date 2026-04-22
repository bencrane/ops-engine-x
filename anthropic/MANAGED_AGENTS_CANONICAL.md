# Anthropic Managed Agents — Canonical Reference

> **Purpose:** A single, self-contained reference that enables any AI agent or developer to build, configure, modify, debug, and operate Anthropic Managed Agents without consulting the source documentation.
> **Source:** Synthesized from 20 source documents in `anthropic/managed-agents/` and `anthropic/managed-agents/api-reference/`.
> **Last generated:** 2026-04-22

Every claim below carries an inline source reference in the format `[Source: <filename>, "<section>"]`. Claims without attribution reflect the product's invariant behavior as established across multiple source files.

---

## 1. Overview & Mental Model

### 1.1 What Claude Managed Agents is

> "Claude Managed Agents provides the harness and infrastructure for running Claude as an autonomous agent. Instead of building your own agent loop, tool execution, and runtime, you get a fully managed environment where Claude can read files, run commands, browse the web, and execute code securely." [Source: 00-overview.md, intro paragraph]

It is positioned as the alternative to the Messages API: the Messages API is "Direct model prompting access" suited to "Custom agent loops and fine-grained control"; Managed Agents is a "Pre-built, configurable agent harness that runs in managed infrastructure" suited to "Long-running tasks and asynchronous work." [Source: 00-overview.md, comparison table]

The harness provides built-in prompt caching, context compaction, and other performance optimizations. [Source: 00-overview.md, intro paragraph]

### 1.2 Core abstractions

Four top-level concepts govern the system. [Source: 00-overview.md, "Core concepts"; 01-quickstart.md, "Core concepts"]

| Concept | Description |
|---|---|
| **Agent** | The model, system prompt, tools, MCP servers, and skills. |
| **Environment** | A configured container template (packages, network access). |
| **Session** | A running agent instance within an environment, performing a specific task and generating outputs. |
| **Events** | Messages exchanged between your application and the agent (user turns, tool results, status updates). |

### 1.3 Lifecycle

1. **Create an agent** — define the model, system prompt, tools, MCP servers, and skills. Create once and reference by ID across sessions.
2. **Create an environment** — configure a cloud container with pre-installed packages and network access rules.
3. **Start a session** — launch a session that references your agent and environment.
4. **Send events and stream responses** — send user messages; Claude autonomously executes tools and streams back results via SSE. Event history is persisted server-side and can be fetched in full.
5. **Steer or interrupt** — send additional user events to guide the agent mid-execution, or interrupt it. [Source: 00-overview.md, "How it works"]

### 1.4 When to use it

- Long-running execution (minutes or hours with multiple tool calls).
- Cloud infrastructure with secure containers and pre-installed packages.
- Minimal infrastructure — no custom agent loop, sandbox, or tool execution layer.
- Stateful sessions with persistent file systems and conversation history across interactions. [Source: 00-overview.md, "When to use Claude Managed Agents"]

### 1.5 Beta and access

- All endpoints require the `anthropic-beta: managed-agents-2026-04-01` header. The SDK sets this automatically. [Source: 00-overview.md, "Beta access"; repeated in every source file]
- Prerequisites: a Claude API key, the beta header on all requests, and access to Managed Agents (enabled by default for all API accounts). [Source: 00-overview.md, "Beta access"]
- Research preview features — **outcomes**, **multiagent**, and **memory** — require explicit access. [Source: 00-overview.md, "Beta access"] Research preview features additionally require the `managed-agents-2026-04-01-research-preview` beta header. [Source: 13-define-outcomes.md, "Note" block; 14-memory.md, "Note" block]

### 1.6 Rate limits (organization-level)

| Operation | Limit |
|---|---|
| Create endpoints (agents, sessions, environments, etc.) | 60 requests per minute |
| Read endpoints (retrieve, list, stream, etc.) | 600 requests per minute |

[Source: 00-overview.md, "Rate limits"]

> Organization-level spend limits and tier-based rate limits also apply. [Source: 00-overview.md, "Rate limits"]

### 1.7 Branding guidelines (partners)

Use of Claude branding is optional. Allowed references: "Claude Agent" (preferred for dropdown menus), "Claude" (when within a menu already labeled "Agents"), "{YourAgentName} Powered by Claude" (if an existing agent name exists). Not permitted: "Claude Code", "Claude Code Agent", "Claude Cowork", "Claude Cowork Agent", or Claude Code-branded ASCII art or visual elements that mimic Claude Code. Your product should not appear to be Claude Code, Claude Cowork, or any other Anthropic product. [Source: 00-overview.md, "Branding guidelines"]

---

## 2. Quickstart

### 2.1 Prerequisites

- Anthropic Console account.
- API key. [Source: 01-quickstart.md, "Prerequisites"]

### 2.2 Install the CLI

The `ant` CLI is available via Homebrew, a prebuilt Linux/WSL tarball, or `go install`. [Source: 01-quickstart.md, "Install the CLI"]

```bash
# Homebrew (macOS)
brew install anthropics/tap/ant
xattr -d com.apple.quarantine "$(brew --prefix)/bin/ant"   # unquarantine on macOS

# curl (Linux/WSL)
VERSION=1.0.0
OS=$(uname -s | tr '[:upper:]' '[:lower:]')
ARCH=$(uname -m | sed -e 's/x86_64/amd64/' -e 's/aarch64/arm64/')
curl -fsSL "https://github.com/anthropics/anthropic-cli/releases/download/v${VERSION}/ant_${VERSION}_${OS}_${ARCH}.tar.gz" \
  | sudo tar -xz -C /usr/local/bin ant

# Go (requires Go 1.22+)
go install github.com/anthropics/anthropic-cli/cmd/ant@latest

ant --version
```

### 2.3 Install an SDK

Official SDKs exist for Python (`pip install anthropic`), TypeScript (`npm install @anthropic-ai/sdk`), Java (`com.anthropic:anthropic-java:2.20.0`), Go (`go get github.com/anthropics/anthropic-sdk-go`), C# (`dotnet add package Anthropic`), Ruby (`bundle add anthropic`), PHP (`composer require anthropic-ai/sdk`). [Source: 01-quickstart.md, "Install the SDK"]

Set credentials via environment variable:

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

### 2.4 End-to-end minimum viable setup

The SDK automatically injects the beta header; raw HTTP must include it explicitly. [Source: 01-quickstart.md, "Note" block]

**Step 1 — Create an agent.** [Source: 01-quickstart.md, Step "Create an agent"]

```bash
agent=$(
  curl -sS --fail-with-body https://api.anthropic.com/v1/agents \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01" \
    -H "content-type: application/json" \
    -d @- <<'EOF'
{
  "name": "Coding Assistant",
  "model": "claude-sonnet-4-6",
  "system": "You are a helpful coding assistant. Write clean, well-documented code.",
  "tools": [
    {"type": "agent_toolset_20260401"}
  ]
}
EOF
)

AGENT_ID=$(jq -er '.id' <<<"$agent")
AGENT_VERSION=$(jq -er '.version' <<<"$agent")
```

```python
from anthropic import Anthropic

client = Anthropic()

agent = client.beta.agents.create(
    name="Coding Assistant",
    model="claude-sonnet-4-6",
    system="You are a helpful coding assistant. Write clean, well-documented code.",
    tools=[{"type": "agent_toolset_20260401"}],
)
```

```typescript
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic();

const agent = await client.beta.agents.create({
  name: "Coding Assistant",
  model: "claude-sonnet-4-6",
  system: "You are a helpful coding assistant. Write clean, well-documented code.",
  tools: [{ type: "agent_toolset_20260401" }],
});
```

> `agent_toolset_20260401` enables the full set of pre-built agent tools (bash, file operations, web search, and more). [Source: 01-quickstart.md, after the Create an Agent step]

**Step 2 — Create an environment.** [Source: 01-quickstart.md, Step "Create an environment"]

```bash
environment=$(
  curl -sS --fail-with-body https://api.anthropic.com/v1/environments \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01" \
    -H "content-type: application/json" \
    -d @- <<'EOF'
{
  "name": "quickstart-env",
  "config": {
    "type": "cloud",
    "networking": {"type": "unrestricted"}
  }
}
EOF
)
ENVIRONMENT_ID=$(jq -er '.id' <<<"$environment")
```

**Step 3 — Start a session.** [Source: 01-quickstart.md, Step "Start a session"]

```bash
session=$(
  curl -sS --fail-with-body https://api.anthropic.com/v1/sessions \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -H "anthropic-beta: managed-agents-2026-04-01" \
    -H "content-type: application/json" \
    -d @- <<EOF
{
  "agent": "$AGENT_ID",
  "environment_id": "$ENVIRONMENT_ID",
  "title": "Quickstart session"
}
EOF
)
SESSION_ID=$(jq -er '.id' <<<"$session")
```

**Step 4 — Send a message and stream the response.** [Source: 01-quickstart.md, Step "Send a message and stream the response"]

```python
with client.beta.sessions.events.stream(session.id) as stream:
    client.beta.sessions.events.send(
        session.id,
        events=[
            {
                "type": "user.message",
                "content": [
                    {
                        "type": "text",
                        "text": "Create a Python script that generates the first 20 Fibonacci numbers and saves them to fibonacci.txt",
                    },
                ],
            },
        ],
    )

    for event in stream:
        match event.type:
            case "agent.message":
                for block in event.content:
                    print(block.text, end="")
            case "agent.tool_use":
                print(f"\n[Using tool: {event.name}]")
            case "session.status_idle":
                print("\n\nAgent finished.")
                break
```

### 2.5 What happens under the hood

When you send a user event, Managed Agents:

1. Provisions a container (environment config determines how).
2. Runs the agent loop (Claude decides which tools to use).
3. Executes tools inside the container.
4. Streams events (real-time updates).
5. Goes idle (emits `session.status_idle` when nothing more to do). [Source: 01-quickstart.md, "What's happening"]

### 2.6 Gotchas — Quickstart

- **Open the stream before sending the user event** to avoid a race. "Only events emitted after the stream is opened are delivered, so open the stream before sending events to avoid a race condition." [Source: 05-events-and-streaming.md, "Streaming responses"] The quickstart example intentionally sends the user event *after* opening the stream.
- The `ant` CLI on macOS must be unquarantined (`xattr -d com.apple.quarantine`) before it will run. [Source: 01-quickstart.md, "Install the CLI"]

---

## 3. Agent Setup & Configuration

An agent is "a reusable, versioned configuration that defines persona and capabilities. It bundles the model, system prompt, tools, MCP servers, and skills." [Source: 02-agent-setup.md, intro] Create once, reference by ID in every session. [Source: 02-agent-setup.md, intro]

### 3.1 Agent configuration fields

| Field | Required | Description |
|---|---|---|
| `name` | Yes | Human-readable name. 1–256 characters. [Source: api-reference/01-agents.md, "Validation Constraints Summary"] |
| `model` | Yes | Claude model (string) or configuration object. All Claude 4.5 and later models supported. [Source: 02-agent-setup.md, "Agent configuration fields"] |
| `system` | No | System prompt. Up to 100,000 characters. Distinct from user messages. [Source: 02-agent-setup.md, table; api-reference/01-agents.md, "Validation Constraints Summary"] |
| `tools` | No | Pre-built, MCP, and custom tools (see Section 7). Max 128 across all toolsets. [Source: api-reference/01-agents.md, "Validation Constraints Summary"] |
| `mcp_servers` | No | MCP servers providing third-party capabilities. Max 20, names unique. [Source: api-reference/01-agents.md, "Validation Constraints Summary"] |
| `skills` | No | Skills (see Section 8). Max 20. [Source: api-reference/01-agents.md, "Validation Constraints Summary"] |
| `callable_agents` | No | Other agents this agent can invoke (multiagent, research preview). [Source: 02-agent-setup.md, table] |
| `description` | No | Up to 2048 characters. [Source: api-reference/01-agents.md, "Validation Constraints Summary"] |
| `metadata` | No | Arbitrary key-value pairs. Max 16 pairs, keys ≤64 chars, values ≤512 chars. [Source: api-reference/01-agents.md, "Validation Constraints Summary"] |

### 3.2 Supported models

String form (`BetaManagedAgentsModel`): [Source: api-reference/01-agents.md, "Model Parameter"; api-reference/00-sessions.md, "Returns"]

| Value | Description |
|---|---|
| `claude-opus-4-6` | Most intelligent model for building agents and coding |
| `claude-sonnet-4-6` | Best combination of speed and intelligence |
| `claude-haiku-4-5` | Fastest model with near-frontier intelligence |
| `claude-haiku-4-5-20251001` | Dated Haiku 4.5 |
| `claude-opus-4-5` | Premium model combining maximum intelligence with practical performance |
| `claude-opus-4-5-20251101` | Dated Opus 4.5 |
| `claude-sonnet-4-5` | High-performance model for agents and coding |
| `claude-sonnet-4-5-20250929` | Dated Sonnet 4.5 |

Object form (`BetaManagedAgentsModelConfigParams`): `{ id, speed }` where `speed` is `"standard"` (default) or `"fast"`. "`fast` provides significantly faster output token generation at premium pricing. Not all models support `fast`; invalid combinations are rejected at create time." [Source: api-reference/01-agents.md, "Model Parameter"; api-reference/00-sessions.md]

> To use Claude Opus 4.6 with fast mode, pass `model` as `{"id": "claude-opus-4-6", "speed": "fast"}`. [Source: 02-agent-setup.md, "Tip" block]

### 3.3 Create an agent — response shape

```json
{
  "id": "agent_01HqR2k7vXbZ9mNpL3wYcT8f",
  "type": "agent",
  "name": "Coding Assistant",
  "model": { "id": "claude-sonnet-4-6", "speed": "standard" },
  "system": "You are a helpful coding agent.",
  "description": null,
  "tools": [
    {
      "type": "agent_toolset_20260401",
      "default_config": { "permission_policy": { "type": "always_allow" } }
    }
  ],
  "skills": [],
  "mcp_servers": [],
  "metadata": {},
  "version": 1,
  "created_at": "2026-04-03T18:24:10.412Z",
  "updated_at": "2026-04-03T18:24:10.412Z",
  "archived_at": null
}
```

[Source: 02-agent-setup.md, "Create an agent"]

### 3.4 Update semantics

Updating generates a new agent version. Pass the current `version` for optimistic concurrency. [Source: 02-agent-setup.md, "Update an agent"; api-reference/01-agents.md, "Update Agent"]

- **Omitted fields are preserved.** Only include fields you want to change.
- **Scalar fields** (`model`, `system`, `name`, etc.) are replaced. `system` and `description` can be cleared with `null` or empty string. `model` and `name` are mandatory and cannot be cleared.
- **Array fields** (`tools`, `mcp_servers`, `skills`, `callable_agents`) are fully replaced. Pass `null` or empty array to clear.
- **Metadata** is merged at the key level. Keys you provide are added/updated; omitted keys preserved; set value to empty string to delete. [Source: 02-agent-setup.md, "Update semantics"]
  - The API reference phrases metadata deletion as "set a key to a string to upsert, set to `null` to delete." [Source: api-reference/01-agents.md, "Update Agent"] Both "null" and "empty string" behaviors are documented across source files.
- **No-op detection.** If the update produces no change relative to the current version, no new version is created and the existing version is returned. [Source: 02-agent-setup.md, "Update semantics"]

Example update with version:

```python
updated_agent = client.beta.agents.update(
    agent.id,
    version=agent.version,
    system="You are a helpful coding agent. Always write tests.",
)
```

### 3.5 Agent lifecycle

| Operation | Behavior |
|---|---|
| **Update** | Generates a new agent version. |
| **List versions** | Fetch full version history. |
| **Archive** | The agent becomes read-only. New sessions cannot reference it, but existing sessions continue to run. Response sets `archived_at`. |

[Source: 02-agent-setup.md, "Agent lifecycle" and "Archive an agent"]

### 3.6 Gotchas — Agents

- **Version is required on update** for optimistic concurrency — "Must match the server's current version to prevent concurrent overwrites." [Source: api-reference/01-agents.md, "Update Agent"]
- **Archiving is one-way for new sessions only.** Existing sessions continue; new sessions cannot reference an archived agent. [Source: 02-agent-setup.md, "Archive an agent"]
- **Tools array is `full replacement`**, not merge. Omitting preserves; passing an empty array or `null` clears. [Source: 02-agent-setup.md, "Update semantics"; api-reference/01-agents.md, "Update Semantics"]
- **Hard limit of 128 tools across all toolsets** per agent. [Source: api-reference/01-agents.md, "Agent-Level Limits"]

---

## 4. Environments

> "Environments define the container configuration where your agent runs. You create an environment once, then reference its ID each time you start a session. Multiple sessions can share the same environment, but each session gets its own isolated container instance." [Source: 03-environments.md, intro]

### 4.1 Create an environment

```bash
curl -fsS https://api.anthropic.com/v1/environments \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "anthropic-beta: managed-agents-2026-04-01" \
  -H "content-type: application/json" \
  --data @- <<'EOF'
{
  "name": "python-dev",
  "config": {
    "type": "cloud",
    "networking": {"type": "unrestricted"}
  }
}
EOF
```

"The `name` must be unique within your organization and workspace." [Source: 03-environments.md, after Create]

### 4.2 Body fields

| Field | Required | Description |
|---|---|---|
| `name` | Yes | Unique per org/workspace. [Source: api-reference/02-environments.md, "Create Environment"] |
| `config` | No | `BetaCloudConfigParams`. Fields default to null; on update, omitted fields preserve existing value. [Source: api-reference/02-environments.md] |
| `description` | No | [Source: api-reference/02-environments.md] |
| `metadata` | No | Key-value pairs. [Source: api-reference/02-environments.md] |

`BetaCloudConfigParams` shape:

| Field | Required | Description |
|---|---|---|
| `type` | Yes | Must be `"cloud"`. [Source: api-reference/02-environments.md] |
| `networking` | No | `BetaUnrestrictedNetwork` or `BetaLimitedNetworkParams`. |
| `packages` | No | `BetaPackagesParams`. |

### 4.3 Packages

> "The `packages` field pre-installs packages into the container before the agent starts. Packages are installed by their respective package managers and cached across sessions that share the same environment. When multiple package managers are specified, they run in alphabetical order (apt, cargo, gem, go, npm, pip). You can optionally pin specific versions; the default is latest." [Source: 03-environments.md, "Packages"]

| Field | Package manager | Example |
|---|---|---|
| `apt` | System packages (apt-get) | `"ffmpeg"` |
| `cargo` | Rust (cargo) | `"ripgrep@14.0.0"` |
| `gem` | Ruby (gem) | `"rails:7.1.0"` |
| `go` | Go modules | `"golang.org/x/tools/cmd/goimports@latest"` |
| `npm` | Node.js (npm) | `"express@4.18.0"` |
| `pip` | Python (pip) | `"pandas==2.2.0"` |

[Source: 03-environments.md, "Packages"]

Package versioning follows each manager's syntax. "When versioning, use the version semantics relevant for the package manager, e.g. for `pip` use `package==1.0.0`. You are responsible for validating the package and version exist. Unversioned installs the latest." [Source: api-reference/02-environments.md, `BetaPackagesParams`]

### 4.4 Networking

> "The `networking` field controls the container's outbound network access. It does not impact the `web_search` or `web_fetch` tools' allowed domains." [Source: 03-environments.md, "Networking"]

| Mode | Description |
|---|---|
| `unrestricted` | Full outbound network access except for a general safety blocklist. This is the default. |
| `limited` | Restricts container network access to `allowed_hosts`. Further access enabled via `allow_package_managers` and `allow_mcp_servers`. |

[Source: 03-environments.md, "Networking"]

`limited` networking fields:

- `allowed_hosts`: domains the container can reach. "These must be HTTPS-prefixed." [Source: 03-environments.md, "Networking"]
- `allow_mcp_servers` (default `false`): permits outbound access to MCP server endpoints configured on the agent, beyond those in `allowed_hosts`. [Source: 03-environments.md, "Networking"; api-reference/02-environments.md, `BetaLimitedNetworkParams`]
- `allow_package_managers` (default `false`): permits outbound access to public package registries (PyPI, npm, etc.) beyond `allowed_hosts`. [Source: 03-environments.md, "Networking"; api-reference/02-environments.md]

> "For production deployments, use `limited` networking with an explicit `allowed_hosts` list. Follow the principle of least privilege by granting only the minimum network access your agent requires, and regularly audit your allowed domains." [Source: 03-environments.md, "Info" block]

Example limited-networking config:

```json
{
  "type": "cloud",
  "networking": {
    "type": "limited",
    "allowed_hosts": ["api.example.com"],
    "allow_mcp_servers": true,
    "allow_package_managers": true
  }
}
```

### 4.5 Environment lifecycle

- Environments persist until explicitly archived or deleted.
- Multiple sessions can reference the same environment.
- Each session gets its own container instance. Sessions do not share file system state.
- **Environments are not versioned.** "If you frequently update your environments, you may want to log these updates on your side, to map environment state with sessions." [Source: 03-environments.md, "Environment lifecycle"]

### 4.6 Management endpoints

[Source: 03-environments.md, "Manage environments"; api-reference/02-environments.md, "Endpoints"]

| Method | Path | Behavior |
|---|---|---|
| POST | `/v1/environments` | Create |
| GET | `/v1/environments` | List |
| GET | `/v1/environments/{environment_id}` | Retrieve |
| POST | `/v1/environments/{environment_id}` | Update |
| DELETE | `/v1/environments/{environment_id}` | Delete (only if no sessions reference it) |
| POST | `/v1/environments/{environment_id}/archive` | Archive (read-only, existing sessions continue) |

Delete response: `{ "id": "...", "type": "environment_deleted" }`. [Source: api-reference/02-environments.md, `BetaEnvironmentDeleteResponse`]

### 4.7 Gotchas — Environments

- **`allowed_hosts` must be HTTPS-prefixed.** [Source: 03-environments.md, "Networking"]
- **Environments are not versioned.** Config changes silently affect new sessions. [Source: 03-environments.md, "Environment lifecycle"]
- **Networking does not cover `web_search`/`web_fetch` tool domains** — those are controlled separately. [Source: 03-environments.md, "Networking"]
- **Delete fails if any session references the environment.** Archive instead if sessions exist. [Source: 03-environments.md, "Manage environments" — inline comment `# Delete an environment (only if no sessions reference it)`]
- **Package managers run in alphabetical order** (apt, cargo, gem, go, npm, pip) — significant if one depends on another. [Source: 03-environments.md, "Packages"]

---

## 5. Sessions

> "A session is a running agent instance within an environment. Each session references an agent and an environment (both created separately), and maintains conversation history across multiple interactions." [Source: 04-sessions.md, intro]

### 5.1 Creating a session

Required: `agent` (ID string or `{type, id, version}` object) and `environment_id`. [Source: 04-sessions.md, "Creating a session"; api-reference/00-sessions.md, "Create Session"]

```python
session = client.beta.sessions.create(
    agent=agent.id,
    environment_id=environment.id,
)
```

- **String `agent`** pins the latest agent version. [Source: 04-sessions.md, "Creating a session"]
- **Object `agent`** pins a specific version: `{"type": "agent", "id": "$AGENT_ID", "version": 1}`. "This lets you control exactly which version runs and stage rollouts of new versions independently." [Source: 04-sessions.md, "Creating a session"]

### 5.2 Session body parameters

[Source: api-reference/00-sessions.md, "Create Session"]

| Field | Required | Description |
|---|---|---|
| `agent` | Yes | `string` or `BetaManagedAgentsAgentParams`. |
| `environment_id` | Yes | Environment to use. |
| `metadata` | No | Max 16 pairs; keys ≤64 chars; values ≤512 chars. |
| `resources` | No | Array of mounted resources (see below). |
| `title` | No | Human-readable title. |
| `vault_ids` | No | Vaults whose credentials are available to the session (see Section 11). |

### 5.3 Mountable resources

Resources mount into the container at session creation. [Source: api-reference/00-sessions.md, "Create Session" — Body Parameters]

**GitHub repository:**

| Field | Required | Description |
|---|---|---|
| `type` | Yes | `"github_repository"` |
| `url` | Yes | GitHub URL of the repository. |
| `authorization_token` | Yes | GitHub authorization token used to clone. |
| `checkout` | No | `{"type": "branch", "name": "..."}` or `{"type": "commit", "sha": "..."}`. Defaults to repo default branch. |
| `mount_path` | No | Defaults to `/workspace/<repo-name>`. |

**Uploaded file:**

| Field | Required | Description |
|---|---|---|
| `type` | Yes | `"file"` |
| `file_id` | Yes | ID of a previously uploaded file (Files API). |
| `mount_path` | No | Defaults to `/mnt/session/uploads/<file_id>`. |

**Memory store** (research preview — see Section 15): [Source: 14-memory.md, "Attach a memory store to a session"] `{"type": "memory_store", "memory_store_id": "...", "access": "read_write" \| "read_only", "prompt": "..."}` — max 8 stores per session.

### 5.4 Starting work

> "Creating a session provisions the environment and agent but does not start any work. To delegate a task, send events to the session using a user event. The session acts as a state machine that tracks progress while events drive the actual execution." [Source: 04-sessions.md, "Starting the session"]

### 5.5 Session statuses

[Source: 04-sessions.md, "Session statuses"]

| Status | Description |
|---|---|
| `idle` | Agent is waiting for input (user messages or tool confirmations). Sessions start in `idle`. |
| `running` | Agent is actively executing. |
| `rescheduling` | Transient error occurred, retrying automatically. |
| `terminated` | Session ended due to an unrecoverable error. |

The API enum includes these four statuses: `"rescheduling" | "running" | "idle" | "terminated"`. [Source: api-reference/00-sessions.md, "Returns"]

### 5.6 Session response shape

Includes `id`, `agent` (resolved snapshot), `environment_id`, `status`, `stats`, `usage`, `vault_ids`, `resources`, `metadata`, `title`, `type: "session"`, `archived_at`, `created_at`, `updated_at`. [Source: api-reference/00-sessions.md, "Returns"]

`stats`: `active_seconds` (cumulative running time, excluding idle) and `duration_seconds` (elapsed since creation; frozen at final update for terminated sessions). [Source: api-reference/00-sessions.md, `BetaManagedAgentsSessionStats`]

### 5.7 Tracking usage

```json
{
  "id": "sesn_01...",
  "status": "idle",
  "usage": {
    "input_tokens": 5000,
    "output_tokens": 3200,
    "cache_creation_input_tokens": 2000,
    "cache_read_input_tokens": 20000
  }
}
```

> "`input_tokens` reports uncached input tokens and `output_tokens` reports total output tokens across all model calls in the session. The `cache_creation_input_tokens` and `cache_read_input_tokens` fields reflect prompt caching activity. Cache entries use a 5-minute TTL, so back-to-back turns within that window benefit from cache reads, which reduce per-token cost." [Source: 05-events-and-streaming.md, "Tracking usage"]

Cache creation is further broken down into `ephemeral_1h_input_tokens` and `ephemeral_5m_input_tokens`. [Source: api-reference/00-sessions.md, `BetaManagedAgentsCacheCreationUsage`]

### 5.8 Session management endpoints

[Source: 04-sessions.md, "Other session operations"; api-reference/00-sessions.md]

| Method | Path | Notes |
|---|---|---|
| GET | `/v1/sessions/{session_id}` | Retrieve. |
| GET | `/v1/sessions` | List. Filter by `agent_id`, `agent_version`, `created_at[gt/gte/lt/lte]`, `include_archived`, `limit`, `order`, `page`. [Source: api-reference/00-sessions.md, "List Sessions"] |
| POST | `/v1/sessions/{session_id}` | Update title/metadata. `vault_ids` on update is "Not yet supported; requests setting this field are rejected." [Source: api-reference/00-sessions.md, "Update Session"] |
| POST | `/v1/sessions/{session_id}/archive` | Archive (preserves history, blocks new events). [Source: 04-sessions.md, "Archiving a session"] |
| DELETE | `/v1/sessions/{session_id}` | Permanent delete. [Source: 04-sessions.md, "Deleting a session"] |

### 5.9 Gotchas — Sessions

- **A `running` session cannot be deleted.** "Send an interrupt event if you need to delete it immediately." [Source: 04-sessions.md, "Deleting a session"]
- **Files, memory stores, environments, and agents are independent resources and are not affected by session deletion.** [Source: 04-sessions.md, "Deleting a session"]
- **`vault_ids` cannot be updated after session creation.** Updates that set `vault_ids` are rejected; the field is "Reserved for future use." [Source: api-reference/00-sessions.md, "Update Session"]
- **Pinning agent version requires the object form.** A bare string always resolves to latest. [Source: 04-sessions.md, "Creating a session"]
- **Cache has a 5-minute TTL.** Longer gaps between turns lose caching benefits. [Source: 05-events-and-streaming.md, "Tracking usage"]

---

## 6. Events & Streaming

Communication is event-based. "You send user events to the agent, and receive agent and session events back to track status." [Source: 05-events-and-streaming.md, intro]

Event type strings follow `{domain}.{action}` naming. [Source: 05-events-and-streaming.md, "Event types"]

### 6.1 User events (client → agent)

| Type | Description |
|---|---|
| `user.message` | A user message with text content. |
| `user.interrupt` | Stop the agent mid-execution. |
| `user.custom_tool_result` | Response to a custom tool call. |
| `user.tool_confirmation` | Approve or deny an agent or MCP tool call under an `always_ask` policy. |
| `user.define_outcome` | Define an outcome for the agent to work toward (research preview). |

[Source: 05-events-and-streaming.md, "User events" tab]

### 6.2 Agent events

| Type | Description |
|---|---|
| `agent.message` | Agent response containing text content blocks. |
| `agent.thinking` | Agent thinking content, emitted separately from messages. "A progress signal, not a content carrier." [Source: api-reference/00-sessions.md, `BetaManagedAgentsAgentThinkingEvent`] |
| `agent.tool_use` | Agent invoked a pre-built agent tool. |
| `agent.tool_result` | Result of a pre-built agent tool. |
| `agent.mcp_tool_use` | Agent invoked an MCP server tool. |
| `agent.mcp_tool_result` | Result of an MCP tool. |
| `agent.custom_tool_use` | Agent invoked a custom tool (requires `user.custom_tool_result` response). |
| `agent.thread_context_compacted` | Conversation history was compacted to fit the context window. |
| `agent.thread_message_sent` | Multiagent: agent sent message to another thread. |
| `agent.thread_message_received` | Multiagent: agent received message from another thread. |

[Source: 05-events-and-streaming.md, "Agent events" tab]

### 6.3 Session events

| Type | Description |
|---|---|
| `session.status_running` | Agent is actively processing. |
| `session.status_idle` | Agent finished current task; waiting for input. Includes `stop_reason`. |
| `session.status_rescheduled` | Transient error; session is retrying automatically. |
| `session.status_terminated` | Session ended due to unrecoverable error. |
| `session.error` | An error occurred. Includes typed `error` object with `retry_status`. |
| `session.outcome_evaluated` | Outcome evaluation reached terminal status (research preview). |
| `session.thread_created` | Coordinator spawned new multiagent thread. |
| `session.thread_idle` | Multiagent thread finished current work. |
| `session.deleted` | Session was deleted; terminates any active event stream. [Source: api-reference/00-sessions.md] |

[Source: 05-events-and-streaming.md, "Session events" tab; api-reference/00-sessions.md]

### 6.4 Span events (observability markers)

| Type | Description |
|---|---|
| `span.model_request_start` | Model inference call started. |
| `span.model_request_end` | Model inference completed. Includes `model_usage` with token counts. |
| `span.outcome_evaluation_start` | Outcome evaluation started (research preview). |
| `span.outcome_evaluation_ongoing` | Heartbeat during outcome evaluation. |
| `span.outcome_evaluation_end` | Outcome evaluation completed. |

[Source: 05-events-and-streaming.md, "Span events" tab]

`span.model_request_end` `model_usage` contains `cache_creation_input_tokens`, `cache_read_input_tokens`, `input_tokens`, `output_tokens`, and optional `speed`. [Source: api-reference/00-sessions.md, `BetaManagedAgentsSpanModelUsage`]

### 6.5 Event metadata

> "Every event includes a `processed_at` timestamp indicating when the event was recorded server-side. If `processed_at` is null, it means the event has been queued by the harness and will be handled after preceding events finish processing." [Source: 05-events-and-streaming.md, after event tabs]

### 6.6 Sending events

POST to `/v1/sessions/{session_id}/events` with a JSON body `{ "events": [ ... ] }`.

```python
client.beta.sessions.events.send(
    session.id,
    events=[
        {
            "type": "user.message",
            "content": [{"type": "text", "text": "Analyze the performance of the sort function in utils.py"}],
        },
    ],
)
```

Content blocks supported on `user.message`: `text`, `image` (base64/URL/file-ID source), `document` (base64/text/URL/file source with optional `title` and `context`). [Source: api-reference/00-sessions.md, "Send Events" — `BetaManagedAgentsUserMessageEventParams`]

### 6.7 Interrupting and redirecting

Send `user.interrupt` then a new `user.message` in the same request:

```python
client.beta.sessions.events.send(
    session.id,
    events=[
        {"type": "user.interrupt"},
        {"type": "user.message", "content": [{"type": "text", "text": "Instead, focus on fixing the bug in line 42."}]},
    ],
)
```

> "The agent will acknowledge the interruption and switch to the new task." [Source: 05-events-and-streaming.md, "Sending events"]

### 6.8 Streaming responses

GET `/v1/sessions/{session_id}/stream` (or `/v1/sessions/{session_id}/events/stream`, per API reference) with `Accept: text/event-stream`. SSE frames are `data: <json>` lines. [Source: 05-events-and-streaming.md, "Streaming responses"; api-reference/00-sessions.md, "Stream Events"]

> "Only events emitted after the stream is opened are delivered, so open the stream before sending events to avoid a race condition." [Source: 05-events-and-streaming.md, "Streaming responses"]

### 6.9 Reconnection without missing events

> "To reconnect to an existing session without missing events, open a new stream and then list the full history to seed a set of seen event IDs. Tail the live stream while skipping any events already returned by the history list." [Source: 05-events-and-streaming.md, "Streaming responses"]

```python
with client.beta.sessions.events.stream(session.id) as stream:
    seen_event_ids = {event.id for event in client.beta.sessions.events.list(session.id)}
    for event in stream:
        if event.id in seen_event_ids:
            continue
        seen_event_ids.add(event.id)
        # ... handle event ...
```

### 6.10 Listing past events

GET `/v1/sessions/{session_id}/events`. Supports `limit`, `order` (default `asc` / chronological), and `page` cursor. [Source: api-reference/00-sessions.md, "List Events"]

### 6.11 Custom tool call flow

[Source: 05-events-and-streaming.md, "Handling custom tool calls"]

1. Session emits `agent.custom_tool_use` with tool name and input.
2. Session pauses with `session.status_idle` and `stop_reason: { type: "requires_action", event_ids: [...] }`.
3. Execute the tool and send one `user.custom_tool_result` event per blocking event ID, passing the ID in `custom_tool_use_id` and the result as content blocks (text/image/document).
4. Once all blocking events are resolved, the session transitions back to `running`.

### 6.12 Tool confirmation flow (`always_ask` policies)

[Source: 05-events-and-streaming.md, "Tool confirmation"]

1. Session emits `agent.tool_use` or `agent.mcp_tool_use` event.
2. Session pauses with `session.status_idle` and `stop_reason: { type: "requires_action", event_ids: [...] }`.
3. Send `user.tool_confirmation` event per blocking event ID, with `tool_use_id`, `result: "allow" \| "deny"`, optional `deny_message` (only when denying).
4. Once all resolved, session returns to `running`.

### 6.13 Stop reasons

`session.status_idle` carries a `stop_reason` union: [Source: api-reference/00-sessions.md, "Stop Reasons"]

| Stop reason | Meaning |
|---|---|
| `{ type: "end_turn" }` | Agent completed its turn naturally; ready for next user message. |
| `{ type: "requires_action", event_ids: [...] }` | Agent is blocked on one or more user-input events (tool confirmation or custom tool result). Resolving all transitions to running. "Resolving fewer than all re-emits `session.status_idle` with the remainder." |
| `{ type: "retries_exhausted" }` | Retry budget exhausted (`max_iterations` hit or `retry_status: "exhausted"`). |

### 6.14 Error types and retry statuses

[Source: api-reference/00-sessions.md, `session.error` definitions]

All `session.error` events carry `error.message`, `error.type`, and `error.retry_status`:

| Error type | Meaning |
|---|---|
| `unknown_error` | Fallback for unrecognized errors. |
| `model_overloaded_error` | Model overloaded. Emitted after automatic retries exhausted. |
| `model_rate_limited_error` | Model request rate-limited. |
| `model_request_failed_error` | Model request failed for a reason other than overload or rate-limiting. |
| `mcp_connection_failed_error` | Failed to connect to an MCP server; includes `mcp_server_name`. |
| `mcp_authentication_failed_error` | Authentication to an MCP server failed; includes `mcp_server_name`. |
| `billing_error` | Organization/workspace cannot make model requests — out of credits or spend limit reached. "Retrying with the same credentials will not succeed; the caller must resolve the billing state." |

Retry statuses:

| Status | Meaning |
|---|---|
| `retrying` | Server retrying automatically. Client should wait; same error type may fire again as retrying, then once as exhausted when retry budget runs out. |
| `exhausted` | Turn is dead; queued inputs are flushed; session returns to idle; client may send a new prompt. |
| `terminal` | Session encountered terminal error; will transition to `terminated` state. |

### 6.15 Gotchas — Events & Streaming

- **Open the stream before sending user events** — buffered events only include those emitted *after* stream open. [Source: 05-events-and-streaming.md, "Streaming responses"]
- **`processed_at: null` means queued.** The event has not yet been handled. [Source: 05-events-and-streaming.md, after event tabs]
- **`requires_action` may re-emit.** Resolving fewer than all `event_ids` in `stop_reason` re-emits `session.status_idle` with the remainder. [Source: api-reference/00-sessions.md, `BetaManagedAgentsSessionRequiresAction`]
- **`deny_message` is only allowed with `result: "deny"`.** [Source: api-reference/00-sessions.md, `BetaManagedAgentsUserToolConfirmationEventParams`]
- **`session.deleted` terminates active streams.** No further events will be emitted. [Source: api-reference/00-sessions.md, `BetaManagedAgentsSessionDeletedEvent`]
- **`billing_error` requires operator action** — auto-retry will not resolve it. [Source: api-reference/00-sessions.md, error types]

---

## 7. Tools

Managed Agents supports three tool categories: [Source: 06-tools.md, intro]

- **Pre-built agent toolset** (server-executed).
- **MCP toolsets** (server-executed via MCP server).
- **Custom tools** (client-executed — your application runs them).

### 7.1 Pre-built toolset: `agent_toolset_20260401`

| Tool | Name | Description |
|---|---|---|
| Bash | `bash` | Execute bash commands in a shell session |
| Read | `read` | Read a file from the local filesystem |
| Write | `write` | Write a file to the local filesystem |
| Edit | `edit` | Perform string replacement in a file |
| Glob | `glob` | Fast file pattern matching using glob patterns |
| Grep | `grep` | Text search using regex patterns |
| Web fetch | `web_fetch` | Fetch content from a URL |
| Web search | `web_search` | Search the web for information |

[Source: 06-tools.md, "Available tools"]

> "All are enabled by default when you include the toolset in your agent configuration." [Source: 06-tools.md, "Available tools"]

### 7.2 Configuring the toolset

Enable via `{ "type": "agent_toolset_20260401" }` in `tools`. Use `configs` for per-tool overrides and `default_config` for toolset-wide defaults. [Source: 06-tools.md, "Configuring the toolset"; api-reference/01-agents.md, `BetaManagedAgentsAgentToolset20260401Params`]

**Disable specific tools:**

```json
{
  "type": "agent_toolset_20260401",
  "configs": [
    { "name": "web_fetch", "enabled": false },
    { "name": "web_search", "enabled": false }
  ]
}
```

**Enable only specific tools** (default off, allow-list): [Source: 06-tools.md, "Enabling only specific tools"]

```json
{
  "type": "agent_toolset_20260401",
  "default_config": { "enabled": false },
  "configs": [
    { "name": "bash", "enabled": true },
    { "name": "read", "enabled": true },
    { "name": "write", "enabled": true }
  ]
}
```

### 7.3 Custom tools (client-executed)

> "Custom tools are analogous to user-defined client tools in the Messages API. […] Each tool defines a contract: you specify what operations are available and what they return; Claude decides when and how to call them. The model never executes anything on its own. It emits a structured request, your code runs the operation, and the result flows back into the conversation." [Source: 06-tools.md, "Custom tools"]

Schema — `BetaManagedAgentsCustomToolParams`: [Source: api-reference/01-agents.md, `BetaManagedAgentsCustomToolParams`]

| Field | Required | Constraints |
|---|---|---|
| `type` | Yes | `"custom"` |
| `name` | Yes | 1–128 characters, letters/digits/underscores/hyphens only. |
| `description` | Yes | 1–1024 characters. |
| `input_schema` | Yes | `{ type: "object", properties, required }` — JSON Schema. |

Example:

```json
{
  "type": "custom",
  "name": "get_weather",
  "description": "Get current weather for a location",
  "input_schema": {
    "type": "object",
    "properties": {
      "location": {"type": "string", "description": "City name"}
    },
    "required": ["location"]
  }
}
```

### 7.4 MCP toolset

Reference an MCP server registered on the agent (see Section 9). [Source: 08-mcp-connector.md]

```json
{ "type": "mcp_toolset", "mcp_server_name": "github" }
```

### 7.5 Best practices for custom tools

[Source: 06-tools.md, "Best practices for custom tool definitions"]

- **Provide extremely detailed descriptions** — "by far the most important factor in tool performance." Aim for at least 3–4 sentences per tool description.
- **Consolidate related operations into fewer tools** — use an `action` parameter rather than separate `create_pr`, `review_pr`, `merge_pr` tools.
- **Use meaningful namespacing in tool names** — prefix by resource (e.g. `db_query`, `storage_read`).
- **Return only high-signal information** — semantic, stable identifiers (slugs or UUIDs) over opaque internal references; only the fields Claude needs to reason about its next step.

### 7.6 Execution model

- **Server-executed tools** (`agent_toolset_20260401`, `mcp_toolset`) run inside the container or via the MCP server. Governed by permission policies (Section 10).
- **Custom tools** run in your application. Not governed by permission policies. [Source: 09-permission-policies.md, "Custom tools"; 06-tools.md, intro] Claude emits `agent.custom_tool_use`, you execute and reply with `user.custom_tool_result`.

### 7.7 Gotchas — Tools

- **Maximum 128 tools across all toolsets.** [Source: api-reference/01-agents.md, "Agent-Level Limits"]
- **Custom tool names** have a restricted character set (letters, digits, underscores, hyphens). [Source: api-reference/01-agents.md, `BetaManagedAgentsCustomToolParams`]
- **Permission policies do not apply to custom tools.** Your application is responsible for authorization. [Source: 09-permission-policies.md, "Custom tools"]
- **Network mode `limited` does NOT affect `web_search`/`web_fetch` allowed domains.** Those are tool-specific. [Source: 03-environments.md, "Networking"]
- **`default_config.enabled: false` is the pattern for allow-listing** — combine with `configs` entries that explicitly enable what you need. [Source: 06-tools.md, "Enabling only specific tools"]

---

## 8. Skills

> "Skills are reusable, filesystem-based resources that give your agent domain-specific expertise: workflows, context, and best practices that turn a general-purpose agent into a specialist. Unlike prompts (conversation-level instructions for one-off tasks), skills load on demand, only impacting the context window when needed." [Source: 07-skills.md, intro]

### 8.1 Skill types

| Field | Description |
|---|---|
| `type` | Either `anthropic` for pre-built skills or `custom` for organization-authored skills. |
| `skill_id` | For Anthropic skills, use the short name (for example, `xlsx`). For custom skills, use the `skill_*` ID returned at creation. |
| `version` | Custom skills only. Pin to a specific version or use `latest`. |

[Source: 07-skills.md, "Skill types"]

Pre-built Anthropic skills cover common document tasks: PowerPoint, Excel, Word, and PDF handling. [Source: 07-skills.md, intro]

### 8.2 Attaching skills

Attach at agent creation:

```json
{
  "skills": [
    {"type": "anthropic", "skill_id": "xlsx"},
    {"type": "custom", "skill_id": "skill_abc123", "version": "latest"}
  ]
}
```

> "A maximum of 20 skills per session is supported - this includes skills across all agents for the session, if you are working with multiple agents." [Source: 07-skills.md, "Enable skills on a session"]

### 8.3 How skills interact with the agent

> "Both work the same way: your agent invokes them automatically when they are relevant to the task." [Source: 07-skills.md, intro]

### 8.4 Gotchas — Skills

- **Max 20 skills per session** (counts across all agents in a multiagent session). [Source: 07-skills.md, "Enable skills on a session"]
- **Custom skill `version` defaults to latest if omitted during creation.** [Source: api-reference/01-agents.md, `BetaManagedAgentsCustomSkillParams`]
- **Authoring custom skills is out of scope for Managed Agents docs** — see the Agent Skills overview documentation. [Source: 07-skills.md, intro]

---

## 9. MCP Connector

Managed Agents supports connecting Model Context Protocol (MCP) servers to agents. Configuration is split into two steps: [Source: 08-mcp-connector.md, intro]

1. **Agent creation** declares which MCP servers the agent connects to, by name and URL.
2. **Session creation** supplies auth by referencing a pre-registered vault.

> "This separation keeps secrets out of reusable agent definitions while letting each session authenticate with its own credentials." [Source: 08-mcp-connector.md, intro]

### 9.1 Declaring MCP servers on an agent

```json
{
  "mcp_servers": [
    { "type": "url", "name": "github", "url": "https://api.githubcopilot.com/mcp/" }
  ],
  "tools": [
    { "type": "agent_toolset_20260401" },
    { "type": "mcp_toolset", "mcp_server_name": "github" }
  ]
}
```

> "The `name` you assign in the MCP server array is used to reference the `mcp_toolset` entries in the tools array." [Source: 08-mcp-connector.md, "Declare MCP servers on the agent"]

Fields: `type: "url"`, `name` (1–255 chars, unique within the `mcp_servers` array), `url`. [Source: api-reference/01-agents.md, `BetaManagedAgentsURLMCPServerParams`; `BetaManagedAgentsMCPServerURLDefinition`]

### 9.2 Auth at session creation

Pass `vault_ids` when creating a session; Anthropic matches each server URL against active credentials on the referenced vault and injects the token. [Source: 08-mcp-connector.md, "Provide auth at session creation"; 10-vaults.md]

```python
session = client.beta.sessions.create(
    agent=agent.id,
    environment_id=environment.id,
    vault_ids=[vault.id],
)
```

### 9.3 Auth failure behavior

> "If the authorization credentials supplied in the vault are invalid, session creation will succeed and interaction is still possible. A `session.error` event is emitted describing the MCP auth failure. You can decide whether to block further interactions on this error, trigger a credential update, or allow the session to continue without the MCP. Authentication retries will happen on the following `session.status_idle` to `session.status_running` transition." [Source: 08-mcp-connector.md, after session creation example]

### 9.4 MCP toolset default permission policy

> "The MCP toolset defaults to a permission policy of `always_ask`, which requires user approval before each tool call." [Source: 08-mcp-connector.md, "Tip" block]

### 9.5 Supported server types

> "Claude Managed Agents connects to remote MCP servers that expose an HTTP endpoint. The server must support the MCP protocol's streamable HTTP transport." [Source: 08-mcp-connector.md, "Supported MCP server types"]

### 9.6 Gotchas — MCP

- **Max 20 MCP servers per agent; names must be unique.** [Source: api-reference/01-agents.md, "Validation Constraints Summary"]
- **Invalid credentials do NOT fail session creation** — the session starts and emits `session.error` later. [Source: 08-mcp-connector.md]
- **MCP tools default to `always_ask`, unlike the agent toolset which defaults to `always_allow`.** [Source: 09-permission-policies.md, "MCP toolset permissions"]
- **Container networking must permit the MCP server URL.** When using `limited` networking, set `allow_mcp_servers: true` or add the server's host to `allowed_hosts`. [Source: 03-environments.md, "Networking"]
- **Only remote HTTP MCP servers are supported** — local stdio MCP servers are not. [Source: 08-mcp-connector.md, "Supported MCP server types"]

---

## 10. Permission Policies

> "Permission policies control whether server-executed tools (the pre-built agent toolset and MCP toolset) run automatically or wait for your approval. Custom tools are executed by your application and controlled by you, so they are not governed by permission policies." [Source: 09-permission-policies.md, intro]

### 10.1 Policy types

| Policy | Behavior |
|---|---|
| `always_allow` | Tool executes automatically with no confirmation. |
| `always_ask` | Session emits `session.status_idle` and waits for `user.tool_confirmation` before executing. |

[Source: 09-permission-policies.md, "Permission policy types"]

Schema: `{ "type": "always_allow" }` or `{ "type": "always_ask" }`. [Source: api-reference/01-agents.md, "Permission Policies"]

### 10.2 Defaults by toolset

| Toolset | Default policy |
|---|---|
| `agent_toolset_20260401` | `always_allow` (if `default_config` is omitted) [Source: 09-permission-policies.md, after agent toolset example] |
| `mcp_toolset` | `always_ask` [Source: 09-permission-policies.md, "MCP toolset permissions"; 08-mcp-connector.md, "Tip" block] |

> "MCP toolsets default to `always_ask`. This ensures that new tools that are added to an MCP server do not execute in your application without approval." [Source: 09-permission-policies.md, "MCP toolset permissions"]

### 10.3 Setting toolset-wide policy

```json
{
  "type": "agent_toolset_20260401",
  "default_config": { "permission_policy": { "type": "always_ask" } }
}
```

### 10.4 Overriding per-tool

Use `configs` to override individual tools:

```json
{
  "type": "agent_toolset_20260401",
  "default_config": { "permission_policy": { "type": "always_allow" } },
  "configs": [
    { "name": "bash", "permission_policy": { "type": "always_ask" } }
  ]
}
```

[Source: 09-permission-policies.md, "Override an individual tool policy"]

### 10.5 Responding to confirmation requests

1. Session emits `agent.tool_use` or `agent.mcp_tool_use`.
2. Session pauses with `session.status_idle` + `stop_reason: requires_action` + `event_ids`.
3. Send `user.tool_confirmation` per event ID with `tool_use_id`, `result: "allow" \| "deny"`, optional `deny_message` (deny only).
4. Once all resolved, session returns to `running`. [Source: 09-permission-policies.md, "Respond to confirmation requests"]

### 10.6 `evaluated_permission` on tool-use events

Both `agent.tool_use` and `agent.mcp_tool_use` events carry an optional `evaluated_permission` field: `"allow" | "ask" | "deny"` (the `AgentEvaluatedPermission` enum), indicating how the policy evaluated for that specific invocation. [Source: api-reference/00-sessions.md, `BetaManagedAgentsAgentToolUseEvent` and `BetaManagedAgentsAgentMCPToolUseEvent`]

### 10.7 Gotchas — Permission Policies

- **Custom tools bypass permission policies entirely.** Your app is responsible for authorization before sending `user.custom_tool_result`. [Source: 09-permission-policies.md, "Custom tools"]
- **Default policies differ between toolsets.** Agent toolset is permissive by default; MCP toolset is restrictive. [Source: 09-permission-policies.md]
- **`deny_message` is optional and only valid with `deny`.** [Source: api-reference/00-sessions.md, `BetaManagedAgentsUserToolConfirmationEventParams`]
- **Partial resolution re-emits idle.** If multiple events are blocking and you only answer some, the session re-emits `session.status_idle` with the remaining blockers. [Source: api-reference/00-sessions.md, `BetaManagedAgentsSessionRequiresAction`]

---

## 11. Vaults (Secrets Management)

> "Vaults and credentials are authentication primitives that let you register credentials for third-party services once and reference them by ID at session creation. This means you don't need to run your own secret store, transmit tokens on every call, or lose track of which end user an agent acted on behalf of." [Source: 10-vaults.md, intro]

> "The vault reference is a per-session parameter, so you can manage your product at the agent level and your users at the session level." [Source: 10-vaults.md, intro]

### 11.1 Security warning

> "Vaults and credentials are workspace-scoped, meaning anyone with API key access can use them for authorizing an agent to complete a task. To revoke access, delete the vault or credential." [Source: 10-vaults.md, "Warning" block]

### 11.2 Create a vault

Fields: `display_name` (required, 1–255 chars), `metadata` (optional, max 16 pairs, keys ≤64 chars, values ≤512 chars). [Source: api-reference/03-vaults.md, "Create Vault"]

```python
vault = client.beta.vaults.create(
    display_name="Alice",
    metadata={"external_user_id": "usr_abc123"},
)
```

Response:

```json
{
  "type": "vault",
  "id": "vlt_01ABC...",
  "display_name": "Alice",
  "metadata": { "external_user_id": "usr_abc123" },
  "created_at": "2026-03-18T10:00:00Z",
  "updated_at": "2026-03-18T10:00:00Z",
  "archived_at": null
}
```

[Source: 10-vaults.md, "Create a vault"]

### 11.3 Credentials

> "Each credential binds to a single `mcp_server_url`. When the agent connects to an MCP server at session runtime, the API matches the server URL against active credentials on the referenced vault and injects the token." [Source: 10-vaults.md, "Add a credential"]

Two auth types: [Source: 10-vaults.md; api-reference/03-vaults.md, "Create Credential"]

**MCP OAuth (`mcp_oauth`):**

| Field | Required | Description |
|---|---|---|
| `type` | Yes | `"mcp_oauth"` |
| `mcp_server_url` | Yes | Immutable after creation. |
| `access_token` | Yes | OAuth access token. |
| `expires_at` | No | RFC 3339 timestamp. |
| `refresh` | No | `BetaManagedAgentsMCPOAuthRefreshParams`. "If you supply a `refresh` block, Anthropic refreshes the access token on your behalf when it expires." [Source: 10-vaults.md, "MCP OAuth credential"] |

`refresh` sub-object:

| Field | Required | Description |
|---|---|---|
| `token_endpoint` | Yes | Token endpoint URL used to refresh. |
| `client_id` | Yes | OAuth client ID. |
| `refresh_token` | Yes | OAuth refresh token. |
| `token_endpoint_auth` | Yes | `{type: "none"}` OR `{type: "client_secret_basic", client_secret}` OR `{type: "client_secret_post", client_secret}`. |
| `scope` | No | OAuth scope. |
| `resource` | No | OAuth resource indicator. |

> "`none`: public client; `client_secret_basic`: HTTP Basic auth with the client secret; `client_secret_post`: client secret in the POST body." [Source: 10-vaults.md, "MCP OAuth credential"]

**Static bearer (`static_bearer`):**

| Field | Required | Description |
|---|---|---|
| `type` | Yes | `"static_bearer"` |
| `mcp_server_url` | Yes | Immutable after creation. |
| `token` | Yes | Fixed bearer token. |

> "Use `static_bearer` when the MCP server accepts a fixed bearer token (API key, personal access token, or similar). No refresh flow is needed." [Source: 10-vaults.md, "Static bearer credential"]

### 11.4 Secret handling

> "Secret fields (`token`, `access_token`, `refresh_token`, `client_secret`) are write-only. They are never returned in API responses." [Source: 10-vaults.md, "Warning" block]

> "Credentials are stored as provided and are not validated until session runtime. A bad token surfaces as an MCP auth error during the session, which is emitted but does not block the session from continuing." [Source: 10-vaults.md, after Static bearer example]

### 11.5 Credential constraints

- **One active credential per `mcp_server_url` per vault.** "Creating a second credential for the same URL returns a 409."
- **`mcp_server_url` is immutable.** To point at a different server, archive this credential and create a new one.
- **Maximum 20 credentials per vault.** Matches the max MCP servers per agent. [Source: 10-vaults.md, "Constraints"]

### 11.6 Rotating credentials

> "Only the secret payload and a handful of metadata fields are mutable. `mcp_server_url`, `token_endpoint`, and `client_id` are locked after creation." [Source: 10-vaults.md, "Rotate a credential"]

Example (OAuth rotation):

```bash
curl --fail-with-body -sS \
  "https://api.anthropic.com/v1/vaults/$vault_id/credentials/$credential_id" \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "anthropic-beta: managed-agents-2026-04-01" \
  -H "content-type: application/json" \
  --data @- > /dev/null <<'EOF'
{
  "auth": {
    "type": "mcp_oauth",
    "access_token": "xoxp-new-...",
    "expires_at": "2026-05-15T00:00:00Z",
    "refresh": {"refresh_token": "xoxe-1-new-..."}
  }
}
EOF
```

### 11.7 Runtime behavior

[Source: 10-vaults.md, "Reference the vault at session creation"]

- **Credentials are re-resolved periodically during the session**, so rotation or archive propagates to running sessions without restart.
- **When a vault has no credential for the MCP server**, the connection is attempted unauthenticated and produces an error.
- **When multiple vaults cover the MCP server**, the first vault with a match wins.

### 11.8 Vault/credential lifecycle operations

[Source: 10-vaults.md, "Other operations"; api-reference/03-vaults.md]

- **List** — paginated, newest first. Archived records excluded by default (`include_archived=true` to include).
- **Archive vault** — `POST /v1/vaults/{id}/archive`. Cascades to all credentials. Secrets are purged; records retained for auditing. Future sessions referencing this vault fail; running sessions continue.
- **Archive credential** — `POST /v1/vaults/{id}/credentials/{cred_id}/archive`. Purges secret payload; `mcp_server_url` remains visible. Frees the `mcp_server_url` for a replacement credential.
- **Delete vault/credential** — hard delete. Use archive if you need an audit trail.

### 11.9 Gotchas — Vaults

- **`mcp_server_url`, `token_endpoint`, `client_id` are immutable after credential creation.** [Source: 10-vaults.md, "Rotate a credential"]
- **Invalid credentials DO NOT block session creation** — the session starts and emits `session.error` describing the failure. [Source: 08-mcp-connector.md; 10-vaults.md]
- **Attempting a second active credential for the same `mcp_server_url` returns 409.** Archive the old one first. [Source: 10-vaults.md, "Constraints"]
- **Archive a vault → all its credentials cascade-archive.** [Source: 10-vaults.md, "Other operations"]
- **The first matching vault wins when multiple vaults cover the same MCP server.** Order your `vault_ids` intentionally. [Source: 10-vaults.md, "Reference the vault at session creation"]
- **Secret fields are write-only.** You cannot read them back; you must re-supply to rotate. [Source: 10-vaults.md]
- **Vaults are workspace-scoped — anyone with API key access can use them.** Treat vaults like shared infrastructure. [Source: 10-vaults.md, "Warning"]

---

## 12. Cloud Containers

Cloud containers come pre-installed with a comprehensive set of programming languages, databases, and utilities. "The agent can use these immediately without any installation steps." [Source: 11-cloud-containers.md, intro]

### 12.1 Pre-installed programming languages

| Language | Version | Package manager |
|---|---|---|
| Python | 3.12+ | pip, uv |
| Node.js | 20+ | npm, yarn, pnpm |
| Go | 1.22+ | go modules |
| Rust | 1.77+ | cargo |
| Java | 21+ | maven, gradle |
| Ruby | 3.3+ | bundler, gem |
| PHP | 8.3+ | composer |
| C/C++ | GCC 13+ | make, cmake |

[Source: 11-cloud-containers.md, "Programming languages"]

### 12.2 Databases

| Database | Description |
|---|---|
| SQLite | Pre-installed, available immediately |
| PostgreSQL client | `psql` client for connecting to external databases |
| Redis client | `redis-cli` for connecting to external instances |

> "Database servers (PostgreSQL, Redis, etc.) are not running in the container by default. The container includes client tools for connecting to external database instances. SQLite is fully available for local use." [Source: 11-cloud-containers.md, "Databases"]

### 12.3 Utilities

- **System tools:** `git`, `curl`, `wget`, `jq`, `tar`, `zip`, `unzip`, `ssh`, `scp` (requires network), `tmux`, `screen`.
- **Development tools:** `make`, `cmake`, `docker` (limited availability), `ripgrep` (`rg`), `tree`, `htop`.
- **Text processing:** `sed`, `awk`, `grep`, `vim`, `nano`, `diff`, `patch`. [Source: 11-cloud-containers.md, "Utilities"]

### 12.4 Container specs

| Property | Value |
|---|---|
| Operating system | Ubuntu 22.04 LTS |
| Architecture | x86_64 (amd64) |
| Memory | Up to 8 GB |
| Disk space | Up to 10 GB |
| Network | Disabled by default (enable in environment config) |

[Source: 11-cloud-containers.md, "Container specifications"]

### 12.5 Gotchas — Containers

- **Network is disabled by default** per the container specs table, yet the environment docs state the default `networking.type` is `unrestricted`. Sources conflict on this point; the container-level claim is: "Network: Disabled by default (enable in environment config)." [Source: 11-cloud-containers.md, "Container specifications"] The environment-level claim is: "Full outbound network access … This is the default." [Source: 03-environments.md, "Networking"]
- **Database *servers* are not running** — only *clients* are pre-installed. SQLite is the exception. [Source: 11-cloud-containers.md, "Databases"]
- **`docker` has "limited availability"** within the container. [Source: 11-cloud-containers.md, "Development tools"]
- **x86_64 only** — no ARM64. [Source: 11-cloud-containers.md, "Container specifications"]

---

## 13. Multi-Agent

> **Research Preview feature.** Requires access request, plus the base beta header. "An additional beta header is needed for research preview features. The SDK sets these beta headers automatically." [Source: 12-multi-agent.md, "Note" block]

### 13.1 Model

> "Multi-agent orchestration lets one agent coordinate with others to complete complex work. Agents can act in parallel with their own isolated context, which helps improve output quality and improve time to completion." [Source: 12-multi-agent.md, intro]

> "All agents share the same container and filesystem, but each agent runs in its own session **thread**, a context-isolated event stream with its own conversation history. The coordinator reports activity in the **primary thread** (which is the same as the session-level event stream); additional threads are spawned at runtime when the coordinator decides to delegate." [Source: 12-multi-agent.md, "How it works"]

Threads are persistent: "the coordinator can send a follow-up to an agent it called earlier, and that agent retains everything from its previous turns." [Source: 12-multi-agent.md, "How it works"]

> "Each agent uses its own configuration (model, system prompt, tools, MCP servers, and skills) as defined when that agent was created. Tools and context are not shared." [Source: 12-multi-agent.md, "How it works"]

### 13.2 What to delegate

Good delegation patterns: [Source: 12-multi-agent.md, "What to delegate"]

- **Code review** — a reviewer agent with a focused system prompt and read-only tools.
- **Test generation** — a test agent that writes and runs tests without touching production code.
- **Research** — a search agent with web tools that summarizes findings back to the coordinator.

### 13.3 Declaring callable agents

Set `callable_agents` on the orchestrator agent:

```json
{
  "callable_agents": [
    {"type": "agent", "id": "agent_reviewer_id", "version": 1},
    {"type": "agent", "id": "agent_test_writer_id", "version": 1}
  ]
}
```

> "Each entry in `callable_agents` must be the ID of an existing agent. Only one level of delegation is supported: the coordinator can call other agents, but those agents cannot call agents of their own." [Source: 12-multi-agent.md, "Declare callable agents"]

> "The callable agents are resolved from the orchestrator's configuration. You don't need to reference them at session creation." [Source: 12-multi-agent.md, after the session create example]

### 13.4 Session threads

> "The **session-level event stream** (`/v1/sessions/:id/stream`) is considered the **primary thread**, containing an condensed view of all activity across all threads. You won't see called agents' individual traces, but you will see the start and end of their work. **Session threads** are where you drill into a specific agent's reasoning and tool calls." [Source: 12-multi-agent.md, "Session threads"]

> "The session status also is an aggregation of all agent activity; if at least one thread is `running`, then the overall session status will be `running` as well." [Source: 12-multi-agent.md, "Session threads"]

Thread endpoints: [Source: 12-multi-agent.md]

| Method | Path | Description |
|---|---|---|
| GET | `/v1/sessions/{session_id}/threads` | List threads. |
| GET (SSE) | `/v1/sessions/{session_id}/threads/{thread_id}/stream` | Stream one thread's events. |
| GET | `/v1/sessions/{session_id}/threads/{thread_id}/events` | List past events for a thread. |

### 13.5 Multiagent event types

[Source: 12-multi-agent.md, "Multiagent event types"]

| Type | Description |
|---|---|
| `session.thread_created` | Coordinator spawned a new thread. Includes `session_thread_id` and `model`. |
| `session.thread_idle` | Agent thread finished current work. |
| `agent.thread_message_sent` | Agent sent a message to another thread. Includes `to_thread_id` and `content`. |
| `agent.thread_message_received` | Agent received a message from another thread. Includes `from_thread_id` and `content`. |

### 13.6 Routing confirmations in multiagent

When a callable agent thread needs something from the client (tool confirmation or custom tool result), the request surfaces on the **session stream** with a `session_thread_id` field. [Source: 12-multi-agent.md, "Tool permissions and custom tools in threads"]

- **`session_thread_id` is present** → event originated in a subagent thread. **Echo it on your reply.**
- **`session_thread_id` is absent** → event came from the primary thread. Reply without the field.
- Match on `tool_use_id` to pair requests with responses.

```python
for event_id in stop.event_ids:
    pending = events_by_id[event_id]
    confirmation = {
        "type": "user.tool_confirmation",
        "tool_use_id": event_id,
        "result": "allow",
    }
    if pending.session_thread_id is not None:
        confirmation["session_thread_id"] = pending.session_thread_id
    client.beta.sessions.events.send(session.id, events=[confirmation])
```

### 13.7 Gotchas — Multi-agent

- **Only one level of delegation.** Sub-agents cannot call their own sub-agents. [Source: 12-multi-agent.md, "Declare callable agents"]
- **All agents share the same container and filesystem**, but NOT context or tools. [Source: 12-multi-agent.md, "How it works"]
- **Session status is an aggregation.** Overall status is `running` if any thread is running. [Source: 12-multi-agent.md, "Session threads"]
- **Echo `session_thread_id` on confirmation/result replies** when the triggering event had one — otherwise the platform can't route it back to the waiting thread. [Source: 12-multi-agent.md, "Tool permissions and custom tools in threads"]
- **Callable agents count against the 20-skill-per-session limit**, if those agents have skills — skills are counted "across all agents for the session." [Source: 07-skills.md]
- **Requires research preview access.** [Source: 12-multi-agent.md]

---

## 14. Defining Outcomes

> **Research Preview feature.** Requires the `managed-agents-2026-04-01-research-preview` beta header in addition to the base beta header. [Source: 13-define-outcomes.md, "Note" block]

### 14.1 Concept

> "The `outcome` elevates a session from *conversation* to *work*. You define what the end result should look like and how to measure quality. The agent works toward that target, self-evaluating and iterating until the outcome is met." [Source: 13-define-outcomes.md, intro]

> "When you define an outcome, the harness automatically provisions a *grader* to evaluate the artifact against a rubric. It leverages a separate context window to avoid being influenced by the main agent's implementation choices." [Source: 13-define-outcomes.md, intro]

> "The grader returns a per-criterion breakdown: either confirmation that the artifact satisfies the rubric, or the specific gaps between the current work and the requirements. That feedback is handed back to the agent for the next iteration." [Source: 13-define-outcomes.md, intro]

### 14.2 Rubric

A rubric is a markdown document describing per-criterion scoring. **The rubric is required.** [Source: 13-define-outcomes.md, "Create a rubric"]

> "Structure the rubric as explicit, gradeable criteria, such as 'The CSV contains a price column with numeric values' rather than 'The data looks good.' The grader scores each criterion independently, so vague criteria produce noisy evaluations." [Source: 13-define-outcomes.md, "Tips for writing effective rubrics"]

Rubrics may be passed inline as text on the `user.define_outcome` event, or uploaded via the Files API for reuse (**requires beta header `files-api-2025-04-14`**). [Source: 13-define-outcomes.md]

### 14.3 Defining the outcome

```json
{
  "events": [
    {
      "type": "user.define_outcome",
      "description": "Build a DCF model for Costco in .xlsx",
      "rubric": {"type": "text", "content": "# DCF Model Rubric\n..."},
      "max_iterations": 5
    }
  ]
}
```

Or with a file-based rubric: `"rubric": {"type": "file", "file_id": "file_01..."}`. [Source: 13-define-outcomes.md, "Create a session with an outcome"]

Parameters: [Source: 13-define-outcomes.md]

| Field | Description |
|---|---|
| `description` | Free-form goal statement. |
| `rubric` | `{type: "text", content}` OR `{type: "file", file_id}`. Required. |
| `max_iterations` | Optional; default 3, max 20. |

> "The agent begins work immediately; no additional user message event is required." [Source: 13-define-outcomes.md, "Create a session with an outcome"]

### 14.4 Outcome events

[Source: 13-define-outcomes.md, "Outcome events"]

- `agent.*` events show progress toward the outcome.
- `span.outcome_evaluation_*` events are only emitted for outcome-oriented sessions and show iteration loops and grader feedback process.
- `user.message` events can still be sent to steer the agent but are "not as necessary; the agent knows to work until it has exhausted its iterations or achieved the outcome."
- `user.interrupt` pauses the current outcome and marks `span.outcome_evaluation_end.result` as `interrupted`, allowing a new outcome.
- After final evaluation, the session can be continued as conversational, or a new outcome started. "The session will retain history of the prior outcome."

**Only one outcome at a time.** [Source: 13-define-outcomes.md, "Note" under "Define outcome user event"] To chain: send a new `user.define_outcome` after the terminal event of the previous one.

### 14.5 Evaluation result enum

[Source: 13-define-outcomes.md, "Outcome evaluation end"]

| Result | Next step |
|---|---|
| `satisfied` | Session transitions to `idle`. |
| `needs_revision` | Agent starts a new iteration cycle. |
| `max_iterations_reached` | No further evaluation cycles. Agent may run one final revision before transitioning to `idle`. |
| `failed` | Session transitions to `idle`. Returned when rubric fundamentally does not match the task (e.g., description and rubric contradict). |
| `interrupted` | Only emitted if `outcome_evaluation_start` already fired before the interrupt. |

### 14.6 Example event shapes

```json
{
  "type": "span.outcome_evaluation_start",
  "id": "sevt_01def...",
  "outcome_id": "outc_01a...",
  "iteration": 0,
  "processed_at": "2026-03-25T14:01:45Z"
}
```

> "The `iteration` field is a 0-indexed revision counter: `0` is the first evaluation, `1` is the re-evaluation after the first revision, and so on." [Source: 13-define-outcomes.md, "Outcome evaluation start"]

```json
{
  "type": "span.outcome_evaluation_end",
  "id": "sevt_01jkl...",
  "outcome_evaluation_start_id": "sevt_01def...",
  "outcome_id": "outc_01a...",
  "result": "satisfied",
  "explanation": "All 12 criteria met: ...",
  "iteration": 0,
  "usage": {
    "input_tokens": 2400,
    "output_tokens": 350,
    "cache_creation_input_tokens": 0,
    "cache_read_input_tokens": 1800
  },
  "processed_at": "2026-03-25T14:03:00Z"
}
```

### 14.7 Polling outcome status

`GET /v1/sessions/:id` and read `outcome_evaluations[].result`. [Source: 13-define-outcomes.md, "Checking on outcome status"]

### 14.8 Retrieving deliverables

> "The agent writes output files to `/mnt/session/outputs/` inside the container. Once the session is idle, fetch them via the Files API scoped to the session." [Source: 13-define-outcomes.md, "Retrieving deliverables"]

```bash
curl -fsSL "https://api.anthropic.com/v1/files?scope_id=$session_id" \
  -H "anthropic-beta: files-api-2025-04-14,managed-agents-2026-04-01-research-preview"
```

### 14.9 Grader visibility

> "Heartbeat emitted while the grader runs. The grader's internal reasoning is opaque: you see that it's working, not what it's thinking." [Source: 13-define-outcomes.md, "Outcome evaluation ongoing"]

### 14.10 Gotchas — Outcomes

- **Rubric is required.** [Source: 13-define-outcomes.md, "Create a rubric"]
- **Only one outcome at a time.** Must chain sequentially. [Source: 13-define-outcomes.md]
- **`max_iterations` default 3, max 20.** [Source: 13-define-outcomes.md, "Create a session with an outcome"]
- **Requires two beta headers** — base `managed-agents-2026-04-01` plus `managed-agents-2026-04-01-research-preview` (and `files-api-2025-04-14` for file-based rubrics/deliverables).
- **Deliverables land in `/mnt/session/outputs/`.** Fetch via Files API `scope_id=$session_id`. [Source: 13-define-outcomes.md]
- **`interrupted` is only emitted if `outcome_evaluation_start` already fired.** [Source: 13-define-outcomes.md, result table]
- **`failed` signals a rubric/description contradiction**, not a grading failure. [Source: 13-define-outcomes.md, result table]
- **Grader reasoning is opaque.** You only observe that it is running. [Source: 13-define-outcomes.md, "Outcome evaluation ongoing"]

---

## 15. Memory

> **Research Preview feature.** Requires base beta header plus a research preview beta header. "The SDK sets these beta headers automatically." [Source: 14-memory.md, "Note" block]

> "Managed Agents API sessions are ephemeral by default. When a session ends, anything the agent learned is gone. Memory stores let the agent carry learnings across sessions: user preferences, project conventions, prior mistakes, and domain context." [Source: 14-memory.md, intro]

### 15.1 Overview

> "A **memory store** is a workspace-scoped collection of text documents optimized for Claude. When one or more memory stores are attached to a session, the agent automatically checks the stores before starting a task and writes durable learnings when done - no additional prompting or configuration is needed on your side." [Source: 14-memory.md, "Overview"]

> "Each **memory** in a store can be accessed and edited directly via the API or Console, allowing for tuning, importing, and exporting memories." [Source: 14-memory.md, "Overview"]

> "Every change to a memory creates an immutable **memory version** to support auditing and rolling back memory changes." [Source: 14-memory.md, "Overview"]

### 15.2 Creating a memory store

```python
store = client.beta.memory_stores.create(
    name="User Preferences",
    description="Per-user preferences and project context.",
)
```

`name` and `description` required. "The description is passed to the agent, telling it what the store contains." [Source: 14-memory.md, "Create a memory store"]

The memory store `id` is `memstore_...`. [Source: 14-memory.md]

### 15.3 Seeding content

Pre-load via `memories.write` (path + content). [Source: 14-memory.md, "Seed it with content (optional)"]

> "Individual memories within the store are capped at 100KB (~25K tokens). Structure memory as many small focused files, not a few large ones." [Source: 14-memory.md, "Tip" block]

### 15.4 Attaching to a session

Memory stores go in `resources[]`:

```json
{
  "resources": [
    {
      "type": "memory_store",
      "memory_store_id": "memstore_01...",
      "access": "read_write",
      "prompt": "User preferences and project context. Check before starting any task."
    }
  ]
}
```

[Source: 14-memory.md, "Attach a memory store to a session"]

- `access`: `"read_write"` (default) or `"read_only"`.
- `prompt`: session-specific instructions, capped at 4,096 characters; provided in addition to the store's name and description.
- **Maximum 8 memory stores per session.**

> "Attach multiple stores when different parts of memory have different owners or access rules. Common reasons: shared reference material (one read-only store attached to many sessions), mapping to your product's structure (one store per end-user, per-team, or per-project), different lifecycles." [Source: 14-memory.md, "Attach a memory store to a session"]

### 15.5 Memory tools (agent-side)

When memory stores are attached, the agent gains these tools: [Source: 14-memory.md, "Memory tools"]

| Tool | Description |
|---|---|
| `memory_list` | List memories, optionally filtered by path prefix. |
| `memory_search` | Full-text search across memory contents. |
| `memory_read` | Read a memory's contents. |
| `memory_write` | Create or overwrite a memory at a path. |
| `memory_edit` | Modify an existing memory. |
| `memory_delete` | Remove a memory. |

> "The agent's interactions with memory stores are registered as `agent.tool_use` events in the event stream." [Source: 14-memory.md, "Memory tools"]

### 15.6 Memory CRUD via API

[Source: 14-memory.md]

- **List memories:** `GET /v1/memory_stores/{store_id}/memories?path_prefix=/`. List does not return content, just metadata (including `size_bytes`, `content_sha256`). Path prefix requires trailing slash: `/notes/` matches `/notes/a.md` but not `/notes_backup/old.md`.
- **Read a memory:** returns full content.
- **Write (create/upsert by path):** `memories.write` upserts by path. Creates if missing, replaces if present. To mutate an existing memory by ID (for rename or safe content edit), use `memories.update` instead.
- **Update (by ID):** `memories.update` changes `content`, `path` (rename), or both. Renaming onto an occupied path returns `409 conflict` unless `precondition={"type": "not_exists"}` is passed.
- **Delete.** Optionally pass `expected_content_sha256` for a conditional delete.

### 15.7 Safe concurrency

**Create-only guard:**

```python
client.beta.memory_stores.memories.write(
    memory_store_id=store.id,
    path="/preferences/formatting.md",
    content="...",
    precondition={"type": "not_exists"},
)
```

> "If a memory already exists at the path, the write returns `409 memory_precondition_failed` instead of replacing it." [Source: 14-memory.md, "Safe writes (optimistic concurrency)"]

**Safe content edit with hash:**

```python
client.beta.memory_stores.memories.update(
    memory_id=mem.id,
    memory_store_id=store.id,
    content="CORRECTED: ...",
    precondition={"type": "content_sha256", "content_sha256": mem.content_sha256},
)
```

> "The update only applies if the stored hash still matches the one you read; on mismatch it returns `409 memory_precondition_failed`, at which point you re-read the memory and retry against the fresh state." [Source: 14-memory.md, "Safe content edits (optimistic concurrency)"]

### 15.8 Memory versions

> "Every mutation to a memory creates an immutable **memory version** (`memver_...`). Versions accumulate for the lifetime of the parent memory and form the audit and rollback surface underneath it. The live `memories.retrieve` call always returns the current head; the version endpoints give you the full history." [Source: 14-memory.md, "Audit memory changes"]

Operations that create versions:

- First `memories.write` to a path → `operation: "created"`.
- `memories.update` that changes `content`, `path`, or both → `operation: "modified"`.
- `memories.delete` → `operation: "deleted"`.

Version list filters: `memory_id`, `operation` (`created` / `modified` / `deleted`), `session_id`, `api_key_id`, `created_at_gte`/`created_at_lte`. [Source: 14-memory.md, "List versions"]

**Redact** (`POST /v1/memory_stores/{store_id}/memory_versions/{version_id}/redact`): "Redact scrubs content out of a historical version while preserving the audit trail (who did what, when). Use it for compliance workflows such as removing leaked secrets, PII, or user deletion requests. Redact hard clears `content`, `content_sha256`, `content_size_bytes`, and `path`; all other fields, including the actor and timestamps, are preserved." [Source: 14-memory.md, "Redact a version"]

### 15.9 API reference status

> "Memory Version endpoints (`/versions`, `/redact`) were probed and returned `404 page not found`, indicating they are **not yet implemented** at the API level." [Source: api-reference/04-memory-stores.md, "Memory Version Endpoints"]

> "SDK support: Not present in `anthropic-sdk-python` or `anthropic-sdk-typescript` as of the current release." [Source: api-reference/04-memory-stores.md, "Status"]

> "OpenAPI spec: Not included in the published Stainless-generated OpenAPI spec." [Source: api-reference/04-memory-stores.md, "Status"]

So there is a discrepancy between the conceptual docs (which describe versioning and redact) and the API reference (which reports these endpoints as not yet routed). Treat version/redact operations as available in the SDK flow described in `14-memory.md` but be aware they may currently 404 on direct HTTP probes. [Source: 14-memory.md vs. api-reference/04-memory-stores.md]

### 15.10 Gotchas — Memory

- **Individual memory cap: 100KB (~25K tokens).** "Structure memory as many small focused files, not a few large ones." [Source: 14-memory.md, "Seed it with content"]
- **Max 8 memory stores per session.** [Source: 14-memory.md, "Attach a memory store to a session"]
- **`prompt` is capped at 4,096 characters.** [Source: 14-memory.md]
- **`access: read_write` is the default** even if you don't specify it — if you want read-only, you must explicitly set it. [Source: 14-memory.md]
- **Path prefix matching requires trailing slash.** `/notes/` matches `/notes/a.md` but not `/notes_backup/old.md`. [Source: 14-memory.md, "List memories"]
- **`memories.write` replaces; `memories.update` mutates by ID.** Use `write` for upsert-by-path, `update` for rename or safe content edit. [Source: 14-memory.md, "Create a memory"]
- **Rename collisions return 409.** Use `precondition: {type: "not_exists"}` or delete blocker first. [Source: 14-memory.md, "Update a memory"]
- **Version/redact endpoints may not yet be routed.** Expect possible 404s on direct HTTP probes. [Source: api-reference/04-memory-stores.md]
- **Research preview access required.** [Source: 14-memory.md]

---

## 16. API Reference (Consolidated)

All endpoints require: `anthropic-version: 2023-06-01`, `anthropic-beta: managed-agents-2026-04-01`, `x-api-key: <API key>`, and `content-type: application/json` for writes.

### 16.1 Sessions API

Endpoints: [Source: api-reference/00-sessions.md]

| Method | Path | Operation |
|---|---|---|
| POST | `/v1/sessions` | Create Session |
| GET | `/v1/sessions` | List Sessions |
| GET | `/v1/sessions/{session_id}` | Retrieve Session |
| POST | `/v1/sessions/{session_id}` | Update Session (title/metadata only) |
| DELETE | `/v1/sessions/{session_id}` | Delete Session (returns `{id, type: "session_deleted"}`) |
| POST | `/v1/sessions/{session_id}/archive` | Archive Session |
| POST | `/v1/sessions/{session_id}/events` | Send Events |
| GET | `/v1/sessions/{session_id}/events` | List Events |
| GET | `/v1/sessions/{session_id}/events/stream` | Stream Events (SSE) |

List query parameters: `agent_id`, `agent_version` (only with `agent_id`), `created_at[gt/gte/lt/lte]`, `include_archived` (default `false`), `limit`, `order` (`asc` | `desc`, default `desc`), `page`.

**Create Session body (full):**

| Field | Required | Type | Description |
|---|---|---|---|
| `agent` | Yes | `string \| BetaManagedAgentsAgentParams` | Bare ID string pins latest; object `{type:"agent", id, version}` pins specific version (version ≥1). |
| `environment_id` | Yes | `string` | |
| `metadata` | No | `map[string]` | Max 16 pairs, keys ≤64, values ≤512. |
| `resources` | No | `array` | GitHub repo / file / memory store (see §5.3, §15.4). |
| `title` | No | `string` | |
| `vault_ids` | No | `array of string` | |

**Send Events body:**

```json
{
  "events": [ /* BetaManagedAgentsEventParams entries */ ]
}
```

Supported user event params: `user.message`, `user.interrupt`, `user.tool_confirmation`, `user.custom_tool_result`. For content blocks on `user.message`: `text`, `image` (base64/URL/file), `document` (base64/plain text/URL/file with optional `context` and `title`).

**Stream events** emit all event types listed in §6.

**Session object fields:** see §5.6 and [Source: api-reference/00-sessions.md, "Create Session" Returns].

### 16.2 Agents API

Endpoints: [Source: api-reference/01-agents.md, "Endpoints Summary"]

| Method | Path | Operation |
|---|---|---|
| POST | `/v1/agents` | Create Agent |
| GET | `/v1/agents` | List Agents |
| GET | `/v1/agents/{agent_id}` | Retrieve Agent (use `?version=N`) |
| POST | `/v1/agents/{agent_id}` | Update Agent |
| POST | `/v1/agents/{agent_id}/archive` | Archive Agent |
| GET | `/v1/agents/{agent_id}/versions` | List Agent Versions |

List query parameters: `limit` (default 20, max 100), `page`, `include_archived`, `created_at[gte/lte]`. [Source: api-reference/01-agents.md, "List Agents"]

**Update Agent body:**

| Field | Behavior |
|---|---|
| `version` | Required. Must match server's current version. |
| `name` | Cannot be cleared. Omit to preserve. |
| `description` | Omit to preserve. Empty string or `null` to clear. |
| `model` | Cannot be cleared. Omit to preserve. |
| `system` | Omit to preserve. Empty string or `null` to clear. |
| `metadata` | Patch: key→string upsert, key→null delete. Omit to preserve. |
| `mcp_servers` | Full replacement. Omit to preserve. Empty array or null to clear. |
| `skills` | Full replacement. Omit to preserve. Empty array or null to clear. |
| `tools` | Full replacement. Omit to preserve. Empty array or null to clear. |

### 16.3 Environments API

Endpoints: [Source: api-reference/02-environments.md, "Endpoints"]

| Method | Path | Operation |
|---|---|---|
| POST | `/v1/environments` | Create |
| GET | `/v1/environments` | List |
| GET | `/v1/environments/{environment_id}` | Retrieve |
| POST | `/v1/environments/{environment_id}` | Update (only if the environment is not referenced elsewhere via omitted/null semantics) |
| DELETE | `/v1/environments/{environment_id}` | Delete (returns `{id, type:"environment_deleted"}`) |
| POST | `/v1/environments/{environment_id}/archive` | Archive |

List query parameters: `include_archived`, `limit`, `page`.

### 16.4 Vaults API

Vault endpoints: [Source: api-reference/03-vaults.md]

| Method | Path | Operation |
|---|---|---|
| POST | `/v1/vaults` | Create Vault |
| GET | `/v1/vaults` | List Vaults |
| GET | `/v1/vaults/{vault_id}` | Retrieve Vault |
| POST | `/v1/vaults/{vault_id}` | Update Vault |
| DELETE | `/v1/vaults/{vault_id}` | Delete Vault (returns `{id, type:"vault_deleted"}`) |
| POST | `/v1/vaults/{vault_id}/archive` | Archive Vault |

Credential endpoints:

| Method | Path | Operation |
|---|---|---|
| POST | `/v1/vaults/{vault_id}/credentials` | Create Credential |
| GET | `/v1/vaults/{vault_id}/credentials` | List Credentials |
| GET | `/v1/vaults/{vault_id}/credentials/{credential_id}` | Retrieve Credential |
| POST | `/v1/vaults/{vault_id}/credentials/{credential_id}` | Update Credential |
| DELETE | `/v1/vaults/{vault_id}/credentials/{credential_id}` | Delete Credential (returns `{id, type:"vault_credential_deleted"}`) |
| POST | `/v1/vaults/{vault_id}/credentials/{credential_id}/archive` | Archive Credential |

List query parameters: `include_archived`, `limit` (default 20, max 100), `page`.

Credential auth union: `BetaManagedAgentsMCPOAuthCreateParams` or `BetaManagedAgentsStaticBearerCreateParams`. On update, use the corresponding `UpdateParams` types; `mcp_server_url` is immutable.

OAuth refresh token endpoint auth variants: `none`, `client_secret_basic`, `client_secret_post`. [Source: api-reference/03-vaults.md]

### 16.5 Memory Stores API

Memory store endpoints: [Source: api-reference/04-memory-stores.md, "Confirmed Endpoints"]

| Method | Path | Operation |
|---|---|---|
| POST | `/v1/memory_stores` | Create Memory Store |
| GET | `/v1/memory_stores` | List Memory Stores |
| GET | `/v1/memory_stores/{memory_store_id}` | Get Memory Store |
| POST | `/v1/memory_stores/{memory_store_id}` | Update Memory Store |
| DELETE | `/v1/memory_stores/{memory_store_id}` | Delete Memory Store |
| POST | `/v1/memory_stores/{memory_store_id}/archive` | Archive Memory Store |

Memory endpoints:

| Method | Path | Operation |
|---|---|---|
| POST | `/v1/memory_stores/{memory_store_id}/memories` | Write Memory |
| GET | `/v1/memory_stores/{memory_store_id}/memories` | List Memories |
| GET | `/v1/memory_stores/{memory_store_id}/memories/{memory_id}` | Get Memory |
| POST | `/v1/memory_stores/{memory_store_id}/memories/{memory_id}` | Update Memory |
| DELETE | `/v1/memory_stores/{memory_store_id}/memories/{memory_id}` | Delete Memory |

Memory version endpoints (see §15.9 — may be 404 in current deployment):

| Method | Path | Operation |
|---|---|---|
| GET | `/v1/memory_stores/{store_id}/memory_versions` | List Memory Versions (with `memory_id`, `operation`, etc. filters) |
| GET | `/v1/memory_stores/{store_id}/memory_versions/{version_id}` | Retrieve Memory Version |
| POST | `/v1/memory_stores/{store_id}/memory_versions/{version_id}/redact` | Redact Memory Version |

### 16.6 Beta header values

The `anthropic-beta` header accepts an array. Known values: [Source: api-reference/02-environments.md, "AnthropicBeta Header Values"; api-reference/01-agents.md, "Beta Header"]

`message-batches-2024-09-24`, `prompt-caching-2024-07-31`, `computer-use-2024-10-22`, `computer-use-2025-01-24`, `pdfs-2024-09-25`, `token-counting-2024-11-01`, `token-efficient-tools-2025-02-19`, `output-128k-2025-02-19`, `files-api-2025-04-14`, `mcp-client-2025-04-04`, `mcp-client-2025-11-20`, `dev-full-thinking-2025-05-14`, `interleaved-thinking-2025-05-14`, `code-execution-2025-05-22`, `extended-cache-ttl-2025-04-11`, `context-1m-2025-08-07`, `context-management-2025-06-27`, `model-context-window-exceeded-2025-08-26`, `skills-2025-10-02`, `fast-mode-2026-02-01`, `output-300k-2026-03-24`, `advisor-tool-2026-03-01`.

For Managed Agents specifically: `managed-agents-2026-04-01` (required on every request) and `managed-agents-2026-04-01-research-preview` (for outcomes, multiagent, memory).

### 16.7 Validation Constraints Summary

[Source: api-reference/01-agents.md, "Validation Constraints Summary"]

| Constraint | Limit |
|---|---|
| Agent name length | 1–256 characters |
| Agent description length | Up to 2048 characters |
| Agent system prompt length | Up to 100,000 characters |
| Metadata pairs | Maximum 16 |
| Metadata key length | Up to 64 characters |
| Metadata value length | Up to 512 characters |
| MCP servers per agent | Maximum 20 (unique names) |
| Skills per agent / per session | Maximum 20 |
| Tools per agent | Maximum 128 across all toolsets |
| MCP server name | 1–255 characters |
| MCP tool name | 1–128 characters |
| Custom tool name | 1–128 characters (letters, digits, underscores, hyphens) |
| Custom tool description | 1–1024 characters |
| Vault display_name | 1–255 characters |
| Credentials per vault | Maximum 20 |
| Memory stores per session | Maximum 8 |
| Individual memory size | 100 KB (~25K tokens) |
| Memory store session `prompt` | Max 4,096 characters |
| Outcome `max_iterations` | Default 3, max 20 |

### 16.8 Error semantics

Every `session.error` event carries an `error` object with `message`, `type`, and `retry_status` (`retrying` / `exhausted` / `terminal`). Error types: `unknown_error`, `model_overloaded_error`, `model_rate_limited_error`, `model_request_failed_error`, `mcp_connection_failed_error` (includes `mcp_server_name`), `mcp_authentication_failed_error` (includes `mcp_server_name`), `billing_error`. [Source: api-reference/00-sessions.md, session error definitions]

Memory preconditions: failed `not_exists` or `content_sha256` preconditions return `409 memory_precondition_failed`. [Source: 14-memory.md, "Safe writes" and "Safe content edits"]

Credential `mcp_server_url` collisions: `409`. [Source: 10-vaults.md, "Constraints"]

---

## 17. Critical Gotchas & Guardrails

This section collects non-obvious behaviors surfaced across the source docs. Each item attributed to its source.

### Beta headers

- **Every request requires the base beta header `managed-agents-2026-04-01`.** The SDK injects it automatically; raw HTTP must include it. [Source: every file's "Note" block]
- **Research preview features require an additional beta header** `managed-agents-2026-04-01-research-preview` — outcomes, multi-agent, memory. [Source: 13-define-outcomes.md; 14-memory.md; 12-multi-agent.md]
- **File-based rubrics additionally require `files-api-2025-04-14`.** [Source: 13-define-outcomes.md]

### Streaming & events

- **Open the stream before sending the user event.** Buffered events start only from the moment the stream is opened. [Source: 05-events-and-streaming.md, "Streaming responses"]
- **`processed_at: null` means queued**, not dropped — the event will be handled after preceding events. [Source: 05-events-and-streaming.md, "Event types"]
- **Reconnecting losslessly requires listing history AND tailing the live stream**, de-duping by event ID. [Source: 05-events-and-streaming.md, "Streaming responses"]
- **`session.deleted` terminates the stream.** No further events. [Source: api-reference/00-sessions.md]
- **Partial `requires_action` resolution re-emits idle** with the remaining blockers. [Source: api-reference/00-sessions.md, `BetaManagedAgentsSessionRequiresAction`]
- **Cache TTL is 5 minutes.** Back-to-back turns benefit from caching; longer gaps lose it. [Source: 05-events-and-streaming.md, "Tracking usage"]

### Agents

- **Update is optimistic — must include current `version`.** Version mismatch = rejection. [Source: api-reference/01-agents.md, "Update Agent"]
- **Array fields (`tools`, `skills`, `mcp_servers`, `callable_agents`) are full replacement on update**, not merge. [Source: 02-agent-setup.md, "Update semantics"]
- **`model` and `name` cannot be cleared on update.** [Source: 02-agent-setup.md, "Update semantics"]
- **No-op update returns existing version** — version is not bumped. [Source: 02-agent-setup.md, "Update semantics"]
- **Archiving is one-way for new sessions only.** Existing sessions continue running; new sessions cannot reference. [Source: 02-agent-setup.md, "Agent lifecycle"]
- **Bare-string `agent` ID pins LATEST version.** Object form is required to pin a specific version. [Source: 04-sessions.md, "Creating a session"]

### Environments

- **Environments are NOT versioned.** Config updates affect future sessions silently; log updates on your side if needed. [Source: 03-environments.md, "Environment lifecycle"]
- **`allowed_hosts` must be HTTPS-prefixed.** [Source: 03-environments.md, "Networking"]
- **`networking` does not affect `web_search`/`web_fetch` tool domains.** [Source: 03-environments.md, "Networking"]
- **Package managers run in alphabetical order** (apt, cargo, gem, go, npm, pip). [Source: 03-environments.md, "Packages"]
- **Delete an environment only if no sessions reference it.** Otherwise archive. [Source: 03-environments.md, "Manage environments"]
- **Environment `name` must be unique within org/workspace.** [Source: 03-environments.md, after create]

### Sessions

- **A `running` session cannot be deleted** — send an interrupt first. [Source: 04-sessions.md, "Deleting a session"]
- **Deleting a session does NOT delete its files, memory stores, environments, or agents.** [Source: 04-sessions.md, "Deleting a session"]
- **`vault_ids` on update is rejected**; vaults can only be set at session creation. [Source: api-reference/00-sessions.md, "Update Session"]
- **Sessions start in `idle` status**, not running. Creation does not begin work. [Source: 04-sessions.md]

### Tools / Permissions

- **Default policies differ by toolset** — `agent_toolset_20260401` defaults to `always_allow`; `mcp_toolset` defaults to `always_ask`. [Source: 09-permission-policies.md]
- **Custom tools bypass all permission policies.** Your application must authorize them. [Source: 09-permission-policies.md, "Custom tools"]
- **`deny_message` only valid with `result: "deny"`.** [Source: api-reference/00-sessions.md, `BetaManagedAgentsUserToolConfirmationEventParams`]
- **Max 128 tools across all toolsets per agent.** [Source: api-reference/01-agents.md]
- **Custom tool names: letters, digits, underscores, hyphens only.** [Source: api-reference/01-agents.md]

### MCP

- **Max 20 MCP servers per agent; names unique.** [Source: api-reference/01-agents.md]
- **Invalid MCP credentials DO NOT fail session creation** — session emits `session.error` at runtime. [Source: 08-mcp-connector.md]
- **Auth retries on idle→running transitions** only. [Source: 08-mcp-connector.md]
- **Container must have network access to the MCP server URL.** With `limited` networking, set `allow_mcp_servers: true` or add to `allowed_hosts`. [Source: 03-environments.md, "Networking"]
- **Only remote HTTP streamable-transport MCP servers are supported.** No stdio. [Source: 08-mcp-connector.md, "Supported MCP server types"]
- **`mcp_server_name` in `mcp_toolset` must match a `name` in `mcp_servers`.** [Source: 08-mcp-connector.md]

### Vaults

- **Secret fields are write-only.** Cannot be read back; re-supply to rotate. [Source: 10-vaults.md, "Warning"]
- **`mcp_server_url`, `token_endpoint`, `client_id` are immutable** after credential creation. To change, archive and recreate. [Source: 10-vaults.md, "Rotate a credential"]
- **One active credential per `mcp_server_url` per vault.** Second creation returns 409. [Source: 10-vaults.md, "Constraints"]
- **Vaults are workspace-scoped.** Anyone with API key access can use them. [Source: 10-vaults.md, "Warning"]
- **First matching vault wins** when multiple vaults cover the same MCP server. [Source: 10-vaults.md, "Reference the vault at session creation"]
- **Archive vault cascades to all credentials.** [Source: 10-vaults.md, "Other operations"]
- **Credentials are re-resolved periodically at runtime** — rotations propagate to running sessions without restart. [Source: 10-vaults.md, "Reference the vault at session creation"]
- **Max 20 credentials per vault.** [Source: 10-vaults.md, "Constraints"]

### Multi-agent

- **Only ONE level of delegation.** Sub-agents cannot call sub-agents. [Source: 12-multi-agent.md, "Declare callable agents"]
- **All agents share the same container and filesystem**, but NOT context/tools/MCP. [Source: 12-multi-agent.md, "How it works"]
- **Echo `session_thread_id` when replying to subagent-thread requests** (tool confirmation, custom tool result) — otherwise the platform cannot route the reply to the waiting thread. [Source: 12-multi-agent.md, "Tool permissions and custom tools in threads"]
- **Session status aggregates across threads.** `running` if any thread is running. [Source: 12-multi-agent.md, "Session threads"]
- **Skills count across all agents in a multiagent session** — total cap still 20 per session. [Source: 07-skills.md, "Enable skills on a session"]

### Outcomes

- **Rubric is required.** [Source: 13-define-outcomes.md, "Create a rubric"]
- **Only ONE outcome at a time.** Chain by sending a new `user.define_outcome` after the terminal event. [Source: 13-define-outcomes.md]
- **`max_iterations` default 3, max 20.** [Source: 13-define-outcomes.md]
- **Grader reasoning is opaque.** [Source: 13-define-outcomes.md, "Outcome evaluation ongoing"]
- **`result: "failed"` means rubric contradicts description**, not grading failure. [Source: 13-define-outcomes.md, result table]
- **Deliverables land in `/mnt/session/outputs/`** — fetch via Files API with `scope_id=$session_id`. [Source: 13-define-outcomes.md, "Retrieving deliverables"]

### Memory

- **Individual memory cap: 100 KB (~25K tokens).** Prefer many small focused files. [Source: 14-memory.md, "Seed it with content"]
- **Max 8 memory stores per session; session `prompt` max 4,096 chars.** [Source: 14-memory.md]
- **`access` defaults to `read_write`** — if you want read-only, set it explicitly. [Source: 14-memory.md]
- **`memories.write` upserts by path.** Use `memories.update` to rename or do safe content edits by ID. [Source: 14-memory.md, "Create a memory"]
- **Path prefix must include trailing slash** to avoid matching `_backup` style suffixes. [Source: 14-memory.md, "List memories"]
- **Failed preconditions return `409 memory_precondition_failed`.** Re-read and retry. [Source: 14-memory.md, "Safe content edits"]
- **Memory version/redact endpoints may currently return 404.** [Source: api-reference/04-memory-stores.md]
- **Every mutation creates an immutable version.** Accumulates for lifetime of parent memory. [Source: 14-memory.md, "Audit memory changes"]

### Containers

- **The conceptual docs and environment docs disagree on the default network state.** `11-cloud-containers.md` says "Network: Disabled by default (enable in environment config)"; `03-environments.md` says `unrestricted` is the default. In practice, creating an environment without specifying `networking` is documented as producing unrestricted access. [Source conflict: 11-cloud-containers.md vs 03-environments.md]
- **Database servers are NOT running** — only clients. SQLite is local-only. [Source: 11-cloud-containers.md]
- **x86_64 (amd64) only.** No ARM containers. [Source: 11-cloud-containers.md]

---

## 18. Limitations & Known Constraints

### Rate limits

- 60 requests/minute for create endpoints (agents, sessions, environments, vaults, etc.). [Source: 00-overview.md, "Rate limits"]
- 600 requests/minute for read endpoints. [Source: 00-overview.md, "Rate limits"]
- Organization spend limits and tier-based model rate limits apply separately. [Source: 00-overview.md, "Rate limits"]

### Agent/resource limits

- Max 128 tools across all toolsets per agent. [Source: api-reference/01-agents.md]
- Max 20 MCP servers per agent (unique names). [Source: api-reference/01-agents.md]
- Max 20 skills per session (across all agents in multiagent). [Source: 07-skills.md]
- Max 16 metadata pairs per agent / vault / credential / session; keys ≤64 chars; values ≤512 chars. [Source: api-reference/01-agents.md; api-reference/03-vaults.md; api-reference/00-sessions.md]
- Max 20 credentials per vault. [Source: 10-vaults.md]
- Max 8 memory stores per session. [Source: 14-memory.md]
- Max 100 KB per individual memory (~25K tokens). [Source: 14-memory.md]
- Memory store session `prompt` max 4,096 characters. [Source: 14-memory.md]
- `max_iterations` for outcomes: default 3, max 20. [Source: 13-define-outcomes.md]

### String length caps

- Agent `name`: 1–256 chars. [Source: api-reference/01-agents.md]
- Agent `description`: ≤2048 chars. [Source: api-reference/01-agents.md]
- Agent `system`: ≤100,000 chars. [Source: api-reference/01-agents.md]
- Vault `display_name`: 1–255 chars. [Source: api-reference/03-vaults.md]
- MCP server `name`: 1–255 chars. [Source: api-reference/01-agents.md]
- MCP tool `name`: 1–128 chars. [Source: api-reference/01-agents.md]
- Custom tool `name`: 1–128 chars (alphanumeric + `_` + `-`). [Source: api-reference/01-agents.md]
- Custom tool `description`: 1–1024 chars. [Source: api-reference/01-agents.md]

### Container limits

- Memory: up to 8 GB. [Source: 11-cloud-containers.md]
- Disk: up to 10 GB. [Source: 11-cloud-containers.md]
- OS: Ubuntu 22.04 LTS, x86_64 only. [Source: 11-cloud-containers.md]
- `docker` has "limited availability." [Source: 11-cloud-containers.md]

### Feature gating

- Outcomes, multi-agent, memory are in research preview and require access request. [Source: 00-overview.md, "Beta access"]
- Multi-agent delegation: only one level. [Source: 12-multi-agent.md]
- Only one outcome at a time per session. [Source: 13-define-outcomes.md]
- Memory Version/Redact API endpoints may return 404 in current deployment. [Source: api-reference/04-memory-stores.md]
- SDK support for Memory Stores is not yet present in Python/TypeScript SDKs. [Source: api-reference/04-memory-stores.md]

### Unsupported configurations

- Local stdio MCP servers not supported — remote HTTP streamable-transport only. [Source: 08-mcp-connector.md]
- `vault_ids` on session update is not supported. [Source: api-reference/00-sessions.md, "Update Session"]
- Updating an agent does not retroactively affect sessions that pinned a specific version.
- Secret credential fields are write-only and cannot be read back. [Source: 10-vaults.md]
- `mcp_server_url`, `token_endpoint`, `client_id` cannot be changed after credential creation. [Source: 10-vaults.md]
- Environments are not versioned; no rollback. [Source: 03-environments.md]

---

*End of canonical reference.*
