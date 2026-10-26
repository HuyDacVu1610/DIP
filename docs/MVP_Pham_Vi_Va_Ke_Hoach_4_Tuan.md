# Document Scanner — Phạm vi MVP và kế hoạch 4 tuần

Ngày cập nhật: 17/10/2026.

## 1. Bối cảnh và mục tiêu

- Đề tài giữa kỳ môn Xử lý ảnh số, trọng số khoảng 20%.
- Thời hạn còn khoảng một tháng; ngày nộp chính xác chưa được xác định.
- Làm theo nhóm, người dùng dự kiến đảm nhiệm phần lớn triển khai.
- Giảng viên cho phép dùng OpenCV; đánh giá nhấn mạnh thuật toán và độ am hiểu.
- Người dùng đã chấp nhận phạm vi MVP ngày 09/10/2026, gồm quản lý bộ tài liệu và lưu/mở lại. Tài liệu này ghi phạm vi và kiến trúc đã chốt, chưa xác nhận chức năng đã hoàn thành.

Mục tiêu: ảnh chụp tài liệu → vùng cắt được xác nhận → trang hiệu chỉnh → ảnh/PDF, kèm bằng chứng và giải thích các bước xử lý thật.

Hai tài liệu phiên bản 1.0 tại thư mục gốc được giữ làm bản tham chiếu. Khi thực hiện MVP, dùng phạm vi trong tài liệu này để lập checklist thay cho việc làm đủ 331 tác vụ.

## 2. Phạm vi cần hoàn thành

| Nhóm | Chức năng và tiêu chí |
|---|---|
| Nhập ảnh | JPEG/PNG; EXIF đúng; alpha ghép nền trắng; lỗi tệp riêng; giữ nguồn |
| Phát hiện | Xám → Gaussian →3trial Canny/closing→contour; nếu khôngquad thêm1mask Otsu vùng sáng/contour ngoài → cùng xấp xỉ/geometry/scoring; trả đề xuất hoặc yêu cầu chọn tay khi task tương ứng hoàn thành |
| Chỉnh góc | Bốn handle; dùng toàn ảnh; kiểm tra trùng, tự giao, lõm và suy biến; xác nhận trước xử lý |
| Hiệu chỉnh | Homography, warp từ nguồn chuẩn hóa; kích thước ước lượng, giới hạn cạnh dài 2400; xoay 90° |
| Cải thiện | Màu; xám với CLAHE có thể tắt; BW với Otsu hoặc Adaptive Gaussian; lọc None/Median/Gaussian |
| Quan sát | Trước/sau; phóng to kết quả để kiểm tra chữ; ảnh xám, Gaussian, Canny, closing, contour overlay, warp và kết quả từ phép chạy thật |
| Giải thích | Tham số thực dùng, histogram trước threshold, ngưỡng Otsu khi áp dụng, thời gian từng bước |
| Bộ tài liệu | Đặt tên bộ tài liệu; thêm, chọn, xóa, sắp xếp trang; xử lý lần lượt |
| Lưu và mở lại | Giữ nguồn, cấu hình hiện hành, thứ tự và kết quả; mở lại sau khi khởi động lại backend |
| Xuất | PNG/JPG và PDF nhiều trang; đúng thứ tự, hướng và tỉ lệ; lấy từ full render |

Ảnh trung gian và histogram được ưu tiên như phần cần có của bản nộp vì phục vụ trực tiếp tiêu chí chấm thuật toán.

Giữ giới hạn đầu vào theo đặc tả: 15 MiB/tệp, 16 triệu pixel giải mã, 20 trang/phiên. Không xuất trang có vùng cắt chưa xác nhận hoặc kết quả không khớp cấu hình hiện hành.

## 3. Những phần hoãn để giảm khối lượng

- OCR, tìm kiếm văn bản, AI/deep learning, tài khoản, cloud.
- Camera trực tiếp, hỗ trợ điện thoại/LAN, zoom/pan/kính lúp nâng cao.
- Sharpening, cảnh báo mờ, deskew và tỉ lệ A4 cho vùng warp. PDF vẫn có thể đặt ảnh lên trang A4 theo kiểu fit, giữ tỉ lệ.
- Làm đều sáng/giảm bóng là mở rộng ưu tiên sau khi luồng chính ổn định; chưa phải điều kiện hoàn thành MVP.
- Preset tùy biến, ZIP, drag-and-drop sắp xếp, giao diện trang trí phức tạp.
- Lịch sử sửa đầy đủ, cache bền và dọn rác nâng cao. Vẫn cần xử lý tệp tạm và tệp mới khi thao tác thất bại.

