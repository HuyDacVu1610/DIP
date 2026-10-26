# Xuất tệp qua API và UI — MVP11.05–07

Ngày18/10/2026. Ba task này đạt; checkpoint11-C2 đạt. MVP11.08/AUX11.01 và cổng11/M3 hiện đạt; xem [audit8task](audit-phase-11.md). [Checklist](../tasks/todo.md), [snapshot/lease](export-snapshot.md), [encoder/A4](export-encoding.md), [API](api-contract.md), [bằng chứng](progress.md).

## Ghép và lưu

Service publish_export nhận snapshot bất biến trong lease của export_snapshot/run_export. PDF dùng một Canvas, lần lượt đọc đúng full PNG của từng trang và append_pdf_page theo thứ tự request. Mỗi trang dùng mode/rotation đã render; không xoay, threshold hoặc warp lại trong export. PNG/JPG dùng encoder ảnh đơn hiện có. Không dùng thumbnail/preview.

Chỉ khi encode xong toàn bộ payload mới gọi ArtifactStore.write_bytes. Store ghi tệp tạm, fsync rồi publish UUID không ghi đè. Transaction ngắn sau đó lấy writer lock, kiểm owner/revision/config/full reference, đăng ký Artifact và ExportRecord cùng một commit. Receipt chỉ trả sau commit; GET artifact không thể tìm UUID mới qua DB trước commit. ExportRecord lưu chính mảng page_id/revision có thứ tự đã yêu cầu. Export không đổi config, revision, vị trí trang hoặc timestamp tài liệu.

Nếu encode/ghi/đăng ký/commit lỗi, transaction rollback; dữ liệu cũ giữ nguyên. Nếu đã có tệp output mới, cleanup kiểm nó không còn được DB tham chiếu rồi chỉ xóa đúng tệp đó. Cleanup lỗi được log, có thể để orphan sau crash/I/O; filesystem và SQLite không có transaction chung hoặc GC bền. Lease/slot được tháo theo finally hiện hữu; không đánh dấu thành công khi commit chưa xong.

## API

POST /api/v1/sessions/{sid}/exports nhận ExportRequest, trả ExportRead201 gồm id, session_id, artifact_id, format, pages và created_at. Tải bytes qua GET /api/v1/artifacts/{artifact_id} hiện hữu; MIME đúng PNG/JPEG/PDF, nosniff và private/no-store, filename vật lý UUID server. Không có endpoint nhận đường dẫn tệp từ client hoặc migration mới. OpenAPI hiện12path/15method, SQLite schema3.

Request giữ exact revision và ordered subset: PDF1..20trang, PNG/JPG đúng1trang. A4/orientation/margin0..30mm/image_encoding được validate như contract đã chốt. Shared executor một active/hai waiting và lease dùng chung render/detect/import; quá tải429PROCESSING_BUSY, cùng phiên đang xuất409SESSION_BUSY. Trang chưa xác nhận409PAGE_NOT_CONFIRMED; thiếu run đúng revision409PAGE_NOT_RENDERED với details.pages; stale409REVISION_CONFLICT; owner sai404. Encoder lỗi500PROCESSING_FAILED, metadata/file/DB lỗi500STORAGE_FAILED; thông tin nội bộ không trả client.

Không tự retry POST khi timeout/mất mạng hoặc kết quả chưa rõ. Chưa có idempotency key hay UI lịch sử export; mất response sau commit có thể để một tệp đã lưu mà UI chưa nhận receipt. Người dùng có thể chủ động xuất lượt khác, tạo record mới. Lease chỉ bảo đảm một backend process/một Engine cho DB cục bộ.

## UI

Panel Xuất tài liệu nằm dưới nhập ảnh. Checkbox chọn tập con; thứ tự xuất theo danh sách trang hiện hành. Dùng nút lên/xuống đã có để đổi thứ tự trước xuất. PNG/JPG yêu cầu chọn một trang. PDF có hướng A4 tự động/dọc/ngang, lề mm và ảnh nhúng PNG/JPEG. Lựa chọn mới/revision mới/nháp được chọn làm bỏ link kết quả cũ trên panel.

