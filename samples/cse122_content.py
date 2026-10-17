"""Hand-authored narration aligned to the first six supplied CSE122 HTML slides."""

COURSE_REVISION = "06cbc40dd1e152e5b1504564cd4711590627f684"
COURSE_URL = "https://hieutachi.github.io/cse122-k67/ebook/chuong-2.html"
LESSONS = (
    ("HTML là gì?", (
        "Chào các bạn. Đây là bài giảng thử nghiệm với giọng nói tổng hợp, dựa trên sáu slide đầu của chương hai, môn phát triển ứng dụng web cơ bản.",
        "Hãy hình dung trang web như một ngôi nhà. HTML tạo cấu trúc nội dung, CSS phụ trách cách trình bày, còn JavaScript bổ sung hành vi tương tác.",
        "Trình duyệt phân tích tài liệu thành cây DOM. Các phần tử như tiêu đề, đoạn văn và liên kết cho biết nội dung có ý nghĩa gì, chứ không chỉ trông như thế nào.",
    )),
    ("Cấu trúc tệp HTML", (
        "Một tệp HTML bắt đầu bằng khai báo kiểu tài liệu, rồi đến phần tử gốc. Thuộc tính ngôn ngữ giúp công nghệ hỗ trợ nhận biết tiếng Việt.",
        "Phần head chứa thông tin mô tả tài liệu. Phần body chứa nội dung của trang. Hãy phân biệt tiêu đề trên thẻ trình duyệt với tiêu đề được hiển thị trong bài viết.",
        "Khi tạo tệp mới, hãy lưu với bộ mã UTF tám, mở trong trình duyệt và kiểm tra cấu trúc lồng nhau. Không chỉ kiểm tra xem trang có mở được hay không.",
    )),
    ("Metadata trong head", (
        "Metadata là dữ liệu mô tả tài liệu. Khai báo bộ mã hỗ trợ hiển thị tiếng Việt; viewport giúp trình duyệt di động sử dụng khung nhìn phù hợp.",
        "Tiêu đề nên ngắn gọn và đặc trưng cho từng trang. Mô tả có thể được công cụ tìm kiếm sử dụng, nhưng không bảo đảm được hiển thị hay tăng thứ hạng.",
        "Liên kết stylesheet nạp CSS. Với script cổ điển đặt trong head, thuộc tính defer cho phép thực thi sau khi phân tích tài liệu, thay vì chặn quá trình phân tích lúc tải script.",
    )),
    ("Phân cấp tiêu đề", (
        "Tiêu đề tổ chức nội dung theo thứ bậc. Nên có một tiêu đề chính rõ ràng cho trang, rồi dùng tiêu đề cấp hai cho phần lớn và cấp ba cho tiểu mục.",
        "Đây là khuyến nghị tổ chức nội dung, không phải quy tắc cú pháp cấm mọi trường hợp có nhiều tiêu đề cấp một. Đừng chọn cấp tiêu đề chỉ vì muốn chữ to hay nhỏ.",
        "Trong ví dụ sự kiện, thời gian và đối tượng tham gia là các tiểu mục cùng cấp. Chú ý hình cây trên slide có một nhãn cấp sáu không nhất quán với mã minh họa cấp ba.",
    )),
    ("Nội dung văn bản", (
        "Dùng phần tử đoạn văn cho một đoạn hoàn chỉnh. Phần tử xuống dòng chỉ phù hợp khi cần ngắt dòng bên trong nội dung, không phải để tạo khoảng cách bố cục.",
        "Strong biểu thị tầm quan trọng, còn em biểu thị nhấn giọng. Không nên dùng chúng chỉ để đổi kiểu chữ; cách trình bày thuộc trách nhiệm của CSS.",
        "Code đánh dấu mã nguồn. Pre giữ khoảng trắng và xuống dòng. Với một khối mã nhiều dòng, có thể kết hợp hai phần tử này. Cite dùng cho tên tác phẩm, không phải mọi tên tác giả.",
    )),
    ("Liên kết và điều hướng", (
        "Một liên kết dùng phần tử a với thuộc tính href để chỉ đích đến. Văn bản liên kết nên mô tả rõ nơi sẽ tới, thay vì chỉ ghi bấm vào đây.",
        "Đường dẫn tương đối phụ thuộc vào địa chỉ cơ sở của tài liệu. Liên kết đến vị trí trong trang dùng dấu thăng và mã định danh của phần tử đích.",
        "Với tab mới, noopener tách quyền truy cập cửa sổ mở; noreferrer còn bỏ thông tin nguồn giới thiệu. Hãy kiểm tra điều hướng bằng bàn phím và giữ trạng thái tiêu điểm dễ thấy.",
        "Bài tập cuối: tạo trang giới thiệu sự kiện với cấu trúc đầy đủ, tiêu đề đúng cấp, một đoạn mô tả và liên kết đăng ký. Dùng nút cho hành động, liên kết cho điều hướng.",
    )),
)
TEST_TEXTS = (
    "Một trang giới thiệu câu lạc bộ cần có tiêu đề rõ ràng và đường dẫn đăng ký dễ nhận biết.",
    "Văn bản có dấu cần được lưu đúng bộ mã để người đọc không gặp ký tự bị lỗi.",
    "Hãy giải thích vì sao việc phóng to chữ không tự biến một đoạn văn thành tiêu đề có ngữ nghĩa.",
    "Sau khi sửa liên kết, bạn hãy thử bằng bàn phím và kiểm tra đích đến trong trình duyệt.",
)


def validate_splits(rows: list[dict]) -> None:
    """Reject missing splits, duplicate ids/text, or unknown split labels."""
    ids, texts, splits = set(), set(), set()
    for row in rows:
        text = " ".join(row["text"].casefold().split())
        if not text or row["id"] in ids or text in texts:
            raise ValueError("Empty text, duplicate id, or duplicate text across splits")
        if row["split"] not in {"train", "eval", "test"}:
            raise ValueError("Unknown split")
        ids.add(row["id"])
        texts.add(text)
        splits.add(row["split"])
    if splits != {"train", "eval", "test"}:
        raise ValueError("Separate train/eval/test splits are required")