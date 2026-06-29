# LLM Platform Primitives

A learning repository exploring platform-engineering patterns for LLM
applications: a **secured, multi-agent system** where an authenticated user's
role decides which tools an agent is allowed to call.

The headline idea: an LLM agent should be no more privileged than the user it
acts for. A request carries a signed token describing the caller's role, and
that role is enforced — independently — at the tool servers, so an agent can
never invoke a tool the user isn't authorized to use.

## Focus Areas

- **Auth & AuthZ** — JWT-based authentication and role-based access control (RBAC) for tools
- **Multi-agent orchestration** — a coordinator that classifies intent and delegates to specialists
- **Intent classification** — route requests to the right specialist agent
- **Structured outputs** — specialists return typed, schema-validated results (Pydantic); schema violations are flagged as hallucinations
- **Prompt versioning** — a small registry for versioned, named prompts
- **LLM observability** — per-call token/cost accounting plus per-user metrics (tokens, cost, success/error, latency)

## Architecture

```
                      ┌─────────────────────────────────────────────────┐
  user                │                  Gateway (:7010)                 │
   │  username/pass    │   /login    → validate creds, issue JWT (role)  │
   ▼                   │   /verify   → verify a token                    │
┌──────────────┐  JWT  │   /agent/execute → run the multi-agent system   │
│ Demo app     │──────▶│                                                 │
│ (:7020)      │       │   ┌───────────────────────────────────────────┐ │
│ /auth-token  │       │   │ Root agent (coordinator)                  │ │
│ /run-agent   │◀──────│   │  • classify_intent → delegate             │ │
└──────────────┘       │   │  • sub_agents: docs / codebase /          │ │
                       │   │    research / execution                   │ │
                       │   └──────────────┬────────────────────────────┘ │
                       └──────────────────│──────────────────────────────┘
                                          │ Bearer token threaded per request
                          ┌───────────────┼───────────────┐
                          ▼               ▼               ▼
                   ┌────────────┐  ┌────────────┐  ┌────────────┐
                   │ Team A     │  │ Team B     │  │ Team C     │
                   │ MCP :8001  │  │ MCP :8002  │  │ MCP :8003  │
                   │ Analytics  │  │ DevOps     │  │ Developer  │
                   │            │  │ deploy_*   │  │ read_file  │
                   │ generate_  │  │ restart_*  │  │ query_db   │
                   │  report    │  │ update_*   │  │            │
                   └────────────┘  └────────────┘  └────────────┘
                   Each MCP server independently enforces RBAC
                   (AuthzMiddleware) on every tool call.
```

### Request flow

1. **Get a token.** The client posts credentials to the demo app's
   `/auth-token`, which forwards them to the gateway's `/login`. The gateway
   validates them against `gateway/users.yaml` and returns a signed JWT whose
   claims include the user's **role**.
2. **Run the agent.** The client posts a prompt to `/run-agent` with
   `Authorization: Bearer <jwt>`. The demo app verifies the token via the
   gateway and forwards the prompt to `/agent/execute`.
3. **Coordinate + delegate.** The gateway runs the root agent, which uses
   `classify_intent` to pick a specialist and delegates to it (ADK
   `transfer_to_agent`). The specialist owns the MCP toolsets.
4. **Authorize the tool.** When a specialist calls an MCP tool, the caller's
   token is attached to the request. The MCP server decodes it, resolves the
   role, and checks it against `gateway/policies.yaml`. Unauthorized calls are
   rejected before the tool runs, and the error is surfaced back to the agent.
