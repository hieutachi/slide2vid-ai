"""Download only pinned inference artifacts, not training datasets or ONNX variants."""

import argparse
import json
import os
from pathlib import Path

MODEL_REVISION = "61b85e3d937fbbacb387714180e8182823512523"
CODEC_REVISION = "6aa02b01e445cc585582cf0ba480bc3ea6c8dd68"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache-root", type=Path, required=True)
    args = parser.parse_args()
    args.cache_root.mkdir(parents=True, exist_ok=True)
    os.environ["HF_HOME"] = str(args.cache_root.resolve())
    os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
    from huggingface_hub import snapshot_download

    model = snapshot_download(
        "pnnbao-ump/VieNeu-TTS-v3-Turbo",
        revision=MODEL_REVISION,
        allow_patterns=[
            "update/*",
            "config.json",
            "README.md",
            "LICENSE*",
            "speaker_encoder.onnx",
            "denoiser.onnx",
            "voices_v3_turbo.json",
        ],
        max_workers=3,
    )
    codec = snapshot_download(
        "OpenMOSS-Team/MOSS-Audio-Tokenizer-Nano",
        revision=CODEC_REVISION,
        allow_patterns=["*.json", "*.py", "*.safetensors", "README.md", "LICENSE*"],
        max_workers=3,
    )
    (args.cache_root / "pinned_models.json").write_text(
        json.dumps(
            {
                "model": str(Path(model).resolve()),
                "model_revision": MODEL_REVISION,
                "codec": str(Path(codec).resolve()),
                "codec_revision": CODEC_REVISION,
            },
            indent=2,
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
