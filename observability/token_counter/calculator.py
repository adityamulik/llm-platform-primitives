from __future__ import annotations

from dataclasses import dataclass

from .model_registry import get_config, get_tokenizer


@dataclass
class TokenUsage:
    model: str
    algorithm: str
    input_tokens: int
    output_tokens: int
    input_cost: float   # USD
    output_cost: float  # USD
    total_cost: float   # USD
    source: str = "estimated"   # "estimated" | "api_response"

    def __str__(self) -> str:
        local = self.total_cost == 0.0
        cost_str = "(local — free)" if local else f"${self.total_cost:.6f}"
        return (
            f"model={self.model}  algo={self.algorithm}  source={self.source}\n"
            f"  tokens : {self.input_tokens:>8,} in  /  {self.output_tokens:>8,} out\n"
            f"  cost   : {cost_str}"
        )


class TokenCostCalculator:
    """Calculate token counts and USD cost for any registered model.

    Two entry points:

    ``calculate(input_text, output_text)``
        Pre-call estimation — tokenises with the model's algorithm then
        multiplies by the registry price.  Use this before making an API call.

    ``calculate_from_counts(input_tokens, output_tokens)``
        Post-call — pass the token counts that the API already returned.
        No re-tokenisation, just the price lookup.  This is the accurate path.
    """

    def __init__(self, model: str) -> None:
        self.model = model
        self._config = get_config(model)
        self._tokenizer = get_tokenizer(model)

    @property
    def algorithm(self) -> str:
        return self._config.algorithm

    def calculate(self, input_text: str, output_text: str) -> TokenUsage:
        input_tokens = self._tokenizer.count(input_text)
        output_tokens = self._tokenizer.count(output_text)
        return self._price(input_tokens, output_tokens, source="estimated")

    def calculate_from_counts(self, input_tokens: int, output_tokens: int) -> TokenUsage:
        return self._price(input_tokens, output_tokens, source="api_response")

    def count_tokens(self, text: str) -> int:
        return self._tokenizer.count(text)

    def _price(self, input_tokens: int, output_tokens: int, source: str) -> TokenUsage:
        cfg = self._config
        input_cost = input_tokens * cfg.input_cost_per_1k / 1000
        output_cost = output_tokens * cfg.output_cost_per_1k / 1000
        return TokenUsage(
            model=self.model,
            algorithm=self._config.algorithm,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            input_cost=input_cost,
            output_cost=output_cost,
            total_cost=input_cost + output_cost,
            source=source,
        )


def calculate_cost(model: str, input_text: str, output_text: str) -> TokenUsage:
    return TokenCostCalculator(model).calculate(input_text, output_text)
