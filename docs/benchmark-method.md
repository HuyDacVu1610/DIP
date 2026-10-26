# Phương pháp đánh giá và benchmark — MVP13.07

Phương pháp được ghi trước khi chạy ảnh test. Runner mới [benchmark.py](../experiments/benchmark.py) gọi các helper đã khóa, không sửa `evaluate_detection.py`, core, API hoặc [frozen.json](../experiments/configs/frozen.json). SHA bản khóa vẫn là `ce89a90e2fb9ca092350886276201f87e81cd09c90e6507f799fceca6a8d8109`.

## Dữ liệu, cổng và cấu hình

- Chỉ chọn 7 ảnh `test` của doc_02 theo manifest; kiểm hash nguồn, PNG sau EXIF, kích thước và nhãn. 6 ảnh doc_01 development dùng cho đối chứng trước đây được báo riêng.
- `verify_frozen` chạy trước khi mở ảnh test, trong tiến trình HTTP mới và sau lượt đo. Runner lưu hash riêng, file `protocol.json` được ghi trước khi validator mở pixel test. File frozen và runner cũng được đối chiếu hash sau cùng.
- Môi trường theo [mốc 13.06](experiment-environment.md): i7-11700F, 8 nhân/16 luồng, khoảng 31,68 GiB RAM OS báo; Python 3.12.10, OpenCV 4.14.0/16 threads/optimized true, NumPy 2.5.4, Windows 11. Không ép single-thread OpenCV hoặc đổi tham số detector.
- Một tiến trình mới trên máy có thể tự bật OpenCL, khác trạng thái false đã khóa. Runner dùng `cv2.ocl.setUseOpenCL` để tái lập đúng giá trị trong snapshot trước cổng kiểm tra, trong cả controller và server. Không bỏ qua khác biệt snapshot, không sửa bản khóa hay driver; thao tác này chỉ tác động các tiến trình benchmark.
- Đánh giá detector dùng `detect_document` revised/default, debug true để giữ ảnh trung gian thật. Tính IoU và sai số góc từ `result.corners`; không lấy ứng viên chẩn đoán làm đề xuất khi manual_required. Thiếu đề xuất trên ảnh có nhãn nhận IoU 0; sai số góc để null và báo số mẫu.
- Benchmark detector dùng debug false. Render dùng BW/Median 3/không CLAHE/Adaptive 31/C 10/rotation 0 và góc tham chiếu riêng mỗi ảnh, nhằm đo render độc lập lỗi cắt. `confirmed=true` chỉ đặt trong tài liệu benchmark cô lập để đi qua cổng service; không có nghĩa người dùng đã xác nhận các trang này trên app thật. Không đo ba mode riêng, OCR hoặc dewarping.

## Số lượt, thời gian và cache

Mỗi ảnh chạy tuần tự 4 đường: core detect, core render, HTTP detect, HTTP render. Mỗi đường có **1 warmup + 5 lượt đo**. Dự kiến 7×4×6 = 168 dòng, trong đó 28 warmup và 140 lượt đo; mỗi đường có 35 mẫu đo nếu không lỗi. Warmup được lưu nhưng loại khỏi percentile.

Core dùng nguồn BGR sau EXIF đã giải mã và kiểm hash bên ngoài đồng hồ. Đồng hồ `perf_counter_ns` bao quanh lời gọi hàm, không gồm decode nguồn, encode PNG hoặc I/O. Giữ thêm timing nội bộ mà lõi trả về. Ghi PNG để đối chiếu nằm ngoài thời gian core.

HTTP là một tiến trình Uvicorn thật, một worker xử lý, SQLite/file store riêng dưới thư mục kết quả và bind loopback cổng trống. Đo từ lúc gửi request đến khi đọc/parse xong JSON qua kết nối TCP mới. Bao gồm hàng đợi, đọc/hash PNG nguồn, xử lý, encode, transaction/file persistence và response; không gồm upload/config chuẩn bị, tải ảnh output, frontend hoặc proxy Vite. Upload ảnh gốc được kiểm normalized hash bằng manifest. Server được dừng gracefully sau đo, không dùng DB người dùng.

