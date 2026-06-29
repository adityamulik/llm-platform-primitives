import tiktoken

from .base import TokenizerAlgorithm


class BPETokenizer(TokenizerAlgorithm):
    """Byte Pair Encoding tokenizer backed by tiktoken.

    Used by: OpenAI GPT family, Anthropic Claude.
    Encoding presets: "cl100k_base" (GPT-4/Claude), "o200k_base" (GPT-4o).
    """

    algorithm = "bpe"

    def __init__(self, encoding: str = "cl100k_base") -> None:
        self._enc = tiktoken.get_encoding(encoding)

    def encode(self, text: str) -> list[int]:
        return self._enc.encode(text)
