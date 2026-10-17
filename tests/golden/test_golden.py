from pathlib import Path

from slidevoice.core.pipeline import Pipeline


def test_sample_subtitles_and_chapters_match_reviewed_fixtures(job):
    # Packaging now measures the final MP4; exercise the complete pipeline rather
    # than generating a misleading green report before composition.
    Pipeline(job).run()
    fixtures = Path(__file__).resolve().parent / "fixtures"
    for name in ("subtitles.srt", "subtitles.vtt", "subtitles.ass", "chapters.txt"):
        assert (job / name).read_text(encoding="utf-8").rstrip() == (fixtures / name).read_text(
            encoding="utf-8"
        ).rstrip()
