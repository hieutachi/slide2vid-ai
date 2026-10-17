"""Offline build + clean installed-wheel smoke using the operator's uv cache."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tarfile
from pathlib import Path
from zipfile import ZipFile


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    env = out / "wheel-env"
    executable = env / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    results: dict[str, int] = {}

    def run(name: str, command: list[str], cwd: Path = out) -> None:
        with (
            (out / f"{name}.stdout.log").open("wb") as stdout,
            (out / f"{name}.stderr.log").open("wb") as stderr,
        ):
            result = subprocess.run(command, cwd=cwd, stdout=stdout, stderr=stderr, timeout=300)
        results[name] = result.returncode
        if result.returncode:
            raise RuntimeError(f"{name} failed; inspect its persisted log.")

    try:
        run("build", ["uv", "build", "--offline", "--out-dir", str(out / "dist")], root)
        wheels = list((out / "dist").glob("slidevoice-*.whl"))
        if len(wheels) != 1:
            raise RuntimeError("Use an output directory containing only this release version.")
        wheel = wheels[0]
        with ZipFile(wheel) as archive:
            names = archive.namelist()
            assert "slidevoice/configs/smoke.yaml" in names
            assert any(name.endswith("/licenses/LICENSE") for name in names)
            assert any(name.endswith("/licenses/THIRD_PARTY_NOTICES.md") for name in names)
            assert not any(
                name.startswith(("samples/", "workers/", "tests/", "out/")) for name in names
            )
        with tarfile.open(next((out / "dist").glob("slidevoice-*.tar.gz"))) as archive:
            names = archive.getnames()
            for required in (
                "DEPLOYMENT.md",
                "SECURITY.md",
                "tests/conftest.py",
                "samples/make_samples.py",
            ):
                assert any(name.endswith("/" + required) for name in names)
            assert not any("/.venv/" in name or "/out/" in name for name in names)
        results["distribution_contents"] = 0
        if not executable.is_file():
            run("venv", ["uv", "venv", str(env), "--python", sys.executable, "--offline"])
        run(
            "wheel_install",
            [
                "uv",
                "pip",
                "install",
                "--python",
                str(executable),
                str(wheel),
                "--offline",
                "--reinstall-package",
                "slidevoice",
            ],
        )
        run(
            "wheel_import", [str(executable), "-c", "import slidevoice; print(slidevoice.__file__)"]
        )
        imported = (out / "wheel_import.stdout.log").read_text(encoding="utf-8").strip()
        assert Path(imported).resolve().is_relative_to(env.resolve())
        run("wheel_doctor", [str(executable), "-m", "slidevoice", "doctor", "--json-output"])
        run(
            "wheel_smoke",
            [str(executable), "-m", "slidevoice", "smoke", "--out", str(out / "wheel_smoke")],
        )
        run(
            "wheel_resume",
            [str(executable), "-m", "slidevoice", "resume", str(out / "wheel_smoke")],
        )
        events = json.loads((out / "wheel_smoke/run_events.json").read_text(encoding="utf-8"))
        assert len(events) == 9 and set(events.values()) == {"cache_hit"}
        results["all_stages_cached"] = 0
    except (AssertionError, RuntimeError, OSError, StopIteration, subprocess.TimeoutExpired):
        results["validation_error"] = 1
    (out / "packaging_summary.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    return int(any(results.values()))


if __name__ == "__main__":
    raise SystemExit(main())
