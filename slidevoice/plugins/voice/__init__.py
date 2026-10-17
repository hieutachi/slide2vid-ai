"""Synthetic voice preparation, no speaker recognition or denoising."""

from pathlib import Path

from slidevoice.core.interfaces import VoicePreparer
from slidevoice.core.media import run_process
from slidevoice.core.models import VoiceProfile
from slidevoice.core.registry import register


@register("voice", "fake_voice")
class FakeVoice(VoicePreparer):
    name = "fake_voice"

    def prepare(self, raw_audio: Path, language: str, out_dir: Path) -> VoiceProfile:
        output = out_dir / "reference.wav"
        run_process(
            [
                "ffmpeg",
                "-v",
                "error",
                "-nostdin",
                "-y",
                "-i",
                str(self.workdir / raw_audio),
                "-t",
                str(self.config.get("ref_max_sec", 15)),
                "-ar",
                "24000",
                "-ac",
                "1",
                "-c:a",
                "pcm_s16le",
                str(output),
            ]
        )
        return VoiceProfile(
            ref_audio=output.relative_to(self.workdir),
            ref_text="Synthetic tone, no real speaker.",
            language=language,
            extra={"synthetic": True},
        )


@register("voice", "preset_voice")
class PresetVoice(VoicePreparer):
    """A silent contract placeholder, never a cloning reference."""

    name = "preset_voice"
    version = "0.1.0"

    def prepare(self, raw_audio: Path, language: str, out_dir: Path) -> VoiceProfile:
        from slidevoice.core.media import write_tone

        output = out_dir / "preset_placeholder.wav"
        write_tone(output, 0.1, frequency=0)
        return VoiceProfile(
            ref_audio=output.relative_to(self.workdir),
            ref_text="Bundled preset; no personal speaker reference.",
            language=language,
            extra={"preset_only": True},
        )
