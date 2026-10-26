# Rà soát tám task giai đoạn 03 — AUX03.01

Ngày: 14/10/2026. Người dùng yêu cầu triển khai MVP03.07–MVP03.08 và rà soát lại toàn giai đoạn, tương tự giai đoạn02.

## Kết luận

**Cả tám task đạt tiêu chí sau khi sửa lỗi phát hiện trong đợt rà soát.** Lõi tọa độ/topology/sắp góc/kích thước/H/warp và CLI minh họa đã chạy thực tế; toàn backend371 tests đạt (216 geometry, 8 demo CLI và147 ca cũ). Cổng03 đạt. Đây là nghiệm thu hình học offline, chưa phải detector, luồng scan UI, bộ lọc, lưu tài liệu hoặc exportPDF.

Rà soát phát hiện input40.000×400 hoặc400×40.000 đúng quota16MP nhưng warp trực tiếp thất bại do giới hạn SHRT_MAX của OpenCV remap. Đã tái hiện bằng hai tests thất bại, sửa lấy mẫu từng ROI nguồn gốc với homography dịch hệ tọa độ và kiểm chứng lại. Không nới quota, không resize nguồn trước warp. Ngưỡng geometry vẫn là baseline cần đánh giá thêm trên development; số tests không phải accuracy.

## Ma trận yêu cầu và bằng chứng

Nguồn: [todo](../tasks/todo.md) giai đoạn03, [MVP](MVP_Pham_Vi_Va_Ke_Hoach_4_Tuan.md), [image-contract mục3–6](image-contract.md), đặc tả gốc9.9–9.10 và [hướng thuật toán5.4–5.6](Phan_Tich_Huong_Thuat_Toan_Tu_Tai_Lieu.md). Giữ estimated, nguồn sau EXIF và manual handleorder theo bản MVP.

| Task | Tiêu chí | Implementation | Bằng chứng hiện hành | Kết quả |
|---|---|---|---|---|
| MVP03.01 | Pixel↔normalized theo W−1/H−1, finite/bounds, subpixel | pixel_to_normalized/normalized_to_pixel | Endpoints, fractional round-trip, dimensions2×2 đến16MP; mapping actual analysis dims; lỗi shape/type/NaN/Infinity/outside | Đạt |
| MVP03.02 | Đúng4điểm, không gần trùng/cạnh quá ngắn, tolerance theo resolution | validate_quad_points | Đủ6cặp/4cạnh kể cảđóng, nhiều resolution, pixel metric khi anisotropic; small manual vẫn nhận, không quota10%detector | Đạt |
| MVP03.03 | Shoelace/segment/convexity, chặn bow-tie/lõm/suy biến, winding | validate_quad | Two bow-ties, concave, collinear/near-collinear, signed winding và cycle start; thêm endpoint touch/overlap/disjoint primitive tests | Đạt |
| MVP03.04 | Sort quanh tâm/điểm đầu/chiều, giữ manual handles | order_auto_corners và manual validate riêng | 24permutations trên5bộ points đồng nhất; diamond24permutations qua warp giữ4màu; input không đổi; short diagonal chưa làedge | Đạt |
| MVP03.05 | Cạnh đối/estimated/min2/2400/pixelcap | estimate_warp_size/_estimated_size | Half-up10.5/62.5, dọc/ngang/nhỏ/lớn, trapezoid/diamond/skew, output2400² chạy thật. Full101×51→100×50 là span theo spec | Đạt |
| MVP03.06 | H4cặp/finite, source BGR, INTER_LINEAR, lỗi trước sampler | compute_homography/warp_document | Corner projection≤2e−4px; cyclic4colororders, bilinear subpixel2×2, source preserved; quota/Hnan/inf/singular; long-source fix và ROI pixel equality | Đạt sau sửa |
| MVP03.07 | Source/quad overlay/warp/metadata tái tạo bằng script | experiments/geometry_demo.py | CLI8tests subprocess;3runs full/perspective/diamond; hashes/dims/pixel/source; JSON/error/no-overwrite/outside-cwd/EXIF; xem ảnh overlay/warp | Đạt |
| MVP03.08 | Hồi quy quan trọng và ảnh không lật/xoắn | test_geometry.py, progress | Geometry216tests; diamond đủ24hoán vị warp; source/overlay/warp màu được xem; near-collinear/winding/segment/longsource guard | Đạt |

