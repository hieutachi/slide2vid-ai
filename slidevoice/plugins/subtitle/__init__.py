"""Sentence captions and readable pages with estimated intra-sentence timing."""

import textwrap
from collections.abc import Iterator
from functools import cache
from pathlib import Path

from slidevoice.core.errors import InputInvalid
from slidevoice.core.interfaces import SubtitleWriter
from slidevoice.core.models import Project
from slidevoice.core.registry import register


def balanced_page(text: str, width: int, max_lines: int) -> str:
    """Balance an existing page without splitting tokens or increasing its height."""
    words = text.split()

    @cache
    def split(start: int, remaining: int) -> tuple[float, tuple[str, ...]]:
        if start == len(words):
            return 0.0, ()
        if remaining == 0:
            return float("inf"), ()
        best: tuple[float, tuple[str, ...]] = (float("inf"), ())
        for end in range(start + 1, len(words) + 1):
            line = " ".join(words[start:end])
            if len(line) > width and end > start + 1:
                break
            cost, tail = split(end, remaining - 1)
            # Equal-length lines are easier to scan. A modest preference for
            # punctuation keeps natural clauses together, but never beats width.
            penalty = (width - len(line)) ** 2
            if end < len(words) and line.endswith((",", ";", ":", ".", "?", "!")):
                penalty -= width
            candidate = (cost + penalty, (line, *tail))
            if candidate[0] < best[0]:
                best = candidate
        return best

    return "\n".join(split(0, max_lines)[1])


def caption_pages(text: str, width: int, max_lines: int) -> list[str]:
    """Distribute words across feasible pages instead of leaving a tiny final page."""
    words = text.split()
    if not words:
        return []

    def wrap(value: str) -> list[str]:
        return textwrap.wrap(value, width=width, break_long_words=False, break_on_hyphens=False)

    count = (len(wrap(" ".join(words))) + max_lines - 1) // max_lines
    target = len(" ".join(words)) / count

    @cache
    def partition(start: int, remaining: int) -> tuple[float, tuple[str, ...]]:
        if remaining == 0:
            return (0.0, ()) if start == len(words) else (float("inf"), ())
        best: tuple[float, tuple[str, ...]] = (float("inf"), ())
        for end in range(start + 1, len(words) - remaining + 2):
            page = " ".join(words[start:end])
            if len(wrap(page)) > max_lines:
                break
            cost, tail = partition(end, remaining - 1)
            penalty = (len(page) - target) ** 2
            if end < len(words) and page.endswith((",", ";", ":", ".", "?", "!")):
                penalty -= width / 2
            if cost + penalty < best[0]:
                best = cost + penalty, (page, *tail)
        return best

    return [balanced_page(page, width, max_lines) for page in partition(0, count)[1]]


def timestamp(seconds: float, separator: str = ",") -> str:
    value = round(seconds * 1000)
    hours, value = divmod(value, 3600000)
    minutes, value = divmod(value, 60000)
    secs, millis = divmod(value, 1000)
    return f"{hours:02}:{minutes:02}:{secs:02}{separator}{millis:03}"


@register("subtitle", "fake_subtitle")
class FakeSubtitle(SubtitleWriter):
    name = "fake_subtitle"

    def cues(self, project: Project) -> Iterator[tuple[float, float, str]]:
        for slide in project.slides:
            for seg in slide.segments:
                if seg.start is not None and seg.end is not None:
                    yield (
                        seg.start,
                        seg.end,
                        "\n".join(
                            textwrap.wrap(
                                seg.text, width=int(self.config.get("max_chars_per_line", 42))
                            )
                        ),
                    )

    def write(self, project: Project, out_dir: Path) -> dict[str, Path]:
        srt, vtt = [], ["WEBVTT\n"]
        ass = [
            "[Script Info]\nScriptType: v4.00+\nPlayResX: 640\nPlayResY: 360\n",
            "[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\nStyle: Default,Arial,22,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,1,0,2,15,15,20,1\n",
            "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n",
        ]
        for number, (start, end, raw) in enumerate(self.cues(project), 1):
            text = raw.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            srt.append(f"{number}\n{timestamp(start)} --> {timestamp(end)}\n{text}\n")
            vtt.append(f"{timestamp(start, '.')} --> {timestamp(end, '.')}\n{text}\n")
            ass_text = (
                raw.replace("\\", "\\\\")
                .replace("{", "\\{")
                .replace("}", "\\}")
                .replace("\n", r"\N")
            )
            ass.append(
                f"Dialogue: 0,{timestamp(start, '.')[:-1]},{timestamp(end, '.')[:-1]},Default,,0,0,0,,{ass_text}\n"
            )
        result = {}
        for extension, lines in (("srt", srt), ("vtt", vtt), ("ass", ass)):
            path = out_dir / f"subtitles.{extension}"
            path.write_text("\n".join(lines), encoding="utf-8")
            result[extension] = path.relative_to(self.workdir)
        return result


@register("subtitle", "readable_subtitle")
class ReadableSubtitle(FakeSubtitle):
    """Short caption pages; intra-sentence timing is estimated, NOT word alignment."""

    name = "readable_subtitle"
    version = "0.2.1"

    def cues(self, project: Project) -> Iterator[tuple[float, float, str]]:
        width = self.config.get("max_chars_per_line", 42)
        max_lines = self.config.get("max_lines", 2)
        if type(width) is not int or not 12 <= width <= 80:
            raise InputInvalid("Subtitle max_chars_per_line must be an integer from 12 to 80.")
        if type(max_lines) is not int or not 1 <= max_lines <= 3:
            raise InputInvalid("Subtitle max_lines must be an integer from 1 to 3.")
        for slide in project.slides:
            for seg in slide.segments:
                if seg.start is None or seg.end is None:
                    continue
                pages = caption_pages(seg.text, width, max_lines)
                if not pages:
                    continue
                start_ms, end_ms = round(seg.start * 1000), round(seg.end * 1000)
                if end_ms - start_ms < len(pages):
                    raise InputInvalid("Narration interval is too short for nonzero caption cues.")
                # Character-proportional estimates retain exact sentence boundaries
                # and never spill into pauses or the next segment.
                weights = [len(page.replace("\n", " ")) for page in pages]
                total, elapsed, cursor = sum(weights), 0, start_ms
                for i, (page, weight) in enumerate(zip(pages, weights, strict=True)):
                    elapsed += weight
                    boundary = min(
                        end_ms - (len(pages) - i - 1),
                        max(cursor + 1, start_ms + round((end_ms - start_ms) * elapsed / total)),
                    )
                    yield cursor / 1000, boundary / 1000, page
                    cursor = boundary
