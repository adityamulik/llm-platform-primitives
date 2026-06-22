import logging
from google.adk.agents import LlmAgent
from token_counter import TokenCostCalculator

logger = logging.getLogger(__name__)

OLLAMA_MODEL = "ollama_chat/llama3.1:latest"


class CustomLlmAgent(LlmAgent):
    """
    Enhanced LlmAgent with agent metadata schema support.
    
    Accepts both Google ADK fields (name, model, instruction, tools, sub_agents)
    and agent metadata (id, description, category, specialization, mcp_functions, etc.)
    
    Note: 'name' must be a valid Python identifier (no spaces). Use 'id' or agent_id
    for display names with spaces.
    """
    
    def __init__(
        self,
        # Google ADK fields
        name: str = None,
        model = None,
        instruction: str = None,
        tools = None,
        sub_agents = None,
        # Agent metadata fields (from agents_config.py schema)
        id: str = None,
        description: str = None,
        category: str = None,
        specialization: str = None,
        mcp_functions: list = None,
        capabilities: list = None,
        input_types: list = None,
        output_types: list = None,
        max_conversation_turns: int = None,
        *args,
        **kwargs
    ):
        # If name not provided but id is, derive name from id
        if name is None and id is not None:
            name = id.replace("-", "_")  # Convert to valid identifier
        
        # Filter out metadata fields before passing to parent
        parent_kwargs = {
            "name": name,
            "model": model,
            "instruction": instruction,
        }
        if tools is not None:
            parent_kwargs["tools"] = tools
        if sub_agents is not None:
            parent_kwargs["sub_agents"] = sub_agents
        
        # Initialize parent LlmAgent
        super().__init__(*args, **parent_kwargs, **{k: v for k, v in kwargs.items() if k not in [
            "id", "description", "category", "specialization", "mcp_functions",
            "capabilities", "input_types", "output_types", "max_conversation_turns"
        ]})
        
        # Store agent metadata using object.__setattr__ to bypass Pydantic validation
        object.__setattr__(self, "_agent_id", id)
        object.__setattr__(self, "_agent_description", description)
        object.__setattr__(self, "_agent_category", category)
        object.__setattr__(self, "_agent_specialization", specialization)
        object.__setattr__(self, "_agent_mcp_functions", mcp_functions or [])
        object.__setattr__(self, "_agent_capabilities", capabilities or [])
        object.__setattr__(self, "_agent_input_types", input_types or [])
        object.__setattr__(self, "_agent_output_types", output_types or [])
        object.__setattr__(self, "_agent_max_conversation_turns", max_conversation_turns or 10)
        
        # Initialize token calculator
        self._token_calculator = TokenCostCalculator(OLLAMA_MODEL)
        # Bind callbacks properly
        self.before_model_callback = self._before_model_callback_impl
        self.after_model_callback = self._after_model_callback_impl
        self._last_input_text = ""  # Store input for use in after callback
    
    # Property accessors for agent metadata
    @property
    def agent_id(self):
        return getattr(self, "_agent_id", None)
    
    @property
    def agent_description(self):
        return getattr(self, "_agent_description", None)
    
    @property
    def agent_category(self):
        return getattr(self, "_agent_category", None)
    
    @property
    def agent_specialization(self):
        return getattr(self, "_agent_specialization", None)
    
    @property
    def agent_mcp_functions(self):
        return getattr(self, "_agent_mcp_functions", [])
    
    @property
    def agent_capabilities(self):
        return getattr(self, "_agent_capabilities", [])
    
    @property
    def agent_input_types(self):
        return getattr(self, "_agent_input_types", [])
    
    @property
    def agent_output_types(self):
        return getattr(self, "_agent_output_types", [])
    
    @property
    def agent_max_conversation_turns(self):
        return getattr(self, "_agent_max_conversation_turns", 10)

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
