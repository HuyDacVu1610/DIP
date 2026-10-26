# Mở gói nộp Document Scanner MVP

Giải nén ZIP vào một thư mục mới, mở PowerShell tại thư mục `DocumentScanner` chứa README.
Làm theo [README](README.md) để tạo venv, cài dependency, build và chạy một process tại localhost.
Python 3.12.10 x64 và Node 24.15.0/npm 11.12.1 là môi trường đã kiểm chứng; cần mạng khi cài dependency.
Gói là source, không có Python/Node/venv/node_modules/dist; sau build chỉ cần Python để phục vụ UI/API.

- [Hướng dẫn sử dụng](docs/user-guide.md), [báo cáo](docs/report.md).
- [Kịch bản demo](docs/demo-script.md), [câu hỏi bảo vệ](docs/defense-questions.md).
- [Checklist gói nộp](docs/submission-checklist.md), [rà 8 task](docs/audit-phase-14.md).
- [Mẫu tự thử](fixtures/demo/README.md): sạch, bóng, không biên, highlight và vệt nếp gấp mô phỏng.

`SUBMISSION-MANIFEST.json` trong ZIP liệt kê SHA-256/kích thước từng tệp (trừ chính manifest).
Kiểm manifest trước khi cài; các thư mục phát sinh khi chạy/test nằm ngoài nội dung ZIP ban đầu.
Mỗi lần đóng gói dùng tên ZIP mới, không ghi đè gói cũ.

Gói giữ source/test, lockfile, tài liệu, ảnh tổng hợp, bốn hình báo cáo và các CSV/summary cần đối chiếu
số liệu giai đoạn 13. Giữ nguyên manifest/annotations/frozen lịch sử để truy vết hash.
Không có ảnh chụp cá nhân, DB, log runtime, bí mật, PDF giáo trình/slide của môn học hoặc bản quét thật.
Các đường dẫn ảnh thật, evidence lịch sử và PDF môn học trong tài liệu tham khảo là **tùy chọn cục bộ**,
không phải thành phần có trong gói. Vì thiếu ảnh riêng và bản freeze khác mã đóng gói, gói không tái chạy
benchmark test giai đoạn 13; không sửa/ghi đè frozen để vượt cổng này. Chạy ứng dụng, demo và các tests
tổng hợp được kiểm chứng độc lập. Báo cáo nêu rõ mỗi split chỉ có một tài liệu.

Ứng dụng chỉ dành cho máy cá nhân ở `127.0.0.1`, một worker Uvicorn. Không public lên Internet.
Chưa có OCR, làm phẳng giấy nhàu nặng, migration/GC sau crash hoặc bản cài offline tự chứa runtime.
Mẫu tổng hợp không chứng minh chất lượng trên mọi tài liệu thật. Chưa có yêu cầu định dạng nộp riêng
từ giảng viên; nếu cần DOCX/PDF, bìa, tên nhóm hoặc mã sinh viên thì bổ sung trước khi nộp chính thức.
