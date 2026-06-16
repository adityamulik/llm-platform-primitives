"""Prompt Registry - Versioned store for agent instructions.

Currently maintains prompts in-memory. Can be extended to support database versioning.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class PromptVersion:
    """Represents a versioned prompt."""
    version: str
    content: str
    created_at: datetime
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class PromptRegistry:
    """Manages versioned prompts. In-memory store, extensible for DB backends."""
    
    def __init__(self):
        """Initialize the registry."""
        self._prompts: Dict[str, Dict[str, PromptVersion]] = {}
        self._latest_versions: Dict[str, str] = {}
    
    def register_prompt(
        self,
        name: str,
        content: str,
        version: str = "1.0.0",
        tags: List[str] = None
    ) -> None:
        """Register or update a prompt version. Maintains version history."""
        if name not in self._prompts:
            self._prompts[name] = {}
        
        prompt_version = PromptVersion(
            version=version,
            content=content,
            created_at=datetime.now(),
            tags=tags or []
        )
        
        self._prompts[name][version] = prompt_version
        self._latest_versions[name] = version
    
    def get_prompt(
        self,
        name: str,
        version: Optional[str] = None
    ) -> str:
        """Get prompt content. Returns latest version if version not specified."""
        if name not in self._prompts:
            raise KeyError(f"Prompt '{name}' not found in registry")
        
        # Use latest version if not specified
        if version is None:
            version = self._latest_versions.get(name)
            if version is None:
                raise KeyError(f"No version found for prompt '{name}'")
        
        if version not in self._prompts[name]:
            raise KeyError(f"Version '{version}' not found for prompt '{name}'")
        
        return self._prompts[name][version].content
    
    def get_prompt_version(
        self,
        name: str,
        version: Optional[str] = None
    ) -> PromptVersion:
        """Get prompt with metadata (version, timestamp, tags)."""
        if name not in self._prompts:
            raise KeyError(f"Prompt '{name}' not found in registry")
        
        # Use latest version if not specified
        if version is None:
            version = self._latest_versions.get(name)
            if version is None:
                raise KeyError(f"No version found for prompt '{name}'")
        
        if version not in self._prompts[name]:
            raise KeyError(f"Version '{version}' not found for prompt '{name}'")
        
        return self._prompts[name][version]
    
    def list_prompts(self) -> List[str]:
        """List all registered prompt names."""
        return list(self._prompts.keys())
    
    def list_versions(self, name: str) -> List[str]:
        """List all versions of a prompt."""
        if name not in self._prompts:
            raise KeyError(f"Prompt '{name}' not found in registry")
        return list(self._prompts[name].keys())
    
    def get_latest_version(self, name: str) -> str:
        """Get the latest version number of a prompt."""
        if name not in self._prompts:
            raise KeyError(f"Prompt '{name}' not found in registry")
        return self._latest_versions[name]
    
    def delete_prompt(self, name: str) -> None:
        """Delete all versions of a prompt."""
        if name in self._prompts:
            del self._prompts[name]
            if name in self._latest_versions:
                del self._latest_versions[name]
    
    def delete_prompt_version(self, name: str, version: str) -> None:
        """Delete a specific version of a prompt."""
        if name not in self._prompts:
            raise KeyError(f"Prompt '{name}' not found in registry")
        
        if version not in self._prompts[name]:
            raise KeyError(f"Version '{version}' not found for prompt '{name}'")
        
        del self._prompts[name][version]
        
        # Update latest version if we deleted it
        if self._latest_versions.get(name) == version:
            remaining_versions = list(self._prompts[name].keys())
            if remaining_versions:
                self._latest_versions[name] = remaining_versions[-1]
            else:
                del self._prompts[name]
                del self._latest_versions[name]
    
    def __repr__(self) -> str:
        """String representation of the registry."""
        prompt_count = len(self._prompts)
        total_versions = sum(len(v) for v in self._prompts.values())
        return f"PromptRegistry(prompts={prompt_count}, versions={total_versions})"


# Global registry instance
_registry = PromptRegistry()


def register_prompt(
    name: str,
    content: str,
    version: str = "1.0.0",
    tags: List[str] = None
) -> None:
    """Register a prompt in the global registry."""
    _registry.register_prompt(name, content, version, tags)


def get_prompt(name: str, version: Optional[str] = None) -> str:
    """Get prompt content from the global registry."""
    return _registry.get_prompt(name, version)


def get_prompt_version(name: str, version: Optional[str] = None) -> PromptVersion:
    """Get prompt version metadata from the global registry."""
    return _registry.get_prompt_version(name, version)


def list_prompts() -> List[str]:
    """List all prompts in the global registry."""
    return _registry.list_prompts()


def list_versions(name: str) -> List[str]:
    """List all versions of a prompt."""
    return _registry.list_versions(name)


def get_registry() -> PromptRegistry:
    """Get the global registry instance."""
    return _registry
