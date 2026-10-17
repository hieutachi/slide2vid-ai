# Security policy

SlideVoice is currently a single-operator, local batch application. There is no
supported public multi-tenant API. Do not expose `samples.playback` or the VieNeu
worker to the Internet, publish whole job directories, or execute untrusted
plugins. Python plugin entry points execute arbitrary code with operator rights.

## Boundaries

- Keep credentials in process environment variables, not YAML or job files.
- Slides/notes may be sent to an LLM endpoint selected by the operator. Review
  provider retention and get permission before processing confidential material.
- Input checks bound PPTX metadata sizes and reject macro/OLE/ActiveX members;
  they are **not** antivirus, XML validation or an Office sandbox. Render unknown
  documents in a restricted disposable container/VM without secrets/network.
- Job paths and shared GPU worker volumes belong to one trusted operator. Do not
  allow another user to mutate them during processing. Symlink checks do not
  provide a hostile-filesystem TOCTOU sandbox.
- OS locks coordinate local processes only. NFS/SMB, distributed job scheduling
  and hostile tenants are not supported.
- Hard kills can leave `run_status.json` at `running`; it is historical telemetry,
  not a heartbeat. OS locks are released on process exit. Resume after inspecting
  the supervisor/process state; never delete a lock file to force ownership.
- Job roots contain source slides, intermediate text, narration and provenance.
  Serve only reviewed public artifacts through a proper static server/object
  store with authentication/TLS and retention controls where needed.

## Reporting

No public reporting address/repository has been configured in this workspace.
Before publishing a repository, the maintainer must enable private vulnerability
reporting or document a monitored private contact. Do not post secrets, personal
recordings, harmful documents or sensitive job manifests in public issues.

Only the latest reviewed release is intended to receive security fixes. No
formal support window, external audit or vulnerability-free guarantee exists.