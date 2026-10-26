# Checklist triển khai Document Scanner MVP

Ngày lập:10/10/2026. Cập nhật:26/10/2026. MVP01.01–07, 02–11 và 13–14 xong: **102 task chính, 13 AUX**; MVP01.08 bỏ qua. M4 kỹ thuật đạt26/10/2026: bản chạy cùngorigin localhost8000, sourceZIP/manifest/checksum, cài sạch đúnglock/1.279backend-experiments+103frontendtests/typecheck/build, README/hướng dẫn/báo cáo sốliệu thật vàdemo5–7phút đãkiểm. RehearsalUI sau nhập5phút21giây, PDF3trang/restart65artifact đạt; chưa có lượt tập nói hoặc thủ tục nộp hành chính. Đã rà đủ8task14/AUX14.01; giữlõiảnh/preset/lock/manifest/nhãn/frozen13, chỉ sửa một dòng chú thích dataset trênUI. Giai đoạn12 còn7task chưa nghiệmthu và5optional chưa làm; không tựtích theo cổng hồi quy trước khóa. Giữ ca sai development và giới hạn mỗi split một tài liệu. [Bằng chứng](../docs/progress.md), [hợp đồng](../docs/image-contract.md), [API](../docs/api-contract.md).

Phạm vi: [MVP đã chấp nhận](../docs/MVP_Pham_Vi_Va_Ke_Hoach_4_Tuan.md). Thứ tự, rủi ro và mốc: [kế hoạch thực hiện](plan.md).

**Tổng hiện hành: 14 giai đoạn, 109 task chính cần thực hiện; 1 task bỏ qua; 5 task tùy chọn.** Giữ 110 ID task chính ban đầu để truy vết, không đánh số lại. Các checkpoint là điểm kiểm tra, không cộng vào số task. ID MVPxx.yy độc lập Pxx.yy của bản kế hoạch gốc.

MVP01.05 được tách thành **2 task con**, dùng hậu tố a/b và theo dõi ngay dưới task cha. Chúng phân chia việc của task cha, không cộng lại vào tổng task chính.

Có13AUX ngoài109task chính/5optional: AUX02.01,03.01,04.01;05.01–02;06.01;07.01;08.01;09.01;10.01;11.01–02 và14.01. AUX14.01 do user yêu cầu rà8task14 ngày26/10. Giữ110ID gốc; task con không cộng lại parent.

## Cách sử dụng

- Mỗi task có một đầu ra nhỏ, điều kiện nghiệm thu, kiểm chứng, phụ thuộc và tệp dự kiến. S: 1–2 tệp; M: 3–5 tệp. Nếu lúc làm cần >5 tệp hoặc >một phiên tập trung khoảng 2 giờ, tách thêm task con và cập nhật số lượng.
- Làm 2–3 task liên quan mỗi phiên; ghi bằng chứng và lỗi vào docs/progress.md. Có thể làm task độc lập sớm khi phụ thuộc đã đủ.
- Chỉ tích ô sau khi đạt Xong khi và đã chạy Kiểm chứng. Không coi mock, file rỗng hay ý tưởng là hoàn thành.
- Tên tệp/lệnh ở đây là dự kiến. Đọc code thật khi triển khai; cập nhật task nếu cấu trúc thay đổi. README sẽ ghi lệnh thực tế sau MVP01.06; không tuyên bố đã chạy lệnh khi chưa có môi trường.
- Với logic, dùng focused tests cần thiết; với UI dùng browser thật; với xuất PDF xem/render tệp thật; với sửa văn bản chỉ rà nội dung/link. Không viết test để kiểm tra việc tạo thư mục.
- Kiểm tra sau mỗi nhóm tối đa3 task và tại cổng giai đoạn. Chạy bộ kiểm chứng phù hợp phần đã có, sửa lỗi chặn trước khi mở rộng. Không buộc chạy toàn bộ suite sau từng task nếu không có thay đổi/failure mới.
- MVP02.08, MVP13.01 và phần nhãn MVP13.02 cần người dùng cung cấp/chụp/gán nhãn ảnh thật. Agent có thể tạo fixtures tổng hợp trước; không bịa dữ liệu thu thập hay kết quả đánh giá.
- Lõi xử lý dùng ndarray/config; không import HTTP/DB. Ghi chú thuật toán và dữ liệu development được làm từ tuần 1, không chờ UI xong.
- Phạm vi web cục bộ, giấy tương đối phẳng. Nhàu rõ/cong/lóa/che chữ là ca giới hạn để ghi nhận; không thêm dewarping/OCR vào checklist chính.

## Giai đoạn 01 — Khung dự án và môi trường

**Tuần dự kiến:** 1. **Số task cần làm:** 7; MVP01.08 bỏ qua. **Đầu ra cuối giai đoạn:** Frontend gọi health backend qua proxy; môi trường và lệnh dev/test/build được ghi lại.

### MVP01.01 — Tạo cấu trúc dự án

- [x] **MVP01.01** — Tạo backend, frontend, experiments, fixtures và docs trong workspace hiện tại.
- **Xong khi:** Các thư mục có vai trò rõ; README trỏ đúng phạm vi MVP và hai tài liệu nền.
- **Kiểm chứng:** Kiểm tra cây thư mục và các liên kết tài liệu.
- **Cần trước:** Không.
- **Tệp dự kiến:** `README.md`, `docs/project-map.md`, `frontend/.gitkeep`, `experiments/.gitkeep`, `fixtures/.gitkeep`.
- **Quy mô:** M (5 tệp dự kiến; .gitkeep giữ thư mục trong repository).

### MVP01.02 — Thiết lập Git và ignore

- [x] **MVP01.02** — Thiết lập theo dõi mã nguồn, loại dependency, DB, ảnh runtime và dữ liệu cá nhân khỏi Git.
- **Xong khi:** Git status hoạt động; .gitignore loại đúng các vùng dữ liệu.
- **Kiểm chứng:** Dùng git status và git check-ignore với đường dẫn mẫu.
- **Cần trước:** MVP01.01
- **Tệp dự kiến:** `.gitignore`.
- **Quy mô:** S (1 tệp dự kiến).

### MVP01.03 — Dựng môi trường Python

- [x] **MVP01.03** — Chọn Python 3.11/3.12, tạo venv, cài các thư viện backend đã chốt.
- **Xong khi:** Import được FastAPI, cv2, NumPy, Pillow, SQLAlchemy và ReportLab; ghi phiên bản đã dùng.
- **Kiểm chứng:** Chạy kiểm tra import trong venv; lưu danh sách phiên bản thực tế.
- **Cần trước:** MVP01.01
- **Tệp dự kiến:** `backend/requirements.txt`, `README.md`.
- **Quy mô:** S (2 tệp dự kiến).

**Checkpoint 01-C1 — đạt 14/10/2026:** cấu trúc/link, Git/ignore, venv/import và pip check đều đã kiểm chứng. Xem docs/progress.md cho bằng chứng phạm vi ba task thiết lập.

### MVP01.04 — Tạo API health

- [x] **MVP01.04** — Tạo FastAPI app, settings đường dẫn/quota và endpoint /api/v1/health.
- **Xong khi:** Backend chạy localhost và trả 200 JSON; cấu hình nằm tập trung.
- **Kiểm chứng:** Khởi động backend và gọi health bằng HTTP.
- **Cần trước:** MVP01.03
- **Tệp dự kiến:** `backend/app/main.py`, `backend/app/settings.py`.
- **Quy mô:** S (2 tệp dự kiến).

### MVP01.05 — Dựng React và proxy

- [x] **MVP01.05** — Khởi tạo React/TypeScript/Vite và proxy /api đến backend.
- **Xong khi:** Trang mẫu chạy; request /api/v1/health đi qua proxy thành công.
- **Kiểm chứng:** Mở trình duyệt, kiểm tra response và console; chạy build.
- **Cần trước:** MVP01.04
- **Tệp thực tế:** `frontend/package.json`, `frontend/package-lock.json`, `frontend/vite.config.ts`, `frontend/tsconfig.json`, `frontend/index.html`, `frontend/src/main.tsx`, `frontend/src/App.tsx`, `frontend/src/styles.css`.
- **Quy mô:** Tách 2 task con vì scaffold cần 8 tệp; bằng chứng trong docs/progress.md.

#### MVP01.05a — Cấu hình scaffold và dependency

- [x] **MVP01.05a** — Khóa dependency, tạo cấu hình Vite/proxy, TypeScript và HTML entry.
- **Xong khi:** Dependency cài được trên Node thực tế; proxy trỏ localhost; entry và compiler config nhất quán.
- **Kiểm chứng:** npm install/npm ls; đối chiếu package-lock và phiên bản; kiểm tra cấu hình qua build/dev cùng task con b.
- **Cần trước:** MVP01.04.
- **Tệp thực tế:** `frontend/package.json`, `frontend/package-lock.json`, `frontend/vite.config.ts`, `frontend/tsconfig.json`, `frontend/index.html`.
- **Quy mô:** M (5 tệp).

#### MVP01.05b — Trang React kiểm tra kết nối

- [x] **MVP01.05b** — Dựng entry React và trang health có trạng thái đang chờ/thành công/lỗi, thử lại và kiểu dáng cơ bản.
- **Xong khi:** Fetch cùng origin qua proxy; thao tác bàn phím được; lỗi kết nối có thông báo và phục hồi được.
- **Kiểm chứng:** Browser thật; health 200 qua proxy; tắt/khởi động lại backend và thử lại; console, responsive và build.
- **Cần trước:** MVP01.05a.
- **Tệp thực tế:** `frontend/src/main.tsx`, `frontend/src/App.tsx`, `frontend/src/styles.css`.
- **Quy mô:** M (3 tệp).

### MVP01.06 — Thiết lập lệnh kiểm chứng

- [x] **MVP01.06** — Cấu hình pytest, typecheck/build và ghi lệnh chạy thực tế.
- **Xong khi:** README có lệnh dev/test/build đã kiểm tra; không tạo test cho thao tác tạo thư mục.
- **Kiểm chứng:** Chạy các lệnh trên môi trường vừa dựng; ghi kết quả.
- **Cần trước:** MVP01.05
- **Tệp thực tế:** `backend/pyproject.toml`, `backend/tests/test_health.py`, `backend/requirements.txt`, `frontend/package.json`, `README.md`.
- **Quy mô:** M (5 tệp; TestClient dùng httpx2 và test kiểm tra HTTP contract đã có).

**Checkpoint 01-C2 — đạt 14/10/2026:** API/frontend health qua proxy, pytest, typecheck/build và lệnh README đã được kiểm chứng; bằng chứng ở docs/progress.md. Chưa có chức năng scan; M0 được đóng sau khi người dùng bỏ qua MVP01.08.

### MVP01.07 — Ghi hợp đồng ảnh và cấu hình

- [x] **MVP01.07** — Ghi BGR uint8, EXIF một lần, tọa độ W−1/H−1, thứ tự góc, preset đầy đủ và revision.
- **Xong khi:** Một tài liệu dùng chung đủ để lõi và UI không đoán tọa độ/config.
- **Kiểm chứng:** Đối chiếu mục 5–10 đặc tả gốc với phạm vi MVP.
- **Cần trước:** MVP01.01
- **Tệp dự kiến:** `docs/image-contract.md`.
- **Quy mô:** S (1 tệp dự kiến).

### MVP01.08 — Tạo nhật ký làm việc

- ~~**MVP01.08** — Tạo mẫu tiến độ và thay đổi để ghi task, bằng chứng, quyết định và ảnh hưởng.~~ **BỎ QUA theo yêu cầu người dùng ngày 14/10/2026.**
- **Trạng thái:** Không cần thực hiện hoặc tạo changes.md để chuyển giai đoạn 02. Giữ thông tin task gốc bên dưới để truy vết; không đánh dấu hoàn thành bằng mã/bằng chứng chưa có.
- **Xong khi:** Có progress.md và changes.md; chưa đánh dấu task triển khai nào đã xong khi chưa có evidence.
- **Kiểm chứng:** Đọc lại mẫu và thử ghi một mục tiến độ môi trường khi thực hiện.
- **Cần trước:** MVP01.06, MVP01.07
- **Tệp dự kiến:** `docs/progress.md`, `docs/changes.md`.
- **Quy mô:** S (2 tệp dự kiến).

**Cổng 01 — đạt 14/10/2026:** Frontend gọi health backend qua proxy; môi trường và lệnh dev/test/build được ghi lại. MVP01.08 được người dùng bỏ qua; bằng chứng ở docs/progress.md. MVP02.01 có đủ phụ thuộc MVP01.06/MVP01.07.

---

## Giai đoạn 02 — Chuẩn hóa ảnh và dữ liệu đầu vào

**Tuần dự kiến:** 1. **Số task chính:** 8; thêm 1 task phụ AUX02.01. **Đầu ra cuối giai đoạn:** EXIF/alpha/format/quota đúng; có ảnh development để thử lõi. Thiếu ảnh thật không chặn kiểm thử tổng hợp.

### MVP02.01 — Tạo fixtures định dạng

- [x] **MVP02.01** — Chuẩn bị ảnh góc màu, EXIF, PNG alpha, file giả/hỏng và ảnh header vượt quota.
- **Xong khi:** Fixtures nhỏ, nguồn gốc rõ; ảnh vượt quota không cần giải mã để kiểm tra.
- **Kiểm chứng:** Đọc manifest fixtures và mở các ảnh hợp lệ để xác định hướng/màu mong đợi.
- **Cần trước:** MVP01.06, MVP01.07
- **Tệp thực tế:** `fixtures/manifest.json`, `experiments/create_fixtures.py`; 22 tệp dữ liệu tổng hợp sinh tự động được liệt kê/hash trong manifest.
- **Quy mô:** S (2 tệp nguồn/cấu hình; dữ liệu sinh tự động được kiểm tra theo manifest). Đã đối chiếu hash 22 tệp và giải mã 10 ảnh được chấp nhận; xem docs/progress.md.

### MVP02.02 — Kiểm tra định dạng và quota

- [x] **MVP02.02** — Viết kiểm tra byte, header, JPEG/PNG, một frame, dimensions và pixel count.
- **Xong khi:** Từ chối >15 MiB, >16 MP, chiều <2, ảnh động và format ngoài phạm vi bằng lỗi rõ.
- **Kiểm chứng:** Chạy pytest các fixture hợp lệ/giả/hỏng/quá pixel; xác nhận từ chối trước load lớn.
- **Cần trước:** MVP02.01
- **Tệp dự kiến:** `backend/app/processing/normalize.py`, `backend/tests/test_normalize.py`.
- **Quy mô:** S (2 tệp dự kiến).

**Bằng chứng MVP02.01–MVP02.02 (14/10/2026):** 22 fixtures tổng hợp/80.909 byte, 33 focused tests đạt; toàn bộ backend 34 tests đạt tại thời điểm hoàn thành hai task đầu. Quota kiểm tra trước verify/load; `validate_image` chỉ trả metadata trước EXIF. Bằng chứng cập nhật sau task 03–04 ở các mục bên dưới.

### MVP02.03 — Chuẩn hóa EXIF và alpha

- [x] **MVP02.03** — Áp EXIF đúng một lần, ghép alpha trắng, chuyển RGB sang BGR uint8.
- **Xong khi:** Ảnh đúng hướng, nền trong suốt thành trắng, kênh màu đúng; nguồn không bị sửa.
- **Kiểm chứng:** Kiểm tra fixture EXIF, alpha và pixel màu đã biết.
- **Cần trước:** MVP02.02
- **Tệp dự kiến:** `backend/app/processing/normalize.py`, `backend/tests/test_normalize.py`.
- **Quy mô:** S (2 tệp dự kiến).

**Checkpoint 02-C1 — đạt 14/10/2026:** fixtures/header/quota/decode/EXIF/alpha/BGR đã kiểm chứng; 61 focused tests đạt khi hoàn thành task 03, các ca này tiếp tục đạt trong bộ 83 focused/84 full backend tests sau task 04. Không còn lỗi chặn nhóm task này; xem docs/progress.md.

### MVP02.04 — Encode nguồn chuẩn hóa

- [x] **MVP02.04** — Encode PNG không EXIF cũ; lấy dimensions và hash nội dung tệp đã lưu.
- **Xong khi:** Đọc lại không xoay lần nữa; hash ổn định với cùng nội dung.
- **Kiểm chứng:** Encode/decode fixture và so pixels, dimensions, hash.
- **Cần trước:** MVP02.03
- **Tệp dự kiến:** `backend/app/processing/normalize.py`, `backend/tests/test_normalize.py`.
- **Quy mô:** S (2 tệp dự kiến).

**Bằng chứng MVP02.03–MVP02.04 (14/10/2026):** `normalize_image` trả BGR uint8 sau EXIF; `encode_normalized_png` trả PNG lossless sạch metadata cùng kích thước/SHA-256 của chính payload. 83 focused tests và 84 full backend tests đạt tại thời điểm hoàn thành hai task này, gồm ghi/đọc lại PNG, hash, đủ 8 hướng EXIF, giữ nguồn và lỗi decoder. Lưu bền của ứng dụng thuộc các task storage; bằng chứng thumbnail/CLI cập nhật bên dưới.

### MVP02.05 — Tạo thumbnail và preview helper

- [x] **MVP02.05** — Viết resize giữ tỉ lệ, không upscale, dùng kích thước thực sau làm tròn.
- **Xong khi:** Ảnh dọc/ngang giữ tỉ lệ; đầu ra nhỏ không bị phóng lớn.
- **Kiểm chứng:** Chạy mẫu dọc/ngang/ảnh rất nhỏ; kiểm tra dimensions.
- **Cần trước:** MVP02.04
- **Tệp dự kiến:** `backend/app/processing/image_sizes.py`, `backend/tests/test_image_sizes.py`.
- **Quy mô:** S (2 tệp dự kiến).

### MVP02.06 — Tạo script chuẩn hóa một ảnh

- [x] **MVP02.06** — Nối decode/normalize/encode/thumbnail vào command line.
- **Xong khi:** Một ảnh thật tạo nguồn chuẩn hóa, thumbnail và metadata; lỗi có thông báo.
- **Kiểm chứng:** Chạy script với JPEG EXIF, PNG alpha và một file sai định dạng.
- **Cần trước:** MVP02.05
- **Tệp thực tế:** `experiments/normalize_one.py`, `backend/tests/test_normalize_cli.py`, `.gitignore` (loại ảnh người dùng cung cấp khỏi Git).
- **Quy mô:** M (3 tệp; thêm kiểm thử CLI thật và ignore input theo quy tắc dữ liệu).

**Checkpoint 02-C2 — đạt 14/10/2026:** encode nguồn/resize/CLI đạt tiêu chí; trước rà soát toàn backend 126 tests đạt. AUX02.01 tìm/sửa lỗi float round-half-up và thêm 3 regression cases; helper hiện 29 tests, toàn backend 147 tests đạt cùng manifest. Task 07–08 đã có bằng chứng bên dưới.

### MVP02.07 — Tạo manifest và quy tắc chia tập

- [x] **MVP02.07** — Định nghĩa image_id, document_id, condition, split, đường dẫn và chính sách nhãn EXIF.
- **Xong khi:** Bộ hiện hành13ảnh/2tài liệu (user chốt26/10), một tài liệu development/một test; chưa dùng test để tune. Nghiệm thu MVP02.07 là schema/quy tắc, không phải đã thu đủ bộ cuối.
- **Kiểm chứng:** Kiểm tra manifest không có document_id ở hai split.
- **Cần trước:** MVP01.07
- **Tệp thực tế:** `experiments/dataset_manifest.csv`, `docs/dataset.md`, `experiments/validate_dataset.py`, `backend/tests/test_dataset_manifest.py`.
- **Quy mô:** M (4 tệp; có checker và 18 tests cho split/leakage/hash/schema).

### MVP02.08 — Thu nhóm ảnh development đầu tiên

- [x] **MVP02.08** — Người dùng chụp một nhóm nhỏ sáng đều, nghiêng, bóng/nếp gấp nhẹ và nền khó.
- **Xong khi:** Có ít nhất 6 ảnh development từ các tài liệu đã phân nhóm; không chứa thông tin riêng cần đưa vào Git.
- **Kiểm chứng:** Mở từng ảnh và xác nhận condition/split/path trong manifest.
- **Cần trước:** MVP02.07
- **Tệp dự kiến:** `experiments/dataset_manifest.csv`, `docs/dataset.md`.
- **Quy mô:** S (2 tệp dự kiến).

**Bằng chứng MVP02.07–MVP02.08:** 7 JPG được cung cấp → 6 ảnh khác byte; user xác nhận cùng tờ giấy nên tất cả doc_01/development, test 0. Mỗi ảnh 1536×2048, thumbnail 240×320; đã xem, normalize và đối chiếu pixel/hash/nguồn. Có sáng khá đều, nghiêng, góc gấp nhẹ, bóng đậm/nền gỗ. Validator --check-files đạt; mục tiêu cuối 10/40 chưa thu đủ, chưa có nhãn góc/metric.

### AUX02.01 — Rà soát tám task giai đoạn 02 theo yêu cầu người dùng

- [x] **AUX02.01** — Đối chiếu từng task với đặc tả/MVP/hợp đồng, source/tests và bằng chứng thực tế; sửa sai lệch trong phạm vi giai đoạn.
- **Xong khi:** Có ma trận yêu cầu → implementation → kiểm chứng → kết luận cho đủ 8 task, ghi lỗi/giới hạn và nghiệm thu đúng số thực tế.
- **Kiểm chứng:** Rà source, fixtures, dataset thật và artifacts; tái hiện/sửa bug rồi chạy toàn backend; không lấy test count làm accuracy.
- **Cần trước:** MVP02.01–MVP02.08 (có thể rà phần đã đủ phụ thuộc trong lúc thu dữ liệu).
- **Tệp thực tế:** `docs/audit-phase-02.md`, `backend/app/processing/image_sizes.py`, `backend/tests/test_image_sizes.py`.
- **Quy mô:** M (3 tệp; lỗi làm tròn float đã sửa, 147 tests đạt).

