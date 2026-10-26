# Document Scanner

Đề tài giữa kỳ môn Xử lý ảnh số: nhập nhiều ảnh JPEG/PNG, đề xuất và chỉnh vùng giấy,
hiệu chỉnh phối cảnh, tạo bản quét Color/Gray/BW và xuất ảnh hoặc PDF nhiều trang.
Ứng dụng lưu trên máy, chạy bằng React/TypeScript/Vite + FastAPI/OpenCV + SQLite/ReportLab.

[Mở gói nộp](SUBMISSION.md) · [Demo và bảo vệ](docs/demo-script.md) ·
[Hướng dẫn sử dụng có ảnh](docs/user-guide.md) · [Checklist](tasks/todo.md) ·
[Báo cáo thuật toán/thực nghiệm](docs/report.md) · [Kết quả thực nghiệm](docs/results.md) · [Cấu hình bản chạy](docs/local-runtime.md)

## Cài và mở ứng dụng trên Windows

Môi trường đã kiểm chứng: **Python 3.12.10 64-bit, Node.js 24.15.0, npm 11.12.1**.
Cần có source với hai thư mục `backend/` và `frontend/`; không cần ảnh cá nhân để khởi động.
Dùng thư mục giải nén có đường dẫn ngắn, tránh lồng nhiều cấp trên Windows.
Dùng PowerShell. Thay đường dẫn ví dụ dưới đây bằng thư mục chứa README này trên máy bạn:

```powershell
Set-Location 'C:\Users\03201\OneDrive\Desktop\XU_LY_ANH'
python --version
node --version
npm.cmd --version
```

Nếu Python trong PATH khác bản trên, dùng đường dẫn tới Python 3.12.10 ở bước tạo venv.
Các lệnh sau chạy **từ root dự án**, không chuyển vào `backend/` hay `frontend/`:

```powershell
python -m venv backend/.venv
& .\backend\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt
& .\backend\.venv\Scripts\python.exe -m pip check
& .\backend\.venv\Scripts\python.exe -c "import fastapi, uvicorn, python_multipart, cv2, numpy, PIL, sqlalchemy, reportlab; print('Backend imports OK')"
npm.cmd --prefix frontend ci
npm.cmd --prefix frontend run build
```

`pip check` phải báo không có dependency hỏng; build phải tạo `frontend/dist/index.html`
và các tệp trong `frontend/dist/assets/`. Backend khóa 30 package bằng `==`, frontend dùng
`package-lock.json`. Không cần kích hoạt venv hoặc cài Vite/TypeScript/OpenCV toàn máy;
chỉ dùng một biến thể `opencv-python-headless`.

Khởi động, vẫn ở root:

```powershell
& .\backend\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --workers 1
```

Giữ terminal này chạy, mở **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**.
UI đã build và `/api/v1` chạy cùng origin; không cần mở Vite dev server.
Trong PowerShell thứ hai, kiểm tra:

```powershell
Invoke-RestMethod 'http://127.0.0.1:8000/api/v1/health'
```

