"""Integration tests for the auth gateway (gateway/gateway_server.py).

Uses FastAPI's TestClient. The one place that would otherwise require a live
model — ``/agent/execute`` — has the ADK ``Runner`` replaced with a fake that
yields a canned event, so the endpoint's auth/session/metrics wiring is tested
without invoking Ollama.
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from gateway import gateway_server
from gateway.authz import issue_token


@pytest.fixture
def client():
    return TestClient(gateway_server.app)


def _bearer(username: str, role: str) -> dict:
    return {"Authorization": f"Bearer {issue_token(username, role)['token']}"}


# --- health / roles / metrics ----------------------------------------------
def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert "admin" in body["roles"]
    assert body["users"] >= 1


def test_roles(client):
    resp = client.get("/roles")
    assert resp.status_code == 200
    assert "viewer" in resp.json()["roles"]


def test_metrics_all_and_filtered(client):
    gateway_server.metrics.record_tokens(
        "metrics-user", input_tokens=5, output_tokens=3
    )
    all_users = client.get("/metrics").json()
    assert "metrics-user" in all_users
    one = client.get("/metrics", params={"user": "metrics-user"}).json()
    assert one["input_tokens"] == 5


# --- login ------------------------------------------------------------------
def test_login_success(client):
    resp = client.post(
        "/auth-token", json={"username": "ana", "password": "analyst-pass"}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["role"] == "analyst"
    assert body["token_type"] == "Bearer"


def test_login_bad_password(client):
    resp = client.post(
        "/auth-token", json={"username": "ana", "password": "wrong"}
    )
    assert resp.status_code == 401


def test_login_unknown_user(client):
    resp = client.post(
        "/auth-token", json={"username": "ghost", "password": "x"}
    )
    assert resp.status_code == 401


def test_login_role_not_in_policy(client, monkeypatch):
    monkeypatch.setitem(
        gateway_server.USERS, "weirdo", {"password": "pw", "role": "nonexistent-role"}
    )
    resp = client.post(
        "/auth-token", json={"username": "weirdo", "password": "pw"}
    )
    assert resp.status_code == 500


# --- verify -----------------------------------------------------------------
def test_verify_with_header(client):
    resp = client.post("/verify", headers=_bearer("dev", "developer"), json={})
    assert resp.status_code == 200
    body = resp.json()
    assert body["valid"] is True
    assert body["username"] == "dev"
    assert body["role"] == "developer"


def test_verify_with_body_token(client):
    token = issue_token("ana", "analyst")["token"]
    resp = client.post("/verify", json={"token": token})
    assert resp.status_code == 200
    assert resp.json()["username"] == "ana"


def test_verify_missing_token(client):
    resp = client.post("/verify", json={})
    assert resp.status_code == 401


def test_verify_invalid_token(client):
    resp = client.post(
        "/verify", headers={"Authorization": "Bearer garbage"}, json={}
    )
    assert resp.status_code == 401


# --- prompts (admin only) ---------------------------------------------------
def test_prompts_requires_admin(client):
    resp = client.get("/prompts", headers=_bearer("ana", "analyst"))
    assert resp.status_code == 403


def test_prompts_list_as_admin(client):
    resp = client.get("/prompts", headers=_bearer("root", "admin"))
    assert resp.status_code == 200
    names = [p["name"] for p in resp.json()["prompts"]]
    assert "docs_agent" in names


def test_prompt_rollback_as_admin(client):
    resp = client.post(
        "/prompts/docs_agent/rollback",
        headers=_bearer("root", "admin"),
        json={"version": "1.0.0"},
    )
    assert resp.status_code == 200
    assert resp.json()["active"] == "1.0.0"


def test_prompt_rollback_unknown_version_404(client):
    resp = client.post(
        "/prompts/docs_agent/rollback",
        headers=_bearer("root", "admin"),
        json={"version": "9.9.9"},
    )
    assert resp.status_code == 404


# --- agent execute (Runner faked) ------------------------------------------
class _FakeEvent:
    def __init__(self, text: str):
        self.content = SimpleNamespace(
            parts=[SimpleNamespace(text=text)]
        )


class _FakeRunner:
    def __init__(self, *args, **kwargs):
        pass

    async def run_async(self, *, user_id, session_id, new_message):
        yield _FakeEvent("final agent answer")


def test_agent_execute_requires_auth(client):
    resp = client.post(
        "/agent/execute", json={"session_id": "", "prompt": "hi"}
    )
    assert resp.status_code == 401


def test_agent_execute_success(client, monkeypatch):
    monkeypatch.setattr(gateway_server, "Runner", _FakeRunner)
    resp = client.post(
        "/agent/execute",
        headers=_bearer("ana", "analyst"),
        json={"session_id": "", "prompt": "hello"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["res"] == "final agent answer"
    assert body["session_id"]
    # request should be counted as a success for the user
    snap = gateway_server.metrics.snapshot("ana")
    assert snap["requests"] >= 1


def test_agent_execute_runner_failure_is_500(client, monkeypatch):
    class _BoomRunner(_FakeRunner):
        async def run_async(self, *, user_id, session_id, new_message):
            raise RuntimeError("model exploded")
            yield  # pragma: no cover

    monkeypatch.setattr(gateway_server, "Runner", _BoomRunner)
    resp = client.post(
        "/agent/execute",
        headers=_bearer("dev", "developer"),
        json={"session_id": "", "prompt": "hello"},
    )
    assert resp.status_code == 500
    assert "agent run failed" in resp.json()["detail"]
