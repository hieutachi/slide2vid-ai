# SlideVoice: bài giảng có đạo diễn trình chiếu

## Mục tiêu và phạm vi đã triển khai

Đầu vào: **PPTX có speaker notes + cấu hình LLM API**. Notes nằm trong file
PowerPoint; không phải Node.js. Không cần file giọng cá nhân khi dùng giọng VieNeu
dựng sẵn. Các demo QA cũ được giữ nguyên.

Luồng mới:

1. PowerPoint xuất ảnh slide thật và khung chữ từng dòng sau dàn trang;
   python-pptx lấy chữ, notes, ID và tọa độ shape.
2. LLM nhận ngữ cảnh deck và nội dung slide, tạo JSON: mục tiêu, từng nhịp giảng,
   lời nói, trích dẫn đầu vào, vai trò sư phạm và đối tượng cần nhấn mạnh.
3. Kiểm tra schema, giới hạn lời giảng, trích dẫn chính xác và ID đối tượng.
   JSON sai bị dừng, **không tự thay bằng lời đọc slide**.
4. VieNeu đọc từng nhịp bằng preset. Timeline được tính từ WAV thật từng câu.
5. FFmpeg dựng highlight nhẹ với thanh nhấn bên trái, viền bo góc có đệm cho chữ,
   ellipse cho hình và zoom vào/giữ/trở ra bằng cosine easing (mặc định 1,18 lần,
   giới hạn 1,3). Dòng chữ quá sát nhau dùng highlight thay cho viền dễ đè chữ.
   Sau đó ghép audio, phụ đề mềm và chapter.
6. Xuất MP4 H.264/AAC, transcript, storyboard, timeline JSON và báo cáo QA.

## Chạy với LLM API thật

Yêu cầu Python 3.11, FFmpeg/FFprobe, PowerPoint trên Windows, worker VieNeu đã
cài mô hình (xem `D:\SOFT\STV\workers\vieneu\README.md`). Không cần huấn luyện.

1. Sửa `D:\SOFT\STV\configs\lecture_vietnamese.yaml`:
   - `llm.base_url`: endpoint tương thích Chat Completions, có `/v1` nếu cần.
   - `llm.model`: model ID thực của nhà cung cấp, không giữ `<model-id>`.
   - `llm.response_format`: `json_schema`; chọn `json_object` nếu provider không
     hỗ trợ strict schema. Cả hai vẫn bị kiểm tra schema cục bộ.
   - `script.audience`, `style`, `max_words_per_slide`: mục tiêu người học và độ dài.
   - `tts.preset_voice`: giọng đã nghe thử; mặc định Mai Anh, chưa phải lựa chọn
     được người dùng xác nhận.
   - `compose.max_effects_per_slide`: tối đa hiệu ứng trên slide; đặt 0 để tắt.
   - `compose.zoom_max`: hệ số zoom 1–1,3; `zoom_ramp_sec`: thời gian mỗi đầu
     chuyển động 0,15–2 giây. Nhịp ngắn tự rút ngắn cả hai đầu.
   - `compose.annotation_fade_sec`: fade điểm nhấn 0–0,5 giây (mặc định 0,18).
   - `compose.zoom_min_sec`: nhịp ngắn hơn 1,2 giây dùng highlight thay zoom.
   - `compose.max_zooms_per_slide`: mặc định 1; `zoom_cooldown_sec`: mặc định 2 giây.
   - `compose.reduced_motion: true`: thay zoom bằng highlight, tắt mọi fade.
     Đây là cấu hình lúc dựng video, không phải tùy chọn đổi video trong player.
2. Đặt API key trong môi trường tiến trình PowerShell, không ghi vào YAML/git.
   Giá trị biến `LLM_API_KEY` phải là key thật của bạn.
3. Duyệt kịch bản trước (không cần worker GPU đang chạy):

```powershell
& D:\SOFT\STV\.venv311\Scripts\python.exe -m slidevoice lecture --slides D:\TaiLieu\bai_giang.pptx --config D:\SOFT\STV\configs\lecture_vietnamese.yaml --out D:\SOFT\STV\out\bai_giang --review-only
```

