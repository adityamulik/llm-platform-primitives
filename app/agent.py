import contextvars
import logging
import os
from google.adk.agents import LlmAgent
from google.adk.apps import App
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams
from mcp.shared._httpx_utils import create_mcp_http_client
from intent_classifier import classify_intent
from prompt_registry import get_prompt
from observability.token_counter import TokenCostCalculator

from app.model import (
    CodebaseOutput,
    DocsOutput,
    ExecutionOutput,
    ResearchOutput,
)

logger = logging.getLogger(__name__)

OLLAMA_MODEL = "ollama_chat/llama3.1:latest"

# Caller's bearer token for the current request, threaded into the MCP HTTP
# calls so each MCP server can authorize the tool call (server-side RBAC). Set
# by the gateway via set_request_auth() before running the agent.
_current_auth: contextvars.ContextVar[str] = contextvars.ContextVar("current_auth", default="")


def set_request_auth(authorization: str | None) -> None:
    """Record the caller's Authorization header for the current request."""
    _current_auth.set(authorization or "")


def _auth_http_client_factory(headers=None, timeout=None, auth=None):
    """httpx client for MCP that injects the caller's token on every request."""
    client = create_mcp_http_client(headers=headers, timeout=timeout, auth=auth)

    async def _inject_auth(request):
        token = _current_auth.get()
        if token:
            request.headers["Authorization"] = token

    client.event_hooks.setdefault("request", []).append(_inject_auth)
    return client

# Independent team MCP servers, assumed already running over HTTP. Agents just
# connect to them. Partitioned per team so an auth/authz layer can later gate
# which agent/role may reach which team. Override URLs via env if needed.
_TEAM_SERVERS = {
    "team_a": os.getenv("TEAM_A_MCP_URL", "http://localhost:8001/mcp"),
    "team_b": os.getenv("TEAM_B_MCP_URL", "http://localhost:8002/mcp"),
    "team_c": os.getenv("TEAM_C_MCP_URL", "http://localhost:8003/mcp"),
}


def _team_toolset(url: str) -> MCPToolset:
    """Build an MCPToolset that connects to a running team MCP server.

    Fresh instance per agent so toolsets aren't shared across agents. The
    caller's bearer token is injected per request by _auth_http_client_factory
    so the MCP server can enforce RBAC.
    """
    return MCPToolset(
        connection_params=StreamableHTTPConnectionParams(
            url=url,
            headers={},
            httpx_client_factory=_auth_http_client_factory,
        ),
    )


def team_toolsets() -> list[MCPToolset]:
    """All team MCP toolsets, so agents can use them interchangeably."""
    return [_team_toolset(u) for u in _TEAM_SERVERS.values()]


class CustomLlmAgent(LlmAgent):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._token_calculator = TokenCostCalculator(OLLAMA_MODEL)
        # Bind callbacks properly
        self.before_model_callback = self._before_model_callback_impl
        self.after_model_callback = self._after_model_callback_impl
        self._last_input_text = ""  # Store input for use in after callback

    def _before_model_callback_impl(self, callback_context, llm_request) -> None:
        """Log input tokens and estimated cost before model call."""
        self._last_input_text = str(llm_request.contents)
        input_tokens = self._token_calculator.count_tokens(self._last_input_text)
        input_cost = self._token_calculator._price(input_tokens, 0, source="estimated")
        logger.info(
            f"[{self.name}] INPUT → {input_tokens:,} tokens | "
            f"Estimated: ${input_cost.input_cost:.6f}"
        )
    
    def _after_model_callback_impl(self, callback_context, llm_response) -> None:
        """Log output tokens and total cost after model call."""
        output_text = str(llm_response.content)
        usage = self._token_calculator.calculate(self._last_input_text, output_text)
        logger.info(
            f"[{self.name}] OUTPUT ← {usage.output_tokens:,} tokens | "
            f"Total: {usage.input_tokens:,} in + {usage.output_tokens:,} out = ${usage.total_cost:.6f}"
        )
        logger.info(f"[{self.name}] Output text: {output_text[:500]}...")

# Individual specialized agents
docs_agent = CustomLlmAgent(
    name="docs_agent",
    model=LiteLlm(model=OLLAMA_MODEL),
    instruction=get_prompt("docs_agent"),
    output_schema=DocsOutput,
    output_key="docs_result",
    tools=team_toolsets(),
)

codebase_agent = CustomLlmAgent(
    name="codebase_agent",
    model=LiteLlm(model=OLLAMA_MODEL),
    instruction=get_prompt("codebase_agent"),
    output_schema=CodebaseOutput,
    output_key="codebase_result",
    tools=team_toolsets(),
)

research_agent = CustomLlmAgent(
    name="research_agent",
    model=LiteLlm(model=OLLAMA_MODEL),
    instruction=get_prompt("research_agent"),
    output_schema=ResearchOutput,
    output_key="research_result",
    tools=team_toolsets(),
)

execution_agent = CustomLlmAgent(
    name="execution_agent",
    model=LiteLlm(model=OLLAMA_MODEL),
    instruction=get_prompt("execution_agent"),
    output_schema=ExecutionOutput,
    output_key="execution_result",
    tools=team_toolsets(),
)

# Root agent that coordinates all specialists. The specialists are registered
# as sub_agents so the root agent can delegate to them (transfer_to_agent);
# the MCP tools live on those specialists, so without this wiring they are
# never reachable.
root_agent = CustomLlmAgent(
    name="root_agent",
    model=LiteLlm(model=OLLAMA_MODEL),
    instruction=get_prompt("root_agent"),
    tools=[classify_intent], # classify intent at every turn
    sub_agents=[docs_agent, codebase_agent, research_agent, execution_agent],
)

app = App(
    root_agent=root_agent,
    name="app",
)