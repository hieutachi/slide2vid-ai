"""Objective caption diagnostics; deliberately not a claim of word alignment."""

from itertools import pairwise
from typing import Any


def caption_diagnostics(cues: list[tuple[float, float, str]]) -> dict[str, Any]:
    durations = [end - start for start, end, _ in cues]
    speeds = [
        len(text.replace("\n", " ")) / (end - start) for start, end, text in cues if end > start
    ]
    return {
        "cues": len(cues),
        "timing_basis": "estimated within sentence; not word alignment",
        "max_lines": max((len(text.splitlines()) for _, _, text in cues), default=0),
        "max_line_characters": max(
            (len(line) for _, _, text in cues for line in text.splitlines()), default=0
        ),
        "minimum_duration_seconds": round(min(durations), 3) if durations else None,
        "maximum_characters_per_second": round(max(speeds), 2) if speeds else None,
        "over_20_characters_per_second": sum(speed > 20 for speed in speeds),
        "under_one_second": sum(duration < 1 for duration in durations),
        "invalid_intervals": sum(duration <= 0 for duration in durations),
        "overlaps": sum(left[1] > right[0] for left, right in pairwise(cues)),
        "notice": "20 characters/second is a review flag, not a universal readability threshold.",
    }