Mở `D:\SOFT\STV\out\bai_giang\work\script\storyboard.html`: bấm từng nhịp
để xem vùng nguồn trên ảnh slide (mở trực tiếp cũng được, không cần GPU/JavaScript
framework). Preview này là khung hình học nguồn, không mô phỏng chuyển động/audio.
Đọc thêm `storyboard.md` cùng từng `slide_NNN.plan.json`.
Mặc định không có cổng duyệt bắt buộc: lệnh không có
`--review-only` sẽ chạy toàn bộ. Đây là khả năng preview, không phải human approval.

4. Khởi động worker trong terminal riêng **chỉ nếu cổng 8770 chưa có worker**:

```powershell
& D:\SOFT\STV\workers\vieneu\.venv\Scripts\python.exe D:\SOFT\STV\workers\vieneu\server.py --allowed-root D:\SOFT\STV\out --cache-root D:\SOFT\STV\models\vieneu --port 8770
```

5. Tiếp tục job đã duyệt, tái sử dụng render/kịch bản còn hợp lệ:

```powershell
& D:\SOFT\STV\.venv311\Scripts\python.exe -m slidevoice resume D:\SOFT\STV\out\bai_giang
```

Không sửa riêng file JSON rồi mong resume tự dùng bản sửa: cache kiểm tra hash,
nên file bị sửa sẽ được tạo lại. Muốn thay nội dung, chỉnh notes trong PPTX gốc,
rồi chạy lại lệnh `lecture` với cùng `--out`. Muốn thay style/model, sửa YAML và
chạy lại. `resume --config` hỗ trợ override cấu hình đã lưu.

## Dữ liệu gửi ra ngoài và độ tin cậy học thuật

- Adapter gửi **text, notes toàn deck và thông tin shape** tới endpoint LLM đã cấu
  hình. Không gửi audio hoặc ảnh. Chỉ dùng tài liệu được phép gửi cho nhà cung cấp.
- Slide/notes là dữ liệu không tin cậy trong prompt, không phải chỉ dẫn hệ thống.
  Đây là phòng vệ ở mức prompt, không bảo đảm chống mọi prompt injection.
- LLM được yêu cầu giải thích bám nguồn, không bịa tài liệu nghiên cứu hay số liệu.
  Trích dẫn nguyên văn được kiểm tra bằng chuỗi con. Điều đó chứng minh nguồn
  trích có tồn tại, **không chứng minh suy luận hay diễn giải đúng**.
- Chưa có tìm kiếm web, RAG, kiểm chứng bài báo hoặc cơ chế sửa lỗi học thuật tự động.
  Muốn giải thích một hình/biểu đồ hoặc công thức không trích được chữ, bổ sung
  notes. Vision, OCR và phân tích biểu đồ chưa được triển khai.
- Shape group được khoanh toàn nhóm; không có bounding box từng chữ. Đối tượng
  nhỏ bên trong ảnh không thể tự khoanh chỉ từ tên shape.
- Renderer PowerPoint bổ sung ID `shape_N_line_M`, `parent_id` và nguồn
  `powerpoint_text_line`. LLM ưu tiên chọn dòng; việc chọn đúng ý vẫn cần duyệt.
  Textbox xoay, chữ dọc, group và nội dung bên trong bảng/ảnh chưa có đích dòng.
  `fake_render` không đo dòng và không được quảng bá là hình học dòng thật.
- Timeline v2 ghi `target_text`, `geometry_source`, `rendered_effect`, vùng đệm
  pixel và cảnh báo thị giác. Preview có thể dùng đích thô; cần kiểm tra cảnh báo.

## Giới hạn trình chiếu và YouTube

- Đây là hiệu ứng bổ sung lên ảnh slide, không phát lại animation/transition gốc
  của PowerPoint. Zoom đã có nội suy vào/ra theo frame nhưng FFmpeg zoompan vẫn
  có lượng tử hóa theo pixel; chưa có tracking chuyển động hay layout thích ứng.
