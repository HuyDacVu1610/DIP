# Rà soát tám task giai đoạn 05 — AUX05.02

Ngày: 15/10/2026. Người dùng yêu cầu làm task 7–8, rà đủ tám task và nêu hướng giải quyết nợ kỹ thuật của task 3–4.

## Kết luận nghiệm thu

**Cả tám task đạt tiêu chí triển khai MVP hiện hành.** Detector offline đã có đề xuất/cảnh báo/manual_required, debug từ đúng lần chạy và CLI so baseline/revised. Checkpoint 05-C1/C2 và cổng 05 đạt ở mức chức năng và thực nghiệm ban đầu. Điều này không chứng nhận mọi ảnh khó đều được cảnh báo: khung giả tổng hợp vẫn được đề xuất điểm cao. Nợ thiết kế thuật toán này được giữ công khai bên dưới; không phát hiện lỗi implementation mới chặn tiêu chí task.

Toàn backend **733 passed in 47.01s**: 571 ca trước detection, 64 baseline detection, 30 revision, 18 polygon metrics, 28 selection, 10 debug, 5 compare CLI và 7 batch CLI. Không skip hoặc nới kiểm tra; số tests không phải accuracy. Giai đoạn này chưa nối HTTP/DB/UI/revision; đường xử lý tay được kiểm qua lõi warp/enhancement có sẵn.

Nguồn: [todo](../tasks/todo.md), [MVP](MVP_Pham_Vi_Va_Ke_Hoach_4_Tuan.md), [image-contract](image-contract.md), [hướng thuật toán](Phan_Tich_Huong_Thuat_Toan_Tu_Tai_Lieu.md) và [revision sinh ứng viên](detection-revision-01.md). Cơ sở lý thuyết lấy từ [lượt kiểm chứng ba PDF](verification-img004-theory.md); không đọc lại toàn bộ PDF ở lượt này. Douglas–Peucker không phải MPP; threshold rồi truy contour ngoài không phải region-growing có seed.

## Ma trận tám task

| Task | Tiêu chí và bằng chứng | Kết quả |
|---|---|---|
| 05.01 | prepare_analysis: max1200/không upscale/Gaussian5/dimensions thực; 20 tests nguồn dọc/ngang/nhỏ/subpixel/readonly; batch lưu analysis/gray/blur khớp pixel | Đạt |
| 05.02 | Ba Canny L2true hữu hạn, raw/closing riêng; 13 tests; revised20/60–50/150–75/200 và baseline tái hiện; QA tính lại raw/closing mọi trial | Đạt |
| 05.03 | Top30/epsilon hữu hạn, contour/Q/reason, geometry trước sorter; 15 tests lõm/tự giao/suy biến/diamond; region có điều kiện, không nới gate | Đạt, còn nợ phân vùng/xấp xỉ |
| 05.04 | Mô tả đúng đơn vị, raw support, e có trọng số, S truy vết; 16 tests với oracle khoảng cách/cạnh thiếu; tính lại 19 survivors từ raw và geometry đã lưu | Đạt, score chưa phân biệt đủ giấy/khung |
| 05.05 | NMS polygon IoU>.95, winner giữ provenance; 18 metrics và phần NMS trong 28 selection; nested/touch/skew/subpixel/strict .95/stable ties/không gộp dây chuyền | Đạt |
| 05.06 | Ngưỡng .60/.40, manual có corners=null, không tự confirmed; 28 selection gồm boundary/blank/open/region; 32 runs có status/corners/score/warnings nhất quán | Đạt |
| 05.07 | Timing, nguồn/tham số/trial/overlay/mô tả thực; 10 debug tests clock/hash/provenance/noquad/diagnostic/CV failure; QA replay 104 trial stages | Đạt |
| 05.08 | Development có ví dụ đúng/sai và fallback tay, không tune test; 7 CLI tests split/hash/EXIF/no-overwrite/lỗi riêng; xem đủ 16 comparisons; img_001 draft tay tạo được warp/render | Đạt |

AUX05.01 là revision sinh ứng viên đã nghiệm thu trước. AUX05.02 rà giai đoạn và ghi nợ thiết kế; không thêm ngưỡng hoặc thuật toán phân vùng mới.

## Timing và debug

Entry: detect_document(source_bgr, debug=False, preset='revised'). Baseline là lựa chọn explicit để đối chứng. Timing dùng perf_counter_ns với các khoảng liền nhau: preprocess; candidates (gộp Canny/closing/contours/Otsu); describe; select (gồm NMS); debug; total. Tổng khớp tổng các bước theo sai số số thực. Không gán thời gian nhóm candidates thành riêng Canny hoặc contour; không tính decode/encode/I/O trong core.

