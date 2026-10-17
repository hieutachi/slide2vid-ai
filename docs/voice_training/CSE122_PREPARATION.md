# Chuẩn bị giọng cá nhân và bài giảng Nền tảng web CSE122

## Trạng thái thực tế

- Chưa train/fine-tune; chưa có checkpoint giọng cá nhân.
- Worker VieNeu hiện tại chỉ tổng hợp bằng preset. Không đổi tên preset thành giọng đã train.
- Đã phát hiện NVIDIA RTX 3090 24 GB; đây không phải bằng chứng training tương thích hoặc đủ VRAM với mọi cấu hình.
- Chưa có đề cương/slide CSE122 chính thức trong checkout. Mã học phần chưa đủ xác định trường, phiên bản và nội dung giảng dạy.
- Chưa nhận bộ bản thu, transcript đã đối chiếu và xác nhận quyền sử dụng giọng.
- Không tự dùng `samples/voice.wav`, giọng trong video có sẵn hay âm thanh tổng hợp làm dữ liệu giọng người.

## Cần nhận trước khi huấn luyện

1. Người nói là ai; xác nhận người đó đồng ý dùng bản thu để fine-tune, tạo giọng tổng hợp cho bài giảng, và phạm vi sử dụng/chia sẻ. Không cần đưa giấy tờ định danh vào repository.
2. Audio gốc và transcript đúng lời thực sự đã nói, có quyền sử dụng cho mục đích này. Cho biết nếu bản thu có người nói khác, nhạc, dữ liệu cá nhân hoặc hạn chế sử dụng.
3. Đề cương hoặc slide chính thức CSE122, tên trường và chương/bài muốn làm đầu tiên; xác nhận quyền chuyển tài liệu thành video.

Không upload dữ liệu tới dịch vụ bên ngoài hoặc công khai giọng/checkpoint mặc định. Không suy ra sự đồng ý của người nói chỉ từ việc người dùng có file âm thanh.

## Thu âm

- Một người nói, cùng micro và khoảng cách; phòng yên, không nhạc/hiệu ứng, không chồng tiếng.
- Giữ WAV gốc, ưu tiên PCM mono 24 hoặc 48 kHz; không đổi nhãn sample rate hay upsample để giả chất lượng.
- Đọc giọng tự nhiên như giảng bài; phát âm số, từ viết tắt và thuật ngữ nhất quán. Không cố bắt chước người khác.
- Mỗi clip một câu/ngữ đoạn hoàn chỉnh, không cắt mất âm đầu/cuối. Mốc 1–20 giây là gợi ý ban đầu từ hướng dẫn VieNeu đã ghi trong báo cáo dự án, cần kiểm lại với trainer được chọn.
- Nếu đọc khác kịch bản, sửa transcript theo âm thanh; không giữ chữ dự định đọc.
- Không áp dụng khử nhiễu/nén âm quá mạnh lên bản duy nhất. Giữ bản gốc và bản xử lý tách biệt.

`recording_prompts.csv` là bộ câu khởi đầu **24 câu train, 8 câu eval**, không phải dataset âm thanh. Bộ nhỏ này chưa đủ kết luận về chất lượng fine-tune. Hướng dẫn nhà phát hành từng gợi ý 10–30 phút / 100–300 câu đa dạng; đây không phải ngưỡng bảo đảm. Cần bổ sung cả ngôn ngữ phổ thông, không chỉ thuật ngữ web.

Tên gợi ý: `train_001.wav`, `eval_001.wav`, theo cột `id`. Lưu audio và transcript đã sửa dưới `D:\SOFT\STV\data\private_voice\`, checkpoint dưới `D:\SOFT\STV\runs\voice_training\`; hai thư mục đã được thêm vào `.gitignore`. Không đặt dữ liệu giọng cá nhân vào `samples/` hoặc tài liệu công khai. `.gitignore` không mã hóa dữ liệu, kiểm soát quyền truy cập, chặn backup hay bảo vệ file đã được theo dõi trước đó.

## Chia dữ liệu và đánh giá

- Giữ câu eval ngoài train, gradient updates, chọn reference và xử lý tăng cường dữ liệu; phát hiện trùng nội dung/audio giữa các split.
- Tập eval dùng theo dõi và chọn checkpoint. Trước nghiệm thu, cần thêm **tập test chưa dùng để chọn checkpoint**, tốt nhất từ phiên thu khác cùng người nói.
- Với token viết tắt như HTML, CSS, URL: transcript phải ghi đúng quy ước trainer/normalizer và cách người nói thực sự đọc. Không tự thay toàn bộ thành phiên âm khi chưa kiểm chứng.
- Trước train: kiểm tra sample rate, kênh, duration, clipping, im lặng dài, transcript, một người nói, quyền sử dụng và phân chia dữ liệu.
- Đo baseline pretrained trên cùng văn bản; khi hỗ trợ reference, chỉ dùng mẫu được phép và không lấy từ eval/test.
- So sánh baseline và checkpoint với cùng điều kiện inference. Nghe mù về độ rõ, âm sắc, dấu tiếng Việt, thuật ngữ, nhịp, từ thiếu/lặp.
- ASR độc lập chỉ hỗ trợ phát hiện lỗi; CER/WER không đo đủ giống giọng hoặc độ tự nhiên. Không dùng `fake_align` làm bằng chứng phát âm.
- Chọn LoRA hoặc phương pháp khác sau khi xác minh hướng dẫn trainer, phiên bản model, license và hỗ trợ Windows/Linux. Không giả định SDK inference hiện có đã chứa trainer tương thích.
- Chạy preflight và mini-run trước; giới hạn steps/thời gian/VRAM/đĩa, lưu cấu hình và checkpoint, dừng khi validation xấu đi. Không chạy vô hạn theo ngân sách token.

## Điều kiện chuyển sang video CSE122

1. Chốt mục tiêu học tập, thuật ngữ và nguồn bài giảng theo tài liệu thật.
2. Duyệt kịch bản và chạy ví dụ HTML/CSS/JavaScript tương ứng với bài được chọn.
3. Xuất đoạn giọng thử ngắn từ checkpoint đã đánh giá, nghe duyệt trước khi tổng hợp cả bài.
4. Render video, kiểm tra giải mã AV, âm lượng, phụ đề, đồng bộ và nội dung; giữ các cờ ASR/nghe duyệt ở false cho tới khi có bằng chứng.

Khung bài nhập môn tạm thời nằm tại `D:\SOFT\STV\docs\courses\CSE122_DRAFT.md`. Chưa tạo video mới và chưa thay đổi demo 24 slide.