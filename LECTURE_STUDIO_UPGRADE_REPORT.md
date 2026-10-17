# SlideVoice Studio — visual direction upgrade

Date: 2026-10-15. Workspace: `D:\SOFT\STV`.

## Delivered

- Native rendered-line targets from PowerPoint: IDs, parent shape IDs, text,
  normalized bounds, geometry provenance. Shapes remain available as coarse targets.
- Script prompt prefers line targets without accepting LLM-generated coordinates.
- Text circles become padded, antialiased rounded outlines with transparent interiors.
  Shapes without text retain ellipses. Closely packed native lines use an accent
  highlight instead of a potentially overlapping outline, with a timeline warning.
- Highlight uses a low-opacity teal band and a left accent, not a box through letters.
- Zoom uses symmetric cosine easing in/out and a held view, default 1.18×, maximum
  1.3×. Short beats shorten both ramps. Reduced-motion rendering replaces zoom with
  highlight and disables slide fade.
- Offline `storyboard.html`: select each beat and inspect its source region. Narration,
  titles, warnings and target labels are HTML-escaped. This preview is geometry only.
- Responsive Studio player: 9 selectable beats, seek/play, active beat and narration,
  links to visual storyboard, transcript, subtitles and timeline.
- Timeline v2 records actual annotation type, pixel bounds, target text/provenance,
  visual warnings and motion settings.
- Fixed compose dependency fingerprinting so layout/lecture plans are not discarded
  when subtitle output mappings are read. Custom subtitle filenames remain supported.
- Reports explicitly label the hand-authored demo provider rather than claiming real
  LLM generation. Added matching, hash-validated sentence-cache reuse for demo builds.
- No additional runtime dependency.

## PowerPoint-specific issues found and corrected

1. PowerShell selected integer overloads for `Math.Min/Max` when passed `0`/`1`,
   collapsing normalized line bounds. Explicit `0.0`/`1.0` fixes this.
2. PowerPoint `TextRange.BoundHeight` includes paragraph `SpaceAfter` on non-final
   lines. The exporter records the original position/width, measures height with
   SpaceAfter temporarily zero, then restores it. The input presentation is never
   saved. Exported images retain their original paragraph spacing.

Both were reproduced against the actual installed PowerPoint, not inferred from mocks.

## Demo and entry points

- Player: <http://127.0.0.1:8767/studio_v2/> (existing server, no duplicate launched).
- Launcher: `D:\SOFT\STV\OPEN_LECTURE_STUDIO.cmd`.
- Output: `D:\SOFT\STV\out\lecture_demo\studio_v2\lesson\video.mp4`.
- Script review: `D:\SOFT\STV\out\lecture_demo\studio_v2\lesson\work\script\storyboard.html`.
- Config: `D:\SOFT\STV\configs\lecture_vietnamese.yaml`.
- Instructions: `D:\SOFT\STV\PRESENTATION_GUIDE.md`.

PowerPoint `0.2.2`, presenter `0.2.1`, lecture script `0.2.0`.
Three slides, **71.671 s**, **1280×720**, H.264/AAC, Mai Anh cached VieNeu voice.
16 native line targets; all 7 active effects select measured native lines with no
visual warnings. Screenshots show line-only emphasis rather than a whole textbox.
No new synthesis attempts were needed: sentence-cache integrity checks passed.

The previous demo is preserved. Its original manifest says `presenter@0.1.2`,
its historical pytest log really records 95 passed / 1 skipped, and all 126 original
artifact hashes were rechecked and still match. Earlier voice-QA directories were
not modified. New Studio artifacts are in a separate child directory.

## Validation

- Full suite: **109 passed, 1 skipped**. Skip: Windows symlink privileges/Developer Mode.
  Log: `D:\SOFT\STV\out\lecture_setup\studio_pytest.log` and adjacent stderr log.
- Ruff check and format check pass; mypy passes for all 34 application source files.
- New tests cover native target validation, padding/clamping, crowded-line detection,
  motion configuration, short-beat ramps, escaped storyboard, reduced motion,
  transparent outlines, actual decoded annotation pixels and decoded zoom progression.
- Full final audio/video decode, chapter count, duration, audio signal and sentence
  boundary correspondence pass. HTTP page/storyboard/timeline checks and video
  byte-range 206 response pass. SHA256 inventory is in the Studio output directory.
- Nine-stage resume produced only `cache_hit`; no LLM or TTS rerun.
- Player JavaScript passes Node syntax check and a DOM simulation checking all nine
  buttons, seek/play handlers, active beat, narration updates and gap reset.
  This is **not** browser rendering or mobile-layout acceptance testing.
- Actual decoded circle/highlight/zoom screenshots were opened for inspection.

