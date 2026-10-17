"""Beep fixture with transcript sidecar. It never clones a human voice."""

from pathlib import Path

from slidevoice.core.errors import ConsentMissing, StageFailed
from slidevoice.core.interfaces import TTSEngine
from slidevoice.core.media import wav_duration, write_tone
from slidevoice.core.models import VoiceProfile
from slidevoice.core.registry import register

from .sapi import WindowsSAPI as WindowsSAPI
from .vieneu import VieNeuTTS as VieNeuTTS


@register("tts", "fake_tts")
class FakeTTS(TTSEngine):
    name = "fake_tts"
    _consented = False

    def load_voice(self, voice: VoiceProfile) -> None:
        self._consented = voice.consent_confirmed
        if not self._consented:
            raise ConsentMissing("Voice consent must be confirmed before TTS.")

    def synthesize(self, text: str, out_path: Path, speed: float = 1.0) -> float:
        if not self._consented:
            raise ConsentMissing("Voice consent must be confirmed before TTS.")
        if self.config.get("fail", False):
            raise StageFailed("Injected synthetic failure.")
        duration = max(1.0, len(text.split()) * 0.18) / speed
        write_tone(out_path, duration)
        out_path.with_suffix(".txt").write_text(text, encoding="utf-8")
        return wav_duration(out_path)
