import json
import subprocess

from slidevoice.core.media import run_process
from slidevoice.core.pipeline import Pipeline
from slidevoice.plugins.render import FakeRenderer, color_png


def test_slide_images_are_composed_on_timeline(job, monkeypatch):
    original = FakeRenderer.render
    colors = [bytes((200, 30, 30)), bytes((30, 200, 30)), bytes((30, 30, 200))]

    def render(self, project, out_dir, width, height):
        slides = original(self, project, out_dir, width, height)
        for slide, color in zip(slides, colors, strict=True):
            color_png(self.workdir / slide.image_path, width, height, color)
        return slides

    monkeypatch.setattr(FakeRenderer, "render", render)
    project = Pipeline(job, {"compose": {"plugin": "slide_images"}}).run()
    # Compare decoded RGB against each renderer image, not only stream presence.
    for slide, color in zip(project.slides, colors, strict=True):
        pixels = subprocess.run(
            [
                "ffmpeg",
                "-v",
                "error",
                "-ss",
                str((slide.start + slide.end) / 2),
                "-i",
                str(job / "video.mp4"),
                "-vf",
                "scale=1:1",
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
        assert len(pixels) == 3
        assert all(
            abs(actual - expected) < 10 for actual, expected in zip(pixels, color, strict=True)
        )
    probe = json.loads(
        run_process(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_streams",
                "-of",
                "json",
                str(job / "video.mp4"),
            ]
        )
    )
    assert any(s["codec_type"] == "audio" for s in probe["streams"])
    assert len(project.slides) == 3
    assert (job / "work/compose/slides.ffconcat").read_text().count("duration ") == 3
