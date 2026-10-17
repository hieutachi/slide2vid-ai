"""Headless LibreOffice -> PDF -> PNG, with isolated per-call Office profile."""

from __future__ import annotations

import shutil
import struct
import tempfile
from pathlib import Path

from slidevoice.core.errors import PluginUnavailable, StageFailed
from slidevoice.core.inputs import InputLimits, inspect_pptx
from slidevoice.core.media import run_process
from slidevoice.core.models import Project, Slide
from slidevoice.core.registry import register
from slidevoice.plugins.render import FakeRenderer


@register("render", "libreoffice")
class LibreOfficeRenderer(FakeRenderer):
    name = "libreoffice"
    version = "0.1.0"

    def healthcheck(self) -> None:
        if not (shutil.which("soffice") or shutil.which("libreoffice")) or not shutil.which(
            "pdftoppm"
        ):
            raise PluginUnavailable(
                "LibreOffice and pdftoppm are required.",
                remedy="Install LibreOffice Impress, Poppler utilities and the deck's fonts.",
            )

    def render(self, project: Project, out_dir: Path, width: int, height: int) -> list[Slide]:
        self.healthcheck()
        source = (self.workdir / project.source_slides).resolve()
        inspect_pptx(source, InputLimits.model_validate(self.config.get("input_limits", {})))
        slides = super().render(project, out_dir, width, height)
        for slide in slides:
            if slide.image_path:
                (self.workdir / slide.image_path).unlink()
        timeout = float(self.config.get("timeout_sec", 180))
        # PDF/PNG intermediates stay in the job, not a system shared temp location.
        with tempfile.TemporaryDirectory(prefix="office-", dir=out_dir) as directory:
            scratch = Path(directory)
            office = shutil.which("soffice") or shutil.which("libreoffice")
            assert office is not None  # established by healthcheck
            run_process(
                [
                    office,
                    f"-env:UserInstallation={(scratch / 'profile').as_uri()}",
                    "--headless",
                    "--convert-to",
                    "pdf:impress_pdf_Export:"
                    '{"ExportHiddenSlides":{"type":"boolean","value":"true"}}',
                    "--outdir",
                    str(scratch),
                    str(source),
                ],
                timeout=timeout,
            )
            pdf = scratch / (source.stem + ".pdf")
            if not pdf.is_file():
                raise StageFailed(
                    "LibreOffice did not produce a PDF; no synthetic fallback is used."
                )
            prefix = scratch / "page"
            run_process(
                [
                    "pdftoppm",
                    "-png",
                    "-r",
                    "96",
                    "-scale-to",
                    str(max(width, height)),
                    str(pdf),
                    str(prefix),
                ],
                timeout=timeout,
            )
            pages = sorted(scratch.glob("page-*.png"), key=lambda p: int(p.stem.rsplit("-", 1)[1]))
            if len(pages) != len(slides):
                raise StageFailed(
                    "LibreOffice page count differs from PPTX; refusing shifted slide narration."
                )
            for slide, page in zip(slides, pages, strict=True):
                assert slide.image_path is not None
                target = self.workdir / slide.image_path
                # Preserve 4:3 / portrait aspect ratios with centered black padding.
                run_process(
                    [
                        "ffmpeg",
                        "-v",
                        "error",
                        "-nostdin",
                        "-y",
                        "-i",
                        str(page),
                        "-vf",
                        f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
                        f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1",
                        "-frames:v",
                        "1",
                        str(target),
                    ],
                    timeout=timeout,
                )
                with target.open("rb") as stream:
                    header = stream.read(24)
                if (
                    len(header) != 24
                    or header[:8] != b"\x89PNG\r\n\x1a\n"
                    or struct.unpack(">II", header[16:24]) != (width, height)
                ):
                    raise StageFailed("Renderer returned an invalid output image.")
        return slides
