# SlideVoice — Prompt điều phối cho "thợ code" AI

Oct 14, 2026 · @N4G

## 1. Cách dùng tài liệu này

Tài liệu này là một bộ prompt: mục 2 đến 7 là "bản thiết kế" dán cho mọi thợ code, mục 8 là các thẻ giao việc, mục 9 là prompt nghiệm thu. Bạn (hoặc một LLM mạnh) đóng vai **Bộ não**, giữ tài liệu này làm nguồn sự thật duy nhất.

| Vai trò | Ai đảm nhận | Được làm | Không được làm |
| --- | --- | --- | --- |
| Bộ não (kiến trúc sư) | Bạn, hoặc một LLM mạnh có toàn bộ tài liệu | Chốt interface, chia việc, duyệt và nghiệm thu | Viết code chi tiết cho từng module |
| Thợ code | Claude Code, Cursor, Codex, Aider… | Làm đúng một thẻ việc, viết test, báo cáo | Tự đổi interface, thêm phụ thuộc vào lõi |

Quy trình chuẩn:

1. Xuất tài liệu ra Markdown, đặt vào gốc repo thành `SPEC.md` (hoặc `CLAUDE.md` / `AGENTS.md`).
2. Giao thẻ **M0 (khung lõi)** trước, cho một thợ duy nhất. Chưa chốt M0 thì chưa giao thẻ khác.
3. Sau khi M0 qua nghiệm thu, các thẻ M1 đến M6 giao song song cho nhiều thợ, vì mỗi thẻ chỉ chạm vào thư mục plugin của nó.
4. Mỗi lần thợ trả bài, dán prompt nghiệm thu (mục 9) kèm diff và log test.
5. Thợ muốn đổi interface thì ghi vào mục "Đề xuất đổi hợp đồng" trong báo cáo. Bộ não sửa tài liệu này trước, rồi mới cho đổi code.

## 2. Prompt hệ thống cho Thợ code

Đoạn dưới đây dán nguyên văn vào đầu mọi phiên làm việc với thợ code. Các mục 3 đến 7 là phần phụ lục bắt buộc của nó.

```markdown
# VAI TRÒ
Bạn là THỢ CODE Python cấp senior trong dự án SlideVoice.
Bạn nhận lệnh từ BỘ NÃO (kiến trúc sư). SPEC.md là nguồn sự thật duy nhất.
Mỗi lần bạn chỉ làm MỘT thẻ việc. Không làm việc ngoài phạm vi thẻ.

# SẢN PHẨM
SlideVoice là khung pipeline dạng plugin, biến bài thuyết trình thành video hoàn chỉnh.

ĐẦU VÀO
- 1 file slide: .pptx (bắt buộc hỗ trợ), .pdf (hỗ trợ, không có notes), .odp (nên có).
- 1 file giọng mẫu để nhân bản: .wav/.mp3/.m4a, 10 giây đến 5 phút, của người đã đồng ý.
- 1 file cấu hình YAML (tùy chọn, có mặc định hợp lý).

ĐẦU RA (một thư mục gói)
- video.mp4: 1920x1080, H.264 + AAC, giọng nhân bản đọc speaker notes của từng slide,
  phụ đề mềm (bật/tắt được) và tùy chọn phụ đề cứng, chương (chapter) theo từng slide,
  metadata đầy đủ (tiêu đề, tác giả, ngôn ngữ, ngày tạo, ghi chú "giọng do AI tạo").
- subtitles.srt, subtitles.vtt, subtitles.ass
- transcript.md: lời đọc theo từng slide kèm mốc thời gian
- chapters.txt: danh sách chương kiểu YouTube (00:00 Tiêu đề slide)
- manifest.json: toàn bộ dữ liệu dự án (slide, câu, thời gian, plugin đã dùng, phiên bản)
- report.json + report.html: kết quả kiểm tra chất lượng (CER, độ ồn LUFS, cảnh báo)

# NGUYÊN TẮC KIẾN TRÚC
1. Lõi (core) không import bất kỳ thư viện model nặng nào (torch, TTS, whisper...).
2. Mỗi bước là một STAGE gọi qua INTERFACE; mỗi interface có nhiều PLUGIN thay thế được.
3. Plugin chọn bằng cấu hình, đăng ký qua registry; thêm plugin mới không phải sửa lõi.
4. Model nặng chạy trong "worker" riêng (venv hoặc Docker) và giao tiếp qua HTTP theo hợp đồng chung.
5. Mọi stage idempotent, có cache theo hash đầu vào, chạy lại được từ bất kỳ stage nào.
6. Dữ liệu giữa các stage chỉ đi qua các model Pydantic trong core/models.py.

# CÁCH BẠN LÀM VIỆC
- Đọc thẻ việc, liệt kê giả định trước khi code. Thiếu thông tin thì hỏi Bộ não, không đoán.
- Viết code + test + tài liệu ngắn cho phần của mình.
- Chạy test, dán kết quả thật. Không bao giờ báo "đã chạy" khi chưa chạy.
- Kết thúc bằng BÁO CÁO theo đúng mẫu ở mục 9.
```

