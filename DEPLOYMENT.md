# Deployment guide — single-operator batch, not a public SaaS

## Supported scope and quality boundaries

Use SlideVoice locally or behind your own trusted batch supervisor. The runnable
offline smoke is synthetic. The current real Vietnamese path uses a separately
installed CUDA VieNeu preset worker; this container does **not** include a TTS
model, GPU runtime or a finished speech/ASR evaluation stack.

`doctor` checks prerequisites, not security or teaching quality. A green smoke
only proves packaging/media orchestration. Defaults still list future plugin
names from SPEC; use an explicit working config for full jobs.

Read `SECURITY.md`, `THIRD_PARTY_NOTICES.md` and `DEPLOYMENT_READINESS.md` first.

## Native installation

Python 3.11+ and FFmpeg/ffprobe with libx264/AAC/mov_text/loudnorm are required.
For real Linux slide images install LibreOffice Impress, Poppler utilities and
fonts used by the deck. Do not substitute PowerPoint COM automation in a server
container. Keep the core environment independent of the GPU worker.

From the checkout (Windows example with absolute paths):

```powershell
Set-Location D:\SOFT\STV
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\slidevoice.exe doctor --json-output
.\.venv\Scripts\slidevoice.exe doctor --config D:\SOFT\STV\configs\fake.yaml --json-output
.\.venv\Scripts\slidevoice.exe smoke --out D:\SOFT\STV\out\installed_smoke
.\.venv\Scripts\slidevoice.exe resume D:\SOFT\STV\out\installed_smoke
```

Release installation must also pass **outside the checkout**:

```powershell
python -m build D:\SOFT\STV
python -m venv D:\SOFT\STV\out\wheel-env
# Replace with the actual wheel path emitted by build; do not install the sdist here.
D:\SOFT\STV\out\wheel-env\Scripts\python.exe -m pip install D:\SOFT\STV\dist\slidevoice-0.1.0-py3-none-any.whl
Set-Location D:\SOFT\STV\out
D:\SOFT\STV\out\wheel-env\Scripts\slidevoice.exe doctor --json-output
D:\SOFT\STV\out\wheel-env\Scripts\slidevoice.exe smoke --out D:\SOFT\STV\out\wheel_smoke
```

The installed `smoke` uses packaged resources and generates its own harmless
fixtures, without importing `samples`, downloading media or using a provider.

## Restricted CPU container

Build with Docker on a Linux runner. The image includes system FFmpeg,
LibreOffice/Poppler and distro fonts, but no GPU model and no network listener.
It runs as UID/GID 10001. Named volume ownership is initialized from `/data`;
bind mounts must already be writable by that UID. Preserve `/data` to resume.

```text
docker build -t slidevoice:local D:\SOFT\STV
docker volume create slidevoice-jobs
docker run --rm --network none --read-only --cap-drop ALL --security-opt no-new-privileges --memory 2g --cpus 2 --pids-limit 256 --tmpfs /tmp:rw,nosuid,size=512m -v slidevoice-jobs:/data slidevoice:local doctor --json-output
docker run --rm --network none --read-only --cap-drop ALL --security-opt no-new-privileges --memory 2g --cpus 2 --pids-limit 256 --tmpfs /tmp:rw,nosuid,size=512m -v slidevoice-jobs:/data slidevoice:local smoke --out /data/smoke
docker run --rm --network none --read-only --cap-drop ALL --security-opt no-new-privileges --memory 2g --cpus 2 --pids-limit 256 --tmpfs /tmp:rw,nosuid,size=512m -v slidevoice-jobs:/data slidevoice:local resume /data/smoke
docker run --rm --network none --read-only --cap-drop ALL --security-opt no-new-privileges --memory 2g --cpus 2 --pids-limit 256 --tmpfs /tmp:rw,nosuid,size=512m -v slidevoice-jobs:/data slidevoice:local stage render --slides /data/smoke/inputs/slides.pptx --out /data/real-render
```

Paths such as `/data/smoke` above are absolute **container** paths. For deployment
outside this Windows checkout, substitute its actual absolute host path.
No ports are published. An HTTP liveness healthcheck is inappropriate for this
finite batch process; observe exit status and job telemetry through a supervisor.
Increase resource budgets for 1080p/large decks after measuring your workload.
The checked-in base tag/dependencies are not a reproducibility lock: resolve,
audit, record an SBOM and pin image digests/dependencies for an actual release.

## Real Vietnamese lectures

On Windows use the reviewed `configs/lecture_vietnamese.yaml`, set the provider
model and its environment key, then follow `PRESENTATION_GUIDE.md`. Do not put
keys in YAML. The lecture command supports a config selecting `libreoffice`
instead of `powerpoint`; real font/layout parity and native PDF export still
need the Linux integration test and visual checks on representative decks.

VieNeu's worker remains **loopback-only** with a host-shared job directory.
Container-to-host GPU networking is deliberately not configured or claimed as
validated. Do not weaken that restriction to make a quick public API. Finish
worker identity/authentication, request admission, path mapping, bounded queues
and model/license review before designing a networked GPU topology.

The current `fake_align` text sidecar is not independent ASR. Caption pagination
improves readability, but cannot verify pronunciation or per-word timing.
Teacher/human listening review is required before publishing a real course.

## State, failures and operations

- One writer per job on a local filesystem, enforced with OS locks for creation,
  refresh and pipeline runs. Different jobs may run independently. Multiple TTS
  jobs still need an external GPU admission policy; there is no distributed queue.
- `run_status.json` records running/paused/completed/failed/interrupted, current
  stage and UTC times. Error type only is persisted, not arbitrary exception text.
  A SIGKILL/power loss cannot update telemetry; check the actual process/supervisor.
- Atomic checkpoint writes use unique same-directory temporary files, flush and
  fsync before replacement. This is not a multi-file transactional database or
  a promise of power-failure durability for the whole job.
- Keep the lock file; process death releases its OS ownership. Never delete it
  to bypass contention. Inspect stale state, then use `resume` normally.
- Back up source/config/checkpoints/artifacts together, encrypt sensitive backups,
  and test restoration. Do not place credentials in the job. Review retention
  policy for slides, voices and narration; nothing auto-deletes user jobs.
- Set disk quotas externally. Size limits bound metadata-declared input resource
  use, not total render output. No hostile tenant isolation is provided.
- Publish only approved MP4, captions, chapter/transcript and player files to a
  proper static server/object store; do not expose `inputs`, `work`, configuration
  and manifests by serving a complete job root.

## Release validation

```powershell
Set-Location D:\SOFT\STV
.\.venv311\Scripts\python.exe -m samples.validate_release --out D:\SOFT\STV\out\release_checks
```

This records each command's logs and exit code plus JUnit XML. GitHub CI also
defines Windows/Linux/Python matrices, real LibreOffice checks, clean wheel
execution and restricted container checks. A committed workflow is **not** a
passing run: inspect the remote results before tagging/publishing.

When `uv` and its build/dependency cache are already provisioned, the additional
offline distribution validator builds wheel/sdist, checks their contents and
runs the installed wheel outside the checkout:

```powershell
Set-Location D:\SOFT\STV
.\.venv311\Scripts\python.exe -m samples.validate_distribution --out D:\SOFT\STV\out\distribution_checks
```

It intentionally uses `--offline`: missing cache is a validation failure, not
permission to fetch new dependencies. Normal networked release CI uses the
documented `python -m build` path. Use a separate output root per release version.