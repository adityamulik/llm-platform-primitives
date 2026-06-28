"""Token + authorization helpers shared by the auth server and the MCP bridges.

Tokens are stateless JWTs that carry the authenticated user's ``role`` as a
claim. Any service that holds the shared secret can verify a token and learn the
caller's role without calling back to the auth server — the role is then fed to
the :class:`~mcp_auth.engine.PolicyEngine` to make an allow/deny decision.
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from functools import wraps
from typing import Any, Callable

import jwt

from .engine import policy_engine

# Shared signing secret. Override in every environment that issues OR verifies
# tokens. Defaulting to a dev value keeps local setup friction-free.
JWT_SECRET = os.getenv("MCP_AUTH_SECRET", "dev-insecure-secret-change-me-0123456789")
JWT_ALGORITHM = "HS256"
TOKEN_TTL_SECONDS = int(os.getenv("MCP_AUTH_TOKEN_TTL", "3600"))


class AuthError(Exception):
    """Raised when a token is missing, malformed, expired or invalid."""

    def __init__(self, message: str, status_code: int = 401) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def issue_token(username: str, role: str, ttl_seconds: int = TOKEN_TTL_SECONDS) -> dict[str, Any]:
    """Mint a signed token for an authenticated user and describe it."""
    now = datetime.now(timezone.utc)
    expires = now + timedelta(seconds=ttl_seconds)
    payload = {
        "sub": username,
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int(expires.timestamp()),
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return {
        "token": token,
        "token_type": "Bearer",
        "role": role,
        "username": username,
        "expires_in": ttl_seconds,
        "expires_at": expires.isoformat(),
    }


def decode_token(token: str) -> dict[str, Any]:
    """Verify a token's signature/expiry and return its claims."""
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError as exc:
        raise AuthError("Token has expired") from exc
    except jwt.InvalidTokenError as exc:
        raise AuthError("Invalid token") from exc


def token_from_header(authorization: str | None) -> str:
    """Pull the bearer token out of an ``Authorization`` header value."""
    if not authorization:
        raise AuthError("Missing Authorization header")
    parts = authorization.split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise AuthError("Authorization header must be 'Bearer <token>'")
    return parts[1].strip()


def authorize_claims(
    claims: dict[str, Any],
    *,
    tool: str | None = None,
    resource: str | None = None,
    operation: str | None = None,
) -> dict[str, Any]:
    """Run the policy engine for the role embedded in a verified token."""
    role = claims.get("role", "")
    decision = policy_engine.authorize(
        role, tool=tool, resource=resource, operation=operation
    )
    decision["username"] = claims.get("sub")
    return decision


def require_tool_access(tool_name: Callable[..., Any] | str | None = None):
    """Flask decorator: require a valid token whose role may use the tool.

    The protected tool name defaults to the Flask ``tool`` URL parameter, so it
    works for routes shaped like ``/tools/<tool>``. Pass an explicit string to
    pin a specific tool.

    On success the verified claims are attached to ``flask.g.claims``.
    """

    # Allow bare @require_tool_access usage as well as @require_tool_access("x").
    explicit_tool = None if callable(tool_name) else tool_name

    def decorator(view: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(view)
        def wrapper(*args: Any, **kwargs: Any):
            from flask import g, jsonify, request

            try:
                token = token_from_header(request.headers.get("Authorization"))
                claims = decode_token(token)
            except AuthError as exc:
                return jsonify({"error": exc.message}), exc.status_code

            tool = explicit_tool or kwargs.get("tool")
            if tool is not None:
                decision = authorize_claims(claims, tool=tool)
                if not decision["allowed"]:
                    return (
                        jsonify(
                            {
                                "error": "Forbidden",
                                "reason": f"role '{claims.get('role')}' may not use tool '{tool}'",
                                "decision": decision,
                            }
                        ),
                        403,
                    )

            g.claims = claims
            return view(*args, **kwargs)

        return wrapper

    # Support both @require_tool_access and @require_tool_access(...)
    if callable(tool_name):
        return decorator(tool_name)
    return decorator