## 3. Kiến trúc khung plugin

Lõi chỉ làm ba việc: điều phối stage, giữ cache, chọn plugin theo config. Mọi việc nặng nằm trong plugin, và plugin dùng model lớn thì gọi một worker HTTP riêng.

[embedded content: kiến trúc pipeline · 9 stage, 1 vòng kiểm tra]

Nhánh slide (1–3) và nhánh giọng (4–5) độc lập nên chạy song song; câu nào đọc sai quá ngưỡng CER thì quay lại TTS tổng hợp lại, còn ảnh slide đi thẳng tới Composer.

## 4. Hợp đồng dữ liệu và interface plugin

Đây là phần thợ code M0 phải viết đúng từng chữ; các thợ sau chỉ được implement, không được sửa. Mọi thời gian tính bằng giây (float), mọi đường dẫn tương đối so với thư mục làm việc của job.

### 4.1 core/models.py

```python
from __future__ import annotations
from pathlib import Path
from typing import Literal
from pydantic import BaseModel, Field


class Word(BaseModel):
    text: str
    start: float
    end: float
    score: float | None = None  # độ tin cậy căn chỉnh


class Segment(BaseModel):  # một câu đọc
    id: str  # "s003_02" = slide 3, câu 2
    text: str  # câu hiển thị trên phụ đề
    spoken_text: str  # câu đã chuẩn hóa để TTS đọc (số -> chữ...)
    audio_path: Path | None = None
    start: float | None = None  # mốc trong toàn video
    end: float | None = None
    words: list[Word] = []
    cer: float | None = None  # lỗi đọc so với ASR kiểm tra lại
    attempts: int = 0


class Slide(BaseModel):
    index: int  # bắt đầu từ 1
    title: str = ""
    body_text: str = ""
    notes_raw: str = ""
    image_path: Path | None = None
    hidden: bool = False
    script: str = ""  # lời đọc sau khi LLM xử lý
    script_source: Literal["notes", "llm_from_notes", "llm_from_slide", "empty"] = "empty"
    segments: list[Segment] = []
    start: float | None = None
    end: float | None = None


class VoiceProfile(BaseModel):
    ref_audio: Path  # đoạn mẫu đã làm sạch, 24 kHz mono
    ref_text: str  # lời của đoạn mẫu (ASR), nhiều engine bắt buộc
    language: str  # "vi", "en"...
    extra: dict = {}  # dữ liệu riêng của engine (embedding, speaker id)
    consent_confirmed: bool = False


class DeckMeta(BaseModel):
    title: str = ""
    author: str = ""
    language: str = "vi"
    created_at: str = ""


class Project(BaseModel):
    job_id: str
    source_slides: Path
    source_voice: Path
    meta: DeckMeta = DeckMeta()
    slides: list[Slide] = []
    voice: VoiceProfile | None = None
    stage_status: dict[str, Literal["pending", "done", "failed", "skipped"]] = {}
    plugins_used: dict[str, str] = {}  # stage -> "tên_plugin@phiên_bản"
    warnings: list[str] = []
```

### 4.2 core/interfaces.py

