"""Sentence-synchronous, restrained lecture effects on actual slide images."""

from __future__ import annotations

import json
import math
import shutil
import struct
import zlib
from pathlib import Path

from pydantic import Field, StrictBool, StrictInt, ValidationError

from slidevoice.core.cache import file_hash, stable_hash, write_json
from slidevoice.core.errors import InputInvalid
from slidevoice.core.media import run_process
from slidevoice.core.models import Project
from slidevoice.core.presentation import PlanModel, Target, load_targets, save_timeline
from slidevoice.core.registry import register
from slidevoice.plugins.compose import FakeComposer


def write_rgba(path: Path, width: int, height: int, rows: bytearray) -> None:
    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data))

    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(bytes(rows)))
        + chunk(b"IEND", b"")
    )


def ellipse_png(path: Path, width: int, height: int, thickness: int) -> None:
    """Transparent gold annotation, no Pillow/runtime bitmap dependencies."""
    rows = bytearray()
    rx, ry = max(1, (width - thickness - 2) / 2), max(1, (height - thickness - 2) / 2)
    for y in range(height):
        rows.append(0)
        for x in range(width):
            dx, dy = x - (width - 1) / 2, y - (height - 1) / 2
            radius = math.sqrt((dx / rx) ** 2 + (dy / ry) ** 2)
            # Convert implicit ellipse distance to pixels using its local gradient.
            # Scaling by the minor radius makes a wide ellipse's ends far too thick.
            gradient = math.hypot(dx / (rx * rx), dy / (ry * ry)) / max(radius, 1e-12)
            distance = abs(radius - 1) / max(gradient, 1e-12)
            alpha = round(255 * max(0, min(1, thickness / 2 + 0.5 - distance)))
            rows.extend((255, 207, 64, alpha))

    write_rgba(path, width, height, rows)


def rounded_outline_png(path: Path, width: int, height: int, thickness: int) -> None:
    """Signed-distance rounded outline: transparent interior, no line through text."""
    rows = bytearray()
    inset = thickness / 2 + 1
    bx, by = max(1, (width - 1) / 2 - inset), max(1, (height - 1) / 2 - inset)
    radius = min(12, bx, by)
    for y in range(height):
        rows.append(0)
        for x in range(width):
            qx = abs(x - (width - 1) / 2) - bx + radius
            qy = abs(y - (height - 1) / 2) - by + radius
            distance = math.hypot(max(qx, 0), max(qy, 0)) + min(max(qx, qy), 0) - radius
            alpha = round(255 * max(0, min(1, thickness / 2 + 0.5 - abs(distance))))
            rows.extend((255, 207, 64, alpha))
    write_rgba(path, width, height, rows)


class PresenterStyle(PlanModel):
    reduced_motion: StrictBool = False
    zoom_max: float = Field(default=1.18, ge=1, le=1.3, allow_inf_nan=False)
    zoom_ramp_sec: float = Field(default=0.65, ge=0.15, le=2, allow_inf_nan=False)
    annotation_fade_sec: float = Field(default=0.18, ge=0, le=0.5, allow_inf_nan=False)
    zoom_min_sec: float = Field(default=1.2, ge=0.5, le=10, allow_inf_nan=False)
    max_zooms_per_slide: StrictInt = Field(default=1, ge=0, le=4)
    zoom_cooldown_sec: float = Field(default=2, ge=0, le=30, allow_inf_nan=False)


def highlight_png(path: Path, width: int, height: int, accent: int) -> None:
    """One small RGBA band so both background and accent fade together."""
    rows = bytearray()
    for _ in range(height):
        rows.append(0)
        for x in range(width):
            rows.extend((91, 207, 205, 255 if x < accent else 26))
    write_rgba(path, width, height, rows)


