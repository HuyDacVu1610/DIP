# Rà soát bảy task giai đoạn 04 — AUX04.01

Ngày: 14/10/2026. Người dùng yêu cầu làm MVP04.06–07 rồi rà đủ 7 task, tương tự giai đoạn 02–03.

## Kết luận nghiệm thu

**Cả 7 task đạt tiêu chí hiện hành.** Lõi config, preset, bộ lọc, Color/Gray/CLAHE, BW Otsu/Adaptive, dispatcher, xoay và CLI đã chạy. Toàn backend **571 passed in 52.53s**, gồm 193 config/enhancement, 7 enhancement CLI và 371 ca trước giai đoạn 04. Checkpoint 04-C1/04-C2 và cổng 04 đạt. Đã xem hai ảnh chụp development cùng tờ giấy và hai ảnh tổng hợp có dấu/highlight/nét nhỏ; ảnh nguồn và fixtures giữ nguyên.

Không tìm thấy lỗi implementation mới chặn nghiệm thu trong lượt rà này. Có hạn chế chất lượng phù hợp với lý thuyết: Otsu làm đen vùng bóng trên cả hai ảnh thật; CLAHE làm nổi nền; Adaptive vẫn giữ ô ly và làm đứt một số nét nhỏ. [Algorithm-notes](algorithm-notes.md) ghi từng ca. Đạt task chưa chứng minh mọi ảnh đều trắng sạch hoặc mọi dấu được giữ. Giữ preset khởi đầu, chưa tune và chưa tự viết lại OpenCV.

## Ma trận yêu cầu và bằng chứng

Nguồn: [todo](../tasks/todo.md), [MVP](MVP_Pham_Vi_Va_Ke_Hoach_4_Tuan.md), [image-contract](image-contract.md), đặc tả gốc mục 9.11–9.15. Giữ CLAHE trên gray, tỷ lệ estimated và cap 2400; Lab/sharpen/illumination/dewarp được hoãn theo MVP.

| Task | Tiêu chí | Code/tài liệu | Bằng chứng | Kết quả |
|---|---|---|---|---|
| 04.01 | Full preset/default/schema/strict/inactive; nguồn không đổi | config.py | 74 ca: enum/range/finite/extra/null, frozen, 24 hoán vị góc, source_size và Adaptive fit | Đạt |
| 04.02 | None/Median/Gaussian 3/5 trên full warp | apply_denoise | 26 ca: chấm/nét 1 pixel, padding/readonly/strided/shape; ảnh so 04.02; detection blur không làm nguồn render | Đạt |
| 04.03 | Color giữ màu; Gray bật/tắt CLAHE | render_color/render_gray | 32 ca: BGR weighting, clip 1/2/4, grid 8 tile, source copy, raw gray; ảnh tiếng Việt/highlight | Đạt |
| 04.04 | BW Otsu, polarity, ngưỡng thực cùng config | apply_otsu | 14 ca: histogram biết trước, ảnh hằng/t=0, replay t; sáng đều/bóng t=182/155; CLI ghi t cùng full config, ảnh thật t=147/172 | Đạt |
| 04.05 | Adaptive Gaussian, block/C/ảnh nhỏ | apply_adaptive_gaussian | 25 ca: Gaussian 3×3 khác mean, C −20..30, block 31/51/151, strict/fit; so 31/51 × C 5/10/20; lỗi 8×8/2×2, không fallback | Đạt |
| 04.06 | Đúng luồng, 3 mode × 4 rotation, giữ corners nguồn | enhance_document/EnhancementResult | 22 ca mới: config trước filter, inactive, thứ tự xử lý và actual t; 12 renders 95×63/63×95 khớp np.rot90, corners/source nguyên | Đạt |
| 04.07 | So 3 mode, ưu/nhược, dấu/nét/highlight, preset khởi đầu | enhancement_demo.py/algorithm-notes | 7 ca chạy CLI: EXIF/quad/rotation/hashes/RGB-L/không ghi đè/ảnh nhỏ; 5 runs gồm 2 ảnh development cùng doc, bản None và 2 synthetic; đã xem crop nguyên pixel | Đạt |

