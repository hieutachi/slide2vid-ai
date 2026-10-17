"""Persist local release checks and exit codes without relying on chat output.

Run from a checkout: python -m samples.validate_release --out out/release_checks
This does not publish packages, call paid APIs or rebuild the GPU demo.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    output = args.out.resolve()
    output.mkdir(parents=True, exist_ok=True)
    commands = {
        "ruff": [sys.executable, "-m", "ruff", "check", "."],
        "format": [sys.executable, "-m", "ruff", "format", "--check", "."],
        "mypy": [sys.executable, "-m", "mypy", "slidevoice"],
        "pytest": [sys.executable, "-m", "pytest", "-q", f"--junitxml={output / 'tests.xml'}"],
        "doctor": [sys.executable, "-m", "slidevoice", "doctor", "--json-output"],
    }
    report: dict[str, object] = {"started_at": datetime.now(UTC).isoformat(), "python": sys.version}
    results: dict[str, int] = {}
    for name, command in commands.items():
        with (
            (output / f"{name}.stdout.log").open("wb") as stdout,
            (output / f"{name}.stderr.log").open("wb") as stderr,
        ):
            try:
                result = subprocess.run(
                    command, cwd=root, stdout=stdout, stderr=stderr, timeout=600
                )
                results[name] = result.returncode
            except subprocess.TimeoutExpired:
                results[name] = 124
        (output / f"{name}.exit.txt").write_text(str(results[name]), encoding="utf-8")
    report.update(results=results, finished_at=datetime.now(UTC).isoformat())
    (output / "summary.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return int(any(results.values()))


if __name__ == "__main__":
    raise SystemExit(main())
