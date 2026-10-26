# ĐẶC TẢ KIẾN TRÚC VÀ THUẬT TOÁN — DOCUMENT SCANNER

**Đề tài:** Ứng dụng quét tài liệu từ ảnh chụp (Document Scanner / Cam Scanner)  
**Môn học:** Xử lý ảnh số  
**Phiên bản:** 1.0 — 07/10/2026  
**Phạm vi đề xuất:** Nhóm 1–2 sinh viên, 6–8 tuần  
**Kiến trúc chọn:** Web React + FastAPI + OpenCV, chạy cục bộ  
**Trạng thái:** Thiết kế đề xuất; chỉ tiêu chất lượng và tốc độ là mục tiêu cần đo, chưa phải kết quả thực nghiệm.

> Nền tảng web được chọn vì chưa có yêu cầu bắt buộc về nền tảng. Ứng dụng xử lý ảnh sau khi chụp, không yêu cầu nhận diện liên tục trên video. “Cam Scanner” mô tả loại ứng dụng, không có nghĩa sao chép toàn bộ sản phẩm CamScanner.

---

## Mục lục

1. Mục tiêu và phạm vi
2. Yêu cầu chức năng và phi chức năng
3. Lựa chọn công nghệ
4. Kiến trúc tổng thể
5. Mô hình dữ liệu và quản lý tệp
6. Luồng nghiệp vụ và trạng thái
7. Quy ước ảnh và tọa độ
8. Pipeline xử lý ảnh
9. Đặc tả thuật toán
10. Hợp đồng API
11. Thiết kế giao diện
12. Hiệu năng, lỗi và giới hạn
13. Kiểm thử và thực nghiệm
14. Cấu trúc mã nguồn
15. Kế hoạch triển khai
16. Tiêu chí nghiệm thu
17. Tài liệu tham khảo

---

## 1. Mục tiêu và phạm vi

### 1.1. Bài toán

Người dùng chụp một trang giấy hoặc tải ảnh có sẵn. Ảnh có thể chứa mặt bàn, bị nghiêng do góc chụp, có bóng đổ, tương phản thấp hoặc nhiễu nhẹ. Ứng dụng xác định vùng tài liệu, cho phép sửa bốn góc, biến đổi vùng đó thành ảnh chữ nhật, cải thiện độ đọc và xuất thành ảnh hoặc PDF nhiều trang.

**Đầu vào:** JPEG/PNG chứa một trang tài liệu gần phẳng.  
**Đầu ra:** Ảnh đã hiệu chỉnh và PDF dạng ảnh; chưa có lớp văn bản tìm kiếm.

### 1.2. Giá trị học thuật

Đồ án cần thể hiện:

- Biểu diễn ảnh màu, ảnh xám, nhị phân và histogram.
- Lọc Gaussian/Median và ảnh hưởng kernel đến chữ nhỏ.
- Phát hiện biên bằng gradient và Canny.
- Hình thái học để nối biên.
- Tìm contour và xấp xỉ đa giác.
- Biến đổi phối cảnh bằng homography.
- Cải thiện tương phản; phân ngưỡng toàn cục và cục bộ.
- Đánh giá định lượng kết hợp quan sát chất lượng tài liệu.

Các phép xử lý phải có tên, tham số, ảnh trung gian và giải thích. Một nút “tăng chất lượng” không đủ chứng minh nội dung môn học.

### 1.3. Phạm vi ưu tiên

| Mức | Nội dung |
|---|---|
| Must | Nhập ảnh; kiểm tra đầu vào; tự đề xuất góc; sửa góc; warp; ba chế độ màu/xám/đen trắng; xoay 90°; xuất ảnh; PDF nhiều trang |
| Must | Xem trước/sau; lưu tham số; không ghi đè nguồn; lỗi có thông báo |
| Should | Ảnh trung gian; histogram; lựa chọn Otsu/Adaptive; chỉnh lọc/tương phản; lưu phiên |
| Could | Camera trực tiếp; làm đều sáng; deskew góc nhỏ; preset; ZIP |
| Ngoài MVP | OCR; PDF tìm kiếm; chữ viết tay; tài khoản; cloud; cộng tác; deep learning; khôi phục chữ mất do lóa; trang sách cong |

Nếu chỉ còn 3–4 tuần: giữ nhập ảnh, sửa góc, warp, ba chế độ và PDF; bỏ camera trực tiếp, deskew và làm đều sáng nâng cao.

### 1.4. Giả định

- Mỗi ảnh xử lý một trang. Ảnh hai trang cần tách hoặc chọn từng vùng.
- Bốn góc nằm trong ảnh; không tự khôi phục nội dung ngoài khung hình.
- Tài liệu gần phẳng. Một homography không làm phẳng trang sách cong.
- Nguồn đủ độ phân giải để đọc chữ.
- Người dùng xác nhận vùng cắt trước khi xuất.
- MVP một người dùng trên máy cá nhân; không phải dịch vụ công cộng nhiều tài khoản.

---

## 2. Yêu cầu chức năng và phi chức năng

### 2.1. Chức năng

| ID | Chức năng | Hành vi |
|---|---|---|
| FR-01 | Tạo phiên | Một phiên có các trang theo thứ tự |
| FR-02 | Nhập ảnh | JPEG/PNG, tối đa 20 trang/phiên |
| FR-03 | Chuẩn hóa | EXIF, alpha, màu và kích thước |
| FR-04 | Phát hiện | Tứ giác đề xuất, heuristic score, cảnh báo |
| FR-05 | Chỉnh góc | Kéo bốn điểm; kiểm tra cả UI và backend |
| FR-06 | Warp | Biến vùng xác nhận thành trang chữ nhật |
| FR-07 | Chế độ | Màu, xám cải thiện, đen trắng |
| FR-08 | Tham số | Chọn lọc, tương phản, threshold |
| FR-09 | Xoay | 0/90/180/270°, không đổi tọa độ nguồn |
| FR-10 | Trang | Xóa, đổi tên, sắp xếp, thêm |
| FR-11 | Xuất | JPG/PNG hoặc PDF trang đã xác nhận |
| FR-12 | Học thuật | Xám, lọc, biên, contour, warp, kết quả |
| FR-13 | Lưu phiên | Mở lại, tái tạo từ nguồn và config |
| FR-14 | Lỗi | Một trang lỗi không làm mất các trang khác |

### 2.2. Phi chức năng

| ID | Yêu cầu | Mục tiêu thiết kế |
|---|---|---|
| NFR-01 | Triển khai | Một frontend, một backend; không bắt buộc Docker |
| NFR-02 | Phản hồi | Mục tiêu p95 detect ≤2 giây; render ≤3 giây/trang trên máy thử nghiệm |
| NFR-03 | Tài nguyên | ≤15 MiB/tệp nén; ≤16 triệu pixel giải mã; ≤20 trang/phiên |
| NFR-04 | Hình học | Không xoắn, lật hoặc ép tỉ lệ ngoài ý muốn |
| NFR-05 | Tái lập | Cùng nguồn/config/version cho cùng kết quả trong môi trường khóa |
| NFR-06 | Giải thích | Tham số, cảnh báo và thời gian từng bước |
| NFR-07 | Lưu bền | Tệp tạm→đổi tên; metadata dùng transaction |
| NFR-08 | Riêng tư | Không gửi ảnh sang dịch vụ OCR/AI bên ngoài |

Hiệu năng phải đo và báo cáo CPU, RAM, độ phân giải, số mẫu, cache. Không dùng một ảnh chạy nhanh để kết luận.

