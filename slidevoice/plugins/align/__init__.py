"""Synthetic alignment uses beep transcript sidecars, not speech recognition."""

from pathlib import Path

from slidevoice.core.interfaces import Aligner
from slidevoice.core.media import wav_duration
from slidevoice.core.models import Word
from slidevoice.core.registry import register


@register("align", "fake_align")
class FakeAligner(Aligner):
    name = "fake_align"

    def transcribe(self, audio: Path, language: str) -> str:
        sidecar = audio.with_suffix(".txt")
        return sidecar.read_text(encoding="utf-8") if sidecar.is_file() else ""

    def align(self, audio: Path, text: str, language: str) -> list[Word]:
        words = text.split()
        duration = wav_duration(audio)
        return [
            Word(
                text=word,
                start=i * duration / len(words),
                end=(i + 1) * duration / len(words),
                score=1,
            )
            for i, word in enumerate(words)
        ]