def annotation_filter(start: float, end: float, style: PresenterStyle) -> tuple[str, float]:
    fade = 0.0 if style.reduced_motion else min(style.annotation_fade_sec, (end - start) / 3)
    if fade <= 0:
        return "format=rgba", 0.0
    return (
        f"format=rgba,fade=t=in:st={start:.6f}:d={fade:.6f}:alpha=1,"
        f"fade=t=out:st={end - fade:.6f}:d={fade:.6f}:alpha=1",
        fade,
    )


def zoom_fallback(
    start: float, end: float, count: int, previous_end: float | None, style: PresenterStyle
) -> str | None:
    if style.reduced_motion:
        return "Reduced motion: zoom replaced with highlight."
    if end - start < style.zoom_min_sec:
        return "Short beat: highlight provides a more stable reading window."
    if count >= style.max_zooms_per_slide:
        return "Motion budget: zoom limit reached; use highlight."
    if previous_end is not None and start - previous_end < style.zoom_cooldown_sec:
        return "Motion budget: leave a breathing interval between zooms."
    return None


def clip_cache_hit(clip: Path, record: Path, key: str) -> bool:
    try:
        saved = json.loads(record.read_text(encoding="utf-8"))
        return bool(saved["key"] == key and saved["sha256"] == file_hash(clip))
    except (OSError, ValueError, KeyError, TypeError):
        return False


def zoom_filter(
    width: int,
    height: int,
    fps: int,
    bounds: tuple[int, int, int, int],
    start: float,
    end: float,
    style: PresenterStyle,
) -> str:
    x, y, w, h = bounds
    factor = min(style.zoom_max, width / w, height / h)
    ramp = min(style.zoom_ramp_sec, (end - start) / 2)
    # Ease both ends to the original full-slide frame; never a cut to/from a crop.
    phase = f"min(1,max(0,min((on/{fps}-{start:.6f})/{ramp:.6f},({end:.6f}-on/{fps})/{ramp:.6f})))"
    zoom = f"1+{factor - 1:.8f}*(1-cos(PI*({phase})))/2"
    return (
        f"zoompan=z='{zoom}':"
        f"x='max(0,min(iw-iw/zoom,{x + w / 2:.3f}-iw/zoom/2))':"
        f"y='max(0,min(ih-ih/zoom,{y + h / 2:.3f}-ih/zoom/2))':"
        f"d=1:s={width}x{height}:fps={fps}"
    )


def annotation_bounds(
    bounds: dict[str, float],
    width: int,
    height: int,
    vertical_padding: int | None = None,
) -> tuple[int, int, int, int]:
    x, y, w, h = pixel_bounds(bounds, width, height)
    px, py = max(6, round(width * 0.007)), max(4, round(height * 0.008))
    if vertical_padding is not None:
        py = vertical_padding
    right, bottom = min(width, x + w + px), min(height, y + h + py)
    x, y = max(0, x - px), max(0, y - py)
    return x, y, right - x, bottom - y


def text_clearance(target_id: str, targets: list[Target], height: int) -> float:
    """Minimum vertical gap to an overlapping native text line, in output pixels."""
    target = next(t for t in targets if t.id == target_id)
    a = target.bounds
    gaps = [float(height)]
    for other in targets:
        b = other.bounds
        if other.id == target.id or other.geometry_source != "powerpoint_text_line":
            continue
        if b.x >= a.x + a.width or a.x >= b.x + b.width:
            continue
        gaps.append(max(0, max(b.y - a.y - a.height, a.y - b.y - b.height)) * height)
    return min(gaps)


def pixel_bounds(bounds: dict[str, float], width: int, height: int) -> tuple[int, int, int, int]:
    x = min(width - 2, max(0, round(bounds["x"] * width)))
    y = min(height - 2, max(0, round(bounds["y"] * height)))
    w = max(2, min(width - x, round(bounds["width"] * width)))
    h = max(2, min(height - y, round(bounds["height"] * height)))
    return x, y, w, h


