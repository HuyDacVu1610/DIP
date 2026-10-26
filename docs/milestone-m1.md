# M1 — Lõi quét tài liệu offline

Ngày nghiệm thu:16/10/2026. Mốc này hoàn thành giai đoạn06; chưa phải ứng dụng quét qua UI. [Checklist](../tasks/todo.md), [rà soát6task](audit-phase-06.md), [hợp đồng](image-contract.md), [ghi chú thuật toán](algorithm-notes.md).

## Luồng và đầu ra

JPEG/PNG gốc → kiểm tra/EXIF/alpha → source BGR uint8 → detector hoặc góc tay normalized → homography từ nguồn đầy đủ → warp → denoise → Color/Gray/BW → xoay → full PNG và preview từ full. Nhánh detection có analysis/Canny/closing/Otsu/contour/score riêng; ảnh đã làm mờ ở nhánh này không được dùng để xuất trang.

`scan_one.py INPUT --output-dir NEW` là một lệnh quét. `--mode color|gray|bw` hoặc `--config JSON`; `--corners JSON` cung cấp góc sau EXIF và chuyển draft. Config góc tay giữ thứ tự handle. CLI không tự xác nhận góc hoặc revision; mọi ví dụ nghiệm thu đều confirmed=false.

| Đầu ra | Vai trò |
|---|---|
| source.png | Đúng PNG chuẩn hóa sau EXIF, không đổi nguồn |
| source_overlay.png | Quad/đánh số trên tọa độ source, khi có render |
| detection/ | Các trial/stage/mô tả từ đúng lượt detector, nếu đã chạy |
| render/warp.png, filtered_bgr.png | Full warp và ảnh sau lọc |
| render/prepared_gray.png | Gray/BW sau contrast, trước threshold/xoay; Color không có |
| render/before_rotation.png, full.png, preview.png | Pixel trước xoay, kết quả cuối và preview max1000 thu từ full |
| config.json, metadata.json | Full config, raw/PNG/BGR hash, dimensions, H, version/dependencies/timing, histogram BW |

Histogram256bin đếm actual prepared_gray full. Otsu giữ t toàn cục thực; Adaptive là ngưỡng cục bộ, t=null. Gray/Color không threshold nên histogram=null. Preview BW có thể có mức xám do INTER_AREA, không phân ngưỡng lại. Mỗi output dùng thư mục mới; metadata được ghi cuối.

Exit0:đã có render nháp; exit2/manual_required:chưa có góc, không full giả; exit1:lỗi ảnh/config/I/O. Argparse cũng có thể exit2 nên kiểm status trong metadata. Không coi exit0 là chọn đúng giấy, được người dùng xác nhận hay đủ điều kiện xuất trong ứng dụng.

## Chạy lại không cần ảnh riêng

Từ root, sau khi cài backend theo [README](../README.md). Đoạn PowerShell sau dùng fixtures tổng hợp có sẵn, không cần web/DB/ảnh cá nhân. Góc toàn ảnh fixture chỉ để kiểm chứng luồng, không phải gợi ý áp dụng nguyên ảnh cho mọi tài liệu. Mỗi lượt tạo thư mục mới.

```powershell
$m1Python = (Resolve-Path 'backend/.venv/Scripts/python.exe').Path
$m1Out = Join-Path 'experiments/results' ('m1-smoke-' + (Get-Date -Format 'yyyyMMdd-HHmmss-fff'))
$m1Quad = '[[0,0],[1,0],[1,1],[0,1]]'
New-Item -ItemType Directory -Path $m1Out -ErrorAction Stop | Out-Null
$m1Before = (Get-FileHash 'fixtures/exif_6.jpg' -Algorithm SHA256).Hash
foreach ($m1Mode in @('color','gray','bw')) {
    & $m1Python experiments/scan_one.py fixtures/exif_6.jpg --mode $m1Mode --corners $m1Quad --output-dir (Join-Path $m1Out $m1Mode)
    if ($LASTEXITCODE -ne 0) { throw "Render $m1Mode failed" }
}
$m1Bw = Join-Path $m1Out 'bw'
$m1Replay = Join-Path $m1Out 'bw-replay'
& $m1Python experiments/scan_one.py fixtures/exif_6.jpg --config (Join-Path $m1Bw 'config.json') --output-dir $m1Replay
if ($LASTEXITCODE -ne 0) { throw 'Replay failed' }
foreach ($m1File in @('config.json','render/full.png','render/preview.png','render/prepared_gray.png')) {
    if ((Get-FileHash (Join-Path $m1Bw $m1File)).Hash -ne (Get-FileHash (Join-Path $m1Replay $m1File)).Hash) { throw "Mismatch $m1File" }
}
$m1Blank = Join-Path $m1Out 'blank.png'
& $m1Python -c "from PIL import Image; import sys; Image.new('RGB',(140,100),(200,200,200)).save(sys.argv[1])" $m1Blank
if ($LASTEXITCODE -ne 0) { throw 'Fixture creation failed' }
& $m1Python experiments/scan_one.py $m1Blank --output-dir (Join-Path $m1Out 'manual-required')
if ($LASTEXITCODE -ne 2) { throw 'Expected manual_required' }
$m1Failure = Get-Content -Raw (Join-Path $m1Out 'manual-required/metadata.json') | ConvertFrom-Json
if ($m1Failure.status -ne 'manual_required' -or (Test-Path (Join-Path $m1Out 'manual-required/render/full.png'))) { throw 'Unexpected full render' }
& $m1Python experiments/scan_one.py $m1Blank --corners $m1Quad --output-dir (Join-Path $m1Out 'manual-retry')
if ($LASTEXITCODE -ne 0) { throw 'Manual retry failed' }
if ((Get-FileHash 'fixtures/exif_6.jpg' -Algorithm SHA256).Hash -ne $m1Before) { throw 'Source changed' }
Write-Output "M1 smoke OK: $m1Out"
```

