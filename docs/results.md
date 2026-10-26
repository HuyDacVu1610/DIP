# Kết quả thực nghiệm development/test — MVP13.03–08

[Báo cáo thuật toán và thực nghiệm](report.md) đã tổng hợp ở MVP14.05–06, gồm công thức,
bảng lấy trực tiếp từ CSV, bốn hình không chứa nội dung trang và mục tiêu chưa đạt.
Các phần dưới giữ diễn biến theo mốc13; trạng thái “chưa chạy test” trong phần13.05/06
là lịch sử trước13.07, không phải trạng thái hiện tại. Số liệu gốc và bản khóa không đổi.

Ngày 26/10/2026. Bộ dữ liệu người dùng chốt gồm 13 ảnh/2 tài liệu; phần 13.03–05 dùng 6 ảnh development của doc_01; phần cuối 13.07–08 đánh giá 7 ảnh test doc_02 sau khóa 13.06. Không dùng test để chọn tham số. Kết quả hai tập được báo riêng. Đã đối chiếu [quy ước biểu diễn và mô tả biên, mục 5.5.1–5.5.3](Phan_Tich_Huong_Thuat_Toan_Tu_Tai_Lieu.md) và [quy tắc gắn nhãn với nguồn](dataset.md).

## Quy ước metrics và mẫu số

`experiments/metrics.py` dùng lại `polygon_iou` của lõi: diện tích giao/diện tích hợp của hai đa giác liên tục. Chỉ trong đánh giá mới chấp nhận đảo chiều chu kỳ sau khi xác minh tứ giác đơn, lồi. Không sắp xếp để sửa tứ giác tự giao hoặc đổi thứ tự các điểm kéo trên app. Hai quad giống nhau cho IoU = 1 dù khác điểm đầu hoặc chiều duyệt.

Sai số góc là giá trị nhỏ nhất trên 8 cách ghép (4 dịch vòng × 2 chiều) của trung bình 4 khoảng cách Euclid, đo bằng pixel nguồn sau EXIF. Giữ tọa độ subpixel và chia cho đường chéo `D = hypot(W−1, H−1)` để có sai số chuẩn hóa. Không đo trực tiếp khoảng cách Euclid trên u/v khi W khác H.

Có 3 ảnh với nhãn quad thủ công: img_003/004/005. Ba ảnh img_001/002/006 không thể gán quad đáng tin (`unlabelable`) được giữ trong CSV và báo riêng. Quy ước mẫu số:

- Mean IoU và tỷ lệ IoU ≥ 0,90 dùng toàn bộ 3 ảnh có nhãn. Ảnh có nhãn nhưng thiếu đề xuất nhận IoU = 0, vẫn tính là thất bại.
- Sai số góc để `null` khi thiếu đề xuất; trung bình chỉ dùng ảnh có cả nhãn và đề xuất, kèm số mẫu.
- Tỷ lệ có đề xuất tính trên cả 6 ảnh và không phải độ chính xác.
- Lỗi xử lý ghi `status=error` và giữ dòng ảnh/profile, không âm thầm loại mẫu.

## Bốn cấu hình kiểm soát

[detection_trials.json](../experiments/configs/detection_trials.json) định nghĩa `detection-ablation-v1`:

| Profile | Gaussian | Closing | Chọn ứng viên |
|---|---|---|---|
| scoring | 5×5 | 3×3 | scoring/NMS hiện hành |
| largest_contour | 5×5 | 3×3 | contour hợp lệ có diện tích lớn nhất |
| no_gaussian | tắt, kernel 0 sao chép gray | 3×3 | scoring |
| no_closing | 5×5 | tắt, contour map sao chép cạnh thô | scoring |

Mỗi profile sau chỉ đổi một yếu tố so với `scoring`. Các yếu tố cố định: preset revised với 3 cặp Canny 20/60, 50/150, 75/200; chuyển sang vùng sáng Otsu chỉ khi Canny không có quad; cạnh analysis tối đa 1.200; aperture 3/L2 true; epsilon/P = 0,015/0,02/0,03; ngưỡng diện tích 10% và cạnh 5%; score `clip(.45a + .35e + .20f − .15b, 0, 1)`; ngưỡng status 0,40/0,60.