Không dùng cache kết quả ứng dụng: mọi POST detect/render phải trả run ID mới, render giữ revision 1 nhưng tạo artifact/run mới. Source core đã nằm trong RAM; OS page cache, allocator và các vùng nhớ OpenCV được giữ sau warmup. Đây là **warm-cache benchmark với cache kết quả app tắt**, không giả rằng đã tắt cache hệ điều hành hoặc đo cold start.

Percentile dùng `numpy.quantile(method='linear')`: p50/p95 trên các mẫu đo thành công, gộp đều 5 lượt/ảnh. Báo cùng tổng số lần thử và số lỗi; giữ mọi dòng lỗi trong CSV, không âm thầm loại ảnh. Chỉ 7 ảnh của một tài liệu nên p95 này là mô tả 35 lần đo cục bộ, không ước lượng p95 cho tập người dùng độc lập. Không có ngưỡng SLA được chốt để gọi latency là đạt/trượt.

## RAM

Dùng Win32 `GetProcessMemoryInfo` qua `ctypes`, lấy WorkingSetSize và PeakWorkingSetSize theo byte. Microsoft định nghĩa chúng lần lượt là working set hiện tại và đỉnh working set của tiến trình. [Hàm PSAPI](https://learn.microsoft.com/en-us/windows/win32/api/psapi/nf-psapi-getprocessmemoryinfo), [cấu trúc counters](https://learn.microsoft.com/en-us/windows/win32/api/psapi/ns-psapi-process_memory_counters). Server tự ghi `os.getpid()` trước startup; PID đo phải khớp PID Uvicorn trong log. Không dùng `Popen.pid` làm PID đo trên Windows vì venv có thể chạy một redirector riêng.

Mỗi lời gọi lấy baseline, lấy mẫu khoảng 10 ms bằng thread và lấy điểm cuối. CSV giữ baseline/đỉnh đã lấy mẫu/end, số mẫu và đỉnh cả vòng đời tiến trình. Core đo PID controller; HTTP đo PID server, không tính chung RAM browser, controller hoặc toàn máy vào số server.

Đỉnh lấy mẫu có thể bỏ lỡ cấp phát ngắn hơn khoảng lấy mẫu; đỉnh vòng đời không thể quy hết cho riêng lời gọi hiện tại. Không dùng `tracemalloc` để đại diện toàn bộ buffer native OpenCV/NumPy. Không coi baseline hoặc chênh lệch RSS là kích thước riêng của thuật toán; allocator/cache có thể giữ bộ nhớ giữa lượt. Việc lấy mẫu cũng có overhead nhỏ, không tuyên bố đây là đo không xâm nhập.

## Tái lập, lỗi và bằng chứng

Từ root:

```powershell
& .\backend\.venv\Scripts\python.exe experiments/benchmark.py --output-dir experiments/results/frozen-test-new
```

Thư mục phải mới. CLI kiểm bản khóa và metadata trước đo, xuất source PNG đúng payload, detection stages/overlay/metadata/metrics, full BW/preview, config từng ảnh, accuracy.csv, samples.csv, protocol và summary. Khi lỗi, lưu lỗi/partial samples nếu đã có, trả exit 1 và giữ ảnh trong thống kê; không tự đổi góc, preset hoặc retry để có kết quả đẹp.

Sau khi đã xem test, bộ này trở thành bộ test đã quan sát. Có thể sửa lỗi runner và chạy kiểm chứng lại với lịch sử rõ, nhưng không dùng các ảnh này để tune rồi gọi lại là test chưa thấy. Nếu đổi thuật toán, cần version/bộ đánh giá phù hợp và giữ kết quả bản khóa hiện hành.

### Sửa phép đo PID, không sửa thuật toán

Lượt đầu `mvp13-07-08-verified/test/` giữ nguyên: 7 kết quả góc hợp lệ nhưng RAM HTTP đã đọc launcher (~4,7 MiB), không phải server. Không dùng số RAM đó trong bảng kết quả cuối. Runner v1.1 lấy PID do server báo và kiểm với log Uvicorn; test hồi quy tái hiện thiếu PID/report trước khi sửa. Sau khi kiểm thử, chạy lại toàn bộ protocol trong thư mục mới `final/`; dùng trọn lượt mới cho thời gian/RAM, không trộn số tốt nhất giữa hai lượt. Test đã được quan sát từ lượt đầu; việc chạy lại phục vụ sửa đo lường, không đổi tham số/nhãn/thuật toán hoặc tạo một bộ test độc lập mới.
