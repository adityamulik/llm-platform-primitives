"""Unit tests for the versioned prompt registry (prompt_registry)."""

from __future__ import annotations

import pytest

from prompt_registry import (
    active_version,
    get_prompt,
    get_prompt_version,
    list_prompts,
    list_versions,
    rollback_prompt,
)
from prompt_registry.prompts import initialize_agent_prompts
from prompt_registry.registry import PromptRegistry, PromptVersion


# --- PromptRegistry class (isolated instance) -------------------------------
def test_register_and_get_latest():
    reg = PromptRegistry()
    reg.register_prompt("p", "v1 content", version="1.0.0")
    reg.register_prompt("p", "v2 content", version="2.0.0")
    assert reg.get_prompt("p") == "v2 content"  # latest
    assert reg.get_prompt("p", "1.0.0") == "v1 content"


def test_get_unknown_prompt_raises():
    reg = PromptRegistry()
    with pytest.raises(KeyError):
        reg.get_prompt("missing")


def test_get_unknown_version_raises():
    reg = PromptRegistry()
    reg.register_prompt("p", "c")
    with pytest.raises(KeyError):
        reg.get_prompt("p", "9.9.9")


def test_get_prompt_version_metadata():
    reg = PromptRegistry()
    reg.register_prompt("p", "c", version="1.2.3", tags=["a", "b"])
    pv = reg.get_prompt_version("p")
    assert isinstance(pv, PromptVersion)
    assert pv.version == "1.2.3"
    assert pv.tags == ["a", "b"]


def test_get_prompt_version_unknown_prompt_and_version():
    reg = PromptRegistry()
    with pytest.raises(KeyError):
        reg.get_prompt_version("missing")
    reg.register_prompt("p", "c")
    with pytest.raises(KeyError):
        reg.get_prompt_version("p", "nope")


def test_rollback_repoints_active_version():
    reg = PromptRegistry()
    reg.register_prompt("p", "old", version="1.0.0")
    reg.register_prompt("p", "new", version="2.0.0")
    assert reg.active_version("p") == "2.0.0"
    assert reg.rollback("p", "1.0.0") == "1.0.0"
    assert reg.active_version("p") == "1.0.0"
    assert reg.get_prompt("p") == "old"
    # History preserved: 2.0.0 still retrievable.
    assert reg.get_prompt("p", "2.0.0") == "new"


def test_rollback_unknown_prompt_or_version():
    reg = PromptRegistry()
    with pytest.raises(KeyError):
        reg.rollback("missing", "1.0.0")
    reg.register_prompt("p", "c")
    with pytest.raises(KeyError):
        reg.rollback("p", "9.9.9")


def test_active_version_unknown_prompt():
    reg = PromptRegistry()
    with pytest.raises(KeyError):
        reg.active_version("missing")


def test_list_prompts_and_versions():
    reg = PromptRegistry()
    reg.register_prompt("a", "c1", version="1.0.0")
    reg.register_prompt("a", "c2", version="1.1.0")
    reg.register_prompt("b", "c3")
    assert set(reg.list_prompts()) == {"a", "b"}
    assert set(reg.list_versions("a")) == {"1.0.0", "1.1.0"}


def test_list_versions_unknown_prompt():
    reg = PromptRegistry()
    with pytest.raises(KeyError):
        reg.list_versions("missing")


def test_repr_counts_prompts_and_versions():
    reg = PromptRegistry()
    reg.register_prompt("a", "c1", version="1.0.0")
    reg.register_prompt("a", "c2", version="2.0.0")
    reg.register_prompt("b", "c3")
    assert reg.__repr__() == "PromptRegistry(prompts=2, versions=3)"


def test_prompt_version_defaults_tags_to_empty_list():
    pv = PromptVersion(version="1.0.0", content="c", created_at=None)
    assert pv.tags == []


# --- module-level global registry (seeded on import) ------------------------
def test_global_registry_seeded_with_agent_prompts():
    names = list_prompts()
    for expected in [
        "docs_agent",
        "codebase_agent",
        "research_agent",
        "execution_agent",
        "root_agent",
    ]:
        assert expected in names


def test_docs_agent_active_is_v2():
    assert active_version("docs_agent") == "2.0.0"
    assert set(list_versions("docs_agent")) >= {"1.0.0", "2.0.0"}
    assert "documentation lookup specialist" in get_prompt("docs_agent")


def test_global_rollback_then_restore():
    assert rollback_prompt("docs_agent", "1.0.0") == "1.0.0"
    assert active_version("docs_agent") == "1.0.0"
    pv = get_prompt_version("docs_agent")
    assert pv.version == "1.0.0"


def test_initialize_agent_prompts_is_idempotent_enough():
    # Re-seeding does not raise and keeps the active docs version at 2.0.0.
    initialize_agent_prompts()
    assert active_version("docs_agent") == "2.0.0"
