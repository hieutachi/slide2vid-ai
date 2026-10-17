"""Hand-authored, synthetic teaching material. Not a real-provider LLM evaluation."""

# title, visible lines, spoken sentences, optional illustrative data
LESSONS = [
    (
        "Đọc hiểu dữ liệu",
        ["Từ con số đến câu hỏi đúng", "24 slide • Ví dụ giả định • Giọng AI"],
        [
            "Bài thử này hướng dẫn cách đọc dữ liệu, từ câu hỏi ban đầu đến một kết luận có giới hạn.",
            "Chúng ta dùng các ví dụ giả định, không phải số liệu khảo sát hay bằng chứng nghiên cứu thực tế.",
        ],
        [],
    ),
    (
        "Bắt đầu bằng câu hỏi",
        [
            "Ta muốn biết điều gì?",
            "Đơn vị quan sát là ai hoặc cái gì?",
            "Đo trong khoảng thời gian nào?",
        ],
        [
            "Trước khi tính toán, hãy xác định mình đang muốn biết điều gì và đang quan sát đối tượng nào.",
            "Chẳng hạn, thời gian đi học của sinh viên trong một tuần là một câu hỏi cụ thể hơn câu hỏi chung về giao thông.",
        ],
        [],
    ),
    (
        "Một bảng dữ liệu nhỏ",
        [
            "Mỗi hàng: một lượt quan sát",
            "Mỗi cột: một đặc điểm được đo",
            "Đơn vị và nguồn phải được ghi rõ",
        ],
        [
            "Hãy hình dung mỗi hàng trong bảng là một lượt đi học, còn mỗi cột ghi thời gian, quãng đường hoặc phương tiện.",
            "Nếu không ghi rõ đơn vị phút hay giờ, cùng một con số có thể bị diễn giải rất khác nhau.",
        ],
        [12, 18, 24, 30, 36],
    ),
    (
        "Biến định tính và định lượng",
        [
            "Định tính: nhóm hoặc nhãn",
            "Định lượng: giá trị có ý nghĩa đo lường",
            "Mã số không tự trở thành đại lượng",
        ],
        [
            "Phương tiện đi học là một biến định tính, còn số phút di chuyển là một biến định lượng.",
            "Mã sinh viên tuy được viết bằng chữ số, nhưng lấy trung bình các mã đó không tạo ra một đại lượng có ý nghĩa.",
        ],
        [],
    ),
    (
        "Kiểm tra trước khi phân tích",
        [
            "Thiếu dữ liệu? Trùng dòng?",
            "Có nhầm đơn vị hoặc nhập sai?",
            "Giữ lại dấu vết các bước xử lý",
        ],
        [
            "Một bảng dữ liệu cần được kiểm tra giá trị thiếu, dòng trùng và các lỗi nhập liệu trước khi phân tích.",
            "Không nên âm thầm xóa giá trị khác thường; hãy ghi lại lý do xử lý để người khác có thể kiểm tra.",
        ],
        [],
    ),
    (
        "Nhìn phân bố trước con số",
        [
            "Các giá trị tập trung ở đâu?",
            "Độ trải rộng lớn hay nhỏ?",
            "Có điểm nào khác biệt rõ rệt?",
        ],
        [
            "Một giá trị trung tâm không kể hết câu chuyện, vì các nhóm có cùng trung bình vẫn có thể khác nhau rất nhiều.",
            "Biểu đồ bên phải chỉ là minh họa; hãy chú ý cả vị trí tập trung lẫn khoảng cách giữa các giá trị.",
        ],
        [2, 3, 4, 5, 6],
    ),
    (
        "Trung bình cộng",
        ["Dữ liệu: 2, 3, 4, 5, 6", "Tổng = 20; số quan sát = 5", "Trung bình = 20 / 5 = 4"],
        [
            "Với năm giá trị hai, ba, bốn, năm, sáu, tổng bằng hai mươi.",
            "Chia tổng cho năm quan sát, ta được trung bình bằng bốn; mọi giá trị đều tham gia vào phép tính này.",
        ],
        [2, 3, 4, 5, 6],
    ),
    (
        "Trung vị với số phần tử lẻ",
        ["Sắp xếp: 2, 3, 4, 5, 6", "Chọn giá trị đứng giữa", "Trung vị = 4"],
        [
            "Để tìm trung vị, trước hết sắp xếp các giá trị theo thứ tự tăng dần.",
            "Trong dãy năm phần tử này, vị trí thứ ba nằm giữa, nên trung vị bằng bốn.",
        ],
        [2, 3, 4, 5, 6],
    ),
    (
        "Trung vị với số phần tử chẵn",
        ["Sắp xếp: 2, 3, 5, 8", "Hai giá trị giữa: 3 và 5", "Trung vị = (3 + 5) / 2 = 4"],
        [
            "Khi số phần tử là số chẵn, không có một quan sát duy nhất nằm giữa dãy.",
            "Với dãy hai, ba, năm, tám, lấy trung bình của ba và năm, ta được trung vị bằng bốn.",
        ],
        [2, 3, 5, 8],
    ),
    (
        "Khi một giá trị thay đổi",
        ["Dữ liệu mới: 2, 3, 4, 5, 100", "Trung bình = 114 / 5 = 22,8", "Trung vị vẫn bằng 4"],
        [
            "Bây giờ thay số sáu bằng một trăm, còn bốn giá trị khác giữ nguyên.",
            "Trung bình tăng lên hai mươi hai phẩy tám, nhưng trung vị vẫn bằng bốn vì vị trí giữa không thay đổi.",
        ],
        [2, 3, 4, 5, 100],
    ),
    (
        "Không vội xóa điểm ngoại lệ",
        [
            "Có thể là lỗi nhập liệu",
            "Cũng có thể là quan sát hợp lệ",
            "Kiểm tra nguồn và bối cảnh trước",
        ],
        [
            "Một điểm khác biệt có thể là lỗi nhập liệu, nhưng cũng có thể là hiện tượng thật cần được tìm hiểu.",
            "Vì vậy, hãy kiểm tra nguồn dữ liệu và bối cảnh trước khi quyết định loại bỏ hoặc giữ lại điểm đó.",
        ],
        [],
    ),
    (
        "Chọn thước đo theo câu hỏi",
        [
            "Trung bình: dùng mọi giá trị",
            "Trung vị: dựa vào vị trí đã sắp xếp",
            "Không có lựa chọn luôn tốt nhất",
        ],
        [
            "Trung bình và trung vị trả lời những cách hiểu khác nhau về vị trí trung tâm.",
            "Hãy chọn thước đo phù hợp với mục đích phân tích, thay vì kết luận rằng một đại lượng luôn tốt hơn đại lượng kia.",
        ],
        [],
    ),
    (
        "Tự kiểm tra: đổi thành 1.000",
        ["Dãy: 2, 3, 4, 5, 1.000", "Trung bình thay đổi thế nào?", "Trung vị có thay đổi không?"],
        [
            "Hãy thử thay một trăm bằng một nghìn, rồi tự tính lại trung bình và trung vị.",
            "Bạn có thể dừng video ở đây để suy nghĩ, hoặc chọn lặp nhịp nếu muốn nghe lại câu hỏi.",
        ],
        [2, 3, 4, 5, 1000],
    ),
    (
        "Lời giải và cách giải thích",
        [
            "Tổng mới = 1.014",
            "Trung bình = 1.014 / 5 = 202,8",
            "Trung vị = 4, vì vị trí giữa giữ nguyên",
        ],
        [
            "Tổng mới bằng một nghìn không trăm mười bốn, nên trung bình bằng hai trăm linh hai phẩy tám.",
            "Trung vị vẫn bằng bốn; điều quan trọng là giải thích được kết quả từ cách tính, không chỉ nhớ đáp số.",
        ],
        [],
    ),
    (
        "Cùng trung bình, khác độ trải",
        ["Nhóm A: 4, 4, 4, 4, 4", "Nhóm B: 0, 2, 4, 6, 8", "Cả hai có trung bình bằng 4"],
        [
            "Nhóm A gồm năm số bốn, còn nhóm B gồm không, hai, bốn, sáu, tám.",
            "Hai nhóm đều có trung bình bằng bốn, nhưng nhóm B trải rộng hơn; chỉ báo cáo trung bình sẽ bỏ qua khác biệt này.",
        ],
        [0, 2, 4, 6, 8],
    ),
    (
        "Khoảng biến thiên",
        ["Khoảng biến thiên = lớn nhất - nhỏ nhất", "Nhóm A: 4 - 4 = 0", "Nhóm B: 8 - 0 = 8"],
        [
            "Khoảng biến thiên được tính bằng giá trị lớn nhất trừ giá trị nhỏ nhất.",
            "Đây là cách mô tả độ trải rộng đơn giản, nhưng chỉ dựa vào hai điểm biên nên nhạy với các giá trị cực đoan.",
        ],
        [],
    ),
    (
        "Phân bố lệch và bối cảnh",
        [
            "Quan sát hình dạng phân bố",
            "Đọc trung tâm cùng độ phân tán",
            "Không suy quy luật từ một ví dụ",
        ],
        [
            "Nếu một số ít giá trị lớn kéo dài về một phía, hãy xem kỹ hình dạng phân bố thay vì chỉ nhìn trung bình.",
            "Ví dụ nhỏ trong bài giúp hiểu cách tính, nhưng không đủ để suy ra quy luật của một dân số thực tế.",
        ],
        [2, 3, 4, 5, 22],
    ),
    (
        "Biểu đồ cột: so sánh nhóm",
        [
            "Cột biểu diễn một đại lượng theo nhóm",
            "Ghi tên nhóm và đơn vị",
            "Đọc cả trục và giá trị gốc",
        ],
        [
            "Biểu đồ cột thường được dùng để so sánh một đại lượng giữa các nhóm.",
            "Trong hình minh họa, mỗi cột có giá trị ghi trực tiếp; trước khi so sánh, vẫn cần kiểm tra đơn vị và cách định nghĩa nhóm.",
        ],
        [12, 18, 24, 30, 36],
    ),
    (
        "Trục có thể đổi cảm nhận",
        [
            "Độ dài cột cần mốc gốc phù hợp",
            "Trục bị cắt có thể phóng đại chênh lệch",
            "Đọc nhãn, không chỉ nhìn hình",
        ],
        [
            "Nếu trục của biểu đồ cột bị cắt, một chênh lệch nhỏ có thể trông lớn hơn thực tế.",
            "Hãy đọc nhãn trục và số liệu gốc, rồi mới đánh giá mức chênh lệch có ý nghĩa trong bối cảnh hay không.",
        ],
        [40, 42, 43, 41, 44],
    ),
    (
        "Tương quan không phải nhân quả",
        [
            "Cùng thay đổi chưa đủ để nói gây ra",
            "Có thể tồn tại yếu tố gây nhiễu",
            "Cần thiết kế nghiên cứu phù hợp",
        ],
        [
            "Hai đại lượng cùng tăng không đủ để kết luận rằng đại lượng này gây ra đại lượng kia.",
            "Một yếu tố thứ ba có thể tác động đến cả hai; muốn kết luận nhân quả cần thêm lập luận và thiết kế nghiên cứu phù hợp.",
        ],
        [],
    ),
    (
        "Mẫu quan sát và tổng thể",
        ["Mẫu: phần được quan sát", "Tổng thể: nhóm muốn tìm hiểu", "Mẫu lớn chưa chắc đại diện"],
        [
            "Mẫu là phần dữ liệu thực sự được quan sát, còn tổng thể là nhóm mà ta muốn tìm hiểu.",
            "Một mẫu rất lớn vẫn có thể thiên lệch nếu cách chọn mẫu bỏ sót có hệ thống những nhóm quan trọng.",
        ],
        [],
    ),
    (
        "Thiếu dữ liệu cũng là thông tin",
        [
            "Ai hoặc điều gì đang bị thiếu?",
            "Thiếu ngẫu nhiên hay có hệ thống?",
            "Nêu rõ cách xử lý và giới hạn",
        ],
        [
            "Nếu những người đi xa ít trả lời khảo sát hơn, dữ liệu thời gian đi học có thể bị lệch.",
            "Do đó, hãy xem dữ liệu nào đang thiếu và công khai cách xử lý, thay vì coi mọi giá trị thiếu đều giống nhau.",
        ],
        [],
    ),
    (
        "Viết một kết luận có giới hạn",
        [
            "Nêu phát hiện gắn với câu hỏi",
            "Ghi thước đo, đơn vị và phạm vi",
            "Phân biệt mô tả với suy luận",
        ],
        [
            "Một kết luận tốt cần gắn với câu hỏi ban đầu, nêu rõ thước đo, đơn vị và phạm vi quan sát.",
            "Hãy phân biệt điều dữ liệu trực tiếp mô tả với điều ta đang suy luận, và nói rõ những giới hạn còn tồn tại.",
        ],
        [],
    ),
    (
        "Tóm tắt: năm bước đọc dữ liệu",
        ["Hỏi đúng → Kiểm tra dữ liệu", "Nhìn phân bố → Chọn thước đo", "Kết luận có giới hạn"],
        [
            "Hãy nhớ năm bước: đặt câu hỏi, kiểm tra dữ liệu, nhìn phân bố, chọn thước đo và kết luận có giới hạn.",
            "Khi test video, bạn hãy thử tìm kiếm một ý, chuyển slide, đổi tốc độ và kiểm tra xem phụ đề có còn dễ theo dõi hay không.",
        ],
        [],
    ),
]
