import shutil
import subprocess
from pathlib import Path

import pytest


def test_player_transport_keyboard_and_looping():
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node.js is required for the dependency-free JavaScript behavior check")
    here = Path(__file__).resolve()
    subprocess.run(
        [
            node,
            str(here.with_name("lecture_player_check.cjs")),
            str(here.parents[2] / "samples/lecture_player.html"),
        ],
        check=True,
        capture_output=True,
        text=True,
        timeout=15,
    )
