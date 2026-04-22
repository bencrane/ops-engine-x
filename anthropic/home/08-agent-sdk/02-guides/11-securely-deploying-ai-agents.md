# Securely deploying AI agents

A guide to securing Claude Code and Agent SDK deployments with isolation, credential management, and network controls.

Claude Code and the Agent SDK are powerful tools that can execute code, access files, and interact with external services on your behalf. Like any tool with these capabilities, deploying them thoughtfully ensures you get the benefits while maintaining appropriate controls.

Unlike traditional software that follows predetermined code paths, these tools generate their actions dynamically based on context and goals. This flexibility is what makes them useful, but it also means their behavior can be influenced by the content they process: files, webpages, or user input. This is sometimes called prompt injection. This guide covers practical ways to reduce this risk.

The same principles that apply to running any semi-trusted code apply here: isolation, least privilege, and defense in depth.

## Threat model

Agents can take unintended actions due to prompt injection (instructions embedded in content they process) or model error. Claude models are designed to resist this, and Claude Opus 4.6 is the most robust frontier model available.

Defense in depth is still good practice though. For example, if an agent processes a malicious file that instructs it to send customer data to an external server, network controls can block that request entirely.

## Built-in security features

Claude Code includes several security features that address common concerns:

- **Permissions system**: Every tool and bash command can be configured to allow, block, or prompt the user for approval. Use glob patterns to create rules like "allow all npm commands" or "block any command with sudo".
- **Static analysis**: Before executing bash commands, Claude Code runs static analysis to identify potentially risky operations.
- **Web search summarization**: Search results are summarized rather than passing raw content directly into the context, reducing the risk of prompt injection from malicious web content.
- **Sandbox mode**: Bash commands can run in a sandboxed environment that restricts filesystem and network access.

## Security principles

### Security boundaries

A security boundary separates components with different trust levels. For high-security deployments, you can place sensitive resources (like credentials) outside the boundary containing the agent.

For example, rather than giving an agent direct access to an API key, you could run a proxy outside the agent's environment that injects the key into requests.

### Least privilege

When needed, you can restrict the agent to only the capabilities required for its specific task:

| Resource | Restriction options |
|---|---|
| Filesystem | Mount only needed directories, prefer read-only |
| Network | Restrict to specific endpoints via proxy |
| Credentials | Inject via proxy rather than exposing directly |
| System capabilities | Drop Linux capabilities in containers |

### Defense in depth

For high-security environments, layering multiple controls provides additional protection: container isolation, network restrictions, filesystem controls, and request validation at a proxy.

## Isolation technologies

| Technology | Isolation strength | Performance overhead | Complexity |
|---|---|---|---|
| Sandbox runtime | Good (secure defaults) | Very low | Low |
| Containers (Docker) | Setup dependent | Low | Medium |
| gVisor | Excellent (with correct setup) | Medium/High | Medium |
| VMs (Firecracker, QEMU) | Excellent (with correct setup) | High | Medium/High |

### Sandbox runtime

For lightweight isolation without containers, sandbox-runtime enforces filesystem and network restrictions at the OS level.

- **Filesystem**: Uses OS primitives (bubblewrap on Linux, sandbox-exec on macOS) to restrict read/write access to configured paths
- **Network**: Removes network namespace (Linux) or uses Seatbelt profiles (macOS) to route network traffic through a built-in proxy
- **Configuration**: JSON-based allowlists for domains and filesystem paths

```bash
npm install @anthropic-ai/sandbox-runtime
```

**Security considerations**: Sandboxed processes share the host kernel. A kernel vulnerability could theoretically enable escape. The proxy allowlists domains but doesn't inspect encrypted traffic.

### Containers

Containers provide isolation through Linux namespaces. A security-hardened container configuration:

```bash
docker run \
  --cap-drop ALL \
  --security-opt no-new-privileges \
  --security-opt seccomp=/path/to/seccomp-profile.json \
  --read-only \
  --tmpfs /tmp:rw,noexec,nosuid,size=100m \
  --tmpfs /home/agent:rw,noexec,nosuid,size=500m \
  --network none \
  --memory 2g \
  --cpus 2 \
  --pids-limit 100 \
  --user 1000:1000 \
  -v /path/to/code:/workspace:ro \
  -v /var/run/proxy.sock:/var/run/proxy.sock:ro \
  agent-image
```

Key options:

