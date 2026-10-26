# Checklist gói nộp

Bản source `mvp14-submission-v1`. Chỉ đánh dấu các bước có bằng chứng sau lượt giải nén sạch.
Xem [SUBMISSION](../SUBMISSION.md), [README](../README.md), [demo](demo-script.md) và [audit14](audit-phase-14.md).

## Cổng kiểm chứng

- [x] ZIP được tạo bằng allowlist; đọc lại manifest/hash, không có ảnh cá nhân/DB/bí mật/dependencies/build.
- [x] Giải nén sang thư mục mới; tạo venv không system-site-packages, cài đúng30pins và npmci theo lock.
- [x] pipcheck/imports, frontend103tests/typecheck/build và toàn bộbackend/experiments1279tests đạt.
- [x] ChạyCLI1worker từ bản giải nén, health/UI/API cùngorigin, không dùng DB/userdata có sẵn.
- [x] Demo fallback, so ngưỡng, stage/histogram vàPDF3trang; mở/renderPDF kiểm thứ tự/hướng/nội dung.
- [x] Restart backend cùngDB giữconfig/revision/full/stage/artifact; console không lỗi chưa xử lý.
- [x] README/hướng dẫn/báo cáo/số liệu/giới hạn và8task đã được rà, không tự nghiệm thu giai đoạn12.
- [x] ZIP cuối có source/input hash trùng bản đã test, tài liệu cuối đúng trạng thái; checksum ngoài ZIP.

## Thành phần và giới hạn

Gói dùng allowlist trong [script đóng gói](../experiments/package_submission.py), chứa source/tests/lock,
Markdown, hìnhUI từ ảnh tổng hợp, biểu đồ hình học/histogram/số đo, fixtures/demo và CSV/summary số liệu13.
Giữ nguyên inputmanifest/annotations/frozen lịch sử; các đường dẫn tới ảnh riêng không có payload đi kèm.
PDF giáo trình/slide và các log/ảnh thật trong evidence cục bộ không nằm trong gói.

Không có runtime offline hoặc installer; Python/Node phải cài sẵn, cần mạng lúc pip/npmci.
Thư mụcdata được tạo mới khi chạy; bảo toàn toàn bộdata nếu muốn mở lại.
Gói không tái chạy được đo heldout13 nếu thiếu dữ liệu riêng/bảnmã lịch sử; không bỏ cổngfreeze.
Tests dùng dữ liệu tổng hợp nên vẫn phải chạy đủ. Không giả giấy gấp mô phỏng là thực nghiệm giấy nhàu thật.

Ngày nộp/tên nhóm/mã sinh viên/bìa/định dạng giảng viên chưa được cung cấp; không tự bịa.
M4 ở đây là nghiệm thu kỹ thuật gói source/demo, không phải đã gửi bài hoặc hoàn thành thủ tục hành chính.

## Lệnh tạo lại

Chạy từ root có đủ CSV cần đối chiếu, dùng một tên mới:

```powershell
& .\backend\.venv\Scripts\python.exe experiments/package_submission.py --output output/submission/DocumentScanner-MVP-ban-moi.zip
```

Không ghi đè ZIP đã có; kiểm lại danh sách/hash sau khi tạo. Lệnh không gửi, publish hoặc nộp bài cho ai.
## Kết quả đã kiểm ngày26/10/2026

Gói `output/submission/DocumentScanner-MVP-20261026.zip`, checksum cùng tên thêm `.sha256`;
manifest từngtệp nằm trong ZIP. [Bằng chứng kỹ thuật](submission-verification.json) và
[audit8task](audit-phase-14.md) ghi phạm vi, hash nguồn và giới hạn.

Clean candidate ban đầu252tệp; ZIP cuối thêm tài liệu/bằng chứng/ảnhdemo đãkiểm, source chạy/test
và các input trùngbyte với bảnđãgiảinén. Càiđúnglock/venv/npmci/imports/health/build đạt.
Backend/experiments1279passed144,66s; frontend103passed/typecheck/build41module đạt.
Lượt đầu62lỗi do đườngdẫn test262ký tự đượcgiữlog; cùngprefix ởđườngdẫn112ký tự tạođược,
đổiTEMP/basetemp ngắn vàchạy đủsuite, khôngbỏtest/đổicode storage.

Rehearsal sau nhập320,984s; PDF3trang nhúngpixelđúngfull/A4/lề5mm, cả3trang đãrender/xem.
Process298300→296284 giữmetadata và65artifact, UI phục hồiBW/histogram/100%, console0.
Ảnh khôngbiên cốý trống, nếpgấp môphỏng chỉsángtối; chưacó lượt tậpnói của ngườitrìnhbày.
ServerQA8002đãdừng; dữliệu8000/197tệp vàSQL đầu-cuối giữhash, khôngmutation userdoc.
Sửa duy nhấtmột dòngtextUI vềdataset, khôngđổiAPI/schema3/core/preset/lock/nhãn/frozen13.

Một số liênkết lịch sử tớiảnh riêng/giáotrình khôngcó trongZIP đãđượcghi rõ ởSUBMISSION/báocáo.
Các CSV/summary cầnđối chiếu,4hìnhreport,3hìnhdemo vànguồn tổnghợp vẫnđi kèm.
M4 nghiệmthu kỹthuật đạt; không tựđánh dấu7taskstage12 hoặc5tasktùychọn.
