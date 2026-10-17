import json

import pytest
from pydantic import ValidationError

from slidevoice.core.errors import InputInvalid
from slidevoice.core.presentation import Target, extract_layout
from slidevoice.plugins.compose.presenter import (
    PresenterStyle,
    annotation_bounds,
    annotation_filter,
    clip_cache_hit,
    text_clearance,
    zoom_fallback,
    zoom_filter,
)


def test_native_line_targets_are_measured_and_keep_parent(job):
    source = job / "inputs/slides.pptx"
    parent = extract_layout(source)["1"][0]
    line = {
        "slide": 1,
        "target": {
            "id": parent["id"] + "_line_1",
            "parent_id": parent["id"],
            "text": "Measured line",
            "kind": "text_line",
            "is_text": True,
            "geometry_source": "powerpoint_text_line",
            "bounds": parent["bounds"],
        },
    }
    targets = extract_layout(source, [line])["1"]
    assert targets[-1]["parent_id"] == parent["id"]
    assert targets[-1]["geometry_source"] == "powerpoint_text_line"
    for invalid in (
        {**line["target"], "parent_id": "missing"},
        {**line["target"], "bounds": {"x": 0.9, "y": 0, "width": 0.5, "height": 0.1}},
        {**line["target"], "geometry_source": "pptx_shape"},
    ):
        with pytest.raises(InputInvalid, match="text-line"):
            extract_layout(source, [{"slide": 1, "target": invalid}])


@pytest.mark.parametrize(
    "bounds",
    [
        {"x": 0, "y": 0, "width": 0.1, "height": 0.1},
        {"x": 0.9, "y": 0.9, "width": 0.1, "height": 0.1},
        {"x": 0.3, "y": 0.4, "width": 0.3, "height": 0.1},
    ],
)
def test_annotation_padding_clamps_to_slide(bounds):
    x, y, w, h = annotation_bounds(bounds, 1280, 720)
    assert 0 <= x < x + w <= 1280
    assert 0 <= y < y + h <= 720
    assert x <= round(bounds["x"] * 1280)
    assert y <= round(bounds["y"] * 720)


@pytest.mark.parametrize(
    "settings",
    [
        {"zoom_max": 1.5},
        {"zoom_ramp_sec": 0},
        {"zoom_max": float("nan")},
        {"reduced_motion": "false"},
        {"annotation_fade_sec": -0.1},
        {"zoom_min_sec": 0},
        {"max_zooms_per_slide": True},
        {"zoom_cooldown_sec": -1},
    ],
)
def test_rejects_invalid_motion_settings(settings):
    with pytest.raises(ValidationError):
        PresenterStyle.model_validate(settings)


def test_zoom_expression_has_symmetric_ease_and_short_beat_support():
    graph = zoom_filter(640, 360, 30, (20, 30, 200, 40), 1, 1.2, PresenterStyle())
    assert "cos(PI" in graph and "on/30" in graph
    assert "/0.100000" in graph  # Short beats reduce both ramps instead of jumping.
    assert "1+0.18000000" in graph


def test_annotations_fade_inside_beat_and_disable_for_reduced_motion():
    graph, duration = annotation_filter(2, 2.3, PresenterStyle())
    assert duration == pytest.approx(0.1)
    assert "st=2.000000" in graph and "st=2.200000" in graph
    assert annotation_filter(2, 3, PresenterStyle(reduced_motion=True)) == ("format=rgba", 0)


def test_motion_budget_preserves_reading_time():
    style = PresenterStyle()
    assert zoom_fallback(0, 0.7, 0, None, style).startswith("Short beat")
    assert zoom_fallback(0, 4, 0, None, style) is None
    assert zoom_fallback(10, 14, 1, 4, style).startswith("Motion budget")
    assert zoom_fallback(4, 8, 1, 3, PresenterStyle(max_zooms_per_slide=2)).startswith(
        "Motion budget"
    )
    assert zoom_fallback(0, 4, 0, None, PresenterStyle(reduced_motion=True)).startswith(
        "Reduced motion"
    )


def test_slide_cache_rejects_stale_or_damaged_outputs(tmp_path):
    from slidevoice.core.cache import file_hash, write_json

    clip, record = tmp_path / "clip.mp4", tmp_path / "clip.clip.json"
    assert not clip_cache_hit(clip, record, "key")
    clip.write_bytes(b"encoded media")
    write_json(record, {"key": "key", "sha256": file_hash(clip)})
    assert clip_cache_hit(clip, record, "key")
    assert not clip_cache_hit(clip, record, "other")
    clip.write_bytes(b"damaged")
    assert not clip_cache_hit(clip, record, "key")
    record.write_text("[]", encoding="utf-8")
    assert not clip_cache_hit(clip, record, "key")


def test_crowded_text_lines_are_detected():
    def line(name, y):
        return Target(
            id=name,
            text=name,
            kind="text_line",
            geometry_source="powerpoint_text_line",
            bounds={"x": 0.1, "y": y, "width": 0.5, "height": 0.05},
        )

    assert text_clearance("a", [line("a", 0.2), line("b", 0.25)], 720) < 0.001
    assert text_clearance("a", [line("a", 0.2), line("b", 0.3)], 720) == pytest.approx(36)


def test_visual_storyboard_escapes_source_html(job, monkeypatch):
    from slidevoice.core.pipeline import Pipeline
    from slidevoice.plugins.llm import FakeLLM
    from slidevoice.report.storyboard import write_storyboard
    from tests.unit.test_lecture import response_for

    monkeypatch.setattr(
        FakeLLM, "complete_json", lambda self, system, user, schema: response_for(user)
    )
    project = Pipeline(job, {"script": {"plugin": "lecture_script"}}).run(until="script")
    path = job / "work/script/slide_001.plan.json"
    plan = json.loads(path.read_text(encoding="utf-8"))
    plan["beats"][0]["text"] = '<script>alert("source")</script>'
    path.write_text(json.dumps(plan), encoding="utf-8")
    write_storyboard(project, job, job / "work/script")
    page = (job / "work/script/storyboard.html").read_text(encoding="utf-8")
    assert "&lt;script&gt;alert(&quot;source&quot;)&lt;/script&gt;" in page
    assert '<script>alert("source")</script>' not in page
    assert 'src="../../work/render/slide_001.png"' in page
