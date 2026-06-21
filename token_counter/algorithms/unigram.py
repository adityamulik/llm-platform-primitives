from tokenizers import Tokenizer

from .base import TokenizerAlgorithm


class UnigramTokenizer(TokenizerAlgorithm):
    """Unigram Language Model tokenizer backed by HuggingFace tokenizers.

    Used by: Google T5, mT5, ALBERT, and Google Gemini models (all built on
    SentencePiece with a Unigram LM).  "t5-small" is the default because it
    shares the same SentencePiece Unigram architecture as Gemini's internal
    tokenizer, giving a reasonable token-count approximation.

    Pretrained model is downloaded and cached by HuggingFace on first use.
    """

    algorithm = "unigram"

    def __init__(self, pretrained_model: str = "t5-small") -> None:
        self._tokenizer = Tokenizer.from_pretrained(pretrained_model)

    def encode(self, text: str) -> list[int]:
        return self._tokenizer.encode(text).ids