**Cổng 02 — đạt 14/10/2026:** cả tám task và AUX02.01 đạt; EXIF/alpha/format/quota/PNG/resize/CLI đúng và có 6 ảnh development thực. Tập này chỉ 1 tài liệu, test 0, chưa thay cho dữ liệu đánh giá cuối. Bằng chứng trong docs/progress.md và docs/audit-phase-02.md; có thể sang MVP03.01.

---

## Giai đoạn 03 — Hình học và hiệu chỉnh phối cảnh

**Tuần dự kiến:** 1. **Số task:** 8. **Đầu ra cuối giai đoạn:** Warp đúng bốn góc màu; giữ orientation; từ chối tứ giác tự cắt/lõm/suy biến.

### MVP03.01 — Chuyển đổi tọa độ

- [x] **MVP03.01** — Viết pixel ↔ normalized theo dimensions nguồn chuẩn hóa.
- **Xong khi:** Round-trip đúng W−1/H−1; từ chối số không hữu hạn/ngoài [0,1].
- **Kiểm chứng:** Chạy pytest điểm biên và ảnh nhiều kích thước.
- **Cần trước:** MVP02.03
- **Tệp dự kiến:** `backend/app/processing/geometry.py`, `backend/tests/test_geometry.py`.
- **Quy mô:** S (2 tệp dự kiến).

MVP03.01 đạt 14/10/2026: `pixel_to_normalized`/`normalized_to_pixel` dùng W−1/H−1, giữ subpixel, chặn sai dimensions/điểm/phạm vi. TDD RED thiếu mô-đun → GREEN 55 tests; bộ hình học cuối 111 tests, toàn backend 258 đạt. Bằng chứng trong progress.md.

### MVP03.02 — Kiểm tra điểm và cạnh

- [x] **MVP03.02** — Kiểm tra đúng bốn điểm, điểm trùng, cạnh ngắn và tolerance theo độ phân giải.
- **Xong khi:** Vùng gần suy biến bị từ chối với lý do; tứ giác hợp lệ vẫn được nhận.
- **Kiểm chứng:** Chạy fixture điểm trùng/cạnh rất ngắn/ảnh lớn nhỏ.
- **Cần trước:** MVP03.01
- **Tệp dự kiến:** `backend/app/processing/geometry.py`, `backend/tests/test_geometry.py`.
- **Quy mô:** S (2 tệp dự kiến).

MVP03.02 đạt 14/10/2026: `validate_quad_points` nhận normalized, trả pixel theo đúng thứ tự nhập; kiểm tra sáu cặp điểm/bốn cạnh gồm cạnh đóng. Ngưỡng ≤1e−6·D cho gần trùng, ≤1e−3·D cho cạnh ngắn, D là đường chéo pixel. TDD RED thiếu hàm → GREEN bộ geometry 111 tests; toàn backend 258 đạt tại mốc này. Hàm chỉ kiểm tra điểm/cạnh; topology/diện tích/winding hiện đã được kiểm chứng trong MVP03.03 bên dưới.

### MVP03.03 — Kiểm tra topology tứ giác

- [x] **MVP03.03** — Viết shoelace, segment intersection và convexity.
- **Xong khi:** Bow-tie, lõm, gần thẳng hàng bị từ chối; winding được xác định.
- **Kiểm chứng:** Chạy các tứ giác hợp lệ và ca đối kháng qua validate_quad.
- **Cần trước:** MVP03.02
- **Tệp dự kiến:** `backend/app/processing/geometry.py`, `backend/tests/test_geometry.py`.
- **Quy mô:** S (2 tệp dự kiến).

MVP03.03 đạt 14/10/2026: `validate_quad` nối gate điểm/cạnh, shoelace có dấu, cross/segment intersection và convexity; chặn collinear/near-collinear, tự giao/chạm, diện tích ≤1e−6·D², lõm và ngược winding. Không sắp lại góc tay. TDD RED thiếu hàm → 155 geometry tests đạt; bằng chứng cuối cùng 171 geometry/318 backend trong progress.md.

**Checkpoint 03-C1 — đạt 14/10/2026:** MVP03.01–MVP03.03 có kiểm chứng điểm biên/subpixel/độ phân giải/điểm-cạnh/tự giao/lõm/suy biến/winding; bộ tập trung sau task 03 đạt 155 tests, sau task 04 đạt 171. Giữ gate điểm/cạnh riêng, gate topology đầy đủ riêng; ảnh nguồn và thứ tự góc tay không đổi.

### MVP03.04 — Sắp góc tự phát hiện

- [x] **MVP03.04** — Sắp quanh tâm, chọn điểm đầu và winding; giữ ID khi góc đến từ thao tác tay.
- **Xong khi:** Diamond không trùng đỉnh; góc tay không tự đổi handle.
- **Kiểm chứng:** Chạy các hoán vị của cùng quad và fixture hình thoi.
- **Cần trước:** MVP03.03
- **Tệp dự kiến:** `backend/app/processing/geometry.py`, `backend/tests/test_geometry.py`.
- **Quy mô:** S (2 tệp dự kiến).

MVP03.04 đạt 14/10/2026: `order_auto_corners` chỉ cho auto proposal, sắp atan2 quanh trung bình điểm nguồn, area dương, xoay cycle tới min(x+y), tie y/x theo pixel nguồn. Trả normalized giữ đủ bốn đỉnh; validate_quad kiểm tra cuối. 24 hoán vị cho mỗi bộ rectangle/diamond/perspective/rotated/small đều đồng nhất; manual không reorder. Có ca đường chéo ngắn không nhầm thành cạnh. Bộ geometry 171 tests, toàn backend 318 đạt; đối chiếu 1.000 bộ điểm với OpenCV không có sai khác, không phải accuracy detector.

### MVP03.05 — Ước lượng kích thước warp

- [x] **MVP03.05** — Lấy cạnh đối, giữ tỉ lệ estimated, giới hạn cạnh dài 2400 và pixel đầu ra.
- **Xong khi:** Không upscale vượt kích thước ước lượng; dimensions tối thiểu hợp lệ.
- **Kiểm chứng:** Kiểm tra nguồn lớn/nhỏ và quad rất xiên.
- **Cần trước:** MVP03.04
- **Tệp dự kiến:** `backend/app/processing/geometry.py`, `backend/tests/test_geometry.py`.
- **Quy mô:** S (2 tệp dự kiến).

MVP03.05 đạt 14/10/2026: estimate_warp_size nối validate_quad, max cạnh đối/half-up/min2, cap2400 và5.76MP trước cấp buffer. Bộ geometry sau task05 đạt185 tests; nguồn nhỏ/lớn/dọc/ngang/diamond/phối cảnh và làm tròn .5 đã kiểm chứng. Ca rất xiên chạy thật cho97×50. Bằng chứng trong progress.md.

### MVP03.06 — Tính homography và warp

- [x] **MVP03.06** — Warp từ BGR nguồn bằng bốn cặp điểm, INTER_LINEAR; kiểm tra ma trận hữu hạn.
- **Xong khi:** Vùng xác nhận thành ảnh chữ nhật; lỗi hình học không lọt đến OpenCV.
- **Kiểm chứng:** Chạy fixture bốn góc màu và kiểm tra góc đích.
- **Cần trước:** MVP03.05
- **Tệp dự kiến:** `backend/app/processing/geometry.py`, `backend/tests/test_geometry.py`.
- **Quy mô:** S (2 tệp dự kiến).

MVP03.06 đạt 14/10/2026: compute_homography/warp_document lấy mẫu nguồn BGR bằng INTER_LINEAR/BORDER_REPLICATE, giữ thứ tự p0..p3, kiểm tra H finite/invertible. Tests màu/subpixel/2×2/strided/cap2400 và chặn input/geometry/H sai trước sampler; geometry206, toàn backend353 đạt. Xem trực tiếp fixture màu và source/warp tổng hợp93×58, không lật/xoắn; chưa phải script task07.

**Checkpoint 03-C2 — đạt 14/10/2026:** task04–06 có bằng chứng sort/full validation/kích thước/H/warp; bộ geometry206 tests, toàn backend353 đạt. Source giữ nguyên, lấy mẫu đúng bốn góc và pixel cap; UI/service/confirmed/revision chưa tích hợp. MVP03.07–08 và cổng03 còn chờ.

### MVP03.07 — Xuất minh họa hình học

- [x] **MVP03.07** — Tạo overlay quad nguồn và ảnh warp bằng một script.
- **Xong khi:** Có ảnh trước/overlay/sau cùng quad và dimensions để giải thích.
- **Kiểm chứng:** Chạy toàn ảnh và tứ giác nghiêng, xem bằng mắt các góc màu.
- **Cần trước:** MVP03.06, MVP02.06
- **Tệp thực tế:** `experiments/geometry_demo.py`, `backend/tests/test_geometry_demo.py`.
- **Quy mô:** S (2 tệp; thêm kiểm thử CLI/artifacts thực tế).

MVP03.07 đạt14/10/2026: CLI inputJPEG/PNG, --corners JSON normalized (mặc địnhfull), outputdir mới; normalize/validate/H/warp bằng lõi; source/overlay đánh số0..3/warp/metadata hashes/dimensions/H. TDD7fail1pass trướcscript →8CLItests đạt; đã chạy full/perspective/diamond, đọc9PNG/hash/dimensions và xem overlay/warp. Không detector hoặc tự sắp manual.

### MVP03.08 — Khóa các ca hình học quan trọng

- [x] **MVP03.08** — Hoàn thiện hồi quy diamond, winding, toàn ảnh, tự giao và suy biến.
- **Xong khi:** Test chỉ kiểm chứng quy tắc hình học, có ảnh chứng minh không lật/xoắn.
- **Kiểm chứng:** Chạy tập test geometry và ghi ảnh fixture vào nhật ký.
- **Cần trước:** MVP03.07
- **Tệp dự kiến:** `backend/tests/test_geometry.py`, `docs/progress.md`.
- **Quy mô:** S (2 tệp dự kiến).

MVP03.08 đạt14/10/2026:216geometrytests gồm diamond đủ24hoán vị qua warp giữ màu, winding/full/near-collinear, segment touch/overlap/disjoint và lỗi nguồn dài được bổ sung khi audit. Artifact full96×64→95×63, perspective120×80→93×58, diamond160×160→99×99 chứng minh không lật/xoắn. Toàn backend371tests đạt.

### AUX03.01 — Rà soát tám task giai đoạn03 theo yêu cầu người dùng

- [x] **AUX03.01** — Đối chiếu đặc tả/hợp đồng/lý thuyết/code/tests/artifacts của cả8task, sửa lỗi tìm được và ghi giới hạn thực tế.
- **Xong khi:** Ma trận đủ8task có bằng chứng/kết luận; lỗi chặn được tái hiện/sửa, nghiệm thu đúng phạm vi offline.
- **Kiểm chứng:** Fullsuite371tests, 3CLI runs/9PNG/hash/dims, xem overlay/warp; fixtures22hash không đổi; source dài16MP/crop pixel equality.
- **Cần trước:** MVP03.01–MVP03.08.
- **Tệp thực tế:** `docs/audit-phase-03.md`, `backend/app/processing/geometry.py`, `backend/tests/test_geometry.py`.
- **Quy mô:** M (3tệp; sửa giới hạn remap nguồn dài bằng ROI gốc, không resize nguồn).

**Cổng 03 — đạt14/10/2026:** cả8task và AUX03.01 đạt sau sửa ca40.000×400/400×40.000. Geometry216+CLI8+147cũ=371tests đạt; màu/orientation/invalid cases/artifacts thực đã kiểm tra. Bằng chứng trong progress/audit-phase-03; tiếp theoMVP04.01. Detector/UI/modes/revision/PDF chưa được triển khai.

---

## Giai đoạn 04 — Ba chế độ cải thiện ảnh

**Tuần dự kiến:** 1. **Số task chính:** 7; thêm1task phụ AUX04.01. **Đầu ra cuối giai đoạn:** Cùng một vùng warp tạo được ba mode; có Otsu/Adaptive và lý do chọn mode theo loại tài liệu.

### MVP04.01 — Tạo config và preset lõi

- [x] **MVP04.01** — Định nghĩa color/gray/bw, enum/range, preset đầy đủ và tham số inactive.
- **Xong khi:** Giá trị thiếu lấy default schema; config không sửa nguồn; kernel/block/C được kiểm tra.
- **Kiểm chứng:** Chạy config mặc định, config sai và config đổi mode.
- **Cần trước:** MVP01.07, MVP03.06
- **Tệp dự kiến:** `backend/app/processing/config.py`, `backend/tests/test_enhancement.py`.
- **Quy mô:** S (2 tệp dự kiến).

MVP04.01 đạt14/10/2026: config.py có PageConfig/nested models frozen, get_preset và parse_config; defaults theo mode/trường con, extra/null/sai kiểu/miền bị từ chối, inactive được giữ/đánh dấu. Góc dùng source_size thực để validate_quad; warp_size kiểm tra Adaptive active vừa ảnh. TDD thiếu module →74config tests đạt; toàn backend445 đạt. Chưa lọc ảnh/HTTP/revision; Checkpoint04-C1 còn chờ task02–03.

### MVP04.02 — Viết bộ lọc chọn được

- [x] **MVP04.02** — Thêm None, Median và Gaussian cho ảnh sau warp.
- **Xong khi:** Chọn được lọc/kernel hợp lệ; detection blur không dùng làm nguồn render.
- **Kiểm chứng:** So ảnh chấm nhiễu/nét mảnh; test kích thước/dtype và không mutate source.
- **Cần trước:** MVP04.01
- **Tệp dự kiến:** `backend/app/processing/enhancement.py`, `backend/tests/test_enhancement.py`.
- **Quy mô:** S (2 tệp dự kiến).

MVP04.02 đạt14/10/2026: apply_denoise nhận BGRuint8 sauwarp2..2400/dimension và DenoiseConfig; Nonecopy, Median3/5, Gaussian3/5 sigma0/reflect101. Giữshape/dtype/kênh, khôngmutate nguồn; revalidateconfig và lỗi rõ. REDthiếumodule→100tests enhancement/config đạt (26lọc mới); fullbackend471đạt. So chấm nhiễu/nét1pixel bằngảnhsynthetic: Median xóa chấm vànét mảnh, Gaussian mềm nét, None giữ nguyên. Artifacts/nhận xét trong progress; chưa mode/CLAHE/threshold.

### MVP04.03 — Viết mode màu và xám

- [x] **MVP04.03** — Giữ màu; chuyển xám; CLAHE trên xám theo image-contract; CLAHE màu/Lab của bản gốc được hoãn theo MVP.
- **Xong khi:** CLAHE bật/tắt được; ảnh màu giữ highlight; output đúng channels/dtype.
- **Kiểm chứng:** Chạy cùng một vùng có chữ tiếng Việt và highlight; lưu cặp so sánh.
- **Cần trước:** MVP04.02
- **Tệp dự kiến:** `backend/app/processing/enhancement.py`, `backend/tests/test_enhancement.py`.
- **Quy mô:** S (2 tệp dự kiến).

MVP04.03 đạt14/10/2026: render_color copy BGR sau lọc; render_gray BGR2GRAY và CLAHE bật/tắt với ContrastConfig đã revalidate. Output độc lập/uint8, giữ dimensions, Color giữ highlight, Gray một kênh; không threshold/xoay/dispatcher. RED thiếu helper →132tests tập trung đạt (32modes mới), toàn backend503đạt. Xem cùng vùng synthetic chữ tiếng Việt/highlight640×300 và lưu source/color/gray/gray_clahe/comparison/metadata; Color bằng source, gray229→CLAHE233 tại pixel highlight, source không đổi. Chi tiết trong progress; chưa đánh giá chất lượng ảnh thật.

**Checkpoint 04-C1 — đạt14/10/2026:** Rà MVP04.01–03 với132tests config/preset/inactive/filter/modes và ảnh noise/nét mảnh + tiếng Việt/highlight. Toàn backend503đạt tại mốc này; không có lỗi chặn. Các task04–07 tiếp tục bên dưới; checkpoint04-C2/cổng04 cònchờ.

### MVP04.04 — Viết threshold Otsu

- [x] **MVP04.04** — Thêm Otsu cho ảnh xám trước threshold và trả ngưỡng thực dùng.
- **Xong khi:** BW nền trắng/chữ đen; ngưỡng có thể truy vết cùng config.
- **Kiểm chứng:** So ảnh sáng đều và ảnh bóng; kiểm tra giá trị đầu ra chỉ 0/255.
- **Cần trước:** MVP04.03
- **Tệp dự kiến:** `backend/app/processing/enhancement.py`, `backend/tests/test_enhancement.py`.
- **Quy mô:** S (2 tệp dự kiến).

MVP04.04 đạt14/10/2026: apply_otsu(gray) trả BW uint8 và actual_threshold thực, THRESH_BINARY|THRESH_OTSU, cùngsize/không sửa nguồn, không blur thêm. RED thiếuhelper→146tests tập trung đạt (14Otsu mới). So ảnhsynthetic sángđều/bóng cùngnội dung: t182/t155; nềntrái ảnhbóng thànhđen vớiOtsu. Ghi effective_config/ngưỡng/hashes và xemcomparison tại mvp04-04-otsu/; toànbackend sau04.05 đạt542tests. Khôngsuyraaccuracy.

### MVP04.05 — Viết Adaptive Gaussian

- [x] **MVP04.05** — Thêm block size/C và xử lý ảnh nhỏ theo chính sách config đã ghi.
- **Xong khi:** Block lẻ, C đúng miền; lỗi rõ cho cấu hình không phù hợp; không threshold màu trực tiếp.
- **Kiểm chứng:** Chạy ảnh bóng và ảnh nhỏ; lưu so sánh block 31/51 và C.
- **Cần trước:** MVP04.04
- **Tệp dự kiến:** `backend/app/processing/enhancement.py`, `backend/tests/test_enhancement.py`.
- **Quy mô:** S (2 tệp dự kiến).

MVP04.05 đạt14/10/2026: apply_adaptive_gaussian(gray,ThresholdConfig), ADAPTIVE_THRESH_GAUSSIAN_C/THRESH_BINARY, BW0/255 độc lập/cùngsize. Revalidateconfig, blocklẻ3..151≤cạnhngắn thật, C nguyên−20..30; quáblock báo INVALID_CONFIG, khôngclamp/fallback/màu trực tiếp. RED thiếuhelper→171tests tập trung đạt (25Adaptive mới), toànbackend542đạt. So cùnggray sángđều/bóng; lưu block31/51×C5/10/20: nềnbóng giữtrắng, C20 có thể xóa nét nhạt. Ảnh8×8:31 lỗi/3 chạy/Otsu t40;2×2 Adaptive3 lỗi. Artifacts/hashes và nhận xét trongprogress; checkpoint04-C2 chờ04.06.

### MVP04.06 — Nối dispatcher và xoay

- [x] **MVP04.06** — Ghép bộ lọc, mode, contrast/threshold và rotate90 sau xử lý.
- **Xong khi:** Ba mode có output; rotation đổi hướng nhưng không đổi corners nguồn.
- **Kiểm chứng:** Chạy bốn rotation và ba mode trên cùng warp.
- **Cần trước:** MVP04.05
- **Tệp dự kiến:** `backend/app/processing/enhancement.py`, `backend/tests/test_enhancement.py`.
- **Quy mô:** S (2 tệp dự kiến).

MVP04.06 đạt14/10/2026: enhance_document nhận fullwarp BGR vàfullconfig, parse/revalidate với warp_size thật/source_size thực cho corners trướcfilter. Denoise→mode/contrast/threshold→rotate90 chiều kimđồnghồ, khôngnội suy/đổi corners. EnhancementResult trả image/effective_config/actualOtsut hoặcnull. REDthiếuhelper→193tests tập trung đạt (22dispatcher mới). Chạy12fullrenders ba mode×bốn hướng cùngwarp95×63, equalitynp.rot90 vàsource/config/corners giữnguyên; artifacts mvp04-06-rotations/ đãxem. Serviceconfirmed/revision còn chờ.

**Checkpoint 04-C2 — đạt14/10/2026:** MVP04.04–06 có61cases mới (14Otsu+25Adaptive+22dispatcher), toàn193config/enhancement đạt; ngưỡng/ảnhnhỏ/cả12mode-rotation đượckiểm chứng. Toànbackend sauCLI đạt571tests; khônglỗi chặn. Cổng04 vàtask07 cóbằngchứng dưới đây.

### MVP04.07 — Ghi so sánh độ đọc ban đầu

- [x] **MVP04.07** — Xuất ba mode và nhận xét dấu tiếng Việt/nét mảnh/highlight.
- **Xong khi:** Có ví dụ ưu/nhược và preset khởi đầu; không gọi đây là kết quả test cuối.
- **Kiểm chứng:** Mở ảnh full resolution, ghi lỗi mất dấu/nền đen hoặc mất màu.
- **Cần trước:** MVP04.06, MVP02.08
- **Tệp thực tế:** `experiments/enhancement_demo.py`, `docs/algorithm-notes.md`, `backend/tests/test_enhancement_demo.py`.
- **Quy mô:** M (3tệp thực tế; thêmtest chạyCLI đểkiểm chứng fullảnh/config/provenance/lỗi).

MVP04.07 đạt14/10/2026: CLI chuẩn hóa/warp từquadmanual mộtlần, chạyColor/Gray/BWAdaptive/BWOtsu cùngwarp, ghiPNGfull RGB/L vàsource/overlay/warp/comparison/metadata vào thưmụcmới. Giữ preset/overridefullconfig/rotation/corners/actualt/hash/size; không tựconfirmed/fallback. REDthiếuCLI→7CLItests đạt13.19s. Chạy5runs (2ảnhdevelopment cùngdoc_01, bảnNone củaảnhbóng, 2synthetic); xemfull/cropnguyênpixel vàghiưu/nhược/preset trongalgorithm-notes. Otsu nềnbóngđen, Adaptive giữôly/đứtnét, Colorgiữhighlight; khôngđoaccuracy.

### AUX04.01 — Rà soát bảy task giai đoạn04 theo yêu cầu người dùng