Evidence: `D:\SOFT\STV\out\lecture_demo\studio_v2\validation.json`,
`D:\SOFT\STV\out\lecture_demo\studio_v2\SHA256SUMS.json`,
`D:\SOFT\STV\out\lecture_setup\studio_verify.stderr.log`.
Reproducible verifier: `D:\SOFT\STV\samples\verify_lecture_demo.py`.

## Remaining limits — not production acceptance

- Demo narration and target choices are **hand-authored fixtures**, not a real-provider
  LLM quality evaluation. No external academic research or content verification.
- Human listening, independent ASR and instructor verification remain **false**.
- Line targeting is not phrase/concept/glyph targeting. Rotated/vertical text, groups,
  table internals and image details keep coarse geometry; no OCR/vision was added.
- Line collision handling is conservative; coarse shapes, rotated content and unusual
  typography can still need manual review. PowerPoint geometry is not a universal
  guarantee that no mark can overlap any content.
- Effects follow sentence/segment audio boundaries, not independently aligned words.
- Zoompan is frame-sampled/pixel-quantized, not optical-flow/supersampled camera motion.
- A large textbox may still be chosen by a real model; inspect storyboard and timeline.
- Studio browser layout and complete audio require human playback review. Long mobile
  subtitle segmentation (added in Studio v3 below), review approval gates and real-provider evaluation remain
  sensible next work; no YouTube upload was added.

## Studio v3 follow-up — 2026-10-15

Separate output: `D:\SOFT\STV\out\lecture_demo\studio_v3`.
Player: <http://127.0.0.1:8767/studio_v3/>. The existing v2 launcher is unchanged.

### Delivered

- Presenter `0.3.0`: alpha fades on annotations, default 1 zoom/slide, 1.2-second
  minimum zoom beat and 2-second zoom cooldown. Unsuited zooms become highlights.
  Reduced motion disables both annotation and slide fades and replaces zooms.
- Per-slide hash-validated encoded-clip cache, temporary-file replacement, and
  global frame-boundary rounding to avoid per-slide cumulative timing drift.
  Final H.264 video is stream-copied; mixed/loudness-normalized audio is encoded once.
- Both stage-local and public `presentation_timeline.json` remain available;
  copying instead of moving preserves stage artifacts and repeated-run consumers.
  Timeline records motion settings and clips encoded/reused for its last compose run.
- New `readable_subtitle` plugin: configurable line width and page line count,
  default 42 characters / 2 lines, preserves words and sentence intervals. SRT,
  VTT and ASS share cues. Intra-sentence timing is character-proportional estimation,
  not independent alignment. No new runtime dependencies.
- Player: 0.75–2× speed, previous/next beat, beat repeat, guarded keyboard controls,
  escaped source text, and rejected-play feedback. End-of-file looping is handled.
- Updated lecture config, presentation guide and independent demo verifier.

### Verified against current code

- **126 passed, 1 skipped in 47.22 s**. Skip requires Windows symlink privileges.
  Logs: `D:\SOFT\STV\out\studio_v3_pytest_final.stdout.log`, adjacent stderr log,
  and `D:\SOFT\STV\out\studio_v3_pytest_final.xml`.
- Ruff lint/format and mypy (34 application files) pass.
- Tests cover fade alpha from actual decoded frames, reduced motion, zoom budgets,
  cache reuse after subtitle edits, selective corruption repair, encoder-setting
  invalidation, timeline persistence, multi-slide frame count and full AV decode.
- Compared compressed H.264 coded slices before/after muxing to verify no second
  video encode. Raw packet hashes are not equivalent because concat/container
  conversion inserts parameter sets and changes Annex B / length-prefix framing.
- Node.js dependency-free DOM simulation checks speed, navigation, loop boundaries,
  end-of-file repeat, keyboard guards and rejected playback. This is not an actual
  browser/media implementation test.
- Demo: PowerPoint `0.2.2`, presenter `0.3.0`, cached VieNeu speech, 3 slides,
  **1280×720**, **71.671 s**. Validator checks full AV decode, frame count, chapters,
  exact rounded sentence boundaries, exported caption text/page limits, HTTP 206,
  screenshots and SHA256 inventory. All nine stages resume with `cache_hit`.
- V2 was not regenerated: all **92** entries of its existing SHA256 inventory match.

Evidence: `D:\SOFT\STV\out\lecture_demo\studio_v3\validation.json`,
`D:\SOFT\STV\out\lecture_demo\studio_v3\SHA256SUMS.json`, and
`D:\SOFT\STV\out\lecture_demo\studio_v3\lesson\run_events.json`.

### Still not certified

Human full-length listening, real-browser/mobile interaction acceptance, independent
ASR, real-provider LLM quality and instructor/content verification were not performed.
Caption pages have no maximum reading-speed guarantee; unbroken long tokens can exceed
the configured width. Looping uses media events, not frame-accurate scheduling.
Reduced-motion CSS cannot alter motion already encoded into an MP4. Long-lecture
audio still uses an in-memory timeline buffer; no multi-hour benchmark was performed.
The original slide content and speech were retained; no decorative images or music
were introduced.

