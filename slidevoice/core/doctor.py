"""Machine-readable preflight; reports capability, never production certification."""

from __future__ import annotations

import platform
import shutil
import tempfile
from pathlib import Path
from typing import Any

from slidevoice import __version__

from . import registry
from .config import STAGES
from .errors import SlideVoiceError
from .media import run_process


def diagnose(config: dict[str, Any] | None = None) -> dict[str, Any]:
    checks: list[dict[str, str]] = []

    def record(name: str, status: str, detail: str) -> None:
        checks.append({"name": name, "status": status, "detail": detail})

    for executable in ("ffmpeg", "ffprobe"):
        if shutil.which(executable) is None:
            record(executable, "failed", "Install this executable and add it to PATH.")
            continue
        try:
            version = run_process([executable, "-version"], timeout=10).splitlines()[0]
            record(executable, "passed", version)
            if executable == "ffmpeg":
                encoders = run_process([executable, "-hide_banner", "-encoders"], timeout=10)
                filters = run_process([executable, "-hide_banner", "-filters"], timeout=10)
                for codec in ("libx264", "aac", "mov_text"):
                    record(f"encoder.{codec}", "passed" if codec in encoders else "failed", codec)
                for name in ("loudnorm", "drawbox", "scale"):
                    record(f"filter.{name}", "passed" if name in filters else "failed", name)
        except (SlideVoiceError, IndexError):
            record(executable, "failed", "Executable did not complete a valid capability probe.")

    if config is not None:
        with tempfile.TemporaryDirectory() as directory:
            for kind in (*STAGES, "llm"):
                name = str(config[kind]["plugin"])
                try:
                    registry.create(kind, name, config[kind], Path(directory))
                    record(f"plugin.{kind}", "passed", name)
                except Exception:
                    # Plugin/provider exceptions can include credentials, URLs or prompts.
                    record(
                        f"plugin.{kind}",
                        "failed",
                        "Unavailable; check the selected plugin and its prerequisites.",
                    )
                if name.startswith("fake_"):
                    record(
                        f"quality.{kind}",
                        "warning",
                        "Synthetic fixture, not real speech/graphics/ASR quality evidence.",
                    )
                if name == "powerpoint":
                    record(
                        "deployment.powerpoint",
                        "warning",
                        "Windows desktop Office automation; not a supported Linux/container renderer.",
                    )
    record(
        "scope",
        "warning",
        "Preflight is not a security audit, human listening test or production approval.",
    )
    return {
        "schema_version": 1,
        "slidevoice_version": __version__,
        "python": platform.python_version(),
        "platform": platform.system(),
        "ok": all(item["status"] != "failed" for item in checks),
        "checks": checks,
    }
