"""Loopback-only preset TTS worker. Run with this worker's Python, not core Python."""

import argparse
import json
import logging
import math
import os
import subprocess
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

LOG = logging.getLogger("slidevoice.vieneu")


def output_path(payload, allowed_root):
    """The worker may write only relative WAV paths within an allowed job root."""
    if payload.get("task") != "tts_preset" or payload.get("consent_confirmed") is not True:
        raise ValueError("Only explicitly consented preset speech is supported.")
    if payload.get("language") != "vi":
        raise ValueError("Only Vietnamese is validated.")
    text = payload.get("text")
    if not isinstance(text, str) or not text.strip() or len(text) > 5000:
        raise ValueError("Text must contain 1–5000 characters.")
    speed = float(payload.get("speed", 1))
    if not math.isfinite(speed) or not 0.5 <= speed <= 2:
        raise ValueError("Speed must be between 0.5 and 2.")
    root = Path(payload["workdir"]).resolve()
    relative = Path(payload["out_path"])
    target = (root / relative).resolve()
    if (
        not root.is_relative_to(allowed_root.resolve())
        or relative.is_absolute()
        or not target.is_relative_to(root)
        or target.suffix.lower() != ".wav"
    ):
        raise ValueError("Output must be a job-relative WAV within the allowed root.")
    return target


class PresetEngine:
    def __init__(self):
        import torch
        from vieneu import Vieneu

        if not torch.cuda.is_available():
            raise RuntimeError(
                "CUDA is required for this GPU worker; refusing silent CPU fallback."
            )
        torch.set_num_threads(8)
        pins = Path(os.environ["HF_HOME"]) / "pinned_models.json"
        if not pins.is_file():
            raise RuntimeError("Run download_models.py first to fetch pinned inference artifacts.")
        pinned = json.loads(pins.read_text(encoding="utf-8"))
        self.tts = Vieneu(
            mode="v3turbo",
            backend="pytorch",
            device="cuda",
            backbone_repo=pinned["model"],
            moss_tokenizer=pinned["codec"],
        )
        self.voices = self.tts.list_preset_voices()
        self.voice_ids = {voice_id for _, voice_id in self.voices}
        self.metadata = {
            "model": "pnnbao-ump/VieNeu-TTS-v3-Turbo",
            "backend": self.tts.backend,
            "device": torch.cuda.get_device_name(0),
            "torch": torch.__version__,
            "cuda": torch.version.cuda,
            "native_sample_rate": 48000,
            "voice_mode": "licensed_bundled_presets_only",
            "model_revision": pinned["model_revision"],
            "codec_revision": pinned["codec_revision"],
        }

    def run(self, payload, allowed_root):
        import numpy as np
        import soundfile as sf
        import torch

        target = output_path(payload, allowed_root)
        voice = payload.get("voice")
        if voice not in self.voice_ids:
            raise ValueError("Unknown bundled preset voice; consult /voices.")
        seed = int(payload.get("seed", 42))
        torch.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        np.random.seed(seed % (2**32))
        start = time.perf_counter()
        audio = np.asarray(self.tts.infer(payload["text"], voice=voice), dtype=np.float32)
        elapsed = time.perf_counter() - start
        if audio.ndim != 1 or audio.size == 0 or not np.isfinite(audio).all():
            raise RuntimeError("TTS returned empty, invalid, or non-finite samples.")
        rms = float(np.sqrt(np.mean(audio.astype(np.float64) ** 2)))
        peak = float(np.max(np.abs(audio)))
        if rms < 0.001 or peak < 0.005:
            raise RuntimeError("TTS returned silent or near-silent audio.")
        target.parent.mkdir(parents=True, exist_ok=True)
        native = target.with_suffix(".native48k.wav")
        # Keep a native 48 kHz copy for listening; core compositor requires 24 kHz.
        # Apply the same gain to both; never hard-clip an over-full-scale waveform.
        gain = min(1.0, 0.95 / peak)
        sf.write(str(native), audio * gain, 48000, subtype="PCM_16")
        filters = f"atempo={float(payload.get('speed', 1))}"
        subprocess.run(
            [
                "ffmpeg",
                "-v",
                "error",
                "-nostdin",
                "-y",
                "-i",
                str(native),
                "-af",
                filters,
                "-ar",
                "24000",
                "-ac",
                "1",
                "-c:a",
                "pcm_s16le",
                str(target),
            ],
            check=True,
            timeout=120,
            capture_output=True,
        )
        result = {
            **self.metadata,
            "out_path": payload["out_path"],
            "voice": voice,
            "seed": seed,
            "sample_rate": 24000,
            "native_duration_seconds": len(audio) / 48000,
            "generation_seconds": elapsed,
            "real_time_factor": elapsed / (len(audio) / 48000),
            "rms_dbfs_native": 20 * math.log10(rms),
            "peak_dbfs_native": 20 * math.log10(peak),
            "applied_gain": gain,
            "audible_signal": True,
            "human_listening_verified": False,
        }
        target.with_suffix(".metrics.json").write_text(
            json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        return result


def handler_for(engine, allowed_root):
    class Handler(BaseHTTPRequestHandler):
        def reply(self, code, body):
            data = json.dumps(body, ensure_ascii=False).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            if self.path == "/health":
                self.reply(200, {"status": "ready", **engine.metadata})
            elif self.path == "/voices":
                self.reply(200, {"voices": engine.voices})
            else:
                self.reply(404, {"error": "Not found"})

        def do_POST(self):
            # Not a browser API: reject cross-origin forms / fetches.
            if self.path != "/run":
                return self.reply(404, {"error": "Not found"})
            if self.headers.get("Origin") or self.headers.get_content_type() != "application/json":
                return self.reply(403, {"error": "Only non-browser JSON clients are accepted"})
            try:
                size = int(self.headers.get("Content-Length", "0"))
                if not 0 < size <= 65536:
                    raise ValueError("Invalid body length")
                body = json.loads(self.rfile.read(size))
                if not isinstance(body, dict):
                    raise ValueError("Expected object")
                self.reply(200, engine.run(body, allowed_root))
            except (ValueError, KeyError, TypeError):
                self.reply(400, {"error": "Invalid preset request or output path"})
            except Exception:
                LOG.exception("Preset synthesis failed")
                self.reply(500, {"error": "Synthesis failed; consult local worker log"})

    return Handler


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--allowed-root", type=Path, required=True)
    parser.add_argument("--cache-root", type=Path, required=True)
    parser.add_argument("--port", type=int, default=8770)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    args.cache_root.mkdir(parents=True, exist_ok=True)
    os.environ["HF_HOME"] = str(args.cache_root.resolve())
    os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
    engine = PresetEngine()
    LOG.info("GPU ready: %s", engine.metadata)
    HTTPServer(("127.0.0.1", args.port), handler_for(engine, args.allowed_root)).serve_forever()


if __name__ == "__main__":
    main()