Kết quả phải có `status = ok`. Health chỉ kiểm tra server đáp ứng, chưa chứng nhận một ảnh quét đúng.
[Swagger UI](http://127.0.0.1:8000/docs) dành cho xem/thử API.

Dừng bằng **Ctrl+C** trong terminal chạy Uvicorn, chờ `Application shutdown complete`.
Ngày sau chỉ chạy lại lệnh Uvicorn; không cần cài lại hoặc build lại nếu source không đổi.
Sau khi sửa React cần build lại, rồi reload trình duyệt.
Nếu cổng 8000 đang bận, đổi `--port 8000` thành `--port 8002`, mở URL và health ở 8002 tương ứng.
Lượt kiểm chứng README dùng bản source/venv/node_modules/DB riêng trên cổng 8002 để giữ app hiện tại.

## Sử dụng nhanh

1. Nhập tên → **+ Tạo tài liệu** → **Chọn ảnh tài liệu**, có thể chọn nhiều tệp.
2. App tự nhận diện từng ảnh. Duyệt các trang, chỉnh bốn góc theo mép giấy và bấm **Xác nhận vùng**.
3. Chọn Color/Gray/BW và bộ lọc → **Tạo bản quét**; xem so sánh, zoom hoặc ảnh trung gian.
4. Trong **Xuất tài liệu**, chọn trang và PDF; PNG/JPG yêu cầu đúng một trang.
   Bấm **Tạo tệp xuất → Tải**. Trang đã xác nhận còn thiếu bản quét sẽ được xử lý khi xuất.

[Hướng dẫn chi tiết](docs/user-guide.md) giải thích nháp chưa lưu, xác nhận, trạng thái bận,
khôi phục sau restart và các lỗi thường gặp. Có hai ảnh tổng hợp đi kèm để tự thử.

## Dữ liệu được lưu ở đâu?

`backend/app/settings.py` tính đường dẫn từ vị trí source, không lấy thư mục terminal làm data root.
DB mặc định là **`data/scanner.sqlite3`**, ảnh gốc/nguồn chuẩn hóa/thumbnail/bản quét/debug/tệp xuất
do ArtifactStore quản lý dưới **`data/`** bằng UUID. Giữ nguyên **toàn bộ `data/`** khi mở lại hoặc cập nhật;
chỉ sao lưu sau khi dừng backend và sao chép cả thư mục, không chỉ riêng DB hoặc vài ảnh.

Đóng tab không xóa tài liệu. Mở lại cùng app sẽ đọc danh sách, cấu hình đã lưu và bản quét gần nhất;
bản cũ không khớp cấu hình mới được đánh dấu cũ, không dùng để xuất như bản hiện hành.
Góc/tham số đang chỉnh chưa lưu có thể mất khi đổi trang/reload. Link tải vừa tạo và lựa chọn checkbox
không phải lịch sử xuất được phục hồi đầy đủ qua reload; có thể tạo lượt xuất mới.

Ảnh/PDF chỉ đọc qua API artifact; `/data/...` không được public. Không sửa tên hoặc di chuyển lẻ
các tệp UUID. Nếu chuyển source sang thư mục khác, chép cả `data/` đi cùng khi server đã dừng.
Không đưa data cá nhân, venv, node_modules hoặc kết quả runtime vào Git/gói nộp.

## Khi không mở được hoặc không xuất được

| Hiện tượng | Cách xử lý |
|---|---|
| `python`, `node`, `npm` không tìm thấy/sai bản | Kiểm tra PATH và phiên bản ở phần cài đặt; `npm.cmd` tránh phụ thuộc execution policy của npm.ps1. |
| `No module named app` hoặc thiếu package | Trở về root, dùng đúng Python trong `backend/.venv` và `--app-dir backend`; chạy bước cài/pip check. |
| `[WinError 10048]` / address already in use | Dừng server của chính bạn bằng Ctrl+C hoặc dùng cổng 8002; không mở hai backend cùng DB. |
| Health hoạt động nhưng giao diện 404 | Chạy `npm.cmd --prefix frontend run build`; kiểm tra có `frontend/dist/index.html`, sau đó reload. |
| Trình duyệt không kết nối được | Kiểm tra terminal Uvicorn còn chạy và URL đúng cổng; đọc lỗi startup thay vì xóa data để thử lại. |
| Ảnh bị từ chối | Chỉ JPEG/PNG tĩnh, tối đa 15 MiB và 16 triệu pixel, tối đa 20 trang/tài liệu. Đổi ảnh hoặc giảm kích thước trước khi nhập. |
| Đề xuất nhận diện lệch/không có vùng | Chỉnh bốn góc bằng tay rồi xác nhận; score là heuristic, không phải độ chính xác. |
| Không xuất được, có trang chưa xác nhận/nháp | Mở từng trang được chọn xuất, kiểm vùng, xác nhận và lưu; xử lý nháp trước khi xuất lại. |
| Tham số Adaptive bị từ chối | Chọn block lẻ nhỏ hơn hoặc Otsu; block không được lớn hơn cạnh ngắn vùng warp. |
| Revision conflict, busy hoặc mạng mất lúc lưu/xuất | Chờ thao tác kết thúc, đọc lại tài liệu/cấu hình, kiểm tra rồi chủ động thử lại; không gửi liên tiếp POST hoặc dùng hai tab cùng sửa một trang. |
| DB/schema/tệp lưu trữ lỗi | Giữ nguyên data, lưu thông báo/log và kiểm tra đúng bản source; chưa có công cụ sửa/migrate schema tự động. |
| `FileNotFoundError` lúc tạo artifact/temp dù thư mục tồn tại | Kiểm tra độ dài đường dẫn trên Windows. Giải nén vào thư mục ngắn; với tests, dùng TEMP/basetemp ngắn ở hướng dẫn dưới. Không xóa DB hoặc tắt kiểm tra storage. |

Nếu môi trường tự động hóa không có quyền ghi Temp, đặt Temp cho phiên PowerShell đó rồi thử lại:

```powershell
$scannerTempDirectory = Join-Path (Get-Location).Path '.tmp'
New-Item -ItemType Directory -Path $scannerTempDirectory -Force | Out-Null
$env:TEMP = $scannerTempDirectory
$env:TMP = $scannerTempDirectory
```

Nếu source đang nằm rất sâu, hãy chọn một thư mục tạm **mới, đường dẫn ngắn** thay vì tiếp tục
lồng trong project. Pytest có thể xóa nội dung basetemp, nên không dùng thư mục chứa dữ liệu cần giữ.
Ví dụ đã kiểm chứng trên máy này, chạy từ root source giải nén nhưng đặt basetemp ngoài cây lồng sâu:

```powershell
$scannerTestDirectory = 'C:\Users\03201\OneDrive\Desktop\XU_LY_ANH\.tmp\pytest-moi'
& .\backend\.venv\Scripts\python.exe -m pytest -c backend/pyproject.toml backend/tests experiments/tests -q -W error --basetemp $scannerTestDirectory
```

Thay đường dẫn bằng thư mục thử mới phù hợp máy bạn. Lượt kiểm gói nộp giữ lại lỗi đường dẫn262ký tự
và đã chạy đủ1.279tests với basetemp ngắn; không sửa thuật toán/storage hoặc bỏ test để vượt lỗi.

## Giới hạn và kiến trúc

Ứng dụng dành cho **localhost trên máy cá nhân**, chưa có tài khoản, phân quyền nhiều người dùng
hoặc cấu hình phục vụ Internet. Giữ host `127.0.0.1`, **một Uvicorn process**; không dùng nhiều workers
hoặc `--reload` trong bản chạy đóng gói. Hàng đợi có một tác vụ xử lý và tối đa hai tác vụ chờ.

Luồng ảnh: chuẩn hóa EXIF/alpha → tìm biên/contour và chấm điểm vùng → người dùng xác nhận góc →
homography từ nguồn đầy đủ → lọc/mode/threshold/xoay → render/preview → xuất.
EXIF chỉ áp metadata hướng của máy ảnh, không tự đọc chiều chữ. Homography dành cho mặt giấy gần phẳng;
không làm phẳng nhàu nặng, khôi phục chữ bị che/cháy sáng hoặc OCR. PDF gồm ảnh, chưa có lớp chữ tìm kiếm.
Detector vẫn có thể chọn nền bàn; BW có thể giữ ô ly hoặc làm đứt nét, Otsu có thể làm đen vùng bóng.

`backend/app/processing/` độc lập HTTP/DB/UI; API/service xử lý revision/lưu bền,
`storage/` quản lý SQLite/artifact, `frontend/src/` quản lý giao diện. Preview lấy từ full render,
xuất dùng đúng bản quét/config/revision đã lưu. [Hợp đồng ảnh](docs/image-contract.md),
[API](docs/api-contract.md), [bản đồ thư mục](docs/project-map.md), [hướng thuật toán](docs/Phan_Tich_Huong_Thuat_Toan_Tu_Tai_Lieu.md).

## Dành cho phát triển và kiểm chứng

Sau bước cài, chạy từ root:

```powershell
& .\backend\.venv\Scripts\python.exe -m pytest -c backend/pyproject.toml backend/tests experiments/tests -q -W error
npm.cmd --prefix frontend test
npm.cmd --prefix frontend run typecheck
```

Kiểm lại từ ZIP giải nén sạch ở14.08: **1.279 backend/experiments tests** đạt144,66s,
frontend **103 tests**, typecheck/build đạt. Xem [checklist gói nộp](docs/submission-checklist.md)
và [audit8task](docs/audit-phase-14.md) cho phạm vi kiểm, lỗi đường dẫn và bằng chứng browser/PDF/restart.
Trong sandbox tự động hóa TestClient có thể cần quyền IPC/tệp tạm; PowerShell thông thường không cần đổi code.

Để sửa React với Vite, giữ backend8000 chạy rồi mở terminal thứ hai ở root:

```powershell
npm.cmd --prefix frontend run dev
```

Vite tại [5173](http://127.0.0.1:5173/) proxy `/api` sang8000; giao diện build vẫn dùng8000.
Vite đặt strictPort: nếu5173 bận, dùng instance hiện có hoặc dừng instance của bạn trước khi mở lại.

CLI ảnh offline và metadata: [mốc M1](docs/milestone-m1.md), [ghi chú thuật toán](docs/algorithm-notes.md).
Dataset/nhãn: [quy ước](docs/dataset.md), [manifest](experiments/dataset_manifest.csv).
Thực nghiệm13 giữ snapshot/runner/hash lịch sử; bản đóng gói có hash riêng, cổng freeze13 sẽ từ chối mã đóng gói.
Không ghi đè frozen để chạy lại hoặc tune tập test đã thấy. [Môi trường](docs/experiment-environment.md),
[phương pháp đo](docs/benchmark-method.md), [kết quả và giới hạn](docs/results.md).

## Tiến độ và phạm vi

MVP01.01–07, 02–11 và 13–14 xong: **102 task chính, 13 AUX**; MVP01.08 bỏ qua. M4 kỹ thuật đạt26/10/2026: bản chạy cùngorigin localhost8000, sourceZIP/manifest/checksum, cài sạch đúnglock/1.279backend-experiments+103frontendtests/typecheck/build, README/hướng dẫn/báo cáo sốliệu thật vàdemo5–7phút đãkiểm. RehearsalUI sau nhập5phút21giây, PDF3trang/restart65artifact đạt; chưa có lượt tập nói hoặc thủ tục nộp hành chính. Đã rà đủ8task14/AUX14.01; giữlõiảnh/preset/lock/manifest/nhãn/frozen13, chỉ sửa một dòng chú thích dataset trênUI. Giai đoạn12 còn7task chưa nghiệmthu và5optional chưa làm; không tựtích theo cổng hồi quy trước khóa. Giữ ca sai development và giới hạn mỗi split một tài liệu.
[Kế hoạch](tasks/plan.md), [checklist tiến độ duy nhất](tasks/todo.md),
[phạm vi MVP](docs/MVP_Pham_Vi_Va_Ke_Hoach_4_Tuan.md), [đặc tả gốc](Document_Scanner_Dac_Ta_Kien_Truc_Thuat_Toan.md).
