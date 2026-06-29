#!/usr/bin/env python3

from __future__ import annotations

import hmac
import uvicorn
import logging
import os
import sys
from pathlib import Path
from typing import Optional

import yaml
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from google.adk import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from app import agent

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
from gateway.models import (  # noqa: E402
    AgentExecuteRequest,
    AuthorizeRequest,
    LoginRequest,
    SessionRequest,
    TokenRequest,
)

logger = logging.getLogger(__name__)

USERS_PATH = Path(__file__).resolve().parent / "users.yaml"

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _load_users() -> dict[str, dict[str, str]]:
    with USERS_PATH.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    return data.get("users", {})


USERS = _load_users()

# Get session service
session_service = get_session_service()

# Persistent ADK session service for the agent runner. Must outlive individual
# requests so an existing session_id can be reused across calls.
adk_session_service = InMemorySessionService()


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
        claims = decode_token(token_from_header(request.headers.get("Authorization")))
    except AuthError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)

    user_id = claims.get("sub", "default")
    logger.info("Agent execution request from %s: %r", user_id, data.prompt[:100])

    # Set up the session + runner. Reuse the session if a valid id is given,
    # otherwise create a new one.
    try:
        session = None
        if data.session_id:
            session = await adk_session_service.get_session(
                app_name="default",
                user_id="default",
                session_id=data.session_id,
            )
        if session is None:
            session = await adk_session_service.create_session(
                app_name="default", user_id="default"
            )

        runner = Runner(
            agent=agent.root_agent,
            app_name="default",
            session_service=adk_session_service,
        )
    except Exception as exc:
        logger.exception("Failed to set up agent session/runner")
        raise HTTPException(
            status_code=500, detail=f"agent setup failed: {type(exc).__name__}: {exc}"
        )

    # Run the agent and collect the final text.
    final_response_text = ""
    try:        
        content = types.Content(
            role="user", parts=[types.Part.from_text(text=data.prompt)]
        )
        async for event in runner.run_async(
            user_id="default",
            session_id=session.id,
            new_message=content,
        ):
            if event.content.parts and event.content.parts[0].text:
                final_response_text = event.content.parts[0].text
        return {"session_id": session.id, "res": final_response_text}
    
    except Exception as exc:
        logger.exception("Agent run failed")
        raise HTTPException(
            status_code=500, detail=f"agent run failed: {type(exc).__name__}: {exc}"
        )


if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    port = int(os.getenv("AUTH_PORT", "7010"))
    host = os.getenv("AUTH_HOST", "0.0.0.0")
    print(f"🚀 Gateway Server starting on http://{host}:{port}")
    print(f"👤 users: {', '.join(USERS.keys())}")
    print(f"🛡️  roles: {', '.join(policy_engine.roles())}")
    uvicorn.run(app, host=host, port=port, log_level="info")
