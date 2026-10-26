# Phân tích hướng thuật toán Document Scanner từ tài liệu môn học

Ngày lập:14/10/2026; cập nhật16/10/2026. Phân biệt lý thuyết/đề xuất với các đoạn ghi rõ đã triển khai. Điều chỉnh sinh ứng viên được user chấp nhận và đã kiểm chứng ở [revision01](detection-revision-01.md); không đổi kiến trúc hoặc coi kết quả trên nhóm nhỏ là accuracy.

## 1. Phạm vi đọc và nguồn

- [Giáo trình](<Giáo trình _ Xử lý ảnh.pdf>), 308 trang: đọc mục lục và các phần liên quan trực tiếp đến bài toán, gồm nắn chỉnh/đặc trưng (trang PDF 10–12), hình thái (65, 67, 69–72), phân vùng/biên/ngưỡng (87–89, 96–118), trích rút đặc trưng và biểu diễn/mô tả biên (155–169, 171–180). Không coi việc trích text toàn bộ PDF là đã đọc kỹ toàn bộ 308 trang.
- Đọc toàn bộ [slide chương 5](<xla_Ch05 (1).pdf>), 60 trang: đặc biệt slide 6–9, 19–30, 31–40 về gián đoạn/tương đồng, gradient, thang xử lý và chiếu sáng.
- Đọc toàn bộ [slide chương 6](xla_Ch06.pdf), 63 trang: đặc biệt slide 5–19, 24–36, 48–63 về phát hiện/mô tả, chuỗi biên, đa giác và lựa chọn đặc trưng.
- Render và xem các hình ở giáo trình trang PDF 88, 97, 99, 163, 167; slide chương 5 trang 19, 35; slide chương 6 trang 17, 19, 35 để kiểm tra ý nghĩa hình/đồ thị thay vì chỉ đọc text.

Giáo trình trình bày cụ thể MPP (đa giác chu vi tối thiểu). Slide chương 6 còn trình bày xấp xỉ bằng chia đoạn. `approxPolyDP` dùng Douglas–Peucker; không gọi implementation này là thuật toán MPP.

Nguồn bổ sung để nối lý thuyết với công cụ, không thay thế tài liệu môn học:

