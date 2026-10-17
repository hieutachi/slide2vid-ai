"""Recheck a delivered demo independently; no listening/ASR/LLM quality claims."""

from __future__ import annotations

import argparse
import html
import json
import re
from fractions import Fraction
from pathlib import Path
from urllib.request import Request, urlopen

from slidevoice.core.cache import file_hash, write_json
from slidevoice.core.media import run_process
from slidevoice.report.captions import caption_diagnostics


def verify(root: Path, url: str | None = None, expected_slides: int = 3) -> None:
    job = root / "lesson"
    manifest = json.loads((job / "manifest.json").read_text(encoding="utf-8"))
    timeline = json.loads((job / "presentation_timeline.json").read_text(encoding="utf-8"))
    report = json.loads((job / "report.json").read_text(encoding="utf-8"))
    video = job / "video.mp4"
    probe = json.loads(
        run_process(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_format",
                "-show_streams",
                "-show_chapters",
                "-of",
                "json",
                str(video),
            ]
        )
    )
    run_process(
        [
            "ffmpeg",
            "-v",
            "error",
            "-xerror",
            "-nostdin",
            "-i",
            str(video),
            "-map",
            "0:v:0",
            "-map",
            "0:a:0",
            "-f",
            "null",
            "-",
        ],
        timeout=600,
    )
    assert manifest["plugins_used"]["compose"] in {"presenter@0.2.1", "presenter@0.3.0"}
    assert manifest["plugins_used"]["render"] == "powerpoint@0.2.2"
    assert len(probe["chapters"]) == len(manifest["slides"]) == expected_slides
    assert abs(float(probe["format"]["duration"]) - manifest["slides"][-1]["end"]) < 0.05
    assert report["audio"]["audible_signal"] and not report["silent_segments"]
    assert (job / "work/script/storyboard.html").is_file()
    assert "{{NOTICE}}" not in (root / "index.html").read_text(encoding="utf-8")
    caption_cues = None
    caption_quality = None
    if manifest["plugins_used"]["subtitle"].startswith("readable_subtitle@"):
        config = json.loads((job / "config.json").read_text(encoding="utf-8"))
        # Independently parse the exported VTT; do not call the writer under test.
        vtt = (job / "subtitles.vtt").read_text(encoding="utf-8")
        parsed = re.findall(
            r"(\d+:\d+:\d+\.\d+) --> (\d+:\d+:\d+\.\d+)\n(.*?)(?=\n\n|\Z)",
            vtt,
            re.DOTALL,
        )

        def seconds(value: str) -> float:
            hours, minutes, secs = value.split(":")
            return int(hours) * 3600 + int(minutes) * 60 + float(secs)

        cues = [
            (round(seconds(a), 3), round(seconds(b), 3), html.unescape(text))
            for a, b, text in parsed
        ]
        assert cues
        previous_end = 0.0
        for start, end, text in cues:
            assert previous_end <= start < end
            assert len(text.splitlines()) <= config["subtitle"]["max_lines"]
            assert all(
                len(line) <= config["subtitle"]["max_chars_per_line"] or len(line.split()) == 1
                for line in text.splitlines()
            )
            previous_end = end
        for slide in manifest["slides"]:
            for seg in slide["segments"]:
                if not seg["text"].strip():
                    continue
                start, end = round(seg["start"] * 1000) / 1000, round(seg["end"] * 1000) / 1000
                pages = [cue for cue in cues if cue[0] >= start and cue[1] <= end]
                assert pages and pages[0][0] == start and pages[-1][1] == end
                assert " ".join(page[2] for page in pages).split() == seg["text"].split()
        caption_cues = len(cues)
        caption_quality = caption_diagnostics(cues)
    if manifest["plugins_used"]["compose"] == "presenter@0.3.0":
        assert (
            json.loads(
                (job / "work/compose/presentation_timeline.json").read_text(encoding="utf-8")
            )
            == timeline
        )
        assert timeline["render_stats"]["final_video_stream_copy"]
        video_stream = next(
            stream for stream in probe["streams"] if stream["codec_type"] == "video"
        )
        fps = Fraction(video_stream["r_frame_rate"])
        assert int(video_stream["nb_frames"]) == round(manifest["slides"][-1]["end"] * fps)
    frames = []
    for slide, direction in zip(manifest["slides"], timeline["slides"], strict=True):
        for segment, beat in zip(slide["segments"], direction["beats"], strict=True):
            assert segment["start"] == beat["start"] and segment["end"] == beat["end"]
            if beat["effect"] == "none":
                continue
            assert beat["geometry_source"] == "powerpoint_text_line"
            assert not beat["visual_warnings"]
            assert beat["bounds"]["height"] < 0.15
            if beat["effect"] == "circle":
                assert beat["rendered_effect"] == "rounded_outline"
            screenshot = root / f"slide_{slide['index']:03}_{beat['effect']}.jpg"
            run_process(
                [
                    "ffmpeg",
                    "-v",
                    "error",
                    "-y",
                    "-ss",
                    str((beat["start"] + beat["end"]) / 2),
                    "-i",
                    str(video),
                    "-frames:v",
                    "1",
                    str(screenshot),
                ]
            )
            frames.append(
                {
                    "slide": slide["index"],
                    "effect": beat["rendered_effect"],
                    "target": beat["target_text"],
                    "frame": screenshot.name,
                }
            )
    range_passed = None
    if url:
        base = url.rstrip("/") + "/"
        for path in ("", "lesson/work/script/storyboard.html", "lesson/presentation_timeline.json"):
            with urlopen(base + path, timeout=5) as response:
                assert response.status == 200
        request = Request(base + "lesson/video.mp4", headers={"Range": "bytes=0-1023"})
        with urlopen(request, timeout=5) as response:
            assert response.status == 206
            assert response.headers["Content-Range"].startswith("bytes 0-1023/")
            assert len(response.read()) == 1024
        range_passed = True
    write_json(
        root / "validation.json",
        {
            "composer": manifest["plugins_used"]["compose"],
            "renderer": manifest["plugins_used"]["render"],
            "full_av_decode_passed": True,
            "timing_matches_segment_audio": True,
            "duration_seconds": float(probe["format"]["duration"]),
            "width": probe["streams"][0]["width"],
            "height": probe["streams"][0]["height"],
            "chapters": len(probe["chapters"]),
            "http_range_passed": range_passed,
            "readable_caption_cues_verified": caption_cues,
            "caption_quality": caption_quality,
            "caption_timing_basis": "estimated within sentence; not word alignment"
            if caption_cues
            else None,
            "effect_frames": frames,
            "audio": report["audio"],
            "human_listening_verified": False,
            "independent_asr_verified": False,
            "real_llm_evaluated": False,
            "academic_content_verified": False,
        },
    )
    sums = {
        p.relative_to(root).as_posix(): file_hash(p)
        for p in sorted(root.rglob("*"))
        if p.is_file() and p.name != "SHA256SUMS.json"
    }
    write_json(root / "SHA256SUMS.json", sums)
    assert all(file_hash(root / p) == digest for p, digest in sums.items())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--url")
    parser.add_argument("--expected-slides", type=int, default=3)
    args = parser.parse_args()
    verify(args.root.resolve(), args.url, args.expected_slides)