- [x] **AUX04.01** — Đối chiếu đặc tả/MVP/hợp đồng/code/tests/artifacts của đủ7task, ghi kết luận và giới hạn thực tế.
- **Xong khi:** Ma trận đủ7task có evidence/kết luận, lỗi chặn được sửa nếu phát hiện; khôngcoi sốtests làaccuracy.
- **Kiểm chứng:** Toànbackend571tests đạt52.53s;40PNGCLI+12PNGrotation/hash/dims, xem2ảnhthật/2synthetic/fulltextcrops;6cặpnguồn development và22fixtures khôngđổi.
- **Cần trước:** MVP04.01–MVP04.07.
- **Tệp thực tế:** `docs/audit-phase-04.md`, `docs/progress.md`.
- **Quy mô:** S (2tệp ghi bằngchứng; khôngtìm thấy lỗi implementation chặn mới).

**Cổng 04 — đạt14/10/2026:** cả7task vàAUX04.01 đạt; cùngwarp có3mode/boththresholds/rotate vàlýdochọnmode/preset. Toànbackend571tests, CLI/ảnhthật/tổnghợp đãkiểm chứng; chi tiếttrongprogress/algorithm-notes/audit-phase-04. Lõi offline, chưaUI/confirmed-revision/storage/export hoặcaccuracy cuối. Tiếp theoMVP05.01.

---

## Giai đoạn 05 — Tự phát hiện vùng tài liệu

**Tuần dự kiến:**1. **Số task chính:**8; thêm2task phụ AUX05.01/AUX05.02. **Đầu ra cuối giai đoạn:** Ảnh thuận lợi có đề xuất; ảnh khó có cảnh báo/fallback; score, trial và ảnh trung gian giải thích được.

**Tham chiếu khi thực hiện:** [phân tích thuật toán, mục 5.5.1–5.5.3](../docs/Phan_Tich_Huong_Thuat_Toan_Tu_Tai_Lieu.md). Phân biệt contour/Q là biểu diễn, chu vi/cạnh/góc là mô tả biên, diện tích là đặc trưng vùng. Bộ mô tả phục vụ lọc, scoring và giải thích.

### MVP05.01 — Tạo ảnh phân tích

- [x] **MVP05.01** — Thu nguồn về cạnh dài 1200, tạo gray và Gaussian 5.
- **Xong khi:** Không upscale; góc dùng dimensions thực sau resize; có stages gray/blur.
- **Kiểm chứng:** Chạy ảnh dọc/ngang và kiểm tra mapping ảnh phân tích về nguồn.
- **Cần trước:** MVP03.04, MVP02.05
- **Tệp dự kiến:** `backend/app/processing/detection.py`, `backend/tests/test_detection.py`.
- **Quy mô:** S (2 tệp dự kiến).

MVP05.01 đạt 15/10/2026: prepare_analysis nhận nguồn BGR uint8 sau EXIF, tối đa16MP/mỗi chiều≥2; resize INTER_AREA/half-up/max1200 không upscale, BGR2GRAY và Gaussian5/sigma0/reflect101. Trả AnalysisImages với source_size, BGR/gray/blurred độc lập, analysis_size thực và to_source qua normalized W−1/H−1 dùng geometry có sẵn. Analysis có cạnh<2 sau resize báo ANALYSIS_TOO_SMALL. TDD thiếu module→20tests đạt0.35s; đã chạy dọc1536×2048→900×1200, ngang2000×1001→1200×601 và nguồnnhỏ giữsize, mapping/subpixel/nguồn nguyên được kiểm. Chi tiết trongprogress.

### MVP05.02 — Tạo Canny và closing

- [x] **MVP05.02** — Thử tối đa ba cặp ngưỡng; L2gradient; closing 3 một lần.
- **Xong khi:** Giữ edges trước closing và trial ID; số trial hữu hạn.
- **Kiểm chứng:** Quan sát edge/closing trên ảnh biên hở và nền nhiều họa tiết.
- **Cần trước:** MVP05.01
- **Tệp dự kiến:** `backend/app/processing/detection.py`, `backend/tests/test_detection.py`.
- **Quy mô:** S (2 tệp dự kiến).

MVP05.02 đạt 15/10/2026: create_edge_trials nhận blurred gray uint82..1200, trả tuple đúng3 EdgeTrial ID/thresholds/edges/closed. Canny50/150,75/200,100/250 với aperture3/L2true; closingrect3×3 mộtlần, borderconstant trung tính mặc địnhCV. Giữ edges raw riêng để scoring sau, closed cho contour; không blur lại hoặc tự thử vô hạn. TDD thiếuhelper→33tests đạt0.40s (13edge mới), toànbackend604đạt23.87s. Xem4runs (2synthetic +2ảnhdevelopment cùngdoc),44PNG/hash/shape; closing không kín mọi khoảnghở và làm dày cả nét nền. Chưa contour/score/đề xuất,05-C1 còn chờ03.

### MVP05.03 — Sinh ứng viên contour

- [x] **MVP05.03** — RETR_LIST/CHAIN_APPROX_SIMPLE, tối đa 30 contour lớn mỗi trial, ba epsilon ratio.
- **Xong khi:** Giữ contour có thứ tự/Q và số đỉnh xấp xỉ; tứ giác đủ diện tích/cạnh, vượt validate_quad; lưu lý do loại, không ép góc vuông.
- **Kiểm chứng:** Chạy rectangle/diamond, quad lõm/tự giao/suy biến và ảnh development; đối chiếu contour/Q overlay cùng lý do nhận/loại.
- **Cần trước:** MVP05.02
- **Tệp dự kiến:** `backend/app/processing/detection.py`, `backend/tests/test_detection.py`.
- **Quy mô:** S (2 tệp dự kiến).

MVP05.03 đạt 15/10/2026: generate_candidates(analysis,trial) giữ tối đa30 contour lớn, approxPolyDP epsilon/P=.015/.02/.03; lưu ContourCandidate cho cả lần nhận/loại, contour có thứ tự, polygon gốc/số đỉnh, trial/dimensions và lý do. Gate contour/quad area≥10%WaHa, cạnh≥5%min(Wa,Ha), validate_quad trước auto ordering; không sửa topology bằng sorter hoặc ép 90°. Canonical start dùng pixel nguồn thật. TDD thiếu helper→48tests detection đạt0.49s (15 mới). Runtime rectangle/diamond/texture có quad; lõm, hình tự cắt và suy biến bị loại với lý do thực. Hai ảnh development đã xem overlay; chi tiết trong progress/algorithm-notes.

**Checkpoint 05-C1 — đạt 15/10/2026:** MVP05.01–03 đã kiểm preprocessing/mapping, ba raw/closed trials và contour/Q/geometry bằng tests cùng ảnh runtime. Không có lỗi chặn implementation; có ca không tìm được quad, đúng phạm vi chưa có fallback. Bộ64tests detection và full635tests đạt sau05.04. Cổng05 chưa đạt, cần các task05–08.

### MVP05.04 — Trích mô tả và tính score ứng viên

- [x] **MVP05.04** — Trích chu vi/cạnh/góc/tính lồi, đặc trưng vùng và hỗ trợ biên từng cạnh; tính score từ a/e/f/b như đặc tả.
- **Xong khi:** Bộ mô tả có đơn vị/dimensions rõ; e tổng có trọng số theo số mẫu; score và thành phần truy vết, hữu hạn; không gọi score là accuracy.
- **Kiểm chứng:** Fixture geometry và edge map cố định, gồm cạnh thiếu edge/số mẫu khác nhau; so giấy với khung/mép ảnh; kiểm tra tỷ lệ và đối chiếu công thức mục 5.5.1 tài liệu phân tích.
- **Cần trước:** MVP05.03
- **Tệp dự kiến:** `backend/app/processing/detection.py`, `backend/tests/test_detection.py`.
- **Quy mô:** S (2 tệp dự kiến).

MVP05.04 đạt 15/10/2026: describe_candidate trả CandidateDescription chứa chu vi/cạnh px, góc đổi hướng rad, kết quả geometry và a/e/f/b/heuristic_score; trace về candidate/trial/dimensions. Mỗi cạnh n=max(2,ceil(L/2)+1), lấy cả hai đầu, khoảng cách mẫu≤2px; hỗ trợ khi raw edge cùng trial cách Euclid≤2px, border≤2px. Giữ counts và tỷ lệ từng cạnh; e=sum(m)/sum(n), S=clip(.45a+.35e+.20f−.15b,0,1). Không đọc closed để tạo hỗ trợ, không score ứng viên bị loại. TDD thiếu helper→64tests đạt0.78s (16 mới); toànbackend635đạt48.32s. Runtime10cases/30trials + map kiểm soát,111PNG đã kiểm/xem comparison: img_003 có ví dụ score.502372, img_004 không có quad; frame có thể được score cao nhưng sai. Không NMS/đề xuất/fallback/UI hoặc accuracy; next05.05.

### AUX05.01 — Điều chỉnh sinh ứng viên theo yêu cầu người dùng

- [x] **AUX05.01** — Thử độ nhạy Canny/Gaussian, bổ sung nhánh vùng sáng dự phòng có bằng chứng và đồng bộ tài liệu.
- **Xong khi:** Baseline tái hiện được; revised hữu hạn, giữ nguồn/geometry/score; mask/raw edges và provenance tách rõ; so cả ca đúng/sai, không gọi candidate count là accuracy.
- **Kiểm chứng:** TDD30revision+5CLI; toànbackend670đạt20.17s;16ca/104trial, so baseline/revised, source/hash/dims và uniform mask gate.
- **Cần trước:** MVP05.01–MVP05.04; user chấp nhận thay đổi15/10/2026.
- **Tệp thực tế:** detection.py/test_detection_revision.py và compare_detection.py/test_compare_detection.py; báo cáo [revision01](../docs/detection-revision-01.md), đồng bộ tài liệu liên quan.
- **Quy mô:** M phần code4tệp; chia ba phần để kiểm chứng từng bước:
  - [x] **AUX05.01a** — Khảo sát hữu hạn Gaussian3/5 và ngưỡng trên16ca, giữ baseline và ghi hạn chế.
  - [x] **AUX05.01b** — Core revised20/60,50/150,75/200; tối đa1Otsu khi khôngquad Canny, tests và CLI so một ảnh.
  - [x] **AUX05.01c** — Cập nhật hướng/hợp đồng/kế hoạch và kiểm metadata/ảnh/input, giữ task05.05–08 chưa hoàn thành.

AUX05.01 đạt15/10/2026: giữGaussian5, kernel3 chỉablation; collect_candidates defaultrevised trả3Canny vàregion khi cần. Otsu mask/RETR_EXTERNAL giữactualt, rawsupport20/60 riêng; uniform mask bịloại, không hạarea10%/tăngclosing/đổiscore. anhtestnew cóquad S.634709; img_004/img_006 córegioncandidate nhưng góctrêntrái ăn bàn S.468352/.448517; img_001 chưaquad; khunggiả vẫnscorecao.16runs/104trial/440PNG/272descriptors, khôngaccuracy. Full670tests;34main+4AUX,110IDgốc giữ. Chi tiết và nguồn/giới hạn trongrevision01/progress.

### MVP05.05 — Loại trùng ứng viên

- [x] **MVP05.05** — Dùng polygon IoU để giữ vùng score cao nhất khi IoU >0.95.
- **Xong khi:** Ứng viên từ collect_candidates revised không lặp; cùng quad có IoU=1; giữ method/kernel/actualt/support của ứng viên được giữ.
- **Kiểm chứng:** Chạy ứng viên trùng/khác nhau, khác trial/nguồn sinh Canny-region và test helper IoU; không trộn raw support khi giữ score.
- **Cần trước:** MVP05.04, AUX05.01
- **Tệp thực tế:** `backend/app/processing/polygon_metrics.py`, `backend/app/processing/detection.py`, `backend/tests/test_polygon_metrics.py`, `backend/tests/test_detection_selection.py`.
- **Quy mô:** M (4 tệp).
- **Bằng chứng 15/10:** polygon IoU liên tục, nested/disjoint/touching/skew/subpixel; quad giống nhau IoU=1, IoU=.95 không bị loại. NMS greedy theo score, tie ổn định theo thứ tự vào, giữ nguyên description/method/kernel/actualt/support. Tests: 18 metrics + phần NMS trong 28 selection; xem progress.

### MVP05.06 — Trả đề xuất và fallback

- [x] **MVP05.06** — Chọn theo ngưỡng 0.60/0.40; trả corners normalized hoặc manual_required.
- **Xong khi:** Không dựng giả thành công; detect chỉ đề xuất, không xác nhận vùng.
- **Kiểm chứng:** Chạy ảnh có/không quad; kiểm tra status/corners/warnings.
- **Cần trước:** MVP05.05
- **Tệp thực tế:** `backend/app/processing/detection.py`, `backend/tests/test_detection_selection.py`.
- **Quy mô:** S (2 tệp dự kiến).
- **Bằng chứng 15/10:** select_proposal/detect_document trả proposed/proposed_with_warning/manual_required, không quad thì corners/score=null; dưới .40 chỉ giữ ứng viên làm chẩn đoán, corners=null; confirmed luôn false. Boundary .40/.60 có kiểm. Chạy thật 7 ca tại experiments/results/mvp05-05-06-verified/: img_004 cảnh báo S=.468352, anhtestnew đề xuất S=.634709, img_001 manual_required. 140 tests tập trung và 716 backend đạt; không chứng nhận chọn đúng mọi trang.

**Checkpoint 05-C2:** Rà bằng chứng nghiệm thu MVP05.04 → MVP05.06; chạy kiểm chứng tập trung tương ứng, giữ mốc đã chạy được và ghi lỗi/chặn trước nhóm tiếp theo.

Đạt 15/10/2026: mô tả/score → NMS → đề xuất/fallback đúng hợp đồng; 140 tests tập trung, 716 backend; đã xem đủ 7 overlay. img_004 vẫn ăn bàn nhưng có cảnh báo; khung giả vẫn có thể được đề xuất điểm cao. Giữ các giới hạn này để đối chứng ở05.08; chưa thay phân vùng/epsilon/score hoặc thêm gate từng cạnh. Cổng05 chờ05.07–08.

### MVP05.07 — Ghi timing và stage được chọn

- [x] **MVP05.07** — Trả timing, trial, contour overlay và bộ mô tả/đặc trưng của ứng viên được chọn từ phép chạy thật.
- **Xong khi:** Debug metadata có dimensions/đơn vị, method/kernel/actual Otsut/support_trial_id, khớp nguồn/config/trial và score; region_mask tách closed/raw Canny, manual_required có trạng thái rõ.
- **Kiểm chứng:** Đối chiếu overlay, quad, mô tả từng cạnh, a/e/f/b, score và tổng timing; không trộn metadata giữa các trial.
- **Cần trước:** MVP05.06
- **Tệp thực tế:** `backend/app/processing/detection.py`, `backend/tests/test_detection_debug.py`.
- **Quy mô:** S (2 tệp dự kiến).

MVP05.07 đạt15/10: debug opt-in giữ đúng analysis/trials/selected raw-or-mask/overlay/provenance/hash BGR; timings_ms đo các khoảng liền nhau, không gồm decode/encode/I/O. 10 tests debug; mặc định không giữ stage arrays. Không quad không vẽ giả; low-score quad chỉ diagnostic.

### MVP05.08 — Chạy nhóm development ban đầu

- [x] **MVP05.08** — Chạy detector trên ảnh thuận lợi và khó, lưu overlay và lỗi.
- **Xong khi:** Có ví dụ đúng/sai, không tune bằng test; biết fallback vẫn quét được.
- **Kiểm chứng:** Xem từng overlay và ghi nguyên nhân thất bại, so baseline/revised; cócandidate chưa đồng nghĩa chọn đúng. Các chạy core16ca trong AUX05.01 không thay nghiệm thu detector/proposal/manual fallback của task này.
- **Cần trước:** MVP05.07, MVP02.08
- **Tệp thực tế:** `experiments/detect_batch.py`, `backend/tests/test_detect_batch.py`, `docs/algorithm-notes.md`.
- **Quy mô:** M (3 tệp).

MVP05.08 đạt15/10: CLI chỉ đọc development, thêm ảnh bổ sung chưa gán split, chạy cả baseline/revised. 7 CLI tests; 16ca/32runs/104trials/368PNG, xem đủ16comparison, QA replay metadata/stages/descriptors. img_001 manual draft tạo warp951×1284 và4mode qua CLI có sẵn, thêm8PNG. Không GT/accuracy hoặc UI tay; score cao vẫn có thể chọn khung sai. Full733tests đạt47.01s.

### AUX05.02 — Rà soát giai đoạn05 và nợ kỹ thuật task03–04

- [x] **AUX05.02** — Đối chiếu đủ8task với đặc tả, bằng chứng và lý thuyết; ghi giới hạn và hướng xử lý nợ thuật toán.
- **Xong khi:** Ma trận8task có evidence/kết luận; lỗi chặn được xử lý; nợ thiết kế phân biệt với lỗi code, không báo accuracy từ score/status.
- **Kiểm chứng:** 733backend; 32runs/104trials/368PNG +8manualPNG, source/fixtures giữhash; QA replay stages và19survivors.
- **Cần trước:** MVP05.01–MVP05.08/AUX05.01.
- **Tệp thực tế:** `docs/audit-phase-05.md`, `docs/progress.md`.
- **Quy mô:** S (2tệp bằng chứng; không phát hiện lỗi implementation mới chặn nghiệm thu).

**Cổng 05 — đạt15/10/2026:** cả8task và AUX05.02 có bằng chứng; ảnh thuận lợi có đề xuất, ảnh khó có ví dụ cảnh báo/manual; trial/score/stages/timing giải thích được. Fallback góc tay đã tạo warp/render draft, chưa có UI. Không bảo đảm cảnh báo mọi ca sai: frame giả vẫn điểm cao, img_004/006 còn ăn bàn. Xem audit-phase-05/algorithm-notes; nợ phân vùng/epsilon/score vẫn mở. Tiếp theo MVP06.01.

---

## Giai đoạn 06 — Pipeline offline và dữ liệu minh họa

**Tuần dự kiến:** 1. **Số task:** 6. **Đầu ra cuối giai đoạn:** M1: một lệnh quét ảnh và xuất ảnh/config/stages, độc lập web; fallback tay chạy.

### MVP06.01 — Ghép pipeline scan một ảnh

- [x] **MVP06.01** — Script normalize → detect hoặc góc tay → warp → mode → rotate.
- **Xong khi:** Chọn được góc tay khi detect thất bại; full render lấy từ nguồn chuẩn hóa.
- **Kiểm chứng:** Chạy một ảnh thuận lợi và một ảnh manual_required.
- **Cần trước:** MVP04.06, MVP05.07
- **Tệp thực tế:** `experiments/scan_one.py`, `backend/app/processing/render.py`, `backend/tests/test_render.py`, `backend/tests/test_scan_one.py`.
- **Quy mô:** M (4 tệp).

MVP06.01 đạt15/10: render_document chuẩn hóa config → góc tay hoặc detector revised → source warp → mode/rotation. scan_one CLI normalize một lần, draft không tự confirmed; manual_required lưu chẩn đoán/exit2, không dựng render giả. Case analysis có cạnh1 được chuyển manual_required; manual vẫn phải qua gate geometry. Source40000×42 dùng tay được, không dùng analysis để warp. 21 tests pipeline trong30render và8scanCLI; runtime auto tốt/cảnh báo/thất bại và tay đã chạy.

### MVP06.02 — Xuất full render và preview

- [x] **MVP06.02** — Encode full render, rồi resize preview từ kết quả đó.
- **Xong khi:** Preview và ảnh xuất cùng phép xử lý; không render riêng từ thumbnail.
- **Kiểm chứng:** So full/preview cùng mode, kiểm tra dimensions và màu khi mở lại.
- **Cần trước:** MVP06.01
- **Tệp thực tế:** `backend/app/processing/render.py`, `backend/tests/test_render.py`.
- **Quy mô:** S (2 tệp dự kiến).

MVP06.02 đạt15/10: encode_render_images xuất PNGfullRGB/L và previewmax1000 từ đúng pixel cuối, INTER_AREA/half-up/khôngupscale; previewBW được cógray, không thresholdlại. Full2..2400, preview cócạnh1; hash đúngpayload/khôngEXIF. 9tests encoder trong30render; caseBW90 full1300×2000→preview650×1000 đượckiểm.

### MVP06.03 — Ghi snapshot config và debug stages

- [x] **MVP06.03** — Ghi nguồn/hash, version, config thực dùng, timing và ảnh stage bằng tên thống nhất.
- **Xong khi:** Có thể tái chạy một case; không trộn detection trial với render.
- **Kiểm chứng:** Chạy case và đối chiếu JSON với ảnh stage và output.
- **Cần trước:** MVP06.02
- **Tệp thực tế:** phần a: enhancement.py/test_enhancement_stages.py và nối render.py; phần b: detection_artifacts.py/detect_batch.py/scan_one.py/test_scan_one.py.
- **Quy mô:** chia a (3 tệp)/b (4 tệp), có overlap với01–02; không thêm task chính.

Phần triển khai được chia thành hai task con để mỗi phần không vượt5tệp; không cộng thêm task chính:

- [x] **MVP06.03a** — Trả stage enhancement từ đúng dispatcher đang chạy; tests chứng minh filtered/prepared gray/before rotation, không tính lại để giả debug.
- [x] **MVP06.03b** — Dùng chung writer debug detection cho batch/scan, ghi config/source/hash/version/stages/timing của đúng pipeline; kiểm CLI và ranh giới detection/render.

MVP06.03 đạt15/10: EnhancementStages lấy filtered/preparedgray/before_rotation từ đúng dispatcher, không replay giả. Writer detection dùng chung nhận actualresult, không chạy lại detector; entry_point/run_id/sourcehash đúng scan/batch. config.json full + metadata/sourcePNG/sourceoverlay/H/stages/render/timing/version/dependency; detection/ vàrender/ tách thưmục. 6stage tests,8scanCLI; runtime7runs/92PNG/4detection/14trial,6render+1manual_required. Snapshot tay cùngảnh táichạy giữhashfull/preview/stages; chưa nghiệmthu06.05 rộng hơn. Full777đạt38.83s.

