"""Agents Configuration - Consolidated Registry.

This module imports and consolidates all agent categories.
Individual agents are defined in dedicated agent category files:
- analytics_agents.py
- dev_agents.py
- devops_agents.py
- content_agents.py
- research_agents.py
- ml_agents.py
- business_agents.py
- specialized_agents.py
"""

from .analytics_agents import ANALYTICS_AGENTS
from .dev_agents import DEV_AGENTS
from .devops_agents import DEVOPS_AGENTS
from .content_agents import CONTENT_AGENTS
from .research_agents import RESEARCH_AGENTS
from .ml_agents import ML_AGENTS
from .business_agents import BUSINESS_AGENTS
from .specialized_agents import SPECIALIZED_AGENTS


# ============================================================================
# COMPLETE AGENT REGISTRY
# ============================================================================

ALL_AGENTS = (
    ANALYTICS_AGENTS +
    DEV_AGENTS +
    DEVOPS_AGENTS +
    CONTENT_AGENTS +
    RESEARCH_AGENTS +
    ML_AGENTS +
    BUSINESS_AGENTS +
    SPECIALIZED_AGENTS
)

AGENTS_BY_CATEGORY = {
    "analytics": ANALYTICS_AGENTS,
    "development": DEV_AGENTS,
    "devops": DEVOPS_AGENTS,
    "content": CONTENT_AGENTS,
    "research": RESEARCH_AGENTS,
    "ml": ML_AGENTS,
    "business": BUSINESS_AGENTS,
    "orchestration": [SPECIALIZED_AGENTS[0]],
    "advisory": [SPECIALIZED_AGENTS[1], SPECIALIZED_AGENTS[2]],
    "operations": [SPECIALIZED_AGENTS[3]],
}

# Summary statistics
AGENT_COUNT = len(ALL_AGENTS)
CATEGORY_COUNT = len(AGENTS_BY_CATEGORY)
TOTAL_MCP_FUNCTION_SLOTS = sum(len(agent.agent_mcp_functions) for agent in ALL_AGENTS)

print(f"✓ Agents Loaded: {AGENT_COUNT} total agents")
print(f"✓ Categories: {CATEGORY_COUNT} categories")
print(f"✓ MCP Function Slots: {TOTAL_MCP_FUNCTION_SLOTS} total access points")
