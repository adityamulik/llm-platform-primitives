"""Intent Classifier Module - Rule-based intent classification for agent routing."""

from .classifier import classify_intent, INTENT_RULES

__all__ = ["classify_intent", "INTENT_RULES"]
