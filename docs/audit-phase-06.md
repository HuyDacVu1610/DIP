# Rà soát sáu task giai đoạn06 — AUX06.01

Ngày:16/10/2026. User yêu cầu hoàn thành task5–6 rồi rà cả6task như các giai đoạn trước. Nguồn: [checklist](../tasks/todo.md), [kế hoạch](../tasks/plan.md), [MVP](MVP_Pham_Vi_Va_Ke_Hoach_4_Tuan.md), [hợp đồng ảnh](image-contract.md), [hướng thuật toán](Phan_Tich_Huong_Thuat_Toan_Tu_Tai_Lieu.md), [M1/lệnh chạy lại](milestone-m1.md).

## Kết luận

**Cả6task đạt tiêu chí triển khai MVP; checkpoint06-C1 và cổng06/M1 đạt.** Có một lệnh offline từ ảnh gốc đến source/quad/warp/ba mode/rotation/full-preview/config/stages/histogram; manual_required không tạo trang giả và chạy lại bằng góc tay được. Tái lập đã kiểm trên cùng máy và dependencies hiện tại. Không phát hiện lỗi implementation mới chặn nghiệm thu; lượt này chỉ thêm kiểm thử và tài liệu, không đổi detector/render hoặc preset.

M1 chưa chứng nhận một hệ thống scan qua UI hoặc chất lượng xử lý mọi ảnh. **img_004 vẫn ăn bàn**, img_001 cần góc tay; các đầu ra được lặp lại chính xác có thể vẫn sai về nội dung vùng quét. Nợ phân vùng/xấp xỉ/score ở [audit05](audit-phase-05.md) giữ nguyên. Development6ảnh/1doc_01/test0 không đủ đánh giá tổng quát.

## Ma trận sáu task

| Task | Tiêu chí / mã và bằng chứng kiểm tra lại | Kết luận |
|---|---|---|
| 06.01 pipeline | scan_one normalize → render_document detect hoặc manual → source warp → enhance/rotate. Runtime anhtestnew auto tạo201×285; img_001 auto2lượt manual_required,3mode tay tạo full. Tests kiểm low-score diagnostic không warp, source40000×42, quota/config/confirmed, fullsource không dùng analysis | Đạt |
| 06.02 full/preview | encode_render_images RGB/L/hash/cleanEXIF; preview thu từ chính full sau rotation, max1000/no upscale/INTER_AREA. Mở lại230PNG; checkerboard full1300×2000→preview650×1000, preview cógray; các rotation/dimensions/byte-count/hash được đối chiếu | Đạt |
| 06.03 snapshot/stages | effective/requestedconfig, source raw/PNG/BGRhash, H, version/environment/timing. Detection/render tách thư mục, cùngrun_id/source, không rerun để dựng debug. QA8detection/28trial rawCanny/closing/region, sourcewarp/filter/gray/threshold/rotate và ảnh kết quả | Đạt |
| 06.04 histogram | BW counts256 từ actual prepared_gray sau lọc/CLAHE, trước threshold/rotate; sum=N và hash PNG/size. Otsu global/actualt (img_004=140); Adaptive local/t=null. Gray/Color/failure=null. Test readonly/stride/255/5.76MP và QA NumPy trên savedPNG | Đạt |
| 06.05 tái lập | 4core tests serialize/reparse config rồi render mới, đủColor/Gray/Otsu/Adaptive và90/180/270;2CLI tests auto/failure tách process. Runtime10ca×2tiếntrình cùng requestedconfig/source/version, so toànmetadata/PNG/stages/config/H/histogram trừ run_id/timings; không nhầm replaycorners với rerundetect | Đạt trong môi trường hiện tại |
| 06.06 mốc M1 | milestone-m1.md có lệnh chạy không cần ảnh cá nhân và bảng ảnh thật tốt/xấu/fallback, môi trường và giới hạn. Đã chạy nguyên blockPowerShell trong tài liệu:3mode EXIFfixture, replayBW, blankfailure→manualretry; kiểm config/full/preview/grayhash và giữsource. Fullsuite800đạt | Đạt |

Task03a/b vẫn là con của03. AUX06.01 là task phụ rà giai đoạn, không tăng6task chính của giai đoạn hoặc đổi110ID gốc.

