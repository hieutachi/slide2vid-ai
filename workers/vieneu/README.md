# VieNeu GPU worker (Windows / Python 3.11)

This environment is isolated from SlideVoice core. Model: VieNeu-TTS v3 Turbo,
SDK 3.8.3, PyTorch 2.8.0 CUDA 12.8, Transformers 4.57.6. Only the publisher's
licensed bundled presets are exposed; personal voice cloning is not available
through this worker.

From the repository root in PowerShell, create the worker environment and install
its dependencies. The CUDA wheel index and versions must match the worker setup:

```powershell
python -m venv workers\vieneu\.venv
workers\vieneu\.venv\Scripts\python.exe -m pip install --upgrade pip setuptools wheel
workers\vieneu\.venv\Scripts\python.exe -m pip install torch==2.8.0 torchaudio==2.8.0 --index-url https://download.pytorch.org/whl/cu128
workers\vieneu\.venv\Scripts\python.exe -m pip install -r workers\vieneu\requirements.txt
workers\vieneu\.venv\Scripts\python.exe workers\vieneu\download_models.py --cache-root D:\SOFT\STV\models\vieneu
workers\vieneu\.venv\Scripts\python.exe workers\vieneu\server.py --allowed-root D:\SOFT\STV\out --cache-root D:\SOFT\STV\models\vieneu --port 8770
```

The downloader pins model/codec revisions in `pinned_models.json`; the codec
includes publisher Python code loaded by Transformers, confined to the worker
environment. First inference may additionally download phonemizer assets. No local
slides or audio are uploaded. The service binds **127.0.0.1 only**, rejects
browser-origin requests, and allows writes only within the configured output
root. Native 48 kHz PCM is retained next to pipeline-compatible 24 kHz PCM. Do
not expose this unauthenticated local worker to a network.

Generate the QA demo with the core environment and the worker running:

```powershell
.venv\Scripts\python.exe -m samples.vietnamese_qa --out D:\SOFT\STV\out\qa_vietnamese\delivery
```

## Rights and quality limits

- [Source](https://github.com/pnnbao97/VieNeu-TTS)
- [Model and preset usage-rights statement](https://huggingface.co/pnnbao-ump/VieNeu-TTS-v3-Turbo#-usage-rights--licensing-faq)
- Model/presets: Apache-2.0 per publisher; keep attribution/license notices when redistributing.
- `fake_align` uses text sidecars. Its CER and word timestamps are **not** independent ASR or forced-alignment evidence. Listening remains required.
- The worker metrics set `human_listening_verified` to false; only a human listener can change the quality assessment.

# VieNeu GPU worker (Windows / Python 3.11)

This environment is isolated from SlideVoice core. Model: VieNeu-TTS v3 Turbo,
SDK 3.8.3, PyTorch 2.8.0 CUDA 12.8, Transformers 4.57.6.
Only the publisher's licensed bundled presets are exposed, not voice cloning.

From `D:\SOFT\STV`:

```powershell
uv venv --python .venv311\Scripts\python.exe workers\vieneu\.venv
uv pip install --python workers\vieneu\.venv\Scripts\python.exe torch==2.8.0 torchaudio==2.8.0 --index-url https://download.pytorch.org/whl/cu128
uv pip install --python workers\vieneu\.venv\Scripts\python.exe -r workers\vieneu\requirements.txt
workers\vieneu\.venv\Scripts\python.exe workers\vieneu\download_models.py --cache-root D:\SOFT\STV\models\vieneu
workers\vieneu\.venv\Scripts\python.exe workers\vieneu\server.py --allowed-root D:\SOFT\STV\out --cache-root D:\SOFT\STV\models\vieneu --port 8770
```

The downloader pins model/codec revisions in `pinned_models.json`; the codec
includes publisher Python code loaded by Transformers, confined to the worker
environment. First inference may additionally download phonemizer assets. No local
slides or audio are uploaded. The service binds **127.0.0.1 only**, rejects
browser-origin requests, and allows writes only within the configured output
root. Native 48 kHz PCM is retained next to pipeline-compatible 24 kHz PCM.
Do not expose this unauthenticated local worker to a network.

Generate the demo with the worker running:

```powershell
.venv311\Scripts\python.exe -m samples.vietnamese_qa --out D:\SOFT\STV\out\qa_vietnamese_20261015\delivery
```

## Rights and quality limits

- [Source](https://github.com/pnnbao97/VieNeu-TTS)
- [Model and preset usage-rights statement](https://huggingface.co/pnnbao-ump/VieNeu-TTS-v3-Turbo#-usage-rights--licensing-faq)
- Model/presets: Apache-2.0 per publisher; keep attribution/license notices when redistributing.
- No from-scratch training or fine-tuning is needed to test preset quality.
  Fine-tuning requires suitable recordings, transcripts, rights/consent and a
  held-out evaluation set; better hardware alone cannot supply these.
- `fake_align` uses text sidecars. Its CER and word timestamps are **not**
  independent ASR or forced-alignment evidence. Listening remains required.
- `human_listening_verified` remains false for this new Vietnamese output until
  the user actually listens; confirmation of the older English demo is separate.