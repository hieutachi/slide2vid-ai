"""Loopback-only media player with byte-range support and visible browser errors."""

import argparse
import functools
import re
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


class MediaHandler(SimpleHTTPRequestHandler):
    """Serve local MP4 seeking correctly, including HEAD and invalid ranges."""

    def send_head(self):
        self._remaining = None
        path = Path(self.translate_path(self.path))
        if not path.is_file() or "Range" not in self.headers:
            return super().send_head()
        size = path.stat().st_size
        match = re.fullmatch(r"bytes=(\d*)-(\d*)", self.headers["Range"])
        if not match or not any(match.groups()) or size == 0:
            return self._invalid_range(size)
        left, right = match.groups()
        if not left:
            count = int(right)
            if count == 0:
                return self._invalid_range(size)
            start, end = max(0, size - count), size - 1
        else:
            start, end = int(left), min(int(right) if right else size - 1, size - 1)
        if start >= size or end < start:
            return self._invalid_range(size)
        stream = path.open("rb")
        stream.seek(start)
        self._remaining = end - start + 1
        self.send_response(HTTPStatus.PARTIAL_CONTENT)
        self.send_header("Content-type", self.guess_type(str(path)))
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.send_header("Content-Length", str(self._remaining))
        self.end_headers()
        return stream

    def _invalid_range(self, size):
        self.send_response(HTTPStatus.REQUESTED_RANGE_NOT_SATISFIABLE)
        self.send_header("Content-Range", f"bytes */{size}")
        self.send_header("Content-Length", "0")
        self.end_headers()
        return None

    def copyfile(self, source, outputfile):
        if self._remaining is None:
            return super().copyfile(source, outputfile)
        remaining = self._remaining
        while remaining:
            data = source.read(min(65536, remaining))
            if not data:
                break
            outputfile.write(data)
            remaining -= len(data)


def write_player(root: Path) -> None:
    (root / "index.html").write_text(
        """<!doctype html><html lang="vi"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>SlideVoice — kiểm tra slide và tai nghe</title>
<style>body{max-width:960px;margin:32px auto;padding:16px;font:18px system-ui;
background:#101c30;color:#eef4ff}video{width:100%;background:#000}audio{width:100%}
a{color:#8edaff}pre{white-space:pre-wrap}button{padding:12px;font:inherit}</style>
<h1>Slide thật + lời đọc tổng hợp</h1>
<p><strong>Kiểm tra Windows đã phát hiện GSX 1200 Pro Main Audio đang mute,
âm lượng 0% tại thời điểm QA. Hãy chọn đúng tai nghe, bỏ mute và thử mức âm lượng
thấp trước. Trang này không tự đổi thiết bị hay âm lượng Windows.</strong></p>
<p>Nhấn Play. Không tự phát và không tự thay đổi âm lượng Windows.
Giọng thử nghiệm là tiếng Anh, không phải giọng Việt hay voice cloning.</p>
<video id="video" controls playsinline preload="metadata" src="slides_compatible.mp4">
<track kind="subtitles" src="narrated/subtitles.vtt" srclang="en" label="English" default>
</video><button id="play">Phát video có tiếng</button>
<pre id="status">Đang nạp metadata…</pre>
<h2>1. Lời đọc riêng, không qua codec video</h2>
<audio controls preload="metadata" src="narrated/audio_check.wav"></audio>
<h2>2. Kiểm tra kênh trái / phải</h2>
<p>Lần lượt nghe “Left channel” ở tai trái và “Right channel” ở tai phải.</p>
<audio controls preload="metadata" src="headphone_check.wav"></audio>
<h2>Nếu không phát được</h2><ol>
<li>Nếu WAV có tiếng nhưng MP4 không phát: ghi lại lỗi bên dưới và thử tải MP4.</li>
<li>Nếu cả WAV cũng im lặng: kiểm tra output Windows đang chọn đúng USB/tai nghe,
Volume Mixer của trình duyệt và nút mute vật lý. Chưa có bằng chứng lỗi nằm ở thiết bị.</li>
<li>Nếu chỉ nghe một bên: thử file trái/phải và kiểm tra balance trong Windows.</li></ol>
<p><a download href="slides_compatible.mp4">Tải MP4 H.264/AAC</a> ·
<a download href="slides_fallback.webm">Tải WebM VP9/Opus dự phòng</a> ·
<a href="fixtures/slides.pptx">Slide PPTX</a> ·
<a href="qa_checks.json">Bằng chứng QA</a></p>
<script>
const v=document.querySelector('#video'),s=document.querySelector('#status');
function status(e){s.textContent=JSON.stringify({event:e.type,readyState:v.readyState,
networkState:v.networkState,time:v.currentTime,duration:v.duration,muted:v.muted,
volume:v.volume,error:v.error?{code:v.error.code,message:v.error.message}:null,
h264:v.canPlayType('video/mp4; codecs="avc1.42E01F, mp4a.40.2"')},null,2);}
['loadedmetadata','canplay','playing','pause','waiting','stalled','error','volumechange']
.forEach(e=>v.addEventListener(e,status));
document.querySelector('#play').onclick=async()=>{v.muted=false;try{await v.play();}
catch(e){s.textContent=e.name+': '+e.message;}};
</script></html>""",
        encoding="utf-8",
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    handler = functools.partial(MediaHandler, directory=str(args.root.resolve()))
    ThreadingHTTPServer(("127.0.0.1", args.port), handler).serve_forever()
