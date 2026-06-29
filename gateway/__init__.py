"""MCP auth/authz package.

- ``engine``      RBAC policy engine driven by ``policies.yaml``.
- ``authz``       Token (JWT) issue/verify + policy authorization helpers.
- ``auth_server`` Standalone login/token service (run as a script).
"""

from .engine import PolicyEngine, policy_engine

__all__ = ["PolicyEngine", "policy_engine"]
