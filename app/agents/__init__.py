"""Agents Package - Unified Agent Access.

Import all agents from this package:
    from app.agents import ALL_AGENTS, AGENTS_BY_CATEGORY
    from app.agents import ANALYTICS_AGENTS, DEV_AGENTS, etc.
"""

from .analytics_agents import ANALYTICS_AGENTS
from .dev_agents import DEV_AGENTS
from .devops_agents import DEVOPS_AGENTS
from .content_agents import CONTENT_AGENTS
from .research_agents import RESEARCH_AGENTS
from .ml_agents import ML_AGENTS
from .business_agents import BUSINESS_AGENTS
from .specialized_agents import SPECIALIZED_AGENTS
from .agents_config import (
    ALL_AGENTS,
    AGENTS_BY_CATEGORY,
    AGENT_COUNT,
    CATEGORY_COUNT,
    TOTAL_MCP_FUNCTION_SLOTS,
)

__all__ = [
    # "ALL_AGENTS",
    # "AGENTS_BY_CATEGORY",
    # "AGENT_COUNT",
    # "CATEGORY_COUNT",
    # "TOTAL_MCP_FUNCTION_SLOTS",
    "ANALYTICS_AGENTS",
    # "DEV_AGENTS",
    # "DEVOPS_AGENTS",
    # "CONTENT_AGENTS",
    # "RESEARCH_AGENTS",
    # "ML_AGENTS",
    # "BUSINESS_AGENTS",
    # "SPECIALIZED_AGENTS",
]