---

## 3. Lựa chọn công nghệ

| Thành phần | Công nghệ | Vai trò |
|---|---|---|
| Frontend | React + TypeScript + Vite | Nhập ảnh, quản lý trang, xem kết quả |
| Chỉnh góc | Canvas 2D + Pointer Events | Overlay, chuột/cảm ứng |
| Backend | Python 3.11/3.12 + FastAPI | API và điều phối |
| Xử lý ảnh | OpenCV 4.x headless + NumPy | Lọc, biên, contour, warp, threshold |
| Chuẩn hóa | Pillow | Metadata, EXIF transpose, chuyển mode |
| Metadata | SQLite + SQLAlchemy | Phiên, trang, revision, artifact |
| PDF | ReportLab | Bố trí ảnh trên từng trang |
| Upload | python-multipart | multipart/form-data |
| Kiểm thử | pytest | Hình học, API, revision, export |
| Thí nghiệm | Script/Jupyter + Matplotlib | Histogram, số liệu, so sánh |

Python/OpenCV giúp tập trung thuật toán môn học; React cung cấp giao diện thao tác thuận tiện. Backend giữ một implementation xử lý ảnh, không cần duy trì thêm OpenCV.js.

Kiến trúc là **ứng dụng đơn khối chia mô-đun**. Không cần microservices, Redis, message broker hay Kubernetes.

Chỉ cài một biến thể OpenCV Python để tránh tranh chấp namespace cv2. Chốt phiên bản đã chạy thành công và lưu lockfile; không bắt buộc theo bản mới nhất.

Nếu giảng viên yêu cầu desktop: thay UI/API bằng PySide6; giữ lại lõi xử lý ảnh độc lập HTTP.

---

## 4. Kiến trúc tổng thể

### 4.1. Thành phần

~~~mermaid
flowchart TB
    UI["React: nhập, sửa góc, xem"]
    API["FastAPI: kiểm tra và điều phối"]
    CORE["Lõi xử lý ảnh"]
    EXPORT["Xuất ảnh và PDF"]
    META["SQLite: metadata"]
    FILES["Nguồn và artifact"]

    UI --> API
    API --> CORE
    API --> EXPORT
    API --> META
    API --> FILES
    CORE --> FILES
    EXPORT --> FILES
~~~

### 4.2. Phân lớp

| Lớp | Trách nhiệm | Không đảm nhiệm |
|---|---|---|
| Presentation | Thao tác, canvas, trạng thái tải | Homography/threshold |
| API | Request schema, ID, lỗi | Công thức lọc |
| Application | Điều phối upload/detect/render/export | SQL trong thuật toán |
| Processing | ndarray/config→ndarray/result | HTTP, DB, React |
| Infrastructure | Repository, encode/decode, tệp, PDF | Quyết định UI |

### 4.3. Mô-đun

- **SessionService:** phiên, thứ tự, thêm/xóa trang.
- **ImportService:** kiểm tra, EXIF, chuẩn hóa, thumbnail.
- **DetectionService:** ảnh phân tích, contour, xếp hạng.
- **GeometryService:** góc, kích thước, homography.
- **EnhancementService:** preset và bộ lọc.
- **RenderService:** snapshot config, revision, cache.
- **ExportService:** artifact đúng revision, đúng thứ tự.
- **ArtifactRepository:** metadata và truy cập tệp theo ID.

Hợp đồng lõi:

~~~python
detect_document(image_bgr, detection_config) -> DetectionResult
validate_quad(points_normalized, width, height) -> ValidationResult
warp_document(image_bgr, ordered_points_px, max_long_edge) -> WarpResult
enhance_document(warped_bgr, render_config) -> RenderResult
~~~

Các hàm này không tự đọc đường dẫn tùy ý, cập nhật DB hoặc trả HTTP response.

### 4.4. Thực thi

MVP dùng HTTP đồng bộ, frontend chờ kết quả. Đưa tác vụ xử lý vào executor có giới hạn **một worker ảnh**, tách khỏi event loop API. Dùng một tiến trình Uvicorn để giới hạn có hiệu lực toàn ứng dụng.

- Một render active, tối đa hai yêu cầu chờ; đầy trả 429.
- Không giữ transaction DB khi xử lý ảnh/PDF.
- Hủy chờ ở frontend không bảo đảm dừng tác vụ; kiểm tra revision trước commit.
- Không dựng queue phân tán. Chỉ chuyển sang job API 202 nếu đo thực tế thấy tác vụ kéo dài.
- Async không tự làm thuật toán CPU nhanh hơn.

### 4.5. Triển khai

Phát triển: Vite proxy /api đến FastAPI. Demo: build React, FastAPI phục vụ static cùng origin. Bind localhost.

Truy cập camera trực tiếp bằng getUserMedia yêu cầu secure context, thường HTTPS; localhost trên điện thoại không trỏ đến máy tính [R10]. Nhập ảnh/chụp qua input file là dự phòng. Truy cập điện thoại qua LAN cần cấu hình mạng và kiểm thử riêng.

---

## 5. Mô hình dữ liệu và quản lý tệp

### 5.1. Thực thể

| Thực thể | Trường chính | Ý nghĩa |
|---|---|---|
| ScanSession | id, title, created_at, updated_at | Phiên nhiều trang |
| ScanPage | id, session_id, position, original_artifact_id, normalized_artifact_id, width, height | Trang và nguồn |
| PageConfig | page_id, revision, corners_json, confirmed, mode, filters_json, rotation | Config hiện hành |
| Artifact | id, page_id nullable, session_id, kind, revision nullable, path, mime, byte_size, sha256, created_at | Tệp nội bộ |
| ExportRecord | id, session_id, page_snapshot_json, artifact_id, created_at | PDF theo snapshot |

Một phiên có nhiều trang; một trang có config hiện hành và nhiều artifact. MVP không bắt buộc lịch sử chỉnh sửa đầy đủ. Lưu nguồn, config và artifact đang được tham chiếu.

### 5.2. Config đầy đủ mẫu

~~~json
{
  "revision": 3,
  "corners": [[0.08, 0.09], [0.91, 0.12], [0.88, 0.93], [0.06, 0.90]],
  "confirmed": true,
  "mode": "bw",
  "rotation": 0,
  "denoise": {"method": "median", "kernel": 3},
  "illumination": {"enabled": false, "kernel": 101},
  "contrast": {"method": "none", "clip_limit": 2.0, "tile_grid": [8, 8]},
  "threshold": {"method": "adaptive_gaussian", "block_size": 31, "c": 10},
  "sharpen": {"enabled": false, "amount": 0.5},
  "geometry": {"aspect_policy": "estimated", "max_long_edge": 2400}
}
~~~

Đây là preset khởi đầu, không tối ưu cho mọi ảnh. Backend trả effective_config sau kiểm tra.

### 5.3. Lưu trữ

| Vùng | Nội dung |
|---|---|
| data/app.sqlite3 | Metadata |
| data/sessions/{sid}/sources | Nguồn nhập và nguồn chuẩn hóa |
| data/sessions/{sid}/renders | Kết quả theo trang/revision |
| data/sessions/{sid}/debug | Ảnh trung gian khi bật |
| data/sessions/{sid}/exports | PDF/ảnh |
| data/tmp | Tệp chưa commit |

Tên vật lý dùng UUID; tên upload chỉ hiển thị, không ghép thành đường dẫn. Không lưu ảnh blob vào SQLite.

### 5.4. Lưu bền và xóa