Điều chỉnh sau trao đổi: giữ lưu bền và reopen theo FR-13 của đặc tả gốc; không áp dụng đề xuất phiên chỉ tồn tại trong bộ nhớ của bản rút gọn trước.

## 4. Kiến trúc đã chốt

- Ứng dụng web chạy cục bộ, kiến trúc đơn khối chia mô-đun. Frontend React + TypeScript + Vite; backend Python 3.11/3.12 + FastAPI; xử lý ảnh OpenCV headless + NumPy + Pillow; SQLite + SQLAlchemy cho metadata; ReportLab cho PDF. Khóa phiên bản dependency sau khi môi trường chạy thành công.
- Lõi normalize/detection/geometry/enhancement độc lập HTTP, chạy được bằng script trước khi nối UI.
- SQLite lưu bộ tài liệu, trang, cấu hình hiện hành, revision và metadata artifact/export. Ảnh nguồn, nguồn chuẩn hóa, kết quả, ảnh trung gian và PDF lưu trên đĩa; DB giữ tham chiếu và đường dẫn nội bộ, không chứa blob ảnh. Không giữ ndarray của mọi trang trong RAM.
- API kiểm tra request và quan hệ tài liệu/trang; service điều phối; processing chỉ xử lý ndarray/config; storage quản lý DB/tệp; export bố trí ảnh/PDF.
- Một tác vụ ảnh active, tối đa hai chờ; một tiến trình backend. UI upload/render lần lượt; tác vụ CPU nằm ngoài event loop.
- Giữ revision cho cấu hình và kiểm tra trước khi nhận/ghi kết quả. Frontend tách cấu hình đang sửa với cấu hình đã xác nhận.
- Export chụp danh sách trang/revision/thứ tự và giữ các artifact đang được dùng. MVP tạm khóa sửa/xóa/thay thứ tự của bộ tài liệu đang xuất, kiểm tra cả backend và UI; giải phóng khóa khi hoàn tất hoặc thất bại. Khởi động lại phải mở lại được tài liệu mà không giữ khóa cũ.
- Chỉ phục vụ tệp qua artifact ID; không public thư mục runtime. Ghi tệp tạm rồi đổi tên khi hoàn tất.
- DB ghi metadata trong transaction ngắn; không giữ transaction trong lúc chạy OpenCV/PDF. Nếu commit thất bại, dọn tệp mới chưa được tham chiếu và giữ nguồn/config đã lưu.
- Chưa triển khai cache; mỗi render tính lại. Điều này giảm độ phức tạp và giúp ảnh trung gian khớp phép chạy.
- Phát triển: Vite proxy /api đến FastAPI. Bản demo: build React, FastAPI phục vụ giao diện và /api/v1 cùng origin, bind localhost. Ảnh được xử lý trên máy chạy backend.

Luồng thành phần: React → HTTP/FastAPI → service → processing/storage/export. Storage gồm SQLite và tệp trên đĩa. Thuật toán nằm ở backend; frontend đảm nhiệm tương tác và hiển thị.

Giao diện gồm danh sách tài liệu, màn hình chỉnh sửa và phần xuất ảnh/PDF. Tab các bước xử lý phục vụ giải thích môn học.

## 5. Thuật toán cần hiểu để bảo vệ

| Nội dung | Cần giải thích được |
|---|---|
| Xám và lọc | BGR/RGB; Gaussian làm mượt; Median phù hợp chấm nhiễu; tác động đến nét và dấu nhỏ |
| Canny | Gradient, non-maximum suppression, hai ngưỡng, hysteresis; tác động của ngưỡng |
| Closing | Dilation rồi erosion trên edge trắng; nối hở và nguy cơ nối nhầm |
| Contour | Chu vi, diện tích, Douglas–Peucker, epsilon; điều kiện tứ giác và hạn chế nền phức tạp |
| Mô tả biên | Chu vi/cạnh/số đỉnh/góc/độ lồi là mô tả hình học; contour/Q là biểu diễn; diện tích là đặc trưng vùng bổ sung; dùng để lọc/xếp hạng và giải thích |
| Scoring | Thành phần diện tích, hỗ trợ biên, khớp contour, phạt viền; score là heuristic, không phải accuracy |
| Homography | Tài liệu phẳng, bốn cặp điểm, 8 bậc tự do; thứ tự góc; nội suy; giới hạn tỉ lệ ước lượng |
| CLAHE | Histogram cục bộ, clip limit; lợi ích và khả năng khuếch đại nhiễu |
| Otsu | Histogram, phương sai giữa hai lớp; ngưỡng toàn cục; hạn chế khi có bóng |
| Adaptive | Ngưỡng cục bộ Gaussian; block size và C; mất màu/highlight khi nhị phân hóa |

