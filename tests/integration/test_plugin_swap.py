from slidevoice.core import registry
from slidevoice.core.pipeline import Pipeline
from slidevoice.plugins.compose import FakeComposer
from slidevoice.plugins.subtitle import FakeSubtitle


def test_plugin_return_paths_are_respected(job, monkeypatch):
    class RenamedSubtitles(FakeSubtitle):
        name = "renamed_subtitles"

        def write(self, project, out_dir):
            paths = super().write(project, out_dir)
            renamed = {}
            for ext, path in paths.items():
                target = (self.workdir / path).with_name(f"custom.{ext}")
                (self.workdir / path).rename(target)
                renamed[ext] = target.relative_to(self.workdir)
            return renamed

    class RenamedComposer(FakeComposer):
        name = "renamed_composer"

        def compose(self, project, subtitles, out_path):
            return super().compose(project, subtitles, out_path.with_name("custom.mp4"))

    registry.ensure_builtin_plugins_loaded()
    monkeypatch.setattr(
        registry, "_PLUGINS", {kind: dict(bucket) for kind, bucket in registry._PLUGINS.items()}
    )
    registry.register_class("subtitle", "renamed_subtitles", RenamedSubtitles)
    registry.register_class("compose", "renamed_composer", RenamedComposer)
    pipeline = Pipeline(
        job,
        {"subtitle": {"plugin": "renamed_subtitles"}, "compose": {"plugin": "renamed_composer"}},
    )
    pipeline.run()
    assert (job / "video.mp4").is_file()
    assert "Xin chào" in (job / "subtitles.srt").read_text(encoding="utf-8")
    resumed = Pipeline(job)
    resumed.run()
    assert resumed.events["compose"] == "cache_hit"