1. Encode vào tệp tạm cùng filesystem, thành công rồi đổi tên nguyên tử.
2. Transaction DB ghi metadata và tham chiếu artifact.
3. DB thất bại: xóa tệp mới không được tham chiếu; dọn rác xử lý phần còn lại sau crash.
4. Xóa trang: bỏ tham chiếu trong transaction trước, rồi xóa tệp không dùng.
5. Giữ artifact đang được export snapshot tham chiếu.
6. Không xóa nguồn của phiên còn tồn tại; tệp tạm >24 giờ có thể dọn.
7. Không giữ mọi ndarray của phiên trong RAM.

Revision tăng khi đổi góc, mode, bộ lọc, rotation; đổi tên/thứ tự không tăng revision ảnh.

---

## 6. Luồng nghiệp vụ và trạng thái

### 6.1. Luồng chính

1. Tạo phiên và nhập ảnh.
2. Chuẩn hóa từng ảnh; ảnh lỗi được báo riêng.
3. Đề xuất góc.
4. Người dùng kiểm tra/sửa và xác nhận.
5. Warp, lọc, tạo preview.
6. Thay tham số và xem trước/sau.
7. Thêm/xóa/sắp xếp.
8. Xuất trang đã xác nhận và render thành công.

Không xuất vùng nhận diện chưa xác nhận.

### 6.2. Trạng thái

~~~mermaid
stateDiagram-v2
    [*] --> Imported
    Imported --> NeedsReview: đề xuất hoặc thiếu góc
    NeedsReview --> Ready: xác nhận hợp lệ
    Ready --> Rendering: render
    Rendering --> Rendered: thành công
    Rendering --> RenderError: lỗi
    RenderError --> Rendering: thử lại
    RenderError --> NeedsReview: sửa góc
    Rendered --> Ready: đổi bộ lọc
    Rendered --> NeedsReview: đổi vùng cắt
~~~

### 6.3. Request trả ngược thứ tự

Render revision 4 trong lúc config đã thành revision 5:

- Revision 4 không trở thành kết quả hiện hành của 5.
- Render nhận expected_revision; lệch trả 409.
- Kiểm tra revision lần nữa trước commit.
- Frontend chỉ nhận response đúng page_id và revision hiện tại.
- Debounce thanh trượt khoảng 300 ms; không render mỗi pointer move.
- Export chụp snapshot page_id/revision/thứ tự trước tạo PDF.

---

## 7. Quy ước ảnh và tọa độ

### 7.1. Ảnh

- Ảnh chuẩn hóa đã áp dụng EXIF đúng một lần, là nguồn hình học duy nhất.
- OpenCV: BGR uint8 [0,255]; xám H×W uint8.
- Nhị phân: nền 255, chữ 0.
- Chia, gradient, sharpening dùng float trước clip.
- Frontend RGB; đổi kênh đúng khi encode/decode.
- Alpha ghép nền trắng.
- Không hứa độ chính xác màu in theo ICC trong MVP.

### 7.2. Tọa độ API

Gốc trái trên, x sang phải, y xuống; tọa độ trên ảnh chuẩn hóa:

$$
u=x/(W-1),\quad v=y/(H-1)
$$

$$
x=u(W-1),\quad y=v(H-1)
$$

Điểm hữu hạn, thuộc [0,1]; W/H tối thiểu 2.

### 7.3. Các độ phân giải

| Ảnh | Mục đích | Cạnh dài đề xuất |
|---|---|---|
| Chuẩn hóa | Nguồn warp, tái xử lý | Giữ nguồn, ≤16 MP |
| Phân tích | Contour | 1200, không upscale |
| Render chuẩn | Lọc và xuất | 2400, không upscale vượt mức ước lượng |
| Preview | Hiển thị nhanh | 1000, thu từ render |

Detection trên ảnh nhỏ; warp từ nguồn. Không xuất từ thumbnail. Lọc chỉ trên render chuẩn; preview thu nhỏ sau lọc để tránh hai kích thước dùng cùng kernel nhưng cho kết quả khác nhau.

### 7.4. Canvas mapping

Ảnh contain trong canvas Wc×Hc:

$$
s=\min(W_c/W,H_c/H)
$$

$$
o_x=(W_c-sW)/2,\quad o_y=(H_c-sH)/2
$$

$$
x=(x_{\mathrm{pointer}}-o_x)/s,\quad
y=(y_{\mathrm{pointer}}-o_y)/s
$$

Pointer đổi qua boundingClientRect về CSS pixel canvas. Backing store nhân devicePixelRatio nhưng tọa độ pointer không nhân lần nữa. Zoom/pan dùng inverse display transform.

Kiểm thử ảnh dọc/ngang, letterbox và HiDPI.

---

## 8. Pipeline xử lý ảnh

### 8.1. Phát hiện

~~~mermaid
flowchart TB
    A["Nguồn chuẩn hóa"] --> B["Thu nhỏ, xám, Gaussian"]
    B --> C["Canny và closing"]
    C --> D["Contour và tứ giác"]
    D --> E{"Ứng viên hợp lệ?"}
    E -->|Có| F["Xếp hạng, đề xuất"]
    E -->|Không| G["Chọn thủ công"]
    F --> H["Người dùng xác nhận"]
    G --> H
~~~

### 8.2. Tạo trang

~~~mermaid
flowchart TB
    A["Nguồn và góc xác nhận"] --> B["Homography và warp"]
    B --> C{"Chế độ"}
    C --> D["Màu: giữ màu, chỉnh nhẹ"]
    C --> E["Xám: lọc, tương phản"]
    C --> F["Đen trắng: lọc, threshold"]
    D --> G["Xoay, lưu render"]
    E --> G
    F --> G
    G --> H["Preview, ảnh, PDF"]
~~~

Ảnh Gaussian trong detection không thành nguồn xuất; tách nhánh để tránh làm mờ chữ.

Làm đều sáng trước tương phản/threshold; deskew sau warp; sharpening sau tương phản màu/xám, không sau nhị phân cuối. Không chạy mọi bộ lọc cho mọi ảnh.

---

## 9. Đặc tả thuật toán

### 9.1. Nhập và chuẩn hóa

**Đầu vào:** byte ảnh. **Đầu ra:** BGR chuẩn hóa, kích thước, hash, thumbnail.

1. Đọc upload theo khối, giới hạn byte; không tin Content-Length.
2. Kiểm tra bằng decoder, không chỉ MIME/phần mở rộng.
3. Kiểm tra kích thước từ header trước giải mã toàn bộ; xử lý cảnh báo ảnh quá lớn.
4. Chỉ nhận JPEG/PNG một frame; từ chối ảnh động/multi-frame.
5. ImageOps.exif_transpose [R11].
6. Chuyển RGB; alpha ghép trắng.
7. RGB→BGR; kiểm tra kích thước/pixel count.
8. Encode ảnh chuẩn hóa lossless, bỏ EXIF.
9. Lưu nguồn và metadata.

HEIC/WebP/PDF đầu vào ngoài MVP; HEIC cần chuyển JPEG hoặc cấu hình camera tương thích.

### 9.2. Xám và thu nhỏ

cv2.cvtColor(BGR2GRAY), gần đúng:

$$
Y=0.299R+0.587G+0.114B
$$

$$
r=\min(1,1200/\max(W,H))
$$

$$
W_a=\operatorname{round}(rW),\quad H_a=\operatorname{round}(rH)
$$

Dùng INTER_AREA khi thu nhỏ [R5]. Ánh xạ góc dùng kích thước thực sau làm tròn:

$$
u=x_a/(W_a-1),\quad v=y_a/(H_a-1)
$$

Không chỉ chia cho r vì hai chiều có thể làm tròn khác nhau.

### 9.3. Gaussian

Giảm nhiễu trước biên. Nhánh detection: kernel 5×5, sigma=0 để thư viện suy ra.

$$
G_\sigma(i,j)=\frac{1}{2\pi\sigma^2}
\exp\left(-\frac{i^2+j^2}{2\sigma^2}\right)
$$

Chuẩn hóa kernel tổng bằng 1:

$$
I_f(x,y)=\sum_{i,j}K(i,j)I(x-i,y-j)
$$

Gaussian làm mượt cả chi tiết; Median thay bằng trung vị và phù hợp nhiễu muối tiêu [R1]. Không mặc định mọi nhiễu từ thiết bị điện tử đều là Gaussian.

### 9.4. Canny

Ảnh xám đã lọc→edge map uint8. Các bước: gradient, non-maximum suppression, hai ngưỡng và hysteresis [R2].

$$
M=\sqrt{G_x^2+G_y^2},\quad
\theta=\operatorname{atan2}(G_y,G_x)
$$

cv2.Canny: apertureSize=3, L2gradient=True.

Thử tối đa ba cặp (50,150), (75,200), (100,250); gộp và loại trùng ứng viên. Đây là cấu hình thực nghiệm của đồ án. UI kiểm tra 0≤low<high≤255.

Không khẳng định ngưỡng theo median mức xám luôn tốt; ảnh giấy gần trắng có thể làm heuristic đó thiếu ổn định.

### 9.5. Closing

Edge trắng 255; kernel 3×3, một iteration:

$$
A\bullet B=(A\oplus B)\ominus B
$$

Dilation mở rộng trắng; erosion thu trắng; closing dilation rồi erosion để nối hở nhỏ [R3].

~~~python
closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel_3x3)
~~~

Closing quá mạnh nối cả chữ/bóng. Hiệu ứng lên chữ phải xét foreground; không gọi erosion “làm chữ nhỏ” khi chữ là đen.

### 9.6. Contour và Douglas–Peucker

1. findContours(closed, RETR_LIST, CHAIN_APPROX_SIMPLE).
2. Loại vùng nhỏ; giữ tối đa 30 contour lớn/trial.
3. Tính chu vi P.
4. approxPolyDP với epsilon=eP, e∈{0.015,0.02,0.03}.
5. Giữ bốn đỉnh, lồi, không suy biến.

OpenCV cung cấp diện tích, chu vi, Douglas–Peucker và kiểm tra lồi [R4]. RETR_LIST giữ cơ hội nhận diện contour con.

Bộ lọc ban đầu:

- Area ≥10% ảnh.
- Mỗi cạnh ≥5% cạnh ngắn ảnh.
- Điểm phân biệt; không ba điểm gần thẳng hàng.
- Không tự cắt, winding thống nhất.
- Không buộc góc gần 90° vì phối cảnh làm góc xiên.

Tài liệu nhỏ có thể bị loại; vẫn cho chọn tay.

### 9.7. Xếp hạng

**Heuristic do đồ án đề xuất**, cần tune validation, không phải xác suất học máy:

$$
S(Q)=\operatorname{clip}(0.45a+0.35e+0.20f-0.15b,0,1)
$$

| Biến | Cách tính | Vai trò |
|---|---|---|
| a | area(Q)/(WaHa) | Ưu tiên vùng lớn |
| e | Tỉ lệ điểm dọc cạnh có edge trong 2 px | Hỗ trợ biên |
| f | min(area(contour),area(Q))/max(...) | Khớp diện tích |
| b | Tỉ lệ mẫu cạnh trong dải sát mép 2 px | Phạt viền ảnh |

Lấy mẫu cạnh cách khoảng 2 px; đo e trên edge map **trước closing**. Loại trùng bằng polygon IoU>0.95, giữ score cao nhất.

- ≥0.60: đề xuất.
- 0.40–0.60: đề xuất và cảnh báo.
- <0.40: manual_required.

Ngưỡng phải kiểm chứng. Trường tên heuristic_score; không hiển thị “độ chính xác 85%” từ score=0.85.

Không chỉ lấy contour lớn nhất: mặt bàn/bìa/khung có thể lớn hơn giấy.

### 9.8. Fallback

- Không có ứng viên: status=manual_required, corners=null.
- UI tạo vùng kéo cách mép 5%, chưa được xác nhận.
- Cho “dùng toàn ảnh”.
- Không dùng minAreaRect thay cho tứ giác phối cảnh; rectangle bao không xác định bốn góc trang thật.
- Thiếu góc, lóa, mờ: gợi ý chụp lại; vẫn có chỉnh tay.

### 9.9. Thứ tự góc và tính hợp lệ

Nội bộ [p0,p1,p2,p3] theo chiều kim đồng hồ trong tọa độ y xuống. Nhãn UI thường là trên trái/phải/dưới phải/trái, nhưng đây là nhãn ánh xạ hình học.

Tự phát hiện:

1. Tâm c là trung bình bốn điểm.
2. Sắp theo atan2(y−cy,x−cx).
3. Kiểm tra tích có hướng liên tiếp cùng dấu, area và cạnh.
4. Điểm đầu min(x+y), tie-break y rồi x.
5. Xoay vòng danh sách; không chọn đỉnh độc lập.
6. Signed shoelace area dương cho winding này; đảo nếu cần.

Không chọn bốn đỉnh độc lập qua min/max tổng/hiệu vì có thể trùng điểm.

Trang gần hình thoi: góc bắt đầu không xác định hướng đọc chữ; người dùng xoay 90°.

Góc tay giữ ID handle, không tự sắp lại mỗi khi kéo. Backend từ chối tự cắt/trùng/không lồi/gần suy biến.

### 9.10. Homography và warp

Giả định tài liệu phẳng:

$$
w=\max(\|p_1-p_0\|,\|p_2-p_3\|),\quad
h=\max(\|p_3-p_0\|,\|p_2-p_1\|)
$$

Làm tròn, tối thiểu 2; giảm cùng tỉ lệ nếu cạnh dài >2400.

Đích: (0,0), (w−1,0), (w−1,h−1), (0,h−1).

$$
\lambda
\begin{bmatrix}x'\\y'\\1\end{bmatrix}
=H\begin{bmatrix}x\\y\\1\end{bmatrix}
$$

$$
x'=\frac{h_{11}x+h_{12}y+h_{13}}{h_{31}x+h_{32}y+h_{33}},
\quad
y'=\frac{h_{21}x+h_{22}y+h_{23}}{h_{31}x+h_{32}y+h_{33}}
$$

getPerspectiveTransform(src,dst), warpPerspective(..., INTER_LINEAR) [R5].

H có 8 bậc tự do sau khi cố định hệ số tỷ lệ; bốn cặp điểm không suy biến cung cấp 8 phương trình. Khi sinh ảnh đích, dùng ánh xạ ngược và nội suy để tránh lỗ trống do đẩy pixel nguồn. Mỗi pixel đích lấy tổng có trọng số của bốn láng giềng tại vị trí nguồn không nguyên khi dùng nội suy song tuyến tính. warpPerspective thực hiện phần lấy mẫu này; không cần tự viết trong MVP.

Độ dài cạnh ảnh **không suy ra tỉ lệ giấy vật lý chính xác** khi chụp xiên:

- estimated: theo công thức cạnh; tỉ lệ ước lượng.
- a4: người dùng xác nhận A4, ép tỉ lệ cạnh dài/ngắn=√2.

