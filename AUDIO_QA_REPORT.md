# QA âm thanh SlideVoice — 2026-10-15

> Cập nhật tiếp theo: đã thử với slide PowerPoint thật và kiểm tra Chrome playback;
> phát hiện đầu ra multimedia GSX đang mute ở 0%. Xem
> `D:\SOFT\STV\SLIDE_AUDIO_QA_REPORT.md`. Phần dưới là kết quả fixture trailer
> trước đó, không phải báo cáo mới nhất về thiết bị phát.

## Kết luận và phạm vi

**Đạt kiểm tra kỹ thuật cho fixture video tải về + lời đọc tổng hợp tiếng Anh.**
Không gọi đây là nghiệm thu sản phẩm giọng Việt, voice cloning hoặc slide thật.
Không thay đổi `D:\SOFT\STV\slidevoice\core\models.py`,
`D:\SOFT\STV\slidevoice\core\interfaces.py` hay `D:\SOFT\STV\SPEC.md`.
Chưa tự chuyển sang nghiệm thu M1–M6.

## 1. Điều tra output cũ

Đã giải mã lại cả ba file:

- `D:\SOFT\STV\out\m0\video.mp4`
- `D:\SOFT\STV\out\m0_acceptance\video.mp4`
- `D:\SOFT\STV\out\m0_final_20261015_121349\video.mp4`

Cả ba có AAC và tín hiệu beep thật: mean −16,8 dBFS, peak −10,5 dBFS.
Bản cuối có 203.776 mẫu PCM mono ở 24 kHz sau giải mã; peak 9.824/32.768.
**Không có narration bằng lời nói:** `fake_tts` chỉ tạo tone 440 Hz.
Do đó không có bằng chứng file bị digital silence, nhưng bản demo trước chưa đáp
ứng trải nghiệm lời đọc. Chưa xác định được nguyên nhân trình phát/thiết bị của
người dùng không phát được beep; không tự quy lỗi cho máy người dùng.

## 2. Video tải về và cách sử dụng

- Nguồn: https://media.w3.org/2010/05/sintel/trailer.mp4
- File: `D:\SOFT\STV\out\qa_audio_20261015\sintel-trailer.mp4`
- Kích thước: 4.372.373 byte; thời lượng container 52,208333 giây.
- SHA-256: `b670602fa00934ca27c4351bb0efe7ea7a07fae57284e44226025eeed7c51254`.
- Bản quyền: Blender Foundation, CC BY 3.0; https://durian.blender.org/sharing/.
- Audio nguồn có tín hiệu: −12,91 LUFS, true peak +1,16 dBTP. Đây không phải
  audio đã chuẩn hóa; không dùng nó để đánh giá output narration.

Đã tạo hai nhánh độc lập:

1. Narration qua pipeline, dùng hình trailer và lời đọc Microsoft Zira Desktop.
   Không trộn audio gốc; không học, clone hay suy diễn consent của diễn viên.
2. Bản đối chứng giữ toàn bộ trailer và audio gốc, chỉ chuẩn hóa audio. Dùng để
   so sánh với output narration nếu trình phát không có tiếng.

## 3. Thay đổi triển khai

- `D:\SOFT\STV\slidevoice\core\media.py`: đo LUFS, true peak, loudness range,
  RMS/peak từ audio đã giải mã. Tách volumedetect khỏi loudnorm để không cắt
  tín hiệu float AAC trước khi đo true peak; đọc log UTF-8 an toàn.
- `D:\SOFT\STV\slidevoice\report\__init__.py`: đo MP4 cuối và từng WAV câu;
  ghi `audio`, `silent_segments`, `qa_status` và LUFS thật. Narration im lặng
  toàn phần hoặc một câu sẽ ghi report failed và ném lỗi, kể cả khi resume.
  Đây là kiểm tra mức tín hiệu, không chứng minh hiểu lời hay CER thật.
- `D:\SOFT\STV\slidevoice\plugins\tts\sapi.py` và
  `D:\SOFT\STV\slidevoice\plugins\tts\__init__.py`: adapter Windows system
  speech tùy chọn, offline, giữ consent gate, không đọc/học reference voice.
  Chỉ chấp nhận `language: en` trong fixture đã kiểm chứng.
- `D:\SOFT\STV\slidevoice\plugins\compose\__init__.py`: AAC stereo mặc định,
  giữ audio track default; composer QA dùng video tải về, scale/pad về output,
  map narration riêng, không dùng tiếng người trong nguồn. Tăng version composer
  để không dùng lại cache output cũ.
- `D:\SOFT\STV\slidevoice\core\pipeline.py`: hash background video trong cache
  compose; sửa nội dung background sẽ làm mất hiệu lực checkpoint compose.
- `D:\SOFT\STV\configs\qa_speech.yaml`,
  `D:\SOFT\STV\samples\audio_qa.py`: fixture tái lập, trang nghe đối chiếu,
  attribution, WAV riêng và bảng so sánh phép đo.
- `D:\SOFT\STV\tests\unit\test_audio_qa.py`,
  `D:\SOFT\STV\tests\integration\test_pipeline.py`,
  `D:\SOFT\STV\tests\golden\test_golden.py`: regression signal/silence,
  một câu im lặng, resume không được trả xanh với audio hỏng, SAPI runtime,
  consent/ngôn ngữ, stereo/default stream và invalidation video nền.
