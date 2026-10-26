# Hồi quy phục vụ khóa cấu hình 13.06 — 26/10/2026

Người dùng cho phép chạy hồi quy cần thiết trước khi khóa; đây không phải nghiệm thu toàn bộ giai đoạn 12. Checklist 12 giữ nguyên. Không thay implementation ứng dụng để đạt các kiểm chứng này.

| Phạm vi | Bằng chứng thực hiện | Kết quả |
|---|---|---|
| Geometry, EXIF/alpha/import/quota, revision/CAS, worker, storage, reopen, export/error paths | `pytest -c backend/pyproject.toml backend/tests experiments/tests -q --tb=short -W error --basetemp=.tmp/pytest13-05-06-full` | 1.255 passed, 203,28 s; không skip |
| Frontend logic/race/callback/export flow | `npm.cmd test` từ frontend | 103 passed, 0 fail/skip, 521,4369 ms |
| TypeScript và bundle | `npm.cmd run build` từ frontend | typecheck đạt, 41 modules, Vite 631 ms |
| Browser nhập nhiều ảnh và lỗi riêng từng tệp | QA riêng: page1.png → fake.jpg → page2.png qua file chooser | 2 trang/2 lượt tự nhận diện; lỗi 415 ở giữa không làm mất trang |
| Xác nhận, render, cấu hình nhiều trang | Trang 1 Color, trang 2 BW Otsu, người kiểm chủ động xác nhận | r1/confirmed; không tự xác nhận lúc nhập |
| Xuất có trang thiếu render | Browser chọn cả hai trang, tạo PDF | 409 PAGE_NOT_RENDERED → render đúng trang thiếu → 201; tải thật |
| Đúng full và thứ tự PDF | Đọc bằng pypdf, render Poppler, xem đủ hai trang | 2 ảnh nhúng bằng full từng pixel; tải browser bằng byte API; PAGE 1/2 đúng thứ tự |
| Lưu bền qua tiến trình mới | Graceful stop/start backend cùng SQLite rồi reload UI | document/export bằng snapshot; 38 artifact hash giữ; hai full bằng core chạy mới |
| Mở lại UI | Sau restart xem BW trang 2 ở 100% | GET phục hồi, không POST/PUT xử lý lại; console error/warn rỗng |
| Route/error/data exposure | 5 GET: đường data, route sai prefix, UUID sai, session và artifact không tồn tại | đều 404, không lộ đường dẫn/tên người dùng/trace; OpenAPI 12 paths |
| Giữ dữ liệu cũ | So hàng SQL trước/sau và hash file artifact cũ | 61 hàng cũ và 49 artifact nguyên, FK check rỗng |
| Cách ly dữ liệu test | Evaluator development-only và capture snapshot không đọc ảnh test | 0 ảnh test chạy detector/enhancement hoặc tune |
| Khóa tái lập | `freeze_config.py --check` ở tiến trình mới | snapshot khớp 91 source files/config/dependencies/environment |

Bằng chứng ignored: `experiments/results/mvp13-05-06-verified/` gồm pytest/frontend logs, regression-proof.json, runtime-before.json, restart.json, pdf-checks.json, qa-export.pdf, hai raster PDF, browser-reopen.png và các ảnh enhancement. Snapshot public ở [frozen.json](../experiments/configs/frozen.json), giải thích ở [môi trường thực nghiệm](experiment-environment.md).

Đây là smoke và hồi quy chức năng, không phải benchmark tải, chứng nhận an toàn nhiều người dùng hoặc kiểm chứng toàn bộ lỗi phần cứng/mất điện. Không đo p50/p95/RAM ở lượt này. Các ca lỗi/concurrency được bao phủ bằng tests với môi trường cô lập; không gọi fault injection trong tests là lỗi đã tái hiện trên browser sản phẩm.
