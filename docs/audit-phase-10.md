# Rà soát bảy task giai đoạn 10 — AUX10.01

Ngày 18/10/2026. Theo yêu cầu làm MVP10.03–07 rồi rà lại kết quả cả giai đoạn. Đối chiếu [MVP](MVP_Pham_Vi_Va_Ke_Hoach_4_Tuan.md), [kế hoạch](../tasks/plan.md), [checklist](../tasks/todo.md), [API](api-contract.md), [hợp đồng ảnh](image-contract.md), [progress](progress.md) và [smoke](../frontend/tests/scanner-smoke.md).

## Kết luận và phạm vi

**Cả bảy task, checkpoint10-C1/C2 và cổng10 đạt.** Có đổi tên, thêm trang, lên/xuống, xóa trang/tài liệu và tự mở lại bản quét/debug đã lưu. Đổi thứ tự không render lại hoặc tăng revision ảnh. Mở lại không tự nhận diện, xác nhận hoặc tạo ảnh mới.

78 task chính +10AUX hoàn thành; giữ110 ID gốc/109active/1skip/5optional. Next **MVP11.01**: xuất ảnh/PDF còn chờ. Schema3/dependency/lõi ảnh không đổi. Dataset vẫn6development/1doc_01/test0 và nợ detector img_004/006; kiểm chứng quản lý tài liệu không phải đo accuracy.

## Ma trận nghiệm thu

| Task | Triển khai và bằng chứng | Kết luận |
|---|---|---|
| 10.01 đổi tên | PATCH strict title trim1..200, metadata-only/no-op, rollback. DocumentTitleForm cập nhật header/list không remount editor. Bằng chứng lượt10.01–02: tên Việt/200ký tự/hủy/lỗi/restart; 11rename tests vẫn nằm trong full suite hiện tại | Đạt |
| 10.02 thêm trang | Sequential batch giữ lock qua GET đối soát; lỗi từng file, quota20, backend413 cuối cùng. Editor chọn theo ID, giữ draft/result khi append. Bằng chứng10.01–02: badJPEG, lost response sau201, quota19→20/21st413, 13UIstates/19requestrecords; tests append-render/quota và batch được chạy lại trong suite hiện tại | Đạt |
| 10.03 API order | PUT đủ toàn bộ page_ids không trùng/thiếu/ngoài phiên; writer gate và hai lượt position tạm/final tránh UNIQUE tức thì. No-op không sửa timestamp; order chỉ session timestamp, không config/revision/run/source. 8tests và3request sai thực đều giữ snapshot; commit lỗi rollback | Đạt |
| 10.04 UI order | PageList nút lên/xuống khóa ở đầu/cuối, gửi cả permutation. Ba ảnh tổng hợp in PAGE1/2/3 được xếp [2,1,3]. Giữ page_id, draftGray/180° chưa lưu và run/full cũ. Mô phỏng500 trước PUT, mất reply sau commit và giữ response rồi chọn trang3: GET đối soát, không retry mutation/không ghi đè lựa chọn mới. Order giữ qua restart | Đạt |
| 10.05 xóa trang | DELETE owner-scoped/204; cascade DB, compact position, sau commit kiểm tệp không còn reference rồi verify/hash/unlink đúng UUID. 7tests kiểm owner/tệp khác/rollback/cleanup failure/live reference; UI mô phỏng xóa không chọn/chọn/cuối giữ lựa chọn hợp lệ. API thật xóa3trang QA/9source files, dữ liệu cũ giữ | Đạt |
| 10.06 xóa tài liệu | DELETE session/204, cascade configs/artifacts/runs, UI modal xác nhận với hủy/Escape và chọn tài liệu còn lại. 4session tests, xóa rỗng/nhiều trang thật trên QA. 5race tests giữ CPU thật qua barrier: render/detect × page/session và import × session; owner gate chặn publish sau xóa | Đạt |
| 10.07 mở lại | PageRead thêm latest_render/latest_detection từ run đã lưu, ràng buộc page/source/hash/dims/revision; GET chỉ metadata. Hook phục hồi persisted draft/render/diagnostic, không áp proposal làm góc. Ba trang Color0°/Gray90°/BWOtsu270° qua physical restart giữ nguyên JSON/debug/17artifact hashes, UI hiện đúng full cũ và histogram. Các request mở lại chỉ GET. Draft chưa lưu được bỏ, không giả persisted | Đạt |

## Bằng chứng và phép đo mới

Evidence cục bộ ignored tại `experiments/results/mvp10-final-verified/`: before/after và SQLite backup, seed, document/debug/hashes trước-sau restart, requests-main/delete-ui-simulated/reopen/status, browser-cases, deletion-api, raster-checks, layout, console, ảnh sản phẩm và bản sao harness. Harness đã gỡ khỏi frontend; không có route QA trong backend.

