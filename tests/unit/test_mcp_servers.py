"""Unit tests for the MCP team servers + RBAC middleware (mcp_server/)."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

import authz_middleware
import server_team_a
import server_team_b
import server_team_c
from authz_middleware import AuthzMiddleware
from fastmcp.exceptions import ToolError
from gateway.authz import issue_token


# --- tool implementations (pure functions) ----------------------------------
def test_generate_report_shape():
    result = server_team_a.generate_report("sales", format="csv")
    assert result["status"] == "generated"
    assert result["report_type"] == "sales"
    assert result["format"] == "csv"
    assert result["team"] == "A"
    assert "timestamp" in result


def test_deploy_application_shape():
    result = server_team_b.deploy_application("billing", "2.3", environment="production")
    assert result["status"] == "deployed"
    assert result["environment"] == "production"
    assert "billing-production.company.com" in result["url"]
    assert result["team"] == "B"


def test_restart_and_update_configuration():
    restarted = server_team_b.restart_service("api")
    assert restarted["status"] == "restarted"
    updated = server_team_b.update_configuration("api", "timeout", "30")
    assert updated["config"] == {"timeout": "30"}


def test_read_file_shape():
    result = server_team_c.read_file("/etc/hosts")
    assert result["status"] == "success"
    assert result["path"] == "/etc/hosts"
    assert result["team"] == "C"


def test_query_database_select_and_delete():
    select = server_team_c.query_database("SELECT * FROM t")
    assert select["rows"] == 42
    delete_users = server_team_c.query_database("DELETE FROM users")
    assert delete_users["affected_rows"] == 10234
    delete_other = server_team_c.query_database("DELETE FROM sessions")
    assert delete_other["affected_rows"] == 5


# --- AuthzMiddleware --------------------------------------------------------
class _FakeContext:
    def __init__(self, tool_name: str):
        self.message = SimpleNamespace(name=tool_name)


async def _call_next(context):
    return "TOOL_RAN"


def _patch_headers(monkeypatch, header_value):
    monkeypatch.setattr(
        authz_middleware,
        "get_http_headers",
        lambda include=None: ({"authorization": header_value} if header_value else {}),
    )


async def test_middleware_allows_authorized_tool(monkeypatch):
    token = issue_token("ana", "analyst")["token"]
    _patch_headers(monkeypatch, f"Bearer {token}")
    mw = AuthzMiddleware()
    # analyst is permitted generate_report per policies.yaml
    result = await mw.on_call_tool(_FakeContext("generate_report"), _call_next)
    assert result == "TOOL_RAN"


async def test_middleware_denies_unauthorized_role(monkeypatch):
    token = issue_token("ana", "analyst")["token"]
    _patch_headers(monkeypatch, f"Bearer {token}")
    mw = AuthzMiddleware()
    with pytest.raises(ToolError) as exc:
        await mw.on_call_tool(_FakeContext("deploy_application"), _call_next)
    assert "not authorized" in str(exc.value)


async def test_middleware_rejects_missing_token(monkeypatch):
    _patch_headers(monkeypatch, None)
    mw = AuthzMiddleware()
    with pytest.raises(ToolError) as exc:
        await mw.on_call_tool(_FakeContext("generate_report"), _call_next)
    assert "Unauthorized" in str(exc.value)


async def test_middleware_rejects_invalid_token(monkeypatch):
    _patch_headers(monkeypatch, "Bearer not-a-real-jwt")
    mw = AuthzMiddleware()
    with pytest.raises(ToolError):
        await mw.on_call_tool(_FakeContext("generate_report"), _call_next)


async def test_middleware_admin_can_deploy(monkeypatch):
    token = issue_token("root", "admin")["token"]
    _patch_headers(monkeypatch, f"Bearer {token}")
    mw = AuthzMiddleware()
    result = await mw.on_call_tool(_FakeContext("deploy_application"), _call_next)
    assert result == "TOOL_RAN"
