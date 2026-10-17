# Agent instructions for SlideVoice

## Purpose and truthful scope
SlideVoice is a local/batch slide-to-video orchestration project, not a production multi-tenant service. Read `README.md`, `SPEC.md`, `SECURITY.md`, `DEPLOYMENT_READINESS.md`, and `THIRD_PARTY_NOTICES.md` before changing architecture, security boundaries, packaging, or deployment claims. Treat executable code and current tests as authoritative over historical reports and aspirational SPEC milestones.

Do not claim personal voice cloning is exposed by the current pipeline. VieNeu worker supports licensed bundled Vietnamese presets only; it is separate, CUDA-dependent, loopback-only, and not part of core installation. `fake_tts` is synthetic. The fake aligner does not provide independent ASR/forced-alignment evidence. Do not present fixture metrics as independent quality evaluation.

## Workflow
1. Inspect repository status and relevant implementation, tests, config, and CLI before editing. Preserve unrelated user changes; do not reset, clean, or overwrite them.
2. Identify the smallest compatible change. Follow existing Python typing, plugin interfaces, error handling, config validation, and naming conventions. Do not add a dependency without establishing need and compatibility.
3. Add/update tests for behavior changes. Keep offline tests deterministic; do not require GPU, network, API credentials, or private media unless a test explicitly requires them.
4. Run focused tests, then appropriate full checks. Report commands and actual results; never claim checks passed without running them.
5. Review the final diff for secrets, private user data, generated artifacts, licensing notices, and inaccurate documentation. Do not stage or publish private inputs, model weights, credentials, or generated outputs.

## Project map and commands
- CLI and options: `slidevoice/cli.py`; module entry point: `python -m slidevoice`.
- Core config merge/validation: `slidevoice/core/config.py`; packaged defaults: `slidevoice/configs/default.yaml`.
- Pipeline/interfaces: `slidevoice/core/pipeline.py`, `slidevoice/core/interfaces.py`, plugin implementations under `slidevoice/plugins/`.
- Tests: `tests/unit/`, `tests/integration/`, and `tests/golden/`.
- Install development environment: `python -m pip install -e ".[dev]"`.
- Basic offline checks: `python -m slidevoice --help`, `python -m pytest`, and `slidevoice smoke --out <absolute-job-path>` when dependencies are installed.
- Explicit working example config: `configs/fake.yaml`. The packaged default names future/unimplemented plugins; do not imply it runs a complete real pipeline.

## Safety and compatibility
- Follow consent and content-rights requirements in `SECURITY.md`; obtain explicit permission for human voice recordings. Never encourage impersonation.
- Keep API credentials in environment variables, not source, YAML, logs, or examples. Config validation deliberately rejects literal credential keys and credential/query-bearing endpoint URLs.
- Preserve worker restrictions: bind to loopback, constrain writes to allowed job roots, and do not expose unauthenticated worker endpoints to networks.
- Do not loosen input limits, path validation, consent checks, or security tests merely to make a scenario pass. Explain any required behavior change and test it.
- Avoid changing public plugin signatures without reviewing all implementations and tests. Config keys must be accepted by strict validation and packaged config resources kept in sync where relevant.

## Documentation and release
Distinguish implemented behavior, optional integrations, and roadmap/specification. Verify every command, path, plugin name, Python version, and environment variable against code/scripts before documenting it. Review `LICENSE` and `THIRD_PARTY_NOTICES.md`; the project license does not license external dependencies, models, voices, user content, or generated media. A release requires a fresh secret/privacy and license review, passing relevant tests, and explicit confirmation of repository/branch before publishing.
