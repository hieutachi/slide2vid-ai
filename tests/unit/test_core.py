import json
from pathlib import Path
from unittest.mock import patch

import httpx
import pytest

from slidevoice.core import registry
from slidevoice.core.cache import StageCache, file_hash, stable_hash
from slidevoice.core.config import load_config, merge, validate
from slidevoice.core.errors import ConsentMissing, InputInvalid, PluginUnavailable, StageFailed
from slidevoice.core.media import run_process
from slidevoice.core.models import Project, Slide
from slidevoice.core.pipeline import Pipeline, cer, checked_path
from slidevoice.core.worker_client import WorkerClient


def test_hash_and_defaults():
    assert stable_hash({"b": 2, "a": 1}) == stable_hash({"a": 1, "b": 2})
    a = Slide(index=1)
    b = Slide(index=2)
    a.segments.clear()
    assert a.segments is not b.segments
    assert load_config()["project"]["voice_consent"] is False


@pytest.mark.parametrize(
    "override",
    [
        {"project": {"voice_consent": "true"}},
        {"project": {"voice_consent": 1}},
        {"timing": {"gap": -1}},
        {"tts": {"speed": 0}},
        {"render": {"width": 3}},
        {"tts": {"speed": float("nan")}},
        {"llm": {"nested": {"api_key": "dont-persist"}}},
        {"llm": {"base_url": "https://name:password@localhost"}},
    ],
)
def test_config_rejects_unsafe_values(override):
    with pytest.raises(InputInvalid):
        validate(merge(load_config(), override))


def test_yaml_errors(tmp_path):
    path = tmp_path / "bad.yaml"
    for text in ("[x]", "a: [", "project: null"):
        path.write_text(text, encoding="utf-8")
        with pytest.raises(InputInvalid):
            load_config(path)


def test_registry_snapshot_loads_builtins(tmp_path):
    names = registry.snapshot()
    assert len(names) == 10
    assert "fake_tts" in names["tts"]
    with pytest.raises(PluginUnavailable, match="missing"):
        registry.create("tts", "missing", {}, tmp_path)


def test_entry_point_discovery(monkeypatch):
    from slidevoice.plugins.normalize import FakeNormalizer

    class Entry:
        name = "normalize.external"
        value = "example:Normalizer"

        def load(self):
            return FakeNormalizer

    monkeypatch.setattr(registry, "_EXTERNAL_LOADED", False)
    monkeypatch.setattr(registry, "_PLUGINS", {})
    monkeypatch.setattr(registry, "entry_points", lambda **kwargs: [Entry()])
    assert registry.get_class("normalize", "external") is FakeNormalizer


def test_stage_cache_corruption_and_artifact_integrity(job):
    project = Project.model_validate_json((job / "initial.json").read_text(encoding="utf-8"))
    cache = StageCache(job)
    asset = job / "test.txt"
    asset.write_text("old", encoding="utf-8")
    cache.save("render", "key", project, [asset])
    assert cache.load("render", "key") is not None
    assert cache.load("render", "other") is None
    asset.write_text("new", encoding="utf-8")
    assert cache.load("render", "key") is None
    (job / "work/render/cache.json").write_text("{", encoding="utf-8")
    assert cache.load("render", "key") is None


def test_paths_and_cer(job):
    with pytest.raises(InputInvalid):
        checked_path(job, Path("../escape.wav"))
    with pytest.raises(InputInvalid):
        checked_path(job, job / "absolute.wav")
    assert cer("xin chào", "xin chào") == 0
    assert cer("abc", "abd") == pytest.approx(1 / 3)
    assert cer("", "x") == 1


def test_subprocess_uses_safe_args_and_timeout():
    with (
        patch("slidevoice.core.media.shutil.which", return_value="ffmpeg"),
        patch("slidevoice.core.media.subprocess.run") as run,
    ):
        run.return_value.stdout = "ok"
        assert run_process(["ffmpeg", "-version"]) == "ok"
        assert run.call_args.kwargs["check"] is True
        assert run.call_args.kwargs["timeout"] > 0
        assert run.call_args.args[0] == ["ffmpeg", "-version"]
    with (
        patch("slidevoice.core.media.shutil.which", return_value=None),
        pytest.raises(PluginUnavailable),
    ):
        run_process(["missing"])


def test_worker_retry_health_shared_paths(tmp_path, monkeypatch):
    attempts = []

    def handler(request):
        if request.url.path == "/health":
            return httpx.Response(200, json={"status": "ok"})
        attempts.append(request)
        return httpx.Response(503 if len(attempts) < 3 else 200, json={"output": "a.wav"})

    monkeypatch.setattr("slidevoice.core.worker_client.time.sleep", lambda _: None)
    with WorkerClient(
        "http://localhost", tmp_path, transport=httpx.MockTransport(handler)
    ) as client:
        client.healthcheck()
        assert client.run({"input": "a.wav"}) == {"output": "a.wav"}
        assert len(attempts) == 3
        assert client.shared_path(tmp_path / "a.wav") == "a.wav"
        with pytest.raises(InputInvalid):
            client.shared_path(Path("../escape"))
        with pytest.raises(InputInvalid):
            client.run({"base64_audio": "abc"})


def test_worker_client_error_sanitized(tmp_path):
    transport = httpx.MockTransport(lambda _: httpx.Response(400, json={"secret": "DO-NOT-LOG"}))
    with WorkerClient("http://localhost", tmp_path, transport=transport) as client:
        with pytest.raises(PluginUnavailable):
            client.healthcheck()
        with pytest.raises(StageFailed) as exc:
            client.run({})
        assert "DO-NOT-LOG" not in str(exc.value)


def test_consent_before_any_execution(job):
    with patch("slidevoice.core.registry.create") as create:
        with pytest.raises(ConsentMissing):
            Pipeline(job, {"project": {"voice_consent": False}}).run()
        create.assert_not_called()
    assert not (job / "work/tts").exists()


def test_secret_not_persisted(job):
    before = file_hash(job / "config.json")
    with pytest.raises(InputInvalid):
        Pipeline(job, {"tts": {"api_key": "DO-NOT-PERSIST"}})
    assert file_hash(job / "config.json") == before


def test_plugin_secret_never_enters_failure_manifest(job, monkeypatch, caplog):
    from slidevoice.plugins.compose import FakeComposer

    Pipeline(job).run(until="avatar")
    before = file_hash(job / "manifest.json")
    marker = "DO-NOT-PERSIST-PLUGIN-SECRET"

    def fail_with_secret(self, project, subtitles, out_path):
        project.voice.extra["authorization"] = marker
        raise RuntimeError(marker)

    monkeypatch.setattr(FakeComposer, "compose", fail_with_secret)
    with pytest.raises(InputInvalid) as exc:
        Pipeline(job).run(from_stage="compose")
    assert marker not in str(exc.value)
    assert marker not in caplog.text
    assert file_hash(job / "manifest.json") == before
    for path in job.rglob("*.json"):
        assert marker not in path.read_text(encoding="utf-8")


def test_changed_plugin_version_invalidates_cache(job, monkeypatch):
    from slidevoice.plugins.render import FakeRenderer

    Pipeline(job).run(until="render")
    monkeypatch.setattr(FakeRenderer, "version", "0.2.0")
    pipeline = Pipeline(job)
    pipeline.run(until="render")
    assert pipeline.events["render"] == "executed"
    manifest = json.loads((job / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["plugins_used"]["render"] == "fake_render@0.2.0"
