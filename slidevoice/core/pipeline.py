"""M0 orchestration: checkpoints, consent gates, sentence cache and bounded QA retries."""

from __future__ import annotations

import json
import logging
import shutil
import time
from collections.abc import Callable
from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, TypeVar, cast
from uuid import uuid4

from . import registry
from .cache import SegmentCache, StageCache, atomic_text, file_hash, stable_hash, write_json
from .config import STAGES, merge, reject_secrets, validate
from .errors import ConsentMissing, InputInvalid, SlideVoiceError, StageFailed
from .inputs import InputLimits, check_file, inspect_pptx
from .interfaces import (
    Aligner,
    Composer,
    LLMProvider,
    Plugin,
    ScriptWriter,
    SlideRenderer,
    SubtitleWriter,
    TextNormalizer,
    TTSEngine,
    VoicePreparer,
)
from .locking import JobLock
from .media import wav_duration, write_tone
from .models import DeckMeta, Project

P = TypeVar("P", bound=Plugin)
log = logging.getLogger("slidevoice.pipeline")


def cer(reference: str, actual: str) -> float:
    """Unicode character edit distance divided by reference length."""
    reference, actual = reference.casefold().strip(), actual.casefold().strip()
    previous = list(range(len(actual) + 1))
    for i, left in enumerate(reference, 1):
        current = [i]
        for j, right in enumerate(actual, 1):
            current.append(min(current[-1] + 1, previous[j] + 1, previous[j - 1] + (left != right)))
        previous = current
    return previous[-1] / max(1, len(reference))


def checked_path(root: Path, value: Path) -> Path:
    resolved = (root / value).resolve()
    if value.is_absolute() or not resolved.is_relative_to(root.resolve()):
        raise InputInvalid("Model paths must be job-relative and stay inside the job directory.")
    return resolved


def validate_paths(project: Project, root: Path) -> None:
    reject_secrets(project.model_dump(mode="json"))
    paths = [project.source_slides, project.source_voice]
    if project.voice:
        paths.append(project.voice.ref_audio)
    for slide in project.slides:
        if slide.image_path:
            paths.append(slide.image_path)
        paths.extend(s.audio_path for s in slide.segments if s.audio_path)
    for path in paths:
        checked_path(root, path)


def create_job(slides: Path, voice: Path, out: Path, config: dict[str, Any]) -> Path:
    """Copy input assets once. Re-runs may refresh copies, never external sources."""
    config = validate(deepcopy(config))
    slides, voice, out = slides.resolve(), voice.resolve(), out.resolve()
    if not slides.is_file() or not voice.is_file():
        raise InputInvalid(
            "Slides and voice must be existing files.",
            remedy="Run samples/make_samples.py or provide valid input paths.",
        )
    if slides.is_relative_to(out) or voice.is_relative_to(out):
        raise InputInvalid("Input files must be outside the output job directory.")
    limits = InputLimits.model_validate(config["limits"])
    check_file(slides, limits)
    check_file(voice, limits)
    if slides.suffix.lower() == ".pptx":
        inspect_pptx(slides, limits)
    out.mkdir(parents=True, exist_ok=True)
    with JobLock(out):
        if (
            any(p.name != ".slidevoice.lock" for p in out.iterdir())
            and not (out / "initial.json").is_file()
        ):
            raise InputInvalid(
                "Output directory is not an existing SlideVoice job and is not empty."
            )
        return _create_job(slides, voice, out, config)


def _create_job(slides: Path, voice: Path, out: Path, config: dict[str, Any]) -> Path:
    (out / "inputs").mkdir(exist_ok=True)
    slide_copy = Path("inputs") / ("slides" + slides.suffix.lower())
    voice_copy = Path("inputs") / ("voice" + voice.suffix.lower())
    shutil.copyfile(slides, checked_path(out, slide_copy))
    shutil.copyfile(voice, checked_path(out, voice_copy))
    if (out / "initial.json").is_file():
        project = Project.model_validate_json((out / "initial.json").read_text(encoding="utf-8"))
        project.source_slides, project.source_voice = slide_copy, voice_copy
    else:
        project = Project(
            job_id="job_" + uuid4().hex[:12],
            source_slides=slide_copy,
            source_voice=voice_copy,
            meta=DeckMeta(created_at=datetime.now(UTC).isoformat()),
        )
    project.meta.title = config["project"]["title"]
    project.meta.author = config["project"]["author"]
    project.meta.language = config["project"]["language"]
    write_json(out / "initial.json", project.model_dump(mode="json"))
    write_json(out / "config.json", config)
    return out


