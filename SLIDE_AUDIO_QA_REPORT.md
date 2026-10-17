# Kiểm tra slide, trình phát và thiết bị âm thanh — 2026-10-15

## Phát hiện quan trọng

Kiểm tra read-only bằng Windows Core Audio cho thấy:

| Vai trò Windows | Thiết bị | Âm lượng | Mute |
| --- | --- | --- | --- |
| Default console / multimedia | GSX 1200 Pro Main Audio | 0% | Có |
| Default communications | HyperX Cloud Flight Wireless | 24% | Không |

Đây là nguyên nhân khả dĩ, có bằng chứng, khiến media có tín hiệu nhưng không
nghe ở đầu ra mặc định. Chưa chứng minh ứng dụng cụ thể không có override riêng.
Không thay đổi thiết bị, mute hoặc âm lượng. Chưa nghe qua tai nghe bằng tai.

Đã gọi `System.Media.SoundPlayer.PlaySync` với WAV kiểm tra trái/phải;
Windows trả exit code 0. Điều này không chứng minh tiếng đến tai nghe, đặc biệt
khi đầu ra mặc định đang mute. Bằng chứng trong `windows_playback.json`.

## Thử với slide thật

- Tạo PPTX ba slide, có văn bản, bố cục và màu nền xanh dương/xanh lá/tím.
- Export bằng PowerPoint được cài trên máy, mở read-only, tắt macro, không cửa sổ.
- Ghép các ảnh slide đã export theo timeline lời đọc Windows SAPI tiếng Anh.
- Không dùng trailer hoặc nền màu giả làm hình video bàn giao lần này.
- Không voice cloning, không giọng Việt, chưa nghiệm thu renderer production.
- Alignment/CER vẫn dựa sidecar, chưa chứng minh đồng bộ âm vị bằng ASR thật.

## Kiểm chứng video và trình duyệt

- MP4 tương thích: 1280×720, H.264 Baseline/yuv420p, AAC stereo 48 kHz.
- Thời lượng: 34,725 giây; −16,47 LUFS, true peak −4,50 dBTP.
- Không có câu im lặng trong report; không có cảnh báo TTS.
- Giải mã toàn bộ A/V của MP4 pipeline, MP4 tương thích và WebM đều thành công.
- HTTP localhost: GET 200; MP4 byte range 206 với Content-Range đúng.
- Chrome headless chạy thời gian thực: currentTime 4,936118 giây, 153 frame,
  audio decoded 88.986 byte, 1280×720, paused=false, muted=false, error=null.
  Đây là bằng chứng trình duyệt thực sự tiến thời gian và giải mã cả audio/video,
  không chỉ đọc metadata. Không tương đương xác nhận nghe bằng tai.
- Đã xem ảnh chụp trình duyệt: hiển thị slide đầu có chữ, không màn hình trống.

## Kiểm thử mã

Ruff check qua; 46 file đúng format; mypy strict qua 28 source file.
Toàn bộ suite: **63 passed in 28.76s**, exit code 0.
Thêm kiểm tra HTTP range, HEAD, range lỗi và pixel video ở giữa từng slide để
phát hiện việc ghép nhầm một nền duy nhất thay vì chuyển slide theo timeline.
Log đầy đủ: `D:\SOFT\STV\out\qa_slides_20261015\delivery\validation.log`.

## Cách mở không phụ thuộc link file của chat

Mở trình duyệt trên máy đang chạy workspace tại http://127.0.0.1:8765/.
Nếu server đã dừng, chạy `D:\SOFT\STV\OPEN_SLIDE_QA.cmd`.
Server chỉ lắng nghe loopback; link này không dùng trên điện thoại/máy khác.

Video: `D:\SOFT\STV\out\qa_slides_20261015\delivery\slides_compatible.mp4`.
PPTX: `D:\SOFT\STV\out\qa_slides_20261015\delivery\fixtures\slides.pptx`.
WAV: `D:\SOFT\STV\out\qa_slides_20261015\delivery\narrated\audio_check.wav`.
Trái/phải: `D:\SOFT\STV\out\qa_slides_20261015\delivery\headphone_check.wav`.

Chọn HyperX nếu đó là tai nghe đang dùng, hoặc bỏ mute GSX nếu tai nghe nối với
GSX. Bắt đầu âm lượng thấp. Người dùng cần xác nhận nghe video và hai kênh;
không ghi `human_listening_verified=true` trước xác nhận thực tế.