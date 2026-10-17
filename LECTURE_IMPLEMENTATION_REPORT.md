# Lecture presentation implementation — 2026-10-15

## Delivered

- `D:\SOFT\STV\slidevoice\plugins\llm\openai_compat.py`: HTTP Chat Completions
  JSON adapter; environment credentials, bounded transport/429/5xx retries,
  no raw provider errors, no redirect following. Real provider not evaluated.
- `D:\SOFT\STV\slidevoice\plugins\script\lecture.py`: grounded lecture JSON,
  validated beats, exact input evidence quotes, shape references and word budget.
- `D:\SOFT\STV\slidevoice\core\presentation.py`: PPTX layout extraction,
  plan models and actual sentence-audio timeline compilation. Core model/interface
  contracts unchanged; sidecar artifacts are hashed by pipeline caches.
- `D:\SOFT\STV\slidevoice\plugins\compose\presenter.py`: highlight, ellipse,
  limited zoom, short fade-up; effects bounded to sentence narration intervals.
- `D:\SOFT\STV\configs\lecture_vietnamese.yaml`: presets, audience/style,
  LLM environment settings, 1080p output, restrained effect budget.
- `lecture --review-only` / `resume`: script preview before GPU synthesis;
  bundled VieNeu preset preparation needs no personal reference recording.
- `D:\SOFT\STV\PRESENTATION_GUIDE.md`: commands, data disclosure, limitations.
- `D:\SOFT\STV\samples\lecture_demo.py`: explicitly hand-authored teaching
  fixture, not a fabricated claim of a successful real LLM evaluation.
- `D:\SOFT\STV\OPEN_LECTURE_DEMO.cmd`: player launcher, separate port 8767.

## Verified in this session

- Final regression: **95 passed, 1 skipped in 35.81 seconds**. Skip is the existing
  Windows symlink privilege case. Log:
  `D:\SOFT\STV\out\lecture_setup\pytest_verified.log`.
- Ruff check: passed across workspace. Ruff format check: 59 files formatted.
  Strict mypy: passed, 33 source files.
- Added 23 tests, including malformed plans/evidence/targets, word budget,
  HTTP adapter modes/retries/sanitization, preset restrictions, CLI review,
  sidecar corruption and cache recovery, decoded effect pixels and stroke width.
- Actual demo used installed PowerPoint and VieNeu on **NVIDIA GeForce RTX 3090**.
  Worker health confirmed pinned model/codec and CUDA Torch 2.8.0+cu128.
- `D:\SOFT\STV\out\lecture_demo\lesson\video.mp4`: 3 slides, 71.671 seconds,
  1280×720 H.264, AAC 48 kHz, soft Vietnamese subtitles, 3 chapters.
- Decoded audio: -16.21 LUFS, true peak -4.33 dBTP, no silent narration segments.
- Whole video/audio decoded with FFmpeg `-xerror`; timeline timestamps matched
  manifest segment boundaries; duration within one frame of the narration timeline.
- Local player HTTP 200, range request HTTP 206 with exactly 1024 requested bytes.
  Not a claim of automated browser playback or human listening in this session.
- 126 delivered file SHA-256 hashes verified after regeneration; evidence:
  `D:\SOFT\STV\out\lecture_demo\validation.json` and `SHA256SUMS.json`.
- Final demo composer: `presenter@0.1.2`. Ellipse stroke thickness corrected and
  tested; inspection still found coarse target selection described below.

## Outstanding quality gaps — not production acceptance

1. **Shape-level targeting is coarse.** The current demo circles a whole wide
   textbox; the ellipse crosses some text and includes unnecessary empty space.
   It is an implemented effect, NOT a polished pedagogical annotation. Next work:
   per-line/concept bounds, padded outline/callout selection and visual QA rules.
2. Zoom is a sentence-level cut to a mildly enlarged crop, not smooth camera motion.
   Original PowerPoint animations are not preserved.
3. No real LLM API key was available. HTTP behavior is mocked in tests; generation
   quality and compatibility with a specific real provider remain unverified.
4. No vision/OCR, independent ASR, external research, RAG, citation verification,
   mandatory human approval gate or YouTube upload. Notes must explain diagrams.
5. Traceable quotes do not prove correct interpretation. An instructor must verify
   the resulting academic content; exact-source checking is not fact-checking.
6. Long decks/context windows, many-hour timelines and mobile subtitle layout
   remain unbenchmarked. Current final audio assembly holds PCM in memory.
7. Full deck text/notes/shape descriptions are sent to the configured LLM provider.
   Confirm permission/privacy requirements before processing real student material.

Human listening, independent ASR and academic verification flags remain **false**.
No training, fine-tuning or custom voice cloning was performed.

## Listening entry points

- `http://127.0.0.1:8767/` while the local player is running.
- `D:\SOFT\STV\OPEN_LECTURE_DEMO.cmd` to restart/open playback.
- `D:\SOFT\STV\out\lecture_demo\lesson\work\script\storyboard.md` for the script.
- `D:\SOFT\STV\out\lecture_demo\lesson\presentation_timeline.json` for effects.

Worker 8770 and player 8767 were started for this task. Existing voice QA outputs
were not replaced; the new demo is in a separate output directory.