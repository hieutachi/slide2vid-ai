# Đánh giá sẵn sàng phát hành / triển khai SlideVoice

Ngày kiểm tra: **2026-10-15**. Phạm vi: checkout Windows hiện tại; kết quả CI/Linux
không được suy diễn từ việc có file workflow. Phiên bản package giữ `0.1.0`, thay
đổi nằm ở nhánh làm việc **Unreleased**, chưa tag/publish.

## Kết luận

**GO có điều kiện cho thử nghiệm nội bộ bằng CLI/batch, với dữ liệu tin cậy và
người vận hành. NO-GO cho SaaS public / đa tenant / tuyên bố chất lượng giảng dạy
production.** Đã nâng nền tảng đóng gói và vận hành, không huấn luyện một mô hình
TTS/LLM mới và không có bằng chứng model tự cải thiện chỉ từ tăng token.

## Đã đạt trước đợt hardening

- Kiến trúc core nhẹ, plugin, worker GPU tách môi trường; cache stage/câu có hash,
  resume, kiểm tra artifact và gate đồng ý sử dụng giọng.
- Đường bài giảng: schema kịch bản, trích dẫn nguồn slide/notes, target hình học,
  hiệu ứng highlight/circle/zoom, storyboard và player có chương/beat/phím tắt.
- Demo thực tế trên đĩa: 24 slide / 48 beat, 304.067 giây, 1920×1080; caption
  83 cue, tối đa 2 dòng × 42 ký tự, cue ngắn nhất 2.244 giây. Đây là demo kịch bản
  viết tay và số liệu minh họa, không phải đánh giá LLM-provider độc lập.
- Đọc lại được log lịch sử: **134 passed, 1 skipped**. Validation AV/browser cũ
  có trên đĩa; không diễn giải chúng thành bằng chứng nghe bằng tai hoặc test
  điện thoại vật lý. Caption timing vẫn ước lượng trong câu, không align từng từ.

## Đã triển khai thêm trong đợt này

| Hạng mục | Thay đổi | Giới hạn còn lại |
| --- | --- | --- |
| Ghi trạng thái job | Khóa OS một writer/job; tự giải phóng khi process chết; reload state trong lock | Local filesystem; không phải distributed queue/NFS; tiến trình khởi tạo và chạy là hai lần acquire lock riêng |
| Checkpoint | Temp file riêng, flush/fsync, replace; retry ngắn hữu hạn cho tranh chấp Windows | Không có giao dịch nhiều file hoặc bảo đảm power-loss toàn bộ job |
| Telemetry | `run_status.json`: running/paused/completed/failed/interrupted, stage, UTC, loại lỗi | Không heartbeat; kill cứng có thể để trạng thái running |
| Input/resource | Giới hạn kích thước file, ZIP/member/slide/ratio, dimensions/FPS; chặn macro/OLE/ActiveX | Không antivirus/sandbox, không quota tổng output; config và filesystem vẫn phải tin cậy |
| Chẩn đoán | `doctor`, JSON, mã thoát; codec/filter và plugin prerequisite | Không chứng nhận bảo mật/chất lượng; healthcheck PowerPoint chưa thử COM thực tế |
| Wheel smoke | Fixture offline thuộc package; video/caption/report và resume | Âm tổng hợp, không phải tiếng nói hay CER thực |
| Linux renderer | LibreOffice → PDF → PNG; profile riêng, hidden-slide mapping, letterbox, không fake fallback | Unit test mock đạt; real executable chưa có ở máy này; CI/visual parity chưa chạy |
| Open source | LICENSE MIT, third-party notice, security/contribution/changelog | Cần chủ repo xác nhận quyền và audit dependency/model/media theo bản release |
| Deploy assets | Container batch non-root, resource restrictions; CI Windows/Linux/Python/wheel/container | Chưa thực thi Docker/Linux tại máy; không GPU image/API public |

## Bằng chứng kiểm tra cục bộ

Nguồn log: `D:\SOFT\STV\out\release_hardening\verified`.

- **159 passed, 2 skipped**, 54.19 giây, Python 3.11.15/Windows; JUnit `tests.xml`.
  Hai skip: chưa có LibreOffice thật; Windows không cho tạo symlink trong test.
- Ruff check, Ruff format, mypy **40 file nguồn**, `doctor`: exit 0.
- Kiểm thử mới bao gồm lock ở process khác/crash release, checkpoint concurrent
  và failure preservation, interruption/status, ZIP/resource policy, doctor JSON
  và sanitize lỗi, hợp đồng renderer, installed-package smoke/cache.
- Lần chạy đầu phát hiện trùng tên module test unit/integration và đã sửa tên;
  log thất bại cũ được giữ riêng trong `final`, không dùng làm kết quả đạt.
- Build wheel/sdist bằng backend cache offline **đã đạt**; cài vào virtualenv sạch
  rồi chạy ngoài checkout: import từ `site-packages`, doctor, smoke, resume đều
  exit 0, **9/9 stage cache hit**. Kiểm tra nội dung wheel và sdist đều đạt;
  `packaging_summary.json` lưu riêng trong thư mục `release_hardening`. Không cần
  cài `build` vào core; `uv build --offline` sử dụng build isolation/cache sẵn có.
