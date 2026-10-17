"""Non-blocking OS locks for a single writer per job on local filesystems."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from types import TracebackType
from typing import BinaryIO

from .errors import InputInvalid


class JobLock:
    """The OS releases ownership on process exit, including crashes.

    Keep the lock file: deleting it can create a second inode and two owners.
    Shared NFS/SMB volumes are not a supported coordination mechanism.
    """

    def __init__(self, root: Path) -> None:
        self.path = root / ".slidevoice.lock"
        self.stream: BinaryIO | None = None

    def __enter__(self) -> JobLock:
        stream = self.path.open("a+b")
        try:
            stream.seek(0, os.SEEK_END)
            if stream.tell() == 0:
                stream.write(b"\0")
                stream.flush()
            stream.seek(0)
            if sys.platform == "win32":
                import msvcrt

                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl

                fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            stream.close()
            raise InputInvalid(
                "Job is busy or cannot be locked; no state was changed.",
                remedy="Wait for the other process to exit, then resume. Use a local writable filesystem.",
            ) from None
        self.stream = stream
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        if self.stream is not None:
            # close() releases the advisory lock on both platforms.
            self.stream.close()
            self.stream = None