## Kiểm tra chéo trong lượt rà

- Core nhận full warp BGR sau EXIF/geometry; denoise → mode → contrast/threshold → rotate. Enhancement.py độc lập với detect/HTTP/DB/I/O/cache. Source/warp/config được giữ; đổi mode bắt đầu lại từ cùng warp.
- Revalidate toàn PageConfig trước CV; source_size thật bắt buộc nếu corners khác null; warp_size lấy dimensions trước xoay. Inactive vẫn kiểm kiểu/miền, không chạy contrast màu hoặc fit Adaptive ở Color/Gray/Otsu. Góc/confirmed được giữ; service sau này kiểm confirmed/revision.
- Rotation 0/90/180/270 theo chiều kim đồng hồ: 90/270 đổi W/H, không nội suy, không áp EXIF lại hoặc đổi corners. Kết quả uint8 độc lập/contiguous, BW chỉ 0/255. Otsu trả float thực; các nhánh khác trả null cho ngưỡng global.
- CLI chuẩn hóa input theo 15 MiB/16 MP một lần, dùng quad tay, giữ config draft. PNG mới không EXIF: Color RGB, Gray/BW L; metadata chứa hash/size/full config/inactive/threshold. Comparison thu từ full renders. Không ghi đè; nhánh không hợp lệ không tạo metadata/thư mục thành công.
- Rà code theo spec, tính dễ đọc và ranh giới module; reuse CV/Pydantic/dataclass, không dependency mới; strict và bounded 2400²/block 151. Frontend không đổi nên không lặp build/browser.

## Artifacts thực tế

| Thư mục experiments/results/ ignored | Warp W×H | Kiểm tra |
|---|---|---|
| mvp04-06-rotations | 95×63 trước xoay; 63×95 sau 90/270 | 12 full renders ba mode × bốn hướng; exact pixels/corners/source, đã xem contact |
| mvp04-07-shadow | 899×1288 | img_003, quad tay; 4 full renders/overlay/metadata, Otsu t=147; đã xem full text crop |
| mvp04-07-even | 1116×1228 | img_004, quad tay; 4 full renders, Otsu t=172, gradient bên phải; đã xem full text crop |
| mvp04-07-shadow-none | 899×1288 | Cùng img_003/quad; denoise None, Gray CLAHE off, Otsu t=147; đã xem full text crop |
| mvp04-07-vietnamese-highlight | 639×299 | Chữ có dấu/highlight tổng hợp; Color giữ vàng, BW mất màu; Otsu t=214 và nền đen |
| mvp04-07-thin-strokes | 259×179 | Aa123/nét nhỏ tổng hợp qua warp; Otsu t=209, đứt phần A |

Kiểm 40 PNG CLI bằng hash/size/mode và 12 PNG rotation bằng hash/shape: tổng 52 PNG có metadata. Comparison/crops bổ sung dùng xem, không đo accuracy. Sáu cặp raw/normalized development giữ hash CSV; cả 22 fixtures giữ hash/byte count manifest. Quad trên ảnh thật là góc chọn thử, chưa phải ground truth hoặc accuracy detector. Development vẫn 6 ảnh/1 doc_01, test 0; chỉ hai ảnh thật được so trong lượt này.

## Bàn giao

30 task chính và AUX02.01/AUX03.01/AUX04.01 hoàn thành; MVP01.08 vẫn bỏ qua. Giữ 110 ID gốc, 109 task cần làm và 5 optional; AUX nằm ngoài tổng chính. Checklist duy nhất là todo; progress giữ mốc test cũ và mốc hiện hành 571. Không commit/push/deploy hoặc gửi ảnh ra ngoài.

Tiếp theo MVP05.01: nguồn → resize 1200 → gray/Gaussian 5 để detect. Đây là nhánh khác với bộ lọc render đã làm. Debug/HTTP/UI/confirmed-revision/storage/nhiều trang/PDF và đánh giá cuối chờ các task tương ứng.
