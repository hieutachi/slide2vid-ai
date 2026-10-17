"""Deterministic notes-to-sentences fixture, not an LLM rewrite."""

import re

from slidevoice.core.interfaces import LLMProvider, ScriptWriter
from slidevoice.core.models import Segment, Slide
from slidevoice.core.registry import register


@register("script", "fake_script")
class FakeScript(ScriptWriter):
    name = "fake_script"

    def write(self, slide: Slide, deck_context: str, llm: LLMProvider | None) -> Slide:
        slide.script = slide.notes_raw.strip()
        slide.script_source = "notes" if slide.script else "empty"
        # Notes-free slides stay silent in M0; no invented narration.
        sentences = [
            text.strip() for text in re.split(r"(?<=[.!?])\s+|\n+", slide.script) if text.strip()
        ]
        slide.segments = [
            Segment(id=f"s{slide.index:03}_{i:02}", text=text, spoken_text=text)
            for i, text in enumerate(sentences, 1)
        ]
        return slide