`e` luôn lấy từ cạnh Canny thô cùng trial, không lấy từ closing hoặc mask. `largest_contour` dùng cùng tập ứng viên đã qua kiểm tra và cùng ngưỡng status; chỉ thay lựa chọn trước NMS. Đây là đối chứng chọn contour hợp lệ lớn nhất. Khi thay Gaussian/closing, điều kiện kích hoạt Otsu có thể đổi như hệ quả của pipeline cố định.

## Số đo từ 24 lượt (6 ảnh × 4 profile)

| Profile | Có đề xuất / 6 ảnh | IoU ≥ 0,90 / 3 ảnh có nhãn | Mean IoU / 3 ảnh | Sai số góc trung bình (pixel) / 3 ảnh đã đề xuất |
|---|---:|---:|---:|---:|
| scoring | 5/6 | 2/3 | 0.952871 | 20.031 |
| largest_contour | 5/6 | 2/3 | 0.951532 | 20.424 |
| no_gaussian | 6/6 | 2/3 | 0.901162 | 53.427 |
| no_closing | 6/6 | 2/3 | 0.951532 | 20.424 |

Mỗi profile đều đề xuất được trên đủ 3 ảnh có nhãn nên mẫu số sai số góc lượt này là 3. Không gọi 2/3 là accuracy toàn bộ 13 ảnh hoặc kết quả test; cả 6 ảnh development đều cùng một tài liệu.

| Ảnh có nhãn | scoring IoU | largest_contour IoU | no_gaussian IoU | no_closing IoU |
|---|---:|---:|---:|---:|
| img_003 | 0.993795 | 0.993795 | 0.994018 | 0.993795 |
| img_004 | 0.872497 | 0.872497 | 0.716925 | 0.872497 |
| img_005 | 0.992319 | 0.988302 | 0.992543 | 0.988302 |

## Quan sát và giải thích từ overlay/mô tả ứng viên

- **img_003 (bóng):** cả bốn profile gần mép giấy. Bỏ Gaussian tăng IoU rất ít, chưa chứng minh nên bỏ lọc trên tập tổng quát.
- **img_004:** scoring dùng region Otsu vì Canny không có quad, nhưng vùng sáng nối thêm nền bàn. IoU ≈ 0,872497 và sai số góc ≈ 54,771 px; largest_contour và no_closing chọn cùng quad sai. No_gaussian chọn quad Canny lấn ra bàn nhiều hơn: IoU ≈ 0,716925 và sai số ≈ 155,015 px. Thêm đề xuất hoặc đổi biên chưa khắc phục khả năng phân biệt giấy với bàn.
- **img_005:** scoring và largest chọn khác một chút trên cùng tập 12 ứng viên. Scoring có a = 0,280987; e = 0,512048; f = 0,977604; S = 0,501182. Largest có a = 0,281214; e = 0,490972; f = 0,976260; S = 0,493638. Diện tích quad lớn hơn không bù được mức hỗ trợ từ cạnh thô và độ khớp thấp hơn. Metadata còn có diện tích contour, chu vi, số mẫu cạnh, góc đổi hướng, trial và epsilon để kiểm tra. Diện tích là đặc trưng vùng; không gọi nó là mô tả biên thuần túy. Chênh lệch IoU khoảng 0,004, quá ít mẫu và còn sai số nhãn thủ công để suy rộng ưu thế.
- **img_001/006:** no_gaussian hoặc no_closing có thêm đề xuất nhưng overlay còn chọn bàn, dòng chữ hoặc cắt thiếu giấy. Không có quad tham chiếu đáng tin nên không tính IoU. Tăng số ảnh có đề xuất từ 5/6 lên 6/6 không có nghĩa là tăng tỷ lệ đúng.

