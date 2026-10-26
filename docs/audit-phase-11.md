# Rà soát tám task giai đoạn 11 — AUX11.01

Ngày 18/10/2026. Thực hiện MVP11.08 và rà đủ tám task theo yêu cầu. Đối chiếu [MVP](MVP_Pham_Vi_Va_Ke_Hoach_4_Tuan.md), [kế hoạch](../tasks/plan.md), [checklist](../tasks/todo.md), [API](api-contract.md), [ảnh/revision](image-contract.md), [snapshot/lease](export-snapshot.md), [encoder/A4](export-encoding.md), [luồng xuất](export-workflow.md) và [smoke](../frontend/tests/scanner-smoke.md).

## Kết luận

**MVP11.01–08, checkpoint 11-C1/C2 và cổng 11/M3 đạt trong phạm vi MVP cục bộ.** Xuất PNG/JPG/PDF dùng đúng full render, revision và thứ tự đã yêu cầu. Các thao tác trên tài liệu đang xuất bị từ chối rõ ràng; khóa được giải phóng sau thành công, lỗi và theo vòng đời executor.

**86 task chính + 11 AUX** hoàn thành; giữ 110 ID gốc/109 active/1 skip và năm task tùy chọn riêng. Tiếp theo là MVP12.01: củng cố ca lỗi nhập ảnh trong ứng dụng hoàn chỉnh.

Lượt này chỉ thêm năm kiểm thử tích hợp, thực nghiệm và tài liệu. Không sửa logic sản phẩm, thuật toán ảnh, dependency hoặc schema. OpenAPI vẫn 12 path/15 method, SQLite schema3; core/CLI khớp mốc M1.

## Ma trận nghiệm thu

| Task | Triển khai và bằng chứng | Kết luận |
|---|---|---|
| 11.01 — Request | Request/receipt frozen, ordered subset, strict UUID/revision, kiểm trùng ID/quota/options. 19 schema tests; membership/exact revision tại service. PDF1–20 trang, PNG/JPG một trang; options inactive vẫn validate | Đạt |
| 11.02 — Snapshot/khóa | Frozen snapshot, confirmed quad/exact revision/source/run/full-preview binding, kiểm hash ngoài transaction. Reserve trước enqueue, lease giữ đến worker finally. Có tests queued/active cancel, 429, exception. Actual POST qua barrier: tám mutation và export thứ hai cùng tài liệu đều409; GET/health/tài liệu khác dùng được | Đạt |
| 11.03 — PNG/JPG | 28 tests kiểm full RGB/L, PNG pixel-exact/nét1 pixel, JPEG95/subsampling0/sạch EXIF-ICC, không preview. Lượt cuối tải Color1119×1599 RGB: PNG MAE0, JPG MAE0.0829946032/255. UUID filename hợp lệ; slug của encoder/client chỉ là gợi ý | Đạt |
| 11.04 — A4 | 23 tests mm→point, auto/square/explicit, margin và fit. Hai PDF ba trang auto/PNG/5mm và portrait/JPEG/30mm đã parse/render/xem; MediaBox/matrix đúng trong sai số<0.001point, không crop/stretch/xoay thêm | Đạt |
| 11.05 — Ghép/lưu | Lặp đúng request order; complete payload→temp/fsync/publish→commit Artifact+ExportRecord. Bảy service tests kiểm ba format và lỗi encode/write/register/commit. DB snapshot đúng [3,1,2]/subsetColor/r1. Lỗi ở PDF trang2 không để file/record dở; xuất sau thành công | Đạt |
| 11.06 — API/executor | POST201 qua shared executor một active/hai waiting và lease; artifact GET đúng MIME/nosniff/private-no-store. 16 API tests gồm11 cũ+5 mới. Lúc giữ POST trước writer chưa có file/ExportRecord; receipt chỉ trả sau commit. Success/busy/429/error/missing/stale/foreign/lifecycle đủ bằng chứng | Đạt |
| 11.07 — UI | Chọn subset/order/options/download; dirty selected/chưa confirmed bị chặn, không PUT/auto-confirm. Chỉ valid409 missing mới render thiếu và thử POST lại một lần. Tám frontend tests mới giữ trong suite95. Evidence05–07 kiểm missing/dirty unselected/download ba format; lượt cuối tải bốn tệp, pending khóa mutation UI, console sạch | Đạt |
| 11.08 — Nghiệm thu cuối | QA ba nguồn PAGE1/2/3, Color0°/Gray90°/BWOtsu270°/r1, UI order[3,1,2]. Hai PDF/sáu trang đọc/render/xem và so full/order/options. Physical restart giữ SessionDetail/bốn ExportRecord/30 hash. UI mở ba full chỉ GET, không render lại; export mới sau restart thành công. Dữ liệu cũ nguyên | Đạt |

