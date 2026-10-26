# Rà soát mười task giai đoạn08 — AUX08.01

Ngày17/10/2026. User yêu cầu hoàn thành08.09–10 rồi dò cả10task. Nguồn: [MVP](MVP_Pham_Vi_Va_Ke_Hoach_4_Tuan.md), [checklist](../tasks/todo.md), [kế hoạch](../tasks/plan.md), [hợp đồng ảnh](image-contract.md), [API](api-contract.md), [hướng thuật toán](Phan_Tich_Huong_Thuat_Toan_Tu_Tai_Lieu.md), [smoke có bước chạy lại](../frontend/tests/scanner-smoke.md), [progress](progress.md).

## Kết luận

**Đủ10task theo tiêu chí giai đoạn08; checkpoint08-C1/C2/C3, cổng08 và M2 đạt.** Người dùng nhập ảnh, chọn/xác nhận góc tay, tạo bản quét bằng core thật, so nguồn/kết quả và phóng to đúng full raster. Fullbackend983tests đạt với-Werror,64frontendtests/typecheck/build và browser đạt. Không sửa thuật toán để làm test xanh; chỉ sửa một test cũ không đóng CSV và nhãn hình học dễ gây hiểu nhầm.

M2 là luồng **quét tay** đã dùng được. Detector offline đã có nhưng chưa nốiAPI/UI; phạm vi đó bắt đầu09.01–02. Dataset6development/1doc/test0 và nợimg_004/006 ăn bàn giữ nguyên, không thể suy accuracy/tổng quát từ kiểm thử luồng. Giấy gấp/cong không được dewarp bằng homography.

## Ma trận mười task

| Task | Mã và bằng chứng đối chiếu | Kết luận |
|---|---|---|
| 08.01 configCAS | page_config service/PUTroute, writerlock trướclookup/CAS, fullreplacement, no-opgiữtimestamp, explicitconfirmed, quad/source/warp validation.25configAPItests trong strictfullsuite; concurrent1commit+1conflict, malformed400/owner404/revision409/commitrollback đã có | Đạt |
| 08.02 snapshot render | renders.py giữnormalizedsource/config frozen, CPU ngoàiDB, finalCAS/source/config gate trước publish haiPNG.21service tests trongfullsuite: config/page/session đổi, lỗi process/encode/write/register/commit giữ nguồn/cũ/dọn mới. PNGinternal>15MiB không nhận uploadquota nhầm | Đạt |
| 08.03 HTTP/executor | POSTrender wholeusecase qua sharedworker, confirmed/revision gates, actualfull/previewUUID/size/timings,409/429/health/500sanitized/workerphụchồi.21HTTPtests trong strictfullsuite;UI09–10 gọiAPI thật | Đạt |
| 08.04 mapping | cornerGeometry dùng bitmapW/Hcontain, W−1/H−1 điểm, subpixel/CSSrect, backingDPR không áp vào pointer.27mappingtests/64frontend hiện tại; browserDPR1/2 mới có maxhandleerror.01685323CSSpx<1.936quadparity/22canvasstates là bằng chứng trước | Đạt |
| 08.05 overlay | Native normalizedimg, evenoddmask/4buttonID0–3; nguồn không bị vẽ lên. Lượt mới có3nguồn dọc/ngang/chữnhỏ, sourcehash cũ30tệp nguyên; maskalpha140ngoài/0trong, responsive320/768/1440 khôngtràn | Đạt |
| 08.06 pointer/quad | Hittest/capture/clamp/keyboard/cancel, invalid quad khôngsort.24hittest/quadtests hiện tại; native kéo4góc trangchữnhỏ/keyboard mới đạt. Cancel/lost/Escape/blur/touchsynthetic có bằng chứng05–08, không claim vật lý | Đạt |
| 08.07 draft/confirm | pageRenderState tách persisted/draft, fullconfig inactive giữ, edit/fullimagefalse,save-draftfalse/confirmtrue/reset/cancelsnapshot.12state tests hiện tại; UI3trang explicitconfirm, trở lạiedit mấtconfirmed vàresetphục hồi. Unknowncommit/GETđốisoát có bằng chứng07–08 | Đạt |
| 08.08 current request | PUT/CAS→POSTreturnedrev; page/rev/payload/operation/edit guards; late response khôngghi đè và lỗi giữ ảnhcũ/stale.64frontend gồm12state/race+1APIwire. Heldsave/render/switch/500/dropaftercommit kiểm07–08; đổicomponentảnh sangComparison vẫn giữ cùngstate/guards | Đạt |
| 08.09 comparison/zoom | ComparisonView đọc normalizedsource và render_artifact_id, verify naturaldimensions,fit/100/200/nativeoverflow/keyboard,loading/error/retry,returnfocus0. Browser detailfull1009×1406,preview718×1000;100%CSS1009×1406/200%2018×2812,sameUUID,sourcefit;responsive/labelstale đúng | Đạt |
| 08.10 manual endtoend | UIcreate/filechooser3files→pageselect/fullimage hoặc4cornerdrag→confirm→render→viewzoom. EXIF64×96→63×95, ngang96×64→95×63, detail1200×1600→1009×1406.12mẫu bốn màu thực khác nhau projectH khớp0kênh;3preview byteequal từfull. ForcedDPR2 render/zoom và nguồn/DB cũ nguyên | Đạt |

