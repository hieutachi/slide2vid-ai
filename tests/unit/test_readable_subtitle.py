from itertools import pairwise
from pathlib import Path

import pytest

from slidevoice.core.errors import InputInvalid
from slidevoice.core.models import Project, Segment, Slide
from slidevoice.plugins.subtitle import ReadableSubtitle, balanced_page, caption_pages
from slidevoice.report.captions import caption_diagnostics


def project_with(text, start=1.234, end=9.876):
    return Project(
        job_id="captions",
        source_slides=Path("slides.pptx"),
        source_voice=Path("voice.wav"),
        slides=[
            Slide(
                index=1,
                segments=[Segment(id="s1", text=text, spoken_text=text, start=start, end=end)],
            )
        ],
    )


def test_short_pages_preserve_words_boundaries_and_have_no_gaps(tmp_path):
    text = "Đây là ví dụ minh họa để người học dễ theo dõi nội dung bài giảng trên điện thoại. " * 5
    project = project_with(text)
    cues = list(
        ReadableSubtitle({"max_chars_per_line": 24, "max_lines": 2}, tmp_path).cues(project)
    )
    assert len(cues) > 5
    assert cues[0][0] == 1.234 and cues[-1][1] == 9.876
    assert all(start < end for start, end, _ in cues)
    assert all(left[1] == right[0] for left, right in pairwise(cues))
    assert all(len(page.splitlines()) <= 2 for _, _, page in cues)
    assert all(len(line) <= 24 for _, _, page in cues for line in page.splitlines())
    assert " ".join(page.replace("\n", " ") for _, _, page in cues).split() == text.split()


def test_all_subtitle_formats_escape_markup_and_share_cues(tmp_path):
    subtitle = ReadableSubtitle({"max_chars_per_line": 24}, tmp_path)
    project = project_with("A & B <script> ví dụ {test} " * 8)
    paths = subtitle.write(project, tmp_path)
    cues = list(subtitle.cues(project))
    srt = (tmp_path / paths["srt"]).read_text(encoding="utf-8")
    vtt = (tmp_path / paths["vtt"]).read_text(encoding="utf-8")
    ass = (tmp_path / paths["ass"]).read_text(encoding="utf-8")
    assert srt.count(" --> ") == vtt.count(" --> ") == ass.count("Dialogue:") == len(cues)
    assert "&amp;" in vtt and "&lt;script&gt;" in srt and "<script>" not in vtt
    assert r"\{test\}" in ass


@pytest.mark.parametrize(
    "settings",
    [
        {"max_lines": 0},
        {"max_lines": True},
        {"max_chars_per_line": 2},
        {"max_chars_per_line": "42"},
    ],
)
def test_invalid_caption_settings_rejected(tmp_path, settings):
    with pytest.raises(InputInvalid):
        list(ReadableSubtitle(settings, tmp_path).cues(project_with("Nội dung")))


def test_empty_untimed_and_tiny_intervals(tmp_path):
    writer = ReadableSubtitle({"max_chars_per_line": 12, "max_lines": 1}, tmp_path)
    assert list(writer.cues(project_with(""))) == []
    assert list(writer.cues(project_with("chưa có audio", start=None, end=None))) == []
    with pytest.raises(InputInvalid, match="too short"):
        list(writer.cues(project_with("nội dung rất dài " * 10, start=0, end=0.001)))


def test_balancing_avoids_short_orphan_and_keeps_tokens():
    text = "Trung bình dùng thông tin của mọi giá trị trong dãy số."
    page = balanced_page(text, 42, 2)
    lines = page.splitlines()
    assert len(lines) == 2 and abs(len(lines[0]) - len(lines[1])) < 15
    assert page.split() == text.split()
    assert balanced_page("x" * 90, 42, 2) == "x" * 90


def test_caption_diagnostics_disclose_fast_short_and_invalid_cues():
    report = caption_diagnostics([(0, 0.5, "x" * 42), (0.4, 0.4, "bad"), (1, 3, "a\nb")])
    assert report["over_20_characters_per_second"] == 1
    assert report["under_one_second"] == 2
    assert report["invalid_intervals"] == report["overlaps"] == 1
    assert report["max_lines"] == 2 and report["max_line_characters"] == 42
    assert caption_diagnostics([])["minimum_duration_seconds"] is None


def test_page_partition_removes_short_tail_without_changing_sentence_timing(tmp_path):
    text = "Một câu minh họa cần được chia đều giữa các trang để tránh phần đuôi quá ngắn nhé."
    pages = caption_pages(text, 24, 2)
    assert " ".join(pages).split() == text.split()
    lengths = [len(page.replace("\n", " ")) for page in pages]
    assert max(lengths) - min(lengths) < 15
    cues = list(ReadableSubtitle({"max_chars_per_line": 24}, tmp_path).cues(project_with(text)))
    assert min(end - start for start, end, _ in cues) > 2


@pytest.mark.parametrize("width,lines", [(12, 1), (24, 2), (42, 2), (80, 3)])
def test_partition_preserves_long_tokens_and_all_words(width, lines):
    text = "ví dụ " + "x" * 100 + " rồi kết thúc câu minh họa. " * 8
    pages = caption_pages(text, width, lines)
    assert " ".join(pages).split() == text.split()
    assert all(len(page.splitlines()) <= lines for page in pages)
    assert all(
        len(line) <= width or len(line.split()) == 1 for p in pages for line in p.splitlines()
    )
