# Kiểm chứng nguyên nhân img_004 với tài liệu môn học

Ngày 15/10/2026. Người dùng yêu cầu xác định nguyên nhân vùng trang bị lấy lẫn bàn và dò lại giáo trình, hai slide PDF. Lượt này chỉ chẩn đoán, đối chiếu và lưu bằng chứng; không thay thuật toán, preset, score hoặc trạng thái task.

## Kết luận

Otsu được thực hiện đúng công thức trên ảnh này. Nguyên nhân chính là ngưỡng global gộp một phần bàn sáng với giấy thành cùng foreground. Contour lấy từ vùng đó vốn đã sai so với mục tiêu tìm giấy. Bước xấp xỉ dùng epsilon theo chu vi của contour răng cưa cho phép sai số lớn, rút vùng sai thành một tứ giác vẫn vượt gate hình học. Bộ mô tả hiện tại đo được hỗ trợ biên yếu nhưng chưa có điều kiện từ chối riêng một cạnh gần như không được hỗ trợ.

Vì vậy, tính đúng của từng phép xử lý chưa bảo đảm chuỗi xử lý tìm đúng trang. Đây là thiếu sót về giả thiết phân tách và tiêu chí chấp nhận của baseline dự án, không phải bằng chứng OpenCV tính sai Otsu hoặc geometry đổi nhầm thứ tự góc.

## Phạm vi đọc lại PDF

Đọc lại từ PDF hiện có, lưu SHA-256 và text theo từng trang bằng pypdf; không chỉ dựa vào ghi nhớ từ phiên trước. Toàn bộ text được trích để tìm mục, nhưng chỉ các trang liên quan bên dưới được đọc kỹ trong lượt này:

| Nguồn | Trang PDF đọc liên quan | Căn cứ |
|---|---|---|
| [Giáo trình](<Giáo trình _ Xử lý ảnh.pdf>) |111–120,163–164|Điều kiện ngưỡng toàn cục, chiếu sáng/phản xạ, Otsu mục5.3.2, phát triển vùng mục5.4.1, xấp xỉ MPP mục6.2.3 |
| [Slide chương5](<xla_Ch05 (1).pdf>) |5–6,31–32,35–40|Tiêu chí phân vùng, histogram không chứa vị trí, ánh sáng không đều, công thức Otsu và phân biệt phát triển vùng |
| [Slide chương6](xla_Ch06.pdf) |9,12,17–19,24,36|Biên từ vùng nhị phân, biểu diễn đa giác/chia đoạn, ảnh hưởng tolerance, mô tả biên và giới hạn diện tích |

Render bằng Poppler và xem đầy đủ 9 trang: giáo trình114/118/119, slide5 trang35/37/40, slide6 trang17/19/36. File trung gian/hash/text/render nằm tại .tmp/theory-review-img004/ (ignored). Không tuyên bố đọc lại toàn bộ308+60+63trang bằng mắt trong lượt này; PDF gốc không sửa.

## 1. Kiểm tra Otsu bằng công thức giáo trình

Giáo trình trang116–118 định nghĩa histogram chuẩn hóa, xác suất/tổng cường độ tích lũy và chọn k tối đa hóa phương sai giữa hai lớp, các phương trình(5-62),(5-63). Ảnh nhị phân dùng f(x,y)>k thành foreground, phương trình(5-64). Slide5 trang36–37 trình bày cùng tiêu chuẩn tối ưu.

Script `.tmp/diagnose_img004.py` tính độc lập bằng NumPy từ histogram của analysis blurred, không gọi cv.threshold cho phép tính tham chiếu:

```text
p[i] = histogram[i] / N
w[k] = sum(p[0:k+1])
m[k] = sum(i*p[i], i=0..k)
mG = sum(i*p[i], i=0..255)
sigma_between[k] = (mG*w[k] - m[k])² / (w[k]*(1-w[k]))
k* = argmax, với 0 < w[k] < 1
mask = 255 nếu gray > k*, ngược lại 0
```

Kết quả có cực đại duy nhất tại **k=102**, trùng actualt102 của OpenCV. Mask tham chiếu khớp toàn bộ pixel với mask của core hiện hành và mask đã lưu trong revision01. Hai lớp có mức xám trung bình khoảng42.87 và161.76, tương ứng57.24%/42.76% số pixel. Đây là chia ảnh theo độ sáng, chưa phải các lớp có ngữ nghĩa bàn/giấy.

Sách trang118–119 có quy ước lấy trung bình các k khi cùng đạt cực đại; không suy từ phép kiểm một ảnh rằng mọi chi tiết tie-breaking của thư viện đều giống giả mã sách. Ở img_004 cực đại duy nhất nên tie không gây khác biệt hoặc gây lỗi này.

## 2. Xác định chỗ mask bị nhập nhầm

Nguồn sau EXIF1536×2048, analysis900×1200. Các điểm dưới đây chọn trực quan để kiểm tra pixel, không phải nhãn GT đánh giá detector:

| Điểm | Tọa độ x,y trên analysis | Gray sau Gaussian5 | Mask với t102 | Nhãn liên thông8 |
|---|---|---:|---:|---:|
| A trên mặt bàn |200,340|109|255|26|
| B bên trong giấy |400,650|186|255|26|

Hai điểm đều >102 và thuộc cùng thành phần26. Thành phần đó còn chạm biên trái ảnh (bounding box x=0), tổng453983pixel trắng. Không phải thao tác sắp bốn góc nhập hai vùng vào nhau: chúng đã nối nhau trong mask trước khi lấy contour và xấp xỉ.

