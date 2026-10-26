# KẾ HOẠCH TRIỂN KHAI CHI TIẾT — DOCUMENT SCANNER

**Phiên bản:** 1.0 — 07/10/2026  
**Cơ sở:** Đặc tả kiến trúc và thuật toán đã được duyệt trong cuộc trao đổi.  
**Stack:** React + TypeScript + FastAPI + OpenCV + SQLite.  
**Trạng thái:** Kế hoạch chưa triển khai; tất cả checkbox ban đầu chưa hoàn thành.  
**Quy mô:** 331 tác vụ trong lộ trình chính và 25 tác vụ tùy chọn.

> Kế hoạch này tổ chức thứ tự thực hiện, không thay thế hoặc chỉnh sửa bản đặc tả đã duyệt. Chi tiết triển khai có thể thay đổi khi có bằng chứng; ghi lý do và ảnh hưởng, rồi cập nhật đặc tả khi chốt sản phẩm.

## 1. Cách sử dụng

Mỗi checkbox gồm **một hành động cụ thể** và **“Xong khi”**: dấu hiệu kiểm chứng được. Một tác vụ thường đủ nhỏ để thực hiện trong một phiên làm việc ngắn; 10–45 phút là mức chia việc mong muốn, không phải thời gian cam kết. Cài môi trường, lỗi máy, thuật toán và thí nghiệm có thể cần lâu hơn. Nếu một task vẫn mất hơn khoảng một giờ và có nhiều đầu ra độc lập, tách thành a/b/c ngay khi thực hiện.

“Chia nhỏ đến mức tối thiểu” ở đây là tối thiểu còn có giá trị theo dõi: một hàm, một quy tắc, một endpoint, một tương tác hoặc một ca kiểm chứng. Không tách thành từng dòng code, cú nhấp chuột hay thao tác lưu file.

- Làm theo giai đoạn 01→21. Trong mỗi giai đoạn, đọc từ trên xuống, đặc biệt các bước tạo hàm trước bước sử dụng hàm.
- **Cần trước** là phụ thuộc đầu vào. Không đánh dấu task hoàn thành khi chỉ có mock hoặc placeholder.
- Chỉ tích checkbox sau khi đạt “Xong khi”. Với sửa thuật toán, lưu ảnh/config chứng minh; với luồng sản phẩm, chạy luồng thật.
- Một giai đoạn kết thúc bằng **Cổng hoàn thành**. Nếu chưa qua cổng, sửa phần đang chặn trước khi tiếp tục.
- Không thêm test cho từng dòng/việc tạo file. Tập trung kiểm thử các quy tắc dễ sai: EXIF, góc, phối cảnh, tọa độ, revision, lưu bền, PDF.
- Mỗi phiên làm việc chọn 3–5 task liên tiếp; commit khi có một thay đổi chạy được. Không cần một commit cho mọi checkbox.
- Các task cần kiến thức chưa có: học đúng phần cần dùng, áp dụng trên một ví dụ nhỏ rồi quay lại task.
- Tác vụ tùy chọn ở phần 4 không chặn MVP. Nếu giảng viên yêu cầu tự cài thuật toán, chuyển nhóm 4.E thành yêu cầu học thuật bắt buộc.
- Trong thời gian làm UI, tiếp tục thu/gán nhãn dataset theo 03 và 20; không đợi ứng dụng hoàn chỉnh mới chuẩn bị dữ liệu.

**Quy ước ID:** P05.03 = giai đoạn 05, việc 03; O-A.01 = việc tùy chọn nhóm A. ID giữ ổn định để trao đổi, ghi lỗi và đánh dấu tiến độ.

### Định nghĩa một việc đã hoàn thành

1. Đầu ra đã tồn tại trong repository hoặc dữ liệu thí nghiệm đúng chỗ.
2. Kiểm chứng tương ứng đã chạy; có thể mô tả hoặc tái thực hiện.
3. Không làm hỏng mốc chạy được trước đó.
4. Ghi lại điểm chưa đạt nếu còn; không dùng checkbox để che lỗi.
5. Chỉ dùng số đo thực tế trong báo cáo; số ví dụ trong đặc tả không phải kết quả.

### Phân biệt dữ liệu trong repository và dữ liệu sử dụng

Fixtures nhỏ, tổng hợp, không chứa thông tin riêng có thể đưa vào Git. Ảnh người dùng, artifact runtime, DB cá nhân và bộ ảnh lớn nằm ngoài Git; giữ manifest và cách truy cập dữ liệu để tái lập. Khi bàn giao, kèm dataset cần cho đánh giá theo yêu cầu môn học.

## 2. Thứ tự và các mốc chạy được

| Mốc | Giai đoạn | Sản phẩm phải chạy được |
|---|---|---|
| M0 — Môi trường | 01–02 | Frontend gọi health backend |
| M1 — Lõi thuật toán | 03–08 | Một ảnh→detect/chọn tay→warp→ba chế độ→ảnh xuất, không cần web |
| M2 — Backend | 09–12 | HTTP tạo phiên/import/config/render, có revision |
| M3 — MVP ứng dụng | 13–17 | UI chỉnh góc, quét nhiều trang, xuất ảnh/PDF, mở lại phiên |
| M4 — Bản nộp | 18–21 | Minh họa thuật toán, kiểm thử, số liệu, build và báo cáo |
| Mở rộng | Phần 4 | Camera/đều sáng/deskew hoặc minh họa tự cài nếu cần |

Tất cả chức năng Must phải qua M3 và kiểm chứng lại ở 19. Giai đoạn 18 là phần Should nhưng rất hữu ích cho môn Xử lý ảnh số; nên hoàn thành để bảo vệ cách làm. Thí nghiệm và báo cáo ở 20–21 vẫn cần thực hiện dù không làm tính năng tùy chọn.

### Phân bổ thời gian tham khảo

| Tuần | Tập trung | Cổng kiểm tra |
|---|---|---|
| 1 | 01–04: môi trường, fixtures, chuẩn hóa | M0; EXIF/alpha đúng |
| 2 | 05–08: góc, warp, chế độ, detect | M1 |
| 3 | 09–12: schema, DB, API, revision | M2 |
| 4 | 13–15: UI, canvas, render | Quét một trang qua UI |
| 5 | 16–17: nhiều trang, export | M3 |
| 6 | 18–19: minh họa và củng cố | Luồng quan trọng ổn định |
| 7 | 20: đo trên validation/test | Có kết quả thật |
| 8 | 21: build, báo cáo, demo | M4 |

Đây là phân bổ tương đối từ phạm vi sơ bộ, chưa biết số giờ rảnh và kinh nghiệm thực tế của bạn. Sau M1, dựa vào tốc độ làm và lỗi còn lại để cập nhật lịch. Ưu tiên bỏ phần 4 trước; nếu phải bỏ Should, ghi rõ. Không bỏ chỉnh góc, kiểm tra hình học hoặc kiểm chứng revision để dành thời gian trang trí UI.

Nếu có hai người, có thể chia **người A: lõi ảnh + dataset/thí nghiệm**, **người B: schema/storage/API/UI/export** sau khi cùng chốt hợp đồng tọa độ và config. Vẫn ghép và kiểm tra tại từng mốc; không đợi cuối kỳ mới tích hợp.

## 3. Danh sách tác vụ chi tiết

### Giai đoạn 01 — Chốt cách làm và khởi tạo dự án

**Mức:** Bắt buộc  
**Cần trước:** Không  
**Đầu ra:** Khung repository và danh sách phạm vi

- [ ] **P01.01** — Tạo thư mục gốc document-scanner. **Xong khi:** Có một thư mục duy nhất cho mã nguồn dự án.
- [ ] **P01.02** — Khởi tạo Git trong thư mục gốc. **Xong khi:** Có thể xem trạng thái thay đổi.
- [ ] **P01.03** — Tạo thư mục backend. **Xong khi:** Có nơi chứa Python.
- [ ] **P01.04** — Tạo thư mục frontend. **Xong khi:** Có nơi chứa React.
- [ ] **P01.05** — Tạo thư mục docs và experiments. **Xong khi:** Tài liệu và thí nghiệm tách khỏi ứng dụng.
- [ ] **P01.06** — Tạo .gitignore cho venv, node_modules, data runtime và tệp tạm. **Xong khi:** Git không theo dõi dependency hoặc ảnh người dùng.
- [ ] **P01.07** — Ghi mục tiêu một câu vào README: ảnh chụp → trang đã hiệu chỉnh → ảnh/PDF. **Xong khi:** Người đọc hiểu đầu vào và đầu ra.
- [ ] **P01.08** — Ghi stack React/TypeScript, FastAPI, OpenCV, SQLite vào README. **Xong khi:** Không còn lựa chọn nền tảng chưa rõ trong MVP.
- [ ] **P01.09** — Chép danh sách Must từ đặc tả vào docs/scope.md. **Xong khi:** Có danh sách tính năng bắt buộc để đối chiếu.
- [ ] **P01.10** — Ghi Should và Could vào hai nhóm riêng trong docs/scope.md. **Xong khi:** Tính năng tùy chọn không lẫn vào điều kiện hoàn thành MVP.
- [ ] **P01.11** — Ghi giới hạn localhost, JPEG/PNG, 20 trang, 15 MiB, 16 MP. **Xong khi:** Cả nhóm dùng cùng giới hạn.
- [ ] **P01.12** — Lưu bản đặc tả đã duyệt vào docs. **Xong khi:** Có bản thiết kế nền để đối chiếu về sau.
- [ ] **P01.13** — Tạo docs/changes.md với cột ngày, lý do, ảnh hưởng. **Xong khi:** Có chỗ ghi thay đổi đặc tả khi phát sinh.
- [ ] **P01.14** — Commit khung ban đầu. **Xong khi:** Có mốc khôi phục trước khi cài môi trường.