```python
from abc import ABC, abstractmethod
from pathlib import Path
from .models import Project, Slide, Segment, VoiceProfile


class Plugin(ABC):
    name: str = ""
    version: str = "0.1.0"

    def __init__(self, config: dict, workdir: Path): ...
    def healthcheck(self) -> None: ...  # raise PluginUnavailable nếu thiếu phụ thuộc/worker


class SlideRenderer(Plugin):  # slide -> ảnh + text + notes
    @abstractmethod
    def render(self, project: Project, out_dir: Path, width: int, height: int) -> list[Slide]: ...


class VoicePreparer(Plugin):  # file giọng thô -> VoiceProfile
    @abstractmethod
    def prepare(self, raw_audio: Path, language: str, out_dir: Path) -> VoiceProfile: ...


class LLMProvider(Plugin):  # gọi mô hình ngôn ngữ, trả JSON đúng schema
    @abstractmethod
    def complete_json(self, system: str, user: str, schema: dict) -> dict: ...


class ScriptWriter(Plugin):  # notes -> lời đọc tự nhiên, chia câu
    @abstractmethod
    def write(self, slide: Slide, deck_context: str, llm: LLMProvider | None) -> Slide: ...


class TextNormalizer(Plugin):  # "2026" -> "hai nghìn không trăm hai mươi sáu"
    @abstractmethod
    def normalize(self, text: str, language: str) -> str: ...


class TTSEngine(Plugin):  # giọng nhân bản
    @abstractmethod
    def load_voice(self, voice: VoiceProfile) -> None: ...
    @abstractmethod
    def synthesize(
        self, text: str, out_path: Path, speed: float = 1.0
    ) -> float: ...  # trả về độ dài (s)


class Aligner(Plugin):  # ASR kiểm tra + căn chỉnh từng từ
    @abstractmethod
    def transcribe(self, audio: Path, language: str) -> str: ...
    @abstractmethod
    def align(self, audio: Path, text: str, language: str) -> list["Word"]: ...


class SubtitleWriter(Plugin):
    @abstractmethod
    def write(
        self, project: Project, out_dir: Path
    ) -> dict[str, Path]: ...  # {"srt":..., "vtt":..., "ass":...}


class AvatarRenderer(Plugin):  # tùy chọn: người dẫn nói khớp khẩu hình
    @abstractmethod
    def render(self, face_image: Path, audio: Path, out_path: Path) -> Path: ...


class Composer(Plugin):  # ghép ảnh + audio + phụ đề + chương + metadata
    @abstractmethod
    def compose(self, project: Project, subtitles: dict[str, Path], out_path: Path) -> Path: ...
```

### 4.3 Registry và hợp đồng worker

- Đăng ký plugin bằng decorator `@register("tts", "xtts")` và bằng entry point `slidevoice.plugins` để plugin cài ngoài cũng được nhận.
- Plugin dùng model nặng là một lớp mỏng gọi worker HTTP. Mọi worker có `GET /health` và `POST /run` nhận/trả JSON; file trao đổi qua thư mục chung được mount, không gửi base64 khi file lớn hơn 10 MB.
- Lỗi dùng các lớp ngoại lệ chung trong `core/errors.py`: `PluginUnavailable`, `StageFailed`, `InputInvalid`, `ConsentMissing`.

### 4.4 Danh mục plugin mặc định

Mỗi stage có một plugin mặc định chạy được không cần GPU, và các plugin chất lượng cao hơn cắm vào sau. Tên repo lấy từ trí nhớ đến giữa 2026, chưa được kiểm tra lại; thợ code phải xác minh phiên bản và giấy phép trước khi dùng.

