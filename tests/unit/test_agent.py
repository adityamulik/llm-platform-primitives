"""Unit tests for the ADK multi-agent wiring + token threading (app/agent.py).

These tests avoid invoking a real model. They cover the pure helpers, the
token-threading http client factory, the token-accounting model callbacks, and
the structured-output validation retry loop.
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from pydantic import BaseModel, ValidationError

from app import agent as agent_mod
from app.agent import (
    CustomLlmAgent,
    _auth_http_client_factory,
    _prompt_provider,
    docs_agent,
    root_agent,
    set_request_auth,
    team_toolsets,
)


def _make_validation_error() -> ValidationError:
    class _M(BaseModel):
        x: int

    try:
        _M(x="not-an-int")
    except ValidationError as exc:
        return exc
    raise AssertionError("expected ValidationError")


# --- wiring -----------------------------------------------------------------
def test_root_agent_has_four_specialists():
    names = {a.name for a in root_agent.sub_agents}
    assert names == {"docs_agent", "codebase_agent", "research_agent", "execution_agent"}


def test_specialist_output_key_derives_from_name():
    assert docs_agent.output_key == "docs_result"


def test_max_validation_retries_property():
    assert docs_agent.max_validation_retries == 3
    custom = CustomLlmAgent(name="tmp_agent", max_validation_retries=7)
    assert custom.max_validation_retries == 7


def test_team_toolsets_builds_one_per_server():
    toolsets = team_toolsets()
    assert len(toolsets) == len(agent_mod._TEAM_SERVERS)


def test_prompt_provider_resolves_from_registry():
    provider = _prompt_provider("root_agent")
    text = provider(None)  # InstructionProvider is called with a context
    assert "root coordinator agent" in text


# --- token threading --------------------------------------------------------
def test_set_request_auth_sets_contextvar():
    set_request_auth("Bearer abc")
    assert agent_mod._current_auth.get() == "Bearer abc"
    set_request_auth(None)
    assert agent_mod._current_auth.get() == ""


async def test_http_client_factory_injects_auth_header():
    set_request_auth("Bearer injected-token")
    client = _auth_http_client_factory()
    hooks = client.event_hooks["request"]
    assert hooks, "expected a request event hook to be registered"

    request = SimpleNamespace(headers={})
    for hook in hooks:
        await hook(request)
    assert request.headers["Authorization"] == "Bearer injected-token"
    await client.aclose()


async def test_http_client_factory_no_token_leaves_headers_untouched():
    set_request_auth(None)
    client = _auth_http_client_factory()
    request = SimpleNamespace(headers={})
    for hook in client.event_hooks["request"]:
        await hook(request)
    assert "Authorization" not in request.headers
    await client.aclose()


# --- model callbacks (token accounting) -------------------------------------
def test_before_model_callback_records_input_text():
    llm_request = SimpleNamespace(contents=["hello world from the user"])
    docs_agent._before_model_callback_impl(SimpleNamespace(), llm_request)
    assert docs_agent._last_input_text == str(llm_request.contents)


def test_after_model_callback_records_tokens(monkeypatch):
    recorded = {}

    def _fake_record(user, *, input_tokens, output_tokens, cost_usd):
        recorded.update(
            user=user,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost_usd,
        )

    monkeypatch.setattr(agent_mod.metrics, "record_tokens", _fake_record)
    monkeypatch.setattr(agent_mod, "get_current_user", lambda: "ana")

    docs_agent._last_input_text = "a prompt"
    llm_response = SimpleNamespace(content="a generated answer")
    docs_agent._after_model_callback_impl(SimpleNamespace(), llm_response)

    assert recorded["user"] == "ana"
    assert recorded["output_tokens"] > 0
    assert recorded["cost_usd"] == 0.0  # local ollama model is free


# --- validation retry loop --------------------------------------------------
async def test_run_async_impl_retries_then_raises(monkeypatch):
    calls = {"n": 0}
    hallucinations = {"n": 0}

    async def _always_fail(self, ctx):
        calls["n"] += 1
        raise _make_validation_error()
        yield  # make it an async generator

    monkeypatch.setattr(agent_mod.LlmAgent, "_run_async_impl", _always_fail)
    monkeypatch.setattr(
        agent_mod.metrics,
        "record_hallucination",
        lambda _u: hallucinations.__setitem__("n", hallucinations["n"] + 1),
    )

    agent = CustomLlmAgent(name="retry_agent", max_validation_retries=3)
    with pytest.raises(ValidationError):
        async for _ in agent._run_async_impl(SimpleNamespace()):
            pass

    assert calls["n"] == 3  # tried max_validation_retries times
    assert hallucinations["n"] == 3


async def test_run_async_impl_succeeds_after_retry(monkeypatch):
    calls = {"n": 0}

    async def _fail_once_then_ok(self, ctx):
        calls["n"] += 1
        if calls["n"] == 1:
            raise _make_validation_error()
            yield
        else:
            yield "event-1"
            yield "event-2"

    monkeypatch.setattr(agent_mod.LlmAgent, "_run_async_impl", _fail_once_then_ok)
    monkeypatch.setattr(agent_mod.metrics, "record_hallucination", lambda _u: None)

    agent = CustomLlmAgent(name="retry_ok_agent", max_validation_retries=3)
    events = [e async for e in agent._run_async_impl(SimpleNamespace())]

    assert calls["n"] == 2  # failed once, then succeeded
    assert events == ["event-1", "event-2"]
