"""Policy Engine.

Python port of engine.ts. Enforces RBAC (role-based access control) for MCP
tools, resources and operations. Unlike the TypeScript version — which hardcoded
the policy in the class — this engine loads the policy from ``policies.yaml`` so
the rules can be edited without touching code.

Default posture is *deny*: a role that is not present, or a tool/resource/
operation that is not explicitly granted, is rejected.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

# policies.yaml lives next to this file.
DEFAULT_POLICY_PATH = Path(__file__).resolve().parent / "policies.yaml"


class PolicyEngine:
    """Loads an RBAC policy and answers authorization questions about it."""

    def __init__(self, policy_path: str | Path = DEFAULT_POLICY_PATH) -> None:
        self.policy_path = Path(policy_path)
        self._roles: dict[str, dict[str, Any]] = {}
        self.reload()

    def reload(self) -> None:
        """(Re)read the policy file from disk."""
        with self.policy_path.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
        # policies.yaml nests everything under a top-level ``roles:`` key.
        self._roles = data.get("roles", {})

    # ------------------------------------------------------------------
    # Public API (mirrors engine.ts)
    # ------------------------------------------------------------------
    def roles(self) -> list[str]:
        """Return the list of known role names."""
        return list(self._roles.keys())

    def _permissions(self, role: str) -> dict[str, list[str]] | None:
        role_policy = self._roles.get(role)
        if not role_policy:
            return None
        return role_policy.get("permissions", {})

    def can_access_tool(self, role: str, tool: str) -> bool:
        perms = self._permissions(role)
        if perms is None:
            return False
        tools = perms.get("tools", [])
        return "*" in tools or tool in tools

    def can_access_resource(self, role: str, resource: str) -> bool:
        perms = self._permissions(role)
        if perms is None:
            return False
        for pattern in perms.get("resources", []):
            if pattern == "*" or self._match_pattern(resource, pattern):
                return True
        return False

    def can_perform_operation(self, role: str, operation: str) -> bool:
        perms = self._permissions(role)
        if perms is None:
            return False
        operations = perms.get("operations", [])
        return "*" in operations or operation in operations

    def get_authorized_tools(self, role: str) -> list[str]:
        """Get all tools authorized for a role.
        
        Args:
            role: Role name
            
        Returns:
            List of tool names the role can access, or empty list if role unknown
        """
        perms = self._permissions(role)
        if perms is None:
            return []
        tools = perms.get("tools", [])
        # If wildcard, return empty list (user has access to all tools)
        if "*" in tools:
            return ["*"]
        return tools

    def authorize(
        self,
        role: str,
        *,
        tool: str | None = None,
        resource: str | None = None,
        operation: str | None = None,
    ) -> dict[str, Any]:
        """Evaluate every supplied dimension at once.

        Only the dimensions that are provided are checked. ``allowed`` is True
        only when *all* provided dimensions pass.
        """
        checks: dict[str, bool] = {}
        if tool is not None:
            checks["tool"] = self.can_access_tool(role, tool)
        if resource is not None:
            checks["resource"] = self.can_access_resource(role, resource)
        if operation is not None:
            checks["operation"] = self.can_perform_operation(role, operation)

        known_role = role in self._roles
        allowed = known_role and bool(checks) and all(checks.values())
        denied = [dim for dim, ok in checks.items() if not ok]
        return {
            "allowed": allowed,
            "role": role,
            "known_role": known_role,
            "checks": checks,
            "denied": denied,
        }

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------
    @staticmethod
    def _match_pattern(resource: str, pattern: str) -> bool:
        """Glob-style match where ``*`` means "any characters".

        Mirrors the regex approach in engine.ts but escapes the rest of the
        pattern so URI characters (``:``, ``/``) are matched literally.
        """
        regex = "^" + re.escape(pattern).replace(r"\*", ".*") + "$"
        return re.match(regex, resource) is not None


# Module-level singleton, mirroring `export const policyEngine` in engine.ts.
policy_engine = PolicyEngine()
