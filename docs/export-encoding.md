# Xuất PNG/JPG và bố trí một trang PDF — MVP11.03–04

Ngày18/10/2026. Kế thừa [snapshot/lease11.01–02](export-snapshot.md), [hợp đồng API](api-contract.md) và [checklist](../tasks/todo.md). Hai task03–04 tạo bytes ảnh/PDF một trang từ full render đã xác nhận. Từ11.05–07 đã có ghép/lưuExportRecord/API/UI, xem [luồng xuất](export-workflow.md); next11.08. Không nghiệm thu cả giai đoạn11/M3 từ việc có encoder.

## 11.03 — Ảnh đơn

`export/images.py` độc lậpHTTP/DB/filesystem. `encode_image(full_bgr,format,title='document')` nhận grayHxW hoặcBGRHxWx3 uint8, mỗi chiều2..2400; trả EncodedImage frozen(payload,mime,filename,width,height). Không resize/filter/threshold/xoay lại, không dùng preview và không mutate array đầu vào.

- PNG dùng encoder sạchRGB/L hiện hữu encode_stage_png: BGR đảo kênh đúng trước encode, gray/BW giữL. Lossless/cùngdimensions; BW giữ cả nét1pixel và các mức0/255 của full.
- JPG dùng Pillow từ ảnhRGB/L mới, **quality95/subsampling0**, không EXIF/ICC. Là lossy kể cả ởBW; PNG phù hợp hơn để giữ nét chữ. Không có trườngquality mới trong request, không ngầm đổi lựa chọn JPG của người dùng.
- Tên tải dùngdownload_filename: chuyển dấu Việt sangASCII, thay dấu phân cách/control/path bằnghyphen, slug≤80ký tự/fallbackdocument, tránhDOSreservedbasename, extension chỉpng/jpg/pdf từ whitelist. Đây là tên gợi ý tải xuống, không phải path lưu artifact. Ởmốc03–04 chưa kiểm HTTP; từ11.07 đã tải thật quaartifactGET vớiContent-Dispositioninline/UUID server. Tên gợi ý chưa đượcserver dùng làmfilename.

`services/exports.encode_snapshot_image(store,snapshot)` yêu cầu đúng một trangPNG/JPG, gọiload_export_pixels trênfull descriptor của snapshot. Sau verify, đọc bytes và kiểm lạiSHA/size, decode chỉPNG modeRGB/L/singleframe/đúngdimensions/sạchEXIF-ICC, trả BGR/gray như hợp đồng. I/O hoặc decoder sai được bọcArtifactFileError. Tên gợi ý lấy từ title/pageIDprefix/revision của snapshot rồi sanitize/bound. Hàm chỉ chuẩn bị bytes, không thêm Artifact/ExportRecord. Phải gọi bên trongexport_snapshot hoặcwriter củarun_export để giữ lease tới khi đọc/ghi/commit hoàn tất.

## 11.04 — Một trang A4

`export/pdf.py` cómm_to_points,layout_a4,append_pdf_page,encode_pdf_page. DùngReportLab đã khóa trong requirements; không thêm dependency runtime.

Đổi đơn vị: `point = mm / 25.4 × 72`. A4portrait210×297mm, landscape297×210mm. Auto chọnlandscape khi **fullwidth>fullheight sau rotation**, còn lạiportrait (ảnhvuông cũngportrait); explicitportrait/landscape được giữ. Không xoay thêm ảnh hoặc suy luận hướng đọc chữ. Đổi hướng tờPDF chỉ thay khung giấy, không xoaypixel đã có.

Với paperPw×Ph, marginm(point), ảnhW×H:

```text
s = min((Pw - 2m)/W, (Ph - 2m)/H)
draw_width = W*s; draw_height = H*s
x = (Pw - draw_width)/2; y = (Ph - draw_height)/2
```

GốcReportLab ởgóc dưới trái. Mỗi trục dùng cùngs, căn giữa trong lề, không stretch/crop để lấp đầy. Full pixels không resize lại; phép scale chỉ là kích thước đặt ảnh trênPDF. Dimensionsstrictint2..2400, orientationenum vàmarginfinite0..30mm kiểm ởpurelayout cả khi gọi ngoàiAPI.

