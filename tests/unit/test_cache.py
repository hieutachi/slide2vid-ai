import json
import os
from pathlib import Path

import pytest

from slidevoice.core.cache import SegmentCache, StageCache, file_hash, write_json
from slidevoice.core.errors import InputInvalid
from slidevoice.core.media import write_tone
from slidevoice.core.models import Project, Segment, Slide, Word


def test_nested_relative_artifacts_and_bad_snapshots(job):
    project = Project.model_validate_json((job / "initial.json").read_text(encoding="utf-8"))
    cache = StageCache(job)
    audio = job / "work/tts/sentences/deep/test.wav"
    write_tone(audio, 0.1)
    project.slides = [
        Slide(
            index=1,
            segments=[
                Segment(id="s001_01", text="a", spoken_text="a", audio_path=audio.relative_to(job))
            ],
        )
    ]
    cache.save("tts", "test", project, [audio])
    checkpoint = job / "work/tts/cache.json"
    original = checkpoint.read_text(encoding="utf-8")
    assert cache.load("tts", "test") is not None
    audio.unlink()
    assert cache.load("tts", "test") is None
    write_tone(audio, 0.1)
    for bad in (
        [],
        {},
        {"key": "test", "artifacts": []},
        {"key": "test", "project": "not a project"},
    ):
        checkpoint.write_text(json.dumps(bad), encoding="utf-8")
        assert cache.load("tts", "test") is None
    record = json.loads(original)
    record["project"]["slides"][0]["segments"][0]["audio_path"] = "../escape.wav"
    checkpoint.write_text(json.dumps(record), encoding="utf-8")
    assert cache.load("tts", "test") is None
    record = json.loads(original)
    record["artifacts"].pop(str(audio.relative_to(job)))
    checkpoint.write_text(json.dumps(record), encoding="utf-8")
    assert cache.load("tts", "test") is None


@pytest.mark.parametrize("value", [None, [], 42, "invalid"])
def test_non_object_checkpoints_are_cache_misses(job, value):
    checkpoint = job / "work/render/cache.json"
    checkpoint.parent.mkdir(parents=True)
    checkpoint.write_text(json.dumps(value), encoding="utf-8")
    assert StageCache(job).load("render", "key") is None


def test_save_requires_every_declared_artifact(job):
    project = Project.model_validate_json((job / "initial.json").read_text(encoding="utf-8"))
    with pytest.raises(FileNotFoundError):
        StageCache(job).save("render", "key", project, [job / "missing.png"])
    assert not (job / "work/render/cache.json").exists()


def test_full_hash_detects_middle_change_with_unchanged_stat(tmp_path):
    path = tmp_path / "large.bin"
    with path.open("wb") as stream:
        stream.truncate(33 * 1024 * 1024)
    before = file_hash(path)
    info = path.stat()
    with path.open("r+b") as stream:
        stream.seek(16 * 1024 * 1024)
        stream.write(b"changed")
    os.utime(path, ns=(info.st_atime_ns, info.st_mtime_ns))
    assert file_hash(path) != before


def test_word_audio_subtitle_and_plugin_inputs_are_fingerprinted(job):
    project = Project.model_validate_json((job / "initial.json").read_text(encoding="utf-8"))
    cache = StageCache(job)
    project.slides = [Slide(index=1, segments=[Segment(id="s001_01", text="a", spoken_text="a")])]
    key = cache.key(project, {}, "fake@1")
    project.slides[0].segments[0].words = [Word(text="a", start=0, end=0.1)]
    assert key != cache.key(project, {}, "fake@1")
    key = cache.key(project, {}, "fake@1")
    audio = job / "audio.wav"
    write_tone(audio, 0.1)
    project.slides[0].segments[0].audio_path = Path("audio.wav")
    assert key != cache.key(project, {}, "fake@1")
    key = cache.key(project, {}, "fake@1")
    write_tone(audio, 0.2)
    assert key != cache.key(project, {}, "fake@1")
    assert key != cache.key(project, {}, "fake@2")
    assert key != cache.key(project, {"speed": 2}, "fake@1")
    subtitle = job / "subs.srt"
    subtitle.write_text("old", encoding="utf-8")
    key = cache.key(project, {}, "fake@1", [Path("subs.srt")])
    subtitle.write_text("new", encoding="utf-8")
    assert key != cache.key(project, {}, "fake@1", [Path("subs.srt")])


def test_sentence_cache_malformed_missing_and_corrupt(tmp_path):
    cache = SegmentCache(tmp_path)
    audio = tmp_path / "key.wav"
    write_tone(audio, 0.1)
    audio.with_suffix(".txt").write_text("Hello", encoding="utf-8")
    cache.save("key", 0, 1)
    assert cache.load("key").attempts == 1
    (tmp_path / "key.json").write_text('{"cer":0}', encoding="utf-8")
    assert cache.load("key") is None
    cache.save("key", 0, 1)
    audio.with_suffix(".txt").unlink()
    assert cache.load("key") is None


def test_snapshot_metadata_secret_blocked(tmp_path):
    with pytest.raises(InputInvalid):
        write_json(
            tmp_path / "snapshot.json", {"voice": {"extra": {"authorization": "DO-NOT-PERSIST"}}}
        )
    assert not (tmp_path / "snapshot.json").exists()
