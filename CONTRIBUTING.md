# Contributing

Python 3.11+ is required. Keep GPU/model libraries in isolated workers; do not add
them to core. Public plugin/data contracts are in `SPEC.md`; discuss interface
changes and provide migration tests. Keep real speech quality distinct from
synthetic fixtures and estimated alignment.

```text
python -m pip install -e ".[dev]"
python -m ruff check .
python -m ruff format --check .
python -m mypy slidevoice
python -m pytest -q
python -m build
```

Install FFmpeg/ffprobe and Node.js for AV/player tests. LibreOffice/Poppler tests
skip when the real executables are unavailable; the Linux CI job installs them.
Tests must not require a GPU, provider key, network download or private fixture.
Use a separate job directory per test and exercise failures/cache invalidation.

Never commit `.env`, personal slides/recordings, weights, virtual environments,
generated jobs or build output. Do not claim a container/provider/GPU combination
was validated without actual evidence. Before release use `DEPLOYMENT.md` and
update `DEPLOYMENT_READINESS.md` with observed, not predicted results.