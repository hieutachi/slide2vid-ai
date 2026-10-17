"""Safe subprocess and dependency-free PCM helpers."""

from __future__ import annotations

import json
import math
import re
import shutil
import struct
import subprocess
import wave
from pathlib import Path

from .errors import PluginUnavailable, StageFailed


def _run_process(args: list[str], timeout: float = 120) -> subprocess.CompletedProcess[str]:
    if not shutil.which(args[0]):
        raise PluginUnavailable(
            f"Executable {args[0]} is missing.",
            remedy="Install ffmpeg/ffprobe and add their bin directory to PATH.",
        )
    try:
        return subprocess.run(
            args,
            check=True,
            timeout=timeout,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError):
        raise StageFailed(
            "Media command failed or timed out.",
            remedy="Check input media, permissions, configured dimensions and the installed ffmpeg codecs.",
        ) from None


def run_process(args: list[str], timeout: float = 120) -> str:
    return _run_process(args, timeout).stdout


def measure_audio(path: Path) -> dict[str, float | bool | None]:
    """Measure decoded samples, not merely the presence of an audio stream.

    Non-finite loudness (digital silence) is represented as null in JSON. This is
    a signal-level check, not ASR or proof of intelligible speech.
    """
    result = _run_process(
        [
            "ffmpeg",
            "-hide_banner",
            "-nostdin",
            "-i",
            str(path),
            "-map",
            "0:a:0",
            "-af",
            "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json",
            "-f",
            "null",
            "-",
        ],
        timeout=300,
    ).stderr
    # Keep volumedetect on a separate decode: it forces int16 sample conversion,
    # which would clip over-full-scale AAC before true-peak measurement.
    levels = _run_process(
        [
            "ffmpeg",
            "-hide_banner",
            "-nostdin",
            "-i",
            str(path),
            "-map",
            "0:a:0",
            "-af",
            "volumedetect",
            "-f",
            "null",
            "-",
        ],
        timeout=300,
    ).stderr
    match = re.search(r'\{\s*"input_i".*?\}', result, re.DOTALL)
    if match is None:
        raise StageFailed("FFmpeg did not return audio loudness measurements.")
    loudness = json.loads(match.group())

    def finite(value: str) -> float | None:
        number = float(value)
        return number if math.isfinite(number) else None

    mean_match = re.search(r"mean_volume: ([\w.+-]+) dB", levels)
    peak_match = re.search(r"max_volume: ([\w.+-]+) dB", levels)
    if mean_match is None or peak_match is None:
        raise StageFailed("FFmpeg did not return decoded audio levels.")
    rms = finite(mean_match.group(1))
    peak = finite(peak_match.group(1))
    lufs = finite(loudness["input_i"])
    return {
        "integrated_lufs": lufs,
        "true_peak_dbtp": finite(loudness["input_tp"]),
        "loudness_range_lu": finite(loudness["input_lra"]),
        "rms_dbfs": rms,
        "peak_dbfs": peak,
        "audible_signal": rms is not None
        and rms > -50
        and peak is not None
        and peak > -45
        and lufs is not None,
    }


def wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as reader:
        return reader.getnframes() / reader.getframerate()


def write_tone(path: Path, duration: float, *, frequency: float = 440, rate: int = 24000) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    samples = round(duration * rate)
    # Tiny edge fades avoid clicks; frequency=0 generates digital silence.
    data = bytearray()
    for i in range(samples):
        fade = min(1, i / 120, (samples - 1 - i) / 120)
        value = int(3000 * fade * math.sin(2 * math.pi * frequency * i / rate))
        data.extend(struct.pack("<h", value))
    with wave.open(str(path), "wb") as writer:
        writer.setparams((1, 2, rate, 0, "NONE", "not compressed"))
        writer.writeframes(data)
