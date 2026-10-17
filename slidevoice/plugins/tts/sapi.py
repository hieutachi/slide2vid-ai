"""Offline Windows system speech for audible QA; never learns a reference voice."""

import math
import os
import shutil
from pathlib import Path

from slidevoice.core.errors import ConsentMissing, PluginUnavailable
from slidevoice.core.interfaces import TTSEngine
from slidevoice.core.media import run_process, wav_duration
from slidevoice.core.models import VoiceProfile
from slidevoice.core.registry import register

SCRIPT = r"""
param([string]$TextPath, [string]$OutPath, [string]$VoiceName, [int]$Rate)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Speech
$s = New-Object System.Speech.Synthesis.SpeechSynthesizer
try {
    if ($VoiceName) { $s.SelectVoice($VoiceName) }
    $s.Rate = $Rate
    $s.Volume = 100
    $format = New-Object System.Speech.AudioFormat.SpeechAudioFormatInfo(
        24000,
        [System.Speech.AudioFormat.AudioBitsPerSample]::Sixteen,
        [System.Speech.AudioFormat.AudioChannel]::Mono)
    $s.SetOutputToWaveFile($OutPath, $format)
    $s.Speak([System.IO.File]::ReadAllText($TextPath, [System.Text.Encoding]::UTF8))
} finally { $s.Dispose() }
"""


@register("tts", "windows_sapi")
class WindowsSAPI(TTSEngine):
    name = "windows_sapi"
    _consented = False

    def healthcheck(self) -> None:
        if os.name != "nt" or not shutil.which("powershell"):
            raise PluginUnavailable(
                "windows_sapi requires Windows PowerShell and an installed system voice.",
                remedy="Use fake_tts for portable tone QA, or install a supported speech plugin.",
            )

    def load_voice(self, voice: VoiceProfile) -> None:
        self._consented = False
        if not voice.consent_confirmed:
            raise ConsentMissing("Consent must be confirmed even for system speech QA.")
        # The validated desktop voices on this machine are English only. Do not
        # silently pronounce Vietnamese through an English voice.
        if voice.language != "en":
            raise PluginUnavailable(
                "windows_sapi QA currently supports English only; no Vietnamese voice is assumed.",
                remedy="Set project.language: en for this QA fixture; use a Vietnamese TTS plugin for Vietnamese.",
            )
        self._consented = True

    def synthesize(self, text: str, out_path: Path, speed: float = 1.0) -> float:
        if not self._consented:
            raise ConsentMissing("Consent must be confirmed before speech synthesis.")
        self.healthcheck()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        text_path = out_path.with_suffix(".input.txt")
        text_path.write_text(text, encoding="utf-8")

        def literal(value: str) -> str:
            return "'" + value.replace("'", "''") + "'"

        # Use the .NET API through normal inline PowerShell; do not change the
        # machine's execution policy. Narration is read as data, never as code.
        command = (
            "& {"
            + SCRIPT
            + "} -TextPath "
            + literal(str(text_path.resolve()))
            + " -OutPath "
            + literal(str(out_path.resolve()))
            + " -VoiceName "
            + literal(str(self.config.get("voice_name", "Microsoft Zira Desktop")))
            + " -Rate "
            + str(max(-10, min(10, round(10 * math.log2(speed)))))
        )
        run_process(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", command],
        )
        out_path.with_suffix(".txt").write_text(text, encoding="utf-8")
        return wav_duration(out_path)
