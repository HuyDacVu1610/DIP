# Quét tay và so sánh — nghiệm thu MVP08.10

Đã thực hiện17/10/2026 trên Vite5173/FastAPI8000, browser tích hợp. Evidence riêng tư/synthetic nằm tại `experiments/results/mvp08-final-verified/` (ignored); bảng dưới là các bước đã chạy, cũng là hướng dẫn chạy lại. Không dùng detector trong luồng này.

1. Tạo tài liệu mới bằng UI, chọn file qua filechooser: `fixtures/exif_6.jpg`, `fixtures/corners_rgb.png` và ảnh chữ nhỏ/highlight tổng hợp1200×1600 do `.tmp/verify_phase08.py before` tạo cục bộ. Kiểm cả3 mục “Đã lưu”,3trang đúng thứ tự; ảnh EXIF nguồn64×96, ngang96×64, chữ nhỏ1200×1600.
2. Trang1/2: chọn “Dùng toàn ảnh”, “Xác nhận vùng”, “Tạo bản quét”. Kiểm configconfirmed=true/revision1 và kết quả63×95/95×63. So bốn màu với normalizedsource bằng H thật: không lật/xoắn. Trang3: kéo4handle tới mép giấy tổng hợp, xác nhận rồi render1009×1406; preview718×1000.
3. So sánh phải có hai nhãn “Ảnh nguồn sau chuẩn hóa” và “Bản quét đầy đủ”. URL ảnh bên phải phải là render_artifact_id, naturalWidth/Height1009×1406, không dùng preview718×1000 hoặc canvasoverlay. “Vừa khung” hiển thị trọn ảnh;100% có CSS1009×1406;200% có2018×2812; nguồn vẫnfit. ArrowDown/Right trong viewport cuộn được; không gọi xử lý lại để zoom.
4. “Quay lại chỉnh góc” focushandle0. ArrowRight bỏ confirmed, nút quét khóa, ảnh cũ và caption đánh dấu cũ; renderUUID vẫn ảnh cũ. “Đặt lại góc đã lưu” phục hồi confirmed/config, “Vừa khung” phục hồi fit. Chuỗi trạng thái ghi trong browser-evidence.json.
5. Kiểm viewport320/768/1440×800: khôngtrànngang; nguồn/kết quả xếp dọc ở320/768 và hai cột1440. UUID ảnh không đổi và confirmed giữtrue. Reset viewport sau thử.
6. Trang thử DPR tạm dùng đúng ScannerPage/CornerEditor; ép propertywindowDPR1→2 rồi phát resize. Backing653×432→1306×864, normalizedgóc nguyên, maskalpha140ngoài/0trong, maxhandleerror.01685323CSSpx<1. Render ởDPR2/zoom100% vẫn dùng full1009×1406. Đóng probe; archivehtml/tsx vào evidenceignored và xóa khỏifrontendroot. DeviceDPR thật1; đây là forcedDPR, chưa thử thiết bịHiDPI/touch vật lý.
7. `.tmp/verify_phase08.py after`: so source/config/metadata cũ trước/sau;7session/10page/30sourcehash nguyên. Đọc full/preview qua API, SHA-256 khớp metadata, encode_render_images từ full khớp từng byte preview. Bốn màu khác nhau trên mỗi trang được project qua homography: sai số kênh0 ở12mẫu.
8. Chạy `npm.cmd test`, `npm.cmd run build` từfrontend;64tests/typecheck/build đạt. Từroot chạy `backend/.venv/Scripts/python.exe -m pytest -c backend/pyproject.toml backend/tests -q --tb=short -W error --basetemp=.tmp/pytest-phase08-final`;983tests đạt142.37s. Trước đó strictsuite bắt2lỗi test CSV chưa đóng; đã sửa contextmanager,7batchtests và strictfullsuiteGREEN, không hạ cảnh báo.

