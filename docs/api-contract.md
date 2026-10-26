# Hợp đồng API Document Scanner MVP

Chốt18/10/2026, đã triển khaiMVP07.01–09,08.01–10/AUX08.01 và09.01–08/AUX09.01,10.01–07/AUX10.01 và11.01–08/AUX11.01 (contract/service/encoders/API/UI/nghiệmthu). [Snapshot xuất](export-snapshot.md), [Audit10](audit-phase-10.md), [Audit09](audit-phase-09.md), [Audit10task](audit-phase-08.md), [bằng chứng](progress.md), [MVP](MVP_Pham_Vi_Va_Ke_Hoach_4_Tuan.md), [checklist](../tasks/todo.md), [hợp đồng ảnh](image-contract.md), [đặc tả gốc](../Document_Scanner_Dac_Ta_Kien_Truc_Thuat_Toan.md).

## Trạng thái triển khai

Trạng thái 26/10: MVP01.01–07, 02–11 và 13–14 xong: **102 task chính, 13 AUX**; MVP01.08 bỏ qua. M4 kỹ thuật đạt26/10/2026: bản chạy cùngorigin localhost8000, sourceZIP/manifest/checksum, cài sạch đúnglock/1.279backend-experiments+103frontendtests/typecheck/build, README/hướng dẫn/báo cáo sốliệu thật vàdemo5–7phút đãkiểm. RehearsalUI sau nhập5phút21giây, PDF3trang/restart65artifact đạt; chưa có lượt tập nói hoặc thủ tục nộp hành chính. Đã rà đủ8task14/AUX14.01; giữlõiảnh/preset/lock/manifest/nhãn/frozen13, chỉ sửa một dòng chú thích dataset trênUI. Giai đoạn12 còn7task chưa nghiệmthu và5optional chưa làm; không tựtích theo cổng hồi quy trước khóa. Giữ ca sai development và giới hạn mỗi split một tài liệu. API/schema3/core/dependencies giữ nguyên;14.08 chỉ sửa chú thích datasetUI và bổ sung gói nộp. Xem [cấu hình bản chạy](local-runtime.md). [Kết quả](results.md), [audit13](audit-phase-13.md), [bản khóa](experiment-environment.md), [phương pháp đo](benchmark-method.md).

`create_app(database_path)` dùng lifespan khởi tạo/kiểm schema DB, ArtifactStore tại thư mục chứa DB và một ProcessingExecutor dùng chung. Shutdown hủy việc chờ, đợi việc đang chạy xong và join worker trước dispose engine. App mặc định dùng `data/scanner.sqlite3`; import module chưa tạo DB. Route metadata đồng bộ chạy qua threadpool của FastAPI, không chạy OpenCV trong transaction; route upload async gửi import qua app.state.processing. Các route `/verification/*` của mốc trước chỉ nằm trong script ignored; luồng07.07–09 đã kiểm trực tiếp API sản phẩm và UI.

## Quy ước chung

- Base `/api/v1`, JSON snake_case; ID UUIDv4, server cấp và serialize dạng chuẩn. Thời gian có timezone, trả UTC ISO8601 (`Z`); không nhận datetime naive trong response model.
- Bộ tài liệu gọi session. Mọi lookup trang phải lọc cảsession_id/page_id, artifact phải kiểm owner; không suy ra membership từ UUID hợp lệ. Detail session hiện trả404/SESSION_NOT_FOUND cho ID sai hoặc không tồn tại. Các route trang/artifact sau này phải giữ cùng quy tắc ownership/404. ID không được ghép thành đường dẫn từ input người dùng.
- Body extra bị từ chối, revision/count/boolean nghiêm ngặt, số phải hữu hạn. Sessiontitle mặc định `Tài liệu chưa đặt tên`, trim,1..200ký tự. Query list `limit=20` (1..100), `offset=0` (≥0), order updated_at giảm dần vàid làm tie-break.
- Trang mới **revision=0**, confirmed=false. Đây là điều chỉnh lỗi tài liệu cũ image-contract ghi1: dùng taskMVP07.05 hiện hành làm căn cứ, không có dữ liệu runtime cần migrate. Revision ở envelope/servermetadata, không nằm trong config.
- Upload từng file multipart field `file`; tối đa15MiB/16MP/20trang. Không gửi JSON body config vào multipart. Filename chỉ hiển thị; MIME/header do backend kiểm; original bytes và normalizedPNG giữ riêng. PNG chuẩn hóa nội bộ có thể lớn hơn15MiB.
- State-changing POST (tạo/import/export) chưa có idempotency-key: không tự retry khi mất response/timeout vì có thể đã commit. GET an toàn để thử lại. PUTconfig dùng expected_revision; client nhận409 thì tải lại trạng thái, không tăng expected_revision rồi gửi mù.

## Kiểu dữ liệu thực thi

Trong `backend/app/schemas/`: common.py (base/time/revision/kind), sessions.py (tài liệu/order/alias export), exports.py (request/receipt xuất), pages.py (trang/config/artifact/detect/render), errors.py (envelope lỗi). Model dùng UUID4 của Pydantic; không import HTTP/DB vào processing hoặc schemas vào storage.

| Model | Các trường / quy tắc chính |
|---|---|
| SessionCreate | title optional, default/trim/1..200 |
| SessionRename | title bắt buộc, strictstring/trim/1..200; không nhận config/revision/extra |
| SessionRead | id,title,created_at,updated_at |
| SessionDetail | SessionRead+pages theo position tăng dần; khôngtrùng ID/position, mỗi trang cùngsession, tối đa20 |
| SessionList | items,limit,offset,total; không đổi sang listtrần giữa các lần |
| PageRead | id,session_id,position,width,height,3sourceartifactIDs,revision,render_revision|null,latest_render|null,latest_detection|null,effective_config,created_at,updated_at |
| ConfigUpdateRequest | expected_revision bắt buộc; config object thay thế, không merge persistedconfig |
| ConfigRead | page_id,revision,effective_config,inactive_fields dottednames |
| ArtifactRead | id,kind,revision|null,mime,byte_size,sha256,width/height hoặc cảnull,created_at; **khôngpath** |
| DetectRequest / DetectRead | debugbool/defaultfalse; page/source size,status,corners|null,heuristic_score|null,algorithm_version,confirmed=false,warnings,timings_ms |
| DetectionRunRead | DetectRead + run_id,source_artifact_id,source_revision,source_sha256,selected_trial_id,stage_artifacts{name:UUID}; confirmed luônfalse |
| RenderRequest / RenderRead | expected_revision/debug; page_id/revision/render+previewartifactIDs/render_run_id/fullwidth-height,warnings,timings_ms |
| PageOrderRequest | page_ids duy nhất, giữ thứ tự gửi,≤20; service kiểm danh sách đầy đủ của phiên |
| PageSnapshot / ExportRequest | page_id/revision theo thứ tự; format pdf/png/jpg,PDF1..20trang,PNG/JPGđúng1trang; A4/orientation/margin0..30mm/encodingpng hoặcjpeg |

Request/receipt export đã chốt11.01, snapshot/khóa đã kiểm11.02; PNG/JPG vàPDF một trang đã kiểm11.03–04;ghép/lưu/HTTP/UI/nghiệm thu cuối còn11.05–08. Không ZIP/ảnhnhiềutrang trong một PNG/JPG.

## Endpoint và nơi nối thực thi