Giáo trình trang112–114 nói hiệu quả ngưỡng phụ thuộc khả năng phân tách cường độ, nguồn chiếu sáng và phản xạ. Slide5 trang32 nói histogram không chứa vị trí không gian; trang35 chỉ ra ngưỡng toàn cục có thể gán nhầm vùng sáng và cần cân nhắc ngưỡng biến đổi/hiệu chỉnh nền. Đây là cơ sở phù hợp với hiện tượng quan sát được; không có định lý rằng lớp sáng nhất của toàn cảnh luôn là giấy.

Production dùng threshold→findContours(RETR_EXTERNAL) để lấy biên ngoài các thành phần trắng. Nó **không phải thuật toán phát triển vùng có hạt giống** ở giáo trình119–120/slide5 trang40; không có bước chọn seed hay cập nhật tiêu chuẩn tương đồng của vùng. connectedComponentsWithStats chỉ được dùng trong script chẩn đoán để xác nhận A và B cùng thành phần, không thêm vào core ở lượt này.

## 3. Vì sao vùng sai vẫn thành tứ giác hợp lệ?

Contour vùng giấy+bàn có chu vi **5417.48px** trên analysis. Ba lần xấp xỉ cho:

| epsilon/P | Số đỉnh | Kết quả gate |
|---:|---:|---|
|.015|13|NOT_QUADRILATERAL|
|.020|10|NOT_QUADRILATERAL|
|.030|4|Qua gate topology/area/cạnh|

Ở ratio.03, **epsilon=162.52px**. Khoảng cách lớn nhất đo từ điểm contour tới cạnh Q gần nhất là **160.76px**. Đây là phép đo khoảng cách một chiều contour→Q, không phải Hausdorff hoặc sai số góc so GT. Nó cho thấy tolerance hiện tại cho phép một xấp xỉ rất thô đối với đường bao răng cưa này.

Slide6 trang17–19 giải thích tolerance lớn làm mất chi tiết và chia đoạn chỉ rút gọn đường biên đầu vào. Xấp xỉ một vùng đã lấy lẫn bàn không tự tìm lại ranh giới giấy. Code dùng Douglas–Peucker qua approxPolyDP, phù hợp nguyên lý chia đoạn trên slide19; **không phải MPP** được giáo trình163–164 và slide18 trình bày. Epsilon/P=.015/.02/.03 và gate10%/5% là heuristic dự án, không phải tham số bắt buộc lấy từ PDF.

`validate_quad` chỉ xác lập bốn điểm lồi/không tự giao/không suy biến; nó không xác định vật thể là tờ giấy. Tứ giác này hợp lệ hình học nhưng sai nội dung cần cắt. Cạnh/vùng không bị ép góc vuông, và không có lỗi mapping hoặc winding quan sát được trong phép tái hiện.

## 4. Bộ mô tả có phản ánh vấn đề không?

Có: cạnh trên của Q chỉ có **7/245mẫu hỗ trợ raw Canny =2.86%**. Ba cạnh còn lại khoảng35.28%,44.04%,31.83%; e tổng=.304282. a=.390704, f=.930180, b=0, S=.468352, trùng metadata revision01.

f chỉ so diện tích contour/Q nên có thể cao dù góc lệch và một cạnh gần như không có bằng chứng. b lấy trên các cạnh Q; sau khi xấp xỉ bỏ các nhánh răng cưa sát mép, b=0 dù thành phần mask gốc chạm biên ảnh. Đây là các giới hạn của bộ đặc trưng/score hiện hành, không phải trị số accuracy. Slide6 trang36 nhắc diện tích đơn lẻ không đủ phân biệt hình và cần đặc trưng bổ sung; nó không quy định các trọng số a/e/f/b của dự án.

Ứng viên này chưa được tự confirmed/warp hoặc xem là trang đã nhận đúng. Task05.05–08/proposal/manual fallback vẫn chưa hoàn thành. Có thể dùng số đo từng cạnh để thiết kế cảnh báo/gate sau này, nhưng chưa chọn ngưỡng mới chỉ từ một ảnh.

## Bằng chứng và hướng cần đánh giá tiếp

Evidence mới tại experiments/results/img004-theory-verification/: diagnostic.png gồm ảnh/điểmA-B, thành phần chung trong mask, contour/Q; otsu-mask.png và metadata.json chứa phép tính độc lập, provenance, epsilon/deviation và các số đo. Source bytes/array giữ nguyên, PDF không sửa, ảnh/results/scripts đều ignored. Không đổi code nên không lặp fullsuite670tests; script chẩn đoán có assertions kiểm Otsu/mask/liên thông và phép tái hiện.

Hướng cần thử tiếp là tăng khả năng phân biệt vùng giấy với nền sáng (đánh giá đặc trưng màu/chiếu sáng/ngưỡng cục bộ phù hợp) và kiểm sai số xấp xỉ theo kích thước ảnh/cạnh thay vì chỉ dùng chu vi răng cưa. Cần đánh giá cả ca tốt/xấu; không mặc nhiên thay bằng Adaptive sẽ tìm đúng trang, không đổi sang MPP để mong sửa một mask sai, và không chỉ tăng score. Đây là kết luận chẩn đoán, chưa phải một thay đổi thuật toán đã được chấp nhận/triển khai thêm.
