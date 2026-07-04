"""Shared pytest fixtures and path setup.

The ``mcp_server`` team servers import their siblings as top-level modules
(``import authz_middleware`` / ``from server_common import serve``) because they
are launched as scripts (``python mcp_server/server_team_a.py``). Put that
directory on ``sys.path`` so the same imports resolve under pytest.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
MCP_SERVER_DIR = REPO_ROOT / "mcp_server"

for _p in (REPO_ROOT, MCP_SERVER_DIR):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(autouse=True)
def _reset_prompt_registry():
    """Restore the global prompt registry to its seeded state after each test.

    Tests that register/rollback prompts mutate a process-wide singleton; reset
    it so ordering never changes results.
    """
    from prompt_registry import registry as _registry_mod

    yield
    _registry_mod._registry = _registry_mod.PromptRegistry()
    from prompt_registry.prompts import initialize_agent_prompts

    initialize_agent_prompts()
