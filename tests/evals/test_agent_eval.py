"""ADK agent evaluations (https://adk.dev/evaluate/).

These drive the real ``root_agent`` through ADK's ``AgentEvaluator`` against the
eval set in ``data/``. Unlike the unit/integration tests, they need a live model
(Ollama serving ``llama3.1``) and the three team MCP servers running, so they are
gated behind:

  * the ``eval`` marker (deselected in the default CI run), and
  * a reachability probe for Ollama — the suite is skipped, not failed, when the
    model backend is unavailable, so ``make test`` stays green on a laptop.

Run them explicitly with::

    make ollama-serve          # in one terminal
    make run-all               # MCP servers + gateway (another terminal)
    make eval                  # -> pytest -m eval

The pass/fail bar (tool-trajectory + response-match thresholds) lives in
``data/test_config.json``; ``AgentEvaluator.evaluate`` raises if a metric's
average score across ``num_runs`` falls below its threshold.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

try:  # httpx ships as a project dependency; guard just in case.
    import httpx
except Exception:  # pragma: no cover
    httpx = None

DATA_DIR = Path(__file__).parent / "data"
EVALSET = DATA_DIR / "root_agent.evalset.json"
CONFIG = DATA_DIR / "test_config.json"

OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")


def _ollama_available() -> bool:
    if httpx is None:
        return False
    try:
        return httpx.get(f"{OLLAMA_URL}/api/tags", timeout=1.0).status_code == 200
    except Exception:
        return False


def _eval_service_importable() -> bool:
    # The ADK `eval` extra provides the local eval service + metric evaluators
    # (install with `uv sync --group eval`).
    import importlib.util

    return importlib.util.find_spec("google.adk.evaluation.local_eval_service") is not None


def _eval_skip_reason() -> str | None:
    if os.getenv("RUN_ADK_EVALS") != "1":
        return "set RUN_ADK_EVALS=1 to run the model-backed ADK evals (see `make eval`)."
    if not _eval_service_importable():
        return "ADK eval extra not installed; run `uv sync --group eval`."
    if not _ollama_available():
        return (
            f"Ollama not reachable at {OLLAMA_URL}; run `make ollama-serve` and "
            "`make run-all` (for the team MCP servers)."
        )
    return None


@pytest.mark.eval
@pytest.mark.skipif(_eval_skip_reason() is not None, reason=_eval_skip_reason() or "")
async def test_root_agent_routing_evalset():
    """The root agent classifies intent and routes correctly across the eval set.

    The eval set encodes the *designed* routing contract — call ``classify_intent``
    then ``transfer_to_agent`` for the right specialist — and enforces the
    ``tool_trajectory_avg_score`` threshold in ``data/test_config.json`` (the
    metric's mean score across ``num_runs`` must clear the bar).

    Note: ``tool_trajectory`` scoring is an exact-sequence match, so this is a
    meaningful bar only for a model capable of following the contract reliably.
    The small default local model (``llama3.1`` via Ollama) is not guaranteed to
    clear it — point the agent at a stronger model to use this as a real gate.
    """
    from google.adk.evaluation.agent_evaluator import AgentEvaluator

    await AgentEvaluator.evaluate(
        agent_module="app.agent",
        eval_dataset_file_path_or_dir=str(EVALSET),
        num_runs=int(os.getenv("ADK_EVAL_NUM_RUNS", "2")),
    )


def test_evalset_and_config_are_well_formed():
    """Cheap always-on guard: the eval fixtures stay valid JSON with the ADK schema.

    Runs without a model so a malformed eval set is caught in normal CI even
    though the model-backed eval above is skipped.
    """
    import json

    config = json.loads(CONFIG.read_text())
    assert set(config["criteria"]) <= {
        "tool_trajectory_avg_score",
        "response_evaluation_score",
        "response_match_score",
        "safety_v1",
    }

    evalset = json.loads(EVALSET.read_text())
    assert evalset["eval_set_id"]
    assert evalset["eval_cases"], "eval set must contain at least one case"
    for case in evalset["eval_cases"]:
        assert case["eval_id"]
        assert case["conversation"], "each eval case needs a conversation"
        for turn in case["conversation"]:
            assert turn["user_content"]["parts"][0]["text"]
            assert turn["final_response"]["parts"][0]["text"]
            # The canonical routing contract: classify intent, then delegate to
            # the correct specialist via transfer_to_agent.
            tool_uses = turn["intermediate_data"]["tool_uses"]
            assert tool_uses, "each turn must specify an expected tool trajectory"
            names = [t["name"] for t in tool_uses]
            assert "classify_intent" in names
            transfers = [t for t in tool_uses if t["name"] == "transfer_to_agent"]
            assert transfers, "expected a transfer_to_agent routing call"
            assert transfers[0]["args"]["agent_name"].endswith("_agent")
