import json
import re
import subprocess
from fractions import Fraction
from itertools import pairwise

import pytest

from slidevoice.core.cache import file_hash
from slidevoice.core.errors import InputInvalid
from slidevoice.core.media import run_process
from slidevoice.core.pipeline import Pipeline
from slidevoice.core.presentation import plan_path
from slidevoice.plugins.compose.presenter import (
    PresenterStyle,
    annotation_filter,
    ellipse_png,
    rounded_outline_png,
    zoom_filter,
)
from slidevoice.plugins.llm import FakeLLM
from tests.unit.test_lecture import response_for


def pixel(job, time, x, y):
    pixels = subprocess.run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-ss",
            str(time),
            "-i",
            str(job / "video.mp4"),
            "-frames:v",
            "1",
            "-pix_fmt",
            "rgb24",
            "-f",
            "rawvideo",
            "-",
        ],
        capture_output=True,
        check=True,
    ).stdout
    offset = (y * 640 + x) * 3
    return tuple(pixels[offset : offset + 3])


def test_presenter_decodes_effect_pixels_audio_timing_and_resume(job, monkeypatch):
    monkeypatch.setattr(
        FakeLLM, "complete_json", lambda self, system, user, schema: response_for(user)
    )
    cfg = {
        "script": {"plugin": "lecture_script"},
        "compose": {"plugin": "presenter", "preset": "ultrafast"},
    }
    project = Pipeline(job, cfg).run(only_slide=1)
    slide = project.slides[0]
    timeline = json.loads((job / "presentation_timeline.json").read_text(encoding="utf-8"))
    assert [beat["effect"] for beat in timeline["slides"][0]["beats"]] == [
        "none",
        "highlight",
        "circle",
        "zoom",
    ]
    assert timeline["slides"][0]["beats"][1]["start"] == slide.segments[1].start
    beat = timeline["slides"][0]["beats"][2]
    assert beat["rendered_effect"] == "rounded_outline"
    x, y, _w, h = beat["annotation_bounds_px"]
    # Read decoded pixels on the padded outline's left edge, not only filter text.
    px, py = min(639, x + 3), min(359, y + h // 2)
    before = pixel(job, slide.segments[0].start + 0.4, px, py)
    during = pixel(job, slide.segments[2].start + 0.4, px, py)
    after = pixel(job, slide.segments[3].end + 0.3, px, py)
    assert during[0] > before[0] + 80
    assert during[1] > before[1] + 70
    assert abs(after[0] - before[0]) < 15
    run_process(
        ["ffmpeg", "-v", "error", "-xerror", "-i", str(job / "video.mp4"), "-f", "null", "-"]
    )
    resumed = Pipeline(job)
    resumed.run(only_slide=1)
    assert set(resumed.events.values()) == {"cache_hit"}
    # Export deletion re-composes, but does not regenerate the LLM narration.
    (job / "presentation_timeline.json").unlink()
    repaired = Pipeline(job)
    repaired.run(only_slide=1)
    assert repaired.events["script"] == "cache_hit"
    assert repaired.events["compose"] == "executed"
    assert json.loads((job / "report.json").read_text())["audio"]["audible_signal"]
    repaired_timeline = json.loads((job / "presentation_timeline.json").read_text(encoding="utf-8"))
    assert repaired_timeline["render_stats"]["slides_reused"] == 1
    assert repaired_timeline["render_stats"]["slides_encoded"] == 0


def test_slide_cache_selective_repair_and_stream_copy_multi_slide(job, monkeypatch):
    def response(self, system, user, schema):
        data = response_for(user)
        for beat in data["beats"]:
            beat["text"] += " Nội dung minh họa."
        return data

    monkeypatch.setattr(FakeLLM, "complete_json", response)
    cfg = {
        "script": {"plugin": "lecture_script"},
        "subtitle": {"plugin": "readable_subtitle"},
        "compose": {"plugin": "presenter", "preset": "ultrafast"},
    }
    project = Pipeline(job, cfg).run()
    clips = sorted((job / "work/compose").glob("present_*.mp4"))
    original = {p: (file_hash(p), p.stat().st_mtime_ns) for p in clips}
    # Caption edits must only remux; the slide video remains bit-identical.
    Pipeline(job, {"subtitle": {"max_chars_per_line": 24}}).run()
    assert all((file_hash(p), p.stat().st_mtime_ns) == original[p] for p in clips)
    stats = json.loads((job / "presentation_timeline.json").read_text(encoding="utf-8"))[
        "render_stats"
    ]
    assert stats["slides_reused"] == len(clips) == 3
    assert stats["final_video_stream_copy"]
    clips[1].write_bytes(b"damaged media")
    Pipeline(job).run()
    stats = json.loads((job / "presentation_timeline.json").read_text(encoding="utf-8"))[
        "render_stats"
    ]
    assert stats["slides_encoded"] == 1 and stats["slides_reused"] == 2
    assert clips[0].stat().st_mtime_ns == original[clips[0]][1]
    probe = json.loads(
        run_process(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_streams",
                "-show_format",
                "-of",
                "json",
                str(job / "video.mp4"),
            ]
        )
    )
    video = next(s for s in probe["streams"] if s["codec_type"] == "video")
    fps = Fraction(video["r_frame_rate"])
    assert fps == 15  # The job fixture uses configs/fake.yaml, not the lecture preset.
    assert int(video["nb_frames"]) == round(project.slides[-1].end * fps)
    assert abs(float(probe["format"]["duration"]) - project.slides[-1].end) < 1 / fps

    # Container conversion changes start codes and inserts parameter sets. Compare
    # coded H.264 slices (NAL types 1/5) to prove the picture was not re-encoded.
    def coded_slices(path):
        stream = subprocess.run(
            [
                "ffmpeg",
                "-v",
                "error",
                "-i",
                str(path),
                "-map",
                "0:v:0",
                "-c:v",
                "copy",
                "-bsf:v",
                "h264_mp4toannexb",
                "-f",
                "h264",
                "-",
            ],
            capture_output=True,
            check=True,
        ).stdout
        return [
            nal for nal in re.split(b"\x00\x00\x00?\x01", stream) if nal and nal[0] & 31 in {1, 5}
        ]

    assert coded_slices(job / "video.mp4") == [nal for clip in clips for nal in coded_slices(clip)]
    assert (job / "work/compose/presentation_timeline.json").is_file()
    resumed = Pipeline(job)
    resumed.run()
    assert set(resumed.events.values()) == {"cache_hit"}
    # Encoder settings invalidate every clip, even when narration is unchanged.
    Pipeline(job, {"compose": {"crf": 25}}).run()
    stats = json.loads((job / "presentation_timeline.json").read_text(encoding="utf-8"))[
        "render_stats"
    ]
    assert stats["slides_encoded"] == 3 and stats["slides_reused"] == 0
    run_process(
        ["ffmpeg", "-v", "error", "-xerror", "-i", str(job / "video.mp4"), "-f", "null", "-"]
    )