Không cần tự viết lại toàn bộ OpenCV. Nếu phần chính đã ổn định, có thể tự viết histogram và Otsu trên ảnh nhỏ, đối chiếu OpenCV để minh họa mức độ hiểu; phần này không chặn MVP.

Phần mô tả biên được thực hiện trong MVP05.03–MVP05.04, lưu debug ở MVP05.07, hiển thị/giải thích ở MVP09.07–MVP09.08 và đánh giá ở MVP13.04. Cách tính, đơn vị, trường debug và nghiệm thu cụ thể ở [phân tích thuật toán, mục 5.5.1–5.5.3](Phan_Tich_Huong_Thuat_Toan_Tu_Tai_Lieu.md). Giữ baseline scoring a/e/f/b; sai số khoảng cách contour–đa giác hoặc descriptor nâng cao là thí nghiệm bổ sung khi có bằng chứng, không bắt buộc thêm vào MVP.

Điều chỉnh user chấp nhận15/10/2026, đã triển khai AUX05.01: giữGaussian5 và3Canny revised20/60,50/150,75/200; khi khôngquad mới thử1Otsu vùng sáng. Baseline cũ còn để so. Mask/actualt và raw Canny support tách biệt; giữ gate10%/5%, closing3, geometry vàscore, không thêm ML/Hough/dewarp. Cócandidate chưa đồng nghĩa đúngtrang: anhtestnew được khôi phục mép, img_004/img_006 còn ăn bàn. [Revision01](detection-revision-01.md) ghi quyết định/kiểm chứng và ảnh hưởng các task kế tiếp; phạm vi quản lýtrang/lưubền/PDF không đổi.

## 6. Thực nghiệm vừa sức

- User chốt bộ hiện có26/10/2026 là đủ MVP:13ảnh/2tài liệu, thay mục tiêu20/5 ngày18/10 và40/10 ban đầu. Báo điều kiện thật, không bù ảnh tổng hợp hoặc tuyên bố đủ phủ nhàu rõ/glare/highlight.
- Chia theo tài liệu vật lý/nội dung:6ảnh/doc_01 development và7ảnh/doc_02 test. User xác nhận các ảnh trong mỗi nhóm cùng tờ/nội dung. Một tài liệu mỗi split/cùng bối cảnh là giới hạn phải nêu; số đo13 và phạm vi kết luận ởdocs/report.md.
- Chọn tham số trên development; khóa cấu hình trước khi chạy test. Nêu rõ đây là tập nhỏ và không có tập validation riêng.
- Gán bốn góc trên nguồn đã chuẩn hóa. Mẫu thiếu góc/lóa/mờ được ghi nhận, không âm thầm loại.
- Detection: tỉ lệ đề xuất, IoU, lỗi góc và các ca thất bại; không có đề xuất tính thất bại tự nhận diện.
- So sánh có kiểm soát: có/không Gaussian; có/không closing; largest contour/scoring; Otsu/Adaptive trên cùng vùng cắt.
- Render: quan sát dấu tiếng Việt, nét mảnh, nền và mất highlight; không gọi histogram hay entropy là độ chính xác chữ.
- Đo thời gian core và đầu-cuối trên máy thực tế; ghi CPU/RAM, độ phân giải và số lượt. Nếu báo p95, nêu số mẫu để tránh kết luận quá mức.
- Các mục tiêu 80% IoU ≥ 0.90, detect p95 ≤ 2 giây, render p95 ≤ 3 giây vẫn chỉ là mục tiêu tham chiếu; báo kết quả thật và giới hạn.

Quy mô dữ liệu này rút gọn kế hoạch 80 ảnh/ba tập trong đặc tả gốc để phù hợp đề tài giữa kỳ.

## 7. Kế hoạch theo bốn tuần tương đối

