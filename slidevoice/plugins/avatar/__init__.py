"""Disabled avatar interface. No fake talking face is produced."""

from pathlib import Path

from slidevoice.core.interfaces import AvatarRenderer
from slidevoice.core.registry import register


@register("avatar", "none")
class NoAvatar(AvatarRenderer):
    name = "none"

    def render(self, face_image: Path, audio: Path, out_path: Path) -> Path:
        return out_path
