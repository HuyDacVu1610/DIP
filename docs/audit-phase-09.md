# Rà soát tám task giai đoạn 09 — AUX09.01

Ngày 18/10/2026. Theo yêu cầu hoàn thành MVP09.07–08 rồi dò lại cả tám task. Đối chiếu [MVP](MVP_Pham_Vi_Va_Ke_Hoach_4_Tuan.md), [checklist](../tasks/todo.md), [kế hoạch](../tasks/plan.md), [hợp đồng ảnh](image-contract.md), [API](api-contract.md), [phân tích thuật toán](Phan_Tich_Huong_Thuat_Toan_Tu_Tai_Lieu.md) và [smoke](../frontend/tests/scanner-smoke.md).

## Kết luận

**Tám task, checkpoint 09-C1/C2 và cổng 09 đạt trong phạm vi đã chốt.** Luồng nhận diện → kiểm tra/sửa → xác nhận → chọn mode → render sử dụng lõi thật. UI xem được các stage đã lưu, histogram trước threshold và mô tả ứng viên của đúng run. Không có thay đổi thuật toán, dependency hoặc schema trong MVP09.07–08.

Kiểm thử luồng và truy vết không chứng minh detector luôn chọn đúng trang. Nợ img_004/006, sáu ảnh development cùng một tờ giấy, test độc lập bằng 0 vẫn giữ. Tính năng quản lý trang tiếp ở giai đoạn 10, xuất ảnh/PDF ở 11; tự mở kết quả cũ khi mở lại tài liệu thuộc MVP10.07.

## Ma trận nghiệm thu

| Task | Mã và bằng chứng | Kết luận |
|---|---|---|
| 09.01 API detect | `services/detections.py`, DetectionRun/schema2, route/executor và loader nguồn dùng chung. Owner/revision/source binding, manual_required200, rollback và migration đã kiểm trong suite. Evidence 09.01–02 có 11 run/118 stage; lượt mới chạy proposed, manual_required và warning trên ba nguồn riêng | Đạt |
| 09.02 đề xuất trên UI | Client/hook/SourcePreview chỉ đưa góc vào nháp, confirmed=false; không tự PUT/render. Fallback5% không được gọi là kết quả detector. State tests giữ mode/inactive, chặn late/edit/reset/unmount và sai nguồn. Browser mới xác nhận rồi render ảnh tốt; ảnh trắng không bịa descriptor; img_004 giữ cảnh báo | Đạt |
| 09.03 mode và lọc | FilterPanel Color/Gray/BW, None/Median/Gaussian, kernel, CLAHE; full config/CAS và inactive fields được giữ. Browser mới đổi Color→Gray→BW; evidence 09.03–04 có 17 ca UI, 9 full/preview khớp core chạy mới từ nguồn và Color round-trip bằng byte | Đạt |
| 09.04 Otsu/Adaptive | UI method/block/C, chỉ render khi bấm; không tự clamp/fallback. Evidence trước có biên3/151 và C−20/30, warp nhỏ từ chối block quá lớn. Lượt mới thực hiện Otsu→Adaptive51/C10/CLAHE→Otsu, giữ quad; histogram phản ánh snapshot thật | Đạt |
| 09.05 persist debug render | RenderRun/schema3, mỗi render một UUID; capture một lần các buffer thật, histogram BW gắn prepared_gray/hash, commit cùng artifacts. Debugfalse vẫn có run cơ bản, không ghép stage cũ. Full suite có debug parity, publish rollback, v1/v2 migration và lịch sử cùng revision. Evidence 09.05–06: 5 JSON nguyên sau restart, 36 artifact hash, 2 histogram NumPy | Đạt |
| 09.06 GET debug | Strict selector revision/render_run_id/detection_run_id, owner/source/ref validation; available/not_requested/not_recorded/incomplete. GET không chạy CV hoặc ghi DB. Tests query400/owner404/corrupt500/missing stage. Browser mới luôn GET exact run; giả lập phản hồi sai run bị chặn, lỗi GET cho đọc lại | Đạt |
| 09.07 viewer/histogram/descriptors | PipelineViewer/HistogramView/CandidateMetrics/pipelineData/debugState. Từng số, cạnh, góc radian, thành phần score và trial đối chiếu JSON; stage qua UUID envelope và kiểm natural dimensions. 256 bin dùng counts trước threshold; Otsu có actual t, Adaptive không có t global. GET cũ bị abort/sequence guard; render stale và detection nguồn được phân biệt; thiếu dữ liệu không thay bằng 0 hoặc ảnh khác | Đạt |
| 09.08 giải thích | `pipelineExplanation.ts`, phần hướng dẫn trên UI và [algorithm-notes](algorithm-notes.md). Mục đích/tham số/giới hạn gắn với stage/config thật; phân biệt phát hiện, biểu diễn, mô tả, đặc trưng vùng, chọn ứng viên. Đối chiếu ba PDF môn học: DP khác MPP, findContours không tự gán Moore, góc phối cảnh không cần90°, homography không dewarp giấy nhàu | Đạt |

## Bằng chứng mới