## Lỗi nguồn vượt giới hạn OpenCV và cách sửa

Runtime OpenCV4.14 báo `dst.cols < SHRT_MAX && dst.rows < SHRT_MAX && src.cols < SHRT_MAX && src.rows < SHRT_MAX` tại cv::remap. [Mã nguồn OpenCV](https://raw.githubusercontent.com/opencv/opencv/4.x/modules/imgproc/src/imgwarp.cpp) cũng có assertion này. Quota16MP không suy ra cạnh<32767, nên bản warp trực tiếp trước đây không bao phủ mọi nguồn hợp lệ.

TDD: thêm hai ca nguồn dài16MP → **2 failed, 206 deselected** trước sửa. Khi cạnh nguồn≥32767, `_warp_large_source` chia các rectangle đích đến khi boundingbox của bốn góc ánh xạ ngược nằm trong ROI nguồn<32767. Padding một pixel quanh ROI giữ các láng giềng bilinear. H_local = T(−gốc đích)·H·T(gốc nguồn); vẫn dùng warpPerspective/INTER_LINEAR/BORDER_REPLICATE trên pixel gốc. Đầu ra được ghép từ tile, cap2400/5.76MP vẫn áp trước buffer; source thường đi nguyên đường cũ.

Sau sửa geometry208tests đạt; thêm task08 thành216. Dọc/ngang40.000 có hai plateau màu đúng qua đường ghép; crop thật tương đương ở offset35.000 cho kết quả khớp **mọi pixel**, góc màu đúng. Không tự viết bilinear sampler hoặc lấy ảnh analysis làm nguồn. Phần dịch homography chỉ đổi hệ tọa độ cục bộ.

Rà tests cũng siết ca JSON lỗi để đòi thông báo `--corners`/JSON, tránh coi mọi exit2 là đạt; ca CLI thiếu script trước TDD từng trả exit2. Test ROI cuối dùng equality chính xác trên fixture cố định, không tolerance rộng. Lượt cuối trong [progress](progress.md).

## Artifacts đã kiểm tra

| Thư mục cục bộ ignored | Nguồn | Warp | Quan sát |
|---|---|---|---|
| experiments/results/mvp03-07-full/ | corners_rgb.png96×64 |95×63|Toàn ảnh; overlay0..3,4vùng màu đúng|
| experiments/results/mvp03-07-perspective/ | synthetic120×80 |93×58|Quad nghiêng thành chữ nhật, đỏ/xanh lá/xanh dương/vàng đúng chu kỳ|
| experiments/results/mvp03-08-diamond/ | synthetic160×160 |99×99|Diamond giữ4đỉnh/màu, không xoắn hoặc mirror|

Đã đọc lại9PNG của3runs, so hash/dimensions với metadata; mở overlay full/perspective/diamond và warp perspective/diamond. Cả22fixtures giữ đúng hash/byte count của manifest. Không đọc, thay hoặc gửi ảnh cá nhân trong đợt này. Các hình màu chỉ chứng minh mapping, không chứng minh chất lượng chữ của ảnh thật.

## Phần còn chờ

Giai đoạn04: config/preset/filter/mode. Detector và debug descriptors ở05/06; canvas pointer mapping, confirmed/revision, persistent storage, nhiều trang và PDF ở các giai đoạn sau. Source/warp không giải quyết mặt giấy cong do nhàu; aspect estimated không là tỷ lệ giấy vật lý hoặc DPI. Bộ development vẫn6ảnh/1tài liệu, test0; chưa có groundtruth hoặc accuracy.

Checklist duy nhất [todo](../tasks/todo.md): 23task chính hoàn thành +AUX02.01/AUX03.01, MVP01.08 bỏqua. Giữ110IDgốc (109cầnlàm+1skip),5optional; hai AUX nằm ngoài tổng chính. Không commit/push/deploy, frontend vẫnhealth.
