# SlideVoice — Vietnamese GPU voice demo

Date: 2026-10-15. This is a pretrained **preset voice** demonstration, not custom
voice cloning, fine-tuning, or proof of human-level pronunciation quality.

## Listen

- Local player: http://127.0.0.1:8766/ (workspace machine only).
- Restart player: `D:\SOFT\STV\OPEN_VIETNAMESE_QA.cmd`.
- Delivery: `D:\SOFT\STV\out\qa_vietnamese_20261015\delivery`.
- Main video: `slides_compatible.mp4` — **Mai Anh**, three actual PowerPoint slides.
- Separate narration: `narrated\audio_check.wav`.
- Native 48 kHz comparisons, same text:
  - `voice_samples\voice_01.native48k.wav`: Mai Anh, 11.92 s.
  - `voice_samples\voice_02.native48k.wav`: Hải Đăng, 10.08 s.
  - `voice_samples\voice_03.native48k.wav`: Thùy Dung, 10.08 s.

The page does not autoplay or modify Windows volume/output routing. Confirmation
of the previous English playback is not treated as listening to this new output.

## Installed locally

- AMD Ryzen 9 9950X; ~125.38 GiB reported RAM; NVIDIA RTX 3090, 24 GiB VRAM.
- Python 3.11.15 worker, VieNeu SDK **3.8.3**, Torch/Torchaudio **2.8.0+cu128**,
  Transformers **4.57.6**. Actual CUDA inference confirmed, no CPU fallback.
- VieNeu-TTS v3 Turbo revision `61b85e3d937fbbacb387714180e8182823512523`.
- MOSS-Audio-Tokenizer-Nano revision `6aa02b01e445cc585582cf0ba480bc3ea6c8dd68`.
- 25 bundled presets available. Only preset synthesis is exposed by the worker;
  input reference audio is never sent to the model or used for cloning/training.
- Model cache: `D:\SOFT\STV\models\vieneu`.
- Isolated environment: `D:\SOFT\STV\workers\vieneu\.venv`.
- Official CUDA Torch wheel SHA256 verified:
  `34c55443aafd31046a7963b63d30bc3b628ee4a704f826796c865fdfd05bb596`.

## Observed technical results

- MP4: **1280×720**, H.264 Constrained Baseline, AAC-LC stereo **48 kHz**,
  duration **35.737 s**, faststart. WebM VP9/Opus fallback also fully decoded.
- Final decoded MP4 audio: **−16.01 LUFS**, **−4.50 dBTP**, RMS **−19.1 dBFS**;
  audible-signal check passed. These are signal checks, not speech recognition.
- Chrome real-time probe: **4.938 s** playback, **153** frames,
  **107,633** decoded audio bytes, no media error, not muted.
- Byte-range request returned **206** with exactly **1024 bytes**.
- Nine synthesis requests: **63.2 s** native audio in **7.0765 s** measured
  generation time, aggregate **RTF 0.112 (~8.93× real-time)**. Excludes download,
  model load, resampling and video rendering; it is not a training benchmark.
- Pipeline completed without warnings. Native 48 kHz PCM retained; core video
  composition currently uses 24 kHz mono sentence PCM before AAC output.
- Python 3.11 final regression: **72 passed, 1 skipped**. The skip is the symlink
  creation test because Windows requires Developer Mode/privileges; neither was
  enabled. Python 3.14 earlier regression: 72 passed before that extra skip test.
- Ruff check/format and strict mypy on core passed. Worker syntax/static checks
  and dependency consistency passed. Runtime/installation do not validate wheels.

Evidence: `qa_checks.json`, `browser_runtime.json`, `browser_screenshot.png`,
`worker_health.json`, `available_voices.json`, `validation/`, `SHA256SUMS.json`.

## Quality and training decision

**human_listening_verified: false** for this Vietnamese output.
**independent_asr_verified: false**. Alignment, per-word timestamps and CER are
still the existing synthetic text-sidecar fixture; a zero fixture CER must not be
represented as independently verified pronunciation accuracy.

No training performed. First select the preferred preset and assess clarity,
prosody, accent, speaking pace and any omitted/repeated words on held-out text.
If domain-specific readings or a consented custom voice genuinely require it,
the publisher documents LoRA fine-tuning on a consumer GPU. Its suggested starting
dataset is **10–30 minutes / 100–300 varied sentences**, one consenting speaker,
clean recordings with accurate transcripts, clips 1–20 seconds. This is publisher
guidance, not a quality guarantee. Keep a separate evaluation set, compare against
the pretrained baseline, and stop on validation plateau/regression rather than
training indefinitely. A 3090 is suitable for trying that workflow; no local
training/VRAM benchmark has been run here.

## Rights and sources

- [VieNeu source and installation](https://github.com/pnnbao97/VieNeu-TTS).
- [Model/preset licensing statement](https://huggingface.co/pnnbao-ump/VieNeu-TTS-v3-Turbo#-usage-rights--licensing-faq).
  The publisher explicitly states bundled preset assets and weights are Apache-2.0,
  permits commercial generated audio, and confirms rights/consent for those presets.
  This is a publisher statement, not an independent legal audit.
- [MOSS codec](https://huggingface.co/OpenMOSS-Team/MOSS-Audio-Tokenizer-Nano), Apache-2.0.
- [Publisher LoRA guide](https://github.com/pnnbao97/VieNeu-TTS/blob/main/finetune/README.md).

Model weights are not included in the listening ZIP. Source/license attribution
is retained in `ATTRIBUTION.txt` and `LICENSE_VieNeu.txt`. No audio/slides were
uploaded to a remote TTS service. Worker and player bind **127.0.0.1 only** on
8770 and 8766 respectively. No Windows device, mute, volume or execution-policy
settings were changed.