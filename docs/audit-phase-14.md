# Rà soát giai đoạn14: bản chạy, tài liệu, báo cáo và gói nộp

Ngày26/10/2026. **MVP14.01–08 và AUX14.01 đạt theo phạm vi kỹ thuật MVP; M4 đạt.**
Giữ102task chính/13AUX/110ID gốc, MVP01.08 bỏ qua. Bảy task giai đoạn12 vẫn chưa nghiệm thu;
không dùng cổng hồi quy đã chấp nhận riêng để tự tích cả giai đoạn đó.
M4 không có nghĩa đã gửi bài, có bìa/thông tin nhóm hoặc đã được giảng viên duyệt.

## Đối chiếu từng task

| Task | Điều kiện nghiệm thu | Bằng chứng và kết quả rà |
|---|---|---|
|14.01| Bản chạy localhost có cấu hình rõ, tách dữ liệu runtime, một worker | FastAPI phục vụ build cùngorigin; settings/root/data/quota, API404/405 và static guard có tests. Mốc01–02 chạy sạch8001; lượt08 chạy lại từ ZIP8002. Đạt. |
|14.02| Khóa dependency, cài/build/test được trên môi trường sạch |30pins và npm lock nguyên SHA; Python3.12.10/Node24.15/npm11.12.1, venv khôngsystempackages/npmci mới. Lượt08 đủ1279backend/experiments+103frontend, typecheck/build41module. Đạt, cần mạng lúc cài. |
|14.03| README ghi lệnh đã chạy/root/data/lưu bền/lỗi/localhost | Tự theoREADME ở sourcecopy/venv/DB mới03–04, rồi ZIP giải nén08. Bổ sung giới hạn đường dẫn Windows phát hiện ở lượt08, không nới storagegate. Đạt. |
|14.04| Hướng dẫn tạo/nhập/góc/mode/lưu-mở/xuất, trạng thái và ảnh thật |4ảnhUI với mẫuQA, walkthrough2trang/PDF-PNG/39artifact/restart ở03–04. Lượt08 thêm UI3trang, fallback, stage và65artifact qua restart. Đạt. |
|14.05| Thuật toán/công thức/tham số/phần thư viện và tự viết, đối chiếu lý thuyết | Báo cáo mục1–7,3PDF kiểmhash và các trang liên quan, nguồnOpenCV; Canny/closing/contour-DP/descriptors/score/NMS/H/CLAHE/Otsu/Adaptive. Hình thật từ số liệu/biên, ảnhdevelopment riêng qua linkcục bộ. Đạt; DP không phảiMPP. |
|14.06| Dataset/split/metrics/bảng đo khớpCSV, mục tiêu chưa đạt và giới hạn |4bảng/hashledger,24development/9enhancement/7test/168samples;140measured/28warmup/p50/p95/RSS đã tính lại. Giữ img_004 sai,1doc/split và thiếu nhàu/lóa/highlight thật. Đạt; không suy accuracy tổng quát. |
|14.07| Chuẩn bị demo5–7phút, fallback/so ngưỡng/stage/PDF3trang và câu hỏi |5mẫu tổng hợp có generator/hash/ghi nguồn; kịch bản và34câuQ&A. Rehearsal UI sau nhập320,984s, tạoPDF ở229,785s, console0. Ảnh sáng tối quanh nếp gấp chỉ là mô phỏng; ca gấp thật development được chỉ đường dẫn riêng. Đạt kỹ thuật; người trình bày còn cần tập nói. |
|14.08| Clean run, kiểm nội dung gói source/docs/kết quả, checksum và checklist | ZIP allowlist, manifest từngtệp, giải nén riêng/venv/npmci/build/test/HTTP/UI/PDF/restart; source trongZIP cuối bằngbyte source đã test, chỉ cập nhật tài liệu sau kiểm. Đạt. Không gửi bài/publish; ảnh riêng/DB/log/deps/dist/PDFmôn học bị loại. |

Chi tiết: [bản chạy](local-runtime.md), [README](../README.md), [hướng dẫn](user-guide.md),
[báo cáo](report.md), [demo](demo-script.md), [Q&A](defense-questions.md),
[checklist nộp](submission-checklist.md), [bằng chứng gói](submission-verification.json).

## Lượt kiểm sạch cuối

Bản candidate được tạo bằng `experiments/package_submission.py`, đọc lại từngbytes/hash rồi giải nén
vào `.tmp/mvp14-submission-clean/DocumentScanner`. Ban đầu không códata/venv/node_modules/dist.
Thực hiện pipinstall đúngrequirements/pipcheck/imports/npmci, frontend103tests (0skip/0fail),
typecheck/build41modules; ba tệpbuild bằngbyte build của workspace sau cập nhật chú thíchUI.

Lượtpytest đầu:1217passed/62errors/143,23s. Các lỗi cùnggốc ởmkstemp đườngdẫn262ký tự;
đã xác minh thư mục cha tồn tại, cùngprefix tạođược ởđườngdẫn112ký tự nhưng lỗi ởcây lồngsâu.
Giữ nguyênlog/diagnosis; đặtTEMP/basetemp ngắn rồi chạy lại **toàn bộ1279tests đạt144,66s**,
`-W error`, không bỏtest, không sửaassertion/registry hoặc đổi storage/thuậttoán.
README vàchecklist đã ghi cách dùng đườngdẫn ngắn. Đây là giới hạn môi trường, không chứng nhận
mọi đườngdẫn dài trên Windows đều được hỗ trợ.