Client đọc lại metadata để kiểm membership/revision/confirmed trước POST. Không tự lưu nháp, xác nhận góc hoặc đổi expected_revision. Trang đang chọn có nháp chưa lưu bị chặn; nháp của trang ngoài tập xuất được giữ nguyên khi GET đối soát sau export. Lúc pending khóa nhập/đổi tên/sắp xếp/xóa/chỉnh góc/filter và chuyển tài liệu; vẫn đọc được nội dung. Chặn double click bằng pending ref.

Chỉ lỗi409PAGE_NOT_RENDERED hợp lệ mới kích hoạt phục hồi: kiểm details.pages là tập con duy nhất đúng page/revision của request, đọc lại metadata, render tuần tự các trang thiếu đã xác nhận rồi POST lại đúng snapshot một lần. Lỗi lần hai, stale, 429, network hoặc danh sách thiếu không hợp lệ được hiển thị; không lặp vô hạn. Không sửa cấu hình hay tự nhận proposal detector. Phản hồi sau unmount bị bỏ.

Khi có receipt hợp lệ, link Tải dùng artifact GET và thuộc tính download của trình duyệt. Trình duyệt kiểm chứng ưu tiên filename UUID từ Content-Disposition của server, có đúng extension; tên gợi ý ở client/encoder không phải đường dẫn lưu. PDF là ảnh, không có OCR/tìm chữ. JPG nén mất dữ liệu; PNG thích hợp để giữ nét.

## Kiểm chứng thực

18 backend tests mới: ba định dạng/commit/ordered snapshot, lỗi encode/write/register/commit giữ dữ liệu cũ, request sai/stale/chưa confirmed/missing/foreign, 429/worker recovery, export đồng thời/rename busy/health. Full1194tests với -W error đạt195.83s. Frontend95tests đạt252.9859ms, typecheck/build đạt; tám tests mới kiểm wire contract/details, bounded missing-render recovery, stale/config changed, malformed reply, network/429 và late response.

Tài liệu QA riêng dùng ba ảnh tổng hợp1120×1600 in PAGE1/2/3: Color0°, Gray90°, BWOtsu180°, revision1/1/2. UI ban đầu chặn trang3 chưa xác nhận; sau thao tác xác nhận rõ ràng, export409 → render đúng trang2+3 còn thiếu → retry201. Trang1 không bị render lại. Đã bấm tải PDF/PNG/JPG thật vào Downloads rồi sao chép evidence local.

Hai PDF ba trang đã đọc bằng Pypdf, render cả6trang bằng Poppler và xem contact sheet: UI order[1,2,3], API order[3,1,2]; mọi XObject trùng từng pixel full render, MediaBox/A4 auto và placement matrix đúng, không xoay pixel lần nữa. Full Color/BW1119×1599, Gray1599×1119. PNG trang3 modeL trùng full từng pixel (MAE0); JPEG Color modeRGB cùng dimensions, MAE0.0829946032/255 trên ảnh tổng hợp này, không phải số đo accuracy.

Browser kiểm chọn subset, dirty selected bị chặn, dirty unselected giữ270° sau xuất JPG; responsive320/768 không tràn. Rà console phát hiện UploadPanel/ExportPanel trùng key cùng document.id, đã sửa prefix export và chạy lại tab sạch: không warning/error. Không thêm test chỉ soi chuỗi JSX. Build39modules186ms, JS298.11kB/gzip92.09, CSS12.88/gzip3.22.

Evidence ignored tại experiments/results/mvp11-05-07-verified/: runtime-checks.json, browser-checks.json, pdf-inspection.json, product-verification.json, các tệp tải/full/render/contact-sheet/export-ui. Bốn record đầu đối chiếu DB đủ ordered snapshot; các lần xuất lại khi rà UI tạo thêm record riêng. Giữ nguyên14tài liệu/49trang/147hash nguồn và mọi hàng SQL đã có, FKcheck rỗng; core/CLI/requirementsM1 không đổi. Dataset6development/1doc_01/test0 và nợ detectorimg004/006 giữ nguyên.

Mốc11.05–07 chưa tích cổng11/M3. Từ11.08 đã kiểm chứng cuối/restart/lifecycle/rà8task và đạtM3;1199backend-Werror/95frontendtests/typecheck/build. [Audit8task](audit-phase-11.md), nextMVP12.01.