## Kiểm thử

Backend chạy:

    backend/.venv/Scripts/python.exe -m pytest -c backend/pyproject.toml backend/tests -q --tb=short -W error --basetemp=.tmp/pytest11-phase-final

Kết quả **1.199 passed trong 217.02 giây**. Frontend npm.cmd test: **95 passed/297.0281ms**; npm.cmd run build gồm typecheck đạt,39modules/173ms, JS298.11kB/gzip92.09, CSS12.88kB/gzip3.22. Không skip, suppress warning hoặc nới điều kiện thuật toán.

Năm test mới trong test_export_api.py kiểm hai outcome thành công/lỗi giữa PDF và ba định dạng qua hai app lifespans liên tiếp. Export cũ giữ nguyên snapshot/bytes dù cấu hình sau đó lên revision2; render/export mới dùng revision2.

Lần đầu có15 passed/1 failed trong12.22s vì helper files chứa cả scanner.sqlite3. Test cố ý đổi tên tài liệu khác để chứng minh không khóa toàn hệ thống; thao tác được phép đó làm đổi bytes DB. Đã sửa oracle bằng baseline chính xác sau rename, vẫn giữ kiểm owner JSON/files/record counts và trạng thái trước rename. Focus sau sửa:16 passed/13.31s. Đây là lỗi kỳ vọng của test, không phải lỗi runtime; không sửa app để chiều test.

Giai đoạn11 bổ sung128 backend tests từ baseline1.071 và tám frontend tests từ87. Không phá implementation để tạo RED giả khi mục đích là thêm nghiệm thu cho hành vi đã có.

## PDF, ảnh và restart

Tài liệu QA riêng gồm ba ảnh1120×1600 in PAGE1/2/3, ô màu và nét chữ. Dùng full quad/denoiseNone, Color0°, Gray90°, BWOtsu270°, revision1. Full Color1119×1599, Gray/BW1599×1119. UI đưa trang3 lên hai lần thành [3,1,2], không tăng page revision.

Đã bấm Tải trên UI cho bốn file: PDF auto/PNG nhúng/lề5mm, PNG Color, JPG Color và PDF portrait/JPEG nhúng/lề30mm. Tệp trong Downloads được copy sang evidence ignored; SHA khớp artifact GET. Bốn ExportRecord đầu lưu đúng page/revision/order. Filename tải là UUID server có extension tương ứng.

Pypdf kiểm hai PDF, Poppler72dpi render đủ sáu trang và đã xem contact sheet. Ba image XObject trong PDF/PNG trùng full từng pixel. Ba image trong PDF/JPEG giữ đúng dimensions/mode, MAE theo thứ tự0.0668804956/0.0988432411/0.0780307844 trên0..255. MediaBox/draw matrix đúng options, giữ đủ khung/mép/chữ. Hướng chữ theo rotation explicit, không tự suy ra hướng đọc.

PNG Color1119×1599 RGB trùng full từng pixel; JPG cùng dimensions/mode, MAE0.0829946032/255. Cả hai sạch EXIF/ICC. MAE chỉ mô tả nén mất dữ liệu trên ảnh QA, không phải accuracy thuật toán scan.