Các ca requesttrễ/đổi trang/mất response saucommit/500 giữ ảnh cũ của08.07–08 vẫn có executable state tests và bằng chứng `mvp08-07-08-verified/`; không coi chúng là đã chạy lại toàn bộ trong lượt09–10. API/core regressions nằm trong strictfullsuite hiện tại. [Audit10task](../../docs/audit-phase-08.md) phân biệt lịch sử và lần kiểm mới.

Giới hạn ở mốc08: khi đó mở lại chưa tự hiện render. MVP10.07 hiện đã tự mở full/debug đã lưu; xem mục10.03–07 dưới. DetectorAPI/UI nối09.01–02; đây là M2quét tay, không phải nghiệm thu tự nhận diện hoặc quality/accuracy. Ảnh cá nhân/DB/results không đưa vàoGit.

## Nhận diện — MVP09.01–02, đã chạy18/10/2026

1. Tài liệu QA riêng: nhập anhtestnew, img_004 và blank320×240. Bấm “Tự nhận diện vùng”; kiểm loading rồi đề xuất chưa xác nhận. Ảnh tốt UIheuristic0.635, ảnh khó0.468 kèmLOW_HEURISTIC_SCORE, blankmanual_required→vùng thử5% kéo được. Đây là kết quả đo riêng các ảnh này, khôngaccuracy/khôngcamkết run khác cùngtiming.
2. Nhận diện ảnh tốt hai lần: runID vàstageUUID riêng, cùngnguồn/hash. Không có PUTconfig hoặc render cho tới khi xác nhận tay; confirm→render201×285. Ảnh khó vẫn ăn bàn; cần chỉnh góc theo giấy. Scorelabel ghiheuristic và cảnh báo chọn nhầm nền.
3. Giữ actualresponse200 bằng harness tạm; sửaArrowRight rồi thảresponse: giữgóc tay. Giữ lượt khác, đổi trang rồi thả: không gánproposal trang cũ sangtrang mới. Mock500 có kiểm soát giữdraft, cho thửlại/chỉnh tay. Harness dùng đúng ScannerPage/client, đãarchive/dọnfrontendroot sau kiểm.
4. Kiểm320/768 khôngoverflow vàbuttons trongviewport; resetoverride. Product/probeconsolewarn/error rỗng. Evidenceignored `experiments/results/mvp09-01-02-verified/` gồm browser-evidence/requests/layout/product-console/auto-detection.jpg. Backend996tests-Werror/frontend68tests/typecheck/build đạt; [progress](../../docs/progress.md) ghi migration và hash nguồn cũ.

## Mode và threshold — MVP09.03–04, đã chạy18/10/2026

1. Tài liệu QA riêng gồm ảnhchữViệt/highlight1200×1600, img_003cóbóng1536×2048, corners_rgb96×64. Dùngtoànảnh/xácnhận; giữquad khi so mode. Chuỗi ColorNone→GrayNone→GrayCLAHE4/Gaussian5→BWAdaptive31/C10/Median3→BWOtsu→ColorNone tạo1199×1599. Đổi tham số chỉstale, khôngrequest/khôngtăngrevision tới khiTạo bảnquét; confirmed củaquadgiữ.
2. KernelNone/Colorcontrast/Graythreshold/Otsublock-C disabled vàgiữfullvalues. Chọnblock3/C−20→151/C30→31/C10 nhanhkhôngHTTP. Otsukhóablock-C. Nativefield cólabel/keyboardHome-End-Arrows/Tab. Modekhôngresetpresetngầm; gửi fullconfigPUTCAS→POSTreturnedrevision.
3. Ảnhbóng:Otsu rồiAdaptive151/C30. Ảnhnhỏwarp95×63: block151bịPUT400/rev0giữ, khôngrender; GET→block3/C−20→confirm/renderđạt. Backendkhôngclamp/fallback. NgưỡngOtsu thực165/116 kiểmoffline, chưahiệnUIdebug.
4.9full/preview khớptừngbytefreshsource/core vàColorreturnbằngColorđầu; ColorRGB/Gray-BWL/fullBWchỉ0–255.9session/48sourcehash cũ nguyên.320/768/1440khôngtràn,console sạch, viewportreset/harnessarchive-dọn. ProductcleanBWOtsurevision7 giữtab/screenshot.71frontendtests/typecheck/build và273backendtests liênquan-Werror đạt; full996giữmốc09.01–02, backendkhôngđổi. Evidenceignored `experiments/results/mvp09-03-04-verified/`. [Progress](../../docs/progress.md) ghi giới hạn; khôngaccuracy/tune/đánhgiátổngquát.

