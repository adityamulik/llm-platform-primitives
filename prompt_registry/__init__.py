"""Prompt Registry Module - Versioned in-memory store for agent instructions."""

from .registry import (
    PromptRegistry,
    PromptVersion,
    register_prompt,
    get_prompt,
    get_prompt_version,
    list_prompts,
    list_versions,
    get_registry,
)
from .prompts import initialize_agent_prompts

__all__ = [
    "PromptRegistry",
    "PromptVersion",
    "register_prompt",
    "get_prompt",
    "get_prompt_version",
    "list_prompts",
    "list_versions",
    "get_registry",
    "initialize_agent_prompts",
]

# Initialize prompts on import
initialize_agent_prompts()
