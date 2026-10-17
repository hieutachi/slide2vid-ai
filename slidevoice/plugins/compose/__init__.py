"""M0 color-video composer with real AAC, soft subtitles, chapters and metadata."""

import wave
from pathlib import Path

from slidevoice import __version__
from slidevoice.core.errors import InputInvalid
from slidevoice.core.interfaces import Composer
from slidevoice.core.media import run_process
from slidevoice.core.models import Project
from slidevoice.core.registry import register


def metadata_escape(value: str) -> str:
    return (
        value.replace("\\", "\\\\")
        .replace("=", "\\=")
        .replace(";", "\\;")
        .replace("#", "\\#")
        .replace("\n", " ")
        .replace("\r", " ")
    )


@register("compose", "fake_compose")
class FakeComposer(Composer):
    name = "fake_compose"
    version = "0.1.1"

    def video_input(self, duration: float, width: int, height: int) -> list[str]:
        return [
            "-f",
            "lavfi",
            "-i",
            f"color=c=0x192846:s={width}x{height}:r={self.config.get('fps', 30)}:d={duration}",
        ]

    def video_encoding_args(self, width: int, height: int) -> list[str]:
        return [
            "-c:v",
            "libx264",
            "-preset",
            str(self.config.get("preset", "ultrafast")),
            "-crf",
            str(self.config.get("crf", 20)),
            "-pix_fmt",
            "yuv420p",
            "-vf",
            f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1",
            "-r",
            str(self.config.get("fps", 30)),
        ]

    def compose(self, project: Project, subtitles: dict[str, Path], out_path: Path) -> Path:
        duration = max((s.end or 0 for s in project.slides), default=0)
        audio = out_path.parent / "timeline.wav"
        # All TTS contracts produce 24 kHz mono PCM in M0. Place samples on the actual timeline.
        frames = bytearray(round(duration * 24000) * 2)
        for slide in project.slides:
            for seg in slide.segments:
                if seg.audio_path is None or seg.start is None:
                    continue
                with wave.open(str(self.workdir / seg.audio_path), "rb") as reader:
                    data = reader.readframes(reader.getnframes())
                start = round(seg.start * 24000) * 2
                frames[start : start + len(data)] = data
        with wave.open(str(audio), "wb") as writer:
            writer.setparams((1, 2, 24000, 0, "NONE", "not compressed"))
            writer.writeframes(frames)
        meta = out_path.parent / "metadata.ffmeta"
        lines = [
            ";FFMETADATA1",
            f"title={metadata_escape(project.meta.title)}",
            f"artist={metadata_escape(project.meta.author)}",
            f"author={metadata_escape(project.meta.author)}",
            f"language={metadata_escape(project.meta.language)}",
            f"creation_time={project.meta.created_at}",
            "comment=AI-generated voice / giọng do AI tạo; review content before publication",
        ]
        for slide in project.slides:
            lines.extend(
                [
                    "[CHAPTER]",
                    "TIMEBASE=1/1000",
                    f"START={round((slide.start or 0) * 1000)}",
                    f"END={round((slide.end or 0) * 1000)}",
                    f"title={metadata_escape(slide.title or f'Slide {slide.index}')}",
                ]
            )
        meta.write_text("\n".join(lines) + "\n", encoding="utf-8")
        width = int(self.config["width"])
        height = int(self.config["height"])
        language = project.meta.language
        iso = {"vi": "vie", "en": "eng"}.get(language, language)
        run_process(
            [
                "ffmpeg",
                "-v",
                "error",
                "-nostdin",
                "-y",
                *self.video_input(duration, width, height),
                "-i",
                str(audio),
                "-i",
                str(self.workdir / subtitles["srt"]),
                "-f",
                "ffmetadata",
                "-i",
                str(meta),
                "-map",
                "0:v",
                "-map",
                "1:a",
                "-map",
                "2:s?",
                "-map_metadata",
                "3",
                "-map_chapters",
                "3",
                *self.video_encoding_args(width, height),
                "-c:a",
                "aac",
                "-ar",
                "48000",
                "-ac",
                "2",
                "-disposition:a:0",
                "default",
                "-b:a",
                "192k",
                "-af",
                f"loudnorm=I={self.config.get('target_lufs', -16)}:TP=-1.5:LRA=11",
                "-c:s",
                "mov_text",
                "-metadata:s:a:0",
                f"language={iso}",
                "-metadata:s:s:0",
                f"language={iso}",
                "-movflags",
                "+faststart+use_metadata_tags",
                "-metadata",
                f"encoding_tool=SlideVoice {__version__}",
                "-metadata:s:v:0",
                f"encoder=SlideVoice {__version__}",
                "-t",
                str(duration),
                str(out_path),
            ],
            timeout=float(self.config.get("timeout_sec", 120)),
        )
        return out_path.relative_to(self.workdir)


@register("compose", "qa_video")
class QAVideoComposer(FakeComposer):
    """Downloaded footage with system narration, without retaining source voices."""

    name = "qa_video"

    def video_input(self, duration: float, width: int, height: int) -> list[str]:
        path = Path(self.config.get("background_path", "inputs/background.mp4"))
        resolved = (self.workdir / path).resolve()
        if (
            path.is_absolute()
            or not resolved.is_relative_to(self.workdir.resolve())
            or not resolved.is_file()
        ):
            raise InputInvalid("QA background must be an existing job-relative video file.")
        # compose maps only this input's video, never its original speech/audio.
        return ["-stream_loop", "-1", "-i", str(resolved)]


@register("compose", "slide_images")
class SlideImageComposer(FakeComposer):
    """Compose the actual rendered slide images on their narration timeline."""

    name = "slide_images"
    version = "0.1.0"

    def compose(self, project: Project, subtitles: dict[str, Path], out_path: Path) -> Path:
        if not project.slides:
            raise InputInvalid("Slide image composition requires at least one slide.")
        entries = ["ffconcat version 1.0"]
        last_image = ""
        for slide in project.slides:
            if slide.image_path is None:
                raise InputInvalid("A rendered image is required for each slide.")
            image = (self.workdir / slide.image_path).resolve()
            if not image.is_relative_to(self.workdir.resolve()) or not image.is_file():
                raise InputInvalid("Slide images must exist inside the job directory.")
            length = (slide.end or 0) - (slide.start or 0)
            if length <= 0:
                raise InputInvalid("Each slide requires a positive timeline duration.")
            last_image = image.as_posix().replace("'", "'\\''")
            entries.extend([f"file '{last_image}'", f"duration {length:.9f}"])
        entries.append(f"file '{last_image}'")
        self._image_list = out_path.parent / "slides.ffconcat"
        self._image_list.write_text("\n".join(entries) + "\n", encoding="utf-8")
        return super().compose(project, subtitles, out_path)

    def video_input(self, duration: float, width: int, height: int) -> list[str]:
        return ["-f", "concat", "-safe", "0", "-i", str(self._image_list)]