**Cổng hoàn thành:** Có thể chỉ đúng nơi chứa frontend, backend, dữ liệu thử và tài liệu.

---

### Giai đoạn 02 — Dựng môi trường chạy tối thiểu

**Mức:** Bắt buộc  
**Cần trước:** 01  
**Đầu ra:** Backend health, frontend trống và hướng dẫn chạy

- [ ] **P02.01** — Kiểm tra Python trên máy và chọn Python 3.11 hoặc 3.12. **Xong khi:** Ghi được phiên bản thực tế trong README.
- [ ] **P02.02** — Tạo virtual environment riêng cho backend. **Xong khi:** Python của dự án tách khỏi môi trường toàn máy.
- [ ] **P02.03** — Cài FastAPI, Uvicorn và python-multipart. **Xong khi:** Import ba dependency thành công.
- [ ] **P02.04** — Cài NumPy, Pillow và một gói opencv-python-headless. **Xong khi:** Import cv2, numpy, PIL thành công.
- [ ] **P02.05** — Cài SQLAlchemy, ReportLab và pytest. **Xong khi:** Đủ dependency cho các giai đoạn sau.
- [ ] **P02.06** — Lưu phiên bản dependency backend đã cài. **Xong khi:** Có requirements/lock có thể tái lập.
- [ ] **P02.07** — Tạo backend/app/main.py và FastAPI app. **Xong khi:** Uvicorn khởi động được.
- [ ] **P02.08** — Thêm GET /api/v1/health. **Xong khi:** Nhận 200 với JSON trạng thái.
- [ ] **P02.09** — Kiểm tra Node và trình quản lý gói. **Xong khi:** Ghi được phiên bản môi trường frontend.
- [ ] **P02.10** — Khởi tạo React + TypeScript bằng Vite trong frontend. **Xong khi:** Trang mẫu mở được.
- [ ] **P02.11** — Cấu hình proxy /api đến backend. **Xong khi:** Frontend fetch /api/v1/health không lỗi origin.
- [ ] **P02.12** — Tạo frontend/src/api/client.ts với base path /api/v1. **Xong khi:** Các request dùng chung một nơi cấu hình.
- [ ] **P02.13** — Ghi hai lệnh khởi động và thư mục chạy vào README. **Xong khi:** Tắt rồi mở lại cả hai ứng dụng theo hướng dẫn được.
- [ ] **P02.14** — Commit và đánh dấu mốc M0. **Xong khi:** Môi trường tối thiểu chạy được từ repository.

**Cổng hoàn thành:** Backend trả health; trình duyệt gọi được health qua frontend.

---

### Giai đoạn 03 — Chuẩn bị dữ liệu thử và quy tắc gán nhãn

**Mức:** Bắt buộc  
**Cần trước:** 02  
**Đầu ra:** Fixtures nhỏ, manifest dữ liệu và quy tắc chia tập

- [ ] **P03.01** — Tạo thư mục fixtures chứa dữ liệu nhỏ dùng trong kiểm thử. **Xong khi:** Dữ liệu thử có nơi riêng, không lẫn ảnh runtime.
- [ ] **P03.02** — Tạo một ảnh tổng hợp có bốn góc tô bốn màu khác nhau. **Xong khi:** Nhìn được ảnh có bị lật hoặc xoắn sau warp.
- [ ] **P03.03** — Tạo ảnh tổng hợp có hình chữ nhật nghiêng. **Xong khi:** Có mẫu kiểm tra góc đã biết.
- [ ] **P03.04** — Tạo ảnh tổng hợp gần hình thoi. **Xong khi:** Có mẫu kiểm tra góc không bị chọn trùng.
- [ ] **P03.05** — Chuẩn bị JPEG có EXIF xoay 90°. **Xong khi:** Biết chiều hiển thị đúng của ảnh này.
- [ ] **P03.06** — Chuẩn bị PNG có vùng trong suốt. **Xong khi:** Có thể kiểm tra ghép nền trắng.
- [ ] **P03.07** — Chuẩn bị một tệp không phải ảnh nhưng mang đuôi .jpg. **Xong khi:** Có mẫu kiểm tra decoder.
- [ ] **P03.08** — Chuẩn bị một ảnh bị hỏng dữ liệu. **Xong khi:** Có mẫu kiểm tra lỗi giải mã.
- [ ] **P03.09** — Chuẩn bị ảnh vượt giới hạn pixel nhưng có byte nén nhỏ. **Xong khi:** Có mẫu kiểm tra giới hạn sau giải mã.
- [ ] **P03.10** — Tạo manifest với image_id, document_id, condition, split và đường dẫn. **Xong khi:** Mỗi ảnh có ID ổn định.
- [ ] **P03.11** — Ghi quy tắc ảnh của cùng tài liệu vật lý phải cùng split. **Xong khi:** Không rò rỉ tài liệu giữa development, validation và test.
- [ ] **P03.12** — Chọn kế hoạch 16 tài liệu: 8 development, 4 validation, 4 test. **Xong khi:** Có thể thu khoảng 40/20/20 ảnh nếu mỗi tài liệu chụp 5 lần.
- [ ] **P03.13** — Thu nhóm ảnh development đầu tiên gồm nền đơn giản, nền khó và bóng. **Xong khi:** Đủ ảnh để bắt đầu thử mà chưa dùng test.
- [ ] **P03.14** — Ghi quy ước gán nhãn trên ảnh đã áp dụng EXIF. **Xong khi:** Tọa độ nhãn không bị lệch hướng nguồn.

**Cổng hoàn thành:** Có ảnh thử cho các lỗi hình học/định dạng trước khi viết thuật toán.

---

### Giai đoạn 04 — Viết chuẩn hóa ảnh độc lập API

**Mức:** Bắt buộc  
**Cần trước:** 03  
**Đầu ra:** processing/normalize.py và nguồn chuẩn hóa đúng

- [ ] **P04.01** — Tạo kiểu kết quả NormalizedImage gồm ndarray, width, height và metadata. **Xong khi:** Hàm chuẩn hóa có đầu ra rõ.
- [ ] **P04.02** — Tạo hàm kiểm tra số byte đầu vào. **Xong khi:** Quá 15 MiB bị từ chối.
- [ ] **P04.03** — Tạo hàm xác định định dạng bằng decoder. **Xong khi:** Tệp giả đuôi JPEG bị phát hiện.
- [ ] **P04.04** — Thêm kiểm tra chỉ JPEG/PNG. **Xong khi:** Định dạng ngoài phạm vi có lỗi riêng.
- [ ] **P04.05** — Thêm kiểm tra chỉ một frame. **Xong khi:** Không âm thầm lấy một frame từ ảnh nhiều frame.
- [ ] **P04.06** — Đọc kích thước header trước khi load toàn bộ. **Xong khi:** Có thể kiểm tra giới hạn pixel sớm.
- [ ] **P04.07** — Xử lý cảnh báo decompression bomb thành lỗi đầu vào. **Xong khi:** Ảnh quá lớn không chạy tiếp đến pipeline.
- [ ] **P04.08** — Kiểm tra chiều rộng/cao tối thiểu và pixel count. **Xong khi:** W/H dưới 2 hoặc trên 16 MP bị từ chối.
- [ ] **P04.09** — Áp dụng EXIF transpose đúng một lần. **Xong khi:** JPEG mẫu hiển thị đúng hướng.
- [ ] **P04.10** — Ghép alpha PNG lên nền trắng. **Xong khi:** Vùng trong suốt không trở thành đen.
- [ ] **P04.11** — Chuyển ảnh về RGB rồi BGR uint8. **Xong khi:** Dtype, số kênh và thứ tự màu đúng.
- [ ] **P04.12** — Tạo hàm tính SHA-256 của ảnh chuẩn hóa được lưu. **Xong khi:** Có định danh nội dung cho cache.
- [ ] **P04.13** — Tạo hàm thumbnail giữ tỉ lệ. **Xong khi:** Không bóp méo ảnh dọc/ngang.
- [ ] **P04.14** — Tạo hàm encode PNG chuẩn hóa không kèm EXIF cũ. **Xong khi:** Đọc lại không bị xoay lần nữa.
- [ ] **P04.15** — Viết script normalize_one.py cho một tệp. **Xong khi:** Chạy command line nhận được nguồn chuẩn hóa và thumbnail.
- [ ] **P04.16** — Chạy nhóm fixtures định dạng/EXIF/alpha. **Xong khi:** Các ca đúng và sai có kết quả mong đợi.

**Cổng hoàn thành:** JPEG EXIF và PNG alpha được chuẩn hóa đúng; nguồn gốc không bị ghi đè.

---

### Giai đoạn 05 — Viết kiểm tra góc và hiệu chỉnh phối cảnh

**Mức:** Bắt buộc  
**Cần trước:** 04  
**Đầu ra:** processing/geometry.py