**Checkpoint 06-C1:** Rà bằng chứng nghiệm thu MVP06.01 → MVP06.03; chạy kiểm chứng tập trung tương ứng, giữ mốc đã chạy được và ghi lỗi/chặn trước nhóm tiếp theo.

Đạt15/10/2026: core36tests pipeline/encoder/stages,8scanCLI mới và hồi quy7batchCLI; toànbackend777đạt. QA7runs/92PNG,source/hash/config/stages/preview/rotation vàmanualfailure khớp. img_004 vẫnsaiquad vàBWđenbàn, warningsgiữ; khôngaccuracy hoặcđổi detector. Cổng06/M1 và06.04–06.06 vẫnchờ.

### MVP06.04 — Tính histogram trước threshold

- [x] **MVP06.04** — Tính 256 bin trên ảnh xám thực đưa vào threshold; giữ ngưỡng Otsu nếu có.
- **Xong khi:** Tổng bin bằng số pixel; Adaptive được mô tả là ngưỡng cục bộ.
- **Kiểm chứng:** Kiểm tra histogram fixture và metadata Otsu/Adaptive.
- **Cần trước:** MVP06.03
- **Tệp thực hiện:** `backend/app/processing/histogram.py`, `backend/app/processing/enhancement.py`, `experiments/scan_one.py`, `backend/tests/test_histogram.py`, `backend/tests/test_scan_one.py`.
- **Quy mô:** M (5 tệp code/tests; thêm nối dispatcher/metadata để histogram thuộc đúng lần chạy, tài liệu cập nhật kèm).
- **Bằng chứng 16/10/2026:** 16tests histogram/dispatcher mới và1CLI Adaptive mới; focused25 đạt23.56s, toànbackend794 đạt95.24s. Histogram256 raw counts từ BW prepared_gray sau lọc/CLAHE, trước threshold/xoay; có cả debug=false. Metadata gắn hash PNG/size, Otsu global/actual t hoặc Adaptive local/t=null; Color/Gray/manual_required histogram=null. Hai run thật img_004 có tổng1.510.096pixel/213bin khác0, Otsu t=140; cùng gray cho histogram giống nhau nhưng BW khác. Hash full/preview/stages Otsu trùng mốc06.01–03, nguồn/fixtures giữ nguyên. [Progress](../docs/progress.md), evidence cục bộ `experiments/results/mvp06-04-histogram/verification.json`; không sửa detector/UI hoặc đánh dấu06.05/06.06.

### MVP06.05 — Kiểm chứng tái lập pipeline

- [x] **MVP06.05** — Chạy lại cùng nguồn/config/version trong môi trường hiện tại.
- **Xong khi:** Pixels/config ổn định; stage và full render nhất quán.
- **Kiểm chứng:** So output hai lượt; ghi dependency và thông tin môi trường.
- **Cần trước:** MVP06.04
- **Tệp thực tế:** `backend/tests/test_render.py`, `backend/tests/test_scan_one.py`, `docs/progress.md`.
- **Quy mô:** M (3 tệp; thêm CLI repeat để kiểm cả version/environment/metadata và hai tiến trình).
- **Bằng chứng16/10:** 4core repeat/snapshot và2CLI auto/failure repeat mới; focused45đạt30.73s, full800đạt99.97s.10cặp/20runs thật/fixture tại `experiments/results/mvp06-m1-verified/verification.json`: pixels/config/stages/histogram/H và metadata ổn định trừ run_id/timings; rawsource/code/requirements giữhash, môi trường/version được ghi. QA replay đúng stage/full/preview và manualfailure; không tuyên bố tất định trên mọi máy hoặc accuracy. [M1](../docs/milestone-m1.md).

### MVP06.06 — Ghi mốc lõi xử lý ảnh

- [x] **MVP06.06** — Lưu lệnh chạy, ảnh tốt/xấu và giải thích pipeline trước khi nối web.
- **Xong khi:** M1 có bằng chứng normalize/quad/ba mode/export ảnh và fallback.
- **Kiểm chứng:** Chạy lại script theo hướng dẫn trong tài liệu mốc.
- **Cần trước:** MVP06.05, MVP04.07, MVP05.08
- **Tệp thực tế:** `docs/milestone-m1.md`, `docs/progress.md`, `docs/algorithm-notes.md`.
- **Quy mô:** M (3 tài liệu; thêm hướng dẫn mốc riêng để chạy lại được).
- **Bằng chứng16/10:** M1 có bảng10ca/230PNG của20runs, normalize/autoquad/manual/ba mode/2threshold/4rotation/full-preview/stages/histogram/config. Đã chạy nguyên blockPowerShell trong tài liệu mốc:6CLI trên fixture,3mode/replayBW/blankmanual_required→retrytay; config/full/preview/grayhash vàsource nguyên. Xem các ảnh thuận lợi/bóng/ăn bàn/manual; không giấu lỗiimg_004 hoặc coiPNG làPDF/scanUI.

### AUX06.01 — Rà soát sáu task giai đoạn06

- [x] **AUX06.01** — Đối chiếu đủ6task với đặc tả/hợp đồng/lý thuyết đã phân tích, kiểm mã/tests/runtime và giới hạn.
- **Xong khi:** Ma trận6task có kết luận/bằng chứng, M1 có thể chạy lại; phân biệt lỗi chặn với nợ thuật toán cũ.
- **Kiểm chứng:** 800backend/10cặp20runs/230PNG,8detect28trials;6smokeCLI từ tài liệu; source6cặp/22fixtures nguyên, không đổi thuật toán để qua audit.
- **Cần trước:** MVP06.01–MVP06.06.
- **Tệp thực tế:** `docs/audit-phase-06.md`, `docs/progress.md`.
- **Quy mô:** S (2 tài liệu; không phát hiện lỗi implementation mới chặn cổng06).

**Cổng06/M1 — đạt16/10/2026:** đủ6task và AUX06.01 có bằng chứng. Một lệnh offline normalize→detect/góc tay→sourcewarp→ba mode/rotate→full/preview/config/stages/histogram; manual_required không tạo full giả và retrytay được. Tái lập cùng môi trường đã kiểm; nợ detector05 vẫn mở, chưa scanUI/revision/storage/PDF. [M1](../docs/milestone-m1.md), [audit06](../docs/audit-phase-06.md), [progress](../docs/progress.md). Tiếp theo07.01.

---

## Giai đoạn 07 — Nhập một trang, lưu bền và mở lại qua UI

**Tuần dự kiến:** 2. **Số task:** 9. **Đầu ra cuối giai đoạn:** Một trang được nhập từ UI, lưu vào SQLite/tệp và mở lại sau restart; nguồn hiển thị đúng EXIF.

### MVP07.01 — Chốt schema API MVP

- [x] **MVP07.01** — Ghi contract /api/v1, ID/artifact, full config, revision, error envelope và types.
- **Xong khi:** Schema phản ánh phạm vi đã chốt; thiếu trường lấy default, không kế thừa ngầm config cũ.
- **Kiểm chứng:** Đối chiếu ví dụ request/response với lõi và đặc tả; ghi khác biệt cần thiết.
- **Cần trước:** MVP06.06
- **Tệp thực tế:** `backend/app/schemas/common.py`, `pages.py`, `sessions.py`, `errors.py`, `backend/tests/test_api_schemas.py`, `docs/api-contract.md`.
- **Quy mô:** chia a (5 tệp schemas/tests), b (contract/ví dụ kiểm chứng); không thêm task chính.
- [x] **MVP07.01a** — Kiểu dữ liệu UUID/UTC/config/artifact/revision/session/error và tests executable.
- [x] **MVP07.01b** — Chốt bảng endpoint/status/phạm vi thực thi, kiểm ví dụ JSON và ghi điều chỉnh MVP so đặc tả gốc.
- **Bằng chứng17/10:**21schema tests;5vídụ JSON validate/serialize khôngwarning,13schemas sinhđược; ConfigUpdateRequest.validate_config dùng source_size thật và parse_config, khôngmergeold. Trang mới revision0 theo07.05 (sửa image-contract cũghi1); detectstatus theo coreproposed, khôngsuggested; APIerrorhandlers/routes ngoàihealth chưa nối. [Contract](../docs/api-contract.md), [progress](../docs/progress.md).

### MVP07.02 — Tạo schema SQLite tối thiểu

- [x] **MVP07.02** — Tạo session/page/config/artifact/export metadata, foreign keys và schema_version.
- **Xong khi:** DB khởi tạo lần đầu và đọc lại được; liên kết trang/artifact thuộc đúng bộ tài liệu.
- **Kiểm chứng:** Chạy test quan hệ DB, transaction và restart connection.
- **Cần trước:** MVP07.01
- **Tệp thực tế:** `backend/app/storage/database.py`, `backend/app/storage/models.py`, `backend/app/storage/repository.py`, `backend/tests/test_storage.py`.
- **Quy mô:** M (4 tệp).
- **Bằng chứng17/10:**19storage tests;SQLite6bảng/schema_version1/FKmọikếtnối/UTC/compositeownership/deferredsourcepointer/uniqueorder/rollbackmetadata+DDL/cascade/rejectunknownversion. Runtime `.tmp/verify_mvp07_01_02.py`:2tiếntrình write/reopen, configrevision0/UTC/crosssessionblock/FKcheck rỗng; syntheticmetadata tại `experiments/results/mvp07-01-02-verified/`, khôngghiảnh hoặcclaimedHTTPfeature. Focused40testsđạt;07.03/fileatomic/import/UI vẫnchờ.

### MVP07.03 — Ghi tệp artifact an toàn

- [x] **MVP07.03** — Viết đường dẫn UUID, tệp tạm cùng filesystem, encode thành công rồi đổi tên.
- **Xong khi:** Filename upload không điều khiển path; metadata không trỏ tệp chưa ghi xong.
- **Kiểm chứng:** Gây lỗi ghi/đổi tên; kiểm tra tệp cũ còn và tệp mới không publish.
- **Cần trước:** MVP07.02
- **Tệp thực tế:** `backend/app/storage/files.py`, `backend/app/storage/repository.py`, `backend/tests/test_artifact_files.py`.
- **Quy mô:** M (3 tệp; tách tests file khỏi tests metadata DB).
- **Bằng chứng17/10:**19tests artifact; payload normalized PNG giữ đúng bytes/hash, temporary cùng thư mục/fsync/publish không ghi đè; partial write/fsync/rename lỗi giữ file cũ, collision/traversal/kind/MIME sai bị chặn. Hai junction thật (trong/ngoài root) bị từ chối; verify file trước register; rollback FK và dọn orphan mới, không xóa file active. Runtime9tệp fixture và lỗi rename/commit được kiểm cùng HTTP/restart. [Contract](../docs/api-contract.md), [progress](../docs/progress.md).

**Checkpoint07-C1 — đạt17/10/2026:**07.01–03 đủ schema/DB/file an toàn,40tests schema+DB và19tests artifact trong nhóm78tests tập trung đạt; kiểm byte/hash/owner/FK/rollback/đường dẫn/lỗi publish. Runtime localhost/restart giữ9file fixture. Chưa có use case nhập/UI; không coi checkpoint là cổng07. [Progress](../docs/progress.md).

### MVP07.04 — API tạo và lấy bộ tài liệu

- [x] **MVP07.04** — Thêm create/list/detail tài liệu, danh sách trang theo position và kiểm tra membership.
- **Xong khi:** Các endpoint trả metadata thật từ SQLite, ID sai trả 404.
- **Kiểm chứng:** Chạy HTTP create → list → detail và kiểm tra bộ tài liệu rỗng.
- **Cần trước:** MVP07.03
- **Tệp thực tế:** `backend/app/services/sessions.py`, `backend/app/storage/repository.py`, `backend/app/api/sessions.py`, `backend/app/api/errors.py`, `backend/app/main.py`, `backend/tests/test_sessions_api.py`, `backend/tests/test_health.py`.
- **Quy mô:** chia a/b do7tệp; task con không cộng lại vào tổng chính.
- [x] **MVP07.04a** — Query session/list/count/ordered page-config theo owner và service DTO/commit; repository/service/test_sessions_api (3tệp).
- [x] **MVP07.04b** — Router create/list/detail, lifespan DB/store, handler lỗi/OpenAPI và health test dùng DB tạm; router/errors/main/test_sessions_api/test_health (5tệp, test API dùng chung với a).
- **Bằng chứng17/10:**18APItests +health, SQLite thật; create201/list200/detail200/rỗng, order/membership, pagination stable ties, UUID404/bodyquery400, commit500 rollback/sanitized,405 giữ Allow, OpenAPI3paths đúng ErrorEnvelope/không422 giả. Runtime Uvicorn localhost create/list/detail, hai trang thứ tự đúng/không lẫn tài liệu khác, restart tiến trình riêng cùngDB giữ metadata/9file. Trang runtime được seed qua lower layer, chưa là import07.05/upload07.07. [Progress](../docs/progress.md).

### MVP07.05 — Service nhập và commit một trang

- [x] **MVP07.05** — Lưu original/normalized/thumbnail, dimensions và config revision0 bằng use case.
- **Xong khi:** Nguồn được giữ; initial confirmed=false; DB lỗi dọn tệp mới chưa tham chiếu.
- **Kiểm chứng:** Test import đúng và lỗi commit sau ghi tệp; kiểm tra artifact/DB.
- **Cần trước:** MVP07.04, MVP02.06
- **Tệp thực tế:** `backend/app/services/imports.py`, `backend/app/storage/repository.py`, `backend/tests/test_imports.py`.
- **Quy mô:** M (3 tệp).
- **Bằng chứng17/10:**14import tests trên SQLite/tệp thật; original bytes/MIME theo nội dung, normalizedPNG đúng payload/hash/pixels sauEXIF/alpha, thumbnail320 kể cả cạnh1, configrevision0/confirmedfalse/cornersnull, append/update timestamp/reopen. Encode/write/commit lỗi giữ trang cũ; session xóa giữa lúc nhập dọn file mới. Writer lock trước count/position: hai lượt tranh suất20 chỉ một commit, không orphan. Runtime2trang/6file qua executor và restart thật tại mvp07-05-06-verified/; không là endpoint upload07.07. [Contract](../docs/api-contract.md), [progress](../docs/progress.md).

### MVP07.06 — Tạo executor dùng chung

- [x] **MVP07.06** — Giới hạn một tác vụ ảnh active, tối đa hai chờ; giải phóng slot khi lỗi/hủy chờ.
- **Xong khi:** Normalize/detect/render/export dùng cùng cửa xử lý; quá quota trả 429; shutdown đóng worker.
- **Kiểm chứng:** Chạy tác vụ giả có chặn; kiểm tra slot và health vẫn phản hồi.
- **Cần trước:** MVP07.05
- **Tệp thực tế:** `backend/app/services/processing_executor.py`, `backend/app/main.py`, `backend/app/api/errors.py`, `backend/tests/test_processing_executor.py`.
- **Quy mô:** M (4 tệp, thêm mapping ProcessingBusyError→429/ErrorEnvelope).
- **Bằng chứng17/10:**5executor tests, FIFO/mộtworker/haiwaiting/429, queuedcancel trảslot/khôngchạy, activecaller cancel vẫn giữslot đến khi threadxong, exception khônglàm chếtworker, shutdowncancelqueued/đợiactive/join/idempotent. app.state.processing mộtinstance/lifespan, health còn phản hồi. Runtime probe localhost kiểm429/cancel/FIFO/import/commitfault/recovery, health14.19ms lượt này, restart/shutdown join thread. Các route ảnh sau phải dùng cùnginstance; chưa tạo route sản phẩm giả. [Contract](../docs/api-contract.md), [progress](../docs/progress.md).

**Checkpoint07-C2 — đạt17/10/2026:**07.04–06 đủ metadataAPI/import/worker;97tests tập trung schemas/DB/files/API/import/executor/health đạt với -W error. Runtime localhost import2trang/6file,429/cancellation/health/commitrollback/workerrecovery/restart vàshutdown giữnguồn/config/order. Upload/artifactGET/UI/cổng07 còn chờ. [Progress](../docs/progress.md).

### MVP07.07 — API upload và đọc artifact

- [x] **MVP07.07** — Upload multipart từng tệp, đếm byte theo khối, kiểm tra 20 trang trước commit; đọc tệp qua ID.
- **Xong khi:** Vượt byte/pixel/quota bị từ chối; artifact có MIME đúng; không public data directory.
- **Kiểm chứng:** Chạy HTTP upload hợp lệ/sai/oversize; đọc normalized/thumbnail; thử ID/path lạ.
- **Cần trước:** MVP07.06
- **Tệp thực tế:** `backend/app/api/pages.py`, `artifacts.py`, `errors.py`, `backend/app/storage/repository.py`, `backend/app/main.py`, `backend/tests/test_import_api.py`, `test_sessions_api.py`; tái dùng imports không sửa.
- **Quy mô:** chia a/b vì7tệp; không tăng số task chính.
- [x] **MVP07.07a** — Multipart boundedstream/đếmfile/validator/worker/error mapping: pages/errors/main/test_import_api (4tệp).
- [x] **MVP07.07b** — ArtifactGET/owner/fileverify/MIME/headers/OpenAPI5paths: artifacts/repository/main/test_import_api/test_sessions_api (5tệp; main/testimport dùng chung với a).
- **Bằng chứng17/10:**20HTTPtests mới, đúng15MiB đượcnhận/quábyte-pixel-page bịchặn, malformed/cutmultipart đóngspoolfile,1file/0textfield, EXIF/alpha/MIME thật/filename traversal, hash/pathfilecorruption, DBcommitrollback vàrouteupload429 khiworkerđầy/healthcònphảnhồi. ArtifactGET quaUUID, verify sauDBtransaction, khôngpublicdata. Browser/API sản phẩm đãnhập2fixture+img_004. [Audit](../docs/audit-phase-07.md), [progress](../docs/progress.md).

### MVP07.08 — UI nhập ảnh và chọn nguồn

- [x] **MVP07.08** — Nối client/errors/types, danh sách tài liệu tối thiểu, upload tuần tự và thumbnails.
- **Xong khi:** Tạo tài liệu → chọn nhiều ảnh → thấy lỗi từng tệp → chọn trang → nguồn đúng EXIF.
- **Kiểm chứng:** Chạy trình duyệt với một JPEG, PNG alpha và file lỗi; kiểm tra console/network.
- **Cần trước:** MVP07.07
- **Tệp thực tế:** `frontend/src/api/client.ts`, `types/scanner.ts`, `pages/ScannerPage.tsx`, `components/UploadPanel.tsx`, `PageList.tsx`, `SourcePreview.tsx`, `frontend/src/App.tsx`, `styles.css`.
- **Quy mô:** chia a/b vì8tệp; không thêm task chính.
- [x] **MVP07.08a** — Client/DTO/Quad4điểm/enums và batch tuần tự/errors từngfile: client/types/UploadPanel (3tệp).
- [x] **MVP07.08b** — Giao diện tài liệu/trang/nguồn/loading-empty-error/responsive: ScannerPage/PageList/SourcePreview/App/styles (5tệp).
- **Bằng chứng17/10:**Browser thật tạo tài liệu, filechooser chọnJPEGEXIF6→fakeJPG→PNGalpha,2trangđượcgiữ/1lỗiriêng, chọn nguồn64×96 đúngEXIF; xem img_0041536×2048, PNGhashkhớpmanifest. Kếtquảbatch giữ sau refreshmetadata; chọnlạidoc khôngmấttrang.320/768/1024/1440px khôngtrànngang; keyboardfocus/labels/console cuối đạt, npm typecheck/buildđạt. [Audit](../docs/audit-phase-07.md), [progress](../docs/progress.md).

### MVP07.09 — Kiểm chứng dữ liệu sau restart

- [x] **MVP07.09** — Kiểm tra UI refresh, tắt/mở backend và mở tài liệu đã nhập.
- **Xong khi:** Tên/nguồn/thứ tự/config còn đúng; lỗi một ảnh không mất trang khác.
- **Kiểm chứng:** Thực hiện restart thật và kiểm tra DB cùng artifact; ghi evidence.
- **Cần trước:** MVP07.08
- **Tệp thực tế:** `backend/tests/test_import_api.py`, `docs/progress.md`; script/JSON/screenshot kiểm chứng nằm trong .tmp/results ignored.
- **Quy mô:** S (2 tệp; tái dùng tests upload/reopen, bổ sung bằng chứng tiến trình/browser thật).
- **Bằng chứng17/10:**UIrefresh giữ session/page; graceful shutdownbackendv1→UIrefreshbáolỗi→backendv2cùngDB→Tảilại mởđúngtài liệu/nguồn. before-restart.json/verification.json đối chiếu name/order/fullconfig/revision/IDs/dimensions và6artifactbytes/hash nguyên;2tranghợplệ, fakefilekhôngpersist. [Audit](../docs/audit-phase-07.md), [progress](../docs/progress.md).

### AUX07.01 — Rà cả chín task giai đoạn 07

- [x] **AUX07.01** — User yêu cầu17/10/2026: sau07.07–09, đối chiếu9task với đặc tả/MVP/code/tests/runtime/browser và ghi giới hạn.
- **Xong khi:** Mỗi task có evidence, sửa lỗi chặn; phân biệt lưu/mở nguồn với quét/renderUI, không suy từ testcount thành accuracy.
- **Kiểm chứng:** Ma trận9task, suite backend/typecheck/build, browser create/upload/error/select/refresh/restart, artifact snapshot/hash, rà an toàn/ownership/cleanup/quota/worker.
- **Cần trước:** MVP07.09
- **Tệp thực tế:** `docs/audit-phase-07.md`, `docs/progress.md`.
- **Quy mô:** S (2 tài liệu; thêm1test cho routeupload429 trong test_import_api đãcó, không thêm task chính).
- **Bằng chứng17/10:**Audit9row/20HTTPtests mới/117ca phase07 trong916backend; UI4viewport/keyboard/console và2trang6blob restart thật. Sửa multipartspool leak, batchresult unmount, reselectdoc clearsselection; khôngnớiquota hoặc sửa core/detector. Cổng07đạt, next08.01.