## Stage, histogram và giải thích — MVP09.07–08/AUX09.01

1. Tạo tài liệu QA riêng, nhập ảnh tốt/anhtestnew, ảnh trắng, img_004 và ảnh chữ/highlight. Không sửa tài liệu người dùng. Nhận diện ảnh tốt, chờ hoàn tất rồi mở “Xem các bước xử lý và histogram”. Chọn nhận diện: xem overlay, rawedges/closed, trial, descriptor, bốn cạnh và score. Mở JSON cùngrun; so từng số/đơn vị, không coi score là accuracy.
2. Xác nhận vùng → renderColor → đổiGray → render → BWOtsu → render. Mọi renderPOST códebugtrue; viewer GETexactrender_run_id. Color/Gray khônghistogram; Otsu256counts và actualt. Đổi sangAdaptive51/C10/CLAHE → render: histogram trước threshold vẫn256counts, không có ngưỡngt toànảnh. Đổi mode chỉdraft/stale, không tựrender.
3. Chọn warp/filtered/prepared_gray/before_rotation/full/preview. Ảnh từ refs của đúngrun, naturaldimensions khớpJSON. Histogram lấyprepared_gray trướcthreshold/xoay, không từpreviewBW. Đổi draft rồi xem lại nhận diện: diagnostic nguồn còn, không biến góctay thànhproposal.
4. Ảnh trắng→manual_required: stage thật có thể xem, selected=null khôngbịa chu vi/score từkhung5%. img_004→warning/nhánhvùng: mask/Otsu actualt/trial có thật, cảnh báo ăn bàn vẫngiữ. Mở hướngdẫn: DP≠MPP, gócphốicảnh khôngép90°, homography khôngdewarp nhàu.
5. Fault harness tạm (bản sao trong evidence, đã gỡ khỏi app) chủđộng môphỏng: descriptor thiếu→“Không có dữ liệu”; prepared_gray unavailable→incomplete/khôngthayảnh; histogram sai tổng→khôngSVG; wrongrun→báolỗi; GET500→đọclại phục hồi. Đây khôngphải lỗi API thật. Giữ cảGETcũ/mới rồi thả: viewer vẫn đúngrun mới. Unitstate kiểm thêm unmount/superseded/AbortSignal.
6. Responsive320/768/1440 khôngtràn,256bars cònđủ; console sảnphẩm sạch. Resetviewport, xóaharness, giữtab sảnphẩm. Lượt18/10 có27snapshotUI/11run/81artifact/6histogramNumPy/2descriptor;11tài liệu cũ22trang66sourcehash nguyên.76frontendtests/typecheck/build và1031backend-Werror đạt. [Audit8task](../../docs/audit-phase-09.md).

Ở mốc09 chưa tự mở render cũ. Từ10.07, reload tự hiện latest_render và cho GET debug exactrun, không cần POST/detect.

## Đổi tên và thêm trang — MVP10.01–02,18/10/2026

