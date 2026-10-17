"""Bounded PPTX package inspection before Office/python-pptx parses it.

This is resource/format validation, NOT a document malware sandbox.
"""

from __future__ import annotations

import re
from pathlib import Path, PurePosixPath
from zipfile import BadZipFile, ZipFile

from pydantic import BaseModel, ConfigDict, Field

from .errors import InputInvalid


class InputLimits(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    max_file_bytes: int = Field(default=100 * 1024 * 1024, ge=1024)
    max_archive_bytes: int = Field(default=512 * 1024 * 1024, ge=1024)
    max_member_bytes: int = Field(default=64 * 1024 * 1024, ge=1024)
    max_members: int = Field(default=10000, ge=1)
    max_slides: int = Field(default=500, ge=1)
    max_compression_ratio: int = Field(default=1000, ge=1)


def check_file(path: Path, limits: InputLimits) -> None:
    try:
        if not path.is_file() or not 0 < path.stat().st_size <= limits.max_file_bytes:
            raise InputInvalid("Input must be a nonempty file within limits.max_file_bytes.")
    except OSError:
        raise InputInvalid("Cannot inspect input file; check its permissions.") from None


def inspect_pptx(path: Path, limits: InputLimits | None = None) -> dict[str, int]:
    limits = limits or InputLimits()
    check_file(path, limits)
    try:
        with ZipFile(path) as archive:
            members = archive.infolist()
            if not members or len(members) > limits.max_members:
                raise ValueError("Member count")
            names: set[str] = set()
            total = 0
            slides = 0
            for member in members:
                # ZipInfo.filename can normalize backslashes on Windows; inspect
                # the original central-directory name before any normalization.
                name = member.orig_filename
                parts = PurePosixPath(name).parts
                if (
                    not parts
                    or name.startswith("/")
                    or "\\" in name
                    or ":" in name
                    or ".." in parts
                    or member.flag_bits & 1
                    or name.casefold() in names
                ):
                    raise ValueError("Unsafe/ambiguous archive member")
                names.add(name.casefold())
                if member.file_size > limits.max_member_bytes or member.file_size > (
                    max(1, member.compress_size) * limits.max_compression_ratio
                ):
                    raise ValueError("Member size/ratio")
                total += member.file_size
                if total > limits.max_archive_bytes:
                    raise ValueError("Archive size")
                if re.fullmatch(r"ppt/slides/slide[0-9]+\.xml", name):
                    slides += 1
                lowered = name.casefold()
                if "vbaproject" in lowered or lowered.startswith(
                    ("ppt/activex/", "ppt/embeddings/")
                ):
                    raise ValueError("Active content")
            if not {"[content_types].xml", "ppt/presentation.xml"} <= names:
                raise ValueError("Not a presentation package")
            if not 1 <= slides <= limits.max_slides:
                raise ValueError("Slide count")
            return {"members": len(members), "slides": slides, "uncompressed_bytes": total}
    except (BadZipFile, OSError, ValueError, NotImplementedError):
        raise InputInvalid(
            "PPTX package is invalid, contains active/embedded content, or exceeds input limits.",
            remedy="Export a plain .pptx without macros/OLE/ActiveX; check the limits configuration.",
        ) from None