**Cổng07 — đạt17/10/2026:**Đủ9task/AUX07.01, nhập từUI/lưuSQLite+tệp/mởlại saurestart/nguồnđúngEXIF;916backendtests vàfrontendtypecheck/build/browser đạt. Checkpoint07-C1/C2 giữ; chưa làM2quét/renderUI. [Audit9task](../docs/audit-phase-07.md), [progress](../docs/progress.md). Tiếp theoMVP08.01 fullconfig/góc/confirmed/revisionCAS.

---

## Giai đoạn 08 — Chỉnh góc và render một trang từ UI

**Tuần dự kiến:** 2. **Số task:** 10. **Đầu ra cuối giai đoạn:** Một ảnh quét tay được từ UI; canvas đúng; preview đúng revision và có thể xem phóng to.

### MVP08.01 — API cập nhật config có revision

- [x] **MVP08.01** — Validate quad/full config; tăng revision đúng một lần trong transaction ngắn.
- **Xong khi:** expected_revision cũ trả 409; lưu góc cần confirmed rõ; response có effective_config.
- **Kiểm chứng:** Chạy API config đúng/sai, NaN/quad tự giao, hai update cùng revision.
- **Cần trước:** MVP07.09, MVP03.08, MVP04.01
- **Tệp thực tế:** `backend/app/services/page_config.py`, `backend/app/storage/repository.py`, `backend/app/api/pages.py`, `backend/app/api/errors.py`, `backend/tests/test_config_api.py`, `backend/tests/test_sessions_api.py`.
- **Quy mô:** Tách hai lát dưới đây vì6tệp, không cộng lại parent vào tổng task chính.
  - [x] **MVP08.01a** — Service/DB writer lock trước lookup/CAS, fullconfig/no-op/confirmed và source/warp dimensions thật.
  - [x] **MVP08.01b** — PUTconfig/400–404–409/error details/OpenAPI và kiểm thử HTTP/rollback/concurrency.
- **Bằng chứng17/10:**25configAPI tests đạt; fullreplacement/defaults/inactive/no-op giữ cả timestamps, quad/NaN/Infinity/activeAdaptive block sai400, owner/UUID404, hai update đồngrevision chỉ1commit+1conflict409, commitfault rollback. Runtime HTTP/DB riêng với WrongEXIF.jpg có config/no-op/409/400/restart; xem [progress](../docs/progress.md).

### MVP08.02 — Service render theo snapshot

- [x] **MVP08.02** — Chụp nguồn/config, yêu cầu confirmed, xử lý ngoài transaction và kiểm tra revision trước commit.
- **Xong khi:** Full render/preview đúng revision; lỗi thời không publish; lỗi xử lý giữ source/config.
- **Kiểm chứng:** Test thay config/xóa trang trong lúc render và lỗi encode/commit.
- **Cần trước:** MVP08.01, MVP06.05
- **Tệp thực tế:** `backend/app/services/renders.py`, `backend/tests/test_render_service.py`; tái dùng repository helpers đã thêm08.01a.
- **Quy mô:** S (2 tệp mới).
- **Bằng chứng17/10:**21service tests đạt: full/preview pixels/hash/revision, PNG nội bộ>15MiB/preview1000×667, source/config/oldrender giữ khi process/encode/write/register/commit lỗi; config/page/session đổi trong lúc CPU bị chặn đều từ chối trước publish. Runtime service thật tạo2PNG, artifactGET đúng bytes, revision2/render_revision1 giữ sau restart; chưa renderHTTP/UI. [Hợp đồng](../docs/api-contract.md), [progress](../docs/progress.md).

### MVP08.03 — API render qua executor

- [x] **MVP08.03** — Thêm POST render, error envelope và artifact IDs/dimensions/timings.
- **Xong khi:** HTTP render trả kết quả thật; chưa xác nhận hoặc lệch revision bị từ chối.
- **Kiểm chứng:** Chạy upload → config → render → GET output; kiểm tra health và 409/429.
- **Cần trước:** MVP08.02, MVP07.06
- **Tệp thực tế:** `backend/app/api/pages.py`, `backend/app/api/errors.py`, `backend/tests/test_render_api.py`, `backend/tests/test_sessions_api.py`; tái dùng schemas hiện có.
- **Quy mô:** M (4 tệp).
- **Bằng chứng17/10:**21HTTP render tests mới; focused90 với config/service/session/executor đạt-Werror, full983passed139.55s. Upload→config→render→GET PNG đúng core/owner/hash/revision,409draft/stale/404owner/400body/429 cùngworker/health vẫn200, mutationgiữaCPU khôngpublish,500sanitized/workerphụchồi. Runtime2tiếntrình HTTP thật/restart tại mvp08-03-04-verified/, debug=true trả DEBUG_NOT_AVAILABLE rõ vì persistdebug thuộc09.05. [Progress](../docs/progress.md).

**Checkpoint 08-C1 — đạt17/10/2026:** Đủ08.01–03,25configAPI/21service/21renderHTTP tests, focused90 và full983 đạt; runtime upload/config/render/artifactGET/restart quaAPI sản phẩm, source/config giữ khi lỗi/stale, sharedworker/health/409/429 được kiểm. [Ma trận nghiệm thu](../docs/progress.md). Chưa M2/canvasUI/debugPDF.

### MVP08.04 — Mapping canvas theo CSS pixel

- [x] **MVP08.04** — Viết contain scale/offset và source↔canvas↔normalized; backing store theo DPR.
- **Xong khi:** Round-trip sai số ≤1 CSS pixel trên portrait/landscape/HiDPI.
- **Kiểm chứng:** Chạy test transform và kiểm tra resize canvas ở hai DPR.
- **Cần trước:** MVP07.08, MVP03.01
- **Tệp thực tế:** `frontend/src/components/cornerGeometry.ts`, `frontend/src/components/cornerGeometry.test.mjs`, `frontend/package.json`.
- **Quy mô:** M (3 tệp; native Node24 runner, không dependency mới).
- **Bằng chứng17/10:**27tests Node đạt/typecheck/build đạt; W/H contain và W−1/H−1 tọa độ, CSSresize/clientrect/subpixel/portrait/landscape/2×2/thin/DPR1–1.25–2/invalid inputs. Browser canvas thật8tổhợp source×CSS×backingDPR1–2,22trạngthái, maxerror5.684e−14CSSpx; handle center đọc đúng pixel, console trống. DPRbacking được ép thử, deviceDPR thực1; chưa canvaseditor/hit-test/clamp/quadvalidation của05–06. [Hợp đồng](../docs/image-contract.md), [progress](../docs/progress.md).

### MVP08.05 — Vẽ vùng cắt và handle

- [x] **MVP08.05** — Vẽ normalized source, mask ngoài polygon và bốn handle ID ổn định.
- **Xong khi:** Overlay không đổi byte nguồn; letterbox/resize không lệch góc.
- **Kiểm chứng:** Mở ảnh dọc/ngang trên trình duyệt; resize và so vị trí các góc.
- **Cần trước:** MVP08.04
- **Tệp thực tế:** `frontend/src/components/CornerEditor.tsx`, `frontend/src/components/SourcePreview.tsx`, `frontend/src/styles.css`.
- **Quy mô:** M (3 tệp, nối vào viewer thật).
- **Bằng chứng17/10:**Ảnh normalizedPNG giữ nativeimg/object-fit contain, canvasmaskevenodd/drawstroke theo mapping04,4button44CSSpx ID0–3 ổn định. Browser ảnh thật480×640 vàfixture4×2 tại320/768/1440, maxlệchhandle≈.021CSSpx<1; backingDPR1/2/maskalpha140ngoài-0trong đúng. Metadata4session/7page và21hashsource trước/sau nguyên. Build/typecheck và51frontendtests đạt; không lưu/confirm/render góc nháp. [Progress](../docs/progress.md).

### MVP08.06 — Kéo góc bằng Pointer Events

- [x] **MVP08.06** — Thêm hit test, pointer capture, giới hạn điểm và validate quad dự kiến.
- **Xong khi:** Chuột/cảm ứng kéo được; cancel không kẹt; vùng trùng/lõm/tự giao có thông báo.
- **Kiểm chứng:** Thử kéo ra ngoài canvas, tạo bow-tie và hủy thao tác.
- **Cần trước:** MVP08.05
- **Tệp thực tế:** `frontend/src/components/CornerEditor.tsx`, `frontend/src/components/cornerGeometry.ts`, `frontend/src/components/cornerGeometry.test.mjs`, `frontend/src/styles.css`.
- **Quy mô:** M (4 tệp; tái dùng script Node24 test đã có).
- **Bằng chứng17/10:**51tests (24mới),936quad/6source sizes frontendcode khớpcore,216geometry backend đạt-Werror. Browsermouse capture/clamp/bowtie/keyboard đạt; touchsynthetic move/cancel/lostcapture/Escape/blur/secondary qua component thật, releasecapture vàrestoređúng. Sửa clickkhôngkéo bịdirtydoULP và mobilegrid3trangtràn320px; browser6responsivecases đạt. Touchchưa trênthiếtbịvậtlý; cornerslocal/chưaAPIpersist thuộc07. [Hợp đồng](../docs/image-contract.md), [progress](../docs/progress.md).

**Checkpoint 08-C2 — đạt17/10/2026:** Đủ04mapping/05overlay/06pointer,51frontendtests/typecheck/build,936quadparity/216coregeometry, browser6responsivecases/DPRmask1–2/mousecapture/clamp/invalidquad/cancel vàtouchsynthetic đạt.21sourcehash/4session metadata nguyên. [Ma trận nghiệm thu](../docs/progress.md). Next08.07 draft/persisted vàxácnhận, chưaM2/renderUI.

### MVP08.07 — Lưu draft và xác nhận vùng

- [x] **MVP08.07** — Tách draft/persisted config; nút toàn ảnh/đặt lại/xác nhận lưu config mới.
- **Xong khi:** Sửa góc làm mất trạng thái đã xác nhận; chưa lưu không render/xuất nhầm kết quả cũ.
- **Kiểm chứng:** Thử sửa sau xác nhận, dùng toàn ảnh và đổi trang; kiểm tra request config.
- **Cần trước:** MVP08.06, MVP08.01
- [x] **MVP08.07a** — Full config DTO/client và state draft/persisted/CAS, kiểm thử native Node.
- [x] **MVP08.07b** — Nối controls/controlled CornerEditor và reset theo trang/refresh; kiểm browser thật.
- **Tệp thực tế:** a: `frontend/src/types/scanner.ts`, `frontend/src/api/client.ts`, `frontend/src/api/client.test.mjs`, `frontend/src/hooks/pageRenderState.ts`, `frontend/src/hooks/pageRenderState.test.mjs`; b: `frontend/src/components/CornerEditor.tsx`, `frontend/src/components/SourcePreview.tsx`, `frontend/src/pages/ScannerPage.tsx`, `frontend/src/styles.css`.
- **Quy mô:** M+M, chia a/b vì >5 tệp; không cộng lại task cha. Package test/TS config dùng chung lát08.08.
- **Bằng chứng17/10:** Sửa góc bỏ confirmed, giữ inactive/fullconfig; fullimage/reset/save-draft/confirm qua API thật, cancel phục hồi full snapshot trước kéo. Đổi trang/refresh đọc config mới; nháp chưa lưu bỏ có nhắc trên UI. Unknown commit được chặn retry và GET đối soát, giữ nháp unconfirmed. 64frontend tests/typecheck/build và browser đạt. [Progress](../docs/progress.md).

### MVP08.08 — Nối nút render với request hiện hành

- [x] **MVP08.08** — Update config đầy đủ rồi render revision mới; nhận response đúng page/revision.
- **Xong khi:** Đổi trang hoặc response trễ không ghi đè; lỗi giữ kết quả cũ với nhãn rõ.
- **Kiểm chứng:** Làm chậm request có kiểm soát, đổi trang/cấu hình và kiểm tra preview.
- **Cần trước:** MVP08.07, MVP08.03
- [x] **MVP08.08a** — Async save→render/state guards và hook, kiểm deterministic race bằng Node.
- [x] **MVP08.08b** — Preview/error/stale labels, runtime API thật và controlled delays; lưu evidence/cập nhật tài liệu.
- **Tệp thực tế:** a: `frontend/src/hooks/usePageRender.ts`, state/tests/client/types dùng chung08.07; b: `frontend/src/components/SourcePreview.tsx`, `frontend/src/styles.css`, `frontend/package.json`, `frontend/tsconfig.json`; tài liệu tại docs/progress/README/contracts và checklist.
- **Quy mô:** Chia a/b tối đa5 tệp code mỗi lát (state/client/types chia sẻ07, không đếm task hai lần); không thêm dependency/framework test.
- **Bằng chứng17/10:** PUTfullconfig/CAS trước POSTexpected_revision trả về, đúng page/rev/generation/draft version mới nhận. Edit trong save chặn render, edit/đổi trang trong render bỏ late response. Lỗi giữ preview cũ có nhãn; mất response sau commit bắt GET trước retry. Browser warp thực nguồn1536×2048→1076×1281/preview840×1000 và EXIF64×96→63×95. 64frontendtests,67backend focused -Werror/typecheck/build đạt;5session cũ/21sourcehash nguyên. [Progress](../docs/progress.md). 08-C3 vẫn chờ09, chưaM2.

### MVP08.09 — So sánh và phóng to kết quả

- [x] **MVP08.09** — Tạo view nguồn/kết quả có nhãn và phóng to ảnh render để xem chữ.
- **Xong khi:** Xem được nét ở độ phân giải render; không nhầm thumbnail hoặc overlay với ảnh xuất.
- **Kiểm chứng:** Mở chữ nhỏ/highlight, zoom và quay lại chỉnh source corners.
- **Cần trước:** MVP08.08
- **Tệp thực tế:** `frontend/src/components/ComparisonView.tsx`, `frontend/src/components/SourcePreview.tsx`, `frontend/src/components/CornerEditor.tsx`, `frontend/src/styles.css`.
- **Quy mô:** M (4 tệp, giữ ScannerPage/state/CAS hiện có).
- **Bằng chứng17/10:** Comparison dùng normalizedsource/render_artifact_id, nhãn/size/rev/stale rõ;100%CSS1009×1406/200%2018×2812 đúngfull, khôngpreview718×1000. Scroll/keyboard/returnfocus0/edit/confirmedfalse/reset đạt. Browser320/768/1440 khôngtràn, fullsource/fullrendercolors/hash nguyên;64frontend/typecheck/build đạt. Đổi nhãn “Hình học vùng hợp lệ”, nhắc default chưa nhận diện biên. [Smoke](../frontend/tests/scanner-smoke.md), [audit](../docs/audit-phase-08.md).

**Checkpoint 08-C3 — đạt17/10/2026:**07draft/confirm,08save→render đúngsnapshot/late/failure và09fullcomparison/zoom đạt.64frontendtests/typecheck/build, browserquét/so sánh/100–200%/returnedit vàfullbackend983-Werror đạt. [Audit](../docs/audit-phase-08.md), [progress](../docs/progress.md).

### MVP08.10 — Kiểm chứng quét tay đầu-cuối

- [x] **MVP08.10** — Chạy UI nhập → chọn tay → xác nhận → warp/render → xem kết quả.
- **Xong khi:** Luồng quét tay hoàn thành độc lập detector; các góc màu không lật/xoắn.
- **Kiểm chứng:** Browser smoke portrait/landscape/HiDPI và backend focused tests; lưu evidence.
- **Cần trước:** MVP08.09
- **Tệp thực tế:** `docs/progress.md`, `frontend/tests/scanner-smoke.md`; evidence/scripts ngoàiGit; sửa contextmanager CSV trong `backend/tests/test_detect_batch.py` khi strictaudit phát hiện.
- **Quy mô:** M (2tài liệu+1test cũ; không đổi core/API/dependency).
- **Bằng chứng17/10:** UIcreate/filechooser3files/quét tay:portraitEXIF64×96→63×95, ngang96×64→95×63, detail1200×1600→1009×1406/preview718×1000.12mẫu4màu distinct projectH khớp0kênh,3previewbyteequal từfull;forcedDPR1/2 giữgóc/mask140–0,maxhandleerror.01685323CSSpx.7session/10page/30sourcehash cũ nguyên. Full983-Werror142.37s/64frontend192.3675ms/typecheck/build/browser/console đạt. [Smoke](../frontend/tests/scanner-smoke.md), [audit](../docs/audit-phase-08.md).

### AUX08.01 — Rà cả mười task giai đoạn 08

- [x] **AUX08.01** — User yêu cầu17/10/2026: sau09–10, đối chiếu10task với MVP/contracts/code/tests/browser; ghi lỗi và giới hạn.
- **Xong khi:** Mỗi task có bằng chứng; sửa lỗi chặn; phân biệt quét tayM2 với tựdetect09, không suy testcount thànhaccuracy.
- **Kiểm chứng:** Ma trận10task/983backendstrict/64frontend/build, browsermanualscan/comparison/zoom/DPR/sourcehash/colourorientation; kiểm các state/revision/failure gates.
- **Cần trước:** MVP08.10
- **Tệp thực tế:** `docs/audit-phase-08.md`, `docs/progress.md`; tái dùng smoke/CLI/API/core tests và evidence đã có.
- **Quy mô:** S (2tài liệu; lỗiCSVtest sửa cùng08.10).
- **Bằng chứng17/10:** Audit10row đạt; sửa testCSVunclosedfile không suppress-Werror và nhãnquad dễhiểu nhầm; core/CLI/requirements nguyên, không đổi thuậttoán/preset/quota. Full983/64frontend/browser/rasterchecks đạt. Reopenauto-resultUUID deferred10.07, physicaltouch/HiDPI chưatest; [audit](../docs/audit-phase-08.md).

**Cổng08/M2 — đạt17/10/2026:**10task/AUX08.01 đủbằngchứng, quét tay quaUI→warp→full/preview→so sánh/zoom đúngsnapshot, config/nguồn lưu bền. Checkpoint08-C1/C2/C3 đạt;983backend-Werror/64frontend/typecheck/build/browser/dọc-ngang/forcedDPR đạt. [Audit10task](../docs/audit-phase-08.md), [progress](../docs/progress.md). NextMVP09.01detectAPI; M2 chưanghiệmthu autodetect/debugUI/PDF/reopenauto-result.

---

## Giai đoạn 09 — Tự nhận diện, tham số và giải thích trên UI

**Tuần dự kiến:** 3. **Số task:** 8. **Đầu ra cuối giai đoạn:** Detect → sửa/xác nhận → chọn mode → render chạy; các bước thật và histogram truy vết được trên UI.

### MVP09.01 — API detect và detection run

- [x] **MVP09.01** — Nối detector qua executor; ghi run ID/source/version/trial cho debug.
- **Xong khi:** Detect không ghi đè config đã xác nhận; manual_required trả 200; debug có nguồn gốc.
- **Kiểm chứng:** Chạy detect hai lần và đối chiếu run/stage, kiểm tra config không đổi.
- **Cần trước:** MVP08.10, MVP05.08
- **Tệp dự kiến:** `backend/app/api/pages.py`, `backend/app/services/detection.py`, `backend/app/schemas/pages.py`, `backend/tests/test_detection_api.py`.
- **Quy mô:** M (4 tệp dự kiến).

**Lát triển khai09.01 (không cộng task):** (a) DetectionRun/schema2/migration+tests; (b) shared source loader/service/route/schema/error; (c) API/OpenAPI/rollback/executor regressions. Mỗi lát kiểm trước khi nối lát sau.

**Bằng chứng18/10:** 11API+2migrationtests; hai run cùng ảnh có ID và stageUUID riêng, hash/stage/trial/timing thật; config/confirmed/timestamps nguyên. manual_required200, lỗi400/404/429/500; hỏng ghi/commit dọn stage mới, config đổi trong CPU không bị ghi đè, xóa trang không publish. DBv1→v2 rollback/idempotent/reopen và migration thật giữ8session/13page/39sourcehash. Full996backend-Werror đạt. [Chi tiết](../docs/progress.md).

### MVP09.02 — UI nhận góc đề xuất

- [x] **MVP09.02** — Nối nút tự nhận diện, loading/cảnh báo, fallback vùng cách mép 5%.
- **Xong khi:** Góc vào draft chưa confirmed; score ghi là heuristic; fallback kéo tay được.
- **Kiểm chứng:** Chạy ảnh tốt/nền khó, đổi trang khi detect trả trễ và xác nhận tay.
- **Cần trước:** MVP09.01
- **Tệp dự kiến:** `frontend/src/pages/ScannerPage.tsx`, `frontend/src/components/CornerEditor.tsx`.
- **Quy mô:** S (2 tệp dự kiến).

**Lát triển khai09.02 (không cộng task):** (a) DTO/client/state/controlled-response tests; (b) SourcePreview/CornerEditor/CSS và browser thật. Tệp thực tế mở rộng ngoài dự kiến để giữ logic trong state hiện hữu, không tạo tầng mới.

**Bằng chứng18/10:** 68frontendtests/typecheck/build đạt; UI anhtestnew proposed≈0.635, img_004 warning≈0.468, blank manual_required→5% kéo được. Nút loading, nháp false, xác nhận tay→render201×285 thật. Giữ phản hồi thật rồi sửa góc/đổi trang: không ghi đè nháp/trang mới; lỗi500 giữ góc. Responsive320/768 và console sạch. Score ghi heuristic, khôngaccuracy. [Chi tiết](../docs/progress.md). Checkpoint09-C1 còn chờ09.03.

### MVP09.03 — UI chọn mode và bộ lọc

