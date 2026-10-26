# Mẫu demo tổng hợp

Năm PNG do `experiments/create_demo_samples.py` vẽ từ hình học và chữ giả lập, không chứa tài liệu cá nhân.
Chúng phục vụ thao tác UI và giải thích thuật toán; không được tính thêm vào dataset 13 ảnh/2 tài liệu.

| Tệp | Mục đích |
|---|---|
| 01-clean.png | Trang phẳng, mép rõ, phối cảnh; đề xuất tự động vẫn cần xác nhận. |
| 02-shadow.png | Độ sáng thay đổi mạnh; so Otsu và Adaptive với cùng góc/bộ lọc. |
| 03-no-boundary.png | Ảnh xám đồng nhất, cố ý không có trang/biên; detector phải yêu cầu chọn tay. Dùng toàn ảnh chỉ là lựa chọn của người dùng. |
| 04-highlight.png | Dải màu vàng; Color giữ màu, BW không giữ ý nghĩa màu. |
| 05-fold-light-simulation.png | Vệt tối mô phỏng ánh sáng quanh nếp gấp trên một đa giác phẳng; không mô phỏng hình học 3D hoặc chứng minh xử lý nhàu. |

`manifest.json` lưu hash, kích thước và góc **dựng hình**, không phải nhãn gán cho ảnh chụp thật.
Đã chạy lặp generator với cùng môi trường và kiểm byte/hash; thư mục tồn tại sẽ bị từ chối ghi đè.
Muốn tự tạo bản riêng, chạy từ root sau khi cài backend:

```powershell
& .\backend\.venv\Scripts\python.exe experiments/create_demo_samples.py --output-dir .tmp/demo-moi
```

Để xem nếp gấp thật trong workspace, dùng các ảnh development img_001/img_006 đã đăng ký trong
[manifest dữ liệu](../../experiments/dataset_manifest.csv). Các ảnh này không đi kèm gói nộp.
