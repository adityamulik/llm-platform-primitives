from google.adk.agents import Agent, LlmAgent
from google.adk.apps import App
from google.adk.models.lite_llm import LiteLlm
from intent_classifier import classify_intent
from prompt_registry import get_prompt
from google.adk.tools.toolbox_toolset import ToolboxToolset

OLLAMA_MODEL = "ollama_chat/llama3.1:latest"

# Individual specialized agents
docs_agent = LlmAgent(
    name="docs_agent",
    model=LiteLlm(
        model=OLLAMA_MODEL,
    ),
    instruction=get_prompt("docs_agent"),
)

codebase_agent = LlmAgent(
    name="codebase_agent",
    model=LiteLlm(
        model=OLLAMA_MODEL,
    ),
    instruction=get_prompt("codebase_agent"),
)

research_agent = LlmAgent(
    name="research_agent",
    model=LiteLlm(
        model=OLLAMA_MODEL,
    ),
    instruction=get_prompt("research_agent"),
)

execution_agent = LlmAgent(
    name="execution_agent",
    model=LiteLlm(
        model=OLLAMA_MODEL,
    ),
    instruction=get_prompt("execution_agent"),
)

# Root agent that coordinates all specialists
root_agent = Agent(
    name="root_agent",
    model=LiteLlm(
        model=OLLAMA_MODEL,
    ),
    instruction=get_prompt("root_agent"),
    tools=[classify_intent],
)

app = App(
    root_agent=root_agent,
    name="app",
)