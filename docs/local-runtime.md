# Bản chạy cục bộ và dependency đã khóa

MVP14.01–14.02, bản đóng gói `mvp14-local-v1`, Windows x64, 26/10/2026.
Cấu hình dựng/chạy đã kiểm chứng. [README cài/chạy](../README.md) và [hướng dẫn sử dụng](user-guide.md) đã hoàn thành ở MVP14.03–04.

## Môi trường và file khóa

| Thành phần | Bản đã kiểm chứng | Nguồn khóa |
|---|---|---|
| CPython 64-bit | 3.12.10 | Interpreter tạo venv, không dùng system-site-packages |
| Node.js / npm | 24.15.0 / 11.12.1 | Công cụ dựng; dependency JS lấy từ project |
| Backend | 30 package runtime/test và dependency gián tiếp pin `==` | [requirements.txt](../backend/requirements.txt) |
| Frontend | React 19.3.0, Vite 8.3.4, TypeScript 7.0.2 và dependency gián tiếp | [package.json](../frontend/package.json), [package-lock.json](../frontend/package-lock.json) |

Giữ nguyên hai file khóa của bản thực nghiệm, không nâng package:

- `backend/requirements.txt`: SHA-256 `4be3ab6d12678812a1857c5b24d568bd3d8fccf2e32820246e39580191cfa67a`.
- `frontend/package-lock.json`: SHA-256 `a32bab86fe19ebd0a1f69071687a0a6a01714f3439a1e22fe164cc4c3428395f`.

PowerShell từ root, dùng Python/Node đúng các bản trên. Cài package vào venv riêng;
`npm ci` dựng lại node_modules theo lockfile. Python/Node là điều kiện cài sẵn,
không cần package Python, Vite hoặc TypeScript cài toàn máy.

```powershell
python -m venv backend/.venv
& .\backend\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt
& .\backend\.venv\Scripts\python.exe -m pip check
npm.cmd --prefix frontend ci
npm.cmd --prefix frontend run build
& .\backend\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --workers 1
```

Mở [ứng dụng](http://127.0.0.1:8000/) và [health](http://127.0.0.1:8000/api/v1/health).
Sau khi build, chỉ cần Python để chạy app; Vite dev server và Node không nằm trong luồng phục vụ.
Đổi source React cần build lại, rồi tải lại trang. Dừng backend bằng Ctrl+C trong terminal chạy nó.
Không thêm `--reload` hoặc nhiều workers: khóa xuất và hàng đợi hiện nằm trong một tiến trình.

## Đường dẫn và quota

[settings.py](../backend/app/settings.py) tính đường dẫn từ vị trí source, không phụ thuộc thư mục khởi chạy:

| Cấu hình | Giá trị |
|---|---|
| UI đã build | `frontend/dist/`, chỉ phục vụ `index.html` và tệp trong `assets/` |
| DB / artifact | `data/scanner.sqlite3` / thư mục do ArtifactStore quản lý dưới `data/` |
| Upload | JPEG/PNG, tối đa 15 MiB bytes gốc và 16.000.000 pixel |
| Số trang | 20 trang/tài liệu |
| Tải xử lý | 1 Uvicorn process, 1 image worker, tối đa 2 tác vụ chờ |
| Địa chỉ | `127.0.0.1:8000`, API `/api/v1` |

Không áp quota 15 MiB lên PNG chuẩn hóa nội bộ. Không xóa `data/` khi cập nhật hoặc khởi động lại.
Đường dẫn runtime là cấu hình source hiện hành; chưa thêm biến môi trường hoặc UI chỉnh quota.

## Static và fallback

[web.py](../backend/app/web.py) dùng `StaticFiles` của Starlette với kiểm tra realpath,
không theo symlink ra ngoài thư mục build. `index.html` có `Cache-Control: no-cache`,
phản hồi static có `nosniff`. Navigation GET/HEAD dạng HTML tới đường dẫn không có phần mở rộng
được trả entry point; URL query session/page vẫn mở lại dữ liệu đã lưu.

Fallback chỉ xử lý routing 404, giữ thứ tự route API và lỗi 405/Allow. `/api`, `/data`,
đường dẫn source/tài liệu nội bộ, dot-path và asset thiếu không nhận HTML thay lỗi.
Artifact tiếp tục qua endpoint UUID/metadata/hash; không mount project hoặc thư mục data.
Không có build thì backend/API vẫn chạy, UI trả 404; build trước khi mở giao diện.
`create_app(database_path, frontend_dir=None)` hỗ trợ chạy API riêng trong kiểm chứng.

## Định danh và bằng chứng

Snapshot [giai đoạn 13](experiment-environment.md) vẫn giữ SHA-256
`ce89a90e2fb9ca092350886276201f87e81cd09c90e6507f799fceca6a8d8109`.
Trong 91 source đã khóa, chỉ `main.py` và `settings.py` đổi, thêm `web.py`.
Toàn bộ processing, presets, dependency, manifest và annotations giữ hash.
Cổng freeze cũ phải báo khác phiên bản khi chạy trên bản đóng gói này; không ghi đè snapshot để làm xanh.

Hai HTTP integration test tổng hợp tạo snapshot tạm của mã hiện tại và truyền tường minh
vào `isolated_server`; child vẫn kiểm đầy đủ snapshot, có test từ chối drift.
CLI benchmark test thật vẫn mặc định bắt buộc snapshot 13 ban đầu và sẽ từ chối mã đóng gói.
Runner mới có hash riêng trong manifest; số liệu báo cáo 13 vẫn gắn runner v1.1 và hash cũ.

Bằng chứng cục bộ, ignored: `experiments/results/mvp14-01-02-verified/` chứa
`packaging-manifest.json`, runtime trước/sau restart, ảnh browser, PDF tổng hợp và bản lưu
91 source/10 input/runner cũ với từng hash khớp snapshot. Không đo lại hay tune tập test.
Xem [nhật ký](progress.md) để biết lệnh, số kiểm thử và giới hạn nghiệm thu.

## Gói nộp được kiểm ở14.07–08

`mvp14-submission-v1` giữ API/schema3/core/preset/dependencies của bản chạy này;
chỉ thêm một sửa nội dungUI: bỏ dòng “test0” đã cũ, nêu đúng giới hạn mỗi split một tài liệu.
Giữ nguyên manifest `mvp14-local-v1` và frozen13 để truy vết, không coi mã đóng gói là cùng bản đo13.
Gói có manifestSHA riêng; [checklist](submission-checklist.md), [bằng chứng](submission-verification.json)
và [audit14](audit-phase-14.md) ghi cleanrun1279/103tests, PDF3trang/restart65artifact.
README có cách tránh lỗi đườngdẫn quá dài trênWindows; runtime vẫn mộtprocess/localhost.
