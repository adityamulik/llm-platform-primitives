"""Intent classifier for routing user requests to appropriate agents."""

import os
import yaml
from typing import Dict


# Load intent rules from YAML
def _load_intent_rules() -> Dict:
    """Load intent classification rules from YAML file."""
    config_path = os.path.join(os.path.dirname(__file__), "intent_rules.yml")
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Warning: Could not load intent rules from {config_path}: {e}")
        # Fallback to default rules
        return {
            "agents": {},
            "default_agent": "research_agent"
        }


INTENT_RULES = _load_intent_rules()


def classify_intent(user_input: str) -> str:
    """
    Classify user intent based on YAML rules and return the appropriate agent name.
    
    Args:
        user_input: The user's input message
        
    Returns:
        The name of the appropriate agent to handle the request
    """
    user_input_lower = user_input.lower()
    
    # Score each agent based on keyword matches
    agent_scores = {}
    agents_config = INTENT_RULES.get("agents", {})
    
    for agent_name, agent_rules in agents_config.items():
        keywords = agent_rules.get("keywords", [])
        weight = agent_rules.get("weight", 1.0)
        
        # Calculate score based on keyword matches
        score = sum(1 for keyword in keywords if keyword in user_input_lower) * weight
        agent_scores[agent_name] = score
    
    # Return the agent with the highest score, default to configured default agent
    if not agent_scores or all(v == 0 for v in agent_scores.values()):
        return INTENT_RULES.get("default_agent", "research_agent")
    
    best_agent = max(agent_scores, key=agent_scores.get)
    return best_agent if agent_scores[best_agent] > 0 else INTENT_RULES.get("default_agent", "research_agent")
