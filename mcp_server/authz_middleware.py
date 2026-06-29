"""FastMCP middleware that enforces RBAC on tool calls.

Each MCP server is an independent resource server: it must not trust the caller.
This middleware reads the caller's JWT from the ``Authorization`` header,
resolves the role, and checks it against ``policies.yaml`` via the shared policy
engine. Unauthorized calls are rejected (as a tool error) before the tool runs.

Requires the same signing secret as the gateway (``MCP_AUTH_SECRET``) so the
token issued by the gateway can be verified here.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

# Run-as-script support: ensure the repo root is importable so `gateway` resolves.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastmcp.exceptions import ToolError  # noqa: E402
from fastmcp.server.dependencies import get_http_headers  # noqa: E402
from fastmcp.server.middleware import Middleware, MiddlewareContext  # noqa: E402

from gateway.authz import AuthError, decode_token, token_from_header  # noqa: E402
from gateway.engine import policy_engine  # noqa: E402

logger = logging.getLogger(__name__)


class AuthzMiddleware(Middleware):
    """Deny tool calls whose caller role isn't permitted by the policy."""

    async def on_call_tool(self, context: MiddlewareContext, call_next):
        tool_name = context.message.name
        # get_http_headers() strips "authorization" by default; opt back in.
        auth_header = get_http_headers(include={"authorization"}).get("authorization")

        try:
            claims = decode_token(token_from_header(auth_header))
        except AuthError as exc:
            logger.warning("MCP authz REJECT tool=%r: %s", tool_name, exc)
            raise ToolError(f"Unauthorized: {exc}")

        role = claims.get("role", "")
        if not policy_engine.can_access_tool(role, tool_name):
            logger.warning("MCP authz DENY role=%r tool=%r", role, tool_name)
            raise ToolError(
                f"Forbidden: role '{role}' is not authorized to use tool '{tool_name}'"
            )

        logger.info("MCP authz OK role=%r tool=%r", role, tool_name)
        return await call_next(context)
