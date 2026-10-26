# Hợp đồng ảnh, tọa độ và cấu hình — Document Scanner MVP

Ngày chốt14/10/2026; cập nhật18/10/2026. Đã có nguồn/geometry/enhancement/detector/scanUI/debug và10.01–02 đổi tên/thêm trang. [Checklist](../tasks/todo.md), [API](api-contract.md), [audit09](audit-phase-09.md), [M1](milestone-m1.md). Order/xóa/mở lại kết quả đầy đủ và PDF còn chờ.

Nguồn: [đặc tả gốc, mục 5–10](../Document_Scanner_Dac_Ta_Kien_Truc_Thuat_Toan.md), áp dụng điều chỉnh trong [phạm vi MVP](MVP_Pham_Vi_Va_Ke_Hoach_4_Tuan.md). Phần mô tả/xếp hạng đọc cùng [hướng thuật toán, mục 5.5.1–5.5.3](Phan_Tich_Huong_Thuat_Toan_Tu_Tai_Lieu.md). Khi chốt schema ở MVP04.01/MVP07.01, phải đối chiếu tài liệu này; không tự thay đơn vị, thứ tự góc hoặc mặc định.

## 1. Nguồn, kiểu ảnh và chuẩn hóa

| Đối tượng | Quy ước |
|---|---|
| Đầu vào | JPEG/PNG, một frame; kiểm tra decoder/header, không chỉ đuôi/MIME |
| Quota | Tối đa 15 MiB = 15×1024×1024 byte; 16.000.000 pixel; mỗi chiều tối thiểu 2; 20 trang/phiên |
| Nguồn gốc | Giữ byte nhập riêng, không ghi đè hoặc lọc trực tiếp lên nguồn |
| Nguồn chuẩn hóa | Áp EXIF một lần, ghép alpha trên trắng, RGB→BGR; `uint8`, shape `(H, W, 3)`, giá trị 0–255 |
| Lưu nguồn chuẩn hóa | PNG lossless, không mang EXIF orientation cũ; width/height/hash của đúng tệp đã lưu |
| Ảnh xám | `uint8`, shape `(H, W)`; không coi mảng H×W×1 là hợp đồng lõi |
| Render BW trước encode | `uint8`, shape `(H, W)`, chỉ 0/255; chữ đen 0, nền trắng 255 |
| Trình duyệt | Ảnh đã encode; decoder/canvas dùng RGB/RGBA. OpenCV encode nhận BGR; Pillow encode màu cần đổi BGR→RGB |

W/H là kích thước **sau EXIF**. Render, detect và reopen đọc nguồn chuẩn hóa đã lưu, không áp EXIF thêm lần nữa. Các phép chia/lọc cần số thực phải chuyển dtype trước tính, clip rồi mới đưa về uint8; tránh overflow/wrap-around. MVP chưa bảo đảm quản lý màu ICC cho in ấn.

Giao diện lõi hiện có: `validate_image(bytes)` trả metadata trước EXIF; `normalize_image(bytes)` kiểm tra lại đầu vào, giải mã và trả BGR uint8 sau EXIF; `encode_normalized_png(BGR)` trả PNG lossless mới không kế thừa EXIF cùng W/H và SHA-256 của đúng byte PNG. Storage ghi chính payload này và giữ byte nhập riêng. Giới hạn 15 MiB áp cho tệp upload; PNG chuẩn hóa nội bộ có thể lớn hơn, được đọc theo hợp đồng source thay vì nhập lại qua quota byte của upload. Giới hạn 16 triệu pixel và dimensions ≥2 vẫn áp cho nguồn chuẩn hóa.

Preview thu nhỏ của BW có thể chứa mức xám ở rìa nét do nội suy; không threshold lần nữa chỉ để ép preview về 0/255. PNG giữ pixel render; JPG có nén mất mát nên không dùng pixel JPG để kiểm tra tính nhị phân của lõi.

## 2. Các ảnh trong pipeline

| Ảnh | Kích thước/chức năng | Quy tắc |
|---|---|---|
| Source chuẩn hóa | Giữ kích thước, trong quota | Nguồn hình học duy nhất |
| Analysis | Cạnh dài tối đa 1200 | Không upscale; chỉ phục vụ detection |
| Full render | Cạnh dài tối đa 2400 | Warp từ source; các bộ lọc chạy ở kích thước này |
| Preview | Cạnh dài tối đa 1000 | Thu từ full render sau lọc/xoay; không upscale |
| Thumbnail/debug | Kích thước thật kèm metadata | Không dùng làm nguồn warp hoặc xuất |

Resize thu nhỏ dùng INTER_AREA, giữ tỉ lệ dự kiến và kích thước thực sau làm tròn. Để Python/JS không khác ở trường hợp .5, quy ước kích thước dương là `floor(value + 0.5)`. Ảnh phân tích phải có Wa/Ha ≥2 để chuyển tọa độ; nếu thu nhỏ làm một chiều <2, trả `manual_required`, không tiếp tục phép chia với mẫu số 0. Preview/thumbnail chỉ dùng để hiển thị, không cung cấp hệ tọa độ hình học mới.

Helper hiện có `resize_to_max_edge(image, max_edge)` nhận gray/BGR uint8, max_edge nguyên dương; không upscale và trả mảng độc lập. Chiều sau làm tròn tối thiểu 1 để OpenCV không nhận dimensions bằng 0; ngưỡng này dành cho display, không thay Wa/Ha ≥2 của geometry. CLI tạo thumbnail từ nguồn với max_edge mặc định 320; preview kết quả sau này vẫn thu từ full render với giới hạn 1000.

Với dimensions nguyên, half-up hiện thực chính xác bằng `(2*dimension*max_edge + longest)//(2*longest)`, tránh float làm 62.5 thành 62.49999999999999. Đây là cùng quy tắc floor(x+0.5), không thay thuật toán resize hay hệ tọa độ; tests hồi quy được thêm trong AUX02.01.

Nhánh detection: source → analysis → gray → Gaussian → Canny → closing → contour/đa giác → mô tả/xếp hạng. Nhánh render: source + góc xác nhận → warp → bộ lọc/mode → xoay → full render → preview. Gaussian/closing ở detection không làm thay đổi nguồn xuất.

Canny/closing dùng edge trắng 255 trên nền 0; BW render dùng chữ đen 0 trên nền 255. Không áp cùng phép hình thái vào hai ảnh mà bỏ qua polarity/mục đích.

## 3. Tọa độ nguồn và ảnh phân tích

Gốc trái trên, x là cột sang phải, y là hàng xuống; tọa độ hình học giữ số thực. API truyền `[u, v]` trên **nguồn chuẩn hóa**, không phải ảnh chụp trước EXIF, preview hoặc ảnh đã xoay.

```text
u = x / (W - 1)          x = u * (W - 1)
v = y / (H - 1)          y = v * (H - 1)
```

u/v hữu hạn và trong [0,1]; không nhận NaN/Infinity. Normalized 0/1 ứng với chỉ số pixel 0/W−1 hoặc 0/H−1; không dùng W/H làm mẫu số. Không làm tròn góc thành pixel nguyên trước homography.

Góc tìm trên analysis chuyển bằng `u = xa/(Wa−1)`, `v = ya/(Ha−1)`, sau đó ra source bằng W−1/H−1. Không chỉ chia xa/ya cho tỷ lệ resize danh nghĩa vì hai chiều có thể làm tròn khác nhau. Một ví dụ kiểm chứng: source 101×51 có góc (100,50) ↔ (1,1); analysis 51×26 có góc (50,25) ↔ cùng (1,1). Đây là tọa độ ví dụ, không phải số đo detector.

Đã hiện thực trong `processing/geometry.py`: `pixel_to_normalized(point, width, height)` và `normalized_to_pixel(point, width, height)` nhận đúng hai số thực hữu hạn, dimensions nguyên ≥2; trả tuple số thực, không làm tròn/clamp/đổi input. NumPy scalars cũng được nhận. Lỗi `GeometryValidationError(ValueError)` có code `INVALID_DIMENSIONS`, `INVALID_POINT` hoặc `POINT_OUT_OF_BOUNDS`; không phụ thuộc HTTP. Quota nguồn vẫn thuộc normalize/storage, không nhân bản quota upload trong geometry.

## 4. Bốn góc và thứ tự ánh xạ

`corners` là null hoặc đúng bốn điểm `[p0,p1,p2,p3]` theo chu kỳ **chiều kim đồng hồ trong hệ y xuống**. Mỗi điểm giữ ID/vị trí trong danh sách. Full-image quad là `[[0,0],[1,0],[1,1],[0,1]]`; vẫn cần xác nhận trước render.

Auto proposal: sắp quanh tâm bằng atan2, chuẩn hóa winding, chọn điểm đầu min(x+y), tie-break y rồi x, sau đó xoay vòng danh sách. Không chọn bốn góc độc lập bằng min/max tổng/hiệu vì diamond có thể trùng đỉnh. Signed shoelace area dương ứng với winding đã chốt.

Manual: giữ ID handle khi kéo; backend kiểm tra thứ tự, không tự sắp lại hoặc đảo danh sách để biến vùng sai thành vùng khác. Quad ngược winding, tự giao, lõm, trùng điểm, cạnh/diện tích gần suy biến phải báo lỗi. Tolerance hình học theo độ phân giải được hiện thực/kiểm chứng ở MVP03.02–MVP03.04; không áp bộ lọc diện tích ≥10% của detector lên mọi vùng chọn tay.

MVP03.02 hiện có `validate_quad_points(corners, width, height)`: nhận đúng bốn điểm normalized, trả bốn tuple pixel theo nguyên thứ tự nhập. Đây là bước kiểm tra điểm/cạnh, **chưa chứng nhận tứ giác hợp lệ đầy đủ**; diện tích, tự giao, lồi và winding thuộc MVP03.03. Caller không được dùng riêng bước này để cho phép homography.

Mốc triển khai ban đầu: D = hypot(W−1,H−1) trong hệ pixel đang kiểm tra; khoảng cách Euclid của mọi cặp điểm ≤1e−6·D trả `DUPLICATE_POINTS`; cạnh theo chu kỳ (kể cả 3→0) ≤1e−3·D trả `SHORT_EDGE`. Sáu cặp được kiểm tra trước bốn cạnh; số điểm sai trả `INVALID_CORNER_COUNT`. Độ dài phải tính sau ánh xạ sang pixel, không dùng Euclid trực tiếp trên u/v vì hai trục có thể khác tỷ lệ. Các ngưỡng tương đối giữ hành vi khi scale cùng vùng; ảnh 2×2 toàn vùng vẫn được nhận, vùng tay nhỏ vẫn được nhận nếu cạnh đủ dài. Đây là baseline triển khai, không phải ngưỡng từ giáo trình hoặc số đo accuracy; detector/debug sẽ dùng lại cùng quy ước và đánh giá thêm trên development.

MVP03.03: `validate_quad(corners, width, height)` nhận bốn normalized có thứ tự, trả pixel theo nguyên thứ tự khi hợp lệ. Dùng lại gate điểm/cạnh. Sau đó chặn ba điểm liên tiếp gần thẳng hàng nếu `abs(cross(b−a,c−b)) ≤ (1e−6·D)·max(length(b−a),length(c−b))`, rồi kiểm tra hai cặp cạnh đối giao/chạm/overlap, diện tích `abs(A) ≤1e−6·D²`, độ lồi (bốn cross cùng dấu) và winding dương. Shoelace được tịnh tiến về p0 và tính qua hai tam giác có dấu; các phép topology dùng pixel chia **cùng D ở hai trục** để giữ hình học và tránh tràn/tổn thất số. Không nhầm chuẩn hóa này với u/v theo từng trục.

Lỗi mới: `DEGENERATE_QUAD` (gần thẳng hàng/diện tích quá nhỏ), `SELF_INTERSECTION` (cạnh đối giao hoặc chạm), `NON_CONVEX_QUAD`, `INVALID_WINDING`. Thứ tự kiểm tra như trên; một vùng có nhiều lỗi sẽ nhận lý do đầu tiên. Kiểm tra đoạn dùng orientation cross, tolerance theo khoảng cách tới đường thẳng và bounding box, gồm chạm đầu mút/overlap. Ngưỡng diện tích/tolerance là baseline dự án để đánh giá thêm, không là quota diện tích 10% của detector. Vùng hợp lệ nhỏ, diamond/phối cảnh vẫn được nhận; reverse/crossed manual không được sửa thứ tự.