- Khoanh/nổi/zoom bật trong thời gian câu nói. Không bảo đảm khớp một từ cụ thể.
   `fake_align` vẫn là sidecar, không phải ASR độc lập. `readable_subtitle` chia
   caption thành trang tối đa 2 dòng, khoảng 42 ký tự/dòng (không chẻ từ dài).
   Thời gian trang được ước lượng theo số ký tự trong câu; không phải word alignment.
   Trang giữ nguyên ranh giới câu, không tràn vào khoảng nghỉ. Không bảo đảm tốc độ
   đọc tối đa nếu câu nói nhanh; hãy kiểm tra trên thiết bị đích.
- Có MP4 1080p theo cấu hình thật, phụ đề SRT/VTT/ASS và chapter. YouTube không
  tự lấy phụ đề mềm từ MP4: cần upload SRT riêng. `chapters.txt` là mốc từng slide;
  trước khi dán mô tả YouTube cần nhóm chương đủ dài và kiểm tra quy tắc nền tảng.
- Không tự đăng lên YouTube, không tạo thumbnail/SEO hay nhạc nền.
- Presenter cache clip từng slide theo hash nội dung, hiệu ứng, frame/FPS và encoder.
  Cache hỏng hoặc đổi cấu hình sẽ dựng lại clip liên quan. Ghép cuối stream-copy
  H.264, không encode hình lần hai; audio vẫn mix/encode một lần. Chưa tối ưu RAM cho bài giảng
  nhiều giờ. Ngữ cảnh toàn deck cũng có thể vượt context window model; không tự
  cắt mất notes để giả vờ đủ ngữ cảnh. Chia deck thành bài nhỏ khi cần.
- Luôn duyệt nội dung và nghe thử trước khi đăng. Các cờ human listening, ASR và
  academic verification giữ `false` cho đến khi có đánh giá thật.

## Demo không cần LLM API

`D:\SOFT\STV\samples\lecture_demo.py` có bài thống kê ba slide, kịch bản soạn sẵn,
ghi nhãn rõ **fixture không phải kết quả LLM**. Với worker VieNeu đang chạy:

```powershell
& D:\SOFT\STV\.venv311\Scripts\python.exe -m samples.lecture_demo --out D:\SOFT\STV\out\lecture_demo --speech vieneu --render powerpoint
& D:\SOFT\STV\.venv311\Scripts\python.exe -m samples.playback --root D:\SOFT\STV\out\lecture_demo --port 8767
```

Xem `http://127.0.0.1:8767/`. Nếu không có PowerPoint/GPU, mặc định CLI demo dùng
ảnh màu + beep để kiểm tra pipeline, **không đại diện chất lượng bài giảng**.

### Studio v2 — giữ nguyên bản demo và QA cũ

```powershell
& D:\SOFT\STV\.venv311\Scripts\python.exe -m samples.lecture_demo --out D:\SOFT\STV\out\lecture_demo\studio_v2 --speech vieneu --render powerpoint --reuse-audio D:\SOFT\STV\out\lecture_demo\lesson
& D:\SOFT\STV\.venv311\Scripts\python.exe -m samples.verify_lecture_demo --root D:\SOFT\STV\out\lecture_demo\studio_v2 --url http://127.0.0.1:8767/studio_v2/
```

Player đang phục vụ thư mục demo cũ có thể mở Studio tại
`http://127.0.0.1:8767/studio_v2/`, không cần khởi động server thứ hai.
Hoặc dùng `D:\SOFT\STV\OPEN_LECTURE_STUDIO.cmd`.
Giao diện có nhịp giảng bấm để tua và theo dõi nhịp đang phát, transcript,
phụ đề, timeline và liên kết duyệt vùng nhấn. Nội dung nguồn được escape,
không chèn thành HTML thực thi.

`--reuse-audio` chỉ chép cache câu của job cũ; pipeline vẫn kiểm tra hash audio,
transcript, giọng, TTS và cấu hình trước khi dùng. Không đảm bảo cache hit khi
đã đổi giọng/nội dung/cấu hình. Demo v2 vẫn **1280×720**, fixture soạn sẵn,
không phải đánh giá chất lượng LLM thật. Validator kiểm tra giải mã AV toàn bộ,
mốc câu, target dòng, screenshot và hash; không chứng nhận nghe hay học thuật.

### Studio v3 — phụ đề ngắn và điều khiển học tập