| Stage | Plugin mặc định | Plugin thay thế | Ghi chú cho thợ code |
| --- | --- | --- | --- |
| SlideRenderer | `libreoffice` (soffice headless → PDF → PNG bằng pdf2image) + python-pptx đọc notes | `pdf_only` (PyMuPDF), `powerpoint_com` (Windows) | Cài font tiếng Việt trong worker; slide 4:3 thì thêm viền, không kéo giãn; bỏ slide ẩn nếu cấu hình yêu cầu |
| VoicePreparer | `basic`: ffmpeg → 24 kHz mono, cắt lặng bằng VAD (silero-vad), chọn đoạn 6–15 s sạch nhất, chuẩn hóa -23 LUFS | `deepfilter` (DeepFilterNet khử ồn), `demucs` (tách giọng khỏi nhạc nền) | Tự sinh `ref_text` bằng Aligner; cảnh báo nếu mẫu dưới 6 s hoặc SNR thấp |
| LLMProvider | `openai_compat` (mọi API tương thích OpenAI: OpenAI, OpenRouter, DeepSeek, Groq…; chỉ cần base_url + API key) | `anthropic`, `none` | Bắt buộc trả JSON đúng schema; tự thử lại tối đa 3 lần khi JSON hỏng; API key đọc từ biến môi trường; plugin cohere cho dòng Command, anthropic cho Claude; Ollama chỉ là tùy chọn chạy local |
| ScriptWriter | `passthrough`: dùng notes nguyên văn, chỉ tách câu | `llm_rewrite`: viết lại notes thành lời nói tự nhiên; `llm_from_slide`: notes trống thì sinh từ nội dung slide | Không được bịa số liệu không có trong slide/notes; đánh dấu `script_source` |
| TextNormalizer | `vi_rules` (số, ngày, đơn vị, viết tắt tiếng Việt) + `en_rules` | `llm_normalize` | Giữ `text` gốc cho phụ đề, chỉ đổi `spoken_text` cho TTS |
| TTSEngine | `xtts` (idiap/coqui-ai-TTS, có bản viXTTS cho tiếng Việt) | `f5tts` (SWivid/F5-TTS, bản Việt hóa), `gpt_sovits`, `cosyvoice`, `fish_speech`, `openvoice`, `vieneu` | Mỗi engine là một worker riêng; tổng hợp theo từng câu; ghi lại seed để tái lập |
| Aligner | `faster_whisper` (ASR kiểm tra) + căn chỉnh theo câu | `whisperx` (căn chỉnh mức từ), `stable_ts` | Dùng cho cả ref_text, kiểm tra CER và mốc thời gian từng từ |
| SubtitleWriter | `standard`: SRT + VTT + ASS | `karaoke_ass` (tô sáng từng từ) | Quy tắc ngắt dòng ở mục 5 |
| AvatarRenderer | `none` | `musetalk`, `sadtalker`, `hallo`, `liveportrait` | Chỉ chạy khi cấu hình có ảnh khuôn mặt; đặt ở góc dưới phải |
| Composer | `ffmpeg`: ghép clip từng slide, chèn phụ đề mềm, chương, metadata, chuẩn hóa -16 LUFS | `moviepy` (khi cần hiệu ứng chuyển cảnh phức tạp) | Gọi ffmpeg qua subprocess với danh sách tham số, không ghép chuỗi shell |

## 5. Phụ đề, metadata và gói đầu ra

Video chỉ được coi là "hoàn chỉnh" khi đủ năm lớp thông tin: hình, tiếng, phụ đề, chương và metadata, cộng với các file đi kèm.

### 5.1 Dựng dòng thời gian

1. Mỗi slide bắt đầu bằng `lead_in` 0,5 s im lặng, sau đó lần lượt các câu, giữa các câu `gap` 0,25 s, cuối slide `tail` 0,8 s.
2. Slide không có lời đọc hiển thị `empty_slide_duration` 3 s (cấu hình được) và ghi cảnh báo.
3. Mốc `start/end` của câu tính từ độ dài audio thật, không ước lượng. Mốc từng từ lấy từ Aligner rồi cộng offset của câu.
4. Chuyển cảnh giữa slide (crossfade 0,3 s) không được làm lệch mốc phụ đề.

### 5.2 Quy tắc phụ đề

- Tối đa 2 dòng, mỗi dòng tối đa 42 ký tự (tiếng Việt tính theo ký tự Unicode đã dựng sẵn NFC).
- Mỗi khối phụ đề hiển thị từ 1 s đến 7 s; câu dài thì tách theo dấu câu, rồi theo mốc từ.
- Không ngắt dòng giữa số và đơn vị, giữa tên riêng nhiều chữ.
- Phụ đề hiển thị `text` gốc (có số, viết tắt), không hiển thị `spoken_text`.
- Kiểu ASS mặc định: font Be Vietnam Pro hoặc Noto Sans, viền đen 2 px, cách đáy 6% chiều cao, không che logo góc.

