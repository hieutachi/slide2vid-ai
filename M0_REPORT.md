# BÁO CÁO: M0 — Khung lõi

> **Cập nhật QA âm thanh 2026-10-15:** các số 45 test/37 file/26 package file và
> LUFS `null` bên dưới là kết quả lịch sử, không phải hiện trạng sau sửa QA.
> Xem `D:\SOFT\STV\AUDIO_QA_REPORT.md` và log trong
> `D:\SOFT\STV\out\qa_audio_20261015\delivery` cho lần kiểm tra mới.
> Đã bổ sung phép đo âm thanh MP4 thật, chặn output narration im lặng và fixture
> Windows system speech tiếng Anh trên video tải về. Chưa học giọng thật, chưa chèn
> slide thật, chưa tự nghiệm thu M1–M6 hay thay đổi hợp đồng model/interface.

## 1. Đã làm

- Hoàn thiện pipeline tuần tự 9 stage, registry decorator/entry point, YAML mặc định
  và cấu hình fake; CLI run/resume/stage/plugins/preview.
- Cache stage có snapshot Project, SHA-256 toàn bộ nội dung, metadata phiên bản/thời
  điểm và kiểm tra artifact; cache từng câu có kiểm tra audio/transcript/metadata.
- Consent được kiểm tra trước mọi lượt chạy có TTS, trước cache TTS và trước từng
  lần tổng hợp; model path tương đối theo job, input được sao chép, manifest cập nhật
  sau mỗi stage; chặn credential literal lồng nhau trước khi lưu JSON.
- Plugin giả cho toàn bộ interface; video nền màu có tiếng bíp, phụ đề mềm, chapter,
  metadata AI; đủ SRT/VTT/ASS, transcript, manifest, report JSON/HTML.
- Có fixture tạo deck 3 slide tiếng Việt và WAV tổng hợp, test unit/integration/golden;
  retry seed khác, giữ audio CER tốt nhất, chèn im lặng khi TTS lỗi hết lượt.

## 2. File thay đổi

Tất cả đường dẫn dưới gốc tuyệt đối `D:\SOFT\STV`:

- `D:\SOFT\STV\.gitignore`, `D:\SOFT\STV\pyproject.toml`,
  `D:\SOFT\STV\README.md`, `D:\SOFT\STV\M0_REPORT.md`.
- `D:\SOFT\STV\slidevoice\core\`: cache, config, media, pipeline, worker_client,
  registry, package initializer; models/interfaces/errors đã có từ phiên trước.
  Phiên tiếp tục này không chỉnh models/interfaces/errors hay SPEC. Git hiện chưa có
  commit hoặc file tracked, nên không có baseline để chứng minh diff lịch sử; danh
  sách này là inventory bàn giao, không phải diff đã đối chiếu với một commit gốc.
- `D:\SOFT\STV\slidevoice\cli.py`, `D:\SOFT\STV\slidevoice\__main__.py`,
  `D:\SOFT\STV\slidevoice\__init__.py`.
- `D:\SOFT\STV\slidevoice\plugins\`: render, voice, llm, script, normalize,
  tts, align, subtitle, avatar, compose và package initializer.
- `D:\SOFT\STV\slidevoice\configs\`, `D:\SOFT\STV\configs\`:
  packaged default, root default override và fake.yaml.
- `D:\SOFT\STV\slidevoice\report\__init__.py`.
- `D:\SOFT\STV\samples\make_samples.py`, `D:\SOFT\STV\samples\demo.pptx`,
  `D:\SOFT\STV\samples\voice.wav` (giọng mẫu là tone, không phải người thật).
- `D:\SOFT\STV\tests\`: conftest, unit core/cache/plugins, integration pipeline/
  plugin_swap, golden test và fixture SRT/VTT/ASS/chapters.

## 3. Giả định đã dùng

- `--out` chính là thư mục job. Resume dùng bản input đã copy. Muốn nhận notes đã sửa
  ở file nguồn, chạy lại run cùng `--out`. Một writer cho mỗi job.
- `--from-stage` yêu cầu checkpoint trước đó hợp lệ, chạy lại các stage phía sau nhưng
  vẫn giữ cache từng câu. Consent không có cờ bỏ qua, kể cả resume từ compose.
- M0 được phép nền màu/tiếng bíp. Không triển khai plugin thật M1–M6 hay worker model.
- Fake aligner đọc transcript sidecar. CER giả không chứng minh ASR thật; LUFS chưa đo,
  report để null. Golden fixture đã kiểm tra trong triển khai, còn cần Bộ não duyệt.

## 4. Kết quả kiểm tra thực tế

Môi trường: Windows, Python 3.14.7, ffmpeg/ffprobe 8.1.1, ngày 2026-10-15.

Lệnh chạy từ `D:\SOFT\STV` và output lần kiểm thử đầy đủ:

```text
python -m mypy D:\SOFT\STV\slidevoice
Success: no issues found in 26 source files

python -m ruff check .
All checks passed!

python -m ruff format --check .
37 files already formatted