- `D:\SOFT\STV\README.md`, `D:\SOFT\STV\M0_REPORT.md`: bổ sung hướng dẫn QA,
  phân biệt số liệu lịch sử với lần kiểm tra mới.

Không thêm dependency Python, không thay đổi chính sách thực thi của Windows.
Môi trường chạy: Windows, Python 3.14.7, FFmpeg/FFprobe 8.1.1,
Microsoft Zira Desktop (en-US). Python 3.11 runtime và packaging vẫn chưa được
xác minh trong lượt này; không coi mypy target 3.11 là runtime test 3.11.

## 4. Output bàn giao

Mở trang `D:\SOFT\STV\out\qa_audio_20261015\delivery\listen.html`, bấm Play.
Trang không autoplay/mute; trình phát và hệ điều hành vẫn có thể có mute riêng.

- Video: `D:\SOFT\STV\out\qa_audio_20261015\delivery\narrated\video.mp4`
- WAV: `D:\SOFT\STV\out\qa_audio_20261015\delivery\narrated\audio_check.wav`
- Control: `D:\SOFT\STV\out\qa_audio_20261015\delivery\source_audio_control.mp4`
- Report: `D:\SOFT\STV\out\qa_audio_20261015\delivery\narrated\report.json`
- Bằng chứng FFprobe: `D:\SOFT\STV\out\qa_audio_20261015\delivery\narrated\ffprobe.json`
- Phép đo đối chiếu: `D:\SOFT\STV\out\qa_audio_20261015\delivery\comparison.json`
- Kiểm tra output: `D:\SOFT\STV\out\qa_audio_20261015\delivery\acceptance_checks.json`
- Log test: `D:\SOFT\STV\out\qa_audio_20261015\delivery\validation.log`

| Thuộc tính narration | Kết quả kiểm chứng |
| --- | --- |
| Video | H.264, 1920 × 1080, yuv420p, 30 fps |
| Audio | AAC, 48.000 Hz, stereo, default track |
| Thời lượng container | 32,672 giây |
| Chênh lệch thời lượng video/audio | 5,333 ms (không phải đo đồng bộ âm vị) |
| Integrated loudness | −16,63 LUFS |
| True peak | −4,49 dBTP |
| RMS / sample peak | −20,4 / −4,5 dBFS |
| Câu có tín hiệu | 6/6, không có `silent_segments` |
| Peak từng câu trên PCM giải mã từ MP4 | 19.480–19.541 / 32.768 |
| Subtitle | mov_text, `eng`; SRT/VTT/ASS riêng |
| Chapter | 3, theo fixture 3 slide notes |
| Decode toàn bộ A/V với `-xerror` | Exit code 0 |
| Artifact bắt buộc | 9/9 tồn tại và không rỗng |
| Resume | 9/9 cache hit, SHA-256 MP4 không đổi |
| SHA-256 MP4 | `9fe2cf5ea1727c0f241c261ca4d556220334e78ae6610c72f5ba22e64bfd8e6f` |

Control có −15,81 LUFS và true peak −1,83 dBTP sau AAC; vẫn giữ soundtrack gốc.
Đã xem frame trích xuất ở giây 8: có nội dung Sintel, không chỉ nền màu của M0.

## 5. Log kiểm thử đã lưu đọc được

```text
python -m ruff check .
All checks passed!
EXIT_CODE=0

python -m ruff format --check .
41 files already formatted
EXIT_CODE=0

python -m mypy slidevoice
Success: no issues found in 27 source files
EXIT_CODE=0

python -m pytest -q --durations=10
...................................................                      [100%]
51 passed in 21.86s
EXIT_CODE=0
```

Lượt đầu phát hiện một golden test gọi package writer trước khi có MP4; đã sửa
test chạy pipeline đầy đủ, không bỏ qua kiểm tra audio để làm test xanh.

## 6. Những điều chưa được chứng minh

- **Chưa nghe bằng tai:** agent xác minh tín hiệu và codec, không có xác nhận từ
  người nghe/loa. `human_listening_verified: false` được ghi trong bằng chứng.
- Fixture tiếng Anh, không phải giọng Việt hoặc giọng nhân bản của người dùng.
- CER vẫn dựa transcript sidecar; không phải nhận dạng lời nói độc lập. Word
  alignment vẫn chia đều; chưa chứng minh subtitle lệch âm vị dưới 150 ms.
- Đây là QA đường media, không triển khai renderer slide thật, ASR thật, clone
  voice, crossfade, avatar hay typography phụ đề production.
- Report `qa_status` xác nhận kiểm tra mức âm thanh được triển khai, không chứng
  nhận toàn bộ yêu cầu sản phẩm. File im lặng cố ý chỉ được chấp nhận khi không
  có narration segment; không dùng điều này để che lỗi TTS.

**Bước xác nhận của người dùng:** nghe narration MP4 hoặc WAV trong trang đối
chiếu trước khi đưa voice thật (có consent) và slide thật vào các milestone sau.