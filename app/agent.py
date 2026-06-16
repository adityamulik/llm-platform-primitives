from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models.lite_llm import LiteLlm


root_agent = Agent(
    name="root_agent",
    model=LiteLlm(
        model="ollama_chat/llama3.1:latest",
    ),
    instruction="You are a helpful AI assistant.",
)

app = App(
    root_agent=root_agent,
    name="app",
)