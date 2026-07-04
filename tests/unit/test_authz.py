"""Unit tests for JWT issue/verify + authorization helpers (gateway/authz.py)."""

from __future__ import annotations

import time

import jwt
import pytest

from gateway import authz
from gateway.authz import (
    AuthError,
    authorize_claims,
    decode_token,
    issue_token,
    token_from_header,
)


def test_issue_token_roundtrip():
    info = issue_token("ana", "analyst")
    assert info["token_type"] == "Bearer"
    assert info["role"] == "analyst"
    assert info["username"] == "ana"
    assert info["expires_in"] == authz.TOKEN_TTL_SECONDS

    claims = decode_token(info["token"])
    assert claims["sub"] == "ana"
    assert claims["role"] == "analyst"
    assert claims["exp"] > claims["iat"]


def test_issue_token_custom_ttl_reflected_in_claims():
    info = issue_token("dev", "developer", ttl_seconds=10)
    assert info["expires_in"] == 10
    claims = decode_token(info["token"])
    assert claims["exp"] - claims["iat"] == 10


def test_decode_expired_token_raises_auth_error():
    expired = issue_token("dev", "developer", ttl_seconds=-1)["token"]
    with pytest.raises(AuthError) as exc:
        decode_token(expired)
    assert exc.value.status_code == 401
    assert "expired" in exc.value.message.lower()


def test_decode_token_wrong_secret_is_invalid():
    forged = jwt.encode({"sub": "x", "role": "admin"}, "not-the-secret", algorithm="HS256")
    with pytest.raises(AuthError) as exc:
        decode_token(forged)
    assert "invalid" in exc.value.message.lower()


def test_decode_garbage_token_is_invalid():
    with pytest.raises(AuthError):
        decode_token("not-a-jwt")


@pytest.mark.parametrize(
    "header,expected",
    [
        ("Bearer abc.def.ghi", "abc.def.ghi"),
        ("bearer   spaced-token  ", "spaced-token"),
    ],
)
def test_token_from_header_valid(header, expected):
    assert token_from_header(header) == expected


@pytest.mark.parametrize(
    "header",
    [None, "", "Token abc", "abc", "Bearer"],
)
def test_token_from_header_invalid(header):
    with pytest.raises(AuthError):
        token_from_header(header)


def test_authorize_claims_uses_role_and_adds_username():
    claims = {"sub": "ana", "role": "analyst"}
    decision = authorize_claims(claims, tool="read_file")
    assert decision["username"] == "ana"
    assert decision["role"] == "analyst"
    # analyst may read_file per shipped policies.yaml
    assert decision["allowed"] is True


def test_authorize_claims_denies_missing_role():
    decision = authorize_claims({"sub": "nobody"}, tool="read_file")
    assert decision["allowed"] is False


def test_auth_error_default_status_code():
    err = AuthError("boom")
    assert err.status_code == 401
    assert str(err) == "boom"
