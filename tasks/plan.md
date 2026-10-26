# Kế hoạch triển khai Document Scanner MVP

Ngày lập:10/10/2026. Cập nhật:26/10/2026. MVP01.01–07, 02–11 và 13–14 xong: **102 task chính, 13 AUX**; MVP01.08 bỏ qua. M4 kỹ thuật đạt26/10/2026: bản chạy cùngorigin localhost8000, sourceZIP/manifest/checksum, cài sạch đúnglock/1.279backend-experiments+103frontendtests/typecheck/build, README/hướng dẫn/báo cáo sốliệu thật vàdemo5–7phút đãkiểm. RehearsalUI sau nhập5phút21giây, PDF3trang/restart65artifact đạt; chưa có lượt tập nói hoặc thủ tục nộp hành chính. Đã rà đủ8task14/AUX14.01; giữlõiảnh/preset/lock/manifest/nhãn/frozen13, chỉ sửa một dòng chú thích dataset trênUI. Giai đoạn12 còn7task chưa nghiệmthu và5optional chưa làm; không tựtích theo cổng hồi quy trước khóa. Giữ ca sai development và giới hạn mỗi split một tài liệu. [Bằng chứng](../docs/progress.md), [hợp đồng](../docs/image-contract.md), [API](../docs/api-contract.md).

## 1. Mục tiêu và nguồn yêu cầu

Hoàn thành bộ tài liệu từ ảnh chụp: nhập nhiều ảnh → đề xuất/sửa và xác nhận góc → warp → chọn mode/tham số → xem trước/sau → đặt tên/sắp xếp/lưu/mở lại → xuất ảnh/PDF. Có ảnh trung gian thật, histogram và thực nghiệm để bảo vệ môn Xử lý ảnh số.

Phạm vi và kiến trúc đã được người dùng chấp nhận tại [tài liệu MVP](../docs/MVP_Pham_Vi_Va_Ke_Hoach_4_Tuan.md). Kế hoạch này cụ thể hóa phạm vi đó; giữ hai tài liệu gốc làm tham chiếu, không dùng toàn bộ 331 task gốc để đánh giá hoàn thành MVP.

**Nơi theo dõi duy nhất:** [tasks/todo.md](todo.md), gồm **14 giai đoạn, 109 task chính cần thực hiện, 1 task bỏ qua và 5 task tùy chọn**. Giữ 110 ID gốc để truy vết. Các checkpoint không tính vào số task. Bảng dưới là mục lục, không phải checklist tiến độ thứ hai.

Task chính MVP01.05 có 2 task con a/b để chia scaffold 8 tệp thành các bước tối đa 5 tệp; không cộng task con lần nữa vào tổng task chính.

Có13AUX ngoài109task chính/5optional: AUX02.01,03.01,04.01;05.01–02;06.01;07.01;08.01;09.01;10.01;11.01–02 và14.01. AUX14.01 do user yêu cầu rà8task14 ngày26/10. Giữ110ID gốc; task con không cộng lại parent.

## 2. Giả định đã dùng

- Workspace hiện tại là gốc dự án; backend/frontend/experiments được tạo bên trong. Khi tiếp tục, đọc todo.md/progress.md và git status để giữ các thay đổi hiện có.
- Thời hạn khoảng một tháng, chưa có ngày nộp chính xác. Bốn tuần là phân bổ tương đối, không phải cam kết giờ làm.
- Người dùng cung cấp ảnh thật và xác nhận nhãn; có thể dùng fixtures tổng hợp để viết lõi trước khi đủ dataset.
- User chốt bộ hiện có26/10:13ảnh/2tài liệu (development6/doc_01,test7/doc_02), thay mục tiêu20/5 ngày18/10. Giữ split theo tài liệu, ghi giới hạn một tài liệu mỗi tập/cùng nền; không tune trên7ảnh test.13.01–08 đãđạt và giữ bảnkhóa lịch sử; giai đoạn12 chưa nghiệm thu toàn bộ.
- Phạm vi/tiến độ theo todo/progress. Đã xong7task khởi tạo, giai đoạn02–11,13.01–04 và12AUX; M1offline/M2quét tayUI đạt.07.07/08 và08.07/08 chia lát tối đa5tệp code, không tăngtask chính. Bộ13ảnh/2tài liệu được user chốt26/10 chỉ có một tài liệu mỗi split, chưa đủ kết luận khả năng tổng quát.

## 3. Quyết định kiến trúc và lý do