Đã xem 6 ảnh comparison, mỗi ảnh có 4 panel; overlay riêng giữ độ phân giải analysis, với nhãn tham chiếu màu xanh lá, đề xuất đỏ, chẩn đoán vàng và contour xanh dương. Không vẽ nhãn tham chiếu cho ảnh unlabelable. Với ngưỡng tham chiếu 0,90, img_004 vẫn chưa đạt. Chưa thay preset, trọng số hay ngưỡng của app từ các quan sát này.

## Tái lập và giới hạn

```powershell
& .\backend\.venv\Scripts\python.exe experiments/evaluate_detection.py --output-dir experiments/results/detection-evaluation-new
& .\backend\.venv\Scripts\python.exe -m pytest -c backend/pyproject.toml experiments/tests backend/tests/test_detection_ablation.py backend/tests/test_annotations.py --basetemp=.tmp/pytest-detection-evaluation-new
```

Output phải là thư mục mới; CLI chọn development trước khi mở nguồn. `validate_annotations(split='development')` kiểm hash, kích thước và nhãn của tập này, không mở pixel test. CLI giải mã đúng payload PNG đã kiểm hash qua `BytesIO`, chặn trường hợp nguồn/nhãn thay đổi giữa validation và decode. CSV có 24 dòng; metadata từng profile có config, mô tả ứng viên, metrics, timings và tham chiếu ảnh trung gian thật; summary có hash đầu vào, mã nguồn và môi trường. Lỗi hoặc output đã tồn tại trả exit 1, không ghi đè.

Bằng chứng chính tại `experiments/results/mvp13-03-04-verified/final/` (ignored): results.csv, summary.json, 6 PNG nguồn, 24 thư mục profile và 6 comparison. Timings là quan sát core một lượt/profile, không gồm decode/encode/I/O. Không có warmup, chạy lặp hoặc cách ly tải máy nên không dùng để kết luận tốc độ/p50/p95; benchmark chính thức thuộc 13.07. Các lượt `development` và `development-final` được giữ làm bằng chứng trung gian, không trộn thời gian hoặc chọn kết quả tốt nhất giữa các lượt.

Lõi `detection.py` thêm tùy chọn Gaussian 0/closing False cho ablation; mặc định app vẫn Gaussian 5/closing True/`detect-v1`. Đã đối chiếu mã trước sửa với mặc định mới và profile scoring trên 6 ảnh development: status, góc, score, mô tả, ứng viên, cạnh thô, blur và overlay bằng nhau; nguồn giữ nguyên. Hash mã nguồn detection.py thay đổi nên snapshot M1 cũ chỉ là bằng chứng lịch sử, không sửa hash cũ. Snapshot mã hiện hành được lưu ở summary; việc khóa cấu hình cho test thuộc 13.06. HTTP, DB, PageConfig, UI và dependency không đổi.

Kiểm chứng cuối: **1.244 tests đạt trong 166,50 giây với `-W error`**. `verification.json` ở thư mục bằng chứng đã kiểm hash của 254 PNG trung gian, score và nguồn gốc của 151 mô tả ứng viên, mẫu số, 24 dòng CSV và 6 comparison. Ảnh overlay/comparison của lượt đầu và lượt cuối giống nhau từng byte; hash manifest và nhãn giữ nguyên.

Nhãn do một người gán và tự rà, giấy có cong/gấp và chỉ có 3 quad tham chiếu từ 1 tài liệu development. Bộ này chưa đủ kết luận khả năng tổng quát hoặc giải quyết biến dạng giấy cong. Giữ 7 ảnh test chưa đánh giá và nợ img_004/006. Phần dưới cập nhật task 13.05–06.

## So sánh Otsu và Adaptive — MVP13.05