python -m pytest -q --durations=10
.............................................                            [100%]
45 passed in 9.28s
```

Ruff check và format check đều qua. Integration chạy pipeline mới dưới 60 giây,
kiểm tra ffprobe H.264/AAC 48 kHz/mov_text/vie/3 chapter/metadata, khớp mốc chapter,
audio duration và word offset. Có kiểm tra CLI, resume sau compose lỗi, restart từ TTS,
consent bị tắt trên job đã cache, sửa một câu chỉ synthesize một câu, plugin trả tên
artifact khác, hash file 33 MiB đổi ở giữa dù giữ nguyên mtime, snapshot hỏng/thiếu
output lồng nhau/đường dẫn vượt job, retry worker và không lưu secret lồng nhau.
Các regression mới xác nhận JSON checkpoint không phải object trở thành cache miss,
save từ chối artifact bắt buộc bị thiếu, secret do plugin thêm rồi ném lỗi không vào
manifest/log/JSON, và stage timings trong report khớp chính xác với pipeline.

Chạy thực tế:

```text
python -m slidevoice run --slides D:\SOFT\STV\samples\demo.pptx --voice D:\SOFT\STV\samples\voice.wav --config D:\SOFT\STV\configs\fake.yaml --out D:\SOFT\STV\out\m0_final_20261015_121349
render: executed
script: executed
normalize: executed
voice: executed
tts: executed
align: executed
subtitle: executed
avatar: executed
compose: executed
Done: D:\SOFT\STV\out\m0_final_20261015_121349
```

Job mới chạy hết trong **0.846 giây wall-clock** (bao gồm khởi động CLI). Timing
từng stage ở lần chạy mới, đơn vị giây, làm tròn 6 chữ số:

| Stage | Thời gian |
| --- | ---: |
| render | 0.136690 |
| script | 0.006051 |
| normalize | 0.006376 |
| voice | 0.039535 |
| tts | 0.092842 |
| align | 0.012640 |
| subtitle | 0.016465 |
| avatar | 0.012200 |
| compose | 0.218904 |

Đã lưu bản report lần chạy đầu tại
`D:\SOFT\STV\out\m0_final_20261015_121349\fresh_report.json` trước khi resume;
`report.json` luôn phản ánh lần chạy gần nhất. Resume xác nhận cache-hit toàn bộ 9
stage và SHA-256 video không đổi. Sau đó `--from-stage tts` cache-hit 4 stage trước,
execute 5 stage sau; integration spy xác nhận không gọi synthesize lại câu hợp lệ.

ffprobe trên job mới xác nhận video dài **8.490 giây**, H.264, AAC 48 kHz,
mov_text `vie`, audio `vie`, 3 chapter bắt đầu tại 0.000/3.550/5.930 giây,
AI comment, `encoding_tool=SlideVoice 0.1.0`, video-stream
`encoder=SlideVoice 0.1.0`, container `encoder=Lavf62.12.101`.

**Kiểm tra chưa thành công / giới hạn môi trường:**

- Python 3.11.15 có trên máy nhưng thiếu dependency. Đã tạo môi trường local
  `D:\SOFT\STV\.venv311` (git-ignored); cài offline thất bại vì không có
  `python-pptx`/`wheel` trong cache. Phiên tiếp tục xác nhận môi trường này không có
  pip hay bất kỳ dependency runtime/dev nào được khai báo. Chưa chứng minh runtime
  trên Python 3.11. `ast.parse` bằng Python 3.11.15 đã qua cho cả 34 file Python trong
  source/tests/samples; đây chỉ là kiểm tra cú pháp, không thay thế chạy test runtime.
- Editable install và wheel build với `--no-build-isolation --no-deps` thất bại:
  `BackendUnavailable: Cannot import 'setuptools.build_meta'`. Interpreter hiện tại
  thiếu build backend. Chưa xác nhận lệnh console `slidevoice` đã cài và wheel build.
  CLI `python -m slidevoice` và Typer runner đã chạy thật. Không tải dependency mới.

## 5. Tiêu chí xong của M0

- [x] Core theo hợp đồng dữ liệu/interface, registry, config và CLI.
- [x] Pipeline cache/resume/--from-stage, cache từng câu và consent gate.
- [x] Fake plugin mọi interface; gói đầu ra đủ bằng CLI module.
- [x] Unit/integration/golden test xanh; ffprobe xác nhận video package.
- [x] Ruff và strict mypy (cả package, vượt phạm vi core).
- [ ] Xác nhận bản cài console script, build wheel và runtime Python 3.11: bị chặn
  bởi build/dependency environment, không báo đã qua.

## 6. Rủi ro / việc còn dở

- Chờ Bộ não nghiệm thu; không tự coi M0 đã được chấp nhận.
- Chưa có model thật, giọng nhân bản, ASR thật, PDF/ODP renderer, ref cleaning,
  crossfade, burn-in, production subtitle splitting, avatar hay parallel branches.
- Stage fingerprints bảo thủ: notes đổi có thể chạy lại stage rẻ nhưng sentence
  cache tránh tổng hợp các câu không đổi. Hash file đầy đủ ưu tiên đúng hơn tốc độ.
- Job state là dữ liệu local đáng tin cậy, không phải định dạng import không tin cậy.
  Không hỗ trợ nhiều process ghi đồng thời cùng job.
- Mọi artifact đã được kiểm tra hash nhưng không có chữ ký chống sửa cố ý.

## 7. Đề xuất đổi hợp đồng

- Không đề xuất đổi model hay chữ ký interface.
- Đề nghị làm rõ §5.3: ffmpeg ghi đè `encoder` ở cấp container bằng tên muxer.
  Bản M0 lưu `SlideVoice 0.1.0` vào `encoding_tool` của container và `encoder` của
  video stream, đồng thời giữ container encoder thực. Test xác nhận cả hai vị trí.
- `--out`/`--from-stage`/preview semantics đã ghi README; đề nghị kiến trúc sư duyệt.

**Trạng thái bàn giao:** khung M0 chạy được và test xanh trên Python 3.14.7;
nghiệm thu có điều kiện đối với packaging và Python 3.11, chưa chuyển sang M1–M6.