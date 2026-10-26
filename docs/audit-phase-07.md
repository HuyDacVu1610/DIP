# Rà soát chín task giai đoạn 07 — AUX07.01

Ngày:17/10/2026. Người dùng yêu cầu làm task7–9 rồi rà đủ9task, theo cách các giai đoạn trước. Nguồn: [checklist](../tasks/todo.md), [kế hoạch](../tasks/plan.md), [phạm vi MVP](MVP_Pham_Vi_Va_Ke_Hoach_4_Tuan.md), [đặc tả gốc](../Document_Scanner_Dac_Ta_Kien_Truc_Thuat_Toan.md) mục4–7/9.1/10, [API](api-contract.md), [hợp đồng ảnh](image-contract.md), [M1](milestone-m1.md).

## Kết luận

**Cả9task đạt tiêu chí MVP; checkpoint07-C1/C2 và cổng07 đạt.** Luồng thực đã nối React → HTTP multipart → executor chung → normalize/encode → tệpUUID/SQLite → artifactGET → thumbnails/nguồn. Tạo/mở tài liệu, nhập nhiều ảnh tuần tự, báo lỗi từng ảnh và mở lại sau refresh/restart đã kiểm bằng trình duyệt thật. Không còn lỗi mới chặn giai đoạn08.

Đây là luồng nhập và xem nguồn đã lưu. Chỉnh/xác nhận góc, render qua UI và CAS/revision ở giai đoạn08; detector/debugUI ở09, sắp xếp/xóa/đổi tên ở10 và xuấtPDF ở11. Chưa đạt M2 quét tay qua UI. Nợ detector img_004/006 ăn bàn, khung giả và dataset6ảnh/1tài liệu development/test0 giữ nguyên; việc nhập ảnh không sửa thuật toán.

## Ma trận chín task

| Task | Đối chiếu mã và bằng chứng nghiệm thu | Kết luận |
|---|---|---|
| 07.01 schema API | schemas common/pages/sessions/errors; UUIDv4/UTC/full config/revision/error,21tests; PageRead kiểm config theo dimensions nguồn thật. TypeScript có Quad4điểm và enums preset; OpenAPI5paths đúng implementation, uploadfilebinary/multipart và artifactbinary, không422 giả | Đạt |
| 07.02 SQLite | database/models/repository,6bảng/schema_version1/FK mọi connection/deferred ownership/sourcepointer;19tests khởi tạo/reopen/rollback/cascade/version. DB runtime thực giữ session/page/config/artifact sau tiến trình backend mới | Đạt |
| 07.03 tệp an toàn | ArtifactStore UUID/temp cùng filesystem/fsync/no-overwrite/verify bytes+hash;19tests gồm partialwrite/fsync/rename/collision/junction. Upload filename traversal không tạo path tùy ý; artifactGET từ chối file bị đổi bytes. Metadata chỉ đăng ký sau file hoàn tất | Đạt |
| 07.04 API tài liệu | POST/list/detail SQLite thật;18APItests title/UTC/order/membership/pagination/errors/commitrollback. UI tạo tài liệu rỗng và chọn/mở tài liệu đã lưu; không lộ path trong DTO | Đạt |
| 07.05 service nhập | import_page giữ originalbytes, normalizedPNG sauEXIF/alpha và thumbnail320, configrevision0/confirmedfalse.14tests gồm skinny1pixel thumbnail, lỗi encode/write/commit, session bị xóa và haiimport tranh suất20; không mất trang cũ/orphan do lỗi thường | Đạt |
| 07.06 executor | Một app.state.processing/lifespan, một worker/haiwaitingFIFO,5tests cancel/error/shutdown/health. Ca audit mới gọi **route upload sản phẩm** khi queue đầy:429, không tạo trang và health vẫn phản hồi; trước đó task06 đã kiểm worker vật lý và giữslot sau activecaller cancel | Đạt |
| 07.07 upload/artifactGET | api/pages.py/artifacts.py, bounded multipart/bytecounter không tinContent-Length, tối đa1file/0textfield, MIME theo decoder.20HTTPtests JPEG/PNG/EXIF/alpha/corrupt/multiframe/16MP/15MiB/20pages/traversal/malformed/commit/429; artifactGET kiểm owner/path/regularfile/bytes/hash/MIME/nosniff, không publicdata | Đạt |
| 07.08 UI nhập/chọn nguồn | client/types/ScannerPage/UploadPanel/PageList/SourcePreview; React localstate/nativefetch, không dependency mới. Browser filechooser chọn EXIF6→fakeJPG→alphaPNG:2trang đúng thứ tự, lỗi ở giữa được báo và không mất ảnh hợp lệ. Chọn trangEXIF thấy64×96; ảnh thật img_004 thấy1536×2048 và hash nguồn khớpmanifest | Đạt |
| 07.09 refresh/restart | UI giữ session/page bằng query URL; refresh vẫn chọn đúng trang. Dừng backendv1 bằng graceful shutdown, UI refresh báo lỗi; mở tiến trìnhv2 cùngdata, bấmTảilại mở đúng tài liệu/nguồn. So snapshot JSON của2page và6blob hashes trước/sau: tên/order/config/revision/IDs/dimensions nguyên; fakeJPG không được persist | Đạt |