`evaluate_enhancement.py` chỉ chọn development và dùng góc tham chiếu đã gán thủ công. Mỗi ảnh chỉ warp một lần từ nguồn PNG sau EXIF, sau đó hai lượt `enhance_document` dùng cùng warp. Giữ BW/Median 3/không CLAHE/rotation 0/block 31/C 10; chỉ đổi `threshold.method`. Prepared gray của hai lượt được kiểm bằng pixel, histogram và hash. Không dùng quad detector của 13.04 để tránh trộn lỗi cắt vùng với chất lượng nhị phân; nhãn thực nghiệm không có nghĩa người dùng đã xác nhận ảnh trên app.

| Ảnh | Warp W×H | Otsu t thực | Pixel đen Otsu | Pixel đen Adaptive |
|---|---|---:|---:|---:|
| img_003 | 899×1290 | 147 | 41,86% | 7,59% |
| img_004 | 1118×1229 | 172 | 46,37% | 7,16% |
| img_005 | 1368×813 | 186 | 51,28% | 6,49% |

Tỷ lệ pixel đen là mô tả ảnh, **không phải accuracy chữ**. Không có một ngưỡng global cho Adaptive; metadata giữ `otsu_threshold=null`, scope local. Chênh lệch kích thước so với demo giai đoạn 04 đến từ quad tham chiếu hiện hành, không đổi cách ước lượng kích thước warp.

Đã mở cả 6 ảnh BW full, các warp màu và crop 100%:

- **img_003, bóng mạnh:** Otsu gộp vùng tối bên trái vào foreground đen, che nhiều chữ/dấu. Adaptive giữ được chữ trong vùng đó, nhưng giữ cả ô ly và làm đứt một số đoạn nét mảnh.
- **img_004, nhãn even_light:** ảnh thực vẫn có gradient sáng. Otsu làm đen vùng bên phải/dưới, che một phần nội dung; Adaptive tách chữ ra rõ hơn nhưng không loại nền ô ly. Warp lần này dùng góc tham chiếu, nên nhận xét này tách khỏi lỗi detector ăn bàn.
- **img_005:** ảnh ngang và sáng không đều; Otsu tạo mảng đen lớn bên trái/dưới. Adaptive giữ được nhiều dòng hơn, vẫn có nét nhạt/ô ly bị đứt. Không tự xoay theo chữ khi rotation đã cố định 0.
- **Màu và dấu:** cả hai BW đều mất màu mực/nền do chuyển gray rồi nhị phân. Không có OCR hoặc nhãn ký tự để đếm dấu/chữ đúng; những nhận xét trên là quan sát trực quan.

Ba ảnh img_001/002/006 vẫn có dòng `unlabelable` kèm lý do trong CSV, không bịa quad hay bỏ âm thầm. Tổng 6 ảnh development → 3 cặp/6 output BW, 3 dòng unlabelable, 0 lỗi xử lý; 9 dòng CSV. Bảy ảnh test chưa được chạy.

Dataset chưa có highlight thật rõ hoặc một trang sáng đều được kiểm soát. Ví dụ `synthetic-highlight/` dùng trang tổng hợp có chữ Việt, mực nhạt và ba dải vàng/hồng/xanh để minh họa riêng: Otsu mất nhiều nét nhạt; Adaptive giữ được nhiều nét đó nhưng tạo đường viền đen quanh dải màu. Cả hai làm mất màu highlight. Đã xem hai bản full; đây không phải ảnh chụp thật, không thêm vào manifest/số mẫu và không chứng minh chất lượng trên tài liệu highlight thực tế.

Bằng chứng tại `experiments/results/mvp13-05-06-verified/enhancement/`: source PNG, warp, filtered, prepared_gray, hai BW full, comparison, crop 100%, metadata/config/histogram/hash và results.csv. Các PNG output chỉ có 0/255; comparison thu nhỏ có thể có mức xám do nội suy. Đã tính lại Otsu/Adaptive từ prepared_gray và kiểm hash/kích thước 28 PNG của ba cặp thật cùng ví dụ tổng hợp. Không thay nguồn, nhãn, preset hoặc thuật toán app.

```powershell
& .\backend\.venv\Scripts\python.exe experiments/evaluate_enhancement.py --output-dir experiments/results/enhancement-new
```

