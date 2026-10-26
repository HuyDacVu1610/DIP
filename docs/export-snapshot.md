# Hợp đồng và snapshot xuất — MVP11.01–02

Ngày18/10/2026. Hai task nền tảng của [giai đoạn11](../tasks/todo.md); không phải nghiệm thu cả giai đoạn. Người dùng xác nhận không cần hoàn tác; không thêm Undo/Trash vào MVP.

## Request và thứ tự

`schemas/exports.py` là nơi định nghĩa ExportRequest/ExportRead. Đường import cũ `schemas.sessions.ExportRequest` được re-export để giữ tương thích. Request frozen, nested PageSnapshot frozen/tuple; không sửa list input, không tự sắp xếp. Pages là **tập con có thứ tự xuất do request chỉ định**, không nhất thiết toàn bộ tài liệu hoặc theo position hiện tại. Membership phải kiểm bằng cả session_id/page_id tại service, schema riêng không biết DB.

- PDF:1..20 trang duy nhất. PNG/JPG: đúng1trang, không ZIP hoặc nhiều trang trong một ảnh.
- Mỗi phần tử `{page_id:UUIDv4,revision:strict nonnegative integer}`; không path, filename, config nháp hoặc client artifact ID.
- `format=pdf|png|jpg` mặc địnhpdf; `paper_size=a4`; `orientation=auto|portrait|landscape` mặc địnhauto; `margin_mm` hữu hạn0..30 mặc định5; `image_encoding=png|jpeg` mặc địnhpng.
- Extra/null/sai kiểu/ID trùng kể cả revision khác bị từ chối. Options PDF vẫn được kiểm và giữ khi xuất PNG/JPG nhưng không áp dụng; định dạng ảnh doformat quyết định. image_encoding là lựa chọn nhúng ảnh trong PDF. Chưa có JPEGquality tùy chọn mới.

Ví dụ request PDF hai trang, đây là dữ liệu minh họa chứ không phải ID runtime:

```json
{
  "format": "pdf",
  "pages": [
    {"page_id": "33333333-3333-4333-8333-333333333333", "revision": 2},
    {"page_id": "11111111-1111-4111-8111-111111111111", "revision": 1}
  ],
  "paper_size": "a4",
  "orientation": "auto",
  "margin_mm": 5,
  "image_encoding": "png"
}
```

ExportRead đã chốt `{id,session_id,artifact_id,format,pages,created_at}`: UUID server, timestampUTC và ordered page/revision snapshot; không path/tệp tạm. Chỉ trả sau commit khi nối encoder/publication ở11.03–06. POST `/sessions/{sid}/exports` vẫn thuộc11.06, **chưa được tạo** ở hai task này.

## Chụp và giữ snapshot

`services/exports.export_snapshot(engine,store,sid,request)` là synchronous context manager. Context phải bao trọn chụp snapshot, đọc/encode, ghi và commit kết quả. Không lấy snapshot rồi thả khóa trước khi writer dùng ảnh. `run_export(processing,engine,store,sid,request,writer)` giữ cùng quy tắc khi dùng ProcessingExecutor hiện hữu; writer là callback đồng bộ cho các task encode sau, không phải bộ tạo PDF giả.

Thứ tự kiểm: request revalidate kể cả model_copy không validate → session/membership → exactrevision → PageConfig hợp lệ/confirmed/corners → RenderRun tương ứng → full artifact/source/hash/dimensions/config snapshot. Chọn run revisionDESC/created_atDESC/idDESC như reopen, chỉ nhận revision đúng request. Lấy helper read_render_history từ logic đã có, không gọi detector hoặc render. Legacy có artifact nhưng chưa RenderRun đủ cặp vẫn được coi là thiếu render, không ghép ảnh từ lượt khác.

ExportSnapshot/ExportPage là dataclass frozen; chứa title/session, request, ordered pages với revision/render_run_id/config frozen/StoredArtifact full frozen. Không giữ ORM session hoặc transaction qua encode. Sau khi thoát read transaction mới verify đường dẫn/hash/byte size của từng fullPNG. Không dùng preview, thumbnail hoặc xử lý chồng từ ảnh cũ. Không tạo file export/ExportRecord trong hai task này.

Các lỗi:

| Điều kiện | Hành vi |
|---|---|
| Schema/options sai | ValidationError tại schema; route tương lai dùng400INVALID_REQUEST |
| Session/page không có hoặc sai owner |404SESSION_NOT_FOUND/PAGE_NOT_FOUND theo handler hiện hữu |
| Revision request khác current |409REVISION_CONFLICT với expected_revision/actual_revision |
| Config chưa xác nhận hoặc không có quad |409PAGE_NOT_CONFIRMED; không tự xác nhận |
| Trang đúng revision/confirmed nhưng thiếu full run đúng revision |409PAGE_NOT_RENDERED, details.pages liệt kê **mọi trang thiếu** theo thứ tự request; không tự render |
| DBbinding/config/run/fullpair hỏng |500STORAGE_FAILED sanitized, không chọn ảnh khác |
| Tệp full mất/hỏng/hash/path không khớp |500STORAGE_FAILED qua ArtifactFileError; không xuất ảnh thay thế |
| Tài liệu đã có lease xuất |409SESSION_BUSY |
| Shared worker kín1active+2waiting hoặc đang đóng |429PROCESSING_BUSY, lease mới được trả |

