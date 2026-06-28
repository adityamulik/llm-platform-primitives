
import hmac
from pathlib import Path

import yaml
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

from gateway.authz import (
    AuthError,
    decode_token,
    issue_token,
    token_from_header,
)
from app import agent

from google.adk import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

USERS = (yaml.safe_load(Path(__file__).parent.joinpath("gateway/users.yaml").read_text()) or {}).get(
    "users", {}
)

app = FastAPI()


class LoginRequest(BaseModel):
    username: str
    password: str


@app.post("/auth-token")
async def generate_auth_token(data: LoginRequest):
    """Validate credentials and issue a signed JWT carrying the user's role."""
    user = USERS.get(data.username)
    if not user or not hmac.compare_digest(str(user.get("password", "")), data.password):
        raise HTTPException(status_code=401, detail="invalid credentials")
    return issue_token(data.username, user["role"])


@app.post("/run-agent", status_code=201)
async def run_agent(request: Request):
    """Verify the bearer token and open a session for the caller."""
    try:
        claims = decode_token(token_from_header(request.headers.get("Authorization")))
    except AuthError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)

    role = claims.get("role")

    session_service = InMemorySessionService()

    req = await request.json()

    session = await session_service.create_session(
        app_name="default", user_id="default"
    )

    runner = Runner(
        agent=agent.root_agent,
        app_name='default',
        session_service=session_service,
    )

    final_response_text = ""
    content = types.Content(
        role='user', parts=[types.Part.from_text(text=req["prompt"])]
    )

    async for event in runner.run_async(
        user_id="default",
        session_id=session.id,
        new_message=content,
    ):
      if event.content.parts and event.content.parts[0].text:
        final_response_text = event.content.parts[0].text

    return final_response_text