5. **Return a typed result.** Each specialist is bound to a Pydantic output
   schema (`app/model.py`); its final answer is validated and written to session
   state under a per-agent key. A schema-validation failure is logged and
   counted as a hallucination, and per-user token/cost/latency metrics are
   recorded for the request (see [Metrics](#metrics)).

## Security model

Authorization is layered and enforced where it matters — at the resource
(tool) servers, which trust no caller:

- **Authentication** — `gateway/authz.py` issues stateless JWTs (HS256) carrying
  the user's role. Any service holding the shared secret can verify a token
  without calling back to the gateway.
- **Per-user session isolation** — agent sessions are namespaced by the
  authenticated `user_id`, so a caller can only reuse their *own* `session_id`.
  Passing another user's `session_id` simply won't resolve (no role escalation
  via borrowed sessions).
- **Token threading** — the caller's token is propagated from the gateway,
  through the in-process agent, to the MCP servers via a `contextvars`-backed
  httpx client factory (`app/agent.py`), so every MCP request carries the
  caller's identity.
- **Server-side RBAC enforcement** — each MCP server runs `AuthzMiddleware`
  (`mcp_server/authz_middleware.py`), which verifies the token and checks
  `policy_engine.can_access_tool(role, tool)` on every `tools/call`. This is the
  authoritative enforcement point: even a direct (non-agent) caller is gated.
- **Strict delegation** — the root agent is instructed to rely on specialist
  agents rather than its own knowledge, unless the user explicitly authorizes a
  web search or a direct answer.

> **Shared secret:** the gateway and all MCP servers must use the same
> `MCP_AUTH_SECRET` (defaults to an insecure dev value) so issued tokens verify
> everywhere. Set it in every process for any non-local use.

### Roles & demo users

Roles and their permitted tools are defined in `gateway/policies.yaml`
(default posture: **deny**). Demo users live in `gateway/users.yaml`
(plaintext passwords — demo only):

| User | Password        | Role      | Example permitted tools                         |
|------|-----------------|-----------|-------------------------------------------------|
| vera | viewer-pass     | viewer    | read_file, list_directory, generate_report      |
| ana  | analyst-pass    | analyst   | query_database, read_file, generate_report      |
| dev  | developer-pass  | developer | read_file, list_directory, query_database       |
| dale | deployer-pass   | deployer  | deploy_application, restart_service, update_*    |
| root | admin-pass      | admin     | (broad administrative set)                       |

Example: `ana` (analyst) asking to deploy is **denied** — `deploy_application`
is a `deployer`/`admin` tool. The MCP server rejects it with
`Forbidden: role 'analyst' is not authorized to use tool 'deploy_application'`.

## Getting started

### Prerequisites

- [uv](https://docs.astral.sh/uv/) for dependency management
- [Ollama](https://ollama.ai/) running the `llama3.1` model (the agents use a
  local model by default)

```bash
make install        # uv sync
make ollama-setup   # one-time: pull llama3.1
make ollama-serve   # start Ollama (keep running)
```

### Run the full stack

```bash
make run-all        # start everything in the background
make kill-all       # stop everything started by run-all
```

`make run-all` starts the three MCP servers (:8001–:8003), the auth gateway
(:7010), and the demo app (:7020) — all in the background — and returns your
shell immediately. `make kill-all` stops them again (it frees each service's
port, so it cleans up even if a process was started separately).

Individual pieces:

```bash
make gateway        # auth gateway only
make main           # demo app only
make mcp-team-a     # a single MCP server (also mcp-team-b / mcp-team-c)
```

See `make help` for all targets.

### Logs

Because the services run in the background, watch them through the `logs/`
folder (git-ignored). Each service writes its own structured log file via
`observability/logging`:

| Service       | Log file               |
|---------------|------------------------|
| Demo app      | `logs/demo.log`        |
| Gateway       | `logs/gateway.log`     |
| MCP — Team A  | `logs/mcp_team_a.log`  |
| MCP — Team B  | `logs/mcp_team_b.log`  |
| MCP — Team C  | `logs/mcp_team_c.log`  |

```bash
tail -f logs/demo.log       # follow the demo app
tail -f logs/*.log          # follow everything at once
```

Raw stdout/stderr for each process is also captured alongside as `logs/*.out`
(useful if a service crashes before logging is configured).

### Metrics

The gateway aggregates per-user counters in memory and exposes them at
`GET /metrics` (`observability/metrics`): the user's team (derived from their
role), request/success/error counts, hallucinations, input/output tokens,
estimated cost, and latency.

```bash
curl -s localhost:7010/metrics            # all users
curl -s localhost:7010/metrics?user=ana   # one user
```

> Counters are in-process and reset on restart. The endpoint is unauthenticated
> and returns every user's stats — gate it before any shared deployment.

### Prompt rollback

Prompts are versioned in `prompt_registry`, and agents resolve their instruction
from the registry on every request — so rolling a prompt back to an earlier
version takes effect on the next agent run, no restart needed. The gateway
exposes this (admin-only):

```bash
# List prompts with their active version + history
curl -s localhost:7010/prompts -H "Authorization: Bearer <admin-token>"

# Roll a prompt back to an earlier version
curl -s -X POST localhost:7010/prompts/docs_agent/rollback \
  -H "Authorization: Bearer <admin-token>" \
  -H 'Content-Type: application/json' \
  -d '{"version":"1.0.0"}'
```

History is never deleted — rollback only repoints which version is active.
Changes are in-memory and reset on restart (the registry re-seeds from
`prompt_registry/prompts.py`).

### Try it (curl)

```bash
# 1) Log in as an analyst -> get a token
curl -s -X POST localhost:7020/auth-token \
  -H 'Content-Type: application/json' \
  -d '{"username":"ana","password":"analyst-pass"}'

# 2) Run the agent with the token (analyst asking to deploy is denied)
curl -s -X POST localhost:7020/run-agent \
  -H "Authorization: Bearer <token-from-step-1>" \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"Deploy billing v2.3 to production","session_id":""}'
```

## Services & ports

| Service              | Port  | Notes                                        |
|----------------------|-------|----------------------------------------------|
| Demo app (`main.py`) | 7020  | Edge proxy: `/auth-token`, `/run-agent`      |
| Gateway              | 7010  | `/login`, `/verify`, `/agent/execute`, `/health`, `/roles`, `/metrics`, `/prompts` |
| MCP — Team A         | 8001  | Analytics                                    |
| MCP — Team B         | 8002  | DevOps (deploy / restart / configure)        |
| MCP — Team C         | 8003  | Developer (files / db)                       |
| Ollama               | 11434 | Local model server                           |

> **macOS note:** avoid port 7000 — AirPlay Receiver (Control Center) binds it
> and returns 403 to everything else.

## Project layout

```
main.py                     Demo edge app (proxies to the gateway)
gateway/
  gateway_server.py         Auth gateway + agent execution endpoint
  authz.py                  JWT issue/verify helpers
  engine.py                 RBAC policy engine (loads policies.yaml)
  policies.yaml             Role -> permitted tools/resources/operations
  users.yaml                Demo user directory (user -> role)
  models.py                 Shared Pydantic request models
  helper.py                 Password check + claim resolution helpers
app/
  agent.py                  ADK multi-agent system + MCP token threading
  model.py                  Pydantic output schemas for the specialist agents
mcp_server/
  server_team_{a,b,c}.py    Independent MCP tool servers
  server_common.py          Shared server bootstrap (logging + HTTP run)
  authz_middleware.py       Per-tool RBAC enforcement (FastMCP middleware)
intent_classifier/          Keyword-based intent classification
prompt_registry/            Versioned, named prompts
observability/
  token_counter/            Token counting + cost estimation
  metrics/                  Per-user metrics (tokens, cost, success/error, latency)
  logging/                  Per-service structured logging (-> logs/)
```

## Built with

- [Google Agent Development Kit (ADK)](https://adk.dev/get-started/python/) for the multi-agent runtime
- [FastMCP](https://github.com/jlowin/fastmcp) for the MCP tool servers
- [FastAPI](https://fastapi.tiangolo.com/) for the gateway and demo app
- [Ollama](https://ollama.ai/) for local model execution (`llama3.1`)

## License

MIT
