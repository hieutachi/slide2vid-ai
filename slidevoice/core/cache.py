"""Content-addressed stage and sentence caches, with atomic checkpoints."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from slidevoice import __version__

from .config import reject_secrets
from .errors import InputInvalid
from .models import Project


def canonical_json(payload: Any) -> str:
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
        allow_nan=False,
    )


def stable_hash(payload: Any) -> str:
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def atomic_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent, prefix=".sv-", suffix=".tmp", delete=False
        ) as stream:
            temporary = Path(stream.name)
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        for attempt in range(6):
            try:
                temporary.replace(path)
                break
            except PermissionError:
                # Windows readers/antivirus can briefly deny replacement. Never
                # truncate the old checkpoint; fail after a small bounded wait.
                if os.name != "nt" or attempt == 5:
                    raise
                time.sleep(0.01 * 2**attempt)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def write_json(path: Path, value: Any) -> None:
    reject_secrets(value)
    atomic_text(path, json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False))


def project_paths(project: Project) -> list[Path]:
    paths = [project.source_slides, project.source_voice]
    if project.voice:
        paths.append(project.voice.ref_audio)
    for slide in project.slides:
        if slide.image_path:
            paths.append(slide.image_path)
        paths.extend(s.audio_path for s in slide.segments if s.audio_path)
    return paths


class StageCache:
    """Project snapshots plus artifact hashes detect deleted or corrupt outputs."""

    def __init__(self, workdir: Path) -> None:
        self.workdir = workdir

    def key(
        self,
        project: Project,
        config: dict[str, Any],
        plugin: str,
        extra_files: list[Path] | None = None,
    ) -> str:
        data = project.model_dump(mode="json", exclude={"stage_status"})
        paths = project_paths(project) + (extra_files or [])
        hashes = {str(p): file_hash(self.workdir / p) for p in paths}
        return stable_hash({"input": data, "files": hashes, "config": config, "plugin": plugin})

    def load(self, stage: str, key: str) -> Project | None:
        try:
            record = json.loads(
                (self.workdir / "work" / stage / "cache.json").read_text(encoding="utf-8")
            )
            if record["key"] != key:
                return None
            if record["slidevoice_version"] != __version__:
                return None
            project = Project.model_validate(record["project"])
            reject_secrets(record["project"])
            for path in project_paths(project):
                resolved = (self.workdir / path).resolve()
                if path.is_absolute() or not resolved.is_relative_to(self.workdir.resolve()):
                    return None
                if str(path) not in record["artifacts"]:
                    return None
            for path, digest in record["artifacts"].items():
                artifact = (self.workdir / path).resolve()
                if Path(path).is_absolute() or not artifact.is_relative_to(self.workdir.resolve()):
                    return None
                if file_hash(artifact) != digest:
                    return None
            return project
        except (OSError, ValueError, KeyError, TypeError, AttributeError, InputInvalid):
            return None

    def save(self, stage: str, key: str, project: Project, artifacts: list[Path]) -> None:
        paths = set(artifacts) | {self.workdir / p for p in project_paths(project)}
        write_json(
            self.workdir / "work" / stage / "cache.json",
            {
                "key": key,
                "saved_at": datetime.now(UTC).isoformat(),
                "slidevoice_version": __version__,
                "project": project.model_dump(mode="json"),
                "artifacts": {str(p.relative_to(self.workdir)): file_hash(p) for p in paths},
            },
        )


class SegmentRecord(BaseModel):
    hash: str
    transcript_hash: str
    cer: float = Field(ge=0, allow_inf_nan=False)
    attempts: int = Field(ge=1, strict=True)


class SegmentCache:
    """Sentence metadata is reusable only with intact PCM and transcript artifacts.

    The orchestrator must enforce consent BEFORE calling this cache.
    """

    def __init__(self, folder: Path) -> None:
        self.folder = folder
        folder.mkdir(parents=True, exist_ok=True)

    def load(self, key: str) -> SegmentRecord | None:
        audio = self.folder / f"{key}.wav"
        try:
            record = SegmentRecord.model_validate_json(
                (self.folder / f"{key}.json").read_text(encoding="utf-8")
            )
            if (
                file_hash(audio) != record.hash
                or file_hash(audio.with_suffix(".txt")) != record.transcript_hash
            ):
                return None
            return record
        except (OSError, ValueError, TypeError):
            return None

    def save(self, key: str, cer: float, attempts: int) -> None:
        audio = self.folder / f"{key}.wav"
        record = SegmentRecord(
            hash=file_hash(audio),
            transcript_hash=file_hash(audio.with_suffix(".txt")),
            cer=cer,
            attempts=attempts,
        )
        write_json(self.folder / f"{key}.json", record.model_dump())
