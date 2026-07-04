"""Unit tests for per-user metrics collection (observability.metrics)."""

from __future__ import annotations

import pytest

from observability.metrics import (
    MetricsCollector,
    UserMetrics,
    get_current_team,
    get_current_user,
    set_current_user,
    team_for_role,
)
from observability.metrics.collector import _as_dict


@pytest.mark.parametrize(
    "role,team",
    [
        ("viewer", "shared"),
        ("analyst", "analytics"),
        ("developer", "developer"),
        ("deployer", "devops"),
        ("admin", "platform"),
        ("unknown-role", "unknown"),
        (None, "unknown"),
    ],
)
def test_team_for_role(role, team):
    assert team_for_role(role) == team


def test_set_and_get_current_user_and_team():
    set_current_user("ana", role="analyst")
    assert get_current_user() == "ana"
    assert get_current_team() == "analytics"


def test_set_current_user_defaults_when_none():
    set_current_user(None, role=None)
    assert get_current_user() == "anonymous"
    assert get_current_team() == "unknown"


# --- UserMetrics computed properties ----------------------------------------
def test_user_metrics_properties_with_zero_requests():
    m = UserMetrics(user_id="x")
    assert m.total_tokens == 0
    assert m.avg_latency_s == 0.0
    assert m.success_rate == 0.0


def test_user_metrics_properties_with_data():
    m = UserMetrics(
        user_id="x",
        requests=4,
        successes=3,
        input_tokens=100,
        output_tokens=50,
        total_latency_s=2.0,
    )
    assert m.total_tokens == 150
    assert m.avg_latency_s == 0.5
    assert m.success_rate == 0.75


# --- MetricsCollector -------------------------------------------------------
def test_record_tokens_accumulates():
    c = MetricsCollector()
    c.record_tokens("ana", input_tokens=10, output_tokens=5, cost_usd=0.01)
    c.record_tokens("ana", input_tokens=20, output_tokens=5, cost_usd=0.02)
    snap = c.snapshot("ana")
    assert snap["input_tokens"] == 30
    assert snap["output_tokens"] == 10
    assert snap["total_cost_usd"] == pytest.approx(0.03)
    assert snap["total_tokens"] == 40


def test_record_request_success_and_error():
    c = MetricsCollector()
    c.record_request("dev", success=True, latency_s=1.0)
    c.record_request("dev", success=False, latency_s=3.0)
    snap = c.snapshot("dev")
    assert snap["requests"] == 2
    assert snap["successes"] == 1
    assert snap["errors"] == 1
    assert snap["avg_latency_s"] == pytest.approx(2.0)
    assert snap["success_rate"] == pytest.approx(0.5)


def test_record_hallucination():
    c = MetricsCollector()
    c.record_hallucination("ana")
    c.record_hallucination("ana")
    assert c.snapshot("ana")["hallucinations"] == 2


def test_track_request_success_context_manager():
    c = MetricsCollector()
    with c.track_request("ana"):
        pass
    snap = c.snapshot("ana")
    assert snap["successes"] == 1
    assert snap["errors"] == 0


def test_track_request_error_reraises_and_counts():
    c = MetricsCollector()
    with pytest.raises(ValueError):
        with c.track_request("ana"):
            raise ValueError("boom")
    snap = c.snapshot("ana")
    assert snap["errors"] == 1
    assert snap["successes"] == 0


def test_snapshot_all_users():
    c = MetricsCollector()
    c.record_tokens("a", input_tokens=1, output_tokens=1)
    c.record_tokens("b", input_tokens=1, output_tokens=1)
    snap = c.snapshot()
    assert set(snap.keys()) == {"a", "b"}


def test_snapshot_unknown_user_is_empty():
    c = MetricsCollector()
    assert c.snapshot("nobody") == {}


def test_bucket_refreshes_team_from_context():
    c = MetricsCollector()
    set_current_user("ana", role="analyst")
    c.record_tokens("ana", input_tokens=1, output_tokens=1)
    assert c.snapshot("ana")["team"] == "analytics"


def test_as_dict_adds_derived_fields():
    m = UserMetrics(user_id="x", requests=2, successes=1, total_latency_s=1.0)
    d = _as_dict(m)
    assert d["total_tokens"] == 0
    assert d["avg_latency_s"] == 0.5
    assert d["success_rate"] == 0.5