- [x] **MVP09.03** — Thêm color/gray/bw, None/Median/Gaussian và CLAHE bật/tắt theo mode.
- **Xong khi:** Gửi full config; điều khiển inactive rõ; đổi mode không tích lũy xử lý lên ảnh cũ.
- **Kiểm chứng:** Chạy ba mode cùng góc với highlight và chữ tiếng Việt.
- **Cần trước:** MVP09.02, MVP04.07
- **Tệp dự kiến:** `frontend/src/components/FilterPanel.tsx`, `frontend/src/pages/ScannerPage.tsx`.
- **Quy mô:** S (2 tệp dự kiến).

**Checkpoint 09-C1 — đạt18/10/2026:** rà09.01run/source/trial/stage/config-immutable,09.02proposal/manual/late-response và09.03fullconfig/mode/inactive/sourcefresh.273backendtests liên quan/71frontend/typecheck/build/browser đạt;9renderfull/previewbyteequal,9session/48sourcehash cũ nguyên. Khôngclaimaccuracy hoặc cổng09; next09.05 sau09.04đãđạt. [Bằng chứng](../docs/progress.md).

**Bằng chứng09.03/18–10:** FilterPanel/SourcePreview/state/CSS và state tests (5tệp thực tế, không đổi API). Color/Gray/BW cùnggóc trênchữViệt/highlight, None/Gaussian5/Median3 vàCLAHE4 chạy thật. Giữ fullinactive/corners/confirmation, inputcopy và late-save/render/detect tests;71frontend/typecheck/build đạt. RenderlạiColor sauGray/BW bằng byteColorbanđầu; source khôngđổi. [Chi tiết](../docs/progress.md).

### MVP09.04 — UI chỉnh Otsu và Adaptive

- [x] **MVP09.04** — Thêm threshold method, block/C hợp lệ và nút render; debounce chỉ nếu bật auto-preview.
- **Xong khi:** Otsu không hiện block/C đang active; backend validate lại; không render mỗi pointer move.
- **Kiểm chứng:** Thử giá trị biên, ảnh bóng và thay tham số nhanh; kiểm tra network/revision.
- **Cần trước:** MVP09.03
- **Tệp dự kiến:** `frontend/src/components/FilterPanel.tsx`, `frontend/src/hooks/usePageRender.ts`.
- **Quy mô:** S (2 tệp dự kiến).

**Bằng chứng09.04/18–10:** nativeblockselectlẻ3–151/Cslidernguyên−20..30; BWOtsu khóa block/C, modeinactive khóa controls/giữgiátrị. Đổi nhanh min→max→31/C10 khôngrequest; explicitPUTCAS→render đúngrevision. Ảnhbóngimg_003 chạyOtsu/Adaptive151/C30, ảnhnhỏwarp95×63 từchối151 bằng400/revision0giữ, GET→block3/C−20→confirm/renderđạt.9renderfull/preview khớpbytecorefresh;273backendtests liên quan đạt. [Chi tiết](../docs/progress.md).

### MVP09.05 — Lưu debug render theo revision

- [x] **MVP09.05** — Persist gray trước threshold, warp, histogram, config/version/timing cùng render.
- **Xong khi:** Debug revision hiện hành đúng; thiếu stage có trạng thái rõ; không dùng placeholder.
- **Kiểm chứng:** So output/stage/config ở hai revision và sau restart.
- **Cần trước:** MVP08.02, MVP06.04
- **Tệp dự kiến:** `backend/app/services/renders.py`, `backend/app/storage/repository.py`, `backend/tests/test_render_service.py`.
- **Quy mô:** M (3 tệp dự kiến).

**Lát09.05 (khôngcộngID):** (a) RenderRun/schema3/migrationv1-v2+rollback; (b) corecapture→encode→atomicpersist/snapshot/cleanup; (c) regressionstage/histogram/single-dispatch/fault/reopen. Tệp thực tế vượt dự kiến do runmetadata cần bảngriêng, không gắnJSON vàoảnhPNG.

**Bằng chứng18/10:**1031backend-Werror;4mode/threshold casesstagepre-rotation vàNumPyhist, debugbật/tắtcùngfullbytes, dispatcherchỉ1lần, stale3mutation×debugon-off, faultstagethứ2/commit sauINSERTdọnmọifilemới. Runtime2revision/2restart giữconfig/H/hash/actualt/timing;10session/57sourcehashcũ nguyên. [Chi tiết](../docs/progress.md).

### MVP09.06 — API lấy các bước xử lý

- [x] **MVP09.06** — Trả artifact/metadata debug theo render revision hoặc detection run ID.
- **Xong khi:** Không trộn debug cũ; ID sai trả lỗi ổn định; artifact truy cập qua route hiện có.
- **Kiểm chứng:** Gọi endpoint revision hiện tại/cũ/sai và run có/không candidate.
- **Cần trước:** MVP09.05, MVP09.01
- **Tệp dự kiến:** `backend/app/api/pages.py`, `backend/app/schemas/pages.py`, `backend/tests/test_debug_api.py`.
- **Quy mô:** M (3 tệp dự kiến).

**Lát09.06 (khôngcộngID):** (a) DebugQuery/DebugRead + readonlylookup/ownership/missingfile; (b) routes/errors/OpenAPI + query/history/legacy/detection tests.

**Bằng chứng18/10:** GETtheorevision/render_run_id/detection_run_id, defaultcurrent, oldrun/samerevdebugfalse khôngtrộn; proposed/manual vàdebugoff, invalid400/unknown404, corruptbinding500sanitize, missingfile/hash/DB/ref/owner→incomplete.5JSONqua restartnguyên/36hash/2histogramkhớp.55focusedcuối/1031fullbackend-Werror/71frontendtests đạt. [Chi tiết](../docs/progress.md).

**Checkpoint 09-C2 — đạt18/10/2026:** rà09.04UIfullconfig/thresholdbiên/noautorequest (bằngchứng03–04),09.05snapshot/buffer/histogram/rollback/restart,09.06run/revision/owner/missingstage. Full1031backend-Werror/71frontend đạt; HTTP9path10method/schema3, corekhôngđổi. Next09.07UIviewer; cổng09chưađạt.

### MVP09.07 — UI xem stage và histogram

- [x] **MVP09.07** — PipelineViewer hiện stage, histogram/Otsu và bảng mô tả ứng viên bên cạnh contour overlay.
- **Xong khi:** Hiện chu vi/số đỉnh/cạnh, đặc trưng vùng, hỗ trợ từng cạnh và thành phần score với nhãn/đơn vị đúng; Adaptive là ngưỡng cục bộ; biết trial được chọn.
- **Kiểm chứng:** Đối chiếu từng số với JSON/debug của phép chạy; thử stage/mô tả thiếu và đổi revision; không hiện placeholder như kết quả thật.
- **Cần trước:** MVP09.06, MVP09.04
- **Tệp dự kiến:** `frontend/src/components/PipelineViewer.tsx`, `frontend/src/components/HistogramView.tsx`, `frontend/src/pages/ScannerPage.tsx`.
- **Quy mô:** M (3 tệp dự kiến).

**Bằng chứng18/10 — 09.07:** PipelineViewer mở GET theo exact run, ảnh từ UUID envelope/kiểm dimensions; HistogramView256bin/counts/Otsuactualt hoặc Adaptive local; CandidateMetrics đủ trial/chu vi/nQ/cạnh/rad/a/e/f/b/S/đóng góp. Giữ detection diagnostic sau edit, render cũ có nhãn stale; abort/sequence guard chặn GET muộn. Thiếu stage/descriptor/histogram hoặc sai run không bịa dữ liệu. Chia lát API+types+parser/state, components, editor+style/tests; không tăng ID chính.11run/81artifact/6histogram,27 trạng thái UI và76frontendtests đạt. [Audit](../docs/audit-phase-09.md).

### MVP09.08 — Ghi lời giải thích từng bước

- [x] **MVP09.08** — Viết mô tả mục đích, tham số và giới hạn cho từng thuật toán ở UI/tài liệu.
- **Xong khi:** Giải thích được Gaussian/Canny/closing/contour/warp/threshold và sự khác nhau giữa phát hiện, biểu diễn, mô tả biên, đặc trưng vùng và lựa chọn.
- **Kiểm chứng:** Demo một ảnh, đối chiếu lời giải thích với config/ảnh/số mô tả; phân biệt MPP với Douglas–Peucker, không ép góc 90° khi có phối cảnh.
- **Cần trước:** MVP09.07
- **Tệp dự kiến:** `frontend/src/components/PipelineViewer.tsx`, `docs/algorithm-notes.md`.
- **Quy mô:** S (2 tệp dự kiến).

**Bằng chứng18/10 — 09.08:** Lời giải thích gắn stage/config thật và hướng dẫn phân biệt phát hiện/biểu diễn/mô tả/vùng/chọn. Đối chiếu lại3PDF/SHA, không gán DP=MPP/findContours=Moore, không ép90° khi phối cảnh. Ảnh tốt, trắng và img_004 đều xem được diagnostic/giới hạn. [Ghi chú thuật toán](../docs/algorithm-notes.md), [audit](../docs/audit-phase-09.md).

### AUX09.01 — Rà cả tám task giai đoạn 09

- [x] **AUX09.01** — User yêu cầu18/10/2026: hoàn thành09.07–08 rồi dò cả8task theo đặc tả và bằng chứng.
- **Xong khi:** Có ma trận8task, kiểm stage/số/config/run/revision; ghi nợ thuật toán và phạm vi còn chờ.
- **Kiểm chứng:**1031backend-Werror/76frontend/typecheck/build/browser;11run/81artifact/6histogram;11tài liệu/22trang/66hash nguồn cũ nguyên, core/CLI/requirements khớpM1.
- **Cần trước:** MVP09.08
- **Tệp thực tế:** `docs/audit-phase-09.md`, `docs/progress.md`; cập nhật hợp đồng/smoke/tiến độ.
- **Quy mô:** S (rà soát và bàn giao tài liệu, không đổi detector).
- **Bằng chứng:** [Audit8task](../docs/audit-phase-09.md), [progress](../docs/progress.md). Giữ nợimg_004/006/dataset1doc/test0, không suy testcount hoặc heuristic thành accuracy.

**Cổng09 — đạt18/10/2026:** Detect → kiểm tra/sửa/xác nhận → chọn mode → render thật; stage/histogram/descriptors cùng run truy vết trên UI. Checkpoint09-C1/C2 và8task/AUX09.01 đủ bằng chứng.71main+9AUX; nextMVP10.01. [Audit](../docs/audit-phase-09.md).

---

## Giai đoạn 10 — Quản lý bộ tài liệu nhiều trang

**Tuần dự kiến:** 3. **Số task:** 7. **Đầu ra cuối giai đoạn:** Tài liệu nhiều trang có tên, thêm/xóa/order và mở lại đúng toàn bộ dữ liệu đã lưu sau restart.

### MVP10.01 — Đặt tên bộ tài liệu

- [x] **MVP10.01** — Thêm metadata route/service và UI đổi tên; ghi bổ sung vào contract.
- **Xong khi:** Tên giữ sau refresh/restart; đổi tên không tăng revision ảnh.
- **Kiểm chứng:** Đổi tên qua UI và API; kiểm tra revision trước/sau.
- **Cần trước:** MVP09.08, MVP07.04
- **Tệp dự kiến:** `backend/app/api/sessions.py`, `backend/app/services/sessions.py`, `frontend/src/pages/ScannerPage.tsx`, `docs/api-contract.md`, `backend/tests/test_sessions_api.py`.
- **Quy mô:** M (5 tệp dự kiến).

**Bằng chứng18/10 — 10.01:** SessionRename/PATCH/service/repository atomic metadata-only, titletrim1..200/required/strict; no-op giữ timestamp,404/400/commit500rollback. Nativeform lưu/hủy/focus, header/list cập nhật không remount editor.29sessionAPItests đạt gồm11case rename mới; UI tên Việt/space/200ký tự/error/cancel và tên qua physicalrestart. Revision/config/render/source giữ. [Chi tiết](../docs/progress.md).

### MVP10.02 — Thêm trang vào tài liệu đang mở

- [x] **MVP10.02** — Hoàn thiện upload nhiều tệp, quota và selected_page ổn định.
- **Xong khi:** Thêm ảnh không làm mất config/kết quả trang cũ; một upload active, tối đa 20 trang.
- **Kiểm chứng:** Upload thêm vào tài liệu đã render; thử tệp lỗi và trang thứ 21.
- **Cần trước:** MVP10.01, MVP07.08
- **Tệp dự kiến:** `frontend/src/components/UploadPanel.tsx`, `frontend/src/pages/ScannerPage.tsx`, `backend/tests/test_import_api.py`.
- **Quy mô:** M (3 tệp dự kiến).

**Bằng chứng18/10 — 10.02:** Sequential batch lock qua GET đối soát, quota/error từng tệp, backend vẫn chặn413. Append giữ page_id/editor key/draft/render, GET sau batch không tăng detailReload. HTTPtest thêm vào trang Gray+CLAHE đã render, tệp lỗi/20trang/21st413 giữ dữ liệu/bytes cũ. Browser main4trang giữ draftGray/UUIDfull và selectedpage; lostreply201 được GET đối soát; quota19→20 bỏ tệp dư.81frontend/1043backend-Werror/typecheck/build/browser đạt. [Chi tiết](../docs/progress.md).

### MVP10.03 — API đổi thứ tự trang

- [x] **MVP10.03** — Nhận toàn bộ ID không trùng/thiếu/ngoài tài liệu; cập nhật position transaction.
- **Xong khi:** Thứ tự toàn vẹn, không tăng revision; request sai giữ order cũ.
- **Kiểm chứng:** Test ID thiếu/trùng/ngoài tài liệu và rollback lỗi.
- **Cần trước:** MVP10.02
- **Tệp dự kiến:** `backend/app/api/sessions.py`, `backend/app/services/sessions.py`, `backend/tests/test_page_order.py`.
- **Quy mô:** M (3 tệp dự kiến).

**Bằng chứng18/10 — 10.03:** PUT full permutation dưới writer lock, position tạm/final tránh UNIQUE; không đổi revision/config/run/source.8tests kiểm missing/duplicate/foreign/no-op/rollback và3request sai thật giữ snapshot.11path/14method/schema3. [Audit](../docs/audit-phase-10.md).

**Checkpoint 10-C1 — đạt18/10/2026:** 10.01–03 đủ bằng chứng rename/append/order, quota/no-op/rollback/không tăng revision ảnh; strict full suite1071 và browser đạt. [Audit](../docs/audit-phase-10.md).

### MVP10.04 — UI sắp xếp bằng lên xuống

- [x] **MVP10.04** — Nối PageList với thứ tự backend; giữ lựa chọn theo page_id.
- **Xong khi:** Lên/xuống và reload giữ order; đổi order không render lại.
- **Kiểm chứng:** Sắp ba trang có số in trên nội dung và refresh.
- **Cần trước:** MVP10.03
- **Tệp dự kiến:** `frontend/src/components/PageList.tsx`, `frontend/src/pages/ScannerPage.tsx`.
- **Quy mô:** S (2 tệp dự kiến).

**Bằng chứng18/10 — 10.04:** UI lên/xuống ba trang PAGE1/2/3 thành[2,1,3], giữ selectedID/draftGray180/fullUUID.500 trước request, mất reply sau commit và response trễ được GET đối soát, không retry/không chọn lại trang cũ. Order giữ qua restart. [Audit](../docs/audit-phase-10.md).

### MVP10.05 — Xóa trang và giữ lựa chọn hợp lệ

- [x] **MVP10.05** — Thêm DELETE page, bỏ tham chiếu DB rồi dọn tệp không dùng; UI chọn trang kế.
- **Xong khi:** Không xóa tệp trang khác; xóa trang đang render không publish kết quả vào trang đã mất.
- **Kiểm chứng:** Chạy xóa trang chọn/không chọn và xóa trong render; test storage references.
- **Cần trước:** MVP10.04, MVP08.02
- **Tệp dự kiến:** `backend/app/api/pages.py`, `backend/app/services/sessions.py`, `frontend/src/pages/ScannerPage.tsx`, `backend/tests/test_page_delete.py`.
- **Quy mô:** M (4 tệp dự kiến).

**Bằng chứng18/10 — 10.05:** Owner DELETE204/cascade/compact; sau commit kiểm reference/hash/path rồi unlink đúng UUID.7page-delete tests, render/detect race và3page APIdelete thật trênQA; UI mock xóa không chọn/chọn/cuối cho lựa chọn hợp lệ. Tệp trang khác nguyên; cleanup lỗi giữ orphan/log. [Audit](../docs/audit-phase-10.md).

### MVP10.06 — Xóa bộ tài liệu

- [x] **MVP10.06** — Thêm DELETE session và UI thao tác rõ với trạng thái đang xử lý.
- **Xong khi:** Không publish artifact vào tài liệu đã xóa; dữ liệu của tài liệu khác giữ nguyên.
- **Kiểm chứng:** Chạy xóa rỗng/nhiều trang/trong processing; kiểm tra lỗi và tệp.
- **Cần trước:** MVP10.05
- **Tệp dự kiến:** `backend/app/api/sessions.py`, `backend/app/services/sessions.py`, `frontend/src/pages/ScannerPage.tsx`, `backend/tests/test_session_delete.py`.
- **Quy mô:** M (4 tệp dự kiến).

**Bằng chứng18/10 — 10.06:** DELETE204 session rỗng/nhiều trang;4tests session và5processing races (cảpage/session) chặn publish sau xóa. Modal có hủy/Escape/xác nhận, UI mock chọn tài liệu còn lại. API thật xóa QA mới, không chạm14tài liệu cũ. [Audit](../docs/audit-phase-10.md).

**Checkpoint 10-C2 — đạt18/10/2026:** UI order và DELETE page/session, owner/reference/rollback/5processing races đạt; UI mock và API thật được phân biệt. [Audit](../docs/audit-phase-10.md).

### MVP10.07 — Mở lại tài liệu nhiều trang

- [x] **MVP10.07** — Hoàn thiện danh sách tài liệu, chọn mở, trạng thái trang và restart persistence.
- **Xong khi:** Tên/order/corners/mode/rotation/full render/debug lưu đúng; draft chưa lưu không giả là persisted.
- **Kiểm chứng:** Tắt/mở backend với ba trang khác mode/rotation và mở lại từ UI.
- **Cần trước:** MVP10.06
- **Tệp dự kiến:** `frontend/src/pages/ScannerPage.tsx`, `backend/tests/test_reopen.py`, `docs/progress.md`.
- **Quy mô:** M (3 tệp dự kiến).

**Bằng chứng18/10 — 10.07:** GET latest_render/latest_detection metadata-only; hook phục hồi full/debug/config không POST/không áp proposal.3trang Color0/Gray90/BWOtsu270 qua physicalrestart giữ3debugJSON/17hash, draftGray180 chưa lưu không phục hồi.14old docs50pages150sourcehash/alloldSQLrows nguyên;3full/preview byteequal corefresh.1071backend-Werror/87frontend/typecheck/build/23UIstates đạt. [Audit](../docs/audit-phase-10.md).

### AUX10.01 — Rà cả bảy task giai đoạn10

- [x] **AUX10.01** — User yêu cầu làm10.03–07 rồi rà lại cả giai đoạn.
- **Xong khi:** Ma trận7task, checkpoint/cổng, kiểm chứng và giới hạn được ghi đúng.
- **Kiểm chứng:**1071backend-Werror/87frontend/typecheck/build/23UIstates;3full-preview byteequal, physicalrestart3debugJSON/17hash;14old docs/50pages/150sourcehash và toàn bộ row cũ giữ nguyên.
- **Bằng chứng:** [Audit10](../docs/audit-phase-10.md), [progress](../docs/progress.md); evidence ignored mvp10-final-verified. Không thay110ID gốc.

**Cổng10 — đạt18/10/2026:** 7task/checkpoint10-C1/C2/AUX10.01 đủ bằng chứng; tên/thêm/xóa/order/mở lại full/debug sau restart đạt.78main+10AUX; nextMVP11.01 xuất ảnh/PDF. [Audit](../docs/audit-phase-10.md).

---

## Giai đoạn 11 — Xuất ảnh và PDF nhiều trang

**Tuần dự kiến:** 3. **Số task:** 8. **Đầu ra cuối giai đoạn:** M3: ứng dụng nhập/chỉnh/lưu nhiều trang và xuất ảnh/PDF đúng; khóa export rõ ràng, giải phóng đúng.

### MVP11.01 — Chốt request xuất tài liệu

- [x] **MVP11.01** — Định nghĩa format, page/revision/order snapshot, paper/orientation/margin và error danh sách thiếu render.
- **Xong khi:** Chọn được trang xuất; request trùng ID/ngoài tài liệu/options sai bị từ chối.
- **Kiểm chứng:** Kiểm tra schema và cập nhật ví dụ request/response trong contract.
- **Cần trước:** MVP10.07
- **Tệp dự kiến:** `backend/app/schemas/exports.py`, `docs/api-contract.md`, `backend/tests/test_export_schema.py`.
- **Quy mô:** M (3 tệp dự kiến).

**Bằng chứng18/10 — 11.01:** ExportRequest/ExportRead ởschemas/exports.py; alias sessions.ExportRequest giữ tương thích.19tests schema strict/frozen/subset-order/duplicate/quota/options/receipt đạt; membership/exactrevision ởservice11.02. Contract có ví dụrequest/error. [Snapshot](../docs/export-snapshot.md).

### MVP11.02 — Chụp snapshot và giữ artifact

- [x] **MVP11.02** — Kiểm tra confirmed/exact revision; giữ artifact; khóa mutation tài liệu trong export và mở khóa mọi đường thoát.
- **Xong khi:** Sửa/import/xóa/order khi export bị từ chối rõ; kết quả nguồn snapshot không bị dọn; restart không giữ khóa cũ.
- **Kiểm chứng:** Test snapshot thiếu render, hai export đồng thời, mutation và exception/cancel/429.
- **Cần trước:** MVP11.01, MVP07.06
- **Tệp dự kiến:** `backend/app/services/exports.py`, `backend/app/services/session_guards.py`, `backend/app/storage/repository.py`, `backend/tests/test_export_snapshot.py`.
- **Quy mô:** M (4 tệp dự kiến).