1. Tài liệu QA có ảnh chữ/highlight1200×1600. “Đổi tên tài liệu” → nhập tên Việt có khoảng trắng hai đầu → Lưu: header/list dùng tên đã trim. Space-only báo lỗi khôngPATCH; hủy xóa lỗi/returnfocus. Tên200ký tự lưu được,320/768/1440 không tràn. Backendtests kiểm title201/null/sai kiểu/extra/missingtitle400, saiID404 và commitrollback500. Tên giữ sau physicalrestart/browserreload.
2. Dùng toàn ảnh/xác nhận/renderColor, rồi chỉ đổi draftGray. Chọn batch broken.jpg/exif_6.jpg/alpha_rgba.png: lỗi415 riêng, hai ảnh tốt lưu; page1 vẫn được chọn, modeGray chưa lưu và UUIDfull/debugColor cũ không đổi. Trong GET đối soát bị giữ: input/rename/navigation vẫn khóa. Thả GET: batch xong/nhập tiếp được, không remount editor.
3. Harness tạm chủ động mất response sau upload201: UI báo không nhận phản hồi; GET cuối lượt vẫn tìm thấy trang đã commit, giữ selectedpage/draft/render cũ. Đây là fault mô phỏng sau commit, không phải lỗi backend thật. Rename500 cũng được mô phỏng trước gửi PATCH; UI giữ heading và cho hủy. Harness đã archiveignored rồi gỡ.
4. Tài liệu riêng19trang, chọn2file: thành20trang,1done/1errorquota và chỉ1POST. Input khóa khi đủ20. Request21 trực tiếp/APItest trả413, không sửa page/config/render/file cũ. HTTPintegrationtest mới chạy chuỗi renderedpage→badfile→20→21 và kiểm snapshot/hash.
5. Restart backend thật cùngDB: haiQA document giữ nguyên title/pages/config/render revision;5debug artifact hash cũ giữ.12tài liệu/26trang/78hash nguồn trước đó nguyên.13snapshotUI/19requestrecords, console product sạch, viewportreset; ảnh product-view.png trong ignored `experiments/results/mvp10-01-02-verified/`.

Mốc10.01–02 đạt1043backend-Werror/81frontend/typecheck/build, khi đó checkpoint10-C1/cổng10 còn chờ. Từ10.07 đã tự phục hồi output, cổng10 hiện đạt; xem phần dưới.



## Sắp xếp, xóa, mở lại — MVP10.03–07/AUX10.01

1. Tạo QA ba ảnh600×800 in PAGE1/2/3, fullsource corners manual. Trang vật lý1Color0°,2Gray90°,3BWOtsu270°; xác nhận/render từng trang. Full599×799/799×599/799×599, PageList cập nhật trạng thái saved ngay; đổi draftGray180° chưa lưu không làm metadataColor0° thay đổi.
2. Lên/xuống thành[2,1,3]; selectedID/draftGray180°/run/full cũ giữ. Mock500 trước PUT giữ order; chủ động mất reply sau commit thì GET tìm đúngorder, không retry. Giữ actual response rồi chọn trang3, thảresponse: vẫn trang3. Request thiếu/trùng/foreign400 giữ nguyên snapshot; APIunit kiểm no-op/rollback.
3. UI DELETE dùng harness mô phỏng hoàn toàn trước fetch: hủy “Giữ lại”/Escape không DELETE; xóa trang không chọn giữdraft/chọn, xóa trang chọn sangtrang kế, xóa cuối thànhtrống, xóa session sangtài liệu còn lại. API thật riêng chỉ xóa QA vừa tạo,3trang/9sourcefiles vàcácsession rỗng/nhiều trang; không xóa ảnh/tài liệu cũ.
4. Chụp document/debug/hash, graceful stopbackend rồi mở lại cùngDBschema3. So đủtitle/order/corners/mode/rotation/config/revision/3debugJSON/17hash. UI chọn lại3trang hiện đúngfull/run; Color0° trởlại thaydraftGray180° đãbỏ. MởdebugBW có256bin/tổng478.601/t149/cùngrun;8requestreopen chỉGET, khôngPOST.
5. Backendunit giữCPU qua barrier rồi DELETEpage/session trong render/detect/import: khôngpublishrun/file mới. Cleanup failure/commit rollback/live reference giữan toàn; filesystemcrashorphan vẫn làgiới hạn.3full-preview runtime byteequal corefresh;14old docs50pages150sourcehash/alloldSQLrows nguyên.
6. Responsive320/768/1440 documentkhôngtràn; list320 cuộnngang, resetviewport. Consoleproduct sạch, archive/gỡharness, giữURLproductsạch ba trang.1071backend-Werror/87frontend/typecheck/build/23UIstates đạt. [Audit7task](../../docs/audit-phase-10.md) ghi rõ nguồn bằng chứng/giới hạn; nextMVP11.01 xuất ảnh/PDF.


