# Cấu hình và môi trường đã khóa — MVP13.06

Ngày 26/10/2026. Bản khóa chính: [frozen.json](../experiments/configs/frozen.json), `freeze_id=mvp13-freeze-v1`, schema 1. SHA-256:

```text
ce89a90e2fb9ca092350886276201f87e81cd09c90e6507f799fceca6a8d8109
```

Khóa được tạo lúc `2026-10-26T04:45:10.619065+00:00`, sau hồi quy tự động, smoke UI và restart. Tại thời điểm khóa chưa chạy detector hoặc đánh giá enhancement trên 7 ảnh test. Đây là mốc trước đánh giá; kết quả sau khóa13.07 được cập nhật ở cuối tài liệu.

## Quyết định giữ cấu hình

Development chỉ có một tài liệu, 3 quad tham chiếu và 3 ảnh không thể gán quad đáng tin. [Đối chứng detector](results.md) chưa đủ bằng chứng để thay preset: bỏ Gaussian làm giảm mean IoU, bỏ closing tăng đề xuất nhưng có ca chọn chữ/bàn. Giữ detector `detect-v1`, pipeline `scan-v1`, preset revised, Gaussian 5×5 và closing 3×3 một lần.

Giữ 3 cặp Canny 20/60, 50/150, 75/200; analysis tối đa 1.200; epsilon/P = 0,015/0,02/0,03; tối đa 30 contour/trial; ngưỡng diện tích 10%, cạnh 5%. Fallback vùng sáng Otsu chỉ khi cả ba trial Canny thiếu quad. Score vẫn `clip(.45a + .35e + .20f − .15b, 0, 1)`, hỗ trợ biên lấy từ raw Canny; NMS chỉ loại IoU > 0,95; ngưỡng proposed/cảnh báo là 0,60/0,40. Các tùy chọn ablation giữ để đối chứng, không trở thành mặc định.

| Preset | Lọc | Tương phản | Nhị phân |
|---|---|---|---|
| Color | không | không hoạt động | không hoạt động |
| Gray | không | CLAHE clip 2, lưới 8×8 | không hoạt động |
| BW | Median 3 | không | Adaptive Gaussian, block 31, C 10 |

Các preset đầy đủ, gồm trường inactive, rotation 0, corners null và confirmed false, được xuất từ `get_preset` thật vào JSON. Phần so sánh enhancement chỉ đổi `threshold.method` sang Otsu trên cùng warp; ngưỡng Otsu thực được đo từng ảnh, không khóa thành một số cố định. Góc của từng ảnh, thao tác xác nhận và cấu hình người dùng vẫn là đầu vào riêng; file frozen phục vụ thực nghiệm, không ghi đè tài liệu trên app.

## Môi trường thực tế

| Thành phần | Giá trị |
|---|---|
| OS | Windows 11, 10.0.26300, AMD64 |
| CPU | Intel Core i7-11700F @ 2.50 GHz, 8 nhân/16 luồng |
| RAM vật lý do OS báo | 34.017.787.904 byte, khoảng 31,68 GiB |
| Python | CPython 3.12.10 |
| Node / npm | v24.15.0 / 11.12.1 |
| OpenCV Python / distribution | 4.14.0 / opencv-python-headless 4.14.0.94 |
| NumPy / Pillow | 2.5.4 / 12.3.0 |
| FastAPI / SQLAlchemy / ReportLab | 0.143.0 / 2.1.4 / 5.0.1 |
| React / TypeScript / Vite | 19.3.0 / 7.0.2 / 8.3.4 |
| OpenCV | 16 threads, optimized true, OpenCL false |

`frozen.json` lưu 31 distribution Python thực tế và phiên bản trực tiếp của các dependency frontend, đồng thời đối chiếu với requirements/package.json. Hash build information OpenCV cũng được giữ. Khi hỏi trạng thái OpenCL, OpenCV ghi native diagnostic “Can't create default OpenCL queue” và trả false; đây là kết quả probe trên máy này. Pipeline nhận mảng NumPy và các lượt kiểm chứng dùng CPU; không tuyên bố đã thử GPU. Không thay cài đặt OpenCV để che diagnostic này. RAM trên là dung lượng máy, không phải đỉnh RAM khi chạy; đo RAM/thời gian lặp thuộc 13.07.

## Danh tính mã nguồn và đầu vào

Chưa có commit để định danh bản hiện hành. Snapshot lưu SHA-256 của **91 tệp**: toàn bộ mã app backend/frontend theo các phần mở rộng được liệt kê trong `freeze_config.py`, cùng các helper xử lý/đánh giá hiện có. Lưu thêm hash requirements, package-lock, cấu hình build, manifest, annotations và detection_trials. Không đọc ảnh test để tạo snapshot. Metadata nhãn/test đã được chuẩn bị trước đây được ràng buộc bằng hash.

Hash nguồn detector thay đổi ở 13.03–04 vì thêm tùy chọn ablation; snapshot M1 cũ vẫn là bằng chứng lịch sử. Lượt 13.05–06 không thay mã lõi/backend HTTP/frontend hoặc dependency. Mã benchmark mới của 13.07 có thể gọi các helper đã khóa và phải lưu hash riêng; không sửa helper đã khóa sau khi nhìn kết quả test.

