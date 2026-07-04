import contextvars
import logging
import os
from pydantic import ValidationError
from google.adk.agents import LlmAgent
from google.adk.apps import App
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams
from google.adk.plugins import ReflectAndRetryToolPlugin
from mcp.shared._httpx_utils import create_mcp_http_client
from intent_classifier import classify_intent
from prompt_registry import get_prompt
from observability.token_counter import TokenCostCalculator
from observability.metrics import metrics, get_current_user

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
    
    def __init__(self, *args, max_validation_retries: int = 3, **kwargs):
        super().__init__(*args, **kwargs)
        self._token_calculator = TokenCostCalculator(OLLAMA_MODEL)
        # LlmAgent is a pydantic model with ``extra="forbid"``, so only private
        # (underscore-prefixed) attributes can be set on an instance. Keep this
        # private and expose it via a read-only property below.
        self._max_validation_retries = max_validation_retries
        # Bind callbacks properly
        self.before_model_callback = self._before_model_callback_impl
        self.after_model_callback = self._after_model_callback_impl
        self._last_input_text = ""  # Store input for use in after callback

    @property
    def max_validation_retries(self) -> int:
        """How many times structured-output validation is retried before failing."""
        return self._max_validation_retries

    def _before_model_callback_impl(self, callback_context, llm_request) -> None:
        """Log input tokens and estimated cost before model call."""
        self._last_input_text = str(llm_request.contents)
        input_tokens = self._token_calculator.count_tokens(self._last_input_text)
        # _price returns a TokenUsage; the estimated input cost is its total_cost.
        input_cost = self._token_calculator._price(
            input_tokens, 0, source="estimated"
        ).total_cost
        logger.info(
            f"[{self.name}] INPUT → {input_tokens:,} tokens | "
            f"Estimated: ${input_cost:.6f}"
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
        # Attribute this model call's usage to the current user (all agents in a
        # request share one user via the context var set by the gateway).
        metrics.record_tokens(
            get_current_user(),
            input_tokens=usage.input_tokens,
            output_tokens=usage.output_tokens,
            cost_usd=usage.total_cost,
        )

    async def _run_async_impl(self, ctx):
        """Run the agent with retry logic for validation errors.

        Both structured-output paths raise pydantic.ValidationError from inside
        ADK's _run_async_impl: the `set_model_response` tool (output_schema +
        tools) and the plain-text postprocess (__maybe_save_output_to_state).
        
        This wrapper retries on validation errors up to max_validation_retries times,
        logging each failure before retrying.
        """
        for attempt in range(self.max_validation_retries):
            try:
                async for event in super()._run_async_impl(ctx):
                    yield event
                return  # Success
            except ValidationError as exc:
                is_last_attempt = attempt == self.max_validation_retries - 1
                logger.warning(
                    "[%s] VALIDATION ERROR (attempt %d/%d): output failed %s validation "
                    "(%d error(s)): %s%s",
                    self.name,
                    attempt + 1,
                    self.max_validation_retries,
                    getattr(self.output_schema, "__name__", "?"),
                    exc.error_count(),
                    exc.errors(include_url=False),
                    " — retrying..." if not is_last_attempt else " — max retries exceeded",
                )
                metrics.record_hallucination(get_current_user())
                
                if is_last_attempt:
                    raise  # Re-raise on last attempt

# Resolve an agent's instruction from the registry at run time (ADK
# InstructionProvider) rather than capturing a fixed string at construction, so
# a prompt rollback via the registry takes effect on the next request without
# rebuilding the agents.
def _prompt_provider(name: str):
    return lambda _ctx: get_prompt(name)


# Individual specialized agents. They share the same wiring (local model + all
# team MCP toolsets) and differ only by name, prompt, and structured-output
# schema. output_key derives from the name (docs_agent -> docs_result) so each
# typed result lands in session state under a predictable key.
def _specialist(name: str, output_schema) -> CustomLlmAgent:
    return CustomLlmAgent(
        name=name,
        model=LiteLlm(model=OLLAMA_MODEL),
        instruction=_prompt_provider(name),
        output_schema=output_schema,
        output_key=name.replace("_agent", "_result"),
        tools=team_toolsets(),
    )


docs_agent = _specialist("docs_agent", DocsOutput)
codebase_agent = _specialist("codebase_agent", CodebaseOutput)
research_agent = _specialist("research_agent", ResearchOutput)
execution_agent = _specialist("execution_agent", ExecutionOutput)

# Root agent that coordinates all specialists. The specialists are registered
# as sub_agents so the root agent can delegate to them (transfer_to_agent);
# the MCP tools live on those specialists, so without this wiring they are
# never reachable.
root_agent = CustomLlmAgent(
    name="root_agent",
    model=LiteLlm(model=OLLAMA_MODEL),
    instruction=_prompt_provider("root_agent"),
    tools=[classify_intent], # classify intent at every turn
    sub_agents=[docs_agent, codebase_agent, research_agent, execution_agent],
)

app = App(
    root_agent=root_agent,
    name="app",
    plugins=[
        ReflectAndRetryToolPlugin(max_retries=3),
    ],
)