| Quyết định hiện hành | Lý do và ảnh hưởng |
|---|---|
| Web cục bộ, React/TypeScript/Vite + FastAPI | UI kéo góc thuận tiện; xử lý bằng Python/OpenCV; ảnh ở máy backend |
| Đơn khối chia mô-đun | Vừa quy mô đề tài; API/service/processing/storage/export có ranh giới rõ |
| Lõi độc lập HTTP/DB | Thử nghiệm thuật toán và kiểm chứng hình học trước khi ghép UI |
| SQLite/SQLAlchemy + tệp trên đĩa | Lưu/mở lại tài liệu; DB chỉ metadata, source/render/PDF thành tệp |
| Một worker ảnh, hai request chờ | Giữ mức dùng RAM/CPU có giới hạn; event loop vẫn phản hồi; đầy trả 429 |
| Full config + revision + draft riêng | Response cũ không ghi đè; thao tác chưa xác nhận không được xuất |
| Preview thu từ full render | Kết quả xem và xuất cùng phép xử lý |
| Snapshot và khóa mutation lúc export | Kết quả đúng page/revision/order; tránh thay/xóa nguồn snapshot giữa chừng |
| Mỗi render tính lại, không cache bền | Giảm logic cache/version; debug khớp phép chạy thật |
| Giảm bóng là tùy chọn, không dewarping/OCR | Giữ mục tiêu một tháng; homography chỉ phù hợp trang tương đối phẳng |

Các quyết định này được kế thừa từ tài liệu đã chốt. Người dùng bỏ task mẫu nhật ký MVP01.08 ngày 14/10/2026, nên không yêu cầu tạo docs/changes.md; quyết định này đã ghi trong docs/progress.md hiện có. Khi đổi phạm vi/kiến trúc, ghi lý do/ảnh hưởng tại tài liệu liên quan và hỏi người dùng khi thay đổi đáng kể chưa được chấp nhận.

## 4. Thứ tự và phụ thuộc

~~~mermaid
flowchart TD
    P1["01: môi trường"] --> P2["02: chuẩn hóa và dữ liệu"]
    P2 --> P3["03: hình học"]
    P3 --> P4["04: cải thiện ảnh"]
    P3 --> P5["05: detector"]
    P4 --> P6["06: pipeline offline"]
    P5 --> P6
    P6 --> P7["07: nhập và lưu một trang qua UI"]
    P7 --> P8["08: chỉnh góc và render qua UI"]
    P8 --> P9["09: detect, tham số, debug"]
    P9 --> P10["10: nhiều trang và reopen"]
    P10 --> P11["11: xuất ảnh/PDF"]
    P11 --> P12["12: củng cố tích hợp"]
    P6 --> DATA["Thu ảnh/gán nhãn tiếp tục trong tuần 1–3"]
    DATA --> P13["13: thực nghiệm đã khóa"]
    P12 --> P13
    P12 --> P14["14: đóng gói và báo cáo"]
    P13 --> P14
~~~

Mỗi task ghi phụ thuộc riêng trong todo.md. Task có thể làm sớm khi tất cả phụ thuộc đã đủ, ví dụ chuẩn bị dataset, ghi thuật toán và thử detector sau geometry. Không đợi hết UI để thu ảnh hoặc giải thích công thức.

Sau pipeline offline, ghép theo lát chức năng nhỏ: nhập/lưu/mở một trang; chỉnh góc/render một trang; detector/tham số/debug; quản lý nhiều trang; xuất. Không dựng toàn bộ DB/API/UI riêng rồi đợi cuối mới tích hợp.

## 5. Danh mục giai đoạn

| Giai đoạn | Nội dung | Task chính | Dải ID | Tuần |
|---|---|---:|---|---:|
| 01 | Khung dự án và môi trường | 7 | MVP01.01–MVP01.07; MVP01.08 bỏ qua | 1 |
| 02 | Chuẩn hóa ảnh và dữ liệu đầu vào | 8 | MVP02.01–MVP02.08 | 1 |
| 03 | Hình học và hiệu chỉnh phối cảnh | 8 | MVP03.01–MVP03.08 | 1 |
| 04 | Ba chế độ cải thiện ảnh | 7 | MVP04.01–MVP04.07 | 1 |
| 05 | Tự phát hiện vùng tài liệu | 8 | MVP05.01–MVP05.08 | 1 |
| 06 | Pipeline offline và dữ liệu minh họa | 6 | MVP06.01–MVP06.06 | 1 |
| 07 | Nhập một trang, lưu bền và mở lại qua UI | 9 | MVP07.01–MVP07.09 | 2 |
| 08 | Chỉnh góc và render một trang từ UI | 10 | MVP08.01–MVP08.10 | 2 |
| 09 | Tự nhận diện, tham số và giải thích trên UI | 8 | MVP09.01–MVP09.08 | 3 |
| 10 | Quản lý bộ tài liệu nhiều trang | 7 | MVP10.01–MVP10.07 | 3 |
| 11 | Xuất ảnh và PDF nhiều trang | 8 | MVP11.01–MVP11.08 | 3 |
| 12 | Củng cố các ca lỗi và luồng tích hợp | 7 | MVP12.01–MVP12.07 | 4 |
| 13 | Thực nghiệm và bằng chứng hiểu thuật toán | 8 | MVP13.01–MVP13.08 | 4 |
| 14 | Đóng gói, báo cáo và demo | 8 | MVP14.01–MVP14.08 | 4 |
| **Tổng cần thực hiện** | | **109** | | |

