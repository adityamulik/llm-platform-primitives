#!/usr/bin/env python3
"""Auth/AuthZ server.

Provides the login + token-issuance side of the MCP auth story:

  POST /login      {username, password}            -> issues a signed auth token
                                                       carrying the user's role
  POST /verify     {token} or Bearer header        -> validates a token, returns
                                                       its claims (who + role)
  POST /authorize  {tool?, resource?, operation?}  -> policy decision for the
                   + Bearer token                     caller's role (PEP/PDP)
  GET  /roles                                      -> roles known to policies.yaml
  
  POST /session    {token or Bearer header}        -> creates a session for the user,
                                                       returns session_id + authorized_tools
  GET  /agent/session/<session_id>                 -> get session context and execution history
  
  POST /agent/execute  {session_id, prompt}        -> execute agent with authorization,
                       + Bearer token                 returns result + tools_used
  
  GET  /health

Run standalone:  uv run python mcp_auth/auth_server.py
Configure with:  MCP_AUTH_SECRET, MCP_AUTH_TOKEN_TTL, AUTH_PORT, AUTH_HOST
"""

from __future__ import annotations

import asyncio
import hmac
import os
import sys
from pathlib import Path
from typing import Optional

import yaml
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Allow running as a script (python mcp_auth/auth_server.py) by ensuring the
# repo root is importable so the `mcp_auth` package resolves.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from gateway.authz import (  # noqa: E402
    AuthError,
    authorize_claims,
    decode_token,
    issue_token,
    token_from_header,
)
from gateway.engine import policy_engine  # noqa: E402
from gateway._delete_session_service import get_session_service  # noqa: E402
from gateway._delete_agent_runner import run_agent_with_auth  # noqa: E402

USERS_PATH = Path(__file__).resolve().parent / "users.yaml"

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models
class LoginRequest(BaseModel):
    username: str
    password: str


class TokenRequest(BaseModel):
    token: Optional[str] = None


class AuthorizeRequest(BaseModel):
    tool: Optional[str] = None
    resource: Optional[str] = None
    operation: Optional[str] = None


class SessionRequest(BaseModel):
    token: Optional[str] = None


class AgentExecuteRequest(BaseModel):
    session_id: str
    prompt: str
    token: Optional[str] = None


def _load_users() -> dict[str, dict[str, str]]:
    with USERS_PATH.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    return data.get("users", {})


USERS = _load_users()

# Get session service
session_service = get_session_service()


def _check_password(stored: str, supplied: str) -> bool:
    # Constant-time compare. DEMO: plaintext store (see users.yaml).
    return hmac.compare_digest(str(stored), str(supplied))


async def _claims_from_request(request: Request, body: Optional[dict] = None) -> dict:
    """Resolve token claims from a Bearer header or a JSON `token` field."""
    auth_header = request.headers.get("Authorization")
    if auth_header:
        return decode_token(token_from_header(auth_header))
    if body and body.get("token"):
        return decode_token(body.get("token"))
    raise AuthError("Provide a Bearer token or a 'token' field")


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "MCP Auth Server",
        "users": len(USERS),
        "roles": policy_engine.roles(),
    }


@app.get("/roles")
async def roles():
    return {"roles": policy_engine.roles()}


@app.post("/login")
async def login(data: LoginRequest):
    username = data.username
    password = data.password

    user = USERS.get(username)
    if not user or not _check_password(user.get("password", ""), password):
        # Same response for unknown user and bad password (no enumeration).
        raise HTTPException(status_code=401, detail="invalid credentials")

    role = user["role"]
    if role not in policy_engine.roles():
        raise HTTPException(
            status_code=500, detail=f"user role '{role}' is not defined in policies.yaml"
        )

    token_info = issue_token(username, role)
    print(f"🔑 issued token for '{username}' (role={role})")
    return token_info


@app.post("/verify")
async def verify(request: Request, data: TokenRequest):
    try:
        token = data.token or None
        body_dict = {"token": token} if token else {}
        claims = await _claims_from_request(request, body_dict)
    except AuthError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)
    
    return {
        "valid": True,
        "username": claims.get("sub"),
        "role": claims.get("role"),
        "expires_at": claims.get("exp"),
    }


