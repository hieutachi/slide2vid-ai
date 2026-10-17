# Third-party components and content

The MIT license covers SlideVoice's own source, not every external program,
model, voice, font, deck or media file used with it. No model weights, downloaded
video or personal voice recordings are included in the Python distribution.

| Component | Distribution boundary | License / operator action |
| --- | --- | --- |
| Python dependencies | Installed by pip; not vendored | Retain each distribution's license notices; inspect installed metadata before redistribution. |
| FFmpeg / ffprobe | System package / container | License depends on build options. The `libx264` encoder commonly implies GPL obligations. Review the actual binary, corresponding source and distribution obligations. |
| LibreOffice / Poppler | Optional system packages / container | Review the installed packages' MPL/LGPL/GPL notices and source availability. The container is not wholly MIT. |
| Fonts | Host or distro fonts | Verify font embedding/redistribution rights. Containers install distro-packaged DejaVu/Noto fonts. |
| PowerPoint / Windows SAPI | Host software, not bundled | Requires the applicable proprietary product license. No server-automation support is implied. |
| VieNeu-TTS and bundled presets | Separate operator-installed GPU worker | Publisher declares Apache-2.0 for the referenced model/presets; preserve publisher notices and verify the pinned revisions' terms. See the worker README. |
| LLM APIs | Operator-configured external service | Provider terms, data retention, region and costs are operator responsibilities. |
| User slides / voices | Local input, excluded from wheel | Obtain content rights and explicit speaker consent; do not use for impersonation. |

The package license is not a legal opinion about an operator's generated output
or a model publisher's rights. A distributable release needs a dependency/SBOM
and license review for its exact resolved environment, not just this table.