Không suy ra “300 DPI” chỉ từ 2400 px. Kiểm tra H hữu hạn và hình học không suy biến; không đặt ngưỡng condition number tùy tiện trên H chưa chuẩn hóa.

### 9.11. Lọc ảnh đã warp

| Lọc | Khi dùng | Khởi đầu | Rủi ro |
|---|---|---|---|
| None | Sắc, ít nhiễu | — | Giữ nhiễu |
| Median | Chấm rời | 3×3 | Mất dấu/nét mảnh |
| Gaussian | Nhiễu nhẹ trước threshold | 3×3 | Mềm nét |
| Bilateral tùy chọn | Màu, giữ biên | d=5, sigmaColor=30, sigmaSpace=30 | Chậm |

Màu mặc định None; BW Median 3 nhưng cho tắt. Không mặc định kernel 7 cho chữ nhỏ. Cơ chế lọc theo OpenCV [R1].

### 9.12. CLAHE

Chia vùng, giới hạn khuếch đại histogram và kết hợp vùng [R6].

- Xám: trực tiếp.
- Màu: BGR→Lab, sửa L, giữ a/b, đổi lại.
- clipLimit=2.0, tileGridSize=(8,8), cho chọn None.
- Có thể làm nổi nhiễu/bóng; không dùng quá mạnh.
- Không cân bằng riêng B/G/R vì có thể đổi màu.

### 9.13. Làm đều sáng — tùy chọn

Baseline đề xuất:

$$
B=\operatorname{GaussianBlur}(\operatorname{close}(I,K_b))
$$

$$
I_n=\operatorname{clip}
\left(I_{\mathrm{float}}
\frac{255}{\max(B_{\mathrm{float}},\epsilon)},0,255\right)
$$

ε=5; kernel lẻ khoảng 101 trên render chuẩn, lớn hơn nét chữ. Tính float.

Chỉ bật xám/BW. Bóng cứng, giấy màu, hình minh họa lớn có thể làm ước lượng nền sai. Không khôi phục vùng lóa. Cho tắt và so sánh.

Grayscale closing dùng phép hình thái [R3]; công thức chia nền là thiết kế thí nghiệm của đồ án.

### 9.14. Otsu

Histogram chuẩn hóa p(i). Chia [0,t] và [t+1,255]:

$$
\omega_0(t)=\sum_{i=0}^{t}p(i),\quad
\omega_1(t)=1-\omega_0(t)
$$

$$
t^*=\arg\max_t
[\omega_0(t)\omega_1(t)(\mu_0(t)-\mu_1(t))^2]
$$

Bỏ nhóm rỗng. Dùng THRESH_BINARY|THRESH_OTSU [R7]. Nền trắng, chữ đen cho giấy thông thường.

Trong đó μ0 và μ1 là trung bình mức xám của hai nhóm, tính bằng tổng i·p(i) trong nhóm chia cho trọng số ω tương ứng. Histogram có thể tính bằng vòng lặp/NumPy để minh họa trước khi dùng hàm OpenCV.

Phù hợp sáng khá đều, hai nhóm tách biệt; baseline so với Adaptive, không hứa tốt nhất khi có bóng.

### 9.15. Adaptive Gaussian

$$
T(x,y)=\sum_{(i,j)\in N}w_{ij}I(x+i,y+j)-C
$$

$$
D(x,y)=
\begin{cases}
255 & I(x,y)>T(x,y)\\
0 & \text{ngược lại}
\end{cases}
$$

w Gaussian chuẩn hóa. adaptiveThreshold với ADAPTIVE_THRESH_GAUSSIAN_C, THRESH_BINARY [R8].

Khởi đầu blockSize=31, C=10. Block lẻ >1, trong [3,151], phù hợp kích thước ảnh.

C tăng hạ ngưỡng, thường làm nhiều pixel thành trắng; giảm C làm chữ đậm hơn nhưng tăng nền đen. Block nhỏ dễ nhiễu; lớn ít thích nghi bóng.

Không threshold ảnh màu. Binarization mất highlight, màu và sắc độ; dùng màu/xám khi cần giữ.

### 9.16. Unsharp masking

$$
I_{\mathrm{sharp}}=\operatorname{clip}(I+\alpha(I-G_\sigma*I),0,255)
$$

Float trước clip; α=0.5, miền [0,1.5]. Màu chỉ sửa luminance. Tắt mặc định, chỉ màu/xám.

Tăng cảm giác sắc nhưng không khôi phục chữ đã mất do rung/mất nét. Gaussian theo cơ chế 9.3.

### 9.17. Xoay và deskew

Xoay 90° dùng cv2.rotate sau lọc; không nội suy, không sửa corners nguồn.

Deskew góc nhỏ thuộc Could:

1. Tạo mask chữ tạm, trắng là chữ.
2. HoughLinesP tìm dòng dài.
3. Góc về [-90°,90°), giữ |θ|≤10°.
4. Trung vị có trọng số độ dài; chỉ dùng khi đủ dòng nhất quán.
5. Xoay ảnh màu/xám theo −θ, mở rộng canvas, nền trắng.
6. Threshold cuối nếu BW.

Bảng/ảnh/bố cục nhiều cột làm góc sai; không đủ bằng chứng giữ 0°. Không lấy minAreaRect tất cả chữ làm phương án đúng mọi trường hợp.

### 9.18. Cảnh báo mờ

Thử chỉ số:

$$
V=\operatorname{Var}(\nabla^2 I)
$$

Đo trên tài liệu warp, cùng cạnh dài 1000 và dtype. V thấp có thể do mờ hoặc trang ít chữ; phải tune trên dữ liệu nhóm.

Chỉ cảnh báo, không tự từ chối/xóa. Không dùng một ngưỡng Internet như chuẩn chung.

### 9.19. Pseudocode

~~~text
IMPORT(file):
    validate bytes, format, dimensions
    decode and apply EXIF once
    composite alpha on white; normalize BGR uint8
    persist original + normalized source + metadata

DETECT(page):
    source -> analysis(max edge 1200) -> gray -> Gaussian(5)
    candidates = []
    for each of at most 3 Canny pairs:
        edges = Canny(blurred)
        closed = closing(edges, 3)
        contours = find_contours(closed)
        for each of at most 30 large contours:
            for each epsilon ratio:
                quad = approximate(contour)
                if quad valid:
                    score against edges before closing
                    add candidate
    remove duplicates
    return best normalized quad or manual_required

RENDER(page, expected_revision):
    read config snapshot; require revision match and confirmed quad
    load normalized source
    normalized corners -> source pixel corners; validate
    warped = perspective_warp(source, corners, max_edge=2400)
    rendered = apply selected mode and validated parameters
    rotate rendered
    encode full render and downscaled preview into temporary files
    verify revision unchanged before committing artifacts
    return artifact IDs, effective config and timings

EXPORT(session, ordered_snapshot):
    verify page membership, confirmed quad and exact render revision
    create PDF from full renders in snapshot order
    persist PDF and page/revision snapshot
    return artifact ID
~~~

### 9.20. Tham số khởi đầu

