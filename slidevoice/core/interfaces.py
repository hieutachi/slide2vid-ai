"""Interface của mọi plugin (SPEC.md mục 4.2).

HỢP ĐỒNG: chữ ký hàm và kiểu trả về ở đây do thẻ M0 viết theo SPEC.md mục 4.2;
các thẻ M1-M8 chỉ implement, KHÔNG được sửa.

Sai lệch có chủ đích so với khung trong SPEC.md (chỉ ở phần THÂN, không đổi chữ ký):
- `Plugin.__init__` lưu `config`, `workdir` và tạo logger dùng chung, để mọi plugin
  không phải lặp lại ba dòng này.
- `-> None` thêm vào `__init__` để `mypy --strict` (mục 7) sạch cảnh báo.
- `Word` được import thật (SPEC.md ghi `list["Word"]` dạng forward-ref chưa import).
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from pathlib import Path

from .models import Project, Segment, Slide, VoiceProfile, Word  # noqa: F401  (hợp đồng mục 4.2)


class Plugin(ABC):
    name: str = ""
    version: str = "0.1.0"

    def __init__(self, config: dict, workdir: Path) -> None:
        self.config: dict = dict(config or {})
        self.workdir = Path(workdir)
        self.workdir.mkdir(parents=True, exist_ok=True)
        self.log = logging.getLogger(
            f"slidevoice.plugin.{self.name or type(self).__name__}".lower()
        )

    def healthcheck(self) -> None:
        """raise PluginUnavailable nếu thiếu phụ thuộc/worker (mặc định: luôn OK)."""


class SlideRenderer(Plugin):  # slide -> ảnh + text + notes
    @abstractmethod
    def render(self, project: Project, out_dir: Path, width: int, height: int) -> list[Slide]: ...


class VoicePreparer(Plugin):  # file giọng thô -> VoiceProfile
    @abstractmethod
    def prepare(self, raw_audio: Path, language: str, out_dir: Path) -> VoiceProfile: ...


class LLMProvider(Plugin):  # gọi mô hình ngôn ngữ, trả JSON đúng schema
    @abstractmethod
    def complete_json(self, system: str, user: str, schema: dict) -> dict: ...


class ScriptWriter(Plugin):  # notes -> lời đọc tự nhiên, chia câu
    @abstractmethod
    def write(self, slide: Slide, deck_context: str, llm: LLMProvider | None) -> Slide: ...


class TextNormalizer(Plugin):  # "2026" -> "hai nghìn không trăm hai mươi sáu"
    @abstractmethod
    def normalize(self, text: str, language: str) -> str: ...


class TTSEngine(Plugin):  # giọng nhân bản
    @abstractmethod
    def load_voice(self, voice: VoiceProfile) -> None: ...

    @abstractmethod
    def synthesize(self, text: str, out_path: Path, speed: float = 1.0) -> float:
        """Tổng hợp một câu, trả về độ dài audio thật (giây)."""
        ...


class Aligner(Plugin):  # ASR kiểm tra + căn chỉnh từng từ
    @abstractmethod
    def transcribe(self, audio: Path, language: str) -> str: ...

    @abstractmethod
    def align(self, audio: Path, text: str, language: str) -> list[Word]: ...


class SubtitleWriter(Plugin):
    @abstractmethod
    def write(self, project: Project, out_dir: Path) -> dict[str, Path]:
        """Trả về {"srt": ..., "vtt": ..., "ass": ...}."""
        ...


class AvatarRenderer(Plugin):  # tùy chọn: người dẫn nói khớp khẩu hình
    @abstractmethod
    def render(self, face_image: Path, audio: Path, out_path: Path) -> Path: ...


class Composer(Plugin):  # ghép ảnh + audio + phụ đề + chương + metadata
    @abstractmethod
    def compose(self, project: Project, subtitles: dict[str, Path], out_path: Path) -> Path: ...