MVP03.04: `order_auto_corners(corners, width, height)` chỉ nhận auto proposal chưa có chu kỳ. Chuyển sang pixel nguồn, lấy trung bình bốn đỉnh, sắp atan2, chuẩn hóa area dương, xoay cycle tới min(x+y), tie y rồi x **trên pixel nguồn**; trả bốn normalized, giữ giá trị đỉnh gốc và kiểm tra cuối bằng validate_quad. Không áp cyclic edge gate trước khi sắp vì một đường chéo ngắn trong danh sách lộn xộn chưa phải cạnh. Không dùng hàm này cho handle tay. Đây là bước chuẩn hóa đề xuất, không suy ra hướng chữ và không tạo thêm đỉnh để biến bộ điểm lõm thành vùng hợp lệ. Kích thước warp/ma trận/lấy mẫu ảnh vẫn thuộc MVP03.05–MVP03.06.

Ánh xạ giữ nguyên danh sách:

```text
p0 → (0,0)             p1 → (Wr−1,0)
p2 → (Wr−1,Hr−1)       p3 → (0,Hr−1)
```

Nhãn “trên trái…” là nhãn đích, không bảo đảm hướng đọc chữ khi trang gần hình thoi. Người dùng sửa hướng bằng rotation; không tự tìm hướng chữ. Không ép góc 90° hoặc cạnh song song trên quad nguồn vì có phối cảnh.

## 5. Canvas mapping và DPR

Với vùng canvas CSS Wc×Hc chứa ảnh source W×H theo contain:

```text
s  = min(Wc/W, Hc/H)
ox = (Wc - s*W)/2       oy = (Hc - s*H)/2
cx = (clientX - rect.left) * Wc/rect.width
cy = (clientY - rect.top)  * Hc/rect.height
x  = (cx - ox)/s        y  = (cy - oy)/s
u  = x/(W−1)           v  = y/(H−1)
```

rect là boundingClientRect của vùng canvas không có border/padding; nếu cần viền, đặt trên wrapper. Thông thường Wc/rect.width = Hc/rect.height =1; công thức vẫn xử lý tỷ lệ CSS. Chiều ngược để vẽ handle là `cx=ox+s*u*(W−1)`, `cy=oy+s*v*(H−1)`.

Backing store dùng CSS size×devicePixelRatio để vẽ sắc; pointer vẫn theo CSS pixel, không nhân DPR lần nữa. Khung bitmap có bề rộng sW nhưng vị trí pixel cuối là ox+s(W−1); không nhầm biên khung với chỉ số pixel W. Pointer-down ở letterbox trống không bắt đầu kéo; vùng hit22CSSpx quanh handle vẫn cho phép chạm phần tay cầm nhô ra mép ảnh. Khi kéo tới ngoài ảnh, editor clamp normalized[0,1]; backend vẫn từ chối tọa độ ngoài miền. Nếu thêm transform zoom/pan, phải dùng phép nghịch đảo; không bổ sung zoom/pan nâng cao vào MVP này.

Ca kiểm chứng: ảnh dọc/ngang, offset contain, CSS resize, DPR1/2, bốn góc biên và round-trip pointer→normalized→display; xem bằng chứng04–06 bên dưới.

**MVP08.04 đã thực hiện17/10/2026:** `frontend/src/components/cornerGeometry.ts` có createContainTransform, sourceToCanvas/canvasToSource, normalizedToSource/sourceToNormalized, normalizedToCanvas/canvasToNormalized, clientToCanvas và getCanvasBackingSize. Transform frozen giữ source/CSS dimensions/scale/offset; giữ subpixel, không nhân DPR vào pointer. Source dimensions safeinteger≥2, CSS/rect/DPR hữu hạn dương, điểm hữu hạn; sai ném RangeError. Đây là phép đổi tọa độ liên tục: ngoài bitmap có thể ra normalized ngoài[0,1], **không tự clamp/hit-test/sort/validate quad**. Các transform vẫn liên tục; editor08.05–06 hiện dùng hittest/moveCorner riêng để bỏ blankletterbox và clamp drag. Backend vẫn validate chặt.

Backing width/height=max(1,round(CSSsize×DPR)); dùng scaleX=backingWidth/CSSwidth và scaleY tương ứng sau làm tròn, gọi ctx.setTransform thay vì scale tích lũy khi resize. Canvas contentbox khôngborder/padding; CSStransform được xử lý bằng clientrect ratios, chưa zoom/pan. 27tests bằng native Node24 (`npm.cmd test`, không dependency mới), typecheck/build đạt. Browser canvas thật8tổhợp dọc/ngang×2CSSsize×backingDPR1–2,22lượtdraw/5điểm mỗi lượt, max roundtrip5.684e−14CSSpx<1; đọc pixel xanh ở đúng handlecenter, console trống. Probe ép DPR đầu vào1/2, devicePixelRatio thật1; không claim đã thử thiết bịHiDPI riêng. Đây là nghiệm thu08.04; editor05–06 và checkpoint08-C2 hiện đã đạt như mục dưới. [Progress](progress.md).

### Editor và quad nháp — MVP08.05–06

Mục này ghi mốc05–06; hành vi lưu/xác nhận/render hiện hành ở mục12 bên dưới.

CornerEditor đã nối vào SourcePreview. Ảnh normalizedPNG nằm trên img native/object-fit contain; canvas chỉ vẽ mask ngoài polygon bằng evenodd và stroke, không encode hoặc đổi pixel nguồn. Bốn button44CSSpx/ID0–3 giữ nguyên thứ tự; góc lấy từ persisted config nếu có, nếu chưa thì inset5% làm nháp. SourcePreview remount editor theo page_id/revision/normalized_artifact_id; đổi trang/revision/nguồn không giữ góc của trang cũ. ResizeObserver đo contentbox thật, window resize/matchMedia theo DPR, backing và ctx.setTransform được tính lại. Canvas không border/padding; wrapper chừa24px cho handle. Loading/error/retry và kiểm dimensions ảnh thật trước bật editor; chỉ GET nguồn, không PUT config/render.

hitTestCorner chọn handle gần nhất trong22CSSpx, tie giữ ID thấp; không dựa vào thứ tự vẽ để đổi ID. Pointer Events nhận primary/button0; setPointerCapture trên stage, giữ offset điểm nắm để tránh nhảy góc khi nhấn lệch tâm. pointermove/up chỉ nhận cùng pointerId; moveCorner đổi riêng một điểm và clamp normalized[0,1], không sort. Pointerup chốt nháp và release; pointercancel/lostcapture/Escape/windowblur/focus ra ngoài/resize/DPR đổi hủy lần kéo, khôi phục snapshot góc/dirty trước pointerdown. Cleanup unmount bỏ listener; DOM tự giải phóng capture khi stage bị bỏ. Nhấn không kéo (delta≤1e−6CSSpx) không đổi góc/dirty vì sai số float. Empty letterbox không nhảy góc. Bàn phím Arrow dịch1CSSpx, Shift+Arrow10CSSpx; Escape hủy kéo. Invalid draft vẫn hiện để sửa, stroke lỗi kèm message, không chỉ đổi màu.

validateDraftQuad là preflight giao diện, backend validate_quad vẫn là gate cuối. Cùng thứ tự/đơn vị:4điểm finite/normalized bounds →6khoảng cách≤1e−6D →4cạnh≤1e−3D →near-collinear cross →giao cạnh đối →shoelace |A|≤1e−6D² →lồi →windingdương. D tính trên pixel nguồn W−1/H−1; topology chia cùng D hai trục. Không dùng khoảng cách trực tiếp trên u/v hoặc quota vùng10% của detector. Code INVALID_CORNER_COUNT/INVALID_POINT/POINT_OUT_OF_BOUNDS/DUPLICATE_POINTS/SHORT_EDGE/DEGENERATE_QUAD/SELF_INTERSECTION/NON_CONVEX_QUAD/INVALID_WINDING có message; không tự chữa topology.

Nghiệm thu17/10:51frontendtests (24mới),216coregeometry-Werror,936quad/6kíchthước đối chiếu codes khớp. Browser sản phẩm:mouse/capture/clamp/bowtie/keyboard,2nguồn portrait480×640/landscapefixture4×2×3viewport320/768/1440; maxhandleerror≈.021CSSpx<1, normalizedpoints không đổi khi resize, không tràn ngang. Probe component thật:touch synthetic, cancel/lostcapture/Escape/blur/secondary đều release/restore đúng; forced windowDPR1/2 giữgóc và maskalpha ngoài140/trong0. Chưa kiểm thiết bị touch/HiDPI vật lý; các sự kiện touch được dựng ở trang thử, capture dùng pointer đang active thật. Metadata4session/7page/21hashsource trước/sau nguyên. Checkpoint08-C2 đạt, next08.07 táchdraft/persisted và lưu/xác nhận; hiện nháp chỉ tồn tại cục bộ, chưa renderUI/M2. [Progress](progress.md).

## 6. Warp và hướng ảnh

Đổi corners normalized thành pixel source, validate trước OpenCV. Ước lượng theo đặc tả:

```text
w0 = max(length(p1−p0), length(p2−p3))
h0 = max(length(p3−p0), length(p2−p1))
```

Làm tròn kích thước, tối thiểu 2; giảm đồng thời hai chiều nếu cạnh dài vượt 2400. Không upscale vượt mức ước lượng ngoài làm tròn/minimum cần thiết. `aspect_policy="estimated"` là lựa chọn duy nhất của MVP; không ép A4 cho warp. Kiểm tra dimensions trước cấp buffer: mỗi chiều ≤2400, tối đa 5.760.000 pixel; kiểm tra ma trận H hữu hạn. Dùng getPerspectiveTransform/warpPerspective với INTER_LINEAR. Tỉ lệ giấy chỉ được ước lượng từ ảnh, không suy ra khổ vật lý/DPI chính xác.

MVP03.05 đã hiện thực `estimate_warp_size(corners, width, height)` trong geometry.py: normalized → validate_quad → cạnh pixel → half-up `floor(length+0.5)`, min2; nếu vượt2400, giảm cả hai dimensions đã làm tròn theo cùng tỷ lệ, dùng half-up nguyên chính xác như resize. Trả `(W,H)` nguyên; kiểm tra pixel cap trước tạo buffer. Công thức dùng khoảng cách giữa tâm pixel, không cộng1: source toàn ảnh101×51 cho100×50, source2×2 vẫn2×2 do min2. Đây là quy ước estimated của đặc tả, không cố giữ nguyên dimensions của source hoặc đặt ratio A4.

MVP03.06 đã có `compute_homography(corners, width, height)` trả `(H, (Wr,Hr))`. H là float64 3×3 **source→đích**, tính từ bốn cặp theo thứ tự p0..p3 và đích `(0,0),(Wr−1,0),(Wr−1,Hr−1),(0,Hr−1)`. Source points chuyển float32 theo yêu cầu OpenCV nhưng không làm tròn thành pixel nguyên. Gate topology chạy trước OpenCV; ma trận phải hữu hạn/khả nghịch (`slogdet`), nếu không báo `INVALID_HOMOGRAPHY`. Không tự sắp lại góc tay. Tính kích thước/ma trận không tự xác nhận góc; service vẫn cần confirmed/revision ở task tương ứng.

