from pathlib import Path

import pytest

from samples.make_samples import make_samples
from slidevoice.core.config import load_config
from slidevoice.core.pipeline import create_job

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def job(tmp_path):
    slides, voice = make_samples(tmp_path / "samples")
    config = load_config(ROOT / "configs" / "fake.yaml")
    return create_job(slides, voice, tmp_path / "job", config)