## Xuất ảnh/PDF — MVP11.05–07,18/10/2026

1. Tài liệu QA riêng ba ảnh1120×1600 in PAGE1/2/3, Color0°, Gray90°, BWOtsu180°. Chỉ trang1 có render; trang3 chưa confirmed: nút xuất bị chặn, không POSTconfig/auto-confirm. Chủ động bấm Xác nhận vùng trang3 (r1→2).
2. Chọn cả3/PDFauto/lề5/PNGembedding, Tạo tệp xuất: GETmetadata → POST409PAGE_NOT_RENDERED → GETkiểm lại → render trang2r1/trang3r2 → POST201. Khôngrenderlạitrang1. TảiPDFthật; mởPypdf/renderPoppler/xemđủ3trang, exactfullpixel/order/MediaBox/matrix.
3. Chỉ chọntrang3/PNG: xoaynháp270° chưa lưu thì bị chặn; trả180° cũ→export/tảiPNG1119×1599modeL, mọi pixeltrùngfull. Chỉ chọntrang1/JPG, giữnháptrang3ở270°: xuất/tảiđược, sauGETđốisoátnháp270°vẫngiữ; JPGRGBcùngdimensions/EXIF-ICC sạch/MAE.0829946032.
4. Unitflow kiểmchangedrevisiontrướcexport/vàtrướcmissingrecovery,unconfirmed/foreign,missinglần2/malformedlist/network/429/lateunmount/wrongreceiptorder đều dừngkhôngretryvôhạn/khôngPUT. Backend18tests mới kiểmcommit/rollback/write/encode/429/busy/error/release,worker còn dùngđược.
5. Browserresponsive320/768documentkhôngtràn;resetviewport. ConsolebanđầucảnhbáoUploadPanel/ExportPaneltrùngkeydocument.id;đãđổikeyexport: vàchạylạitab sạch→khôngwarning/error. Kếtquảcũtrênpanelbỏkhilựachọn/options/revision/dirtyselectedđổi. Khôngthêmmirror-JSXtest.
6. ĐãtảiPNG/JPG/PDFbằngnútTải trongbrowser; serverContent-Dispositionưu tiênfilenameUUIDđuôiđúng. Evidenceignoredmvp11-05-07-verified/runtime-checks/browser-checks/pdf-inspection/export-ui;1194backend-Werror/95frontendtests/typecheck/buildđạt.14docs49pages147sourcehash/alloldSQLrowsnguyên. Task11.08/cổng11/M3chờlượtkiểmchứngcuối,khôngtíchthay.


## Nghiệm thu cuối xuất và restart — MVP11.08/AUX11.01

1. Tạo3nguồn tổnghợp1120×1600PAGE1/2/3,fullquad/confirmed/r1,Color0/Gray90/BWOtsu270. Đưa trang3 lênhai lần bằngUIthành[3,1,2],khôngtăngrevision.
2. Xuất/tảiPDF3trangauto/lề5/PNGnhúng,PNG/JPGmộttrangColor;đổiportrait/lề30/JPEGnhúngxuất/tảiPDF3trangthứ2. Đọcrenderxem6trang/soMediaBox-matrix/fullpixels/order và4ExportRecord;PNGexactfull1119×1599RGB,JPGMAE.0829946032/255.
3. Physicalstop/startbackendcùngDB:4record/30artifactSHA/SessionDetailbằngtrước. ReloadUIvàchọnđủ3trangthấyfull1599×1119/1119×1599/1599×1119r1,khôngPOSTrender/detect. XuấtPDFmớisauđóđược;trongPOSTactualUIworkingtrue/rename-delete-order-fullimage-render-uploaddisabled,sauxongtrởlạiTạotệpxuất/Tải.
4. Integrationtests actualPOSTbarriersuccess/failpage2chặn8mutation/secondexport409;GET/health/tàiliệukhácvẫnđược,lỗikhôngpublishfile/record vàworker/leasephụchồi. Baformat qua haiapp lifespansliêntiếp vàđổiconfigR2giữsnapshot/bytescũ. Đây làtestASGIthậtvớiDBfilesriêng,khôngfaultmocktrongproductsocket8000.
5. Browser320/768/1440khôngtràn,viewportreset,consoletrống,tabsảnphẩmgiữ.15old docs52pages156hashnguồn/alloldSQLrowsnguyên.1199backend-Werror/95frontendtests/typecheck/buildđạt. Evidenceignoredmvp11-final-verified;[audit8task](../../docs/audit-phase-11.md) ghi đủma trận/cổng11M3đạt, next12.01.