@register("compose", "presenter")
class PresenterComposer(FakeComposer):
    name = "presenter"
    version = "0.3.0"

    def compose(self, project: Project, subtitles: dict[str, Path], out_path: Path) -> Path:
        width, height = int(self.config["width"]), int(self.config["height"])
        fps = int(self.config.get("fps", 30))
        try:
            style = PresenterStyle.model_validate(
                {k: self.config[k] for k in PresenterStyle.model_fields if k in self.config}
            )
        except ValidationError:
            raise InputInvalid("Invalid presenter motion settings.") from None
        if not 0 <= int(self.config.get("max_effects_per_slide", 6)) <= 16:
            raise InputInvalid("max_effects_per_slide must be between zero and sixteen.")
        timeline_path = out_path.parent / "presentation_timeline.json"
        timeline = save_timeline(
            project, self.workdir, timeline_path, int(self.config.get("max_effects_per_slide", 6))
        )
        timeline["render_style"] = style.model_dump()
        timeline["render_stats"] = {
            "slides_encoded": 0,
            "slides_reused": 0,
            "final_video_stream_copy": True,
        }
        entries = ["ffconcat version 1.0"]
        for slide, direction in zip(project.slides, timeline["slides"], strict=True):
            targets = load_targets(self.workdir, slide.index)
            if slide.image_path is None or slide.start is None or slide.end is None:
                raise InputInvalid("Presenter requires slide images and synthesized timing.")
            image = (self.workdir / slide.image_path).resolve()
            if not image.is_relative_to(self.workdir.resolve()) or not image.is_file():
                raise InputInvalid("Presenter slide images must exist inside the job directory.")
            duration = slide.end - slide.start
            if duration <= 0:
                raise InputInvalid("Presenter slide durations must be positive.")
            # Exact global frame boundaries avoid cumulative drift on long lectures.
            frames = round(slide.end * fps) - round(slide.start * fps)
            if frames < 1:
                raise InputInvalid("Slide duration is shorter than one output frame.")
            clip = out_path.parent / f"present_{slide.index:03}.mp4"
            args = [
                "ffmpeg",
                "-v",
                "error",
                "-nostdin",
                "-y",
                "-loop",
                "1",
                "-framerate",
                str(fps),
                "-i",
                str(image),
            ]
            filters = [
                f"[0:v]scale={width}:{height}:force_original_aspect_ratio=decrease,"
                f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1,format=yuv420p[v0]"
            ]
            current = "v0"
            input_index = 1
            annotations = []
            zoom_count, last_zoom_end = 0, None
            for i, beat in enumerate(direction["beats"], 1):
                beat["rendered_effect"] = beat["effect"]
                beat["annotation_bounds_px"] = None
                beat["visual_warnings"] = []
                beat["annotation_fade_sec"] = 0.0
                if beat["effect"] == "none":
                    continue
                clearance = (
                    text_clearance(beat["target_id"], targets, height)
                    if beat["geometry_source"] == "powerpoint_text_line"
                    else float(height)
                )
                padding = min(max(4, round(height * 0.008)), max(0, int(clearance / 2) - 1))
                x, y, w, h = annotation_bounds(beat["bounds"], width, height, padding)
                beat["annotation_bounds_px"] = [x, y, w, h]
                if beat["geometry_source"] != "powerpoint_text_line":
                    beat["visual_warnings"].append("Coarse shape target; inspect placement.")
                origin = round(slide.start * fps) / fps
                start = max(0.0, float(beat["start"]) - origin)
                end = min(frames / fps, float(beat["end"]) - origin)
                enable = f"enable='gte(t,{start:.6f})*lt(t,{end:.6f})'"
                output = f"v{i}"
                if beat["effect"] == "zoom":
                    reason = zoom_fallback(start, end, zoom_count, last_zoom_end, style)
                    if reason:
                        beat["rendered_effect"] = "highlight"
                        beat["visual_warnings"].append(reason)
                if beat["effect"] == "circle" and clearance < 4:
                    beat["rendered_effect"] = "highlight"
                    beat["visual_warnings"].append(
                        "Crowded lines: use accent instead of crossing neighboring text."
                    )
                if beat["rendered_effect"] == "highlight" or beat["effect"] == "circle":
                    annotation = out_path.parent / f"annotation_{slide.index:03}_{i:02}.png"
                    if beat["rendered_effect"] == "highlight":
                        highlight_png(annotation, w, h, max(2, width // 400))
                    else:
                        text_target = beat["target_is_text"]
                        draw = rounded_outline_png if text_target else ellipse_png
                        beat["rendered_effect"] = "rounded_outline" if text_target else "ellipse"
                        draw(annotation, w, h, max(2, width // 480))
                    annotations.append(file_hash(annotation))
                    args.extend(["-loop", "1", "-framerate", str(fps), "-i", str(annotation)])
                    envelope, fade_sec = annotation_filter(start, end, style)
                    beat["annotation_fade_sec"] = fade_sec
                    filters.append(
                        f"[{input_index}:v]{envelope}[a{i}];"
                        f"[{current}][a{i}]overlay=x={x}:y={y}:{enable}[{output}]"
                    )
                    input_index += 1
                else:
                    filters.append(
                        f"[{current}]{zoom_filter(width, height, fps, (x, y, w, h), start, end, style)}[{output}]"
                    )
                    beat["rendered_effect"] = "smooth_zoom"
                    zoom_count += 1
                    last_zoom_end = end
                current = output
            # Short fade-up at slide changes, without moving any narration timestamps.
            if style.reduced_motion:
                filters.append(f"[{current}]null[out]")
            else:
                fade = min(0.15, duration / 4)
                filters.append(f"[{current}]fade=t=in:st=0:d={fade:.6f}[out]")
            graph = out_path.parent / f"present_{slide.index:03}.filters.txt"
            graph.write_text(";\n".join(filters), encoding="utf-8")
            key = stable_hash(
                {
                    "version": self.version,
                    "image": file_hash(image),
                    "annotations": annotations,
                    "graph": filters,
                    "frames": frames,
                    "fps": fps,
                    "preset": self.config.get("preset", "fast"),
                    "crf": self.config.get("crf", 20),
                }
            )
            record = clip.with_suffix(".clip.json")
            reused = clip_cache_hit(clip, record, key)
            temporary = clip.with_suffix(".partial.mp4")
            if not reused:
                run_process(
                    [
                        *args,
                        "-filter_complex_script",
                        str(graph),
                        "-map",
                        "[out]",
                        "-an",
                        "-frames:v",
                        str(frames),
                        "-r",
                        str(fps),
                        "-c:v",
                        "libx264",
                        "-preset",
                        str(self.config.get("preset", "fast")),
                        "-crf",
                        str(self.config.get("crf", 20)),
                        "-pix_fmt",
                        "yuv420p",
                        str(temporary),
                    ],
                    timeout=float(self.config.get("timeout_sec", 3600)),
                )
                temporary.replace(clip)
                write_json(record, {"key": key, "sha256": file_hash(clip)})
            timeline["render_stats"]["slides_reused" if reused else "slides_encoded"] += 1
            quoted = clip.resolve().as_posix().replace("'", "'\\''")
            entries.append(f"file '{quoted}'")
        self._clip_list = out_path.parent / "presenter.ffconcat"
        self._clip_list.write_text("\n".join(entries) + "\n", encoding="utf-8")
        write_json(timeline_path, timeline)
        result = super().compose(project, subtitles, out_path)
        shutil.copyfile(timeline_path, self.workdir / "presentation_timeline.json")
        return result

    def video_input(self, duration: float, width: int, height: int) -> list[str]:
        return ["-f", "concat", "-safe", "0", "-i", str(self._clip_list)]

    def video_encoding_args(self, width: int, height: int) -> list[str]:
        # All clips already have identical H.264 format, geometry and frame rate.
        # Remux video, encode/mix audio once; never degrade text with a second encode.
        return ["-c:v", "copy"]
