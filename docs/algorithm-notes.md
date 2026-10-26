# Ghi chú thuật toán và độ đọc ban đầu — giai đoạn 04

Tài liệu có bổ sung hiện hành ở cuối: MVP09.07–08 ngày18/10/2026, giải thích stage trên UI và đối chiếu PDF. Các số đo của giai đoạn04–06 bên dưới giữ nguyên ngữ cảnh lịch sử.

Ngày: 14/10/2026. Nghiệm thu MVP04.07, dùng lõi thật và CLI [enhancement_demo.py](../experiments/enhancement_demo.py). Đây là quan sát development và ảnh tổng hợp, chưa phải kết quả test cuối hoặc accuracy. Nguồn yêu cầu: [MVP](MVP_Pham_Vi_Va_Ke_Hoach_4_Tuan.md), [hợp đồng ảnh](image-contract.md), đặc tả gốc9.11–9.15 và [phân tích hướng thuật toán](Phan_Tich_Huong_Thuat_Toan_Tu_Tai_Lieu.md).

## Luồng đã chạy

JPEG/PNG gốc → chuẩn hóa EXIF/alpha/BGR một lần → quad tay trên nguồn chuẩn hóa → homography/warp full → lọc → mode/contrast/threshold → xoay90 → full render. Comparison thu nhỏ từ full render; đánh giá nét chữ dùng PNG full và crop giữ nguyên pixel, không dùng comparison làm nguồn xuất.

`enhance_document(warped_bgr, config, source_size=(W,H))` revalidate toàn config với dimensions warp thật trước lọc. Trả EnhancementResult gồm image, effective_config frozen và otsu_threshold thực hoặc null. Corners vẫn normalized theo nguồn sau EXIF, không đổi theo rotation. Dispatcher nhận ảnh đã warp; service sau này chịu trách nhiệm confirmed/revision, không suy ra một ảnh BGR bất kỳ là đúng vùng trang.

## Thuật toán cần giải thích khi bảo vệ

| Bước | Ý nghĩa | Lợi/hại phải hiểu |
|---|---|---|
| Median3/5 | Thay pixel theo trung vị lân cận, từng kênh | Có thể loại chấm rời và nét/dấu nhỏ; không mặc định tốt cho mọi chữ |
| Gaussian3/5 | Trung bình có trọng số theo khoảng cách, sigma0 của OpenCV | Giảm nhiễu và làm mềm biên/nét; lọc trong nhánh render riêng detection |
| BGR2GRAY | Y≈0.114B+0.587G+0.299R | Giữ độ sáng nhưng mất hue của highlight; không lấy trung bình ba kênh |
| CLAHE | Histogram cục bộ, clip limit, nội suy giữa các tile | Tăng tương phản, có thể làm nổi vân giấy/ô ly/nhiễu; chỉ gray theo MVP |
| Otsu | Tìm t tối đa hóa ω0ω1(μ0−μ1)² từ histogram | Một ngưỡng toàn trang, dễ làm đen nền có bóng; lưu t thực |
| Adaptive Gaussian | T(x,y)=trung bình Gaussian trong block−C | Theo sáng cục bộ, vẫn có thể giữ nền ô ly hoặc mất nét nhạt |
| THRESH_BINARY | I≤T→0, I>T→255 | Chữ đen/nền trắng trên giấy thông thường; mất màu/sắc độ |
| Rotate90 | Đổi vị trí pixel theo góc90/180/270 chiều kim đồng hồ | Không nội suy; 90/270 đổi W/H, không đổi corners nguồn |