- 23 trạng thái UI ghi lại. Các DELETE trên browser được **mô phỏng trước fetch**, không tác động DB; không gọi chúng là xóa thật. API xóa thật riêng chỉ nhắm UUID QA mới, loại trừ toàn bộ14ID cũ. Tài liệu QA trạng thái có render cũng được xóa bằng API để kiểm whole-document không rỗng; tài liệu ba trang được giữ cho người dùng xem.
- Color0° full599×799, Gray90°/BWOtsu270° full799×599. Cả3full/preview byte-equal với core chạy mới từ PNG nguồn/config đã lưu, nguồn không đổi. 12hash code/core/CLI/requirements khớp mốc M1. Đổi góc/EXIF/detector/threshold không nằm trong thay đổi này; chọn xoay UI dùng lõi rotation hiện hữu.
- Physical restart giữ nguyên3SessionDetail page payloads/config/run, 3debugJSON và17PNGhash; metadata/title/order cũng nguyên. UI mở lại cả3trang, Color trở về0° thay vì draftGray180° chưa lưu. BW mở debug cùng run,256bin/tổng478.601 trước xoay, Otsuactualt149; không có POST trong8request mở lại ghi được.
- Bảo toàn **14 tài liệu/50 trang/150hash nguồn cũ**, toàn bộ row cũ:14sessions/50pages/537artifacts/50page_configs/24detection_runs/13render_runs/0exports và schema_version; FKcheck rỗng. So DTO cũ bỏ đúng hai trường mới additive latest_render/latest_detection; mọi trường cũ và tất cả row DB nguyên.
- Bố cục320/768/1440: document không tràn ngang; ở320 danh sách trang cuộn ngang như thiết kế hiện hữu, không yêu cầu mọi nút của mọi trang cùng nằm trong viewport. Console sản phẩm không warning/error; viewport reset. PageList nhận metadata persisted sau lưu/render, cập nhật mode/rotation/render revision ngay, không đợi refresh và không remount editor; ca Gray90° đã kiểm riêng.

## Kiểm thử và rà mã

Backend: `backend/.venv/Scripts/python.exe -m pytest -c backend/pyproject.toml backend/tests -q --tb=short -W error --basetemp=.tmp/pytest10-phase-final-green` → **1071passed189.56s**. Frontend: `npm.cmd test` → **87passed380.9416ms**; `npm.cmd run build` gồmtypecheck,37modules262ms, JS290.78kB/gzip90.07, CSS12.20kB/gzip3.07. Không skip/suppress warning hoặc nới điều kiện thuật toán để đạt kiểm thử.

TDD mới28backendtests (8order+7page-delete+4session-delete+5processing races+4reopen) và6frontendtests (wire204/order,2selection/permutation,3history/rotation). RED ban đầu: order404, delete405, reopen thiếu trường. Trong quá trình triển khai sửa lỗi chuyển ref UUID string sang UUID khi query SQLAlchemy; sửa test đọc detached ORM sau commit bằng chụp ID trước. Full suite đầu1066pass/5fail vì assertions trước đây coi SessionDetail không đổi sau tạo run; cập nhật đúng trường latest_detection/latest_render rồi vẫn so toàn payload. Final strict suite xanh; không xóa assertions bảo toàn source/config/revision.

Rà correctness/boundary/security: nguồn file từ DB/StoredArtifact, không nhận path client; không recursive-delete hoặc xóa theo filename. Writer lock chung với finalize/config/import/reorder/delete giữ transaction ngắn, CPU bên ngoài. Dọn tệp sau commit, kiểm reference mới và hash/path ngoài DB transaction. UI chặn mutation trùng, reconcile bằng GET khi không rõ outcome, giữ lựa chọn hiện hành khi response trễ. Native dialog có nhãn, focus “Giữ lại”, hủy/Escape; không thêm thư viện, cache hoặc migration.

## Giới hạn và bàn giao

- Xóa vĩnh viễn qua sản phẩm, không có Trash/Undo. Cleanup sau commit là best effort: nếu crash/file đang mở/hash hỏng hoặc lỗi I/O có thể còn tệp orphan. Metadata không được phục hồi giả; lỗi được log, không xóa tệp chưa chứng minh an toàn. Chưa có GC/retry cleanup bền sau crash; không tuyên bố giao dịch atomic giữa SQLite và filesystem.
- Artifact render legacy không có RenderRun đủ cặp vẫn trả latest_render=null; UI báo rõ và cho tạo lại bằng hành động explicit, không ghép full/preview từ hai lượt hoặc backfill trong GET. GET metadata không đọc mọi tệp; artifactGET/debugGET vẫn xác minh bytes và báo missing/incomplete khi cần.
- Nhiều client reorder dùng permutation hợp lệ hiện tại/commit cuối; chưa thêm CAS cho metadata order. Tập ID thay đổi do import/delete làm permutation cũ bị400 thay vì âm thầm bỏ trang. Giai đoạn11 còn phải tích hợp snapshot/khóa mutation khi export.
- Backend8000/Vite5173 giữ chạy, stopfile `.tmp/phase10-final-reopened.stop`. Tab sản phẩm sạch giữ tài liệu ba trang [2,1,3]. Không commit/push/deploy hoặc gửi ảnh ra ngoài.