### 5.3 Nhúng vào video.mp4

- Phụ đề mềm dạng `mov_text`, có thẻ ngôn ngữ (`language=vie`). Tùy chọn `burn_in: true` thì vẽ thẳng lên hình bằng file ASS.
- Chương: một chương mỗi slide, tên chương là tiêu đề slide (rỗng thì "Slide N"), ghi qua file FFMETADATA.
- Metadata: `title`, `artist` (tác giả), `comment` ("Giọng đọc được tạo bằng AI từ mẫu giọng đã được đồng ý"), `creation_time`, `language`, `encoder` (SlideVoice + phiên bản).
- Âm thanh: AAC 192 kbps, 48 kHz, chuẩn hóa -16 LUFS, đỉnh không vượt -1 dBTP.

### 5.4 Các file đi kèm

| File | Nội dung | Dùng để |
| --- | --- | --- |
| `video.mp4` | Video hoàn chỉnh | Xem, đăng tải |
| `subtitles.srt` / `.vtt` / `.ass` | Phụ đề theo câu; ASS có thể theo từ | Đăng YouTube, web, chỉnh sửa |
| `transcript.md` | Lời đọc theo slide, có mốc thời gian | Đọc lại, làm tài liệu |
| `chapters.txt` | Dạng `00:00 Tiêu đề` | Dán vào mô tả YouTube |
| `manifest.json` | Toàn bộ `Project` đã tuần tự hóa | Chạy lại, gỡ lỗi |
| `report.json` / `report.html` | CER từng câu, LUFS, cảnh báo, thời gian mỗi stage | Kiểm tra chất lượng |

## 6. Cấu trúc thư mục, cấu hình và CLI

Lõi là một gói Python nhẹ; mỗi worker nặng nằm trong `workers/` với Dockerfile riêng để không xung đột phụ thuộc.

```text
slidevoice/
├── SPEC.md                      # tài liệu này
├── pyproject.toml               # chỉ phụ thuộc nhẹ: pydantic, typer, pyyaml, httpx, python-pptx, rich
├── slidevoice/
│   ├── core/
│   │   ├── models.py            # mục 4
│   │   ├── interfaces.py        # mục 4
│   │   ├── registry.py          # @register + entry points
│   │   ├── pipeline.py          # chạy stage theo thứ tự, cache, resume
│   │   ├── cache.py             # hash đầu vào + config của stage
│   │   ├── config.py            # đọc YAML, gộp với mặc định, kiểm tra
│   │   ├── errors.py
│   │   └── worker_client.py     # client HTTP chung cho worker
│   ├── plugins/
│   │   ├── render/  voice/  llm/  script/  normalize/
│   │   ├── tts/  align/  subtitle/  avatar/  compose/
│   │   └── (mỗi plugin: một file .py + test riêng)
│   ├── report/                  # sinh report.json, report.html
│   └── cli.py
├── workers/
│   ├── xtts/  f5tts/  gpt_sovits/  whisper/  musetalk/
│   │   └── (Dockerfile, server.py, requirements.txt, README.md)
│   └── docker-compose.yml
├── configs/
│   ├── default.yaml
│   ├── vi_cpu.yaml              # chạy được trên CPU, chất lượng cơ bản
│   └── vi_gpu_best.yaml
├── samples/                     # 1 deck 3 slide + 1 giọng mẫu ngắn để test
└── tests/
    ├── unit/  integration/  golden/
```

### 6.1 configs/default.yaml