## Studio v4 — 24-slide Full-HD scale trial (2026-10-15)

This section supersedes the earlier 3-slide-only/browser-test limitations **only
for the new v4 output**; historical v2/v3 artifacts were not regenerated.

### Research and improvements

- Surveyed Manim Community, ManimGL, Manim Voiceover, WhisperX, reveal.js,
  Auto-Editor and FFmpeg README pages. Findings, licensing boundaries and decisions:
  `D:\SOFT\STV\REPO_RESEARCH_V4.md`. No additional runtime dependency or copied code.
- `readable_subtitle@0.2.1` balances content between pages and then between lines.
  The initial 24-slide export exposed 17 sub-second trailing cues (minimum 0.224s).
  Repartitioning preserves all words and exact sentence endpoints while removing
  this avoidable flashing-caption artifact. Timing is still estimated within a
  sentence; no word-level alignment is claimed.
- Caption diagnostics expose reading rate, shortest cue, page size and overlaps.
  The 20 characters/second flag is a review heuristic, not readability certification.
- Player adds chapter selection by title, previous/next slide, Vietnamese
  accent-insensitive search, subtitle toggle, MP4/PPTX download and explicit
  resume from local storage. Fixed initial update overwriting saved progress.
  Native media errors are visible. No autoplay or system-volume/device changes.
- New 24-slide fixture covers questions, data checks, mean/median, outliers,
  spread, charts, sampling, missing data and qualified conclusions. Illustrative
  bars have direct values; group-comparison examples have A–E labels. Native
  PowerPoint title placeholders populate chapter names. Input-content fingerprints
  detect deck revisions without needlessly invalidating resume caches.

### Verification

- Final full suite: **134 passed, 1 skipped in 47.71s**, exit **0**. Skip is the
  existing Windows symlink privilege requirement. Logs/JUnit/exit status:
  `D:\SOFT\STV\out\studio_v4_pytest_final.stdout.log`,
  `D:\SOFT\STV\out\studio_v4_pytest_final.stderr.log`,
  `D:\SOFT\STV\out\studio_v4_pytest_final.xml`, and
  `D:\SOFT\STV\out\studio_v4_pytest_final.exit.txt`.
- Ruff lint and format check (61 files), mypy (35 application files), and
  dependency-free Node player behavior checks pass with explicit exit 0.
- New regressions cover 24 distinct slide titles and evidence-grounded plans,
  balanced page tails, long unbreakable tokens, token preservation, diagnostics,
  caption toggling, search, slide navigation, storage and end-of-file behavior.
- Real headless Chromium tests play and seek the actual MP4, toggle real text
  tracks, search, reload twice before accepting saved position, and reach EOF.
  Desktop and 390×844 viewport screenshots are saved. This is not merely DOM
  simulation, but remains headless/muted and is not a physical mobile-device test.
- Existing SHA256 inventories rechecked: **92 v2 entries and 98 v3 entries match**.

### Delivery and honest limits

Final verified export: **24 slides, 48 narration beats, 304.067 seconds,
1920×1080 / 30 FPS, H.264/AAC**, 10,074,719 bytes (approximately 10.1 MB).
83 subtitle cues, maximum 2 lines / 42 characters, shortest cue **2.244s**,
maximum estimated 19.75 characters/second, zero sub-second cues and zero overlaps.
Measured final audio: **−16.18 LUFS**, **−4.49 dBTP**. Full AV decode, exact
frame count, sentence timing and HTTP byte-range checks passed. Final verifier
and actual-browser checks both exited 0. Final resume hit all nine stage caches.

Player: <http://127.0.0.1:8767/studio_v4_24slides/>.
Launcher: `D:\SOFT\STV\OPEN_LECTURE_24_SLIDES.cmd`.
Video: `D:\SOFT\STV\out\lecture_demo\studio_v4_24slides\lesson\video.mp4`.
PPTX: `D:\SOFT\STV\out\lecture_demo\studio_v4_24slides\lesson.pptx`.
Independent AV/caption/HTTP evidence: `D:\SOFT\STV\out\lecture_demo\studio_v4_24slides\validation.json`.
Browser evidence: `D:\SOFT\STV\out\lecture_demo\studio_v4_24slides\browser_validation.json`.

This is approximately five minutes of hand-authored demonstration material, not
a multi-hour benchmark or real-provider LLM evaluation. No instructor review,
independent ASR or human full-length listening is claimed. Those flags remain
false. On a narrow portrait display the full slide necessarily shrinks; use
landscape/fullscreen or the large narration panel when needed. Motion remains
restrained; this deck intentionally uses highlight/outline rather than zoom.