
import os

import httpx
from fastapi import FastAPI, HTTPException, Request
import uvicorn


from gateway.models import LoginRequest

# The auth gateway (gateway/server.py) is the only service that checks
# credentials and mints tokens. We forward credentials to it and verify the
# tokens it issues locally via the shared signing secret.
GATEWAY_URL = os.getenv("GATEWAY_URL", "http://localhost:7010")

app = FastAPI()


@app.post("/auth-token")
async def generate_auth_token(data: LoginRequest):
    """Forward credentials to the auth gateway and return the token it issues."""
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(
                f"{GATEWAY_URL}/login", json=data.model_dump()
            )
        except httpx.RequestError as exc:
            raise HTTPException(status_code=503, detail=f"auth gateway unreachable: {exc}")

    if resp.status_code != 200:
        detail = resp.json().get("detail", resp.text) if resp.content else "auth failed"
        raise HTTPException(status_code=resp.status_code, detail=detail)
    return resp.json()


@app.post("/run-agent", status_code=201)
async def run_agent(request: Request):
    """Verify the caller's token via the gateway, then run the agent through it."""
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    body = await request.json()
    if not body.get("prompt"):
        raise HTTPException(status_code=400, detail="Missing 'prompt' in request body")

    # The agent run can take much longer than httpx's 5s default, so give the
    # execute call a generous read timeout; otherwise we'd time out and never
    # see the gateway's real response/error.
    timeout = httpx.Timeout(connect=10.0, read=300.0, write=30.0, pool=10.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        # 1. Validate the token. The gateway reads it from the Authorization header.
        try:
            verify_resp = await client.post(
                f"{GATEWAY_URL}/verify",
                headers={"Authorization": auth_header},
                json={},
            )
        except httpx.RequestError as exc:
            raise HTTPException(status_code=503, detail=f"token validation failed: {exc}")
        if verify_resp.status_code != 200:
            raise HTTPException(status_code=verify_resp.status_code, detail=verify_resp.text)

        # 2. Execute the agent. /agent/execute requires session_id + prompt in the
        #    body and the token in the Authorization header.
        try:
            exec_resp = await client.post(
                f"{GATEWAY_URL}/agent/execute",
                headers={"Authorization": auth_header},
                json={
                    "session_id": body.get("session_id", "default"),
                    "prompt": body["prompt"],
                },  # both required by the gateway's AgentExecuteRequest model
            )
        except httpx.RequestError as exc:
            raise HTTPException(status_code=503, detail=f"Agent Response Failed: {exc}")
        if exec_resp.status_code not in (200, 201):
            raise HTTPException(status_code=exec_resp.status_code, detail=exec_resp.text)

    return exec_resp.json()


if __name__ == "__main__":
    # Specify your port number here (e.g., 7020)
    uvicorn.run(app, host="127.0.0.1", port=7020)