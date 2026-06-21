import logging
from google.adk.agents import LlmAgent
from google.adk.apps import App
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from mcp import StdioServerParameters
from intent_classifier import classify_intent
from prompt_registry import get_prompt
from token_counter import TokenCostCalculator

logger = logging.getLogger(__name__)

OLLAMA_MODEL = "ollama_chat/llama3.1:latest"


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


# Context7 MCP toolset — provides live library documentation via npx
# Requires Node.js: https://context7.com
_context7_toolset = MCPToolset(
    connection_params=StdioServerParameters(
        command="npx",
        args=["-y", "@upstash/context7-mcp"],
        env={"DEFAULT_MINIMUM_TOKENS": "10000"},
    ),
    tool_filter=["resolve-library-id", "get-library-docs"],
)

# Individual specialized agents
docs_agent = CustomLlmAgent(
    name="docs_agent",
    model=LiteLlm(model=OLLAMA_MODEL),
    instruction=get_prompt("docs_agent"),
    tools=[_context7_toolset],
)

codebase_agent = CustomLlmAgent(
    name="codebase_agent",
    model=LiteLlm(model=OLLAMA_MODEL),
    instruction=get_prompt("codebase_agent"),
)

research_agent = CustomLlmAgent(
    name="research_agent",
    model=LiteLlm(model=OLLAMA_MODEL),
    instruction=get_prompt("research_agent"),
)

execution_agent = CustomLlmAgent(
    name="execution_agent",
    model=LiteLlm(model=OLLAMA_MODEL),
    instruction=get_prompt("execution_agent"),
)

# Root agent that coordinates all specialists
root_agent = CustomLlmAgent(
    name="root_agent",
    model=LiteLlm(model=OLLAMA_MODEL),
    instruction=get_prompt("root_agent"),
    sub_agents=[docs_agent, codebase_agent, research_agent, execution_agent],
    tools=[classify_intent],
)

app = App(
    root_agent=root_agent,
    name="app",
)