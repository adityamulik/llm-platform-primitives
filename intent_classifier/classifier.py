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


def classify_intent(user_input: str) -> Dict:
    """
    Classify user intent based on YAML keyword rules.

    Args:
        user_input: The user's input message

    Returns:
        A structured decision the calling agent can act on:

        - When a rule matches:
            {"status": "classified", "agent": <name>, "score": <float>}

        - When no rule matches, the request is left *unclassified* rather than
          defaulting to a fixed agent. The caller (LLM) is told to decide for
          itself or ask the user whether a web search should be performed to
          ground the response:
            {"status": "unclassified", "agent": None, "reason": ...,
             "available_agents": [...], "next_action": "ask_user_about_web_search",
             "message": ...}
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

    # No confident match: do NOT default to a specific intent. Hand control
    # back so the LLM can answer directly or ask the user about grounding via
    # web search.
    if not agent_scores or all(score == 0 for score in agent_scores.values()):
        return {
            "status": "unclassified",
            "agent": None,
            "reason": "No intent rule matched the request.",
            "available_agents": list(agents_config.keys()),
            "next_action": "ask_user_about_web_search",
            "message": (
                "I couldn't confidently match this request to a specialist agent. "
                "Should I perform a web search to ground the response, or answer "
                "directly from existing knowledge?"
            ),
        }

    best_agent = max(agent_scores, key=agent_scores.get)
    
    return {
        "status": "classified",
        "agent": best_agent,
        "score": agent_scores[best_agent],
    }