- [OpenCV: Canny](https://docs.opencv.org/4.x/da/d22/tutorial_py_canny.html).
- [OpenCV: contour features và Douglas–Peucker](https://docs.opencv.org/4.x/dd/d49/tutorial_py_contour_features.html).
- [OpenCV: biến đổi hình học](https://docs.opencv.org/4.x/da/d6e/tutorial_py_geometric_transformations.html).

## 2. Bài toán cần giải quyết

Biên là đặc trưng quan trọng cho bước xác định trang. Toàn bộ sản phẩm còn có hiệu chỉnh hình học và cải thiện độ đọc.

| Bài toán con | Đầu vào | Đầu ra cần thiết |
|---|---|---|
| Định vị trang | Ảnh đã chuẩn hóa, có giấy và nền | Vùng trang và bốn góc theo chu kỳ, hoặc yêu cầu sửa tay |
| Hiệu chỉnh hình học | Nguồn và bốn góc xác nhận | Ảnh trang chữ nhật, không lật/xoắn |
| Cải thiện nội dung | Ảnh warp | Màu/xám/BW đọc được, giữ nét và dấu theo mode |
| Giải thích/đánh giá | Stages, config, nhãn và kết quả | Bằng chứng chọn vùng đúng và cải thiện phù hợp |

Đối tượng cần tìm trước tiên là toàn bộ trang giấy, kể cả phần lề. Vùng chứa chữ không đồng nhất với vùng giấy; cắt theo khối chữ có thể mất lề, hình, số trang hoặc ghi chú.

## 3. Phân biệt các mức biểu diễn

1. **Đáp ứng gradient:** cường độ thay đổi ở đâu, mạnh thế nào, hướng nào. Gradient vuông góc với hướng tiếp tuyến của biên.
2. **Bản đồ điểm biên:** tập pixel ứng viên sau ngưỡng/định vị. Có thể chứa chữ, bảng, vật nền, bóng và nếp gấp.
3. **Đường bao có thứ tự:** C = [(x0,y0), …, (xK−1,yK−1)]. Thứ tự giúp tính chu vi, diện tích, thay đổi hướng và xấp xỉ đa giác.
4. **Đa giác ứng viên:** rút gọn đường bao, giữ các điểm đổi hướng có ý nghĩa. Với giả định trang gần phẳng có đủ góc, tìm tứ giác lồi.
5. **Bộ mô tả:** các giá trị định lượng dùng để so sánh/xếp hạng ứng viên.
6. **Bốn điểm được xác nhận:** Q = [p0,p1,p2,p3], giữ vị trí và chiều duyệt để tính warp.

`findContours` giải quyết việc lấy đường bao từ ảnh nhị phân. Nó không tự gán ý nghĩa 'trang giấy' cho một đường bao. Thuật toán Moore trong môn học minh họa nguyên lý theo dõi biên; không mặc nhiên coi nó là implementation của findContours.

## 4. Vì sao Canny chưa đủ để chọn trang

Một tờ giấy trên bàn thường chứa nhiều chuyển tiếp cường độ: mép giấy, chữ, đường bảng, hình ảnh, đường gấp, ranh giới bóng và họa tiết bàn. Tất cả đều có thể tạo đáp ứng biên hợp lệ theo định nghĩa ảnh; chỉ một phần liên quan đến đường bao cần cắt.

Nếp gấp có thể tạo một đường dài và tương phản mạnh hơn mép giấy. Giấy trắng trên nền trắng có thể có mép rất yếu. Vì vậy, chọn pixel gradient mạnh nhất hoặc đường dài nhất không đủ xác định trang.

Phát hiện biên tạo bằng chứng cục bộ. Chọn trang cần thêm cấu trúc toàn cục: vùng lớn hợp lý, đường bao, các cạnh của cùng một hình, độ lồi và quan hệ giữa bốn đỉnh. Tờ giấy và một vật khác cùng hình tứ giác vẫn có thể mơ hồ; heuristic không có bảo đảm nhận biết ngữ nghĩa giấy trong mọi cảnh.

## 5. Hướng chính phù hợp MVP

### 5.1. Chuẩn hóa và tạo ảnh phân tích

Áp EXIF, chuyển màu đúng, giữ nguồn. Tạo ảnh nhỏ cho detection và làm trơn nhẹ ở nhánh này. Làm trơn để giảm nhiễu/chi tiết nhỏ nhưng phải giữ mép; tăng kernel không mặc nhiên cải thiện mọi ảnh.

Revision01 giữ analysis≤1200/Gaussian5 sigma0/reflect101. Đã so3/5 trên16ca;3 không tốt hơn đều nên chỉ giữ tùy chọn ablation, không tự đổi theo ảnh. Ghi gaussian_kernel để trace, không lấy blur này làm ảnh warp/render.

### 5.2. Sinh điểm biên

Giữ Canny làm ứng viên chính của kế hoạch: gradient, non-maximum suppression và hysteresis hai ngưỡng giúp tạo biên mỏng với điều kiện liên thông. Blur được thực hiện rõ ở bước tiền xử lý; không dựa vào giả định lời gọi cv2.Canny tự làm Gaussian cho chúng ta.

Preset hiện hành ở collect_candidates là revised:20/60,50/150,75/200, aperture3/L2true; đúng3trial hữu hạn, thay100/250 bằng20/60 để thử mép yếu. Baseline Gaussian5/50–150/75–200/100–250 vẫn tái hiện riêng. Khảo sát10/30 làm xuất hiện thêm vùng ăn sang bàn nên chưa chọn. Chưa chứng minh bộ ngưỡng mới tối ưu cho mọi ảnh; giữ cấu hình so sánh và các ca lỗi.

Sobel + ngưỡng là baseline phù hợp để giải thích/so sánh nguyên lý, không cần thêm một chế độ UI riêng. Canny cũng dùng thông tin gradient; không cần chạy hai detector độc lập nối tiếp để có cùng thông tin.

### 5.3. Nối hở nhỏ và lấy đường bao

Closing nhẹ trên edge map có pixel biên trắng giúp nối khoảng hở nhỏ. Kernel lớn có thể nối nhầm nét chữ, bóng hoặc vật nền. Sau đó lấy contour và giữ ứng viên theo diện tích/độ dài/điều kiện hình học.

Edge map chưa phải mask giấy hoàn chỉnh. Với đường hở hoặc biên yếu, contour có thể không bao được trang; tăng morphology quá mạnh không bảo đảm khôi phục biên thật.

Giữ closing3×3 mộtlần và RETR_LIST cho Canny; area contour/Q≥10%, cạnh≥5% cạnh ngắn, không hạ gate để nhận contour bao nét mỏng. Nếu cả3trial không có quad hợp lệ, mới chạy một nhánh vùng sáng ở mục7. Đây là fallback sinh ứng viên, khác manual fallback giao diện.

### 5.4. Xấp xỉ đa giác

Rút contour về đa giác bằng Douglas–Peucker, chọn tolerance có quan hệ với chu vi/độ phân giải. Epsilon nhỏ giữ gợn và tạo nhiều đỉnh; quá lớn có thể mất góc hoặc biến vật khác thành tứ giác.

Chỉ nhận tứ giác hợp lệ: điểm riêng biệt, không tự giao, lồi, cạnh/diện tích đủ lớn, thứ tự ổn định. Không điều chỉnh epsilon vô hạn cho đến khi mọi contour có đúng bốn đỉnh.

### 5.5. Mô tả và xếp hạng

| Thuộc tính | Câu hỏi thực tế | Lưu ý |
|---|---|---|
| Diện tích chuẩn hóa A/(WH) | Vùng có đủ lớn để là trang cần quét? | Vật nền lớn hơn giấy vẫn có thể đứng đầu |
| Chu vi, chiều dài cạnh | Đường bao có kích thước/cạnh hợp lý? | Chuẩn hóa khi so các độ phân giải |
| Bốn đỉnh, độ lồi, không tự giao | Có phù hợp giả định hình học trang gần phẳng? | Phối cảnh tạo góc xiên; không ép góc 90° |
| Hỗ trợ biên dọc cạnh | Các cạnh đa giác có bằng chứng trên ảnh? | Đo trên edges trước closing; xem từng cạnh khi phân tích lỗi |
| Khớp contour và đa giác | Rút gọn có còn đại diện đúng đường bao? | Khớp diện tích là heuristic hiện có; có thể thử thêm sai số khoảng cách khi cần |
| Khoảng cách với viền ảnh | Có đang lấy khung ảnh hoặc nền? | Trang thực cũng có thể sát mép; đây chỉ là bằng chứng phụ |

Scoring hiện có là heuristic thiết kế của dự án. Công thức/trọng số/ngưỡng phải thử trên development, không phải kết luận suy ra từ giáo trình. Có thể xem việc cải thiện hỗ trợ từng cạnh hoặc sai số fit là đề xuất thí nghiệm, chưa tự thay schema/implementation.

Giấy chữ nhật trong thực tế được chiếu thành tứ giác: góc vuông và cạnh song song của giấy không nhất thiết giữ trong ảnh. Độ gần hình chữ nhật trong hệ tọa độ ảnh không nên là điều kiện cứng.

### 5.5.1. Quy ước mô tả để dùng khi triển khai

Mô tả biên là một phần của MVP, nằm giữa việc tạo contour/đa giác và quyết định chọn ứng viên. Dùng bộ thuộc tính hình học gọn phục vụ định vị trang; chưa cần dùng mã chuỗi/Fourier làm bộ phân loại.

Tách ba nhóm thông tin trong kết quả nội bộ và debug:

1. **Biểu diễn:** contour có thứ tự và đa giác Q, gồm tọa độ thực của các điểm trên ảnh phân tích. Giữ chúng để overlay, xấp xỉ và ánh xạ về nguồn.
2. **Mô tả hình học biên:** các số/thuộc tính được tính từ contour hoặc Q.
3. **Đặc trưng bổ sung:** diện tích vùng, bằng chứng biên trên ảnh và vị trí tương đối với khung ảnh để xếp hạng.

Các trường nội bộ dưới đây đã có trong ContourCandidate/CandidateDescription ở MVP05.03–04 ngày15/10/2026; không phải hợp đồng HTTP đã triển khai. Chốt ánh xạ vào schema ở MVP07.01 và debug ở MVP09.06.

| Nhóm | Trường dự kiến | Cách tính / đơn vị | Vai trò |
|---|---|---|---|
| Biên | `contour_perimeter_px` | Tổng khoảng cách các điểm liên tiếp, gồm đoạn đóng | Chu vi contour |
| Biên | `polygon_vertex_count` | Số đỉnh sau xấp xỉ, trước lọc tứ giác | Giải thích vì sao ứng viên được nhận/loại |
| Biên | `quad_edge_lengths_px` | Bốn độ dài cạnh theo chu kỳ | Kiểm tra cạnh quá ngắn hoặc suy biến |
| Biên | `quad_turn_angles_rad` | Bốn góc đổi hướng giữa cạnh trước và cạnh sau | Giải thích cấu trúc góc; không ép 90° |
| Biên | `is_convex`, `self_intersects` | Kết quả kiểm tra hình học dùng chung | Lọc tứ giác lõm/tự giao |
| Vùng | `area_ratio` | A(Q)/(Wa·Ha) | Kích thước vùng giấy ứng viên so với ảnh |
| Vùng/fit | `fit_area_ratio` | min(A(C),A(Q))/max(A(C),A(Q)) | Độ khớp diện tích theo scoring đã chốt |
| Biên + ảnh | `edge_support_per_side` | Bốn tỷ lệ mẫu cạnh có edge lân cận trên Canny trước closing | Nhìn ra cạnh nào thiếu bằng chứng |
| Biên + ảnh | `edge_support` | Tổng mẫu được hỗ trợ / tổng mẫu trên cả bốn cạnh | Thành phần e của scoring hiện hành |
| Ngữ cảnh ảnh | `border_penalty` | Tỷ lệ mẫu cạnh trong dải sát mép ảnh | Thành phần b, hạn chế chọn khung ảnh |

Các độ dài tính bằng pixel trên ảnh phân tích. Nếu dùng độ dài để so các kích thước khác nhau, chuẩn hóa theo đường chéo D = sqrt((Wa−1)²+(Ha−1)²); luôn ghi dimensions tương ứng. Tọa độ đầu ra vẫn dùng quy ước normalized của dự án.

Góc đổi hướng tại pi có thể tính từ e trước = pi−p(i−1) và e sau = p(i+1)−pi, bằng atan2(cross(e trước,e sau), dot(e trước,e sau)), với chỉ số vòng tròn. Dấu phụ thuộc quy ước trục/chiều duyệt; app dùng x sang phải, y xuống. Geometry validation cần được dùng lại, không tự sắp lại handle tay.

Chỉ tính các đặc trưng bốn cạnh sau khi có tứ giác hợp lệ. Contour/đa giác suy biến phải trả lý do loại; không chia cho diện tích/chu vi bằng 0 hoặc đưa NaN/Infinity vào debug.

Với ni mẫu trên cạnh i và mi mẫu được edge hỗ trợ, ei = mi/ni. Giữ e tổng = sum(mi)/sum(ni), không lấy trung bình không trọng số của bốn ei khi số mẫu từng cạnh khác nhau. Dải tìm edge và mẫu cách khoảng 2 px theo ảnh phân tích là preset cần kiểm chứng, không phải hằng số tối ưu phổ quát.

Quy ước hiện thực MVP05.04: ni=max(2,ceil(Li/2)+1), linspace cả hai đầu nên khoảng mẫu≤2px; góc chung được tính ở cả hai cạnh kề. Một mẫu được hỗ trợ khi tâm pixel trắng raw Canny cùng trial cách Euclid≤2px. b dùng cùng mẫu, cách mép ảnh≤2px. Giữ ni/mi từng cạnh để đối chiếu e; đây là chi tiết preset triển khai, không gán là công thức lấy từ giáo trình. Test đối chiếu khoảng cách toàn bộ white pixels trên fixture nhỏ, gồm cạnh nghiêng và ảnh chỉ có một pixel biên.

**Giữ scoring ban đầu:** S = clip(0.45a + 0.35e + 0.20f − 0.15b, 0, 1), với a/e/f/b tương ứng area_ratio/edge_support/fit_area_ratio/border_penalty. Chu vi, cạnh, góc và tính lồi phục vụ lọc/giải thích; không tự thêm trọng số vào score.

Sai số khoảng cách contour–đa giác (ví dụ khoảng cách từ điểm contour đến cạnh gần nhất, chuẩn hóa theo D) là mô tả hình học có thể thử thêm. Phần này chưa bắt buộc tính hoặc đưa vào score của baseline; chỉ bổ sung khi thí nghiệm trên development chứng minh lợi ích.

### 5.5.2. Nghiệm thu phần mô tả biên

- Một ứng viên được chọn có contour/Q overlay và bộ mô tả số tương ứng; nguồn/run/trial/dimensions rõ.
- Giải thích được cái nào là biểu diễn, mô tả biên, đặc trưng vùng và bằng chứng ảnh; diện tích không được gọi là mô tả biên thuần túy.
- Rectangle, diamond và các quad hợp lệ đều được mô tả mà không ép góc vuông; self-intersection/concave/degenerate có lý do loại.
- Với fixture cố định, thay edge map quanh một cạnh phải thay hỗ trợ cạnh đó và e tổng đúng; closing không tự tạo bằng chứng edge cho score.
- Đổi số mẫu trên các cạnh vẫn tính e tổng theo đúng số mẫu; các giá trị phải hữu hạn và các tỷ lệ nằm trong [0,1].
- UI học thuật hiện các số đã tính thật cùng overlay và thành phần score; không dựng số giả hoặc phần trăm accuracy.

### 5.5.3. Nối vào checklist hiện hành

| Task | Đầu ra liên quan |
|---|---|
| MVP05.03 | Biểu diễn contour có thứ tự, Q và kết quả kiểm tra hình học |
| MVP05.04 | Bộ mô tả/đặc trưng của ứng viên và scoring từ a/e/f/b |
| MVP05.05 | Polygon IoU/NMS loại các đề xuất trùng, giữ nguyên bằng chứng của ứng viên thắng |
| MVP05.06 | Dùng điểm heuristic chọn đề xuất/cảnh báo/yêu cầu chỉnh tay, không tự xác nhận |
| MVP05.07 | Debug lưu các số, nguồn gốc và overlay tương ứng |
| MVP09.07 | PipelineViewer hiện mô tả của ứng viên được chọn |
| MVP09.08 | Giải thích sự khác nhau giữa phát hiện, biểu diễn, mô tả và lựa chọn |
| MVP13.04 | CSV/metadata để phân tích vì sao scoring chọn đúng/sai so với largest contour |

Đây là việc làm rõ nghiệm thu các task đã có. Giữ110ID task chính/5task tùy chọn; trạng thái tại tasks/todo.md. MVP05.01–06 hiện có nguồn → analysis1200/Gaussian5 → revised3Canny và tối đa1Otsu → contour/Q → mô tả/score → polygon NMS → đề xuất hoặc manual_required. NMS so diện tích giao/hợp, loại IoU>.95 theo score giảm dần, không sửa tọa độ hoặc trộn raw support giữa trial. S≥.60 đề xuất; .40≤S<.60 cảnh báo; thấp hơn/khôngquad thì result.corners=null. Mọi kết quả confirmed=false. Phân loại này là quy ước dự án, không phải công thức nhận biết giấy được chứng minh trong giáo trình.

Tại mốc05.06:140 tests tập trung/716backend đạt, 7ca chạy kiểm chứng. img_004 cảnh báo S.468352 nhưng góc vẫn ăn bàn; anhtestnew đề xuất S.634709; img_001 manual_required; khung giả vẫn có thể điểm cao và chọn sai. Checkpoint05-C1/C2 đạt, timing/debug05.07 và batch05.08 còn chờ. Không coi candidate count/score/status là accuracy. Chưa thêm ngưỡng hỗ trợ từng cạnh hoặc giới hạn epsilon mới: cần đối chứng development trước điều chỉnh, giữ ca sai công khai. Xem [hợp đồng lựa chọn](image-contract.md), [progress](progress.md) và [revision01](detection-revision-01.md).

Tại mốc05.08/AUX05.02: debug/timing và batch baseline/revised đã có, 733backend đạt. Cổng05 đạt theo MVP ban đầu; [audit05](audit-phase-05.md) đối chiếu đủ8task,32runs/104trial và nợtask03–04. Debug giữ đúng trial/raw support/mask/đơn vị, khôngquadvẽgiả. img_004/006 vẫn ăn bàn; frame vẫn có thể chọn sai điểm cao. Đã thử đường manualdraft→warp/render trên img_001 bằng CLI có sẵn, chưa UI/GT/xác nhận thật.

Hướng thử tiếp, **chưa triển khai đổi thuật toán**: giới hạn epsilon theo kích thước ảnh/đường chéo hoặc kiểm fit distance chuẩn hóa; cảnh báo từng cạnh thiếu raw support; đối chứng màu/chiếu sáng khi Otsu gộp nền. f diện tích vẫn không phải spatial fit. Khung giả có mọi cạnh mạnh và fit nhỏ nên không thể chữa chỉ bằng hai gate đó; cần đánh giá cảnh mơ hồ/vùng lồng nhau và giữ chọn tay. Không chốt ngưỡng mới từ sáu ảnh cùng một tài liệu; thu thêm development/GT và chạy từng biến riêng trước test. Chi tiết số đo/tiêu chí ở audit05.

### 5.5.4. Đối chiếu hình học đã triển khai — MVP03.03–MVP03.04

Ngày 14/10/2026, đọc lại giáo trình mục 6.2.3 (trang PDF 163–164, hình 6.8 về đỉnh lồi/lõm và chiều đi trên biên), slide chương 6 trang 17–19 và 35, slide chương 5 trang 6–8; render/xem giáo trình trang 164 và slide 6 trang 17–18. Đây là cơ sở cho biểu diễn đa giác có thứ tự, điểm đổi hướng và phân biệt đặc trưng biên/vùng. Không coi việc trích text toàn PDF là đã đọc kỹ toàn bộ giáo trình. MPP của giáo trình và chia đoạn của slide là thuật toán xấp xỉ biên; hai task hình học này chưa hiện thực MPP/Douglas–Peucker hoặc detector.

`validate_quad` hiện kiểm tra diện tích có dấu bằng shoelace, giao cạnh đối bằng orientation/bounding box, độ lồi bằng dấu cross liên tiếp và winding theo hệ y xuống. `order_auto_corners` sắp quanh trung bình bốn điểm bằng atan2, chuẩn hóa chiều và xoay chu kỳ tới min(x+y), tie y/x trên pixel nguồn. Các phép kiểm tra/sắp này cụ thể hóa đặc tả dự án mục 9.9 và image-contract; không gán tên MPP hoặc nói rằng các công thức/ngưỡng đều được trích từ giáo trình. Shoelace là đặc trưng vùng; tính lồi/đổi hướng thuộc hình học biên. Không dùng số Euler/compactness thay cho kiểm tra cạnh tự giao của một tứ giác.

Mọi thao tác tay giữ handle/thứ tự; auto proposal mới được sắp. Vùng nguồn không bị ép 90° hoặc song song. Ngưỡng suy biến theo D và D² ghi tại [image-contract mục 4](image-contract.md), là baseline triển khai, chưa phải đánh giá accuracy. Đã kiểm chứng 171 ca geometry/318 backend; detector, bộ mô tả debug và warp vẫn chờ task tương ứng. Bằng chứng và các ca đối kháng tại [progress](progress.md).

### 5.6. Xác nhận và warp từ nguồn

Người dùng xác nhận bốn góc, sau đó tính homography và lấy mẫu từ nguồn đầy đủ. Không dùng ảnh detection đã thu nhỏ/làm mờ để xuất. Tỷ lệ theo độ dài cạnh là ước lượng, không tự suy ra đúng khổ giấy vật lý.

MVP06.01–03 đã nối pipeline **offline để tạo bản nháp**: normalize → detector hoặc góc tay → source warp → enhancement/rotation → full/preview/config/stages. Auto không tự xác nhận; config góc tay giữ thứ tự và không chạy sorter. Khi manual_required không lấy góc diagnostic hoặc dựng full giả. HTTP/UI xác nhận và revision vẫn là phần sau. Stage prepared_gray của BW được lấy ngay trong dispatcher sau denoise/contrast, chính là input của threshold; khác gray/blur phân tích của detector. Preview lấy từ full sau rotation, BW preview được có gray vì nội suy, không threshold lại. Checkpoint06-C1 và bằng chứng mốc03 ở [progress](progress.md).

MVP06.04 đã tính histogram h(k)=số pixel prepared_gray bằng k, k=0..255; tổng256bin=N=width×height. Dùng hàm thư viện OpenCV calcHist trên full gray sau lọc/CLAHE, trước threshold/xoay, không mask/resize/chuẩn hóa xác suất. Nếu cần công thức Otsu, p(k)=h(k)/N là bước suy ra riêng; counts không phải p(k). Otsu đi kèm actual t toàn cục; Adaptive Gaussian vẫn là ngưỡng cục bộ theo block/C, histogram toàn ảnh không biến nó thành global threshold. Metadata gắn hash PNG/kích thước gray của cùng lần chạy. Color/Gray không threshold nên trường này null; đây là lựa chọn tên/ý nghĩa dữ liệu, không phải hai mode không thể có histogram trong lý thuyết. [Hợp đồng mục11.2](image-contract.md#112-histogram-trước-threshold--mvp0604), [OpenCV histogram](https://docs.opencv.org/4.x/d1/db7/tutorial_py_histogram_begins.html). Mốc04 có794tests và hai lượt img_004 kiểm; không đọc lại PDF hay sửa detector, dùng phân tích và kiểm chứng PDF đã ghi trước đó.

MVP06.05–06/AUX06.01 đã nghiệm thu M1 và rà6task:800backendtests,10cặp20CLIrun/230PNG,8detection/28trial, source/fixtures giữhash; so pixels/config/stages/histogram chỉ bỏ run_id/timing, kiểm phép biến đổi từsource. [M1](milestone-m1.md) có lệnh chạy lại và giới hạn, [audit06](audit-phase-06.md) có ma trận6task. Không sửa lý thuyết/preset/thuật toán để đạt kiểm tái lập; img_004 vẫnănbàn, homography khôngdewarp, score khôngaccuracy. Tái lập cùngmáy/dependencies không chứng nhận góc đúng hoặc tính tất định mọi môi trường. HistogramUI/OPT-B và API/UI/confirmed-revision/storage/PDF cònchờ; tiếp theo07.01.

Giai đoạn03 đã nghiệm thu lõi offline ngày14/10/2026: estimate_warp_size → compute_homography → warp_document và CLI geometry_demo; công thức/đơn vị theo đặc tả9.10 và [image-contract mục6](image-contract.md). H source→đích3×3 từ bốn cặp điểm, OpenCV lấy mẫu ngược và nội suy song tuyến tính INTER_LINEAR; BORDER_REPLICATE giữ biên. Kiểm tra geometry/H trước sampler; không làm tròn source corners thành số nguyên, không dùng nguồn analysis. Nguồn cạnh≥32767 được lấy mẫu qua ROI gốc và H dịch hệ tọa độ, không resize để né giới hạnCV. Giao diện xác nhận và pipeline filters/revision còn chờ; không coi lõi warp là ứng dụng scan hoàn chỉnh. Tham chiếu [OpenCV transformations](https://docs.opencv.org/4.x/da/d6e/tutorial_py_geometric_transformations.html) đã được đối chiếu. Bằng chứng216geometry/8demoCLI/371backend và ma trận tám task tại [audit03](audit-phase-03.md); màu/diamond/near-collinear/subpixel đều có kiểm chứng thực.

## 6. Vai trò các cách biểu diễn khác trong chương 6

| Cách biểu diễn/mô tả | Vai trò với đề tài |
|---|---|
| Chuỗi tọa độ contour | Biểu diễn chính để giữ vị trí, thứ tự và hình học |
| Đa giác | Biểu diễn chính để lấy bốn cạnh/góc và warp |
| Mã chuỗi Freeman | Minh họa theo dõi biên, hướng và ảnh hưởng lấy mẫu; không cần làm định dạng lõi của app |
| Biên dạng 1D, số hình dạng | Có thể minh họa mô tả hình dạng; chưa cần cho định vị bốn góc |
| Fourier biên | Hữu ích mô tả/so hình dạng; làm trơn quá mạnh có thể làm mất góc; chưa cần cho MVP |
| Hu/compactness/moments | Thuộc tính bổ sung nếu có thí nghiệm chứng minh lợi ích; không nhận biết giấy chỉ từ một scalar |
| Harris | Phát hiện góc cục bộ; chữ/bảng cũng có nhiều góc; chưa đủ chọn bốn góc trang |
| SIFT/HOG/LBP/PCA | Phù hợp những nhiệm vụ mô tả/khớp/phân loại khác; hiện không có nhu cầu so mẫu hay học bộ phân loại để bắt buộc chúng |
| Skeleton | Phù hợp cấu trúc nét/nhánh như chữ hoặc mạch máu; không trực tiếp phục vụ đường bao tứ giác trang |

Bất biến dịch/quay/tỷ lệ không mặc nhiên là bất biến phối cảnh. Với cropping/warp, tọa độ góc là thông tin cần giữ; không chuẩn hóa loại mất vị trí rồi chỉ giữ một véc tơ phân loại.

Hai lưu ý khi đối chiếu công thức: giáo trình dùng compactness P²/A, slide dùng P²/(4πA), khác hệ số; phải chọn một quy ước khi báo cáo. Một số đoạn giáo trình chọn x theo hàng và y theo cột; app đã chốt x sang phải, y xuống, nên kiểm tra hướng và dấu tích có hướng theo quy ước app.

## 7. Hướng dự phòng dựa trên vùng

Chương5 cung cấp nguyên lý tương đồng bên cạnh gián đoạn. Theo điều chỉnh user chấp nhận15/10/2026, đã hiện thực nhánh Otsu vùng sáng dự phòng khi cả3Canny không có quad: analysis blurred → THRESH_BINARY|THRESH_OTSU → contour ngoài thành phần trắng bằng RETR_EXTERNAL/CHAIN_APPROX_SIMPLE → cùng Douglas–Peucker/geometry/scoring. Giữ raw mask; biên lỗ bên trong được bỏ ở bước truy contour ngoài, không thêm hole filling/closing lớn. Mask toàn0/toàn255 báo UNIFORM_REGION_MASK, không tự coi toàn khung là giấy.

Đây là một cách sinh ứng viên khác. Chữ làm vùng giấy không hoàn toàn đồng nhất; lóa/bóng hoặc nền cùng sáng có thể làm threshold sai. Không dùng Otsu trên toàn ảnh như một bảo đảm luôn tìm được giấy. Nếu grayscale làm mất phân biệt màu, nên thử thông tin màu trên nhóm lỗi trước khi thêm một pipeline màu vào app.

RegionTrial giữ mask, actual otsu_threshold, raw Canny20/60 copy và support_trial_id cùngkernel/dimensions. e vẫn đo raw Canny, không đo boundary mask để tự nâng score. anhtestnew được Canny20/60 khôi phục; img_004/img_006 có ứng viên Otsu nhưng góc trên trái lấn sang bàn, score .468352/.448517. Chưa đánh giá nhánh màu hoặc Hough; không tuyên bố nhánh vùng đã sửa mọi ca thiếu mép. Phân biệt Otsu tìm vùng giấy trước warp với Otsu tách chữ sau warp ở mục8. [OpenCV thresholding](https://docs.opencv.org/4.x/d7/d4d/tutorial_py_thresholding.html), [chi tiết quyết định/kiểm chứng](detection-revision-01.md).

Đối chiếu lại trực tiếp giáo trình/slide theo yêu cầu user15/10/2026: [kiểm chứng img_004](verification-img004-theory.md). Otsu tính độc lập theo giáo trình(5-62)–(5-64) cho102 và mask khớp từng pixel với OpenCV. Bàn109 và giấy186 cùng foreground/thành phần26; contour P≈5417px khiến epsilon.03P≈162.5px, rút13/10đỉnh xuống4 và cho phép bỏ nhiều chi tiết vùng lấy nhầm. Cạnh trên chỉ7/245mẫu rawsupport. Kết luận: đúng phép Otsu nhưng tiêu chí phân tách/kiểm xấp xỉ của baseline chưa đủ cho ảnh này; geometry/diện tích không chứng nhận giấy. Nhánh threshold+contour không phải region-growing cóseed; Douglas–Peucker không phảiMPP. Chưa đổi preset/code hoặc tự thêm descriptor sau lượt đối chiếu này.

Chưa thêm region-growing/K-means/watershed/graph-cut vào MVP theo tên gọi. Chỉ mở rộng khi quan sát lỗi của baseline và chứng minh phương pháp bổ sung giải quyết đúng lỗi đó. Manual fallback vẫn là phương án hoàn thành tác vụ trong các ca mơ hồ.

## 8. Nội dung sau warp và giấy gấp/nhàu

Sau khi chọn trang, mục tiêu chuyển sang độ đọc. Phân ngưỡng lúc này tách chữ với nền giấy, khác việc tách giấy với mặt bàn. Canny không phải output dùng để thay chữ trong ảnh xuất.

- Otsu là baseline cho mức sáng đủ đều; Adaptive dùng ngưỡng theo lân cận khi chiếu sáng đổi theo vị trí.
- Gaussian/Median phải cân nhắc mất nét/dấu nhỏ. Chỉ lọc nhẹ và cho tắt theo mode.
- Hình thái ở detection dùng biên trắng là foreground; ảnh BW cuối dùng chữ đen, giấy trắng. Áp cùng một phép closing không kiểm tra polarity/mục đích có thể làm mất nét.
- Màu/xám giữ highlight và sắc độ mà nhị phân hóa bỏ đi.

| Trường hợp giấy | Ảnh hưởng chính | Kỳ vọng xử lý |
|---|---|---|
| Có vết gấp nhưng đã trải phẳng | Đường gấp/bóng là biên nội bộ | Chọn đường bao ngoài bằng cấu trúc; thử ngưỡng cục bộ cho độ đọc |
| Bóng mềm, chữ còn thông tin | Nền không đều sáng | Adaptive; làm đều sáng là mở rộng đã dự kiến, cần so mất nét |
| Nhàu làm dòng chữ cong/co giãn | Biến dạng không phẳng, thay đổi cục bộ | Homography chỉ sửa tổng thể; dewarping ngoài MVP |
| Góc giấy gập/che hoặc chữ lóa/mất | Thiếu thông tin hình học/nội dung | Sửa tay nếu còn đủ căn cứ; ưu tiên trải giấy/chụp lại; không khôi phục chữ giả |

## 9. Thí nghiệm trước khi chốt tham số detector

1. Dùng nhóm development có nền tương phản, nền nhiều họa tiết, giấy cùng sáng nền, ảnh có khung/bảng, vết gấp/bóng và nhàu rõ. Thu/gán nhãn đúng nguồn EXIF.
2. Đánh dấu đường bao thật và bốn góc, không coi dòng chữ hoặc mép bóng là ground truth trang.
3. So baseline Sobel+ngưỡng với Canny cùng tiền xử lý; quan sát biên yếu/đứt và biên nội bộ.
4. Giữ detector cố định để so không closing/closing nhẹ; ghi ca nối nhầm.
5. Giữ candidate generation cố định để so largest contour với scoring và thử epsilon có giới hạn.
6. Nếu nhóm lỗi phù hợp giả định vùng, thí nghiệm nhánh threshold/mask như nguồn candidate bổ sung; không đưa vào app khi chưa có bằng chứng.
7. Đo IoU/corner error/tỷ lệ manual và thời gian; ảnh biên nhìn đẹp chưa chứng minh chọn đúng trang.
8. Với Otsu/Adaptive/CLAHE, giữ cùng vùng cắt và đánh giá nét/dấu/nền/highlight để không trộn lỗi detector vào chất lượng render.

Không tune bằng test. Không khẳng định một phương pháp tốt hơn trên ảnh của dự án khi chưa có dữ liệu. Các so sánh bổ sung ở đây là hướng nghiên cứu, chưa thay bảng task hoặc tăng phạm vi được duyệt.

## 10. Hướng làm việc tiếp theo

Khi chuyển sang xử lý ảnh, dùng phân tích này để thống nhất bài toán và thử lõi trên ảnh mẫu. Tiến độ thực hiện theo tasks/todo.md; không tích task xử lý ảnh chỉ vì đã đọc tài liệu.

Hướng chính đề xuất: điểm biên → contour có thứ tự → đa giác ứng viên → mô tả/xếp hạng → bốn góc xác nhận → warp từ nguồn → cải thiện nội dung. Điều cần kiểm chứng sớm nhất là khả năng phân biệt đường bao trang với các biên gây nhiễu trong ảnh thật.