OpenCV thực hiện các phép lọc/CLAHE/Otsu/Adaptive/rotate trong lõi hiện tại; dự án chưa tự viết lại Otsu hoặc histogram minh họa của OPT-B. Việc hiểu công thức và giải thích ca thất bại vẫn cần cho bảo vệ. Tham chiếu chính: [filtering](https://docs.opencv.org/4.x/d4/d86/group__imgproc__filter.html), [CLAHE](https://docs.opencv.org/4.x/d5/daf/tutorial_py_histogram_equalization.html), [thresholding](https://docs.opencv.org/4.x/d7/d4d/tutorial_py_thresholding.html), [adaptiveThreshold](https://docs.opencv.org/4.x/d7/d1b/group__imgproc__misc.html), [rotate](https://docs.opencv.org/4.x/d2/de8/group__core__array.html).

## Mốc preset khởi đầu — đã giữ và khóa ở MVP13.06 bên dưới

| Mode | Lọc | Contrast | Threshold | Khi cân nhắc |
|---|---|---|---|---|
| Color | None | None, inactive | Inactive | Highlight/màu giấy/ảnh hoặc muốn giữ nét gốc sau warp |
| Gray | None | CLAHE clip2, grid8×8 tile, có thể tắt | Inactive | Muốn bỏ màu nhưng giữ sắc độ; thử tắt CLAHE khi vân nền nổi mạnh |
| BW | Median3 | None | Adaptive31/C10 | Chữ tối trên giấy, sáng không đều; so với None khi dấu/nét nhỏ bị mất |
| BW Otsu để so | Median3 | None | Otsu | Sáng khá đều, histogram tách chữ/nền; không dùng mặc định cho bóng mạnh |

Block Adaptive phải lẻ3..151 và≤cạnhngắn; C nguyên−20..30. Tăng C hạ ngưỡng và làm nhiều pixel trắng hơn; có thể xóa nét nhạt. Ảnh nhỏ không phù hợp báo INVALID_CONFIG để chỉnh lựa chọn, không tự clamp/fallback. Color giữ từng pixel **sau lọc**; preset None mới bằng warp nguyên. Không đổi preset dựa trên một tờ giấy development.

## Ảnh đã chạy và quan sát trực tiếp

Tất cả outputs dưới đây local/ignored tại experiments/results/, gồm source/overlay/warp, bốn full renders, comparison và metadata effective_config/inactive/otsu_threshold/hash/dimensions. Quad tay dưới đây là lựa chọn thử gần đúng, chưa có annotation ground truth. Hai ảnh thật img_003/img_004 cùng doc_01 do user xác nhận, đều development; không là hai tài liệu độc lập và không dùng test để tune.

| Run | Input và warp W×H | Otsu t thực | Quan sát full render/crop |
|---|---|---|---|
| mvp04-07-shadow | img_003, shadow_strong;899×1288 |147|Color/Gray giữ chữ và sắc độ trong vùng bóng. Otsu che phần lớn chữ bên trái bằng nền đen; Adaptive giữ nhiều nội dung ở đó nhưng nét/dấu nhỏ có thể đứt và ô ly vẫn đen |
| mvp04-07-even | img_004, nhãn even_light;1116×1228 |172|Ảnh vẫn có gradient sáng phía phải; Otsu làm đen vùng phải. Gray làm nổi ô ly/vân nền; Adaptive giữ vùng chữ rộng hơn nhưng không loại nền ô ly |
| mvp04-07-shadow-none | Cùng img_003/quad, denoiseNone và Gray CLAHEoff;899×1288 |147|Không lọc giữ chi tiết khác với Median3, không chữa bóngglobal củaOtsu. Gray raw giữ sắc độ, không tăng tương phản như GrayCLAHE; không có lựa chọn luôn tốt hơn |
| mvp04-07-vietnamese-highlight | Synthetic chữ có dấu/highlight vàng;639×299 |214|Color giữ vàng, Gray mất hue; BW mất màu highlight, Adaptive vẫn thấy hàng chữ/dấu, Otsu làm đen một phần nền gradient. Không kết luận mọi dấu được bảo toàn trên ảnh thật |
| mvp04-07-thin-strokes | Synthetic Aa123/nét1pixel/chấm;259×179 |209|Sau warp, BWAdaptive vẫn thấy chữ/nét trong ví dụ này; BWOtsu làm đứt/mất phần chữA. Kết quả có ảnh hưởng của nội suy warp, không mâu thuẫn ca Median trực tiếp xóa nét1pixel ở04.02 |

Quad normalized sử dụng theo nguồn sau EXIF1536×2048:

- img_003: `[[0.348,0.260],[0.806,0.297],[0.681,0.919],[0.116,0.804]]`.
- img_004: `[[0.281,0.316],[0.728,0.313],[0.866,0.904],[0.139,0.900]]`.

Đã xem overlay img_003, toàn trang và text_full_resolution.png của cả hai ảnh thật cùng bản None. Crop lấy x từ10%..99%, y19%..43% của full render, giữ nguyên pixel; crop là tài liệu kiểm tra bổ sung, không nằm trong metadata CLI. Ảnh output giữ BGR/RGB với Color và một kênh L với Gray/BW. Cả ba mode bắt đầu cùng warp, không lọc chồng lên ảnh mode trước.

Thực nghiệm kiểm soát04.04–05 còn có ảnh sángđều/bóng tổng hợp cùng chữ: Otsu t182/t155; Adaptive31/C10 giữ nềntrắng ở vùng Otsulàmđen. Block31→51/C10 khác253pixel; C5→20/block31 khác1338pixel, C20 làm đứt nét nhạt. Đây là số pixel khác nhau, không phải accuracy.

## Cách chạy lại

Từ root, bằng backend venv và một thư mục đầu ra **mới**:

```powershell
& .\backend\.venv\Scripts\python.exe experiments/enhancement_demo.py fixtures/corners_rgb.png --output-dir experiments/results/my-modes
$photo = (Import-Csv experiments/dataset_manifest.csv | Where-Object image_id -eq 'img_003').source_path
& .\backend\.venv\Scripts\python.exe experiments/enhancement_demo.py $photo --corners '[[0.348,0.260],[0.806,0.297],[0.681,0.919],[0.116,0.804]]' --output-dir experiments/results/my-shadow
```

Đổi hướng bằng --rotation0/90/180/270; --denoise none/median/gaussian ghi đè lọc của cả bốn nhánh với kernel3; --no-gray-clahe tắt CLAHE nhánhGray. Ngưỡng/block/C còn lại theo full preset được ghi trongmetadata. CLI lỗi nếu bất kỳ nhánh không hợp lệ, không bỏ qua Adaptive trên ảnh nhỏ để báo thành công. Tất cả ảnh hoàn thành trước khi ghi tệp; ghi exclusive, metadata cuối. CLI là minh họa offline/draft, không tự confirmed hoặc export tài liệu trong app.

## 15/10/2026 — Ảnh phân tích, Canny và closing (MVP05.01–02)

Nhánh mới bắt đầu từ **nguồn sau EXIF**, khác với nhánh cải thiện ảnh sau warp ở giai đoạn04. `prepare_analysis` thu cạnh dài về tối đa1200, không upscale; tạo BGR analysis, gray và Gaussian5×5/sigma0/reflect101 thành các stages riêng. `analysis_size` là kích thước thật sau half-up; `to_source` đi qua normalized bằng W−1/H−1 của hai ảnh. Ví dụ nguồn2000×1001 → analysis1200×601, nên không ánh xạ bằng cách chia cả hai trục cho r=0.6. Cạnh analysis<2 trả ANALYSIS_TOO_SMALL, không ép chiều để làm sai aspect.

`create_edge_trials(analysis.blurred)` chạy đúng ba preset Canny50/150,75/200,100/250, aperture3/L2gradient=true. Mỗi trial có ID ổn định, thresholds, edges raw và closed; closing dùng kernel chữ nhật3×3 một lần. Giữ border morphology trung tính mặc định OpenCV. Không blur thêm trong Canny helper, không thay source hoặc nhánh render. Xem [Canny](https://docs.opencv.org/4.x/da/d22/tutorial_py_canny.html) và [morphology](https://docs.opencv.org/4.x/d9/d61/tutorial_py_morphological_ops.html).

Khi nối task sau, lấy contour từ **closed**, còn edge_support phải đo trên **edges trước closing** của cùng trial. Closing thêm các pixel để nối nét, nhưng chúng chưa phải bằng chứng quan sát được từ gradient. Không tính edge_support từ comparison đã thu nhỏ hoặc từ closed, không trộn dữ liệu giữa ba trial.

Đã chạy `.tmp/mvp05_01_02_verify.py`, xem cả bốn comparison tại experiments/results/mvp05-01-02/ (ignored). Mỗi run có source/analysis/gray/blurred, ba cặp edges/closed, comparison và metadata kích thước/mapping/params/hashes. Kiểm44PNG bằng hash/shape và mức nhị phân của edge maps; nguồn và blurred không đổi.

| Run | Nguồn W×H → analysis W×H | Quan sát |
|---|---|---|
| synthetic_open_edge |420×300 →420×300|Khung nét trắng bị hở5pixel, Canny vẫn hở; closing thêm17pixel ở mỗi trial nhưng chưa nối kín khoảng hở. Ba ngưỡng cho cùng kết quả trên ca tương phản cao này |
| synthetic_landscape_texture |2000×1001 →1200×601|Canny thấy mép trang và các hàng nội dung; closing làm dày/nối các nét bên trong. Không suy ra mask giấy hoặc góc chỉ từ số pixel biên |
| img_003 |1536×2048 →900×1200|Ngưỡng tăng làm bớt nét chữ và nét vật nền; vẫn có nhiều đường bao ngoài giấy. Số pixel trắng raw lần lượt9644/6431/3653, closing thêm2643/1016/185 |
| img_004 |1536×2048 →900×1200|Ô ly và nét nền hiện nhiều ở50/150, một số đoạn mép yếu vẫn hở; closing làm nổi cả nét trong giấy. Raw16842/4315/2938pixel, closing thêm8556/895/117 |

Hai ảnh thật vẫn cùngdoc_01, đều development; không có test độc lập hoặc accuracy. Các counts trên là số pixel, không phải phần trăm nhận đúng biên. Một test edge map kiểm soát riêng xác nhận kernel3 lấp khoảng hở2pixel nhưng giữ khoảng hở4pixel; không gán test này là Canny tự tìm mép giấy thành công.

33tests detection đạt, toànbackend604đạt. Hai task chưa sinh contour, Q, mô tả, score, đề xuất góc hoặc manual_required. Checkpoint05-C1 cần task05.03; cổng05 vẫn chờ. Preset giữ nguyên, chưa tune theo hai ảnh thật.

## 15/10/2026 — Contour/Q và mô tả/scoring (MVP05.03–04)

Đọc lại phân tích mục5.5.1–5.5.3 và đặc tả phần ứng viên/scoring trước khi làm. `generate_candidates` gọi findContours(RETR_LIST,CHAIN_APPROX_SIMPLE) trên closed, xét30 contour lớn/trial và Douglas–Peucker epsilon/P=.015/.02/.03. OpenCV thực hiện tracing/approximation; code dự án giới hạn trial, giữ provenance/lý do và kiểm hình học. Đây không phải MPP của giáo trình. Tham chiếu [OpenCV shape API](https://docs.opencv.org/4.x/d3/dc0/group__imgproc__shape.html) và [contour features](https://docs.opencv.org/4.x/dd/d49/tutorial_py_contour_features.html).

Contour có thứ tự và polygon Q gốc là **biểu diễn**. Chu vi, số đỉnh, độ dài cạnh, góc đổi hướng và tính lồi/tự giao là **mô tả biên**. Diện tích/fit là đặc trưng vùng; hỗ trợ raw Canny và vị trí sát mép bổ sung bằng chứng ảnh/ngữ cảnh. Chỉ mô tả bốn cạnh sau khi validate_quad thành công; không ép góc90° hoặc cho sorter sửa một polygon tự giao thành hợp lệ. Chỉ đảo winding giữ nguyên topology, rồi canonical start theo pixel nguồn thực. Test nguồn2000×1001→1200×601 có trường hợp tie min(x+y) khác nếu dùng analysis thay nguồn.

`describe_candidate` đo chu vi/cạnh bằng pixel analysis, góc rad signed atan2(cross,dot) theo cycle x phải/y xuống. CandidateDescription chứa candidate để truy về trial, source_size/analysis_size và contour/Q. n=max(2,ceil(L/2)+1), linspace gồm hai đầu mỗi cạnh, spacing≤2px; góc chung đếm ở hai cạnh kề. Mẫu hỗ trợ khi raw white pixel cách Euclid≤2px, không lấy vùng vuông bán kính2 hoặc closed. Giữ n/m và e từng cạnh, **e=sum(m)/sum(n)**. b dùng cùng các mẫu cách mép≤2px. a=AQ/(WaHa), f=min(AC,AQ)/max(AC,AQ), **S=clip(.45a+.35e+.20f−.15b,0,1)**. Không tự thêm trọng số góc/chu vi.

Fixture rectangle200×160 có Q(20,20)–(180,140): P560px, cạnh160/120/160/120px, bốn góc đổi hướngπ/2; a=.6, f=1, b=0. Counts81/61/81/61; đủ raw biên thì e=1,S=.82. Bỏ cạnh trên, giữ góc và ba cạnh khác: counts được hỗ trợ4/61/81/61, e=207/284≈.728873,S≈.725106. Không mean4; closed vẫn đầy cũng không nâng e. Raw rỗng: e=0,S=.47. Oracle fixture nhỏ kiểm khoảng cách tới mọi white pixel, gồm cạnh nghiêng và một pixel biên, không chỉ so output với hàm CV tương tự.

Runtime `.tmp/mvp05_03_04_verify.py` có10cases×3trials và map kiểm soát riêng. Evidence chính tại `experiments/results/mvp05-03-04-verified/` (ignored),111PNG gồm raw/closed, contour/Q overlay và comparison; JSON giữ mọi attempt nhận/loại cùng descriptor thật. Contour xanh, Q đỏ/đánh số canonical; nhãn được đặt ngoài ảnh để không che biên. Overlay chỉ minh họa tối đa3 ví dụ có score cao trong từng trial, vẫn giữ bản trùng; **chưa là đề xuất của detector**. Bản render nháp trước đó tại mvp05-03-04/ có nhãn che vùng trên/dưới, dùng bản verified khi xem.

| Case | Kết quả thực qua ba trial | Nhận xét |
|---|---|---|
| rectangle320×240 |2contour/trial,6accepted attempts/trial; score lớn nhất .837687|Mỗi contour thử3epsilon, còn trùng; không gọi6 là6trang |
| diamond320×240 |2contour/trial,6accepted; score .730757|Giữ quad nghiêng, không ép góc vuông |
| concave |2contour/trial,0accepted;6 NON_CONVEX_QUAD/trial|Giữ polygon và lý do, không sửa bằng sắp lại |
| self_cross |3contour/trial,0accepted;9 NOT_QUADRILATERAL/trial|Tracing ảnh tự cắt không tạo đúng4đỉnh. Test Q bowtie kiểm riêng SELF_INTERSECTION; không bịa rằng runtime này trả cùng mã |
| degenerate |1contour/trial,0accepted; CONTOUR_AREA_TOO_SMALL|Nét thẳng không đủ diện tích |
| synthetic_open_edge420×300 |6contour/trial,0accepted; area quá nhỏ|Khoảng hở5px còn hở làm contour chạy quanh nét thay vì bao toàn vùng; không retry để ép quad |
| synthetic_landscape_texture2000×1001→1200×601 |9contour/trial,6accepted; score .725465|Overlay bám mép trang trong ví dụ tổng hợp này |
| frame_and_paper320×240 |4contour/trial,12accepted; score .975859|**Sai theo mục tiêu chọn giấy:** ứng viên lớn bám khung, không bám giấy nhỏ bên trong. Cạnh khung nằm ngoài dải2px nên b=0; score cao vẫn sai |
| img_0031536×2048→900×1200 |108/54/19contour, xét30/30/19;6accepted/trial; score .502372|Overlay bám khá sát trang, a≈.312,e≈.474,f≈.982,b=0. Mép thực hơi cong và Q đoạn thẳng làm nhiều mẫu cách rawedge>2px; không tăng bán kính để ép score cao |
| img_0041536×2048→900×1200 |172/54/13contour, xét30/30/13;0accepted|Các contour xét đều area<10%; raw mép chưa kín, nét ô ly/nội dung tạo contour nhỏ. Chưa có đề xuất hoặc fallback ở hai task này |

Đã xem cả10comparison và map hỗ trợ, gồm hai ảnh thật cùngdoc_01/development. Quan sát không thay thế ground truth hoặc tập test độc lập. Frame penalty giảm điểm khung nằm đúng dải mép, nhưng khung lớn vẫn có thể thắng trang nhỏ; unit fixture còn có frame S≈.844952>paper S=.82. Giữ trọng số/preset ban đầu để ghi nhận hạn chế, không tune từ hai ảnh này. Fallback tay vẫn cần ở task05.06/UI sau.

64tests detection và635tests toàn backend đạt; checkpoint05-C1 đạt. Tiếp theo05.05 loại trùng IoU, rồi05.06 chọn đề xuất/fallback; debug/timing sản phẩm ở05.07, batch development ở05.08 còn chờ. Không tạo HTTP/UI hoặc tự confirmed trong lượt này.

## 15/10/2026 — Thử ảnh bổ sung anhtestnew.jpg theo yêu cầu người dùng

Nguồn mới tại experiments/data/anhtestnew.jpg,612×460; giữ kích thước analysis vì không upscale. Chạy `.tmp/verify_anhtestnew.py` bằng đúng preset05.01–04, không đổi ngưỡng/closing/gate. Mỗi cặp50/150,75/200,100/250 chỉ có1contour, đều bị CONTOUR_AREA_TOO_SMALL trước approximation/scoring. Diện tích contour lớn nhất lần lượt≈0.483%/.365%/.000710% ảnh, dưới10%; không có quad hoặc score. Đây là diện tích contour chạy quanh nét, không phải diện tích tờ giấy thực trong ảnh.

Đã xem source/comparison/raw Canny/closed: mép phải gần như không xuất hiện, ngưỡng cao còn mất mép trên; closing3×3 không nối được khoảng thiếu dài. Nét bóng trái mạnh hơn biên giấy bên phải trên nền sáng. Với cấu hình này chưa tìm được trang dù bố cục nhìn đơn giản; không kết luận dataset tổng quát hoặc thay preset chỉ để qua ảnh này. Evidence tại experiments/results/anhtestnew-mvp05-03-04/: source PNG, analysis/gray/blurred,3raw/3closed/3overlay,comparison vàmetadata, tổng14PNG. Nguồn/raw bytes và array không đổi; output PNG đã đọc lại kiểm pixel/hash. Chưa thêm ảnh vào manifest vì chưa xác định document_id/split; không đổi trạng thái task hoặc tạo warp tự động từ góc giả.

## 15/10/2026 — Điều chỉnh Canny và nhánh vùng sáng, AUX05.01

User chấp nhận sửa sau các ca lỗi. [Revision01](detection-revision-01.md) ghi quyết định, hợp đồng và bảng đầy đủ. Khảo sát16ca×12biến thể Gaussian3/5, Canny50/150–75/200–100/250–20/60–10/30 và Otsu vùng sáng. GiữGaussian5 vì3 không tốt hơn đều; chọn revised20/60,50/150,75/200, không dùng10/30 vì dễ lấy thêm bàn. Baseline cũ vẫn tái hiện; chưa kết luận các tham số này tối ưu hoặc bỏ100/250 không ảnh hưởng ảnh chưa thấy.

Entry collect_candidates revised chạy3Canny/closing3; chỉ khi cả3khôngquad mới thêm1RegionTrial Otsu/RETR_EXTERNAL. Mask vẫn có lỗ chữ, chỉ lấy biên ngoài thành phần trắng; không thêmfill/closinglớn hoặc hạgate10%. Mask toàn0/255 có reason UNIFORM_REGION_MASK, không thành trang giả. Actualt/method/kernel/support_trial_id ghi rõ; e luôn đo raw Canny20/60 của cùng analysis, không dùng boundary mask tự tạo hỗ trợ. S vẫn=.45a+.35e+.20f−.15b cóclip; các tỷ lệ/đơn vị/canonical corners giữ.

Đã chạy production CLI compare_detection trên16ca/104trial:440PNG,272descriptors; xem đủ16comparison tại experiments/results/detection-revision-01-verified/ (ignored). anhtestnew baseline0→revised6acceptedattempts, ví dụ Canny S=.634709/e=.989837 bám sát giấy. img_002/003/005 giữ cùng ví dụ/score, count một số ca giảm do bỏtrialtrùng; img_001 vẫn0. img_004 vàimg_006 thêm1candidate Otsu mỗi ảnh, S=.468352/.448517, nhưng góc trên trái **ăn sang bàn**. Không gọi việc tăng ảnh cócandidate3→5 trong6development làaccuracy. Frame giả vẫnS=.975859 sai, ảnhnét hở lớn vẫnkhôngquad. Constant không cócandidate dù Otsumask toàntrắng.

94tests detection+5CLI, toànbackend670đạt20.17s; TDD mới30core/5CLI. Chưa NMS/proposal/manual fallback/timing/UI, không tạo warp từ ví dụ tự chọn. Dataset6ảnh/1doc_01/test0 giữ; anhtestnew chưaidentity/split. Hướng màu/Hough hoặc đổi scoring còn cần thí nghiệm riêng; nhánh Otsu hiện là dự phòng giới hạn, không phải giải pháp hoàn chỉnh cho bàn sáng/bóng/giấy gập.

## 15/10/2026 — Đối chiếu PDF và định vị lỗi img_004

Theo yêu cầu user, đọc lại các trang liên quan trong cả3PDF và render/xem9trang có công thức/hình; phạm vi/trang cụ thể ở [báo cáo kiểm chứng](verification-img004-theory.md). Không chỉ viện dẫn lời gọi thư viện: tính Otsu từ histogram theo giáo trình(5-62)–(5-64), cực đại duy nhất102, mask bằng toàn bộ pixel của core. Probe bàn(200,340)=109 và giấy(400,650)=186 sauGaussian5 trênanalysis900×1200 đều>102 và cùngcomponent26. Đây là nguyên nhân nhập nhầm vùng trước xấp xỉ.

Contourgốc P5417.48px, approximation .015/.020/.030 lần lượt13/10/4đỉnh; epsilon.03P=162.52px, maxkhoảngcáchcontour→cạnhQ gần nhất160.76px. Tolerance lớn làm đơn giản cả phần bàn dính vào vùng, đúng giới hạn slide6 trang17–19 nêu; chưa phải mask giấy đúng. Q qua topology nhưng cạnh trên chỉ7/245support=2.86%; f.93018 chỉkhớpdiệntích, b0 dùcomponent chạmbiênảnh. Chưa đề ra gate mới chỉ từảnhnày; không thay score hoặc gọi MPP/region-growing cho các hàm đang dùng. Evidence tại experiments/results/img004-theory-verification/, source/PDF nguyên; corekhôngđổi,670tests là mốc hồi quy trước đó.

## 15/10/2026 — Polygon NMS và đề xuất chưa xác nhận, MVP05.05–06

Giữ preset/segmentation/epsilon và S hiện có; nối thêm IoU/NMS rồi chọn status. IoU dùng diện tích liên tục của hai tứ giác lồi đã validate, gồm containment; không thay bằng bounding box. NMS greedy score giảm dần, tie theo thứ tự vào, chỉ loại IoU>.95 với survivor. Giữ description thắng nguyên vẹn, gồm method/kernel/actual Otsut/raw support origin và counts. Với cùng polygon khác start, trả IoU=1 chính xác để tránh sai số float32. Có18tests metrics và28tests selection/proposal; 140focused,716backend đạt.

`detect_document` nhận source BGR uint8 sauEXIF, Gaussian5/revised → collect → describe → select_proposal. S≥.60 trả proposed; .40≤S<.60 proposed_with_warning/LOW_HEURISTIC_SCORE; dưới.40 manual_required/corners=null và giữ best chỉ làm chẩn đoán. Khôngquad trả manual_required/NO_VALID_QUAD, corners/score=null. confirmed=false mọi trường hợp. Input/CV lỗi không bị che thành manual_required. Đây là trạng thái đề xuất, không tự xác nhận giấy hoặc render.

Evidence tập trung7ca tại experiments/results/mvp05-05-06-verified/ (ignored), đã xem đủ overlay:

| Ca | Accepted attempts → NMS survivors | Status | S | Quan sát |
|---|---:|---|---:|---|
| img_001 | 0→0 | manual_required | null | Giấy gập/nền phức tạp, chưa quad |
| img_003 | 12→1 | proposed_with_warning | .502372 | Bám trang, cạnh giấy hơi cong |
| img_004 | 1→1 | proposed_with_warning | .468352 | Vẫn ăn bàn ở góc trên trái |
| anhtestnew | 6→1 | proposed | .634709 | Bám trang trắng trong ảnh nhỏ |
| rectangle synthetic | 18→1 | proposed | .807809 | Vùng trang rõ |
| frame_and_paper synthetic | 36→2 | proposed | .979901 | Chọn sai khung ngoài |
| blank synthetic | 0→0 | manual_required | null | Không dựng giả vùng giấy |

Không gọi các trạng thái trên là accuracy. Cảnh báo img_004 đến từ ngưỡng S hiện có, chưa phải bộ phát hiện bàn/giấy hoặc gate hỗ trợ từng cạnh. Topside support2.86% đã được chẩn đoán trước, vẫn giữ để đọc debug ở05.07. Đợt này không thêm ngưỡng epsilon/khoảng cách/side-support chỉ để chữa một ảnh. Hoàn tất05.07–08, đối chứng giới hạn rồi mới quyết định điều chỉnh nhỏ trước đóng cổng05. Chức năng UI sau này cho chỉnh tay, không tự khắc phục phân vùng sai.

## 15/10/2026 — Timing/debug, batch và rà đủ8task, MVP05.07–08/AUX05.02

Detector giữ Gaussian5/revised và công thức điểm cũ. Có timings_ms thực và debug opt-in: analysis/trials/selected_trial đúng ID, raw/closed hoặc regionmask tách biệt, overlay giữ tọa độ analysis, source BGR hash và đơn vị. Timing candidates gộp Canny/closing/contours/region; select gồmNMS; không gồm decode/encode/I/O. Khi tắt debug không giữ stage arrays. Khi khôngquad không vẽ giả; low-score best chỉ làm diagnostic.

`experiments/detect_batch.py` chỉ đọc development trong manifest, cho thêm --input chưa gán identity/split; chạy baseline/revised trên cùng nguồn. Ghi sourcePNG đúngpayload, stages/hash/config/trial/selected description/timing, comparison, CSV và summary. Lỗi từng ảnh có error.json và exit1, vẫn xử lý ảnh khác; test không được mở để tune. Có10tests debug và7batchCLI mới; toànbackend733đạt47.01s.

Evidence chính experiments/results/mvp05-07-08-verified/:16ca gồm6development cùngdoc_01, anhtestnew và9synthetic;32runs/104trial/368PNG. Xem đủ16comparison, QA tính lại gray/Gaussian/Canny/closing/Otsu và19survivors từraw đãlưu. Baseline9manual/3warning/4proposed; revised6manual/5warning/5proposed, **không phải tỷ lệ đúng**. img_002/003/005 giữquad/score; img_004/006 revised cảnh báo nhưng ăn bàn; anhtestnew proposed bám giấy; frame vẫn proposed sai S.975859. Các ca concave/self_cross/degenerate/open_edge/constant vẫnmanual. Source/normalized6cặp và22fixtures khôngđổi.

Fallback img_001: quadnormalized draft doagent chọn thử, khôngGT/userconfirmed, qua enhancement_demo cósẵn từJPEGgốc tạo warp951×1284 vàColor/Gray/Adaptive/Otsu. Evidence8PNG ở mvp05-08-manual-img001/; đãxemcomparison/warp, config confirmed=false, Color=warp do denoiseNone. Cònmép bàn/gócgiấy gấp, BW có mấtôly/đứtnét vàđenbóng; khôngdewarp. Đây là bằngchứng lõi xửlý tay, chưaUItay/pipeline06.

[Audit05](audit-phase-05.md) có ma trận8task và hướng nợ03–04. Max khoảngcách đỉnhcontour đãlưu→Q là160.76px/.10727D ởimg_004 và143.62px/.09583D ởimg_006; các ca giấy kháđúng trongnhóm thấp hơn rõ. f diện tích vẫn cao.93/.92 vàcạnhyếu cósupport.02857/.07394. Hướng thử: cap epsilon theoD/kiểmfitdistance, thêmcảnhbáocạnhyếu, đối chứngmàu/chiếu sáng khiOtsu nhập bàn. **Chưa chọn ngưỡng hoặc sửa score/phânvùng.** Frame cóminsupport1 vàdistance1px, nên cácgate này khôngcứuđược khunggiả; cầnđánhgiácảnhmơhồ/vùnglồngnhau vàgiữ xácnhậntay. Phépđo khoảngcách khôngphải Hausdorff liên tục hoặc GTerror; dữliệu1doc chưa đủ tune tổngquát.

## Giới hạn và bước sau

### Mốc MVP06.01–03 — 15/10/2026

Đã nối một pipeline offline từ normalize đến full render/preview/config/stages, không đổi detector. `scan_one.py` chạy auto hoặc góc tay; góc tự động giữ confirmed=false. Có warning vẫn có thể tạo render nháp để xem; manual_required không tạo full giả, lưu chẩn đoán để chạy lại bằng góc tay. Nhánh detection và render dùng thư mục riêng, cùng run_id và hash nguồn; writer dùng chính DetectionResult đã chạy, không tạo debug bằng một lượt detection khác.

Evidence tại experiments/results/mvp06-01-03-verified/ (ignored):

| Run | Góc/mode | Full W×H | Preview W×H | Quan sát |
|---|---|---:|---:|---|
| anhtestnew-color-auto | detected/Color |201×285|201×285|Bản trắng giữ sắc độ; ảnh nhỏ không upscale |
| img003-gray-auto | detected/Gray |898×1288|697×1000|Có warning; còn bóng đậm/ô ly, CLAHE không xóa bóng |
| img004-bw-auto | detected/BW Otsu |1112×1358|819×1000|**Quad vẫn ăn bàn**, phối cảnh lệch theo quad sai, phần bàn bị đen |
| img001-auto | none/Color |không có|không có|manual_required, không warp/full giả |
| img001-gray-manual | draft tay/Gray |951×1284|741×1000|Đọc được trang, còn mép bàn/góc gấp; không GT hoặc userconfirmed |
| checkerboard-bw90 | tay/BW Otsu/90° |1300×2000|650×1000|Full nhị phân; preview cógray do INTER_AREA, không threshold lại |
| img001-gray-snapshot | config tay/Gray |951×1284|741×1000|Cùng ảnh gốc/config giữ hash full/preview/stages so run tay |

QA7runs/92PNG,4detection/14trial,6render/1manual_required: đọc lại hash/bytes/dimensions/mode/EXIF, config, sourcewarp, filtered/preparedgray/Otsu, before_rotation/full/preview và H. prepared_gray được lấy ngay trong dispatcher sau denoise/contrast, là input BW threshold thật; không dùng gray/Gaussian của detector thay thế. Color không tạo prepared_gray giả. Hash Gray manual img_001 trùng bản full ở giai đoạn05;6cặp nguồn/normalized và22fixtures không đổi.

777backend đạt38.83s, gồm44tests mới (30pipeline/encoder,6enhancement stages,8scanCLI). Snapshot này phục vụ chạy lại case; nghiệm thu tái lập đầy đủ06.05, histogram06.04 và mốcM1/06.06 vẫn chờ. Không tuyên bố score/nhãn rendered là accuracy hoặc nguồn đã được xác nhận cho xuất tài liệu. Nợ detector task03–04 trong audit05 vẫn mở.

Chưa có OCR, điểm độ đọc, ground truth nét/dấu hoặc tập test độc lập. Không báo precision/recall/F1 hoặc “độ chính xác” từ số test/pixel khác nhau. Góc tay/estimated aspect có thể ảnh hưởng hình dạng chữ; warp không dewarp trang nhàu. Bộ development hiện6ảnh/1tài liệu, chỉ dùng hai ảnh thật ở lượtso này. Không hứa làm trắng nền trong mọi điều kiện.

Giai đoạn04 có lõi mode/threshold/xoay, giai đoạn05 có detector/debug/batch; [audit04](audit-phase-04.md) và [audit05](audit-phase-05.md) ghi nghiệm thu cùng giới hạn. Giai đoạn06/M1 đã hoàn thành offline/full-preview/config/stages/histogram và kiểm tái lập. Tiếp theo07.01 schemaAPI; HTTP/UI sửa/xác nhận/revision/lưu bền/nhiều trang/PDF và đánh giá độc lập vẫn chờ. Sáu ảnh cùng một tài liệu không thay cho GT/test độc lập; nợ detector chưa được sửa trong lượt tích hợp này.

### Histogram trước threshold — MVP06.04, 16/10/2026

Histogram h(k) đếm pixel mức xám k=0..255; h(k)≥0 và tổng=N. Lõi dùng OpenCV calcHist256bin trên **prepared_gray full sau lọc/CLAHE, trước threshold/xoay**. Không dùng ảnh analysis của detector, preview hoặc BW đã phân ngưỡng. Trả counts nguyên, không xác suất; nếu giải thích Otsu thì p(k)=h(k)/N được suy ra riêng. Tham số [0,256) vẫn bao gồm mức255;5.76MP nằm dưới giới hạn đếm nguyên chính xác của float32. [OpenCV](https://docs.opencv.org/4.x/d1/db7/tutorial_py_histogram_begins.html), [hợp đồng11.2](image-contract.md#112-histogram-trước-threshold--mvp0604).

Otsu chọn một t toàn ảnh, giữ actual t của lần chạy; Adaptive Gaussian dùng trung bình Gaussian cục bộ trừ C, không có một t toàn cục. Histogram không chứa thông tin vị trí, nên hai ảnh có cùng histogram có thể có cấu trúc/bóng rất khác; không dùng histogram đơn lẻ để chứng nhận chọn đúng trang. Color/Gray không phân ngưỡng nên trường mang ý nghĩa “trước threshold” là null. Histogram có cả debug=false; stagearrays chỉ giữ khi debug=true. UI vẽ đồ thị thuộc09.07, phần tự viết giáo dục OPT-B chưa làm.

Evidence `experiments/results/mvp06-04-histogram/` (ignored):

| Run img_004 | Input gray W×H | Tổng count / bin khác0 | Ngưỡng | Kiểm chứng |
|---|---:|---:|---|---|
| Otsu auto |1112×1358|1.510.096 /213|global t=140|Full/preview/warp/filtered/gray/before_rotation giữ nguyên hash mốc03; vẫn ăn bàn |
| Adaptive replay góc |1112×1358|1.510.096 /213|local, t=null; block31/C10|Cùng gray/hash/histogram, BW khác Otsu; không sửa quad |

Ngưỡng140 là của render full sau warp/Median, khác Otsu102 của detector analysis ở chẩn đoán trước; đó là hai stage/kích thước/tiền xử lý khác nhau. Run Adaptive dùng config đã có corners từ run Otsu, skipdetect nên warnings detect rỗng không có nghĩa detector vừa tốt hơn. Cả hai confirmed=false, quad vẫn có vùng bàn. Đọc PNG gray bằng Pillow rồi đếm độc lập NumPy, đối chiếu toàn256bin/hash/dimensions; tính kiểm BW với actualmethod/config. Nguồn và22fixtures giữ hash. Đây là kiểm chứng task04, chưa đánh dấu nghiệm thu tái lập06.05 hoặc M1.

16tests histogram/dispatcher và1CLI mới; focused25tests đạt23.56s, toànbackend794đạt95.24s. Không thêm dependency hoặc thay thuật toán xử lý pixel; timing đếm histogram nằm trong enhance/total. Metadata/hash chi tiết và lệnh ở [progress](progress.md).

### Mốc M1 và tái lập — MVP06.05–06/AUX06.01, 16/10/2026

Đã nghiệm thu cả6task ở [audit06](audit-phase-06.md), có [hướng dẫn M1](milestone-m1.md) và lệnh smoke6CLI đã chạy không cần ảnh riêng. Lượt này không sửa core/preset; bổ sung4tests core serializedsnapshot/repeat và2tests CLI auto/failure, toànbackend800đạt99.97s. Runtime10ca×2tiếntrình giữ cùng input/config/scan-v1:20runs/230PNG,18render/2manual_required,8detect/28trial. So toàn metadata trừ run_id/timing; tính kiểm sourcewarp/filter/gray/threshold/rotation/preview/histogram vàhashảnh, không chỉ so hai bộ output. Nguồn6cặp và22fixtures nguyên; environment/codehash ở verification.json của mvp06-m1-verified/.

Đã xem overlay anhtestnew bám vùng trang trắng201×285; img_003 Gray898×1288 vẫn bóng rõ; img_004 Otsu1112×1358/t140 vẫn ăn bàn/đen biên. img_001 auto khôngquad, tayColor951×1284 hiện trang nhưng cònmépbàn/gấpgóc; Gray180 vàBWAdaptive90 tạođúngdimensions. Adaptive90 Gaussian+CLAHE giữ nhiềuôly/nhiễu vàcónétđứt; không dùngrun nàyđểtuyênbố cải thiện độđọc. Exif6Otsu270 cho95×63/t150; checkerboard90 cho1300×2000/t118 vàpreview650×1000 cógray. Rotation là lựa chọn kiểm thuật toán, không suyra hướng đọc tựđộng.

Tái lập trong cùng dependencies chứng minh tính ổn định của phép chạy, **không chứng minh quad đúng giấy**. Ngưỡng140 render khác102 detector là hai stage; không cố làm bằng nhau. Nợ epsilon/fitdistance/cạnhyếu/phânbiệt nền/khunggiả ở audit05 vẫn mở; khôngđổi weights từ1tờgiấy. M1 chỉoffline/PNG, scanUI/storage/revision/multipage/PDF ở sau; chưaaccuracy hoặctestđộclập.

## Giải thích stage trên UI — MVP09.07–08, 18/10/2026

PipelineViewer hiển thị mục đích, tham số thực và giới hạn ngay cạnh stage đã lưu. Chọn nhóm nhận diện để xem analysis/trial/contour; chọn xử lý bản quét để xem warp/filter/prepared_gray/before_rotation/full/preview. Không tạo lại stage từ một phép chạy khác để làm minh họa. Mỗi nhóm ghi run/version/UTC/source/revision; ảnh nguồn và kết quả trước/sau vẫn độc lập.

| Bước | Tham số/phép toán hiện hành | Cần hiểu và giới hạn |
|---|---|---|
| Analysis/gray | Nguồn sauEXIF → cạnh dài≤1200 INTER_AREA/no-upscale → BGR2GRAY | Chỉ phân tích vị trí, không phải nguồn warp. Màu có thể giúp mắt phân biệt bàn/giấy nhưng bị giảm khi về gray |
| Gaussian/Canny | Gaussian5/sigma0/reflect101; Canny20/60,50/150,75/200, aperture3/L2 | Làm mượt → gradient → NMS → ngưỡng kép/hysteresis. Biên chữ/bóng/nếp gấp cũng hợp lệ về cường độ, chưa đồng nghĩa biên trang |
| Closing | Dilation rồi erosion, kernel3×3 một lần | Nối hở nhỏ trên map biên trắng; có thể nhập chữ/bàn/bóng. Đo e từ rawCanny trướcclosing, không từ mask vùng |
| Contour và Q | RETR_LIST/CHAIN_APPROX_SIMPLE; DP với ε/P=.015/.02/.03, cap30contour/trial, geometry gate | Chuỗi điểm/đa giác là **biểu diễn**. DP không phải tối ưu đa giác chu vi tối thiểu MPP; không tự gọi findContours là Moore |
| Mô tả biên | Chu vi contour, nQ, bốn độ dài analysis px, góc đổi hướng radian, lồi/tự giao | Đây là **descriptor**. Tọa độ Q/góc normalized thuộc biểu diễn; diện tích tương đối a thuộc vùng. Không loại quad chỉ vì góc ảnh khác90° |
| Chọn ứng viên | a=AQ/(WaHa), f=min(AC,AQ)/max(...), e=Σmi/Σni, b=sátkhung; S=clip(.45a+.35e+.20f−.15b) | Mẫu nᵢ=max(2,ceil(Lᵢ/2)+1), raw edge trong bán kính Euclid≤2analysispx. NMS IoU>.95; score≥.6 đề xuất,.4–.6 cảnh báo,còn lại tay. Trọng số là heuristic của dự án, không phải công thức accuracy trong giáo trình |
| Nhánh vùng | Chỉ khi cả3Canny khôngquad, thử Otsu trên blurred analysis/RETR_EXTERNAL; rawsupport20/60 giữ riêng | Otsu ở đây phân vùng sáng để tìm giấy. Bàn cùng sáng có thể dính giấy; khác Otsu sauwarp tách chữ |
| Homography | Bốn góc normalized theo nguồn W−1/H−1; source→rectangle; fullsource/INTER_LINEAR/BORDER_REPLICATE | Cắt boundingbox không sửa phối cảnh. Góc trên ảnh xiên không cần90°; một homography không làm phẳng giấy cong/nhàu3D |
| Cải thiện/threshold | None/Median/Gaussian → Color hoặc Gray/CLAHE(grid8×8,clip1–4) → BW Otsu/Adaptive nếu chọn → xoay | Median có thể mất dấu mảnh, Gaussian mềm nét; CLAHE có thể tăng nhiễu. Otsu actualt toàn ảnh, AdaptiveGaussian blocklẻ3..151≤cạnhngắnwarp/C−20..30 là cục bộ, không có t chung. Color giữ highlight tốt hơnBW |
| Full/preview/histogram | Full sauxoay; preview thu từfull≤1000; histogram256counts của prepared_gray trướcthreshold/xoay | PreviewBW cógray doINTER_AREA nhưng fullBW chỉ0/255. Histogram mất thông tin vị trí, không chứng nhận đã chọn đúng giấy; Color/Gray không phân ngưỡng nên không có histogram mang nghĩa trước threshold |

### Đối chiếu lại tài liệu môn học

Đã so SHA-256 của cả ba PDF với bản trích cục bộ đã đọc; nội dung không đổi. Giáo trình308trang, slideCh05 60trang, slideCh06 63trang; số trang sau là vị trí trong PDF, không khẳng định trùng số in trên trang.

- [Giáo trình](<Giáo trình _ Xử lý ảnh.pdf>): trang97–99 về mô hình biên/đạo hàm và nhạy nhiễu; trang164 về biểu diễn đa giác/MPP. Cơ sở này giải thích cần làm mượt và không coi mọi cạnh cường độ là mép tài liệu.
- [SlideCh05](<xla_Ch05 (1).pdf>): trang19 về dạng biên; trang35 minh họa sáng không đều làm hai phân bố mức xám chồng nhau, giải thích vì sao ngưỡng toàn ảnh có thể thất bại và cần xem xét ngưỡng cục bộ.
- [SlideCh06](xla_Ch06.pdf): trang17–19 về xấp xỉ đa giác, MPP theo ô và chia đoạn lặp theo độ lệch. Chúng là những cách biểu diễn/xấp xỉ khác nhau; implementation dùng Douglas–Peucker của OpenCV, không tuyên bố đã cài thuật toán MPP trong slide.

Homography, giới hạn/preset/đơn vị/scoring của dự án được đối chiếu implementation và [hợp đồng](image-contract.md); không quy toàn bộ lựa chọn triển khai thành công thức lấy nguyên từ baPDF. [Phân tích5.5.1–5.5.3](Phan_Tich_Huong_Thuat_Toan_Tu_Tai_Lieu.md) vẫn là quy ước nghiệm thu detector/descriptor. Các hàm OpenCV làm phép lọc/Canny/contour/DP/warp/CLAHE/threshold; dự án tự nối pipeline, kiểm hình học, tính descriptor/support/score, quản lý config/revision/provenance và UI. OPT-B tự viết histogram/Otsu giáo dục chưa thực hiện.

### Demo và số đo

Ảnh tốt có P979.698analysispx/nQ4/e.989837/S.634709; bốn cạnh hỗ trợ102/102,139/144,102/102,144/144. img_004 có P5417.476/e.304282/S.468352, nhánh vùng và cảnh báo, vẫn có thể chọn dính bàn. Ảnh trắng không có quad/selected nên UI báo thiếu mô tả, không đo từ khungtay5%.

Otsu ảnh tốt prepared_gray201×285/t247/tổng57.285; Adaptive51/C10/CLAHE t=null. Ảnh chữ/highlight full1199×1599/t163/tổng1.917.201; khác t165 của phép chạy Median trước vì config khác. Sáu histogram được đọc PNG/NumPy đối chiếu đủ256bin, không chỉ kiểm tổng. Chi tiết [audit09](audit-phase-09.md); dữ liệu và screenshot ở ignored `experiments/results/mvp09-final-verified/`.

UI giúp giải thích vì sao thất bại, chưa tự sửa nợimg_004/006. Nhiều màu nền, bóng mạnh và nhàu/cong có thể làm mất mép/chữ; filter sauwarp không lấy lại vùng giấy đã cắt sai. Dataset6ảnh/1tờgiấy/test0 không cho phép tuyên bố accuracy tổng quát.



## 26/10/2026 — Metrics và đối chứng Gaussian/closing/lựa chọn ứng viên

MVP13.03 dùng coreIoU liên tục,chu kỳ đảo/đổi điểm đầu chỉ được chuẩn hóa trong công cụ đánh giá,sau kiểm topology. Cornererror làmin trung bình4khoảng cáchsourcepixel trên8cách ghép,chiaD=hypot(W−1,H−1);không dùngu/vEuclid trực tiếp. Khôngproposal trênảnhcóGT→IoU0/mẫu số giữ;cornererrornullkhônggiả vôcực,mean chỉtrênảnhcó góc vàbáosốmẫu. Unlabelable táchriêng. [Định nghĩa và bảng](results.md).

MVP13.04 dùngbốnprofile chungrevised3Canny vàconditionalOtsu fallback; mỗiđốichứng chỉđổi selection hoặcGaussian hoặcclosing. prepare_analysis hỗtrợgaussian_kernel=0 explicit đểcopygray,create_edge_trials/collect_candidates hỗtrợclosing=False explicit đểcopiedges; rawCanny vẫnriêngđểtínhsupport. Gaussian0 cótrialIDg0/provenance riêng,chứkhônggắnmetadataGaussian5vàoảnhchưalọc. App vẫnGaussian5/closingTrue/detect-v1;defaultresult/stages bằngmãtrướcsửatrên6development. Codehash nguồn thay đổi doopt-in,phải dùngsnapshot13mới khi khóa,khôngsửa bằngchứngM1cũ.

Largest chọnmaxdiệntíchcontour trongcùngvalidpoolvàcùngstatusgate,khôngbỏcácgategiấy/tựnhận mọiứngviên. img005 scoringe.512048/S.501182 so largest e.490972/S.493638 nên cóIoU hơi tốt hơn; vẫn chỉ một tài liệu. BỏGaussian làmimg004 xấu hơn(.872497→.716925),bỏclosing đưaproposal saiởimg001/006. Khôngcoicóproposal làđúng,mô tảbiên/vùng vàrawsupport giữđơnvị như5.5.1–3. Mặcđịnh/scoringweights/threshold khôngđổi theoquan sát này. Bảyảnhtestdoc_02 chưa chạy detector,đợifrozen13.06/đánhgiá13.07.


## MVP13.05–06 — So threshold và giữ cấu hình trước test (26/10/2026)

So Otsu/Adaptive dùng 3 quad tham chiếu thật của development, mỗi ảnh warp một lần;
giữ Median 3/không CLAHE/rotation 0/block 31/C 10, chỉ đổi threshold.method.
Hai lượt dispatcher có prepared_gray/histogram giống nhau, ngưỡng Otsu thực 147/172/186
cho img_003/004/005; Adaptive không có một ngưỡng global. Đã mở đủ 6 BW full và warp:
Otsu gộp nền tối vào foreground nên che chữ; Adaptive giữ nhiều nội dung hơn nhưng
vẫn giữ ô ly và có nét đứt. Không đo OCR/accuracy chữ hoặc suy rằng ít pixel đen hơn là đúng hơn.
Ảnh even_light vẫn có gradient; dataset không có highlight thật/sáng đều được kiểm soát.
Ví dụ highlight tổng hợp riêng cho thấy mất màu, Otsu mất nét nhạt, Adaptive tạo viền dải màu.

Giữ các preset và score của app vì một tài liệu development chưa đủ cơ sở đổi ngưỡng.
[Bản khóa/môi trường](experiment-environment.md) lưu detect-v1/scan-v1 và hash mã hiện hành;
code hash M1 cũ giữ làm lịch sử. Không sửa core, API, DB schema, frontend hoặc dependency ở lượt này.
13.05 không sửa lỗi detector ăn bàn: đã dùng góc tham chiếu để tách hai vấn đề.
13.07 phải kiểm bản khóa trước đánh giá test và ghi riêng hash runner benchmark mới.


## MVP13.07–08 — Kết quả sau khóa và giới hạn (26/10/2026)

Giữ detect-v1/scan-v1/revised/Gaussian5/closing/score và preset13.06.
7 test/doc_02 đều chọn từ Canny,meanIoU0,995347,sai số góc2,303px;6proposed/1warning.
img_009 có a.325122/e.727423/f.994234/b0 → S.599750<.60 nên cảnh báo dù IoU.994511.
Score tổng hợp hình học/hỗ trợ cạnh không phải xác suất đúng; không chỉnh ngưỡng sau khi thấy test.
Đã xem7overlay và giữ ca development img004ăn bàn/001–002–006unlabelable/Otsuđenbóng.

Nhóm test in tương phản biên rõ hơn development giấy ô ly/bóng mạnh; mỗi split chỉ một tài liệu,
nhãn thủ công và cùng nền bàn. Không suy rộng7/7 thành accuracy mọi tài liệu hoặc che3unlabelable.
Không có bằng chứng dewarping nhàu mạnh/lóa/highlight thật. Homography qua4góc là mặt phẳng xấp xỉ,
không khôi phục nội dung ngoài khung/bị che/cháy sáng. Giữ kiểm tra/xác nhận tay và chụp lại khi mất thông tin.

[Benchmark](benchmark-method.md) có140mẫu đo/28warmup;không đổi thuật toán để sửa lỗi đoPID Windows.
Lượt đầu RAM launcher bị loại khỏi kết luận,final dùng PIDserver thật;metrics/full/overlay hai lượt bằng byte.
Version/hashrunner riêng,bảnkhóa/91source files/nhãn giữ. Nếu thử nợepsilon/fitdistance/cạnhyếu/phân biệt nền
sau này phải ghi version/dữ liệu phù hợp,không gọi test đã thấy là tập chưa quan sát.