Mặc định không giữ ảnh stage trong result. Khi bật debug, trả analysis/trials thật, selected_trial đúng ID, hash bytes BGR C-order, preset/version và overlay đúng dimensions analysis. overlay_kind là proposal, diagnostic (best dưới .40 nhưng result.corners vẫn null), hoặc none (không quad, không vẽ giả). Metadata dataclass frozen; các ndarray không phải ảnh bất biến để caller sửa rồi dùng lại cùng provenance. Service sau này cần ghi/tách ảnh khỏi JSON metadata.

Hash BGR khác hash PNG. CLI ghi cả hai cùng raw hash, dimensions sau EXIF và source PNG đúng payload encode_normalized_png. Selected description giữ method/kernel/actual Otsu t/raw support origin; mask không được dùng làm edge_support. Đơn vị length/radian/normalized/ms được ghi rõ; mọi result và manual config đều confirmed=false.

## Thực nghiệm và lỗi còn giữ

Evidence: experiments/results/mvp05-07-08-verified/ (ignored). Có 6 ảnh development cùng doc_01, anhtestnew chưa biết identity/split và 9 synthetic: tổng 16 ca × 2 preset. case-index.json ánh xạ supplemental ID sang tên ca. Mỗi ảnh chạy baseline rồi revised; một lượt và thứ tự này không chứng minh preset nào nhanh hơn.

| Ca | Baseline | Revised | Quan sát |
|---|---|---|---|
| img_001 | manual | manual | Gấp góc/nền khó, không quad |
| img_002/003/005 | warning S=.525122/.502372/.501182 | Giữ quad/score tương ứng | Bám phần lớn mép giấy, mép hơi cong |
| img_004 | manual | warning S=.468352 | Vẫn ăn bàn, không ghi là nhận đúng |
| img_006 | manual | warning S=.448517 | Ăn bàn và có góc giấy gấp |
| anhtestnew | manual | proposed S=.634709 | Bám trang trắng trong ảnh nhỏ |
| rectangle/diamond | proposed | proposed | Tứ giác rõ, không ép vuông ở nguồn |
| frame_and_paper | proposed S=.975859 | proposed S=.975859 | **Sai: chọn khung ngoài thay giấy** |
| landscape texture | proposed S=.725465 | proposed S=.725465 | Bám trang trên nền họa tiết |
| concave/self_cross/degenerate/open_edge/constant | manual | manual | Giữ failure thật, không dựng quad giả |

Baseline có 9 manual/3 warning/4 proposed; revised có 6 manual/5 warning/5 proposed. Đây là đếm trạng thái, **không phải tỷ lệ đúng**: hai Otsu quad mới sai, frame sai. Chưa có GT/test độc lập; một tờ giấy không đủ kết luận tổng quát. Batch bỏ qua test trước đọc ảnh, đã kiểm bằng test path không tồn tại. Ảnh bổ sung không tự được thêm manifest hoặc gán nhãn vật lý.

QA .tmp/qa_phase05_evidence.py kiểm 32 profiles/104 trials/8 region/368 PNG/19 survivors. Đọc lại hash/bytes/dimensions/mode/EXIF; tính lại gray/Gaussian/Canny/closing/Otsu và descriptors từ raw đã lưu; geometry/NMS/status/score/provenance/timing khớp. Sáu cặp raw/normalized và 22 fixtures giữ hash. Core timing một lượt từ 2.072 đến 218.8952ms, chỉ là quan sát trên máy này, không phải benchmark/SLO.

Fallback ở experiments/results/mvp05-08-manual-img001/: agent chọn quad normalized dạng draft, **không phải GT hoặc xác nhận của người dùng**. Reuse enhancement_demo trên JPEG gốc; warp951×1284 rồi Color/Gray/Adaptive/Otsu, tổng8 PNG. Color=warp từng pixel do denoiseNone; configs confirmed=false. Đã xem comparison/warp: còn mép bàn và vùng giấy gấp, homography không dewarp. Detect thất bại không chặn lõi quét bằng góc tay; giao diện sửa góc vẫn chưa có.

## Nợ kỹ thuật task 3–4 và hướng giải quyết

Đây chủ yếu là **nợ thiết kế/hiệu chỉnh thuật toán**, chưa thấy bằng chứng gọi sai OpenCV hoặc tính sai công thức. Đổi score/status không sửa được mask hoặc nhận nhầm đối tượng. Số đo dưới đây lấy từ ứng viên revised thực trong batch:

| Ca | Max khoảng cách điểm contour→cạnhQ | Chia đường chéo analysis | min hỗ trợ một cạnh | f diện tích |
|---|---:|---:|---:|---:|
| img_002 |9.02px|.00602|.11373|.97953|
| img_003 |7.08px|.00472|.15040|.98200|
| img_004 |160.76px|.10727|.02857|.93018|
| img_005 |8.83px|.00589|.13184|.97760|
| img_006 |143.62px|.09583|.07394|.92281|
| anhtestnew |2.65px|.00347|.96528|.98427|
| frame_and_paper |1.00px|.00251|1.00000|.99270|