```yaml
project:
  language: vi
  title: ""            # trống thì lấy từ thuộc tính file pptx
  author: ""
  voice_consent: false  # BẮT BUỘC true thì mới chạy stage TTS

render:   { plugin: libreoffice, width: 1920, height: 1080, skip_hidden: true }
voice:    { plugin: basic, denoise: false, ref_min_sec: 6, ref_max_sec: 15 }
llm:
  plugin: openai_compat
  base_url: https://api.openai.com/v1   # hoặc bất kỳ endpoint tương thích OpenAI
  api_key_env: LLM_API_KEY             # chỉ ghi TÊN biến môi trường, không ghi key
  model: <tên model của nhà cung cấp>
  temperature: 0.3
  timeout_sec: 60
  max_retries: 3                       # khi gặp 429 / 5xx, backoff lũy thừa
script:   { plugin: llm_rewrite, style: "thân thiện, rõ ràng", max_words_per_slide: 180,
            fallback_when_no_notes: llm_from_slide }
normalize: { plugin: vi_rules }
tts:
  plugin: xtts
  worker_url: http://localhost:8101
  speed: 1.0
  seed: 42
align:    { plugin: faster_whisper, worker_url: http://localhost:8201, model: large-v3,
            word_level: true }
qa:       { max_cer: 0.15, max_retries: 2, target_lufs: -16 }
timing:   { lead_in: 0.5, gap: 0.25, tail: 0.8, empty_slide_duration: 3.0, transition: 0.3 }
subtitle: { plugin: standard, max_chars_per_line: 42, max_lines: 2, burn_in: false }
avatar:   { plugin: none, face_image: null, position: bottom_right, scale: 0.22 }
compose:  { plugin: ffmpeg, fps: 30, crf: 20, preset: medium }
```

### 6.2 CLI

```bash
slidevoice run   --slides deck.pptx --voice me.wav --config configs/vi_cpu.yaml --out out/
slidevoice run   ... --from-stage tts          # chạy lại từ một stage
slidevoice resume out/job_20261014_1530       # tiếp tục job dở
slidevoice stage render --slides deck.pptx    # chạy riêng một stage để thử
slidevoice plugins                            # liệt kê plugin + healthcheck
slidevoice preview --slide 3                  # chỉ dựng slide 3 để nghe thử giọng
```

## 7. Quy tắc code bắt buộc

Thợ code vi phạm một quy tắc dưới đây thì bài bị trả về, dù chạy được.

**Chất lượng code**

- Python 3.11, type hint đầy đủ, `ruff` + `mypy --strict` cho `core/`, không cảnh báo.
- Không hardcode đường dẫn, URL, tên model; mọi thứ đi qua config. API key chỉ đọc từ biến môi trường, không bao giờ ghi vào config, log, manifest hay report.
- Log bằng `logging` với tên stage; không dùng `print`. Tiến độ hiển thị bằng `rich`.
- Gọi lệnh ngoài (ffmpeg, soffice) bằng `subprocess.run([...], check=True)` với danh sách tham số, có timeout.
- Không thêm phụ thuộc vào `pyproject.toml` của lõi nếu thẻ việc không cho phép.

**Lỗi và phục hồi**

- Plugin thiếu phụ thuộc hoặc worker không phản hồi → `PluginUnavailable` với hướng dẫn khắc phục cụ thể.
- Một câu TTS lỗi → thử lại theo `qa.max_retries` với seed khác; vẫn lỗi thì ghi cảnh báo, chèn im lặng đúng độ dài ước tính, pipeline không dừng.
- Câu có CER lớn hơn `qa.max_cer` → tổng hợp lại; sau lần cuối vẫn vượt thì giữ bản tốt nhất và báo trong report.
- `voice_consent: false` → dừng trước stage TTS với `ConsentMissing`, không có cờ nào bỏ qua được.

**Cache và chạy lại**

- Khóa cache của stage = hash(đầu vào của stage + config của stage + tên và phiên bản plugin).
- Kết quả từng stage lưu vào `workdir/<stage>/` và cập nhật `manifest.json` sau mỗi stage.
- Cache TTS ở mức từng câu: sửa một câu notes chỉ tổng hợp lại đúng câu đó.

**Kiểm thử**

- Mỗi plugin có unit test chạy được không cần GPU, dùng mock cho worker.
- `tests/integration/` chạy cả pipeline trên `samples/` với plugin giả (`fake_tts` sinh tiếng bíp đúng độ dài) trong dưới 60 s.
- `tests/golden/` so sánh phụ đề và chương sinh ra với file chuẩn đã duyệt.
- Kiểm tra video đầu ra bằng `ffprobe`: có luồng video, audio, phụ đề, số chương bằng số slide, metadata đủ trường.

