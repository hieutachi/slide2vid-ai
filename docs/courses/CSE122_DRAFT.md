# Nền tảng web — khung bài mở đầu dự kiến cho CSE122

**Bản nháp tự soạn, chưa đối chiếu đề cương chính thức.** Không suy luận trường, số tín chỉ, chuẩn đầu ra, lịch học hay đánh giá học phần từ mã CSE122. Chưa phải slide chính thức hoặc bài giảng đã nghiệm thu.

## Phạm vi đề xuất

Bài mở đầu: **Từ địa chỉ trang web đến nội dung trên trình duyệt**.

Mục tiêu dự kiến sau bài học:

1. Phân biệt vai trò trình duyệt, máy chủ và tài nguyên web.
2. Nhận biết các thành phần cơ bản của URL.
3. Mô tả ở mức nhập môn chu trình request/response và ý nghĩa mã trạng thái.
4. Phân biệt vai trò HTML, CSS, JavaScript.
5. Dùng công cụ nhà phát triển quan sát một trang đơn giản.

## Storyboard dự kiến

| Slide | Ý chính | Minh họa / kiểm tra hiểu |
| --- | --- | --- |
| 1 | Mục tiêu và tình huống truy cập trang học tập | Hỏi: nhập địa chỉ xong thì chuyện gì xảy ra? |
| 2 | Trình duyệt và máy chủ | Sơ đồ hai vai trò, không đồng nhất Internet với Web |
| 3 | URL và tên miền | Tách thành phần của một địa chỉ ví dụ; lưu ý đường dẫn không luôn tương ứng tệp vật lý |
| 4 | DNS ở mức khái niệm | Tra địa chỉ và cache; không khẳng định luôn tra lại mỗi request |
| 5 | Request và response | Minh họa HTTP; không mô tả mọi phản hồi đều có body |
| 6 | Mã trạng thái | So sánh 200, 404 và 500; mã 200 không bảo đảm đúng nghiệp vụ |
| 7 | HTML | Tiêu đề, đoạn văn, liên kết; cấu trúc có ý nghĩa |
| 8 | CSS | Cùng nội dung với cách trình bày khác nhau |
| 9 | JavaScript | Nút tương tác có phản hồi; không coi JS là bắt buộc cho mọi trang |
| 10 | DevTools | Quan sát Elements, Console, Network trên ví dụ do mình tạo |
| 11 | Thực hành có hướng dẫn | Thay tiêu đề, màu và phản hồi của nút; dự đoán rồi kiểm tra |
| 12 | Tổng kết và câu hỏi | Giải thích vì sao HTML tải được nhưng ảnh trả 404 |

## Lời mở đầu mẫu

“Khi bạn nhập địa chỉ một trang học tập vào trình duyệt, nội dung không tự xuất hiện từ một tệp duy nhất trên máy. Trình duyệt có thể cần tìm địa chỉ của máy chủ, gửi yêu cầu và nhận nhiều tài nguyên khác nhau. Trong bài này, chúng ta tách từng vai trò để hiểu điều gì đang xảy ra, rồi dùng công cụ của trình duyệt để tự quan sát. Các sơ đồ ban đầu là mô hình đơn giản; bộ nhớ đệm, kết nối có sẵn và cách triển khai thực tế có thể làm chu trình khác đi.”

## Việc cần chốt từ tài liệu môn học

- Trường, học kỳ, phiên bản đề cương và kiến thức tiên quyết.
- Bài/chương bắt đầu, thời lượng, chuẩn đầu ra và công nghệ bắt buộc.
- Có yêu cầu backend, framework, cơ sở dữ liệu hay triển khai không; không tự thêm vào phạm vi môn.
- Tài liệu nào được dùng lại, hình ảnh nào có quyền sử dụng và cách ghi nguồn.
- Quy ước đọc HTML, CSS, HTTP, HTTPS, URL, API, DOM trong giọng giảng.

Chỉ chuyển bản nháp này thành bài giảng gắn nhãn CSE122 sau khi đối chiếu nguồn môn học. Việc chuẩn bị nội dung không đồng nghĩa đã train giọng, gọi LLM thật hay render video.