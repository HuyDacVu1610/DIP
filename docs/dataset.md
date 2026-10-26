# Dataset development/test — Document Scanner MVP

Ngày lập: 14/10/2026. Nguồn: [phạm vi MVP, mục 6](MVP_Pham_Vi_Va_Ke_Hoach_4_Tuan.md), [task 07–08](../tasks/todo.md). Đây là chính sách dữ liệu; số dự kiến không phải số đã thu.

## Bộ dữ liệu chốt ngày 26/10/2026

Người dùng đã cung cấp doc_ver2 và chấp nhận bộ ảnh hiện có là đủ cho MVP, thay mục tiêu khoảng20ảnh/5tài liệu ngày18/10 (trước đó40/10). Số thực tế:

| Nhóm | Tài liệu | Ảnh khác nhau | ID |
|---|---:|---:|---|
| development | 1 | 6 | doc_01, img_001…006 |
| test | 1 | 7 | doc_02, img_007…013 |
| Tổng | 2 | 13 | Không đếm bản sao |

User xác nhận ngày26/10 rằng7ảnh mới chụp cùng một tờ hoặc các bản in cùng nội dung. Giữ toàn bộ chúng chung doc_02/test; doc_01 là nhóm viết tay đã dùng thử/chọn tham số nên giữ development. Không chia các góc chụp của một tài liệu sang hai tập. Tập test đã được chuẩn hóa/gán nhãn trước khóa13.06 và đánh giá sau khóa ở13.07 ngày26/10. Không dùng test để tune; từ mốc13.07 bộ này đã được quan sát. Kết quả và giới hạn ở [results](results.md).

doc_ver2 có8tệp,7hash nguồn khác nhau. Tệp có đuôi (1) trùng hoàn toàn img_009 nên giữ nguyên byte trên máy nhưng không thêm dòng manifest. Nhóm doc_01 trước đây cũng có một bản sao img_006. Hai ảnh anhtestnew.jpg/WrongEXIF.jpg đã dùng thử và chưa xác nhận nhóm, không tự thêm vào test. JPG demo, DB runtime và fixtures tổng hợp không tính vào bộ13ảnh này.

Đây là bộ minh họa nhỏ chỉ có một tài liệu mỗi split và cùng bối cảnh nền bàn. Có phối cảnh, bóng, gấp/curl nhẹ, một ảnh mờ; không có ca nhàu rõ/glare/highlight đủ đa dạng như kế hoạch đầu. Giữ nguyên các ca khó, ghi giới hạn khi báo cáo; không kết luận khả năng tổng quát hoặc hiệu quả dewarping từ bộ này. Không tạo thêm ảnh/nhãn giả để bù quy mô.

## Manifest và nhận dạng tài liệu

[dataset_manifest.csv](../experiments/dataset_manifest.csv) dùng UTF-8, dấu phẩy; header và thứ tự cột:

| Cột | Quy ước |
|---|---|
| image_id | ID ảnh ổn định, ví dụ img_001; duy nhất, không chứa tên/thông tin riêng |
| document_id | ID của **cùng tài liệu vật lý/nội dung**, ví dụ doc_01; nhiều ảnh của cùng tài liệu giữ cùng ID |
| condition | Một hoặc nhiều tag bên dưới, ngăn bằng `;`, không trùng tag |
| split | Chỉ `development` hoặc `test`; cố định theo document_id |
| source_path | Đường dẫn POSIX `/` tương đối gốc dự án đến JPEG/PNG gốc, trong experiments/data/ hoặc experiments/results/ được ignore |
| source_sha256 | SHA-256 của byte nguồn thật, 64 ký tự hex thường; không dùng hash pixel/thumbnail |
| normalized_path | PNG nguồn sau EXIF, thường experiments/results/development/img_001/source.png; có thể trống trước chuẩn hóa |
| normalized_sha256 | Hash của chính PNG đã lưu; đi cùng normalized_path hoặc cùng trống |

ID dùng chữ thường, số, `_`/`-`, bắt đầu bằng chữ. Tag condition: `even_light`, `perspective`, `shadow_light`, `shadow_strong`, `fold_light`, `complex_background`, `blur`, `glare`, `occlusion`, `highlight`, `wrinkled`, `cropped`. Hai tag cuối bổ sung18/10: giấy nhàu rõ và giấy/góc sát hoặc cắt khung ảnh. Tag phản ánh ảnh quan sát thực tế; ví dụ một ảnh nghiêng có bóng là `perspective;shadow_light`. Bóng đậm bao phủ vùng giấy ghi shadow_strong, không gắn nhãn bóng nhẹ để khớp kế hoạch. `even_light` mô tả ánh sáng đều, không tự bảo đảm dễ nhận diện. Ca cong/nhàu/lóa/mất góc được giữ và mô tả giới hạn, không bỏ để làm số đo đẹp.