Tùy chọn: OPT-A.01–OPT-A.03 (làm đều sáng và đánh giá); OPT-B.01–OPT-B.02 (histogram/Otsu tự viết minh họa), tổng **5 task**. Không dùng task tùy chọn để bù cho thiếu task chính.

## 6. Mốc chạy được

| Mốc | Kết thúc | Bằng chứng |
|---|---|---|
| M0 | Giai đoạn 01 — đạt 14/10/2026 | Frontend gọi health; lệnh dev/test/build thực tế được ghi; MVP01.08 bỏ qua theo yêu cầu |
| M1 | Giai đoạn06 — đạt16/10/2026 | Script ảnh → detect/góc tay → warp → ba mode → full/preview/config/stages/histogram;10cặp tái lập và smoke6CLI |
| M2 | Giai đoạn08 — đạt17/10/2026 | UI nhập/chọn góc/xác nhận/quét/so sánh/zoom full; config/revision đúng. [Audit10task](../docs/audit-phase-08.md) |
| M3 | Giai đoạn11 — đạt18/10/2026 | Nhiều trang/tên/order/reopen/debug/xuấtảnh-PDF/khóa/lỗi/restart; [Audit8task](../docs/audit-phase-11.md) |
| M4 | Giai đoạn14 — đạt26/10/2026 | Clean run, bảng đo, báo cáo và demo 5–7 phút |

M2 của checklist MVP bao gồm UI một trang để có bằng chứng dùng được sớm; nó không phải số giai đoạn M2 của bản kế hoạch gốc.

Checkpoint sau mỗi nhóm tối đa ba task và cổng cuối giai đoạn được ghi trong todo.md. Checkpoint cần evidence theo phần đã triển khai; không tuyên bố test/build pass trước khi có môi trường và lệnh chạy.

## 7. Phân bổ bốn tuần

| Tuần | Trọng tâm | Task chính | Kết quả |
|---|---|---:|---|
| 1 | Giai đoạn 01–06, thu development và ghi công thức | 44 | M0, M1 |
| 2 | Giai đoạn 07–08; tiếp tục thu ảnh/gán nhãn | 19 | M2 |
| 3 | Giai đoạn 09–11; hoàn thiện dataset | 23 | M3 |
| 4 | Giai đoạn 12–14; khóa config và đo test | 23 | M4 |

Số task phản ánh mức chia việc, không quy đổi trực tiếp thành giờ. Sau M1 rà tốc độ thực tế; ưu tiên hoàn tất task chính và chừa thời gian xử lý lỗi, thực nghiệm, báo cáo. Bỏ phần tùy chọn trước khi cắt phạm vi đã chấp nhận.

## 8. Đối chiếu phạm vi với task

| Phạm vi MVP | Task thực hiện và kiểm chứng |
|---|---|
| JPEG/PNG, EXIF, alpha, quota và giữ nguồn | MVP02.01–MVP02.06; MVP07.05–MVP07.09; MVP12.01 |
| Đề xuất góc, score/cảnh báo và fallback | MVP05.01–MVP05.08; MVP09.01–MVP09.02 |
| Chỉnh/xác nhận góc và warp | MVP03.01–MVP03.08; MVP08.01–MVP08.10 |
| Ba mode, lọc, CLAHE, Otsu/Adaptive, xoay | MVP04.01–MVP04.07; MVP09.03–MVP09.04 |
| Trước/sau và phóng to xem chữ | MVP08.09–MVP08.10 |
| Ảnh trung gian thật, histogram, config và timing | MVP06.03–MVP06.05; MVP09.05–MVP09.08 |
| Tên tài liệu, nhiều trang, thêm/xóa/order | MVP07.08; MVP10.01–MVP10.07 |
| Lưu/mở lại sau restart | MVP07.02–MVP07.09; MVP10.07; MVP12.04–MVP12.05 |
| PNG/JPG/PDF đúng full render/revision/order | MVP11.01–MVP11.08; MVP12.02–MVP12.07 |
| Thực nghiệm, dữ liệu độc lập và giới hạn | MVP13.01–MVP13.08 |
| Bản chạy, hướng dẫn, báo cáo và bảo vệ | MVP14.01–MVP14.08 |

