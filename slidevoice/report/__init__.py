"""Human-readable package and honest synthetic QA report."""

import html
import json
import shutil
from pathlib import Path
from typing import Any

from slidevoice.core.cache import atomic_text, write_json
from slidevoice.core.errors import StageFailed
from slidevoice.core.media import measure_audio
from slidevoice.core.models import Project


def chapter_time(seconds: float) -> str:
    minutes, secs = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02}:{minutes:02}:{secs:02}" if hours else f"{minutes:02}:{secs:02}"


def write_package(
    project: Project, root: Path, events: dict[str, str], durations: dict[str, float] | None = None
) -> None:
    outputs = json.loads((root / "work/subtitle/outputs.json").read_text(encoding="utf-8"))
    for ext in ("srt", "vtt", "ass"):
        shutil.copyfile(root / outputs[ext], root / f"subtitles.{ext}")
    chapters = [
        f"{chapter_time(s.start or 0)} {s.title or f'Slide {s.index}'}" for s in project.slides
    ]
    atomic_text(root / "chapters.txt", "\n".join(chapters) + "\n")
    transcript = [
        f"# {project.meta.title}",
        "",
        "> AI-generated voice — synthetic M0 demonstration.",
        "",
    ]
    for slide in project.slides:
        transcript.extend(
            [f"## {chapter_time(slide.start or 0)} — {slide.title}", "", slide.script, ""]
        )
    atomic_text(root / "transcript.md", "\n".join(transcript))
    segments = [seg for s in project.slides for seg in s.segments]
    errors = [seg.cer for seg in segments if seg.cer is not None]
    audio = measure_audio(root / "video.mp4")
    segment_audio = {
        seg.id: measure_audio(root / seg.audio_path) if seg.audio_path else None for seg in segments
    }
    silent_segments = [
        seg_id
        for seg_id, levels in segment_audio.items()
        if levels is None or not levels["audible_signal"]
    ]
    audio_ok = (bool(audio["audible_signal"]) or not segments) and not silent_segments
    report: dict[str, Any] = {
        "job_id": project.job_id,
        "synthetic": True,
        "human_listening_verified": False,
        "independent_asr_verified": False,
        "academic_content_verified": False,
        "notice": "M0 alignment checks sidecars, not speech. CER is not real ASR quality. Audio levels are measured from the decoded final MP4; no human listening is claimed.",
        "mean_cer": sum(errors) / len(errors) if errors else None,
        "lufs": audio["integrated_lufs"],
        "audio": audio,
        "silent_segments": silent_segments,
        "qa_status": "passed" if audio_ok else "failed",
        "stage_seconds": durations or {},
        "warnings": project.warnings,
        "stages": events,
        "segments": [
            {"id": s.id, "cer": s.cer, "attempts": s.attempts, "audio": segment_audio[s.id]}
            for s in segments
        ],
    }
    if "lecture_script@" in project.plugins_used.get("script", ""):
        report["presentation"] = {
            "script": (
                "Hand-authored demo fixture; no real LLM API call; instructor review required"
                if project.plugins_used.get("llm", "").split("@")[0]
                in {"lecture_demo_fixture", "lecture_long_fixture"}
                else "LLM-generated lecture; instructor review required"
            ),
            "llm_provider": project.plugins_used.get("llm"),
            "storyboard": "work/script/storyboard.md",
            "visual_storyboard": "work/script/storyboard.html",
            "timeline": "presentation_timeline.json",
            "timing": "sentence audio boundaries, not independently aligned words",
            "external_research_performed": False,
        }
    write_json(root / "report.json", report)
    atomic_text(
        root / "report.html",
        "<!doctype html><meta charset='utf-8'><title>SlideVoice M0 QA</title>"
        "<h1>Synthetic M0 QA</h1><pre>"
        + html.escape(json.dumps(report, ensure_ascii=False, indent=2))
        + "</pre>",
    )
    if not audio_ok:
        raise StageFailed(
            "Final video or a narration segment has no sufficiently audible audio signal.",
            remedy="Inspect report.json, TTS warnings and sentence WAVs; fix synthesis before handing off the video.",
            stage="compose",
        )
