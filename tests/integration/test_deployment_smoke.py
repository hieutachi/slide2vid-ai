import json

from typer.testing import CliRunner

from slidevoice.cli import app
from slidevoice.core.pipeline import Pipeline


def test_installed_package_smoke_and_resume(tmp_path):
    out = tmp_path / "smoke"
    result = CliRunner().invoke(app, ["smoke", "--out", str(out)])
    assert result.exit_code == 0, result.exception
    assert (out / "video.mp4").stat().st_size > 1000
    status = json.loads((out / "run_status.json").read_text())
    assert status["status"] == "completed"
    pipeline = Pipeline(out)
    pipeline.run()
    assert set(pipeline.events.values()) == {"cache_hit"}
