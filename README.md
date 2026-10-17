# SlideVoice

Plugin-based slide-to-video orchestration with a Vietnamese lecture demo.
**Status: local/batch preview; not a production multi-tenant service.**

- [Deployment guide](DEPLOYMENT.md) — native install, offline smoke, Linux batch container, operations.
- [Readiness assessment](DEPLOYMENT_READINESS.md) — verified capabilities and release blockers.
- [Security boundaries](SECURITY.md), [license](LICENSE), [third-party notices](THIRD_PARTY_NOTICES.md), [contributing](CONTRIBUTING.md).
- `slidevoice doctor --json-output` checks media tools; add `--config` to check selected plugins.
- `slidevoice smoke --out <absolute-job-path>` exercises the installed package offline with synthetic audio.

The sections below document the original M0 fixtures and subsequent QA additions;
historical counts and host paths are not current deployment guarantees. The
24-slide demo demonstrates orchestration/presentation, not a newly trained model
or an independent LLM/TTS/ASR benchmark.

Lightweight Python orchestration for a plugin-based slide-to-video pipeline.
**The default M0 fixture uses synthetic beeps and a solid background, not voice cloning.**
An optional Windows system-speech QA fixture now produces audible English narration
over downloaded test footage. It does not learn or clone the source video's voices.
No heavyweight model libraries, GPU, network service or LibreOffice are needed for M0.
The architecture and later milestones are specified in [SPEC.md](SPEC.md).

## Lecture presentation mode (new)

PPTX + embedded speaker notes + a compatible LLM API can now produce a structured
teaching script and sentence-synchronous **highlight, ellipse and restrained zoom**.
The `lecture` command uses bundled VieNeu presets without a personal voice file;
`--review-only` produces a storyboard before speech/video synthesis.
See [presentation setup, privacy and limitations](PRESENTATION_GUIDE.md), with the
configuration at `D:\SOFT\STV\configs\lecture_vietnamese.yaml`.
The original fake and voice QA workflows remain available. New LLM/presenter
plugins do not implement all of the production milestones described below.

## Vietnamese GPU voice demo

An optional **VieNeu-TTS v3 Turbo** worker now provides licensed bundled
Vietnamese preset speech on CUDA. Heavy dependencies stay outside core in
`D:\SOFT\STV\workers\vieneu\.venv`.
See [worker setup and limitations](workers/vieneu/README.md).
The reproducible config is `D:\SOFT\STV\configs\qa_vietnamese.yaml` and the
generator is `python -m samples.vietnamese_qa --out D:\SOFT\STV\out\qa_vietnamese_20261015\delivery`.
After generation, `D:\SOFT\STV\OPEN_VIETNAMESE_QA.cmd` opens the local player
on port **8766**, separate from the previous English demo on 8765.
The Vietnamese page includes actual PowerPoint graphics, a main narration voice,
three short 48 kHz preset comparisons, MP4/WebM and a separate narration WAV.
No training or custom voice cloning is performed. Synthetic alignment/CER from
the existing fixture is not an independent assessment of Vietnamese pronunciation.

## Requirements and quick start

Python **3.11+**, ffmpeg and ffprobe on `PATH` (H.264/AAC/mov_text support).
The earlier validation used Python 3.14.7. The Vietnamese integration also has
an editable Python 3.11.15 core environment and a separate GPU worker environment;
72 regression tests passed on both Python 3.11 and 3.14 during this setup.
Wheel packaging remains separate from runtime validation.
From the repository root in PowerShell:

```powershell
python -m pip install -e ".[dev]"
python -m samples.make_samples
slidevoice run --slides samples/demo.pptx --voice samples/voice.wav --config configs/fake.yaml --out out/demo
slidevoice resume out/demo
slidevoice resume out/demo --from-stage tts
slidevoice plugins
slidevoice stage render --slides samples/demo.pptx --config configs/fake.yaml --out out/render
slidevoice preview --slide 2 out/demo --out out/preview2
```