Phép đo là max trên **các đỉnh contour đã lưu bởi CHAIN_APPROX_SIMPLE** tới đoạn Q gần nhất; không phải Hausdorff liên tục hoặc corner error so GT. Định nghĩa/số liệu ở audit-evidence.json và script QA. Chưa đưa phép đo hoặc gate mới vào production descriptor.

**Task 3: epsilon phụ thuộc chu vi răng cưa.** img_004 dùng epsilon162.52px, img_006 dùng189.46px mà vẫn tạo quad hợp lệ. Hướng nhỏ nhất cần thử là giữ Douglas–Peucker, so baseline với epsilon=min(ratio·P, alpha·D) trên cùng contours; hoặc sinh như cũ rồi kiểm fit distance chuẩn hóa. Chọn alpha bằng development, không chốt từ hai ca sai. Nếu siết khiến không còn bốn đỉnh thì trả manual; không ép minAreaRect hoặc hạ gate. [OpenCV](https://docs.opencv.org/4.x/dd/d49/tutorial_py_contour_features.html) xác định epsilon là tolerance khoảng cách; cap theo D ở đây là **đề xuất của dự án**, chưa là công thức từ giáo trình.

**Task 3: Otsu nhập bàn và giấy.** Kiểm fit có thể loại quad sai nhưng chưa tìm ra giấy. Sau bước trên mới thử đặc trưng màu giấy–bàn hoặc hiệu chỉnh chiếu sáng, so mask/contour trên cả ảnh tốt/xấu. Ngưỡng cục bộ là biến thể để thử, không bảo đảm thắng Otsu: ô ly/chữ/bóng có thể làm mask vỡ. [Tài liệu thresholding](https://docs.opencv.org/4.x/d7/d4d/tutorial_py_thresholding.html) phân biệt global/local, không khẳng định lớp sáng là giấy. Với MVP, giữ nhánh phụ hữu hạn và sửa tay; chưa cần ML/dewarp hoặc pipeline Hough mới.

**Task 4: e tổng và f diện tích che cạnh yếu/sai lệch không gian.** Ưu tiên thử **cảnh báo** từ min(e_i)/số cạnh yếu và fit distance riêng trước khi đổi trọng số. Không chọn .10 chỉ vì nó phân biệt nhóm ảnh này: quad bám giấy khá đúng cũng có min support chỉ .113–.150, và mép cong/tối có thể thấp hơn. Nếu thử thống kê robust như p95, cần lấy mẫu theo độ dài biên để tránh lệch do CHAIN_APPROX_SIMPLE. Giữ f area là thông tin riêng, không đổi tên thành spatial fit.

**Task 4: khung giả có biên đẹp.** Frame có min support=1 và fit distance nhỏ: **siết epsilon/side gate không giải quyết ca này**. Cần thử phát hiện vùng lồng nhau/ứng viên khác biệt để cảnh báo mơ hồ, hoặc đặc trưng phân biệt bên trong/ngoài trang; người dùng chọn vùng đúng. Không loại ứng viên lớn nhất vô điều kiện vì giấy thật có thể gần đầy ảnh. Mọi đề xuất, kể cả S≥.60, vẫn cần xác nhận tay.

**Nợ dữ liệu:** cần thêm nhiều tài liệu vật lý/nền/màu/độ sáng và nhãn góc development. Đổi từng biến độc lập; ghi đúng/sai/không đề xuất và IoU/corner error khi có GT; giữ frame/img_004/img_006 làm ca hồi quy. Khóa điều kiện trước test. Counts hoặc sáu ảnh cùng doc_01 chưa chứng minh thuật toán mới tốt hơn.

Khuyến nghị: thử cap/fit distance và cảnh báo cạnh yếu trước; phân vùng màu/chiếu sáng sau khi có đối chứng. Giữ manual confirmation cho cảnh mơ hồ. Thí nghiệm phù hợp MVP13.04, có thể đưa lên sớm khi người dùng chọn. **Lượt này chỉ đo và nêu hướng, chưa sửa ngưỡng/score/phân vùng.** Nguồn/geometry/enhancement và hợp đồng góc không cần viết lại.

## Bàn giao

38 task chính và 5 AUX hoàn thành; giữ110ID gốc/109 task cần làm/1 skip/5 optional. Checklist duy nhất là [todo](../tasks/todo.md). Tiếp theo MVP06.01: pipeline offline detect hoặc góc tay → warp → enhancement; không suy ra UI/revision/storage/PDF hoặc accuracy cuối đã có. Ảnh/kết quả/script.tmp cục bộ ignored; không commit/push/deploy hoặc gửi ảnh ra dịch vụ ngoài.
