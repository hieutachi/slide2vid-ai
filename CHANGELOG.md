# Changelog

## Unreleased — deployment hardening

- Add MIT license and contributor/security/third-party documentation.
- Add OS-backed single-writer job locks, crash-release coverage, unique/fsynced
  atomic JSON writes, per-run status and clean per-invocation event tracking.
- Bound PPTX input sizes, package members, slides and render resource settings;
  reject macro/OLE/ActiveX content before copying/parsing pipeline inputs.
- Add `slidevoice doctor --json-output` and packaged offline `slidevoice smoke`.
- Add LibreOffice/Poppler rendering with isolated profiles, hidden-slide mapping,
  aspect-ratio padding and fail-closed export checks.
- Add cross-platform CI, clean-wheel smoke, a non-root batch container and
  explicit deployment limitations. Container/GPU readiness requires separate
  validation; this is not a public API or a newly trained voice model.