| Method/path (sau prefix) | Input → output | Status thành công / task |
|---|---|---|
| GET /health | — → {status:ok} |200, đã có |
| POST /sessions | SessionCreate → SessionRead |201, đã có /07.04 |
| GET /sessions | limit/offset → SessionList |200, đã có /07.04 |
| GET /sessions/{sid} | — → SessionDetail |200, đã có /07.04 |
| POST /sessions/{sid}/pages | multipartfile → PageRead |201, đã có /07.07 |
| GET /artifacts/{aid} | artifactID → binary MIME đúng |200, đã có /07.07, không public data/ |
| PUT /sessions/{sid}/pages/{pid}/config | ConfigUpdateRequest → ConfigRead |200, đã có /08.01 |
| POST /sessions/{sid}/pages/{pid}/render | RenderRequest → RenderRead |200, đã có /08.03 |
| POST /sessions/{sid}/pages/{pid}/detect | DetectRequest → DetectionRunRead |200, đã có /09.01 |
| GET /sessions/{sid}/pages/{pid}/debug | DebugQuery → DebugRead |200, đã có /09.06; chỉ đọc |
| DELETE /sessions/{sid}/pages/{pid} | — → empty |204, đã có /10.05 |
| PUT /sessions/{sid}/page-order | PageOrderRequest → SessionDetail |200, đã có /10.03 |
| PATCH /sessions/{sid} | SessionRename → SessionRead |200, đã có /10.01 |
| DELETE /sessions/{sid} | — → empty |204, đã có /10.06 |
| POST /sessions/{sid}/exports | ExportRequest → {id,session_id,artifact_id,format,pages,created_at} |201 /11.06; snapshotgiữtheoorderrequest |

Debug trả refs thuộc đúng page/run, ArtifactRead khôngpath; xác minh bytes/hash ngoài transaction đọc. Histogram/counts/hash/scope theo image-contract11.2; không ndarray hoặc dựng stage bằng lượt giả. DebugQuery/DebugRead đã hiện thực09.06; responseexport còn11. Render/detect/export qua một CPUworker/haiwaiting ở07.06; quá tải429. Không tạo jobID/polling/cloud ở MVP.

## Config, góc và revision

`ConfigUpdateRequest` chỉ kiểm envelope trước lookup. Sau khi tìm đúng trang trong session, service **bắt buộc** gọi `request.validate_config(source_size=(W,H),warp_size=...)`, trả PageConfig frozen từ `parse_config`. Không tạo dimensions giả để FastAPI parsecorners. API chưa được phép gửi rawdictconfig thẳng vào persistence.

Missing trường/fieldcon lấy preset theo mode của **request mới**, không giữ giá trị config cũ. `null`,extra,sai kiểu/miền kể cảinactive bị từ chối. Inactiveparams vẫn lưu để frontend đổi mode. Không có illumination/sharpen/A4warp ở configMVP. PageRead dùng chính width/height của nguồn để validate config; ConfigRead khi build cócorners phải truyền validationcontext source_size thật, như lõi. Geometry không bị nới để serializeJSON.

PUTconfig so toànfullconfig sau parse; đổi thì revision+1 một lần/commit, no-op giữrevision và cả page/config/session timestamps. Mới nhập0. expected_revision cũ luôn409, kể cả payload làno-op; không cập nhật từartifact. Request mới có góc mà thiếu confirmed dùngdefaultfalse/draft; muốn xác nhận phải gửi confirmed=true cùngquad hợp lệ. Backend không suy từ trạng thái confirmed cũ hoặc tựdetect. UI kéo góc phải đặt confirmed=false; một request có thể gửiquad mới và xác nhận rõ cùnglúc. Detect chỉ đề xuất, không cập nhật config. CAS/no-op/confirmation đã thực thi08.01; không có lịch sử config riêng trongDB.

Render cần confirmed, chụp source/config/revision rồi xử lý ngoài DBtransaction, kiểm revision lần nữa trước publish. Artifactsource không có revision; render/preview/debug có page_revision; oldartifact không tự thành render mới. PageRead.render_revision có thể nhỏ hơn currentrevision để đánh dấu cũ. Full/preview/debug/histogram/config thuộc cùng phép chạy; preview từfull,khôngcachebền. Thayfilterkhông được xử lý chồng lênrender trước.

Export đòi đúng session/page/revision/confirmed/order, fullrender đủ; thiếu trả409/PAGE_NOT_RENDERED và danh sách thiếu, không tự xác nhận. Khóa mutation trong lúc export, finallygiải phóng; **không persist khóa** qua restart. PNG/JPG lấy full mộttrang; PDF fitA4/khôngstretch/crop. Các gate/snapshot/khóa đã hiện thực11.02 vàencoder/layout11.03–04; ghép/lưu/route201 vàUI đã có11.05–07; không có cột khóa trong SQLite.

## Ví dụ JSON (minh họa kiểu, không là số đo)

Tạo tài liệu (`SessionCreate`):

```json
{"title":"Bài tập xử lý ảnh"}
```

Trang mới (`PageRead`), source100×80 sauEXIF, IDsminhhọa:

```json
{
  "id":"22222222-2222-4222-8222-222222222222",
  "session_id":"11111111-1111-4111-8111-111111111111",
  "position":0,"width":100,"height":80,
  "original_artifact_id":"33333333-3333-4333-8333-333333333333",
  "normalized_artifact_id":"44444444-4444-4444-8444-444444444444",
  "thumbnail_artifact_id":"55555555-5555-4555-8555-555555555555",
  "revision":0,"render_revision":null,
  "effective_config":{
    "mode":"color","corners":null,"confirmed":false,"rotation":0,
    "denoise":{"method":"none","kernel":3},
    "contrast":{"method":"none","clip_limit":2.0,"tile_grid":[8,8]},
    "threshold":{"method":"adaptive_gaussian","block_size":31,"c":10},
    "geometry":{"aspect_policy":"estimated","max_long_edge":2400}
  },
  "created_at":"2026-10-17T09:00:00Z","updated_at":"2026-10-17T09:00:00Z"
}
```

Thay config (`ConfigUpdateRequest`):

```json
{
  "expected_revision":0,
  "config":{
    "mode":"bw","corners":[[0.1,0.1],[0.9,0.1],[0.9,0.9],[0.1,0.9]],
    "confirmed":true,"rotation":0,
    "denoise":{"method":"none","kernel":3},
    "contrast":{"method":"none","clip_limit":2.0,"tile_grid":[8,8]},
    "threshold":{"method":"otsu","block_size":31,"c":10},
    "geometry":{"aspect_policy":"estimated","max_long_edge":2400}
  }
}
```

Render (`RenderRequest`), sau commit config trên tăngrevision1:

```json
{"expected_revision":1,"debug":true}
```

Lỗi (`ErrorEnvelope`):

```json
{"error":{"code":"REVISION_CONFLICT","message":"Cấu hình đã thay đổi; tải lại trang.","details":{"expected_revision":0,"actual_revision":1}}}
```

## Lỗi thống nhất

| HTTP | Code | Ý nghĩa |
|---|---|---|
|400|INVALID_REQUEST,INVALID_CONFIG,INVALID_QUAD|Body/options/config/góc sai; validationerrors không lộ input/path/trace |
|400|EMPTY_FILE,INVALID_IMAGE,IMAGE_TOO_SMALL|Tệp rỗng/hỏng/decoder lỗi hoặc cạnh nguồn dưới2pixel |
|404|SESSION_NOT_FOUND,PAGE_NOT_FOUND,ARTIFACT_NOT_FOUND|ID sai/thiếu/khôngmembership |
|405|METHOD_NOT_ALLOWED|Sai method; giữ header Allow |
|409|REVISION_CONFLICT,PAGE_NOT_CONFIRMED,PAGE_NOT_RENDERED,SESSION_BUSY|State cũ/chưađủđiềukiện/đangexport |
|413|FILE_TOO_LARGE,TOO_MANY_PIXELS,PAGE_LIMIT_EXCEEDED|Quota15MiB/16MP/20trang |
|415|UNSUPPORTED_IMAGE|Khôngphải JPEG/PNGmộtframe; map core UNSUPPORTED_FORMAT |
|429|PROCESSING_BUSY|Worker/haiwaiting đãđầy |
|500|STORAGE_FAILED,PROCESSING_FAILED,INTERNAL_ERROR|Thôngbáochung, khônglộSQL/path/exception |

