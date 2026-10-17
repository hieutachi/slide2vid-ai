import os
import wave
from pathlib import Path

import pytest

from slidevoice.core.errors import ConsentMissing, PluginUnavailable
from slidevoice.core.media import measure_audio, write_tone
from slidevoice.core.models import VoiceProfile
from slidevoice.plugins.tts import WindowsSAPI


def test_audio_measurement_distinguishes_silence_from_signal(tmp_path):
    tone = tmp_path / "tone.wav"
    silence = tmp_path / "silence.wav"
    write_tone(tone, 4)
    write_tone(silence, 4, frequency=0)
    audible = measure_audio(tone)
    quiet = measure_audio(silence)
    assert audible["audible_signal"] is True
    assert -40 < audible["integrated_lufs"] < 0
    assert quiet["audible_signal"] is False
    assert quiet["integrated_lufs"] is None


def test_system_speech_consent_and_language(tmp_path):
    engine = WindowsSAPI({}, tmp_path)
    profile = VoiceProfile(ref_audio=Path("not-read.wav"), ref_text="unused", language="en")
    with pytest.raises(ConsentMissing):
        engine.synthesize("Hello", tmp_path / "test.wav")
    with pytest.raises(ConsentMissing):
        engine.load_voice(profile)
    profile.consent_confirmed = True
    profile.language = "vi"
    with pytest.raises(PluginUnavailable, match="English only"):
        engine.load_voice(profile)
    with pytest.raises(ConsentMissing):
        engine.synthesize("Hello", tmp_path / "test.wav")


@pytest.mark.skipif(os.name != "nt", reason="Windows system speech integration")
def test_system_speech_produces_audible_pcm(tmp_path):
    engine = WindowsSAPI({}, tmp_path)
    engine.load_voice(
        VoiceProfile(
            ref_audio=Path("not-read.wav"),
            ref_text="unused",
            language="en",
            consent_confirmed=True,
        )
    )
    audio = tmp_path / "speech.wav"
    assert engine.synthesize("This is an audible system speech quality test.", audio) > 1
    with wave.open(str(audio), "rb") as reader:
        assert (reader.getframerate(), reader.getnchannels(), reader.getsampwidth()) == (
            24000,
            1,
            2,
        )
    assert measure_audio(audio)["audible_signal"] is True
    assert audio.with_suffix(".txt").read_text(encoding="utf-8").startswith("This is")
