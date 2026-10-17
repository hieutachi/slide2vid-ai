"""Mô hình dữ liệu dùng chung giữa các stage (SPEC.md mục 4.1).

HỢP ĐỒNG: file này do thẻ M0 viết theo SPEC.md mục 4.1. Các thẻ sau CHỈ được đọc,
không được sửa. Dữ liệu giữa các stage chỉ đi qua các model ở đây (nguyên tắc 6, mục 2).

Ghi chú triển khai (không đổi chữ ký/trường nào):
- `Field(default_factory=...)` được dùng cho các default khả biến (list/dict) — đây là
  dạng chuẩn của pydantic, ngữ nghĩa giống hệt `= []` / `= {}` trong SPEC.md.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field


class Word(BaseModel):
    text: str
    start: float
    end: float
    score: float | None = None  # độ tin cậy căn chỉnh


class Segment(BaseModel):  # một câu đọc
    id: str  # "s003_02" = slide 3, câu 2
    text: str  # câu hiển thị trên phụ đề
    spoken_text: str  # câu đã chuẩn hóa để TTS đọc (số -> chữ...)
    audio_path: Path | None = None
    start: float | None = None  # mốc trong toàn video
    end: float | None = None
    words: list[Word] = Field(default_factory=list)
    cer: float | None = None  # lỗi đọc so với ASR kiểm tra lại
    attempts: int = 0


class Slide(BaseModel):
    index: int  # bắt đầu từ 1
    title: str = ""
    body_text: str = ""
    notes_raw: str = ""
    image_path: Path | None = None
    hidden: bool = False
    script: str = ""  # lời đọc sau khi LLM xử lý
    script_source: Literal["notes", "llm_from_notes", "llm_from_slide", "empty"] = "empty"
    segments: list[Segment] = Field(default_factory=list)
    start: float | None = None
    end: float | None = None


class VoiceProfile(BaseModel):
    ref_audio: Path  # đoạn mẫu đã làm sạch, 24 kHz mono
    ref_text: str  # lời của đoạn mẫu (ASR), nhiều engine bắt buộc
    language: str  # "vi", "en"...
    extra: dict = Field(default_factory=dict)  # dữ liệu riêng của engine (embedding, speaker id)
    consent_confirmed: bool = False


class DeckMeta(BaseModel):
    title: str = ""
    author: str = ""
    language: str = "vi"
    created_at: str = ""


class Project(BaseModel):
    job_id: str
    source_slides: Path
    source_voice: Path
    meta: DeckMeta = Field(default_factory=DeckMeta)
    slides: list[Slide] = Field(default_factory=list)
    voice: VoiceProfile | None = None
    stage_status: dict[str, Literal["pending", "done", "failed", "skipped"]] = Field(
        default_factory=dict
    )
    plugins_used: dict[str, str] = Field(default_factory=dict)  # stage -> "tên_plugin@phiên_bản"
    warnings: list[str] = Field(default_factory=list)
