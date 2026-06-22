import logging
from google.adk.apps import App
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from mcp import StdioServerParameters
from intent_classifier import classify_intent
from prompt_registry import get_prompt
from .custom_llm_agent import CustomLlmAgent


logger = logging.getLogger(__name__)

OLLAMA_MODEL = "ollama_chat/llama3.1:latest"


# # Individual specialized agents
# docs_agent = CustomLlmAgent(
#     name="docs_agent",
#     model=LiteLlm(model=OLLAMA_MODEL),
#     instruction=get_prompt("docs_agent"),
#     tools=[_context7_toolset],
# )

# codebase_agent = CustomLlmAgent(
#     name="codebase_agent",
#     model=LiteLlm(model=OLLAMA_MODEL),
#     instruction=get_prompt("codebase_agent"),
# )

# research_agent = CustomLlmAgent(
#     name="research_agent",
#     model=LiteLlm(model=OLLAMA_MODEL),
#     instruction=get_prompt("research_agent"),
# )

# execution_agent = CustomLlmAgent(
#     name="execution_agent",
#     model=LiteLlm(model=OLLAMA_MODEL),
#     instruction=get_prompt("execution_agent"),
# )

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