## Khóa cấu hình — MVP13.06

Giữ các preset hiện tại vì chưa có bằng chứng development đủ mạnh để đổi. Bản [frozen.json](../experiments/configs/frozen.json) ràng buộc algorithm versions, score, preset đầy đủ, 91 hash mã nguồn, input metadata và dependency/môi trường thực tế. [Tài liệu môi trường](experiment-environment.md) ghi quyết định, SHA-256, lệnh kiểm tra và giới hạn.

Theo lựa chọn của người dùng ngày 26/10, đã chạy [hồi quy cần thiết trước khóa](verification-matrix.md): **1.255 backend/experiments tests**, **103 frontend tests**, typecheck/build và smoke UI nhập–confirm–render–PDF–reopen qua physical restart đều đạt. Giai đoạn 12 vẫn chưa nghiệm thu toàn bộ. Task 13.05–06 và checkpoint 13-C2 đạt; đánh giá test/benchmark 13.07, tổng hợp 13.08 và cổng 13 còn chờ.


## Đánh giá test sau khóa — MVP13.07 (26/10/2026)

Đánh giá bằng preset/score/detect-v1/scan-v1 đã khóa; SHA frozen giữ nguyên
`ce89a90e2fb9ca092350886276201f87e81cd09c90e6507f799fceca6a8d8109`.
Runner mới benchmark.py v1.1 có hash riêng, không sửa 91 tệp đã khóa.
[Phương pháp](benchmark-method.md) ghi trước số lượt, scope timing/RAM, cache và kiểm chứng.

Tập test gồm **7 ảnh/1 tài liệu doc_02**, cùng tờ hoặc cùng nội dung do user xác nhận;
độc lập document_id với development nhưng không phải 7 tài liệu độc lập.
Có 7/7 ảnh được đề xuất và đạt IoU ≥ 0,90; mean IoU = **0,995347**,
sai số góc trung bình = **2,303 pixel nguồn**, hay **0,000900 đường chéo nguồn**.
Mẫu số IoU là 7 ảnh có nhãn; sai số góc cũng có 7 mẫu, không thiếu proposal.
Đây là kết quả của một nhóm ảnh nhỏ, không gọi là “accuracy 100% trên mọi tài liệu”.

| Ảnh | Status | Score heuristic | IoU với nhãn thủ công | Sai số góc (px) |
|---|---|---:|---:|---:|
| img_007 | proposed | 0.674979 | 0.994572 | 2.690 |
| img_008 | proposed | 0.635145 | 0.995559 | 2.017 |
| img_009 | proposed_with_warning | 0.599750 | 0.994511 | 2.689 |
| img_010 | proposed | 0.644122 | 0.995016 | 2.262 |
| img_011 | proposed | 0.659978 | 0.995489 | 2.015 |
| img_012 | proposed | 0.676754 | 0.995895 | 2.700 |
| img_013 | proposed | 0.651041 | 0.996386 | 1.748 |

Cả 7 đề xuất đều từ Canny. img_009 có score 0,599750 nên cảnh báo vì thấp hơn 0,60,
dù IoU = 0,994511. Các thành phần a = 0,325122; e = 0,727423; f = 0,994234; b = 0
cho đúng score theo công thức đã khóa. Cảnh báo không phải bằng chứng cắt sai,
cũng như score cao không bảo đảm cắt đúng. Không hạ ngưỡng cảnh báo sau khi thấy test.

Đã xem contact sheet đủ 7 cặp overlay GT/đề xuất và overlay riêng img_009;
đường đề xuất bám gần các cạnh trang. Nhãn thủ công chỉ xấp xỉ bốn mốc,
một người gán/tự rà nên sai số vài pixel có cả thành phần không chắc chắn của nhãn.
Giấy có nếp nhẹ; IoU tứ giác cao không chứng nhận đã làm phẳng dòng chữ cong.

## Benchmark bản khóa