Demo mới nằm riêng tại `D:\SOFT\STV\out\lecture_demo\studio_v3`; v2 không bị ghi đè.
Mở `http://127.0.0.1:8767/studio_v3/` khi server thư mục demo đang chạy.

```powershell
& D:\SOFT\STV\.venv311\Scripts\python.exe -m samples.lecture_demo --out D:\SOFT\STV\out\lecture_demo\studio_v3 --speech vieneu --render powerpoint --reuse-audio D:\SOFT\STV\out\lecture_demo\studio_v2\lesson
& D:\SOFT\STV\.venv311\Scripts\python.exe -m samples.verify_lecture_demo --root D:\SOFT\STV\out\lecture_demo\studio_v3 --url http://127.0.0.1:8767/studio_v3/
```

Player thêm tốc độ 0,75–2×, nhịp trước/sau, lặp nhịp. Ngoài vùng nút, nhập liệu
và video: Space phát/dừng, ←/→ tua 5 giây, `[`/`]` đổi nhịp, L bật/tắt lặp.
Tua ra ngoài nhịp sẽ tắt lặp; đổi nhịp bằng nút sẽ chuyển vòng lặp sang nhịp mới.
Vòng lặp dùng sự kiện media của trình duyệt, không cam kết chính xác từng frame.
Tùy chọn reduced motion trong CSS không tắt chuyển động đã encode trong MP4;
cần dựng với `compose.reduced_motion: true` nếu cần video ít chuyển động.

### Studio v4 — bài thử 24 slide Full HD

Mở `D:\SOFT\STV\OPEN_LECTURE_24_SLIDES.cmd`, hoặc khi server cổng 8767 đang chạy:
<http://127.0.0.1:8767/studio_v4_24slides/>.

- MP4: `D:\SOFT\STV\out\lecture_demo\studio_v4_24slides\lesson\video.mp4`.
- PPTX: `D:\SOFT\STV\out\lecture_demo\studio_v4_24slides\lesson.pptx`.
- Kịch bản 24 slide khác nhau về đọc hiểu dữ liệu, **soạn sẵn**, không phải đánh
  giá LLM API thật; biểu đồ và số liệu là ví dụ giả định. Giọng VieNeu preset,
  PowerPoint xuất slide thật, 1920×1080, 30 FPS, H.264/AAC, 24 chapter.
- Player có chọn slide theo tiêu đề, slide trước/sau, tìm kiếm không dấu,
  bật/tắt phụ đề, tùy chọn tiếp tục vị trí lần trước (lưu cục bộ trình duyệt).
  Không tự phát khi mở trang, không thay đổi thiết bị/âm lượng hệ thống.
- `readable_subtitle@0.2.1` cân cả trang và dòng, không dồn vài từ cuối câu
  thành một trang chớp nhanh. Timing trong câu vẫn ước lượng. Báo cáo chỉ số
  đọc trong `D:\SOFT\STV\out\lecture_demo\studio_v4_24slides\validation.json`.
- Chromium headless kiểm tra phát media thật và viewport 390px; không đồng nghĩa
  đã test thiết bị di động thật hoặc nghe trọn video bằng tai.
- Khảo sát repo và giới hạn: `D:\SOFT\STV\REPO_RESEARCH_V4.md`.

```powershell
& D:\SOFT\STV\.venv311\Scripts\python.exe -m samples.lecture_long_demo --out D:\SOFT\STV\out\lecture_demo\studio_v4_24slides --real
& D:\SOFT\STV\.venv311\Scripts\python.exe -m samples.verify_lecture_demo --root D:\SOFT\STV\out\lecture_demo\studio_v4_24slides --url http://127.0.0.1:8767/studio_v4_24slides/ --expected-slides 24
```

Không dùng bản giả lập mặc định (ảnh màu + beep) để đánh giá chất lượng giọng.
Để test: nghe ở 1× trước, bật phụ đề, thử slide 7–10 về cách tính, slide 13–14
về tự kiểm tra, và slide 18–20 về biểu đồ/nhân quả. Ghi lại mốc thời gian khi
thấy phát âm, phụ đề hoặc điểm nhấn không phù hợp. Cần duyệt nội dung trước khi đăng.