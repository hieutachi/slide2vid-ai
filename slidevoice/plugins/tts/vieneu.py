"""Local preset-only Vietnamese TTS through an isolated, persistent GPU worker."""

import math
import wave
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from slidevoice.core.errors import ConsentMissing, InputInvalid, PluginUnavailable, StageFailed
from slidevoice.core.interfaces import TTSEngine
from slidevoice.core.media import wav_duration
from slidevoice.core.models import VoiceProfile
from slidevoice.core.registry import register
from slidevoice.core.worker_client import WorkerClient


@register("tts", "vieneu")
class VieNeuTTS(TTSEngine):
    """Use licensed bundled presets; never read or upload ref_audio for cloning."""

    name = "vieneu"
    version = "0.1.0"
    _consented = False

    def _client(self) -> WorkerClient:
        url = str(self.config.get("worker_url", "http://127.0.0.1:8770"))
        parsed = urlparse(url)
        if parsed.scheme != "http" or parsed.hostname != "127.0.0.1":
            raise InputInvalid("VieNeu worker must use an HTTP loopback URL at 127.0.0.1.")
        return WorkerClient(
            url, self.workdir, timeout=float(self.config.get("timeout", 600)), retries=0
        )

    def healthcheck(self) -> None:
        with self._client() as client:
            client.healthcheck()

    def load_voice(self, voice: VoiceProfile) -> None:
        self._consented = False
        if not voice.consent_confirmed:
            raise ConsentMissing("Consent must be confirmed before preset speech synthesis.")
        if voice.language != "vi":
            raise PluginUnavailable("This VieNeu integration is validated for Vietnamese only.")
        self._consented = True

    def synthesize(self, text: str, out_path: Path, speed: float = 1.0) -> float:
        if not self._consented:
            raise ConsentMissing("Consent must be confirmed before preset speech synthesis.")
        if not text.strip() or not math.isfinite(speed) or not 0.5 <= speed <= 2:
            raise InputInvalid("Provide text and a finite speed between 0.5 and 2.")
        with self._client() as client:
            relative = client.shared_path(out_path)
            payload: dict[str, Any] = {
                "task": "tts_preset",
                "workdir": str(self.workdir.resolve()),
                "out_path": relative,
                "text": text,
                "language": "vi",
                "voice": str(self.config.get("preset_voice", "Mai Anh")),
                "seed": int(self.config.get("seed", 42)),
                "speed": speed,
                "consent_confirmed": True,
            }
            result = client.run(payload)
        if result.get("out_path") != relative or result.get("sample_rate") != 24000:
            raise StageFailed("VieNeu worker returned an inconsistent artifact contract.")
        try:
            with wave.open(str(out_path), "rb") as audio:
                if (audio.getframerate(), audio.getnchannels(), audio.getsampwidth()) != (
                    24000,
                    1,
                    2,
                ):
                    raise StageFailed("VieNeu pipeline audio must be 24 kHz mono PCM16.")
            duration = wav_duration(out_path)
        except (OSError, EOFError, wave.Error):
            raise StageFailed("VieNeu worker did not produce readable PCM audio.") from None
        if duration <= 0 or result.get("audible_signal") is not True:
            raise StageFailed("VieNeu worker produced empty or silent audio.")
        # A sidecar is NOT an independent ASR transcript; QA reports disclose this.
        out_path.with_suffix(".txt").write_text(text, encoding="utf-8")
        return duration
