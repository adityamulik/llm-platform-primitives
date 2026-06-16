from google.adk.agents import Agent, LlmAgent
from google.adk.apps import App
from google.adk.models.lite_llm import LiteLlm
from intent_classifier import classify_intent


# Individual specialized agents
docs_agent = LlmAgent(
    name="docs_agent",
    model=LiteLlm(
        model="ollama_chat/llama3.1:latest",
    ),
    instruction="""You are a documentation specialist. Your role is to:
- Write clear, concise documentation
- Explain complex concepts in simple terms
- Create API documentation and guides
- Ensure documentation is well-structured and accessible""",
)

codebase_agent = LlmAgent(
    name="codebase_agent",
    model=LiteLlm(
        model="ollama_chat/llama3.1:latest",
    ),
    instruction="""You are a code analysis specialist. Your role is to:
- Analyze and understand codebases
- Explain code architecture and design patterns
- Identify potential improvements and refactoring opportunities
- Generate code snippets and examples
- Provide best practices for code organization""",
)

research_agent = LlmAgent(
    name="research_agent",
    model=LiteLlm(
        model="ollama_chat/llama3.1:latest",
    ),
    instruction="""You are a research specialist. Your role is to:
- Conduct in-depth research on technical topics
- Synthesize information from multiple sources
- Identify patterns and insights
- Provide well-reasoned analysis and recommendations
- Explore edge cases and potential issues""",
)

execution_agent = LlmAgent(
    name="execution_agent",
    model=LiteLlm(
        model="ollama_chat/llama3.1:latest",
    ),
    instruction="""You are an execution specialist. Your role is to:
- Translate ideas into actionable tasks
- Break down complex problems into steps
- Implement and execute solutions
- Monitor progress and adapt as needed
- Ensure deliverables meet quality standards""",
)

# Root agent that coordinates all specialists
root_agent = Agent(
    name="root_agent",
    model=LiteLlm(
        model="ollama_chat/llama3.1:latest",
    ),
    instruction="""You are an intelligent routing agent that coordinates with specialized agents:
- docs_agent: For documentation, guides, and tutorials
- codebase_agent: For code analysis, architecture, and implementation
- research_agent: For research, analysis, and best practices
- execution_agent: For building, implementing, and executing tasks

ROUTING INSTRUCTIONS:
1. Use the classify_intent tool to analyze the user's request and determine the appropriate agent
2. Based on the classification, delegate to the appropriate specialized agent
3. Provide a clear, helpful response leveraging the specialized agent's expertise

When routing:
- docs_agent: Documentation and explanation requests
- codebase_agent: Code analysis and implementation requests
- research_agent: Research, analysis, and evaluation requests
- execution_agent: Building, executing, and task implementation requests""",
    tools=[classify_intent],
)

app = App(
    root_agent=root_agent,
    name="app",
)