- [ ] **P05.01** — Tạo kiểu Point và Quad với đúng bốn điểm. **Xong khi:** Không chấp nhận số điểm tùy ý.
- [ ] **P05.02** — Viết chuyển pixel sang tọa độ chuẩn hóa. **Xong khi:** Dùng W−1/H−1 theo đặc tả.
- [ ] **P05.03** — Viết chuyển chuẩn hóa sang pixel. **Xong khi:** Round-trip giữ sai số số thực rất nhỏ.
- [ ] **P05.04** — Kiểm tra số hữu hạn và miền [0,1]. **Xong khi:** NaN, Infinity và điểm ngoài ảnh bị từ chối.
- [ ] **P05.05** — Viết tính khoảng cách hai điểm. **Xong khi:** Có thể kiểm tra cạnh và điểm trùng.
- [ ] **P05.06** — Viết shoelace area có dấu. **Xong khi:** Xác định được diện tích và winding.
- [ ] **P05.07** — Viết kiểm tra hai đoạn thẳng tự cắt. **Xong khi:** Tứ giác bow-tie bị phát hiện.
- [ ] **P05.08** — Viết kiểm tra convexity từ tích có hướng. **Xong khi:** Tứ giác lõm bị từ chối.
- [ ] **P05.09** — Đặt tolerance theo độ phân giải cho điểm trùng/diện tích/cạnh. **Xong khi:** Không dùng epsilon tùy tiện chỉ đúng một kích thước ảnh.
- [ ] **P05.10** — Gộp các kiểm tra thành validate_quad. **Xong khi:** Trả được mã lỗi và lý do.
- [ ] **P05.11** — Viết sắp thứ tự góc tự phát hiện quanh tâm. **Xong khi:** Không chọn bốn đỉnh độc lập qua tổng/hiệu.
- [ ] **P05.12** — Viết chọn góc bắt đầu và chuẩn hóa winding. **Xong khi:** Danh sách góc ổn định, không trùng.
- [ ] **P05.13** — Viết ước lượng width/height từ cạnh đối. **Xong khi:** Có kích thước đích theo aspect_policy=estimated.
- [ ] **P05.14** — Thêm aspect_policy=a4 và giữ hướng dọc/ngang đã chọn. **Xong khi:** Chỉ ép A4 khi người dùng chọn.
- [ ] **P05.15** — Thêm giới hạn cạnh dài render và không upscale quá ước lượng. **Xong khi:** Kích thước đầu ra nằm trong quota.
- [ ] **P05.16** — Tạo bốn điểm đích và tính homography. **Xong khi:** H hữu hạn cho tứ giác hợp lệ.
- [ ] **P05.17** — Warp nguồn BGR bằng INTER_LINEAR. **Xong khi:** Có ảnh chữ nhật từ vùng nguồn.
- [ ] **P05.18** — Kiểm tra góc màu, hình thoi, winding, tự giao và suy biến. **Xong khi:** Không lật/xoắn; ca sai bị từ chối.

**Cổng hoàn thành:** Warp ảnh bốn góc màu đúng hướng; từ chối tứ giác tự cắt và suy biến.

---

### Giai đoạn 06 — Viết các chế độ cải thiện ảnh cơ bản

**Mức:** Bắt buộc  
**Cần trước:** 05  
**Đầu ra:** processing/enhancement.py

- [ ] **P06.01** — Tạo enum color, gray, bw. **Xong khi:** Không nhận mode không tồn tại.
- [ ] **P06.02** — Viết grayscale BGR→gray. **Xong khi:** Ảnh một kênh đúng kích thước.
- [ ] **P06.03** — Viết denoise=None trả bản phù hợp không sửa nguồn ngoài ý muốn. **Xong khi:** Nguồn vẫn dùng lại được cho mode khác.
- [ ] **P06.04** — Viết Median với kernel hợp lệ. **Xong khi:** Chọn 3/5; loại giá trị chẵn hoặc không hỗ trợ.
- [ ] **P06.05** — Viết Gaussian nhánh render với kernel 3. **Xong khi:** Tách khỏi Gaussian nhánh tìm biên.
- [ ] **P06.06** — Viết CLAHE cho ảnh xám. **Xong khi:** clipLimit và tile grid được kiểm tra.
- [ ] **P06.07** — Viết CLAHE màu chỉ trên L của Lab. **Xong khi:** Không cân bằng B/G/R độc lập.
- [ ] **P06.08** — Viết Otsu qua OpenCV. **Xong khi:** Nhận ảnh BW nền trắng/chữ đen.
- [ ] **P06.09** — Viết Adaptive Gaussian. **Xong khi:** Block lẻ và C đúng config.
- [ ] **P06.10** — Thêm kiểm tra block theo kích thước ảnh nhỏ. **Xong khi:** Ảnh nhỏ không gây exception không rõ.
- [ ] **P06.11** — Viết preset màu không lọc mặc định. **Xong khi:** Giữ được highlight và màu nguồn.
- [ ] **P06.12** — Viết preset xám CLAHE nhẹ. **Xong khi:** Có đầu ra xám rõ và cho tắt CLAHE.
- [ ] **P06.13** — Viết preset BW Median3 + Adaptive31/C10. **Xong khi:** Có cấu hình mặc định đầy đủ.
- [ ] **P06.14** — Viết dispatcher enhance_document. **Xong khi:** Chỉ chạy bộ lọc phù hợp mode.
- [ ] **P06.15** — Viết xoay 0/90/180/270° sau lọc. **Xong khi:** 90° đổi đúng chiều ảnh, không đổi source corners.
- [ ] **P06.16** — So sánh ba mode trên cùng vùng có chữ tiếng Việt và highlight. **Xong khi:** Ghi được trường hợp mất dấu/mất màu để điều chỉnh.

**Cổng hoàn thành:** Cùng ảnh warp tạo được màu, xám và BW có thể đọc.

---

### Giai đoạn 07 — Viết phát hiện tài liệu tự động

**Mức:** Bắt buộc  
**Cần trước:** 05; ảnh development của 03  
**Đầu ra:** processing/detection.py

- [ ] **P07.01** — Tạo DetectionResult với status, corners, heuristic_score, warnings và timings. **Xong khi:** Schema không gọi score là accuracy.
- [ ] **P07.02** — Viết thu nhỏ cạnh dài 1200 không upscale. **Xong khi:** Giữ tỉ lệ nguồn.
- [ ] **P07.03** — Viết chuyển góc phân tích về chuẩn hóa bằng kích thước sau làm tròn. **Xong khi:** Góc không lệch vì rounding hai chiều.
- [ ] **P07.04** — Tạo ảnh xám phân tích. **Xong khi:** Nhánh detection có dữ liệu riêng.
- [ ] **P07.05** — Áp dụng Gaussian5 cho ảnh phân tích. **Xong khi:** Không dùng ảnh này làm nguồn export.
- [ ] **P07.06** — Tạo một Canny trial với L2gradient=True. **Xong khi:** Sinh edge map đầu tiên.
- [ ] **P07.07** — Thêm ba cặp ngưỡng cấu hình theo đặc tả. **Xong khi:** Tối đa ba trial, không thử vô hạn.
- [ ] **P07.08** — Thêm closing kernel3 một lần. **Xong khi:** Nối khoảng hở nhỏ.
- [ ] **P07.09** — Tìm contour bằng RETR_LIST và CHAIN_APPROX_SIMPLE. **Xong khi:** Giữ được cả contour con phù hợp.
- [ ] **P07.10** — Lọc nhỏ và giữ tối đa 30 contour lớn mỗi trial. **Xong khi:** Chi phí được giới hạn.
- [ ] **P07.11** — Tính chu vi và thử ba epsilon ratio. **Xong khi:** Có danh sách đa giác ứng viên.
- [ ] **P07.12** — Giữ tứ giác lồi và đủ diện tích/cạnh. **Xong khi:** Không buộc góc gần 90°.
- [ ] **P07.13** — Chuẩn hóa thứ tự góc từng ứng viên bằng geometry. **Xong khi:** Dùng lại kiểm tra đã có.
- [ ] **P07.14** — Tính thành phần area_ratio của score. **Xong khi:** Giá trị thuộc [0,1].
- [ ] **P07.15** — Tính edge_support trên Canny trước closing. **Xong khi:** Lấy mẫu dọc cạnh và kiểm tra lân cận 2 px.
- [ ] **P07.16** — Tính contour-fit và border penalty. **Xong khi:** Có đủ bốn thành phần score.
- [ ] **P07.17** — Gộp score và loại trùng polygon IoU>0.95. **Xong khi:** Cùng vùng không lặp từ nhiều trial.
- [ ] **P07.18** — Chọn ứng viên theo ngưỡng 0.60/0.40. **Xong khi:** Phân biệt đề xuất, cảnh báo và fallback.
- [ ] **P07.19** — Trả manual_required với corners=null khi không đủ bằng chứng. **Xong khi:** Không dựng giả góc nhận diện thành công.
- [ ] **P07.20** — Chạy nhóm ảnh development thuận lợi và khó, lưu overlay. **Xong khi:** Có ảnh đúng/sai cụ thể; chưa tune theo test.

**Cổng hoàn thành:** Ảnh thuận lợi có đề xuất; ảnh khó trả manual_required và không tự xác nhận.

---

### Giai đoạn 08 — Ghép pipeline offline và mốc thuật toán

**Mức:** Bắt buộc  
**Cần trước:** 04–07  
**Đầu ra:** Script quét một ảnh không cần web

