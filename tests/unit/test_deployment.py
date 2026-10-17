import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

import pytest
from typer.testing import CliRunner

from samples.make_samples import make_samples
from slidevoice.cli import app
from slidevoice.core.cache import atomic_text, file_hash
from slidevoice.core.config import load_config, merge, validate
from slidevoice.core.doctor import diagnose
from slidevoice.core.errors import ConsentMissing, InputInvalid
from slidevoice.core.inputs import InputLimits, inspect_pptx
from slidevoice.core.locking import JobLock
from slidevoice.core.pipeline import Pipeline, create_job


def test_job_lock_rejects_second_process_and_releases_after_crash(job):
    code = (
        "from pathlib import Path; import os,sys; "
        "from slidevoice.core.locking import JobLock; "
        "lock=JobLock(Path(sys.argv[1])); lock.__enter__(); os._exit(0)"
    )
    with JobLock(job):
        before = file_hash(job / "config.json")
        child = subprocess.run(
            [sys.executable, "-c", code, str(job)], capture_output=True, timeout=15
        )
        assert child.returncode != 0
        with pytest.raises(InputInvalid, match="busy"):
            Pipeline(job).run(until="render")
        with pytest.raises(InputInvalid, match="busy"):
            create_job(
                job.parent / "samples/demo.pptx",
                job.parent / "samples/voice.wav",
                job,
                load_config(),
            )
        assert file_hash(job / "config.json") == before
    child = subprocess.run([sys.executable, "-c", code, str(job)], capture_output=True, timeout=15)
    assert child.returncode == 0, child.stderr
    with JobLock(job):
        pass


def test_atomic_writes_do_not_share_temporary_files(tmp_path):
    path = tmp_path / "state.json"
    values = [json.dumps({"value": i, "payload": "x" * 5000}) for i in range(24)]
    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(lambda text: atomic_text(path, text), values))
    assert path.read_text(encoding="utf-8") in values
    assert list(tmp_path.glob("*.tmp")) == []


def test_atomic_write_failure_preserves_previous_state(tmp_path):
    path = tmp_path / "state.json"
    atomic_text(path, "old")
    with patch.object(Path, "replace", side_effect=OSError("test failure")), pytest.raises(OSError):
        atomic_text(path, "new")
    assert path.read_text(encoding="utf-8") == "old"
    assert list(tmp_path.glob("*.tmp")) == []


def test_run_status_paused_failed_completed_and_reused_object(job):
    pipeline = Pipeline(job)
    pipeline.run(until="render")
    assert json.loads((job / "run_status.json").read_text())["status"] == "paused"
    pipeline.run(until="script")
    assert set(pipeline.events) == {"render", "script"}
    with pytest.raises(ConsentMissing):
        Pipeline(job, {"project": {"voice_consent": False}}).run()
    status = json.loads((job / "run_status.json").read_text())
    assert status["status"] == "failed"
    assert status["error_type"] == "ConsentMissing"
    assert "finished_at" in status


def test_interruption_releases_job_and_records_no_exception_message(job, monkeypatch):
    def interrupt(*args):
        raise KeyboardInterrupt("DO-NOT-PERSIST")

    pipeline = Pipeline(job)
    monkeypatch.setattr(pipeline, "execute", interrupt)
    with pytest.raises(KeyboardInterrupt):
        pipeline.run(until="render")
    status = (job / "run_status.json").read_text()
    assert json.loads(status)["status"] == "interrupted"
    assert "DO-NOT-PERSIST" not in status
    with JobLock(job):
        pass


def test_package_limits_valid_deck_and_size_rejection(tmp_path):
    slides, voice = make_samples(tmp_path / "fixtures")
    assert inspect_pptx(slides)["slides"] == 3
    for limits in (
        InputLimits(max_file_bytes=1024),
        InputLimits(max_members=1),
        InputLimits(max_slides=1),
        InputLimits(max_archive_bytes=1024),
        InputLimits(max_member_bytes=1024),
    ):
        with pytest.raises(InputInvalid):
            inspect_pptx(slides, limits)
    with pytest.raises(InputInvalid):
        create_job(
            slides,
            voice,
            tmp_path / "job",
            validate(merge(load_config(), {"limits": {"max_slides": 1}})),
        )
    assert not (tmp_path / "job").exists()


@pytest.mark.parametrize(
    "member",
    [
        "../outside",
        "/absolute",
        "a\\b",
        "ppt/vbaProject.bin",
        "ppt/embeddings/object.bin",
        "ppt/activeX/a.xml",
    ],
)
def test_plain_package_policy_rejects_unsafe_or_active_members(tmp_path, member):
    path = tmp_path / "bad.pptx"
    with ZipFile(path, "w") as archive:
        archive.writestr("[Content_Types].xml", "types")
        archive.writestr("ppt/presentation.xml", "presentation")
        archive.writestr("ppt/slides/slide1.xml", "slide")
        info = ZipInfo("member")
        # zipfile otherwise normalizes the host OS separator while constructing
        # ZipInfo; exercise the actual package entry, including on Windows.
        info.filename = member
        archive.writestr(info, "content")
    with pytest.raises(InputInvalid):
        inspect_pptx(path)


def test_package_policy_bounds_compression_and_rejects_duplicates(tmp_path):
    path = tmp_path / "bad.pptx"
    with ZipFile(path, "w", compression=ZIP_DEFLATED) as archive:
        archive.writestr("ppt/large.xml", "x" * 20000)
    with pytest.raises(InputInvalid):
        inspect_pptx(path, InputLimits(max_compression_ratio=2))
    with ZipFile(path, "w") as archive:
        archive.writestr("ppt/a.xml", "a")
        archive.writestr("PPT/A.xml", "b")
    with pytest.raises(InputInvalid):
        inspect_pptx(path)


@pytest.mark.parametrize(
    "override",
    [
        {"render": {"width": 10000}},
        {"compose": {"fps": True}},
        {"compose": {"fps": 121}},
        {"limits": {"max_slides": 0}},
        {"limits": {"max_slides": "5"}},
    ],
)
def test_resource_config_rejects_invalid_limits(override):
    with pytest.raises(InputInvalid):
        validate(merge(load_config(), override))


def test_doctor_missing_tools_and_json_exit_code(monkeypatch):
    monkeypatch.setattr("slidevoice.core.doctor.shutil.which", lambda _: None)
    report = diagnose()
    assert report["ok"] is False
    result = CliRunner().invoke(app, ["doctor", "--json-output"])
    assert result.exit_code == 1
    assert json.loads(result.output)["schema_version"] == 1


def test_doctor_sanitizes_plugin_exceptions(monkeypatch):
    def fail(*args):
        raise RuntimeError("DO-NOT-LOG")

    monkeypatch.setattr("slidevoice.core.doctor.registry.create", fail)
    report = diagnose(load_config())
    assert not report["ok"]
    assert "DO-NOT-LOG" not in json.dumps(report)