07.07 chia a/b do7tệp implementation/tests;07.08 chia a/b do8tệp. Task con không cộng lại tổng chính. AUX07.01 là đúng một task rà soát ngoài9task giai đoạn, do người dùng yêu cầu.

## Bằng chứng đã chạy

- Backend: **916tests đạt**;117ca của giai đoạn07 nằm trong suite này (21schema+19DB+19file+18sessionAPI+14import+5executor+20importAPI+health). Số test không phải accuracy của detector. Lệnh/thời gian cuối xem [progress](progress.md).
- `npm.cmd run build` chạy typecheck rồi Vite thành công.21modules; JS230.23kB/gzip72.30kB, CSS6.07kB/gzip1.81kB. Bổ sung kiểu Quad/enum không đổi output runtime/hash build. Không cài dependency, không thay thuật toán hoặc quota để vượt kiểm thử.
- `experiments/results/mvp07-07-09-verified/`: before-restart.json/verification.json cho2trang/6file qua **API sản phẩm**, browser-proof.json/responsive.json và ảnh UI. Data thực ở `data/scanner.sqlite3`/sessions; tất cả ảnh/DB/results/.tmp ignored.
- `real-source.json`: ảnh development img_004 được nhập qua API sản phẩm vào tài liệu riêng, sourcePNG hash khớp manifest. Browser xem nguồn1536×2048. Đây là xem nguồn, không detector/warp/render; ca restart chính dùng EXIF/alpha ở tài liệu kiểm chứng riêng.
- Browser: viewport320/768/1024/1440px, không tràn ngang; nguồn thật tải1536×2048 ở cả4size. KeyboardTab từ ô tên đến nútTạotài liệu, focus outline rõ. Inputs cólabel/buttons cótên; console cuối khôngerror/warn. Đây là kiểm tra cơ bản, chưa phải chứng nhận WCAG hoặc kiểm screenreader độc lập.
- Request thật được kiểm bằng luồng UI, HTTPtests và snapshot/artifactGET; không sửa DOM hoặc gọiAPI qua browser evaluate để giả thao tác. Ảnh fixture chọn bằng filechooser của browser. Filechooser phản hồi chậm bất thường trong một lượt; các bước sau chạy bình thường. Không dùng thời gian đó làm số đo hiệu năng app.

Ảnh minh chứng sau restart:

![UI mở lại nguồn EXIF](../experiments/results/mvp07-07-09-verified/browser-reopened.jpg)

Ảnh nguồn thực trên UI:

![UI nguồn img_004](../experiments/results/mvp07-07-09-verified/browser-real-source.jpg)

## Các lỗi phát hiện và xử lý

1. **Multipart thiếu boundary kết thúc có thể để spool file chưa đóng.** Test giữ handle của SpooledTemporaryFile để phát hiện leak đãRED. Chuyển kiểm kết thúc stream vào vòng parse được bảo vệ của Starlette; exception đóng cả file chưa được đưa vàoFormData. Ca test chuyểnGREEN, giữ-Werror; không dựaGC hoặc suppresswarning.
2. **Reload sau batch có thể làm mất danh sách lỗi từng ảnh.** Giữ component tài liệu hiện tại khi chỉ refresh metadata, không unmount UploadPanel; kết quả3file vẫn hiển thị sau đồng bộ. Đổi tài liệu vẫn tách state bằng UUID; kết quả batch chỉ là state UI, không được hứa persist qua refresh trình duyệt.
3. **Bấm lại tài liệu đang mở có thể xóa lựa chọn trang mà không fetch lại.** Chỉ reset lựa chọn khi UUID tài liệu thay đổi; browser bấm lại docimg_004 vẫn thấy ảnh nguồn. Các requestGET cũ cóAbortController để không ghi đè lựa chọn mới.

Lỗi1 có regressiontest executable. Lỗi2–3 được kiểm qua luồng browser thật; không thêm testframework frontend mới chỉ để kiểm wiring UI của giai đoạn này.

## Ranh giới và nợ còn lại

- Upload đọc request stream có cap15MiB+64KiB cho multipart envelope, rồi đếm riêng bytefile theo chunk64KiB với cap15MiB. Chặn2file/textfield/bodymalformed/thiếuend; không tinfilename/clientMIME/Content-Length. Đây là quota từng request, không là giới hạn tổng số kết nối upload đồng thời. Mộtworker/haiwaiting giới hạn tác vụ xử lý ảnh; ảnhbody được parse trước submit.
- ArtifactGET join session/pageowner, kiểm descriptor/path/root và hash trước FileResponse. App localhost không có tài khoản; không suy ra đây là authorization đa người dùng. Root runtime tin cậy; chưa chống tiến trình OS thay file đồng thời giữa verify/serve.
- Không có transaction chung filesystem+SQLite/GC saucrash. Lỗi thường dọn descriptor mới không tham chiếu; nếuDB/disk không cho cleanup thì log/giữ lỗi gốc, tránh xóa mù. Không cam kết phục hồi sau mất điện.
- Hủy caller sau khi thread bắt đầu không ngừng computation hoặc tự rollback commit. POST không auto-retry; networkerror nhắc tải lại tài liệu để kiểm trước khi thử lại. Shutdown bình thường đợi active; không hard-kill thread hoặc job persisted.
- Config còn draft: confirmedfalse/cornersnull/revision0; không auto-confirm vì ảnh đã được lưu. SourcePNG là nguồn hình học duy nhất; thumbnail chỉ hiển thị. Không dựng fullrender giả, không gọi lại decoder upload cho PNG nguồn nội bộ vượt15MiB.
- Production build đã sinh được, nhưng phục vụ static cùngorigin từFastAPI/đónggói ở14.01 còn chờ. Hiện chạy Viteproxy/FastAPI localhost theoREADME. Không CORS/LAN/cloud/deploy mới.

## Bàn giao

**53task chính+7AUX**,110IDgốc/109active/1skip/5optional; MVP01.08 vẫn bỏ qua. Cổng07 đạt. Bước tiếp theo **MVP08.01 — API cập nhật fullconfig, góc/confirmed và revision/CAS**; sau đó mới render tay qua UI. Đọc [image-contract](image-contract.md) và [APIcontract](api-contract.md) trước nối. Không dùng cổng07 để chứng nhận detector, hiệu quả threshold hay PDF.