Nguồn đều 3.145.728 pixel: 6 ảnh 1536×2048 và 1 ảnh 2048×1536.
Full BW theo góc tham chiếu có diện tích khoảng 1,08–1,69 triệu pixel; ví dụ img_010 là
862×1250, img_011 là 1482×900 và img_012 là 1108×1523. Kích thước từng ảnh được giữ trong PNG/config.
Rotation 0 giữ hướng nguồn, kể cả img_011 có nội dung nằm ngang so với hướng đọc.
Benchmark render dùng góc tham chiếu và cùng preset BW; không lấy chất lượng detector
làm điều kiện loại ảnh khỏi benchmark render. HTTP import/config và tải ảnh output ở ngoài đồng hồ.

Mỗi đường có 35 mẫu đo thành công (7 ảnh × 5), thêm 7 warmup lưu riêng.
Tổng **140 mẫu đo + 28 warmup = 168 dòng**, không lỗi xử lý; server thật dùng SQLite/file store cô lập.

| Đường đo | p50 (ms) | p95 (ms) | Đỉnh working set đã lấy mẫu (MiB) | Thành công / lần đo |
|---|---:|---:|---:|---:|
| core_detect | 238.853 | 297.319 | 105.93 | 35/35 |
| core_render | 16.865 | 21.026 | 117.22 | 35/35 |
| http_detect | 313.193 | 340.877 | 155.89 | 35/35 |
| http_render | 178.500 | 204.495 | 155.85 | 35/35 |

RAM là số của tiến trình controller đối với core và tiến trình server thật đối với HTTP,
không phải tổng RAM cả app/máy hoặc lượng cấp phát riêng của một thuật toán.
Sampling 10 ms có thể bỏ lỡ đỉnh ngắn; CSV giữ baseline/end/lifetime peak để đọc đúng ý nghĩa.
Percentile dùng quantile linear trên mẫu đo thành công; lỗi và mẫu số vẫn được báo riêng.
Không có test tải đồng thời hoặc SLA để kết luận nhanh/chậm đạt chuẩn.

Cache kết quả ứng dụng tắt: **84 HTTP run ID khác nhau**, mỗi POST thực hiện lại xử lý.
Cache hệ điều hành/allocator vẫn giữ sau warmup; không gọi đây là cold-cache benchmark.
Core không tính decode/encode/I/O, HTTP tính request/queue/load/CPU/encode/persist/JSON qua loopback,
không qua frontend. Hai loại thời gian có phạm vi khác nhau.

Lượt đầu `test/` đo nhầm RAM của launcher Windows (~4,7 MiB), được giữ nguyên và gắn
`MEASUREMENT_INVALID.json`; không dùng RAM đó trong kết luận. Sau khi tái hiện lỗi bằng test,
runner v1.1 lấy PID do server tự báo và đối chiếu log Uvicorn rồi chạy lại trọn protocol vào `final/`.
Toàn bộ số thời gian/RAM trong bảng trên lấy từ lượt final, không trộn giá trị tốt nhất giữa hai lượt.
Chênh lệch thời gian giữa lượt đầu và lượt đo lại không phải cải thiện thuật toán.
Test đã được quan sát từ lượt đầu; lượt đo lại chỉ sửa phép đo, không trở thành một test độc lập mới.
Kết quả metrics, full PNG và comparison của 7 ảnh giống nhau từng byte giữa hai lượt.

## Tổng hợp kết quả, ca sai và giới hạn — MVP13.08