Evidence cục bộ ignored: `experiments/results/mvp09-final-verified/`. Có seed, before/after, requests, 27 bản ghi trạng thái UI, layout, console, ảnh giao diện, raster-checks và verification. Harness tạm đã lưu bản sao trong evidence rồi gỡ khỏi frontend. Các lỗi `500`, missingstage, histogram sai tổng, descriptor thiếu và wrongrun là **phản hồi chủ động sửa trong harness**, không phải lỗi backend quan sát được. Ca giữ GET dùng dữ liệu thật, chỉ trì hoãn thời điểm trả về; thả cả GET cũ/mới vẫn hiển thị run mới.

- **11 run/81 artifact** được tải lại qua API, kiểm SHA-256/dimensions/PNG; không dùng ảnh minh họa thay stage. **6 histogram** đối chiếu đủ256bin bằng `numpy.bincount` từ PNG prepared_gray, tổng bằng W×H; before_rotation xoay đúng ra full. Hai bộ descriptor kiểm lại e=Σm/Σn và S từ a/e/f/b. Trong 11 run có cả hai run được giữ GET và run của tab sản phẩm sạch; không tính phản hồi bị sửa lỗi là bằng chứng pixel thật.
- Ảnh tốt: analysis612×460, P=979.6984843015671px, nQ=4, a=.20313832054560954, f=.9842689087200847, e=.9898373983739838, b=0, S=.6347091154204355. Hỗ trợ bốn cạnh102/102,139/144,102/102,144/144; góc đổi hướng khoảng1.568729/1.572839/1.573729/1.567889rad. UI chỉ làm tròn để hiển thị.
- img_004: P=5417.475508213043 analysis px, a=.3907037037037037, e=.304282494365139, S=.4683515931077459, nhánh vùng/cảnh báo vẫn còn. Đây là diagnostic cho trường hợp dính nền, không phải nhận diện đúng đã được chứng nhận.
- Ảnh tốt Otsu/không CLAHE: prepared_gray201×285, tổng57.285, t=247. Adaptive51/C10/CLAHE có cùng dimensions/tổng nhưng t=null. Ảnh chữ/highlight toàn nguồn1199×1599: tổng1.917.201, Otsu t=163; khác165 của run Median trước do config khác, không ép hai ngưỡng bằng nhau.
- Bảo toàn **11 tài liệu/22 trang/66 hash nguồn cũ**. Không reset DB, thay nguồn hoặc gửi ảnh ra ngoài. Core/CLI/requirements khớp hash mốc M1; schema3/9 OpenAPI paths/10methods giữ nguyên.
- Responsive320/768/1440: document không tràn ngang, SVG giữ256bin, grid một/hai cột phù hợp. Console sản phẩm không có warning/error. Viewport đã reset; tab sản phẩm giữ lại ở ảnh chữ và histogram.

## Kiểm thử và rà mã

Backend đầy đủ: **1031passed181.84s**, `-W error --tb=short`, basetemp `.tmp/pytest09-final-audit`. Frontend: **76passed346.4371ms**; typecheck/build33modules262ms, JS282.67kB/gzip87.90, CSS11.48kB/gzip2.91. Không bỏ test, nới assertion hoặc suppress warning để đạt kiểm thử.

TDD: client test ban đầu phát hiện render chưa gửi debugtrue; test cần parser/state mới chưa có; test giữ detection diagnostic sau sửa draft ban đầu thất bại. Sau triển khai đều xanh. Năm test mới bao phủ run/source/revision/artifact binding, histogram/scope/hash/sum, score thiếu trường, superseded/unmounted GET và error/retry. Test hiện hữu thêm giữ diagnostic; API wire test kiểm hai query exactrun và AbortSignal.

Rà correctness/readability/boundary/security/performance: dùng client/artifact route và hook editor hiện hữu; phần JSON được kiểm tại parser, UI tách ảnh/histogram/descriptors/explanations. GET lazy khi mở details, không retry mutation hoặc chạy render để lấy debug. Unknown metadata không được biến thành số0. Stage refs lấy từ envelope, histogram giữ provenance lịch sử. Giữ detectionRun riêng giúp giải thích proposal dù người dùng đã chỉnh góc; note xác nhận vẫn theo draft hiện hành. Không thêm cache, thư viện đồ thị hoặc public file path.

## Nợ và bàn giao

Nợ thuật toán trong [audit05](audit-phase-05.md)/[revision01](detection-revision-01.md) còn mở: epsilon toàn contour có thể cắt mép yếu, fit diện tích chưa đo sát biên, bàn sáng/khung lớn dễ đạt score. Hướng thử khi có nhiều tài liệu/GT: khoảng cách contour–cạnh, kiểm hỗ trợ riêng cạnh yếu và phân tích nền/khung; đo trên development, khóa version trước test. Không đổi trọng số dựa trên duy nhất doc_01, không ép90° hay thêm dewarp tùy tiện. Người dùng vẫn sửa và xác nhận góc tay để khắc phục vùng sai.

**71 task chính +9AUX hoàn thành**, giữ110 ID chính/109 active/1skip/5optional. AUX09.01 chỉ ghi yêu cầu rà soát này. Next **MVP10.01**; chưa nghiệm thu quản lý/xuất tài liệu đầy đủ, OCR, hướng đọc tự động, độ chính xác tổng quát hay phần tự viết Otsu giáo dục.