## Kiểm chứng ảnh thật và tái lập

Evidence đầy đủ ở `experiments/results/mvp06-m1-verified/verification.json` (ignored). Mỗi ca dưới chạy bằng **hai tiến trình CLI độc lập** với cùng raw source và cùng file config đầu vào. So toàn metadata/ảnh detection-render/config/histogram/H/hash, chỉ loại run_id và timings_ms. Ảnh được mở/đếm lại, tính kiểm warp/filter/gray/threshold/rotation/preview; không chỉ so hai lượt có cùng một lỗi. Full/preview PNG và config ổn định trong môi trường này. Điều đó không chứng nhận chất lượng quét hoặc tính tất định trên mọi máy.

| Ca | Mode/góc/xoay | Full W×H | Quan sát |
|---|---|---:|---|
| anhtestnew-color-auto | Color/auto/0° |201×285|Trang trắng khá phẳng; overlay bám vùng giấy, ảnh nhỏ không upscale |
| img003-gray-auto | Gray/auto/0° |898×1288|Warning; còn bóng đậm/ô ly |
| img004-otsu-auto | BW Otsu/auto/0° |1112×1358|Warning; vẫn ăn bàn, vùng bàn/biên thành đen; t=140 |
| img004-adaptive-manual | BW Adaptive/config góc/0° |1112×1358|Cùng quad sai; local/t=null, bỏ detector không có nghĩa hết lỗi |
| img001-auto | Color/auto |không có|manual_required, không warp/full/histogram giả |
| img001-color-manual | Color/tay/0° |951×1284|Có trang; còn mép bàn/gấp góc, không dewarp |
| img001-gray180-manual | Gray/tay/180° |951×1284|Kiểm xoay180 và CLAHE; không kết luận xóa bóng |
| img001-adaptive90-manual | BW Adaptive/tay/90° |1284×951|Gaussian+CLAHE; giữ ô ly/nhiễu, nét có thể đứt |
| exif6-otsu270-manual | BW Otsu/tay/270° |95×63|Fixture EXIF6; source64×96 sau EXIF, t=150 |
| checkerboard-otsu90-manual | BW Otsu/tay/90° |1300×2000|Fixture, preview650×1000 có gray do INTER_AREA; t=118 |

Tổng10cặp/20runs,18render/2manual_required;230PNG,8detection/28trials. Nguồn6cặp trong manifest và22fixtures giữ hash. Các góc tay img_001 là draft agent chọn để kiểm luồng, không GT/userconfirmed:

```json
[[0.32,0.25],[0.82,0.265],[0.75,0.89],[0.14,0.81]]
```

Để chạy lại một **case cụ thể** còn ảnh và file config cục bộ, ví dụ autoOtsu (thay tên output để không ghi đè):

```powershell
$m1Photo = (Import-Csv experiments/dataset_manifest.csv | Where-Object image_id -eq 'img_004').source_path
& .\backend\.venv\Scripts\python.exe experiments/scan_one.py $m1Photo --config experiments/results/mvp06-m1-verified/configs/img004-otsu-auto.json --output-dir experiments/results/my-m1-img004
```

Dùng config **đầu vào** với corners=null sẽ chạy detector lại. Dùng `.../img004-otsu-auto-1/config.json` có góc sẽ đi đường manual; không đòi metadata detection giống run auto. Giữ đúng nguồn theo hash/dimensions; PageConfig riêng lẻ không chứng nhận danh tính ảnh.

## Môi trường và kiểm thử

Windows11 build26300; Python3.12.10/OpenCV4.14.0/NumPy2.5.4/Pillow12.3.0, pipeline scan-v1. Package OpenCV trong requirements là4.14.0.94; cv2.__version__ hiển thị4.14.0. `backend/requirements.txt` khóa dependencies. Verification.json lưu hash source code processing/CLI/writer và requirements lúc chạy để phân biệt đổi code mà quên đổi nhãn version. Không thay code hoặc dependency trong lượt nghiệm thu; chỉ thêm tests/tài liệu.

```powershell
& .\backend\.venv\Scripts\python.exe -m pytest -c backend/pyproject.toml backend/tests/test_render.py backend/tests/test_scan_one.py
& .\backend\.venv\Scripts\python.exe -m pytest -c backend/pyproject.toml backend/tests
```

Focused45tests đạt30.73s; full **800passed99.97s** (794trước+4core snapshot/repeat+2CLI auto/failure repeat). Thời gian và run_id là thông tin từng lượt, không yêu cầu giống byte. Chưa khóa/đánh giá lại trên máy khác hoặc môi trường sạch; đó là phần đóng gói và thực nghiệm sau.

## Giới hạn và bước tiếp theo

M1 xác nhận luồng offline, giữ nguồn, fallback, ba mode, PNGfull/preview, actualstages/histogram/config/timing và tái lập trong môi trường hiện tại. Chưa có scanUI, persisted revision/storage/export ứng dụng, quản lý nhiều trang hoặc PDF. Homography giả định trang tương đối phẳng, không làm phẳng giấy nhàu; score heuristic không là accuracy.

Development chỉ6ảnh cùng1doc_01/test0; anhtestnew chưa identity/split. Nợ detector vùng nền sáng/epsilon theo contour/khung giả còn ở [audit05](audit-phase-05.md); giai đoạn06 không sửa chúng. Bước tiếp theo **MVP07.01 chốt schema API** để nối UI/lưu một trang.