- [ ] **P08.01** — Tạo scan_one.py nhận đường dẫn ảnh và nơi xuất. **Xong khi:** Một lệnh chạy được pipeline.
- [ ] **P08.02** — Thêm tùy chọn nhận bốn góc thủ công bằng JSON. **Xong khi:** Không phải phụ thuộc detect để quét được.
- [ ] **P08.03** — Ghép normalize→detect. **Xong khi:** Góc trả trên đúng ảnh chuẩn hóa.
- [ ] **P08.04** — Ghép góc xác nhận→warp từ nguồn đầy đủ. **Xong khi:** Không warp từ ảnh Gaussian.
- [ ] **P08.05** — Ghép warp→mode→rotate. **Xong khi:** Kết quả theo config cố định.
- [ ] **P08.06** — Xuất ảnh render chuẩn. **Xong khi:** Có tệp đủ độ phân giải theo quota.
- [ ] **P08.07** — Tạo preview từ render chuẩn. **Xong khi:** Không lọc riêng preview.
- [ ] **P08.08** — Ghi JSON cấu hình và timing bên cạnh kết quả thử. **Xong khi:** Có thể tái chạy đúng case.
- [ ] **P08.09** — Thử lại cùng nguồn/config/version. **Xong khi:** Kết quả ổn định trong môi trường đã khóa.
- [ ] **P08.10** — Chạy toàn ảnh development hiện có, ghi nhóm thất bại. **Xong khi:** Có baseline trước khi làm UI.
- [ ] **P08.11** — Commit và ghi mốc M1. **Xong khi:** Lõi xử lý có điểm khôi phục đã kiểm chứng.

**Cổng hoàn thành:** M1: nhập→detect hoặc sửa tay→warp→ba mode→tệp ảnh chạy được.

---

### Giai đoạn 09 — Chốt schema API và quy tắc revision

**Mức:** Bắt buộc  
**Cần trước:** 08  
**Đầu ra:** Pydantic schemas và hợp đồng frontend/backend

- [ ] **P09.01** — Tạo schema SessionCreate và SessionResponse. **Xong khi:** ID/timestamp theo đặc tả.
- [ ] **P09.02** — Tạo PageResponse với source width/height và artifact IDs. **Xong khi:** UI không cần đường dẫn filesystem.
- [ ] **P09.03** — Tạo schema Quad và dùng validation số hữu hạn. **Xong khi:** API dùng tọa độ chuẩn hóa.
- [ ] **P09.04** — Tạo schema đầy đủ PageConfig và defaults. **Xong khi:** Cấu hình thiếu được bổ sung nhất quán.
- [ ] **P09.05** — Tạo ConfigUpdateRequest với expected_revision. **Xong khi:** Có kiểm soát cập nhật lỗi thời.
- [ ] **P09.06** — Tạo DetectionResponse và RenderResponse. **Xong khi:** Output lõi ánh xạ được sang API.
- [ ] **P09.07** — Tạo ExportRequest với page_id/revision theo thứ tự. **Xong khi:** Định nghĩa snapshot rõ.
- [ ] **P09.08** — Tạo error envelope dùng chung. **Xong khi:** API lỗi có code/message/details.
- [ ] **P09.09** — Ghi quy tắc revision khởi đầu và thời điểm tăng. **Xong khi:** Chốt revision=0 khi nhập; sửa config tăng; đổi tên/order không tăng.
- [ ] **P09.10** — Ghi quy tắc corners thay đổi làm mất xác nhận trước thao tác xác nhận mới. **Xong khi:** Không xuất vùng vừa sửa mà chưa xác nhận.
- [ ] **P09.11** — Chốt ví dụ JSON đủ cấu hình vào docs/api-contract.md. **Xong khi:** Frontend không đoán trường thiếu.
- [ ] **P09.12** — Đối chiếu schema với đặc tả đã duyệt. **Xong khi:** Khác biệt cần thiết được ghi changes.md, chưa tự mở rộng phạm vi.

**Cổng hoàn thành:** Các module dùng cùng config, tọa độ và mã lỗi.

---

### Giai đoạn 10 — Lưu trữ SQLite và artifact

**Mức:** Bắt buộc  
**Cần trước:** 09  
**Đầu ra:** Models, repository và ghi tệp an toàn

- [ ] **P10.01** — Tạo settings cho đường dẫn data và quota. **Xong khi:** Không hardcode rải rác.
- [ ] **P10.02** — Tạo SQLite engine, connection/session lifecycle. **Xong khi:** Đóng kết nối sau use case.
- [ ] **P10.03** — Bật foreign keys và cấu hình transaction phù hợp. **Xong khi:** Quan hệ được kiểm tra.
- [ ] **P10.04** — Tạo model ScanSession. **Xong khi:** Có UUID, title, timestamps.
- [ ] **P10.05** — Tạo model ScanPage. **Xong khi:** Có session, position, dimensions và source references.
- [ ] **P10.06** — Tạo model PageConfig. **Xong khi:** Một config hiện hành mỗi trang, có revision.
- [ ] **P10.07** — Tạo model Artifact. **Xong khi:** Có kind, mime, size, hash, path nội bộ.
- [ ] **P10.08** — Tạo model ExportRecord. **Xong khi:** Có snapshot theo page/revision/order.
- [ ] **P10.09** — Tạo cách khởi tạo schema DB và ghi schema_version. **Xong khi:** Khởi động lần đầu không cần sửa SQL tay.
- [ ] **P10.10** — Viết repository tạo/lấy phiên. **Xong khi:** Không viết SQL trong hàm ảnh.
- [ ] **P10.11** — Viết repository tạo/lấy trang/config. **Xong khi:** Lấy đúng quan hệ session.
- [ ] **P10.12** — Viết UUID-based path builder. **Xong khi:** Filename upload không điều khiển đường dẫn.
- [ ] **P10.13** — Viết ghi tệp tạm rồi đổi tên cùng filesystem. **Xong khi:** Artifact chỉ được publish sau encode thành công.
- [ ] **P10.14** — Viết lưu nguồn và normalized artifact cùng metadata. **Xong khi:** Truy vết được hai loại ảnh.
- [ ] **P10.15** — Viết xử lý DB commit lỗi sau khi đã ghi tệp. **Xong khi:** Không giữ tham chiếu hỏng; tệp không tham chiếu được dọn.
- [ ] **P10.16** — Viết quy tắc giữ artifact đang được export snapshot dùng. **Xong khi:** Không xóa tệp trong lúc xuất.
- [ ] **P10.17** — Kiểm tra đóng/mở lại DB và đọc nguồn/config. **Xong khi:** Dữ liệu bền qua restart.

**Cổng hoàn thành:** Nguồn/config mở lại được; DB không tham chiếu tệp chưa ghi xong.

---

### Giai đoạn 11 — API phiên và nhập ảnh

**Mức:** Bắt buộc  
**Cần trước:** 10  
**Đầu ra:** Luồng HTTP tạo phiên và thêm trang

- [ ] **P11.01** — Thêm POST /sessions. **Xong khi:** Tạo và trả phiên mới.
- [ ] **P11.02** — Thêm GET /sessions có phân trang. **Xong khi:** Danh sách ổn định và có giới hạn.
- [ ] **P11.03** — Thêm GET /sessions/{sid}. **Xong khi:** Trả trang theo position.
- [ ] **P11.04** — Viết kiểm tra session/page membership dùng chung. **Xong khi:** Page không thuộc phiên trả 404.
- [ ] **P11.05** — Thêm upload một file multipart. **Xong khi:** API nhận được byte ảnh.
- [ ] **P11.06** — Đếm byte upload theo khối. **Xong khi:** Vượt quota trả 413 ngay khi phát hiện.
- [ ] **P11.07** — Gọi normalize service từ import service. **Xong khi:** HTTP không chứa code EXIF/alpha.
- [ ] **P11.08** — Lưu nguồn, thumbnail, trang và config revision0. **Xong khi:** Response đủ để UI hiển thị.
- [ ] **P11.09** — Kiểm tra số trang hiện tại trước import commit. **Xong khi:** Trang thứ 21 bị từ chối, không để rác.
- [ ] **P11.10** — Thêm GET /artifacts/{aid}. **Xong khi:** Trả MIME đúng qua ID.
- [ ] **P11.11** — Thêm tên tải xuống an toàn cho artifact. **Xong khi:** Không lộ đường dẫn vật lý.
- [ ] **P11.12** — Ánh xạ lỗi chuẩn hóa sang HTTP 413/415/400 phù hợp. **Xong khi:** Decoder lỗi không thành traceback người dùng.
- [ ] **P11.13** — Thử JPEG EXIF và PNG alpha qua API. **Xong khi:** Khớp kết quả pipeline offline.
- [ ] **P11.14** — Thử file giả, hỏng và quá pixel qua API. **Xong khi:** Lỗi rõ, các trang cũ vẫn còn.

**Cổng hoàn thành:** API import đúng ảnh; lỗi một tệp không mất phiên.

---

### Giai đoạn 12 — API config, detect và render có giới hạn

**Mức:** Bắt buộc  
**Cần trước:** 11; lõi 08  
**Đầu ra:** Luồng backend xử lý trang hoàn chỉnh