Handler đã nối400body/query/multipart/config; sid sai/thiếu404SESSION_NOT_FOUND, pid sai/thiếu/khácowner404PAGE_NOT_FOUND, aid sai/thiếu404ARTIFACT_NOT_FOUND; route lạ404NOT_FOUND; sai method405 giữAllow. Lỗi ảnh giữ corecode400; UNSUPPORTED_FORMAT/MULTI_FRAME_IMAGE ánh xạ415UNSUPPORTED_IMAGE; byte/pixel/pagequota413. Config/quad400 trả message chung, details rỗng; revision409 có đúng expected_revision/actual_revision. ProcessingBusyError→429PROCESSING_BUSY. SQLAlchemy/metadata/ArtifactFileError→500STORAGE_FAILED, exceptionkhác→500INTERNAL_ERROR. Storage/internal message chung/details rỗng, không echo input/SQL/path/trace. OpenAPI dùng ErrorEnvelope/4XX native để không có422 giả. PageNotConfirmedError→409/PAGE_NOT_CONFIRMED, RenderProcessingError→500/PROCESSING_FAILED đã nối08.03; SESSION_BUSY và PAGE_NOT_RENDERED handler đã có11.02; route xuất vẫn ở11.06, không đổi core cho HTTP.

## Upload và đọc artifact — MVP07.07

Upload nhận đúng1partfile tên `file`, không textfield/configbody hoặc nhiều file trong cùng request. Starlette multipart parser đọc request.stream có cap **15MiB+64KiB envelope**; từng file được đọc chunk64KiB và đếm riêng tối đa15MiB, không tinContent-Length. Tràn cap trả413; sai multipart/boundary/thiếu kết thúc/sai field trả400. Việc kiểm thiếu kết thúc nằm trong vòng parse được bảo vệ để đóng cả spoolfile chưa vàoFormData; form.close chạy ởfinally cho luồng đã parse xong. Giới hạn stream này là chính sách triển khai, không tính64KiB vào bytequota của ảnh.

Payload bytes gửi vào `await app.state.processing.run(import_page, engine, store, sid, payload)`. Validator decoder/header/pixel/EXIF/alpha và quota20 lúccommit giữ như service07.05. Filename/clientMIME không xác nhận nội dung hoặc chọn đường dẫn. Filename chỉ xuất hiện tạm trong kết quả batch trênUI, chưa persist tên file gốc trongDB. Không auto-retryPOST. Body được parse trước khi submit; quota worker không là giới hạn tổng kết nối upload đồng thời.

GETartifact lookup UUID, join session/pageowner trongDB rồi đóng transaction; tạo StoredArtifact, guard path/root/symlink/junction và verify regularfile/bytecount/SHA-256 trước FileResponse. UUID thiếu trả404; metadata tồn tại nhưng file hỏng/thiếu trả500STORAGE_FAILED, không phục vụ bytes sai. MIME từ artifact metadata do service tạo; Content-Disposition inline/UUIDfilename, X-Content-Type-Options nosniff và Cache-Control private,no-store. Không public data directory hoặc nhận path từ query. App localhost chưa có tài khoản; đây không phải authorization đa người dùng. Không chống tiến trìnhOS có quyền thay tệp giữa verify vàserve.

## Config và render snapshot — MVP08.01–02

`update_page_config(engine,sid,pid,request) -> ConfigRead`: transaction lấy SQLite writer lock bằng UPDATE session giữ nguyên timestamp **trước** lookup/CAS. Parse full config theo dimensions nguồn thật; có corners thì estimate_warp_size rồi kiểm block Adaptive active theo warp thật. Payload canonical đổi thì revision+1 và timestamps config/page/session đổi cùng commit; no-op giữ tất cả. CAS kiểm cả no-op. Request mới thiếu confirmed dùng false, không kế thừa xác nhận cũ; confirmed=true phải được gửi rõ cùng quad hợp lệ. ConfigRead được validate theo source_size thật trước commit. Không merge persisted config.

`render_page(engine,store,sid,pid,expected_revision) -> RenderRead` là use case blocking, được route08.03 gửi nguyên use case vào shared executor. Read transaction chụp config frozen/source descriptor/dimensions, kiểm owner/revision và confirmed=true. Ngoài transaction, verify tệp/hash rồi decode PNG RGB một frame, không EXIF, dimensions khớp page/descriptor và ≤16MP; không áp upload cap15MiB hay EXIF lần hai. Gọi render_document với góc đã xác nhận: warp từ nguồn đầy đủ → denoise/mode/threshold/rotation → encode_render_images tạo full và preview từ final pixels. Không detector tự xác nhận, không xử lý chồng lên render cũ.

Transaction mới lấy writer lock, kiểm lại page/session/revision và so sourceID/dimensions/config với snapshot trước bất cứ publish nào. Sửa config/xóa trang trong lúc CPU chạy thì từ chối kết quả; không ghi file mới. Sau gate, giữ lock qua ghi bytes đã encode/register hai artifact cùng page/revision/commit; decode/OpenCV/resize/encode đều ở ngoài lock. Chọn I/O bytes có giới hạn trong lock để không có khe hở giữa gate và publish. Artifact chỉ đọc được qua API sau metadata commit. Lỗi write/register/commit rollback rồi dọn từng descriptor mới chưa tham chiếu bằng transaction mới; giữ source/config/oldrender, log nếu cleanup lỗi. Crash vẫn có thể để orphan; chưa GC/transaction nguyên tử file+DB.

Render không tăng revision hoặc đổi config/timestamps. Lặp cùng revision tạo UUID mới; đổi config giữ oldartifact với render_revision<revision. RenderRead có full/preview UUID, dimensions full sau rotation, warnings rỗng vì chỉ dùng góc manual đã xác nhận. timings_ms gồm source_load (verify+decode), encode (full+preview) và core.validate/detect/warp/enhance/total; core.detect=0 ở nhánh manual, core.total không gồm DB/file/source_load/encode. Không cộng total với các khoảng con. PageNotConfirmedError/RenderProcessingError đã ánh xạ HTTP ở08.03. Debug/histogram persistence còn09; không thêm schema/dependency/job/cache.

25configAPI +21service tests kiểm concurrent CAS/no-op/inactive/quad/nonfinite, nguồn lớn>15MiB, full/preview pixels, nguồn sai role/hash/dimensions/mode/EXIF/decoder, stale khi config/page/session đổi và process/encode/write/register/commit faults. Runtime riêng `experiments/results/mvp08-01-02-verified/` dùng WrongEXIF.jpg480×640/góc toàn khung/rotation90 →639×479, artifactGET đúng bytes, revision2/render_revision1 và hashes giữ sau restart thật. Góc toàn khung chỉ là thử service, chưa nhãn mép giấy/đánh giá detector. Đây là mốc08.01–02 (962tests); nghiệm thu HTTP/checkpoint08-C1 hiện hành ở mục08.03 dưới đây. [Progress](progress.md).

## API render qua executor — MVP08.03

POST render nhận RenderRequest strict expected_revision/debug (defaultfalse), trả RenderRead với page_id/revision, UUID full/preview, dimensions full sau rotation, warnings và timings_ms. Route async gửi **toàn bộ** render_page vào chính app.state.processing dùng cùng import, không tạo threadpool hoặc render trong event loop. Không đổi revision/config hoặc tự xác nhận. Từ09.05 debug=true lưu stage thật và RenderRun; đã bỏ cảnh báo DEBUG_NOT_AVAILABLE. Debugfalse vẫn lưu RenderRun cơ bản/full-preview nhưng không giữ stage/histogram, debugGET báo not_requested. Xem mục09.05–06 bên dưới; gateconfirmed/revision không đổi.

Chưa confirmed→409/PAGE_NOT_CONFIRMED, revision cũ→409/REVISION_CONFLICT kèm expected/actual; sid/pid sai/thiếu/khácowner404; body sai400; worker+hàng chờ đầy429/PROCESSING_BUSY. RenderProcessingError→500/PROCESSING_FAILED với message chung/log server; file/DB giữ500/STORAGE_FAILED, không lộ path/exception. Config có thể thay trong lúc render, service kiểm lại trước publish; response lỗi thời không trở thành render hiện hành. Cancel HTTP không dừng thread đã chạy, theo executor07.06; không tự retry POST khi mất response.