- Kiểm lại SHA256 của **552 artifact** theo manifest demo v4: **không mismatch**.
  Video v4: `46cec064b74ca848c35aa1744135405c7bd6bb5b8afdf06b906b4121397e4dd9`.
  Không rebuild demo v2/v3/v4; các hash video được ghi trong `demo_integrity.json`.

Kết quả chạy cuối sau thay đổi packaging được lưu ở `final_verified`. Nếu khác
với bản ghi trên, dùng log/exit code/JUnit của vòng cuối làm nguồn sự thật.

Wheel/sdist nằm trong `D:\SOFT\STV\out\release_hardening\dist`. Chỉ là artifact
kiểm chứng cục bộ, chưa đăng PyPI/GitHub và chưa có chứng thực supply-chain.

## Gate trước khi gắn tag mã nguồn mở

1. Repo hiện **chưa có commit**, source đều untracked. Chủ repo cần review secret,
   quyền nội dung, diff/inventory rồi mới commit và đặt remote. Không tự publish.
2. Chạy CI matrix thực sự; Linux phải thực thi test LibreOffice thật, wheel ở
   ngoài checkout và container read-only/offline/non-root. Không chấp nhận skip
   renderer ở Linux release runner.
3. Kiểm tra source distribution có test/config/tài liệu và wheel không chứa
   source input, weight, secret, virtualenv. Audit lỗ hổng/license; tạo SBOM và
   dependency lock/image digest cho đúng release (chưa có release lock hiện tại).
4. Cấu hình kênh báo cáo lỗ hổng riêng tư, người duy trì, release notes, version
   policy và quy trình rollback. Workflow không tự publish package.

## Gate trước khi chạy khóa học thật

1. Bộ deck đại diện: font Việt, bảng/chart, 4:3/16:9/portrait, slide ẩn/notes trống,
   nhiều trang. Review ảnh và nội dung với LibreOffice lẫn PowerPoint khi cần.
2. Nghe toàn bộ video 1×, kiểm phát âm/số/đơn vị/tên riêng và sự nhấn ý; giảng viên
   duyệt storyboard, độ đúng kiến thức và nguồn trích dẫn. Dùng điện thoại thật.
3. ASR/forced alignment độc lập và bộ đánh giá held-out có quyền sử dụng. Tách
   CER thật khỏi sidecar giả; đo word/segment timing và readability theo corpus.
4. Chạy soak/recovery, giới hạn đĩa/GPU, backup-restore, process kill và service
   restart trên chính máy deploy. Xác định ngân sách latency và concurrency.

## Lộ trình tiếp tục nâng cấp theo gate, không theo số token

### P0 — Release engineering (đã có nền tảng, còn gate môi trường)

Hoàn thành CI thực, wheel install sạch, real Linux renderer/container, license
audit/SBOM/lock. Chấp nhận: mọi lane release pass có artifact, cài không cần
checkout, startup fail có hướng dẫn, resume không đổi artifact hợp lệ.

### P1 — Chất lượng ngôn ngữ và đánh giá mô hình

- Xây corpus có consent và provenance; tách train/dev/held-out theo người nói và
  chủ đề. Bao phủ số thập phân, phần trăm, công thức, từ mượn/tên riêng.
- Hoàn thiện normalizer tiếng Việt thay fixture, pronunciation dictionary có
  override theo môn học; test text gốc/spoken text và khả năng truy vết.
- Tích hợp ASR/align worker độc lập (không dùng transcript sidecar làm bằng chứng
  chất lượng); xuất metric có backend/model/revision/dataset rõ ràng.
- So sánh TTS bằng nghe mù, intelligibility, CER/WER độc lập, lỗi số/đơn vị và
  latency/VRAM/real-time factor. Không tự đặt điểm MOS hoặc ngưỡng chất lượng
  trước khi có baseline và human labels.

Chấp nhận: metric tái lập trên held-out, xử lý regression theo từng nhóm lỗi;
fine-tune chỉ khi có dữ liệu/giấy phép và chứng minh tốt hơn baseline.

### P2 — Bài giảng đúng và dễ học

Đánh giá factual grounding của từng beat, mục tiêu/takeaway, lỗi hallucination,
thời lượng, nhấn vùng/chart và accessibility. Review ở script stage trước khi
chi GPU/API. Benchmark provider bằng cùng bộ deck và schema, báo cáo cả lỗi,
chi phí và variance; không dùng demo viết tay để xếp hạng provider.

### P3 — Dịch vụ có kiểm soát

Chỉ sau P0/P1: API có auth/tenant isolation, idempotency, admission/queue hữu hạn,
worker identity, cancel/timeouts, quota GPU/đĩa, storage lifecycle, metrics/log
redaction, retry/backpressure, disaster recovery. Không công khai worker local
hay HTTP sample server như shortcut. Dữ liệu tenant phải được sandbox thực sự.

Ưu tiên hoàn thành gate nhỏ có bằng chứng; 200 triệu token là ngân sách dự kiến
của người dùng, không phải bằng chứng chất lượng hoặc cam kết agent chạy nền
vô hạn. Không có chi phí provider/model download/deploy public được tự phát sinh.