**Bằng chứng18/10 — 11.02:** ExportSnapshot/ExportPage frozen, exact confirmedrevision/fullrun/sourcebinding, aggregate missinglist và verifyPNG ngoàiDB. Lease theoappEngine/beforeenqueue,8mutationHTTP409/3CPUlatepublishblocked, queuedcancel/activecancel/429/exception/restart đạt.54tests mới/63focused/1125full-Werror; demo riêng3ảnh→subset[3,1]/26hashnguyên;14productdocs49pages147sourcehash/allSQLrowsnguyên saurestart. [Snapshot](../docs/export-snapshot.md).

### MVP11.03 — Xuất PNG và JPG

- [x] **MVP11.03** — Encode một trang từ full render, đổi gray/BGR đúng và tạo tên tải xuống hợp lệ.
- **Xong khi:** Download mở được đúng dimensions/màu; không dùng preview; BW PNG giữ cạnh chữ.
- **Kiểm chứng:** Mở PNG/JPG đã tải và so dimensions/pixels PNG với full render.
- **Cần trước:** MVP11.02
- **Tệp dự kiến:** `backend/app/export/images.py`, `backend/app/services/exports.py`, `backend/tests/test_image_export.py`.
- **Quy mô:** M (3 tệp dự kiến).

**Bằng chứng18/10 — 11.03:** EncodeImage PNG/JPG từfullBGR-grayuint8, PNG dùngcodecRGB/L cũ/pixel-exact/BW1pixel; JPEG95/0, filenamesASCIIbounded. Serviceverify/hash/decodefull dướilease, khôngpreview/filter/xoaylại.28tests image và6tệpQA mởlại đúng1199×1599/1599×1199;3PNGexactfull. HTTPdownload còn06. [Chi tiết](../docs/export-encoding.md).

**Checkpoint11-C1 — đạt18/10/2026:**11.01schema/request,11.02snapshot/lease/lifecycle và11.03fullimageencoder đủbằngchứng;1176full-Werror/83focused,6ảnhQA vàsnapshot regressions đạt. [Chi tiết](../docs/export-encoding.md).

### MVP11.04 — Bố trí một trang PDF

- [x] **MVP11.04** — Đổi mm→point, chọn portrait/landscape và fit ảnh vào margin A4.
- **Xong khi:** Giữ tỉ lệ, không stretch/crop; hướng theo render đã xoay; margin có miền hợp lệ.
- **Kiểm chứng:** Kiểm tra PDF một trang dọc/ngang bằng công cụ đọc/render PDF khi thực hiện.
- **Cần trước:** MVP11.03
- **Tệp dự kiến:** `backend/app/export/pdf.py`, `backend/tests/test_pdf_export.py`.
- **Quy mô:** S (2 tệp dự kiến).

**Bằng chứng18/10 — 11.04:** mm/25.4×72,A4auto theofullsauxoay/explicitoverride, fitcùngscale/căn giữa/lề0..30/khôngcrop.23testsPDF,4fileonepage đọcPypdf/renderPoppler96dpi/xemcontactsheet;MediaBox/matrix/fullimage đúng,16mẫugócmaxerror2.1176backend-Werror/83focused đạt; ghéplưu/PDFHTTP còn05–06. [Chi tiết](../docs/export-encoding.md).

### MVP11.05 — Ghép và lưu PDF nhiều trang

- [x] **MVP11.05** — Ghép từng full render theo snapshot, ghi PDF tạm rồi commit artifact/ExportRecord.
- **Xong khi:** Đủ trang đúng order; ghi snapshot vào DB; lỗi giữ dữ liệu trước đó và giải phóng khóa.
- **Kiểm chứng:** Xuất ba trang đánh số, kiểm tra PDF cùng ExportRecord và mô phỏng lỗi.
- **Cần trước:** MVP11.04
- **Tệp dự kiến:** `backend/app/export/pdf.py`, `backend/app/services/exports.py`, `backend/tests/test_pdf_export.py`.
- **Quy mô:** M (3 tệp dự kiến).

### MVP11.06 — API export qua executor

- [x] **MVP11.06** — POST exports dùng cùng quota CPU; trả artifact ID và đọc bằng artifact route.
- **Xong khi:** 429/error/success đều giải phóng slot/khóa; PDF chỉ xuất hiện sau ghi hoàn tất.
- **Kiểm chứng:** Chạy HTTP export success/busy/failure và kiểm tra GET artifact.
- **Cần trước:** MVP11.05
- **Tệp dự kiến:** `backend/app/api/exports.py`, `backend/app/main.py`, `backend/tests/test_export_api.py`.
- **Quy mô:** M (3 tệp dự kiến).

**Checkpoint11-C2 — đạt18/10/2026:**11.04A4/layout,11.05ghép/lưu/rollback và11.06API/executor đủ bằng chứng;1194backend-Werror, haiPDF/sáutrang đọc-render/orderedDBsnapshot đúng. [Chi tiết](../docs/export-workflow.md).

### MVP11.07 — UI chọn trang và tải kết quả

- [x] **MVP11.07** — Nối lựa chọn trang/options/download; xử lý PAGE_NOT_RENDERED bằng render trang đủ điều kiện rồi thử lại có giới hạn.
- **Xong khi:** Không tự xác nhận góc; không xuất config draft; tải PNG/JPG/PDF thật; lỗi không retry vô hạn.
- **Kiểm chứng:** Chạy selected subset, trang chưa confirmed, thiếu render và thay config trước export.
- **Cần trước:** MVP11.06
- **Tệp dự kiến:** `frontend/src/components/ExportPanel.tsx`, `frontend/src/pages/ScannerPage.tsx`, `frontend/src/api/client.ts`.
- **Quy mô:** M (3 tệp dự kiến).

**Bằng chứng18/10 — 11.05–07:** Ghép theo request order và commit Artifact/ExportRecord sau khi tệp hoàn tất; API201/429/busy/error và rollback/unlock đã kiểm. UI chọn subset/options, không xuất draft hoặc tự confirmed, thiếu render phục hồi đúng trang và thử lại một lần. Tải PNG/JPG/PDF thật;1194backend-Werror/95frontendtests/typecheck/build đạt. HaiPDF3trang order[1,2,3]/[3,1,2] đúngfull pixel/A4; PNGexactfull, JPGMAE0.0829946. Giữ14docs49pages147sourcehash/alloldSQLrows. [Chi tiết](../docs/export-workflow.md). Task08/cổng11/M3 chưa tích.

### MVP11.08 — Kiểm chứng tài liệu xuất cuối cùng

- [x] **MVP11.08** — Chạy ba trang khác mode/rotation/order, tải ảnh/PDF và thử mutation lúc export.
- **Xong khi:** Kết quả đúng nguồn full/revision/order; khóa được tháo cả khi thất bại; reopen vẫn được.
- **Kiểm chứng:** Render PDF để xem từng trang, thử sửa/xóa/import trong export, ghi evidence.
- **Cần trước:** MVP11.07
- **Tệp dự kiến:** `backend/tests/test_export_api.py`, `docs/progress.md`, `frontend/tests/scanner-smoke.md`.
- **Quy mô:** M (3 tệp dự kiến).

**Bằng chứng18/10 — 11.08:** QA3trang Color0/Gray90/BWOtsu270/r1; UIorder[3,1,2],tảiPNG/JPG vàhaiPDFautoPNG5/portraitJPEG30,đọcrenderxem6trang/đúngfull/order/A4matrix. ActualPOSTbarrierchặn8mutation+secondexport409; lỗi giữaPDFkhôngfile/recorddở vàxuấtlạithànhcông. Physicalrestartgiữdocument/4ExportRecord/30artifactSHA,UIreopen3fullchỉGET vàxuấtPDFmớiđược.1199backend-Werror/95frontendtests/typecheck/buildđạt;15docs52pages156sourcehash/alloldSQLrowsnguyên. [Audit8task](../docs/audit-phase-11.md).

**Cổng11 — đạt18/10/2026:** M3 nhập/chỉnh/lưu nhiều trang và xuấtảnh/PDF đúng nguồn/revision/order; khóa rõ/giải phóng saulỗi/restart, checkpoint11-C1/C2đạt. [Bằng chứng/ràngbuộc](../docs/audit-phase-11.md).

### Rà soát bổ sung giai đoạn11

- [x] **AUX11.01** — Rà đủ8task theo đặc tả, tests/API/UI/PDF/restart/bảo toàn dữ liệu; ghi ma trận và giới hạn.
- **Bằng chứng:** docs/audit-phase-11.md,1199backend-Werror/95frontendtests/typecheck/build,experiments/results/mvp11-final-verified/qa.json(ignored); khôngđổithuậttoán hoặcgiảaccuracy.86main+11AUX/110ID;nextMVP12.01.

---

### Bổ sung theo yêu cầu: tự nhận diện sau nhập ảnh

- [x] **AUX11.02** — Mỗi ảnh nhập mới tự nhận diện, giữ proposal chưa xác nhận để duyệt từng trang; lỗi riêng không chặn batch.
- **Xong khi:** Không cần bấm detect từng trang mới; không auto-confirm/PUT/render, không thay nháp cũ; detect lỗi vẫn giữ trang/quota và tiếp tục.
- **Bằng chứng:**102frontendtests/typecheck/build/36APIhồi quy;browserbatchpaper/broken/blank→haiDetectionRuns,revision0 vànhápGray cũgiữ;17old docs58pages174hashnguồnnguyên. [Hànhvi/kiểmchứng](../docs/auto-detect-on-import.md).86main+12AUX;nextMVP12.01khôngđổi. Sửa hồi quy callback tab cũ:103frontendtests/typecheck/build;browser một ảnh→một DetectionRun;18old docs59pages177hash nguồn nguyên. Không cộng thêm task.

## Giai đoạn 12 — Củng cố các ca lỗi và luồng tích hợp

**Tuần dự kiến:** 4. **Số task:** 7. **Đầu ra cuối giai đoạn:** Luồng chính, lỗi input/concurrency/storage và restart được kiểm chứng; lỗi còn lại được ghi bằng chứng.

### MVP12.01 — Kiểm tra nhập ảnh qua UI

- [ ] **MVP12.01** — Chạy EXIF/alpha/file giả/hỏng/quá byte/quá pixel và quota 20 trong ứng dụng hoàn chỉnh.
- **Xong khi:** Nguồn/overlay/output đúng; lỗi riêng từng ảnh; từ chối trang 21 không mất trang cũ.
- **Kiểm chứng:** Browser smoke kết hợp test API import; lưu pass/fail với ảnh fixture.
- **Cần trước:** MVP11.08
- **Tệp dự kiến:** `backend/tests/test_import_api.py`, `frontend/tests/scanner-smoke.md`, `docs/progress.md`.
- **Quy mô:** M (3 tệp dự kiến).

### MVP12.02 — Kiểm tra request trễ và draft

- [ ] **MVP12.02** — Tạo detect/render trả chậm, đổi trang/config và thử export với draft chưa lưu.
- **Xong khi:** UI chỉ nhận page/revision hiện hành; 409 không mất config mới; draft chưa confirmed không xuất.
- **Kiểm chứng:** Chạy ca timing có kiểm soát ở browser và API; ghi lỗi nếu tái hiện.
- **Cần trước:** MVP12.01
- **Tệp dự kiến:** `backend/tests/test_render_api.py`, `frontend/src/hooks/usePageRender.test.ts`, `frontend/tests/scanner-smoke.md`.
- **Quy mô:** M (3 tệp dự kiến).

### MVP12.03 — Kiểm tra giới hạn xử lý

- [ ] **MVP12.03** — Gửi normalize/detect/render/export vượt quota, hủy chờ và gây lỗi tác vụ.
- **Xong khi:** Một active/hai waiting; 429 đúng; không rò slot, health vẫn phản hồi.
- **Kiểm chứng:** Focused executor test và request HTTP đồng thời trong một process.
- **Cần trước:** MVP12.02
- **Tệp dự kiến:** `backend/tests/test_processing_executor.py`, `backend/tests/test_processing_integration.py`.
- **Quy mô:** S (2 tệp dự kiến).

**Checkpoint 12-C1:** Rà bằng chứng nghiệm thu MVP12.01 → MVP12.03; chạy kiểm chứng tập trung tương ứng, giữ mốc đã chạy được và ghi lỗi/chặn trước nhóm tiếp theo.

### MVP12.04 — Kiểm tra lưu bền khi thao tác thất bại

- [ ] **MVP12.04** — Mô phỏng encode/rename/DB commit lỗi ở import/render/export.
- **Xong khi:** DB không tham chiếu tệp thiếu; nguồn/config trước lỗi còn; khóa export được giải phóng.
- **Kiểm chứng:** Chạy fault-injection tests rồi mở lại tài liệu trên UI.
- **Cần trước:** MVP12.03
- **Tệp dự kiến:** `backend/tests/test_storage.py`, `backend/tests/test_render_service.py`, `backend/tests/test_export_snapshot.py`, `docs/progress.md`.
- **Quy mô:** M (4 tệp dự kiến).

### MVP12.05 — Khởi động lại và dọn tệp tạm

- [ ] **MVP12.05** — Thêm dọn tệp tmp quá hạn theo đường dẫn runtime xác định; kiểm tra restart sau tác vụ bị gián đoạn.
- **Xong khi:** Không xóa source/render được tham chiếu hoặc tệp active; không giữ khóa export sau restart.
- **Kiểm chứng:** Tạo tmp mới/cũ và artifact thật; restart; kiểm tra DB/tệp và reopen.
- **Cần trước:** MVP12.04
- **Tệp dự kiến:** `backend/app/storage/cleanup.py`, `backend/app/main.py`, `backend/tests/test_cleanup.py`.
- **Quy mô:** M (3 tệp dự kiến).

### MVP12.06 — Hoàn thiện trạng thái giao diện

- [ ] **MVP12.06** — Rà loading/empty/error, nhãn nút, focus và panel trên cửa sổ hẹp.
- **Xong khi:** Không màn trắng hoặc nút âm thầm thất bại; người dùng hiểu confirmed/dirty/busy và thao tác bằng bàn phím cơ bản.
- **Kiểm chứng:** Đi qua luồng chính bằng chuột/bàn phím, kiểm tra browser console.
- **Cần trước:** MVP12.05
- **Tệp dự kiến:** `frontend/src/pages/ScannerPage.tsx`, `frontend/src/components/FilterPanel.tsx`, `frontend/src/components/ExportPanel.tsx`, `frontend/src/styles.css`.
- **Quy mô:** M (4 tệp dự kiến).

**Checkpoint 12-C2:** Rà bằng chứng nghiệm thu MVP12.04 → MVP12.06; chạy kiểm chứng tập trung tương ứng, giữ mốc đã chạy được và ghi lỗi/chặn trước nhóm tiếp theo.

### MVP12.07 — Chạy hồi quy MVP

- [ ] **MVP12.07** — Chạy tập kiểm chứng geometry/import/revision/reopen/export và smoke UI; rà ID lỗi/data exposure.
- **Xong khi:** Không còn lỗi chặn luồng; 404 ổn định; đường dẫn data không truy cập public; thiếu tính năng được ghi rõ.
- **Kiểm chứng:** Chạy lệnh test/build đã ghi README, browser smoke và kiểm tra route; sửa lỗi đúng lớp.
- **Cần trước:** MVP12.06
- **Tệp dự kiến:** `docs/progress.md`, `docs/verification-matrix.md`, `frontend/tests/scanner-smoke.md`.
- **Quy mô:** M (3 tệp dự kiến).

**Cổng 12:** Luồng chính, lỗi input/concurrency/storage và restart được kiểm chứng; lỗi còn lại được ghi bằng chứng. Ghi bằng chứng thực hiện vào docs/progress.md; lỗi chặn phải được sửa trước task phụ thuộc.

---

## Giai đoạn 13 — Thực nghiệm và bằng chứng hiểu thuật toán

**Tuần dự kiến:** 4. **Số task:** 8. **Đầu ra cuối giai đoạn:** Có số liệu độc lập và so sánh thuật toán; test không tune; nêu được giới hạn giấy gấp/nhàu.

### MVP13.01 — Hoàn thành bộ ảnh thực nghiệm

- [x] **MVP13.01** — Chốt bộ13ảnh/2tài liệu theo quy mô người dùng chấp nhận26/10/2026, thay mục tiêu20/5; ghi điều kiện thực tế và thiếu phủ nhàu rõ/highlight/glare.
- **Bằng chứng26/10:** doc_ver2 có8tệp/7ảnh khác nhau, user xác nhận cùng tờ/nội dung; đăng kýimg007…013/doc_02/test, giữ6ảnh/doc_01/development. Normalize/hash/dimensions/split/file checks đạt; duplicate giữ ngoài manifest. [Giới hạn và số thực tế](../docs/dataset.md).
- **Xong khi:** Ghi số thực tế, condition và split theo document_id; ca khó không bị bỏ âm thầm.
- **Kiểm chứng:** Rà manifest/path và độc lập tài liệu giữa development/test.
- **Cần trước:** MVP02.08, MVP06.06
- **Tệp dự kiến:** `experiments/dataset_manifest.csv`, `docs/dataset.md`.
- **Quy mô:** S (2 tệp dự kiến).

### MVP13.02 — Gán nhãn và kiểm tra overlay

- [x] **MVP13.02** — Chuẩn hóa rồi gán bốn góc theo chu kỳ cho ảnh đủ góc, ghi lý do mẫu không gán được.
- **Bằng chứng26/10:**13record source-bound,10quad thủ công/3unlabelable có lý do,reviewed13/13 sau mở nguồn/overlay. Validator đạt,35focusedtests1.62s; không sửa implementation hoặc chạy detector trên test. Evidenceignoredmvp13-doc-ver2-20261026. [Quy tắc và lệnh](../docs/dataset.md).
- **Xong khi:** Nhãn đúng EXIF/source dimensions; overlay được kiểm tra trực quan toàn tập.
- **Kiểm chứng:** Mở overlay từng ảnh; sửa nhãn sai trước đánh giá; không chỉnh thuật toán bằng test.
- **Cần trước:** MVP13.01
- **Tệp dự kiến:** `experiments/annotations.json`, `experiments/validate_annotations.py`, `docs/dataset.md`.
- **Quy mô:** M (3 tệp dự kiến).

### MVP13.03 — Tạo metrics đánh giá góc

- **Bằng chứng26/10:**metrics.py dùng lại coreIoU, ghép8chu kỳ trên pixelnguồn,normalizedD; thiếuproposalIoU0/khôngbỏmẫuthấtbại,GTthiếubáoriêng.15metrics tests cùng18coreIoU đạt trongfull1244. [Công thức/mẫu số](../docs/results.md).

- [x] **MVP13.03** — Viết polygon IoU và corner error xét xoay vòng/đảo chu kỳ; định nghĩa mẫu số tỷ lệ.
- **Xong khi:** Polygon giống nhau IoU=1; lỗi góc không phạt vì khác điểm đầu; không đề xuất tính thất bại.
- **Kiểm chứng:** Chạy fixture giống/khác/hoán vị/không detection và kiểm tra aggregate.
- **Cần trước:** MVP13.02, MVP05.05
- **Tệp dự kiến:** `experiments/metrics.py`, `backend/tests/test_polygon_metrics.py`, `experiments/tests/test_metrics.py`.
- **Quy mô:** M (3 tệp dự kiến).

**Checkpoint 13-C1:** Rà bằng chứng nghiệm thu MVP13.01 → MVP13.03; chạy kiểm chứng tập trung tương ứng, giữ mốc đã chạy được và ghi lỗi/chặn trước nhóm tiếp theo. **Đạt26/10:**13ảnh/2tài liệu user chốt,nhãn13record vàmetrics/mẫu số đã kiểm;1244tests đạt. Không suy ra13-C2/cổng13 đã đạt.

### MVP13.04 — So sánh detector trên development

- **Bằng chứng26/10:**evaluate_detection.py/config4profile×6development=24runs/0error,CSV/metadata/stages/6comparison đã xem;test7ảnh không xử lý. Defaultparity với mã trước đổi đạt6/6nguồn. Fullbackend+experiments1244passed166.50s,source/labels giữ. [Bảng số đo/ca sai](../docs/results.md),evidenceignoredmvp13-03-04-verified/final.

- [x] **MVP13.04** — Batch baseline largest contour/scoring, có/không Gaussian và closing, giữ các biến khác cố định.
- **Xong khi:** CSV từng ảnh/status/IoU/error/time và thành phần score; metadata có mô tả ứng viên cho ca đúng/sai; ghi cấu hình từng lượt; chỉ tune bằng development.
- **Kiểm chứng:** Kiểm tra số dòng/split, mỗi so sánh chỉ đổi biến đã định; dùng overlay và mô tả để giải thích ca largest contour/scoring chọn khác nhau.
- **Cần trước:** MVP13.03, MVP05.08
- **Tệp dự kiến:** `experiments/evaluate_detection.py`, `experiments/configs/detection_trials.json`, `docs/results.md`.
- **Quy mô:** M (3 tệp dự kiến).

### MVP13.05 — So sánh Otsu và Adaptive

**Bằng chứng 26/10:** evaluate_enhancement.py chạy 3 cặp từ GT/cùng warp, cùng prepared_gray; 3 ảnh unlabelable giữ lý do, 0 lỗi, không mở 7 ảnh test. Đã xem 6 BW full/warp/crop và highlight tổng hợp riêng; thiếu highlight/sáng đều kiểm soát thực tế được ghi rõ, không bịa accuracy chữ. [Kết quả](../docs/results.md), evidence ignored mvp13-05-06-verified/enhancement.

- [x] **MVP13.05** — Dùng cùng góc đã xác nhận/ground truth và cùng warp, lưu cặp ảnh sáng đều/bóng/highlight.
- **Xong khi:** So sánh tách khỏi sai vùng cắt; nhận xét nét/dấu/nền/mất màu, không bịa accuracy chữ.
- **Kiểm chứng:** Mở ảnh full resolution, đối chiếu config và ghi nhận xét có ví dụ.
- **Cần trước:** MVP13.04, MVP04.07
- **Tệp dự kiến:** `experiments/evaluate_enhancement.py`, `docs/results.md`.
- **Quy mô:** S (2 tệp dự kiến).