Backend thật8002 từCLI mộtworker, process298300 dừng có `Application shutdown complete`,
khởi động lại bằng process296284. Detail/config/revision/full/debug và65artifact giữhash, FKcheckrỗng.
Browser sau restart mở lại BW r3/histogram đúnghash,100%full vàconsole0. Server kiểm chứng đãdừng;
server8000 của người dùng được giữ, chỉ cập nhật các tệpbuild cho dòng chú thíchUI đãsửa.

Demo nhập baPNG qua filechooser thật, frontend tựdetect từngảnh:2proposal/1manual_required,
không tựconfirmed. UI xác nhậnColorr1; bóngBWMedian3/Otsur2→Adaptiver3;
ảnhkhôngbiên dùngtoànảnh/dịchgóc bằngphím/Grayr1. Chỉ đổi threshold.method giữa haiBW:
warp/preparedgray/hash/histogram bằngnhau, sum555901 vàOtsut156/Adaptivenull.
Ba fullPNG bằngbyte kếtquảcore; rawCanny UI bằngpixel khi replay trên mẫu tổng hợp.

PDF3trang A4portrait/lề5mm/PNG: pypdf kiểm từng ảnh nhúng bằngpixel full tương ứng, tỉlệcontain đúng,
Poppler render vàxem đủ3trang. ThứtựColor01/BW02/Gray03 đúng; trang03đồng nhất là ca cố ý,
không phải bỏ mất nội dung. Adaptive vẫn có ít nét/đốm ở mép, không gọi là khôi phục hoàn hảo.
PDF đã tải quaartifactAPI; lượt03–04 trước đó còn có thao tác bấm tảiPDF thật trong browser.

## Những vấn đề được phát hiện và xử lý khi rà

1. Chú thích thuật toánUI còn ghi “development6ảnh/test0”: thay bằng giới hạn mỗi split một tài liệu,
   liên hệ báo cáo. Chỉ mộtdòng văn bản ởPipelineViewer, không đổi logic, score hoặc nhãn.
2. Đườngdẫn test lồngsâu vượtgiới hạnWindows: táihiện, giữlog, đổi thư mục tạm ngắn; chạy lại đủsuite.
3. Gói source nếu sao chép cả thư mục sẽ mang theo ảnh riêng/DB/dependencies: dùng allowlist,
   kiểm hash từngảnh chỉ thuộc fixtures/ảnh tổng hợp/biểuđồ đã rà, giữCSV màkhông cópixeltrang riêng.
4. Báo cáo có link tới ảnh thật/PDF lý thuyết trong workspace: ghi rõ nguồn tham chiếu cục bộ,
   không tự đưa tài liệu riêng hoặc giáo trình của môn học vàoZIP. CSV/summary/hình báo cáo vẫn có trong gói.

## Giới hạn giữ công khai

- Dataset13ảnh/2doc, mỗi split1doc;7/7test chỉ áp dụng trong nhóm đã đo. Một người gán nhãn,
  test đã được quan sát ở lượt trước; không có kết luận tổng quát hoặc bộ test mới.
- img_004/006 có thể ăn bàn; fitdistance/epsilon/cạnhyếu chưa triển khai, không tựtune theo test.
  Homography không dewarp cong/nhàu mạnh, OCR/phục hồi thông tin mất chưa có.
- Demo tổng hợp không tăng số ảnh thật, không chứng minh xử lý lóa/nhàu/highlight thật.
  Rehearsal đo thao tác/kiểm dữ liệu tự động sau nhập; chưa có người nói thành tiếng.
- Applocalhost/mộtprocess, chưa multiuser/Internet; queue/khóa trongRAM, crash cóthể đểorphan,
  chưaGC/migration/Undo. Tên tệp tải làUUID, không có lịch sửlinktải đầy đủ qua reload.
- Sourcepackage cầnPython/Node cài sẵn vàmạng lúc cài; không installer/offlinebundle.
  Không tái chạy benchmark13 khi thiếu ảnhriêng vàsourcekhácfreeze. Snapshot13 giữ nguyênSHA,
  khôngghiđè đểgiả pass. Số đo13không được đổi thành số đo của bảnnộp14.
- Chưa có ngày nộp/mẫu bìa/tênnhóm/mãsinhviên hoặc địnhdạng báo cáo bắt buộc; không tựbịa
  vàkhông coi M4 kỹ thuật là đã nộp bài chính thức.

## Bằng chứng

Ignored `experiments/results/mvp14-07-08-verified/`: candidate-manifest, clean-steps/logs ban đầu,
backend-tests-short-path.log, windows-path-diagnosis, rehearsal/events, UI screenshots,
runtime trước/sau restart, pixel-checks, pdf-inspection, PDF/PNG đãrender vàverification cuối.
Các mốc01–02/03–04/05–06 giữ bằng chứng riêng; không sửa lại kết quả cũ.
ZIPcuối vàSHA-256 ở `output/submission/`, bịignore; manifest trongZIP gắn đúngbyte của nguồn/tài liệu.
DB đang phục vụ8000 và197tệpdata có ở đầu lượt này giữnguyênSQL/hash; không suy ngược rằng DB
khôngthayđổi giữa cácphiên trước. Không mutation dữ liệu người dùng trong lượt nghiệmthu này.
Khôngcommit/push/deploy/agents hoặc gửiảnh ra dịch vụ ngoài.
