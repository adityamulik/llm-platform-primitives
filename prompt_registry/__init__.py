"""Prompt Registry Module - Versioned in-memory store for agent instructions."""

from .registry import (
    PromptVersion,
    register_prompt,
    get_prompt,
    get_prompt_version,
    list_prompts,
    list_versions,
)
from .prompts import initialize_agent_prompts

__all__ = [
    "PromptVersion",
    "register_prompt",
    "get_prompt",
    "get_prompt_version",
    "list_prompts",
    "list_versions",
    "initialize_agent_prompts",
]

# Initialize prompts on import
initialize_agent_prompts()