class Pipeline:
    def __init__(self, job_dir: Path, config: dict[str, Any] | None = None) -> None:
        self.root = job_dir.resolve()
        self.overrides = deepcopy(config or {})
        self._load_state()
        self.cache = StageCache(self.root)
        self.events: dict[str, str] = {}
        self.durations: dict[str, float] = {}

    def _load_state(self) -> None:
        try:
            saved = json.loads((self.root / "config.json").read_text(encoding="utf-8"))
            self.config = validate(merge(saved, self.overrides))
            self.initial = Project.model_validate_json(
                (self.root / "initial.json").read_text(encoding="utf-8")
            )
        except (OSError, ValueError, TypeError):
            raise InputInvalid(
                "Cannot load job state.", remedy="Use run to create a job before resume."
            ) from None
        validate_paths(self.initial, self.root)

    def plugin(
        self, kind: str, expected: Callable[..., P], extra: dict[str, Any] | None = None
    ) -> P:
        cfg = merge(self.config[kind], extra or {})
        item = registry.create(kind, cfg["plugin"], cfg, self.root)
        if not isinstance(item, cast(type[P], expected)):
            raise InputInvalid(f"Plugin for {kind} does not implement its required interface.")
        return item

    def consent(self, project: Project) -> None:
        if self.config["project"]["voice_consent"] is not True:
            raise ConsentMissing(
                "project.voice_consent must be true before TTS, including cache hits.",
                remedy="Obtain explicit speaker permission and set project.voice_consent: true.",
            )
        if project.voice is None or not project.voice.consent_confirmed:
            raise ConsentMissing("Prepared voice does not carry confirmed consent.")

    def run(
        self, from_stage: str | None = None, until: str | None = None, only_slide: int | None = None
    ) -> Project:
        with JobLock(self.root):
            # Another process may have updated the job since this object was created.
            self._load_state()
            self.events.clear()
            self.durations.clear()
            started = datetime.now(UTC).isoformat()
            status: dict[str, Any] = {"status": "running", "started_at": started, "stage": None}
            write_json(self.root / "run_status.json", status)
            self._run_status = status
            try:
                project = self._run(from_stage, until, only_slide)
                status["status"] = "completed" if until in {None, "compose"} else "paused"
                return project
            except BaseException as exc:
                status["status"] = (
                    "interrupted" if isinstance(exc, (KeyboardInterrupt, SystemExit)) else "failed"
                )
                status["error_type"] = type(exc).__name__
                raise
            finally:
                status["finished_at"] = datetime.now(UTC).isoformat()
                write_json(self.root / "run_status.json", status)

    def _run(
        self, from_stage: str | None = None, until: str | None = None, only_slide: int | None = None
    ) -> Project:
        if (from_stage is not None and from_stage not in STAGES) or (
            until is not None and until not in STAGES
        ):
            raise InputInvalid("Unknown stage name.", remedy=f"Choose one of: {', '.join(STAGES)}")
        project = self.initial.model_copy(deep=True)
        project.meta.title = self.config["project"]["title"]
        project.meta.author = self.config["project"]["author"]
        project.meta.language = self.config["project"]["language"]
        if (until is None or STAGES.index(until) >= STAGES.index("tts")) and self.config["project"][
            "voice_consent"
        ] is not True:
            raise ConsentMissing(
                "project.voice_consent must be true before TTS, including resumed and cached jobs.",
                remedy="Obtain speaker consent and explicitly set project.voice_consent: true.",
            )
        write_json(self.root / "config.json", self.config)
        force = STAGES.index(from_stage) if from_stage else len(STAGES)
        for index, stage in enumerate(STAGES):
            self._run_status["stage"] = stage
            write_json(self.root / "run_status.json", self._run_status)
            started = time.perf_counter()
            folder = self.root / "work" / stage
            folder.mkdir(parents=True, exist_ok=True)
            try:
                validate_paths(project, self.root)
                if stage == "tts":
                    self.consent(
                        project
                    )  # Before stage lookup, cache lookup, load_voice, or synthesis.
                plugin_cls = registry.get_class(stage, self.config[stage]["plugin"])
                identity = f"{self.config[stage]['plugin']}@{plugin_cls.version}"
                # Dependency configs and all input content are fingerprinted conservatively.
                relevant = {
                    "stage": self.config[stage],
                    "timing": self.config["timing"],
                    "project": self.config["project"],
                    "only_slide": only_slide,
                }
                if stage == "render":
                    relevant["layout_version"] = 1
                    relevant["limits"] = self.config["limits"]
                if stage in {"tts", "align", "compose"}:
                    relevant["qa"] = self.config["qa"]
                if stage in {"tts", "align"}:
                    relevant["align"] = self.config["align"]
                    relevant["tts"] = self.config["tts"]
                    relevant["align_version"] = registry.get_class(
                        "align", self.config["align"]["plugin"]
                    ).version
                if stage == "compose":
                    relevant["render"] = self.config["render"]
                if stage == "script":
                    relevant["llm"] = self.config["llm"]
                    relevant["llm_version"] = registry.get_class(
                        "llm", self.config["llm"]["plugin"]
                    ).version
                extra_files = []
                if (
                    stage in {"script", "compose"}
                    and self.config["script"]["plugin"] == "lecture_script"
                ):
                    extra_files.append(Path("work/render/layout.json"))
                if stage == "compose" and self.config[stage]["plugin"] == "presenter":
                    extra_files.extend(
                        Path("work/script") / f"slide_{slide.index:03}.plan.json"
                        for slide in project.slides
                    )
                if stage == "compose":
                    mapping = self.root / "work/subtitle/outputs.json"
                    if mapping.is_file():
                        outputs = json.loads(mapping.read_text(encoding="utf-8"))
                        extra_files.append(Path("work/subtitle/outputs.json"))
                        extra_files.extend(Path(value) for value in outputs.values())
                        for path in extra_files:
                            checked_path(self.root, path)
                    else:
                        extra_files.extend(
                            Path("work/subtitle") / f"subtitles.{ext}"
                            for ext in ("srt", "vtt", "ass")
                        )
                    if self.config[stage]["plugin"] == "qa_video":
                        background = Path(
                            self.config[stage].get("background_path", "inputs/background.mp4")
                        )
                        checked_path(self.root, background)
                        extra_files.append(background)
                key = self.cache.key(project, relevant, identity, extra_files)
                cached = self.cache.load(stage, key) if index < force else None
                if from_stage and index < force and cached is None:
                    raise StageFailed(
                        f"Required checkpoint for {stage} is missing or stale.",
                        remedy=f"Run from {stage} or run without --from-stage.",
                    )
                if cached is not None:
                    validate_paths(cached, self.root)
                    project = cached
                    self.events[stage] = "cache_hit"
                else:
                    project = self.execute(stage, project, folder, only_slide)
                    self.events[stage] = "executed"
                if project.voice:
                    project.voice.consent_confirmed = (
                        self.config["project"]["voice_consent"] is True
                    )
                project.stage_status[stage] = (
                    "skipped"
                    if stage == "avatar" and self.config[stage]["plugin"] == "none"
                    else "done"
                )
                project.plugins_used[stage] = identity
                validate_paths(project, self.root)
                if cached is None:
                    artifacts = [
                        p for p in folder.rglob("*") if p.is_file() and p.name != "cache.json"
                    ]
                    if stage == "compose":
                        artifacts += [self.root / "video.mp4"]
                        if self.config[stage]["plugin"] == "presenter":
                            artifacts += [self.root / "presentation_timeline.json"]
                    if stage == "subtitle":
                        outputs = json.loads((folder / "outputs.json").read_text(encoding="utf-8"))
                        artifacts.extend(
                            checked_path(self.root, Path(value)) for value in outputs.values()
                        )
                    self.cache.save(stage, key, project, artifacts)
                write_json(self.root / "manifest.json", project.model_dump(mode="json"))
                self.durations[stage] = time.perf_counter() - started
                logging.getLogger(f"slidevoice.{stage}").info("%s: %s", stage, self.events[stage])
                if stage == until:
                    break
            except Exception as exc:
                project.stage_status[stage] = "failed"
                write_json(self.root / "manifest.json", project.model_dump(mode="json"))
                write_json(self.root / "run_events.json", self.events)
                if isinstance(exc, SlideVoiceError):
                    raise
                raise StageFailed(
                    f"Stage {stage} failed ({type(exc).__name__}).",
                    remedy="Check inputs and plugin settings, then resume the job.",
                    stage=stage,
                ) from None
        write_json(self.root / "run_events.json", self.events)
        if project.stage_status.get("compose") == "done":
            from slidevoice.report import write_package

            write_package(project, self.root, self.events, self.durations)
        return project

    def execute(
        self, stage: str, project: Project, folder: Path, only_slide: int | None
    ) -> Project:
        cfg = self.config
        if stage == "render":
            source = checked_path(self.root, project.source_slides)
            if source.suffix.lower() == ".pptx":
                inspect_pptx(source, InputLimits.model_validate(cfg["limits"]))
            renderer = self.plugin(stage, SlideRenderer, {"input_limits": cfg["limits"]})
            project.slides = renderer.render(
                project, folder, cfg[stage]["width"], cfg[stage]["height"]
            )
            project.slides = [
                s
                for s in project.slides
                if not (cfg[stage].get("skip_hidden", True) and s.hidden)
                and (only_slide is None or s.index == only_slide)
            ]
            if not project.slides:
                raise InputInvalid("No selected visible slides remain.")
            if project.source_slides.suffix.lower() == ".pptx":
                from .presentation import extract_layout

                write_json(
                    folder / "layout.json",
                    extract_layout(
                        self.root / project.source_slides,
                        json.loads((folder / "text_lines.json").read_text(encoding="utf-8-sig"))
                        if cfg[stage]["plugin"] == "powerpoint"
                        else None,
                    ),
                )
        elif stage == "script":
            writer = self.plugin(stage, ScriptWriter)
            llm = self.plugin("llm", LLMProvider)
            project.plugins_used["llm"] = f"{llm.name}@{llm.version}"
            context = json.dumps(
                [
                    {"index": s.index, "title": s.title, "text": s.body_text, "notes": s.notes_raw}
                    for s in project.slides
                ],
                ensure_ascii=False,
            )
            project.slides = [writer.write(s, context, llm) for s in project.slides]
            if cfg[stage]["plugin"] == "lecture_script":
                from .presentation import load_plan, load_targets

                storyboard = ["# Kịch bản bài giảng — cần giảng viên duyệt", ""]
                for slide in project.slides:
                    plan = load_plan(self.root, slide.index)
                    targets = {t.id: t for t in load_targets(self.root, slide.index)}
                    storyboard.extend(
                        [
                            f"## Slide {slide.index}: {slide.title}",
                            f"Mục tiêu: {plan.objective}",
                            "",
                        ]
                    )
                    for i, beat in enumerate(plan.beats, 1):
                        target = targets.get(beat.target_id or "")
                        storyboard.extend(
                            [
                                f"### {i}. {beat.purpose} / {beat.effect} / {beat.target_id or '-'}",
                                beat.text,
                                f"Đích: {target.text} ({target.geometry_source})"
                                if target
                                else "Đích: không nhấn vùng",
                                "",
                            ]
                        )
                    storyboard.extend([f"Chốt ý: {plan.takeaway}", *plan.warnings, ""])
                    project.warnings.extend(
                        f"Slide {slide.index} LLM: {warning}" for warning in plan.warnings
                    )
                atomic_text(folder / "storyboard.md", "\n".join(storyboard))
                from slidevoice.report.storyboard import write_storyboard

                write_storyboard(project, self.root, folder)
        elif stage == "normalize":
            normalizer = self.plugin(stage, TextNormalizer)
            for slide in project.slides:
                for seg in slide.segments:
                    seg.spoken_text = normalizer.normalize(seg.text, project.meta.language)
        elif stage == "voice":
            preparer = self.plugin(stage, VoicePreparer)
            project.voice = preparer.prepare(project.source_voice, project.meta.language, folder)
            project.voice.consent_confirmed = cfg["project"]["voice_consent"] is True
        elif stage == "tts":
            self.synthesize(project, folder)
            self.timeline(project)
        elif stage == "align":
            aligner = self.plugin(stage, Aligner)
            for slide in project.slides:
                for seg in slide.segments:
                    if seg.audio_path is None or seg.start is None:
                        continue
                    seg.words = aligner.align(
                        checked_path(self.root, seg.audio_path), seg.text, project.meta.language
                    )
                    for word in seg.words:
                        word.start += seg.start
                        word.end += seg.start
        elif stage == "subtitle":
            outputs = self.plugin(stage, SubtitleWriter).write(project, folder)
            if not {"srt", "vtt", "ass"} <= outputs.keys():
                raise StageFailed("Subtitle plugin must produce SRT, VTT and ASS files.")
            for path in outputs.values():
                if not checked_path(self.root, path).is_file():
                    raise StageFailed("Subtitle plugin returned a missing output file.")
            write_json(folder / "outputs.json", {name: str(path) for name, path in outputs.items()})
        elif stage == "avatar":
            if cfg[stage]["plugin"] != "none":
                raise InputInvalid("M0 supports only the disabled avatar; use avatar.plugin: none.")
        elif stage == "compose":
            outputs = json.loads(
                (self.root / "work/subtitle/outputs.json").read_text(encoding="utf-8")
            )
            subtitles = {name: Path(value) for name, value in outputs.items()}
            composer = self.plugin(
                stage,
                Composer,
                {
                    "width": cfg["render"]["width"],
                    "height": cfg["render"]["height"],
                    "target_lufs": cfg["qa"]["target_lufs"],
                },
            )
            output = composer.compose(project, subtitles, folder / "video.mp4")
            shutil.copyfile(checked_path(self.root, output), self.root / "video.mp4")
        return project

    def synthesize(self, project: Project, folder: Path) -> None:
        self.consent(project)
        assert project.voice is not None
        voice = project.voice
        aligner = self.plugin("align", Aligner)
        sentence_cache = SegmentCache(folder / "sentences")
        cache_dir = sentence_cache.folder
        for slide in project.slides:
            for seg in slide.segments:
                self.consent(project)  # Also required before sentence cache access.
                tts_class = registry.get_class("tts", self.config["tts"]["plugin"])
                key = stable_hash(
                    {
                        "text": seg.spoken_text,
                        "voice": voice.model_dump(mode="json"),
                        "voice_hash": file_hash(checked_path(self.root, voice.ref_audio)),
                        "tts": self.config["tts"],
                        "version": tts_class.version,
                        "qa": self.config["qa"],
                        "align": self.config["align"],
                        "align_version": aligner.version,
                    }
                )
                audio = cache_dir / f"{key}.wav"
                record = sentence_cache.load(key)
                if record is not None:
                    seg.audio_path = audio.relative_to(self.root)
                    seg.cer, seg.attempts = record.cer, record.attempts
                    if record.cer > self.config["qa"]["max_cer"]:
                        project.warnings.append(
                            f"{seg.id}: cached CER {record.cer:.3f} exceeds threshold; best attempt retained"
                        )
                    continue
                best: tuple[float, Path] | None = None
                for attempt in range(self.config["qa"]["max_retries"] + 1):
                    self.consent(project)
                    seg.attempts = attempt + 1
                    candidate = folder / f"{seg.id}_attempt_{attempt}.wav"
                    try:
                        engine = self.plugin(
                            "tts", TTSEngine, {"seed": self.config["tts"].get("seed", 42) + attempt}
                        )
                        engine.load_voice(voice)
                        engine.synthesize(seg.spoken_text, candidate, self.config["tts"]["speed"])
                        if wav_duration(candidate) <= 0:
                            raise StageFailed("TTS produced empty audio.")
                        error = cer(seg.spoken_text, aligner.transcribe(candidate, voice.language))
                        if best is None or error < best[0]:
                            best = error, candidate
                        if error <= self.config["qa"]["max_cer"]:
                            break
                    except ConsentMissing:
                        raise
                    except Exception:
                        log.warning(
                            "TTS failed for %s attempt %d; retrying within configured budget",
                            seg.id,
                            attempt + 1,
                        )
                if best is None:
                    write_tone(audio, max(1, len(seg.spoken_text.split()) * 0.18), frequency=0)
                    atomic_text(audio.with_suffix(".txt"), "")
                    seg.cer = None
                    project.warnings.append(
                        f"{seg.id}: synthesis failed; estimated silence inserted"
                    )
                else:
                    seg.cer = best[0]
                    shutil.copyfile(best[1], audio)
                    sidecar = best[1].with_suffix(".txt")
                    atomic_text(
                        audio.with_suffix(".txt"),
                        sidecar.read_text(encoding="utf-8")
                        if sidecar.exists()
                        else seg.spoken_text,
                    )
                    if best[0] > self.config["qa"]["max_cer"]:
                        project.warnings.append(
                            f"{seg.id}: CER {best[0]:.3f} exceeds threshold; best attempt retained"
                        )
                    sentence_cache.save(key, seg.cer, seg.attempts)
                seg.audio_path = audio.relative_to(self.root)

    def timeline(self, project: Project) -> None:
        timing = self.config["timing"]
        cursor = 0.0
        for slide in project.slides:
            slide.start = cursor
            if not slide.segments:
                project.warnings.append(
                    f"Slide {slide.index}: no narration; displaying for configured empty duration"
                )
                cursor += timing["empty_slide_duration"]
            else:
                cursor += timing["lead_in"]
                for i, seg in enumerate(slide.segments):
                    if seg.audio_path is None:
                        raise StageFailed("Segment has no synthesized audio.")
                    if i:
                        cursor += timing["gap"]
                    seg.start = cursor
                    cursor += wav_duration(checked_path(self.root, seg.audio_path))
                    seg.end = cursor
                cursor += timing["tail"]
            # M0 uses hard cuts; transition config is fingerprinted but crossfade is M6.
            slide.end = cursor
