"""Unit tests for the keyword intent classifier (intent_classifier)."""

from __future__ import annotations

from intent_classifier import INTENT_RULES, classify_intent
from intent_classifier import classifier as classifier_mod


def test_classifies_documentation_request():
    result = classify_intent("Please write documentation and a tutorial")
    assert result["status"] == "classified"
    assert result["agent"] == "docs_agent"
    assert result["score"] > 0


def test_classifies_deploy_request_as_execution():
    result = classify_intent("Deploy and run the build")
    assert result["status"] == "classified"
    assert result["agent"] == "execution_agent"


def test_case_insensitive_matching():
    lower = classify_intent("refactor this code")
    upper = classify_intent("REFACTOR THIS CODE")
    assert lower["agent"] == upper["agent"] == "codebase_agent"


def test_unclassified_when_no_keyword_matches():
    result = classify_intent("zzz qqq wxyz")
    assert result["status"] == "unclassified"
    assert result["agent"] is None
    assert result["next_action"] == "ask_user_about_web_search"
    assert set(result["available_agents"]) == set(INTENT_RULES["agents"].keys())


def test_highest_score_wins():
    # "analyze" appears in several agents; "research investigate study" tips it.
    result = classify_intent("research investigate study analyze best practice")
    assert result["status"] == "classified"
    assert result["agent"] == "research_agent"


def test_load_intent_rules_fallback(monkeypatch, tmp_path):
    # Point the loader at a missing file to exercise the except branch.
    monkeypatch.setattr(classifier_mod.os.path, "dirname", lambda _p: str(tmp_path))
    rules = classifier_mod._load_intent_rules()
    assert rules == {"agents": {}, "default_agent": "research_agent"}


def test_classify_with_empty_agents_config(monkeypatch):
    monkeypatch.setattr(classifier_mod, "INTENT_RULES", {"agents": {}})
    result = classify_intent("anything")
    assert result["status"] == "unclassified"