def test_presenter_rejects_missing_plan(job):
    Pipeline(job).run(until="avatar")
    with pytest.raises(InputInvalid):
        Pipeline(job, {"compose": {"plugin": "presenter"}}).run(from_stage="compose")
    assert not plan_path(job, 1).exists()


def test_wide_ellipse_stroke_is_even_and_not_clipped(tmp_path):
    image = tmp_path / "ellipse.png"
    width, height, stroke = 400, 80, 4
    ellipse_png(image, width, height, stroke)
    rgba = subprocess.run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-i",
            str(image),
            "-frames:v",
            "1",
            "-pix_fmt",
            "rgba",
            "-f",
            "rawvideo",
            "-",
        ],
        capture_output=True,
        check=True,
    ).stdout

    def alpha(x, y):
        return rgba[(y * width + x) * 4 + 3]

    left = sum(alpha(x, height // 2) >= 128 for x in range(width // 2))
    top = sum(alpha(width // 2, y) >= 128 for y in range(height // 2))
    assert abs(left - stroke) <= 1
    assert abs(top - stroke) <= 1
    assert alpha(0, height // 2) == alpha(width - 1, height // 2) == 0


def test_rounded_outline_has_clear_interior_and_unclipped_stroke(tmp_path):
    image = tmp_path / "outline.png"
    width, height = 400, 60
    rounded_outline_png(image, width, height, 3)
    rgba = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(image), "-pix_fmt", "rgba", "-f", "rawvideo", "-"],
        capture_output=True,
        check=True,
    ).stdout

    def alpha(x, y):
        return rgba[(y * width + x) * 4 + 3]

    # A full text rectangle fits inside; unlike an ellipse, its corners stay clear.
    assert all(alpha(x, y) == 0 for y in range(8, height - 8) for x in range(8, width - 8))
    assert all(alpha(x, 0) == alpha(x, height - 1) == 0 for x in range(width))
    assert max(alpha(x, height // 2) for x in range(6)) == 255


def test_reduced_motion_uses_highlight_and_no_fade(job, monkeypatch):
    monkeypatch.setattr(
        FakeLLM, "complete_json", lambda self, system, user, schema: response_for(user)
    )
    Pipeline(
        job,
        {
            "script": {"plugin": "lecture_script"},
            "compose": {"plugin": "presenter", "reduced_motion": True, "preset": "ultrafast"},
        },
    ).run(only_slide=1)
    timeline = json.loads((job / "presentation_timeline.json").read_text(encoding="utf-8"))
    assert timeline["slides"][0]["beats"][3]["rendered_effect"] == "highlight"
    graph = (job / "work/compose/present_001.filters.txt").read_text()
    assert "zoompan" not in graph and "fade=" not in graph


def test_annotation_fade_decoded_alpha_stays_inside_beat():
    envelope, _ = annotation_filter(0.5, 1.5, PresenterStyle())
    pixels = subprocess.run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-f",
            "lavfi",
            "-i",
            "color=white:s=16x16:r=30:d=2",
            "-vf",
            envelope,
            "-frames:v",
            "60",
            "-pix_fmt",
            "rgba",
            "-f",
            "rawvideo",
            "-",
        ],
        capture_output=True,
        check=True,
    ).stdout
    alpha = [pixels[i * 16 * 16 * 4 + 3] for i in range(60)]
    assert alpha[0] == alpha[15] == alpha[45] == alpha[-1] == 0
    assert 0 < alpha[17] < alpha[19] < alpha[22] == 255
    assert 255 > alpha[42] > alpha[44] > 0


def test_smooth_zoom_decoded_frames_grow_gradually_and_return():
    width, height, fps = 320, 180, 30
    effect = zoom_filter(width, height, fps, (80, 50, 80, 60), 0.5, 2.5, PresenterStyle())
    pixels = subprocess.run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-f",
            "lavfi",
            "-i",
            "color=black:s=320x180:r=30:d=3,drawbox=x=80:y=50:w=80:h=60:color=white:t=fill",
            "-vf",
            effect,
            "-frames:v",
            "90",
            "-pix_fmt",
            "gray",
            "-f",
            "rawvideo",
            "-",
        ],
        capture_output=True,
        check=True,
    ).stdout
    assert len(pixels) == width * height * 90
    widths = []
    for frame in range(90):
        offset = (frame * height + 90) * width
        widths.append(sum(v > 128 for v in pixels[offset : offset + width]))
    assert widths[0] == widths[14] == widths[76] == widths[-1] == 80
    assert widths[45] >= 92
    assert max(abs(a - b) for a, b in pairwise(widths)) <= 3
