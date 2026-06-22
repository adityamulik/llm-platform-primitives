import logging
from google.adk.apps import App
from google.adk.models.lite_llm import LiteLlm
from intent_classifier import classify_intent
from prompt_registry import get_prompt
from .custom_llm_agent import CustomLlmAgent
from app.agents.analytics_agents import ANALYTICS_AGENTS


logger = logging.getLogger(__name__)

OLLAMA_MODEL = "ollama_chat/llama3.1:latest"


# Root agent that coordinates all specialists
root_agent = CustomLlmAgent(
    name="root_agent",
    model=LiteLlm(model=OLLAMA_MODEL),
    instruction=get_prompt("root_agent"),
    sub_agents=ANALYTICS_AGENTS,
    tools=[classify_intent],
)

app = App(
    root_agent=root_agent,
    name="app",
)