## Bằng chứng và phạm vi so sánh

- Backend **800passed99.97s** =794trước+4core reproducibility+2CLI reproducibility; focused45passed30.73s. Không skip hoặc nới validation.
- `experiments/results/mvp06-m1-verified/verification.json`:10cặp/20runs,230PNG,18render/2manual_required,8detection/28trials.4ảnh thật độc nhất (img_001/003/004 vàanhtestnew),1fixtureEXIF và1checkerboard; các ảnh thật không phải4tài liệu độc lập.
- Version scan-v1; Python3.12.10/OpenCV4.14.0/NumPy2.5.4/Pillow12.3.0, Windows11build26300. Verification lưu hash code processing/CLI/writer/requirements và ảnh nguồn; code/dependency giữ nguyên trong lượt này.
- Mỗi cặp dùng **cùng config đầu vào**: corners=null sẽ chạy detector cả hai lần; cornersmanual sẽ bỏ detector cả hai lần. Đã so cả metadata root và detection, chỉ loại hai trường run_id/timings_ms có tính từnglượt. Config đầu ra cógóc chạy lại theo đường manual là cách dùng hợp lệ khác, không chứng minh detector đã chạy lại.
- QA mở/đọc ảnh kiểm hash/bytes/mode/dimensions/EXIF; replay các stage từ source/config/rawtrials và kiểm threshold/rotation/preview, không chỉ so hai bộ hash giống nhau. Timing hữu hạn/không âm/tổng đúng và detect đã chứa timing con, không cộnglặp.
- Nguồn6cặp manifest và22fixtures giữ hash, ảnh nguồn không bị ghi đè. Ảnh thật/results/.tmp ignored, không gửi ảnh ra ngoài. Các run đều confirmed=false.

Đã xem overlay trang trắng thuận lợi; full-preview Colormanual img_001, Gray có bóng img_003, Otsu ăn bàn img_004, Adaptive90 giữ ôly/nhiễu img_001. Ảnh thu nhỏ dùng kiểm bố cục; không suy ra bảo toàn từng nét/dấu từ preview. Tests/fullPNG và stage/hash là chứng cứ pixel riêng.

## Đối chiếu thuật toán và giới hạn còn mở

Lõi giữ các quy ước đã chốt: BGR sauEXIF, normalizedW−1/H−1, topology trênpixel/khôngsort handlemanual; detector dùnganalysis còn warp lấyfullsource. Gaussian/Median trước mode; CLAHE trêngray; Otsu mộtngưỡng từhistogram, Adaptive dùngGaussian cục bộ−C; histogram chỉ biểu diễn phân bố sáng/tối. Homography nắn phối cảnh từquad, khônglà dewarping giấy cong/nhàu. Các ngưỡng hình học/score là baseline dự án, không gán cho giáo trình.

Đối chiếu phần lý thuyết qua hướngthuậttoán và [lượt kiểm PDF trước](verification-img004-theory.md); không đọc lại toàn3PDF trong audit này. Douglas–Peucker không phảiMPP; threshold+contour không phải region-growing cóseed. Otsu102ở detector analysis và140ở fullrender img_004 là hai phép tính khácstage/tiềnxửlý, khôngmâu thuẫn.

Không thấy lý do đổi thuật toán chỉ để qua tiêu chí06. Để xử lý nợ05 sau này vẫn cần đối chứng development độc lập: capepsilon/fitdistance, cạnhthiếusupport, phân biệt giấy/nền sáng; các gatehìnhhọc này không giải quyết khunggiả cócạnh mạnh/fit tốt. Khôngtune từ1tờgiấy, khôngcoi repeatability là accuracy. Giữ chọn/xácnhận tay khi nốiUI, không bỏ gateconfirmed/revision vìCLIđãrendered.

## Bàn giao sang giai đoạn07

44task chính+6AUX đã hoàn thành; MVP01.08 vẫn bỏ qua. M1 chỉ là lõi offline và bằng chứng. Bước kế tiếp07.01 schemaAPI; service/storage/UI mộttrang ở07, confirmed/revision ở08, histogramUI ở09, nhiều trang/PDF ở10–11. Không tích các task sau từ việc core đã cóPNG/config.