## Kiểm chứng và lỗi đã xử lý

- Fullbackend **983passed142.37s với-Werror**, gồm67config/render tests giai đoạn08 cùng toàn bộgeometry/core/CLI/DB/executor cũ. Lượt đầu981passed/2failed143.93s do test_detect_batch.py:82 mởCSV trong biểu thức không đóng stream; focusedRED2failed3.10s tái hiện ResourceWarning/PytestUnraisableExceptionWarning. Sửa `with ...open(...) as stream` giữ nguyênassert2rows;7batchtestsGREEN15.10s rồi full983GREEN. Không suppresswarning, skiptest hoặc đổi thuật toán.
- Frontend **64tests192.3675ms**, typecheck/build26modules174ms;JS248.13kB/gzip78.08,CSS8.16kB/gzip2.29. Không thêmdependency. Comparison UI được kiểm bằngbrowser thật, không thêm bộ testframework để lặp lại CSS.
- “Bốn góc hợp lệ” từng dễ bị hiểu là bám biên giấy. Đổi thành “Hình học vùng hợp lệ”, nhắc khung ban đầu là vùng thử chưa nhận diện theo mép giấy. Vùng5% mặc định vẫn làdraft; không auto-confirm hoặc giảdetector.
- Browser đã xem chữ nhỏ/highlight ở100/200%; xác nhận CSS/natural/UUID chínhảnhfull, cuộnviewport được. Returnfocus0→ArrowRight giữ oldimage/stale và khóaquét;reset phục hồi config. Hai cột1440, một cột320/768; đúngviewport thực vànohorizontaloverflow. DPRprobe thật653×432→1306×864, normalizedpoints/maskkhôngđổi;100%fullvẫnđúngởDPR2.
- `experiments/results/mvp08-final-verified/`: before/after/browser-evidence/document/raster-checks/dpr/dpr2-render/layout/console,3fullPNG vàảnhUI. Snapshot **7session/10page/30sourceartifact cũ nguyên cả metadata/config/revision/timestamps/hash**; tài liệu test mới3trang tách riêng. Source mới cũng sohash/previewfull vàcolorproject; không gửi ảnh ra ngoài. PrivateDPRharness archiveignored rồi xóa khỏifrontendroot, console trống.

Ảnh minh chứng:

![So sánh với ảnh full ở100%](../experiments/results/mvp08-final-verified/comparison-100.jpg)

## Ranh giới và nợ còn lại

- GETdetail chưa trả render/previewUUID; reopen đã đọc config/revision mới nhưng cần render explicit để xem ảnh. Fullrender đã persist và đọc quaartifactAPI khi biếtUUID. Đây là giới hạn đã ghi ở07–08; hoàn thiện reopen nhiềutrang ởMVP10.07. Cổng08 không hứa tự mở lịch sửrender/DBcache.
- Lỗi/mất response bắt GET đối soát trước mutation; không tựretry, không coi abortHTTP làrollbackworker/commit. Không jobpersisted/hardkill/GCcrash; các giới hạn executor/fileDB của07 vẫn áp dụng.
- HiDPI kiểm bằng forcedwindowDPR1/2 trên browser thật, thiết bịthậtDPR1; touchsynthetic trước đây vẫnchưathiếtbịcảmứngvậtlý. Không claim đã thử phầncứngkhác hoặc WCAGscreenreaderchuyênsâu.
- Zoom100% là1pixelảnh/1pixelCSS,200% chỉ phóng hiển thị raster; không cải thiện độ nét nguồn hay thay PNG xuất. Ảnh nguồn sauEXIF làảnh chụp đểđốichiếu, không là ảnhgốcraw chưaEXIF.
- Debug persistence/histogramUI/modecontrols/detect nối09; PDF/export11; staticpackaging14. Không dùng983tests làm accuracydetector hoặc kết luận thresholdchomọiảnh.

## Bàn giao

**63task chính+8AUX**,110IDgốc/109active/1skip/5optional. AUX08.01 đúng yêu cầu rà10task, không cộng task con lần nữa. Next **MVP09.01 — API detect và detection run**; đọc contracts/algorithm-notes/audit05 trước nối. M2 đạt trong phạm vi quét tay và các giới hạn trên.