Đã graceful stop backend cũ rồi mở tiến trình mới trên cùng SQLite: stopfile chuyển từ phase11-05-07.stop sang phase11-final.stop. SessionDetail bằng JSON trước restart, bốn ExportRecord bằng từng trường,30 artifact SHA giữ nguyên, FK check rỗng. UI reload và chọn cả ba trang hiện full r1 đúng dimensions. Log mở lại chỉ GET, không POST render/detect. Một POST export mới sau đó trả201, chứng minh không giữ khóa cũ.

Đọc DOM trong lượt xuất thật sau restart ghi nhận working=true và rename/delete/order/full-image/render/upload đều disabled. Sau khi xong, Tạo tệp xuất/Tải dùng được. Không có harness/fetch mock/route QA trong sản phẩm. Bố cục320/768/1440 không tràn; viewport đã reset và console không warning/error.

Evidence cục bộ ignored tại experiments/results/mvp11-final-verified/: product-before/after/SQLite backup/product-verification; qa-document/runtime-checks/restart-checks/browser-checks/ui-image-bindings/qa.json; bốn tệp tải/full PNG/sáu PDF raster/pdf-inspection/contact-sheet/product-view. Scripts tái lập trong .tmp/: seed11_final.py, verify11_final_runtime.py, inspect11_final_pdf.py, verify11_final_product.py và qa11_final.py. Parser/Poppler dùng bundled runtime; không thêm dependency runtime.

## Bảo toàn và rà mã

Giữ nguyên **15 tài liệu/52 trang/156 hash nguồn** có trước lượt nghiệm thu và mọi row cũ:15sessions/52pages/575artifacts/52configs/7exports/25DetectionRuns/16RenderRuns/schema_version. QA mới có ba trang, bốn exports trước restart và một PDF sau restart. Không sửa/xóa tài liệu cũ; hash core/CLI/requirements vẫn khớp M1.

Đã rà schemas/exports, services/exports/session_guards, API/errors/artifacts, export/images/pdf và ExportPanel/exportFlow/ScannerPage/SourcePreview theo correctness/readability/architecture/security/performance. Validation/owner/exact revision giữ boundary; file lấy từ DB/UUID, không nhận path client. Vòng lặp tối đa20 trang, CPU ngoài transaction. Cleanup chỉ xóa output mới đã chứng minh không reference. Không thêm abstraction/dependency/migration/cached pixels hoặc lọc/warp trong export. Không còn phát hiện chặn M3.

## Giới hạn và bước tiếp theo

- Lease dùng bộ nhớ của một process/một Engine cho DB cục bộ; không áp dụng cho nhiều Uvicorn workers hoặc hai backend cùng DB. File bị sửa/xóa từ ngoài ứng dụng sẽ được verify báo lỗi.
- SQLite/filesystem không có transaction chung. Publish trước DB commit; cleanup best effort. Crash/I/O có thể để orphan, chưa có GC bền.
- Chưa có idempotency key/UI lịch sử export. Mất response sau commit có thể đã lưu tệp; app không tự retry POST. Chủ động xuất lại sẽ tạo record mới.
- PDF là ảnh, chưa OCR/tìm chữ. JPG nén mất dữ liệu. A4 auto dựa trên dimensions full sau rotation, không tự xoay đúng hướng chữ. Tên gợi ý slug chưa được server ưu tiên.
- Dataset vẫn sáu ảnh development/cùng tờ doc_01, test0. Nợ detector img_004/006 có thể chọn cả bàn; dùng chỉnh góc tay. M3 xác nhận luồng MVP, không chứng nhận accuracy/tổng quát hoặc khả năng làm phẳng nhàu nặng.

Tiếp MVP12.01. Giai đoạn12 còn củng cố EXIF/alpha/quota/concurrency/lỗi lưu trữ trong ứng dụng hoàn chỉnh. Backend8000/Vite5173 giữ chạy, stopfile .tmp/phase11-final.stop. Không commit/push/deploy hoặc gửi ảnh/DB ra ngoài.
