"""Whitespace-only normalizer for M0; Vietnamese number rules belong to M4."""

from slidevoice.core.interfaces import TextNormalizer
from slidevoice.core.registry import register


@register("normalize", "fake_normalize")
class FakeNormalizer(TextNormalizer):
    name = "fake_normalize"

    def normalize(self, text: str, language: str) -> str:
        return " ".join(text.split())