| Tuần | Công việc | Cổng hoàn thành |
|---|---|---|
| 1 | Khung môi trường; fixtures; normalize; góc/warp; ba mode; detect; thu ảnh development | Script một ảnh → detect hoặc góc tay → warp → ba mode → ảnh và tham số |
| 2 | SQLite/artifact; API bộ tài liệu, upload/config/detect/render; UI chọn ảnh, kéo góc, trước/sau; revision | Quét một trang từ UI với ảnh thật; dữ liệu được lưu; lỗi hình học và response cũ được xử lý |
| 3 | Nhiều trang; đặt tên và reopen; xuất ảnh/PDF; ảnh trung gian; histogram; kiểm thử luồng chính | Demo đầu-cuối ba trang; mở lại sau restart; đúng thứ tự/hướng; truy vết được các bước thật |
| 4 | Khóa tham số; chạy test và so sánh; sửa lỗi; build; hướng dẫn; báo cáo và luyện bảo vệ | Cài/chạy lại được; có bảng số liệu, ảnh thất bại và demo 5–7 phút |

Thu dữ liệu và ghi giải thích thuật toán ngay từ tuần 1. Không dành toàn bộ tuần cuối mới viết báo cáo.

## 8. Điều kiện hoàn thành bản nộp

- Luồng nhập → xác nhận góc → warp → mode → xuất hoạt động, kể cả khi detect thất bại và phải chỉnh tay.
- EXIF/alpha, bốn góc bốn màu, bow-tie/suy biến, canvas mapping, revision và PDF ba trang được kiểm chứng.
- Sau restart, mở lại được bộ tài liệu với tên, nguồn, cấu hình, thứ tự và kết quả đã lưu; phần xem phóng to giúp kiểm tra chữ.
- Ảnh trung gian, histogram và timing đến từ xử lý thật.
- Có so sánh thuật toán, tham số đã khóa và kết quả test; không dùng số minh họa làm số đo.
- Báo cáo nêu phần dùng thư viện, phần tự viết, giới hạn và lý do rút gọn phạm vi.
- Có README, dependency đã khóa, ảnh demo và kịch bản bảo vệ.

Chỉ đánh dấu hoàn thành khi có mã chạy và bằng chứng tương ứng. Tài liệu này hiện là kế hoạch, không xác nhận tiến độ triển khai.

## 9. Checklist triển khai chi tiết

Phạm vi trên đã được chia thành **14 giai đoạn, 110 task chính và 5 task tùy chọn** ngày 10/10/2026.

- [Kế hoạch thứ tự, mốc, rủi ro và tiêu chuẩn hoàn thành](../tasks/plan.md).
- [Checklist task với nghiệm thu, kiểm chứng, phụ thuộc và tệp dự kiến](../tasks/todo.md).

Tiến độ26/10/2026:110ID chính/109active/1skip/5optional,12AUX. MVP01.01–07, 02–11 và 13–14 xong: **102 task chính, 13 AUX**; MVP01.08 bỏ qua. M4 kỹ thuật đạt26/10/2026: bản chạy cùngorigin localhost8000, sourceZIP/manifest/checksum, cài sạch đúnglock/1.279backend-experiments+103frontendtests/typecheck/build, README/hướng dẫn/báo cáo sốliệu thật vàdemo5–7phút đãkiểm. RehearsalUI sau nhập5phút21giây, PDF3trang/restart65artifact đạt; chưa có lượt tập nói hoặc thủ tục nộp hành chính. Đã rà đủ8task14/AUX14.01; giữlõiảnh/preset/lock/manifest/nhãn/frozen13, chỉ sửa một dòng chú thích dataset trênUI. Giai đoạn12 còn7task chưa nghiệmthu và5optional chưa làm; không tựtích theo cổng hồi quy trước khóa. Giữ ca sai development và giới hạn mỗi split một tài liệu. [Bằng chứng](progress.md), [API](api-contract.md).


## Điều chỉnh thao tác nhập —18/10/2026

Theo yêu cầu người dùng, ảnh nhập mới (một hoặc nhiều tệp) tự chạy nhận diện lần lượt. Người dùng duyệt proposal/chỉnh tay/xác nhận từng trang; không tự confirmed/render/export. Lỗi nhận diện giữ trang đã nhập và không chặn tệp sau, không tự upload lại. Không áp tự động lên trang cũ hoặc thay nháp/góc đã lưu. Thuật toán và phạm vi xử lý ảnh không đổi. [Chi tiết](auto-detect-on-import.md).