- [ ] **P12.01** — Thêm PUT config với kiểm tra expected_revision trong transaction. **Xong khi:** Cập nhật lỗi thời trả 409.
- [ ] **P12.02** — Chuẩn hóa defaults và kiểm tra mode/kernel/block/corners. **Xong khi:** Trả effective_config đầy đủ.
- [ ] **P12.03** — Tăng revision đúng một lần mỗi cập nhật ảnh thành công. **Xong khi:** Đổi tên/order không tác động revision.
- [ ] **P12.04** — Thêm POST detect không sửa config đã xác nhận. **Xong khi:** Chỉ trả đề xuất.
- [ ] **P12.05** — Lưu và trả timing detect. **Xong khi:** Có thời gian từng bước.
- [ ] **P12.06** — Tạo executor xử lý ảnh một worker. **Xong khi:** Không chạy CPU trong event loop.
- [ ] **P12.07** — Tạo cơ chế nhận tối đa một active và hai waiting. **Xong khi:** Yêu cầu vượt mức trả 429.
- [ ] **P12.08** — Đưa detect/render và export sau này qua cùng giới hạn xử lý. **Xong khi:** Các endpoint không vượt quota bằng đường khác.
- [ ] **P12.09** — Thêm POST render kiểm tra xác nhận và revision. **Xong khi:** Góc chưa xác nhận không được render.
- [ ] **P12.10** — Chụp config snapshot rồi đóng transaction trước xử lý. **Xong khi:** Không khóa DB suốt thời gian lọc.
- [ ] **P12.11** — Render full và preview vào tệp tạm. **Xong khi:** Chưa publish response trước encode xong.
- [ ] **P12.12** — Kiểm tra lại revision trước commit artifact hiện hành. **Xong khi:** Kết quả cũ bị loại nếu config đã đổi.
- [ ] **P12.13** — Tạo cache key theo source hash/config/version. **Xong khi:** Không dùng riêng page_id làm cache.
- [ ] **P12.14** — Thêm dùng cache cùng revision hợp lệ. **Xong khi:** Response vẫn đúng dimensions/config.
- [ ] **P12.15** — Dọn tệp tạm khi xử lý thất bại hoặc lỗi thời. **Xong khi:** Nguồn/config vẫn còn.
- [ ] **P12.16** — Thử sửa config trong lúc render và gửi request vượt hàng chờ. **Xong khi:** 409/429 đúng, health vẫn phản hồi.
- [ ] **P12.17** — Commit và ghi mốc M2. **Xong khi:** Backend đầu-cuối được kiểm chứng trước khi nối UI.

**Cổng hoàn thành:** M2: HTTP upload→config→render chạy; response cũ không ghi đè mới.

---

### Giai đoạn 13 — Giao diện phiên, upload và xem nguồn

**Mức:** Bắt buộc  
**Cần trước:** 11; hợp đồng 09  
**Đầu ra:** ScannerPage có dữ liệu thật

- [ ] **P13.01** — Tạo TypeScript types từ hợp đồng API. **Xong khi:** UI và backend dùng cùng tên trường.
- [ ] **P13.02** — Tạo HTTP client parse lỗi envelope. **Xong khi:** Có code/message thay lỗi chung chung.
- [ ] **P13.03** — Tạo layout thumbnail/editor/filter. **Xong khi:** Chưa cần trang trí chi tiết.
- [ ] **P13.04** — Thêm hành động tạo phiên. **Xong khi:** Gọi API và giữ session_id.
- [ ] **P13.05** — Thêm danh sách phiên để mở phiên cũ. **Xong khi:** Không chỉ phụ thuộc session trong RAM.
- [ ] **P13.06** — Tạo file input chỉ nhận JPEG/PNG. **Xong khi:** Accept hỗ trợ UX, backend vẫn là kiểm tra cuối.
- [ ] **P13.07** — Hiển thị tên và kích thước tệp trước upload. **Xong khi:** Người dùng biết tệp đang nhập.
- [ ] **P13.08** — Upload lần lượt nhiều tệp. **Xong khi:** Tối đa một upload active.
- [ ] **P13.09** — Hiển thị trạng thái thành công/lỗi từng tệp. **Xong khi:** Một tệp lỗi không dừng các tệp còn lại.
- [ ] **P13.10** — Tạo PageList từ artifact thumbnail. **Xong khi:** Không tải toàn bộ nguồn của 20 trang.
- [ ] **P13.11** — Giữ selected_page_id ổn định. **Xong khi:** Chọn thumbnail mở đúng trang.
- [ ] **P13.12** — Tải ảnh normalized của trang đang chọn. **Xong khi:** Hiển thị đúng hướng EXIF.
- [ ] **P13.13** — Tạo trạng thái loading/empty/error. **Xong khi:** Không còn màn trắng khó hiểu.
- [ ] **P13.14** — Kiểm tra refresh và mở lại phiên. **Xong khi:** Metadata/ảnh xuất hiện lại.

**Cổng hoàn thành:** Tạo phiên, upload và chọn trang được trong trình duyệt.

---

### Giai đoạn 14 — Canvas chỉnh bốn góc

**Mức:** Bắt buộc  
**Cần trước:** 13; geometry 05  
**Đầu ra:** CornerEditor thao tác chính xác

- [ ] **P14.01** — Tạo CornerEditor nhận ảnh, corners và callback. **Xong khi:** Canvas không tự gọi thuật toán backend.
- [ ] **P14.02** — Đo kích thước CSS của vùng canvas. **Xong khi:** Có kích thước hiển thị thực.
- [ ] **P14.03** — Thiết lập backing store theo devicePixelRatio. **Xong khi:** Hình/handle sắc trên HiDPI.
- [ ] **P14.04** — Viết contain transform gồm scale và offsets. **Xong khi:** Giữ tỉ lệ, tính đúng letterbox.
- [ ] **P14.05** — Viết pixel nguồn→tọa độ canvas. **Xong khi:** Góc vẽ đúng trên ảnh.
- [ ] **P14.06** — Viết pointer CSS→pixel nguồn→chuẩn hóa. **Xong khi:** Không nhân devicePixelRatio lần nữa.
- [ ] **P14.07** — Vẽ ảnh nguồn. **Xong khi:** Không thêm overlay vào byte ảnh.
- [ ] **P14.08** — Vẽ polygon và mask ngoài vùng cắt. **Xong khi:** Nhìn rõ vùng đang chọn.
- [ ] **P14.09** — Vẽ bốn handle có ID ổn định. **Xong khi:** Không tự đổi đỉnh trong lúc kéo.
- [ ] **P14.10** — Viết hit test với vùng chạm đủ lớn. **Xong khi:** Chọn được góc bằng chuột/cảm ứng.
- [ ] **P14.11** — Xử lý pointerdown và pointer capture. **Xong khi:** Kéo ra ngoài handle vẫn theo.
- [ ] **P14.12** — Xử lý pointermove giới hạn điểm trong ảnh. **Xong khi:** Không cho corners ngoài [0,1].
- [ ] **P14.13** — Xử lý pointerup/cancel. **Xong khi:** Không bị kẹt trạng thái kéo.
- [ ] **P14.14** — Kiểm tra tứ giác dự kiến trong UI. **Xong khi:** Chặn hoặc báo tự giao/lõm/trùng.
- [ ] **P14.15** — Thêm nút dùng toàn ảnh. **Xong khi:** Tạo bốn góc [0,0]–[1,1], chưa tự xuất.
- [ ] **P14.16** — Thêm nút đặt lại vùng cắt. **Xong khi:** Khôi phục draft rõ ràng.
- [ ] **P14.17** — Thêm nút xác nhận gọi PUT config. **Xong khi:** Lưu corners, confirmed và revision mới.
- [ ] **P14.18** — Vô hiệu render/xuất khi draft corners chưa được lưu/xác nhận. **Xong khi:** Không dùng kết quả cũ như kết quả vùng mới.
- [ ] **P14.19** — Kiểm tra mapping round-trip trên HiDPI, portrait và landscape. **Xong khi:** Sai số hiển thị ≤1 CSS pixel cho điểm kiểm tra.
- [ ] **P14.20** — Kiểm tra resize cửa sổ và chọn trang khác. **Xong khi:** Overlay không lệch hoặc mang góc của trang cũ.

**Cổng hoàn thành:** Ảnh dọc/ngang/HiDPI kéo góc đúng; vùng sai không được xác nhận.

---

### Giai đoạn 15 — Nối tự nhận diện, chế độ và render vào UI

**Mức:** Bắt buộc  
**Cần trước:** 12;14  
**Đầu ra:** Luồng scan đầy đủ trong trình duyệt

- [ ] **P15.01** — Thêm nút tự nhận diện gọi detect. **Xong khi:** Có loading độc lập.
- [ ] **P15.02** — Đưa góc đề xuất vào draft editor. **Xong khi:** Không âm thầm lưu confirmed=true.
- [ ] **P15.03** — Hiển thị cảnh báo hoặc manual_required. **Xong khi:** Người dùng biết cần kéo tay.
- [ ] **P15.04** — Không đưa heuristic_score thành phần trăm accuracy. **Xong khi:** Nhãn đúng ý nghĩa heuristic.
- [ ] **P15.05** — Tạo ba lựa chọn màu/xám/BW. **Xong khi:** Cập nhật draft config.
- [ ] **P15.06** — Tạo lựa chọn None/Median/Gaussian phù hợp. **Xong khi:** Không gửi kernel không hợp lệ.
- [ ] **P15.07** — Tạo điều khiển CLAHE cho mode xám/màu. **Xong khi:** Tham số không áp dụng được ẩn/vô hiệu.
- [ ] **P15.08** — Tạo lựa chọn Otsu/Adaptive cho BW. **Xong khi:** UI chỉ hiện block/C khi Adaptive.
- [ ] **P15.09** — Tạo nút render với config update rồi expected_revision mới. **Xong khi:** Không render revision cũ.
- [ ] **P15.10** — Hiển thị preview từ response. **Xong khi:** Không dùng ảnh nguồn thay kết quả.
- [ ] **P15.11** — Thêm view trước/sau có nhãn. **Xong khi:** Người dùng biết từng ảnh là gì.
- [ ] **P15.12** — Thêm xoay 90° cập nhật config. **Xong khi:** Preview đổi hướng nhưng corners nguồn giữ nguyên.
- [ ] **P15.13** — Debounce thay tham số khoảng 300 ms nếu bật auto-preview. **Xong khi:** Không gửi mỗi sự kiện input.
- [ ] **P15.14** — Chỉ nhận render response đúng page_id/revision. **Xong khi:** Chuyển trang hoặc response trễ không ghi đè.
- [ ] **P15.15** — Tách draft config và persisted config trong state. **Xong khi:** Nút xuất biết còn thay đổi chưa lưu.
- [ ] **P15.16** — Giữ kết quả cũ khi lỗi nhưng đánh dấu không phải revision mới. **Xong khi:** Không gây hiểu nhầm kết quả hiện hành.
- [ ] **P15.17** — Kiểm tra ảnh nền khó→sửa tay→BW và ảnh highlight→màu. **Xong khi:** Hai luồng đều hoàn thành trong UI.

