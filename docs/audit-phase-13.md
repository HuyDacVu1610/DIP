# Rà soát giai đoạn 13 — 8 task

Ngày 26/10/2026. **13.01–13.08 và cổng 13 đạt theo phạm vi MVP đã được user chấp nhận: 13 ảnh/2 tài liệu.**
Đây không phải chứng nhận accuracy tổng quát; các giới hạn và ca sai giữ trong báo cáo.

| Task | Tiêu chí/bằng chứng đối chiếu | Kết quả và giới hạn |
|---|---|---|
| 13.01 | Manifest 6 development/doc_01 + 7 test/doc_02; duplicate không đếm; user xác nhận nhóm và chốt đủ | Đạt. Một tài liệu mỗi split, thiếu phủ nhàu/lóa/highlight thật |
| 13.02 | 13 record nguồn PNG sau EXIF/hash/dims; 10 quad/3 unlabelable; reviewed 13/13 | Đạt. Nhãn thủ công một người, không lấy output detector làm GT |
| 13.03 | Core polygon IoU + 8 ghép góc, source-pixel error/chia đường chéo; thiếu proposal IoU 0 | Đạt. Mẫu số GT và sai số góc được báo rõ, unlabelable không bịa góc |
| 13.04 | 6 development×4 profile = 24 lượt, CSV/stages/descriptors; chỉ đổi một yếu tố | Đạt. Có ca ăn bàn img_004, không thay score theo test |
| 13.05 | 3 GT/cùng warp, chỉ đổi threshold.method; gray/histogram bằng nhau, full đã xem | Đạt. 3 unlabelable giữ lý do; highlight tổng hợp riêng, không thay ảnh thật |
| 13.06 | frozen-v1/SHA, 91 source files, preset/score/version/dependencies/environment; regression gate | Đạt. User chọn cổng hồi quy cần thiết; không tự tích giai đoạn 12 |
| 13.07 | 7 test sau khóa, 168 samples/140 đo/28 warmup, core và HTTP thật, PSAPI PID server | Đạt. Lỗi PID phép đo đầu được tái hiện/sửa, giữ lượt đầu và dùng trọn lượt final; không tune thuật toán |
| 13.08 | Bảng development/test riêng, ca sai/thiếu phủ, ảnh/CSV/mẫu số, giới hạn homography | Đạt. Không lấy 7/7 ảnh cùng tài liệu làm accuracy mọi tài liệu |

## Kiểm chứng cuối

- Test metrics/selection/provenance và toàn bộ hồi quy: 1.261 backend/experiments tests đạt 173,10 s, không skip; gồm 1.219 backend + 42 experiments.
- Test runner dùng fixture, không dùng ảnh test thật để phát triển logic: percentiles loại warmup/giữ lỗi, native working set, hash/dim drift, frozen gate trước pixel, HTTP cô lập/fresh runs/full bằng core, PID khớp log Uvicorn.
- Mã benchmark mới tách khỏi 91 tệp đã khóa. Frozen SHA/config/versions/dependencies/environment khớp trước/sau; manifest/annotations và 13 nguồn nguyên. Không đổi label, threshold, score hoặc chọn ảnh sau khi nhìn test.
- Replay 70 PNG detection/hash/dimensions, gray/Gaussian/Canny/closing, score và metrics; 7 cặp full HTTP/core bằng byte. 84 run ID HTTP khác nhau; server shutdown gracefully. Đã xem contact sheet đủ 7 overlay và riêng img_009.
- Mean test IoU 0,995347, sai số góc 2,303 px, 7/7 IoU≥0,90; 6 proposed/1 warning. Mỗi đường benchmark có 35 lượt đo/0 lỗi. RAM HTTP final khoảng 156 MiB của server thật; số ~4,7 MiB launcher ở lượt đầu bị đánh dấu không hợp lệ.
- Frontend103/typecheck/build giữ bằng chứng 13.06; không rerun vì frontend/core/API/dependencies không sửa. Benchmark server/database mới cô lập, không chạy test vào DB app người dùng.

## Giới hạn và nợ thuật toán còn giữ

Development chỉ 3 GT từ giấy ô ly; test 7 ảnh của cùng tài liệu in, khác giấy nhưng cùng bối cảnh bàn. Một người gán nhãn và độ chính xác vài pixel của mốc tham chiếu giới hạn ý nghĩa con số. Test đã được quan sát từ lượt đầu; đo lại sau sửa PID không tạo test độc lập mới. Không tune hoặc sửa bản khóa để cải thiện số test.

Giữ nợ detector img_004/006 chọn bàn/thiếu vùng và khung giả có score cao. Gate fit-distance/epsilon/cạnh yếu chỉ là hướng thử; chưa triển khai hay lựa ngưỡng từ test. Homography không dewarp giấy nhàu hoặc khôi phục chữ bị che/cháy sáng. Chưa có kết luận từ ảnh thật về nhàu mạnh/lóa/highlight; ví dụ synthetic ghi đúng nguồn gốc.

Benchmark tuần tự một máy, warmup và cache kết quả app tắt, OS cache/allocator còn giữ. RAM lấy mẫu 10 ms là working set theo tiến trình, không exact peak mỗi lời gọi; p95 mô tả 35 lượt/đường, không SLA dân số hoặc thử tải đồng thời. Không gọi chênh lệch hai lượt đo là tối ưu thuật toán.

## Bàn giao

94 task chính + 12 AUX/110 ID gốc; MVP01.08 giữ bỏ qua. Checkpoint 13-C1/C2 và cổng 13 đạt; next 14.01. Các task/cổng 12 vẫn chưa nghiệm thu toàn bộ theo quyết định thu hẹp cổng hồi quy ở 13.06. Không bắt đầu 14, không tự commit/push/deploy hoặc gửi ảnh ra ngoài.

Nguồn: [kết quả](results.md), [phương pháp đo](benchmark-method.md), [bản khóa/môi trường](experiment-environment.md), [dataset](dataset.md), [checklist](../tasks/todo.md), [progress](progress.md). Evidence ignored `experiments/results/mvp13-07-08-verified/`: `final/` là bản chính, `test/` là lượt đầu có lỗi RAM HTTP, verification/pytest/logs/review-sheet giữ riêng.