21HTTP tests mới và focused90 (config/service/session/executor) đạt-Werror; backend983passed139.55s. Kiểm ba mode/rotation/outputbytes/reopen/owner/hash, strictbody, draft/stale, update/xóa page khi CPU đang chạy, health200 cùng worker bị chặn, render và upload đều429 khi queue đầy, lỗi xử lý sanitized và worker phục hồi. Runtime mvp08-03-04-verified/ dùng API sản phẩm upload→config→render→GET output, restart hai tiến trình giữ config/revision/hashes. Checkpoint08-C1 đạt, frontend mapping27tests/typecheck/build/browser8tổhợp DPR đạt riêng ở08.04; chưa UIeditor/renderbutton/M2/debugPDF. [Progress](progress.md).

## UI và mở lại — MVP07.08–09

**Mốc08.07–08 (lịch sử):** CornerEditor dùng draft đầy đủ tách khỏi config/revision đã lưu; source luôn normalized PNG. Xác nhận explicit gửi confirmed=true, lưu nháp gửi false; sửa góc/toàn ảnh bỏ confirmed, cancel phục hồi full snapshot trước kéo. “Tạo bản quét” chỉ mở khi draft đã xác nhận/hợp lệ/không cần đối soát: PUT full config trước, sau đó POST đúng revision từ ConfigRead. Cả phản hồi config và render phải đúng page/revision; operation generation và draft edit counter chặn response sau unmount/đổi trang/sửa góc. Không tự retry mutation, không coi hủy HTTP là rollback; lỗi bắt GET “Đọc lại cấu hình”, giữ draft nhưng bỏ xác nhận để người dùng đối chiếu lại. Old preview giữ cùng nhãn cũ khi draft/revision thay đổi hoặc state chưa chắc chắn. Page editor đọc GET detail mỗi lần mở lại để không dùng metadata cũ của page list; refresh/chuyển trang bỏ nháp chưa lưu đã có nhắc trên UI. GET detail chưa trả UUID kết quả; lần mở lại cần render explicit để xem preview. So sánh/zoom09, không thêm cache/history API. [Hợp đồng editor](image-contract.md), [bằng chứng](progress.md).

React client dùng nativefetch/DTO TypeScript, không dependency mới. Có create/list/detail, phântrang danh sách20, batch chọn nhiềuJPEG/PNG nhưng POST từngfile theo thứtự. Lỗi mộtfile được báo riêng và tiếp tục file khác; kết quảbatch giữ khi refresh metadata nội bộ. Lỗi network không tự gửi lạiPOST, hướng dẫn tải lại tài liệu để kiểm trước khi thử nhập lại.

PageList dùng thumbnail artifact, SourcePreview dùng normalizedPNG/fullsource theo đúngEXIF/dimensions. Không xử lý ảnh trênfrontend, không áp CSSxoay lầnhai, không lấythumbnail làm nguồn geometry. Session/page selection lưu trong URL query; name/order/config/revision/ảnh lấy lại từDB/artifactGET, không localStorage bảncopy. RequestGET dùngAbortController khi đổi tài liệu; bấm lại tài liệu đang mở giữ lựa chọn trang. Kết quả từngfile của batch chỉ là UIstate, không persist qua browserrefresh.

Trình duyệt thật đã tạo tài liệu/chọn EXIF6→fakeJPG→alphaPNG: hai trang hợp lệ64×96/4×2, lỗi ở giữa không mất trang. Refresh giữ lựa chọn; dừng backendv1, UI báo lỗi, mở backendv2 cùngDB rồiTảilại giữ tên/order/config/UUID/hash6file. Nguồnimg_0041536×2048 nhập quaAPI sản phẩm và xem trênUI khớp normalizedhash manifest. Responsive320/768/1024/1440 khôngoverflow; keyboardfocus/label/basicconsole đãkiểm. [Audit](audit-phase-07.md) ghi giới hạn và ảnh minh chứng.

## SQLite metadata — MVP07.02

`open_database(path)` không sideeffect import. `initialize_database` tạo8table/schema_version3 hoặc nhận đúngschema3. Migrationtườngminh, atomic: đúngschema1/6table tạo detection_runs+render_runs; đúngschema2/7table chỉtạo render_runs; cậpnhậtversion3 trongcùngtransaction. Giữmọirow/bảngcũ, lỗirollbackDDL/version, idempotent; DBlạ vẫn từchối/khôngreset. SQLitebackup trước migration và đối chiếu toànrow/hash nguồn sau restart.

| Table | Dữ liệu / ràng buộc |
|---|---|
|schema_version|Mộtrow id=1/version=3; version1/2 được migrate tường minh |
|sessions|UUID,title,created_at/updated_at UTC |
|pages|SessionFK,unique(session,position),width/height sauEXIF≤16MP,3sourceartifactIDs bắt buộc,UTCtimestamps |
|page_configs|Mộtrow/page,session+pageFK,revision≥0,full configJSONobject; core/service kiểmtham số/góc |
|artifacts|UUID,session/pageowner,kind,revision,pathrelative,MIME,bytes/hash,size/UTC; khôngblobảnh |
|exports|Session+artifactownerFK,format,ordered pagesnapshotJSONArray1..20,UTCtimestamp |
|detection_runs|UUID,owner/session/page/sourceartifactFK,source_revision≥0,source_sha256,algorithm_version,metadataJSONobject,created_atUTC; cascade metadata theo nguồn/page |
|render_runs|UUID,session/page/source/full/preview compositeownershipFK,revision≥0,source_sha256,metadataJSONobject,created_atUTC; mỗi lượt mộtrow, không unique theo revision |

CompositeFK ép artifact và config thuộc đúng(session,page); sourcepointer phải về **đúng page đó**, không chỉ cùngsession. Vòng page↔sourceartifact dùng deferredFK đến COMMIT: cấp UUID trước rồi insert cảmetadata trong transaction. Xóa mộtsource đangđượcpage thamchiếu bịchặn; xóasession cascademetadata. Ghi tạm→publish và primitive dọn tệp đã có ở07.03; use case nhập và cleanup khi commit lỗi ở07.05. CascadeSQL **chưa xóa tệp** và không được dùng thay filecleanup.