Không chia ngẫu nhiên theo image_id: các góc chụp, crop, đổi tên tệp hoặc biến thể của cùng tài liệu ở cùng split. Bản sao/bản in cùng nội dung cũng giữ chung nhóm để tránh gần trùng giữa hai tập. Người dùng xác nhận nhóm tài liệu; checksum hoặc hình thức tệp không chứng minh hai trang là tài liệu khác nhau. Không chuyển ảnh test sang development sau khi xem kết quả test.

Giữ byte nhập, ảnh chuẩn hóa và output ở vùng ignored; chỉ schema/quy tắc/manifest với ID và đường dẫn không nhạy cảm theo Git. Có thể đặt ảnh bổ sung ở experiments/data/development/; trước khi cập nhật manifest, xác nhận ảnh nào thuộc cùng tài liệu. Ảnh test thu vào vùng riêng và không dùng để chọn threshold/epsilon/kernel/scoring. Kiểm tra checksum tự động không phải tuning hoặc xem nội dung để chọn tham số.

## Chuẩn hóa và nhãn EXIF

1. Giữ JPEG/PNG gốc; chạy normalize_one.py để tạo nguồn PNG sau EXIF và alpha trắng. Ghi đúng source_sha256/normalized_sha256 từ metadata.json.
2. Nhãn bốn góc gắn với **nguồn PNG chuẩn hóa**, kích thước sau EXIF, không gắn với JPEG raw, thumbnail hay preview. Trình xem JPEG có thể tự xoay, nên kiểm tra metadata/dimensions chứ không dựa vào hai ảnh nhìn giống nhau.
3. Quy ước nhãn/API theo [image-contract](image-contract.md): `[u,v]` hữu hạn trong [0,1], `u=x/(W−1)`, `v=y/(H−1)`; thứ tự bốn góc theo chu kỳ clockwise trong hệ y xuống. Lưu dimensions và normalized_sha256 cùng nhãn ở MVP13.02 để phát hiện đổi nguồn.
4. Nhãn chưa có không được coi là nhãn đã xác minh. Ghi trạng thái thiếu góc/không thể gán khi thu dữ liệu; không phát minh góc hoặc âm thầm loại ảnh lỗi. Gán và kiểm tra overlay ở task nhãn riêng; task 08 chỉ thu/kiểm tra nhóm development ban đầu.

## Kiểm tra manifest

[validate_dataset.py](../experiments/validate_dataset.py) kiểm tra schema, ID/condition/split/path/hash, cùng document_id ở một split, ảnh không trùng ID/path/hash; normalized hash trùng cũng bị từ chối dù JPEG gốc khác byte. Checker không suy luận danh tính tài liệu từ hình ảnh và không chứng nhận chất lượng ảnh/nhãn.

Từ root, dùng venv:

```powershell
& .\backend\.venv\Scripts\python.exe experiments/validate_dataset.py
& .\backend\.venv\Scripts\python.exe experiments/validate_dataset.py --check-files
```

`--check-files` đọc theo khối để so hash với tệp thực; không giải mã hay tune test. Kết quả JSON là số dòng ảnh/tài liệu thực; bộ hiện hành là13ảnh. Manifest chỉ có header hợp lệ được chấp nhận với số0 để hoàn thành schema task07; điều đó **không nghiệm thu task08 hoặc cổng giai đoạn02**.

## Nghiệm thu nhóm đầu tiên

MVP02.08 chỉ hoàn thành sau khi có ≥6 ảnh development khác nhau, document_id được xác nhận, file đọc/chuẩn hóa được, condition/split/path ghi đúng và từng ảnh được xem trực quan. Nhóm cần có các ca sáng đều, nghiêng, bóng/nếp gấp nhẹ và nền khó theo kế hoạch. Không nhân bản một ảnh hoặc tạo bóng/nếp gấp tổng hợp để thay cho ảnh thu thật.

Nhóm đầu đã đạt MVP02.08, gồm:

