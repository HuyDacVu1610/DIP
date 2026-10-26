# Tự nhận diện vùng sau nhập ảnh — AUX11.02

Ngày 18/10/2026, theo yêu cầu của người dùng: khi nhập một hoặc nhiều ảnh, app tự nhận diện vùng cho từng trang để người dùng duyệt và chỉnh lại.

## Hành vi

Batch chạy tuần tự: nhập ảnh → nhận diện ảnh vừa nhập → hiện trang và kết quả → sang tệp tiếp theo. Giao diện phân biệt “Đang nhập” với “Đã lưu · đang nhận diện vùng”; kết quả từng tệp ghi đã đề xuất, có cảnh báo, cần chỉnh tay hoặc nhận diện lỗi. Cách chạy này dùng cùng giới hạn executor hiện có, không gửi đồng loạt nhiều tác vụ CPU.

Ảnh nhập hỏng báo lỗi riêng và không chặn các tệp sau. Nếu nhập đã thành công nhưng nhận diện lỗi/429/mất phản hồi, trang vẫn được giữ, vẫn tiêu thụ đúng một chỗ trong quota20. Không tự gửi lại upload/detect. Người dùng mở trang để chỉnh tay hoặc bấm “Tự nhận diện vùng” thử lại.

Trang được đưa vào danh sách sau khi lượt nhận diện hoàn tất hoặc báo lỗi. Trang đang chọn và nháp của trang cũ được giữ khi append. Có nhãn “Đã nhận diện · chờ kiểm tra”, “Vùng có cảnh báo” hoặc “Cần chỉnh vùng tay” trên các trang mới.

Khi mở một trang còn nguyên trạng thái nhập mới — revision0, corners=null, confirmed=false — app dùng latest_detection đúng nguồn/revision để khởi tạo góc nháp. Proposal được kiểm page/source/dimensions/status/score/quad; manual_required dùng khung thử5% và thông báo chỉnh tay. Góc đề xuất không ghi vào PageConfig hoặc tự xác nhận. Duyệt/reload chỉ GET lại dữ liệu đã có, không nhận diện thêm lần nữa.

Góc đã lưu, cấu hình revision>0 và nháp của editor đang mở không bị thay bằng proposal cũ. Người dùng vẫn phải kiểm tra mép giấy, chỉnh góc nếu cần và xác nhận rõ ràng trước render/export. Chức năng tự động áp dụng cho các ảnh nhập mới; không chạy hàng loạt trên tài liệu cũ.

## Triển khai

- importDetection.ts nối upload→detect bằng các API hiện hữu; detectionProposal.ts dùng chung gate với nút nhận diện tay và bước mở trang mới.
- uploadBatch/UploadPanel có trạng thái nhận diện và thông báo kết quả, giữ khóa batch đến GET đối soát cuối. Lỗi detect không bị tính thành upload thất bại.
- ScannerPage append trang sau lượt nhận diện; pageRenderState chỉ nạp proposal một lần cho trang mới chưa lưu góc; PageList có nhãn chờ kiểm tra.
- Không đổi backend/API/schema/thuật toán/threshold/scoring. Upload API vẫn chỉ nhập ảnh; sự tự động nằm ở orchestration frontend. DetectionRun/debug được lưu bằng endpoint detect hiện hữu.

## Kiểm chứng

TDD trước triển khai: module importDetection chưa tồn tại và test mở trang mới vẫn nhận khung5% thay proposal. Sau triển khai, **102 frontend tests** đạt298.4506ms; typecheck/build đạt,41modules178ms, JS299.66kB/gzip92.54. Bảy tests mới kiểm thứ tự và khóa qua detection, quota khi detect lỗi, tiếp tục batch, upload lỗi không detect, binding sai, mở proposal/manual fallback, giữ góc đã lưu và nháp đã chỉnh. Các tests manual detection/revision/export trước đó vẫn đạt.

Backend không sửa. Chạy hồi quy test_import_api/test_detection_api/test_reopen với -W error: **36 passed/11.13s**. Mốc full1199tests của nghiệm thu M3 là bằng chứng trước lượt này, không gọi là đã chạy lại full suite.

Browser thật trên tài liệu QA riêng có một trang Color đã render, sau đó đổi nháp thành Gray chưa lưu. Chọn cùng lúc paper.png, broken.jpg, blank.png:

1. paper nhập thành công và tự có proposal, score0.7820204972;
2. broken trả415, không tạo trang/detection;
3. blank nhập thành công và tự có manual_required.

Kết quả ba trang tổng cộng, hai POST detect/hai DetectionRuns đúng hai trang mới. Nháp Gray và bản quét Color cũ giữ nguyên. Duyệt hai trang mới/reload không thêm POST detect; mọi trang mới vẫn revision0/corners persisted=null/confirmed=false và chưa render. Góc handle trên UI khớp proposal, chênh lệch biểu diễn normalized tối đa1.11e−16 (so với dung sai kiểm chứng1e−12); ảnh trắng dùng đúng khung5%. Console sạch,320/768 không tràn và viewport đã reset.

Evidence ignored tại experiments/results/auto-detect-import-verified/: seed/document/browser-checks/verification/product-before-after/product-verification, ảnh tổng hợp và product-view. Giữ nguyên17tài liệu/58trang/174hash nguồn cùng mọi row có trước; core/CLI/requirementsM1/schema3/12path15method không đổi. Chưa gửi ảnh/DB ra ngoài, không commit/push/deploy.

Đây là cải thiện thao tác nhập, không làm detector chính xác hơn. Giới hạn img_004/006 có thể ăn bàn vẫn giữ; proposal luôn cần người dùng kiểm tra. [Hợp đồng ảnh](image-contract.md), [API](api-contract.md), [checklist](../tasks/todo.md).

## Sửa lỗi callback trên tab đã mở — 18/10/2026

Người dùng gặp `onDetecting is not a function` sau khi ảnh đã được lưu nhưng trước POST detect. Bộ chạy nhập cũ gọi `onUpload(file)` với một tham số; khi giữ hàm này trong useState, Fast Refresh có thể giữ implementation cũ trong tab đang mở. Helper mới lại yêu cầu callback tiến độ nên ném lỗi sau upload thành công. Kiểm thử gọi theo giao diện cũ tái hiện đúng TypeError này trước bản sửa.

Callback tiến độ của importWithDetection giờ có giá trị mặc định; thiếu callback vẫn tiếp tục nhận diện đúng trang đã nhập. UploadPanel giữ bộ chạy qua useMemo với dependency factory để khóa batch bền qua render bình thường và cập nhật implementation khi hot reload. Không tự gửi lại ảnh đã lưu.

Sau sửa: **103 frontend tests**, typecheck/build đạt (41 modules,203ms). Browser trên tài liệu QA riêng nhập một paper.png → một trang/một DetectionRun, UI báo đã đề xuất vùng; revision0, góc lưu null, confirmed=false và chưa render. Console không warning/error. Bằng chứng ignored ở experiments/results/callback-upload-fix-verified/ gồm browser-checks/product-view, snapshot và kiểm tra bảo toàn: 18 tài liệu/59 trang/177 hash nguồn cũ cùng mọi hàng SQLite giữ nguyên. Backend/thuật toán/schema/API không đổi; không chạy lại bộ backend cho bản sửa frontend này.

Ảnh đã nhập trong lượt lỗi không cần tải lại: mở đúng trang và bấm “Tự nhận diện vùng” để bổ sung lượt nhận diện bị ngắt. Không tự sửa nháp đang mở của người dùng khi phục hồi.