**Cổng hoàn thành:** Chọn góc→mode→render thấy đúng kết quả revision hiện hành.

---

### Giai đoạn 16 — Quản lý nhiều trang và vòng đời phiên

**Mức:** Bắt buộc  
**Cần trước:** 15  
**Đầu ra:** Thêm/xóa/order/rename/reopen

- [ ] **P16.01** — Thêm service đổi tên phiên và trang. **Xong khi:** Tên hiển thị được lưu.
- [ ] **P16.02** — Bổ sung PATCH metadata cho phiên/trang vào hợp đồng API. **Xong khi:** Truy vết phần FR-10 chưa có endpoint riêng trong sơ đồ sơ bộ.
- [ ] **P16.03** — Nối đổi tên UI đến endpoint metadata. **Xong khi:** Refresh giữ tên mới.
- [ ] **P16.04** — Thêm PUT page-order nhận toàn bộ ID không trùng. **Xong khi:** Từ chối ID thiếu/ngoài phiên.
- [ ] **P16.05** — Cập nhật position trong một transaction. **Xong khi:** Không có thứ tự nửa chừng.
- [ ] **P16.06** — Thêm nút lên/xuống trước khi làm drag-drop. **Xong khi:** Có reorder cơ bản dễ kiểm chứng.
- [ ] **P16.07** — Lưu thứ tự mới và cập nhật PageList. **Xong khi:** Reload giữ thứ tự.
- [ ] **P16.08** — Thêm DELETE page. **Xong khi:** Bỏ đúng trang và tham chiếu artifact.
- [ ] **P16.09** — Dọn tệp trang không được export snapshot tham chiếu. **Xong khi:** Không xóa nguồn trang khác hoặc artifact đang dùng.
- [ ] **P16.10** — Đổi selected_page khi xóa trang đang chọn. **Xong khi:** UI không giữ ID đã xóa.
- [ ] **P16.11** — Thêm DELETE session và thao tác UI rõ ràng. **Xong khi:** Xóa được cả phiên.
- [ ] **P16.12** — Kiểm tra xóa phiên trong lúc processing. **Xong khi:** Không publish artifact vào phiên đã xóa.
- [ ] **P16.13** — Kiểm tra đổi tên/order không tăng revision ảnh. **Xong khi:** Không render lại không cần thiết.
- [ ] **P16.14** — Kiểm tra restart backend và reopen phiên nhiều trang. **Xong khi:** Config, nguồn, kết quả và order còn đúng.

**Cổng hoàn thành:** Không mất dữ liệu khi đổi trang; thứ tự và revision đúng.

---

### Giai đoạn 17 — Xuất ảnh và PDF nhiều trang

**Mức:** Bắt buộc  
**Cần trước:** 16;render 12  
**Đầu ra:** Download ảnh/PDF theo snapshot

- [ ] **P17.01** — Tạo export schema kiểm tra format, paper, orientation và margin. **Xong khi:** Không nhận layout/encoding ngoài phạm vi.
- [ ] **P17.02** — Viết lấy snapshot page_id/revision/order trong transaction ngắn. **Xong khi:** Nội dung xuất có định danh ổn định.
- [ ] **P17.03** — Kiểm tra confirmed và render đúng revision của mọi trang. **Xong khi:** Thiếu render trả 409 với danh sách.
- [ ] **P17.04** — Giữ tham chiếu artifact của snapshot trước tạo PDF. **Xong khi:** Xóa/render mới không làm mất tệp đang xuất.
- [ ] **P17.05** — Viết xuất PNG từ full render. **Xong khi:** Không dùng preview.
- [ ] **P17.06** — Viết xuất JPG và chuyển xám/màu đúng khi encode. **Xong khi:** File tải xuống mở được.
- [ ] **P17.07** — Viết đổi mm→PDF point. **Xong khi:** A4 có kích thước đúng.
- [ ] **P17.08** — Viết chọn portrait/landscape khi orientation=auto. **Xong khi:** Theo trang render đã xoay.
- [ ] **P17.09** — Viết tính fit image vào vùng trừ margin. **Xong khi:** Giữ tỉ lệ, không stretch.
- [ ] **P17.10** — Viết đặt ảnh và tạo trang PDF. **Xong khi:** Một render tạo đúng một trang.
- [ ] **P17.11** — Ghép nhiều trang lần lượt theo snapshot. **Xong khi:** Không load tất cả ndarray cùng lúc.
- [ ] **P17.12** — Ghi PDF tạm rồi commit artifact/ExportRecord. **Xong khi:** PDF chỉ tải sau hoàn tất.
- [ ] **P17.13** — Thêm POST exports qua executor có giới hạn. **Xong khi:** Không bypass worker quota.
- [ ] **P17.14** — Thêm UI chọn trang và tùy chọn xuất cơ bản. **Xong khi:** Có thể xuất một hoặc nhiều trang theo thứ tự.
- [ ] **P17.15** — Thêm UI xử lý PAGE_NOT_RENDERED bằng render trang thiếu rồi thử lại. **Xong khi:** Không lặp vô hạn hoặc xuất bản cũ.
- [ ] **P17.16** — Thêm download với tên hợp lệ. **Xong khi:** Người dùng nhận JPG/PNG/PDF thật.
- [ ] **P17.17** — Kiểm tra PDF ba trang có số thứ tự đánh dấu trên nội dung. **Xong khi:** Đúng số/order/hướng, không thumbnail.
- [ ] **P17.18** — Kiểm tra sửa config hoặc xóa trang trong lúc export. **Xong khi:** Snapshot đã nhận giữ đúng nội dung hoặc thất bại rõ trước khi nhận snapshot.
- [ ] **P17.19** — Commit và ghi mốc M3. **Xong khi:** Các chức năng Must đã có luồng UI chạy.

**Cổng hoàn thành:** M3: sản phẩm MVP quét và xuất được nhiều trang.

---

### Giai đoạn 18 — Ảnh trung gian và phần giải thích môn học

**Mức:** Nên hoàn thành trước nộp  
**Cần trước:** 17;detection 07  
**Đầu ra:** PipelineViewer và histogram

- [ ] **P18.01** — Tạo danh mục debug stages và artifact kinds. **Xong khi:** Tên bước thống nhất backend/UI.
- [ ] **P18.02** — Thêm cờ debug vào detect/render. **Xong khi:** Mặc định không giữ mọi ảnh trung gian.
- [ ] **P18.03** — Thu ảnh gray, Gaussian, edges và closing của detection. **Xong khi:** Artifact từ phép chạy thật.
- [ ] **P18.04** — Ghi contour overlay cùng score và trial ID. **Xong khi:** Biết trial tạo ứng viên được chọn.
- [ ] **P18.05** — Thu ảnh warp và ảnh trước threshold. **Xong khi:** Phân biệt hình học với cải thiện.
- [ ] **P18.06** — Lưu effective_config/version/timing trong debug metadata. **Xong khi:** Có thể giải thích kết quả.
- [ ] **P18.07** — Thêm GET debug theo revision và detection run ID nếu cần. **Xong khi:** Không trộn debug cũ với config mới.
- [ ] **P18.08** — Thêm xử lý cache có render nhưng thiếu debug. **Xong khi:** Tính lại khi cần, không trả placeholder.
- [ ] **P18.09** — Tạo PipelineViewer với tên bước và thumbnail. **Xong khi:** Bấm xem ảnh trung gian thật.
- [ ] **P18.10** — Tính histogram 256 bin của ảnh xám trước threshold. **Xong khi:** Không tính từ ảnh BW rồi gọi là histogram trước threshold.
- [ ] **P18.11** — Hiển thị histogram và ngưỡng Otsu nếu mode sử dụng Otsu. **Xong khi:** Giá trị hiển thị khớp phép chạy.
- [ ] **P18.12** — Hiển thị Adaptive là ngưỡng cục bộ, không vẽ một ngưỡng toàn cục giả. **Xong khi:** Giải thích đúng phương pháp.
- [ ] **P18.13** — Thêm mô tả ngắn mục đích và tham số từng bước. **Xong khi:** Dùng được trong demo môn học.
- [ ] **P18.14** — Kiểm tra debug bị thiếu/thất bại có trạng thái rõ. **Xong khi:** Không giả ảnh trung gian thành công.

**Cổng hoàn thành:** Người xem truy vết được bước thật, cấu hình thật.

---

### Giai đoạn 19 — Củng cố lỗi, lưu bền và các ca tích hợp

**Mức:** Bắt buộc  
**Cần trước:** 17;18 nếu đã làm  
**Đầu ra:** Danh sách ca quan trọng đã kiểm chứng

