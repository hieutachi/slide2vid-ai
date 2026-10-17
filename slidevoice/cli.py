"""Typer entry points for synthetic M0 and external interface plugins."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated, Any

import typer
import yaml  # type: ignore[import-untyped]
from rich.console import Console
from rich.logging import RichHandler

from .core import registry
from .core.config import STAGES, load_config
from .core.errors import InputInvalid, SlideVoiceError
from .core.interfaces import Plugin
from .core.pipeline import Pipeline, create_job

app = typer.Typer(
    no_args_is_help=True, help="SlideVoice — slide narration and lecture presentation"
)
console = Console()


@app.command()
def smoke(out: Annotated[Path, typer.Option()]) -> None:
    """Run an offline synthetic AV fixture using only the installed package."""
    from .core.smoke import smoke as run_smoke

    run_smoke(out)
    console.print("Synthetic smoke passed; not a real speech or ASR quality benchmark.")


@app.command()
def doctor(config: Path | None = None, json_output: bool = False) -> None:
    """Check media tools and optionally selected plugins; nonzero exit on failure."""
    import json

    from .core.doctor import diagnose

    report = diagnose(load_config(config) if config is not None else None)
    if json_output:
        typer.echo(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        for check in report["checks"]:
            console.print(f"{check['status']:7} {check['name']}: {check['detail']}", markup=False)
    if not report["ok"]:
        raise typer.Exit(1)


@app.command()
def lecture(
    slides: Annotated[Path, typer.Option()],
    out: Annotated[Path, typer.Option()],
    config: Annotated[Path, typer.Option()],
    review_only: bool = False,
) -> None:
    """PPTX + embedded speaker notes + LLM API -> narrated teaching video.

    --review-only stops after the structured storyboard, before GPU synthesis.
    """
    import tempfile

    from .core.media import write_tone

    cfg = load_config(config)
    if (
        cfg["script"]["plugin"] != "lecture_script"
        or cfg["compose"]["plugin"] != "presenter"
        or cfg["voice"]["plugin"] != "preset_voice"
        or cfg["tts"]["plugin"] != "vieneu"
    ):
        raise InputInvalid(
            "lecture requires lecture_script, presenter, preset_voice and vieneu plugins.",
            remedy="Use the repository's configs/lecture_vietnamese.yaml as the starting config.",
        )
    with tempfile.TemporaryDirectory() as directory:
        placeholder = Path(directory) / "preset.wav"
        write_tone(placeholder, 0.1, frequency=0)
        job = create_job(slides, placeholder, out, cfg)
    execute(job, until="script" if review_only else None)


def overrides(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("Expected mapping")
        return data
    except (OSError, ValueError, yaml.YAMLError):
        raise InputInvalid("Cannot load configuration override.") from None


def execute(
    job: Path,
    config: dict[str, Any] | None = None,
    from_stage: str | None = None,
    until: str | None = None,
    only_slide: int | None = None,
) -> None:
    pipeline = Pipeline(job, config)
    with console.status("Running SlideVoice stages…"):
        pipeline.run(from_stage, until, only_slide)
    console.print(f"[green]Done:[/green] {job.resolve()}")


@app.command()
def run(
    slides: Annotated[Path, typer.Option()],
    voice: Annotated[Path, typer.Option()],
    out: Annotated[Path, typer.Option()],
    config: Path | None = None,
    from_stage: str | None = None,
) -> None:
    """Create/update a job at --out; run the complete pipeline."""
    job = create_job(slides, voice, out, load_config(config))
    execute(job, from_stage=from_stage)


@app.command()
def resume(job: Path, config: Path | None = None, from_stage: str | None = None) -> None:
    """Validate and reuse completed checkpoints, continue incomplete stages."""
    execute(job, overrides(config), from_stage)


@app.command()
def stage(
    name: str,
    slides: Path | None = None,
    voice: Path | None = None,
    job: Path | None = None,
    config: Path | None = None,
    out: Path = Path("out/stage"),
) -> None:
    """Run dependencies through NAME, or restart NAME in an existing --job."""
    if name not in STAGES:
        raise InputInvalid(f"Unknown stage. Choose: {', '.join(STAGES)}")
    if job is None:
        if slides is None:
            raise InputInvalid("--slides is required for a new stage job.")
        if voice is None and name != "render":
            raise InputInvalid("--voice is required for stages after render.")
        # render does not read audio, so an inert copied placeholder is sufficient.
        job = create_job(slides, voice or slides, out, load_config(config))
        execute(job, until=name)
    else:
        execute(job, overrides(config), from_stage=name, until=name)


@app.command()
def plugins() -> None:
    """List discovered classes and execute local healthchecks."""
    import tempfile

    with tempfile.TemporaryDirectory() as directory:
        for kind, names in registry.snapshot().items():
            for name in names:
                cls = registry.get_class(kind, name)
                try:
                    instance: Plugin = cls({}, Path(directory))
                    instance.healthcheck()
                    status = "ok"
                except SlideVoiceError:
                    status = "unavailable"
                console.print(f"{kind}.{name}  {cls.version}  {status}")


@app.command()
def preview(
    slide: Annotated[int, typer.Option(min=1)],
    job: Path,
    out: Path | None = None,
    config: Path | None = None,
) -> None:
    """Create an isolated single-slide video without modifying the original job."""
    pipeline = Pipeline(job, overrides(config))
    target = out or job.parent / (
        job.name + f"_preview_{slide}_" + datetime.now(UTC).strftime("%H%M%S%f")
    )
    preview_job = create_job(
        job / pipeline.initial.source_slides,
        job / pipeline.initial.source_voice,
        target,
        pipeline.config,
    )
    execute(preview_job, only_slide=slide)


def main() -> None:
    logging.basicConfig(
        level=logging.INFO, format="%(message)s", handlers=[RichHandler(show_path=False)]
    )
    try:
        app()
    except SlideVoiceError as exc:
        console.print(str(exc), style="red", markup=False)
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
