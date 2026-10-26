# Bản đồ dự án Document Scanner

Workspace hiện tại là gốc repository; không tạo thêm một thư mục dự án lồng bên trong.

| Vùng | Vai trò hiện tại và dự kiến |
|---|---|
| `backend/` | FastAPI/processing/schemas/SQLite/ArtifactStore/imports/executor/page_config/renders; API tài liệu/renamePATCH/orderPUT/page-sessionDELETE/upload/artifactGET/configCAS/render đã có. Sharedworker1/haiwaiting, confirmed/revision gate; detection service/source loader/DetectionRun đã có; RenderRun/schema3/renderdebug/histogram/debugGET đã có; UIviewer đã có; schemas/exports vàservices/exports/session_guards đã córequest/snapshot/lease, export/images.py vàpdf.py đã cóPNG-JPG/PDFonepageA4;services/publish_export vàPOSTexports đãghiArtifact-ExportRecord;ExportPanel chọntrang/options/tải thật; .venv chỉlocal |
| `frontend/` | React/TS/Vite create/list/rename/upload-batch/order/delete/reopen full-debug, CornerEditor/quadpreflight/full draft/persisted/CAS/confirm/render; ComparisonView nguồn/fullPNG/fit100–200%/native scroll/returnedit/stale labels.102native Node tests/typecheck/build/browser đạt; UI nhận diện và FilterPanel mode/filter/CLAHE/threshold đã có; PipelineViewer/HistogramView/CandidateMetrics và giải thích stage đã có |
| `experiments/` | create_fixtures.py, normalize_one.py, geometry_demo.py, enhancement_demo.py, compare_detection.py, detect_batch.py, detection_artifacts.py, scan_one.py, dataset_manifest.csv và validate_dataset.py; demos/so mode/baseline-revised,6ảnh development vàanhtestnew chưaidentity trong results/data ignored; đánh giácuối/nhãn còn chờ |
| `fixtures/` | 22 tệp tổng hợp nhỏ và manifest với hash/kết quả mong đợi; có thể theo dõi trong Git; không dùng để đo accuracy |
| `docs/` | Phạm vi, bản đồ, quyết định, tiến độ, thực nghiệm và báo cáo |
| `tasks/` | `plan.md` ghi thứ tự/mốc; `todo.md` là checklist tiến độ duy nhất |
| `data/` | Backend khởi động tạo/kiểm scanner.sqlite3; artifact dưới sessions/{UUID}/sources,renders,debug,exports; không public, được ignore |
| `datasets/` | Tùy chọn cho ảnh thu thập cục bộ; được ignore |
| `.tmp/` | Tệp tạm cục bộ phục vụ dựng môi trường khi sandbox không cho ghi Temp hệ thống; được ignore |
| `AGENTS.md` | Quy tắc sử dụng skill, phạm vi và kiểm chứng |

Hai tài liệu gốc giữ tại root; [phạm vi MVP](MVP_Pham_Vi_Va_Ke_Hoach_4_Tuan.md) là nguồn các điều chỉnh đã được chấp nhận. Tệp `.gitkeep` chỉ giúp giữ các thư mục chưa có nội dung trong Git; không biểu thị chức năng đã được triển khai.

Luồng thành phần dự kiến: React → FastAPI → service → processing/storage/export. Thuật toán làm việc với ảnh/config; metadata vào SQLite; ảnh/PDF lưu tệp trên đĩa.

Trạng thái 26/10: MVP01.01–07, 02–11 và 13–14 xong: **102 task chính, 13 AUX**; MVP01.08 bỏ qua. M4 kỹ thuật đạt26/10/2026: bản chạy cùngorigin localhost8000, sourceZIP/manifest/checksum, cài sạch đúnglock/1.279backend-experiments+103frontendtests/typecheck/build, README/hướng dẫn/báo cáo sốliệu thật vàdemo5–7phút đãkiểm. RehearsalUI sau nhập5phút21giây, PDF3trang/restart65artifact đạt; chưa có lượt tập nói hoặc thủ tục nộp hành chính. Đã rà đủ8task14/AUX14.01; giữlõiảnh/preset/lock/manifest/nhãn/frozen13, chỉ sửa một dòng chú thích dataset trênUI. Giai đoạn12 còn7task chưa nghiệmthu và5optional chưa làm; không tựtích theo cổng hồi quy trước khóa. Giữ ca sai development và giới hạn mỗi split một tài liệu. API/schema3/core/dependencies giữ nguyên;14.08 chỉ sửa chú thích datasetUI và bổ sung gói nộp. Xem [cấu hình bản chạy](local-runtime.md). [Kết quả](results.md), [audit13](audit-phase-13.md), [bản khóa](experiment-environment.md), [phương pháp đo](benchmark-method.md).

[image-contract.md](image-contract.md) là quy ước chung cho ảnh/EXIF, normalized/canvas, preset, xác nhận và revision; đọc trước các task normalize/geometry/config/API/UI. Tài liệu không thay cho implementation hoặc bằng chứng kiểm thử.


[Nhập tự nhận diện](auto-detect-on-import.md): importDetection/detectionProposal dùng chung gate, uploadBatch/UploadPanel chạy tuần tự; pageRenderState phục hồi proposal mới vào nháp, PageList ghi trạng thái chờ kiểm tra. Không tự confirmed hoặc đổi backend.