| Tham số | Mặc định | Miền API/UI | Lưu ý |
|---|---:|---|---|
| Analysis edge | 1200 | Server config | Không upscale |
| Render edge | 2400 | 1200–3000 | Thêm giới hạn pixel |
| Detection Gaussian | 5 | 3/5/7 | Lẻ |
| Canny pairs | 50/150;75/200;100/250 | low<high | ≤3 trial |
| Closing | 3×3, 1 lần | 3/5; 1/2 lần | Detection |
| Epsilon | 0.015/0.02/0.03 | Server config | Theo chu vi |
| Min quad area | 0.10 | Server config | Tỉ lệ ảnh |
| Median | 3 | 3/5/None | Tránh quá mạnh |
| CLAHE | 2.0; 8×8 | clip 1–4 | Tùy chọn |
| Adaptive | 31; C=10 | block lẻ 3–151; C −20…30 | Sau warp |
| Illumination | 101 | lẻ 31–201 | Tùy chọn |
| Sharpen | 0.5 | 0–1.5 | Tắt mặc định |
| Rotation | 0 | 0/90/180/270 | Sau lọc |

Đây là chính sách ứng dụng cần tune, không phải thông số tối ưu đã chứng minh.

---

## 10. Hợp đồng API

/api/v1; UUID; timestamp UTC ISO 8601. Endpoint trang kiểm tra thuộc session.

### 10.1. Endpoint

| Method | Endpoint | Đầu vào | Đầu ra |
|---|---|---|---|
| POST | /sessions | title | Phiên |
| GET | /sessions | Phân trang | Danh sách |
| GET | /sessions/{sid} | — | Phiên và trang |
| DELETE | /sessions/{sid} | — | Xóa |
| POST | /sessions/{sid}/pages | Một file multipart | Trang |
| DELETE | /sessions/{sid}/pages/{pid} | — | Xóa trang |
| PUT | /sessions/{sid}/page-order | Danh sách ID đầy đủ | Thứ tự |
| POST | /sessions/{sid}/pages/{pid}/detect | Detection config | Đề xuất, chưa xác nhận |
| PUT | /sessions/{sid}/pages/{pid}/config | expected_revision + config | Config, revision mới |
| POST | /sessions/{sid}/pages/{pid}/render | expected_revision, debug | Artifact |
| GET | /sessions/{sid}/pages/{pid}/debug | revision | Ảnh trung gian |
| POST | /sessions/{sid}/exports | Snapshot, PDF options | PDF artifact |
| GET | /artifacts/{aid} | — | Byte ảnh/PDF |
| GET | /health | — | Trạng thái |

Frontend upload từng ảnh, tối đa một active; lỗi riêng, không rollback toàn phiên. File dùng multipart/form-data; không ghép JSON body thông thường vào request upload [R9].

### 10.2. Detect response

~~~json
{
  "page_id": "uuid",
  "source_width": 3024,
  "source_height": 4032,
  "status": "suggested",
  "corners": [[0.08, 0.09], [0.91, 0.12], [0.88, 0.93], [0.06, 0.90]],
  "heuristic_score": 0.74,
  "algorithm_version": "detect-v1",
  "warnings": [],
  "timings_ms": {"preprocess": 38, "edges": 55, "contours": 42, "total": 148}
}
~~~

Số liệu chỉ minh họa schema. Detect không ghi đè config đã xác nhận; người dùng chấp nhận bằng cập nhật config.

### 10.3. Config request

~~~json
{
  "expected_revision": 2,
  "config": {
    "corners": [[0.08, 0.09], [0.91, 0.12], [0.88, 0.93], [0.06, 0.90]],
    "confirmed": true,
    "mode": "bw",
    "rotation": 90,
    "denoise": {"method": "median", "kernel": 3},
    "threshold": {"method": "adaptive_gaussian", "block_size": 31, "c": 10}
  }
}
~~~

Config nhận cấu trúc PageConfig; trường tùy chọn thiếu được bổ sung mặc định schema, **không âm thầm kế thừa giá trị cũ**. Response trả đầy đủ effective_config; frontend nên gửi config đầy đủ để giữ tham số.

Sửa góc cần xác nhận lại. Tham số không áp dụng với mode hiện tại được đánh dấu inactive.

### 10.4. Render response

~~~json
{
  "page_id": "uuid",
  "revision": 3,
  "render_artifact_id": "uuid-render",
  "preview_artifact_id": "uuid-preview",
  "width": 1700,
  "height": 2400,
  "warnings": [],
  "timings_ms": {"warp": 65, "enhance": 120, "encode": 80, "total": 290}
}
~~~

Khóa cache gồm hash nguồn, config chuẩn hóa, version thuật toán và dependency liên quan. Debug thiếu có thể phải tính lại; cache preview không chứng minh debug đã lưu.

### 10.5. Export

~~~json
{
  "pages": [
    {"page_id": "uuid-1", "revision": 3},
    {"page_id": "uuid-2", "revision": 5}
  ],
  "format": "pdf",
  "paper_size": "a4",
  "orientation": "auto",
  "margin_mm": 5,
  "image_encoding": "png"
}
~~~

- ID không trùng, thuộc phiên; snapshot revision hợp lệ.
- Thiếu render trả 409 và danh sách cần render; UI render rồi thử lại.
- Tối đa 20 trang; xử lý lần lượt.
- A4 210×297 mm; 72 point/inch, 25.4 mm/inch.
- Fit theo tỉ lệ, không stretch/crop để lấp đầy trang.
- PNG cho BW tránh artefact JPEG quanh chữ.
- PDF ảnh không copy/tìm chữ.

### 10.6. Lỗi

~~~json
{
  "error": {
    "code": "INVALID_QUAD",
    "message": "Bốn góc đang tạo vùng cắt tự giao nhau.",
    "details": {"page_id": "uuid"}
  }
}
~~~

| HTTP | Code | UI |
|---|---|---|
| 400 | INVALID_CONFIG, INVALID_QUAD | Sửa giá trị/góc |
| 404 | PAGE_NOT_FOUND, ARTIFACT_NOT_FOUND | Tải lại |
| 409 | REVISION_CONFLICT, PAGE_NOT_RENDERED | Đồng bộ/render |
| 413 | FILE_TOO_LARGE, TOO_MANY_PIXELS | Giảm ảnh |
| 415 | UNSUPPORTED_IMAGE | Đổi JPEG/PNG |
| 422 | REQUEST_VALIDATION_FAILED | Chỉ lỗi schema |
| 429 | PROCESSING_BUSY | Thử lại, không gửi dồn |
| 500 | PROCESSING_FAILED | Giữ nguồn/config, thử lại |

Không phát hiện tài liệu là 200/manual_required, không phải 500.

---

## 11. Giao diện

### 11.1. Bố cục

Trái: thumbnails và thứ tự. Giữa: Nguồn/Vùng cắt/Kết quả/Các bước. Phải: mode/tham số/xác nhận/render/xuất.

Mobile: thumbnail ngang, tham số panel thu gọn.

### 11.2. Chỉnh góc

- Handle đủ lớn cảm ứng, hit area lớn hơn điểm vẽ.
- Ngoài polygon tối hơn; overlay không ghi lên ảnh nguồn.
- Kính lúp tại handle là Should.
- Chặn tự giao và báo lý do; backend vẫn kiểm tra.
- Tự nhận diện / Đặt lại / Dùng toàn ảnh / Xác nhận.
- Xuất bị vô hiệu khi chưa xác nhận hoặc chưa render revision hiện hành.

### 11.3. Mode

| Mode | Tham số | Mặc định |
|---|---|---|
| Màu | Lọc, CLAHE luminance, nét | Không lọc |
| Xám | Lọc, CLAHE, đều sáng, nét | CLAHE nhẹ |
| BW | Lọc, Otsu/Adaptive, block/C, đều sáng | Adaptive Gaussian |

“Màu” giữ màu còn trong nguồn, không tái tạo màu từ ảnh BW.

