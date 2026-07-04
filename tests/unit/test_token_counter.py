"""Unit tests for token counting + cost estimation (observability.token_counter)."""

from __future__ import annotations

import pytest

from observability.token_counter import (
    ModelConfig,
    TokenCostCalculator,
    TokenUsage,
    calculate_cost,
    get_config,
    get_tokenizer,
    register_model,
)
from observability.token_counter.algorithms import (
    BPETokenizer,
    UnigramTokenizer,
    WordPieceTokenizer,
)


# --- model registry ---------------------------------------------------------
def test_get_config_exact_match():
    cfg = get_config("gpt-4o")
    assert cfg.algorithm == "bpe"
    assert cfg.input_cost_per_1k == 0.0025


def test_get_config_ollama_prefix_is_free():
    cfg = get_config("ollama_chat/some-unlisted-model:latest")
    assert cfg.algorithm == "bpe"
    assert cfg.input_cost_per_1k == 0.0
    assert cfg.output_cost_per_1k == 0.0


def test_get_config_unknown_model_raises():
    with pytest.raises(ValueError):
        get_config("totally-made-up-model")


def test_register_model_adds_entry():
    register_model("test-model-x", ModelConfig("bpe", 0.001, 0.002))
    cfg = get_config("test-model-x")
    assert cfg.output_cost_per_1k == 0.002


def test_register_model_rejects_unknown_algorithm():
    with pytest.raises(ValueError):
        register_model("bad", ModelConfig("nonsense", 0.0, 0.0))


def test_get_tokenizer_is_cached():
    t1 = get_tokenizer("gpt-4o")
    t2 = get_tokenizer("gpt-4o")
    assert t1 is t2  # lru_cache


# --- tokenizer algorithms ---------------------------------------------------
@pytest.mark.parametrize(
    "tokenizer_cls",
    [BPETokenizer, WordPieceTokenizer, UnigramTokenizer],
)
def test_tokenizers_count_and_encode(tokenizer_cls):
    tok = tokenizer_cls()
    ids = tok.encode("hello world")
    assert isinstance(ids, list)
    assert len(ids) > 0
    assert tok.count("hello world") == len(ids)


def test_empty_string_counts_zero_tokens():
    assert BPETokenizer().count("") == 0


def test_algorithm_names():
    assert BPETokenizer().algorithm == "bpe"
    assert WordPieceTokenizer().algorithm == "wordpiece"
    assert UnigramTokenizer().algorithm == "unigram"


# --- calculator -------------------------------------------------------------
def test_calculate_estimated_from_text():
    calc = TokenCostCalculator("gpt-4o")
    assert calc.algorithm == "bpe"
    usage = calc.calculate("hello world", "hi there friend")
    assert usage.source == "estimated"
    assert usage.input_tokens > 0
    assert usage.output_tokens > 0
    expected = (
        usage.input_tokens * 0.0025 / 1000 + usage.output_tokens * 0.0100 / 1000
    )
    assert usage.total_cost == pytest.approx(expected)


def test_calculate_from_counts_uses_api_source():
    calc = TokenCostCalculator("gpt-4o")
    usage = calc.calculate_from_counts(1000, 2000)
    assert usage.source == "api_response"
    assert usage.input_cost == pytest.approx(0.0025)
    assert usage.output_cost == pytest.approx(0.0200)
    assert usage.total_cost == pytest.approx(0.0225)


def test_local_ollama_model_is_free():
    calc = TokenCostCalculator("ollama_chat/llama3.1:latest")
    usage = calc.calculate("some prompt", "some answer")
    assert usage.total_cost == 0.0


def test_count_tokens_helper():
    calc = TokenCostCalculator("gpt-4o")
    assert calc.count_tokens("hello world") > 0


def test_calculate_cost_convenience_function():
    usage = calculate_cost("gpt-4o", "input text", "output text")
    assert isinstance(usage, TokenUsage)
    assert usage.model == "gpt-4o"


# --- TokenUsage.__str__ -----------------------------------------------------
def test_token_usage_str_local_is_free():
    usage = TokenUsage(
        model="ollama_chat/llama3.1:latest",
        algorithm="bpe",
        input_tokens=10,
        output_tokens=5,
        input_cost=0.0,
        output_cost=0.0,
        total_cost=0.0,
    )
    rendered = str(usage)
    assert "local — free" in rendered
    assert "ollama_chat/llama3.1:latest" in rendered


def test_token_usage_str_paid_shows_dollar_amount():
    usage = TokenUsage(
        model="gpt-4o",
        algorithm="bpe",
        input_tokens=1000,
        output_tokens=1000,
        input_cost=0.0025,
        output_cost=0.01,
        total_cost=0.0125,
        source="api_response",
    )
    rendered = str(usage)
    assert "$0.012500" in rendered
    assert "api_response" in rendered