append_pdf_page đặt page size, drawImage fullRGB/L đã encode vàshowPage đúng một lần; trả PdfPageLayout frozen. encode_pdf_page tạoCanvas/BytesIO, append một trang vàsave→PDFbytes thật. Caller11.05 có thể lặpappend_pdf_page để ghép; không có ghép/lưu nhiều trang ở task04. image_encodingpng dùng ảnh nhúnglossless, jpeg dùngJPEG95/0 nhúngDCT; không có rotationPDF bổ sung. PDF ảnh, chưaOCR/tìm chữ.

## Kiểm thử và nghiệm thu

51test mới:28image (channels/PNGexact/BW1pixel/invalidarrays/safename/decodegate/full-vs-preview) và23PDF (mm/A4/auto-square/explicitorientation/margin0-5-30/invalidoptions/standalone/header/embed/onepage). RED trước module/encoder, GREEN sau triển khai. Không thêmPypdf/Poppler vào requirements; parser/render dùng bundled tools cho nghiệm thu thật.

- Focus83passed17.96s gồm snapshot/mutation/lifecycle regressions. Full `-W error --tb=short --basetemp=.tmp/pytest11-03-04-full`: **1176passed167.56s**. Frontend không đổi, không chạy lại frontendtests/build; mốc87tests/build ở10 là lịch sử.
- DB tổng hợp riêng:3nguồn1200×1600 có gócmàu/chữViệt/highlight/nétmảnh; xác nhận fullquad,render Color0/Gray90/BWOtsu270. FullColor1199×1599, Gray/BW1599×1199; preview cạnh1000, mọi ảnh xuất dùngfullID và cùngdimensions lớn hơnpreview.
-6tệp PNG/JPG được ghi/mở lại bằngPillow.3PNG khớp toànpixel vớifull, BWbinary giữ0/255; JPGMAE lần lượtColor**0.0536005354**,Gray**0.0364181951**,BW**0.0201069163** mức/channel trên0..255. Đây là sai sốpixel của3ảnhQA, khôngaccuracy/khôngcamkết cho ảnh khác. TênASCII/mime/kênhRGB-L/EXIF rỗng đúng.
-4PDF thật, mỗi file đúng1page: portraitColor/PNG5mm, auto-landscapeGray90/PNG5mm, forcedlandscapeColor/JPEG30mm, forcedportraitBW270/PNG0mm. Pypdf đọcMediaBox595.2756×841.8898point hoặcđảo,1imageXObject/fullresolution/khôngRotate;3PNG nhúngpixel-equal full, JPEG lossy. Contentmatrix khớpfitrect<.001point.
- Poppler96dpi render cả4page;16mẫu góc chiếu theo fitrect có lệchchannel tối đa2. Đãxemcontactsheet: khung/mép/chữ/highlight đầy đủ, khôngcắt/giãn ảnh; hướng chữ theo rotation đãchọn, không tự dựng hướng đọc. TệpQA ngoàiGit tại `experiments/results/mvp11-03-04-verified/`:6images,4PDF,4renders,contactsheet,JSONrequest/image-checks/pdf-checks/pdf-inspection/document/runtimeDB. Bộ tạo chỉ ghi tệp kiểm chứng, **0ExportRecord**; chưaHTTPdownload/UI.

Checkpoint11-C1 (01request/02snapshot-lease/03imageencoder) đạt.11.04layout/onepage đạt; checkpoint11-C2/cổng11/M3 vẫn chờ11.05–08. Next **MVP11.05** ghép/lưu PDF nhiều trang theo cùngsnapshot/order/lease.


Cập nhật11.05–07: ghép/lưu/API/UI tải PNG/JPG/PDF đã kiểm, checkpoint11-C2đạt;1194backend-Werror/95frontendtests/typecheck/build. Next11.08 kiểm chứng cuối toàn giai đoạn. Các số đo ở mục03–04 phía trên là lịch sử. [Luồng xuất hiện hành](export-workflow.md).


Cập nhậtnghiệmthu11.08/AUX11.01: cả8task/checkpoint11-C1/C2/cổng11/M3đạt,86main+11AUX;1199backend-Werror/95frontendtests/typecheck/build. NextMVP12.01. Cácnext/chờởmốc11.01–07phía trênlàlịch sử;trạngtháihiệnhànhxem [audit8task](audit-phase-11.md).
