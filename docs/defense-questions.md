# Câu hỏi bảo vệ và câu trả lời kiểm chứng được

Đọc cùng [báo cáo](report.md), [demo](demo-script.md) và [hướng thuật toán](Phan_Tich_Huong_Thuat_Toan_Tu_Tai_Lieu.md).
Các câu dưới đây phân biệt phần thư viện, quy tắc dự án và giới hạn của dữ liệu.

| Câu hỏi | Câu trả lời ngắn và bằng chứng nên mở |
|---|---|
| Sản phẩm làm gì ngoài nhập ảnh? | Nhiều trang, chỉnh/xác nhận góc, warp, Color/Gray/BW, xoay, debug/histogram, lưu/mở lại và xuất ảnh/PDF. PDF là ảnh, chưa OCR. Mở luồng demo3trang. |
| EXIF có tự xoay chữ cho đứng không? | Không. Nó áp quy tắc orientation được camera ghi vào tệp, một lần lúc chuẩn hóa; xoay kết quả là lựa chọn riêng. Ảnh không có metadata phù hợp không tự suy ra chiều chữ. |
| Sao không lấy bốn góc rồi cắt bounding box? | Bounding box vẫn giữ méo phối cảnh và nền. Homography ánh xạ tứ giác gần phẳng sang hình chữ nhật; bốn cặp điểm cung cấp8ràng buộc cho ma trận3×3 xác định tới hệ số tỷ lệ. Xem warp và H. |
| Có bốn góc có bảo đảm đó là giấy không? | Không. Geometry chỉ kiểm chu kỳ/lồi/diện tích/cạnh, không hiểu ngữ nghĩa. Khung bàn có thể hợp lệ và điểm cao; xem img_004 rồi chỉnh tay. |
| Vì sao không ép góc90° trong ảnh chụp? | Hình chữ nhật trong không gian có thể thành tứ giác góc xiên do phối cảnh. Ép90° ở ảnh nguồn loại mất ảnh chụp nghiêng đúng. |
| Có xử lý giấy nhàu/gấp không? | Có thể cải thiện bóng/nếp nhẹ nếu mép còn rõ, nhưng một homography không dewarp mặt cong/không đồng phẳng. Không khôi phục chữ che/cháy sáng. Mẫu05 chỉ mô phỏng ánh sáng, chưa là bằng chứng giấy nhàu thật. |
| Biên có vai trò gì? | Biên là thay đổi cường độ; mép giấy, chữ, bóng, nền và nếp gấp đều có thể tạo biên. Phải từ edge map tới contour, đa giác và chọn vùng; không coi mọi biên là mép giấy. |
| Gaussian trước Canny làm gì? | Giảm nhiễu để gradient ít phản ứng với dao động nhỏ, nhưng có thể làm mất mép yếu. Bản chính dùng5×5/sigma0; ablation noGaussian có cả lợi và hại. Không blur nguồn dùng warp. |
| Canny gồm những bước nào? | Làm trơn, gradient/độ lớn-hướng, non-maximum suppression, hai ngưỡng và hysteresis liên thông. Dùng OpenCV aperture3/L2true; ba cặp20/60,50/150,75/200 thuộc preset revised. Không tự viết lại Canny. |
| Closing có phải tô kín giấy không? | Không. Giãn rồi co với rect3×3 một lần để nối hở nhỏ trên edge map. Có thể nối nhầm, không fill mọi lỗ. Đo hỗ trợ cạnh trên raw Canny, không dùng closed để tự chứng minh. |
| Biểu diễn và mô tả biên khác nhau ra sao? | Contour có thứ tự và quad Q là biểu diễn; chu vi, cạnh, góc đổi hướng, số đỉnh và cờ hình học là mô tả. Diện tích tương đối/độ khớp là đặc trưng vùng. Xem bảng CandidateMetrics. |
| CHAIN_APPROX_SIMPLE có phải mãFreeman? | Không. Nó nén các đoạn contour thẳng; dự án không xuất mãchuỗiFreeman. Không nhận findContours là implementation Moore tự viết. |
| approxPolyDP có phải MPP trong slide? | Không. OpenCV dùng Douglas–Peucker với ε/P=.015/.02/.03. Có liên hệ ý tưởng xấp xỉ/chia đoạn, nhưng không đồng nhất đa giác chu vi tối thiểu MPP. |
| Vì sao ứng viên phải có bốn đỉnh? | MVP mô hình trang gần phẳng bằng tứ giác. Chỉ nhận contour/quad có diện tích≥10%analysis và cạnh≥5%cạnh ngắn, topology hợp lệ; không ép mọi contour thành tứ giác. |
| Score gồm gì? | S=clip(.45a+.35e+.20f−.15b,0,1): diện tích tương đối, hỗ trợ rawedge, khớp diện tích contour–quad, phạt sát khung. f không phải sai số khoảng cách contour. Đây là heuristic của dự án. |
| e có phải trung bình4cạnh? | Không. Mỗi cạnh lấy mẫu cách nhau≤2analysispx, hỗ trợ khi có rawedge trong bán kính2px. e=tổng mẫu được hỗ trợ/tổng mẫu; cạnh dài có nhiều mẫu hơn. |
| S=.8 có nghĩa80%đúng không? | Không. Chưa hiệu chuẩn xác suất. S≥.60 đề xuất; .40≤S<.60 cảnh báo; dưới.40 hoặc khôngquad yêu cầu tay. Tất cả vẫn chưa xác nhận. |
| Tại sao cần NMS? | Loại quad trùng giữa các trial bằng greedy theo score, chỉ loại khi IoU>.95 với survivor. Nó không nhận diện ngữ nghĩa, không gộp rawsupport giữa trial. |
| Otsu được dùng ở hai chỗ à? | Nhánh vùng trướcwarp chỉ chạy khi cả ba Canny không có quad, lấy thành phần sáng ngoài để tìm vùng. Otsu sauwarp nhị phân chữ/nền. Mục tiêu và raster đầu vào khác nhau. |
| Đổi từanalysisvềsource bằng chia tỉ lệ là đủ? | Không dùng một r lý tưởng: dimensions resize được làm tròn. Dùng u=x/(W−1),v=y/(H−1) ở mỗi raster để map sang nguồn, giữ subpixel. |
| Sao preview nhỏ mà xuất không mờ theo? | Preview được thu từ fullrender sau xử lý/xoay; PNG/JPG/PDF dùng fullrender đúngrevision. Không xuất từ thumbnail/ảnh màn hình. |
| Median/Gaussian khác nhau gì? | Median giảm nhiễu xung nhưng có thể xóa nét mảnh; Gaussian làm mềm nhiễu và nét. Dùng kernel3/5 trước chuyểnmode, không lọc chồng lên output cũ. |
| CLAHE là gì,8×8là gì? | Cân bằng histogram cục bộ có giới hạn khuếch đại và nội suy giữa tile. 8×8là sốtile, không phải8pixel. clip_limit1–4; chỉ Gray/BW, Color giữ màu. Không bảo đảm tăng độ đọc mọi ảnh. |
| Otsu chọn ngưỡng thế nào? | Tối đa phương sai giữa hai lớp histogram toàn ảnh. Không có một sốt cố định cho mọi ảnh; xem actualthreshold/histogram của đúngrun. Bóng mạnh có thể bị gộp thành foregroundđen. |
| Adaptive có một ngưỡng chung không? | Không. T(x,y)=trung bình Gaussian quanh pixel−C. Blocklẻ3–151 phải vừa cạnh ngắnwarp; mặc định31/C10. Có thể giữ ôly/nhiễu hoặc làm đứt dấu. |
| Histogram chứng minh ảnh tốt chưa? | Không. Nó đếm256mức của preparedgray đầy đủ trướcthreshold/xoay; tổngbin=W×H. Không chứa vị trí pixel, không chứng minh đúngvùng hoặc đọc đượcchữ. |
| Thư viện làm hết thì phần tự làm là gì? | OpenCV/Pillow/ReportLab cung cấp phép toán. Dự án tổ chức multi-trial/fallback, validation/provenance, descriptors/score/NMS, geometry/config, revision/CAS, lưu artifact, debug và luồng UI/export. Xem bảng mục7 báo cáo. |
| Vì sao cần confirmed/revision? | Góc đề xuất chỉ là nháp. Người dùng xác nhận; revision phát hiện cấu hình đổi trong lúc xử lý. Bản render và snapshot xuất phải khớp config/thứ tự đã lưu, tránh phản hồi cũ ghi đè. |
| Tại sao chỉ một worker? | Hàng đợi và khóa export ở một process;1 image worker/2 waiting. Giảm độ phức tạp cho MVP cục bộ; không được tự tăng Uvicorn workers khi không có khóa liên process. |
| Kết quả test7/7 có tốt không? | Có ích trong7 góc chụp cùng1 tài liệu; chưa đủ độc lập để suy100% cho tài liệu mới. Development6 ảnh cũng chỉ1doc. Split theo tài liệu/nội dung, không random ảnh cùng tờ qua hai tập. |
| Dùng IoU/sai góc thế nào? | IoU diện tích giao/hợp quad liên tục; góc theo matching chu kỳ/winding với nhãn trên nguồn sau EXIF. Mean và mẫu số được ghi;3ca không đủ quad phẳng giữ unlabelable, không bỏ im lặng. |
| p95/RAM đo phần nào? |35 measured/operation, loại warmup, quantile linear. Core và HTTP khác scope; HTTP không gồm upload/tải output/UI. RAM sampled working set PID thật, không phải RAM tăng riêng hoặc số đo trên phần cứng khác. |
| Vì sao freeze check báo lệch ở bản nộp? | Bản13 khóa trước đo;14 thêm phục vụ web và sửa một dòng chú thích UI. Giữ bản khóa/CSV, dùng manifest đóng gói riêng; không ghi đè freeze để giả cùng bản đã đo. |
| Nợ thuật toán giải quyết sao? | Thử epsilon cap/fit distance/cạnh yếu bằng development mới. Các gate này không đủ với khung giả hỗ trợ edge cao; cần thêm nhiều doc/cảnh mơ hồ và đặc trưng giấy–nền, rồi đối chứng. Chưa triển khai/tune theo test. |

Những điểm chưa thể trả lời bằng dữ liệu hiện có: độ chính xác trên tài liệu chưa từng thấy,
độ đọc/OCR định lượng, lỗi giữa nhiều người gán nhãn, giấy nhàu mạnh/lóa mất chữ, hiệu năng trên máy khác
và tải nhiều người. Câu trả lời đúng là **chưa đo/chưa hỗ trợ**, không biến chúng thành tính năng đã đạt.
Thông tin hành chính (ngày nộp, tên nhóm, mã sinh viên, định dạng bắt buộc) còn chờ người dùng cung cấp,
không chặn bản source/demo kỹ thuật hiện tại.
