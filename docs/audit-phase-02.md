# Rà soát tám task giai đoạn 02 — AUX02.01

Ngày: 14/10/2026. Người dùng yêu cầu kiểm tra lại đặc tả và bằng chứng, ngoài triển khai MVP02.07–MVP02.08.

## Kết luận

**Tám task đạt tiêu chí của giai đoạn 02 sau đợt rà soát/sửa lỗi này.** Phát hiện một lỗi làm tròn số thực ở helper resize (task 05), đã tái hiện bằng 3 tests thất bại và sửa bằng phép tính nguyên tương đương round-half-up. Toàn backend **147 tests đạt trong 25.17s**. Bộ development hiện có **6 ảnh khác nhau / 1 tài liệu vật lý**, được người dùng xác nhận; chưa có ảnh test hoặc ground truth góc.

Kết luận này nghiệm thu lõi nguồn/resize/CLI/dữ liệu đầu vào, không phải ứng dụng scan hoàn chỉnh hoặc kết quả accuracy. Quy mô 10 tài liệu/40 ảnh là kế hoạch cuối, chưa phải số đã thu. Cổng giai đoạn 02 đạt; có thể sang hình học giai đoạn 03.

## Ma trận đối chiếu

Nguồn yêu cầu: [todo](../tasks/todo.md) giai đoạn 02; [MVP](MVP_Pham_Vi_Va_Ke_Hoach_4_Tuan.md) mục 5–6; [image-contract](image-contract.md) mục 1–2; đặc tả gốc mục 9.1–9.2/16.1, áp dụng thay đổi MVP (10/40, hai split thay kế hoạch gốc 80 ảnh/ba split).

| Task | Yêu cầu được kiểm tra | Mã/tài liệu thực tế | Bằng chứng | Kết quả |
|---|---|---|---|---|
| MVP02.01 | Fixtures nhỏ, nguồn tổng hợp rõ; EXIF/alpha/tệp giả/hỏng/header quota | create_fixtures.py, fixtures/manifest.json, 22 assets | So SHA-256/dung lượng 22 tệp; load 10 ảnh hợp lệ; 3 header-only quota probes không load | Đạt |
| MVP02.02 | JPEG/PNG thật, một frame, ≤15 MiB/16 MP, dimensions ≥2 trước load | processing/normalize.py: validate_image | Bộ normalize có case đúng ngưỡng/+1 byte, PNG đuôi JPG, fake/BMP/APNG, CRC/header/truncation, bomb warning/error; tests chặn parser/verify/load với input quá quota | Đạt |
| MVP02.03 | Giải mã rồi EXIF một lần, alpha trắng, BGR uint8, giữ nguồn | normalize_image | 8 hướng EXIF với bảng màu kỳ vọng độc lập; RGBA/LA/palette/tRNS, gray/CMYK; bắt payload JPEG/PNG lỗi dù header qua; 6 ảnh development pixel/source không đổi | Đạt |
| MVP02.04 | PNG lossless không EXIF cũ, dimensions/hash của đúng payload | encode_normalized_png, EncodedSource | Ghi/đọc tệp thật; so mọi pixel/dimensions/EXIF trống/file SHA; repeated/hash-change/strided arrays; reopen không xoay lần hai | Đạt |
| MVP02.05 | Không upscale, giữ tỉ lệ dự kiến, làm tròn half-up, dimensions thật | image_sizes.py, test_image_sizes.py | 29 tests gồm dọc/ngang/nhỏ/1-pixel/gray/BW/invalid; 3 regression cases số thực đã sửa | Đạt sau sửa |
| MVP02.06 | CLI một ảnh tạo source/thumbnail/metadata, lỗi rõ, giữ nguồn | normalize_one.py, test_normalize_cli.py | 16 tests subprocess; EXIF/alpha/fake và ảnh người dùng đã chạy thật; 6 ảnh mới cũng chạy CLI, pixel/hash đúng; Unicode/outside-cwd/byte-cap/no-overwrite | Đạt |
| MVP02.07 | Schema, split theo document_id, dự kiến 10/40, nhãn sau EXIF; không tune test | dataset_manifest.csv, dataset.md, validate_dataset.py | 18 tests ID/path/hash/condition/split/leakage; --check-files trên CSV thực → dev 6 ảnh/1 doc, test 0; user xác nhận nhóm vật lý | Đạt |
| MVP02.08 | ≥6 ảnh development thực; quan sát điều kiện, nhóm/split/path đúng | 6 dòng CSV; ảnh gốc trong experiments/data, PNG ở results/development | Nhận 7 JPG → 6 SHA khác nhau; giữ bản sao trùng nhưng không đếm; xem cả 6; có sáng đều, nghiêng, góc gấp, bóng đậm/nền gỗ; normalize/decode/hash/pixel đúng | Đạt nhóm ban đầu |