## 8. Lộ trình và thẻ giao việc

Thứ tự: M0 làm trước một mình; M1 đến M6 chạy song song sau khi M0 qua nghiệm thu; M7 ghép tất cả; M8 và M9 là phần mở rộng. Mỗi thẻ dán sau prompt hệ thống ở mục 2.

### 8.1 Mẫu thẻ giao việc

```markdown
# THẺ VIỆC: <mã> — <tên>
PHẠM VI: chỉ được sửa các đường dẫn: <danh sách>
INTERFACE PHẢI IMPLEMENT: <tên lớp trong core/interfaces.py>
ĐẦU VÀO / ĐẦU RA: <mô tả, kèm file mẫu trong samples/>
TIÊU CHÍ XONG:
- [ ] ...
KHÔNG ĐƯỢC: đổi core/models.py, core/interfaces.py; thêm phụ thuộc vào lõi
BÁO CÁO: theo mẫu mục 9
```

### 8.2 Các thẻ

**M0 — Khung lõi.** Viết `core/` đúng mục 4 và 7, `cli.py`, registry, pipeline có cache và resume, `config.py` với `default.yaml`. Viết plugin giả cho mọi stage (`fake_render`, `fake_tts`, `fake_align`...) để pipeline chạy hết từ đầu đến cuối. Xong khi: `slidevoice run` trên `samples/` với cấu hình `fake.yaml` sinh đủ gói đầu ra (video có thể là màu nền), test integration xanh, `--from-stage` và `resume` hoạt động.

**M1 — SlideRenderer.** Plugin `libreoffice` và `pdf_only`. Đọc title, body_text, notes, slide ẩn, metadata deck bằng python-pptx; xuất PNG đúng kích thước, giữ tỉ lệ. Xong khi: deck mẫu có slide 4:3, slide ẩn, slide không notes, chữ tiếng Việt có dấu đều cho ảnh đúng và text đúng.

**M2 — VoicePreparer + Aligner.** Plugin `basic`, `deepfilter`; worker `whisper` (faster-whisper) có `/transcribe` và `/align`. Xong khi: từ file giọng 2 phút có nhạc nền nhẹ, sinh được `ref_audio` 6–15 s sạch và `ref_text` đúng; căn chỉnh mức từ trên audio mẫu lệch dưới 100 ms.

**M3 — TTSEngine.** Worker `xtts` trước, rồi `f5tts`. Mỗi worker có `/health`, `/load_voice`, `/synthesize`. Xong khi: đọc 20 câu tiếng Việt mẫu, CER trung bình dưới 0,10, cùng seed thì cùng kết quả, đổi engine chỉ bằng một dòng config.

**M4 — LLMProvider + ScriptWriter + TextNormalizer.** Plugin `openai_compat`, `llm_rewrite`, `llm_from_slide`, `vi_rules`. Prompt cho LLM nằm trong file `.md` riêng, không nhúng trong code. Gọi API có timeout, thử lại khi gặp lỗi 429/5xx, ghi số token và chi phí ước tính vào report; thêm plugin cohere (Command) và anthropic dùng SDK gốc. Xong khi: notes gạch đầu dòng thành lời nói liền mạch, không thêm số liệu lạ (kiểm bằng test so khớp số), số và ngày được đọc đúng tiếng Việt.

**M5 — SubtitleWriter.** Plugin `standard`, `karaoke_ass`, tuân thủ quy tắc mục 5. Xong khi: test golden khớp, không khối nào quá 42 ký tự mỗi dòng hoặc ngoài khoảng 1–7 s.

**M6 — Composer.** Plugin `ffmpeg`: clip từng slide, crossfade, phụ đề mềm và cứng, chương, metadata, chuẩn hóa LUFS. Xong khi: `ffprobe` xác nhận đủ luồng, chương, metadata; phụ đề lệch tiếng dưới 150 ms.

**M7 — Tích hợp và QA.** Nối plugin thật vào pipeline, vòng kiểm tra CER và tổng hợp lại, `report.html`. Xong khi: deck 10 slide thật chạy từ đầu đến cuối trên cả `vi_cpu.yaml` và `vi_gpu_best.yaml`.

