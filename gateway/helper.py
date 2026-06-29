import hmac
from typing import Optional
from fastapi import Request
from gateway.authz import (  # noqa: E402
    AuthError,
    authorize_claims,
    decode_token,
    issue_token,
    token_from_header,
)

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