FK bật **mọi kết nối**, BEGINexplicit để SELECT/DDL/rollback nhấtquán; thamchiếu [SQLAlchemySQLite](https://docs.sqlalchemy.org/en/21/dialects/sqlite.html). UTC lưuISOtext, mởlại trảdatetime aware. JSONconfig lưu một snapshot đầyđủ thay vì tách mode/filters thànhcột trùngthôngtin. Snapshotexport làbằngchứng lịch sử, khôngFK vào revision config hiệnhành. Không có cột khóaexport persisted.

DB kiểm quyền sở hữu và miền cơ bản, khôngchứngnhận blob/tệp tồn tại/hash thật, MIME thực, đúngloại ảnh ởsourcepointer, mọi phần tửsnapshot hay PageConfigsemantics. Service nhập/render/export sẽ kiểm chúng với processing/files; rawORM không phải usecase nhậpảnh. Quota20/CAS/revision/confirmed/full-render gating cũng ởservice tươngứng. PathcheckSQL làsyntax tươngđối, **không thay** resolve/root/symlink kiểm antoàn. Repository có unit of work, query session/page/artifact theo owner, đăng ký tệp đã kiểm hash và dọn tệp mới chưa tham chiếu; không tự commit mỗi query hoặc chạy OpenCV trong transaction.

List trả count/rows trong cùng transaction, order updated_at DESC/id ASC. Detail chỉ lấy trang thuộc session, theo position, dùng dimensions nguồn thật để kiểm config và fail nếu thiếu config. `render_revision` là max revision metadata full-render của trang hoặc null; chưa chứng nhận cặp full/preview hay điều kiện xuất. Create chỉ trả thành công sau commit.

## Tệp artifact — MVP07.03

`ArtifactStore.write_bytes` nhận payload bytes đã encode xong; không nhận upload filename/path và không encode lại. Server cấp UUIDv4, đường dẫn cố định `sessions/{sid}/{sources|renders|debug|exports}/{artifact_id}.{jpg|png|pdf}`. Owner/kind/MIME/revision/dimensions phải hợp lệ; normalized/thumbnail/render/preview/debug chỉ PNG. Byte count/SHA-256 tính trên đúng payload lưu. Không áp quota upload15MiB cho PNG nội bộ.

Ghi temporary trong cùng thư mục đích → write/flush/fsync/close → publish không ghi đè UUID cũ. Windows dùng [os.rename](https://docs.python.org/3.12/library/os.html#os.rename), destination đã tồn tại sẽ lỗi; POSIX dùng hard link không thay tệp đã có rồi unlink temporary. Kiểm path nằm trong root và từ chối symlink/junction/reparse ở các thành phần con, kể cả junction trỏ lại trong root. Root runtime do backend tin cậy; đây không phải sandbox chống tiến trình OS có quyền thay thư mục đồng thời.

`register_artifact` chỉ thêm metadata sau khi verify regular file/bytes/hash; caller giữ transaction/commit. Lỗi ghi/fsync/rename dọn đúng temporary của lần ghi và không thay tệp cũ. Sau rollback, `discard_unreferenced` chỉ dùng cho descriptor tệp mới của thao tác vừa lỗi; kiểm DB theo cả ID/path trước khi verify/unlink, không dọn artifact còn tham chiếu, không recursive delete. Không có transaction nguyên tử chung filesystem+SQLite: crash giữa publish/commit có thể để orphan; chưa có GC và chưa chứng nhận phục hồi sau mất điện. Use case07.05 đã nối cleanup lỗi thông thường; nếu chính cleanup không đọc/ghi được DB/tệp thì log phía server, giữ lỗi gốc và tránh xóa file không rõ tham chiếu.

## Service nhập một trang — MVP07.05

`import_page(engine, store, session_id, payload_bytes) -> PageRead` là hàm blocking, gọi qua executor từ route async khi nối07.07. Không nhận filename/config/góc hoặc tự detector/confirmed. Kiểm session/quota trước xử lý; validate_image kiểm JPEG/PNG thật và15MiB/16MP; normalize_image load/EXIF/alpha→BGR. Encode normalized PNG và thumbnail320 bằng INTER_AREA/half-up/no-upscale trước ghi bất cứ file nào. Thumbnail có thể có một cạnh1pixel, dùng encode_stage_png hiện có; PNG nguồn vẫn dùng encode_normalized_png và giữ đúng payload/hash.

Ghi original bytes không đổi (MIME theo nội dung, dimensions trướcEXIF), normalized/thumbnail PNG (dimensions theo từng raster). Sau đó transaction ngắn UPDATE session để lấy writer lock SQLite **trước** đọc count/position, kiểm lại session/quota20 và append max(position)+1. Commit cùng page/3artifact/config đầy đủ revision0/confirmed=false/corners=null; session.updated_at được cập nhật. Không decode/filter/resize/encode trong transaction. PageRead được kiểm theo source dimensions thật trước commit, chỉ trả sau commit.

Encode lỗi chưa có file; write/commit/session bị xóa/quota tranh chấp lỗi thì rollback và dọn từng descriptor mới chưa tham chiếu bằng transaction mới. Không xóa nguồn/trang đã commit. Hai lượt nhập tranh suất thứ20 chỉ một được commit, lượt thua dọn ba file; thử riêng ngoài executor để kiểm guard DB. Không tự retry POST khi mất response: tác vụ có thể đã commit.

## Executor dùng chung — MVP07.06

`app.state.processing` có `submit(blocking_callable, *args, **kwargs)` trả asyncio.Future và `await run(...)` trả kết quả. Dùng từ event loop của app; một ThreadPoolExecutor worker, tối đa hai callable chờ FIFO. Chỉ đưa một việc active vào thread pool, hàng chờ riêng bị giới hạn; không tích vô hạn các work item đã hủy. Đây là giới hạn số tác vụ ảnh, không cấu hình số thread nội bộ OpenCV.

Hủy Future/tác vụ async đang chờ sẽ trả slot ngay trước lần submit kế tiếp và không chạy callable đó. Hủy người gọi sau khi worker bắt đầu không dừng thread hoặc rollback việc đã chạy; vẫn giữ slot đến khi callable kết thúc, bỏ kết quả cho người gọi đã hủy. Exception thường trả về caller và worker tiếp tục nhận việc. Không submit đệ quy từ worker vì có thể deadlock; một whole use case chiếm một slot. Các route import/detect/render/export sau này phải dùng chính instance này, không tự tạo executor khác; CLI offline độc lập.

`aclose()` từ chối submit mới, hủy hàng chờ, đợi active hoàn tất rồi shutdown/join thread. Chạy đúng một Uvicorn process; nhiều process sẽ có nhiều executor riêng. Không có jobID/polling, hard-kill thread, timeout giả dừng tính toán hoặc state hàng chờ persisted. Đối chiếu [Python executor shutdown/cancel](https://docs.python.org/3.12/library/concurrent.futures.html#concurrent.futures.Executor.shutdown) và [asyncio run_in_executor](https://docs.python.org/3.12/library/asyncio-eventloop.html#asyncio.loop.run_in_executor).

## Kiểm chứng

Mốc08.09–10/AUX08.01: hợp đồngHTTP/DTO không đổi. ComparisonView đọc normalizedsource và **render_artifact_id** quaartifactGET, onLoadkiểm đúngnaturalsize,fit/100/200/nativeoverflow/returnedit; previewvẫnđượcservicepersist/kiểm byteequal nhưngkhôngdùngđểzoomfull. Page/revision/draft/late guards của07–08 giữ. GETdetail chưa cóUUIDrender đểautoreopen, thuộc hoànthiệnMVP10.07. Full983backend-Werror/64frontend/typecheck/build vàbrowserquét tay3ảnh/dọc-ngang/forcedDPR/12colorprojections đạt; cổng08/M2/checkpoint08-C3 đạt. [Audit10task](audit-phase-08.md), [smoke](../frontend/tests/scanner-smoke.md).

21 schema tests +19 DB tests +19 artifact tests +18 session API tests +health: **78 tests tập trung đạt**, có partial write/fsync/rename, collision, exact normalized payload/hash, commit rollback, cleanup active/orphan và hai junction thật. API kiểm create/list/detail/rỗng, order/membership, malformed/missing UUID404, request400, commit500 rollback/sanitized,405 giữ Allow, OpenAPI đúng routes/errors.

Mốc07.03–04: runtime `.tmp/verify_mvp07_03_04.py` kiểm localhost/restart với9file fixture seed lower layer, không là use case nhập. Checkpoint07-C1 đạt; evidence cũ giữ nguyên ở `experiments/results/mvp07-03-04-verified/` (ignored).

Mốc07.05–06:14import tests +5executor tests mới, tổng **97tests tập trung đạt** với -W error. Có EXIF/alpha/MIME theo bytes/skinny thumbnail, encoder/write/commit fault, xóa session giữa nhập, cạnh tranh trang thứ20, FIFO/overload/cancel queued/cancel active/exception/shutdown, HTTP429 và health. Runtime `.tmp/verify_mvp07_05_06.py` dùng probe riêng gọi use case thật qua worker, nhập EXIF6/alpha thành2trang/6file; lỗi commit dọn file mới/giữ cũ, worker phục hồi, restart tiến trình riêng giữ detail/filehash và shutdown join thread. Health trong lúc worker bị chặn đo14.19ms trong lượt này, không là benchmark/SLA. Evidence `experiments/results/mvp07-05-06-verified/verification.json` (ignored). Checkpoint07-C2 đạt; API upload07.07/UI và cổng07 còn chờ. Hồi quy đầy đủ ghi tại [progress](progress.md).

Mốc07.07–09/AUX07.01:20HTTPupload/artifacttests mới đạt-Werror; backendfull **916passed125.89s**,117tests phase07 trongsuite (health đã có từM1). Frontendtypecheck/build/browser/restart đạt. Runtime sản phẩm `experiments/results/mvp07-07-09-verified/` có2page6file giữsau restart, sourceimg_004hashkhớpmanifest, screenshot/DOM/4viewport/console. [Audit9task](audit-phase-07.md) cóma trận/bugs đãsửa/giới hạn. Cổng07đạt, next08.01 config/góc/confirmed/revisionCAS; chưaM2renderUI.

## Detect API và proposal UI — MVP09.01–02

POST detect yêu cầu body JSON `{ "debug": true }` hoặc `{}` (defaultfalse). Lookup owner/page/config/source, snapshot revision và kiểm chính normalizedPNG RGB/hash/dimensions sauEXIF bằng shared `load_normalized_source`; không EXIF lầnhai/không quota15MiB PNG nội bộ. Toàn usecase qua sharedexecutor; decode/detect/encode ngoài DBtransaction. Core detector gọi đúngmột lần với debug nội bộ để giữ provenance; cờ request chỉ quyết định lưu PNG/fullcontour attempts. Không debug thì vẫn lưu run/trials/result, stage_artifacts rỗng.

Run lưu PNGsourcehash/BGRhash/analysis_size/version/preset, tham số và trial thật, selected descriptors/candidates, warnings, đơn vị, timing core.* cùng source_load/encode. debug=true ghi analysis/gray/blurred/overlay và edges/closed hoặc region_mask của từng trial; UUID/hash/size/mode trong metadata, không ndarray/path response. manual_required là200/cornersnull. Cổng publish kiểm owner/page/sourceID/dimensions còn khớp, không sửa config/confirmed/revision/timestamps; config đổi trong CPU vẫn giữ và source_revision là revision tại snapshot. File/metadata commit lỗi dọn đúng stage mới chưa tham chiếu. Run/stage tồn tại qua reopen.

**Truy xuất09.06 theo runID và metadata.artifacts**, không gom mọi debug cùng page/revision: nhiều detectionrun và renderdebug có thể cùng revision. Ở mốc09.01–02 chưa có GETdebug; hiện09.05–06 đã persist/render/debugGET, UIviewer đã nối09.07.

UI gửi debug=true, hiển thị loading/status/score **heuristic**/warnings/version/runID, góc chỉ vào draft confirmed=false; manual_required tạo inset5% để kéo tay. Không tự PUT/render/xác nhận, không tự retry. Operation/page-instance/editcounter chặn phản hồi muộn sau sửa góc/reset/đổi trang. Sai nguồn/dimensions/quad bị từ chối; source_revision khác persistedrevision yêu cầu đọc lại. Lỗi detect giữ draft để thử lại/chỉnh tay. Đổi góc bỏ thông tin proposal cũ. Đã kiểm proposed≈0.635, warning≈0.468 và blankmanual; img_004 vẫn ăn bàn, score khôngaccuracy. [Bằng chứng](progress.md).

## UI cấu hình xử lý — MVP09.03–04

FilterPanel dùng native select/range, không thêm dependency hoặc auto-preview/debounce. Chọn mode chỉ đổi mode trên fullconfignháp, không áp preset ngầm; giữ denoise/contrast/threshold/corners/rotation/geometry và inactivevalues. Kernel3/5 khóa khiNone; Color khóa contrast/CLAHE; Gray/Color khóa threshold; BWOtsu khóa block/C. CLAHEclip1..4/step0.1/grid8×8 cố định, Adaptiveblocklẻ3..151/Cnguyên−20..30. Backend PUT config vẫn parse lại cảinactive và blockfit với estimate_warp_size thật, khôngclamp/fallback.

Chỉnh processing giữ confirmed của vùng góc đã xác nhận; sửa góc mới bỏconfirmed. Mọi chỉnh sửa tăng editcounter, đánh dấu resultstale; không gọiHTTP. “Tạo bản quét” dùng fullconfigPUT/CAS rồi POSTrender revision vừa trả về. Một chuỗi đổi nhanh không tạo request trung gian; render xử lý nguồn normalized, không ảnh kết quả trước. Panel khóa khi busy/needsReload; stateguard vẫn giữ nháp mới nếu action đến trong lúc save/render/detect. Thay mode xóa noteproposal cũ, không thay nguồn/góc. Lỗi PUT giữdraft và cầnGET đối soát theo luồng hiện hữu, sau đó sửablock/chọnOtsu và xác nhận lại. [Bằng chứng](progress.md).

## Debug render và đọc provenance — MVP09.05–06

Mỗi POSTrender thànhcông trả `render_run_id` (trường bổsung nullable trong RenderRead để tươngthích DTO cũ; lượt mới luôncó). RenderRun ghi sourceartifact/SHA, full/previewartifactIDs, revision, UTC và metadata. `debug:false` mặcđịnh vẫn ghi run/config/version/timing/full-preview, `debug_persisted=false`, không giả stage/histogram. `debug:true` gọi core đúng một lần, lưu warp/filtered_bgr/before_rotation/prepared_gray nếu có cùngfull/preview, fullconfig/inactive/H/scan-v1/environment/timing/đơnvị. Color prepared_gray khôngápdụng. Tấtcả stage trướcxoay; full/preview sauxoay. Histogram chỉBW:256counts của chínhprepared_gray trướcthreshold/rotation, sum=W×H, source_png_sha256 của stage cùngrun, otsu/global/actualt hoặcadaptive/local/t=null. Color/Gray histogramnull với reasonmode_has_no_threshold; debugfalse reasondebug_not_requested.

CPU/encode trướctransactionpublish; writerlock vàsource/config/revision gate cũ giữ. Full/preview/stages/RenderRun commit cùngmetadata; lỗi ghi/INSERT/COMMIT dọn đúngfile mới chưathamchiếu. Không sửa config/revision/confirmed/timestamps, không replay filter để làmdebug. StagePNG dùng UUID riêng mỗi run; không gom mọi kinddebug cùngrevision. Histogramtiming nằmtrong core.enhance, không cộnglặp. Source_load đoverify/read/decode; encode đo full/preview/debug PNG; khôngcó timingpublication/commit giả.

GET `/sessions/{sid}/pages/{pid}/debug` nhận **tốiđa1selector**:

- `revision=R`: render mới nhất đúngrevisionR, tie created_atDESC/idDESC; **không lọc bỏ debugfalse để tìm debug cũ**.
- `render_run_id=UUID`: lấy chínhlượt render, phùhợp ghép với RenderRead của UI.
- `detection_run_id=UUID`: đọc đúngDetectionRun, giữ selected_trial/contours/descriptors/units/cảnhbáo và stagecủanó, kểcảmanual_required.
- Bỏcảba: render ởrevisionconfig hiệnhành. Khôngtựlấyrevisiontrước nếuhiệnhành chưa render.

DebugQuery extra/saimiền/saiUUID hoặc nhiềuselector→400INVALID_REQUEST; revisionlàchuỗisốnguyênkhôngâm≤2^63−1, khôngcoerce1.0/true. Owner/page lookup404; runkhôngcó/khácpage hoặc revisionkhôngcóvàkhôngphảihiệnhành→404DEBUG_NOT_FOUND. Currentchưa córun hoặc legacyfullchưa cóRenderRun→200not_recorded/metadata=null, khôngbackfillbằng xửlýảnh.

DebugRead có page_id/kind/current_revision/revision(render hoặcnull detection)/run_id/created_at/debug_persisted/metadata/artifacts/missing_stages. `artifacts` chỉchứarefs đãkiểmowner/kind/revision/SHA/dims vàfilehash; khôngpath. Metadata giữsnapshot đãlưu, khôngmerge configmới. Trạngthái: **available** (debugđãlưu/đủ), **not_requested** (run khôngbậtdebug), **not_recorded** (legacy/chưacórun), **incomplete** (thiếu/hỏng/wrongowner stage). missing_stages map name→not_found/invalid_metadata/file_unavailable, khônglấystagekháctrámvào; metadata.artifacts vẫn làthamchiếulịch sử, UI nên dùngenvelopeartifacts/missing_stages đểquyếtđịnhhiểnthị. DBbindingnguồn/runhỏng→500STORAGE_FAILED sanitize. GET không ghiDB, không lọc/warp/histogram/detect, xácminhfile ngoàiDBtransaction qua threadpool I/O hiệncó. ArtifactGET giữroutehiệnhành. [Bằng chứng](progress.md).

## Client viewer — MVP09.07–08

React render gửi `{expected_revision,debug:true}`. Client debug GET exact `render_run_id` hoặc `detection_run_id`, truyền AbortSignal; parser kiểm identity/artifacts và histogram trước hiển thị. Component sở hữu state theo page/run, không retry mutation. Đọc lại debug chỉ GET; mở JSON cũng cùng selector. Missing stage dùng envelope/missing_stages, giữ metadata refs như lịch sử; không lấy ảnh từ run khác.

Đổi tham số/góc không GET lại hoặc chạy CV cho detection cũ; detectionRun giữ để xem diagnostic, note proposal hiện hành vẫn bị xóa khi edit. Render cũ có nhãn snapshot/stale. Ở mốc09 chưa tự mở lại render;10.07 hiện đã phục hồi latest_render/latest_detection theo mục dưới. Chưa có UI liệt kê mọi run. Không thêm endpoint, schema hoặc thuật toán ở lượt viewer. [Audit09](audit-phase-09.md).

## Đổi tên và thêm trang — MVP10.01–02

PATCH `/sessions/{sid}` nhận `{title:string}` bắt buộc, trim hai đầu, dài1..200, từ chối null/sai kiểu/extra. Trả SessionRead200 sau commit; title đổi thì cập nhật session.updated_at, cùng title đã trim là no-op kể cả timestamp. Không nhận expected_revision vì chỉ sửa metadata tài liệu; không sửa page/config/revision/artifact/render/detection. Writer SQL trước lookup để tránh read→write upgrade race, concurrent rename tuần tự theo commit cuối. ID sai/không tồn tại404SESSION_NOT_FOUND; input400INVALID_REQUEST; commit lỗi500STORAGE_FAILED sanitized/rollback. Không thay schema3, không xử lý pixel hoặc tệp.

UI có “Đổi tên tài liệu”, form lưu/hủy/nhãn/focus và thông báo lỗi. Success cập nhật header/list cùng metadata, không reload/remount editor ảnh; không tự retry PATCH. Mất kết nối không chứng minh server chưa commit: dùng Tải lại để kiểm tra nếu chưa rõ tên đã lưu.

Upload HTTP vẫn mỗi request một file JPEG/PNG; UI chọn nhiều tệp và gửi tuần tự, một batch active đến khi GET đối soát xong. Lỗi một file không chặn file sau, file lỗi không tiêu thụ slot cục bộ. Trên20trang báo riêng các tệp dư không gửi; backend vẫn là quota cuối, kể cả client khác hoặc trạng thái cục bộ cũ. PAGE_LIMIT_EXCEEDED413 chặn phần còn lại của batch; không retry POST. Giới hạn15MiB/16MP/20trang và xử lý từ nguồn chuẩn hóa giữ nguyên.

Append không tự chọn trang vừa nhập khi đã có lựa chọn hợp lệ; tài liệu trống chọn trang thành công đầu tiên. GET detail cuối batch đối soát cả upload mất phản hồi sau commit, giữ page_id hợp lệ và dữ liệu server. Không tăng detailReload hoặc đổi key editor hiện hành, nên góc/mode chưa lưu và full/preview/debug đang xem vẫn còn. Điều này khác nút Tải lại chủ động; tự phục hồi render khi mở lại đã có10.07, xem mục dưới. Trong batch khóa đổi tài liệu/tạo mới/đổi tên/refresh; PageList vẫn cho chọn trang. Nếu GET đối soát thất bại, báo lỗi và khóa nhập mới đến khi Tải lại thành công, tránh tự gửi lại tệp chưa rõ kết quả.

Kiểm chứng: rename qua UI/API và restart thật; giữ page/config/revision/render/debug/hash. Thêm vào trang có render và draftGray vẫn giữ UUID kết quả/selectedpage; batch badJPEG415 và2ảnh tốt; mất phản hồi sau upload201 được GET tìm lại. Quota19→20: chỉ một POST, tệp dư báo lỗi; request21 trực tiếp413.12tài liệu/26trang/78hash nguồn cũ nguyên. [Progress](progress.md).


## Order, xóa và mở lại — MVP10.03–07

PUT `/sessions/{sid}/page-order` nhận `{page_ids:[UUIDv4,...]}` đúng toàn bộ tập ID hiện hành, tối đa20/duy nhất; tài liệu rỗng nhận[]. Sai schema400INVALID_REQUEST; thiếu/thừa/ngoài phiên400INVALID_PAGE_ORDER; phiên không có404SESSION_NOT_FOUND. Transaction lấy writer lock, gán các vị trí tạm không va chạm rồi0..n−1 và trả SessionDetail200 sau commit. No-op giữ mọi timestamp; order đổi chỉ cập nhật session.updated_at, không tăng page revision hoặc render lại. Không CAS order: cùng tập ID dùng thứ tự commit cuối, khác tập do append/delete bị từ chối. UI lên/xuống theo page_id; pending/mất response chỉ GET đối soát, không gửi lại mutation.

DELETE `/sessions/{sid}/pages/{pid}` và `/sessions/{sid}` trả204 thân rỗng. ID sai/owner sai/không tồn tại404PAGE_NOT_FOUND hoặcSESSION_NOT_FOUND theo lớp lookup; commit lỗi500STORAGE_FAILED sanitized/rollback. Page delete compact position, cập nhật session.updated_at; giữ page/config/revision/artifact của các trang khác. Session delete cascade toàn phiên. Tệp lấy từ DB/UUID server, không từ path/filename client. Sau commit, kiểm reference ID/path mới rồi verify/hash/unlink từng tệp, không recursive-delete. File đang mở/hỏng/crash/I/O lỗi có thể để orphan; log và không xóa tệp chưa chắc an toàn. Không có Trash/Undo/GC bền. Finalize render/detect/import kiểm owner dưới writer gate nên không publish vào owner đã mất.

PageRead có hai trường additive nullable: **latest_render** là RenderRead của revision lớn nhất đã có RenderRun (tie created_atDESC/idDESC), **latest_detection** là DetectionRunRead mới nhất (created_atDESC/idDESC), kể cảmanual_required/debugoff. Ràng buộc owner/sourceID/SHA/dimensions/revision/snapshot/full-preview pair; corrupt binding→500STORAGE_FAILED, không fallback run khác. Config mới hơn giữ render cũ với revision cũ để UI đánh stale. Legacy artifact chưa RenderRun→null; không bịa cặp full/preview hoặc backfill trong GET. GET detail chỉ đọc metadata, không đọc mọi PNG/không chạy CV/ghi DB; artifactGET/debugGET xác minh bytes khi truy cập. Missing debug refs không được thay bằng ảnh run khác.

UI khởi tạo draft từ persisted config, tự hiện ảnh full của latest_render, giữ latest_detection như diagnostic nguồn và chỉ GET debug theo exact run khi mở viewer. Không áp góc proposal, tự confirmed hoặc POST render khi reopen. Draft chưa lưu bị bỏ khi đổi trang/reload chủ động. PageList nhận mode/rotation/render revision persisted ngay sau lưu/render; xoay0/90/180/270° là explicit draft và dùng lõi rotation đã có, không phải auto-EXIF/hướng chữ. Modal xóa có hủy/Escape, cảnh báo không thể hoàn tác; xóa trang chọn thì chọn kế tiếp, nếu hết thì trang trước, hết trang thìnull; xóa trang khác giữ chọn. Xóa tài liệu chọn tài liệu còn lại hoặc empty state. [Audit10](audit-phase-10.md).


## Request và snapshot xuất — MVP11.01–02

ExportRequest/ExportRead đã có trongschemas/exports.py, đườngimport cũ qua sessions.ExportRequest giữ tương thích. Request pages là tập con có thứ tự xuất tường minh, không tựsort theo position; PDF1..20/PNG-JPG1/unique UUIDv4/exactrevision nghiêm ngặt. OptionsPDF vẫn validate/retain nhưng inactive với ảnh. Receipt định nghĩaid/session_id/artifact_id/format/pages/created_atUTC; khôngpath. Encoder/layout11.03–04 vàcommit/POST201/UI11.05–07 đã có; bytes tải quaartifactGET hiện hữu.

Ví dụ request PDF (ID minh họa):

```json
{"format":"pdf","pages":[{"page_id":"33333333-3333-4333-8333-333333333333","revision":2},{"page_id":"11111111-1111-4111-8111-111111111111","revision":1}],"paper_size":"a4","orientation":"auto","margin_mm":5,"image_encoding":"png"}
```

Service export_snapshot giữ lease quanh snapshot và writer; run_export reserve trước enqueue dùng sharedProcessingExecutor. Snapshot chỉ config persisted/confirmed/corners/exactrevision/fullRenderRun/source/SHA/pair hợp lệ, khôngpreview/draft/auto-render. Tất cả trang thiếu run đúngrevision được liệt kê trong409PAGE_NOT_RENDERED; stale409REVISION_CONFLICT, chưaconfirmed409PAGE_NOT_CONFIRMED, wrongowner404. Metadata/filecorrupt500STORAGE_FAILED, khôngfallback. Hash/path/sizefullPNG kiểm ngoài readtransaction.

Ví dụ lỗi thiếu render (endpoint export đã nối11.06):

```json
{"error":{"code":"PAGE_NOT_RENDERED","message":"Cần tạo bản quét đúng revision cho các trang đã chọn.","details":{"pages":[{"page_id":"33333333-3333-4333-8333-333333333333","revision":2}]}}}
```

Trong lease, rename/config/order/deletepage/deletesession/import/render/detect cùngsid→409SESSION_BUSY; GET/health và tài liệu khác hoạt động. Asyncupload/render/detect kiểm trướcCPUqueue; publish cũng kiểm lại khi việc đã bắt đầu trướcexport. Reserve đồng bộ với các transactionmutationngắn, khônggiữDBtransaction quaCPU. Descriptorfull bất biến/DBrefs/khóaowner giữtệp, khôngpin table/migration. Queuecancel/429/exception trảlease; activecancel giữlease/slot đếnthreadfinally. Khôngpersistbusy marker, Engine mới/restart khôngkhóa cũ. Chỉmộtprocess/mộtEngine choDB; khôngclaimđaUvicornworker. [Chi tiết/bằng chứng](export-snapshot.md).


## Encoder ảnh và bố trí A4 — MVP11.03–04

encode_snapshot_image(store,snapshot) chỉ PNG/JPG1page: đọc đúngfull descriptor dướilease, verify/hash/size/decodePNGmodeRGB-L/dimensions/sạchEXIF-ICC, chuyểnBGR/gray rồiencode. EncodedImagefrozen cópayload/mime/filenameASCIIleaf/width/height; khôngDB/filepublication. PNGpixel-exact/fullBW0–255, JPGquality95/subsampling0/RGB-L/lossy. PDFoptionsinactivevớiảnh, khôngresize/filter/xoaylại. Tênfile vật lý vẫnUUIDserver; filenameởđây chỉgợiýtảixuống, artifactGET giữContent-Dispositioninline/UUID server; UI dùngdownloadanchor đã tải thật11.07.

PDFpurelayout dùngA4portrait210×297mm/landscapeđảo,point=mm/25.4×72;autolandscape khiwidth>heightcủafullsauxoay, squareportrait; explicitoverride khôngxoaypixel. Lềfinite0..30;fit min availableWidth/W,availableHeight/H/cùngscale/căn giữa/khôngstretch-crop. append_pdf_page tạo1pageđầyđủ trênCanvas;encode_pdf_page trảPDFbytes một trang thật, image_encodingpnglossless hoặcJPEG95/0. PDFnhiềutrang/ExportRecord/route/UI đã có11.05–07, xem mục bên dưới. [Bằng chứng](export-encoding.md).


## Ghép/lưu và API/UI xuất — MVP11.05–07

POST /sessions/{sid}/exports → ExportRead201 chỉ sau khi file đã ghi hoàn tất và Artifact+ExportRecord commit cùng transaction; pages trong receipt/DB giữ đúng orderrequest. PDF lặp append_pdf_page trên fullpixels; ảnh dùng encode_snapshot_image. Service không sửa config/revision/order/session timestamp. Lỗi encode500PROCESSING_FAILED; storage/metadata/commit500STORAGE_FAILED sanitized; rollback/cleanup không xóa file đang reference. Sharedexecutor429 vàlease409 tháo theo lifecycle đã kiểm. Không thêm migration, path client hoặc download endpoint.

GET /artifacts/{aid} hiện hữu trả MIME PNG/JPEG/PDF, filename UUID extension tương ứng, Content-Dispositioninline/nosniff/private-no-store. Link UI có thuộc tính download; browser đã tải cả ba định dạng thật, filename server được ưu tiên. Receipt không có filename/path. Thiếu idempotency nên network/unknown outcome không tự POST lại.

Client đọcmetadata/exactR/confirmed trước export; dirty selected bịchặn, dirty ngoài selection được giữ. Chỉ definitive409PAGE_NOT_RENDERED kèm details.pages hợp lệ mới GET kiểm lại → render thiếu đúngrevision → POST lại đúngrequest một lần. Không PUTconfig/auto-confirm, không thử lại lần hai hoặcretry429/network. Pending khóa mutationUI vàlate/unmounted response bịbỏ. [Chi tiết kiểmchứng](export-workflow.md).


## Nghiệm thu export hoàn chỉnh — MVP11.08

16APItests hiệncó bao5tests mới:actualPOSTblockedqua barrier/thànhcông-lỗigiữaPDF,8mutation+secondexport409SESSION_BUSYtrướcCPUqueue/DBpublication;GET/health/tàiliệukhácvẫndùngđược. Khi lỗiởpage2khôngfile/ExportRecorddở;response500PROCESSING_FAILEDsanitized vàexportsauthànhcông. Baformatđãcommitgiữnguyênreceiptpages/byteskểcảconfigsangrevision2vàđóng/mởapphai vòngđời liêntiếp;exportmớidùngR2,khôngđổitệpcũ. Physicalrestartprod vàUI3trang/4downloadthật cũngđãkiểm;khôngthayHTTPcontract/schema3. Cổng11/M3đạt. [Chi tiết](audit-phase-11.md).


## Tự nhận diện sau nhập — AUX11.02

Frontend gửi POSTpages cho từng ảnh rồi POSTdetect(debug=true) đúng trang vừa nhập, tuần tự; không đổi upload endpoint/DTO/status/quota hay thêm API. Detect lỗi không hoàn tác trang đã nhập và không tự retry upload. GET đối soát/hook mở trang dùng latest_detection đúng nguồn/revision0 để nạp proposal vào nháp nếu persistedcorners=null/confirmedfalse và chưa sửa; không PUTconfig/auto-confirm/render. Góc đã lưu/nháp đang chỉnh luôn được giữ. Manual detect vẫn có để thử lại. [Chi tiết/bằng chứng](auto-detect-on-import.md).