| image_id | document_id/split | Quan sát thực tế |
|---|---|---|
| img_001 | doc_01 / development | Chụp nghiêng, góc trái trên gấp nhẹ, nền gỗ/đồ vật |
| img_002 | doc_01 / development | Trang khá sáng đều, nghiêng, nền gỗ nhiều chi tiết; góc dưới trái sát/cắt mép ảnh, thêm cropped ngày18/10 |
| img_003 | doc_01 / development | Bóng đậm phủ vùng chữ/giấy, nghiêng; ghi shadow_strong như ca khó |
| img_004 | doc_01 / development | Trang khá sáng đều, có phối cảnh, nền và đồ vật phía trên |
| img_005 | doc_01 / development | Giấy nằm ngang/nghiêng trong khung ảnh; nền gỗ phức tạp |
| img_006 | doc_01 / development | Góc trái trên gấp nhẹ, phối cảnh và nền gỗ |

Nguồn chuẩn hóa của mỗi ảnh **1536×2048**, thumbnail **240×320**. Source/thumbnail/metadata ở experiments/results/development/img_001…img_006/; đường dẫn và hash cụ thể trong manifest. Normalization sửa EXIF/alpha/màu, giữ toàn bộ khung chụp; chưa phát hiện/cắt/warp trang ở giai đoạn 02. Hai trang có góc gấp và ảnh bóng đậm được giữ để ghi giới hạn, không làm dewarping hoặc làm sạch bóng trong bước nhập.

Ở mốc14–18/10: development6ảnh/doc_01,test0 đủ nhóm đầu02.08. Ngày26/10 đã bổ sung7ảnh/doc_02/test và chốt bộ13ảnh/2tài liệu như phần đầu. Chưa có accuracy/IoU/error hoặc benchmark dataset.

## Nghiệm thu thu ảnh — MVP13.01,26/10/2026

Manifest13dòng có đủ source/normalized path, SHA-256 thực, condition, document_id và split; ID/hash không trùng, một tài liệu không xuất hiện ở hai tập. img_007–010/012–013 có nguồn1536×2048; img_011 chụp ngang2048×1536. Dùng normalize_one.py có sẵn, giữ toàn bộ JPEG gốc và ghi đúng PNG payload nguồn/thumbnail/metadata vào thư mục mới; không qua uploadDB hoặc detector.

Nguồn mới ở experiments/data/doc_ver2/, PNG chuẩn hóa và inventory/hash/overlay/snapshot/verification ở experiments/results/mvp13-doc-ver2-20261026/ (ignored). Nhóm tài liệu được user xác nhận, không suy ra từ checksum. MVP13.01 nghiệm thu theo quy mô13ảnh/2tài liệu user chốt; không ghi đã thu đủ20/5.

## Nhãn góc thủ công — MVP13.02

[annotations.json](../experiments/annotations.json) schema_version1 có coordinates=normalized_w_minus_1_h_minus_1 và records phủ đúng image_id của manifest. Mỗi record lưu normalized_sha256,width,height,status,corners,reason,reviewed,labeler,notes. Kích thước/hash buộc với PNG nguồn sau EXIF; tọa độ u=x/(W−1),v=y/(H−1), không dùng thumbnail. Chọn bốn mốc theo chu kỳ clockwise trong hệ y xuống; giữ điểm đầu phù hợp góc trên trái của ảnh, không cố xoay theo hướng chữ. Chỉ làm tròn khi vẽ overlay.

- labeled: bốn góc đủ quan sát, corners là quad hợp lệ, reason rỗng.
- unlabelable: corners=null, reason giải thích cụ thể. Với góc gấp lật làm mép gãy/nonplanar hoặc góc bị cắt khung, không dựng góc phẳng tưởng tượng. Ảnh vẫn nằm trong manifest và báo số lượng riêng; không âm thầm bỏ khỏi bảng kết quả sau này.
- reviewed=true nghĩa là người gán đã mở nguồn/overlay để rà, không phải validator chứng nhận độ chính xác. Nhãn hiện do codex_manual_visual_v1 chọn và tự rà độc lập detector; chưa có người thứ hai xác minh. Góc giấy bo nhẹ chọn mốc tại chỗ chuyển hai mép, có sai số thủ công chưa đo; không quảng cáo nhãn có độ chính xác subpixel.

