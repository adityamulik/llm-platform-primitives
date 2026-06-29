#!/usr/bin/env python3

from __future__ import annotations


import uvicorn
import logging
import os
import sys
from pathlib import Path


import yaml
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from google.adk import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Allow running as a script (python gateway/gateway_server.py) by ensuring the
# repo root is importable so the `app` and `gateway` packages resolve.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import agent

from gateway.authz import (  # noqa: E402
    AuthError,
    decode_token,
    issue_token,
    token_from_header,
)
from gateway.engine import policy_engine
from gateway.models import (
    AgentExecuteRequest,
    LoginRequest,
    PromptRollbackRequest,
    TokenRequest,
)
from gateway.helper import _check_password, _claims_from_request, _require_admin, _prompt_state
from observability.metrics import metrics, set_current_user  # noqa: E402
from prompt_registry import (
    list_prompts,
    rollback_prompt,
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
# session_service = get_session_service()

# # Persistent ADK session service for the agent runner. Must outlive individual
# # requests so an existing session_id can be reused across calls.
adk_session_service = InMemorySessionService()


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


@app.get("/metrics")
async def get_metrics(user: str | None = None):
    """Per-user runtime metrics: tokens, cost, success/error counts, latency.

    Pass ``?user=<username>`` for one user, or omit for everyone.
    """
    return metrics.snapshot(user)


@app.get("/prompts")
async def get_prompts(request: Request):
    """List every prompt with its active version and full version history."""
    _require_admin(request)
    return {"prompts": [_prompt_state(name) for name in list_prompts()]}


@app.post("/prompts/{name}/rollback")
async def rollback_prompt_version(name: str, data: PromptRollbackRequest, request: Request):
    """Roll a prompt back to an earlier version (admin only).

    History is preserved; this only repoints which version the agents use on
    their next request. Returns the prompt's new active version.
    """
    claims = _require_admin(request)
    try:
        new_active = rollback_prompt(name, data.version)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    logger.info(
        "Prompt %r rolled back to %s by %s", name, new_active, claims.get("sub")
    )
    return _prompt_state(name)


@app.post("/auth-token")
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
    role = claims.get("role", "")
    logger.info("Agent execution request from %s (role=%s): %r", user_id, role, data.prompt[:100])

    # Thread the caller's token to the MCP servers so they can authorize tools,
    # and attribute this request's metrics (tokens/latency/errors) to the user.
    agent.set_request_auth(request.headers.get("Authorization"))
    set_current_user(user_id, role=role)

    # track_request times the body and records success/error + latency for the
    # user: a normal return counts as success, any raised HTTPException as error.
    with metrics.track_request(user_id):
        # Set up the session + runner. Sessions are namespaced by the
        # authenticated user_id, so a caller can only reuse their OWN session_id
        # — passing another user's session_id simply won't resolve. The caller's
        # role is stored in session state so before_tool_callback can enforce RBAC.
        try:
            session = None
            if data.session_id:
                session = await adk_session_service.get_session(
                    app_name="default",
                    user_id=user_id,
                    session_id=data.session_id,
                )
            if session is None:
                session = await adk_session_service.create_session(
                    app_name="default",
                    user_id=user_id,
                    state={"user_role": role},
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
                user_id=user_id,
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

    from observability.logging import setup_logging

    log_file = setup_logging("gateway")
    print(f"📝 Logging to {log_file}")
    port = int(os.getenv("AUTH_PORT", "7010"))
    host = os.getenv("AUTH_HOST", "0.0.0.0")
    print(f"🚀 Gateway Server starting on http://{host}:{port}")
    print(f"👤 users: {', '.join(USERS.keys())}")
    print(f"🛡️  roles: {', '.join(policy_engine.roles())}")
    uvicorn.run(app, host=host, port=port, log_level="info")
