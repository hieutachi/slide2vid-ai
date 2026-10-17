"""Deterministic fake structured-output provider, makes no network calls."""

from typing import Any

from slidevoice.core.interfaces import LLMProvider
from slidevoice.core.registry import register


@register("llm", "fake_llm")
class FakeLLM(LLMProvider):
    name = "fake_llm"

    def complete_json(self, system: str, user: str, schema: dict[str, Any]) -> dict[str, Any]:
        return {"script": user}