| Vấn đề/ca | Bằng chứng | Kết luận trong phạm vi dữ liệu |
|---|---|---|
| Development: scoring/largest/không Gaussian/không closing | 24 lượt, 3 GT/3 unlabelable; bảng phần đầu | Scoring mean IoU 0,952871; bỏ Gaussian 0,901162. Chưa đủ cơ sở đổi preset chỉ từ một tài liệu |
| Test doc_02 | 7 ảnh, 7 GT, bản khóa | 7/7 IoU ≥ 0,90, mean 0,995347. Không suy rộng sang mọi nền/tài liệu |
| img_004 development ăn bàn | overlay, region Otsu, IoU 0,872497; bỏ Gaussian 0,716925 | Nợ phân biệt giấy/nền vẫn còn; không dùng kết quả test tốt để che ca này |
| Bóng trên img_003/004/005 | cùng GT warp, Otsu/Adaptive full | Otsu có mảng đen che chữ; Adaptive giữ nhiều nội dung hơn nhưng vẫn ô ly/đứt nét |
| Gấp/cắt góc img_001/002/006 | lý do unlabelable và nguồn/overlay trước đây | Không bịa GT; chỉnh tay không tạo lại vùng giấy/chi tiết đã khuất hoặc bị cắt khỏi ảnh |
| Nếp nhẹ test, img_009 blur | overlay và score/mô tả | Bốn góc vẫn tốt trong nhóm này; không chứng minh dewarping hoặc phục hồi blur |
| Highlight | minh họa tổng hợp riêng, không có ảnh thật đủ phủ | BW mất màu; Otsu mất nét nhạt, Adaptive tạo viền dải. Không có accuracy highlight thực tế |
| Nhàu mạnh/lóa gắt/chữ bị che | chưa có tập đủ đại diện | Chưa kiểm chứng; không bịa tỷ lệ hoặc giả rằng homography/threshold khôi phục được thông tin mất |

Ảnh test in có ranh giới giấy–bàn rõ hơn nhóm development viết tay trên ô ly và có bóng mạnh.
Test tốt hơn development không phải bằng chứng tổng quát hóa mạnh: mỗi split chỉ có một tài liệu,
cùng bối cảnh bàn và nhãn một người; thiếu dữ liệu nhàu/lóa/highlight thật. Không gộp hai split
thành một accuracy tổng để giấu khác biệt điều kiện hoặc bỏ các ảnh unlabelable.

Homography chỉ đổi phối cảnh của một mặt phẳng xấp xỉ qua bốn điểm. Nó không nắn cong từng dòng
trên giấy nhàu, khôi phục góc ngoài khung, chữ bị che hoặc vùng cháy sáng mất chi tiết.
MVP giữ kiểm tra/xác nhận góc và chỉnh tay; trải giấy/chụp lại khi thiếu thông tin.
Nếu thử hướng giảm bóng/phân biệt nền/giới hạn fit sau này, dùng phiên bản và development phù hợp,
giữ bản khóa hiện hành và kết quả này; bộ test đã quan sát không còn là tập mới để tune.

## Bằng chứng và nghiệm thu giai đoạn 13

Thư mục chính ignored: `experiments/results/mvp13-07-08-verified/final/` có protocol,
accuracy.csv, samples.csv, summary, server-process/log, nguồn PNG, debug detector và full BW/preview.
`verification.json` ở thư mục cha kiểm 70 PNG detector/hash/kích thước, replay Gaussian/Canny/closing,
score/metrics, 84 run ID mới, 7 full HTTP bằng core, và manifest/nhãn/13 nguồn giữ nguyên.
Ảnh chứa thông tin riêng được giữ cục bộ; không chép nội dung cá nhân vào báo cáo hoặc đưa ảnh vào Git.

Hồi quy cuối: **1.261 tests backend/experiments, 173,10 s, -W error**, không skip.
103 frontend tests/typecheck/build là bằng chứng 13.06, không chạy lại vì source frontend/dependency không đổi.
Chưa có thay đổi thuật toán/API/UI; chỉ thêm runner/test và báo cáo. [Audit cả 8 task](audit-phase-13.md)
xác nhận 13.01–08/cổng 13 đạt trong phạm vi MVP 13 ảnh/2 tài liệu mà user đã chốt.
Giai đoạn 12 vẫn chưa nghiệm thu toàn bộ; điều chỉnh cổng hồi quy cho 13.06 giữ nguyên.
Tiếp theo 14.01, không thực hiện đóng gói trong lượt này.