### MVP13.06 — Khóa cấu hình trước test

**Bằng chứng 26/10:** frozen.json/mvp13-freeze-v1 khóa preset/score/detect-v1/scan-v1, 91 source hashes và dependency/môi trường thực tế; --check ở tiến trình mới đạt. User chọn chạy hồi quy cần thiết trước khóa: 1.255 tests/103 frontend/typecheck/build, browser nhập–confirm–render–PDF–reopen, 38 artifact hash sau restart giữ. [Môi trường/bản khóa](../docs/experiment-environment.md), [cổng hồi quy](../docs/verification-matrix.md).

- [x] **MVP13.06** — Chốt preset/score/algorithm_version và môi trường đã chạy; lưu mã nguồn định danh hoặc hash nếu chưa có commit.
- **Xong khi:** Có file config/version/dependency trước chạy test; kết quả sau dùng cùng cấu hình.
- **Kiểm chứng:** Đối chiếu hash/config và danh sách dependency thực tế với script.
- **Cần trước:** MVP13.05 và cổng hồi quy phục vụ khóa theo phạm vi MVP12.07 (người dùng chọn 26/10/2026); không yêu cầu nghiệm thu toàn bộ giai đoạn 12 ở lượt này. Các checkbox 12.01–12.07 giữ chưa hoàn thành.
- **Tệp dự kiến:** `experiments/configs/frozen.json`, `docs/experiment-environment.md`.
- **Quy mô:** S (2 tệp dự kiến).

**Checkpoint 13-C2 — đạt 26/10/2026:** Đủ 13.04–06: đối chứng detector development, Otsu/Adaptive cùng warp và bản khóa đã kiểm hash sau hồi quy được user chọn. Giữ 7 ảnh test chưa chạy; chưa đạt 13.07–08/cổng 13 hoặc nghiệm thu toàn bộ giai đoạn 12.

### MVP13.07 — Chạy test và benchmark đã khóa

**Bằng chứng 26/10:** benchmark.py v1.1 giữ 91 source files/frozen SHA, đánh giá 7 test/doc_02, mean IoU 0,995347/sai số góc 2,303 px. 168 samples gồm 140 đo/28 warmup, mỗi đường core/HTTP detect/render 35 mẫu/0 lỗi; native working set theo PID server thật. Lượt đầu đo launcher được đánh dấu không hợp lệ về RAM, giữ nguyên; lượt final dùng trọn bộ số đo, không tune/đổi nhãn. [Phương pháp](../docs/benchmark-method.md), [kết quả](../docs/results.md).

- [x] **MVP13.07** — Chạy tập test độc lập; đo core/HTTP detect/render, p50/p95 và RAM với phương pháp rõ.
- **Xong khi:** Không tune bằng test; báo số mẫu, resolution, CPU/RAM, số lượt và cache off.
- **Kiểm chứng:** Kiểm tra log/CSV, đo RAM bằng công cụ có trên máy; giữ kết quả tất cả ảnh.
- **Cần trước:** MVP13.06
- **Tệp dự kiến:** `experiments/evaluate_detection.py`, `experiments/benchmark.py`, `docs/results.md`.
- **Quy mô:** M (3 tệp dự kiến).

### MVP13.08 — Tổng hợp kết quả và ca thất bại

**Bằng chứng 26/10:** results.md tách development/test và mẫu số, giữ ca img_004 ăn bàn/001–002–006 unlabelable/Otsu đen bóng/thiếu phủ nhàu-lóa-highlight thật. Đã xem đủ 7 cặp overlay test; 70 PNG detector replay/hash/dims và 7 full HTTP/core bằng byte. 1.261 tests -Werror đạt 173,10s; [audit 8 task](../docs/audit-phase-13.md) và giới hạn homography đã ghi.

- [x] **MVP13.08** — Tổng hợp số liệu development/test và ví dụ bóng/nhàu/lóa/thiếu góc.
- **Xong khi:** Phân biệt mục tiêu/kết quả; nêu giới hạn homography cho trang không phẳng và chữ bị che/mất.
- **Kiểm chứng:** Rà bảng theo CSV và mẫu số; đối chiếu mỗi nhận xét với ảnh thực.
- **Cần trước:** MVP13.07
- **Tệp dự kiến:** `docs/results.md`, `docs/algorithm-notes.md`.
- **Quy mô:** S (2 tệp dự kiến).

**Cổng 13 — đạt 26/10/2026:** Đủ 8 task theo quy mô 13 ảnh/2 tài liệu user chốt; development/test theo tài liệu, bản khóa không đổi, có đối chứng/metrics/thời gian/RAM và ca thất bại công khai. Test đã quan sát, không dùng để tune; không suy rộng 7/7 ảnh cùng tài liệu thành accuracy tổng quát. [Audit](../docs/audit-phase-13.md), [kết quả](../docs/results.md), [progress](../docs/progress.md).

---

## Giai đoạn 14 — Đóng gói, báo cáo và demo

**Tuần dự kiến:** 4. **Số task:** 8. **Đầu ra cuối giai đoạn:** M4: bản chạy tái lập, báo cáo có số liệu thật và demo 5–7 phút; có checklist gói nộp.

### MVP14.01 — Build và phục vụ cùng origin

- [x] **MVP14.01** — Build React và FastAPI static/fallback, bind localhost.
- **Xong khi:** UI và /api/v1 cùng chạy; reload không hỏng API/artifact; data không public.
- **Kiểm chứng:** Chạy production build thật, mở browser và kiểm tra route fallback.
- **Cần trước:** MVP12.07
- **Tệp dự kiến:** `frontend/vite.config.ts`, `backend/app/main.py`, `backend/tests/test_static_routes.py`.
- **Quy mô:** M (3 tệp dự kiến).

**Bằng chứng 26/10:** StaticFiles/HTML fallback qua handler404, giữ API405/Allow/OpenAPI12paths; 17tests static/import/artifact/missingbuild/privatepaths đạt. Browser build thật cùng origin: nhập2ảnh tổng hợp/detect/confirm/Color-BW/render/PDF2trang/reload/fallback/restart;38artifact giữ hash. [Cấu hình](../docs/local-runtime.md), [nhật ký](../docs/progress.md).

### MVP14.02 — Khóa dependency và cấu hình chạy

- [x] **MVP14.02** — Lưu phiên bản frontend/backend đã đo, data directory và quota cấu hình.
- **Xong khi:** Cài lại từ file khóa được; không dựa vào dependency toàn máy; một Uvicorn process.
- **Kiểm chứng:** Tạo môi trường sạch, cài khóa và chạy imports/build/health.
- **Cần trước:** MVP14.01, MVP13.06
- **Tệp dự kiến:** `backend/requirements.txt`, `frontend/package-lock.json`, `backend/app/settings.py`.
- **Quy mô:** M (3 tệp dự kiến).

**Bằng chứng 26/10:** Venv mới khôngsystem-site-packages/pipinstall30pin/pipcheck/imports đạt; npmci sạch/103tests/typecheck/build41modules,3tệpbuild bằngbyte bản phục vụ. Full1.279tests-Werror233.16s từvenv sạch; health thật8001/restart2PID/cùngDB. 8000giữtoànbộSQL/87tệp user. Hai lockfile/frozen cũ nguyênhash; packaging-manifest/frozen-source ignored lưu riêng. [Cấu hình](../docs/local-runtime.md).

### MVP14.03 — Viết README cài và chạy

- [x] **MVP14.03** — Ghi lệnh thực tế, thư mục chạy, vị trí data, lưu bền, lỗi thường gặp và giới hạn localhost.
- **Xong khi:** Người khác có thể làm theo để mở app; không có lệnh giả định chưa chạy.
- **Kiểm chứng:** Làm theo README trong môi trường sạch và sửa bước thiếu.
- **Cần trước:** MVP14.02
- **Tệp dự kiến:** `README.md`.
- **Quy mô:** S (1 tệp dự kiến).

**Checkpoint 14-C1 — đạt26/10/2026:** Rà14.01–03, source/preset/lock giữ hash; bản sao sạch cài30pin/npmci/build41modules/imports/health thật8002 đạt;17static/APItests đạt4.51s, CLI1worker/Ctrl+C/restart giữ39artifact. Hồi quy1.279/103tests ở14.01–02 còn hợp lệ vì chỉ sửa docs/ảnh tổng hợp. M4 còn chờ14.08.

**Bằng chứng26/10:** [README](../README.md) bỏ mô tả cũ, có setup từroot/đườngdẫn/tham số host-worker/build/health/stop/reopen/data/quota/lỗi/localhost. Đã tự chạy từ source/venv/node_modules/DB mới ở8002, không dùng data user. Log`.tmp/phase14-readme-install.log`, [nhật ký](../docs/progress.md).

### MVP14.04 — Viết hướng dẫn sử dụng

- [x] **MVP14.04** — Hướng dẫn tạo tài liệu → nhập → góc → mode → lưu/mở lại → xuất.
- **Xong khi:** Có ảnh chụp thao tác thật và giải thích trạng thái dirty/confirmed/busy.
- **Kiểm chứng:** Nhờ người khác hoặc tự chạy theo hướng dẫn từ tài liệu mới.
- **Cần trước:** MVP14.03, MVP11.08
- **Tệp dự kiến:** `docs/user-guide.md`.
- **Quy mô:** S (1 tệp dự kiến).

- [x] **MVP14.04a** — Nội dung hướng dẫn và2ảnh nguồn tổng hợp tự thử (3tệp).
- [x] **MVP14.04b** — Walkthrough tài liệu mới và4ảnh chụp UI thật (4tệp). Hai task con không cộng lại task cha.

**Bằng chứng26/10:** [Hướng dẫn](../docs/user-guide.md) gồm dirty/confirmed/busy, nhập2ảnh→auto detect→sửa góc→lưu nháp chưaconfirmed→confirm→BWMedian/Otsu→PDF2trang/PNGđơn→tảiPDF thật→reload/Ctrl+C/restart.39artifact/metadata giữhash; PNGbằngfull;PDF2trang được render/xem, console0. Ảnh/sample tổng hợp trong docs/images/user-guide, không chứa ảnh cá nhân.

### MVP14.05 — Viết phần thuật toán báo cáo

- [x] **MVP14.05** — Trình bày công thức, thứ tự pipeline, tham số và phần OpenCV/phần tự viết.
- **Xong khi:** Giải thích được Canny/closing/contour/scoring/homography/CLAHE/Otsu/Adaptive với ảnh thật.
- **Kiểm chứng:** Đối chiếu báo cáo với implementation, config và debug stages.
- **Cần trước:** MVP09.08, MVP13.08
- **Tệp dự kiến:** `docs/report.md`.
- **Quy mô:** S (1 tệp dự kiến).

**Bằng chứng26/10:** [Báo cáo](../docs/report.md) mục1–7 đối chiếu3PDF/source/OpenCV: Canny/closing/contour-DouglasPeucker/mô tả-scoring/NMS/homography/CLAHE/Otsu/Adaptive, tham số/đơn vị/thứ tự và phầnthưviện/tựviết.2hình từ hình học/histogram thật, linklocalảnhdevelopment; khôngcopybodytrangriêng. Không gọiDouglasPeucker làMPP, điểmS làaccuracy hoặcwarp làdewarping.

### MVP14.06 — Viết phần thực nghiệm báo cáo

- [x] **MVP14.06** — Đưa dataset/split, metrics, bảng đo, so sánh và giới hạn vào báo cáo.
- **Xong khi:** Bảng khớp CSV; mục tiêu chưa đạt được ghi rõ; không hứa phục hồi chữ mất hoặc làm phẳng nhàu nặng.
- **Kiểm chứng:** Rà từng số và ảnh tham chiếu, ghi môi trường và phương pháp đo.
- **Cần trước:** MVP14.05
- **Tệp dự kiến:** `docs/report.md`, `docs/results.md`.
- **Quy mô:** S (2 tệp dự kiến).

**Bằng chứng26/10:** [Báo cáo](../docs/report.md) mục8–14:13ảnh/2doc/10GT/3unlabelable, bảng24ablation/9enhancement/7test/168samples;4bảng vàhashledger sinh từCSV đã kiểm, p50/p95/RAM tính lại.2biểuđồ metrics/latency-RAM, giữimg004sai/targetdevelopment2/3<80%/thiếuphủdataset/OCR; test7/7chỉ1doc. Khôngretune/rebenchmarktest, snapshotce89a90… giữ; [kết quả](../docs/results.md) nối report.

**Checkpoint 14-C2 — đạt26/10/2026:** Rà14.04–06: walkthroughtài liệumới/restart/39artifact/PDF-PNG đạt;4hìnhUI+4hìnhreport đãxem, côngthức/đơnvị/thưviện-codetựviết/CSV/mẫusố/hash/nguồn lýthuyết/link đãkiểm. Tiếp14.07demo;14.08/M4 chưađạt,stage12 giữchưa nghiệmthu toàn bộ.

### MVP14.07 — Chuẩn bị và luyện demo

- [x] **MVP14.07** — Chuẩn bị ảnh tốt/khó/bóng/highlight/gấp và kịch bản 5–7 phút; luyện câu hỏi thuật toán.
- **Xong khi:** Demo được fallback, so threshold, stage và PDF 3 trang; giải thích lý do/giới hạn từng bước.
- **Kiểm chứng:** Chạy rehearsal đo thời gian; ghi câu hỏi còn chưa trả lời được và hoàn thiện.
- **Cần trước:** MVP14.04, MVP14.06
- **Tệp dự kiến:** `docs/demo-script.md`, `docs/defense-questions.md`.
- **Quy mô thực hiện:** Tách ba task con cho generator, mẫu và tài liệu/ảnh UI; không cộng lại parent.

- [x] **MVP14.07a** — Generator, manifest hash và README nguồn gốc mẫu (3tệp).
- [x] **MVP14.07b** — Năm PNG tổng hợp: sạch/bóng/khôngbiên/highlight/vệt nếp gấp (5tệp); không tính thêm dataset thật.
- [x] **MVP14.07c** — Kịch bản,34câuQ&A,3ảnh minh chứng UI/so ngưỡng/PDF (5tệp); rehearsal bấm giờ320,984s sau nhập.

**Bằng chứng26/10:** [Demo](../docs/demo-script.md) có fallback, rawCanny/closing/descriptors/histogram,
Otsu156/Adaptive cùngwarp-preparedgray, Color/BW/Gray vàPDF3trang. Console0;65artifact giữhash qua
restart298300→296284. Kịch bản5–7phút, rehearsal thao tác5phút21giây, chưa tập nói thành tiếng.
Mẫu gấp chỉ mô phỏng ánh sáng, ca gấp thật development chỉ tham chiếu cục bộ; không đưa ảnh riêng vào gói.

### MVP14.08 — Kiểm chứng gói nộp trên môi trường sạch

- [x] **MVP14.08** — Chạy cài/build/test/smoke theo hướng dẫn, đối chiếu checklist và tạo gói nộp không chứa data cá nhân.
- **Xong khi:** M4 tái lập được; có source/docs/kết quả cần thiết; biết task nào chưa đạt; không tự push/publish.
- **Kiểm chứng:** Lưu lệnh/kết quả clean run và kiểm tra nội dung gói nộp.
- **Cần trước:** MVP14.07
- **Tệp dự kiến:** `docs/progress.md`, `docs/submission-checklist.md`.
- **Quy mô thực hiện:** Hai task con về đóng gói và kiểm sạch; không cộng lại parent.

- [x] **MVP14.08a** — Script allowlistZIP, SUBMISSION.md vàignoreoutput (3tệp); manifestSHA từngtệp, khôngghiđèZIP.
- [x] **MVP14.08b** — Cleanrun/checklist/proofJSON vàsửa một dòng chú thích datasetUI đãcũ (4tệp);
  source/input gói cuối bằngbyte bản đãtest, chỉđồngbộ tài liệu sau kiểm.

**Bằng chứng26/10:** [Checklist](../docs/submission-checklist.md), [proof](../docs/submission-verification.json).
ZIP giải nén mới/venv/npmci/30pin/imports/health/build41module;1279tests144,66s và103frontend/typecheck
đạt. Lỗi62test banđầu do đườngdẫn262ký tự đãtáihiện, dùngbasetempngắn rồi chạy lại đầyđủ, giữlog.
PDF3trang ảnhnhúng bằngfull/A4contain/lề5mm đãrender/xem; restart giữmetadata/65file.
ZIP ởoutput/submission, khôngảnhcá nhân/DB/log/runtime/deps/dist/PDFgiáotrình; CSV/summary/hình cóđi kèm.

### AUX14.01 — Rà cả tám task giai đoạn14

- [x] **AUX14.01** — User yêu cầu làm14.07–08 rồi dò đủ8task: ma trận tiêu chí/bằng chứng,
  nguồn/lock/hash/CSV/UI/PDF/restart/riêngtư gói nộp; ghi rõ giới hạn.
- **Xong khi/kiểm chứng:** [Audit8task](../docs/audit-phase-14.md), manifestZIP vàbằngchứng kỹthuật khớp;
  khôngtựtíchstage12/optional hoặcghiđèfreeze13. Lõi ảnh và197tệpdata/SQL người dùng đầu-cuối giữ.

**Checkpoint14-C3 và cổng14 — đạt26/10/2026:**14.01–08/AUX14.01 đủ bằngchứng, **M4 kỹthuật đạt**:
bản source chạy tái lập, báo cáo sốliệuthật, demo5–7phút/rehearsal sau nhập vàchecklistZIP.
102main+13AUX/110IDgốc;7taskstage12 và5optional chưanghiệmthu,01.08giữbỏqua.
Thủtục hànhchính/bìa/thôngtinnhóm/tậpnói còn do người trìnhbày hoànthiện trước nộp; chưa gửi bài/publish.

---

## Phần tùy chọn — không chặn MVP

Chỉ làm sau M3, nếu còn thời gian cho thực nghiệm và báo cáo. Giữ kết quả version gốc; thay pipeline sau khóa phải đổi version và đánh giá lại phần liên quan.

### OPT-A.01 — Lõi làm đều sáng

- [ ] **OPT-A.01** — Ước lượng nền closing/blur và chia nền bằng float/epsilon cho gray/BW; giữ toggle off mặc định.
- **Xong khi:** Có ảnh nền ước lượng và output; không sửa nguồn, không áp dụng mode màu.
- **Kiểm chứng:** So bóng nhẹ/bóng cứng/ảnh minh họa trên development và lưu ca nền ước lượng sai.
- **Cần trước:** MVP11.08
- **Tệp dự kiến:** `backend/app/processing/illumination.py`, `backend/app/processing/enhancement.py`, `backend/tests/test_illumination.py`.
- **Quy mô:** M (3 tệp dự kiến).

### OPT-A.02 — Điều khiển giảm bóng trên UI

- [ ] **OPT-A.02** — Nối config/API/FilterPanel và stage nền của thuật toán làm đều sáng.
- **Xong khi:** Bật/tắt rõ cho gray/BW; revision/debug/config đúng; màu hiển thị inactive.
- **Kiểm chứng:** Chạy UI bật/tắt trên cùng quad, kiểm tra stage và output thật.
- **Cần trước:** OPT-A.01, MVP09.08
- **Tệp dự kiến:** `backend/app/processing/config.py`, `frontend/src/components/FilterPanel.tsx`, `frontend/src/components/PipelineViewer.tsx`, `docs/api-contract.md`.
- **Quy mô:** M (4 tệp dự kiến).

### OPT-A.03 — Đánh giá phần giảm bóng

- [ ] **OPT-A.03** — So Adaptive với làm đều sáng+Adaptive cùng góc; ghi version mới nếu đổi pipeline đã khóa.
- **Xong khi:** Có bằng chứng lợi/hại; kết quả main frozen giữ riêng; bản nộp dùng version nào ghi rõ.
- **Kiểm chứng:** Chọn tham số bằng development, khóa version mới rồi chạy lại test/benchmark liên quan.
- **Cần trước:** OPT-A.02, MVP13.08
- **Tệp dự kiến:** `experiments/evaluate_enhancement.py`, `experiments/configs/frozen-illumination.json`, `docs/results.md`, `docs/report.md`.
- **Quy mô:** M (4 tệp dự kiến).

### OPT-B.01 — Tự viết histogram minh họa

- [ ] **OPT-B.01** — Viết histogram 256 trên ảnh nhỏ bằng vòng lặp/NumPy để giải thích.
- **Xong khi:** Tổng bin đúng số pixel, khớp histogram thư viện; không thay lõi đã đo.
- **Kiểm chứng:** So ảnh hằng/gradient/ảnh thật nhỏ và ghi ví dụ trong ghi chú.
- **Cần trước:** MVP06.04, MVP11.08
- **Tệp dự kiến:** `experiments/educational/histogram.py`, `experiments/tests/test_educational.py`, `docs/algorithm-notes.md`.
- **Quy mô:** M (3 tệp dự kiến).

### OPT-B.02 — Tự viết Otsu minh họa

- [ ] **OPT-B.02** — Từ histogram tính trọng số/trung bình/phương sai giữa lớp, bỏ lớp rỗng và ghi tie-break.
- **Xong khi:** Ngưỡng/output đối chiếu OpenCV; khác tie-break được giải thích; báo cáo ghi phần tự viết.
- **Kiểm chứng:** So ảnh hằng/hai mức/ảnh nhỏ và giải thích công thức trong demo.
- **Cần trước:** OPT-B.01
- **Tệp dự kiến:** `experiments/educational/otsu.py`, `experiments/tests/test_educational.py`, `docs/algorithm-notes.md`, `docs/report.md`.
- **Quy mô:** M (4 tệp dự kiến).

## Nhật ký và bàn giao

Mỗi mục progress ghi: ngày; task hoàn thành/chặn; tệp thực sửa; lệnh và kết quả kiểm chứng; ảnh/config/CSV minh chứng; khác biệt với kế hoạch; task tiếp theo. Không tích checkpoint bằng một câu 'chạy ổn' nếu chưa có evidence.