## Lỗi đã tìm và sửa

Helper trước dùng float `scale=max_edge/longest`, rồi `floor(dimension*scale+0.5)`. Phép tính float có thể làm giá trị half chính xác nhỏ đi một lượng rất nhỏ:

| Nguồn W×H | max_edge | Giá trị toán học cạnh ngắn | Trước sửa | Sau sửa |
|---|---:|---:|---:|---:|
| 77×9856 | 320 | 2.5 | 2 | 3 |
| 76×1216 | 1000 | 62.5 | 62 | 63 |
| 11×1760 | 1200 | 7.5 | 7 | 8 |

Đã thêm các tests trước khi sửa: **3 failed, 26 passed**. Công thức mới tính bằng số nguyên:

```text
rounded = (2 * dimension * max_edge + longest) // (2 * longest)
```

Đây là đúng `floor(dimension*max_edge/longest+0.5)` với dimensions nguyên dương, tránh sai số float. Không đổi INTER_AREA, quota, min display 1 hoặc chính sách no-upscale. Focused resize sau sửa **29 passed in 0.54s**; full suite cũng đạt. Các thumbnail development 240×320 đã được so lại với helper mới.

## Dữ liệu và kiểm chứng trực tiếp

- Nhóm mới: 7 tệp JPG do người dùng cung cấp, 6 ảnh khác byte. Hai tệp có/không hậu tố `(1)` trùng SHA; không xóa tệp của người dùng, chỉ bỏ bản sao khỏi số đếm/CSV.
- Người dùng xác nhận cả nhóm chụp cùng một tờ giấy → tất cả `doc_01`, development. Không suy luận document_id từ tên tệp hoặc coi 6 góc chụp là 6 tài liệu.
- Các source PNG 1536×2048 không EXIF, thumbnails 240×320; pixel/hash của từng tệp đúng, raw bytes giữ nguyên. Condition gắn theo ảnh đã xem; bóng đậm dùng shadow_strong, không ghi giả là bóng nhẹ.
- Metadata/hash checker chỉ chứng minh cấu trúc, phân nhóm đã khai báo và tệp đúng checksum; không tự chứng minh danh tính vật lý, nhãn góc, chất lượng detector hoặc accuracy. Xác nhận nhóm đến từ người dùng; góc chưa gán.

Các ảnh, thumbnails, metadata runtime và inventory/hash kiểm chứng nằm trong data/results/.tmp được ignore. CSV có ID/path/hash để tái lập; không gửi nội dung ảnh ra dịch vụ ngoài.

## Lệnh và kết quả hiện hành

```powershell
& .\backend\.venv\Scripts\python.exe -m pytest -c backend/pyproject.toml backend/tests
& .\backend\.venv\Scripts\python.exe experiments/validate_dataset.py --check-files
```

Kết quả: **147 passed in 25.17s** = 1 health +83 normalize +29 resize +16 CLI +18 dataset. Validator thực trả development 6/1 doc, test 0/0 doc, files_checked=true. Full pytest dùng quyền auto-review đã cho phép vì TestClient async bị hạn chế sandbox, như bằng chứng môi trường trước; không skip hoặc tắt test/cảnh báo.

Ngoài pytest đã kiểm tra lại hash/dung lượng của 22 fixtures, load 10 fixture hợp lệ, và so trực tiếp cả 6 source/thumbnail với mảng normalize/resize. Không lặp frontend build/browser vì phần này không đổi frontend và chưa có UI nhập ảnh.

## Phạm vi chưa được kết luận

HTTP upload đọc khối/quota 20 trang, DB/lưu bền trong ứng dụng, preview từ full render và UI scan nằm ở các task sau. Các helper/CLI hiện không thay cho các chức năng đó. PNG source nội bộ có thể lớn hơn 15 MiB; byte cap chỉ ở upload, source vẫn giữ pixel quota.

Nhóm 6 ảnh cùng một tờ giấy đủ MVP02.08 nhưng chưa có độ đa dạng/độc lập để kết luận khả năng tổng quát. Cần bổ sung tài liệu khác và bộ test theo document_id, nhãn trên source sau EXIF, khóa cấu hình rồi mới đánh giá ở giai đoạn 13. Không có metric accuracy/IoU/latency dataset trong đợt này.
