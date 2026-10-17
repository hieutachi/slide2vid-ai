from pathlib import Path

import pytest

from slidevoice.core.errors import ConsentMissing
from slidevoice.core.media import wav_duration, write_tone
from slidevoice.core.models import Project, Slide, VoiceProfile
from slidevoice.core.pipeline import Pipeline
from slidevoice.plugins.align import FakeAligner
from slidevoice.plugins.avatar import NoAvatar
from slidevoice.plugins.llm import FakeLLM
from slidevoice.plugins.normalize import FakeNormalizer
from slidevoice.plugins.script import FakeScript
from slidevoice.plugins.subtitle import FakeSubtitle
from slidevoice.plugins.tts import FakeTTS


def test_fake_interfaces(tmp_path):
    llm = FakeLLM({}, tmp_path)
    assert llm.complete_json("", "Hello", {}) == {"script": "Hello"}
    script = FakeScript({}, tmp_path)
    slide = script.write(Slide(index=1, notes_raw="Một câu. Câu hai!"), "", llm)
    assert [s.id for s in slide.segments] == ["s001_01", "s001_02"]
    assert script.write(Slide(index=2), "", llm).segments == []
    assert FakeNormalizer({}, tmp_path).normalize(" Xin  chào ", "vi") == "Xin chào"
    assert NoAvatar({}, tmp_path).render(Path("x"), Path("a.wav"), Path("none.mp4")) == Path(
        "none.mp4"
    )


def test_fake_tts_and_alignment(tmp_path):
    engine = FakeTTS({}, tmp_path)
    audio = tmp_path / "a.wav"
    with pytest.raises(ConsentMissing):
        engine.synthesize("Hello", audio)
    with pytest.raises(ConsentMissing):
        engine.load_voice(VoiceProfile(ref_audio=Path("ref.wav"), ref_text="test", language="vi"))
    engine.load_voice(
        VoiceProfile(
            ref_audio=Path("ref.wav"), ref_text="test", language="vi", consent_confirmed=True
        )
    )
    duration = engine.synthesize("Xin chào", audio)
    assert duration == wav_duration(audio)
    aligner = FakeAligner({}, tmp_path)
    assert aligner.transcribe(audio, "vi") == "Xin chào"
    words = aligner.align(audio, "Xin chào", "vi")
    assert words[0].start == 0
    assert words[-1].end == duration


def test_renderer_voice_subtitle(job):
    project = Pipeline(job).run(until="voice")
    assert len(project.slides) == 3
    assert project.slides[0].title == "Giới thiệu"
    assert project.slides[0].image_path.suffix == ".png"
    assert project.voice.consent_confirmed is True
    import wave

    with wave.open(str(job / project.voice.ref_audio), "rb") as audio:
        assert audio.getframerate() == 24000
        assert audio.getnchannels() == 1
    output = job / "subtest"
    output.mkdir()
    paths = FakeSubtitle({}, job).write(project, output)
    assert set(paths) == {"srt", "vtt", "ass"}
    assert (job / paths["vtt"]).read_text(encoding="utf-8").startswith("WEBVTT")


def test_timeline_uses_audio_not_reported_duration(job):
    pipeline = Pipeline(job)
    project = pipeline.run(until="voice")
    for i, slide in enumerate(project.slides):
        for j, seg in enumerate(slide.segments):
            path = job / f"{i}_{j}.wav"
            write_tone(path, 0.123)
            seg.audio_path = path.relative_to(job)
    pipeline.timeline(project)
    for slide in project.slides:
        for seg in slide.segments:
            assert seg.end - seg.start == pytest.approx(0.123)


def test_failure_falls_back_to_silence(job):
    project = Pipeline(job, {"tts": {"fail": True}, "qa": {"max_retries": 1}}).run(until="tts")
    assert len(project.warnings) == 4
    assert all(
        seg.attempts == 2 and seg.cer is None and seg.audio_path
        for s in project.slides
        for seg in s.segments
    )


def test_high_cer_keeps_best_attempt(job, monkeypatch):
    seen = []
    original = FakeTTS.synthesize

    def synth(self, text, out_path, speed=1.0):
        seen.append(self.config["seed"])
        return original(self, text, out_path, speed)

    monkeypatch.setattr(FakeTTS, "synthesize", synth)
    monkeypatch.setattr(FakeAligner, "transcribe", lambda *_: "wrong")
    project = Pipeline(job, {"qa": {"max_retries": 1}}).run(until="tts")
    assert seen == [42, 43] * 4
    assert len(project.warnings) == 4
    assert all(seg.attempts == 2 and seg.cer > 0.15 for s in project.slides for seg in s.segments)


def test_empty_slide_warning(job):
    pipeline = Pipeline(job)
    project = Project(
        job_id="x",
        source_slides=Path("inputs/slides.pptx"),
        source_voice=Path("inputs/voice.wav"),
        slides=[Slide(index=1)],
    )
    pipeline.timeline(project)
    assert project.slides[0].end == 3
    assert "no narration" in project.warnings[0]