### 11.4. Học thuật

Hiển thị ảnh đã chạy thực: chuẩn hóa, xám, Gaussian, Canny, closing, contour/score, warp, histogram trước threshold, kết quả.

Với nhiều Canny trial, mặc định artifact của trial tạo ứng viên được chọn; cho xem trial khác. Không dùng placeholder như kết quả thuật toán thật.

---

## 12. Hiệu năng, lỗi và giới hạn

### 12.1. RAM

16 MP BGR uint8 khoảng 48 MB; float32 ba kênh khoảng 192 MB. Bản sao làm tăng RAM nhanh.

Xử lý một trang, detection 1200, render 2400; float chỉ ma trận cần thiết; debug xuống đĩa; giải phóng sau encode. Không giữ 20 trang ndarray.

### 12.2. Chi phí

| Bước | Chi phí tham khảo | Lưu ý |
|---|---|---|
| Màu/histogram | O(N) | Pixel đầu vào |
| Lọc trực tiếp k×k | O(Nk²) | Thư viện có tối ưu |
| Gaussian separable | O(Nk) | Hai chiều |
| Threshold cục bộ | Theo cách tính cửa sổ | Không mặc định O(N) |
| Canny/morphology kernel cố định | Xấp xỉ tuyến tính | Theo implementation |
| Contour | Edge/số điểm | Giới hạn trial |
| Warp | O(Nout) | Pixel đầu ra |
| Encode/PDF | Theo độ phân giải/nén | Đo riêng |

Phân tích không thay thế benchmark.

### 12.3. Tình huống khó

| Trường hợp | Vấn đề | Xử lý |
|---|---|---|
| Giấy/bàn cùng sáng | Biên yếu | Trial khác, chọn tay |
| Nền nhiều họa tiết | Nhiễu contour | Scoring, xác nhận |
| Khung/bìa lớn | Chọn sai vùng | Support biên, border penalty |
| Thiếu góc | Thiếu hình học | Chụp lại |
| Bóng | Otsu nền đen | Adaptive/đều sáng |
| Lóa | Mất chữ | Chụp lại |
| Mờ | Chữ kém đọc | Cảnh báo, chụp lại |
| Cong | Warp chưa thẳng dòng | Ghi giới hạn |
| Dấu/chữ nhỏ | Mất nét | Giảm lọc, đổi block/C |
| Highlight/ảnh | BW mất thông tin | Màu/xám |
| EXIF | Overlay lệch | Chuẩn hóa trước tọa độ |
| Bow-tie | Warp xoắn | Từ chối góc |
| Response cũ | Preview ghi đè | Revision |

### 12.4. Đầu vào và triển khai

Kiểm tra format/frame/byte/pixel; xử lý decompression bomb; enum/range; từ chối NaN/Infinity. Artifact ID thay đường dẫn. Không log ảnh/base64. Không public toàn data.

Nếu mở Internet: phải bổ sung xác thực, phân quyền chủ sở hữu, quota/rate limit; MVP localhost chưa bao gồm các phần đó.

---

## 13. Kiểm thử và thực nghiệm

### 13.1. Dataset

Kế hoạch: khoảng **80 ảnh tự chụp, tối thiểu 15 tài liệu**; chưa có dataset đính kèm.

Điều kiện: nền đơn giản/họa tiết, sáng đều/bóng, thẳng/nghiêng, chữ nhỏ/lớn, màu, nhiễu/mờ.

- 40 development, 20 validation, 20 test.
- Cùng tài liệu vật lý nằm trong cùng tập.
- Gán bốn góc trên nguồn đã EXIF.
- Mẫu khó/thiếu góc đánh dấu, không âm thầm loại.
- Test không dùng tune score/threshold.
- Dataset nhỏ: nêu số mẫu và giới hạn tổng quát hóa.

### 13.2. Detection metrics

$$
IoU(Q_p,Q_g)=\frac{Area(Q_p\cap Q_g)}{Area(Q_p\cup Q_g)}
$$

Có thể rasterize cùng kích thước; dùng nhất quán.

$$
E_c=\frac{1}{4\sqrt{W^2+H^2}}
\min_{\pi\in\Pi}\sum_{i=0}^{3}\|p_i-g_{\pi(i)}\|
$$

Π là xoay vòng/đảo thứ tự chu kỳ, không mọi hoán vị tùy ý.

Báo cáo tỉ lệ đề xuất, tỉ lệ IoU≥0.90, mean/median IoU, corner error, tỉ lệ cần sửa và thời gian sửa. Không có đề xuất tính là thất bại tự nhận diện; IoU có điều kiện phải ghi rõ.

Mục tiêu: ≥80% tự đề xuất IoU≥0.90 trên test tương đối thuận lợi. Báo cáo nhóm khó và tổng thể; không đảm bảo trước.

### 13.3. Chất lượng render

- Quan sát dấu tiếng Việt, nét mảnh, nền và halo.
- Vùng nền không chữ: đo mean/std sáng trước/sau đều sáng.
- Có ground truth chữ: foreground F1/IoU.
- 10–20 cặp ảnh, 2–3 người đánh giá độ đọc 1–5; ghi chủ quan.
- Entropy/tương phản tăng không chứng minh đọc tốt.
- Không PSNR/SSIM trực tiếp ảnh nghiêng với ảnh warp khác kích thước.
- Chỉ dùng PSNR/SSIM khi reference căn chỉnh cùng hình học.
- Không có mask chữ: không tự tạo “accuracy” từ histogram.

### 13.4. So sánh

| Thí nghiệm | Cố định | Biến | Ghi |
|---|---|---|---|
| A | Ảnh/Canny/score | None/Gaussian3/Gaussian5 | IoU, sai, time |
| B | Ảnh/Canny | None/closing3/closing5 | Nối tốt/nối nhầm |
| C | Candidate generation | Largest contour/score | IoU, sửa tay |
| D | Góc/warp | Otsu/Adaptive31/51 | Chữ/nền/F1 nếu có |
| E | Góc/xám | None/CLAHE | Độ đọc/nhiễu |
| F | Ảnh bóng | Adaptive/nền-normalize+Adaptive | Bóng/chữ mất |
| G | Các bước còn lại | Analysis800/1200/1600 | IoU, p50/p95, RAM |

D/E/F dùng cùng góc ground truth hoặc góc tay đã xác nhận để tách ảnh hưởng vùng cắt.

### 13.5. Test cần thiết

| Ca | Kết quả |
|---|---|
| EXIF 90° | Dimensions, overlay, warp đúng |
| PNG alpha | Nền trắng |
| File giả/hỏng | Lỗi rõ, phiên còn |
| Nén nhỏ >16 MP | Từ chối |
| Trùng/tự cắt/gần suy biến | Từ chối góc tay |
| Diamond | Không trùng; xoay sửa hướng |
| Bốn góc bốn màu | Đúng góc đích |
| Canvas round-trip HiDPI | Sai số trong ngưỡng |
| Sửa trong render | Revision cũ không hiện hành |
| Render lỗi | Nguồn/config còn |
| Đổi thứ tự ba trang | PDF đúng snapshot |
| Config mới | Không xuất render cũ |
| PDF | Đủ trang, không stretch, không thumbnail |
| Restart | Phiên mở lại |
| DB commit lỗi sau encode | Không tham chiếu tệp thiếu, dọn rác |

### 13.6. Bảng báo cáo