Without editable installation use `python -m slidevoice` instead of `slidevoice`.
Commands elsewhere in this repository that spell out `.\.venv311\Scripts\python.exe`
come from the original Python 3.11 validation environment. `scripts\setup.bat`
creates `.venv`; substitute your own interpreter path for `.venv311`.
`--out` is the **job directory itself**, not a parent in which another job is created.
`preview` requires an existing job and creates an isolated one-slide job. `stage`
runs dependencies through the requested stage; with `--job`, it validates prior
checkpoints and restarts that stage. A render-only job without `--voice` uses an
inert input copy; start a full `run` with a real voice file before rendering audio.

The packaged default YAML mirrors SPEC §6.1, including future real plugin names.
Those plugins are **not implemented in M0**; use `configs/fake.yaml`.
That file explicitly enables consent for the generated synthetic tone; for a human
sample obtain permission before enabling `project.voice_consent`. Never store API
keys in YAML: configure only an environment-variable name such as `api_key_env`.
Use a partial YAML with `resume --config` to override saved settings.

## Output and persistence

`video.mp4` (H.264/AAC, mov_text Vietnamese subtitles, per-slide chapters and AI
metadata), SRT/VTT/ASS, `transcript.md`, `chapters.txt`, `manifest.json`, and JSON/HTML
QA reports. `inputs/` holds copies; source files are never overwritten. Every model
path is job-relative. Each stage has `work/<stage>/cache.json` with its Project
snapshot and content-hashed artifacts. `run_events.json` records execution/cache hits.

Cache keys include input data/content, relevant configuration and plugin versions.
Stage fingerprints are deliberately conservative; an upstream edit may rerun cheap
stages. TTS additionally caches individual sentences using normalized text, prepared
voice content, engine configuration/version, seed, speed and QA settings. Re-running
`run` with the same output directory refreshes input **copies**, so changing a note
only synthesizes changed sentences. Resume uses the existing copies, not the external
originals. Deleted/corrupt artifacts invalidate their checkpoints. `--from-stage`
requires valid earlier checkpoints, forces subsequent stages, and still reuses valid
sentence audio. Remove sentence cache records to force synthesis of unchanged text.

Consent is checked even when all TTS outputs are cached. Treat job directories as
trusted local state. Checkpoints are atomically replaced; **one writer per job** is
required (no concurrent invocations targeting the same directory).

## Audible QA before real voice/slide integration

The previous MP4s contain a measurable beep, **not spoken narration**. Audio stream
presence alone is not acceptance. Reports now measure the **decoded final MP4**:
integrated LUFS, true peak, RMS/peak dBFS and an audible-signal flag. A narrated job
with silent output writes a failed report and exits with an error, including on resume.
This is a signal check, not a human listening test or ASR quality guarantee.

On Windows with Microsoft Zira Desktop installed, use this independent fixture:

```powershell
New-Item -ItemType Directory -Force D:\SOFT\STV\out\qa_audio_20261015 | Out-Null
curl.exe --fail --location --max-time 120 --output D:\SOFT\STV\out\qa_audio_20261015\sintel-trailer.mp4 https://media.w3.org/2010/05/sintel/trailer.mp4
python -m samples.audio_qa --source-video D:\SOFT\STV\out\qa_audio_20261015\sintel-trailer.mp4 --out D:\SOFT\STV\out\qa_audio_20261015\delivery
```

Open `D:\SOFT\STV\out\qa_audio_20261015\delivery\listen.html` manually and press
Play. It presents three controls: generated narration MP4, the same audio as PCM WAV,
and the full downloaded trailer with its original soundtrack normalized. Generated
narration is `D:\SOFT\STV\out\qa_audio_20261015\delivery\narrated\video.mp4`:
1080p H.264/yuv420p, 30 fps, AAC stereo/48 kHz, soft English subtitles and 3 chapters.
The source soundtrack is **not** mixed into this narration video. Attribution and
source/license URLs are included in `ATTRIBUTION.txt`; Sintel is CC BY 3.0, Blender Foundation.