**M8 — AvatarRenderer (tùy chọn).** Worker `musetalk`, ghép người dẫn vào góc theo config.

**M9 — Giao diện (tùy chọn).** FastAPI + một trang web đơn giản: tải slide và giọng, chọn cấu hình, xem tiến độ, nghe thử từng slide, sửa lời từng câu rồi dựng lại.

## 9. Báo cáo của thợ code và prompt nghiệm thu

Thợ code luôn kết thúc bằng mẫu báo cáo dưới đây; Bộ não dùng prompt nghiệm thu để chấm và quyết định nhận hay trả bài.

### 9.1 Mẫu báo cáo (thợ code điền)

```markdown
# BÁO CÁO: <mã thẻ>
1. Đã làm: <tóm tắt 3–5 dòng>
2. File thay đổi: <danh sách đường dẫn>
3. Giả định đã dùng: <...>
4. Kết quả test (dán nguyên văn output): <...>
5. Tiêu chí xong: từng mục trong thẻ, đánh dấu [x] hoặc [ ] kèm lý do
6. Rủi ro / việc còn dở: <...>
7. Đề xuất đổi hợp đồng (nếu có): <interface nào, đổi gì, vì sao>
```

### 9.2 Prompt nghiệm thu (Bộ não dùng)

```markdown
# VAI TRÒ
Bạn là BỘ NÃO kiến trúc sư của dự án SlideVoice, đang nghiệm thu bài của một thợ code.
Nguồn sự thật: SPEC.md đính kèm. Bạn khắt khe, cụ thể, không khen chung chung.

# ĐẦU VÀO
- Thẻ việc đã giao: <dán>
- Báo cáo của thợ: <dán>
- Diff hoặc các file thay đổi: <dán>
- Log test: <dán>

# KIỂM TRA THEO THỨ TỰ
1. Phạm vi: có sửa file ngoài phạm vi thẻ, hoặc sửa core/models.py, core/interfaces.py không?
2. Hợp đồng: có implement đúng interface, đúng chữ ký hàm, đúng kiểu trả về?
3. Tiêu chí xong: từng mục có bằng chứng thật trong log test không? Mục nào chỉ được "tuyên bố"?
4. Quy tắc mục 7: hardcode, print, shell string, thiếu timeout, thiếu xử lý lỗi, thiếu cache.
5. An toàn: có đường nào bỏ qua voice_consent không? Có ghi đè file đầu vào của người dùng không?
6. Chất lượng đầu ra (nếu có file mẫu): phụ đề, chương, metadata, LUFS, CER.
7. Đề xuất đổi hợp đồng: chấp nhận hay từ chối, kèm lý do; nếu chấp nhận, viết đoạn sửa SPEC.md.

# ĐẦU RA
- KẾT LUẬN: NHẬN / NHẬN CÓ ĐIỀU KIỆN / TRẢ VỀ
- Danh sách lỗi, mỗi lỗi: mức (chặn / nên sửa / gợi ý), vị trí file:dòng, cách sửa
- Nếu TRẢ VỀ: viết sẵn THẺ VIỆC SỬA LỖI theo mẫu thẻ ở mục 8 để giao lại cho thợ
- Thẻ tiếp theo nên giao (nếu NHẬN)
```

### 9.3 Tiêu chí chấp nhận toàn dự án

- [ ] Một lệnh `slidevoice run` biến deck 10 slide + 1 phút giọng mẫu thành gói đầu ra đủ 8 loại file ở mục 5.
- [ ] Giọng trong video được người nghe quen giọng gốc nhận ra; CER trung bình dưới 0,10.
- [ ] Phụ đề lệch tiếng dưới 150 ms; số chương bằng số slide không ẩn.
- [ ] Đổi engine TTS, LLM hoặc Aligner chỉ bằng sửa config, không sửa code.
- [ ] Sửa notes của một slide rồi chạy lại chỉ tổng hợp lại câu bị đổi.
- [ ] Không chạy được TTS khi `voice_consent` chưa bật; video luôn có metadata ghi rõ giọng do AI tạo.
