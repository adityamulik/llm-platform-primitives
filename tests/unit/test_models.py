"""Unit tests for shared gateway request models (gateway/models.py)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from gateway.models import (
    AgentExecuteRequest,
    AuthorizeRequest,
    LoginRequest,
    PromptRollbackRequest,
    SessionRequest,
    TokenRequest,
)


def test_login_request_requires_fields():
    req = LoginRequest(username="ana", password="pw")
    assert req.username == "ana"
    with pytest.raises(ValidationError):
        LoginRequest(username="ana")  # missing password


def test_token_request_optional():
    assert TokenRequest().token is None
    assert TokenRequest(token="abc").token == "abc"


def test_authorize_request_all_optional():
    req = AuthorizeRequest(tool="read_file")
    assert req.tool == "read_file"
    assert req.resource is None and req.operation is None


def test_session_request_optional():
    assert SessionRequest().token is None


def test_agent_execute_request_requires_session_and_prompt():
    req = AgentExecuteRequest(session_id="s1", prompt="hi")
    assert req.session_id == "s1"
    assert req.token is None
    with pytest.raises(ValidationError):
        AgentExecuteRequest(prompt="hi")  # missing session_id


def test_prompt_rollback_request_requires_version():
    assert PromptRollbackRequest(version="1.0.0").version == "1.0.0"
    with pytest.raises(ValidationError):
        PromptRollbackRequest()