`warp_document(source, corners)` nhận BGR uint8 HWC3 sau EXIF, dimensions≥2 và tối đa16MP; trả mảng BGR độc lập. Kiểm tra nguồn/quota/hình học/size/H trước lấy mẫu và cấp buffer ảnh đích. Gọi warpPerspective với H thuận (không WARP_INVERSE_MAP), `INTER_LINEAR`, `BORDER_REPLICATE` để lấy mẫu ngược và tránh viền đen nhỏ ở biên nguồn do sai số số học. Giữ nguồn, không EXIF lại, không lọc/xoay/preview. Lỗi thêm `INVALID_SOURCE`, `TOO_MANY_PIXELS`, `INVALID_WARP_SIZE`, `WARP_FAILED`; API/HTTP mapping còn chờ. Docs OpenCV: [biến đổi hình học](https://docs.opencv.org/4.x/da/d54/group__imgproc__transform.html).

AUX03.01: quota16MP vẫn cho phép cạnh≥32767, vượt SHRT_MAX của CPU remap. Trường hợp này giữ nguyên nguồn, chia rectangle đích và lấy inverse-map bốn góc để chọn ROI nguồn<32767 có halo một pixel cho bilinear. H_local=T(−gốc đích)·H·T(gốc nguồn); warpPerspective từng ROI và ghép ảnh đích, vẫnINTER_LINEAR/BORDER_REPLICATE/cap2400/5.76MP. Không resize source hoặc thay góc/tham số. Nguồn thường dùng đường warp trực tiếp cũ. Source40.000×400/400×40.000 và crop offset35.000 đã có hồi quy; chi tiết [audit03](audit-phase-03.md).

`experiments/geometry_demo.py` là CLI minh họa offline: normalize input gốc theo quota upload/EXIF, --corners JSON normalized sau EXIF (mặc địnhfull), validate manual order, tạo source.png/overlay.png/warp.png/metadata.json vào thư mục mới. Overlay đánh số0..3 và chỉ làm tròn khi vẽ; metadata giữ điểm thực/H source→warp, dimensions/hashes của đúng PNG, interpolation/border/CV version. Ghi exclusive, metadata cuối; lỗi không tạo success directory nếu input/quad sai. Đây không phải detect/confirmed/revision hoặc render modes; nguồn PNG lưu nội bộ>15MiB vẫn theo source contract ở pipeline, không nhập lại qua CLI raw-upload cap.

Rotation là số độ **chiều kim đồng hồ**, chỉ 0/90/180/270, thực hiện sau lọc bằng rotate90, không nội suy. 90/270 đổi width/height của render; không sửa corners hoặc dimensions source. Homography sửa phối cảnh của trang gần phẳng; không làm phẳng các dòng chữ cong do nhàu.

## 7. Full config và preset

Ba preset bên dưới đầy đủ cho cấu hình khởi đầu, không phải tham số tối ưu đã đo. `corners=null`, `confirmed=false` ở trang mới; khi xác nhận, thay bằng quad hợp lệ. Preset không tự xác nhận vùng cắt.

### Color

```json
{
  "corners": null,
  "confirmed": false,
  "mode": "color",
  "rotation": 0,
  "denoise": {"method": "none", "kernel": 3},
  "contrast": {"method": "none", "clip_limit": 2.0, "tile_grid": [8, 8]},
  "threshold": {"method": "adaptive_gaussian", "block_size": 31, "c": 10},
  "geometry": {"aspect_policy": "estimated", "max_long_edge": 2400}
}
```

### Gray

```json
{
  "corners": null,
  "confirmed": false,
  "mode": "gray",
  "rotation": 0,
  "denoise": {"method": "none", "kernel": 3},
  "contrast": {"method": "clahe", "clip_limit": 2.0, "tile_grid": [8, 8]},
  "threshold": {"method": "adaptive_gaussian", "block_size": 31, "c": 10},
  "geometry": {"aspect_policy": "estimated", "max_long_edge": 2400}
}
```

### BW

```json
{
  "corners": null,
  "confirmed": false,
  "mode": "bw",
  "rotation": 0,
  "denoise": {"method": "median", "kernel": 3},
  "contrast": {"method": "none", "clip_limit": 2.0, "tile_grid": [8, 8]},
  "threshold": {"method": "adaptive_gaussian", "block_size": 31, "c": 10},
  "geometry": {"aspect_policy": "estimated", "max_long_edge": 2400}
}
```

| Nhóm | Giá trị/kiểm tra | Khi áp dụng |
|---|---|---|
| mode | color/gray/bw | Quyết định channels/render branch |
| denoise | none/median/gaussian; kernel 3 hoặc 5 khi lọc | Cả ba mode; none không blur |
| contrast | none/clahe; clip_limit hữu hạn trong [1,4]; tile_grid cố định [8,8] | Gray và gray trước threshold BW; color inactive theo MVP |
| threshold | otsu/adaptive_gaussian | Chỉ BW |
| block_size | Số nguyên lẻ trong [3,151], ≤min(Wr,Hr) khi Adaptive active | Ảnh nhỏ không phù hợp trả INVALID_CONFIG; chọn block nhỏ hoặc Otsu, không tự đổi phương pháp |
| c | Số nguyên trong [−20,30] | Chỉ Adaptive active |
| geometry | estimated; max_long_edge=2400 | Cố định ở MVP; giới hạn 1200–3000/A4 của bản gốc đã được rút gọn |
| rotation | 0/90/180/270 | Sau mode/filter |

Field inactive vẫn hiện trong full config và được kiểm tra kiểu/miền cơ bản; không tham gia tính ảnh. Kiểm tra phụ thuộc kích thước chỉ áp dụng cho bước active. Otsu trả ngưỡng từ phép chạy thật; không đọc block_size/c như ngưỡng Otsu. Chọn color giữ màu, CLAHE màu/Lab trong bản gốc được hoãn theo phạm vi MVP. Không có sharpen/deskew/illumination trong config lõi; illumination chỉ bổ sung khi làm OPT-A và cập nhật hợp đồng.

Frontend gửi full config. Nếu trường thiếu, backend lấy mặc định schema từ preset của mode yêu cầu (thiếu mode thì color), kể cả trường con; không merge giá trị config cũ. Giá trị sai bị từ chối, không coi null/sai enum là “thiếu” để tự chữa. Response trả đầy đủ effective_config và thông tin inactive. Preset/reset hay đổi mode không lọc chồng lên ảnh kết quả cũ: mỗi render bắt đầu từ source và config hiện tại.

confirmed là boolean; kernel/block/rotation/revision là số nguyên, không nhận boolean hoặc chuỗi thay số. u/v và clip_limit là số hữu hạn. Schema lõi từ chối field ngoài hợp đồng, thay vì âm thầm bỏ qua cấu hình của chức năng đã hoãn.

confirmed=true bắt buộc corners là quad hợp lệ; corners=null chỉ hợp lệ khi confirmed=false. Quad đang kéo sai topology là draft UI, không được lưu như một cấu hình hợp lệ để render/export.

MVP04.01 đã hiện thực trong `backend/app/processing/config.py` bằng Pydantic2 đã khóa trong môi trường. `get_preset(mode="color")` trả PageConfig mới, đầy đủ và draft; `parse_config(data, source_size=None, warp_size=None)` trả snapshot PageConfig/nested models frozen, tuple corners/grid. Scalar numbers dùng strict/finite, extra bị forbid; trường inactive cũng phải đúng kiểu/miền. `model_dump(mode="json")` xuất full config với list tọa độ/grid, không có metadata server hoặc inactive_fields. Không đọc/sửa ảnh, không HTTP/DB và không thêm dependency.

Defaults được bổ sung từ preset của mode yêu cầu (thiếu mode→color), kể cả nested fields; null không được coi là thiếu. Full config đổi mode giữ các giá trị đã gửi; muốn reset thì dùng get_preset, không âm thầm merge config cũ. `config.inactive_fields` là tuple dotted paths: denoise.kernel khi none; cả contrast khi color, chỉ clip/grid khi gray/BW contrast none; cả threshold khi color/gray, chỉ block/c khi BW Otsu. Inactive phản ánh mode/method, không phản ánh confirmed=false, và không xóa dữ liệu khỏi snapshot.

Với corners khác null, **phải truyền source_size=(W,H) thật sau EXIF**; reuse validate_quad, giữ cycle/handles, gồm cả config confirmed=false. Không giả dimensions vuông để kiểm tra topology/tolerance. Truyền warp_size=(Wr,Hr) khi biết kích thước warp, trước bước filter/threshold: dimensions nguyên2..2400; BW Adaptive đòi block_size≤min(Wr,Hr). Chưa có warp_size thì chỉ kiểm tra kiểu/miền; preset không chứng minh cấu hình đã render được trên một ảnh cụ thể. Otsu và threshold inactive không áp fit-block. Không tự co block hoặc đổi phương pháp. Render service sau này vẫn phải kiểm confirmed/revision và truyền dimensions thực; schema không tự xác nhận, áp EXIF hay chạy lọc.

Input sai trả `ConfigValidationError(ValueError)` với code `INVALID_CONFIG` và thông báo field/lý do; parse_config revalidate cả PageConfig instances (không tin model_copy/update chưa kiểm chứng). Không dùng model_copy(update=...) như bước validation; chỉnh full JSON rồi gọi parse_config lại. Chuẩn schema/API detailed và revision vẫn thuộc MVP07.01/service tasks. Đối chiếu [Pydantic validators](https://docs.pydantic.dev/latest/concepts/validators/) và [strict mode](https://docs.pydantic.dev/latest/concepts/strict_mode/).

MVP04.02: `apply_denoise(warped_bgr, config.denoise)` trong enhancement.py nhận BGRuint8 HWC3, dimensions2..2400 của fullwarp (khônganalysis/preview), trả mảng độc lập cùngshape/dtype/kênh. Lọc trước mode conversion; Gray và gray trước threshold BW dùng kết quả BGR này. None trảcopy; Median dùng medianBlur kernel3/5, borderREPLICATE nội bộ OpenCV; Gaussian dùng GaussianBlur kernel3/5, sigmaX=0, borderREFLECT_101. Không threshold/resize/tự đổikernel dù warp nhỏ2×2; padding cho phép kernel lớn hơn ảnh. Revalidate DenoiseConfig; errors INVALID_CONFIG, INVALID_RENDER hoặc FILTER_FAILED, khôngHTTP/DB/I/O.

Ảnh thử synthetic cho thấy Median3 xóa chấm muối tiêu và cả nét rộng1pixel, Gaussian3 đưa nétđen0 thành128/mềm nét; None giữ nguyên. Đây là kiểm chứng hành vi/rủi ro chọn lọc, không kết luận chất lượng ảnh thật hoặc preset tối ưu. Giữ khả năng chọnNone, kernel3/5 như hợp đồng; source không sửa và Color defaultNone. Tham chiếu [OpenCV image filtering](https://docs.opencv.org/4.x/d4/d86/group__imgproc__filter.html).

MVP04.03: `render_color(filtered_bgr)` copy BGR sau lọc, giữ nguyên mọi pixel/màu highlight; không đọc contrast hoặc áp CLAHE màu/Lab. `render_gray(filtered_bgr, config.contrast)` nhận cùng full-warp BGR2..2400, dùng BGR2GRAY (Y≈0.114B+0.587G+0.299R), trả HxW uint8 độc lập. Contrast none giữ gray thô; clahe dùng createCLAHE clipLimit1..4, tileGridSize=(8,8). Grid là số ô chia ảnh, không phải ô8pixel; padding nội bộ vẫn cho phép ảnh2×2. Cả hai không sửa source, resize, threshold hoặc xoay; dispatcher chọn mode và validation toàn PageConfig ở MVP04.06. Gray revalidate ContrastConfig kể cả clip/grid inactive; lỗi INVALID_RENDER/INVALID_CONFIG/MODE_FAILED. Tham chiếu [OpenCV chuyển màu](https://docs.opencv.org/4.x/de/d25/imgproc_color_conversions.html) và [CLAHE](https://docs.opencv.org/4.x/d5/daf/tutorial_py_histogram_equalization.html).

Ảnh nghiệm thu synthetic640×300 có chữ tiếng Việt/dấu và highlight vàng, denoiseNone, so Color/GrayNone/GrayCLAHE2 trên cùng vùng: Color bằng source, Gray một kênh; CLAHE thay170753pixel. Pixel highlight(40,95) BGR[130,235,255]→gray229→CLAHE233. Đã xem comparison/metadata trong experiments/results/mvp04-03-modes/ (ignored); ảnh giữ đủ dấu, CLAHE đổi cả nền gradient. Đây là bằng chứng hành vi, không phải độ chính xác hay đánh giá ảnh chụp thật. Checkpoint04-C1 đạt với132tests config/filter/modes tại mốc04.03.

MVP04.04: `apply_otsu(gray)` nhận gray uint8 HxW của fullwarp đã lọc/chỉnh tương phản, dimensions2..2400; trả `(bw, actual_threshold)` với BW uint8 độc lập, cùngsize/chỉ0 hoặc255. Dùng THRESH_BINARY|THRESH_OTSU, pixel≤t thành0, >t thành255; t là giá trị thực CV trả, không lấy block_size/C làm ngưỡng. Ảnh hằng có thể t=0; không bịa ngưỡng hoặc tự đảo polarity. Không thêm blur/CLAHE/resize. Lỗi INVALID_RENDER hoặc THRESHOLD_FAILED. Config đầy đủ phải được parse trước; helper không có tham số config vì Otsu không dùng block/C. Ngưỡng được ghi cùng effective_config trong metadata thử, dispatcher04.06 sẽ nối metadata render.

MVP04.05: `apply_adaptive_gaussian(gray, config.threshold)` nhận cùnggray chuẩn bị, trả BW uint8 độc lập/cùngsize/chỉ0/255. Ngưỡng theo từngpixel là trung bình lân cận có trọng số Gaussian trừC; CV dùng BORDER_REPLICATE|BORDER_ISOLATED. Revalidate ThresholdConfig, method phải adaptive_gaussian, blocklẻ3..151 và≤min(W,H) thật, C nguyên−20..30. Quáblock báo INVALID_CONFIG, kể cả ảnh2×2 không có block hợp lệ; người dùng chọn block nhỏ hơn hoặc Otsu. Không tự đổi block/phương pháp, không threshold màu, không trả một giá trị global giả cho Adaptive. Input/CV lỗi cùng INVALID_RENDER/THRESHOLD_FAILED. Tham chiếu [OpenCV threshold](https://docs.opencv.org/4.x/d7/d4d/tutorial_py_thresholding.html) và [adaptiveThreshold API](https://docs.opencv.org/4.x/d7/d1b/group__imgproc__misc.html).

Nghiệm thu04.04–05 trên cùng nội dung tiếng Việt tổng hợp640×300, sángđều/bóng gradient, Median3/contrastNone: Otsu ngưỡng182/155; nềntrái(10,10) của ảnhbóng thành0 vớiOtsu,255 vớiAdaptive31/C10. Lưu so block31/51 vàC5/10/20: ởC10 đổi253pixel khiđổi block; C5→20 block31 đổi1338pixel, C20 làm đứt nét nhạt khi xem trực tiếp. Ảnh8×8: Adaptive31 lỗi, Adaptive3 chạy, Otsu t40;2×2 Adaptive3 lỗi. Artifacts experiments/results/mvp04-04-otsu/ và mvp04-05-adaptive/ ignored, config/hash/số đo thật trongmetadata. Đây là kiểm chứng hành vi, không đánh giá chất lượng ảnhchụp thật hoặc accuracy. Tại mốc04.05 có171tests enhancement/config đạt.

MVP04.06: `enhance_document(warped_bgr, config, source_size=None)` nhận fullwarp BGR2..2400 vàPageConfig, dùng parse_config vớiwarp_size thật trướcfilter vàsource_size sauEXIF nếucornersnonnull. Denoise→Color hoặcGray/optionalCLAHE→BWthreshold nếumodeBW→xoay90 theo chiều kimđồnghồ. Không xửlýcontrast/thresholdinactive, khôngfilterchồngkếtquảtrước. Rotation0 giữhướng,90/270đổiW/H, dùngcv2.rotate khôngnội suy;source/config/corners giữnguyên. EnhancementResult trả image uint8 độc lập/contiguous, effective_config frozen vàotsu_threshold thực hoặcNone (Color/Gray/Adaptive). Input/params/CVerrors nhưhelper, thêmROTATION_FAILED. Core khôngwarp/EXIF/I/O/HTTP/DB/caching hoặc tựconfirmed; service sẽgateconfirmed/revision. Caller chịu trách nhiệm warp thực thuộcsource/quad đãchọn.

MVP04.07: CLIenhancement_demo chuẩn hóa rawsource theoquota/EXIF, quadtay/fullảnh mặc định, computeH/warp rồichạy4bảnColor/Gray/BWAdaptive/BWOtsu. Configdraft chứa cornersnguồn/rotation/preset đầyđủ, --denoise overridechung hoặc--no-gray-clahe đểso. PNGColorRGB,Gray/BWL, metadatahash/size/fullconfig/inactive/Otsut. Comparison maxedge800 tạo từfullrender; fullảnh khôngthu nhỏ. Validation/renders xong trướcghi, exclusive vàmetadata cuối; ảnhnhỏ nếuAdaptive31khôngfit báo lỗi, khôngfallback/skipnhánh. Đãso2ảnhdevelopment cùngdoc +2synthetic/bảnNone vớifulltextcrops, chưaaccuracy/tập testcuối. Xem [algorithm-notes](algorithm-notes.md) và [audit04](audit-phase-04.md);193config/enhance+7CLI, toànbackend571đạt,12rotationoutputs/cổng04/C2 đạt. Tiếp theo05.01.

## 8. Revision, xác nhận và request cũ

- Trang mới có revision=0 do server cấp, config chưa xác nhận. MVP07.01 ngày17/10/2026 sửa số1 trong bản cũ theo taskMVP07.05 của checklist hiện hành; chưa có dữ liệu nhập cần migrate. `revision` là metadata server, không đặt trong phần config mà client tự ghi.
- PUT config gửi `expected_revision` và full config. So sánh sau chuẩn hóa; config thay đổi thì tăng revision một lần khi commit thành công, gồm corners/confirmed/mode/filter/rotation/geometry và tham số inactive. No-op giữ revision. Đổi tên/thứ tự trang không tăng revision ảnh.
- Kéo góc làm draft `confirmed=false`; không xuất draft. Detect chỉ đề xuất, không tự ghi đè config đã xác nhận. Người dùng xác nhận quad hợp lệ bằng cập nhật config.
- Render yêu cầu confirmed=true, corners hợp lệ và expected_revision khớp. Chụp snapshot source/config/revision trước xử lý, kiểm tra revision lại trước commit; conflict trả 409, không ghi kết quả cũ làm hiện hành.
- Render không tự tăng revision. Artifact full/preview/debug và response gắn page_id/revision; width/height response là render sau rotation. UI chỉ nhận đúng trang và revision đang chờ, bỏ response cũ khi đổi trang/config.
- Full render, preview, histogram, config và timing phải thuộc cùng phép chạy. Histogram trước threshold lấy từ gray full render tại bước đó; không lấy histogram preview để đại diện ảnh khác kích thước.
- Export dùng snapshot page_id/revision/order, chỉ lấy full render đã xác nhận/khớp revision. Khóa mutation tài liệu trong lúc export, giải phóng cả khi lỗi; reopen không giữ khóa cũ. Không xuất từ thumbnail, preview hoặc config đang kéo chưa lưu.

MVP không có cache bền hoặc lịch sử sửa đầy đủ. SQLite lưu metadata/config/order; tệp lưu source/render/debug/export. Mọi tên file vật lý do hệ thống cấp, không ghép tên upload thành đường dẫn. Đường dẫn thực tế hiện có theo [settings.py](../backend/app/settings.py): `data/scanner.sqlite3`, `data/tmp`; tên DB này thay tên minh họa `data/app.sqlite3` trong đặc tả gốc, không đổi mô hình lưu trữ.

## 9. Detection và mô tả biên

Mục tiêu là đường bao toàn trang giấy, gồm lề; không lấy khối chữ làm vùng trang. Biên chữ/bảng/bóng/nếp gấp đều có thể xuất hiện trong Canny; findContours không tự nhận biết đường bao nào là giấy. Cần kiểm tra hình học và xếp hạng, giữ fallback tay khi cảnh mơ hồ.

Preset hiện hành sau AUX05.01: analysis edge1200; Gaussian5×5/sigma0/reflect101; Canny aperture3/L2true, đúng3cặp revised20/60,50/150,75/200. Closing3×3 mộtlần, RETR_LIST/CHAIN_APPROX_SIMPLE/top30contour/trial, Douglas–Peucker epsilon/P=.015/.02/.03. Nếu cả3Canny không có quad hợp lệ, thử thêm tối đa1RegionTrial Otsu/RETR_EXTERNAL; không dùng nhánh này khi Canny đã có quad. Gate area contour/Q≥10%WaHa, cạnh≥5%min(Wa,Ha), topology và source mapping giữ nguyên. Baseline50/150,75/200,100/250 và không region vẫn tái hiện riêng. Kernel3 chỉ là ablation được ghi metadata, default5. Đây là preset development, không phải tham số tối ưu; Douglas–Peucker không phải MPP. [Quyết định revision01](detection-revision-01.md).

MVP05.01 (15/10/2026): `prepare_analysis(source_bgr)` nhận nguồn BGR uint8 sauEXIF, mỗi chiều≥2, tối đa16MP; trả AnalysisImages frozen metadata với source_size=(W,H), bgr/gray/blurred độc lập. Reuse resize_to_max_edge1200/INTER_AREA/half-up/khôngupscale rồi BGR2GRAY và Gaussian5×5/sigma0/BORDER_REFLECT_101 rõ ràng. Nếu analysis có chiều<2 báo ANALYSIS_TOO_SMALL trước geometry; không ép chiều2 để thay aspect. `analysis_size` lấy kích thước bgr thực, `to_source(point)` gọi pixel_to_normalized theo Wa−1/Ha−1 rồi normalized_to_pixel theo W−1/H−1, giữ subpixel/bounds; không chia đều cho r. Lỗi INVALID_SOURCE/TOO_MANY_PIXELS/ANALYSIS_FAILED rõ, không EXIF lại/CLAHE/render/I/O.

MVP05.02: `create_edge_trials(analysis.blurred)` nhận gray uint8 HxW, mỗi chiều2..1200; chạy đúng3cặp preset rồi trả tuple EdgeTrial(trial_id,thresholds,edges,closed). ID ổn định canny_50_150/canny_75_200/canny_100_250; Canny aperture3/L2true, không blur lại. Closing rect3×3/1iteration, BORDER_CONSTANT với giá trị morphology trung tính mặc địnhCV; không gán borderValue0 cho cả dilation/erosion. Edges/closed uint8 cùngsize/chỉ0/255, buffers riêng và input nguyên. Closed dành cho contour ở05.03; edges raw dành cho e ở05.04, không trộn trial. Input lỗi INVALID_ANALYSIS; CV lỗi EDGE_FAILED, không trả partialsuccess. Helper này chỉ tạo edge trials, không tạo candidate/score/fallback hoặc tựconfirmed. Tham chiếu [Canny](https://docs.opencv.org/4.x/da/d22/tutorial_py_canny.html), [closing](https://docs.opencv.org/4.x/d9/d61/tutorial_py_morphological_ops.html), [morphology border](https://docs.opencv.org/4.x/d4/d86/group__imgproc__filter.html).

Tại mốc nghiệm thu05.01–02: 33tests detection và toànbackend604đạt; runtime dọc1536×2048→900×1200, ngang2000×1001→1200×601 và nhỏ420×300 khôngupscale, mapping qua dimensions thực. Bốn runs real/synthetic lưu44PNG/hash/shape tại experiments/results/mvp05-01-02/ (ignored), đã xem gray/blur/rawedges/closing. Ca hở lớn vẫn hở sauclosing; ngưỡng cao bớt cả chữ lẫn nền, closing làm dày cả nét nền. Hai task kế tiếp được nối dưới đây.

MVP05.03: `generate_candidates(analysis,trial)` kiểm binary uint8 edge/closed cùng dimensions thực/ID khớp preset; findContours trên closed với RETR_LIST/CHAIN_APPROX_SIMPLE. Xếp diện tích giảm dần, tie index tìm contour, xét tối đa30/trial; contour có area<.10WaHa hoặc chu vi≤0 bị loại trước approximation, lưu một attempt epsilon=null. Contour còn lại thử đủ epsilon/P=.015/.02/.03. CandidateBatch giữ total_contours/considered_contours/attempts; mỗi ContourCandidate chứa trial/thresholds, source_size/analysis_size, contour_index, contour_px có thứ tự, epsilon_ratio, polygon_px gốc, số đỉnh, corners hoặc rejection_reason. Không dedup các epsilon/trial ở task này.

Polygon phải đúng4đỉnh; chỉ đảo chiều winding khi cần, kiểm validate_quad trên cycle hiện có trước sắp góc. Sau đó gate A(Q)≥.10WaHa và từng cạnh≥.05min(Wa,Ha). Không ép 90°/song song hoặc thay bằng minAreaRect; tự giao/lõm/suy biến có mã loại. order_auto_corners chuẩn hóa start theo pixel **nguồn**, giữ normalized W−1/H−1 để tránh tie bị đổi do làm tròn resize khác nhau ở hai trục. Coordinates contour/Q, area/cạnh lọc là của analysis. Input lỗi INVALID_TRIAL/INVALID_ANALYSIS; CV lỗi CANDIDATES_FAILED.

MVP05.04: `describe_candidate(candidate,trial)` chỉ nhận candidate hợp lệ, kiểm lại validate_quad, raw trial ID/thresholds/dimensions và contour hữu hạn/trong ảnh/area-perimeter>0 trước chia. CandidateDescription giữ candidate cùng chu vi contour px, số đỉnh4, bốn độ dài cạnh px và góc đổi hướng rad theo thứ tự canonical corners. Góc atan2(cross incoming/outgoing,dot), x phải/y xuống, cycle lồi dương; geometry flags is_convex=true/self_intersects=false là kết quả validator, không dự đoán giấy. a=A(Q)/(WaHa); f=min(A(C),A(Q))/max(A(C),A(Q)). Sai candidate/trial báo INVALID_CANDIDATE/INVALID_TRIAL.

Quy ước lấy mẫu cụ thể: cạnh dài L có n=max(2,ceil(L/2)+1) mẫu linspace gồm hai đầu; spacing≤2pixel. Góc chung được tính trên cả hai cạnh kề, nhất quán cho mọi mẫu số. Mẫu p được hỗ trợ nếu có pixel trắng của **raw edges cùng trial** cách p theo Euclid≤2pixel; kiểm tâm pixel lân cận, không dùng khoảng cách Chebyshev hoặc ảnh closed. Giữ edge_sample_counts/edge_supported_counts/edge_support_per_side. e=sum(m_i)/sum(n_i); b=border_sample_count/sum(n_i), mẫu sát mép khi min(x,y,Wa−1−x,Ha−1−y)≤2pixel. S=clip(.45a+.35e+.20f−.15b,0,1). Không thêm trọng số chu vi/góc, không gọi S là xác suất/accuracy; metadata giữ dimensions/trial tại candidate.

Nghiệm thu05.03–04:64tests detection/635backend đạt;10cases×3trials và map kiểm soát tại experiments/results/mvp05-03-04-verified/ (ignored). Rectangle/diamond/skew hợp lệ, malformed có lý do; e mất cạnh dài207/284 thay vì mean4. img_003 có quad score.502372, img_004 chưa quad; ca khung giả có score.975859 nhưng sai. Checkpoint05-C1 đạt;05-C2/cổng05 chờ. Đây là core candidate/scoring và evidence cục bộ, chưa NMS/chọn đề xuất/fallback/debug pipeline/API/UI. Không tự confirm, sửa nguồn hoặc dùng analysis để warp/render.

Contour/Q là biểu diễn có tọa độ; chu vi/cạnh/góc/độ lồi là mô tả biên, diện tích là đặc trưng vùng. Độ dài/đơn vị và field debug theo tài liệu phân tích; luôn ghi Wa/Ha/trial. e đo trên Canny **trước closing**, tổng theo tổng số mẫu được hỗ trợ/tổng số mẫu, không trung bình bốn cạnh không trọng số. Giữ `S=clip(0.45a+0.35e+0.20f−0.15b,0,1)`, IoU>0.95 loại trùng.

S≥0.60 đề xuất; 0.40≤S<0.60 đề xuất kèm cảnh báo; S<0.40 hoặc không có ứng viên thì `manual_required`, corners=null. Score không phải accuracy/xác suất. UI fallback vùng cách mép 5% hoặc toàn ảnh đều là draft chưa xác nhận; không dùng minAreaRect để giả bốn góc phối cảnh.

Sobel+ngưỡng là baseline giải thích/so sánh với Canny, không phải detector chạy nối tiếp bắt buộc hoặc chế độ UI mới. Nhánh Otsu vùng sáng đã được triển khai có điều kiện trong AUX05.01 phía dưới, dùng chung validate/scoring và giữ giới hạn trên development. Mã chuỗi Freeman, Fourier, Hu và sai số fit theo khoảng cách vẫn là hướng nghiên cứu, không bắt buộc trong lõi MVP; không tự thêm descriptor hoặc trọng số vào baseline.

### Điều chỉnh hiện hành — AUX05.01, 15/10/2026

Các đoạn MVP05.01–04 phía trên ghi mốc baseline đã nghiệm thu. User đã chấp nhận bổ sung nhánh vùng tại revision01; phần dưới là hợp đồng triển khai hiện hành. Không áp raw mask của vùng làm nguồn warp hoặc thay source.

`prepare_analysis(source_bgr, gaussian_kernel=5)` cho đúng kiểu int3/5, lưu AnalysisImages.gaussian_kernel; sai preset/kernel trả INVALID_ANALYSIS_CONFIG. `create_edge_trials(blurred,preset='baseline',gaussian_kernel=5)` vẫn mặc định baseline để tái hiện các phép chạy trước, cho preset revised đúng3cặp mới. Kernel5 giữ ID canny_low_high; kernel3 dùng canny_g3_low_high. Caller trực tiếp phải truyền metadata đúng blur; entry bên dưới tự truyền từ analysis để tránh nhầm kernel.

**Entry dùng cho các task kế tiếp:** `collect_candidates(analysis,preset='revised')` trả tuple TrialCandidates(trial,batch). Baseline trả đúng3EdgeTrial không region; revised trả3EdgeTrial, thêm1RegionTrial chỉ nếu cả3batch.candidates rỗng. Không retry ngưỡng/kernel, không thử Otsu đảo polarity, không NMS/chọn status hoặc tự confirmed. Tối đa4trial×30contour×3epsilon=360attempts; small-area rejection vẫn chỉ lưu1attempt. Kernel analysis phải khớp trial, không chỉ dimensions.

`create_region_trial(analysis,support)` nhận EdgeTrial thực cùng dimensions/kernel, tính threshold(analysis.blurred,0,255,THRESH_BINARY|THRESH_OTSU). RegionTrial giữ trial_id=`region_otsu_gK_<support_trial_id>`, method=region_otsu, gaussian_kernel, actual otsu_threshold finite0..255, support_trial_id, thresholds (cặp **Canny support**, khác t), edges copy của raw Canny và mask phân vùng. Collector dùng support20/60 của cùng analysis; không sinh edge map từ mask hoặc trộn blur. CV lỗi REGION_FAILED; metadata/map sai INVALID_TRIAL/INVALID_ANALYSIS.

Region contour lấy mask bằng RETR_EXTERNAL/CHAIN_APPROX_SIMPLE: truy đường bao ngoài thành phần trắng, bỏ biên lỗ bên trong mà không fill/thay pixel mask. Không thêm morphology vào mask. Nếu mask toàn0/toàn255, trả CandidateBatch.rejection_reason=UNIFORM_REGION_MASK, attempts rỗng, không chạy contour/approx; total/considered=0 vì chưa tìm contour ở trial bị gate. Vẫn giữ mask thật trong debug/experiment. Các mask còn lại dùng cùng cap30/epsilon/area/cạnh/geometry; không bảo đảm thành phần trắng là giấy.

ContourCandidate thêm method, gaussian_kernel, otsu_threshold (null cho Canny), bên cạnh ID/thresholds/source_size/analysis_size/contour/Q/reason. Describe so method/kernel/actualt/ID/thresholds/dimensions với trial, mismatch báo INVALID_CANDIDATE. Geometry flags và bộ mô tả/score ở trên không đổi. **e của RegionTrial vẫn đo edges raw từ support**, không dùng mask/boundary mask/closed; nếu raw không có edge, e=0 dù mask đầy đủ hình trang. Không nâng score để nhánh mới tự qua ngưỡng đề xuất.

`experiments/compare_detection.py` so baseline/revised cho một input, baseline luônGaussian5, revised default5 hoặc --gaussian-kernel3 để ablation. Source PNG dùng đúng encode_normalized_png payload/hash; stages/candidate/method/kernel/t/support/tỷ lệ/score/dimensions thật, thư mục mới/không ghi đè, metadata cuối. Ví dụ overlay theo score chưa là proposal hoặc confirmed; không tạo warp. 30tests revision+5CLI/670backend đạt,16runs/104trial tại detection-revision-01-verified/. anhtestnew có quad; img_004/img_006 region còn ăn bàn, img_001 chưaquad, frame vẫn sai. Không accuracy hoặc cổng05;05.05–08 còn chờ.

### Lựa chọn hiện hành — MVP05.05–06, 15/10/2026

Các mốc phía trên ghi lịch sử trước NMS. Entry detector hiện có là `detect_document(source_bgr)` → prepare_analysis Gaussian5 → collect_candidates revised → describe từng candidate bằng chính trial → select_proposal. Nhận BGR uint8 sau EXIF, không I/O/HTTP/DB hoặc warp. Không tìm được quad là kết quả bình thường; input/CV lỗi vẫn ném DetectionValidationError, không che lỗi thành manual_required.

`polygon_iou(first,second,width,height)` trong polygon_metrics.py nhận hai quad normalized, cùng ảnh/dimensions, cycle clockwise hợp lệ. validate_quad trước giao; chuyển pixel không làm tròn, diện tích liên tục I/(A+B−I), không dùng bounding box hoặc raster đếm pixel. [OpenCV intersectConvexConvex](https://docs.opencv.org/4.x/d3/dc0/group__imgproc__shape.html) với handleNested=true xử lý cả containment, cần polygon lồi. Cùng quad khác start có IoU chính xác1 qua kiểm chu kỳ float64; các giao khác dùng CV float32, có sai số số thực. Giới hạn intersection về min(areaA,areaB) để tránh tràn nhẹ do rounding; lỗi/nonfinite/diện tích không hợp lệ báo POLYGON_IOU_FAILED. Geometry sai giữ reason từ validate_quad.

`deduplicate_candidates(descriptions)` dùng greedy NMS: xếp S giảm dần, tie giữ thứ tự đầu vào; ứng viên chỉ bị loại nếu IoU **> .95** với một ứng viên đã giữ. Không gộp dây chuyền qua ứng viên đã bị loại. Collector xác định thứ tự trial/contour/epsilon nên tie tái hiện được. NMS kiểm score hữu hạn [0,1], quad hợp lệ trên analysis/source và dimensions đồng nhất; mismatch báo INVALID_CANDIDATE, lỗi phép giao báo NMS_FAILED. Caller phải truyền cùng nguồn/run: dimensions không phải danh tính ảnh. Tối đa360 attempts từ collector, scan O(n²) có giới hạn hiện hành; không thêm index/dependency.

Giữ nguyên CandidateDescription thắng, không ghép score/edge support của trial khác. ContourCandidate bổ sung `support_trial_id`: region giữ raw Canny origin thực, Canny để null vì raw origin chính là trial_id. generate_candidates ghi cả accepted/rejected, describe kiểm khớp trial; actualt/method/kernel/thresholds/contour/quad và counts từng cạnh đi cùng ứng viên. Không tính lại S sau NMS.

`select_proposal(descriptions)` gọi NMS và trả DetectionResult frozen:

| Điều kiện | status | corners | heuristic_score | warnings |
|---|---|---|---|---|
| Không có candidate | manual_required | null | null | NO_VALID_QUAD |
| S<.40 | manual_required | null | S thực | LOW_HEURISTIC_SCORE |
| .40≤S<.60 | proposed_with_warning | normalized quad | S thực | LOW_HEURISTIC_SCORE |
| S≥.60 | proposed | normalized quad | S thực | rỗng |

`candidates` là tuple các NMS survivors theo score; `selected` là description cao nhất hoặc null nếu không có. Khi S<.40, selected chỉ là bằng chứng chẩn đoán, không dùng selected.candidate.corners thay result.corners để render. `confirmed` luôn false, không nhận init override. UI tự tạo draft inset5%/toàn ảnh ở task sau; detector không dựng giả góc khi thất bại. Status proposed không chứng nhận đúng trang; UI vẫn cần người dùng kiểm/xác nhận mọi đề xuất.

18 tests metrics +28 selection mới, 140 tests tập trung và716 backend đạt. Chạy7ca tại experiments/results/mvp05-05-06-verified/: img_00312→1/cảnh báo S.502372; img_0041→1/cảnh báo S.468352 vẫn ăn bàn; anhtestnew6→1/đề xuất S.634709; img_001 khôngquad/manual. Khung tổng hợp có thể đề xuất sai S.979901. Chưa thay phân vùng/epsilon/weights hoặc thêm gate từng cạnh; timing/stages public và batch05.08 chưa triển khai. Checkpoint05-C2 đạt, cổng05 còn chờ.

### Timing/debug và batch hiện hành — MVP05.07–08

`detect_document(source_bgr, debug=False, preset='revised')` vẫn mặc định Gaussian5/revised; cho baseline explicit để đối chứng. DetectionResult thêm `timings_ms: DetectionTimings` ở entry này và `debug: DetectionDebug|null`. Helper select_proposal đứng riêng không đo một pipeline nên timings_ms=null. Debug phải là bool, preset baseline/revised; sai báo INVALID_ANALYSIS_CONFIG. Không thay điều kiện region/epsilon/gates/NMS/score hoặc confirmed.

Timing dùng perf_counter_ns, đổi sang ms: preprocess; candidates (Canny/closing/contours và Otsu có điều kiện); describe; select (gồmNMS); debug; total. Các khoảng liền nhau, total bằng tổng bước theo sai số số thực. Debug tắt có debug=0; total chốt sau selection. Debug bật gồm tạo overlay và hash trong bước debug. Không gồm decode, encode, đọc/ghi tệp hoặc dựng result cuối; không chia thời gian candidates thành Canny/contour riêng khi chưa đo riêng.

Debug opt-in giữ AnalysisImages và tuple TrialCandidates thật, selected_trial đúng ID của result.selected (kể cả selected chỉ làm chẩn đoán), overlay BGR uint8 cùng dimensions analysis và overlay_kind proposal/diagnostic/none. Khôngquad trả selected_trial=null, overlay_kind=none và overlay copy analysis.bgr không vẽ quad giả. Best dưới.40 có overlay diagnostic nhưng result.corners vẫnnull. Contour xanh, Q đỏ/đánh số, chỉ làm tròn để vẽ; không resize hoặc dùng overlay để warp. CV overlay lỗi báo DEBUG_FAILED, không đổi thành manual_required. Mặc định tắt không giữ các stage arrays trong result.

DetectionDebug có algorithm_version=detect-v1, preset và source_bgr_sha256 tính trên source.tobytes(order='C') sau EXIF. Hash này **khác hashPNG**; dimensions source đi cùng analysis.source_size. CLI gắn thêm raw/normalized PNG hashes để đối chiếu. Dataclass frozen bảo vệ metadata, không làm mọi ndarray bất biến; caller không sửa ảnh rồi giữ cùng provenance. Service phải tách ảnh khỏi JSON metadata và lưu theo nguồn/revision khi nối API, không asdict toàndebugndarray để gửi JSON.

`experiments/detect_batch.py --output-dir <thư_mục_mới>` kiểm schema manifest, chỉ đọc ảnh development và chạy hai preset trên cùng nguồn. `--input` lặp được cho ảnh bổ sung với supplemental ID, document_id=null/split=supplemental_unassigned; không tự thêm manifest. --project-root phục vụ đường dẫn dataset theo workspace; test không được mở để tune. Kiểm raw hash và normalized hash nếu manifest có; giữ sourcePNG đúng encode_normalized_png payload. Ghi mới, không đè; xử lý từng ảnh, error.json/CSV/summary và exit1 khi có lỗi, vẫn chạy các ảnh còn lại. Summary hiện diện có nghĩa batch đã kết thúc, cần đọc errors, không suy ra mọi ảnh thành công.

Mỗi profile ghi analysis/gray/blurred/contour_overlay; raw `<trial>_edges` riêng `<trial>_closed` hoặc `<trial>_region_mask`, metadata dimensions/đơn vị/config/preset/version/source hash/trials/attempts/selected description/NMS survivors/timings. Selected_trial là metadata trial, không gộp raw evidence của ứng viên khác. results.csv có status/score/a/e/f/b/method/count/timing/error; comparison thu từ overlay đầy đủ với nhãn trạng thái/unconfirmed ngoài ảnh. Không tạo warp hoặc nhãn accuracy trong CLI detector.

Nghiệm thu05.07–08/AUX05.02:10debug+7batchCLI mới,733backend đạt47.01s; 16ca×2preset/32runs/104trial/368PNG, đã xem16comparisons và QA replay stages/19survivors. Manual draft img_001 qua enhancement_demo tạo warp951×1284/4mode/8PNG, config confirmed=false, khôngGT/UI. Cổng05 đạt theo chức năng MVP và bằng chứng ban đầu; vẫn có frame sai điểm cao, img_004/006 ăn bàn. [Audit05](audit-phase-05.md) ghi ma trận tám task và hướng nợ task03–04; chưa thêm cap epsilon/fit gate/side gate hoặc đổi phân vùng/score.

## 10. Đối chiếu và kiểm chứng khi triển khai

| Nguồn gốc | Nội dung giữ/làm rõ trong hợp đồng | Điều chỉnh MVP |
|---|---|---|
| Mục 5–6 | Source/config/artifact, lưu bền, confirmed, revision | Không cache bền; export khóa mutation |
| Mục 7 | BGR uint8, EXIF/alpha, normalized W−1/H−1, contain/DPR | Ghi rõ làm tròn, điểm biên và trường hợp analysis <2 |
| Mục 8–9 | Nhánh detection/render riêng, contour/score, homography, threshold | estimated/2400 cố định; CLAHE gray/BW; hoãn sharpen/A4 warp/deskew |
| Mục 10 | Full config/effective_config, expected_revision và artifact đúng trang | Schema API chi tiết hiện thực ở MVP07.01; hiện chỉ có health |

### Truy vết với tài liệu phân tích hướng thuật toán

| Mục trong tài liệu phân tích | Mục tương ứng ở hợp đồng này | Quy tắc được giữ |
|---|---|---|
| 2–4: bài toán và các mức biểu diễn | 2, 9 | Tìm toàn trang; Canny/contour cung cấp bằng chứng, chưa tự xác định giấy |
| 5.1–5.4: tiền xử lý và đa giác | 2, 9 | Gaussian rõ ở nhánh detection; closing nhẹ; contour → Douglas–Peucker → quad hợp lệ |
| 5.5.1–5.5.3: mô tả/xếp hạng | 4, 9 | Phân biệt biểu diễn/biên/vùng; dùng bộ trường và đơn vị của mục 5.5.1; e trước closing và tính theo tổng số mẫu; giữ a/e/f/b |
| 5.6: xác nhận và warp | 3–6, 8 | Góc trên source chuẩn hóa; người dùng xác nhận; warp từ nguồn đầy đủ |
| 6: descriptor khác | 9 | Giữ tọa độ contour/Q; Freeman/Fourier/Hu chưa thành yêu cầu bắt buộc |
| 7: hướng dựa trên vùng | 9 | Otsu bright-mask dự phòng khi không quad Canny, RETR_EXTERNAL; raw Canny support tách biệt; không thay manual fallback |
| 8: sau warp và gấp/nhàu | 1–2, 6–7 | Otsu/Adaptive sau warp; polarity riêng; homography không dewarp; giữ màu/xám khi cần sắc độ |
| 9: thí nghiệm | 9–10 | Preset cần kiểm chứng bằng development; Sobel/largest contour là baseline nghiên cứu, không tune bằng test |

Các quyết định làm rõ để code cùng quy ước: khởi đầu revision=0 (đồng bộMVP07.05 khi chốtAPI17/10), no-op không tăng; kích thước round-half-up; rotation chiều kim đồng hồ; kernel lọc render3/5; Adaptive quá lớn báo lỗi; thiếu field dùng preset theo mode. Đây là chính sách triển khai có thể kiểm chứng, không phải kết quả nghiên cứu thuật toán.

## 11. Pipeline offline hiện hành — MVP06.01–03

`render_document(source_bgr, config, debug=False)` trong render.py là lõi không HTTP/DB/I/O. Nhận BGR uint8 sau EXIF, mỗi chiều≥2, tối đa16MP; parse_config với dimensions nguồn thật. Config có corners thì giữ nguyên thứ tự và bỏ qua detector. Config chưa có corners thì chạy detector revised; chỉ dùng result.corners, không lấy góc từ selected diagnostic dưới.40. Không có đề xuất trả RenderResult.status=manual_required, warp/enhancement/H=null, config.corners=null; không dựng vùng giả.

Nguồn hợp lệ nhưng analysis thu nhỏ có cạnh1 được chuyển từ ANALYSIS_TOO_SMALL thành kết quả manual_required với warning tương ứng; không bắt các lỗi input/CV khác để giả thất bại bình thường. Đường manual vẫn cần vượt geometry gate: nguồn40000×42 có quad toàn ảnh hợp lệ và analysis cao1, nhưng nguồn40000×2 không vượt ngưỡng cạnh ngắn hiện hành. Không nới gate hoặc resize nguồn để né kiểm tra.

Có góc thì compute_homography/warp_document từ **source**, enhance_document trên full warp rồi rotation; kết quả được giữ trong RenderResult cùng effective_config, corners_origin=manual/detected, detection nếu đã chạy, H source→warp và RenderTimings. Timing validate/detect/warp/enhance/total dùng perf_counter_ns; detect manual=0, warp gồm chuẩn bị corners/H, tổng là các khoảng liên tiếp. Không gồm normalize/encode/I/O; không cộng timing detector lần nữa vì nó đã nằm trong detect của pipeline.

Đây là pipeline **offline** có thể tạo bản nháp để xem: status=rendered chỉ xác nhận đã có pixel kết quả. Nó không tự biến confirmed thành true, không kiểm revision hoặc ghi phiên UI. Explicit confirmed của config được giữ khi không thay góc; auto không thể tạo confirmed=true. CLI --corners thay corners và đặt confirmed=false. Gating confirmed/revision cho render/export trong ứng dụng vẫn thuộc service ở task sau.

`encode_render_images(full_render)` nhận gray HxW hoặc BGR HxWx3 uint8, mỗi chiều2..2400. Trả RenderImages(full,preview), mỗi EncodedRaster có png_bytes/width/height/png_mode/sha256 của đúng payload. PNG mới RGB hoặc L, không kế thừa EXIF/ICC. Preview lấy từ **cùng pixel full sau rotation**, resize_to_max_edge1000/INTER_AREA/half-up/không upscale; không lọc/threshold lại. Preview có thể cao/rộng1 và BW preview được có mức xám do nội suy. encode_stage_png cho stage/preview có cạnh1, không áp quota upload15MiB cho payload nội bộ. Source tiếp tục dùng encode_normalized_png và ghi chính payload đó. Lỗi encoder là INVALID_RENDER/ENCODE_FAILED, không tạo bytes giả.

EnhancementResult thêm stages=null mặc định; `enhance_document(...,debug=True)` trả EnhancementStages từ đúng dispatcher chạy một lần: filtered_bgr, prepared_gray (Gray/BW sau contrast; Color=null), before_rotation. prepared_gray của BW chính là ảnh đưa vào threshold; không lấy gray/Gaussian từ detection thay thế. Các buffer được giữ trước rotation; final image vẫn cùng pixels như khi debug tắt. MVP06.04 bổ sung histogram theo mục11.2 bên dưới. Metadata frozen không làm ndarray bất biến cho caller tùy ý sửa.

`experiments/scan_one.py INPUT --output-dir NEW` là CLI normalize một lần → render_document → encode → ghi tệp. --mode color/gray/bw hoặc --config JSON là hai lựa chọn loại trừ nhau. --corners JSON ghi đè riêng corners, chuyển draft và parse lại; không model_copy bỏ validation. Rotation/denoise/contrast/threshold lấy từ config. Config sai kiểu/null/extra/Adaptive block quá warp bị từ chối, không tự clamp/chuyển Otsu. Cùng config.json có corners và đúng ảnh gốc có thể chạy lại; khi đó đi đường manual, nên metadata detection có thể khác lần auto ban đầu dù full pixels giữ nguyên.

Output chỉ dùng thư mục mới. source.png là PNG sau EXIF; source_overlay.png dùng coordinates nguồn. detection/ chứa trial maps/contour overlay/metadata từ chính DetectionResult của lần chạy, không rerun detector để tạo debug. Writer dùng chung ở experiments/detection_artifacts.py phục vụ scan/batch, nhận entry_point/run_id tường minh, giữ method/kernel/actualt/raw support. render/ chứa warp, filtered_bgr, prepared_gray nếu có, before_rotation, full, preview; tên và kích thước không trộn với detection. config.json là full effective config; metadata.json ghi cuối có requested/effective config, inactive_fields, Otsut, H, hashes raw/PNG/BGR, source dimensions, version môi trường và timing thực.

Exit0 khi có render; exit2/manual_required khi cần góc tay (có source/config/debug nhưng không full giả); exit1 khi ảnh/config/I/O lỗi. Lỗi sử dụng argparse cũng có thể exit2, nên phải đọc metadata/status để phân biệt. Metadata hiện diện là marker hoàn tất việc ghi, không tự chứng nhận render tồn tại, chọn đúng giấy hoặc userconfirmed. Snapshot config đi kèm metadata/hash nguồn; PageConfig đứng riêng không chứng nhận danh tính ảnh.

Nghiệm thu mốc06.01–03:30tests render/pipeline/encoder +6enhancement stages +8scanCLI mới;777backend đạt38.83s. Runtime7runs/92PNG gồm4nguồn ảnh thật và1synthetic,6render/1manual_required;4detection/14trial. QA đọc lại và tính kiểm source warp/filter/gray/Otsu/rotation/preview/config/hash. CaseBW90 full1300×2000→preview650×1000, preview cógray đúng INTER_AREA; manual img_001 Gray giữ nguyênhash so output giai đoạn05. Checkpoint06-C1 đạt; cập nhật06.04 ở dưới, nghiệm thu tái lập06.05 và mốcM1/06.06 còn chờ. Không thay detector: img_004 vẫn ăn bàn và Otsu làm đen phần bàn đó.

### 11.2. Histogram trước threshold — MVP06.04

`compute_histogram(gray)` trong processing/histogram.py nhận full gray H×W uint8, mỗi chiều2..2400, trả tuple256 **số nguyên Python**. Bin k đếm toàn bộ pixel có giá trị k (0..255), không mask, không chuẩn hóa xác suất, không resize hoặc thay đổi input. Dùng `cv2.calcHist([gray],[0],None,[256],[0,256])`, cận trên256 loại trừ nên vẫn tính đủ mức255. Count float32 của OpenCV còn biểu diễn nguyên chính xác ở giới hạn5.760.000pixel<2²⁴; kết quả đổi sang int. Input sai báo INVALID_HISTOGRAM_INPUT, lỗi CV báo HISTOGRAM_FAILED; không tự chuyển ảnh màu/float/preview thành gray. [Tài liệu OpenCV](https://docs.opencv.org/4.x/d1/db7/tutorial_py_histogram_begins.html).

Dispatcher tính một histogram trên prepared_gray **sau denoise/contrast, ngay trước threshold và rotation** khi mode=bw. `EnhancementResult.histogram` có counts ngay cả debug=false; debug chỉ quyết định giữ stage arrays. Color/Gray không threshold nên histogram=null. `RenderResult.enhancement` mang kết quả này; manual_required không có enhancement/histogram. Không chạy lại denoise/CLAHE/Otsu để dựng histogram; ảnh full/preview/config/confirmation vẫn giữ quy tắc cũ.

CLI thêm `metadata.json.histogram` (object hoặc null), không thay PageConfig:

| Trường | Ý nghĩa |
|---|---|
| counts | 256 số nguyên không âm, chỉ số0..255 là mức xám; sum=width×height |
| width, height, pixel_count | Kích thước và số pixel của prepared_gray full **trước xoay**, không phải preview |
| source_artifact, source_png_sha256 | `prepared_gray` và hash payload PNG trong artifacts của cùng run |
| threshold_method, threshold_scope | otsu/global hoặc adaptive_gaussian/local |
| otsu_threshold | Actual t của chính lượt Otsu, trùng trường ngoài; null đối với Adaptive |

Adaptive dùng ngưỡng Gaussian cục bộ theo block_size/c trong effective_config; histogram toàn ảnh chỉ giúp xem phân bố sáng/tối, không biểu diễn bản đồ ngưỡng hay dùng để suy ra một t chung. Histogram cũng không chứng minh detector đã chọn đúng giấy hoặc chữ đã đọc được. Pipeline version vẫn scan-v1 vì chỉ thêm dữ liệu chẩn đoán, không đổi pixel/config/thuật toán; snapshots trước task04 có thể chưa có trường histogram. Timing histogram nằm trong enhance/total, không thêm khoảng thời gian để cộng trùng.

Nghiệm thu16/10/2026:16tests histogram/dispatcher +1CLI mới, tổng794backend đạt95.24s. Runtime2lượt img_004 cùng gray1112×1358:sum=1.510.096/213bin khác0, Otsu t=140/global, Adaptive local/t=null; đọc lại PNG và đối chiếu độc lập NumPy. Hash Otsu full/preview/stages không đổi so mốc03. Cả hai draft, Adaptive dùng config góc từ auto trước đó nên bỏ detector/cảnh báo detect không được tái tạo. Evidence tại experiments/results/mvp06-04-histogram/ (ignored). UI histogram và nghiệm thu06.05/06.06 chưa làm.

### 11.3. Nghiệm thu tái lập và mốc M1 — MVP06.05–06

Đạt16/10/2026,800backendtests và10cặp/20CLI runs/230PNG. Cùng rawsource/config đầu vào/version/môi trường giữ pixels/config/H/stages/histogram/artifact hashes; chỉ run_id/timings_ms là từnglượt. So cả detection metadata khi lặpauto, không thay inputconfig cornersnull bằng outputconfig cócorners rồi nói detector đã tái lập. Snapshot cócorners vẫn được dùng theo đường manual; đó là phạm vi khác. Hash bytesPNG được kiểm trong cùng Pillow/dependencies, không cam kết giống payload trên mọi phiên bản. Verification lưu code/requirements/source hashes bên cạnh nhãn scan-v1; nếu đổi thuật toán/configbaseline thì phải quản lý version và kiểm lại.

M1 có sourcewarp/ba mode/rotation/full-preview/snapshots/stages/histogram/manualfailure→retrytay, độc lập web. [Tài liệu mốc](milestone-m1.md) có smoke6CLI dùng fixtures đã chạy; [audit06](audit-phase-06.md) đối chiếu6task. Không phát hiện lỗi triển khai mới chặn cổng06. img_004 vẫn saiquad/ăn bàn; tái lập pixels sai không chứng nhận chất lượng hoặc userconfirmation. Giữ gateconfirmed/revision ở service sau, không suyra từ CLI rendered. Giaiđoạn07/08/09/10/11 mới nối API/storage/UI/histogramUI/nhiều trang/PDF.

MVP02 kiểm chứng EXIF/alpha/format và giữ nguồn; MVP03 kiểm chứng normalized/diamond/winding/các góc màu; MVP04 kiểm chứng ba preset, inactive, ảnh nhỏ/Otsu/Adaptive/rotation; MVP08 sẽ kiểm canvas/DPR và response cũ; MVP10–MVP11 sẽ kiểm reopen, revision/order và PDF. Chỉ tích các task này khi mã và bằng chứng tương ứng tồn tại. Task MVP01.07 hoàn thành tài liệu, không hoàn thành thay các task thuật toán/API/UI.

## 12. Tích hợp ứng dụng — MVP07.01–09, MVP08.01–10

**Hiện hành 26/10:** MVP01.01–07, 02–11 và 13–14 xong: **102 task chính, 13 AUX**; MVP01.08 bỏ qua. M4 kỹ thuật đạt26/10/2026: bản chạy cùngorigin localhost8000, sourceZIP/manifest/checksum, cài sạch đúnglock/1.279backend-experiments+103frontendtests/typecheck/build, README/hướng dẫn/báo cáo sốliệu thật vàdemo5–7phút đãkiểm. RehearsalUI sau nhập5phút21giây, PDF3trang/restart65artifact đạt; chưa có lượt tập nói hoặc thủ tục nộp hành chính. Đã rà đủ8task14/AUX14.01; giữlõiảnh/preset/lock/manifest/nhãn/frozen13, chỉ sửa một dòng chú thích dataset trênUI. Giai đoạn12 còn7task chưa nghiệmthu và5optional chưa làm; không tựtích theo cổng hồi quy trước khóa. Giữ ca sai development và giới hạn mỗi split một tài liệu. API/schema3/core/dependencies giữ nguyên;14.08 chỉ sửa chú thích datasetUI và bổ sung gói nộp. Xem [cấu hình bản chạy](local-runtime.md). [Kết quả](results.md), [audit13](audit-phase-13.md), [bản khóa](experiment-environment.md), [phương pháp đo](benchmark-method.md).

### Draft, xác nhận và kết quả UI — MVP08.07–08

Đây là mốc07–08; ComparisonView đã mở rộng phần hiển thị ở mục tiếp theo.

`pageRenderState` sở hữu snapshot theo page/source cho một lần mở. Draft giữ toàn bộ config, kể cả inactive; góc null khởi tạo vùng thử inset5% với confirmed=false, chưa tự persist. Kéo/keyboard/toàn ảnh đặt confirmed=false. Pointer cancel phục hồi chính full config trước kéo, bao gồm xác nhận; không tự sort hoặc suy ra xác nhận từ quad hợp lệ. “Đặt lại góc đã lưu” phục hồi snapshot server; “Lưu nháp” persist false; “Xác nhận vùng” gửi fullconfig explicit true. Preflight quad chỉ là phản hồi sớm, backend vẫn gate cuối theo source dimensions/warp thật.

Nút quét cần confirmed/hợp lệ và state đã đối soát. Luồng PUT fullconfig/CAS → kiểm page/revision/payload → nếu draft không đổi thì POST render revision vừa trả → kiểm page/revision/lần request/edit version → mới thay preview. Edit trong PUT vẫn nhận persisted snapshot đã commit nhưng giữ draft mới unconfirmed và không POST. Edit trong render bỏ kết quả trả muộn; switch page/unmount bỏ mọi response của editor cũ. Mở lại editor GET detail để lấy revision/config hiện hành; không cố abort để giả rollback worker/commit. Không có retry mutation tự động.

Lỗi/mất response/409/429/500 giữ ảnh lần trước nếu có, đánh dấu cũ và chặn mutation tới khi “Đọc lại cấu hình” GET thành công. Giữ góc nháp, bỏ xác nhận khi đối soát để người dùng kiểm lại. GET detail không có UUID render/preview nên lần mở lại chưa tự tải lịch sử kết quả; có nhắc tạo lại bản quét. Chuyển trang/refresh bỏ nháp chưa lưu, có nhắc trên editor. Preview artifact đúng response, nhãn revision/dimensions full sau rotate; load/error/retry ảnh riêng. Zoom/so sánh thuộc08.09, chưa nút xuất tại đây. Lõi/source/config defaults/HTTP DTO không đổi.

Nghiệm thu07–08:64frontendtests (51cũ+12state/race+1API wire),67backendconfig/render -Werror, typecheck/build, browser API thật/held response/unknown commit đạt; nguồn1536×2048 chọn tay→full1076×1281/preview840×1000, fixture EXIF64×96→63×95.5session cũ/21sourcehash nguyên. Chi tiết/evidence/giới hạn tại [progress](progress.md); checkpoint08-C3/M2 chờ09–10.

### So sánh và phóng to — MVP08.09–10/AUX08.01

ComparisonView nhận cùng PageRead/RenderRead từ editor đãqua page/revision/operation/edit guards, không tự gọi render hoặc thayconfig. Bên nguồn là normalized_artifact_id sauEXIF, khôngoverlay/thumbnail; bên kết quả là **render_artifact_id fullPNG**, khôngpreview_artifact_id. onLoad kiểm naturalwidth/height đúng descriptor/page, cóloading/error/retry. Nhãn nguồn/kết quả/fullsize/revision vàstale giữ rõ khi sửa góc hoặc lỗi. “Quay lại chỉnh góc” focushandle0, không tựghi config.

Fit dùng nativeimg/object-fit contain trongviewportcuộn.100% đặtCSSdimensions=full(W,H),200%=2×full; source vẫnfit. Không ápDPR vào sizeảnh hoặcpointmapping;1pixelảnh/1pixelCSS ở100% khác1pixelvậtlý trênHiDPI. Zoom làhiểnthị, không resample/threshold lại vàkhôngđổi PNGbytes. Hai cột ởdesktop, một cột≤1023px; overflow nằmtrong từngpane, tabindex/arrowkeys cuộn được. NewartifactUUID resetzoom/loadstate; dirty khôngđổiảnhcũ nhưnggắnnhãn cũ.

Nghiệmthu17/10:983backend-Werror/64frontend/typecheck/build/browserquét tay3ảnh đạt. Ngang96×64→95×63, EXIF64×96→63×95, chữnhỏ/highlight1200×1600→full1009×1406/preview718×1000;100/200%CSS1009×1406/2018×2812 cùngUUIDfull.12mẫu4màu distinct projectH khớp0kênh,3previewbyteequal từfull. ForcedDPR1/2 backing653×432/1306×864 giữgóc/mask140–0,maxhandleerror.01685323CSSpx; physicalDPR/touch chưa thử riêng.7session/10page/30sourcehash cũ nguyên. Cổng08/M2/checkpoint08-C3 đạt; next09.01detectAPI. [Audit10task](audit-phase-08.md), [smoke](../frontend/tests/scanner-smoke.md), [progress](progress.md).

PUTconfig thay full snapshot theo source_size thật; có góc thì kiểm Adaptive theo estimate_warp_size thật. No-op giữ revision/timestamps; mọi thay đổi kể cả inactive tăng đúng1 sau commit; stale409. Gửi góc thiếu confirmed dùngfalse; xác nhận cần true rõ. SQLite writer lock trước read/CAS ngăn hai update cùng revision cùng ghi thành công.

render_page chỉ nhận revision đã xác nhận, đọc normalizedPNG đúng owner/hash/dimensions/RGB/singleframe/noEXIF, không áp bytecap upload hoặc chuẩn hóa EXIF lần nữa. CPU/encode ngoài transaction; core dùng manual corners và full source; preview từ final full. Trước publish lấy writer lock/kiểm snapshot lại rồi ghi đúng hai artifact full/preview cùng page/revision và commit; stale/deleted không ghi kết quả. Lỗi dọn file mới chưa tham chiếu, giữ source/config/oldrender. Chưa GC sau crash hoặc persist debug/histogram; next08.03 nối executor/HTTP,08.04+ canvas/UI,09 debug. Không sửa thuật toán/preset/dataset/schemaVersion1.

[api-contract.md](api-contract.md) chốt UUIDv4/UTC/title/fullconfig/artifact/errors. HTTP5path thực gồmhealth/create-list-detail/upload/artifactGET; multipart1file/0textfield, capbody15MiB+64KiB/envelope vàđếmfile64KiB/chunk15MiB, khôngtinContent-Length/MIME/filename. Malformed/cutmultipart đónghếtspoolfile. ArtifactGET joinowner/guardpath/hash sauDBtransaction, MIME/nosniff/inline/private-no-store; khôngpublicdata. OpenAPIbinary/multipart/Errors đúngroute, không422 giả. Config/góc/revisionCAS vẫntheotask08; khôngauto-confirm khi nhập.

SQLite6bảng/schema_version1/FK/fileUUID/temp/publish/verify/import/executor giữ như07.01–06. UIbatchtuầntự báo riêng từngfile; PageList dùngthumbnail, SourcePreview dùngfullsourcePNG sauEXIF, khôngxoaythêm hoặc dùngthumbnail làmhìnhhọc. Session/page selection theoURL, nội dung lấyDB/artifact; name/order/config/revision0/confirmedfalse/sourceIDs/hash6file giữqua browserrefresh/backendrestart thật.14import/20HTTPuploadtests cóquotalastslot/rollback/20page/15MiBexact/16MP/429/cleanup; tổng916backendtests vàfrontendtypecheck/build/browser4viewport đạt. Cổng07/AUX07.01đạt, next08.01 fullconfig/góc/confirmed/revisionCAS. KhôngGC saucrash/transactionchungfileDB/authorization đauser; render/detect/export HTTP cònchờ.

## Tích hợp nhận diện — MVP09.01–02, 18/10/2026

POSTdetect dùng nguồn PNG sauEXIF/hash/dimensions thật, detector hiện hành không đổi; corners normalized W−1/H−1 chỉ vào nhápfalse. DetectionRun gắn runID/sourceartifact/sourcehash/algorithmversion/trials/stages của đúng một lượt; source_revision ghi thời điểm snapshot, không phải renderrevision và không cập nhật config. StageUUID riêng cho mỗi run kể cả cùng nguồn/revision. Debugrequestfalse vẫn lưu provenance, không stagePNG; UI hiện gửitrue. Truy xuất09.06 phải theo run.metadata.artifacts để tránh lẫn nhiều run cùng revision.

UI chỉ nhận kết quả đúng page/source/dimensions/revision đã biết; sửa nháp/reset/đổi trang khi đang chạy khiến phản hồi cũ bị bỏ. Proposal có thể sai mép giấy; user phải kiểm/chỉnh rồi xác nhận. manual_required200 có cornersnull, UI dùng vùng thử5%, không tuyên bố phát hiện biên. API không ghi đè config dù đã confirmed; backend giữ nguyên config khi thay đổi trong CPU.996backend-Werror/68frontend/typecheck/build và browser proposed/warning/manual/late-response đạt; chưa checkpoint09-C1/modeUI/debugviewer. [API](api-contract.md), [bằng chứng](progress.md).

## Mode và threshold trên UI — MVP09.03–04

FilterPanel nhận fullPageConfig từ store hiện hữu, không xử lý pixel trong browser. Đổi mode không reset preset hoặc xóa inactive; None/Color/Gray/Otsu khóa các trường không áp dụng và giữ giá trị. Native controls chỉ cho kernel3/5, CLAHEclip1..4/grid8×8, blocklẻ3..151/Cnguyên−20..30. Adaptivefit phụ thuộc fullwarp thật, backend PUT kiểm lại; ảnh nhỏ có thể bị từ chối, không tựco block. UI khôngauto-preview, khôngrequest mỗi lần thay tham số; nút render explicitPUTCAS→POST đúngrevision. Đổi filter giữ xác nhận góc, kết quả cũ stale; sửa góc vẫn bỏconfirmed.9full/preview khớp byte với render lại từ nguồn, Colorcuối bằngColorđầu sauchuỗiGray/BW; [bằng chứng](progress.md). Checkpoint09-C1 đạt; debugrender/viewer còn09.05–07.

## Debug HTTP — mốc MVP09.05–06 trước khi có viewer

RenderRun/schema3 gắn nguồnPNG/SHA,full/preview,config/revision/version/timing của đúngmột lần render. POSTdebugtrue giữ bufferthật của core:warp,filtered_bgr,prepared_gray(nếuGray/BW),before_rotation; không dựnglạibằngchạyfilterlầnhai. HistogramBW theo11.2; Color/Graynull với lýdo, Adaptivekhôngcóngưỡngglobal. Full/preview/PNGstage/hash/JSONrun commitcùngmetadata, stalegate/cleanup giữ. Debugfalse vẫn córun nhưng khôngstage/histogram; legacy chưarun được nhậnbiết, khôngbackfill.

GETdebug chọn revision mới nhấtđúngR hoặc render_run_id/detection_run_id cụ thể; chỉ1selector, mặcđịnhrevisionhiệnhành. Khônglọc bỏrenderdebugfalse rồi lấyrundebugcũ. Artifacts truyquaUUID/owner/kind/revision/hash,dims; thiếu/hỏng→incomplete/missing_stages, khôngtrámrun khác. Revisioncũ trả snapshotcũ dùconfigmới đãđổi; current_revision riêng. GET khôngchạyprocessing. UIviewer/phầnhiệnhistogram còn09.07; frontendrender hiệnchưa bậtdebug. [API](api-contract.md), [progress](progress.md).1031backend-Werror/71frontendtests đạt,2restart/36hash/2histogramNumPy/10session57sourcehash nguyên; checkpoint09-C2đạt/cổng09cònchờ.

## Viewer debug hiện hành — MVP09.07–08

UI luôn yêu cầu `debug:true` khi render; backend defaultfalse vẫn phục vụ các client khác. PipelineViewer lấy GET theo render_run_id của RenderRead hoặc detection_run_id của lượt nhận diện được chấp nhận, không query newest revision để ghép với kết quả đang hiển thị. Thiếu run ID báo chưa có dữ liệu; không tự render/retry mutation. GET chỉ bắt đầu khi mở details, hủy khi đóng/chuyển run/trang; sequence guard chặn response muộn kể cả fetch không tuân abort.

Validate page/kind/run/source dimensions/SHA/revision/ref UUID/SHA/kind/dimensions; ảnh từ envelope artifacts, không từ refs lịch sử đang missing. Ảnh kiểm natural dimensions và cho thử lại GET ảnh. Dữ liệu thiếu hiện nhãn, không thay số0/quad5%/ảnh run khác. Detection diagnostic giữ theo nguồn sau khi sửa draft, không biểu thị góc tay mới là proposal. Render trước còn xem được với nhãn stale.

Histogram dùng256counts nguyên từ metadata đã lưu, kiểm sum=W×H, dimensions/hash của prepared_gray và global/local/actualt; không tính từ preview/BW hoặc chạy lại CV. Missing file stage không xóa số đếm snapshot lịch sử đã có, nhưng UI báo incomplete và không hiển thị ảnh thay thế. Color/Gray/debugoff histogramnull có giải thích. Artifact/histogram của run mới không dùng chung với run cũ trong cùng revision. Xem [audit09](audit-phase-09.md).

## Metadata tài liệu và append — MVP10.01–02

Đổi tên chỉ sửa ScanSession.title/updated_at; không tăng revision ảnh hoặc thay nguồn/render/config. Same normalized title là no-op. Upload vẫn nhập một nguồn mới với revision0/confirmedfalse, vị trí append duy nhất dưới writer gate/quota20; không sửa các trang trước.

UI giữ selected_page theo ID; không tự nhảy trang mới khi đã chọn trang hợp lệ. Parent không tăng detailReload khi rename/append/reconcile; editor hiện hành giữ draft và render/debug snapshot. GET đối soát cuối batch đưa các trang commit nhưng mất phản hồi vào danh sách; lỗi request không được hiểu thành chắc chắn chưa lưu. Batch khóa qua GET để tránh mở batch mới trên quota chưa rõ. Reload/navigating chủ động vẫn có thể bỏ draft; tự mở lại kết quả đã lưu hiện đã có10.07, xem phần dưới. [API](api-contract.md), [progress](progress.md).



## Quản lý nhiều trang và phục hồi — MVP10.03–07

Order chỉ thay position và session timestamp, giữ nguồn/config/corners/revision/run; permutation phải đủ tập ID hiện hành. UI giữ lựa chọn bằng ID và không remount editor khi order/reconcile, kể cả bản nháp và full/debug cũ. Xóa owner trước trong DB, compact trang còn lại; sau commit mới verify/unlink từng UUID không còn reference. Finalize CPU kiểm lại owner/revision/source nên xóa trong render/detect/import không tạo kết quả vào owner đã mất. Cleanup lỗi giữ orphan/log; chưa có GC bền hoặc Undo.

GET detail thêm latest_render/latest_detection từ snapshot RenderRun/DetectionRun, không lấy ngẫu nhiên artifact cùngrevision. Latest render chọn revisionDESC/created_atDESC/idDESC; legacy chưa run→null. Current draft persisted có thể mới hơn render: phải giữ nhãn stale/không tự xác nhận. Reopen dựng draft từ config đã lưu và tự hiện full cũ, diagnostic detection không đổi góc. Full/preview/debug cùngrun/nguồn/hash; artifactGET/debugGET kiểm bytes, GET detail chỉ metadata. Thứ tự3trang[2,1,3], Color0/Gray90/BWOtsu270,3debugJSON/17hash giữ qua physicalrestart;3cặpfull-preview khớpcorefresh,14old docs50pages150sourcehash nguyên. [Audit10](audit-phase-10.md), [API](api-contract.md).


## Snapshot xuất hiện thực — MVP11.01–02

Request chọn subset/page_id/exactrevision/order; chỉ config persisted đãconfirmed và fullRenderRun đúngrevision/source/hash/pair được giữ. Không tựxác nhận/render hoặc dùngpreview/draft. Latestfull hợp lệ theo revision/created_at/id, legacychưaRenderRun→PAGE_NOT_RENDERED với danh sách thiếu, corrupt→STORAGE_FAILED. Snapshot/request/config/StoredArtifactfrozen, verifyfullPNG ngoàiDBtransaction.

Lease memory theoappEngine/sid chặn8mutationmetadata/publish trênowner từtrướcenqueue đếnworkerfinally; khôngpersist DB/lockfile. Queuedcancel/429/exception trảlease, activecancel giữđếnthreadxong, restartkhôngbusy cũ. Asyncupload/render/detect kiểmngaytrướcCPUqueue, việcđangchạy cũnggatepublish. Localmộtprocess/mộtEngineDB, khôngclaimlockđa tiếntrình hoặc bảo vệ OSxóa file. Encoder ảnh/PDF/ExportRecord/route/UI vẫn11.03–08. [Contract và kiểm chứng](export-snapshot.md).


## Full image encoder và PDF1page — MVP11.03–04

Ảnhxuất từload_export_pixels/fullsnapshot đãgiữlease, verify/hash/decodeRGB-L đúngdims/sạchEXIF-ICC, khôngthumbnail/preview/ảnhnháp. PNGdùngcodecchuẩnBGR→RGB/grayL/pixel-exact/BW1pixel;JPG95/subsampling0/lossy, khôngresize/filter/xoay. DownloadfilenameASCIIbounded, extensionwhitelist;khôngpathvật lýclient.

A4point=mm/25.4×72,auto theoW/Hfullsauxoay (squareportrait), explicitportrait/landscape giữpixelorientation. Fitcùngscale/căn giữa/lề0..30/khôngstretch-crop. encode_pdf_page/append_pdf_page onepage, PNGnhúnglossless/JPEG95-0DCT.3PNGstandaloneexactfull,4PDFđọc/render/xemkhôngmấtmép;16mẫugócmaxdelta2,1176backend-Werrorđạt. Ghép/commit/HTTP/UI còn05–08. [Chi tiết](export-encoding.md).


## Ghép/lưu và tải tệp — MVP11.05–07

publish_export dùng fullsnapshot đã confirmed/exactrevision theo thứ tự request; PDF append A4 từng full sau rotation, ảnhPNG/JPG một trang. Encode hoàn tất → ArtifactStore temp/fsync/publish → transaction Artifact+ExportRecord/ordered page snapshot → receipt201. Không bump config/revision/order hoặc session timestamp. Lỗi rollback và discard chỉ output mới không reference; crash có thể để orphan. POSTexports dùng shared executor/lease; GETartifact hiện hữu trả bytes MIME thật/UUID server. UI không xuất draft/auto-confirm;409PAGE_NOT_RENDERED hợp lệ mới render thiếu rồi thử POST lại đúng snapshot một lần. HaiPDF/sáutrang đã render/xem và đối chiếu fullpixel/order/A4; PNGexact/JPGquality95lossy. [Chi tiết/bằng chứng](export-workflow.md). Từ11.08, cổng11/M3đạt; xem [audit](audit-phase-11.md).


## Nghiệm thu cuối xuất — MVP11.08/AUX11.01

ActualPOSTexportgiữleasequaencode/commit:8mutation/secondexport409,GET/health/tài liệu khác hoạtđộng. LỗiởpagePDF2khôngpublishfile/record;slots/leaseđượctháo,worker dùnglạiđược. QA3trangColor0/Gray90/BWOtsu270 theoorder[3,1,2],PDFautoPNG5/portraitJPEG30đúngfullpixel hoặcJPEGcùngdimensions/fitmatrix/options;khôngcrop/xoaythêm. PhysicalrestartcùngDBgiữmetadata/4ExportRecord/30SHA,UIreopenchỉGET,POSTexportmớithànhcông.1199backend-Werror/95frontendtests/typecheck/build,15old docs52pages156sourcehash/alloldSQLrowsgiữ. Cổng11/M3đạt theoMVPcục bộ;leaseoneprocess/noOCR/noidempotency/crashorphanlàgiới hạn. [Audit](audit-phase-11.md).


## Proposal khi nhập ảnh — AUX11.02

Chỉ đổi orchestrationUI: upload→detect từng trang mới tuần tự. Detector/debug/scoring/cornersnormalized theo nguồn sauEXIF giữ nguyên. DetectionRun persisted nhưng PageConfig không đổi:revision0/cornersnull/false tới lúc user lưu/xácnhận. Lần mở đầu của trang mới untouched được nạp latest_detection cùng source/revision0 vào draft,manual_required dùng5%;không nhận diện lại trongGET. Không thay góc đã lưu hoặc nháp đã edit. Detect thất bại giữ ảnh/quota,không tựretryPOST. [Luồng và bằng chứng](auto-detect-on-import.md).
