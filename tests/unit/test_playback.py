import functools
import threading
from http.server import ThreadingHTTPServer

import httpx
import pytest

from samples.playback import MediaHandler, write_player


@pytest.fixture
def media_server(tmp_path):
    (tmp_path / "clip.mp4").write_bytes(bytes(range(100)))
    server = ThreadingHTTPServer(
        ("127.0.0.1", 0), functools.partial(MediaHandler, directory=tmp_path)
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_port}"
    server.shutdown()
    server.server_close()
    thread.join()


@pytest.mark.parametrize(
    "value,expected",
    [
        ("bytes=0-9", bytes(range(10))),
        ("bytes=90-", bytes(range(90, 100))),
        ("bytes=-5", bytes(range(95, 100))),
        ("bytes=95-200", bytes(range(95, 100))),
    ],
)
def test_media_byte_ranges(media_server, value, expected):
    response = httpx.get(media_server + "/clip.mp4", headers={"Range": value})
    assert response.status_code == 206
    assert response.content == expected
    assert response.headers["content-type"] == "video/mp4"


@pytest.mark.parametrize(
    "value", ["bytes=100-", "bytes=20-10", "bytes=-0", "bytes=", "bytes=0-1,3-4"]
)
def test_invalid_ranges(media_server, value):
    response = httpx.get(media_server + "/clip.mp4", headers={"Range": value})
    assert response.status_code == 416
    assert response.headers["content-range"] == "bytes */100"


def test_full_get_and_head(media_server):
    assert httpx.get(media_server + "/clip.mp4").content == bytes(range(100))
    response = httpx.head(media_server + "/clip.mp4", headers={"Range": "bytes=10-19"})
    assert response.status_code == 206
    assert response.content == b""
    assert response.headers["content-length"] == "10"


def test_player_has_real_media_and_error_details(tmp_path):
    write_player(tmp_path)
    page = (tmp_path / "index.html").read_text(encoding="utf-8")
    assert "slides_compatible.mp4" in page
    assert "headphone_check.wav" in page
    assert "v.error.message" in page
    assert "autoplay" not in page
