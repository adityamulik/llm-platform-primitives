"""Unit tests for the RBAC PolicyEngine (gateway/engine.py)."""

from __future__ import annotations

import textwrap

import pytest

from gateway.engine import PolicyEngine, policy_engine


@pytest.fixture
def custom_policy(tmp_path):
    """A small standalone policy file for isolated engine tests."""
    policy = tmp_path / "policies.yaml"
    policy.write_text(
        textwrap.dedent(
            """
            roles:
              reader:
                description: read only
                permissions:
                  tools:
                    - read_file
                    - list_directory
                  resources:
                    - "file://logs/*"
                    - "db://public/reports"
                  operations:
                    - GET
                    - LIST
              super:
                description: everything
                permissions:
                  tools: ["*"]
                  resources: ["*"]
                  operations: ["*"]
              empty:
                description: no permissions block
            """
        ).strip()
    )
    return PolicyEngine(policy)


def test_roles_lists_known_roles(custom_policy):
    assert set(custom_policy.roles()) == {"reader", "super", "empty"}


def test_default_singleton_loads_shipped_policy():
    # The module-level singleton loads gateway/policies.yaml.
    assert "admin" in policy_engine.roles()
    assert "viewer" in policy_engine.roles()


@pytest.mark.parametrize(
    "role,tool,expected",
    [
        ("reader", "read_file", True),
        ("reader", "deploy_application", False),
        ("super", "anything_at_all", True),  # wildcard
        ("unknown_role", "read_file", False),
        ("empty", "read_file", False),  # role exists but no permissions block
    ],
)
def test_can_access_tool(custom_policy, role, tool, expected):
    assert custom_policy.can_access_tool(role, tool) is expected


@pytest.mark.parametrize(
    "role,resource,expected",
    [
        ("reader", "file://logs/app.log", True),  # glob match
        ("reader", "file://secrets/key", False),
        ("reader", "db://public/reports", True),  # exact literal (colon/slash)
        ("reader", "db://public/reportsX", False),
        ("super", "any://thing", True),  # wildcard
        ("unknown", "file://logs/app.log", False),
    ],
)
def test_can_access_resource(custom_policy, role, resource, expected):
    assert custom_policy.can_access_resource(role, resource) is expected


@pytest.mark.parametrize(
    "role,operation,expected",
    [
        ("reader", "GET", True),
        ("reader", "DELETE", False),
        ("super", "DELETE", True),  # wildcard
        ("unknown", "GET", False),
    ],
)
def test_can_perform_operation(custom_policy, role, operation, expected):
    assert custom_policy.can_perform_operation(role, operation) is expected


def test_get_authorized_tools(custom_policy):
    assert custom_policy.get_authorized_tools("reader") == [
        "read_file",
        "list_directory",
    ]
    assert custom_policy.get_authorized_tools("super") == ["*"]
    assert custom_policy.get_authorized_tools("unknown") == []


def test_authorize_all_dimensions_pass(custom_policy):
    decision = custom_policy.authorize(
        "reader", tool="read_file", resource="file://logs/x", operation="GET"
    )
    assert decision["allowed"] is True
    assert decision["known_role"] is True
    assert decision["denied"] == []
    assert decision["checks"] == {"tool": True, "resource": True, "operation": True}


def test_authorize_one_dimension_fails(custom_policy):
    decision = custom_policy.authorize(
        "reader", tool="deploy_application", operation="GET"
    )
    assert decision["allowed"] is False
    assert "tool" in decision["denied"]
    assert "operation" not in decision["denied"]


def test_authorize_unknown_role_never_allowed(custom_policy):
    decision = custom_policy.authorize("ghost", tool="read_file")
    assert decision["allowed"] is False
    assert decision["known_role"] is False


def test_authorize_with_no_dimensions_is_denied(custom_policy):
    # No dimension supplied => nothing to allow.
    decision = custom_policy.authorize("super")
    assert decision["allowed"] is False
    assert decision["checks"] == {}


def test_reload_picks_up_changes(custom_policy, tmp_path):
    (tmp_path / "policies.yaml").write_text("roles: {}\n")
    custom_policy.reload()
    assert custom_policy.roles() == []


def test_empty_policy_file(tmp_path):
    policy = tmp_path / "empty.yaml"
    policy.write_text("")  # yaml.safe_load -> None
    engine = PolicyEngine(policy)
    assert engine.roles() == []


def test_match_pattern_escapes_special_chars():
    # A literal dot in the resource must not act as a regex wildcard.
    assert PolicyEngine._match_pattern("file://a.log", "file://a.log") is True
    assert PolicyEngine._match_pattern("file://axlog", "file://a.log") is False
