"""Model registry: tokenization algorithm + pricing per model.

Prices are USD per 1 000 tokens (input / output).
Ollama models run locally — cost is always $0.00.

Add or override entries at runtime with ``register_model()``.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

from .algorithms import BPETokenizer, TokenizerAlgorithm, UnigramTokenizer, WordPieceTokenizer


@dataclass(frozen=True)
class ModelConfig:
    algorithm: str          # "bpe" | "wordpiece" | "unigram"
    input_cost_per_1k: float   # USD per 1 000 input tokens
    output_cost_per_1k: float  # USD per 1 000 output tokens


_REGISTRY: dict[str, ModelConfig] = {

    # ------------------------------------------------------------------
    # Google Gemini  (SentencePiece / Unigram LM)
    # ------------------------------------------------------------------
    "gemini-2.5-pro": ModelConfig("unigram", 0.00125, 0.01000),
    "gemini-2.5-flash": ModelConfig("unigram", 0.00015, 0.00060),
    "gemini-3.5-pro": ModelConfig("unigram", 0.00125, 0.01000),
    
    # ------------------------------------------------------------------
    # OpenAI
    # ------------------------------------------------------------------
    "gpt-4o": ModelConfig("bpe", 0.0025, 0.0100),
    "gpt-4o-mini": ModelConfig("bpe", 0.00015, 0.00060),
    "gpt-4-turbo": ModelConfig("bpe", 0.0100, 0.0300),
    "gpt-3.5-turbo": ModelConfig("bpe", 0.00050, 0.00150),
    "o1": ModelConfig("bpe", 0.0150, 0.0600),

    # ------------------------------------------------------------------
    # HuggingFace BERT (WordPiece tokenizer)
    # ------------------------------------------------------------------
    "bert-base-uncased": ModelConfig("wordpiece", 0.00050, 0.00050),

    # ------------------------------------------------------------------
    # Ollama — local inference, always free
    # ------------------------------------------------------------------
    "ollama_chat/llama3.1:latest": ModelConfig("bpe", 0.0, 0.0),
    "ollama_chat/mistral:latest": ModelConfig("bpe", 0.0, 0.0),
    "ollama_chat/gemma2:latest": ModelConfig("unigram", 0.0, 0.0),
    "ollama_chat/phi3:latest": ModelConfig("bpe", 0.0, 0.0),
    "ollama_chat/qwen2.5:latest": ModelConfig("bpe", 0.0, 0.0),
    "ollama_chat/deepseek-r1:latest": ModelConfig("bpe", 0.0, 0.0),
}

_TOKENIZER_FACTORIES = {
    "bpe": lambda: BPETokenizer("cl100k_base"),
    "wordpiece": lambda: WordPieceTokenizer("bert-base-uncased"),
    "unigram": lambda: UnigramTokenizer("t5-small"),
}


def register_model(model_name: str, config: ModelConfig) -> None:
    """Add or override a model entry at runtime."""
    if config.algorithm not in _TOKENIZER_FACTORIES:
        raise ValueError(
            f"algorithm must be one of {list(_TOKENIZER_FACTORIES)}, got {config.algorithm!r}"
        )
    _REGISTRY[model_name] = config
    get_tokenizer.cache_clear()


def get_config(model_name: str) -> ModelConfig:
    # Exact match
    if model_name in _REGISTRY:
        return _REGISTRY[model_name]
    # Prefix match: any "ollama_chat/*" not explicitly listed → free BPE
    if model_name.startswith(("ollama_chat/", "ollama/")):
        return ModelConfig("bpe", 0.0, 0.0)
    raise ValueError(
        f"Unknown model {model_name!r}. "
        f"Register it with token_counter.register_model() or use one of:\n"
        f"  {sorted(_REGISTRY)}"
    )


# cache the tokenizer as model pricing and algorithm doesn't change often
@lru_cache(maxsize=16)
def get_tokenizer(model_name: str) -> TokenizerAlgorithm:
    cfg = get_config(model_name)
    return _TOKENIZER_FACTORIES[cfg.algorithm]()
