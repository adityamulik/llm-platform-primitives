from tokenizers import Tokenizer

from .base import TokenizerAlgorithm


class WordPieceTokenizer(TokenizerAlgorithm):
    """WordPiece tokenizer backed by HuggingFace tokenizers.

    Used by: BERT-family models, DistilBERT.
    Also used as an approximation for Gemini models (Google uses a
    WordPiece-derived vocabulary in some Gemini variants).

    Pretrained model is downloaded and cached by HuggingFace on first use.
    """

    algorithm = "wordpiece"

    def __init__(self, pretrained_model: str = "bert-base-uncased") -> None:
        self._tokenizer = Tokenizer.from_pretrained(pretrained_model)

    def encode(self, text: str) -> list[int]:
        return self._tokenizer.encode(text).ids
