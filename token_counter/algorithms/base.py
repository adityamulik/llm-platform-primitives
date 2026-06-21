from abc import ABC, abstractmethod


class TokenizerAlgorithm(ABC):
    @property
    @abstractmethod
    def algorithm(self) -> str: ...

    @abstractmethod
    def encode(self, text: str) -> list[int]: ...

    def count(self, text: str) -> int:
        return len(self.encode(text))