- [ ] **P19.01** — Lập ma trận test từ đặc tả và nối mỗi ca với task đã làm. **Xong khi:** Không bỏ ca EXIF/alpha/góc/revision/PDF.
- [ ] **P19.02** — Chạy cả luồng với JPEG EXIF và PNG alpha. **Xong khi:** UI góc và output đúng nguồn chuẩn hóa.
- [ ] **P19.03** — Chạy file giả/hỏng/oversize/pixel-bomb qua UI. **Xong khi:** Lỗi rõ, phiên còn nguyên.
- [ ] **P19.04** — Chạy tứ giác trùng/lõm/bow-tie gần suy biến qua API. **Xong khi:** Không vượt validation frontend bằng request thủ công.
- [ ] **P19.05** — Chạy cập nhật config với expected_revision cũ. **Xong khi:** 409, không mất config mới.
- [ ] **P19.06** — Tạo hai render trả trễ/đổi trang giữa request. **Xong khi:** UI chỉ nhận kết quả đúng trang/revision.
- [ ] **P19.07** — Chạy vượt hàng chờ và kiểm tra health. **Xong khi:** 429 theo quota, event loop vẫn phản hồi.
- [ ] **P19.08** — Gây lỗi encode hoặc commit có kiểm soát. **Xong khi:** Không có artifact hiện hành trỏ tệp thiếu.
- [ ] **P19.09** — Thêm dọn tệp tmp quá hạn. **Xong khi:** Không xóa tệp active hoặc nguồn phiên còn tồn tại.
- [ ] **P19.10** — Thêm dọn orphan artifact theo metadata và retention. **Xong khi:** Không dọn artifact đang được export pin.
- [ ] **P19.11** — Khởi động lại khi còn tệp tạm. **Xong khi:** Phiên mở được, rác có thể dọn.
- [ ] **P19.12** — Chạy PDF với trang chưa render và config mới. **Xong khi:** Không xuất silently revision cũ.
- [ ] **P19.13** — Thử 20 trang và từ chối trang 21. **Xong khi:** Quota không mất trang cũ.
- [ ] **P19.14** — Kiểm tra phục vụ static không lộ thư mục data. **Xong khi:** Chỉ endpoint artifact truy cập tệp đúng.
- [ ] **P19.15** — Kiểm tra session/page/artifact ID sai. **Xong khi:** 404 ổn định, không lộ traceback/path.
- [ ] **P19.16** — Chạy các kiểm thử ý nghĩa tự động và luồng smoke UI. **Xong khi:** Lưu kết quả pass/fail, sửa lỗi còn ảnh hưởng MVP.

**Cổng hoàn thành:** Lỗi đầu vào/request/crash không làm hỏng phiên hoặc kết quả hiện hành.

---

### Giai đoạn 20 — Đánh giá thuật toán và khóa kết quả thí nghiệm

**Mức:** Bắt buộc cho báo cáo  
**Cần trước:** 08;19;dataset 03  
**Đầu ra:** Bảng số liệu, ảnh so sánh và giới hạn

- [ ] **P20.01** — Hoàn thành khoảng 80 ảnh theo manifest đã chia. **Xong khi:** Đủ nhóm development/validation/test, ghi số thực tế.
- [ ] **P20.02** — Chuẩn hóa toàn bộ ảnh trước gán nhãn. **Xong khi:** EXIF/coordinate convention thống nhất.
- [ ] **P20.03** — Gán bốn góc cho ảnh đủ góc. **Xong khi:** Nhãn đi theo chu kỳ và có document_id.
- [ ] **P20.04** — Đánh dấu ảnh thiếu góc/lóa/mờ và lý do. **Xong khi:** Không bỏ ca khó không ghi nhận.
- [ ] **P20.05** — Kiểm tra trực quan overlay ground truth trên một lượt dữ liệu. **Xong khi:** Phát hiện nhãn sai trước đo.
- [ ] **P20.06** — Viết polygon IoU theo một phương pháp nhất quán. **Xong khi:** IoU=1 cho hai polygon giống nhau.
- [ ] **P20.07** — Viết corner error xét xoay vòng/đảo thứ tự. **Xong khi:** Không phạt vì khác điểm bắt đầu.
- [ ] **P20.08** — Viết batch evaluation lưu một dòng mỗi ảnh. **Xong khi:** Có status/score/IoU/error/time.
- [ ] **P20.09** — Đo baseline largest contour trên development. **Xong khi:** Có phương pháp đối chứng.
- [ ] **P20.10** — Đo detector scoring trên development. **Xong khi:** Có kết quả ban đầu.
- [ ] **P20.11** — Tune ngưỡng/preset chỉ bằng development và validation. **Xong khi:** Ghi từng cấu hình thử.
- [ ] **P20.12** — Khóa config, dependency và algorithm_version trước test. **Xong khi:** Có file config và commit ID.
- [ ] **P20.13** — Chạy detector trên test đã tách. **Xong khi:** Mẫu không đề xuất tính thất bại tự nhận diện.
- [ ] **P20.14** — Tổng hợp toàn bộ và nhóm thuận lợi/khó. **Xong khi:** Nêu rõ mẫu số của mọi tỉ lệ.
- [ ] **P20.15** — So sánh Gaussian/closing/scoring theo A/B/C. **Xong khi:** Mỗi lượt chỉ thay biến thí nghiệm.
- [ ] **P20.16** — So sánh Otsu/Adaptive/CLAHE theo D/E trên cùng góc. **Xong khi:** Không trộn ảnh hưởng vùng cắt.
- [ ] **P20.17** — So sánh analysis800/1200/1600 theo G. **Xong khi:** Ghi quality và speed.
- [ ] **P20.18** — Đo p50/p95 detect/render và RAM trên máy thực tế. **Xong khi:** Ghi CPU/RAM/resolution/cache/số lượt.
- [ ] **P20.19** — Đánh giá chữ tiếng Việt, highlight và nền bằng ảnh so sánh. **Xong khi:** Không suy accuracy từ histogram.
- [ ] **P20.20** — Lưu một nhóm ảnh thất bại và phân tích nguyên nhân. **Xong khi:** Báo cáo có giới hạn thực tế.

**Cổng hoàn thành:** Có bằng chứng đo độc lập; test không được dùng để tune.

---

### Giai đoạn 21 — Đóng gói, báo cáo và chuẩn bị nộp

**Mức:** Bắt buộc  
**Cần trước:** 19–20;18 cho bản học thuật  
**Đầu ra:** Bản build, hướng dẫn, báo cáo và demo

- [ ] **P21.01** — Build frontend production. **Xong khi:** Không còn lỗi build/TypeScript.
- [ ] **P21.02** — Cấu hình FastAPI phục vụ build cùng origin. **Xong khi:** /api và frontend cùng chạy.
- [ ] **P21.03** — Kiểm tra route fallback không chặn /api hoặc artifact. **Xong khi:** Reload trang không hỏng API.
- [ ] **P21.04** — Tạo cấu hình mặc định localhost và data directory. **Xong khi:** Không cần sửa code để chạy máy khác.
- [ ] **P21.05** — Khóa dependency frontend/backend. **Xong khi:** Cài lại đúng môi trường đã đo.
- [ ] **P21.06** — Viết README cài đặt, khởi động, xử lý lỗi thường gặp. **Xong khi:** Người khác chạy theo được.
- [ ] **P21.07** — Viết hướng dẫn thao tác nhập→góc→mode→PDF. **Xong khi:** Không cần giải thích trực tiếp từng nút.
- [ ] **P21.08** — Ghi môi trường và giới hạn vào báo cáo. **Xong khi:** Không hứa OCR, trang cong hoặc khôi phục lóa.
- [ ] **P21.09** — Cập nhật sơ đồ/đặc tả chỉ theo thay đổi đã ghi changes.md. **Xong khi:** Tài liệu phản ánh sản phẩm thực.
- [ ] **P21.10** — Chuẩn bị các ảnh demo thuận lợi, khó, bóng và highlight. **Xong khi:** Không cần tìm ảnh trong lúc trình bày.
- [ ] **P21.11** — Viết kịch bản demo 5–7 phút. **Xong khi:** Có các bước và kết quả mong đợi.
- [ ] **P21.12** — Chạy lại trên môi trường cài mới hoặc thư mục clean. **Xong khi:** Không dựa vào dependency/tệp ngoài repository.
- [ ] **P21.13** — Kiểm tra checklist Must và các chỉ tiêu thực tế. **Xong khi:** Tính năng còn thiếu hoặc mục tiêu chưa đạt được ghi rõ.
- [ ] **P21.14** — Tag bản nộp và sao lưu source/tài liệu/kết quả cần thiết. **Xong khi:** Có mốc M4 tái lập, dữ liệu người dùng không lẫn vào gói.

**Cổng hoàn thành:** M4: clone/cài/chạy theo hướng dẫn; quét→xuất hoạt động.

---

## 4. Tác vụ tùy chọn — chỉ thêm khi phần chính ổn định

Nếu mở rộng sau khi đã khóa cấu hình thí nghiệm, đổi algorithm_version và chạy lại đánh giá liên quan. Không trộn kết quả của hai phiên bản rồi gọi là cùng một mô hình.

### 4.A. Camera trực tiếp

**Cần trước:** M3; kiểm thử quyền và secure context.

- [ ] **O-A.01** — Thêm nút mở camera bằng getUserMedia. **Xong khi:** Nhận stream nếu môi trường cho phép.
- [ ] **O-A.02** — Thêm preview video và lựa chọn camera nếu có. **Xong khi:** Ảnh xem trước không bị nhầm camera.
- [ ] **O-A.03** — Chụp một frame thành JPEG/PNG rồi dùng API import hiện có. **Xong khi:** Không tạo pipeline xử lý khác.
- [ ] **O-A.04** — Dừng camera khi đóng panel hoặc rời trang. **Xong khi:** Không giữ camera active ngoài ý muốn.
- [ ] **O-A.05** — Xử lý từ chối quyền, không có camera và môi trường không hỗ trợ. **Xong khi:** Luôn quay lại luồng nhập file được.