Đây là snapshot có thể phát hiện thay đổi, không phải chữ ký chống sửa bởi người có quyền ghi workspace. Nếu đổi source/config/dependency/dataset metadata hoặc môi trường, lệnh kiểm tra sẽ thất bại. Điều tra thay đổi, giữ bản khóa và kết quả cũ; nếu cần đổi thuật toán thì tạo version/bản khóa mới và ghi rõ test đã được quan sát, không dùng lại nó như test chưa thấy.

## Tái lập và kiểm tra trước đánh giá

Từ root dự án:

```powershell
& .\backend\.venv\Scripts\python.exe experiments/freeze_config.py --check
& .\backend\.venv\Scripts\python.exe experiments/evaluate_enhancement.py --output-dir experiments/results/enhancement-new
```

Lệnh thứ hai chỉ chạy development. Công cụ cho tập test/benchmark ở 13.07 phải gọi `verify_frozen` trước khi đọc ảnh hoặc xử lý; chưa hiện thực/chạy benchmark trong task này. Không thêm `--split test` giả vào CLI development hiện có.

Để tạo một bản khóa mới trong một thực nghiệm được phép, dùng `freeze_config.py --output <tệp mới> --regression-proof <JSON bằng chứng>`. Công cụ yêu cầu cổng hồi quy đạt và từ chối ghi đè. Bằng chứng gốc trong `experiments/results/mvp13-05-06-verified/` được giữ cục bộ, ngoài Git.

## Cổng hồi quy và điều chỉnh phụ thuộc

Người dùng ngày 26/10 chọn “Chạy hồi quy cần thiết trước khi khóa”. Theo đó, 13.06 dùng cổng hồi quy phục vụ bản khóa thay cho yêu cầu nghiệm thu toàn bộ chuỗi giai đoạn 12. [Ma trận](verification-matrix.md) ghi đúng phạm vi: 1.255 backend/experiments tests, 103 frontend tests, typecheck/build, browser nhập–confirm–render–PDF–reopen, route 404 và hash sau physical restart.

Task 13.05–06 và checkpoint 13-C2 đạt trong phạm vi này. Giai đoạn 12 vẫn chưa nghiệm thu; không tích các task 12.01–12.07. Task 13.07–08 và cổng 13 chưa đạt. Bản khóa không chứng nhận detector chọn đúng giấy trên mọi ảnh, chất lượng OCR hoặc khả năng tổng quát từ chỉ hai tài liệu.


## Cập nhật sau đánh giá 13.07–08

Ngày26/10, đã chạy7ảnh test sau khóa; frozen SHA và91source files/config/nhãn/dependencies giữ nguyên.
Thêm runner benchmark.py ngoài snapshot, hash b881679641ccd7f54de5708c9f6ef72f0657e72b15384ab8293633b05d05b7ec.
Runner tái lập OpenCL=false trước verify, vì tiến trình mới/elevated có thể tự bật OpenCL.
Lệnh `freeze_config.py --check` tự nó chỉ kiểm tra, không đặt lại trạng thái OpenCL;
nếu process mới bật OpenCL thì cổng phải báo drift. Có thể kiểm môi trường benchmark mà không đọc ảnh bằng:

```powershell
& .\backend\.venv\Scripts\python.exe -c "from experiments.benchmark import verify_runtime; verify_runtime(); print('verified')"
```

Lỗi PID launcher ở lượt đầu được sửa bằng PID server tự báo và đối chiếu logUvicorn; không sửa bản khóa.
Primary evidence mvp13-07-08-verified/final; lượt đầutest/giữ riêng và đánh dấu RAM HTTP không hợp lệ.
140 mẫu đo/28warmup,7/7IoU≥0,90/mean0,995347 trên một tài liệu; xem [kết quả](results.md),
[phương pháp](benchmark-method.md), [audit8task](audit-phase-13.md). Cổng13 đạt; giaiđoạn12 vẫn chưa nghiệm thu toàn bộ.

Test đã được quan sát. Các tác vụ đóng gói sau này có thể đổi mã phục vụ ứng dụng;
khi đó snapshot này tiếp tục định danh bản đã đo, không ghi đè hash cũ hoặc giả rằng bản đóng gói
là đúng91tệp ban đầu. Ghi version/source mới và kiểm chứng tương ứng; không tune theo test đã thấy.

MVP14.01–02 đã tạo bản `mvp14-local-v1`: `main.py`/`settings.py` đổi để phục vụ build,
thêm `web.py`; core/preset/dependency/dataset giữ hash. Vì vậy lệnh `verify_runtime()`
ở trên hiện phải từ chối phiên bản đóng gói. Snapshot cũ không được ghi đè.
91 source/10 input và runner đo cũ đã lưu lại với hash khớp trong evidence ignored;
manifest bản đóng gói và snapshot tạm cho HTTP test tổng hợp tách riêng.
Xem [bản chạy cục bộ](local-runtime.md); chưa có một lượt đánh giá test mới.
