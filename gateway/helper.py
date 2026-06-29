import hmac
from typing import Optional
from fastapi import Request
from gateway.authz import (
    AuthError,
    decode_token,
    token_from_header,
)
from prompt_registry import (
    active_version,
    list_versions,
)

from fastapi import HTTPException

async def _check_password(stored: str, supplied: str) -> bool:
    # Constant-time compare. DEMO: plaintext store (see users.yaml).
    return hmac.compare_digest(str(stored), str(supplied))

async def _require_admin(request: Request) -> dict:
    """Decode the bearer token and require the admin role, else raise 401/403."""
    try:
        claims = decode_token(token_from_header(request.headers.get("Authorization")))
    except AuthError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)
    if claims.get("role") != "admin":
        raise HTTPException(status_code=403, detail="admin role required")
    return claims


async def _prompt_state(name: str) -> dict:
    return {"name": name, "active": active_version(name), "versions": list_versions(name)}

async def _claims_from_request(request: Request, body: Optional[dict] = None) -> dict:
    """Resolve token claims from a Bearer header or a JSON `token` field."""
    auth_header = request.headers.get("Authorization")
    if auth_header:
        return decode_token(token_from_header(auth_header))
    if body and body.get("token"):
        return decode_token(body.get("token"))
    raise AuthError("Provide a Bearer token or a 'token' field")