| Option | Purpose |
|---|---|
| --cap-drop ALL | Removes Linux capabilities that could enable privilege escalation |
| --security-opt no-new-privileges | Prevents processes from gaining privileges through setuid binaries |
| --read-only | Makes the container's root filesystem immutable |
| --network none | Removes all network interfaces; agent communicates through mounted Unix socket |
| --memory 2g | Limits memory usage to prevent resource exhaustion |
| --pids-limit 100 | Limits process count to prevent fork bombs |
| --user 1000:1000 | Runs as a non-root user |

With --network none, the container has no network interfaces at all. The only way for the agent to reach the outside world is through the mounted Unix socket, which connects to a proxy running on the host.

### gVisor

Standard containers share the host kernel. gVisor addresses this by intercepting system calls in userspace before they reach the host kernel.

```json
// /etc/docker/daemon.json
{
  "runtimes": {
    "runsc": {
      "path": "/usr/local/bin/runsc"
    }
  }
}
```

```bash
docker run --runtime=runsc agent-image
```

Performance considerations:

| Workload | Overhead |
|---|---|
| CPU-bound computation | ~0% |
| Simple syscalls | ~2x slower |
| File I/O intensive | Up to 10-200x slower for heavy open/close patterns |

### Virtual machines

VMs provide hardware-level isolation through CPU virtualization extensions. Firecracker is designed for lightweight microVM isolation, booting VMs in under 125ms with less than 5 MiB memory overhead.

### Cloud deployments

For cloud deployments, combine isolation technologies with cloud-native network controls:

- Run agent containers in a private subnet with no internet gateway
- Configure cloud firewall rules to block all egress except to your proxy
- Run a proxy that validates requests, enforces domain allowlists, and injects credentials
- Assign minimal IAM permissions to the agent's service account
- Log all traffic at the proxy for audit purposes

## Credential management

### The proxy pattern

The recommended approach is to run a proxy outside the agent's security boundary that injects credentials into outgoing requests. The agent sends requests without credentials, the proxy adds them, and forwards the request.

Benefits:
- The agent never sees the actual credentials
- The proxy can enforce an allowlist of permitted endpoints
- The proxy can log all requests for auditing
- Credentials are stored in one secure location

### Configuring Claude Code to use a proxy

**Option 1: ANTHROPIC_BASE_URL** (simple but only for sampling API requests)

```bash
export ANTHROPIC_BASE_URL="http://localhost:8080"
```

**Option 2: HTTP_PROXY / HTTPS_PROXY** (system-wide)

```bash
export HTTP_PROXY="http://localhost:8080"
export HTTPS_PROXY="http://localhost:8080"
```

### Implementing a proxy

You can build your own proxy or use an existing one:

- **Envoy Proxy**: production-grade proxy with credential_injector filter
- **mitmproxy**: TLS-terminating proxy for inspecting and modifying HTTPS traffic
- **Squid**: caching proxy with access control lists
- **LiteLLM**: LLM gateway with credential injection and rate limiting

### Credentials for other services

Beyond the Claude API, agents often need authenticated access to other services. Two main approaches:

**Custom tools**: Provide access through an MCP server or custom tool that routes requests to a service running outside the agent's security boundary.

**Traffic forwarding**: For HTTPS services, use a TLS-terminating proxy that decrypts traffic, inspects or modifies it, then re-encrypts before forwarding. This requires installing the proxy's CA certificate in the agent's trust store.

## Filesystem configuration

### Read-only code mounting

```bash
docker run -v /path/to/code:/workspace:ro agent-image
```

Common files to exclude or sanitize before mounting:

| File | Risk |
|---|---|
| .env, .env.local | API keys, database passwords, secrets |
| ~/.git-credentials | Git passwords/tokens in plaintext |
| ~/.aws/credentials | AWS access keys |
| ~/.config/gcloud/application_default_credentials.json | Google Cloud ADC tokens |
| ~/.docker/config.json | Docker registry auth tokens |
| ~/.kube/config | Kubernetes cluster credentials |
| .npmrc, .pypirc | Package registry tokens |
| *.pem, *.key | Private keys |

### Writable locations

For ephemeral workspaces, use tmpfs mounts:

```bash
docker run \
  --read-only \
  --tmpfs /tmp:rw,noexec,nosuid,size=100m \
  --tmpfs /workspace:rw,noexec,size=500m \
  agent-image
```

If you want to review changes before persisting them, an overlay filesystem lets the agent write without modifying underlying files.

## Further reading

- Claude Code security documentation
- Hosting the Agent SDK
- Handling permissions
- Sandbox runtime
- OWASP Top 10 for LLM Applications
- Docker Security Best Practices
- gVisor Documentation
- Firecracker Documentation
