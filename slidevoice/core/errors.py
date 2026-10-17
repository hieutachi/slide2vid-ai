"""Các lớp ngoại lệ chung (SPEC.md mục 4.3, quy tắc mục 7).

Mọi lỗi của SlideVoice đều kế thừa `SlideVoiceError` để CLI có thể bắt một chỗ và
in hướng dẫn khắc phục. `remedy` là BẮT BUỘC về mặt nội dung: lỗi phải nói rõ
người dùng cần làm gì tiếp theo (SPEC.md mục 7 — "hướng dẫn khắc phục cụ thể").
"""

from __future__ import annotations


class SlideVoiceError(Exception):
    """Lỗi gốc của SlideVoice.

    Args:
        message: mô tả lỗi, một dòng, không chứa secret.
        remedy: hướng dẫn khắc phục cụ thể (câu lệnh / config cần sửa).
    """

    def __init__(self, message: str, *, remedy: str = "") -> None:
        super().__init__(message)
        self.message = message
        self.remedy = remedy

    def __str__(self) -> str:
        if self.remedy:
            return f"{self.message}\n  → Khắc phục: {self.remedy}"
        return self.message


class PluginUnavailable(SlideVoiceError):
    """Plugin thiếu phụ thuộc, hoặc worker HTTP không phản hồi."""


class StageFailed(SlideVoiceError):
    """Một stage chạy được nhưng thất bại (dữ liệu hỏng, lệnh ngoài trả lỗi...)."""

    def __init__(self, message: str, *, remedy: str = "", stage: str = "") -> None:
        super().__init__(message, remedy=remedy)
        self.stage = stage


class InputInvalid(SlideVoiceError):
    """Đầu vào người dùng không hợp lệ: file không tồn tại, sai định dạng, config sai."""


class ConsentMissing(SlideVoiceError):
    """`project.voice_consent` chưa bật. KHÔNG có cờ nào bỏ qua được lỗi này."""