Only English desktop voices are installed in the tested environment. This fixture
explicitly uses `project.language: en`; it must not be presented as Vietnamese speech
or cloned speech. `windows_sapi` rejects Vietnamese instead of silently mispronouncing it.
No third-party Python dependencies or changes to machine execution policy are required.
`configs/qa_speech.yaml` enables consent only for synthetic QA, not for a human sample.
The downloaded background is copied inside the job and content-hashed for compose cache.

## Plugins and workers

### Real-slide playback QA (Windows + installed PowerPoint)

The follow-up fixture exports actual PPTX slide graphics through PowerPoint, then
composes them on the narration timeline. It does not use the fake color composer.
Macros are disabled and the deck is opened read-only without a presentation window.
English system speech remains a diagnostic, not cloned or Vietnamese speech.

```powershell
Set-Location D:\SOFT\STV
python -m samples.slides_qa --out D:\SOFT\STV\out\qa_slides_20261015\delivery
python -m samples.playback --root D:\SOFT\STV\out\qa_slides_20261015\delivery --port 8765
```

Open http://127.0.0.1:8765/ on this machine. Alternatively double-click
`D:\SOFT\STV\OPEN_SLIDE_QA.cmd` to start the loopback server and open the player.
The server supports byte ranges for seeking. The package includes a minimal
H.264 Baseline/AAC MP4, a VP9/Opus WebM fallback, PCM narration and a spoken
left/right channel test. Browser playback and audio-device state evidence are in
`D:\SOFT\STV\out\qa_slides_20261015\delivery`.

The read-only diagnostic `D:\SOFT\STV\samples\audio_device.ps1` found the default
multimedia endpoint **GSX 1200 Pro Main Audio muted at 0%**, while the separate
communications endpoint **HyperX Cloud Flight Wireless was unmuted at 24%**.
These are timestamped QA observations, not live state. No audio-device selection,
mute state or master volume was changed. Select the intended headphones in Windows
before listening. Successful decoding/playback APIs do not prove physical audibility.

Implement an interface from `slidevoice/core/interfaces.py`, then register with
`@register("tts", "my_engine")` or an installed entry point:

```toml
[project.entry-points."slidevoice.plugins"]
"tts.my_engine" = "my_package.engine:Engine"
```

Select it in YAML. Plugin artifact paths returned inside models remain relative to
the job root; plugins resolve them against `self.workdir`. Workers use `GET /health`
and `POST /run` JSON with shared-volume paths. `WorkerClient` has bounded timeouts,
429/5xx/transport retries, sanitized errors, and no binary/base64 file transfer.
Actual workers and provider authentication belong to later milestones.

## Checks

```powershell
python -m ruff check .
python -m ruff format --check .
python -m mypy slidevoice
python -m pytest -q
```

Tests include independent fake-plugin checks, mocked HTTP workers, golden subtitles
and chapters, CLI commands, ffprobe stream/metadata validation, failed-stage resume,
sentence cache invalidation and cached-consent denial. Generated golden fixtures are
reviewable baselines, **not yet architect-approved**.

## Intentional M0 limits

- PPTX-only fake renderer extracts notes/text and produces color PNGs, not slide graphics.
- Fake TTS does not clone a voice; fake alignment reads transcript sidecars. Synthetic
  CER is **not** evidence of ASR or pronunciation quality. LUFS is measured from final
  decoded audio; digital silence has `null` LUFS and fails narrated-output signal QA.
- Sequential stages; parallel slide/voice branches are a later optimization.
- Hard cuts, no avatar, no burn-in or production subtitle splitting/typographic rules.
  Production subtitle requirements belong to M5 and composer effects to M6.
- Recovery from synthesis failure inserts estimated silence after bounded retries;
  that fallback is intentionally not sentence-cached. High-CER audio keeps the best attempt.
- ffmpeg owns the container `encoder` tag; SlideVoice version is stored in
  `encoding_tool` and the video stream's `encoder` tag (SPEC §5.3 clarification needed).
- No UI, real LLM/TTS/ASR workers, production reference cleaning, or real model plugins.
  The static QA playback page and Windows system-speech adapter are diagnostics only,
  not M1–M6 production acceptance.

See [M0_REPORT.md](M0_REPORT.md) for validation results and proposed contract clarifications.