@app.post("/authorize")
async def authorize(request: Request, data: AuthorizeRequest):
    try:
        body_dict = {}
        claims = await _claims_from_request(request, body_dict)
    except AuthError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)

    decision = authorize_claims(
        claims,
        tool=data.tool,
        resource=data.resource,
        operation=data.operation,
    )
    if not decision["allowed"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return decision


@app.post("/session", status_code=201)
async def create_session(request: Request, data: SessionRequest):
    """Create a new session for an authenticated user.
    
    Request body:
        {
            "token": "jwt-token" | Authorization header
        }
    
    Returns:
        {
            "session_id": "uuid",
            "user_id": "username",
            "role": "user_role",
            "authorized_tools": ["tool1", "tool2", ...],
            "created_at": "iso-timestamp",
            "expires_at": "iso-timestamp"
        }
    """
    try:
        body_dict = {"token": data.token} if data.token else {}
        claims = await _claims_from_request(request, body_dict)
    except AuthError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)
    
    user_id = claims.get("sub")
    role = claims.get("role")
    
    # Get all tools authorized for this role
    all_tools = policy_engine.get_authorized_tools(role)
    
    # Create session
    session = await session_service.create_session(
        user_id=user_id,
        role=role,
        authorized_tools=all_tools,
    )
    
    return {
        "session_id": session.session_id,
        "user_id": session.user_id,
        "role": session.role,
        "authorized_tools": session.mcp_tools,
        "created_at": session.created_at.isoformat(),
        "expires_at": session.expires_at.isoformat(),
    }


@app.get("/agent/session/{session_id}")
async def get_session_info(session_id: str):
    """Get session context and execution history.
    
    Args:
        session_id: Session ID from URL path
        
    Returns:
        {
            "session_id": "uuid",
            "user_id": "username",
            "role": "user_role",
            "authorized_tools": [...],
            "execution_count": N,
            "execution_history": [...]
        }
    """
    session = await session_service.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or expired")
    
    return {
        "session_id": session.session_id,
        "user_id": session.user_id,
        "role": session.role,
        "authorized_tools": session.mcp_tools,
        "execution_count": len(session.execution_history),
        "execution_history": session.execution_history,
    }


@app.post("/agent/execute")
async def execute_agent(request: Request, data: AgentExecuteRequest):
    """Execute the agent with authorization checks and session tracking.
    
    Request body:
        {
            "session_id": "uuid",          # From POST /session
            "prompt": "user question",     # The agent prompt
            "token": "jwt-token"           # OR use Authorization header
        }
    
    Returns:
        {
            "status": "success" | "error",
            "session_id": "uuid",
            "user_id": "username",
            "result": {...},               # Agent execution result
            "tools_used": [...],           # Tools that were called
            "error": "..."                 # If status is error
        }
    """
    try:
        body_dict = {"token": data.token} if data.token else {}
        claims = await _claims_from_request(request, body_dict)
    except AuthError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)
    
    session_id = data.session_id
    prompt = data.prompt
    user_id = claims.get("sub")
    role = claims.get("role")
    
    # Get authorized tools for this user
    authorized_tools = policy_engine.get_authorized_tools(role)
    
    print(f"🔐 Agent execution request from {user_id} (role={role})")
    print(f"   Session: {session_id}")
    print(f"   Prompt: {prompt[:100]}...")
    print(f"   Authorized tools: {authorized_tools}")
    
    # Mock agent execution
    # Replace with real agent when available
    mock_result = {
        "status": "success",
        "response": f"Mock agent processed: {prompt[:50]}...",
        "tools_used": authorized_tools[:1] if authorized_tools else [],
    }
    
    # Record in session
    await session_service.record_execution(
        session_id=session_id,
        prompt=prompt,
        result=mock_result,
        tools_used=mock_result.get("tools_used", []),
    )
    
    return {
        "status": "success",
        "session_id": session_id,
        "user_id": user_id,
        "result": mock_result,
        "tools_used": mock_result.get("tools_used", []),
    }


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("AUTH_PORT", "8000"))
    host = os.getenv("AUTH_HOST", "0.0.0.0")
    print(f"🚀 Gateway Server starting on http://{host}:{port}")
    print(f"👤 users: {', '.join(USERS.keys())}")
    print(f"🛡️  roles: {', '.join(policy_engine.roles())}")
    uvicorn.run(app, host=host, port=port, log_level="info")
