"""Unit tests for gateway request helpers (gateway/helper.py)."""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from gateway.authz import AuthError, issue_token
from gateway.helper import (
    _check_password,
    _claims_from_request,
    _prompt_state,
    _require_admin,
)


def _request(headers: dict | None = None):
    """Minimal stand-in for a Starlette Request (only .headers.get is used)."""
    return SimpleNamespace(headers=headers or {})


async def test_check_password_matches():
    assert await _check_password("secret", "secret") is True


async def test_check_password_rejects_mismatch():
    assert await _check_password("secret", "wrong") is False


async def test_require_admin_accepts_admin_token():
    token = issue_token("root", "admin")["token"]
    claims = await _require_admin(_request({"Authorization": f"Bearer {token}"}))
    assert claims["role"] == "admin"
    assert claims["sub"] == "root"


async def test_require_admin_rejects_non_admin():
    token = issue_token("ana", "analyst")["token"]
    with pytest.raises(HTTPException) as exc:
        await _require_admin(_request({"Authorization": f"Bearer {token}"}))
    assert exc.value.status_code == 403


async def test_require_admin_rejects_missing_token():
    with pytest.raises(HTTPException) as exc:
        await _require_admin(_request({}))
    assert exc.value.status_code == 401


async def test_prompt_state_shape():
    state = await _prompt_state("docs_agent")
    assert state["name"] == "docs_agent"
    assert state["active"] == "2.0.0"  # v2.0.0 seeded last => active
    assert "1.0.0" in state["versions"]
    assert "2.0.0" in state["versions"]


async def test_claims_from_request_via_header():
    token = issue_token("dev", "developer")["token"]
    claims = await _claims_from_request(_request({"Authorization": f"Bearer {token}"}))
    assert claims["sub"] == "dev"


async def test_claims_from_request_via_body_token():
    token = issue_token("dev", "developer")["token"]
    claims = await _claims_from_request(_request({}), {"token": token})
    assert claims["role"] == "developer"


async def test_claims_from_request_without_any_token():
    with pytest.raises(AuthError):
        await _claims_from_request(_request({}), None)
