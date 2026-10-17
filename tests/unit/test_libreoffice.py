import struct
from pathlib import Path

import pytest

from slidevoice.core.errors import PluginUnavailable, StageFailed
from slidevoice.core.models import Project
from slidevoice.plugins.render import color_png
from slidevoice.plugins.render.libreoffice import LibreOfficeRenderer


def test_libreoffice_missing_dependencies(tmp_path, monkeypatch):
    monkeypatch.setattr("slidevoice.plugins.render.libreoffice.shutil.which", lambda _: None)
    with pytest.raises(PluginUnavailable):
        LibreOfficeRenderer({}, tmp_path).healthcheck()


@pytest.mark.parametrize("missing", [None, "pdf", "page"])
def test_libreoffice_export_contract_preserves_slide_mapping(job, monkeypatch, missing):
    calls = []
    monkeypatch.setattr("slidevoice.plugins.render.libreoffice.shutil.which", lambda name: name)

    def run(args, timeout):
        calls.append(args)
        if args[0] == "soffice":
            destination = Path(args[args.index("--outdir") + 1])
            if missing != "pdf":
                (destination / "slides.pdf").write_bytes(b"pdf-test-double")
        elif args[0] == "pdftoppm":
            prefix = Path(args[-1])
            for index in range(1, 3 if missing == "page" else 4):
                color_png(prefix.parent / f"page-{index}.png", 120, 90, b"\xff\xff\xff")
        else:
            assert "force_original_aspect_ratio=decrease" in args[args.index("-vf") + 1]
            color_png(Path(args[-1]), 320, 180, b"\x00\x00\x00")
        return ""

    monkeypatch.setattr("slidevoice.plugins.render.libreoffice.run_process", run)
    project = Project.model_validate_json((job / "initial.json").read_text())
    renderer = LibreOfficeRenderer({}, job)
    folder = job / "work/render"
    if missing:
        with pytest.raises(StageFailed):
            renderer.render(project, folder, 320, 180)
        assert list(folder.glob("slide_*.png")) == []
    else:
        slides = renderer.render(project, folder, 320, 180)
        assert [s.index for s in slides] == [1, 2, 3]
        assert all(s.title for s in slides)
        assert "UserInstallation=file:" in calls[0][1]
        assert "ExportHiddenSlides" in calls[0][4]
        assert list(folder.glob("office-*")) == []
        assert all((job / s.image_path).is_file() for s in slides)
        assert struct.unpack(">II", (job / slides[0].image_path).read_bytes()[16:24]) == (320, 180)