## 9. Tiêu chuẩn hoàn thành áp dụng cho checklist

1. Task đạt Xong khi và Kiểm chứng, có tệp/ảnh/request/CSV/lệnh thực tế làm bằng chứng.
2. Logic dễ sai có focused tests; UI có browser runtime; PDF được đọc/render để xem order/hướng/tỉ lệ. Không chỉ dựa vào build.
3. Mốc trước vẫn chạy được; test phù hợp và build/typecheck khi có thay đổi frontend không có hồi quy chưa xử lý.
4. Lỗi input/quad/revision/storage được giữ đúng lớp; không hạ quota/validation để có pass.
5. Docs phản ánh hành vi đã làm; báo cáo ghi thư viện/phần tự viết và số đo thật.
6. Dữ liệu cá nhân/DB runtime không vào Git hoặc gói nộp; không gửi ảnh ra dịch vụ ngoài.
7. Không tự merge/deploy/push hoặc gửi tin nhắn cho người khác. Checklist này không tạo thêm quyền cho các hành động đó.

Khi kết thúc một phiên, cập nhật docs/progress.md và checkbox đã đủ evidence; giữ working tree và task đang chặn cho phiên sau. Không tự commit chỉ vì đã tích một nhóm task.

## 10. Rủi ro và cách xử lý

| Rủi ro | Ảnh hưởng | Cách xử lý |
|---|---|---|
| Detector chọn sai nền/khung | Cắt mất nội dung | Giữ fallback tay, score có cảnh báo, luôn xác nhận trước render/xuất |
| Giấy nhàu/cong/lóa | Warp/threshold không sửa đủ | Thu ca thất bại; nêu giới hạn homography; hướng dẫn trải giấy/chụp lại |
| EXIF hoặc canvas mapping sai | Góc lệch toàn bộ | Fixtures EXIF/alpha, góc màu, portrait/landscape/HiDPI ngay từ đầu |
| Response cũ hoặc draft chưa lưu | Xuất sai nội dung | expected_revision, kiểm tra trước commit, page/revision match, nút xuất theo persisted config |
| Crash/DB commit lỗi | Mất kết quả hoặc tham chiếu hỏng | Source giữ nguyên, temp→rename, transaction ngắn, fault injection và restart tests |
| Snapshot export bị thay/xóa | PDF sai hoặc thiếu trang | Khóa mutation, giữ artifact, finally giải phóng, không persist khóa qua restart |
| Dataset tới quá muộn | Không đủ thí nghiệm báo cáo | Thu development tuần 1, bổ sung/gán nhãn xuyên tuần 2–3; ghi số thực tế |
| Rò rỉ tài liệu giữa hai tập | Số đo thiên lệch | Split theo document_id; chỉ chọn tham số development; khóa trước test |
| Task lớn hơn dự kiến | Khó kiểm chứng trong một phiên | Tách thành task con khi >5 tệp/>một phiên; giữ ID đã dùng và cập nhật danh mục |

## 11. Thông tin còn cần xác định khi phù hợp

- Ngày nộp chính xác: ảnh hưởng lịch cuối, không chặn việc chia checklist.
- Python/Node/CPU/RAM thực tế: xác định ở MVP01.03–MVP01.06; không tự bịa phiên bản hoặc tốc độ.
- Bộ ảnh người dùng cung cấp: bắt đầu MVP02.08; fixtures có thể làm trước.
- Định dạng báo cáo/gói nộp do giảng viên yêu cầu nếu có: làm rõ trước giai đoạn 14; hiện không có yêu cầu bắt buộc được biết.

## 12. Bước bắt đầu khi triển khai

MVP01.01–07, 02–11 và 13–14 xong: **102 task chính, 13 AUX**; MVP01.08 bỏ qua. M4 kỹ thuật đạt26/10/2026: bản chạy cùngorigin localhost8000, sourceZIP/manifest/checksum, cài sạch đúnglock/1.279backend-experiments+103frontendtests/typecheck/build, README/hướng dẫn/báo cáo sốliệu thật vàdemo5–7phút đãkiểm. RehearsalUI sau nhập5phút21giây, PDF3trang/restart65artifact đạt; chưa có lượt tập nói hoặc thủ tục nộp hành chính. Đã rà đủ8task14/AUX14.01; giữlõiảnh/preset/lock/manifest/nhãn/frozen13, chỉ sửa một dòng chú thích dataset trênUI. Giai đoạn12 còn7task chưa nghiệmthu và5optional chưa làm; không tựtích theo cổng hồi quy trước khóa. Giữ ca sai development và giới hạn mỗi split một tài liệu. [Audit10](../docs/audit-phase-10.md).