## Nhập ảnh tự nhận diện — AUX11.02

1. Tài liệu QA có một trang Color đã render, chỉ đổi nháp thành Gray. Nhập batch paper.png/broken.jpg/blank.png: paper tự proposal, broken415 riêng, blank tự manual_required; giữ trang chọn và nhápGray/Colorfull cũ.
2. Hai trang mới có nhãn chờ kiểm tra/chỉnh tay. Mở paper thấy quad theo mép giấy, score.782; blank thấy khung5% và NO_VALID_QUAD. CảhaiR0/chưa confirmed/configcornersnull. Đối chiếu handledata-u/v với latest_detection:delta1.11e-16; khôngPUT/render/detecttay.
3. Chuyển trang/reloadpaper vẫn hiệnproposal,DB chỉhaiDetectionRuns/haiPOSTdetect chohaiảnh đãnhập. BackendGET/hookkhôngchạy lạiCV. Consoletrống/320-768khôngtràn/viewportreset;ảnhproduct-view.pngvàJSONevidenceignoredauto-detect-import-verified.
4. Unitcases thêm7 kiểmsequence/progress/busy/quota/recovery/owner-source-quad/reopenkhôngghiđè.102frontendtests/typecheck/build,36APIhồiquy-Werrorđạt. Nhận diện429/network được mô phỏng ởunit,khônggọiđó làlỗi serverthậttrênbrowser.17old docs58pages174hash nguồn/alloldSQLrowsnguyên.

### Hồi quy callback nhập ảnh — 18/10/2026

- Tab đã mở trước cập nhật có thể giữ runner cũ gọi onUpload(file) thiếu callback. Unit mới tái hiện TypeError sau upload trước detect; sau sửa phải upload/detect đúng một lần, trả lại trang với proposal chưa xác nhận.
- Bộ chạy dùng useMemo thay vì giữ function implementation trong useState; callback báo tiến độ có mặc định khi thiếu. Khóa qua detection/GET và quota vẫn được kiểm bằng bộ test hiện có.
- Browser QA riêng thêm một paper.png qua file chooser: done/đã đề xuất vùng, một trang/một DetectionRun, góc UI theo proposal và R0/null/false/chưa render. Console sạch.103frontendtests/typecheck/build đạt; evidence callback-upload-fix-verified. Không tải lại ảnh người dùng đã được lưu trong lượt lỗi.


## Smoke trước khóa MVP13.06 — 26/10/2026

Tài liệu QA riêng: nhập page1.png/fake.jpg/page2.png bằng file chooser → 2 trang tự nhận diện,
415 riêng giữa batch, không tự confirmed. Xác nhận trang 1/Color/render; trang 2/BW Otsu/xác nhận.
Chọn cả hai để xuất PDF: 409 thiếu render → app render đúng trang 2 → 201; tải PDF bằng browser.
Đọc/render hai trang, ảnh nhúng bằng full từng pixel và đúng PAGE 1/2.
Graceful restart backend cùng SQLite rồi reload UI: giữ r1/config/full/PDF/38 artifact hash;
chỉ GET phục hồi, không POST/PUT. Xem BW trang 2 ở 100%, console error/warn rỗng.
103 frontend tests/typecheck/build đạt. Evidence ignored mvp13-05-06-verified/browser-reopen.png.
Đây là cổng hồi quy được user chọn cho bản khóa, không nghiệm thu toàn bộ giai đoạn 12.