### 4.B. Làm đều sáng

**Cần trước:** M3; chỉ dùng development/validation để chọn tham số.

- [ ] **O-B.01** — Ước lượng nền bằng grayscale closing kernel lớn. **Xong khi:** Có ảnh nền ước lượng để quan sát.
- [ ] **O-B.02** — Chia ảnh cho nền bằng float và epsilon. **Xong khi:** Không tràn uint8 hoặc chia cho 0.
- [ ] **O-B.03** — Thêm toggle chỉ áp dụng xám/BW. **Xong khi:** Có thể tắt nếu làm hỏng chữ.
- [ ] **O-B.04** — So sánh Adaptive với đều sáng+Adaptive trên cùng góc. **Xong khi:** Có thí nghiệm F và ví dụ nền ước lượng sai.

### 4.C. Sharpening và cảnh báo mờ

**Cần trước:** M3; không làm thay đổi kết quả test đã khóa.

- [ ] **O-C.01** — Viết unsharp masking bằng float trên luminance. **Xong khi:** Không tạo viền màu do xử lý từng RGB.
- [ ] **O-C.02** — Thêm toggle/amount cho màu và xám. **Xong khi:** BW cuối không bị sharpening.
- [ ] **O-C.03** — Đo variance Laplacian tại độ phân giải cố định. **Xong khi:** Các ảnh được so trên cùng kích thước.
- [ ] **O-C.04** — Tune cảnh báo mờ bằng dữ liệu development/validation. **Xong khi:** Không dùng một ngưỡng chung chưa kiểm chứng.
- [ ] **O-C.05** — Thêm cảnh báo có thể mờ, cho người dùng tiếp tục. **Xong khi:** Không tự xóa/từ chối trang ít chữ.

### 4.D. Deskew góc nhỏ

**Cần trước:** M3; sau warp và trước threshold cuối.

- [ ] **O-D.01** — Tạo mask chữ tạm với chữ là trắng. **Xong khi:** Foreground dùng đúng quy ước.
- [ ] **O-D.02** — Ước lượng hướng bằng các dòng Hough dài và nhất quán. **Xong khi:** Không dùng đường bảng/ảnh tùy ý.
- [ ] **O-D.03** — Giới hạn góc và lấy trung vị có trọng số độ dài. **Xong khi:** Thiếu bằng chứng giữ góc 0.
- [ ] **O-D.04** — Xoay mở rộng canvas nền trắng rồi threshold lại khi BW. **Xong khi:** Không cắt mất chữ ở mép.
- [ ] **O-D.05** — Đánh giá trang nhiều cột/bảng/hình và cung cấp nút tắt. **Xong khi:** Không ép deskew khi ước lượng sai.

### 4.E. Tự cài một phần thuật toán để minh họa

**Cần trước:** M1; đối chiếu yêu cầu giảng viên.

- [ ] **O-E.01** — Tự viết histogram 256 bin trên ảnh nhỏ. **Xong khi:** So tổng số pixel với kích thước ảnh.
- [ ] **O-E.02** — Tự viết threshold thủ công. **Xong khi:** Kiểm tra đúng nhánh pixel bằng ngưỡng.
- [ ] **O-E.03** — Tự viết Otsu từ histogram và bỏ nhóm rỗng. **Xong khi:** Đối chiếu với OpenCV, ghi quy tắc tie-break.
- [ ] **O-E.04** — Tự viết một phép Median hoặc Gaussian convolution. **Xong khi:** So cùng dtype và border policy.
- [ ] **O-E.05** — Tự viết erosion/dilation nhị phân trên ma trận nhỏ. **Xong khi:** Kiểm chứng foreground trắng, không đảo phép.
- [ ] **O-E.06** — Ghi rõ phần tự viết/phần thư viện trong báo cáo. **Xong khi:** Ứng dụng vẫn dùng implementation đã kiểm chứng.

## 5. Các quyết định triển khai cần ghi rõ

Đây là cách làm cụ thể để thực thi đặc tả sơ bộ, không phải bổ sung chức năng mới:

| Điểm | Quy tắc khi thực hiện | Task liên quan |
|---|---|---|
| Config ban đầu | revision=0, confirmed=false; corners có thể null trước khi chọn | P09.09; P11.08 |
| Draft và config lưu | UI giữ hai trạng thái; sửa draft chưa phải sửa DB | P15.15 |
| Xác nhận góc | Detect chỉ đề xuất; kéo góc phải xác nhận lại | P14.17–P14.18; P15.02 |
| Thứ tự góc | Tự phát hiện có thể sắp thứ tự; handle tay giữ ID | P05.11–P05.12; P14.09 |
| Preview | Thu từ full render, không chạy lọc riêng | P08.07; P12.11 |
| HTTP xử lý | Một worker ảnh, hai request chờ; một tiến trình API | P12.06–P12.08 |
| Cạnh tranh | Kiểm tra revision trước tính và trước commit | P12.09–P12.12 |
| Đổi tên | FR-10 cần route metadata nhỏ; ghi bổ sung vào hợp đồng khi implement | P16.01–P16.03 |
| Debug detection | Nếu cần, định danh run để không lẫn trial/phiên chạy | P18.04–P18.07 |
| Export | Snapshot pin full-render artifacts trong lúc xuất | P17.02–P17.04 |
| Khởi tạo DB | Có schema_version; khi đổi schema cần migration/cách nâng cấp trước phát hành | P10.09 |
| Dataset | Chia theo document_id, chưa dùng test để tune | P03.11–P03.12; P20.11–P20.13 |

Các bổ sung trong hợp đồng như metadata route hoặc debug run ID cần được ghi changes.md lúc thực hiện; chúng phục vụ chức năng đã duyệt. Nếu thay đổi nền tảng, lưu trữ, thuật toán chính hoặc phạm vi tính năng, rà lại các task phụ thuộc trước khi triển khai.

## 6. Theo dõi tiến độ và xử lý khi bị chặn

### 6.1. Bảng mốc

| Mốc | Trạng thái ban đầu | Bằng chứng cần có |
|---|---|---|
| M0 | Chưa bắt đầu | health gọi được từ UI |
| M1 | Chưa bắt đầu | source/config/output và ảnh bốn góc màu |
| M2 | Chưa bắt đầu | request/response upload→render và ca revision |
| M3 | Chưa bắt đầu | scan nhiều trang, JPG/PNG/PDF thật |
| M4 | Chưa bắt đầu | clean install, bảng đo, báo cáo, demo |

### 6.2. Nhật ký một phiên làm việc

Dùng mẫu này trong docs/progress.md khi bắt đầu code:

~~~markdown
Ngày:
Mốc hiện tại:
Task dự định: Pxx.xx, Pxx.xx, Pxx.xx
Task đã hoàn thành:
Task còn chặn:
Bằng chứng: ảnh thử / lệnh chạy / request-response / test / commit
Lỗi phát hiện:
Quyết định hoặc thay đổi:
Task tiếp theo:
~~~

### 6.3. Một task bị chặn

1. Ghi input cụ thể: ảnh nào, config nào, request nào hoặc dependency nào.
2. Tạo ví dụ nhỏ nhất tái hiện; không sửa nhiều module cùng lúc.
3. Xác định chặn do môi trường, thuật toán, schema, storage hay UI.
4. Sửa tại đúng lớp rồi chạy lại ca lỗi và mốc đang bị ảnh hưởng.
5. Nếu cần thay đặc tả, ghi thay đổi và các task phụ thuộc; không tích Done khi mới có ý tưởng.
6. Có thể làm task độc lập khác trong lúc chờ, nhưng không bỏ qua phụ thuộc của task bị chặn.

## 7. Năm việc đầu tiên để bắt đầu ngay

1. **P01.01:** Tạo thư mục gốc document-scanner.
2. **P01.02:** Khởi tạo Git trong thư mục đó.
3. **P01.03:** Tạo thư mục backend.
4. **P01.04:** Tạo thư mục frontend.
5. **P01.05:** Tạo docs và experiments.

Sau đó làm P01.06→P02.14 để đạt M0. Phiên đầu chỉ cần khung dự án và môi trường chạy; chưa cần xây giao diện hoàn chỉnh.

## 8. Đối chiếu kế hoạch với yêu cầu chức năng

| Yêu cầu trong đặc tả | Giai đoạn thực hiện | Giai đoạn kiểm chứng |
|---|---|---|
| FR-01 Phiên | 10–11;13 | 19;21 |
| FR-02 Nhập ảnh | 04;11;13 | 19 |
| FR-03 Chuẩn hóa | 04 | 11;19 |
| FR-04 Tự phát hiện | 07;12;15 | 20 |
| FR-05 Góc thủ công | 05;14 | 19 |
| FR-06 Warp | 05;08;12 | 19;20 |
| FR-07 Mode | 06;15 | 19;20 |
| FR-08 Tham số | 06;09;15 | 19;20 |
| FR-09 Xoay | 06;15 | 17;19 |
| FR-10 Trang/đổi tên/order | 16 | 17;19 |
| FR-11 Xuất | 17 | 19;21 |
| FR-12 Minh họa | 18 | 21 |
| FR-13 Lưu/mở lại | 10;13;16 | 19;21 |
| FR-14 Lỗi | 04;09;12;15 | 19 |

**Tài liệu nền:** Document_Scanner_Dac_Ta_Kien_Truc_Thuat_Toan.md, phiên bản 1.0 đã duyệt. Khi hoàn thiện, dùng sản phẩm và bằng chứng thí nghiệm để cập nhật cả kế hoạch lẫn đặc tả.