Kết quả hiện hành26/10:13records,10labeled/3unlabelable,reviewed13/13. img_003/004/005 và007…013 có quad thủ công;001/006 gấp góc,002 sát/cắt khung giữ corners=null và lý do cũ. Bảy nhãn mới được chọn theo mép giấy trên nguồn, đã mở từng nguồn và từng overlay full để rà; không lấy từ detector hay góc app. Giấy in có curl/nếp nhẹ nên quad chỉ xấp xỉ bốn mốc, không phải mask đường bao chính xác. Reviewed là tự rà của Codex, chưa có người thứhai kiểm sai số. Không suy ra10/13 là tỷ lệ đúng của detector.

[validate_annotations.py](../experiments/validate_annotations.py) dùng lại manifest validator và validate_quad của lõi, kiểm toàn bộ hash nguồn/PNG, dimensions, EXIF, ID/coverage, topology, trạng thái và gate reviewed. Không nhận diện, tune, warp hay sửa ảnh nguồn. Lệnh từ root:

```powershell
& .\backend\.venv\Scripts\python.exe experiments/validate_annotations.py
# Trước khi duyệt: reviewed=false; tạo overlay ở thư mục chưa tồn tại.
& .\backend\.venv\Scripts\python.exe experiments/validate_annotations.py --allow-unreviewed --output-dir experiments/results/annotation-review-new
# Sau khi đã mở và kiểm tra overlay, cập nhật reviewed=true rồi kiểm lại.
```

CLI trả lỗi nếu hash/dimensions/góc/coverage sai hoặc nhãn chưa duyệt; --allow-unreviewed chỉ bỏ gate duyệt. --output-dir tạo PNG cùng dimensions, đánh số0–3 cho quad hoặc nhãn unlabelable, snapshot JSON ghi cuối; không ghi đè thư mục cũ. Evidence lịch sử18/10 ở experiments/results/mvp13-01-02-verified/. Bộ hiện hành26/10 ở experiments/results/mvp13-doc-ver2-20261026/:overlays/ có13PNG/snapshot,review-sheet.png,inventory vàverification. Khi có ảnh mới phải thêm nhãn trước khi validator chấp nhận manifest mở rộng.


## Đánh giá chỉ development — 26/10/2026

13.03–04 đã có [metrics/kết quả](results.md),24lượt trên6ảnh doc_01. validate_annotations(...,split='development') là tùy chọn Python cho evaluator: chỉ mở/hash/giải mã nhãn nguồn của split đã chọn; mặc định CLI cũ vẫn kiểm toàn bộ13ảnh. Tests cố ý để filetest không tồn tại vàevaluator vẫn hoàn tất4profile fixture,đảm bảo không đọcpixeltest. Manifest metadata/ID/split vẫn kiểm trên toànCSV. Các hash nhãn/manifest vàbyte nguồn giữ nguyên; test7ảnh chưa chạy detector hoặc dùng đểtune. Thu/nhãn13.01–02 không đổi.


### Mốc khóa 13.06 — 26/10/2026

13.05 dùng 3 nhãn development để so Otsu/Adaptive trên cùng warp; 3 unlabelable giữ lý do,
không suy diễn góc để tăng số mẫu. Highlight tổng hợp chỉ minh họa, không thêm vào manifest.
Manifest/annotations giữ hash của mốc 13.03–04. Bản [frozen.json](../experiments/configs/frozen.json)
đã được tạo và kiểm sau hồi quy; [môi trường](experiment-environment.md) ghi mốc trước test.
7 ảnh doc_02/test vẫn chưa chạy detector/enhancement hoặc tune. Trước 13.07 phải verify_frozen;
không thay nhãn/manifest sau khi nhìn kết quả để cải thiện chỉ số.


### Đánh giá sau khóa 13.07–08 — 26/10/2026

7 ảnh doc_02/test đã chạy đúng bản khóa; tất cả có GT, mean IoU0,995347/sai số góc2,303px,
7/7 IoU≥0,90 trong một tài liệu. Manifest/nhãn/13 nguồn nguyên; không đổi nhãn theo kết quả.
6 ảnh development vẫn tách riêng,3 unlabelable không bị loại khỏi bộ dữ liệu.
Lượt đầu benchmark có lỗi PID đo RAM launcher; giữ nguyên và đo lại bằng PID server thật,
không đổi thuật toán hoặc biến bộ test đã thấy thành tập độc lập mới.
[Kết quả](results.md), [audit](audit-phase-13.md), [phương pháp](benchmark-method.md).
Các đoạn “chưa chạy test” phía trên là lịch sử ở mốc chuẩn bị/khóa, không phải trạng thái hiện hành.
