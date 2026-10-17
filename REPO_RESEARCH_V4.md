# Studio v4 — repository survey and engineering decisions

Inspected public repository README pages on 2026-10-15. This is a targeted
comparison, not an exhaustive search, performance comparison, or code audit.
No source code was copied or third-party runtime dependency added.

| Repository | Documented capability / license | Decision for SlideVoice |
|---|---|---|
| [Manim Community](https://github.com/ManimCommunity/manim) | Programmatic explanatory mathematical animation; MIT licenses | Retain original PowerPoint raster exports, not recreate every slide as a scene. Use restrained emphasis as a design choice, not a claim Manim automatically understands PPTX. |
| [ManimGL](https://github.com/3b1b/manim) | Precise programmatic animation; MIT | Scene authoring is useful for bespoke lessons, not a drop-in renderer for arbitrary slides. Not installed. |
| [Manim Voiceover](https://github.com/ManimCommunity/manim-voiceover) | Voiceover and per-word animation timing using Whisper; MIT | Keep actions attached to actual sentence WAV boundaries. Word-level triggering would require real alignment; do not represent synthetic word estimates as measurements. |
| [WhisperX](https://github.com/m-bain/whisperX) | ASR, forced word alignment, diarization; BSD-2-Clause repository license | Candidate for a separate worker. Language-specific alignment models, GPU dependencies and unalignable tokens need evaluation. Not installed or evaluated against this Vietnamese demo. |
| [reveal.js](https://github.com/hakimel/reveal.js) | Browser presentations, nested slides, notes, API; MIT | Add semantic chapter navigation, lesson search and saved viewing position to the existing dependency-free player. These are local implementations, not reveal.js integration. |
| [Auto-Editor](https://github.com/WyattBlue/auto-editor) | Loudness-based automatic cuts; Unlicense source, binary licensing may differ | Do not cut silence after building the timeline. That would move narration, captions, annotations and chapter boundaries. Pauses are intentional teaching time. |
| [FFmpeg](https://github.com/FFmpeg/FFmpeg) | Multimedia processing, filters, muxing and probing; mainly LGPL with optional GPL components | Continue single-encode slide clips and stream-copy final H.264; independently decode final AV, inspect frames, duration and chapters. Installed binary licensing depends on its build. |

One guessed PPTX2Video repository URL returned HTTP 404 and was excluded; no
capabilities were inferred from it. Repository search discovery did not return
a relevant GitHub tool, so the pages above were fetched directly.

## Changes motivated by this pass

- `D:\SOFT\STV\slidevoice\plugins\subtitle\__init__.py`: distribute sentence
  words across feasible caption pages, then balance line lengths. Prevent the
  very short trailing pages found in the initial 24-slide render. Preserve
  original sentence timing, token order, maximum lines and width (except a
  single unbreakable token). Still character-proportional timing, not alignment.
- `D:\SOFT\STV\slidevoice\report\captions.py`: expose duration, character-rate,
  overlap and page-size diagnostics. A 20 characters/second flag is a review
  heuristic, not a universal readability certificate.
- `D:\SOFT\STV\samples\lecture_player.html`: chapter selector, slide navigation,
  Vietnamese accent-insensitive search, caption toggle, optional explicit resume,
  MP4/PPTX download links and visible media errors. Saved position stays local;
  playback does not resume automatically. Private-mode storage failures are caught.
- `D:\SOFT\STV\samples\lecture_long_demo.py` and content module: 24 distinct
  hand-authored slides, native title placeholders, direct-labelled illustrative
  bars, embedded notes and a reproducible Full-HD export. Content fingerprints
  detect deck revisions without regenerating input bytes on every resume.
- `D:\SOFT\STV\samples\check_lecture_browser.cjs`: real headless Chromium CDP
  media test using Node's built-in WebSocket. Desktop and 390px mobile viewport
  are tested; this is not a physical mobile-device or human-listening test.

## Boundaries

The demo is a 24-slide **scale trial**, around five minutes, not a multi-hour
benchmark or a validated university lecture. Script generation is an explicitly
labelled hand-authored fixture. No real LLM provider, independent ASR, instructor
review or full-length human listening is claimed. No music, avatar or visual
restyling of existing user slides was introduced. V2 and v3 outputs are preserved.