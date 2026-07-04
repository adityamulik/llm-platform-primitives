"""Integration tests for the demo edge app (main.py).

main.py proxies to the gateway over httpx; here httpx.AsyncClient is replaced
with a fake so we can drive the gateway's responses (and failures) deterministic-
ally without a running gateway.
"""

from __future__ import annotations

import httpx
import pytest
from fastapi.testclient import TestClient

import main


@pytest.fixture
def client():
    return TestClient(main.app)


class _FakeResponse:
    def __init__(self, status_code=200, json_body=None, text="", content=b"x"):
        self.status_code = status_code
        self._json = json_body if json_body is not None else {}
        self.text = text
        self.content = content

    def json(self):
        return self._json


class _FakeAsyncClient:
    """Routes POSTs by URL suffix to canned responses or raised errors."""

    routes: dict = {}

    def __init__(self, *args, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    async def post(self, url, **kwargs):
        for suffix, outcome in self.routes.items():
            if url.endswith(suffix):
                if isinstance(outcome, Exception):
                    raise outcome
                return outcome
        raise AssertionError(f"unexpected URL in test: {url}")


@pytest.fixture
def fake_httpx(monkeypatch):
    def _configure(routes):
        _FakeAsyncClient.routes = routes
        monkeypatch.setattr(main.httpx, "AsyncClient", _FakeAsyncClient)

    return _configure


# --- /login -----------------------------------------------------------------
def test_login_forwards_and_returns_token(client, fake_httpx):
    fake_httpx(
        {"/auth-token": _FakeResponse(200, {"token": "abc", "role": "analyst"})}
    )
    resp = client.post("/login", json={"username": "ana", "password": "analyst-pass"})
    assert resp.status_code == 200
    assert resp.json()["token"] == "abc"


def test_login_propagates_gateway_error(client, fake_httpx):
    fake_httpx(
        {
            "/auth-token": _FakeResponse(
                401, {"detail": "invalid credentials"}, content=b"x"
            )
        }
    )
    resp = client.post("/login", json={"username": "ana", "password": "bad"})
    assert resp.status_code == 401
    assert resp.json()["detail"] == "invalid credentials"


def test_login_gateway_unreachable_returns_503(client, fake_httpx):
    fake_httpx({"/auth-token": httpx.RequestError("connection refused")})
    resp = client.post("/login", json={"username": "ana", "password": "x"})
    assert resp.status_code == 503


# --- /run-agent -------------------------------------------------------------
def test_run_agent_missing_auth_header(client):
    resp = client.post("/run-agent", json={"prompt": "hi"})
    assert resp.status_code == 401


def test_run_agent_missing_prompt(client):
    resp = client.post(
        "/run-agent", headers={"Authorization": "Bearer t"}, json={}
    )
    assert resp.status_code == 400


def test_run_agent_success(client, fake_httpx):
    fake_httpx(
        {
            "/verify": _FakeResponse(200, {"valid": True}),
            "/agent/execute": _FakeResponse(
                200, {"session_id": "s1", "res": "answer"}
            ),
        }
    )
    resp = client.post(
        "/run-agent",
        headers={"Authorization": "Bearer t"},
        json={"prompt": "hello", "session_id": "s1"},
    )
    assert resp.status_code == 200
    assert resp.json()["res"] == "answer"


def test_run_agent_verify_rejected(client, fake_httpx):
    fake_httpx({"/verify": _FakeResponse(401, text="Invalid token")})
    resp = client.post(
        "/run-agent",
        headers={"Authorization": "Bearer bad"},
        json={"prompt": "hello"},
    )
    assert resp.status_code == 401


def test_run_agent_verify_unreachable(client, fake_httpx):
    fake_httpx({"/verify": httpx.RequestError("down")})
    resp = client.post(
        "/run-agent",
        headers={"Authorization": "Bearer t"},
        json={"prompt": "hello"},
    )
    assert resp.status_code == 503


def test_run_agent_execute_error_status(client, fake_httpx):
    fake_httpx(
        {
            "/verify": _FakeResponse(200, {"valid": True}),
            "/agent/execute": _FakeResponse(500, text="boom"),
        }
    )
    resp = client.post(
        "/run-agent",
        headers={"Authorization": "Bearer t"},
        json={"prompt": "hello"},
    )
    assert resp.status_code == 500


def test_run_agent_execute_unreachable(client, fake_httpx):
    fake_httpx(
        {
            "/verify": _FakeResponse(200, {"valid": True}),
            "/agent/execute": httpx.RequestError("down"),
        }
    )
    resp = client.post(
        "/run-agent",
        headers={"Authorization": "Bearer t"},
        json={"prompt": "hello"},
    )
    assert resp.status_code == 503