Lỗi thiếu render minh họa (handler đã kiểm HTTP bằng route chỉ có trong test):

```json
{
  "error": {
    "code": "PAGE_NOT_RENDERED",
    "message": "Cần tạo bản quét đúng revision cho các trang đã chọn.",
    "details": {
      "pages": [
        {"page_id": "33333333-3333-4333-8333-333333333333", "revision": 2}
      ]
    }
  }
}
```

## Lease, mutation và hủy

`session_guards.py` giữ busy-set theo session UUID, registry theo app Engine bằng WeakKeyDictionary; không cột DB/lockfile/migration. RLock đồng bộ reserve với các transaction metadata đang chạy, luôn lấy guard trước DB. Mutex chỉ giữ trong transaction metadata ngắn; CPU ở ngoài. Busy-set giữ lâu cho riêng tài liệu xuất; tài liệu khác và GET/health vẫn hoạt động.

Các service rename/config/order/delete page/delete session/import/render/detect đều dùng guard; import/render/detect kiểm trước CPU và trước publish. Một lượt bắt đầu trước export vẫn không được publish vào tài liệu đang giữ snapshot. Async upload/render/detect còn kiểm qua threadpool trước hàng đợi CPU, tránh chờ export xong rồi âm thầm thực hiện thao tác đã gửi khi bị khóa. Read/debug/artifactGET không khóa; cleanup chỉ xử lý UUID chưa tham chiếu của chính lượt thất bại.

Giữ ảnh bằng descriptor immutable + DB reference hiện hữu + chặn mutation/cleanup owner trong lease; không thêm pin table/refcount. Không bảo vệ trước thao tác xóa tệp từ ngoài ứng dụng hoặc một tiến trình backend khác.

`run_export` reserve trước enqueue để lượt thứ hai cùng tài liệu bị từ chối ngay. Nếu429/submit exception hoặc hủy khi còn chờ, release và không chạy writer. Nếu đã bắt đầu thread, hủy HTTP caller **không dừng thread**: giữ lease và slot tới khi worker thoát finally. Claim/cancel/release dùng cùng mutex, release idempotent và không gỡ khóa của lượt kế tiếp. Thành công, snapshot lỗi, writer lỗi, queued cancel đều tháo khóa; shutdown xử lý theo executor hiện hữu. Engine mới sau restart không phục hồi busy marker cũ.

Giới hạn triển khai: local MVP **một process/một Engine cho DB**, không chạy nhiều Uvicorn workers hoặc hai backend cùng DB để kỳ vọng chia sẻ lease. Khi triển khai multi-process phải thay cơ chế khóa; không mở rộng điều đó trong đề tài hiện tại.

## Kiểm chứng

- 54tests mới:19schema,3guard,16snapshot và16mutation/lifecycle. RED schema/guards/snapshot chưa tồn tại;11mutation cases ban đầu không bị chặn;3async cases ban đầu chờ worker xong rồi chạy; lỗi thiếu-render ban đầu500. Tất cả đã GREEN. Lỗi KeyError trong test path Windows đã sửa bằng Path canonical, không đổi runtime để chiều test.
- Focus cuối:63passed21.35s gồm reopen/executor hồi quy. Full `-W error --tb=short --basetemp=.tmp/pytest11-01-02-full`: **1125passed171.02s**. Không skip/suppress hoặc thay thuật toán. Frontend không sửa, không chạy lại build/test của frontend; mốc87tests/build giai đoạn10 vẫn là bằng chứng trước.
- Demo HTTP/worker trên DB riêng với3ảnh synthetic inPAGE1/2/3, Color0/Gray90/BWOtsu270, chọn[3,1]. Snapshot2full đúngrun/revision/config;8mutationHTTP trả409SESSION_BUSY, exportthứhai bị chặn, health/GET đọc được;26artifacthash nguyên, unlock sauworker. Callback chỉ kiểm snapshot/hash, **exports_written=0**, không giả PNG/JPG/PDF đã xuất.
- Evidence ignored `experiments/results/mvp11-01-02-verified/`: request/snapshot/blocked-mutations/runtime-verification và DB tổng hợp; product-before/after/database-backup/product-verification dùng bảo toàn dữ liệu runtime qua restart. Không gửi ảnh cá nhân hoặc DB ra ngoài.

Mốc11.01–02 đạt với checkpoint11-C1 khi đó còn chờ. Hiện11.01–07/checkpoint11-C1/C2 đã đạt, nextMVP11.08; xem [encoder/A4](export-encoding.md). Cổng11/M3 vẫn chưa đạt.


Cập nhật11.05–07: ghép/lưu/API/UI tải PNG/JPG/PDF đã kiểm, checkpoint11-C2đạt;1194backend-Werror/95frontendtests/typecheck/build. Next11.08 kiểm chứng cuối toàn giai đoạn. Các số đo ở mục03–04 phía trên là lịch sử. [Luồng xuất hiện hành](export-workflow.md).


Cập nhậtnghiệmthu11.08/AUX11.01: cả8task/checkpoint11-C1/C2/cổng11/M3đạt,86main+11AUX;1199backend-Werror/95frontendtests/typecheck/build. NextMVP12.01. Cácnext/chờởmốc11.01–07phía trênlàlịch sử;trạngtháihiệnhànhxem [audit8task](audit-phase-11.md).