| Chỉ tiêu | Development | Validation | Test |
|---|---|---|---|
| Số ảnh/tài liệu | Điền sau đo | Điền sau đo | Điền sau đo |
| Đề xuất/thành công | Điền sau đo | Điền sau đo | Điền sau đo |
| IoU/corner error | Điền sau đo | Điền sau đo | Điền sau đo |
| Detect p50/p95 | Điền sau đo | Điền sau đo | Điền sau đo |
| Render p50/p95 | Điền sau đo | Điền sau đo | Điền sau đo |
| RAM đỉnh | Điền sau đo | Điền sau đo | Điền sau đo |

Đo core và request đầu-cuối, nêu cache. Giữ ảnh thất bại kèm phân tích.

---

## 14. Cấu trúc mã nguồn

### 14.1. Frontend

| Đường dẫn | Nội dung |
|---|---|
| frontend/src/pages/ScannerPage.tsx | Trang chính |
| frontend/src/components/UploadPanel.tsx | Nhập/chụp |
| frontend/src/components/PageList.tsx | Trang/thứ tự |
| frontend/src/components/CornerEditor.tsx | Canvas/handle/mapping |
| frontend/src/components/FilterPanel.tsx | Mode/tham số |
| frontend/src/components/ComparisonView.tsx | Trước/sau |
| frontend/src/components/PipelineViewer.tsx | Trung gian |
| frontend/src/api/client.ts | HTTP |
| frontend/src/types/scanner.ts | Schema UI |
| frontend/src/hooks/usePageRender.ts | Debounce/revision/loading |

State/context đủ MVP; không bắt buộc Redux.

### 14.2. Backend

| Đường dẫn | Nội dung |
|---|---|
| backend/app/main.py | App/lifecycle/static/errors |
| backend/app/api/sessions.py | Phiên |
| backend/app/api/pages.py | Upload/detect/config/render |
| backend/app/api/exports.py | Export |
| backend/app/api/artifacts.py | Tệp theo ID |
| backend/app/schemas/ | Pydantic |
| backend/app/services/ | Use case |
| backend/app/processing/normalize.py | EXIF/màu |
| backend/app/processing/detection.py | Biên/contour/score |
| backend/app/processing/geometry.py | Góc/homography |
| backend/app/processing/enhancement.py | Lọc/CLAHE/threshold |
| backend/app/processing/quality.py | Metrics/cảnh báo |
| backend/app/storage/ | DB/tệp |
| backend/app/export/pdf.py | Layout PDF |
| backend/tests/ | Hình học/API/export |
| experiments/ | Script/config thí nghiệm |
| docs/ | Đặc tả/kết quả |

### 14.3. Phần tự cài đặt

Đề xuất tự viết nhỏ: histogram 256 bin, threshold tay, Median hoặc Gaussian convolution, Otsu, erosion/dilation nhị phân, scoring và quad validation.

So với OpenCV trên ảnh nhỏ, cùng border policy/dtype. Pipeline ứng dụng dùng OpenCV để tránh vòng lặp chậm. Nếu giảng viên yêu cầu tự viết thuật toán cụ thể, ưu tiên yêu cầu đó và ghi rõ phần tự viết/phần thư viện.

---

## 15. Kế hoạch 6–8 tuần

| Tuần | Việc | Sản phẩm |
|---|---|---|
| 1 | EXIF/dataset/pipeline offline | Xám/blur/Canny |
| 2 | Contour/score/góc/warp | Overlay, warp, test góc màu |
| 3 | Mode/Otsu/Adaptive/CLAHE | So sánh cùng vùng |
| 4 | API/SQLite/artifact/revision | Luồng backend |
| 5 | React/canvas/nhiều trang | Quét tay hoàn chỉnh |
| 6 | PDF/reopen/lỗi/debug | Demo đầu-cuối |
| 7 | Validation/test/benchmark | Bảng, ảnh thất bại |
| 8 | Báo cáo/demo | Bản chạy, đặc tả cập nhật |

Hai người: một xử lý ảnh/thí nghiệm, một UI/API/storage/export; cùng chốt tọa độ và revision trước ghép.

---

## 16. Tiêu chí nghiệm thu

### 16.1. Chức năng

- [ ] JPEG/PNG, EXIF và giới hạn đúng.
- [ ] Đề xuất góc trên ảnh thuận lợi.
- [ ] Fallback tay vẫn hoàn thành.
- [ ] Góc không trùng/tự cắt/suy biến.
- [ ] Warp không lật/xoắn.
- [ ] Màu/xám/BW và tham số hợp lệ.
- [ ] Preview/export cùng render.
- [ ] Xoay/sắp xếp.
- [ ] JPG/PNG/PDF đủ trang, đúng thứ tự/tỉ lệ.
- [ ] Nguồn giữ nguyên; reopen phiên.
- [ ] Revision cũ không ghi đè mới.

### 16.2. Học thuật

- [ ] Mục đích/công thức/giới hạn.
- [ ] Tách detection/enhancement.
- [ ] Ảnh trung gian thật.
- [ ] Histogram, Otsu/Adaptive.
- [ ] Góc gán nhãn; validation/test tách.
- [ ] Định lượng, máy đo, phương pháp.
- [ ] Ví dụ thất bại.
- [ ] Phân biệt heuristic/mục tiêu/kết quả.

### 16.3. Demo 5–7 phút

1. Ảnh sáng đều nghiêng: detect→xác nhận→warp.
2. Nền khó: nhận diện sai/không có→sửa góc.
3. Bóng: Otsu và Adaptive cùng vùng.
4. Canny/closing/contour/histogram.
5. Highlight: màu giữ thông tin.
6. Ba trang: xoay/sắp xếp/PDF.
7. Lóa/mờ: giới hạn.

Ưu tiên pipeline giải thích được, có chỉnh tay và đánh giá trung thực.

---

## 17. Tài liệu tham khảo

Kiểm tra ngày 07/10/2026. Nguồn xác nhận cơ chế/API; kiến trúc, scoring, preset, quota và mục tiêu là thiết kế đề xuất.

- **[R1] OpenCV — Smoothing Images:** Gaussian, Median, Bilateral.  
  https://docs.opencv.org/4.x/d4/d13/tutorial_py_filtering.html
- **[R2] OpenCV — Canny Edge Detection.**  
  https://docs.opencv.org/4.x/da/d22/tutorial_py_canny.html
- **[R3] OpenCV — Morphological Transformations.**  
  https://docs.opencv.org/4.x/d9/d61/tutorial_py_morphological_ops.html
- **[R4] OpenCV — Contour Features.**  
  https://docs.opencv.org/4.x/dd/d49/tutorial_py_contour_features.html
- **[R5] OpenCV — Geometric Transformations.**  
  https://docs.opencv.org/4.x/da/d6e/tutorial_py_geometric_transformations.html
- **[R6] OpenCV — Histogram Equalization / CLAHE.**  
  https://docs.opencv.org/4.x/d5/daf/tutorial_py_histogram_equalization.html
- **[R7] OpenCV — Image Thresholding / Otsu.**  
  https://docs.opencv.org/4.x/d7/d4d/tutorial_py_thresholding.html
- **[R8] OpenCV — Miscellaneous Image Transformations / adaptiveThreshold.**  
  https://docs.opencv.org/4.x/d7/d1b/group__imgproc__misc.html
- **[R9] FastAPI — Request Files.**  
  https://fastapi.tiangolo.com/tutorial/request-files/
- **[R10] MDN — getUserMedia.**  
  https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia
- **[R11] Pillow — ImageOps.exif_transpose.**  
  https://pillow.readthedocs.io/en/stable/reference/ImageOps.html
