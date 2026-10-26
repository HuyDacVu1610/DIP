# Nhật ký tiến độ Document Scanner

## 26/10/2026 — Bổ sung bộ thuyết trình sau M4

Theo yêu cầu người dùng: bộ 12–15 trang và kèm PowerPoint. Đã tạo 15 trang tiếng Việt,
ghi chú người trình bày cho đủ 15 trang, thời lượng gợi ý tổng 525 giây chưa gồm demo trực tiếp.
Nội dung tập trung Canny/closing, biểu diễn và mô tả biên, Douglas–Peucker, scoring/NMS,
homography, CLAHE và Otsu/Adaptive; có kiến trúc, luồng nhiều trang, số liệu và ca sai img_004.
Nguồn số liệu là report-data của giai đoạn 14 và CSV giai đoạn 13 đã khóa. Giữ rõ mẫu số
3 GT development, 7 GT test và giới hạn mỗi split chỉ có một tài liệu. Ảnh minh họa là mẫu
tổng hợp hoặc UI QA sẵn có; đồ thị ca sai chỉ dùng tọa độ contour/quad, không đưa nội dung riêng.

Dùng using-agent-skills và Presentations; tạo, chỉnh và xem riêng đủ 15 trang trong Artifact Session.
PowerPoint cuối: `output/presentation/DocumentScanner-ThuyetTrinh.pptx` (1.078.025 byte),
SHA-256 `cb3ef7cb865c7637d0d293a332a187d0885f098eafaadabfcdd62040bbc098fc`.
Kiểm gói/layout/font Arial, nhập lại bằng Artifact Tool, 6 bảng và 2 biểu đồ native cùng
2 workbook dữ liệu nhúng đạt. 13 ảnh nhúng khớp byte snapshot, đủ 15 phần ghi chú có nguồn.
Dữ liệu biểu đồ làm tròn 8 chữ số thập phân để Excel giữ chính xác snapshot hiển thị;
không đổi số liệu gốc/metrics. Không tuyên bố đã mở bằng Microsoft PowerPoint.
Bằng chứng và bản dựng ở `.tmp/presentation/`; tệp xuất nằm ngoài Git.

Giữ nguyên thuật toán, dữ liệu ứng dụng, bản khóa và ZIP nộp trước đó. Hash ZIP vẫn
`4648c3c71232871e3669af0e352d48726a71f02a8f8288347455fd32a138d600`.
Slide là bổ sung sau M4, chưa nằm trong ZIP. Không cộng ID vào checklist 110 task gốc.

## 26/10/2026 — MVP14.07–08 và AUX14.01: demo, gói nộp, rà8task

User yêu cầu làm07/08 rồi dò cả8task14. Đã có demo-script,34câuQ&A,5PNG tổng hợp/manifest/
README nguồn gốc vàgenerator tái lập. Task07 tách a/b/c,08 tách a/b để mỗi nhóm≤5tệp;
không cộng lại parent. AUX14.01 ghi riêng yêu cầu rà cả giai đoạn. Sau nghiệmthu102main+13AUX/
110ID gốc;01.08 giữ bỏqua,7taskstage12 và5optional chưa nghiệmthu. Checkpoint14-C3/cổng14/M4
đạt kỹthuật, không phải đã gửi bài, có bìa/thôngtinnhóm hoặc tập nói của người trìnhbày.

Skill đã áp dụng using-agent-skills, documentation-and-adrs, browser-testing-with-devtools quaCUA,
code-review-and-quality, incremental-implementation/git-workflow vàPonytail chohelpers đónggói;
pdf dùng đọc/render/kiểm PDF doapp xuất. Debugging-and-error-recovery khi test fail.
Khôngspawnagent/commit/push/deploy/gửiảnh hoặc tin nhắn bên ngoài.

Năm mẫu900×1100 gồm sạch/bóng/đồng nhất khôngbiên/highlight/vệt nếp gấp. Generator chạy lặp
chohash bằngnhau, thưmục tồn tại bịtừchối ghiđè. Đây là mẫu tổnghợp riêng, không đưa vàodataset13.
Mẫu05 chỉ đổiánh sáng trênđa giác phẳng, không giả giấycong3D; ảnhgấp thật img001/006 chỉthamchiếu
cục bộ. Preflight4proposal/1manual_required; mainUI dùng01/02/03, phụ04/05 đểgiảithích giới hạn.

CandidateZIP252files được đọc lại bytes/hash rồi giải nén mới tại.tmp/mvp14-submission-clean/
DocumentScanner, banđầu khôngdata/venv/node_modules/dist. Thực hiệnREADME/Python3.12.10x64,
venv khôngsystempackages/pipinstall30pin/pipcheck/imports;Node24.15/npm11.12.1/npmci24packages.
Frontend103passed295,1515ms/typecheck/build41modules148ms. Cài đặt/test/build cólogs từngbước.

Pytest lầnđầu1217passed/62errors143,23s: mkstemp không tạo được fileđườngdẫn262ký tự mặc dù
parent cósẵn. Minimalrepro cùngprefix ởparent sâu fail/cùngprefix đườngdẫn112ký tự thànhcông.
Giữbackend-tests.log/windows-path-diagnosis.json/clean-steps error; khônggiả càiđặt thất bại hoặc
che failure. ĐổiTEMP/basetemp sangworkspace.tmp ngắn vàchạy lại **toàn bộ1279passed144,66s**
-Werror, khôngskip/đổiassert/storage/registry hoặcnângdependency. README/checklist bổsungca này.
Đây là hạnchếWindows/đườngdẫn đãquan sát, khônghứa hỗtrợmọi đườngdẫndài.

Chỉ sửa một dòngtextPipelineViewer cũghi “development6ảnh/test0” sanggiới hạnmỗi split1doc/
xemreport. Không đổi logic/frontendstate/API/schema3/core/preset/lock/manifest/nhãn. Bảnclean
đãbuild/test textmới;buildroot thêm mộtlượt để8000cófileJS mới, ba distfiles bằngbyte cleanbuild.
So packaging-manifest14.01chỉPipelineViewer đổi trongtập sourcecũ. Freeze13SHAce89a90… nguyên,
chạycheck từsourcegiảinén trả1 đúnglýdo sourcekhác; khôngghiđèfreeze/đọc lạipixelstest hoặcbenchmark.

CLI thật1worker8002/DBmới, process298300. Browser tạoDemo14/nhập3PNG bằngfilechooser thật,
autodetect2proposal/1manual_required vàkhôngauto-confirm. Filechooser tool mất434,907s đểtrả
điều khiển; ghi riêng, khôngnhét vào sốđoCPU hoặcgiả demo0–7phút đã gồmnhậpfile.
Rehearsal sau nhập từ10:05:26.340Z đến10:10:47.324Z =320,984s (5phút21giây), gồm UI vàkiểm dữliệu/
roundtrip côngcụ; chưa có nói thànhtiếng. Colorr1→rawCanny/closing/descriptors→bóngBWMedian3/Otsur2
→Adaptiver3→khôngbiên dùngtoànảnh/dịchgócphím/Grayr1→PDF3trang→reload/debug/giới hạn.
PDFready229,785s; console0warning/error. Bảngmốc dựkiến6phút và34câuQ&A/điểmchưađo đãghi.

HaiBW chỉkhác threshold.method, cùngwarp/preparedgraySHA204d08fa…/histcounts sum555901,
Otsut156/Adaptiveglobalnull. Ba fullPNGUI bằngbytecore; rawCanny cùngtrial bằngpixelreplay.
Otsublack49,6714%/Adaptive7,0306% chỉmô tảmẫu, khôngqualitymetric. MẫuAdaptive vẫn cóít
đốm/mép; giữcađenbóngOtsu côngkhai.3PNG docs/images/demo làUIclosing, comparisonactualfull,
UIexport3pages; đãxem nhãn/context/cả5mẫu, không chứa bodytrangriêng.

PDFtải quaartifactAPI: pypdf kiểm3ảnhnhúng bằngpixel3full tươngứng, A4portrait/containkhôngméo/
lề5mm; Poppler render/xemcả3trang Color01/BW02/Gray03. Trang03đồng nhất cốý, khôngmất trang.
65artifactGET đềuđúngDBSHA; FKcheckrỗng. Ctrl+C298300 logshutdowncomplete; CLIrestart296284
cùngDB: detail/config/revision/artifact/PDF/SQLdump trước-sau bằngnhau. Browserreloadafterrestart
mởBW r3/histSHA/100%full/console0. Server8002đãdừng,8000/5173usergiữchạy.

Scriptpackage_submission dùngZipFile x/allowlist, rootguard/khôngsymlinkfile, cómanifest từngtệp;
khôngcopydata/privatephotos/DB/log/deps/dist/giáotrìnhPDF. Source/test/lock/docs/fixtures tổnghợp/
4figure report/3figure demo/5CSV-summary cầnđốichiếu đi kèm. Liênkếtảnhriêng/evidence cũ/PDFmôn học
đượcghi local-only ởSUBMISSION/report/checklist; khônggiảbenchmarkheldout táilập được khi thiếuảnh.
ZIPcuối/checksum ởoutput/submission ignored, source vàinputs trùngbyte bảncleanđãtest, tài liệu
cậpnhật cuối vàmanifestkiểm lại riêng. Gói làsource, cầnPython/Node/mạngkhi cài, khôngofflineinstaller.

Audit14 cóma trận8task, reviewtínhđúng/độrõ/kiếntrúc/riêngtư/phạmviđo, lỗiđãsửa vàgiớihạn:
1doc/split/GTmộtngười/testđãthấy/img004ănbàn/nợepsilon-fitdistance-minedge/noOCR/nodewarp/
singleprocess/crashorphan/noGCmigration. Khôngtune thựcnghiệm13. Bằngchứng kỹthuậtpublic ở
docs/submission-verification.json (khôngpixelriêng), log/runtime/hash/PDF/PNG ignored trong
experiments/results/mvp14-07-08-verified/. Đối chiếuđầu-cuốilượt hiện tại SQLroot và197tệpdata
giữhash; khôngsuyngược DBbấtbiến quacácphiêntrước. Cácbằngchứng01–06giữ nguyênlịch sử.

## 26/10/2026 — MVP14.05–06: báo cáo thuật toán và thực nghiệm

Hoàn thành14.05/06 sau yêu cầu tiếp của user; cùng14.03/04 đã chốt trong phiên này.
100main+12AUX/110ID;14.04a/b không cộng parent. Checkpoint14-C1/C2 đạt, next14.07;
14.08/M4 và toàn bộstage12 vẫn chưa được tự nghiệm thu.

docs/report.md mục1–7: bài toán/giả thiết, nguồn3PDF, pipeline/hệ tọa độ, Canny/closing/
contour-DouglasPeucker/representation-description/score/NMS/status, homography và enhancement/
histogram/Otsu/Adaptive. Có công thức/đơn vị/tham số đúngcode, bảng thư viện-vs-tựviết và ca sai.
Đã đọc lại cachetext cóSHA khớp3PDF, đối chiếu gradient slide5tr21, MPP/chiađoạn slide6tr17–19,
chiếu sángtr35, giáo trình65–72/87–118/155–180; render/xem2slide21/19 mới ởevidence.
KhônggọiDP làMPP/findContours làMoore tựviết/CHAIN_APPROX_SIMPLE làmãFreeman; khôngépquad90°.
Nguồn bổ sung chính thứcOpenCV đãmở Canny/contour/morphology/homography/CLAHE/threshold vàAPI
tileGridSize=sốtile. Website4.x trả4.13, ghi rõapp4.14khôngđổi dependency.

Mục8–14:dataset13ảnh/2doc/10GT/3unlabelable, split theotàiliệu, metrics/mẫusố,
4profiledevelopment/so threshold/test/benchmark/casai/mụctiêuchưađạt vàhướnggiảiquyếtnợ05.
Đã tính lại từCSV:24dòngdetector/9enhancement/7test/168samples, trongđó140measured/28warmup.
4bảng vàhashledger sinh trực tiếp từdữliệu đãkiểm, khôngchép số thủcông. DevelopmentmeanIoU
scoring.952870719/largest.951531555/noGaussian.901161692/noClosing.951531555;đạt2/3.
TestmeanIoU.995347032/error2.30312966px/7mẫu7/7IoU≥.9 chỉ1doc, khôngaccuracy100% tổngquát.
35measured/operation:np.quantilelinear p50/p95 vàmaxRSS tínhlại khớpsummaryfinal13.
Giữphạm vi core/HTTP khác nhau,OS cache/warmup,PIDactual/PSAPI vàlượtRAMlauncherinvalid.
Không tune hoặcchạy lạipixelstest/benchmark; snapshot13SHAce89a90… nguyên.

Thêm4PNG trongdocs/images/report:vectorcontour/GT/Q thật3development;
histogramimg003/CLAHEminhhọa;IoUtheosplit;latency/RAM. Khôngchứapixelnộidungtranguser.
Hìnhhọc lấy từmetadata vàmappingW−1/H−1;img004vẫnlấnnền,IoU.872497.
Đếmraw50/150img0039644/closed12287;preparedgray899×1290/sum1159710/tOtsu147.
Tái tínhOtsu/Adaptive31C10 từpreparedgray khớpPNG đãlưu;minhhọaCLAHEclip2grid8×8 thêmtrên
developmentở14.05đượcghi riêng,khôngđổipreset hoặccoilàđối chứngmớitrêntest.
Linkảnhthậtdevelopment đãcó ởignoredresults đểtựmởCanny/closing/overlay/warp/Color/Gray/BW;
khôngcopytranginriêng/tệpảnhuser vàoGit. Demo04quad khácGT13 đượcghi rõngữcảnh.

Matplotlibkhôngcótrongbundledruntime; dùngvenvsoạnthảoriêng.tmp/report-tools-venv/
matplotlib3.11.2, khôngcàivàoprojectvenv hoặcđổilock. Pillow13 ởtoolenvkhôngthayPillow12.3
củaapp. Lưu authoring-requirements.txt trongevidence; fontcachetrong.tmp/report-mpl,
4PNGgiữbyte/hash quahai lượt vẽ sau sửađườngdẫnfontcache. Đãxemcả4hình/nhãn/đơnvị,
khôngbiếnbiểuđồthànhsốđoaccuracyOCR. Khôngthêmsource/test/dependency/algorithm.

Ràcode-review/docs: reportnêu80%IoU≥.9 làmụctiêuthamchiếu,development2/3chưađạt;
thời gian quan sát dưới2s/3stheo phạmviđo nhưngkhôngSLAcảứngdụng;quymô20/5chưađạt
vàuserđãchốt13/2;thiếunhàumạnh/lóa/highlightthật/nhãnchữ.Nợepsilon/fitdistance/min-edge
chỉlàhướngthử,trườnghợpframe/bànvẫncầnphânbiệtvùng/ngữcảnhvàthêmdocdevelopment.
docs/results nối report, README/checklist/plan/contracts/projectmap/phạmvi/AGENTS cậpnhật.
Chỉtài liệu vàảnhminhhọathayđổi: full1279/103tests ở14.01–02giữhiệulực;17focused4.51s ở14.03
vàscriptassertCSV/hash/figures/Markdownlinks/nguyênsource/data làkiểm chứngmới.
Evidenceignoredmvp14-05-06-verified/:report-data/generated-tables/figure-manifest/verification,
authoringrequirements/theoryscreens;helperscục bộ.tmp/collect14_report.py/plot14_report.py/fill14_report.py.
Khôngagents/commit/push/deploy,gói nộp hoặcbiếnsnapshotcũthànhbảnđónggói.

Rà cuối14.03–06:321 liên kết Markdown có đích,4bảng kết quả/hashledger khớp dữ liệu,
10PNG hợp lệ/hash đúng,code/pin/frozen giữ nguyên; verification.json đã ghi ở cả hai thư mục evidence.
87tệp data có trong tham chiếu14.01–02 vẫn giữ hash. Metadata DB đang phục vụ8000 khác tham chiếu
phiên trước (chưa xác định nguồn thay đổi), nên không khẳng định SQL giữ nguyên giữa hai phiên.
Walkthrough của tác vụ này chỉ ghi vào DB riêng8002; không hoàn tác/xóa dữ liệu đang dùng.

## 26/10/2026 — MVP14.03–04: README và hướng dẫn có ảnh

Đã hoàn thành14.03/04 và checkpoint14-C1;98main+12AUX/110ID,14.04a/b là task con,
không cộng parent. User yêu cầu tiếp14.05/06 khi đang chốt walkthrough; tiếp tục phần báo cáo.

README viết lại thành hướng dẫn root/versions/venv/npmci/build/CLI1worker/health/Ctrl+C/reopen,
data/backup/quota/lỗi/localhost/dev/tests và tham chiếu tài liệu lõi. Bỏ các mô tả lịch sử đã sai
như chưa phục vụbuild, mở lại cần tựrender, API9paths hoặc chưa có histogramUI.
Bản README trước lưu ignored trong evidence để đối chiếu; không sửa source/lock/preset.

Tự theo README từsourcecopy sạch `.tmp/mvp14-guide-clean/project`, Python3.12.10/nosystempackages,
Node24.15.0/npm11.12.1;pipinstall30pin/pipcheck/imports/npmci24package/build41modules đạt.
Log`.tmp/phase14-readme-install.log`;wrapperđọclog dùng saiCWD sauSetLocation đã đọc lại đúngroot,
không phải lỗi cài/build. Ba distfiles bằngbyte bản phục vụ8000.
CLI thật `python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8002 --workers 1`
từrootcopy; healthInvoke-RestMethod trảok.17static/APItests từvenv/sourcecopy đạt4.51s-Werror,
log`.tmp/phase14-readme-static.log`. Full1279/103frontend ở14.01–02 còn hợp lệ vì không đổi code.

Tài liệu mới Hướng dẫn quét tài liệu tại8002/DBcopy: nhập2samplePNG→auto detect cả2→dịchgóc0
bằngkeyboard→Lưu nháp(r1/chưaconfirmed)→confirm(r2)→BWMedian3/Otsu→render(r3/590×790).
Trang2Color chỉconfirmr1; khiPDF2trang, app tựrendertrang2 còn thiếu rồi xuất thành công.
ĐãbấmTảiPDF thật vàoDownloads; bytes bằngartifactGET,2Pageobjects,Poppler render cả2trang
và đãxem đúngQAPAGE1/2/khôngmấtchữ. PNGđơn BWbằngbyte fullPNG,590×790/modeL.
Reload rồiCtrl+C (đãthấyApplication shutdown complete ởPID276656)→CLI mớiPID277100/cùngDB:
detail/SQLdump/39artifactSHA/PDF/PNG giữ nguyên;browserđọc lại confirmed/config/latestfull.
Consolewarn/error rỗng. Serverkiểm chứng8002 được dừng sau walkthrough;app8000 không thay đổi.

docs/user-guide.md có4ảnhUIthật+2samplePNG tổng hợp đi kèm, mainflow và dirty/confirmed/busy/
stale/needsReload, không đồng nhấtLưu nháp vớiXác nhận. Ảnh phụ/busyDOM/downloads/CLIlog/
runtimebefore-after ởignored `experiments/results/mvp14-03-04-verified/`. Busy là trạng thái
giải thích từstate machine; lượt render nhỏ kết thúc trước snapshot, không dựng ảnh busy giả.
HaiUIfilechooser/downloadcalls có độtrễ host vài phút; không dùng thời gian chờ đó làm latency thuật toán.

Chỉdocs/ảnhsynthetic thay đổi, khôngpackage/code/algorithm/schema/data thật. Quy tắcảnh cá nhân/
snapshot13 và giới hạnWindows/MVP giữ;giaiđoạn12/M4 không tựnghiệmthu. Checkpoint14-C2 chờ14.05–06.

## 26/10/2026 — MVP14.01–MVP14.02: bản build cùng origin và dependency

Hoàn thành hai task được yêu cầu; **96 task chính +12AUX/110ID gốc**, next MVP14.03.
Checkpoint14-C1 chờ14.03, M4/chốt gói nộp chưa đạt. Stage12 giữ nguyên chưa nghiệm thu toàn bộ;
phụ thuộc hồi quy12.07 dùng cổng đã được user chấp nhận ở13.06 và hồi quy mới dưới đây.

`main.create_app` nhận keyword `frontend_dir` (default `frontend/dist`, None cho API riêng),
`web.install_frontend` dùng Starlette StaticFiles và chỉ xử lý routing HTTP404 để phục vụ
index/assets/HTML fallback. Không thêm catch-all route che API405/Allow hoặc đổi OpenAPI12paths.
Root/index khôngcache dài; nosniff; realpath không thoát dist. API/data/source/dotpath/asset thiếu
trả lỗi JSON, không public runtime/data. Missing build giữ backendhealth/UI404, phải build để xem UI.
Không sửa React/Vite/API schema3/thuật toán/preset hoặc dependency.

TDD:17tests mới RED vì thiếu frontend_dir → GREEN4.15s, gồm root/query/deepreload/asset,
APIhealth/405, import thật/artifact/reload và14ca private/missing/traversal; không hạ gate.
Lượt TestClient trong sandbox bị treo đã dừng, chạy lại với quyền IPC/temporary cần thiết đạt.
Full đầu1.278tests-Werror180.76s; thêm1test chứng minh snapshot tổng hợp vẫn từ chối drift.
**Full cuối1.279tests đạt233.16s từ venv mới**, khôngskip:1.236backend +43experiments.
Lệnh: `.tmp/mvp14-clean/backend-venv/Scripts/python.exe -m pytest -c backend/pyproject.toml backend/tests experiments/tests -q --tb=short -W error --basetemp=.tmp/pytest14-clean-final`.
Log `.tmp/pytest14-clean-final.log`.

Task14.02 giữ nguyên requirements30pin và npm lockfile. Tạo venv mới với Python3.12.10,
`include-system-site-packages=false`; pipinstall-r/pipcheck/imports đạt. Tạo frontend riêng,
copy source/config/lock, `npm ci` cài24package, Node24.15.0/npm11.12.1;
103tests khôngskip/typecheck/productionbuild41modules đạt. Ba tệp dist bằngbyte bản phục vụ:
index8202b1bf…, JS c2804dbb…, CSS407d7e1d…; không dựa package Python/TS/Vite toàn máy.
Cài venv lần đầu lỗi ensurepip do sandboxTemp; dùng Temp trongworkspace và quyền cài đặt phù hợp,
không bật system-site-packages hoặc thay phiên bản.

Chạy app thật từ venv sạch tại127.0.0.1:8001 với SQLite riêng/1Uvicornprocess:
browsercreate→nhập2PNG tổng hợp→detect cả2→confirm→Color/BWOtsu render590×790→PDF2trang.
Không nhập testphoto hoặc đụng tài liệu user trong luồng QA. DOM ghi JS/CSS và5ảnh cùng8001,
tất cả natural dimensions>0/complete; consolewarn/error rỗng. Root reload và
`/document/qa?session=…&page=…` fallback/reload giữ latest render/confirmed/revision1.
HTTP thiếu API/asset/data/traversal trả404JSON; full PNG2trang bằngbyte core render từ cùngsource/config.
38artifact tải qua API đều đúngSHA; PDFheader/MIME và2Pageobjects đạt.

Shutdowngraceful rồi startprocessmới cùngDB: actualPID293352→293492 (xem server-process.json/log);
runtime-before/after giữ nguyên toàn bộ session detail/38hash/parity/PDF; browser mở lại đúng bản quét.
Backend app thật8000 cũng restartgraceful, actualPID269772; UIbuild/API cùng chạy.
Toàn bộ SQLrows/dumpSHA và87tệp dưới data giữ nguyên trước/sau; không có mutation userdata.
Browser mở lại tài liệu QA13 cũ, fullPNG hiển thị100%, console rỗng.
Server8001 kiểm chứng dừng sau nghiệm thu;8000 và Vite5173 trước đó giữ chạy.
Helperstop8000 hiện là `.tmp/phase14-local.stop`, logs `.tmp/phase14-local.*.log`.

Giữ frozenJSON SHAce89a90… nguyên. Trong91source ban đầu chỉmain/settings đổi, thêmweb;
toàn bộprocessing/preset/algorithms và10inputhash (gồm lock/manifest/annotations) giữ.
Cổng snapshot13 hiện phải báo drift với bản đóng gói, không làm giả đã đo cùng bản.
Lưu riêng `mvp14-local-v1`/packaging-manifest.json và91source/10input/runner13 cũ,
phục hồi đúng từng byte kiểm bằnghash snapshot/runnerb8816796…; không retune/retest tập đã thấy.
Runner helper hỗ trợ snapshotpath tường minh cho2HTTPtests tổng hợp; default CLI vẫn gate snapshot13.
Test drift mới không cho snapshot tạm vượt kiểm chứng. Historical metrics/runnerhash13 không sửa.

Đã tự review correctness/readability/architecture/security/performance: không phát hiện blocker;
fallback không shadow route hoặc mount data, static I/O qua Starlette thread helper,
logic ởwebmodule, không thêm dependency/worker/cache kết quả. Khôngagents/commit/push/deploy.
Docs/checklist/currentstatus cập nhật, hướng dẫn README đầy đủ thuộc14.03.
[Cấu hình và lệnh](local-runtime.md). Evidence ignored `experiments/results/mvp14-01-02-verified/`
gồm manifest/runtime/verification/browser/PDF/frozen-source; log cài/build ở`.tmp/mvp14-clean/`.

Giới hạn: mới kiểm chứng Windowsx64/Python3.12.10/Node24.15.0, chưa M4/gói nộp hoặc chứng nhận hệ khác.
Nợ detectorimg004/006 ăn bàn/nhàu mạnh/lóa không thay đổi;7ảnh test cùng1doc khôngaccuracy tổng quát.

## 14/10/2026 — MVP01.01, MVP01.02, MVP01.03

**Phạm vi được yêu cầu:** thực hiện task 1, 2, 3 của giai đoạn 01; chưa triển khai health, frontend hay pipeline.

**Hoàn thành:**

- MVP01.01: tạo backend/frontend/experiments/fixtures, giữ docs có sẵn; README liên kết phạm vi, kế hoạch và hai tài liệu nền; project-map ghi vai trò các vùng. `.gitkeep` giữ ba thư mục chưa có nội dung ứng dụng trong Git.
- MVP01.02: khởi tạo Git trên nhánh main; .gitignore loại venv/cache/node_modules/build/DB/ảnh runtime/dataset/tệp tạm/bí mật.
- MVP01.03: dùng Python 3.12.10 64-bit có sẵn, tạo backend/.venv riêng; cài 9 dependency trực tiếp; khóa 27 package vào backend/requirements.txt.

**Bằng chứng:**

| Kiểm chứng đã chạy | Kết quả |
|---|---|
| Cây thư mục và link Markdown trong README/project-map | Đủ thư mục; không có link nội bộ hỏng |
| `git init --initial-branch=main` | Repository khởi tạo ở đúng workspace |
| `git status --short --branch` | Nhánh main, chưa có commit; các tệp nguồn/tài liệu hiện là untracked |
| `git check-ignore -v --no-index` với mẫu venv, node_modules, dist, data, datasets, experiments/data, experiments/results, .tmp, .env | Đều được ignore đúng |
| `git check-ignore --quiet --no-index` với README, requirements, fixture tổng hợp, dataset_manifest.csv, .gitkeep và .env.example | Không bị ignore nhầm |
| `python --version` | Python 3.12.10 |
| Python venv: `sys.prefix != sys.base_prefix`, kiến trúc pointer | True; 64-bit; include-system-site-packages=false |
| Import fastapi/uvicorn/python_multipart/cv2/numpy/PIL/sqlalchemy/reportlab/pytest trong venv | Cả 9 thành công |
| Kiểm tra metadata các distribution cung cấp cv2 | Chỉ opencv-python-headless |
| `pip freeze` từ Python venv | 27 package, ghi chính xác vào requirements.txt |
| `backend/.venv/Scripts/python.exe -m pip check` | No broken requirements found |

**Phiên bản trực tiếp:** FastAPI 0.143.0; Uvicorn 0.54.0; python-multipart 0.0.32; opencv-python-headless 4.14.0.94; NumPy 2.5.4; Pillow 12.3.0; SQLAlchemy 2.1.4; ReportLab 5.0.1; pytest 9.1.1. Phiên bản gián tiếp nằm trong requirements.txt.

**Lệnh dựng môi trường đã dùng:**

```powershell
# Trong phiên sandbox, chuyển Temp vào workspace trước khi tạo venv.
$scannerTempDirectory = Join-Path (Get-Location).Path '.tmp'
New-Item -ItemType Directory -Path $scannerTempDirectory -Force | Out-Null
$env:TEMP = $scannerTempDirectory
$env:TMP = $scannerTempDirectory
python -m venv backend/.venv
& .\backend\.venv\Scripts\python.exe -m pip install --index-url https://pypi.org/simple --only-binary=:all: --no-cache-dir --disable-pip-version-check --no-input --timeout 20 --retries 1 fastapi uvicorn python-multipart 'opencv-python-headless>=4,<5' numpy Pillow SQLAlchemy reportlab pytest
& .\backend\.venv\Scripts\python.exe -m pip check
```

Thực tế lệnh tạo venv gọi đường dẫn tuyệt đối Python312 trên máy; `python --version` cũng đã xác nhận cùng bản 3.12.10. Ghi requirements bằng pip freeze sau khi import thành công, không chọn số phiên bản từ ví dụ trong đặc tả.

**Lỗi môi trường và cách xử lý:**

1. Python Launcher (`py -0p`) báo không có Python đã đăng ký, nhưng python.exe tại Python312 chạy được; dùng executable này, không cài thêm Python toàn máy.
2. ensurepip lỗi PermissionError khi ghi thư mục Temp sandbox; đặt TEMP/TMP cục bộ trong phiên shell về workspace/.tmp rồi tạo lại venv thành công. Không đổi execution policy hay biến môi trường toàn máy.
3. Pip trong sandbox lỗi DNS với PyPI; gọi cài đặt bằng quyền truy cập mạng đã được auto-review cho phép. Chỉ cài vào backend/.venv, không gửi ảnh hay dữ liệu dự án ra ngoài.
4. Khởi tạo .git cần quyền ghi metadata ngoài sandbox; auto-review đã cho phép thao tác Git init cục bộ.

**Tệp và trạng thái bàn giao:** README.md, docs/project-map.md, .gitignore, ba .gitkeep, backend/requirements.txt, docs/progress.md; cập nhật trạng thái trong tasks/todo.md, tasks/plan.md, tài liệu MVP và AGENTS.md. backend/.venv và .tmp là dữ liệu cục bộ được ignore. Không tạo commit, remote, push hoặc publish.

**Checkpoint 01-C1:** đạt trong phạm vi cấu trúc/Git/môi trường Python. Chưa có app/test nghiệp vụ để chạy; không tuyên bố frontend build hoặc API health đã pass.

**Task tiếp theo:** MVP01.04 — FastAPI app/settings và GET /api/v1/health. MVP01.05–01.08 còn chưa hoàn thành. progress.md được tạo để lưu bằng chứng ba task này, không đồng nghĩa task mẫu nhật ký MVP01.08 đã hoàn thành; changes.md chưa được tạo.

## 14/10/2026 — Nghiên cứu thuật toán theo tài liệu môn học

Người dùng yêu cầu chậm lại, đọc giáo trình và hai slide PDF trong docs để thống nhất bài toán biên và hướng xử lý trước khi tiếp tục triển khai.

- Đã đọc toàn bộ slide chương 5 (60 trang) và chương 6 (63 trang); đối chiếu các phần trực tiếp liên quan trong giáo trình 308 trang về gradient, morphology, segmentation, threshold, contour/biểu diễn và bộ mô tả. Không tuyên bố đã đọc kỹ mọi trang của giáo trình.
- Đã render và xem các hình biên/đặc trưng ở 10 trang chọn từ cả ba PDF; nguồn vẫn giữ nguyên.
- Ghi phân tích ở [Phan_Tich_Huong_Thuat_Toan_Tu_Tai_Lieu.md](Phan_Tich_Huong_Thuat_Toan_Tu_Tai_Lieu.md): mục tiêu là định vị toàn trang, biểu diễn contour/đa giác, xếp hạng dựa trên đặc trưng, xác nhận/warp, sau đó cải thiện độ đọc. Biên chữ/gấp/bóng là cấu trúc khác đường bao trang; homography không làm phẳng nhàu nặng.
- Scoring/ngưỡng/nhánh dự phòng theo vùng là giả thuyết cần kiểm chứng trên development, chưa phải kết quả. Phân biệt MPP trong giáo trình với Douglas–Peucker trong OpenCV; chú ý quy ước trục và compactness.
- Chưa viết thêm code ứng dụng, chưa đổi checklist/pipeline đã duyệt, chưa tích thêm task. Tiến độ code vẫn MVP01.01–MVP01.03; ưu tiên hiện tại là trao đổi/thử nghiệm thuật toán theo yêu cầu mới.

### Bổ sung hướng dẫn mô tả biên sau trao đổi

Người dùng hỏi phần mô tả biên đã được cập nhật để dùng khi thực hiện chưa. Đã cụ thể hóa mục 5.5.1–5.5.3 của tài liệu phân tích: các trường/đơn vị, cách tính hỗ trợ từng cạnh và tổng e, phân biệt diện tích vùng, kiểm chứng và liên kết task.

- Làm rõ nghiệm thu MVP05.03/05.04/05.07, MVP09.07/09.08 và MVP13.04 trong todo.md; không tạo thêm task hoặc tích task code.
- Thêm mô tả biên vào nội dung học thuật của phạm vi MVP; AGENTS.md trỏ hướng dẫn để phiên triển khai sau đọc đúng ngữ cảnh.
- Giữ công thức scoring và ngưỡng baseline đã chốt. Chu vi/cạnh/góc/tính lồi là thuộc tính lọc/giải thích; sai số fit theo khoảng cách và descriptor nâng cao chưa bắt buộc đưa vào score.
- Đây là cập nhật tài liệu, không phải implementation; tổng vẫn 110 task chính, 5 tùy chọn, chỉ MVP01.01–MVP01.03 hoàn thành.

## 14/10/2026 — Rà lại MVP01.01–MVP01.03 sau khi làm rõ thuật toán

**Kết luận:** Ba task thiết lập vẫn đạt tiêu chí. Hướng xử lý contour/đa giác, mô tả biên và homography dùng cấu trúc và OpenCV/NumPy đã có; không cần dựng lại môi trường hoặc thêm dependency. Bổ sung liên kết hướng dẫn thuật toán trong README/project-map để lúc triển khai tìm đúng tài liệu.

| Kiểm chứng chạy lại | Kết quả |
|---|---|
| Cấu trúc workspace và tệp giữ thư mục | Đủ 5 vùng backend/frontend/experiments/fixtures/docs và 3 `.gitkeep` |
| Git branch và check-ignore trên đường dẫn mẫu | Nhánh main; 12 mẫu dữ liệu/môi trường bị ignore, 9 mẫu nguồn/fixture/manifest không bị ignore nhầm |
| Import và metadata trong Python venv | 9 import thành công; 27 pin khớp requirements; Python 3.12.10 64-bit, venv riêng; chỉ một distribution opencv-python-headless |
| `backend/.venv/Scripts/python.exe -m pip check` | No broken requirements found |
| Phép thử tổng hợp trực tiếp trong venv, không lưu ảnh | Canny/findContours chạy được; arcLength/contourArea/approxPolyDP/isContourConvex và độ dài cạnh trả kết quả hợp lệ; getPerspectiveTransform/perspectiveTransform ánh xạ 4 góc đúng trong sai số 1e-4; warpPerspective tạo ảnh uint8 kích thước 80×120×3 |

Phép thử trên kiểm tra khả năng của môi trường, chưa chứng minh detector/scoring/homography ứng dụng đã được triển khai hoặc nghiệm thu. Giữ trạng thái hoàn thành MVP01.01–MVP01.03; MVP01.04 trở đi còn chưa hoàn thành, chưa đạt M0.

## 14/10/2026 — MVP01.04, MVP01.05: health và frontend qua proxy

**Phạm vi được yêu cầu:** thực hiện task 4 và 5. Đã tạo FastAPI health, settings đường dẫn/quota và trang React/TypeScript/Vite kiểm tra kết nối. Phần xử lý ảnh chưa được triển khai; không tích MVP01.06–MVP01.08.

**Tệp triển khai:** `backend/app/main.py`, `backend/app/settings.py`; 8 tệp frontend ở checklist. MVP01.05 được chia thành 2 task con a/b vì scaffold cần hơn 5 tệp. Tổng vẫn 110 task chính, 5 tùy chọn; 2 task con nằm trong task cha, không cộng trùng.

**Hành vi đã có:**

- GET `/api/v1/health` trả `{"status":"ok"}`, có schema HealthResponse trong OpenAPI. Endpoint chỉ kiểm tra API phản hồi.
- Settings tập trung PROJECT_ROOT/DATA_DIR/DATABASE_PATH/TEMP_DIR và quota 15 MiB/16 triệu pixel/20 trang. Chưa tạo DB/runtime và chưa thực thi quota upload vì endpoint upload chưa có.
- Vite bind `127.0.0.1:5173`, strictPort, proxy `/api` tới `127.0.0.1:8000`; không cần mở CORS hoặc LAN.
- Trang health gọi cùng origin, kiểm tra HTTP/JSON, giới hạn chờ 5 giây, cleanup request khi effect cũ kết thúc; có trạng thái chờ/thành công/lỗi và thử lại. Không dựng số liệu hay chức năng quét giả.

| Kiểm chứng đã chạy | Kết quả |
|---|---|
| `node --version`, `npm.cmd --version` | Node 24.15.0, npm 11.12.1 |
| npm view tại registry.npmjs.org; npm install | Cài thành công 24 package, audit tại thời điểm cài báo 0 vulnerabilities; package-lock phiên bản 3 |
| `npm.cmd ls --depth=0` từ frontend | Đủ 7 dependency trực tiếp, không báo missing/invalid |
| Uvicorn + HTTP trực tiếp bằng urllib | Health 200, application/json, đúng body; OpenAPI khai báo status const=ok |
| Đối chiếu settings trên môi trường thật | Gốc workspace/quota đúng; chạy từ frontend vẫn giữ cùng PROJECT_ROOT/DATA_DIR |
| HTTP tới `127.0.0.1:5173/api/v1/health` | 200 application/json; proxy trả cùng body của backend |
| `npm.cmd run build` từ frontend | TypeScript và Vite thành công; dist có HTML/CSS/JS |
| Browser cục bộ: trạng thái và console | Hiện “Đã kết nối máy xử lý”; không có console warning/error được ghi nhận |
| Tắt backend → bấm Kiểm tra lại → khởi động backend → bấm lại | Hiện lỗi kết nối rồi phục hồi trạng thái thành công, không trắng trang |
| Keyboard/AX/DOM | Tab tới nút Kiểm tra lại; h1/h2 và nút có tên; status có aria-live=polite |
| Responsive 320/768/1024/1440 px | Không tràn ngang; có một h1; nút hiện đầy đủ; đã reset viewport sau kiểm tra |

**Phiên bản frontend:** React/React DOM 19.3.0; @types/react/@types/react-dom 19.3.0; @vitejs/plugin-react 6.1.2; TypeScript 7.0.2; Vite 8.3.4. Node hiện tại đáp ứng engines của Vite. Không nâng/cài package toàn máy.

**Lệnh chạy đã kiểm chứng:**

```powershell
# Từ gốc dự án, cửa sổ backend:
& .\backend\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000

# Trong cửa sổ frontend, từ frontend/:
npm.cmd install --registry=https://registry.npmjs.org --no-fund --fetch-retries=1 --fetch-timeout=20000
npm.cmd run build
npm.cmd run dev
```

**Giới hạn môi trường và xử lý:** npm trong sandbox báo ENOTFOUND; HTTP localhost báo WinError 10013 và server sandbox không bind được. Đã dừng tiến trình thử trong sandbox, dùng quyền được auto-review cho phép cho registry và hai server chỉ bind loopback. npm cache của phiên cài đặt ở `.tmp/npm-cache`. Không thay execution policy hoặc mở firewall. Một lệnh npm ls ban đầu chạy nhầm ở root trả cây rỗng; đã kiểm tra lại đúng frontend như bảng trên.

Ảnh giao diện sau phục hồi ở `.tmp/verification/mvp01-05-ready.jpg` (tệp kiểm chứng cục bộ được ignore). README có lệnh dev/build thực tế và liên kết tài liệu chính thức; task/config pytest chung vẫn thuộc MVP01.06.

Rà sau cập nhật: 7 dependency trực tiếp khớp package.json/package-lock và node_modules; 25 liên kết nội bộ hợp lệ; 5 mẫu build/cache bị ignore và 5 mẫu mã nguồn/lockfile không bị ignore nhầm. Checklist có đúng 110 task chính + 5 tùy chọn, 2 task con MVP01.05a/b; chỉ 5 task chính đầu tiên được tích.

**Bàn giao:** MVP01.01–MVP01.05 đã hoàn thành, chưa đạt M0; tiếp theo là MVP01.06. Hai server dev giữ chạy trên localhost để xem bản khởi tạo. Không commit/push/deploy; node_modules/dist/cache vẫn được ignore.

## 14/10/2026 — MVP01.06, MVP01.07: lệnh kiểm chứng và hợp đồng ảnh

**Phạm vi được yêu cầu:** task 6 và 7. Đã cấu hình pytest, typecheck/build và viết docs/image-contract.md. Không triển khai normalize/geometry/enhancement, không tích MVP01.08.

### MVP01.06 — Kiểm chứng môi trường

- Thêm backend/pyproject.toml: pytest thu tests/, pythonpath backend, strict config/markers.
- Thêm một test HTTP health bằng FastAPI TestClient thật trong tiến trình; kiểm tra route versioned, status, MIME và JSON mà frontend sử dụng. Không tạo test để kiểm tra thư mục hoặc import đơn thuần.
- Thêm script typecheck, build gọi typecheck rồi Vite. README có lệnh root/backend/frontend đã kiểm chứng.
- Khóa thêm httpx2 2.13.1, httpcore2 2.13.1, truststore 0.10.5; requirements sinh lại từ pip freeze thành 30 pin, giữ nguyên 27 dependency trước đó. httpx cũ và dependency chỉ phục vụ nó đã được gỡ.

| Kiểm chứng | Kết quả |
|---|---|
| Lần pytest trước cấu hình import | Lỗi collection: No module named app; xác nhận import path cần được thiết lập |
| `backend/.venv/Scripts/python.exe -m pytest -c backend/pyproject.toml backend/tests` sau sửa | 1 passed, không có warning; rootdir/configfile đúng backend/pyproject.toml |
| `npm.cmd run typecheck` từ frontend | TypeScript đạt |
| `npm.cmd run build` từ frontend | Typecheck và Vite build đạt; có dist HTML/CSS/JS |
| `pip check` sau hoàn tất dependency | No broken requirements found, không còn invalid distribution |
| Metadata requirements | 30 pin khớp venv; không còn httpx/httpcore/certifi cũ; httpx2 đúng 2.13.1 |
| HTTP health trực tiếp và qua Vite sau thay đổi | Cả 127.0.0.1:8000 và :5173 trả 200 với status=ok |

**Vấn đề đã xử lý:** tài liệu FastAPI nhắc httpx, nhưng mã Starlette 1.8.0 và tài liệu Starlette hiện hành ưu tiên httpx2; bản httpx cũ tạo deprecation warning. Đã dùng httpx2 và chạy test thực tế. Pip uninstall lần đầu bị Temp sandbox chặn sau khi tạm đổi tên thư mục package; đã kiểm tra các đường dẫn nằm trong venv workspace, khôi phục đúng hai thư mục tạm, đặt TEMP/TMP của phiên vào .tmp/pip-temp rồi gỡ thành công. Không xóa hoặc sửa package toàn máy.

Pytest/TestClient treo trong sandbox ở test; đã dừng tiến trình thử và dùng quyền được auto-review cho phép. Cùng test chạy ngoài sandbox đạt dưới một giây, không gọi dịch vụ ngoài hay gửi ảnh. Một lượt chẩn đoán dùng faulthandler_timeout, sau đó lệnh pytest chuẩn trong README cũng đã chạy đạt. Không tắt cảnh báo để lấy pass.

### MVP01.07 — Hợp đồng cho các task xử lý ảnh

docs/image-contract.md đối chiếu mục 5–10 đặc tả gốc và phạm vi MVP, gồm:

- Nguồn giữ nguyên, EXIF một lần, alpha trắng, BGR/RGB, dtype/channels và polarity; full BW khác preview/JPG đã nội suy/nén.
- Kích thước source/analysis/full render/preview, làm tròn và ánh xạ normalized W−1/H−1 từ dimensions thực.
- Chu kỳ góc clockwise y-down, auto sắp quanh tâm/min(x+y), manual giữ handle ID; contain/letterbox/CSS/DPR.
- Homography từ source, estimated/2400 cố định, rotation clockwise sau lọc, không suy ra A4/DPI vật lý từ ảnh.
- Ba full preset color/gray/BW; miền và tham số inactive; ảnh quá nhỏ cho Adaptive báo lỗi; thiếu field lấy default theo mode, không merge config cũ.
- Revision=1 khi tạo trang, no-op không tăng; confirmed/draft; snapshot render, response cũ, export đúng revision/order và reopen.
- Baseline detector/mô tả biên và weighted edge support theo hướng đã ghi; không thêm descriptor nâng cao vào scoring hoặc gọi score là accuracy.

Đã parse ba JSON preset để kiểm tra cùng đủ field và giá trị cơ bản, kiểm tra ví dụ normalized; có bảng truy vết từng nhóm mục 5–10 và những điều chỉnh MVP. Tên DB ghi theo settings hiện có là data/scanner.sqlite3 thay tên minh họa trong đặc tả gốc. Làm rõ MVP04.03 trong checklist: CLAHE trên xám, không bắt buộc nhánh Lab cho màu theo phạm vi đã rút gọn.

Đây là hợp đồng triển khai, chưa có code cho các quy tắc ảnh/config/revision. Các quy ước nhỏ được ghi rõ để không đoán khi hiện thực: round-half-up, rotation clockwise, kernel render 3/5, revision ban đầu/no-op, lỗi Adaptive quá lớn và defaults theo mode. Chưa có thực nghiệm chứng minh preset tối ưu.

**Bàn giao:** MVP01.01–MVP01.07 hoàn thành; Checkpoint 01-C2 đạt. MVP01.08 còn chưa hoàn thành (changes.md chưa có), chưa đánh dấu M0. Cập nhật README/AGENTS/project-map/phạm vi/plan/todo; giữ 110 task chính + 5 tùy chọn và 2 task con của MVP01.05. Không commit/push/deploy; hai server dev localhost vẫn hoạt động.

Rà sau cập nhật: 30 liên kết nội bộ hợp lệ; checklist chỉ tích 7 task chính đầu tiên và 2 task con của MVP01.05; dependency frontend vẫn khớp lockfile. Pytest cache/tệp tạm/build được ignore, pyproject/test_health/requirements/image-contract không bị ignore nhầm.

### Rà sự phù hợp của task 7 với hướng thuật toán

Đã đối chiếu image-contract.md với Phan_Tich_Huong_Thuat_Toan_Tu_Tai_Lieu.md. Luồng chính, mô tả/scoring, nguồn warp, xác nhận và giới hạn homography phù hợp. Phần hợp đồng trước đó ghi ngắn về toàn trang/Douglas–Peucker và vai trò các hướng thí nghiệm; đã bổ sung rõ ở mục 9, thêm bảng truy vết ở mục 10.

Giữ bộ trường/đơn vị mô tả tại mục 5.5.1 của tài liệu phân tích làm tham chiếu chuẩn; giữ e trên Canny trước closing theo tổng số mẫu và công thức a/e/f/b. Sobel, nhánh vùng, Freeman/Fourier/Hu và fit khoảng cách giữ vai trò nghiên cứu/tùy chọn, không thành chức năng bắt buộc. Không thay preset/scoring, code hoặc trạng thái task; các quy ước kỹ thuật bổ sung của task 7 vẫn được phân biệt với kết luận thuật toán đã đo.

## 14/10/2026 — Bỏ MVP01.08 và chuẩn bị giai đoạn 02

Người dùng không cần task 8 giai đoạn 01, muốn chuyển sang giai đoạn 02 và yêu cầu phân tích mục đích/vai trò MVP02.01–MVP02.02. Đã ghi MVP01.08 là bỏ qua, không tích hoàn thành và không tạo changes.md/mẫu nhật ký. Giữ progress.md hiện có để truy vết quyết định.

Giai đoạn 01/M0 được đóng theo phạm vi điều chỉnh: health frontend qua proxy, môi trường, lệnh dev/pytest/typecheck/build và hợp đồng ảnh đã có bằng chứng ở các mục trước. MVP02.01 phụ thuộc MVP01.06/MVP01.07, cả hai đã xong; MVP02.02 phụ thuộc fixtures của MVP02.01, không phụ thuộc task nhật ký đã bỏ qua.

Tổng hiện hành 109 task chính cần thực hiện + 1 bỏ qua + 5 tùy chọn; giữ 110 ID chính gốc và 2 task con của MVP01.05. Giai đoạn 01 có 7 task cần làm; tuần 1 còn 44 task trong kế hoạch thay 45. Cập nhật checklist/plan/README/phạm vi/AGENTS, không đổi mã.

Phân tích hai task: MVP02.01 tạo fixtures tổng hợp có kết quả mong đợi và manifest cho JPEG/PNG, góc màu/EXIF/alpha, tệp giả/hỏng và header vượt quota; dùng lại cho các bước nhập/chuẩn hóa. MVP02.02 viết kiểm tra byte/format/frame/dimensions/pixel count trước xử lý ảnh lớn, trả lỗi rõ và kiểm chứng bằng fixtures. EXIF transpose/alpha/BGR thuộc MVP02.03, không coi task 2 là đã chuẩn hóa ảnh hoặc phát hiện trang. Chưa tạo fixtures hoặc normalize.py trong lượt trao đổi này, không đánh dấu task giai đoạn 02 đã xong.

## 14/10/2026 — Hoàn thành MVP02.01 và MVP02.02

**Yêu cầu:** triển khai hai task đầu giai đoạn 02. Đọc lại using-agent-skills, task/phụ thuộc và hợp đồng ảnh; áp dụng triển khai từng phần, TDD, thiết kế giao diện mô-đun, đối chiếu nguồn Pillow, kiểm tra đầu vào và rà soát code. Không thêm endpoint hoặc thuật toán phát hiện trang.

### MVP02.01 — Fixtures định dạng

`experiments/create_fixtures.py` sinh 22 tệp tổng hợp, tổng **80.909 byte**, cùng `fixtures/manifest.json` ghi hash/dung lượng/nguồn gốc/kết quả mong đợi. Không dùng ảnh cá nhân hoặc dịch vụ ngoài. Hai tệp nguồn/cấu hình là script và manifest; 22 assets là dữ liệu sinh tự động, không phải 22 phần triển khai độc lập.

Các ca gồm góc màu RGB JPEG/PNG; EXIF 6 (xoay) và 2 (phản chiếu); RGBA bán trong suốt/palette transparency/grayscale; kích thước tối thiểu 2×2 và chiều 1 pixel; PNG có đuôi .jpg; APNG hai frame; BMP ngoài phạm vi; chữ giả JPEG; header JPEG/PNG hỏng, CRC PNG sai và PNG bị cắt; ảnh đúng 16 MP và ba header vượt quota/bomb warning/bomb error.

Ảnh 4000×4000 đúng ngưỡng là PNG hợp lệ, nén từng dòng khi sinh để không cần tạo raster 48 MB. Các probe header 4001×4000, 10000×10000 và 20000×20000 cố ý giữ payload nhỏ; manifest đánh dấu `header_only`, tuyệt đối không load. Ca byte 15 MiB/+1 byte được tạo trong RAM của test từ fixture nhỏ, không lưu tệp lớn vào Git.

**Đã chạy:** `backend/.venv/Scripts/python.exe experiments/create_fixtures.py`; đối chiếu hash/dung lượng toàn bộ 22 tệp, mở và load 10 ảnh được chấp nhận, kiểm tra format/mode/dimensions/frame. Màu góc PNG chính xác, JPEG sai số tối đa 3; EXIF tag/hướng/kích thước sau transpose và alpha ghép trắng khớp manifest. Kiểm tra EXIF/alpha này xác minh dữ liệu thử bằng Pillow, chưa phải triển khai normalize của ứng dụng. Đã xem trực tiếp ảnh góc màu PNG.

### MVP02.02 — Bộ kiểm tra định dạng và quota

`backend/app/processing/normalize.py` có `validate_image(data: bytes) -> ImageInfo` và `ImageValidationError.code`. Metadata bất biến gồm format/width/height/mode/frame_count/byte_count, lấy trước EXIF; lỗi có thông báo tiếng Việt, không import HTTP/DB/UI.

Kiểm tra độ dài trước parser; signature và parser chỉ JPEG/PNG; mỗi chiều ≥2, diện tích ≤16.000.000 và một frame. Kiểm tra quota trước verify; không giải mã pixel. Giữ ngưỡng Pillow toàn cục, ánh xạ cả DecompressionBombWarning/Error về TOO_MANY_PIXELS. Kiểm tra container bằng verify bắt CRC/truncation/header hỏng; không khẳng định mọi payload giải mã được. Task MVP02.03 phải mở lại/load và bắt lỗi decoder, rồi mới áp EXIF/alpha/BGR.

**TDD và kiểm chứng thực tế:**

- RED: focused pytest lỗi collection `ModuleNotFoundError: app.processing` trước khi tạo bộ kiểm tra; không có implementation sẵn.
- GREEN: `backend/.venv/Scripts/python.exe -m pytest -c backend/pyproject.toml backend/tests/test_normalize.py` → **33 passed in 0.17s**.
- Toàn bộ backend: `backend/.venv/Scripts/python.exe -m pytest -c backend/pyproject.toml backend/tests` → **34 passed in 0.72s**, gồm health không hồi quy. Dùng quyền được auto-review cho phép do TestClient async bị giới hạn bởi sandbox đã xác định ở MVP01.06.
- Tests chặn Image.open với input quá byte; chặn verify/load với ba header quá pixel; chặn load cả ảnh bình thường/EXIF/alpha/16 MP để chứng minh validator không decode. Kiểm tra ngưỡng byte/pixel bao gồm đúng giới hạn; bảo vệ toàn cục Pillow còn nguyên và ảnh nhỏ vẫn được nhận sau ca bomb.

Rà soát năm mặt: hành vi/biên đúng checklist; một hàm, metadata và lỗi đơn giản; phụ thuộc chỉ Pillow/stdlib và settings quota chung; chỉ parser được cho phép, thông báo không lộ chi tiết nội bộ; không cấp phát raster trong validator. Không thêm dependency, sửa frontend hoặc tắt test/cảnh báo. README ghi lệnh tạo fixtures, lệnh focused test, giao diện hàm và giới hạn verify theo nguồn Pillow.

**Bàn giao:** tích MVP02.01–MVP02.02 sau bằng chứng trên; tổng 9 task chính đã hoàn thành, MVP01.08 giữ trạng thái bỏ qua. MVP02.03 và Checkpoint 02-C1 chưa hoàn thành. Bước tiếp theo là decode/EXIF/alpha/BGR; chưa có upload/scan trên UI. Không commit/push/deploy.

Rà cuối: chạy lại generator từ thư mục experiments/ và so SHA-256 với bản đã kiểm chứng → 22 fixtures cùng manifest giống hệt. Có 27 liên kết nội bộ hợp lệ trong các tài liệu cập nhật; checklist chỉ tích 9 task chính đã có bằng chứng, task 03 vẫn để trống. Git check-ignore xác nhận script/validator/tests/manifest và fixtures tổng hợp không bị ignore; runtime/dependency tiếp tục theo quy tắc hiện có.

## 14/10/2026 — Hoàn thành MVP02.03 và MVP02.04

**Yêu cầu:** làm task 3–4 giai đoạn 02 và đọc lại tài liệu để tránh mất ngữ cảnh. Đã đọc AGENTS, task/phụ thuộc, mục 1–2 image-contract, mục 9.1 đặc tả gốc, phạm vi MVP, tiến độ 01–02, source/tests/settings và ghi nhớ CentricMem của lượt trước. Nguồn sự thật khớp nhau: BGR uint8 sau EXIF, nguồn gốc giữ riêng, PNG lossless không EXIF cũ, hash trên đúng byte tệp được lưu. Không thay thuật toán detector hoặc phạm vi đã chốt.

Workflow using-agent-skills/context-engineering → triển khai từng phần/TDD/interface → đối chiếu tài liệu chính thức Pillow 12.3.0, NumPy 2.5 và Python 3.12 → rà soát code/tài liệu. Giữ hai tệp source/tests theo task dự kiến; không thêm dependency. Các nguồn kỹ thuật liên kết ở README.

### MVP02.03 — Chuẩn hóa EXIF, transparency và màu

`normalize_image(data: bytes) -> NDArray[np.uint8]` gọi validator trước khi cấp phát raster; mở decoder mới sau verify, load để bắt lỗi bitstream, áp EXIF một lần trên đối tượng decoder riêng và kiểm tra kích thước sau EXIF. Alpha/transparency (RGBA, LA, palette, tRNS của RGB/L) ghép nền trắng; grayscale/CMYK chuyển RGB rồi đảo kênh sang BGR. Đầu ra `(H, W, 3)` uint8 liên tục, ghi được, độc lập decoder; byte nhập không bị sửa. Chỉ thao tác trên nguồn giải mã mới, không ghi đè tệp nhập.

Lỗi payload JPEG bị cắt và PNG có CRC đúng nhưng zlib sai: header/verify vẫn có thể qua, nhưng normalize trả `INVALID_IMAGE`. Không bật LOAD_TRUNCATED_IMAGES hoặc bỏ bảo vệ Pillow. Bộ kiểm tra header vẫn giữ chức năng không load ở task 02.

**TDD thực tế:** viết tests trước → RED `ImportError: normalize_image` chưa tồn tại → hiện thực → focused pytest **61 passed in 0.72s**. Bao gồm 10 fixture hợp lệ (cả đúng 16 MP), bảng kỳ vọng độc lập cho đủ 8 hướng EXIF, màu góc/BGR, alpha trắng, PNG transparency key, JPEG CMYK, lỗi decoder và từ chối header lớn/APNG trước load. Các ca task 01–02 không hồi quy. Checkpoint 02-C1 đạt sau kiểm chứng này và tiếp tục đạt trong bộ cuối task 04.

### MVP02.04 — Encode PNG và metadata đúng payload

`encode_normalized_png(bgr) -> EncodedSource` kiểm tra shape/dtype/quota pixel trước encoder; tạo ảnh RGB mới, không kế thừa EXIF/ICC/XMP; encode PNG lossless với compress_level=6. Kết quả bất biến gồm `png_bytes`, `width`, `height` sau EXIF và `sha256` của chính PNG payload. Lõi không phụ thuộc HTTP/DB/storage; lớp storage ở task sau phải ghi nguyên payload, giữ byte nhập riêng.

15 MiB là quota của upload, không phải PNG nguồn nội bộ: ảnh JPEG trong quota có thể cho PNG lớn hơn. Encoder vẫn kiểm tra ≤16 triệu pixel và mỗi chiều ≥2; đọc source đã lưu theo hợp đồng nội bộ, không áp lại quota byte của upload. SHA-256 ổn định với cùng byte; tests chứng minh PNG/hash lặp lại với cùng pixel trong phiên bản codec đã khóa, không cam kết byte giống hệt khi đổi mọi phiên bản codec.

**TDD và kiểm chứng thực tế:**

- RED `ImportError: encode_normalized_png` sau khi thêm tests và trước implementation.
- Focused tests: `backend/.venv/Scripts/python.exe -m pytest -c backend/pyproject.toml backend/tests/test_normalize.py` → **83 passed in 2.06s**. TEMP/TMP của tiến trình đặt trong `.tmp/pytest-temp` để tệp thử nằm trong workspace sandbox.
- Toàn backend: `backend/.venv/Scripts/python.exe -m pytest -c backend/pyproject.toml backend/tests` → **84 passed in 1.99s**; dùng quyền được auto-review cho phép cho TestClient async như hạn chế môi trường đã ghi. Không skip/tắt test hoặc cảnh báo.
- Với 10 fixture hợp lệ, tests ghi PNG ra tệp tạm, đọc lại để đối chiếu từng pixel BGR, width/height, PNG RGB, EXIF trống và SHA-256 của byte trên đĩa. Kiểm tra nguồn/mảng không bị sửa, dữ liệu không liên tục trong RAM, dtype/shape sai, chiều quá nhỏ/quá pixel trước encoder, hash đổi khi pixel đổi và không xoay lần hai khi reopen EXIF 6/2.

Kiểm chứng thêm bằng hàm thật: tạo ba PNG EXIF 6/EXIF 2/alpha trong `.tmp/verification/mvp02-03-04/`, lưu metadata.json, mở lại và so pixel/hash/EXIF. EXIF 6 từ 96×64 thành 64×96, EXIF 2 giữ 96×64 và phản chiếu, RGBA thành RGB 4×2 nền trắng. Đã xem trực tiếp ảnh EXIF 6 chuẩn hóa; đây là ảnh tổng hợp, không gửi ảnh lên dịch vụ ngoài.

Rà năm mặt: khớp hợp đồng và kiểm thử biên; ba hàm rõ vai trò cùng hai dataclass nhỏ; không import HTTP/DB hoặc thêm storage sớm; whitelist parser, giữ kiểm tra trước allocation và lỗi decoder; dùng in_place EXIF trên decoder riêng và mảng BGR liên tục, không giữ decoder sống. Dùng chung kiểm tra dimensions cho validate/normalize/encode để quota không lệch. Đây là kiểm chứng chức năng, chưa phải đo chất lượng detector hoặc benchmark RAM/CPU.

**Bàn giao:** 11 task chính hoàn thành (MVP01.01–MVP01.07, MVP02.01–MVP02.04); MVP01.08 vẫn bỏ qua. Checkpoint 02-C1 đạt; MVP02.05/MVP02.06, Checkpoint 02-C2 và cổng giai đoạn 02 còn chờ. Cập nhật README/AGENTS/phạm vi/project-map/image-contract/plan/todo; nguồn byte quota và giao diện hàm được ghi bền để phiên sau không nhầm. Không commit/push/deploy; giao diện vẫn là health, chưa có upload/scan.

Rà cuối tài liệu/Git: 32 liên kết nội bộ hợp lệ trong 8 tài liệu cập nhật; checklist chỉ tích 11 task chính đúng bằng chứng, task 05–06 còn trống. Hash/dung lượng 22 fixtures cũ không đổi. PNG kiểm chứng, pytest Temp/cache và venv được ignore; source/tests không bị ignore. Lượt helper kiểm tra Git ban đầu so output bị CRLF/quoting Windows làm lệch đường dẫn; đã dùng giao thức NUL của git check-ignore --stdin -z và xác nhận đúng, không sửa ignore hoặc code ứng dụng vì lỗi helper này.

## 14/10/2026 — Hoàn thành MVP02.05 và MVP02.06

**Yêu cầu:** triển khai task 5–6 giai đoạn 02. Đã đọc using-agent-skills, AGENTS, task/phụ thuộc, image-contract mục 1–2, tiến độ/mã chuẩn hóa và quy tắc Git; áp dụng triển khai từng phần, TDD, thiết kế giao diện hàm/CLI, đối chiếu OpenCV resize/Python argparse và rà soát code. Không đổi kiến trúc hoặc detector. Task 06 cần ảnh thật; đã hỏi đường dẫn trong lúc tiếp tục phần độc lập. Người dùng đặt một JPG ở root và cho phép dùng để kiểm chứng.

### MVP02.05 — Helper thumbnail/preview

`backend/app/processing/image_sizes.py` có `resize_to_max_edge(image, max_edge)`: nhận gray `(H,W)` hoặc BGR `(H,W,3)` uint8; max_edge nguyên dương; không upscale, không thay nguồn, kết quả độc lập. Khi thu nhỏ dùng OpenCV INTER_AREA, kích thước `floor(value + 0.5)` và tối thiểu 1 cho display. Không threshold lại BW preview. Nếu caller dùng cho analysis, cạnh <2 vẫn cần manual_required trước geometry. Preview kết quả sẽ lấy từ full render như hợp đồng, CLI hiện chỉ tạo thumbnail của nguồn.

TDD: `test_image_sizes.py` được viết trước → RED thiếu app.processing.image_sizes → GREEN **26 passed in 0.63s**. Chứng minh dọc/ngang, giới hạn preview 1000, ca .5 ra 11 thay vì bankers-round 10, ảnh rất nhỏ/đúng ngưỡng không upscale, panorama thành 1×320/320×1 không dimensions 0, BW 2×2 thu thành mức xám 128, mảng không liên tục giữ kênh, tham số/dtype/shape sai bị từ chối. Hàm không đổi HTTP/DB/UI.

### MVP02.06 — CLI một ảnh

`experiments/normalize_one.py` nhận input, --output-dir bắt buộc và --thumbnail-max-edge mặc định 320. Đọc tối đa 15 MiB+1, nối normalize_image → encode_normalized_png → resize_to_max_edge, chuẩn bị source.png/thumbnail.png/metadata.json rồi ghi vào thư mục mới. Thư mục đã có bị từ chối (OUTPUT_EXISTS), file ghi exclusive; không ghi đè nguồn. Metadata có kích thước thực, byte_count và SHA-256 của input/source/thumbnail, không dùng ratio danh nghĩa để đo ảnh. Thumbnail có thể chỉ 1 pixel ở cạnh ngắn nên encode riêng, không nới ngưỡng ≥2 của nguồn hình học.

CLI chạy trực tiếp bằng Python venv từ root hoặc thư mục khác với đường dẫn tuyệt đối; dùng UTF-8 cho thông báo/đường dẫn tiếng Việt. Thành công exit 0, lỗi ảnh/I/O/output tồn tại exit 1 có code/thông báo không traceback; tham số sai exit 2. Không thêm dependency, không có server/upload/DB trong CLI. Output thử ở experiments/results/ được ignore; thêm ignore đúng ảnh người dùng cung cấp tại root để giữ ngoài Git. Task 06 thực tế có 3 tệp source/test/ignore, vẫn trong giới hạn một task; tổng ID không thay đổi.

TDD: `test_normalize_cli.py` gọi chương trình thật qua subprocess; RED lần đầu script chưa tồn tại → GREEN **16 passed in 24.94s**. Sau đó bổ sung so pixel thumbnail thực với helper; kiểm chứng cùng cả backend đạt bên dưới. Các ca bao gồm EXIF/alpha/2×2/16 MP, Unicode/khoảng trắng, chạy ngoài cwd, pixels/source/thumbnail/hash, nguyên nguồn, tệp giả/hỏng/APNG/quá pixel/quá byte, thiếu input, chống ghi đè, tham số sai, thumbnail 1 pixel và --help.

**Đã chạy lệnh thực tế từ root:**

```powershell
& .\backend\.venv\Scripts\python.exe experiments/normalize_one.py fixtures/exif_6.jpg --output-dir experiments/results/mvp02-06-exif --thumbnail-max-edge 32
& .\backend\.venv\Scripts\python.exe experiments/normalize_one.py fixtures/alpha_rgba.png --output-dir experiments/results/mvp02-06-alpha
& .\backend\.venv\Scripts\python.exe experiments/normalize_one.py fixtures/fake.jpg --output-dir experiments/results/mvp02-06-invalid
```

JPEG EXIF/PNG alpha exit 0, tạo đủ ba tệp. Tệp giả exit 1, in UNSUPPORTED_FORMAT rõ và không tạo output. Ảnh người dùng cung cấp ở root cũng được chạy bằng CLI thật: kết quả tại experiments/results/mvp02-06-user-image/, source **279×403 / 182.757 byte**, thumbnail **222×320 / 103.659 byte**. Đọc lại hai PNG, so mọi pixel với normalize/resize, dimensions và hash đúng tệp; hash input hiện tại khớp giá trị tính trước xử lý trong metadata. Đã xem ảnh input và thumbnail trực tiếp. Đây là ảnh dùng kiểm chứng CLI, chưa gán split/condition hoặc tính vào nhóm development MVP02.08.

Helper xác minh ban đầu in thông báo CLI qua stdout cp1258 của Windows và lỗi UnicodeEncodeError sau khi CLI đã thành công; chương trình CLI vốn dùng UTF-8 và các tests Unicode đều đạt. Đã sửa encoding của helper xác minh, kiểm tra các tệp đã tạo và hoàn tất đối chiếu; không chạy lại vào thư mục cũ hoặc sửa input.

**Toàn backend:** `backend/.venv/Scripts/python.exe -m pytest -c backend/pyproject.toml backend/tests` → **126 passed in 25.01s** (1 health +83 nguồn/PNG +26 resize +16 CLI). Dùng quyền auto-review đã cho phép vì TestClient async bị hạn chế sandbox; focused tests đặt Temp trong .tmp/pytest-temp. Không skip/tắt test/cảnh báo; frontend không đổi nên không lặp build/browser kiểm chứng đã có.

Rà năm mặt: hành vi đúng hợp đồng và boundaries; một helper/một CLI ngắn, gọi lại lõi thay vì nhân bản normalize; imports không HTTP/DB; bounded read và output exclusive giữ nguồn; resize sử dụng dimensions thực/INTER_AREA, không giữ toàn bộ dataset trong RAM. Chưa phải đo accuracy hoặc benchmark xử lý tài liệu.

**Bàn giao:** 13 task chính hoàn thành (MVP01.01–MVP01.07, MVP02.01–MVP02.06); MVP01.08 vẫn bỏ qua. Checkpoint 02-C2 đạt. MVP02.07 (manifest/split), MVP02.08 (development) và cổng giai đoạn 02 còn chờ. README/AGENTS/phạm vi/project-map/image-contract/plan/todo đã cập nhật. Không commit/push/deploy; giao diện localhost vẫn ở health.

Rà cuối: 34 liên kết nội bộ trong 8 tài liệu cập nhật hợp lệ; checklist chỉ tích 13 task chính đúng bằng chứng, task 07–08 chưa tích. 22 fixtures cũ giữ nguyên hash/dung lượng. Ảnh người dùng, kết quả CLI và Temp được Git ignore; bốn tệp source/tests mới không bị ignore. Output tệp giả không được tạo.

## 14/10/2026 — MVP02.07, MVP02.08 và AUX02.01: dữ liệu và rà tám task

**Yêu cầu:** làm task 7–8, kèm task phụ kiểm tra lại đủ tám task giai đoạn 02 có đúng đặc tả/kiểm chứng không. Đã đọc using-agent-skills, AGENTS, plan/todo, hợp đồng ảnh, MVP mục 6, đặc tả gốc 9.1–9.2/16.1, code/tests/fixtures và tiến độ; dùng triển khai từng phần/TDD, documentation và code review; dùng debugging khi tìm lỗi. Không spawn agent, đổi kiến trúc hoặc mở rộng detector/UI.

### MVP02.07 — Manifest, split và nhãn EXIF

Tạo experiments/dataset_manifest.csv và docs/dataset.md: kế hoạch 10 tài liệu/40 ảnh, 6 development/4 test; giữ nguyên mục tiêu nhưng ghi số thu thực tế. Schema gồm image_id/document_id/condition/split/source_path/source_sha256/normalized_path/normalized_sha256. Split theo tài liệu vật lý/nội dung; variants cùng nhóm; test không tune; nhãn góc gắn PNG sau EXIF, W/H và hash, normalized W−1/H−1. Nhãn chưa gán không được coi là đã nghiệm thu.

Thêm validate_dataset.py và tests để enforce schema, ID/condition/path/hash, cùng doc ở một split, nguồn/normalized không trùng hash/path, path tương đối không thoát project và vùng dữ liệu ignored. --check-files kiểm tra tồn tại/checksum theo khối, không decode/tune test hoặc suy luận danh tính. Task 07 thực tế 4 tệp source/doc/CSV/test, quy mô M, không thêm dependency.

TDD: RED thiếu validate_dataset.py → GREEN **18 passed in 0.43s**. Manifest ban đầu chỉ header, báo 0/0 rõ (không tính ảnh chưa có). Sau khi ảnh/group được user xác nhận đã ghi 6 dòng thật và kiểm tra lại cả tệp/hash. Các tests đi qua metadata mẫu chứ không yêu cầu ảnh private có trong Git/CI.

### MVP02.08 — Thu và kiểm chứng nhóm development

Đã hỏi thiếu ảnh trong lúc tiếp tục phần độc lập. Người dùng thêm **7 JPG trong experiments/data/**, sau đó xác nhận **cùng một tờ giấy vật lý**. So byte SHA thấy hai tệp cùng tên có/không hậu tố `(1)` trùng nhau; giữ nguyên cả hai, chọn bản không hậu tố và **chỉ đếm 6 ảnh khác nhau**. Toàn bộ gán doc_01/development; **test 0**. Không tính ảnh demo root/fixtures vào nhóm này, không tạo góc hoặc augmentation để thay dữ liệu thật.

Chạy normalize_one.py thật cho 6 ảnh vào experiments/results/development/img_001…img_006/. Mỗi source PNG **1536×2048**, thumbnail **240×320**. Đọc lại từng source/thumbnail và so mọi pixel với normalize_image/resize_to_max_edge, kiểm tra hash tệp/dimensions/EXIF trống, byte source gốc giữ nguyên. Đã xem trực quan cả 6: sáng khá đều, nhiều phối cảnh, góc trái trên gấp nhẹ ở img_001/img_006, bóng đậm ở img_003, nền gỗ/đồ vật nhiều chi tiết. Ghi shadow_strong cho bóng đậm, không ghi thành bóng nhẹ.

`backend/.venv/Scripts/python.exe experiments/validate_dataset.py --check-files` → development **6 ảnh/1 tài liệu**, test **0 ảnh/0 tài liệu**, files_checked=true. Điều này đủ nhóm ban đầu ≥6 và cổng 02, chưa đạt dữ liệu thí nghiệm cuối 10/40 hoặc độc lập tài liệu. Ground truth góc/tuning/metrics chưa thực hiện; ảnh gấp/bóng được giữ như ca khó để ghi giới hạn.

### AUX02.01 — Đối chiếu và sửa sai lệch giai đoạn 02

Thêm 1 task phụ do user yêu cầu vào todo.md, ngoài tổng 109 task chính/5 tùy chọn; không đổi ID chính gốc. docs/audit-phase-02.md có ma trận yêu cầu → code/tài liệu → bằng chứng → kết quả của cả tám task, phạm vi chưa triển khai và giới hạn dataset. Source/docs/tests đã được rà lại, không chỉ lấy checklist tồn tại làm bằng chứng.

**Lỗi task 05 tìm được:** float scale gây half chính xác 2.5/62.5/7.5 thành giá trị thấp hơn chút, dẫn đến làm tròn xuống. Các ca W×H/max_edge: 77×9856/320 → rộng2 thay3; 76×1216/1000 →62 thay63; 11×1760/1200 →7 thay8. Thêm 3 regression tests trước sửa → **3 failed, 26 passed**; sau sửa half-up bằng số nguyên `(2*dimension*max_edge+longest)//(2*longest)` → **29 passed in 0.54s**. Giữ INTER_AREA/no-upscale/min display1 và geometry≥2. Rà soát trước khi bổ sung đã thực sự phát hiện lỗi dù suite cũ 126 tests đạt.

**Kiểm chứng cuối mã:** `backend/.venv/Scripts/python.exe -m pytest -c backend/pyproject.toml backend/tests` → **147 passed in 25.17s** = 1 health +83 nguồn/PNG +29 resize +16 CLI +18 dataset. Dùng escalation auto-review đã cho phép do TestClient async bị sandbox hạn chế; không skip/tắt test/cảnh báo. Không lặp suite khi chỉ đổi CSV/doc; manifest thực đã chạy --check-files sau cập nhật dữ liệu.

Kiểm chứng thêm: 22 fixture hashes/dung lượng còn nguyên, load 10 fixture hợp lệ; 6 bộ source/thumbnail khớp pixel/hash/raw bytes và helper đã sửa. Inventory gốc/chuẩn hóa ở .tmp/verification/mvp02-audit/; không đưa ảnh hoặc dữ liệu pixel ra dịch vụ ngoài. Frontend không đổi, vẫn health; upload/session20/DB/full render/geometry/labels là các task sau, không tuyên bố đã có.

**Bàn giao:** 15 task chính đã hoàn thành (MVP01.01–MVP01.07, MVP02.01–MVP02.08) và AUX02.01; MVP01.08 giữ trạng thái bỏ qua. Cổng giai đoạn 02 đạt, tiếp theo MVP03.01 tọa độ trên source sau EXIF. Kế hoạch 10 tài liệu/40 ảnh/test độc lập còn cần bổ sung; dataset hiện một tài liệu không dùng để kết luận khả năng tổng quát. Cập nhật README/AGENTS/plan/todo/phạm vi/project-map/image-contract/dataset/audit/progress. Không commit/push/deploy hoặc xóa/ghi đè ảnh user.

Rà cuối: 49 liên kết nội bộ trong 10 tài liệu hợp lệ; 15 task chính và AUX02.01 được tích theo bằng chứng, MVP03.01 chưa tích. Giữ đủ 110 ID task chính gốc (109 cần làm +1 bỏ qua), thêm 1 AUX ngoài tổng. Đối chiếu SHA của cả 7 ảnh nhập với inventory trước xử lý → không đổi; dữ liệu/results/inventory đều Git ignore, CSV/checker/test/dataset/audit không bị ignore. Manifest thực kiểm tra lại → development 6/1 doc, test 0/0.

## 14/10/2026 — Hoàn thành MVP03.01 và MVP03.02

**Yêu cầu:** triển khai task 1–2 giai đoạn 03 sau khi giải thích vai trò/thuật toán. Đã đối chiếu AGENTS, task/phụ thuộc, bằng chứng cổng 02, image-contract mục 3–4 và phân tích hướng thuật toán mục 5.5.1. Dùng using-agent-skills, incremental implementation, TDD, thiết kế giao diện hàm, rà code và cập nhật tài liệu; giữ lõi độc lập HTTP/DB/UI, dùng standard library, không thêm dependency.

**MVP03.01:** `backend/app/processing/geometry.py` có `pixel_to_normalized(point, width, height)` và `normalized_to_pixel(point, width, height)`. Dimensions nguyên ≥2 sau EXIF; W−1/H−1 theo kích thước thực; điểm gồm hai số thực hữu hạn trong phạm vi. Trả tuple số thực, không clamp/làm tròn/đổi input; nhận NumPy scalars. `GeometryValidationError(ValueError)` có code/thông báo tiếng Việt, không HTTP status. Không nhân bản quota nguồn/upload. TDD: viết tests trước → RED thiếu mô-đun → **55 passed in 0.47s**. Kiểm chứng bốn điểm biên, subpixel, round-trip trên 2×2/101×51/1536×2048/8000×2000/2×8 triệu/9856×77; mapping bằng dimensions thực sau resize, NaN/Infinity/ngoài phạm vi/shape/type/dimensions sai.

**MVP03.02:** `validate_quad_points(corners, width, height)` nhận đúng bốn điểm normalized, tái dùng kiểm tra tọa độ, trả pixel theo nguyên thứ tự nhập. Đo Euclid trên pixel, kiểm tra tất cả sáu cặp điểm trước bốn cạnh theo chu kỳ kể cả 3→0. Khoảng cách ≤1e−6·D báo DUPLICATE_POINTS; cạnh ≤1e−3·D báo SHORT_EDGE, D=hypot(W−1,H−1); số điểm sai báo INVALID_CORNER_COUNT. Đây là baseline tương đối được nêu trước triển khai và ghi trong image-contract, không phải ngưỡng trích giáo trình hoặc đo accuracy. Liên hệ `quad_edge_lengths_px` trong phân tích 5.5.1; debug descriptor/detector chưa được triển khai. Không ép góc vuông/song song, không dùng diện tích tối thiểu 10% của detector lên vùng tay.

TDD task 02: bổ sung tests trước → RED thiếu validate_quad_points → **111 passed in 0.56s** cho cả geometry. Fixture tọa độ kiểm tra trùng/gần trùng ở cả sáu cặp, cạnh ngắn ở mọi vị trí, chiều đóng, ngưỡng inclusive, scaling độ phân giải, đo đúng pixel khi hai trục khác tỷ lệ, full image 2×2, vùng tay nhỏ, phối cảnh và hình thoi. Kiểm tra giữ input/thứ tự NumPy handles. Test cố ý cho bow-tie đi qua gate điểm/cạnh để ghi rõ đây là validation từng phần: topology/diện tích/lồi/winding thuộc MVP03.03, không dùng riêng hàm này để cho phép homography.

**Kiểm chứng cuối:** từ root, `backend/.venv/Scripts/python.exe -m pytest -c backend/pyproject.toml backend/tests` → **258 passed in 25.47s** = 147 ca cũ +111 geometry. Chạy quyền auto-review cho phép để TestClient/CLI không bị sandbox chặn; không skip/tắt test/cảnh báo. Frontend không đổi nên không lặp build/browser. Rà code năm mặt: đúng đơn vị/phạm vi, lỗi có lý do ổn định, reuse conversion, không dependency HTTP/DB hoặc I/O ảnh, vòng lặp giới hạn bốn điểm; không thêm topology/sort/warp ngoài hai task.

**Bàn giao:** 17 task chính hoàn thành (7 giai đoạn 01 +8 giai đoạn 02 +2 giai đoạn 03), AUX02.01 hoàn thành; MVP01.08 vẫn bỏ qua. Tiếp theo MVP03.03; Checkpoint 03-C1 và cổng 03 còn chờ. Cập nhật checklist duy nhất todo, plan/README/AGENTS/phạm vi/project-map/image-contract/progress. Không commit/push/deploy, không đọc hoặc thay ảnh cá nhân, giao diện vẫn health.

Rà cuối: 42 liên kết nội bộ trong 8 tài liệu cập nhật đều hợp lệ; đúng 17 task chính được tích, giữ 110 tiêu đề ID gốc và MVP03.03 chưa tích. Git check-ignore xác nhận geometry.py/test_geometry.py được theo dõi được, data/results và Temp vẫn ignored. Chỉ thêm hai tệp code/test và cập nhật tài liệu trong phạm vi hai task.

## 14/10/2026 — Hoàn thành MVP03.03 và MVP03.04

**Yêu cầu:** triển khai task 3–4 giai đoạn 03 và kiểm tra lại lý thuyết đã gửi. Dùng using-agent-skills, triển khai từng phần/TDD, thiết kế hợp đồng hàm, rà code và PDF. Đối chiếu phụ thuộc/bằng chứng MVP03.01–02, image-contract mục 3–4, phân tích thuật toán 5.4–5.5.3 và đặc tả gốc 9.9. Đọc lại các phần liên quan trong cả ba PDF: giáo trình trang 163–164 (6.2.3, đỉnh lồi/lõm và chiều đi trên biên), chương 6 trang 17–19/35 (đa giác/đặc trưng), chương 5 trang 6–8 (biên/vùng). Trích text để tra cứu, không coi đó là đọc kỹ toàn bộ giáo trình; render/xem trọn giáo trình trang 164 và slide 6 trang 17–18. Runtime không có fitz nên dùng pypdf và pypdfium2 sẵn có, không thêm dependency dự án. Bản tra cứu/render tại .tmp/theory-review-mvp03/ ignored.

**Kết luận lý thuyết:** đa giác là biểu diễn biên có thứ tự; đỉnh lồi/lõm và hướng đi có ý nghĩa hình học. Shoelace là diện tích vùng; cross/segment và sort atan2 là cách cụ thể hóa kiểm tra/sắp của đặc tả dự án 9.9. Không gọi code này là MPP của giáo trình hoặc Douglas–Peucker, không ép góc vuông/song song trên ảnh phối cảnh; số Euler/compactness không thay kiểm tra tự giao của quad. Đã ghi đối chiếu bền trong phân tích mục 5.5.4.

**MVP03.03:** `validate_quad(corners, width, height)` nhận normalized có chu kỳ, trả pixel giữ nguyên điểm đầu và handles. Nối validate_quad_points, rồi kiểm tra near-collinear, hai cặp cạnh đối giao/chạm/overlap, diện tích shoelace, độ lồi và winding. Cross/tolerance đo trên pixel chia cùng đường chéo D ở hai trục để giữ metric và tránh tràn số. Near-collinear: abs(cross)≤1e−6·D·max(hai cạnh kề); abs(area)≤1e−6·D² bị loại. Shoelace tịnh tiến về p0 và fsum qua hai tam giác có dấu để vùng nhỏ gần mép không mất chính xác vì trừ các tích tọa độ lớn. Chỉ area dương trong hệ y xuống được nhận; code lỗi mới DEGENERATE_QUAD/SELF_INTERSECTION/NON_CONVEX_QUAD/INVALID_WINDING. Thứ tự lỗi/tolerance ghi rõ trong image-contract. Các ngưỡng là baseline triển khai đã thông báo, chưa phải số đo accuracy hoặc quota 10% detector.

TDD task 03: thêm tests trước → RED thiếu validate_quad → **155 passed in 0.59s** cho geometry. Các ca gồm full-image 2×2, small manual, perspective/diamond, xoay vòng điểm đầu, hai kiểu bow-tie, concave, collinear/near-collinear, vùng diện tích rất nhỏ dù cạnh dài, ngược winding, lỗi từ gate trước và vùng nhỏ gần phải dưới. Hành vi giữ input/thứ tự.

**Checkpoint 03-C1 đạt:** đối chiếu nghiệm thu task 01–03 với tests/bằng chứng nguồn sau EXIF/W−1/H−1/point-edge/topology. Giữ hàm point gate riêng và validation đầy đủ riêng; không cho rằng point gate đã chứng nhận toàn hình học. Không có lỗi/chặn trước nhóm tiếp theo.

**MVP03.04:** `order_auto_corners` nhận đề xuất auto không có chu kỳ, chuyển sang metric pixel nguồn, sort atan2 quanh trung bình bốn điểm, chuẩn hóa shoelace dương, rotate tới min(x+y), tie y/x theo pixel nguồn. Trả normalized giữ giá trị gốc; gọi validate_quad cuối. Tách `_quad_pixels` dùng chung cho giải mã/count/range để sorter chưa áp cyclic edge validation lên điểm lộn xộn: một đường chéo ngắn chưa phải cạnh. Manual chỉ gọi validate_quad, không sorter; input set lõm/thiếu/trùng/suy biến không được thêm hoặc bỏ đỉnh để sửa.

TDD task 04: thêm tests trước → RED thiếu order_auto_corners → **171 passed in 0.61s** cho geometry. Duyệt đủ 24 hoán vị mỗi bộ rectangle/diamond/perspective/rotated/small; chỉ một kết quả chuẩn, đủ bốn đỉnh và qua validate_quad. Ca metric anisotropic chọn điểm đầu theo pixel, short diagonal không bị nhầm edge, bộ điểm sai được loại; duyệt 24 hoán vị manual để chỉ nhận các cyclic clockwise và giữ handles; idempotence/NumPy input không đổi.

**Kiểm chứng cuối:** `backend/.venv/Scripts/python.exe -m pytest -c backend/pyproject.toml backend/tests` → **318 passed in 26.54s** =147 nguồn/health/resize/CLI/dataset +171 geometry (60 ca mới). Auto-review cho phép chạy TestClient/CLI; không skip/tắt tests/cảnh báo. Một đợt đối chiếu độc lập trên 1.000 bộ 4 điểm nguyên riêng biệt trong lưới 0..100 (seed304): manual acceptance so cv2.isContourConvex + oriented area dương, auto acceptance so hull có đúng 4 đỉnh. **0 sai khác; manual nhận109, auto nhận680**. Đây là kiểm tra hình học trên bộ tọa độ tổng hợp, không accuracy detector, benchmark hoặc đánh giá ảnh thật. Ngưỡng gần suy biến đã có tests riêng; không thay oracle bằng chính validate_quad.

Rà năm mặt: các phép đo đúng đơn vị và sign y-down, validation có reason ổn định, các hàm public nêu rõ normalized/pixel và giới hạn manual/auto, reuse lõi không HTTP/DB/I/O, số điểm/vòng lặp giới hạn bốn, không dependency mới. Frontend không đổi nên không lặp build/browser; kích thước warp/homography chưa làm. Chỉ sửa hai tệp code/test và tài liệu liên quan, không commit/push/deploy hoặc đọc/thay ảnh cá nhân.

**Bàn giao:** 19 task chính hoàn thành (7 giai đoạn 01 +8 giai đoạn 02 +4 giai đoạn 03), AUX02.01 đạt; MVP01.08 giữ bỏ qua. Checkpoint 03-C1 đạt; tiếp theo MVP03.05, Checkpoint 03-C2/cổng 03 còn chờ. Checklist duy nhất todo; README/AGENTS/plan/phạm vi/project-map/image-contract/phân tích/progress được cập nhật.

Rà cuối: 49 liên kết nội bộ trong 9 tài liệu hợp lệ, đúng 19 task chính được tích, đủ 110 ID gốc; MVP03.05 chưa tích. Code/tests không ignored; PDF render/tra cứu/results vẫn ignored. Helper kiểm tra link ban đầu đọc sai dấu ngoặc trong đường dẫn PDF chương 5; đã sửa parser nhận đích trong <...>, không sửa tên tệp hoặc liên kết đúng sẵn có. Chỉ sửa chú thích/docstring sau full suite, không đổi hành vi. Ghi tóm tắt kỹ thuật lên shelf document-scanner của CentricMem, không gửi ảnh/PDF hoặc dữ liệu cá nhân.

## 14/10/2026 — Hoàn thành MVP03.05 và MVP03.06

**Yêu cầu:** tiếp tục task5–6 giai đoạn03. Đọc lại using-agent-skills, AGENTS, tiêu chí/phụ thuộc trong todo, bằng chứng task03–04/Checkpoint03-C1, image-contract mục6 và đặc tả gốc9.10. Áp dụng triển khai từng phần/TDD, hợp đồng hàm, đối chiếu nguồn chính thức và rà code. Kiểm tra tài liệu OpenCV [transformations](https://docs.opencv.org/4.x/da/d6e/tutorial_py_geometric_transformations.html) và [API](https://docs.opencv.org/4.x/da/d54/group__imgproc__transform.html): bốn cặp điểm, H3×3, source points float32; truyền H thuận cho warpPerspective thì lấy mẫu ngược nội bộ. Giữ INTER_LINEAR như đặc tả, không viết lại solver/sampler. Chọn BORDER_REPLICATE và thông báo trước triển khai để tránh viền đen nhỏ sát nguồn do sai số lấy mẫu.

**MVP03.05:** estimate_warp_size(corners,width,height) nhận normalized, validate_quad rồi lấy max độ dài hai cạnh đối theo mỗi chiều; floor(length+0.5), min2. Nếu vượt2400, giảm cả hai dimensions đã làm tròn theo cùng tỷ lệ bằng phép half-up nguyên chính xác; kiểm tra ≤2400/≤5.760.000pixel trước buffer. Constants trong geometry, không thêm cấu hình ngoài MVP. Không upscale lên2400/épA4; aspect estimated không suy ra khổ vật lý. Cạnh là span giữa tâm pixel theo đặc tả, không cộng1: full source101×51→100×50; source2×2 vẫn2×2 do min2.

TDD05: viết tests trước → RED thiếu estimate_warp_size → **185 passed in0.83s** cho geometry (14 ca mới). Kiểm chứng nhỏ/lớn/dọc/ngang/full-cap2400²; fractional10.5→11, rounded ratio62.5→63, cạnh đối dài hơn của trapezoid, diamond theo cạnh không bounding box và vùng sai bị từ chối. Ca rất xiên chạy trực tiếp sau đó: [(0.02,0.05),(0.9,0.45),(0.91,0.9),(0.03,0.55)] trên101×101 →97×50, giữ lựa chọn cạnh/không ép vuông.

**MVP03.06:** compute_homography(corners,width,height) trả (H,(W,H)): nối full validate/size, getPerspectiveTransform từ bốn pixel points float32 (giữ phần thập phân) sang chỉ số bốn góc đích0/W−1/H−1. Hfloat64 phải finite/shape3×3/khả nghịch bằng slogdet trước sampler; errors INVALID_HOMOGRAPHY. warp_document(source,corners) nhận nguồn BGRuint8 HWC3 sau EXIF, dimensions≥2/≤16MP; không nhân quota upload byte. Trả ảnh BGR độc lập từ warpPerspective(INTER_LINEAR,BORDER_REPLICATE); giữ source/handleorder, không filter/rotation/preview/EXIF/confirmed/revision. Errors INVALID_SOURCE/TOO_MANY_PIXELS/INVALID_WARP_SIZE/WARP_FAILED và các reason geometry cũ; khôngHTTP/DB/I/O trong lõi. Dùng cv2/NumPy đã có, không dependency mới.

TDD06: thêm tests trước → RED thiếu compute_homography → **206 passed in1.04s** geometry (21 ca mới). Bốn source corners chiếu về đích đúng trong2e−4px; bốn màu BGR giữ thứ tự cho cả4 cyclicstarts, giữ mảng nguồn; subpixel source4×4 cho output2×2 các giá trị18/108/36/126 đúng bilinear; source2×2 identity và strided view giữ kênh. Hnan/inf/zero/singular bị chặn trước sampler. Input shape/dtype/quota và geometry sai không tới OpenCV; output2400×2400 được chạy thật, pixel nguồn đều giữ BGR[13,27,91].

**Toàn backend:** `backend/.venv/Scripts/python.exe -m pytest -c backend/pyproject.toml backend/tests` → **353 passed in29.74s** =147 health/nguồn/resize/CLI/dataset +206geometry. Auto-review cho phép TestClient/CLI; không skip/tắt test/cảnh báo. Frontend không đổi, không lặp build/browser.

**Xem trực tiếp kết quả:** helper kiểm chứng cục bộ nối đúng các hàm lõi, ghi độc quyền source.png/warp.png/fixture-warp.png/metadata.json ở experiments/results/mvp03-06-verification/. Source màu tổng hợp120×80, quad [(20,15),(95,8),(105,65),(12,70)] →93×58; bốn marker giữ vị trí và giấy thành chữ nhật. normalize fixtures/corners_rgb.png96×64 →warp95×63; so bốn mẫu màu với nguồn, đạt. Đã mở và xem cả baPNG source/warp/fixturewarp; không lật/xoắn. Đây là bằng chứngtask06, không đánh dấu scriptgeometry_demo/task07 đã làm. Không đọc hoặc gửi ảnh cá nhân; kết quả synthetic ignored.

Rà năm mặt: đúng dimensions/thứ tự/đơn vị, validation/size/H trước sampler, nguồn không đổi, lỗi cócode tiếng Việt, reuse validate_quad/estimated_size, loops giới hạn4points; outputbuffer ≤5.76MP. Homography chỉ cho trang gần phẳng, không dewarp nhàu. README/AGENTS/todo/plan/phạm vi/project-map/image-contract/phân tích/progress đã cập nhật; không commit/push/deploy.

**Bàn giao:** 21 task chính đạt (7phase01 +8phase02 +6phase03), AUX02.01 đạt, MVP01.08 giữbỏqua. Checkpoint03-C2 đạt cùng03-C1; tiếp theoMVP03.07. Task07–08/cổng03 còn chờ; UI vẫnhealth, chưascan từUI.

Rà cuối: 51 liên kết nội bộ trong9tài liệu hợp lệ; đúng21task chính và đủ110IDgốc, MVP03.07 chưa tích. Source/tests không ignored, PNG/metadata kiểm chứng vẫn ignored. Tóm tắt kỹ thuật đã lưu CentricMem; không gửi ảnh/dữ liệu cá nhân.

## 14/10/2026 — Hoàn thành MVP03.07–MVP03.08 và AUX03.01

**Yêu cầu:** làm hai task cuối giai đoạn03 rồi rà lại cả tám task tương tự giai đoạn02. Dùng using-agent-skills, triển khai từng phần/TDD, rà chất lượng code, debugging cho lỗi tìm được và cập nhật hợp đồng/tài liệu. Đọc lại AGENTS/task/phụ thuộc, image-contract3–6, phân tích5.4–5.6 và source/tests; không suy ra xong từ tài liệu tồn tại. Rà trước task07 đã tìm được lỗi nguồn dài và xử lý trong AUX03.01.

**Lỗi audit task06:** input40.000×400/400×40.000 đều đúng16MP, nhưng OpenCV4.14 warp trực tiếp ném assertion `src.cols/src.rows < SHRT_MAX` tại cv::remap. Đối chiếu [mã nguồn OpenCV](https://raw.githubusercontent.com/opencv/opencv/4.x/modules/imgproc/src/imgwarp.cpp) xác nhận giới hạn nội bộ. Thêm hai hồi quy → **2 failed,206 deselected** trước sửa. Không hạ quota đầu vào hoặc resize nguồn để né lỗi. Khi source có cạnh≥32767, `_warp_large_source` chia rectangle đích, inverse-map bốn góc để tìm bbox ROI nguồn<32767 có halo1pixel cho bilinear. H_local=T(−gốc đích)·H·T(gốc nguồn), ghép kết quảwarpPerspective/INTER_LINEAR/BORDER_REPLICATE từ nguồn gốc. Outputbuffer vẫn ≤2400², nguồn thường giữ đường cũ. Sau sửa **208geometry passed in1.08s**; dọc/ngang giữ đúng plateau ở hai bên đường ghép.

**MVP03.07:** experiments/geometry_demo.py nhận originalJPEG/PNG, --corners JSON normalized trên source sau EXIF theo manual cycle (mặc địnhfull), --output-dir mới. Nối normalize/validate_quad/compute_homography/warp_document, tạo source/overlay đánh số0..3/warp/metadata. Rounding chỉ khi vẽ overlay, sourcecorners vàH vẫn sốthực; metadata ghi source/targetcoords, Hsource→warp, dimensions/hashes/bytecount của đúngPNG, CVversion/estimated/interpolation/border. Input bounded15MiB+1; normalize16MP/EXIF; ảnh cá nhân/results ignored. Output exclusive, metadata cuối; invalid input/geometry không tạo thư mục success. Không detector/autosortmanual/confirmed/revision/UI. Tệp thực tếscript +test_geometry_demo.py (2tệp thay dự kiến1, để kiểm chứngCLI).

TDD07: viết8tests subprocess trướcscript → **7 failed,1passed** do file chưa tồn tại. Ca usage lỗi ban đầu chỉ kiểm exit2 nên audit siết thông báo --corners/JSON để tránh false positive; sau code **8 passed in12.29s**, siết test còn **8passed in12.01s**. Kiểm chứng chạy ngoàicwd/Unicodeoutput, fullsavedpixels/hash/dimensions/noEXIF, EXIF6source64×96 vàsuppliedquad/subpixels, self-cross/reverse/concave/fakeinput/error/no-overwrite. Không mock CLI.

**MVP03.08:** thêm diamond24auto-permutations qua warp giữ bốn màu thật; segment cross/touch/overlap/disjoint; nguồn dài và ROI offset35.000 so crop thật tương đương. Ban đầu kiểm ROI có tolerance cho quantization; đo sai khác tối đa thực tế0 nên siết thành **pixel equality**, không nới tests để xanh. Bộgeometry cuối **216passed in1.12s**, gồm các ca cũ winding/full-image/near-collinear/area/metric/subpixel/size/H và10ca mới do regression/audit.

**Các lệnh minh họa đã chạy thật:**

```powershell
& .\backend\.venv\Scripts\python.exe experiments/geometry_demo.py fixtures/corners_rgb.png --output-dir experiments/results/mvp03-07-full
```

Đã chạy thêm CLI trên source tổng hợp của mvp03-06-verification với quad đã ghi metadata → experiments/results/mvp03-07-perspective/; source diamond tự sinh160×160 vàquad bốn đỉnh rõ → experiments/results/mvp03-08-diamond/. Cả3runs exit0. Kích thước source→warp: full96×64→95×63; perspective120×80→93×58; diamond160×160→99×99. Đọc lại9PNG, so hash/dimensions với metadata; mở overlayfull/perspective/diamond vàwarpperspective/diamond trực tiếp, thấy bốn marker đúngchu kỳ và trangchữnhật không mirror/xoắn. Đối chiếu hash/bytecount của22fixtures với manifest →khôngđổi. Không đọc/thay/gửi ảnh cá nhân; synthetic artifacts giữ localignored.

**Kiểm chứng cuối:** `backend/.venv/Scripts/python.exe -m pytest -c backend/pyproject.toml backend/tests` → **371passed in39.34s** =147health/normalize/resize/CLI/dataset +216geometry +8demoCLI. Lượt trước371/38.16s; chạy cuối có lý do vì siết testJSON vàpixelROI saureview. Auto-review cho phép TestClient/CLI; khôngskip/tắt test/cảnhbáo. Frontend khôngđổi, khônglặp build/browser.

**AUX03.01/cổng03:** [audit-phase-03.md](audit-phase-03.md) ghi ma trận đủ8task, bug/tái hiện/sửa, artifacts vàgiới hạn; dữ liệu/sốtests khônglàaccuracy. Rà nămmặt: đúngđơnvị/thứtự/nguồn, inputvalidation/hashes/exclusiveoutput, reusecore/stdlibs/depssẵn, vậnsamplingoriginalROI khi cần, bộnhớ đầu ra bounded. Không thêmfeatures/UI/detector/modes/DB/PDF. SourceROI homography chỉ đổi hệ tọa độ, không thuậttoán xấp xỉ biên mới.

**Bàn giao:** cả giai đoạn03 đạt sau sửa lỗi. **23task chính hoàn thành**, AUX02.01/AUX03.01 đạt ngoài tổngchính; MVP01.08 vẫn bỏqua. Giữ110IDgốc (109cầnlàm+1skip),5optional;2AUXngoàitổng. Cổng02/03, Checkpoint03-C1/C2 đạt; tiếp theoMVP04.01config/preset. README/AGENTS/plan/todo/phạmvi/project-map/image-contract/phântích/progress/audit03 đã cậpnhật. Khôngcommit/push/deploy.

Rà cuối:63liên kết nội bộ trong10tài liệu hợp lệ; checklist đúng23task chính,2AUX, đủ110IDgốc vàMVP04.01 chưa tích. Demo/test/audit được theo dõi được, ảnh runtime vẫnignored. Đã lưu tóm tắt kỹ thuật lên CentricMem, không gửi ảnh/bí mật hoặc dữ liệu cá nhân.

## 14/10/2026 — Hoàn thành MVP04.01: cấu hình và preset lõi

**Yêu cầu:** thực hiện task1 giai đoạn4. Đọc using-agent-skills, AGENTS, task/phụ thuộc và bằng chứng cổng03; đối chiếu image-contract mục7, đặc tả gốc10.4 và các range/preset MVP. Áp dụng TDD, hợp đồng interface, incremental implementation và rà code. Pydantic2.14.1 đã có trong môi trường; đối chiếu [validators](https://docs.pydantic.dev/latest/concepts/validators/) và [strict mode](https://docs.pydantic.dev/latest/concepts/strict_mode/), kiểm signature model_validate/context và ValidationError.errors từ bản cài thật. Không thêm dependency.

**Implementation:** backend/app/processing/config.py có PageConfig cùng DenoiseConfig/ContrastConfig/ThresholdConfig/GeometryConfig; models frozen, extra forbid, validate_default và revalidate_instances. Dùng StrictInt/StrictBool, finite strict floats, tuples cho corners/tilegrid để snapshot không chứa danh sách có thể bị sửa. Ba preset color/gray/bw đầy đủ đúng hợp đồng; color None/None, gray None/CLAHE, BW Median3/None; threshold mặc định Adaptive31/C10, geometry estimated/2400, rotation0, cornersnull/confirmedfalse.

get_preset trả snapshot mới; parse_config(data,source_size=None,warp_size=None) bổ sung default theo mode (thiếu mode→color) và trường con, không merge config cũ, không coi null/enum/type sai là thiếu. Full config đổi mode giữ các tham số đã gửi; inactive_fields trả dotted paths theo mode/method nhưng không xóa field hoặc serialize metadata này vào config. Inactive vẫn phải đúng kiểu/miền. Unknown fields của chức năng hoãn/revision bên trong config đều bị từ chối. ConfigValidationError có code INVALID_CONFIG và field/lý do; không HTTP/DB/I/O hoặc ảnh đầu vào để mutate.

**Kiểm tra liên trường:** confirmedtrue cần corners; corners khácnull yêu cầu source_size thực sau EXIF, reuse validate_quad (giữ handles/không reorder), kể cả confirmedfalse. Không giả source vuông để check tolerance. warp_size khi được truyền phải là dimensions nguyên2..2400; BW Adaptive active đòi block≤cạnh ngắn. Khi chưa biết warp_size, chỉ validate basic ranges; preset chưa chứng minh render-ready. Otsu/color/gray không áp fit-block inactive; không tự giảm block/đổi phương pháp. Service/render các task sau phải truyền dimensions thực và kiểm confirmed/revision; module này chưa chạy filter/mode.

**TDD:** viết backend/tests/test_enhancement.py trước → RED thiếu app.processing.config → **74passed in0.44s** sau implementation. Các ca: so đầy đủ cả3presets; partial nested defaults theo BW; no mutation input; fullmode change giữ Gaussian/CLAHE/block/C cũ và inactive; thiếufield khác null; numeric bool/string/float-as-int, range/odd kernel-block/C, NaN/Infinity/clip/grid/rotation/enum/unknown fields; basic validation kể cả inactive; bounds hợp lệ; frozen snapshots và independent JSON; corners confirmed/draft/bow-tie/concave/duplicate/outside/nonfinite qua đủ24permutations; source_size bắt buộc, warp-size/Adaptive active-only fit; JSON roundtrip và revalidate instance model_copy(update=...) chưa hợp lệ.

**Kiểm chứng cuối:** từ root, `backend/.venv/Scripts/python.exe -m pytest -c backend/pyproject.toml backend/tests` → **445passed in37.15s** =371ca cũ +74config. Auto-review cho phép TestClient/CLI; không skip/tắt tests/cảnh báo. Không sửa code cũ, HTTP/DB/UI hoặc filters nên không lặp build/browser. Rà năm mặt: defaults/units/inactive đúng hợp đồng, strict guards/finite/extra, snapshot bất biến, reuse geometry thật, không ảnh/source mutation hoặc deps mới. Errors không dump raw input.

**Bàn giao:** 24task chính hoàn thành +AUX02.01/AUX03.01, MVP01.08 vẫn bỏqua. MVP04.01 đạt; tiếp theoMVP04.02 bộ lọc None/Median/Gaussian. Checkpoint04-C1 và cổng04 còn chờ; không coi schema/preset là thuật toán enhancement đã triển khai. Cập nhật todo/plan/README/AGENTS/phạm vi/project-map/image-contract/progress; không commit/push/deploy hoặc đọc/thay ảnh cá nhân.

## 14/10/2026 — Hoàn thành MVP04.02: bộ lọc sau warp

**Yêu cầu:** làm task2 giai đoạn4. Đọc using-agent-skills, AGENTS, task/phụ thuộc, config, image-contract và đặc tả9.11; dùng Ponytail/TDD/interface/review. Giữ implementation tối thiểu: một hàm chọn lọc trực tiếp bằng cv2 đã cài; không solver/framework hoặc dependency mới. Đối chiếu [OpenCV image filtering](https://docs.opencv.org/4.x/d4/d86/group__imgproc__filter.html) cho Median/Gaussian/sigma0/channels/border.

**Implementation:** enhancement.py có apply_denoise(warped_bgr,DenoiseConfig), trả BGRuint8 HWC3 độc lập cùngdimensions2..2400. None.copy; Median3/5 với borderreplicate nội bộ OpenCV; Gaussian3/5 sigmaX0/BORDER_REFLECT_101. Không resize/threshold/CLAHE/mode/EXIF, không ảnh detection hoặcpreview; helper nằm trước modeconversion. Revalidate DenoiseConfig để chặn model_copy chưa hợp lệ; inputshape/dtype/dimensions sai báo EnhancementValidationError INVALID_RENDER, lỗiCV FILTER_FAILED, config sai INVALID_CONFIG. Giữ source/config, kể cả arrayreadonly/noncontiguous; padding cho phép lọc warp2×2 bằngkernel5 mà không tự sửa config. Tệp code50dòng, không HTTP/DB/I/O.

**TDD:** thêm tests trước → RED thiếu app.processing.enhancement → **100passed in0.76s** (74config +26filter mới). Tests None/Median3/5/Gaussian3/5 giữ shape/dtype/BGR/constant kể cảbiên, independent output/writeable/source readonly khôngmutate; None giữ mọi pixelstrided array; Median xóa salt/pepper vànét1pixel; Gaussian impulse3center64/5center36, cómứcxám/mềm nét chứ khôngthreshold; nét1pixel source0→Gaussian128, neighbor191; source2×2k5 ổn; rejectunsupported grayscale/channels/dtype/empty/1px/overcap, unsafeconfig không tớiCV.

**Xem ảnh thử:** tạo source synthetic260×180, chữAa123 nét1pixel, đường1pixel,5chấm đen rời vàhighlight màu. Nối helper thật choNone/Median3/Gaussian3, encodePNG, ghi độcquyềnsource/none/median/gaussian/comparison/metadata tại experiments/results/mvp04-02-filters/. Kiểm tra sourcearraykhôngđổi; metadatahashes/size và số đo pixel thật: Median chấm0→255, nét0→255 (xóa); Gaussian nét0→128; None nét0. Mởcomparison trực tiếp: Median mất gần hết glyph1pixel/đườngmảnh, Gaussian làm mềm nhưngcòn hình, None nguyên. Không coi noise/line fixture là nội dung tiếngViệt thật hoặcaccuracy; testcase task03/mode sẽ xửlýảnh phùhợp sau.

**Toàn backend:** `backend/.venv/Scripts/python.exe -m pytest -c backend/pyproject.toml backend/tests` → **471passed in37.26s** =445cũ +26filter. Auto-review cho phép TestClient/CLI, khôngskip/tắt checks. Frontend/HTTP không đổi, không lặpbuild/browser. Rà năm mặt: đúng stagedBGR contract/units vàbasicparams, reuseDenoiseConfig/CV, functionngắn/no speculative abstractions, shape/quota/immutabilityguards, buffersbounded≤2400².

**Bàn giao:** 25task chính +2AUXđạt;01.08 vẫnskip,110IDgốc/5optional giữ. MVP04.01–02 đạt; nextMVP04.03 Color/Gray/CLAHE. Checkpoint04-C1 vàgate04 cònchờ; không đánhdấu task03 hoặcdispatcher đãlàm. README/AGENTS/plan/todo/phạmvi/projectmap/imagecontract/progressupdated, ảnhignored, khôngcommit/push/deploy hoặc đọc/thay ảnhcánhân.

## 14/10/2026 — Hoàn thành MVP04.03 và checkpoint 04-C1

**Phạm vi/lý thuyết:** đọc task/phụ thuộc04.02, image-contract mục7 và nguồn MVP: Color giữ màu; Gray có CLAHE tùy chọn; CLAHE màu/Lab của đặc tả gốc được hoãn. Dùng using-agent-skills, incremental-implementation/TDD, Ponytail và rà chất lượng. Đối chiếu [OpenCV chuyển màu](https://docs.opencv.org/4.x/de/d25/imgproc_color_conversions.html): gray theo luminance Y≈0.114B+0.587G+0.299R. [OpenCV CLAHE](https://docs.opencv.org/4.x/d5/daf/tutorial_py_histogram_equalization.html): histogram cục bộ/clip limit/nội suy; tileGridSize=(8,8) là số tile theo mỗi chiều, không phải ô8pixel. Dùng API có sẵn, không thêm thư viện hoặc viết lại thuật toán.

**Implementation:** enhancement.py có render_color(filtered_bgr) copy BGR giữ nguyên từng pixel sau lọc và render_gray(filtered_bgr,ContrastConfig) dùng BGR2GRAY → optionalCLAHE. Input HWC3 uint8 fullwarp, mỗi chiều2..2400; output Color HWC3/Gray HxW độc lập cùngdimensions/uint8, cảreadonly/strided input. Gray revalidate ContrastConfig trước CV kể cả clip/grid khi none; None tắt CLAHE; clip1..4, grid8x8, presetGray clip2. Chia sẻ guard fullBGR với apply_denoise vì ba helper cùng hợp đồng; không thêm tầng service/abstraction. Input/config không đổi, Color không gọi equalizer hoặc đọc contrast; PageConfig giữ contrast inactive để dispatcher04.06 xử lý. Lỗi INVALID_RENDER/INVALID_CONFIG/MODE_FAILED. Không threshold/rotation/dispatcher/HTTP/DB/I/O; BW sẽ dùng gray trước threshold ở task04–05.

**TDD:** thêm test trước → RED import render_color chưa tồn tại → **132passed in0.83s** sau implementation =74config +26filter +32modes mới. Các ca: Color giữ mọi pixel/highlight và khôngcvtColor/CLAHE; BGR weighting blue29/green150/red76/highlight238; none tắt equalizer; CLAHE nhận gray duy nhất với clip1/2/4 vàgrid8x8, đổi ramp thấp tương phản nhưng không threshold; toggle lại trả gray thô. Kiểm shape/dtype/bufferđộc lập/contiguous/writeable/readonly-strided/nguồn nguyên, minwarp2×2 vàinvalidshape/type/size. Unsafe model_copy clipNaN/bool/range/grid/method bị chặn trướcCV kể cả inactive; CVfailure có reason rõ.

**Nghiệm thu cùng vùng:** chạy `.tmp/mvp04_03_verify.py` bằng backend venv; tạo ảnh full-warp tổng hợp640×300 với Arial hỗ trợ tiếng Việt, chữ/dấu/hàng chữ tương phản thấp và highlight vàng trên nền gradient. DenoiseNone → Color/GrayNone/GrayCLAHE2; lưu source.png/color.png/gray.png/gray_clahe.png/comparison.png/metadata.json tại experiments/results/mvp04-03-modes/ (ignored). Assertions source không đổi, Color bằng source, shape/dtype đúng; hash từng PNG trong metadata. Số đo thật: CLAHE đổi170753pixel/192000; pixel highlight(40,95) BGR[130,235,255], gray229, CLAHE233. Đã mở comparison trực tiếp: highlight vàng còn ở Color, Gray mất màu; đủ dấu tiếng Việt ở cả ba, CLAHE đổi cả nền gradient. Không gọi ảnh tổng hợp là ảnh chụp thật, không suy ra accuracy hoặc CLAHE luôn cải thiện độ đọc. Giữ công tắcnone để người dùng lựa chọn.

**Hồi quy/rà soát:** toàn backend `backend/.venv/Scripts/python.exe -m pytest -c backend/pyproject.toml backend/tests` → **503passed in38.20s**. Auto-review cho phép chạy TestClient/CLI ngoài sandbox; khôngskip/tắt check. Đọc lại code/test: đúng thứ tựlọc→mode→contrast, guard bounded2400², configstrict/finite, khôngmutate nguồn hoặc xử lý lạiEXIF; reuse ContrastConfig/OpenCV và chỉhelper phục vụ task. Frontend/HTTP không đổi, không lặpbuild/browser.

**Checkpoint04-C1:** MVP04.01 có preset/fullschema/inactive/góc/warpfit bằng74tests;04.02 có None/Median/Gaussian cùng26tests vàảnh chấm/nét1pixel;04.03 có Color/Gray/CLAHE cùng32tests vàảnh tiếng Việt/highlight. Cả132tests tập trung và503tests toànbackend đạt; không lỗi chặn, checkpoint đạt. Cổng04 vẫn chờ BW Otsu/Adaptive, dispatcher/xoay, demo/rà soát cuối giai đoạn.

**Bàn giao:** 26task chính +2AUX đạt;01.08 vẫn bỏqua,110IDgốc/5optional giữ. Tích MVP04.03 vàcheckpoint04-C1, MVP04.04 vẫnchưa làm. Cập nhật todo/plan/README/AGENTS/phạmvi/projectmap/imagecontract/progress; ảnh tổng hợp local ignored, không commit/push/deploy hoặc gửi ảnh ra ngoài. Tiếp theo MVP04.04 Otsu.

## 14/10/2026 — Hoàn thành MVP04.04: Otsu

**Phạm vi/lý thuyết:** user yêu cầu04.04 rồi04.05. Đọc checklist/phụ thuộc04.03 đã đạt, image-contract và đặc tả gốc9.14–9.15; giữ các điều chỉnh MVP. Dùng using-agent-skills, TDD/incremental-implementation/Ponytail, rà chất lượng; không thêm thư viện. Đối chiếu [OpenCV threshold/Otsu](https://docs.opencv.org/4.x/d7/d4d/tutorial_py_thresholding.html): tìm ngưỡng toàn cục từ histogram, tương đương tối đa hóa phương sai giữa hai lớp; THRESH_BINARY|THRESH_OTSU. Không coi threshold là thuật toán tìm biên trang hoặc tự nhận dạng chữ.

**Implementation:** enhancement.py thêm guard fullgray HxW uint8 dimensions2..2400 và apply_otsu(gray)→(bw,actual_threshold). Nhận gray đã lọc/contrast từ luồng04.02–03; không tự thêm Gaussian/Median/CLAHE, resize, đảo polarity hoặc fallback. Pixel≤t thành0, >t thành255; output độc lập/cùngsize/chỉ0/255. actual_threshold là float thực từ cv2.threshold, không lấy block/C hoặc hằng127; ảnhconstant có thể t0. Helper không có config vì Otsu không dùng tham số block/C; config đầy đủ vẫn parse ở caller, artifacts ghi actual_threshold cạnh effective_config. INVALID_RENDER/THRESHOLD_FAILED rõ, khôngHTTP/DB/I/O.

**TDD:** thêm test trước → RED import apply_otsu chưa có → **146passed in0.86s** =132cũ +14Otsu. Kiểm histogram bốn mức0/30/200/240→t30/BWđúngpolarity và replay gray>t; ảnhconstant0/100/255/min2×2 không bịa ngưỡng; readonly/strided/independent/writeable/contiguous và nguồn không đổi; invalidmàu/uint16/float/shape/range; lỗiCV rõ. Không gọi blur/equalizer lại. Cặp sángđều/bóng nhỏ có t30/t80 minh họa ngưỡngglobal làm nền tối đen.

**Nghiệm thu:** chạy `.tmp/mvp04_04_verify.py` bằng backend venv; tạo cùng nội dung tiếng Việt640×300 dưới sángđều/bóng gradient0.35→1.0. Config BW/Otsu đầy đủ, Median3/contrastNone; lưu source/gray/BW vàcomparison/metadata tại experiments/results/mvp04-04-otsu/ (ignored). Assertions source không đổi, outputshape/dtype/0–255 và replayngưỡng đúng. Số đo thật: t182 sángđều, t155 bóng; nềntrái(10,10) Otsu255 sángđều/0 bóng, nềnphải(620,10)255 ởcảhai. Đã xem ảnh: sángđều giữ chữ/dấu, bóngtrái thànhđen che nội dung. Đây là ảnh tổng hợp/hành vi, không accuracy hoặc đánh giá ảnhchụp thật. Đủ tiêu chí04.04 để chuyển04.05; toànbackend được chạy sau cảhaihelper ởmục dưới.

## 14/10/2026 — Hoàn thành MVP04.05: Adaptive Gaussian

**Implementation/lý thuyết:** apply_adaptive_gaussian(gray,ThresholdConfig) trong enhancement.py dùng ADAPTIVE_THRESH_GAUSSIAN_C/THRESH_BINARY; ngưỡng từngpixel là trung bình lân cận có trọng số Gaussian trừC, borderREPLICATE|ISOLATED theo [OpenCV API](https://docs.opencv.org/4.x/d7/d1b/group__imgproc__misc.html). Reuse fullgrayguard và ThresholdConfig; revalidate cảinstance/model_copy trướcCV. method phảiadaptive_gaussian, blocklẻ3..151≤cạnhngắn thật, Cnguyên−20..30. Quáblock báo INVALID_CONFIG, khôngclamp/tựfallbackOtsu; không thresholdmàu hoặc blurthêm. BWuint8 độc lập/cùngsize/chỉ0/255, khôngmutate source/config, không trả ngưỡngglobal giả; CVfailure THRESHOLD_FAILED. Dispatcher/rotation thuộc04.06.

**TDD:** RED import apply_adaptive_gaussian chưa có → **171passed in0.87s** =146cũ +25Adaptive. Patch3×3 kiểm Gaussianweightedmean85 thay vìmean117.8; center100 vớiC10 phải trắng. C−20/0/1/30 kiểm dấu trừ/equality/polarity; nét190 nền200 C5 giữ, C20 xóa vàsource nguyên. Spy chạyCVthật vớiblock31/51/151 vàC5, flags/arguments chính xác; readonlystrided, outputbounded/independent/binary/dtype/size/config. Oversize2×2/30×64/64×50 lỗi trướcCV; unsafe block/c/method/bool/string/float/range lỗi, grayscaleguard chạytrướcfit, CVfailure córeason rõ. Khôngskiptest.

**Nghiệm thu cùnggray:** `.tmp/mvp04_05_verify.py` đọc gray đãchuẩn bị04.04, không lọc lại. Lưu comparison sángđều/bóng (gray/Otsu/Adaptive31-C10), parameters block31/51×C5/10/20, PNG từngrun vàmetadata fullconfig/hash tại experiments/results/mvp04-05-adaptive/ (ignored). Đã xem trực tiếp: cảhai sángđều có nềntrắng/chữđen; ảnhbóng Adaptive31/C10 giữ nội dung ởphầnOtsulàmđen, dấu còn thấy. Pixelnền(10,10) ảnhbóng Otsu0/Adaptive255. So tham số thực: đổiblock31→51 ởC10 khác253pixel; đổiC5→20 block31 khác1338pixel; C20 làm đứt/mất nét nhạt ởdòngcuối. Không dùng counts làmaccuracy hoặc kết luận preset tốiưu.

**Ảnhnhỏ:** 8×8 cóink40/nền220: Adaptive31 báo INVALID_CONFIG, người dùngchọnAdaptive3 thì chạy; Otsu trả t40/BW. 2×2 vớiAdaptive3 vẫn báo INVALID_CONFIG vìkhông blockhợp lệ; không tự thay lựa chọn. Artifacts nhỏ vàreason thực ghi trongmetadata. Script đã ghi đủảnh/JSON và assertions nhưng lần inreason tiếngViệt ra consolecp1258 bị UnicodeEncodeError; dùng debugging workflow xácđịnh ở stdout, sửa JSONconsole sangASCIIescapes, đọc lại metadata/inra thànhcông; JSON trênđĩa vẫnUTF8. Không có lỗi thuật toán hoặc ảnhnguồn bị sửa.

**Hồi quy/rà soát:** toànbackend `backend/.venv/Scripts/python.exe -m pytest -c backend/pyproject.toml backend/tests` → **542passed in39.58s** =503cũ +14Otsu +25Adaptive. Auto-review cho phépTestClient/CLI ngoài sandbox, khôngdisablecheck. Ràcode/test: đúnggray→threshold/polarity/actualt, reuse CV/schema/grayguard, helpersngắn/fixedscope/noabstractionmới, shape/strict/bounded≤2400²/block≤151, nguồn/config bấtbiến vàerrorpaths rõ. Frontend/HTTP không đổi, không lặpbuild/browser. ChỉlõiBW đãcó; task04.06/service sẽchọnhelper/nối metadata/xoay.

**Bàn giao:** 28task chính +2AUX đạt;01.08 vẫn bỏqua,110IDgốc/5optional giữ. Tích04.04/04.05,04.06 chưa làm; checkpoint04-C1 đạt từmốc trước,04-C2/cổng04 cònchờ. Đồng bộtodo/plan/README/AGENTS/phạmvi/projectmap/imagecontract/progress; ảnhignored/cục bộ, không commit/push/deploy hoặc gửi ảnhra ngoài. Tiếp theo MVP04.06 dispatcher/xoay.

## 14/10/2026 — Hoàn thành MVP04.06: dispatcher và xoay

**Phạm vi:** user yêu cầu task 6, task 7 rồi rà cả 7 task giai đoạn 04. Đọc AGENTS/checklist/phụ thuộc và code thực; dùng using-agent-skills, incremental-implementation/TDD/Ponytail và review. Giữ scope post-warp, quy ước rotation theo chiều kim đồng hồ và source/corners sau EXIF; confirmed/revision thuộc service ở giai đoạn sau.

**Implementation:** enhancement.py thêm EnhancementResult frozen dataclass (image, effective_config, otsu_threshold) và enhance_document(warped_bgr, config, source_size=None). Revalidate toàn PageConfig với warp_size thực trước filter; source_size thực bắt buộc nếu corners khác null. Lọc → mode/contrast/threshold → xoay 0/90/180/270, dùng [OpenCV rotate](https://docs.opencv.org/4.x/d2/de8/group__core__array.html); 90/270 đổi W/H, không đổi corners hoặc áp EXIF lại. Inactive giữ trong config và được kiểm kiểu/miền nhưng không tham gia ảnh; Color không CLAHE/threshold, Gray không threshold. BW chọn đúng Otsu/Adaptive; ngưỡng Otsu thực hoặc null ở nhánh khác. Mỗi lần bắt đầu từ full warp nguyên, không lọc chồng lên render trước. Input/source/config bất biến, output uint8 độc lập/contiguous, lỗi thêm ROTATION_FAILED; không HTTP/DB/I/O/cache hoặc tự xác nhận góc.

**TDD:** thêm tests trước → RED thiếu enhance_document → **193 passed in 1.04s**, gồm 171 cũ và 22 dispatcher mới. Kiểm ba mode × bốn rotation trên mảng không đối xứng, chính xác theo np.rot90; corners/config và nguồn readonly không đổi. Có config trước filter/unsafe nested values/Adaptive fit với warp thực, source_size bắt buộc, inactive không chạy CV, thứ tự helper thật denoise→gray/CLAHE→threshold→rotate, Otsu t/null, đổi mode không tích lũy lọc và lỗi xoay.

**Nghiệm thu runtime:** chạy `.tmp/mvp04_06_verify.py` trên fixture corners_rgb96×64 → cùng warp95×63. Lưu 12 PNG full và metadata tại experiments/results/mvp04-06-rotations/, so equality từng pixel với rotation0 qua np.rot90; 90/270 thành63×95, config/corners/nguồn nguyên. Đã xem comparison trực tiếp và kiểm12hash/shape. Checkpoint04-C2 đạt sau các kiểm chứng Otsu/Adaptive/dispatcher; đầy đủ61cases mới của04.04–06.

## 14/10/2026 — Hoàn thành MVP04.07: so độ đọc ban đầu

**Implementation:** experiments/enhancement_demo.py chuẩn hóa raw JPEG/PNG theo15MiB/16MP/EXIF một lần, nhận quad normalized tay hoặc full ảnh mặc định, computeH/warp và gọi dispatcher bốn nhánh Color/Gray/BWAdaptive/BWOtsu cùngwarp. Preset đầy đủ; --rotation, --denoise override cảbốn, --no-gray-clahe để so. PNG full ColorRGB/Gray-BWL mới không EXIF, source/overlay/warp/comparison và metadata input/source/quad/H/effective_config/inactive/actualt/hash/dimensions. Comparison thu từfull maxedge800, không upscale; không lấy comparison làm render. Tất cả nhánh phải hợp lệ trướcghi, thưmụcmới/exclusive/metadata cuối. Config vẫn draft, không tự confirmed hoặc fallback/skipAdaptive trên ảnhnhỏ. Thêm test CLI vì đây là executable tạo evidence, không chỉ script minh họa chưa chạy.

**TDD:** 7 tests chạy subprocess CLI thật → RED thiếu script → **7 passed in13.19s**. Kiểm outputfull95×63/RGB-L/0–255/hash/bytes/fullconfig/inactive/t, source không đổi; quadtay sauEXIF64×96/rotation90 đổiW-H khôngđổi góc, overrideNone/CLAHEoff; invalidJSON/geometry/rotation, badimage, ảnh8×8 lỗiAdaptive, khôngghiđèthưmụccũ. Lệnh bằng Pythonvenv/pytest của repository; auto-review cho phép subprocess/temp cần thiết.

**Ảnh thực:** chạy CLI trên img_003 vàimg_004, cùngdoc_01 do user đãxácnhận; haiảnh đềudevelopment. Chọn quad thử tay gần đúng trên nguồn1536×2048 sauEXIF, giữ trongmetadata, chưaGT. img_003 shadow: [[.348,.260],[.806,.297],[.681,.919],[.116,.804]] →899×1288, Otsut147. img_004 nhãn even_light: [[.281,.316],[.728,.313],[.866,.904],[.139,.900]] →1116×1228, Otsut172. Ảnh nhãn even vẫn cógradient bênphải; Otsu làmđen vùng đó. Color/Gray giữ sắcđộ/nội dung, GrayCLAHE làmnổiôly/vânnền; Adaptive giữnhiềuchữ trongvùng Otsucheđen nhưngôlyvẫnđậm vàmộtsốnét/dấunhỏđứt. Giữ preset hiện hành, không gọi đây làđánhgiá nhiều tài liệu.

**So có kiểm soát:** chạy lại img_003/cùngquad với denoiseNone/GrayCLAHEoff, Otsuvẫnt147/vùngđen. Chạy synthetic tiếngViệt/highlight640×300 →warp639×299, Otsut214; Colorgiữvàng, BWmấtmàu, cónềnđen trênOtsu. SyntheticAa123/nét1pixel260×180 →259×179, Otsut209; Adaptive vẫn còn chữ/nét ởvídụ này, Otsumất/đứtphầnA. Warp nội suy làm thayđổi cấu trúc nét, không dùng vídụnày phủnhậntestMedian trực tiếp04.02. Các source synthetic là artifacts04.02/03 cục bộ, không tải ảnh ngoài.

**Xem/ghi nhận:** đã mở comparison của cả4nguồn và12rotation, overlay img_003; xem text_full_resolution.png của img_003/img_004 vàbảnNone, crop lấy từ fullrenderer giữnguyênpixel. Đầu ra tại mvp04-07-shadow/even/shadow-none/vietnamese-highlight/thin-strokes/; ghi đầyđủnguồn/quadtay/size/t/preset/ưu-nhược/giới hạn trong docs/algorithm-notes.md. Nhận xét không phảiOCR/accuracy hoặc khẳngđịnh mọi dấu đượcgiữ.

## 14/10/2026 — AUX04.01: rà đủ bảy task giai đoạn04

**Kết luận:** tạo docs/audit-phase-04.md với ma trận7task, nguồnđặc tả/MVP/hợpđồng/code/test/artifact. Đọc lại config/enhancement/CLI vàtests, kiểmthứtựlọc/mode/threshold/xoay, basicinactive/context/source_size/warpfit, polarity/copy/hash/PNGchannels/nooverwrite vàranhgiới offline. Không tìm thấy lỗi implementation mới chặn nghiệmthu; ghi rõ hạnchế Otsu/bóng, ôly/nét vàmộttàiliệu thật. Không sửa preset hoặc mởrộng sangillumination/dewarp/debug/UI.

**Hồi quy:** `backend/.venv/Scripts/python.exe -m pytest -c backend/pyproject.toml backend/tests` → **571 passed in52.53s** =193config/enhancement +7enhancementCLI +371cũ. Khôngskip/nới checks. Frontend/HTTP khôngđổi nênkhônglặpbuild/browser. Task6/7 TDD vàruntime đủ; cổng04/C1/C2 đạt theo phạmvi lõi/độđọc banđầu, khôngaccuracy hoặcMVPapphoànchỉnh.

**Bảo toàn/artifact QA:** kiểm40PNG trong5CLIrun bằnghash/bytes/dimensions/mode, BWchỉ0/255, ColorpresetNone bằngwarp. Kiểm12PNGrotation bằnghash/shape; tổng52PNGmetadata. Cáccropfullresolution bổsung dùngxem riêng. Sáucặp raw/normalized development giữhashCSV,22fixtures giữhash/bytecountmanifest. Ảnh thật/tổnghợp/results vàscripts .tmp đềuignored, khôngsửa input hoặcgửiảnhra ngoài.

**Bàn giao:** 30task chính +AUX02.01/AUX03.01/AUX04.01 đạt;01.08 vẫn bỏqua;110IDgốc/109cầnlàm/5optional giữ. Tích04.06/07/AUX04.01 vàcheckpoint04-C2/cổng04; nextMVP05.01analysis đểdetect. Đồng bộtodo/plan/README/AGENTS/phạmvi/projectmap/imagecontract/progress; thêmalgorithm-notes/audit04, khôngcommit/push/deploy. Service/confirmed-revision/UI/storage/nhiềutrang/PDF vàđánhgiá cuối chờtasktươngứng.

## 15/10/2026 — Hoàn thành MVP05.01: tạo ảnh phân tích

**Phạm vi/ngữ cảnh:** user yêu cầu task1–2 giai đoạn05 sau một lượt bị ngắt. Kiểm tra filesystem/git trước khi làm: chưa có detection.py/test_detection.py, không có phần code dở cần tiếp tục. Đọc AGENTS hiện hành, checklist/phụ thuộc03.04/02.05, audit04, image-contract và phân tích thuật toán mục5.1–5.5.3; đặc tả gốc9.2–9.5. Dùng using-agent-skills, incremental-implementation/TDD/Ponytail và review chất lượng; reuse resize và geometry thay vì tạo công thức mapping mới. OpenCV có sẵn thực hiện Gaussian/Canny/morphology, không thêm dependency.

**Implementation:** backend/app/processing/detection.py thêm prepare_analysis(source_bgr) và AnalysisImages frozen metadata. Nguồn BGR uint8 sau EXIF, mỗi chiều≥2 và≤16MP; resize_to_max_edge1200 dùng INTER_AREA/half-up, không upscale, rồi BGR2GRAY và Gaussian5×5/sigma0/BORDER_REFLECT_101. Trả stages bgr/gray/blurred riêng, uint8 độc lập; source không đổi. AnalysisImages có source_size=(W,H), analysis_size thực từshape và to_source(point), reuse pixel_to_normalized theo Wa−1/Ha−1 rồi normalized_to_pixel theo W−1/H−1, giữ subpixel/bounds. Nếu resize ra cạnh1pixel, báo ANALYSIS_TOO_SMALL trước mapping, không ép chiều2 làm thay aspect. Lỗi INVALID_SOURCE/TOO_MANY_PIXELS/ANALYSIS_FAILED rõ; không EXIF lại, CLAHE, filter render, I/O/HTTP/DB.

**TDD:** viết backend/tests/test_detection.py trước → RED thiếu module → một assert đối kháng ban đầu chọn trụcY vốn tình cờ khớp r trên kích thước này. Kiểm lại công thức, giữ expected mapping theoW−1/H−1 và sửa assert sang trụcX thực sự khác chia r; lỗi ở ví dụ test, không nới tolerance hoặc đổi implementation cho khớp. Kết quả **20passed in0.35s**. Các ca dọc/ngang/nguồn nhỏ/min2×2, nguồn readonly/strided, BGR weighting, Gaussian5 thật/sigma0/border, impulse255→36, độc lập stages/source, actual dimensions, endpoints/subpixel/bounds/NaN, shape/dtype/quota trướcresize, ảnh2×4800→analysis1×1200 bị chặn và CVfailure.

**Runtime:** nguồn development1536×2048 →900×1200; synthetic landscape2000×1001 →1200×601; synthetic nhỏ420×300 không upscale. Thử điểm(25%Wa−1,75%Ha−1) và góc phải dưới về đúng nguồn theo quy ước; sourcearray giữ nguyên. Đã lưu gray/blur/BGR và metadata chung với05.02 ởmục dưới. Task01 đạt trước khi nối Canny; ảnh analysis chỉ phục vụ detection, không thay nguồn warp/render.

## 15/10/2026 — Hoàn thành MVP05.02: Canny và closing

**Lý thuyết/implementation:** đối chiếu [OpenCV Canny](https://docs.opencv.org/4.x/da/d22/tutorial_py_canny.html), [morphology](https://docs.opencv.org/4.x/d9/d61/tutorial_py_morphological_ops.html) và [border mặc định](https://docs.opencv.org/4.x/d4/d86/group__imgproc__filter.html). create_edge_trials(blurred) nhận HxW gray uint8 mỗi chiều2..1200, không blur lại; chạy đúng3cặp50/150,75/200,100/250 với aperture3/L2gradient=true. Closing chữ nhật3×3 một iteration, BORDER_CONSTANT với giá trị morphology trung tính mặc địnhCV. Trả tuple EdgeTrial(trial_id,thresholds,edges,closed); ID canny_50_150/canny_75_200/canny_100_250. Edges raw vàclosed riêng, buffers độc lập/cùngsize/0–255, không mutate input. Closed dành cho contour, raw cho edge_support sau; số trial hữu hạn, chưa candidate/score/đề xuất/fallback. Input lỗi INVALID_ANALYSIS, CV lỗi EDGE_FAILED, không trả partial success.

**TDD:** thêm ca trước → RED thiếu create_edge_trials → **33passed in0.40s**, gồm20analysis +13edge. Spy chạyCV thật xác nhận đủba cặp/aperture/L2/kernelrect3/1iteration/border, không thêm Gaussian; ảnh rectangle kiểm white edge/black background, readonly-strided input nguyên và mọi buffer tách biệt. Edge map kiểm soát giữraw và lấp gap2pixel, để nguyên gap4pixel; minanalysis2×2 chạy đúng, input sai/cạnh>1200/lỗiCanny hoặcmorphology có reason. Testgap là kiểm closing trên mask đã biết, không giả làm nhận dạng giấy.

**Bằng chứng ảnh:** chạy `.tmp/mvp05_01_02_verify.py` trên4cases: synthetic_open_edge420×300, synthetic_landscape_texture2000×1001, developmentimg_003/img_0041536×2048 cùngdoc_01. Lưu11PNG/run (source/BGRanalysis/gray/blurred/3edges/3closed/comparison) vàmetadata size/mapping/preset/ID/hash/count tại experiments/results/mvp05-01-02/ (ignored). Xem cả4comparison: ngưỡng cao bớt cả chữ và vật nền, mép yếu có thể còn hở; closing làm dày cả ô ly/chữ/nền. Khung cóhở5pixel còn hở, closing thêm17pixel nhưng không khôi phục kín toàn biên. Không tăng kernel hoặc retry vô hạn để ép thành quad.

**Số đo thật:** img_003 rawedge9644/6431/3653pixel theo ba cặp, closing thêm2643/1016/185; img_004 raw16842/4315/2938, thêm8556/895/117. Synthetictexture raw9084 vàclosed15737 ởcảba. Đây là counts để mô tả hành vi, không accuracy hoặc đo hỗ trợ biên của một quad. Hai ảnh thật vẫn chỉ một tài liệu development; test0.

**Hồi quy/review:** toànbackend `backend/.venv/Scripts/python.exe -m pytest -c backend/pyproject.toml backend/tests` → **604passed in23.87s** =571cũ +33detection. Auto-review cho phép TestClient/CLI ngoài sandbox; khôngskip/disable/nới checks. Đọc lại source/tests: đúng source→analysis→gray/Gaussian→Canny→closing, bounds16MP/1200 và≥2, fixed3trials, metadata/arrays tách biệt, errorpaths rõ, reuse CV/resize/geometry/dataclass và không dependency mới. Frontend/HTTP không đổi, không lặpbuild/browser. Không chạy contour/scoring trước task tương ứng.

**QA/bàn giao:** kiểm44PNG/hash/shape/binary stages, source/blur nguyên; cả6cặp raw/normalized development giữhashCSV,22fixtures giữhash/bytesmanifest. Đồng bộ todo/plan/README/AGENTS/phạmvi/projectmap/imagecontract/algorithm-notes và trạng thái partialdetection của phân tích thuật toán. 32task chính +3AUX đạt; giữ110IDgốc/109cầnlàm/1skip/5optional. Tích05.01/02;05.03 chưa làm, checkpoint05-C1/cổng05 còn chờ. Ảnh/results/scripts.tmp ignored, khôngcommit/push/deploy hoặc gửi ảnh ra ngoài. Tiếp theo MVP05.03 sinh contour/Q, giữ nguyên raw edges để scoring05.04.

## 15/10/2026 — Hoàn thành MVP05.03: ứng viên contour/Q

**Ngữ cảnh/lý thuyết:** user yêu cầu task3–4 giai đoạn05. Dùng using-agent-skills, incremental implementation/TDD/Ponytail và review; đọc checklist/phụ thuộc, image-contract, algorithm-notes/audit04, phân tích mục5.5.1–5.5.3 và đặc tả ứng viên/scoring. Đối chiếu [OpenCV shape API](https://docs.opencv.org/4.x/d3/dc0/group__imgproc__shape.html) và [contour features](https://docs.opencv.org/4.x/dd/d49/tutorial_py_contour_features.html). Không tuyên bố đã đọc lại toàn bộ ba PDF ở lượt này. Tracing/approxPolyDP dùng OpenCV hiện có; code dự án kiểm giới hạn, geometry/provenance và score. Không thêm dependency, không gọi Douglas–Peucker là MPP.

**Implementation:** detection.py thêm ContourCandidate, CandidateBatch và generate_candidates(analysis,trial). findContours closed/RETR_LIST/CHAIN_APPROX_SIMPLE; xếp diện tích giảm dần/tie index, xét30 contour/trial. Contour area<.10WaHa hoặc perimeter≤0 lưu attempt loại trước approximation; còn lại thử3epsilon/P=.015/.02/.03, giữ contour có thứ tự/polygon gốc/số đỉnh/reason/trial/dimensions. Q đúng4đỉnh, đảo winding nếu cần nhưng kiểm validate_quad trước sorter; area Q≥.10WaHa, cạnh≥.05min(Wa,Ha). Không ép góc vuông/song song, minAreaRect hoặc sửa polygon tự giao bằng sắp lại. Canonical auto start dùng pixel nguồn thật, corners normalizedW−1/H−1; contour/Q px analysis. Không NMS/chọn đề xuất/confirm/I/O trong core.

**TDD:** RED thiếu generate_candidates→**48passed in0.49s**, gồm33cũ+15mới. Rectangle/diamond/skew qua thậtCV; baepsilon/chuvi, cap30largest, smallarea skipapprox, cạnh detector ngắn, Q tự giao/lõm/collinear/trùngđỉnh/3hoặc5đỉnh có mã loại và polygon nguyên. Các malformed Q được inject vào approximation để kiểm đúng gate, không giả là output của Canny. Test nguồn2000×1001→analysis1200×601 khóa canonical min(x+y) theo pixel nguồn khi hai trục làm tròn khác. Closed readonly không bị sửa, blank trả batch rỗng, binary map sai bị chặn.

**Runtime/C1:** `.tmp/mvp05_03_04_verify.py` chạy10cases×3trials. Rectangle/diamond/texture có ứng viên; lõm trả NON_CONVEX_QUAD, nét suy biến area quá nhỏ. Ảnh self-cross sau tracing/approx không đúng4đỉnh nên mã NOT_QUADRILATERAL; test Q bowtie kiểm riêng SELF_INTERSECTION. Khung hở5px không có quad vì contour bao nét hẹp. Có contour/Q overlay và lý do nhận/loại, source/analysis dims rõ. Xem tất cả comparison; checkpoint05-C1 đạt theo preprocessing/edge/contour và hình học, không phải detector đã chọn trang thành công trong mọi ca.

## 15/10/2026 — Hoàn thành MVP05.04: mô tả biên và heuristic score

**Implementation/đơn vị:** describe_candidate(candidate,trial) trả CandidateDescription có candidate/provenance, Pcontour px,4cạnh px/4góc đổi hướng rad, geometry flags và a/e/f/b/score. Revalidate quad, ID/thresholds/dimensions trial và contour hữu hạn/inbounds/area-perimeter>0; candidate bị loại hoặc sai trial báo lỗi trước chia. a=AQ/(WaHa), f=min(AC,AQ)/max(AC,AQ); geometry thành công xác lập lồi/không tự giao. Các độ dài trên analysis, không source/thumbnail; góc atan2(cross incoming/outgoing,dot) theo x phải/y xuống, cycle lồi dương.

**Sampling:** n=max(2,ceil(L/2)+1), linspace cảhai đầu mỗi cạnh, spacing≤2px; góc chung tính trên mỗi cạnh kề. Hỗ trợ nếu white raw Canny cùng trial cách Euclid≤2px; kiểm25tâm pixel lân cận kèm điều kiện khoảng cách thật, không dùng square-neighborhood/closed/dilation làm bằng chứng. Lưu sample/support counts và4tỷ lệ; e=sum(m)/sum(n), b=border_count/sum(n), sát mép khi min(x,y,Wa−1−x,Ha−1−y)≤2px. S=clip(.45a+.35e+.20f−.15b,0,1), không thêm trọng số hoặc gọi accuracy. Caller nội bộ chịu trách nhiệm đưa trial thực thuộc phép chạy; API/schema/provenance tổng hợp còn ở05.07/07.01.

**TDD:** RED thiếu describe_candidate→**64passed in0.78s**, thêm16ca. Rectangle chuẩn P560/cạnh160–120/gócπ/2/a.6/f1/e1/b0/S.82; mất cạnh dài có support4/61/81/61, e207/284 khác mean4, rawrỗng e0/S.47 dù closed đầy. Quad nghiêng/diamond có tổnggóc2π, values hữu hạn/ranges; oracle brute-force mọi whitepixel kiểm đúng Euclid≤2 trên cạnh nghiêng/map chỉ1pixel, không dựa trên cùng helper. Test fit khác1, frame penalty và hạn chế frame>paper; rejected/mismatchedtrial/dimensions/degenerate/NaN không được score. Khôngskip hoặc nới checks.

**Ảnh/số đo thực:** evidence chính experiments/results/mvp05-03-04-verified/ (ignored),10cases/30trials×11PNG +1controlled_supportcomparison =111PNG. Metadata giữ mọi attempt/descriptor/source hash/dims/trial/epsilon và số đo thật. Overlay contour xanh/Q đỏ, đánh số góc canonical; chỉ minh họa top3score mỗi trial, chưa NMS/đề xuất. Sửa riêng cách trình bày helper: nhãn bản nháp che vùng trên/dưới; bản verified đặt nhãn ngoài ảnh, không đổi thuật toán. So complete/missingtop/empty: e1/.728873/0, S.82/.725106/.47. Source arrays/edge maps readonly và equality sau chạy được kiểm.

**Development/giới hạn:** img_0031536×2048→900×1200 có108/54/19contour, xét30/30/19;6acceptedattempts/trial, ví dụ S.502372/a≈.312/e≈.474/f≈.982/b0. Overlay bám khá sát trang, mép hơi cong lệch Qthẳng khiến nhiều mẫu cáchrawedge>2px. img_004 có172/54/13contour, xét30/30/13,0accepted vì area<10%; contour mép chưa kín, giữ lỗi chứ không giảm gate để báo thành công. Cảhai cùngdoc_01/development, chưaGT/testđộc lập. Syntheticframe+paper chọn nhầm khung ở ví dụ score.975859, b0 vì cạnhkhung nằm ngoài dải2px. Không tune lại weights/radius hoặc gọi điểm cao là nhận đúng. Bảng đầy đủ/ảnh tại algorithm-notes; ca thuận lợi tổng hợp không chứng minh tổng quát.

**Hồi quy/review:** `backend/.venv/Scripts/python.exe -m pytest -c backend/pyproject.toml backend/tests` → **635passed in48.32s** =571cũ+64detection. Auto-review cho phép chạy TestClient/CLI; không lỗi bị che/skip. Đọc lại code/tests đối chiếu task03/04: topology trước sorter, source metric cho canonical start, bounded3×30×3attempts, không dùng closed để score, count-weighting/radius/border đúng, finite/quota và bảo toàn input. Không frontend/HTTP thay đổi nên không lặpbuild/browser. Dùng dataclass/NumPy/OpenCV hiện có, không thêm tầng trừu tượng hoặc thực hiện sớm05.05–08.

**QA/bàn giao:** `.tmp/mvp05_03_04_qa.py` kiểm111PNG/hash/shape/binary levels,108descriptors hợp lệ khớp dimensions/trial/counts/góc/score;6cặp raw/normalized development và22fixtures giữ hash/bytecount. Rà10tài liệu/77liên kết nội bộ và checklist:34task chính +3AUX đạt,110IDgốc/109cầnlàm/1skip/5optional giữ. Tích05.03/04 và checkpoint05-C1;05-C2/cổng05 chờ. Đồng bộ README/AGENTS/todo/plan/phạmvi/project-map/image-contract/phân tích/algorithm-notes/progress. Dữ liệu/results/scripts.tmp ignored, khôngcommit/push/deploy hoặc gửi ảnh ra ngoài. NextMVP05.05 IoU/NMS, sauđó05.06 proposal/fallback.

## 15/10/2026 — Chạy anhtestnew.jpg, không thay thuật toán

User bổ sung ảnh và yêu cầu chạy thử. Tìm thấy experiments/data/anhtestnew.jpg,4809bytes; normalize sauEXIF612×460, analysis giữ612×460. `.tmp/verify_anhtestnew.py` chạy prepare_analysis/create_edge_trials/generate_candidates/describe_candidate với preset hiện hành, không tune/fallback/góc tay. Cả3cặp Canny có1contour/trial,0quad; contour area ratios≈.00482737/.00365338/.00000710429, đều dưới.10, bị CONTOUR_AREA_TOO_SMALL trước approximation/score. Không gọi score0 hoặc lỗi decoder; ảnh đọc được, thuật toán phát hiện chưa tạo được ứng viên.

Xem source/comparison/raw50/150/closed: mép phải gần như mất, contour chạy quanh nét mỏng, không bao vùng trang; closing3×3 không nối khoảng thiếu dài. Lưu14PNG vàmetadata hash/dims/params/attempts tại experiments/results/anhtestnew-mvp05-03-04/ (ignored). Đọc lại các PNG và so pixel, kiểm nguồn array/raw bytes không đổi. Source chuẩn hóa ghi đúng encode_normalized_png payload/hash. Không sửa code ứng dụng nên không lặp fullsuite635tests; đây là chạy runtime bổ sung. Ghi nhận trong algorithm-notes, không tích task mới hoặc thêm manifest khi chưa biết document_id/split. Ảnh và kết quả giữ cục bộ, không commit/push/gửi dịch vụ ngoài.

## 15/10/2026 — AUX05.01: điều chỉnh hướng và code sinh ứng viên

**Ủy quyền/phạm vi:** user chấp nhận cập nhật hướng thuật toán/tài liệu và sửa theo đề xuất sau img_004/anhtestnew thất bại. Dùng using-agent-skills, incremental implementation/TDD/Ponytail, source-driven và review. Đọc AGENTS, task05.01–08, hướng mục5.1–5.5.3/7, image-contract và source/tests/callers; đối chiếu OpenCV thresholding/shape/filter API. Không đọc lại toàn bộ ba PDF ở lượt này. Tạo [revision01](detection-revision-01.md) làm quyết định/evidence, sửa các tài liệu MVP hiện hành; hai đặc tả gốc và PDF giữ tham chiếu lịch sử.

**Khảo sát trước khi đổi preset:** `.tmp/explore_detection_revision.py`,16ca×12biến thể =192overlay: Gaussian3/5 × (5cặp Canny50/150,75/200,100/250,20/60,10/30 +Otsu vùng sáng). Thử trên6ảnh development cùngdoc_01, anhtestnew chưaidentity/split và9ca tổng hợp; không dùng test độc lập hoặc gán GT giả. So source/overlay: Gaussian3 không tốt hơn đều,10/30 sinh vùng ăn bàn. ChọnGaussian5/default, revised20/60,50/150,75/200; baseline cũ giữ riêng. Otsu tạo candidate nhưng có thể gộp bàn sáng; chưa chỉnh trọng số/score để ép thành công. Các masks/contours khảo sát chạyCV+geometry có sẵn, chỉ là prototype đếmquad, không coi là runtime core mới cho đến phép chạy actualCLI bên dưới.

**Increment1/TDD:** thêm14tests kernel/preset trước→RED thiếu kwargs. prepare_analysis cho int3/5, giữdefault5/sigma0/reflect101, AnalysisImages ghi kernel. create_edge_trials có preset baseline/revised hữu hạn3cặp; defaultbaseline để tái hiện, metadata kernel và IDg3 phân biệtblur. RED→**78passed** gồm64cũ+14mới. Không nới sourcequota/analysisdims, không thay normalization/warp/render hoặc thêm dependency.

**Increment2/TDD:** thêm16tests trước→RED thiếuRegionTrial/helpers; triển khai create_region_trial và collect_candidates. Entry collect defaultrevised, trả tuple TrialCandidates(trial,batch):3Canny, nếu cả3khôngquad thì thêm tối đa1Otsu/RETR_EXTERNAL. RegionTrial mask/actualt/supportID/cặp ngưỡng support/kernel, raw Canny copy cùnganalysis; mask không làm e. Truy outer components bỏ lỗ nội bộ mà khôngfillmask; uniform0/255 gate trướccontour, reason UNIFORM_REGION_MASK. Candidate ghi method/kernel/otsu_threshold vàdescribe kiểm khớp; giữtop30/3epsilon/10%/5%/geometry/source metric/score. **94passed in0.83s**: ảnh tương phản thấp phục hồi, vùng córawedge0 vẫn e0/score thấp, uniformmask thật không giảpage, holes/independence/mismatch/NaN/binary/CVfailure có kiểm. Không NMS/proposal/confirmed/timing API.

**Increment3/CLI:** tests trước→RED thiếu compare_detection.py; thêm CLI so một input, baselineGaussian5 vàrevised5hoặc3ablation. **5passed in5.08s**, gồm2ảnh tổng hợp weakedge/region, EXIF/kernel/hash/dim/channels/no-overwrite/badimage. CLI đọc raw cóquota, normalizePNG đúngpayload, lưu gray/blur/raw/closed hoặcmask/contour-Q/metadata đủaccepted-rejected/descriptors vào thưmụcmới, metadata cuối. Ví dụ chọn theo heuristic chưaNMS, khôngtựconfirm/warp. Script thử importmain banđầu vướng stdoutcp1258 sau khi ghi runđầu; sửa helper stdoutUTF8 và chạy vào thưmụcverified mới. Không lỗi core bị bỏqua; bảnverified là evidence chính.

**Runtime actualcore:** `.tmp/run_detection_revision.py` gọi compare_detection.main trên16ca,104trial,440PNG/272descriptors tại experiments/results/detection-revision-01-verified/. Xem đủ16comparison, anhtestnew0→6acceptedattempts, ví dụ CannyS.634709/e.989837/a.203138/f.984269 bám sát giấy. img_002/003/005 giữ nguyên quad/score .525122/.502372/.501182, count giảmở003/005 do bỏtrialtrùng. img_001 vẫn0; img_004/img_006 Otsucandidate1mỗiảnh nhưng ăn bàn ở góctrêntrái,S.468352/.448517. Candidate count không phải success/accuracy; frame vẫn chọn nhầmS.975859, nét hở lớn khôngquad, constantbịuniformgate. Dataset/nhãn khôngđổi, anhtestnew chưa vào manifest.

**Hồi quy/review:** toànbackend `backend/.venv/Scripts/python.exe -m pytest -c backend/pyproject.toml backend/tests` → **670passed in20.17s** =635cũ+30revision+5CLI. Khôngskip/nới checks; TestClient/CLI được auto-review cho chạy. Review source/tests: bounded3+1, defaultbaseline/revised rõ, cùngkernel/dimensions/provenance, gate topology trướcsorter, uniformmask thật, e từraw20/60, ratios/scorefinite, sourceđộc lập; khôngthêm abstraction/dependency hoặc chạmHTTP/DB/UI. Sau suite chỉ sửa docstrings/thông báo từclosed thànhcontourmap, không logic. Frontend không đổi nên không lặpbuild/browser.

**Bàn giao:** cập nhật hướng5/7, hợpđồngảnh, MVP, README, AGENTS, project-map, todo/plan, algorithm-notes vàreportrevision01. Giữ110IDchính/109cầnlàm/1skip/5optional;34main+4AUX đạt, phần a/b/c không cộng taskcha thêm. Task05.05–08/cổng05/05-C2 vẫnchờ;05.05 cần lấy collect_candidates revised vàgiữmethod/kernel/actualt/rawsupport. Khôngcommit/push/deploy hoặc gửiảnhra ngoài; scripts/results/dữ liệu cục bộignored. QA PNG/hash/source/dataset/fixtures/link/checklist được ghi tiếp sau kiểm tra cuối.

**QA cuối:** `.tmp/qa_detection_revision.py` đạt16runs/104trials/440PNG/272descriptors,8regiontrials. Kiểm hash/bytes/dimensions/mode/EXIF/binary, geometry/source-analysis mapping, method/kernel/t/cặp ngưỡng, e counts/score và điều kiện region chỉ khi khôngquad Canny.64map raw/closed của50/150–75/200 giữa baseline/revised có cùnghash.6cặp raw/normalized development và22fixtures giữhash/bytecount;sourcePNG CLI đúngnormalizedhashCSV. Input anhtestnew vẫn đúnghashđầuvào. Rà11tài liệu/90linknộibộ vàchecklist34main/4AUX/110ID,05.05–08 vẫnunchecked. Gitignore giữ ảnh/results/scripts.tmp ngoàiGit,4tệpcode/test mới-sửa khôngbịignore. Saukiểm chỉchỉnh whitespace/comment/error wording vànhật ký, khôngthaylogic/preset.

## 15/10/2026 — Dò giáo trình/slide để kiểm chứng nguyên nhân img_004

User hỏi nguyên nhân và yêu cầu kiểm tra thuật toán với PDF. Dùng using-agent-skills, PDF và debugging; chỉ chẩn đoán/ghi tài liệu, không sửa thêm core/preset. Fresh pypdf extraction cả3PDF để tìm mục, lưuhash vàtext theo trang; đọc kỹ giáo trình111–119/163–164, slide5 trang5–6/31–32/35–40, slide6 trang9/12/17–19/24/36. Poppler render/xem9trang đầyđủ: sách114/118/119, slide5 35/37/40, slide6 17/19/36. Không coi trích text toànPDF là đọc kỹ toàn308+60+63trang. PDFgiữnguyên.

Đọc tiếp đầy đủ trang120 để đối chiếu các bước còn lại của region-growing cóseed. QA cuối:3PDF giữSHA-256 như lúc extraction,9trangrender và2PNGdiagnostic kiểmhash/dimensions;4tài liệu/24linknộibộ hợp lệ. Không đổi preset/core hoặc taskcounts.

`.tmp/diagnose_img004.py` tái hiện core từrawsource/hashCSV, analysis900×1200, baCanny khôngquad và1RegionTrial. Tính độc lập bằngNumPy các công thứcOtsu(5-62)–(5-64), khôngcv.threshold cho reference: cựcđại duy nhất102, rawmaskmanual khớp từngpixel vớicore/maskđãlưu. Grayblur bànA(200,340)=109, giấyB(400,650)=186, cảhai255/label26 theo8-connectivity. Componentnày cònchạmx0; leakđãởmask trướcgeometry. Ngưỡngglobal chia sáng/tối chứkhônggánnhãn bàn/giấy, phùhợp giới hạn vềchiếusáng/histogram ởsách112–114 vàslide5 32/35/37.

Phát hiện yếuđiểm thứhai: contourP5417.48px, .015P/.020P/.030P cho13/10/4đỉnh; epsilon3%=162.52px, maxdistancecontour→cạnhQ gầnnhất160.76px. Q lồi/simple qua geometry nhưng vẫnbao bàn; tolerance theoP răngcưa đangcho simplification rấtthô. Slide6 17–19 cảnhbáo tolerance lớn mấtchitiết, chỉ xấpxỉ biênđầuvào; sách163–164 làMPP, codeDouglas–Peucker khôngphảiMPP. Code threshold+RETR_EXTERNAL khônglàregion-growing cóseed ởsách119/slide5 40. Cạnhtrên7/245rawsupport=2.86%, e.304282/f.930180/a.390704/b0/S.468352; bộmôtảphảnánhbiênyếu nhưngf diện tích/b trênQ chưađủ từchối vùngsai. Đây là giới hạn thiết kế/ápdụng, khôngquan sátthấy lỗi côngthứcOtsu/mapping/winding trênca này.

Tạo docs/verification-img004-theory.md, bổ sung link/kếtluận ở phân tích vàalgorithm-notes. Evidence2PNG+metadata tại experiments/results/img004-theory-verification/ gồmprobe/maskcomponent/contourQ vàphéptínhđộlệch, đọc/xemdiagnostic. Assertions Otsu/mask/trial/probes/source nguyên đạt; khônglặpfullsuite670vìkhôngđổi code. Giữ34main/4AUX/110ID vàtask05.05–08chờ; đềxuất nghiêncứuphântách màu/chiếusáng vàgiớihạnsaisốxấpxỉ chưađược triểnkhai ởlượtchẩnđoán này. Ảnh/results/scriptsignored, khônggửira ngoài/commit/push.
## 15/10/2026 — MVP05.05–06: polygon NMS và đề xuất/fallback

**Phạm vi:** user đồng ý tiếp tục hai task sau trao đổi về giới hạn img_004. Đọc task/phụ thuộc05.04/AUX05.01, hướng5.5.1–3, image-contract, source/callers/tests và chẩn đoán PDF trước đó; không đọc lại toànPDF ở lượt này. Dùng using-agent-skills → incremental implementation/TDD/Ponytail → review. Giữ Gaussian5/revised, điều kiện region, các gate sinh quad, epsilon và score; không tự thêm ngưỡng hỗ trợ từng cạnh hoặc tuyên bố sửa phân vùng.

**Task05.05:** thêm polygon_metrics.polygon_iou trên quad normalized/cùng dimensions, validate_quad trước CV intersectConvexConvex(handleNested=true). IoU diện tích liên tục, không bbox/raster. TDD RED thiếu helper → GREEN17tests; NMS RED thiếu helper → GREEN phần14tests cùng94detection/17metrics. deduplicate_candidates sort S giảm dần, tie input order; greedy chỉ so survivors, IoU>.95 mới loại, .95 vẫn giữ. Không trộn method/kernel/Otsu t/e của trial khác. Candidate thêm support_trial_id region để raw origin theo đúng description được giữ; Canny null vì origin=trial_id; generate ghi và describe so khớp.

**Task05.06:** tests trước RED thiếu select_proposal/detect_document, rồi nối prepare_analysis→collect_candidates revised→describe→NMS→proposal. DetectionResult frozen có status/corners/heuristic_score/warnings/selected/candidates và confirmed=false không nhận init override. S≥.60 proposed; .40≤S<.60 proposed_with_warning; thấp hơn manual_required/corners=null, selected chỉ làm chẩn đoán. Khôngquad corners/score/selected=null, warning NO_VALID_QUAD; score thấp warning LOW_HEURISTIC_SCORE. Không dựng góc inset/full giả, không warp hoặc thay config/source. Input/CV lỗi vẫn báo lỗi riêng. Test sát dưới và đúng.40/.60, source readonly, blank/open edge/rectangle và region thiếu raw support.

**Review số học:** thử100quad nghiêng/subpixel cùng chính nó có53ca IoU hơi nhỏ hơn1 do float32 CV (đây là probe số học, không phải accuracy). Đưa một ca vào test tái hiện RED IoU=.999999958587. Kiểm hai cycle cùng tọa độ float64 trước CV, trả1 chính xác; các giao khác vẫn CV float32 với giới hạn intersection≤min(areas), finite/positive checks. Nested/partial/touching/disjoint/skew/subpixel, NMS stable ties/greedy nontransitive/provenance/error đều có kiểm. Tổng mới18metrics+28selection=46tests; không thêm dependency/abstraction. Caller phải giữ cùng nguồn/run, dimensions không chứng nhận danh tính ảnh.

**Bằng chứng runtime:** `.tmp/verify_mvp05_05_06.py` chạy entry thực và đối chiếu select_proposal từ collector thật, nguồn readonly/giữ pixel/hash; ghi7overlay/metadata/summary tại experiments/results/mvp05-05-06-verified/ (ignored), đã xem cả7ảnh. img_0010→0/manual/null; img_00312→1/cảnh báo S=.5023719825; img_0041→1/cảnh báo S=.4683515931 vẫn ăn bàn; anhtestnew6→1/proposed S=.6347091154; rectangle18→1/proposed S=.8078090941; frame36→2/proposed S=.9799005088 **chọn sai khung**; blank0→0/manual/null. Mọi result confirmed=false. Metadata giữ dims/hash/selected/candidates/provenance/counts thật; overlay không vẽ quad giả khi manual. Bảng/giới hạn tại algorithm-notes, không gọi số proposal là accuracy. Dataset6ảnh/1doc_01/test0 giữ; ảnh bổ sung chưaidentity/split. Đây là kiểm chứng tập trung hai task, chưa batch/timing của05.07–08.

**Hồi quy/checkpoint:** 140tests tập trung đạt1.07s; fullbackend **716passed in56.94s** =670cũ+46mới. Lượt full đầu trong sandbox xuất hiện errors ở các fixture CLI và dừng ở TestClient; đã dừng và chạy cùng suite với quyền cho môi trường TestClient/temp/subprocess, không sửa/skip tests để né lỗi. Suite716 đạt57.20s trước review số học và56.94s sau sửa cuối. Review source/tests/callers: source mapping/order giữ, NMS score/provenance không thay, manual có null rõ, errors không giả failure bình thường; không HTTP/DB/UI hoặc source render từ analysis. Frontend không đổi nên không lặp build/browser.

**Bàn giao:** tích MVP05.05/06 và checkpoint05-C2 sau evidence;36task chính+4AUX,110IDgốc/109active/1skip/5optional giữ. Cổng05 chờ05.07 timing/debug và05.08 development. Đồng bộ README/AGENTS/checklist/plan/phạmvi/project-map/image-contract/hướng/algorithm-notes/progress. Dữ liệu, kết quả và script.tmp giữ ngoàiGit; không commit/push/deploy hoặc gửi ảnh ra ngoài. Các cải thiện segmentation/epsilon/side-warning vẫn cần đối chứng development trước đóng cổng05; chưa được coi là đã thực hiện.

**QA cuối:** `.tmp/qa_mvp05_05_06.py` kiểm7runs/7PNG/hash/dimensions/metadata và6survivors; source/analysis mapping, raw support origin/counts/score/status/confirmed khớp. Cả6cặp raw/normalized development và22fixtures giữbytecount/hash;11tài liệu/93link nội bộ hợp lệ. Checklist36main/4AUX/110ID,05.07–08 vẫnunchecked. git check-ignore xác nhận ảnh/kết quả/scripts.tmp ngoàiGit và4tệp source/test hiện hành khôngbịignore. Không đổi code sau suite716 cuối; chỉ tài liệu/QA.

## 15/10/2026 — MVP05.07–08 và AUX05.02: debug, development batch, rà tám task

**Phạm vi:** user yêu cầu hai task cuối và rà giai đoạn, đặc biệt nêu hướng giải quyết nợ task03–04. Dùng using-agent-skills, incremental implementation/TDD/Ponytail, observability và review. Đọc checklist/phụ thuộc/hợp đồng/hướng5.5.1–3, source/tests/callers, audit04 và chẩn đoán img_004 đã đối chiếu baPDF; không đọc lại toànPDF ở lượt này. Đối chiếu thêm tài liệu OpenCV contour approximation/thresholding. Không tự thay ngưỡng/scoring/phân vùng theo hướng được đề xuất.

**Increment task07:** viết9tests trước → RED thiếu debug/preset/perf_counter_ns. Thêm DetectionTimings, DetectionDebug, optional fields của DetectionResult và detect_document(debug=False,preset='revised'); default vẫn Gaussian5/revised. Debug opt-in giữ nguồn BGR hash C-order (khácPNGhash), analysis/trials/selected_trial thực/overlay vàkind proposal/diagnostic/none. Noquad giữoverlay khôngquadgiả; low-score best chỉdiagnostic, result.corners=null. CV overlay lỗi DEBUG_FAILED, không che thành manual. perf_counter_ns đo preprocess/candidates/describe/select/debug/total, các khoảng liền nhau; candidates gộp Canny/closing/contours/region, select gồmNMS. Không decode/encode/I/O trongcore. GREEN149tests tập trung; thêmca CVerror thành10debug/150focused đạt1.94s. Không source mutation hoặc stage arrays trong result mặc định.

**Increment task08:** 7CLItests trước → RED thiếu detect_batch.py, sauđó GREEN7passed10.37s. CLI kiểm manifest, bỏtest trướcđọcảnh, development baseline/revised cùngnguồn; --input bổsung giữidentity/splitunassigned. Verifyraw/normalizedhash, sourcePNG đúngpayload vàEXIF, outputmới/khôngghiđè. Mỗi profile ghi actualstages/config/units/hash/selected/trials/attempts/survivors/timing; source/comparison/CSV/summary ởcase/batch. Error.json vàsummary.errors/exit1 khiảnhlỗi, tiếpảnhkhác; summary làkếtthúcbatch chứkhôngmọiảnhthànhcông. Tests gồm raw/normalized mismatch, ảnhhỏng, EXIF vàtestpathkhôngtồntại. Reviewgiảmmetadata duplicatebatch ởselected_trial vàbắtIOerror outer; fullsuite sauđó kiểm phiênbảncuối.

**Runtime thực:** `.tmp/run_mvp05_07_08.py` gọi CLI hiệnhành,16ca gồm6development cùngdoc_01, anhtestnew chưaidentity và9synthetic;32profile/104trial/8region/368PNG tại experiments/results/mvp05-07-08-verified/ (ignored). Xemđủ16comparison vàraw/mask/overlay quantrọng. Baseline9manual/3warning/4proposed, revised6manual/5warning/5proposed; khônggọi counts/status làaccuracy. img_002/003/005 giữquadS.525122/.502372/.501182; img_004/006 revised cóquad nhưngănbàn/warningS.468352/.448517; img_001manual; anhtestnewproposedS.634709; framevẫnsaiS.975859. Rectangle/diamond/texturebámtrang, lõm/tựcắt/suybiến/hở/constantmanual. Timingcore mộtlượt2.072–218.8952ms, khôngbenchmark/sohiệunăng vìkhôngwarm/repeats vàpresetchạytheothứtự.

**Fallback tay:** chạy enhancement_demo từJPEGgốc img_001 với quadnormalized draft doagent chọnthử [[.32,.25],[.82,.265],[.75,.89],[.14,.81]], denoiseNone. Tạo951×1284warp +Color/Gray/Adaptive/Otsu/overlay/source/comparison tổng8PNG tại mvp05-08-manual-img001/. Color=warp đúnghash/pixel; effectiveconfigs confirmed=false. Đãxemcomparison/warp; cònmépbàn/phầngấp, BWmấtôly/đứtnét/đenbóng. KhôngGT/userconfirmed/dewarp hoặcUItay; chỉchứngminh detectorfailure khôngchặn lõixửlýtaycósẵn. Khôngthựchiệnsớm pipeline06/API/UI.

**QA runtime:** `.tmp/qa_phase05_evidence.py` đọc lạiPNG/hash/bytes/dimensions/mode/EXIF; tínhlạigray/Gaussian/Canny/closing/Otsu từstagesđãlưu, replaydescribe cho19NMSsurvivors từraw/geometry thực vàđốichiếutoànmetadata. Status/score/NMS/provenance/counts/sourcehash/timing khớp; regionchỉkhiCanny khôngquad; nguồn6cặp/22fixtures khôngđổi. Metadata audit-evidence.json lưusốđo đỉnhcontour→Q, khônglàHausdorff/GTerror hoặcdescriptorproductionmới.

**Nợ03–04/AUX05.02:** audit-phase-05.md cómatrận8task, bằngchứng vàhướnggiải. img_004/006 epsilon162.52/189.46px, maxdistance160.76/143.62px (=.10727/.09583D), minside support.02857/.07394 dùfareacao. Hướngthửnhỏ: capepsilon theoD hoặcfitdistancegate, cảnhbáocạnhyếu trướcthayweights; màu/chiếusáng chonhánhOtsu sauđốichứng. Frame cóe_min1 vàdistance1px nên haihướngđó khôngchữađược chọnnhầmkhung; cầnđánhgiácảnhmơhồ/vùnglồngnhau vàgiữmanualconfirmation. Khôngchốt ngưỡng từ6ảnh/1doc, cầnthêmdevelopment/GT, đổi1biến/lượt vàkhóatrướctest. Chỉđo/nêuhướng, khôngcoi debtđãtrả.

**Hồi quy/bàn giao:** fullbackend **733passed in47.01s** =716cũ+10debug+7batchCLI, khôngskip/nớicheck; chạyquyềnchomôitrườngTestClient/temp/subprocess, khôngcóapprovalrejection. Reviewtheođặctả/ranhgiớimôđun/độphứctạp/bảotoànnguồn/provenance/errorpaths; khôngdependency mới. Frontendkhôngđổi nênkhônglặpbuild/browser. Tích05.07/08 vàAUX05.02;38main+5AUX/110IDgốc, cổng05đạt ởmứcMVP vàfailurecatalog, khôngđảmbảomọicảnhđúng/đượccảnhbáo. Next06.01. Đồngbộ README/AGENTS/plan/todo/phạmvi/project-map/hợpđồng/hướng/notes/audit/progress; dữliệu/results/.tmpignored, khôngcommit/push/deploy hoặcgửiảnhra ngoài.

**QA cuối tài liệu:** `.tmp/qa_phase05_docs.py` đạt12tài liệu/100link nội bộ;38main/5AUX/110ID, đủ8task05 đãtích,06.01 vẫnchờ. git check-ignore xác nhận dữliệu/kếtquả/scripts.tmp ngoàiGit;4tệpcode/tests mới-sửa vàaudit khôngbịignore. Không sửa code sau full733; chỉ cập nhật tài liệu và scriptQA. Báo cáo audit-phase-05 được yêu cầu mở trongCodex (tool trảqueued), không coi queued làđãhiện trênmànhình.

## 15/10/2026 — MVP06.01–03: pipeline offline, full/preview và snapshot/stages

**Phạm vi:** user yêu cầu task1–3 giai đoạn06. Đọc using-agent-skills, checklist/phụ thuộc05.07/04.06, hợp đồng ảnh/config/geometry/preview, audit05 và code/tests/callers. Dùng workflow incremental implementation/TDD/API-interface/Ponytail/observability/review đã áp dụng trong phiên. Không sửa detector theo nợ thuật toán; không triển khai histogram06.04, nghiệm thu tái lập06.05 hoặc mốc06.06. Task03 chia a/b để mỗi phần≤5tệp, không tăng số task chính.

**Task01/core:** tests trước RED thiếu render.py → render_document: validate source/config, dùng corners tay giữ thứ tự và bỏ detector, hoặc nhận result.corners của detector revised; không lấy góc diagnostic dưới.40 để warp. Noquad trả manual_required, warp/enhancement/H=null. Cógóc thì warp từsource đầy đủ→enhance→rotate, config không tự confirmed. Explicit confirmed của config được giữ khi không đổi góc, gating UI/revision ở service sau. Trả H/effectiveconfig/origin/detection và timing thực validate/detect/warp/enhance/total. Case analysis có cạnh1 chuyển thành manual với warning ANALYSIS_TOO_SMALL; không bắt lỗi CV/input khác để giả thất bại bình thường. Mẫu test ban đầu40000×2 đúng ra không vượt source quad short-edge gate; đổi fixture thành40000×42 để kiểm đúng ca source quad hợp lệ nhưng analysis cao1, giữ nguyên geometry gate. Core19tests đạt; review thêm quota16MP và khôngwarp từ diagnostic, thành21coretests.

**Task02/encoder:** 9tests RED thiếu helper → encode_render_images/EncodedRaster/RenderImages. PNG RGB/L sạchEXIF/ICC, hash đúngpayload; fullgray/BGRuint8 mỗi chiều2..2400, preview lấy từfull saurotation qua INTER_AREA/half-up/max1000/khôngupscale. BWpreview cógray, khôngthresholdlại; ảnh2×2400 chopreview1×1000 hợp lệ. Lỗi ENCODE_FAILED/INVALID_RENDER rõ; khôngáp15MiB upload choPNG nội bộ. Encoder9 +core21 thành30tests render; Colorchannel/readonly, checkerboard full-source vsanalysis vàBWpreview đượckiểm.

**Task03a/stages:** 6tests trước RED thiếudebug, mởrộng enhance_document(debug=False) giữdefaultcũ; EnhancementResult.stages optional chứa filtered_bgr/prepared_gray/before_rotation từdispatcher thật, khôngreplay filters. Color prepared_gray=null; BW prepared_gray chínhlàinputthreshold sau denoise/contrast. Config/stage/source/pixels khi bật/tắtdebug giữ; mỗi filter chỉ chạy một lần. Nối render_document truyền debug. Focused36tests core/encoder/stages đạt0.78s; hồi quy enhancement cũ cũng đã chạy trong increment trước và fullsuite.

**Task01/03b CLI:** 7tests trước RED thiếu scan_one.py → CLI normalizeJPEG/PNG mộtlần, PageConfig qua--mode hoặc--config, góctay--corners ghiđè/chuyểndraft vàparse lại. Auto có thể tạo bản nháp từproposal/warning, không tựconfirmed; manual_required lưusource/config/debug/metadata, khôngfullgiả, exit2. Exit0 khi rendered,1 choảnh/config/I/Olỗi; outputmới/khôngghiđè, metadata cuối. Ghi sourcePNG đúngencode_normalized_png payload; sourceoverlay/H, render/warp/filtered/preparedgray/before_rotation/full/preview, config.json vàmetadata raw/PNG/BGRhash/dims/units/requested-effective/inactive/Otsut/timing/version/dependencies. Snapshot cócorners điđườngmanual khi chạy lại, không giảdetection giốngrun đầu.

**Writer dùng chung/review:** tách writer từdetect_batch sang detection_artifacts.py, nhận actualDetectionResult thay vì rerun detector; batch vàscan dùngcùng PNG/JSON/debugschema. Lỗi tên hàm khi tách (writewrite_json) bị7batchtests bắt, sửa và7đạt11.21s; không bỏ tests. TDD bổ sung phát hiện detectionmetadata củascan bịghi entry_point=detect_batch; writer nhận entry_point tườngminh, batch/scan truyềnđúng cùngrun_id. FocusedhaiCLI14đạt28.06s trước thêmcaCLIAdaptive-invalid; fullsuite cuối có8scan+7batch. Không tạo framework/storagecache/dependency mới.

**Runtime:** `.tmp/run_mvp06_01_03.py`,7runs tại experiments/results/mvp06-01-03-verified/ (ignored), từ4ảnhthật +1synthetic. anhtestnewColorauto201×285; img_003Grayauto898×1288→preview697×1000 cówarning/bóng/ôly; img_004BWOtsuauto1112×1358→819×1000 vẫnănbàn/đenbàn, giữwarning. img_001auto manual_required/khôngfull; manualdraftGray951×1284→741×1000 bằngquadagent chọnthử từmốc05, khôngGT/userconfirmed. CheckerboardBW90 full1300×2000→650×1000, fullbinary/previewgray; snapshotmanualGrayimg_001 táichạy giữhashfull/preview/stages. Tấtcảruntimeconfigs confirmed=false. Đãxem4kếtquả/preview thật, syntheticpixel assertions vàfailuremetadata; khôngtuyênbố detector đãđúng hoặc nhàu đãđượcdewarp.

**QA:** `.tmp/qa_mvp06_01_03.py` đọc lại92PNG của7runs,4detection/14trial,6render+1manual_required. Kiểmhash/bytes/dimensions/mode/EXIF, source/confighash/H/timing/run_id/entrypoint; tínhkiểmsourcewarp/filter/gray/Otsu/rotation/full-preview từactualstage/config. Source6cặp/22fixtures nguyên; hashfullGraymanualimg_001 trùngoutputGray giaiđoạn05. Snapshotcùngảnhđượckiểm đểđạt03, chưa đánh dấu06.05 hoànthành.

**Hồi quy/bàn giao:** `backend/.venv/Scripts/python.exe -m pytest -c backend/pyproject.toml backend/tests` → **777passed in38.83s** =733trước+30render+6stages+8scanCLI, khôngskip/nớicheck. Auto-review cho chạy TestClient/temp/subprocess, khôngapprovalrejection. Reviewsource/config/mapping/confirmation/stageownership/encoder/error/no-overwrite vàlõiđộclậpI/O; frontendkhôngđổi nên khônglặpbuild/browser. Tích01–03/03a/b vàcheckpoint06-C1 sauevidence;41main+5AUX/110IDgốc/109cầnlàm/1skip/5optional giữ. M1/cổng06 và04–06 cònchờ. Đồngbộ README/AGENTS/plan/todo/phạmvi/project-map/image-contract/hướng/algorithm-notes/progress. Kếtquả/dữliệu/.tmpignored, khôngcommit/push/deploy hoặcgửiảnhra ngoài; khôngsửa code saufullsuite, chỉdocs/QA.

**QA cuối tài liệu:** `.tmp/qa_mvp06_docs.py` đạt12tài liệu/105link nội bộ,41main/5AUX/110ID. Task06.01–03/03a/b checked,04–06 unchecked; không cộng task con lần nữa. Kết quả/dữ liệu/scripts.tmp ignored,8tệp source/tests mới-sửa khôngbịignore. Preview vàmetadata thực đã được mở/đọc để kiểm chứng; không khởi động web hoặc suy ra UI đã nối pipeline.

## 16/10/2026 — MVP06.04: histogram trước threshold

**Phạm vi:** user yêu cầu task4 giai đoạn06. Đọc checklist/phụ thuộc06.03, hợp đồng ảnh, hướng thuật toán và code dispatcher/render/scan/tests trước khi sửa. Dùng using-agent-skills, incremental implementation, TDD, Ponytail, review và documentation; debugging cho lỗi môi trường Temp. Giả định đã thông báo: chỉ BW có ảnh “trước threshold”; Color/Gray hoặc manual_required histogram=null. Không triển khai UI/đồ thị09.07, phần giáo dục OPT-B, task06.05–06.06 hoặc sửa detector. Đối chiếu tham số calcHist với [OpenCV chính thức](https://docs.opencv.org/4.x/d1/db7/tutorial_py_histogram_begins.html); không đọc lại PDF ở lượt này, dùng phân tích/kiểm chứng PDF đã có.

**Lõi và tích hợp:** thêm processing/histogram.py với compute_histogram(gray HxW uint8, mỗi chiều2..2400) → tuple256int, h(k)=số pixel bằng k. Không mask/resize/chuẩn hóa xác suất/mutate; cv2.calcHist channels0/bins256/range[0,256), bao gồm255. Float32 count chính xác trong5.76MP<2²⁴, chuyển int cho JSON. INVALID_HISTOGRAM_INPUT hoặc HISTOGRAM_FAILED có lý do. EnhancementResult thêm histogram optional sau trường stages để giữ vị trí tham số cũ; dispatcher tính trực tiếp trên gray sau lọc/CLAHE ngay trước BW threshold, cả debug=false. Không giữ stagearray khi debug=false và không chạy lại filter/contrast/threshold để tạo metadata. Histogram tính trước rotation, full/preview vẫn từ kết quả gốc.

**CLI/metadata:** scan_one thêm histogram object hoặc null. Counts đi cùng width/height/pixel_count của actual prepared_gray, source_artifact và hash đúng payload PNG; method/scope=otsu/global +actual t hoặc adaptive_gaussian/local +null. Adaptive không có một ngưỡng global; block_size/C ở effective_config. PageConfig/scan-v1 không đổi vì chỉ thêm diagnostic và không thay pixels/thuật toán; snapshots cũ có thể chưa có trường mới. Thời gian histogram đã nằm trong enhance/total, không cộng lặp. Manual_required không tạo gray/full/histogram giả. Không thêm dependency/abstraction mới.

**TDD:** test_histogram viết trước → RED ModuleNotFoundError; thêm helper/dispatcher →16histogram +6stage tests đạt22passed0.52s. Có ảnh0/255, mixed/gradient stride/readonly, ảnh2400² toàn255, sai loại/dtype/dimensions/size, NumPy counts độc lập, tổng/int/JSON, input nguyên; BW Gaussian+CLAHE/Otsu/Adaptive/rotation/debug parity, Color/Gray null. Mở rộng scanCLI tests trước nối metadata: môi trường sandbox không tạo được pytest Temp hệ thống, chuyển basetemp sang thư mục mới `.tmp/pytest-mvp06-04-red`; RED đúng5KeyError histogram/4passed18.09s. Nối CLI → focused25passed23.56s với basetemp mới `.tmp/pytest-mvp06-04-green`. Một CLI Adaptive mới và assertion vào tests hiện có kiểm hash/dims/actualgray/Otsut/Adaptive localnull/EXIF/rotation/largepreview/Color/failure; không bỏ hoặc nới check để vượt lỗi.

**Runtime thật:** `backend/.venv/Scripts/python.exe .tmp/verify_mvp06_04.py` →2CLI run tại `experiments/results/mvp06-04-histogram/` (ignored), `verification.json` ghi số đo. img_004 Otsu auto dùng requested_config gốc mốc03, giữ LOW_HEURISTIC_SCORE/confirmed=false, t=140/global. Run Adaptive dùng config góc vừa có, chỉ thay threshold.method; skipdetect nên không tái tạo warning detector, không coi warnings rỗng là chọn trang đúng. Cùng prepared_gray1112×1358/hash08a452f1…:256bin, tổng1.510.096pixel,213bin khác0; Adaptive local/t=null và BW khác. Đọc PNG Pillow→NumPy bincount kiểm độc lập mọi bin/hash/dims, recompute đúng BW bằng config từng run. Full/preview/warp/filter/gray/before_rotation Otsu giữ nguyênhash mốc03 (fullbc5c98f7…); nguồn và22fixtures giữ hash. Vùng ăn bàn vẫn còn, không tuyên bố histogram khắc phục phân vùng hoặc đo accuracy. Không phải nghiệm thu06.05 dù có kiểm không đổi pixel trong phạm vi task04.

**Hồi quy/review:** lệnh `backend/.venv/Scripts/python.exe -m pytest -c backend/pyproject.toml backend/tests --tb=short -q` → **794passed95.24s** =777cũ+16histogram/dispatcher+1CLI. Fullsuite chạy quyền cho TestClient/temp/subprocess như các mốc trước, auto-review chấp nhận, không rejection/skip. Review cả năm mặt correctness/readability/architecture/security/performance: count bounded/255/validation, khôngI/O ởlõi, tupleint dễJSON, histogram gắn đúng actualstage/hash/method, giữ source/config/pixels/confirmation, không dependency mới. Không sửa code sau suite794; frontend không đổi nên không lặp browser/build/typecheck.

**Bàn giao:** task04 từ2tệp dự kiến thành5tệp code/tests để nối thật dispatcher và CLI; vẫn một task M, không tăng ID. Tích06.04 sau bằng chứng;42main+5AUX/110ID,06.05–06.06/M1 cònchờ. Cập nhật README/AGENTS/plan/todo/phạmvi/project-map/image-contract/hướng/algorithm-notes/progress. Ảnh/data/results/.tmp giữ ngoàiGit, khôngcommit/push/deploy hoặcgửiảnhra ngoài. CentricMem ambient lỗiInternalerror, nhưng cm_done sau đó thành công: shelf document-scanner, sessions/2026-10-16T140054Z-mcp-6fc271.md; chỉ lưu tóm tắt kỹ thuật, không gửi ảnh.

**QA tài liệu:** `.tmp/qa_mvp06_04_docs.py` đạt12tài liệu/111link nội bộ,42main/5AUX/110ID;06.01–04 checked,05–06 unchecked. Giữ snapshots/bằng chứng cũ có ngày rõ; README/currentstatus và phần06.04 trong AGENTS là ngữ cảnh mới. Histogram source/tests không bịignore; ảnh thật/results/scripts.tmp bịignore. Sau fullsuite794 chỉ sửa tài liệu/QA, không đổi source hoặc dependency.

## 16/10/2026 — MVP06.05–06 và AUX06.01: tái lập, M1 và rà sáu task

**Phạm vi:** user yêu cầu task5–6 và rà cả6task như các giai đoạn trước. Các lượt yêu cầu trước bị ngắt chỉ có commentary, chưa có lệnh triển khai dang dở cần khôi phục. Đọc using-agent-skills, AGENTS/checklist/dependencies/progress, hợp đồng11/preview/histogram, hướng5.5–5.6, audit05 và code/tests/callers render/enhancement/scan/writer. Dùng workflow incremental implementation/TDD/Ponytail/review/documentation đã đọc trong phiên; không sinh subagent hoặc thêmdependency. Đối chiếu lý thuyết qua phân tích/PDF audit trước, không đọc lại toàn3PDF hoặc thay detector ở lượt này.

**Task05/tests:** thêm4ca vào test_render:Color270/Gray90/BWOtsu180/BWAdaptive90 trên source readonly, Gaussian5+CLAHE/config serialized→parse lại. So full/config/H/warp/stages/histogram/actualt, encode full-preview và nguồn/config nguyên; các output độc lập bộ nhớ. Thêm2ca test_scan_one:auto đềxuất và blankmanual_required, mỗi ca2tiếntrình CLI cùng configđầuvào, đọc/hash artifacts vàdebug, so version/environment/source/config/metadata/trials/candidates/histogram/H. run_id khác được giữ, timingkhôngyêucầugiống. Đây là bổ sung kiểm chứng hành vi đã có, không dựng lỗi RED hoặc sửa core để tạo pass. Focused `backend/.venv/Scripts/python.exe -m pytest -c backend/pyproject.toml backend/tests/test_render.py backend/tests/test_scan_one.py -q --tb=short --basetemp=.tmp/pytest-mvp06-05-focused` → **45passed30.73s**.

**Runtime tái lập/M1:** `.tmp/verify_mvp06_m1.py` gọi CLI bằng subprocess thật;10ca×2tiếntrình độc lập, cùng raw source và file requestedconfig, lưu tại `experiments/results/mvp06-m1-verified/` (ignored). Ca thuận lợi anhtestnewColorauto201×285; img_003Grayauto898×1288/bóng; img_004Otsuauto1112×1358/t140 vẫnănbàn, Adaptiveconfiggóc cùngsize/localnull; img_001auto manual_required vàtayColor951×1284/Gray180951×1284/Adaptive901284×951; EXIF6Otsu27095×63/t150; checkerboardOtsu901300×2000/t118→preview650×1000 cógray.20runs=18render/2manual_required,8detection/28trial,230PNG. Mọiconfig confirmed=false; các quadmanual làdraftagentchọn, khôngGT/userconfirmed.4rawảnh thật độcnhất nhưng3ảnhmanifest cùngdoc_01, anhtestnewchưaidentity; khôngđo accuracy hoặc bổsung tập test.

**QA runtime:** so toànmetadata root/detection hai lượt trừ run_id/timings_ms; các artifact PNG/hash/bytes/dimensions/mode/EXIF, configfilehash, source/raw/normalized/BGRhash, H, actual Otsut/histogram đềukhớp. Mở ảnh và tính kiểm sourcewarp/filter/gray/CLAHE/Otsu/Adaptive/rotation/full-preview, histogram NumPy từsavedgray; detection analysis/gray/Gaussian/rawCanny/closing/Otsumask từngtrial cũng được tính kiểm. Timing hữu hạn/khôngâm/tổng đúng, detector total nằm trong pipeline detect. Không chỉso haioutput cóthểcùngsai.6cặp nguồn/normalized trong manifest và22fixtures nguyên. Verification.json ghi hash code processing/CLI/writer/requirements và source, environment/version; không đổi code/dependency trong lượt này. Configđầuvào cornersnull lặpauto khác táichạy outputconfigcógóc theođườngmanual, tài liệu ghi rõ. Không tuyênbố pixel/PNGbyte tấtđịnh trênmọimáy/phiên bản.

**Task06/hướng dẫn thực chạy:** tạo docs/milestone-m1.md với luồng/đầu ra/exit/confirmed, bảng10ca, giới hạn, môi trường và PowerShell smoke dùng fixtures sẵn. Trích nguyên blockPowerShell từfile sang `.tmp/m1_smoke.ps1` rồi chạy, không sửa lệnh để khớp output:6CLI ở `experiments/results/m1-smoke-20261016-214342-305/` →3modeEXIF/replayBW/blankmanual_required→retrytay, config/full/preview/preparedgrayhash vàsource giữ. Đãxem overlay anhtestnew, Color tayimg_001, Graybóngimg_003, BWănbànimg_004, Adaptive90nhiễuimg_001. Những quan sát preview không chứngminh giữ mọi nét/dấu; khôngthêmOCR/dewarp/PDF/UI vàoM1. Notes/contract/theory nốiđếnmốc vàphânbiệt t140render/t102detector.

**AUX06.01/audit:** docs/audit-phase-06.md có ma trận6task với code/tests/runtime/tiêu chí vàgiới hạn. Khôngphát hiện lỗi implementation mới chặn cổng06; giữnguyên gate source/geometry/config/confirmation vàdetector debt05. Nợepsilon/fitdistance/cạnhyếu/vùngnềnsáng/khunggiả chưađược trả; repeatability không accuracy. Audit nhắc API/UI phảigiữ confirmed/revision, khôngsuyra từCLI rendered. Task03a/b khôngtăng taskchính; AUX06.01 thêmđúng1taskphụ do user yêu cầu.

**Hồi quy/bàn giao:** `backend/.venv/Scripts/python.exe -m pytest -c backend/pyproject.toml backend/tests --tb=short -q` → **800passed99.97s** =794cũ+4core+2CLI, khôngskip/nớicheck. Fullsuite được auto-review cho quyềnTestClient/temp/subprocess, khôngrejection; source/testkhôngsửa sau800, chỉdocs và QA. Review correctness/readability/architecture/security/performance: giữ mọi ranhgiới/I/O/nguồn/config/version/metadata, khôngcache/abstraction/dependency mới, khôngbiến timing thành sốđếm accuracy. Frontend khôngđổi nênkhônglặpbuild/typecheck/browser. Tích05/06/AUX06.01, M1/cổng06 đạt;44main+6AUX/110IDgốc/109active/1skip/5optional. Next07.01 schemaAPI. Task05 thành3tệp test/progress, task06 thành3tài liệu gồmM1riêng, audit2tài liệu; khôngtạochanges.md/commit/push/deploy hoặcgửiảnhra ngoài.

**QA cuối:** `.tmp/qa_phase06_docs.py` đạt13tài liệu/143link nội bộ,44main/6AUX/110ID; đủ6row audit/6task06 checked,07.01 và5optional chưa tích. Hash code/requirements khớp runtime, artifacts/data/scripts.tmp ignored, tests/M1/audit khôngignore. CentricMem lưu thành công shelf document-scanner/session `sessions/2026-10-16T145012Z-mcp-3264d9.md` với tóm tắt kỹ thuật, không ảnh. Audit được yêu cầu mở trongCodex, tool trảqueued; không coi queued là đã hiện trên màn hình. Không sửa source/tests sau suite800.

## 17/10/2026 — MVP07.01–02: schema API và nền SQLite metadata

**Phạm vi và quyết định:** user yêu cầu task1–2 giai đoạn07. Đọc using-agent-skills, AGENTS/todo/plan, bàn giao M1/audit06, đặc tả gốc5/10 và image-contract trước triển khai. Dùng API/interface design, incremental implementation, TDD, Ponytail, security-and-hardening, debugging khi có warning và review/documentation đã đọc trong phiên. Không tạo subagent hoặc thêm dependency. Phát hiện image-contract cũ ghi initialrevision1, trong khi checklist07.05 hiện hành quy định0; dùng nguồn taskMVP hiện hành để chuẩn hóa0, thông báo user và sửa hợp đồng, không có dữ liệu nhập cần migrate. Chưa làm07.03 hoặc route/UI/import/CAS; chỉhealth tiếp tục làHTTP thật.

**Task01/types:** thêm schemas/common.py/pages.py/sessions.py/errors.py và test_api_schemas.py. UUIDv4, UTCaware→UTCZ, titlestrim/default1..200, strictrevision/int/bool/extra/finite; session/page/artifact/config/detect/render/order/exportrequest/errorenvelope. ConfigUpdateRequest chỉparse envelope trướclookup, validate_config(source_size thật,warp_size khi cần) delegateparse_config đểgiữdefaultspermode/field vàkhôngmerge persistedconfig. PageRead validateconfig theoW/Hnguồn; ConfigRead cócorners phải cócontextsource_size. Sourceartifact khôngrevision, derivedrender/preview/debug córevision; DTOkhônglộpath. SessionDetail kiểmowner/order/unique/max20. Detectluônunconfirmed/status theo coreproposed, khôngstatussuggested minhhọa cũ. Export PNG/JPG mộttrang, PDF1..20; optionsschema baseline không hoànthành task11.

**TDD/review:** test trước RED thiếuapp.schemas, triển khai→18passed0.45s. Bổsungpage response/context/export/DTO/detection; warning serialization nestedPageConfig bị phát hiện khi dumpSessionDetail. Chạyca riêng với -W error thànhRED; localized plainfieldvalidator làmserializer kỳvọngPageConfig nhưng nhận dict trong serialize. Đổi sang wrapvalidator gọi source-boundparse_config, giữserializer/modelJSONschema gốc; bổsungmodel_dump_json(warnings='error') làmregressionguard. Khôngsuppresswarning/nớigeometry. Các tests sau đạt -W error. 21schema tests tổngcuối.

**Task02/schema:** storage/models.py có6bảng sessions/pages/page_configs/artifacts/exports/schema_version, UUIDserver/timeUTCISOtext/JSONconfigsnapshot. Pageposition unique(session,position); sourceW/H/pixels/basickind/mime/bytes/hash/pathsyntax/revision/JSONshape cóSQLchecks. CompositeFK chặnartifact/config khác(session,page), sourcepointer khácpage kểcảcùngsession; page↔sourceartifact FKdeferred đếnCOMMIT đểcấpUUID vàinsert cùngtransaction. Xóasource đangthamchiếu bịchặn; sessioncascade chỉmetadata. Export snapshotlàJSONlịch sửkhôngFKvào currentrevision. Full PageConfig/MIME/hash/tệp/role của sourcepointer/snapshotphầntử/quota/CAS vẫnlàtráchnhiệmservice, khôngcoi SQLshape làtoànbộusecase.

**DB/repository:** open_database(path) tạoenginefile, initialize_database explicit/atomicDBtrống, nhận schema_version1/đủ6table hoặc từchốiunknownversion/partial/foreignDB, khôngrepair/reset/migrate. Eventmỗiconnection bậtFK vàSQLAlchemyownsBEGIN để cảSELECT/DDL transactional. Đốichiếu [SQLAlchemy2.1 SQLite](https://docs.sqlalchemy.org/en/21/dialects/sqlite.html), chọncặp isolation_level=None/beginhook đểtươngthíchPython3.11/3.12; kiểmthựcSQLite3.49.1/SQLAlchemy2.1.4/Pydantic2.14.1. UTCTypeDecorator từchốinaive, lưuISOUTC/trảawareUTC. Repository chỉunitofwork/create_session/list_pages/get_page/get_artifact cóownerlookup; khôngimportAPI/processing hoặcOpenCV/I/Oảnh, khôngtựcommitquery. Titleđượcvalidateởboundary, SQLvẫncóbasiccheck. KhôngruntimeDBsideeffect lúcimport; HTTPmainkhôngđổi.

**Storage tests:** RED thiếuapp.storage→11passed1.53s. Thêm8ca same-session/wrong-page sourcepointer, path/hash/revision/byte metadata sai, negativerevision, rollbackDDL saufaultinjection, foreignDB khôngbịadopt/erase.19storage tests gồmreopenconnection/UTC/ownerFK/uniqueorder/missingsource/active source delete/metadata rollback/export/cascade/unknownversion. Focused40tests API+DB với -W error đạt1.62s sauchỉnhcuối; khôngbỏtests hoặcgiảmvalidation.

**Contract/runtime:** docs/api-contract.md chốtendpoint dựkiến, status/errors/IDs/config/revision/artifact, taskđể nối route, exportbaseline và cácgate chưathựcthi. Giữthiếuconfigfield→defaults, khôngoldmerge; no-op/CAS/confirmation ở08,worker07.06/file07.03/import07.05/HTTP07.04/07.07/UI07.08. Bảng thểhiện healthlàroute duy nhất, errorhandler400chưađăngký. `.tmp/verify_mvp07_01_02.py` chạy2tiếntrìnhwrite/reopen trên DBở experiments/results/mvp07-01-02-verified/ (ignored):6tables/version1/FKON/FKcheckrỗng/UTC/revision0/confignguyên, crosssessioninsert bịchặn vàtransactionkhôngđểartifactmới. Syntheticmetadata thamchiếu3pathảnh **chưaghi**, khôngdùngkhẳngđịnhlưuảnhthật.5vídụJSON trongcontractđượcvalidate/serialize bằngmodel vàcoreConfig;13JSONschemas sinhđược, lưuschemas.json/reopened-session.json/verification.json. Khôngdùngảnhcánhân hoặcgửiảnhra ngoài.

**Hồi quy và bàn giao:** final `backend/.venv/Scripts/python.exe -m pytest -c backend/pyproject.toml backend/tests --tb=short -q` → **840passed106.98s** =800M1+21schema+19storage. Mộtfull840102.61s trướcchỉnhnhỏcuối; rerunfinal sautáchrepositorykhỏiAPI/titlevalidationvàchốtPNGmộttrang, khôngrepeatvôcớ. Fullsuiteauto-review choTestClient/temp/subprocess, khôngrejection. Khôngsửasource/tests saufinalsuite, chỉdocs/QA. Processing/frontend/main/settings/requirements giữ; khônglặpbrowser/frontendbuild vìkhôngđổiUI. Reviewcorrectness/architecture/security/performance/readability vàđốichiếuvídụcontract; pathSQLkhôngthayresolve/symlinkcheck07.03. Task01 chiaa(5tệpschemas/tests)/b(contract/vídụ);02giữ4tệpstorage/tests; khôngtăngparent. Tích07.01–02/a/b:46main+6AUX/110ID/109active/1skip/5optional. Next07.03;checkpoint07-C1 chờ03,khôngtích07.04–09 từmetadataDB. Đồngbộ README/AGENTS/plan/todo/phạmvi/project-map/image-contract; giữM1/audit06 làmốc lịch sử. Khôngcommit/push/deploy hoặcghiảnhngoàiphạmvi.

**QA cuối tài liệu:** `.tmp/qa_mvp07_docs.py` đạt14tài liệu/149link nội bộ,46main/6AUX/110ID,07.01/a/b/02 checked,03–09 và5optional chưa tích. RuntimeDB/JSON/scripts.tmp bịignore;9tệp source/tests mới vàapi-contract khôngignore. Hash processing/CLI/requirements vẫn khớpM1. Bản bàn giao CentricMem lưu thành công shelf document-scanner/session `sessions/2026-10-17T041714Z-mcp-9c0fdf.md`, khônggửiảnh. Tool mởapi-contract trảqueued, khôngcoi làđãhiện trênmànhình. Chỉdocs/QA thayđổi saufull840.

## 17/10/2026 — MVP07.03–04: artifact an toàn và API bộ tài liệu

**Phạm vi:** user yêu cầu task3–4 giai đoạn07. Đọc lại using-agent-skills, AGENTS/plan/todo, hợp đồng API/ảnh, SQLite và các bàn giao trước; dùng incremental implementation, TDD, API/interface design, Ponytail, security-and-hardening, review/documentation. Không mở rộng sang import07.05/worker07.06/upload07.07/UI07.08 hoặc sửa detector. Không subagent/dependency mới.07.04 tách a/b do thực tế7tệp code/tests; task con không cộng tổng chính.

**Task03:** thêm storage/files.py, repository.register_artifact/discard_unreferenced và test_artifact_files.py. ArtifactStore nhận immutable bytes đã encode; không nhận upload filename/path, không re-encode normalized PNG hoặc áp quota upload15MiB lên PNG nội bộ. UUIDv4, owner/kind/MIME/revision/dimensions được kiểm trước ghi. Đường dẫn sessions/{sid}/{bucket}/{artifactUUID}.{extension}; temp cùng thư mục, write/flush/fsync/close rồi publish không ghi đè. Windows os.rename; POSIX hardlink rồi unlink temp để giữ no-replace. Guard lexical/resolved root và symlink/junction/reparse kể cả trỏ trong root. Root local được tin cậy; không chống tiến trình OS có quyền thay directory đồng thời.

**File/DB:** trả descriptor bytes/SHA-256/dimensions của đúng payload. register_artifact verify regular file/bytecount/hash trước add/flush; caller giữ commit. Sau rollback, cleanup chỉ dùng descriptor tệp MỚI của thao tác lỗi, kiểm DB cả ID/path rồi verify/unlink; giữ artifact active, không recursive delete. Không có atomic transaction chung file+DB: crash giữa publish/commit có thể để orphan; chưa GC hoặc chứng nhận mất điện.07.05 cần nối các primitive thành import use case đầy đủ, không coi rawORM là use case nhập.

**TDD/files:** tests trước RED thiếu app.storage.files; triển khai →35file+DB tests đạt2.84s, sau mở rộng có19artifact tests. Có exact PNG bytes/hash từ fixture EXIF6, partial write/fsync/rename lỗi giữ file cũ và không publish tệp mới, collision không overwrite, traversal/owner/kind/MIME/payload/dimensions sai, payload nội bộ hơn15MiB, verify file trước đăng ký, FK commit rollback/cleanup orphan, không xóa file active hoặc bị thay bytes. Hai junction thật Windows được tạo bằng native PowerShell trong thư mục test, cả target trong/ngoài root đều bị từ chối; không skip hoặc cần đặc quyền symlink. Không test chỉ để xác nhận tạo thư mục.

**Task04:** thêm services/sessions.py, api/sessions.py, api/errors.py; sửa main/repository và health test dùng app factory với DB tạm. create_app(database_path) lifespan khởi tạo/kiểm DB/store, dispose khi shutdown; default data/scanner.sqlite3, import không tạo DB. Sync routes chạy qua FastAPI threadpool: POST /api/v1/sessions201, GET /sessions200 với count/limit/offset và updated_at DESC/id ASC, GET /sessions/{sid}200 với pages position và membership. Create chỉ trả sau commit. Detail lấy config/dimensions nguồn thật, thiếu config fail; render_revision là max metadata full-render hoặc null, chưa chứng nhận export. Không load ảnh/chạy OpenCV trong transaction. DBschema_version1 và core/frontend/dependencies giữ nguyên.

**TDD/API:** RED chưa có create_app trước khi nối HTTP;18tests mới gồm actual SQLite create/list/detail/rỗng/reopen, UTC/title/default, pagination/tie stable, trang khácsession không lọt, configrevision0, ID sai/thiếu404, body/query400, DB before_commit fault500/rollback, missing config500, exception sanitized, HTTP405 giữ Allow. TestClient failure dùng raise_server_exceptions=False để kiểm response thật. ErrorEnvelope không echo input/SQL/path/trace, details rỗng; server log giữ lỗi. OpenAPI chỉ3path hiện thực,400/4XX/500 và detail404 đúng ErrorEnvelope; dùng hỗ trợ4XX native của FastAPI, không sinh422 giả. Kiểm installed fastapi/openapi/utils.py; đối chiếu [FastAPI lifespan](https://fastapi.tiangolo.com/advanced/events/) và [Python3.12 rename](https://docs.python.org/3.12/library/os.html#os.rename). Không tạo schema cho endpoint giả.

**Runtime thực:** `.tmp/verify_mvp07_03_04.py` chạy Uvicorn localhost ở cổng tạm,3session create/list/detail/rỗng/errors/OpenAPI; seed3page bằng lower layer với9file EXIF6 original/normalized/thumbnail đã encode trước DB transaction. Hai trang của tài liệu chính đúng thứ tự0/1, trang của tài liệu khác không lọt; source IDs/configrevision0/UTC/path không lộ. Fault rename giữ oldfile/không temp; FK commit lỗi rollback/dọn orphan mới, active cleanup bị chặn/FKcheck rỗng. Dừng backend rồi mở tiến trình riêng với cùngDB: detail và cả9file verify bytes/hash nguyên. Evidence `experiments/results/mvp07-03-04-verified/verification.json` và SQLite/log/files (ignored). Fixture seed này KHÔNG hoàn thành import07.05/upload07.07/UI07.09. Script kiểm chứng lúc đầu import nhầm module resize thay vì image_sizes, sửa script rồi chạy đạt; không phải lỗi processing hoặc nới kiểm thử. Không dùng ảnh cá nhân/gửi ảnh ra ngoài; tiến trình kiểm chứng đã đóng.

**Kiểm chứng cuối/review:** focused schemas/storage/files/API/health với -W error và basetemp workspace → **78passed3.64s**. Full `backend/.venv/Scripts/python.exe -m pytest -c backend/pyproject.toml backend/tests --tb=short -q --basetemp=.tmp/pytest-mvp07-03-04-final` → **877passed105.79s**, tăng37=19artifact+18API so840; không skip/nới check. Auto-review cho quyền localhost/TestClient/SQLite/junction/subprocess, không rejection. Review correctness/readability/architecture/security/performance: giữ source byte/hash/owner/transaction/no-overwrite, lỗi HTTP không lộ chi tiết, không dùng userfilename/path, không OpenCV trongDB, list có giới hạn/queries theoowner và không thêm abstraction/dependency. Không thấy lỗi mới chặn task03–04. Không sửa source/tests sau fullsuite; frontend không đổi nên không chạy lại browser/typecheck/build.

**Bàn giao:** tích07.03/04/a/b và checkpoint07-C1 sau evidence schema/DB/file/fault; **48main+6AUX/110IDgốc/109active/1skip/5optional**. Không đánh dấu cổng07 hoặc07.05–09. Next07.05 service nhập một trang. Cập nhật README/AGENTS/plan/todo/phạm vi/project-map/image-contract/api-contract, giữ các mốc progress/audit cũ làm lịch sử. Nợ detector img_004/006 ăn bàn và dataset6ảnh/1doc/test0 giữ nguyên. Không tạo changes.md/commit/push/deploy hoặc public data directory.

**QA bàn giao:** `.tmp/qa_mvp07_03_04_docs.py` đạt14tài liệu/155link nội bộ,48main/6AUX/110ID,07.01–04/a/b checked,07.05–09 và5optional chưa tích. Kiểm lại9file runtime đúng byte/hash; processing/CLI/requirements giữ hashM1; runtimeDB/JSON/scripts.tmp ignored, source/tests/contract không ignore. CentricMem lưu thành công shelf document-scanner/session `sessions/2026-10-17T043256Z-mcp-9b1bd1.md`, chỉ tóm tắt kỹ thuật. Không sửa source/tests sau full877.

## 17/10/2026 — MVP07.05–06: nhập một trang và executor dùng chung

**Phạm vi:** user yêu cầu task5–6 giai đoạn07. Đọc lại using-agent-skills/AGENTS/plan/todo, hợp đồngAPI/ảnh, DB/files/service hiện có. Dùng incremental implementation, TDD, Ponytail, security-and-hardening, review/documentation/git theo workflow đã đọc. Không subagent/dependency mới; không commit/push/deploy. Phạm vi là blocking import use case và executor/lifespan/429, chưa upload/artifactGET/UI hoặc sửa detector. Giữ revisionmới0, confirmedfalse, một Uvicornprocess, một worker/haiwaiting.

**Task05:** thêm services/imports.py/test_imports.py, thêm repository.lock_import_session/page_count_and_next_position/add_source_page. import_page nhận sessionUUID/immutablebytes, không filename/clientconfig/góc. Kiểm session/quota sớm; validate header/format/byte/pixel, normalize load/EXIF/alpha→BGR, encode_normalized_png giữ đúngpayload và encode_stage_png cho thumbnail320 INTER_AREA/half-up/no-upscale (cạnh1 được phép). Encode cảsource/thumbnail trước ghi. Originalbytes nguyên/MIME theo nội dung/dimensions trướcEXIF; normalized/thumbnail metadata theo từng raster. Không áp quota upload15MiB cho PNG nội bộ.

**Commit/cleanup:** sau ghi3file bằng ArtifactStore, finaltransaction UPDATEsession lấy SQLite writerlock trước đọc count/maxposition; kiểm lại session/quota20, append max+1, đăng ký file đãverify, page/configrevision0/confirmedfalse/cornersnull, timestamp session thay đổi. DTO kiểm với source dimensions thật trướccommit, chỉ trả saucommit. Không decode/resize/encode/OpenCV trong transaction. Tệp và DB không có transaction chung: rollback lỗi thường dọn từng descriptor mới chưa tham chiếu qua DBtransaction mới, giữ active/oldfile. Nếu cleanup cũng lỗiDB/disk thì log/giữ lỗi gốc/khôngxóamù; crash có thể để orphan, chưa GC. Có kiểm cuối vì session/quota có thể đổi trong lúcCPU/ghi file; không chỉ dựa precheck.

**TDD05:** test viết trước→RED ModuleNotFoundError app.services.imports; triển khai→12passed3.44s với -W error. Có EXIF6/alphaRGBA/PNGnamedJPG, originalbyte/MIME/sourcepayload/hash/pixels/UTC/config0/reopen; ảnh sai không tạo page/file; thiếu session, skinny2×2000→thumbnail1×320;20page appendorder/quota; encode/secondwrite/actual before_commit fault giữ trang cũ/dọn mới. Fault commit dùng after_flush đánh dấu thao tác ghi rồi before_commit ném SQLAlchemyOperationalError; không chặn read-only precheck/cleanup. Thêm2tests session bị xóa saughi3file và haiimport thật cùng tranhsuất20 (Barrier trướcfinalcommit, ngoàiexecutor): chỉ một thắngposition19,20pages/60files, không orphan. Tổng14import tests.

**Task06:** thêm services/processing_executor.py/test_processing_executor.py, nối main.py và api/errors.py. ProcessingExecutor eventloop-bound, asyncio Future/deque tối đa2waiting + ThreadPoolExecutor(max_workers=1). Chỉ activecall được gửi pool; không dùng queueunbounded của ThreadPool để nhận hàngchờ. FIFO, nhận3call tổng khi workerbận; quáquota hoặcclosing némProcessingBusyError→429/ErrorEnvelope. submit trảFuture/run async trảkếtquả. HủyqueuedFuture/caller trảslot trướcnextsubmit và không chạy callable; cancelactivecaller không dừngthread, giữslot đếnkhi callablexong, bỏkếtquả cho callerđãhủy. Exception thường chuyểncaller và worker tiếp tục. Khôngsubmit đệquy từworker; wholeusecase giữ một slot. Đây là giới hạn tác vụ ảnh, không số thread nội bộ OpenCV.

**Lifecycle/TDD06:** app.state.processing mộtinstance trong lifespan; shutdown từchốimới/cancelqueued/đợiactive/jointhread trướcdisposeengine, khôngpersistjob hoặchardkillthread. Tests RED thiếu app.services.processing_executor; triển khai→36import/executor/sessionAPI/health đạt3.58s.5executor tests kiểm actualsingleworker/threadkháceventloop/FIFO/overflow, queuedcancel/immediatereplacement, cancelactivecaller khôngsớmnhảslot, lỗiworker/recovery/shutdown/idempotent, appTestClient probe429/health. Probe chỉ đăng ký trên test app, OpenAPI sản phẩm vẫn3path health/sessions/detail. Đốichiếu [Python Executor.shutdown/cancel](https://docs.python.org/3.12/library/concurrent.futures.html#concurrent.futures.Executor.shutdown) và [asyncio run_in_executor](https://docs.python.org/3.12/library/asyncio-eventloop.html#asyncio.loop.run_in_executor); không tạo timeout giả dừng thread. Các routeảnh ở07.07/08/09/11 phải dùng chính instance này; CLIoffline độc lập.

**Runtime localhost/restart:** `.tmp/verify_mvp07_05_06.py` chạy Uvicorn localhost bằng tiến trình ẩn với DB riêng trong experiments/results/mvp07-05-06-verified/ (ignored). Privateverificationroutes gọi blocking import qua executor thật, khôngđưa routeupload giả vào appmain. Giữ active bằngEvent, chờ2call→overflow429; queuedcancel/replacement FIFOtrace active-start/active-end/queued/replacement, canceledcall khôngchạy. Health phản hồi14.19ms trong lượtđo, khôngbenchmark/SLA. Nhập EXIF6/alphaRGBA thành2page/6file original-normalized-thumbnail, configrevision0/confirmedfalse; so originalbytes, exactsourcePNG/hash/pixels, thumbnailpixelso vớiINTER_AREA, noEXIF, FKcheckrỗng. Fault actualcommit trả500STORAGE_FAILED, metadata/hash/count6file giữ, worker tiếp tục nhận việc. Dừng server rồi mở tiến trình riêng cùngDB: detail vàhash6file khớp; mỗi shutdown xác nhận executorclosed/khôngcònscanner-image thread. verification.json ghi kếtquả; tiến trình kiểmchứng đãđóng. Không dùng ảnhcánhân/gửiảnhra ngoài.

**Kiểm chứng/review cuối:** focused schemas/DB/files/sessionAPI/import/executor/health -W error với basetemp mới → **97passed6.12s**. Full `backend/.venv/Scripts/python.exe -m pytest -c backend/pyproject.toml backend/tests -q --tb=short --basetemp=.tmp/pytest-mvp07-05-06-final` → **896passed108.88s**, tăng19=14import+5executor so877, khôngskip/nớivalidation. Auto-review choTestClient/SQLite/junction/localhost/subprocess, khôngrejection. Review5mặt correctness/readability/architecture/security/performance: source/config/metadata/owner/atomicfile giữ, quota final cówriterlock, CPUngoàiDB/eventloop, FIFO/cancel khôngoversubscribe, cleanup khôngactivefile, no filename/path vàno dependencies. Không phát hiện lỗi mới chặn05–06/checkpoint07-C2. Không sửa source/tests saufullsuite; processing/frontend/schemaVersion1/requirements giữnguyên, khônglặp browser/build/typecheck vìUIkhôngđổi.

**Bàn giao:** tích07.05–06 và checkpoint07-C2 sau97tests/runtime; **50main+6AUX/110IDgốc/109active/1skip/5optional**.05giữ3tệpdựkiến,06thành4tệp do mapping429; khôngthêmAUX/taskcon. Đồngbộ README/AGENTS/todo/plan/phạmvi/project-map/image-contract/api-contract, giữhistoricalaudit/progress. Next07.07 APIupload/artifactGET,07.08UI/07.09reopenUI vàcổng07 cònchờ. Nợdetector img_004/006ăn bàn/dataset6ảnh1doc/test0 giữnguyên.

**QA bàn giao:** `.tmp/qa_mvp07_05_06_docs.py` đạt14tài liệu/160link nội bộ,50main/6AUX/110ID,07.01–06 checked/07.07–09 và5optional chưa tích. Kiểm lại2page/6file runtime đúng byte/hash, shutdownclosed/jointhread; hash processing/CLI/requirements vẫn khớpM1. Source/tests/contract khôngignore, DB/results/probe scripts ignored; khôngrouteupload sảnphẩm phát sinh. CentricMem lưu thành công shelf document-scanner/session `sessions/2026-10-17T044300Z-mcp-cd38d7.md`, chỉ tóm tắt kỹ thuật/khôngảnh. Không sửa source/tests sau final896.

## 17/10/2026 — MVP07.07–09 và AUX07.01: UI nhập, mở lại và rà chín task

**Phạm vi/workflow:** user yêu cầu làm một mạch3task07/08/09 rồi rà9task như các giai đoạn trước. Đọc using-agent-skills, AGENTS/plan/todo, API/image-contract, MVP và đặc tả gốc4–7/9.1/10, audit06/M1, code/schema/service/executor hiện có. Dùng incremental/TDD/API/interface/security/Ponytail/review/documentation; bổ sung frontend-ui-engineering/browser-testing-with-devtools, kiểm UI thật bằng cua_repl (nativehost thay DevToolsMCP). Khôngsubagent/dependency mới, khôngcommit/push/deploy. Không đổi thuật toán để phục vụ UI; source/corners/confirmed/revision boundaries giữ.

**Task07/API:** thêm api/pages.py/artifacts.py; sửa errors/main/repository vàtest_sessions_api, thêmtest_import_api.py. Upload đúng1file tênfile/0textfield, rejectextra/config/multifile/malformed. Request.stream cap15MiB+64KiB envelope, file.read64KiB/chunk đếm15MiB riêng, không tinContent-Length/filename/clientMIME. Dùng StarletteMultiPartParser hiện có và callbackon_end; payloadimmutablebytes đưa qua app.state.processing.run(import_page), không CPU trêneventloop. Fileform đóngởfinally. 400imagecodes/415UNSUPPORTED_IMAGE choformat-multiframe/413byte-pixel-page/429executor; storageinternalerror không lộpath/SQL/input. GETartifactUUID join session/pageowner, thoáttransaction rồiguardpath/verifyregularfile-bytehash, trảFileResponse MIME thực/inlineUUIDfilename/nosniff/private-no-store. Khôngmountdata hoặcnhậnpath query. OpenAPI5path/6method, uploadbinarymultipart/GETbinary, khôngauto422 giả. Không thay DBschemaVersion1/requirements.

**TDD/API và lỗi spool:** tests trước RED route404.19tests sau triển khai đạt, gồm EXIF6/alpha/PNGnamedJPG, MIMEbytes/original/source/thumb/IDs/config0/reopen, malformed/multiframe/16MP/15MiB/20page/traversal/privatepaths/corruptblob/commitrollback. Một ca giữ handleSpooledTemporaryFile phát hiện multipart bị cắt thiếuend: FormData.close không cóunfinishedpart đểđóng→RED. Đưa kiểm thiếuend vào boundedstream đang ởtrong protectedparse loop để exception khiến Starlette đóng mọi handle; RED→GREEN, không suppressResourceWarning hoặc dựaGC. Đúng15MiB đượcnhận, hơn1byte/chunkedrequestquábodycap bị413. Nhóm19APItests -Werror đạt3.87s. Đọc implementation Starletteparser đãkhóa (parse đóngfiles trênBaseException); webStarlette502 nên không suy từ docs khôngđọcđược. ImageFileError đãmapSTORAGE_FAILED; dịnhdạng dựa decoder hiện có.

**Task08/UI:** thêm api/client.ts/types/scanner.ts/pages/ScannerPage.tsx/components UploadPanel/PageList/SourcePreview; sửaApp/styles, nativefetch/localReactstate/URLselection, khôngnewlibrary. TypeScriptSession/PageDTO, Quadđúng4điểm vàenumconfig. Tạo/list/detail tài liệu, pagination20, batchFormDataPOST từngfile, báowaiting/uploading/done/error riêng và tiếp tục saulỗi. Fileclientprecheck15MiB chỉUX, backendvẫnchặn. Sourceviewer dùng normalizedPNG, thumbnail riêng; khôngCSSxoay/ảnhgiả/thaypixels. GETAbortController khiđổidoc, POSTkhôngauto-retry; networkerror nhắc tải lại kiểm trạng thái. Loading/empty/error/sourceGETretry/basiclabels/focus/responsive cùng palettegreen hiện có. GiữUploadPanel khirefreshmetadata để khôngmất lỗi batch; resetselection chỉkhiSID đổi đểbấmlạidoc khônglàmtrốngsource. Kiểm browserconfirmed cảhai lỗi này đãsửa.

**Browser thật:** dùngCUAin-appbrowser/tab1 tại127.0.0.1:5173, đãđọc local-web-development/file-uploads/viewport/screenshots. Tạo tài liệu “Kiểm chứng giai đoạn7” quaform. Filechooser multiple thật chọnfixtures/exif_6.jpg→fake.jpg→alpha_rgba.png:2trang64×96/4×2 lưu, fakefile415báoriêng, report3file giữsaurefreshmetadata; chọntrang1 thấysource64×96complete. Toolfilechooser trảkếtquảchậm bấtthường khoảng21phút ởmộtlượt, khôngwait/sleep doagent vàkhôngdùnglàmbenchmark app; nhữngbước sau bìnhthường. Không dùngbrowser evaluate đểclick/mutateDOM/callHTTP giả; evaluate chỉđọc DOM/images/focus. Browserproof/responsive/screenshot lưu cục bộ trong resultsignored, khôngảnhra ngoài.

**Task09/restart:** `.tmp/run_phase07_backend.py` chạy appmain thật, khôngverificationroutes, mộtbackend/data/scanner.sqlite3 vàViteproxy5173, Start-ProcessHidden. UIrefresh giữsession/pageURL. `.tmp/verify_phase07_runtime.py before` đọcGETdetail và6artifact thật ghi before-restart.json. Tạo stopfilebackendv1, Wait-Process/log xác nhận graceful shutdown complete; UIreload khi backendoff báo máy xửlýchưasẵnsàng. Mởbackendv2 tiếntrìnhmới cùngDB, bấmTảilại quaUI: tên/order/config0/confirmedfalse/sourceIDs/dimensions giữ; nguồn64×96load. Scriptafter so JSONtoànDTO/bytecount/hash6blob với before, fakefile khôngpersist, ghiverification.json. Đây làUI +shutdown/startprocessthật, không chỉhaiTestClientcùngmộtprocess. Ảnh/DB giữtrongdata ignored.

**Ảnh thực/responsive/accessibility:** `.tmp/import_phase07_real.py` đọc img_004 theo manifest/hashes, tạo tàiliệu riêng quaAPI sảnphẩm vàPOSTupload, khônghelperroute. normalizedPNGhash đúngmanifest, dimensions1536×2048; UI Tảilại/chọndoc/xemnguồncomplete, khôngchạy detect/warp/render. Viewport320/768/1024/1440 khôngtrànngang, ảnhnguồnloadđúng cả4size; resetviewportvềmặcđịnh. KeyboardTab từTên tài liệu mới→+Tạo tài liệu, outline solid; khônginputthiếulabel hoặcbuttonkhôngtên; consolecuối khôngerror/warn. KhôngclaimWCAGcertificate/screenreader độc lập hoặc hiệu năng từfilechooserlag. real-source.json/browser-proof.json/responsive.json và browser-reopened.jpg/browser-real-source.jpg/browser-mobile-320.jpg ở experiments/results/mvp07-07-09-verified/. Backend vàVite vẫnchạy local đểuserxem, tabmarkDeliverable.

**AUX07.01/audit:** docs/audit-phase-07.md cóma trận9task/code/tests/runtime/tiêu chí/giới hạn, đốichiếu đặc tả nhập9.1/MVP chứkhôngtựmởscope. Sửa3vấnđề mới: multipartspoolleak (regressiontest), reportbatch bịunmount vàreselectdoc mấtpage (browserflow). Bổsungtest routeupload sảnphẩm khiexecutorđủ1active/2waiting:429/khôngtạo trang/healthphảnhồi, không chỉtestgenericprobe. Nhóm20importAPItests-Werror đạt4.52s. Điều này thêm1test saufull915, nênchạy lại finalfullsuite hợp lệ. Audit giữcrashorphan/cleanupfailure/trustedroot/noauth/parsebodybeforeworkerslot nhưgiới hạn, khôngclaimGC hoặcglobaluploadconnectionquota. Nợdetector05/dataset6ảnh1doc/test0 vàPDF/CAS/renderUIgiữnguyên; cổng07 khônglàM2.

**Kiểm chứng cuối:** full915passed128.25s trước thêmca429audit; final `backend/.venv/Scripts/python.exe -m pytest -c backend/pyproject.toml backend/tests -q --tb=short --basetemp=.tmp/pytest-phase07-audited-final` → **916passed125.89s**, tăng20 so896, khôngskip/nớikiểmtra.117ca phase07 trongsuite gồm21schema+19DB+19file+18sessionAPI+14import+5executor+20importAPI+health (healthđãcótrongM1). npm.cmd run typecheck đạt trướcUIruntime; npm.cmd run build sauchốtQuad/enums đạtTypeScript/Vite21modules, JS230.23kB/gzip72.30kB/CSS6.07kB/gzip1.81kB. Reruntypeonlykhôngđổibundlehash. Khôngsửa source/tests saufinal916; frontendtypeonlyđãbuild, core/CLI/schema/dependency giữ. Auto-review chấpnhận localhost/TestClient/junction/hiddenprocess, khôngrejection. Browsernetwork/HTTPnegativecases đãkiểm; lỗi415/500 chủđích khôngReactcrash.

**Bàn giao:** tích07.07–09/AUX07.01/cổng07;53main+7AUX/110ID/109active/1skip/5optional.07.07 chiaa/b vì7tệpimpl-tests,07.08 chiaa/b vì8tệp; khôngcộngtaskconvàparenthai lần. AUX07.01 thêmđúng1task ràtheouser. ĐồngbộREADME/AGENTS/plan/todo/MVP/projectmap/imagecontract/API/audit/progress; giữhistoricalcheckpoints/progress. Next08.01 fullconfig/góc/confirmed/revisionCAS; chưaM2renderUI/detectUI/debugUI/multipagemutation/PDF. Cácảnhruntime/source/screenshots khôngGit, khôngsendảnhra ngoài; khôngcommit/push/deploy.

**QA bàn giao cuối:** `.tmp/qa_phase07_docs.py` đạt15tài liệu/183link nội bộ,53main/7AUX/110ID, đủ9rowaudit/9task07checked/07.07a-b và07.08a-b khôngcộngparent;08.01 và5optional chưa tích. Kiểm2page6file snapshotUIrestart,4viewport, screenshotsJPEG, DOMlabels/console/sourceimg_004, core/CLI/requirements hashes khớpM1. Data/ảnh/results/scripts.tmp ignored; source/tests/audit khôngignore. CentricMem lưu thành công shelf document-scanner/session `sessions/2026-10-17T053624Z-mcp-5a103d.md`, chỉ tóm tắt kỹ thuật/khôngảnh. Source/tests giữ sau final916. Localhost8000/5173 và browserdeliverable vẫn mở cho user xem.

## 17/10/2026 — MVP08.01–02: config CAS và service render snapshot

**Phạm vi:** user yêu cầu hai task đầu giai đoạn08. Đã đọc todo/plan, API/image-contract, audit07 và code config/geometry/render/storage. Áp dụng using-agent-skills, incremental implementation, TDD, API/interface, security, Ponytail và review/documentation; không thay thuật toán, preset, schemaVersion1, dependency hoặc frontend. Không tự làm08.03 renderHTTP/canvas/debug/export. MVP08.01 chia a/b do thực tế6tệp implementation/tests, không cộng lại parent.

**MVP08.01:** thêm PUT /api/v1/sessions/{sid}/pages/{pid}/config qua update_page_config. Transaction lấy writer lock SQLite bằng UPDATE session giữ nguyên timestamp trước read/CAS. Lookup đúng owner, expected_revision cũ trả409 kể cả no-op, details chỉ expected_revision/actual_revision. Parse full config theo nguồn thật sau EXIF và estimate_warp_size thật khi có góc để kiểm Adaptive active; không clamp block hoặc merge config cũ. Thay payload canonical tăng revision đúng1 và timestamps config/page/session cùng commit; no-op giữ tất cả. Góc thiếu confirmed dùng false/draft, true cần gửi rõ cùng quad hợp lệ. Inactive parameters vẫn lưu/tăng revision nếu đổi; response effective_config/inactive_fields có validationcontext nguồn thật. sid/pid sai/thiếu/khác owner404; config/quad/nonfinite400 sanitized; error envelope/OpenAPI không422 giả.

**MVP08.02:** render_page(engine,store,sid,pid,expected_revision) blocking. Read transaction chụp PageConfig frozen/StoredArtifact/dimensions, gate confirmed/revision và source role/owner. Verify source path/bytes/hash rồi decode internal PNG RGB/noEXIF/singleframe/dimensions/≤16MP; không gọi upload normalize_image hoặc áp15MiB vào PNG nội bộ. CPU ngoài DB: render_document manual corners từ full source → enhancement/rotation → encode_render_images full và preview từ final pixels. Không detector bypass xác nhận, không dùng render cũ làm nguồn. Lỗi lõi có RenderProcessingError, lỗi file/source có ArtifactFileError.

Transaction cuối lấy writer lock rồi kiểm lại owner/revision/sourceID/dimensions/config trước bất cứ publish nào; config đổi/xóa page/xóa session trong lúc CPU chạy đều từ chối, không tạo file kết quả. Giữ lock qua ghi encoded bytes/register full+preview cùng page/revision/commit để không có khe hở gate→publish; không OpenCV/encode trong lock. Lỗi write/register/commit rollback và dọn đúng file mới chưa tham chiếu; source/config/oldartifact nguyên. Không có transaction nguyên tử chung file+DB; crash hoặc cleanup lỗi vẫn có thể để orphan, chưa GC. Render không tăng revision/timestamps. Thay config giữ render_revision cũ để đánh dấu stale. Timings source_load/encode/core.* đúng lượt; core.total chỉ core, không tổng end-to-end. Chưa persist debug/histogram hoặc ánh xạ HTTP service errors cho đến08.03/09.

**TDD và kiểm thử:** config RED24failure vì chưa có route →42passed4.80s với18sessionAPI; service RED thiếu module →19passed5.42s. Rà soát thêm3ca inactive/OpenAPI/source role/core error: **25configAPI+21service=46ca mới**, focused cùng18sessionAPI **64passed9.87s, -W error**. Có full replacement/defaults/no-op/timestamps, góc tự giao/winding/trùng/ngoài miền/NaN/Infinity, active block vượt warp, owner UUID404, concurrent CAS chỉ1success+1conflict, commitfault rollback. Render kiểm3mode/rotation/pixels/hash/preview/repeat từ source, unconfirmed/stale chặn trước core, config/page/session mutation lúc CPU bị chặn, process/encode/write/register/commit faults giữ5artifact cũ, source role/hash/dimensions/mode/EXIF/decoder sai. Random JPEG3000×2000 hợp lệ tạo normalizedPNG>15MiB; service render2400×1600/preview1000×667, preview bytes khớp resize độc lập từ full đã lưu.

Hồi quy đầu959passed138.14s; sau thêm3ca review, lệnh `backend/.venv/Scripts/python.exe -m pytest -c backend/pyproject.toml backend/tests -q --tb=short --basetemp=.tmp/final08-01-02` → **962passed133.48s**, không skip/nới checks. Không đổi source/tests sau lượt cuối. Frontend không đổi nên giữ bằng chứng typecheck/build/browser07, không chạy lại vô ích. TestClient trong sandbox bị treo trước collection; dừng đúng tiến trình test rồi chạy cùng lệnh với auto-review cho phép như các giai đoạn trước, không có approval rejection.

**Runtime thật:** `.tmp/verify_mvp08_01_02.py` chạy hai tiến trình Uvicorn trên cổng riêng/DB riêng, không thêm probe routes vào app sản phẩm. Upload WrongEXIF.jpg qua HTTP480×640, service từ chối draft; PUT quad toàn khung/confirmed=true/rotation90 →revision1, no-op giữ1, stale409 và config sai400. Gọi service trực tiếp tạo full/preview639×479; GET artifact đúng bytes/hash của core. PUT rotation180 lên2 giữ render_revision1 và service từ chối expected1. Shutdown/start tiến trình mới cùngDB giữ toàn detail/config/revisions/hash hai PNG. Evidence/config/sourcehash/timings/OpenAPI6path và2PNG ở experiments/results/mvp08-01-02-verified/ (ignored). Đã mở full: chữ dựng lại sau rotation90, còn cả nền bàn vì phép thử chọn toàn khung; không gọi đây là cắt đúng mép giấy hoặc detector accuracy. Không dùng một ảnh này kết luận tổng quát.

**Dev và bàn giao:** reload backend đã xác minh đúng helper/command line, graceful stop/start Hidden; cả4session metadata trước/sau nguyên, không sửa config tài liệu user. Backend8000/Swagger có configAPI; Vite5173 giữ, UI vẫn nhập/xem nguồn. Stopfile mới `.tmp/phase08-backend.stop`, launcher88956; bằng chứng reload trong .tmp/phase08-dev-reloaded.json. Tích08.01a/b/parent và08.02: **55main+7AUX/110ID**, giữ skip01.08/5optional. Next08.03 render qua executor/API; checkpoint08-C1/M2 chưa đạt. Đồng bộ README/AGENTS/plan/todo/MVP/projectmap/API/image-contract; không commit/push/deploy hoặc gửi ảnh ra ngoài.

**QA bàn giao08:** `.tmp/qa_phase08_01_02.py` đạt15tài liệu/191link nội bộ,55main/7AUX/110ID,08.01a/b không cộngparent,08.03–10 và5optional còn chờ; xác minh2PNG/sourcehash/config/revision/restart và4session dev không đổi. Hash core/CLI/requirements khớp mốcM1, nguồn/tests giữ sau full962. Ảnh/DB/results/.tmp ignored; services/tests không bị ignore. Helper QA đọc JSON của Windows PowerShell5 bằng UTF-16 theo BOM, không đổi mã sản phẩm. CentricMem lưu card kỹ thuật thành công shelf document-scanner tại sessions/2026-10-17T063337Z-mcp-267ee3.md, không đính kèm ảnh.

## 17/10/2026 — MVP08.03–04: render HTTP và mapping canvas

**Phạm vi:** user yêu cầu task3/4 giai đoạn08. Đọc using-agent-skills, todo/dependencies, API/image-contract, service render/executor, API errors/schemas và cấu hình frontend. Áp dụng incremental/TDD/API/Ponytail, frontend/browser verification, security/review/documentation theo phần việc. Không thêm editorUI, tự detect, persistence debug, PDF hoặc thư viện mới. Không sửa core/CLI/configbaseline/DB schema/dataset. Task03 dùng4tệp API/errors/tests; task04 dùng3tệp helper/test/package script, cập nhật quy mô từ dự kiến.

**MVP08.03:** POST /api/v1/sessions/{sid}/pages/{pid}/render nhận RenderRequest strict (expected_revision/debug), async dispatch nguyên render_page qua app.state.processing dùng cùng import. Trả RenderRead với page/revision, UUID full/preview, dimensions sau rotation, warnings/timings. Tái dùng service gates đã kiểm: nguồn normalized giữ nguyên, confirmed/revision trước core, CAS/snapshot trước publish, cleanup khi lỗi. Chưa xác nhận409/PAGE_NOT_CONFIRMED, stale409/REVISION_CONFLICT có expected/actual; owner/ID404, body400, overload429. RenderProcessingError→500/PROCESSING_FAILED chung/log server, file/DB giữ500/STORAGE_FAILED. Core chạy ngoài event loop; health vẫn200 khi CPU bị chặn. debug=true hiện render full/preview và trả DEBUG_NOT_AVAILABLE rõ; không silently drop yêu cầu hoặc tạo refs giả/bật coredebug rồi vứt stages. Lưu debug/histogram còn09.05–06, không mở rộng sớm.

**TDD HTTP:**21ca RED vì route chưa có →GREEN; focused configAPI25+renderService21+sessionAPI18+executor5+renderHTTP21 = **90passed11.92s (-W error)**. Ba mode/rotation khớp core PNG và metadata owner/hash/revision, restart TestClient giữ detail/output; strictenvelope, UUID/membership, draft/stale chặn core; update config và xóa page khi worker bị chặn không publish; render và upload cùng429 khi queue đầy, health200; processingfaultsanitized/workerphụchồi; OpenAPI7path/8method/no422 và debugwarning. `backend/.venv/Scripts/python.exe -m pytest -c backend/pyproject.toml backend/tests -q --tb=short --basetemp=.tmp/full08-03-04` → **983passed139.55s**, tăng21; khôngskip/nớichecks, không đổi backend source/tests sau lượt này.

**Runtime HTTP:** `.tmp/verify_mvp08_03_04.py` chạy app sản phẩm trên cổng/DB riêng, không thêm probe routes. WrongEXIF.jpg480×640 upload qua multipart → draft render409 →PUT fullframe quad/confirmed/rotation90 revision1 →POSTrender200 →GET2PNG639×479 khớp bytes/hash core. No-op giữ1; stalePUT409/configsai400. Đổi rotation180 lênrevision2 giữ oldrender1; HTTP renderexpected1 trả409. Shutdown/start tiến trình Uvicorn thứhai cùngDB giữ detail/config/revision/source/outputhashes. verification.json/render.png/preview.png ở experiments/results/mvp08-03-04-verified/ ignored. Fullframequad chỉ thử plumbing/rotation, không phải nhãn mép giấy hay đánh giá detector. Mốc này gọi render qua HTTP thật, khác service direct ở mốc01–02.

**Checkpoint08-C1 — đạt:**

| Task | Bằng chứng nghiệm thu |
|---|---|
| 08.01 config CAS | 25HTTP tests, actual source/warp dimensions, fullreplacement/no-op/inactive/timestamps/concurrentupdate/rollback/409 |
| 08.02 snapshot service | 21service tests, confirmed/sourcehash/full-preview, config/page/session đổi giữa CPU khôngpublish, encode/write/commitfault giữsource/config/oldartifact |
| 08.03 render HTTP | 21HTTP tests, sharedworker/health/429, full→GET bytes, errors/OpenAPI, runtime2process restart |

Không coi checkpoint này là M2/renderUI/debug hoặc chất lượng detector. Nợ img_004 ăn bàn/6ảnh1doc/test0 giữ nguyên.

**MVP08.04:** cornerGeometry.ts xuất createContainTransform/sourceToCanvas/canvasToSource/normalizedToSource/sourceToNormalized/normalizedToCanvas/canvasToNormalized/clientToCanvas/getCanvasBackingSize. Transform frozen dùng source sauEXIF; contain theo W/H, normalized theo W−1/H−1, giữ subpixel. Clientrect có tỷ lệ CSS và offset; pointer không nhân DPR. Backing max1/round(CSS×DPR), scaleX/Y tính lại từ backing thật để tránh lệch khi CSS/DPR lẻ; caller dùng ctx.setTransform sau resize, không scale tích lũy. Reject nonfinite/invalid dimensions/zero CSSrect/DPR/overflow bằng RangeError. Mapping là phép đổi tọa độ liên tục, có thể trả normalized ngoài01; không tự clamp/hit-test/sort/validatequad. Gate letterbox/drag/quad còn05–06, backend giữ validation thật.

**TDD frontend:** RED module chưa có; thêm helper và npm.cmd test dùng **native Node24.15.0** runner với cornerGeometry.test.mjs import moduleTS thật, không Vitest/@types-node/dependency/loader riêng. **27passed148.12ms**, kiểm exact W−1 endpoints, portrait/landscape/2×2/source8triệu×2, CSSsize lẻ/clientrectscaled/roundtrip/resize, DPR1/1.25/2, unbounded mapping/no mutation và invalidinputs. App engine range giữ; README nói rõ npmtest đã kiểm với Node24 có nativeTS, không hứa Node20 chạy lệnh test này. Typecheck và build đạt, Vite21modules192ms, JS230.23kB/gzip72.30/CSS6.07/gzip1.81; bundleindex-4Huu2nud giữ vì helper chưa được UIimport. Không thêm CSS/React component hoặc nút quét.

**Browser canvas thật:** biên dịch chính cornerGeometry.ts bằng TypeScript hiện có vào .tmp/canvas08-check/, staticprobe localhost5184 riêng. CUA click nguồn dọc480×640/ngang1536×1024, CSS320×400/640×360, backingDPR1/2: đủ **8tổhợp/22draw**,5điểm mỗi lượt gồm4biên và1subpixel. DOMreport đo client→canvas→normalized→canvas, **maxerror5.684341886080803e−14CSSpx ≤1**; getImageData xác nhận pixelxanh tại handlecenter theo backing. Console error/warn rỗng, screenshot đã mở kiểm trực quan. DevicePixelRatio thực1; đây là ép backingDPR1/2 để kiểm math/Canvas2D, không claim có hai thiết bị vật lý. canvas-browser.json/.jpg lưu cùngruntimeevidence. Trang thử có nhãn rõ chưa là editorUI, không dùng ảnh cá nhân; tab và serverprobe đã đóng sau lưu bằng chứng.

**Bàn giao:** tích08.03/04 và checkpoint08-C1, **57main+7AUX/110ID**,08.05–10/08-C2/M2 cònchờ; next08.05 overlay/handles. README/AGENTS/plan/todo/MVP/projectmap/API/image-contract đồng bộ; không thêm task rà phụ. Backenddev8000 reload đúng helper/commandline sau graceful stop,4session metadata nguyên; stopfile hiện tại .tmp/phase08-api-backend.stop/launcher69104, Vite5173 giữ. Swagger có renderAPI; UI chính vẫn nhập/xem nguồn cho đến overlay/handles/save/renderUI các task sau. Không commit/push/deploy hoặc gửi ảnh ra ngoài.

**QA bàn giao03–04:** .tmp/qa08_03_04.py đạt15tài liệu/193link nội bộ,57main/7AUX/110ID, checkpoint08-C1 đạt và08-C2/08.05–10 còn chờ. Kiểm runtime HTTP/restart/2PNG,8tổhợp/22draw canvas,4session dev nguyên; hash core/CLI/requirements khớpM1, source/tests giữ sau full983 và frontend27/typecheck/build. Ảnh screenshot do browser trả JPEG đã đặt đúng tên canvas-browser.jpg, không chỉnh pixels. Probe5184 đã dừng. CentricMem card kỹ thuật lưu thành công shelf document-scanner tại sessions/2026-10-17T105742Z-mcp-52debd.md, không ảnh.

## 17/10/2026 — MVP08.05–06: overlay và kéo góc trên UI thật

**Phạm vi:** user yêu cầu task5/6 giai đoạn08. Đọc using-agent-skills, todo/dependencies, image/API contract, geometry backend và helper04, SourcePreview/ScannerPage/styles/types. Dùng incremental/TDD/frontend/browser/review/Ponytail và documentation theo công việc. Task05 thực tế3tệp (CornerEditor/SourcePreview/styles), task06 dùng4tệp (component/helper/tests/styles), tổng5tệp implementation/tests liên quan; không cần chia thêm task con. Không thêm dependency, HTTP route, detector, save-confirm/renderUI hoặc task phụ. Góc nháp chỉ local; persisted config/confirmed/revision không thay trong lượt này.

**MVP08.05:** CornerEditor đã vào viewer nguồn thay ảnh tĩnh. img native lấy normalizedPNG, kiểm natural dimensions đúng PageRead trước bật editor, loading/error/retry giữ; object-fit contain và canvas overlay dùng cùng contentbox. Canvas chỉ mask evenodd ngoài polygon/stroke, không đổi hay encode pixel nguồn. Bốn button44CSSpx/ID0–3 vẽ theo normalized source W−1/H−1; key không đổi khi kéo qua nhau. Init structuredClone persisted corners nếu có, không thì inset5%; SourcePreview key page/revision/normalized artifact khiến đổi trang/nguồn/config mới không giữ góc cũ. ResizeObserver đo CSScontentbox, DPRresize/matchMedia và actualbacking/CSS setTransform mỗi draw; wrapper chừa24px cho handle. Không lấy thumbnail làm geometry hoặc áp EXIF/xoay lại.

**MVP08.06:** hitTestCorner gần nhất/radius22CSSpx, tie ID thấp; blankletterbox không nhảy góc. Primary/button0 Pointer Events bắt capture trên stage, snapshot before/dirty/offset điểm nắm, chỉ update cùngpointerId. moveCorner đổi đúng một điểm/clamp01, không sort. Pointerup lấy điểm cuối/release; pointercancel/lostcapture/Escape/windowblur/focusout/resize/DPR đổi khôi phục before corners/dirty, clear ref trước release nên lostcapture sauup không undo. Cleanup listeners khi unmount, DOM tự nhả capture khi bỏ stage. Arrow1CSSpx/ShiftArrow10, Escape hủy; keyboardfocus/aria-describedby/message role=status. Invalid draft vẫn vẽ để sửa, strokeerror+thông báo cụ thể, không chỉ báo màu. Lưu/xác nhận tách draft/persisted thuộc08.07; chưa gửi PUTconfig/POSTrender.

validateDraftQuad mirror validate_quad:4finite/boundedpoints →allpair duplicate1e−6D →edges1e−3D →near-collinear →oppositeintersection →shoelace area1e−6D² →convex →winding. Distances trên pixel nguồn, topology chia cùng D; không UVEuclid hoặc vùng10% detector. Giữ9reasoncodes/messages, không chữa thứ tự góc tay; đây chỉ là preflight, backend vẫngate lầncuối khi save.

**TDD/đối chiếu:** RED thiếu exports →51frontendtests đạt (27cũ+24mới). Có hit radius/tie/letterbox, clamp/keepID/no mutation, valid diamond/perspective/tinyquad, invalid duplicate/shortedge/collinear/bowtie/concave/reverse/outbounds/nonfinite/count, source anisotropic/2×2/thin. Một kỳ vọng test trên source2×8triệu ban đầu đặt SHORT_EDGE; đối chiếu trực tiếp core trả DUPLICATE_POINTS vì ngưỡng duplicate đã lớn hơn chiều rộng1pixel, sửa kỳ vọng đúng thứ tự gate, không nới thuật toán. `.tmp/verify08_05_06.py parity` tạo936quad/6source sizes, Node moduleTS thật so corecodes: **936khớp/0mismatch**, gồm86VALID/284SELF_INTERSECTION/16DUPLICATE/179NON_CONVEX/11SHORT_EDGE/66INVALID_WINDING/294DEGENERATE; đây là conformance, không accuracy ảnh tài liệu. Python core `test_geometry.py -W error` **216passed0.92s**. Backend không thay đổi, full983 là mốc08.03–04; không chạy lại cả suite vô ích.

`npm.cmd test` cuối →**51passed161.98ms**; `npm.cmd run build` gọi typecheck rồi Vite **23modules156ms**, JS238.98kB/gzip75.64, CSS6.88kB/gzip2.04, index-DlMuWrd8/index-C3tFepI8. Không thêm React testframework/loader; native Node24.15.0 đã dùng. CSS source-stage cũ được bỏ vì SourcePreview đã dùng editor. Không đổi source/tests sau lượt chốt (chỉ tài liệu/evidence).

**Browser sản phẩm:** CUA mở localhost5173 với WrongEXIF đã lưu, không upload hoặc sửa DB để thử. Native mouse kéo0 theo60×70CSSpx thay đúng0,1–3 nguyên; kéo ra ngoài canvas clampu0 và capture khôngkẹt; kéo0 qua cạnh tạo SELF_INTERSECTION, message đúng vàID0–3 giữ. ArrowRight/ShiftArrowDown dịch đúng1/10CSSpx (tọa độviewporty có đổi do autoscroll nên so normalized/source mapping, không lấy y tuyệt đối). Reload đổi về góc mặc định vì nháp chưa lưu, click không kéo giữexact.05/dirtyfalse. Devlogs error/warn rỗng. browser-actions.json/bowtie.jpg/editor.jpg ghi bằng chứng, screenshot đã mở xem4handle/mask/source/status.

Hai lỗi đã phát hiện/sửa bằng runtime: (1) nhấn không kéo từng làmu=.04999999999999997 vàdirtytrue do round-trip float; thêm bỏ delta≤1e−6CSSpx trước chuyển động thật, tái kiểm click giữu=.05 vànhãn banđầu. (2) grid mobile1fr/min-content khi3trang làm viewer rộng400px vàtràn320; đổi track minmax(0,1fr), giữ page-list cuộn ngang bên trong thay vì giấu overflow. Retest6trườnghợp portrait480×640/landscapefixture4×2×viewport320/768/1440 đạt, normalized góc nguyên và maxhandlecenteralignment **.02066652CSSpx<1**, document khôngtrànngang. Viewport capability tác động tab active; lượt đo đầu còn ở tabprobe không dùng để kết luận, đã đóng probe/chuyển đúng tab và ghi lại6viewport thực. Override đã reset trước bàn giao.

**Pointer/DPR probe:** tạm tạo hai filehtml/tsx dưới frontend để Vite chạy chính CornerEditor với PageRead thật quaGET. UI controls phát pointerType=touch synthetic trong lúc pointer của nút điều khiển đang active thật để setPointerCapture vẫn thực thi bình thường; không bỏ qua capture hoặc thêm testhooks vào sản phẩm. Sáu ca touchmove/cancel/lostcapture/Escape/blur/secondary: touchmove thay đúng0, các ca hủy/secondary giữ before, cả6draggingfalse/capturedfalse; có JSON. Không claim đã thử màn hình cảm ứng vật lý. Forced windowDPR1→2 trong tabprobe tạo backing370×432→740×864; resizeCSS590×432→1180×864, normalizedpoints nguyên. Đọc actualcanvaspixel qua nút riêng trong probe:alpha ngoài140/trong0 ởcả3state, không có mask giả. DeviceDPR thật1; chưaphysicalHiDPI. CUA evaluate chỉđọc DOM, canvas.getContext không được facade cung cấp nên việc đọc bitmap diễn ra trong trang thử do mình tạo, kết quả xuất DOM rồiđọc. Probe/tab đóng, hai filetạm archive dưới resultsignored rồixóa khỏifrontendroot.

**Giữ nguồn:** `.tmp/verify08_05_06.py before/after` GETmetadata+bytes cả3sourceartifact/trang trước/sau. **4session/7page/21artifact SHA-256 và toàn detail/config/revision/timestamps nguyên**, không gửi ảnh ra ngoài. Evidence experiments/results/mvp08-05-06-verified/ gồm before/after/quad-parity/pointer-lifecycle/dpr-mask/layout/browser-actions/console vàJPEG; ảnh nguồn cá nhân/DB/results/.tmp tiếp tụcignore. Không dùng một tờ giấy hoặc syntheticfixture để kết luận tổng quát.

**Checkpoint08-C2 — đạt:**

| Task | Bằng chứng nghiệm thu |
|---|---|
| 08.04 mapping |27tests cũ giữ,source/CSS/normalized/DPR và6responsivecases dùnghelperthật,alignment<1CSSpx |
| 08.05 overlay |imgnormalized/maskalpha140–0/4stableIDs,portrait+landscape/resize/DPR,21sourcehash nguyên |
| 08.06 pointer/preflight |24tests mới/936coreparity/native mouse-clamp-bowtie-keyboard/touchsynthetic6ca/cancel-restore,khôngkẹtcapture |

**Bàn giao:**59main+7AUX/110ID,08.05–06/08-C2 tích; next08.07 draft/persisted vàlưu/xácnhận fullconfig/CAS,08.08 renderUI/M2 cònchờ. Đồng bộ README/AGENTS/plan/todo/MVP/projectmap/API/image-contract; giữcácmốclịchsử. Backend8000/Vite5173 giữchạy, khôngrestart backend vìkhôngđổi; stopfile .tmp/phase08-api-backend.stop vẫnnhư03. Tab sản phẩm giữ làm deliverable vớiWrongEXIF/gócbanđầu, viewportđãreset, không lưuquad thử. Không commit/push/deploy hoặc nhắn bênngoài; chỉmemorysummary kỹthuật theoCentricMem, khôngảnh.

**QA bàn giao05–06:** .tmp/qa08_05_06.py đạt15tài liệu/197link nội bộ,59main/7AUX/110ID, checkpoint08-C2 đạt và08.07–10/08-C3 còn chờ. Kiểm936quad parity,6responsivecases/6pointercases/maskDPR, maxalignment.02066652CSSpx,21hashnguồn nguyên; core/CLI/requirements khớpM1, fileharnessroot đãdọn, ảnh/DB/results/.tmp ignored. CentricMem card kỹ thuật lưu thành công shelf document-scanner tại sessions/2026-10-17T112124Z-mcp-ffd092.md; không đính kèm ảnh.

## 17/10/2026 — MVP08.07–08: lưu/xác nhận góc và render từ giao diện

**Yêu cầu:** làm task7 và8 giai đoạn08. Đọc lại task/phụ thuộc/contracts và dùng using-agent-skills, incremental/TDD/frontend/API/browser/review/documentation/Ponytail theo workflow đã áp dụng. Không đổi thuật toán, backend, defaults, dataset hoặc phạm vi MVP. Hai task chia a/b vì số tệp thực tế lớn hơn dự kiến; không cộng task con vào tổng task chính.

**08.07:** CornerEditor nhận controlled full draft, góc kéo/keyboard vẫn source-normalized/W−1/H−1 và không sort. State tách config/revision server khỏi draft trong pageRenderState; góc null khởi tạo inset5% chưa xác nhận. Sửa góc/toàn ảnh bỏ confirmed; cancel phục hồi toàn config trước kéo, gồm confirmed. “Đặt lại góc đã lưu” phục hồi snapshot persisted; “Lưu nháp” gửi confirmed=false; “Xác nhận vùng” explicit true. Đủ inactive/rotation/mode/tham số được gửi trong PUT thay vì merge mặc định. Invalid quad giữ để sửa nhưng không save/confirm/render. Chuyển trang/tải lại bỏ nháp chưa lưu, có nhắc trên editor; mỗi lần mở GET detail mới trước khi mở mutation, không lấy revision cũ từ page list.

**08.08:** usePageRender nối store bằng useSyncExternalStore và cleanup generation, chạy trong StrictMode. Nút quét cần draft confirmed/hợp lệ/state đã đối soát: PUT full config/CAS trước → kiểm response page/revision/payload → POST đúng revision trả về nếu draft không đổi → chỉ nhận render đúng page/revision/operation/edit counter. No-op PUT vẫn CAS. Edit khi đang PUT giữ draft mới và nhận persisted snapshot đã commit, không tự POST tiếp; edit trong render bỏ kết quả muộn. Đổi trang/unmount vô hiệu hóa response editor cũ. Không auto-retry mutation hoặc giả abort HTTP là dừng thread/rollback. Lỗi/mất response chặn mutation tới khi GET “Đọc lại cấu hình” thành công, giữ nháp nhưng bỏ xác nhận để kiểm lại. Kết quả cũ giữ ảnh/nhãn revision riêng và báo stale; preview có loading/error/retry.

**Giới hạn rõ:** GET detail chỉ có render_revision, chưa UUID render/preview; lần mở lại hiển thị nhắc tạo lại bản quét explicit để xem ảnh, không bịa kết quả/cache/history API. Cấu hình/ảnh nguồn vẫn persist. Preview thường chỉ cạnh1000, dimensions nhãn là full sau rotate. Chưa view so sánh/zoom08.09, chưa nghiệm thu toàn giai đoạn08.10/M2, chưa UI detector/đổi mode09 hoặc export11. Lõi homography không sửa; giấy có nếp gấp vẫn không được dewarp.

**Kiểm chứng tự động:** TDD state RED do module chưa tồn tại, GREEN10ca rồi bổ sung cancel/full snapshot và config response sai page/revision/payload; native Node24 chạy **64tests đạt219.9211ms**:51mapping/quad cũ +12state/race +1API wire. Ca state gồm explicit confirm/fullconfig/inactive, saved draftfalse/invalid quad, edit trong save/render, duplicate click, unmount/switch, foreign page/revision, unknown commit và GET cũ sau reconnect. API wire dùng native fetch boundary kiểm JSON/PUT/POST/returned revision/no retry; đã sửa ApiError parameter property thành field assignment để native Node strip-only chạy đúng module thật. Không thêm dependency hoặc framework test. `npm.cmd run build` gồm typecheck đạt;25modules169ms, JS245.90kB/gzip77.49, CSS7.30kB/gzip2.13; index-CHHN4pjg.js/index-F9Md2zO2.css.

Backend không đổi; chạy lại **67tests config_api/render_api/render_service -W error đạt11.66s** với SQLite/temp/executor thật. Full983 giữ bằng chứng08.03–04, không tuyên bố đã chạy lại ở lượt này. 936quadparity/216geometry/DPRmask/6responsivecases giữ bằng chứng05–06.

**Runtime API thật:** `.tmp/verify08_07_08.py before` chụp metadata/hash toàn bộ5session/7page/21sourceartifact đang có, rồi tạo riêng tài liệu “Kiểm chứng08.07–08 · quét tay” với2trang: ảnh development1536×2048 và fixtureEXIF6 normalized64×96. Không sửa config của tài liệu user để thử. Trang thử tạm dùng chính ScannerPage/CornerEditor/hook/client, wrapperfetch chỉ ghi request và giữ/drop response hoặc trả500 có kiểm soát; yêu cầu bình thường vẫn gọi backend thật. Request ghi fullconfig và expected_revision đúng; confirm lần đầu0→1, fullimage unknown commit→2, chọn góc tay→3; trangEXIF lưu nháp0→1/confirm→2/render63×95.

**Ma trận browser:**

| Ca | Kết quả quan sát |
|---|---|
| Confirm/render/sửa sau confirm | PUTfullconfig/POST revision1, preview thật; ArrowRight bỏ confirmed, nút quét khóa, oldpreview có nhãn cũ |
| Edit trong PUT bị giữ | Góc mới giữ unconfirmed, response cũ chỉ cập nhật persisted, không có POST render tiếp |
| Edit trong render bị giữ | Bỏ response muộn, giữ UUID preview trước, có thông báo góc thay đổi |
| Đổi trang trong save/render | Giữ response200/returned=false trước chuyển rồi release; trang đích giữ ID/config/revision riêng, không nhận ảnh trang cũ |
| Render500 có kiểm soát | Giữ oldpreview, nhãn cũ, lỗi/“Đọc lại cấu hình”, không retryPOST |
| Mất response PUT sau commit thật | UI giữ revision1/chặn retry; GET đối soát thấy revision2, giữ góc fullimage nhưng false; confirm lại no-op revision2 |
| Lưu nháp/toàn ảnh/reset | Draftfalse persist, fullimage normalized0/1, reset lấy fullconfig đã lưu; chuyển về trang đọc config mới |
| Cancel sau xác nhận | Touchsynthetic dùng activepointer thật→move→Escape: trước/sau points và confirmed=true giống hệt, capturefalse/draggingfalse |
| Mở tab sản phẩm mới | Config/góc/revision3 đọc lại đúng; explicit render ra full1076×1281, preview840×1000, stale=false/image load đạt |
| Controls responsive mới | Viewport thực320×800/768×800, scrollWidth320/753, controls nằm trong chiều rộng, confirmed không đổi; reset viewport sau thử |

Lượt chuyển trang đầu tiên response tới trước khi wrapper giữ nên không dùng lượt đó làm bằng chứng controlled delay; đã chạy lại với record held=true/returned=false trước chuyển cho cả config/render. Touch vẫn synthetic, không claim thiết bị vật lý. Harness entry bị HMR gọi createRoot lần hai khi bổ sung nút probe, có warning riêng ở tab thử; không phải lỗi sản phẩm. Tab sản phẩm mới không import harness, console error/warn **rỗng** (`product-console-fresh.json`). Temporaryhtml/tsx đã archive trong evidenceignored rồi xóa khỏi frontendroot; không testhooks trong sản phẩm.

**Ảnh/preview:** Tại trang sản phẩm thật, kéo0–3 theo mép tờ giấy, confirm3 rồi render từ normalized nguồn đầy đủ. Full1076×1281/preview840×1000; `.tmp/verify08_07_08.py after` GET bytes, kiểm SHA-256 với artifact metadata và encode_render_images từ full: preview PNG **khớp từng byte**. Nếp gấp/góc chọn tay chưa hoàn hảo vẫn hiện trong kết quả; đây là kiểm nối luồng, không phải accuracy. User5session/7page/21sourcehash và toàn metadata/config/revision/timestamps trước/sau nguyên. Tài liệu kiểm thử riêng2page giữ để xem. Không ảnh nào ra dịch vụ ngoài.

Evidence `experiments/results/mvp08-07-08-verified/` (ignored): before/after/seed/final-document, browser-actions/requests/cancel-confirmed/layout-new-controls, render-check/full.png/preview.png, screenshots failure/product-full/product-result/product-final và console/DOM/state. `.tmp` vàDB runtime vẫnignore. Core/CLI/requirements đối chiếu M1 trong QA cuối; backend dev8000/Vite5173 giữ, stopfile .tmp/phase08-api-backend.stop như trước. Tab sản phẩm có kết quả quét giữ làm deliverable; tab thử đã đóng. Không commit/push/deploy.

**Bàn giao:**61main+7AUX/110ID;08.07–08 tích hoàn thành,08.09–10 chưa tích; checkpoint08-C3/cổng08/M2 còn chờ09–10. Đồng bộ README/AGENTS/plan/todo/MVP/project-map/API/image-contract. Next08.09 so sánh/phóng to dùng full render UUID, giữ source/draft/revision gates hiện có. Nợ detector/dataset không thay đổi.

**QA bàn giao07–08:** `.tmp/qa08_07_08.py` đạt15tài liệu/200link nội bộ,61main/7AUX/110ID/5optional;08.09–10 và08-C3 vẫn chờ. Kiểm13browser evidence records,2responsivecontrols, cancel/full snapshot, heldresponses, fullconfig requests, preview/fullhash và21sourcehash nguyên; core/CLI/requirements khớpM1, harnessroot đãdọn vàruntime/privateevidenceignored. CentricMem card kỹ thuật lưu thành công shelf document-scanner tại sessions/2026-10-17T114658Z-mcp-9c0764.md, không ảnh/bí mật.

## 17/10/2026 — MVP08.09–10/AUX08.01: so sánh/zoom và rà mười task, M2

**Yêu cầu:** làm task9 và10 rồi dò cả10task giai đoạn08. Đọc lại using-agent-skills, task/phụ thuộc/MVP/contracts và workflow frontend/incremental/TDD/browser/review/docs/Ponytail đã áp dụng; debugging-and-error-recovery khi strictsuite lỗi. Giữ thuật toán/manual-vs-detect/config/HTTP/revision, không thêmdependency. AUX08.01 là yêu cầu rà10task, tăngAUX7→8; taskchính61→63, giữ110IDgốc/109active/1skip/5optional.

**09 hoàn thành:** ComparisonView dùng normalizedsource và **render_artifact_id fullPNG** cónhãn rõ, size/revision/stale/confirmed từstate07–08. ImageonLoad kiểm naturaldimensions đúngdescriptor/page,loading/error/retry. Fit dùngobject-fitcontain;100%CSS=fullsize,200%gấpđôi, nativeoverflow/tabindex/arrowkeys; nguồn luônfit, không dùngpreview718×1000 đểzoomfull1009×1406 và khôngrerenderCPU khizoom. “Quay lại chỉnh góc” focus0; edit vẫn bỏconfirmed/khóaquét/giữoldimage/stale,resetconfig phục hồi. Newartifactkey resetzoom/load. Hai cột desktop/một cột≤1023. Filesactual:ComparisonView,SourcePreview,CornerEditor,styles (4tệp,taskM). Từảnhuser hỏi đã sửa nhãn“Bốn góc hợp lệ”→“Hình học vùng hợp lệ”, nhắcdefault vùng thửchưa nhậnbiên; không giảdetector.

**TDD/kiểmfrontend:** trướcimplementation view/100% chưa có; sauimplementation quét thật sinhComparison vàzoom1control đúng. **64native Node tests đạt192.3675ms**,typecheck/build26modules174ms,JS248.13kB/gzip78.08/CSS8.16kB/gzip2.29,index-DNQKJ2D2.js/index-CAg3U14A.css. Không thêmtestframework hoặcunit lặp CSS; hành viComparison kiểm qua browser thật và natural/CSS/UUID/scroll data. State/CAS/race/APIwire tests vẫn chạy module thật.

**10 endtoend:** tạo tài liệu mới “Nghiệm thu giai đoạn8 · quét tay” bằngUI; filechooser nhập3ảnh exif_6.jpg/corners_rgb.png/detail-highlight.png (ảnhsyntheticlocal1200×1600 tạo bằngPillow/Arial18pxtext/highlight/fourcolours). Hộp chọn tệp chậm163s ởlượt này, không dùng làm benchmark app. UI báo3Đãlưu, chọn1/2fullimage+confirm+render,3kéo4góc bằngnativepointer+confirm+render. PortraitEXIF64×96→63×95,landscape96×64→95×63,detail1200×1600→1009×1406/preview718×1000. Backend không gọi detector ởmanual path. Browsernatural/CSSfit/100/200 cùngfullUUID;1009×1406→2018×2812, overflow2018×2812,ArrowRight/Down cuộn40/40. Returneditfocus0→ArrowRightconfirmedfalse/stale/quétkhóa,resetđãlưuconfirmedtrue/fit phục hồi. Các recordtrongbrowser-evidence.json.

**Responsive/DPR:** actualviewport320/768/1440×800 cóscrollWidth320/753/1425, khôngtrànngang; 320/768stacked và1440same-row, source/fullUUID/confirmed khôngđổi. Overrideđãreset. PrivateDPRprobe dùngchínhScannerPage+CornerEditor, chỉthêmbuttonépwindowDPR/đọccanvas, khôngmockcapture/render.1→2: CSS653×432,backing653×432→1306×864, normalizedquadnguyên, outsidealpha140/inside0, maxhandleerror **.016853226694040137CSSpx<1**. DPR2render/100%full1009×1406 đạt. DeviceDPR thật1; chưaHiDPI/touchphầncứngkhác. Probeconsole vàproductconsoleerror/warn rỗng. Probehtml/tsx archiveignored rồi xóa khỏifrontendroot/tabđóng; xóaentryHTML khiếnVitedevreloadtabroot nhưthường, config/rev1 đọc lại đúng vàexplicitrender lại cóComparison. Không cótesthook trongsảnphẩm.

**Raster/giữnguồn:** `.tmp/verify_phase08.py before/after` chỉGET/SQLite-read đểđốisoát, không nhập/sửa góc/render thaybrowser.7session/10page/30sourceartifact cũ giữ toànmetadata/config/revision/timestamps/hash. Newtestdoc3page táchriêng; source/full/preview quaartifactAPI/SHA-256 metadata khớp.3preview **byteequal** vớiencode_render_images từfull.4màuthực khácnhau/page đượcprojectsourcecenter→H→full,12mẫu sai sốkênh **0**; source EXIF cóJPEGcolour254/1 đượcgiữ đúng, khôngépexpected255 giả. FullPNGlưuevidence; ảnhkhôngra ngoài. Khôngdùngfixture đểkếtluậnaccuracy.

**Lỗistrictsuite vàsửa:** chạyfull-Werror đầu **981passed/2failed143.93s**; cả2 do test_detect_batch.py:82 `csv.DictReader(path.open(...))` khôngđóngtệp, ResourceWarning/PytestUnraisableExceptionWarning. Skilldebugging táihiệnfocusRED2failed3.10s. Sửa duy nhất test bằngcontextmanager/newline='', giữassert2rows vàmọicheckstage/hash/decision; khôngsuppress-Werror/skip hoặcđổi core.7batchtestsGREEN15.10s, sauđó full **983passed142.37s với-Werror**. Đây là testresourceleak, không lỗidetector; strictfull983 bao cả67config/render/geometry/executor/core/CLI/DB hiệncó. Khôngcầnrestartbackend vìchỉđổi test/frontend.

**RàAUX08.01:** [Audit10task](audit-phase-08.md) cóma trận08.01–10/code/evidence/lỗi/giới hạn. Chỉ nhữngca ghiởlượt này làđãchạy mới; heldresponse/dropaftercommit/500/cancel/touchsynthetic của07–08 giữevidencecũ vàstate/APIregressions hiệncó, khôngclaim browserđãrerunhếttấtcả. Snapshot/revision/CAS/confirmed/worker/cleanup/geometry/render/fullpreview gates đạt; khôngđổiHTTP8method7path/schemaVersion1/core/CLI/requirements/preset/dataset/nợdetector.

**Giới hạn/bàn giao:** GETdetail chưacóUUIDrender/preview đểtựmởkếtquảcũ, reopen UI cầnexplicitrender; hoànthiệnnhiềutrang10.07. Debug/detect/modeUI09,PDF11,packaging14 cònchờ. M2/cổng08/checkpoint08-C3 đạt trongphạmvihandscan; chưaaccuracy/autodetectUI/physicaltouchHiDPI.63main+8AUX/110ID; nextMVP09.01detectAPI/detectionrun. `frontend/tests/scanner-smoke.md` cóbướcrerun, evidenceignored `experiments/results/mvp08-final-verified/` cósnapshot/browser/raster/DPR/layout/console/3fullPNG/fit–100screenshots. README/AGENTS/plan/todo/MVP/projectmap/image/API đồngbộ;backend8000/Vite5173 giữchạy,stopfile .tmp/phase08-api-backend.stop nhưtrước; tabquétgiữdeliverable/viewportreset. Khôngcommit/push/deploy/nhắn bênngoài.

**QA cuối08:** `.tmp/qa_phase08.py` đạt17tài liệu/236link nội bộ,63main/8AUX/110ID/10task08/5optional; M2pass/next09.01. Kiểm10UIrecords,12colorprojections/3previewbyteequal,30hashnguồn nguyên, responsive/zoom/DPR vàcore/CLI/requirements khớpM1. QA từng bắt reportDPR đọcqua evaluatefacade trảdeviceDPRthật1 trongkhi privateapp đãforced2; khônghạassert2. Đãđọclạitừbutton trongchínhapp sau render/100%:windowDPR2/backing1306×864/fullCSS1009×1406 vànaturalđúng trongcùngDOMreport; thayreportbằnglượtđođúng. Khôngsửa sảnphẩm cho phépđo này. Probe đãarchive/dọnlại;productrender từconfigđãlưu giữtabComparison. CentricMem card kỹthuật lưu thànhcông shelf document-scanner tại sessions/2026-10-17T121157Z-mcp-eb8312.md, khôngảnh/bímật.

## 18/10/2026 — MVP09.01–02: API/UI nhận diện tự động

**Phạm vi và quyết định:** đọc lại plan/todo, image/API contract, audit08/05, algorithm-notes và phân tích hướng thuật toán5.5.1–5.5.3. Áp dụng using-agent-skills, incremental/TDD/API/frontend/browser/review/docs/Ponytail và deprecation-and-migration. Không thay core detector, công thức score hoặc dataset. Hai task được tách lát nhỏ như checklist, không thêm ID/AUX. Chọn bảng DetectionRun riêng vì nhiều lượt detect trên cùng nguồn/revision cần phân biệt provenance và không được ghi đè config đã confirmed. Migration chỉ mở rộng schema hiện hữu; dùng transaction SQLite sẵn có, không thêm framework/dependency cho một bảng.

**MVP09.01:** thêm DetectionRun/model/schema2 và migration tường minh6table/v1→7table/v2; nhận đúng schema mới idempotent, DB lạ vẫn từ chối, rollback DDL/version khi lỗi. Tách loader nguồn hiện hữu từ renders sang services/sources.py dùng chung: verifyPNG/hash/RGB/dims/noEXIF/load→BGRcopy, không áp quota upload lên PNG nội bộ. POST `/api/v1/sessions/{sid}/pages/{pid}/detect` qua sharedexecutor, body DetectRequest strict/debugdefaultfalse, trả DetectionRunRead mở rộng DetectRead. Có8path/9method; owner404/input400/quá tải429/core500PROCESSING_FAILED được sanitize, manual_required200.

Usecase chụp sourceartifact/revision trước CPU, gọi đúngmột lượt detect_document(debug=True) để giữ trialprovenance, requestdebug điều khiển lưu stagePNG/fullcontour attempts. Ghi sourcePNG/BGRhash, analysisdimensions, version/preset/trials/selected/descriptors/units/timings thực và UUID/hash/size/mode stage. debugfalse vẫn run/result/trials nhưng khôngstagePNG. Debugtrue có analysis/gray/blurred/overlay và từngtrialrawedges/closed hoặc regionmask. Finalgate kiểm session/page/sourceID/dims, giữ nguyên config/confirmed/revision/timestamps kể cả config đổi trong CPU. Ghi stage+run cùngmetadata transaction; lỗi ghi hoặc commit dọn đúngfile mới chưathamchiếu. Nhiều run cùngrevision có stageUUID riêng; GETdebug09.06 phải lấy run.metadata.artifacts, không gom mọi kinddebug/revision.

**MVP09.02:** DTO/client/hook hiện hữu thêm detect; SourcePreview có “Tự nhận diện vùng”/loading/status/scoreheuristic/warnings/version/runID. Góc đề xuất chỉ thay draftcorners/confirmedfalse, giữ mode/filter/inactiveparams; khôngPUT/render/auto-confirm/retry. manual_required/null dùng inset5% kéo tay được. Operation/page-instance/editcounter bỏ phản hồi khi đổi trang/unmount/reset/edit; sai nguồn/dims/geometry bị chặn, source_revision khác persisted yêu cầuGET. Lỗi detect giữdraft và cho thử lại/chỉnh tay; sửa góc xóa noteproposal. Confirm vẫn explicit qua PUT/CAS rồi render từfullsource.

**TDD và kiểm thử:** RED thiếu DetectionRun và store.detect trước triển khai; GREENfocused13tests (11API+2migration)3.92s. Kiểm hai run/stageUUID riêng/hash/trial/timing/config/timestamps nguyên; debugfalse/manual200; body sai/owner; coreerror sanitize; lỗi ghi stage thứhai; fault commit sau actualINSERT detection_runs; config sửa khiCPU giữ; pagedelete khiCPU khôngpublish; reopenrun/artifacts; executorhealth/queueoverflow429. Migrationv1data→v2 và rollbackDDL/version/retry có tests. Test portal ban đầu đóng nhầm TestClient.portal đã sửa reuse; latecommitfault được đặt sau actualINSERT để chứng minh rollbackpublish, không fault transaction đọc đầu. Không hạassert hoặc mockcore cho các ca nhận diện/stage chính.

Fullbackend: `backend/.venv/Scripts/python.exe -m pytest -c backend/pyproject.toml backend/tests -q --tb=short -W error --basetemp=.tmp/pytest09-full-final` → **996passed130.56s**. Frontend `npm.cmd test` → **68passed183.7648ms**, typecheck/build qua26modules169ms (JS251.15kB/gzip78.86,CSS8.29/gzip2.31). Controlled state tests có proposal-only/noPUT/render/inactive, manualfallback/networkerror, lateedit/reset/unmount, wrongpage/source/dims/rev/confirmed/quad. Không thêm dependency hoặc sửa lõi để đạt test.

**Runtime/migration thật:** trước restart snapshot8session/13page/39sourceartifacthash và SQLitebackup v1 qua backupAPI vào `experiments/results/mvp09-01-02-verified/database-before-v2.sqlite3` (ignored). Dừng backend cũ bằng stopfile, mở lại cùngDB với schema2, không reset. `.tmp/verify09.py after` kiểm mọi row cũ là tậpcon nguyên của DB mới:8sessions/13pages/73artifacts/13configs/0exports, FKcheckrỗng, SessionDetail và39hash nguồn không đổi. Lượt cuối xác minh11detectionrun và từngstagehash qua artifactGET thật; backup còn giữ. Backend8000 stopfile mới `.tmp/phase09-api-backend.stop`, Vite5173 giữ chạy.

**Browser thật:** tạo riêng tài liệu QA ba trang; anhtestnew612×460 proposed≈0.634709 (UI0.635); hai lượt runID khác/stageUUID tách; explicit confirm revision1→render201×285. img_0041536×2048 proposed_with_warning≈0.468352 (UI0.468/LOW_HEURISTIC_SCORE), vẫn ăn bàn; configpersistedrev0/cornersnull/false nguyên. Blank320×240 manual_required/NO_VALID_QUAD, inset5%false; ArrowRight sửa được và xóa note. Harness tạm dùng ScannerPage/API thật, giữ actual200 rồi mới editArrowRight hoặc đổi trang: response không ghi đè nháp/trang mới. Lỗi500 có kiểmsoát giữgóc và không forcedGET. Responsive320/768 khôngtràn, sáunút trongviewport/noteUUIDwrap, product/probeconsole sạch. Harness archive rồi xóa khỏifrontendroot; không có testhook trong sản phẩm. Finalproduct run307f7292-c4ae-4bcb-add0-1edaa8282f4b vẫn là draftfalse, trang được giữdeliverable/viewportreset.

**Giới hạn và bàn giao:**65main+8AUX/110ID, MVP09.01–02 đạt; nextMVP09.03. Checkpoint09-C1 cần09.03, cổng09 còn chờ. Debugrender09.05/GETdebug09.06/viewer09.07 chưa hiện thực. Thuật toán/nợimg_004/006/frame và6ảnh cùngdoc_01/test0 giữ nguyên; score không xác suất/accuracy. Lần này nối detector đã có vào ứng dụng, không chứng nhận chất lượng tổng quát. Evidence ignored gồm snapshot/backup/migrationcheck/runs/browser/requests/layout/console/screenshots; không gửi ảnh ra ngoài, khôngcommit/push/deploy. README/AGENTS/plan/todo/MVP/projectmap/image/API đồng bộ.

**QA cuối09.01–02:** `.tmp/qa09_01_02.py` đạt17tài liệu/238link nội bộ,65main/8AUX/110ID/5optional, đúng2task09 và checkpoint09-C1 còn chờ.11run/118stageUUID riêng/hash thật,12UIrecords có so góc trước-sau giữresponse,8session/39sourcehash cũ nguyên; OpenAPI8path/9method, core/CLI/requirements khớpM1. QA phát hiện helper ghi case chưa phản ánh trong array evidence đã lưu: đã chạy lại actualhold/edit/pageswitch/500/ảnhkhó, ghi trực tiếp và kiểm assertions trên file cuối; không bỏ kiểm chứng. Harness lại được dọn; không thay sản phẩm. CentricMem đã lưu card kỹthuật shelf document-scanner: sessions/2026-10-18T023109Z-mcp-bd6e59.md, không ảnh/bí mật.

## 18/10/2026 — MVP09.03–04: mode, lọc và tham số threshold trên UI

**Phạm vi:** đọc lại task/phụ thuộc/checkpoint09-C1, AGENTS/image/API contract, config/enhancement/render/page_config và store/UI hiện hữu. Áp dụng using-agent-skills, incremental, frontendUI/TDD/browser/review/docs và Ponytail. Chỉ thêm FilterPanel và action chỉnh processing vào state có sẵn; không đổi API/DB/core/dependencies hoặc detector. Chọn native select/range để giới hạn giá trị hợp lệ, không thêm form library/auto-preview/debounce/warp validator trùng backend. Hai task cùng sửa panel/store, chia lát state→mode/filter/CLAHE→threshold→browser và kiểm từng lát. Có5tệp sản phẩm/test thực tế, không cần thêm ID/AUX.

**MVP09.03:** Color/Gray/BW, None/Median/Gaussian, kernel3/5, CLAHE bật/tắt/clip1..4 step.1 và grid8×8 cố định. Mode chỉ đổi fieldmode, giữ fullinactiveparams/góc/rotation/geometry; không áp preset ngầm. None khóa kernel; Color khóa tươngphản/clip; Gray/Color khóa threshold. Controls inactive có nhãn và disabled, giữgiátrị trongfullPUT. Nhãn aria ngắn rõ cho select/range; browser bắtgetByLabel exact không tìm ra do textlabel bao options lúc đầu, đã bổ sung aria-label rồi kiểm lại thực. Không bỏ kiểm traa11y hoặc dùng selector vịtrí để né lỗi.

**MVP09.04:** Otsu/AdaptiveGaussian, blockselect3..151lẻ và Cslidernguyên−20..30; Otsu khóa block/C. UI nhắc block≤cạnhngắnwarp và cách sửa/chọnOtsu nếu bị từ chối. Backend PUT hiện hữu parse lại đầyđủ kể cảinactive vàestimate_warp_size thật; khôngco block/fallback. Đổi nhanh chỉ cậpnhật nháp, khôngHTTP. NútTạo bảnquét hiện hữu gửi fullPUTCAS rồi POST đúngrevision mới; source normalized đượcwarp/filter lại, khôngrender chồng. Đổi processing giữ confirmed của bốn góc; đổi góc vẫn bỏconfirmed. Resultcũ giữUUID vàstale tới render mới. Panel khóa busy/needsReload; editcounter vẫn chặnoutputmuộn nếu action đến giữa save/render/detect. Thông báo chung đổi từ “góc” sang “cấu hình/bản nháp” cho cảprocessing. LỗiPUT giữdraft/needsReload, GET rồi sửa/xác nhận lại như luồng hiện hữu.

**TDD:** thêm3state tests trước action: RED68pass/3fail với editProcessing missing. GREEN71tests191.4041ms sau látmode. Kiểm inputcopy/khôngmutatepersisted, fullconfignested/inactive gửi đúng, confirmed/góc giữ, minmaxblock/C/Otsumodeswitch, đổi nhanh0request, explicitPUT/render đúngrevision, pending-save/render giữdraft mới/bỏoutputcũ. Mở rộnglate-detect test thêmprocessingchange, không bịproposal ghi đè. Lệnhnpm có patternchứapipe quaWindowscmd banđầu fail shell; chuyển đúngnpm.cmd test đầyđủ, khôngcoi làRED logic. Final **71tests189.2519ms**, typecheck/build **27modules173ms**, JS256.02kB/gzip80.09,CSS9.09/gzip2.45. Không thêm test chỉ soi mãmarkup.

**Backend regressions/checkpoint:** chạy config_api/render_api/render_service/enhancement/detection_api/detection_migration bằngpytest-Werror → **273passed14.23s**. Lượt sandbox đầu không tiến triển ởcaseAPI đầu, đã dừng rồi chạy cùngsuite với quyền thread/IPC cục bộ; không đổi test/giảmassert/boqua lỗi. Backend không đổi; **full996-Werror130.56s là mốc09.01–02**, không tuyên bố chạy lại full lần này. Checkpoint09-C1 rà đủ09.01runprovenance/configimmutable,09.02proposal/manual/late-response và09.03fullconfig/mode/sourcefresh; các regression liênquan/ảnhthật phíaUI đủ đạt. Cổng09/checkpoint09-C2 chưa đạt, còn09.05–08.

**Browser và raster thật:** tạo riêng tài liệu QA gồm highlight/chữViệt1200×1600 từfixture08, img_0031536×2048 cóbóng trongdevelopment, vàcorners_rgb96×64. Không chỉnh tài liệu cũ.17UIrecords: ColorNone→GrayNone→GrayCLAHE4/Gaussian5→BWAdaptive31/C10/Median3→BWOtsu→ColorNone cùngquadtoànảnh/1199×1599. Các lầnđổi nháp giữrevision/confirmed/requests, oldrenderstale; PUT/render chỉtăng đúng lúc bấm. Chọn block3/C−20 rồi151/C30 liêntiếp khôngrequest; BW/Otsu khóa vàgiữblock/C. Img_003 fullwarp1535×2047 Otsu rồiAdaptive151/C30 chạy thật. Vùngnhỏwarp95×63 bịPUT400/INVALID_CONFIG khiblock151, revision0khôngđổi/khôngrender; GET→block3/C−20→confirm→renderrevision1 đạt. LỗiUI nhận generic “Cấu hình không hợp lệ.” từAPI hiện hữu, cách sửa ghi ngay cạnhblock; không tựnới haytrảảnhgiả.

Harnessignored chỉwrapfetch đểghi method/fullbody/status/response vàoDOM, dùng đúngScannerPage/client/backend.22mutationrequests gồm9render thànhcông,1PUT400, cácPUTconfirm/no-op/CAS cònlại. `.tmp/verify09_filters.py after` đọc nguồn/full/preview quaAPI, rerenderfresh bằngcore từconfigđãgửi, **9fullPNG và9preview khớp từngbyte**. Colorrev6 cóhashbằngColorrev1 dù đãquaGray/BW vàinactiveclip/thresholdkhác: khôngtíchlũy. PNGColorRGB, Gray/BWL, mọifullBWchỉ0/255; ngưỡngOtsu thực ảnhchữ165 vàảnhbóng116 ghi ởrasterchecks, UIdebugchưahiện. ĐãxemColor/GrayCLAHE-Gaussian/BWAdaptive: highlightgiữmàu ởColor/mấtnềnmàu ởBW; Gaussianmềmnét, Adaptivecóviềnvùng vàmấtnét nhẹ, khôngclaimtune/accuracy.

9session/48sourcehash trước-sau nguyên (bao gồm tàiliệu người dùng hiệncó vàQA cũ),9rendercorefreshgiữnguồn. Responsive320/768/1440 khôngtràn vàcontrols trongviewport; consoleprobe/productwarn-errorrỗng. Archiveharness rồi xóa đúng2filefrontendroot/đóngtab; viewportreset. Mởproductsạch/tàiliệuQA, chọnBWOtsu→renderrevision7/full1199×1599, screenshotfilter-controls.jpg vàtabdeliverable giữ cho user; lượt sảnphẩm cuối này nằm ngoài9renderđãđốichiếubyte ởharness. Backend8000/Vite5173/stopfilephase09 giữ.

**Bàn giao:**67main+8AUX/110ID, MVP09.03–04/checkpoint09-C1 đạt; nextMVP09.05persistdebugrender. Không hiệnhistogram/ngưỡngOtsuthực/debugstageviewer trước09.05–07; khôngxoayUIngoàiscope. Dataset6ảnh/1doc/test0/nợdetectorgiữnguyên; đổimode/filter khôngsửaquad nhậnnhầm. Source/runtimeDB/ảnh/evidenceignored tại experiments/results/mvp09-03-04-verified/, khôngảnhra ngoài/Git. README/AGENTS/plan/todo/MVP/projectmap/image/API đồngbộ; khôngcommit/push/deploy.

**QA cuối09.03–04:** `.tmp/qa09_filters.py` đạt17tài liệu/242link nội bộ,67main/8AUX/110ID/5optional,4task09 xong/09-C1đạt/09-C2chờ. Assertions kiểm17UIrecords/requestcounts/revisions/stale/inactive/minmax/400/recovery,9full-previewfresh/Colorroundtrip/PNGmode/BWvalues/hash, responsive3viewport/console sạch,48sourcehash nguyên vàcoreCLIrequirements khớpM1. Đã rà code mới theo correctness/simplicity/moduleboundary/inputconstraints/performance: dùng store/revision/executor hiện hữu, không thư viện hay xử lý pixel mới trongUI. CentricMem card kỹthuật đãlưu shelf document-scanner: sessions/2026-10-18T032426Z-mcp-fa94d1.md, khôngảnh/bímật.

## 18/10/2026 — MVP09.05–06: persist debug render và API đọc provenance

**Phạm vi/quyết định:** user xác nhận task5–6 giaiđoạn09 sau tin nhắn lỗi dấu. Đọc plan/todo/AGENTS, image-contract11.2/histogram và các hợpđồng API/run từ09.01–04; đọc corestage/histogram và CLIscan_one để giữ đúng buffer/đơnvị. Dùng using-agent-skills, incremental/TDD/API/review/docs/Ponytail và migration. Không đổi thuật toán/dataset/dependencies/frontend. Chọn RenderRun riêng vì một revision có thể render nhiều lần (có/khôngdebug); ghép mọi kinddebug/revision sẽ trộn stage hoặc ghép với ảnhfull kháclượt. RenderRead thêm render_run_id; GET nhận IDlượt cụ thể để UI09.07 ghép đúng ảnh. Tách các lát DBmigration→capturepersist→readAPI→negative/regression/restart nhưtodo, khôngthêmID/AUX.

**MVP09.05:** schema3/8table thêm RenderRun UUID/session/page/revision/sourcePNG-SHA/full-previewFK/JSONsnapshot/UTC. CompositeFK ép cùngowner, khôngunique theo revision. Migration explicit từschema1/6table tạoDetectionRun+RenderRun hoặc từschema2/7table chỉthêmRenderRun, cậpnhậtversion3 trongcùngtransaction; đúngschema3idempotent,unknown/partialDBvẫntừchối. Tests v1/v2/rollbackDDL-version/retry giữrowcũ. BackupSQLitev2 trước runtime migration, khôngreset hoặcghiđèlịch sử.

render_page nhận debugbool từ route; core render_document gọiđúngmộtlần, reuse EnhancementStages của dispatcher đã có. Debugtrue encodewarp/filtered_bgr/prepared_gray(Gray/BW)/before_rotation, full/preview; stagefull trướcrotation, full/preview saurotation. Metadata effectiveconfig/inactive/H/scan-v1/environment/units/sourceartifact-SHA/dims/timing, histBW256rawcounts từprepared_gray thật/cùngPNGhash/sum/actualOtsu/global hoặcAdaptive/local/null; ColorGraynull với reasonkhôngthreshold. Khônglấyanalysisgray của detector hoặc preview thay prepared_gray, khôngrerunfilter làmdebug. Timinghist nằmtrongcore.enhance, source_load verify/read/decode, encodefull-preview-debug, khôngfake timingpublish/commit. Finalgate/writerlocksource/config/revision giữ; allfiles+metadataRenderRun commitcùngtransaction, lỗi dọnfilemới chưathamchiếu. Config/confirmed/revision/timestamps khôngđổi. Debugfalse vẫn ghi run cơbản/fullpreview; khônggiữstage/histogram và báo debug_not_requested. Bỏ cảnhbáo DEBUG_NOT_AVAILABLE; defaultdebugfalse khôngđổi.

**MVP09.06:** GET `/api/v1/sessions/{sid}/pages/{pid}/debug` sync/read-only. DebugQuery chỉtốiđa1selector revision/render_run_id/detection_run_id, defaultcurrentrevision; strictnonnegativeURLinteger≤2^63−1/UUID4/extra-forbid. Revision chọn newestđúngR kểcảdebugfalse; khônglọcbỏnodebug rồitrảstagecũ. ID chọnchínhrun; detectiongiữtrials/contours/selected/candidates/descriptors/units, manual_required giữmaps thật/noquadgiả. DebugRead page/kind/current_revision/revision/rendernullfordetect/runID/UTC/metadata/artifacts/missing_stages. Session/pageownerlọc, sourcebinding vàrefs kiểmtype/kind/revision/SHA/dims; ArtifactRead khôngpath, filebytes/hashverifyngoàiDBreadtransaction. KhôngCV/DBwrite/recompute histogram trongGET. Có4trạngthái available/not_requested/not_recorded/incomplete; legacy/chưarunmetadata=null/khôngbackfill; missingfile/hash/DB/ref/wrongowner stage→missing_stages, khôngtrámrun khác. Unknownrun/wrongowner/revisionkhôngcó404, invalidquery400, corruptsourcebinding500STORAGE_FAILEDsanitize. Metadata.artifacts giữrefs lịch sử; UIphải dùngenvelopeartifacts/missing_stages khi quyếtđịnhhiểnthị.9path/10method, frontendviewer còn09.07.

**TDD và lỗi đã sửa:** RED importRenderRunmissing trước triểnkhai.23migration/storage tests đạt sau látDB. Látpersist/GET đầu42pass5fail vì StoredArtifact khôngcócreated_at; đã đọc đúng model, snapshot ArtifactRead từ ORM trongtransaction rồi chỉfileverifyngoàiDB, khôngbịa timestamp hoặc bỏfield. Sau sửa26render/APItests đạt. Thêmhistory/samerevdebugoff/12invalidqueries/detectproposed-manual/legacy/missingstage/sourcecorruption, stale3mutation×debugon-off, stagewritefault vàlatecommit sauactualINSERTRenderRun, singledispatch/debugparity.30debug-focused và71storage/service/API-focused đạt ởlát tươngứng.35cases mới ròng (8renderdebug+22debugAPI+3staledebug+2migration); không thêmtestssoimarkup.

Fullbackend `backend/.venv/Scripts/python.exe -m pytest -c backend/pyproject.toml backend/tests -q --tb=short -W error --basetemp=.tmp/pytest09-debug-full` → **1031passed203.33s**. Sau đó chỉlàm rõ chuỗi mô tả phạm vi timing metadata; focusedrenderdebug/debugAPI/renderAPI/migration → **55passed15.38s** trêncodecuối.71frontendtests345.1064ms đạt; frontendkhôngđổi/typecheck-build-browser giữbằngchứng09.03–04, khôngclaimbuildmới. Một lầntooltest khôngtrảoutput đãdừng, khôngdùng làm bằngchứngGREEN; các lệnh pytest được chốt đều có exit0/sốca thực.

**Runtime/migration/restart:** `.tmp/verify09_debug.py before` snapshot10session/19page/57sourcehash vàbackupSQLitev2 tại experiments/results/mvp09-05-06-verified/database-before-v3.sqlite3(ignored). Dừng nhẹbackendqua stopfile, mởlạiẩn cùngDB/schema3. `run` kiểm toànrowcũ còn nguyên trước tạo tài liệuQAriêng3trang (chữViệt/highlight,blank,anhtestnew); renderrevision1BWOtsu/debugtrue,revision2BWAdaptive51/C10/CLAHE/rotation90/debugtrue, renderlạirev2debugfalse. Hai detection:blankmanual_required/goodproposed, debugtrue. Đọc5query revision1/run2/revision2/detectionblank/detectiongood: available/available/not_requested/available/available; revision2 khônglấyrundebugcũ. Configstagemetadata củaoldrevision giữđúngsnapshot, UUIDfull-preview/stages riêng.

Restartẩn lần2 cùngDBv3 rồi`check`: **5JSONdebug nguyên,36artifacthash khớp,2histogramNumPykhớp**, sum1,917,201/preparedgray1199×1599; Otsuactualt165/global, Adaptive/local/t=null. Fullrev2 1599×1199 bằngrotation90 của before_rotation, hist vẫntrướcxoay. Cả10session/19page/295artifact/19config/0export/17detectionrun cũ làrownguyên củaDBmới,FKcheckrỗng;57sourcehash cũ nguyên. Khôngdelete/mutate stage củaDBthật đểgiảlỗi; ca thiếu/hỏng chỉởDB/tệp tạm củaunit tests. Core/CLI/requirements khôngđổi. Backend8000 giữstopfile mới `.tmp/phase09-debug-reopen.stop`, Vite5173giữ.

**Bàn giao/checkpoint:**69main+8AUX/110ID. MVP09.05–06/checkpoint09-C2 đạt: rà09.04fullconfig/thresholdbiên/noautorequest từbằngchứng17UI/9raster03–04;09.05snapshot/stage/histogram/rollback/restart;09.06strictselector/history/owner/missingstage. NextMVP09.07UIstage/histogram,09.08giảithích; cổng09chưađạt. UIrender hiệnchưa gửidebugtrue; task7 cần bật và dùng render_run_id cùngTS DTO đúng. Khôngcó UIảnhtrunggian/histogrammới tronglượtbackend này; khôngclaimaccuracy hoặcchấtlượng tổngquát/datasetmới. README/AGENTS/plan/todo/MVP/projectmap/image/API đồngbộ, khôngcommit/push/deploy/ảnhra ngoài.

**QA cuối09.05–06:** `.tmp/qa09_debug.py` đạt17tài liệu/248link nội bộ,69main/8AUX/110ID/5optional/6task09/C2pass/next09.07,9OpenAPIpaths/10methods. Assertions đối chiếu5JSONrestart/cùngrun-snapshot,36UUID/hash,2histogram/rawcounts/scope/sourcePNG/rotation,57sourcehash/alloldrows, prior09.04UI17records/9fresh-raster vàcoreCLIrequirements khớpM1. Đã rà code theo correctness/readability/moduleboundary/ownership/boundedwork: dùngcore/storage/executorhiệnhữu, không thêmdependency hoặcfilepaths vàoAPI; fileverifyngoàiDBreadtransaction. CentricMem card kỹthuật lưu shelf document-scanner: sessions/2026-10-18T034346Z-mcp-68c323.md, khôngảnh/bímật.

## 18/10/2026 — MVP09.07–08/AUX09.01: viewer, giải thích và rà cả tám task

**Kết quả:** hoàn thành09.07–08 và audit8task;71main+9AUX/110ID, cổng09/checkpoint09-C1/C2 đạt, nextMVP10.01. [Audit](audit-phase-09.md) chứa ma trận, số đo, giới hạn và phân biệt bằng chứng mới/lịch sử. Tự mở kết quả cũ còn10.07; quản lý/xuất tài liệu đầyđủ chưa hoàn thành.

**Workflow:** using-agent-skills → incremental/TDD/frontend/Ponytail, browser/review/documentation và PDF đối chiếu3tài liệu. Khôngthêmdependency, cache/endpoint/schema hoặcđổi thuậttoán. LátAPI/types/parser/state → components → editor/style/tests → browser/docs; IDs khôngtăng vìtaskcon.

**09.07:** TS DebugRead/Artifact, RenderReadrunID, clientrenderdebugtrue/debugGETAbortSignal, parser identity/ref/histogram, GET-onlystate. PipelineViewer lazyexpand/exactrun/keyedstate/retryGET/JSONlink/stale, StageImageUUID/dimensions/loading/error/retry, HistogramViewSVG256rawcounts/actualOtsu/localAdaptive/rawtable, CandidateMetrics trial/selected/descriptor/cạnh/score/NMSvàđơnvị. Hookeditor giữ detectionRun diagnostic riêng noteproposal; sửa draft vẫn xóanote, khôngđổi source/config/revision tựđộng. Full/preview từrun đượcchấpnhận; không ghép stage cùngrevision nhưng kháclượt.

**09.08:** pipelineExplanation vàguideUI/docsalgorithm-notes có mụcđích/tham số/giới hạn. Đọc lại giáo trình/Ch05/Ch06 trongdocs qua textcache cóSHAkhớp và trangMPP minh họa: biên/đạohàm/nhiễu, sángkhôngđều, xấpxỉđa giác/MPP/chiađoạnlặp. Nêu DPkhácMPP, findContours khôngtựgánMoore, contour/Q làbiểudiễn, chuvi/cạnh/góc làdescriptor, a/f làvùng, S làheuristic; khôngép90°/khôngdewarp3D. Các preset/scoring/units làquyước triểnkhai, khônggán nguyênvăn choPDF.

**TDD/kiểm thử:** RED clientbody thiếudebugtrue/parser chưa có; REDgiữdiagnostic sauedit; GREEN5testsparser/state mới vàmởrộngAPI/editor tests. Có exactrun/source/revision/SHA/kind/dimensions, incomplete,256bin/sum/hash/scope/negativecounts,missingscore,GETfailure/retry/older/unmounted. Typecheck từngbáo tupleindex cóthểundefined, đãđịnhtupleđúng rồiqua, khôngtắtstrict.

Fullbackend `backend/.venv/Scripts/python.exe -m pytest -c backend/pyproject.toml backend/tests -q --tb=short -W error --basetemp=.tmp/pytest09-final-audit` → **1031passed181.84s**. Frontend `npm.cmd test` → **76passed346.4371ms**; `npm.cmd run build` gồmtypecheck,33modules262ms,JS282.67kB/gzip87.90,CSS11.48/gzip2.91. Khôngnớiassert/skip/suppresswarning; testsfullbackend kiểmtoàn09.01–06 vàcácgiaiđoạntrước, frontendkiểmphầnviewer mới.

**Browser thật:** QA riêng4trang: anhtestnew612×460, trắng320×240,img_0041536×2048,chữ/highlight1200×1600.27snapshotUI gồm detectorproposed/manual/warning, rawmap/mask/overlay/table, Color/Gray/BWOtsu/Adaptive51C10CLAHE, stale/switchdiagnostic, stage/guide,missingdescriptor/stage/histogram,wrongrun,GET500/retry,heldGETcũ+mới,productclean. Faultđược chủđộng sửa trong harness, khôngclaimbackendlỗi; requestholdgiữpayloadthật. Một lượt giữGET đầu chỉchứngminh chuyểnnhóm; đãđổi harness sanghàngđợi rồi kiểm thảcảhaiGETthật, runmới thắng. DOMreadonly/semanticcontrols/CUA, khôngrawPlaywright hoặcbrowserfetchbằngevaluate.

**Đối chiếu:**11run/81artifact tảiAPIkiểmSHA/dimensions/PNG,6histogramNumPy từprepared_gray/raw256counts/sum/sourcehash,2descriptor e/S khớp. UI từng số đã làmtròn đốichiếuJSON, Otsu ảnh tốt201×285/t247/tổng57.285; Adaptive tnull; chữ1199×1599/t163/tổng1.917.201. Ảnhtốt P979.6984843/e.9898373984/S.6347091154, img004P5417.4755082/e.3042824944/S.4683515931 vẫnwarning/dínhbàn.66hashnguồn/11session22pagecũ vàcore/CLI/requirementsM1nguyên; khôngresetDB hoặcảnhra ngoài.

**Rà8task:** táidùngbằngchứng đãkiểm09.01–02(11run118stage)/09.03–04(17UI9freshfull-preview)/09.05–06(5JSONrestart36hash2histogram), đốichiếucodemới+suitefull+browser. Ma trận8row trongaudit09; khôngsuy taskxongtừviệctàiliệutồntại. Responsive320/768/1440 khôngtràn,SVG256bin;consoleproduct sạch/viewportreset. Harness2file đãarchiveignoredrồigỡ; giữtabproduct với histogram/t163 vàscreenshotproduct-view.png. Evidenceignored experiments/results/mvp09-final-verified/ gồm trước/sau/seed/requests/browser/layout/console/raster/verification.

**Bàn giao:** README/AGENTS/plan/todo/MVP/projectmap/image/API/algorithmnotes/smoke đồngbộ; AUX09.01 ghi yêu cầu audit của user, khôngđổi110IDgốc/109active/1skip/5optional. Dataset6ảnh cùngdoc_01/test0 vànợdetector giữ, khôngtune epsilon/weights từmột tờgiấy. UIgiúpchẩndoán, filtersauwarp khônglấy lại mépgiấycắt sai. Backend8000/Vite5173 giữchạy/stopfile .tmp/phase09-debug-reopen.stop. Khôngcommit/push/deploy hoặcgửiảnh bênngoài.

**QA cuối09:** `.tmp/qa09_final.py` đạt13tài liệu/236link nội bộ,71main/9AUX/110ID/8task09/cổng09/next10.01;54giátrị descriptor trênUI và3bộ256binUI khớpJSON. Verification11run/81artifact/6histogram,66sourcehash,coreM1,9path/10method vàharnessremoved đều đạt. Phép đo bars ởhelper snapshot banđầu dùng saiselector; đãđọc lại bằng `.histogram rect` trong3casebin vàresponsive, không dùng số0 của phép đọc sai làm bằngchứng mấtbiểuđồ. Chỉnhformat âm0 trong QA Python theo JavaScripttoFixed, khôngđổi code xửlýảnh hoặcnớiassert. CentricMem card kỹthuật đãlưu shelf document-scanner: sessions/2026-10-18T043437Z-mcp-6707e7.md, khôngảnh/bímật.

## 18/10/2026 — MVP10.01–02: đổi tên và thêm trang giữ trạng thái

**Kết quả:**73main+9AUX/110ID, hoàn thành10.01–02; nextMVP10.03. Checkpoint10-C1 vẫn cần10.03, cổng10 chưa đạt. Không tạo AUX/audit toàn giai đoạn khi mới có2/7task; không đổi thuật toán/dataset/schema/dependency.

**10.01:** SessionRename kế thừa titletrim nhưng bắt buộc trường, strict1..200/extra-forbid. PATCH `/sessions/{sid}` → service → repository UPDATE trước SELECT trong transaction; title thay đổi thì sửa title/session.updated_at, same title no-op giữtimestamp. Không đọc/sửa pixel, page/config/revision/render/artifact. Owner404/input400/commit500sanitize/rollback. UI DocumentTitleForm lưu/hủy/label/nativeinput/focus, synchronous pendingref chặn double submit, không tựretry PATCH; callback chỉ update metadata header/list, không reload editor. Lỗi mạng nhắc đọc tên đã lưu trước retry. Đã sửa hủyform để xóaerror cũ và trả focus sau React commit.

**10.02:** createUploadBatch thu gọn vòng xử lý hiện hữu thành module độc lập kiểm thử được: một batch active, POST tuần tự, local15MiB/slotquota, tệp lỗi không tiêu slot; backend PAGE_LIMIT_EXCEEDED dừng gửi phần còn lại. Khóa còn giữ qua GET đối soát. Parent upload giữ selectedpage (trống chọn thành công đầu tiên); finishUploads đọc serverdetail/list mới, không tăng detailReload/key SourcePreview. Vì vậy nhập ảnh không làm mất draft/filter/góc hoặc full/preview/debug đang xem. POST mất phản hồi sau commit được GET tìm lại; nếu GET lỗi thì báo rõ và khóa nhập mới đến Tải lại. Navigation/tạo/rename/refresh bị khóa trong batch; PageList vẫn chọn được theo ID.

**Tệp code:** backend schemas/sessions.py, storage/repository.py, services/sessions.py, api/sessions.py; frontend client/DocumentTitleForm/UploadPanel/uploadBatch/ScannerPage/styles; tests session/importAPI/client/batch và npmtestscript. Các lát backendmetadata → queue/client → UI/editor preservation đã kiểm riêng; không tự tạo repo/branch/commit vào workingtree đanguntracked. Lõi/CLI/requirements vẫn M1.

**TDD/test:** RED11renamecase trả405 trước route; GREEN29sessionAPItests3.15s. REDclientrename chưa có và modulebatch chưa có; GREENwire/batch rồi gắnUI. Thêm1integrationtest append vào trang Gray+CLAHE đãrender, badJPEG, đầy20 và21st413, giữ snapshot/oldPNGhash. Bộ kiểm thử cuối `backend/.venv/Scripts/python.exe -m pytest -c backend/pyproject.toml backend/tests -q --tb=short -W error --basetemp=.tmp/pytest10-01-02-full` → **1043passed149.38s**. `npm.cmd test` → **81passed229.8616ms**; `npm.cmd run build` gồmtypecheck →35modules407ms,JS285.86kB/gzip88.74,CSS11.67/gzip2.95. Không skip/suppress/nớiassert.81gồm5test mới: renamewire và4batch (sequential/duplicate lock qua reconcile, lỗi không tiêu slot/quota,15MiB, backendquota/reuse).

**Browser/evidence:** QA riêng có source chữ/highlight1200×1600 và tài liệu quota19trang2×2; không sửa tài liệu cũ. Rename tên Việt trim, space-only khôngPATCH,200ký tự lưu, cancel/error/focus và responsive320/768/1440 khôngtràn. Batch broken.jpg415/exif6/alphaPNG chỉ lỗi một tệp, hai ảnh tốt vào, selectedpage1/draftGray/run2e7c9034-5d14-4188-8f63-aba79df2cb85/fullUUID0449590f-e7d2-405a-83c5-517aa54eb1b2 giữ. Harnesstạm giữ GETcuối cho thấyinput/rename vẫnkhóa, thảGET nhập tiếp được. Faultdrop sau POST201: UI báo mất phản hồi nhưng GET cuối thấy trangthứ4, configpersisted vẫnColor/revision1/draftGray giữ trongUI. Đây là lỗi mô phỏng, không phải backend tự lỗi; rename500 cũng mô phỏng trước gửi PATCH. Tên/quota/selectedpage sau restart và tabproductclean được xem thật bằngCUA/DOMreadonly, khôngbrowserfetchquaJS.

**Quota:**19trang chọn2file → đúng1POST201/thành20, tệp dưerror chưa nhập, inputdisabled. Gửi trực tiếp21st→413PAGE_LIMIT_EXCEEDED, metadata không đổi; integrationtest còn giữ cảfilehash. Filechooser lần đầu với GET bị giữ hoàn tất chậm; không gửi lại batch khi chưa biết kết quả, đọc state rồi thả GET và kiểm status, không tăng số trang do retry.

**Lưu bền:** graceful shutdown backendcũ và khởiđộngẩn bản mới cùngDBschema3; sau thao tác lại physicalrestart vớistopfile .tmp/phase10-reopened.stop. ExactJSON của2QA docs trước/sau restart bằng nhau; tên Việt/main4trang/quota20, config/revision/render giữ.5debug stage/full-previewhash cũ nguyên,12oldsession26page78sourcehash trước task nguyên. Evidence ignored experiments/results/mvp10-01-02-verified/ gồmseed/before-after/requests/browser13states/layout/restartdebug/hashes/quota21/verification/harnessarchive/product-view.png.13UIstates/19requestrecords, console sảnphẩm sạch, viewportreset; harness gỡ và giữtabproduct main4trang.

**Bàn giao:** README/AGENTS/plan/todo/MVP/projectmap/image/API/smoke đồngbộ73main+9AUX/110ID/109active/1skip/5optional. API9path11method/DBschema3; đổi tên metadata không dùng revision ảnh. Next10.03 reorderAPI; auto-reopen kếtquả10.07/PDF11 chưa làm. Cổng09 vẫn đạt; không suy đã xong7task10. Dataset6development cùngdoc_01/test0 và nợdetectorimg_004/006 giữ. Backend8000/Vite5173 giữchạy, stopfile .tmp/phase10-reopened.stop. Khôngcommit/push/deploy hoặcgửiảnh ra ngoài.

**QA cuối10.01–02:** `.tmp/qa10_docs.py` đạt10tài liệu/191link nội bộ,73main/9AUX/110ID,10.01–02checked/10.03–07pending/checkpoint10-C1pending;13UIstates/19requestrecords và9OpenAPIpaths/11methods khớp. So selectedpage/draftGray/run/fullUUID trước/sau nhập và mấtreply, quota chỉ1POST khi còn1slot,5artifacthash/restart78sourcehash/coreM1/harnessremoved đều đạt. Rà mã giữ ranh giới metadata/ảnh, transaction ngắn, quota server và không tựretry; không có lỗi chặn còn mở trong hai task. CentricMem card kỹthuật lưu shelf document-scanner: sessions/2026-10-18T073446Z-mcp-e774e1.md, khôngảnh/bímật.

## 18/10/2026 — MVP10.03–07/AUX10.01: order, xóa, mở lại và rà bảy task

**Kết quả:** làm10.03–07, rà cả7task10 theo yêu cầu.78main+10AUX/110ID; checkpoint10-C1/C2/cổng10 đạt; nextMVP11.01 xuất ảnh/PDF. [Audit10](audit-phase-10.md) có ma trận và giới hạn. Skillusing-agent-skills chọn incremental/TDD/API/frontend/git/Ponytail/browser/review/docs vàsecurity cho xóa dữ liệu; giữ phạm vi localMVP, không thêmauth/dependency/migration, khôngspawnagent.

**10.03/API:** repository.set_page_positions nhậnlist ORM theoorderđích, tìmnslottrống trong[n,3n), gán tạm+flush rồi0..n−1+flush để tránhUNIQUE immediateSQLite, khôngpositionâm hoặcoverflow theoMAX. order_document lấy lock_session trước read, kiểmfullIDset, no-opgiữtimestamp/đổichỉsession.updated_at; trảSessionDetail saucommit. PUTpage-orderroute/errors INVALID_PAGE_ORDER400, requestduplicate/missing/extra/saiUUID400, foreign/thiếu400, phiên404; rollback500sanitize. Khôngtăngrevision ảnh/config/source/run.8testsRED404→GREEN, session regression37tests3.45s.

**10.04/UI:** clientfullpage_ids, movePageIds/selectRemainingPage helpers, PageListlên/xuống/khóađầu-cuối/theoID. ScannerPagechangeDocument giữlockref/managing, xửlýresponse bằngcurrentselectorfunctionalđể không ghiđè trang mới;khôngđổi detailReload/keyeditor khiorder/reconcile. Lỗi hoặc mấtreply chỉGETđối soát, không mutationretry;GETfailkhóa thao tác đếnTảilại. Baảnhsynthetic600×800 inPAGE1/2/3 đổi[2,1,3], draftGray180°/fullrun/selectedphysical1giữ; mock500trướcrequest vàlostresponse saucommit đều đạt. Giữactualorderresponse rồi chọnphysical3/thả→vẫnphysical3/BW270.

**10.05–06/DB-files:** thêmservices/deletions.py dùngwriterlock/lookupowner/collectStoredArtifact, DELETEpage/session vàcascadeconfig/artifact/DetectionRun/RenderRun, pagecompactpositions/sessiontimestamp. Commitxong_cleanup mởreadtransactionkiểmreferenceID/path mới rồi verify/hash/unlinktừngUUID ngoàiDB; khôngrecursive-delete/pathclient. Exceptioncleanup log/giữorphan, khônghoànDBgiả.7page-delete+4session-delete+5CPUbarrierrace tests:render/detect×page/session,import×session. File/metadata trangkhác giữ; rollbackgiữtệp; refcònsốngkhôngunlink; ownerđãxóa chặnfinalize. REDdelete404/405 trướcroute; testlỗiDetachedInstanceđọcORM saucommit đãsửa bằngchụpID trongtransaction, khôngđổi codeđểđápứnglỗitest.53focusedtests9.82sđạt.

**10.05–06/UI:** clientrequest hỗtrợempty204 trướcJSON, khôngretryDELETE. ModalnativeHTMLdialog/aria-label-description/focusGiữlại/hủy/Escape, cảnhbáo vĩnhviễn; xóatrangchọnchọntrangkế/lastprevious/hết→null, xóakhácgiữdraft/chọn; xóatàiliệuchọntàiliệucònlại hoặcemptystate. Các DELETEbrowser trongharness đều bịchặntrướcfetch vàmôphỏng204/GEToverride, khôngDBsideeffects. APIthậtriêng verify10_actions.py chỉnewQAIDs/checkexcluded14oldIDs:3invalidorder400 giữdoc;3pageDELETE204/9sourcefilesđãvắng vàgiữhashfilecòn, retry404;2sessionrỗngDELETE204/retry404. QAstatusdocumentcórenderđượcxóaAPIthật riêng saukiểmUI, chứngminhwhole-docnhiềufile; khôngxóamain3tranghoặctàiliệucũ.

**10.07/history:** PageReadnullablelatest_render/latest_detection additive, page_history.py hydratesexactrun/sourceID/SHA/dims/revision/refkind/pair/configsnapshot/timing, parseconfigsourcebound. RenderchọnrevisionDESC/created_atDESC/idDESC, detectioncreated_atDESC/idDESC; debugoffvẫnlatest, khônglọcđểlấyrundebugcũ. LegacykhôngRenderRun→null, corruptbinding→500STORAGE_FAILED, khôngfallback/backfill. GETchỉDBmetadata, khôngđọcmọiPNG/CV/ghiDB; debug/artifactGETvẫnverifybytes. Hookreloadphụchồifull/diagnostic/persistedconfig, khôngápdetectcorners hoặcconfirmedvàkhôngPOST. Thêmslectxoay0/90/180/270dùnglõirotationcũ, chỉdraftchotới save/renderexplicit. Bốnreopentests và3hooktests mới. LỗiUUIDrefstr→SQLAlchemy.hexpháthiệnởGREENđầu, sửabằngUUIDtrướcquery;57focused12.16sđạt. RàmãpháthiệnPageListstale sauhooksave, thêmcallbackpersistedmetadataSourcePreview→parentuseCallback giữposition/keyvàkhôngcopydraft; QAriêngGray90sauconfirm/renderhiệnngayĐãquétr1khôngreload.

**Kiểm thử:**28backendtests mới (8order/7page-delete/4session-delete/5races/4reopen),6frontend (1wire/2helper/3hook). Fullstrictđầu1066pass/5fail149.06s:5oldassertsSessionDetailkhôngđổi saunewrender/detect naycóadditivehistory. Cậ pnhậtđúnglatest_render/latest_detectiontrongexpectedpayloadrồivẫnsocảdoc, khôngbỏsource/config/revisionassert;23focused8.23sđạt. Final `backend/.venv/Scripts/python.exe -m pytest -c backend/pyproject.toml backend/tests -q --tb=short -W error --basetemp=.tmp/pytest10-phase-final-green` → **1071passed189.56s**. Finalfrontend `npm.cmd test` → **87passed380.9416ms**; `npm.cmd run build` gồmtypecheck,37modules262ms, JS290.78kB/gzip90.07,CSS12.20/gzip3.07. Khôngskip/suppresswarning/thaylõiđểpass.

**Runtime/bảo toàn:** trướcviệcmới chụp14doc/50pages/150sourcehash vàSQLitebackupAPI. BaảnhQAmanualfullsource đượcUIrenderColor0/Gray90/BWOtsu270,full599×799/799×599/799×599. verify10_raster.py freshsource/core/encode_render_images cả3cặpfull-previewbyteequal, sourcekhôngmutate,12hashcore/CLI/requirementskhớpM1. Gracefulstopbackendphase10-final.stop rồiStart-ProcessHidden cùngDBschema3/stopfilemới phase10-final-reopened.stop. JSONdocument/config/order[2,1,3]/3debugJSON/17artifacthashnguyênsauphysicalrestart; browserreload/chọn3trang8requestghiđượcđềuGET, khôngPOST. BWviewer256bin/tổng478.601/t149/cùngrun;draftGray180°chưa lưu khôngphụchồiColor0°.

verify10_final.py verify:14olddoc50pages150sourcehashnguyên; cả14sessions/50pages/537artifacts/50page_configs/24detection_runs/13render_runs/0exports/schema_versionrowcũlàtậpconnguyêncủaDBmới,FKcheckrỗng. DTOcũchỉbỏ2fieldadditivekhiđốichiếunộidungcũ; khôngbỏfieldpersistedhoặcsửaDBcũ.23snapshotUI/main/delete-simulated/reopen/statusrequestsghiởevidenceignored `experiments/results/mvp10-final-verified/`. Responsive320/768/1440documentkhôngtràn;list320cuộnngang, khôngclaimmọicontrolcùngvisible. Consoleproductwarn/errorrỗng;resetviewport/archive2harnessfiles rồiRemove-Itemđúng2fileliteral, giữtabproductsạch3trang vàproduct-view.png.

**Giới hạn/bàn giao:** best-effortcleanupcóthểcònorphan saucrash/I/O, chưaGC/Trash/Undo; khôngatomicDB+filesystem. Legacyrenderchưarunđủpaircầnexplicitrender, GETkhôngbịa/bạckfill. OrdermetadatachưaCAS/nhiềurequestcùngtậpIDcommitcuối; export11cònphảithêm snapshot/khóamutation, khôngclaimđãxuấtPDF. README/AGENTS/plan/todo/MVP/API/image/projectmap/smoke/auditđồngbộ78main+10AUX/11path14method/schema3. Dataset6development1doc_01/test0/nợimg004/006giữ. Backend8000/Vite5173chạy/stopfilephase10-final-reopened.stop. Khôngcommit/push/deploy/ảnhra ngoài.

**QA cuối10:** `.tmp/qa10_final.py` đạt11tài liệu/215link nội bộ,78main/10AUX/110ID,7task10/checkpoint10-C1/C2/cổng10/next11.01.23UIstates/59requestrecords,4orderPUT/8reopenGET-only,4browserDELETEsimulated vàAPIthật3page/3sessionnewQA,3cặprenderbyteequal,17hashrestart/150sourcehashold/alloldSQLrows/M1/harnessremoved/OpenAPI11path14method đều đạt. Bản ghi kỹ thuật CentricMem shelfdocument-scanner: sessions/2026-10-18T081510Z-mcp-d9f99f.md; chỉsummary kỹ thuật, khôngảnh/bímật.

## 18/10/2026 — MVP11.01–02: hợp đồng xuất, snapshot và lease

**Kết quả:**80main+10AUX/110ID, hoàn thành11.01–02; nextMVP11.03 encode PNG/JPG. Checkpoint11-C1 cần03, cổng11/M3 còn chờ. User xác nhận không cần hoàn tác, không thêm Undo/Trash. [Hợp đồng/snapshot](export-snapshot.md) mô tả interface, lifecycle, giới hạn và bằng chứng. Workflowusing-agent-skills/incremental/TDD/API/git/Ponytail/review/docs, giữ phạm vi backend: chưa tạo encoder, route export, ExportPanel hoặc PDF; không đổi thuật toán/dependency/schema3. Khôngspawnagent/commit/push/deploy.

**11.01:** ExportRequest chuyển từ schemas/sessions.py sang exports.py, giữ alias import cũ; thêm ExportRead id/session/artifact/format/orderedpages/created_atUTC khôngpath. FrozenPageSnapshot/tuple, subset/explicitorder khôngsort; PDF1..20/PNG-JPG1, ID duy nhất kể cả revision khác, strictrevision/options vàfinite margin0..30. PDFoptionsretain/inactive khi xuất ảnh. Schema không thể biếtmembership, service11.02 kiểmowner/currentstate.19testschema mới RED modulemissing→GREEN; cùng21schema cũ đạt40tests0.60s. APIcontract córequest/errorJSON vàreceipt; khôngtuyên bố201đã phục vụ khi route11.06chưa có.

**11.02/snapshot:** services/exports.py ExportSnapshot/ExportPage dataclassfrozen và export_snapshot context: reservelease→revalidate request kểcả modelcopy→owner/exactrevision→configsourcebound/confirmed/quad→read_render_history→collectmissing→verifyfullPNG sauDBreadtransaction. Helperrender được tách từpage_history khôngđổi chọn revisionDESC/created_atDESC/idDESC hoặc binding. Full cóStoredArtifactimmutable/configfrozen/render_run_id; không ORMsession/preview/thumbnail/auto-detect/auto-confirm/auto-render. Thiếu tấtcảrunđúngR trảPageNotRenderedError.pages theoorder→handler409PAGE_NOT_RENDERED/details.pages. Stale409REVISION_CONFLICT/chưaconfirmed409PAGE_NOT_CONFIRMED/owner404; binding/filecorrupt500STORAGE_FAILED, khôngfallbacklegacy hoặc ảnhkhác. Exceptioncontext/writer vẫnrelease.

**11.02/lease vàqueue:** services/session_guards.py WeakKeyDictionaryperEngine/RLock/busyUUIDset, khôngpersistmarker/DBmigration; mutationguard trướctransaction, khônggiữ quaCPU. Bọc rename/config/order/deletepage/session, preflight+publish import/render/detect. Các thayđổi chia lát:guardunit3GREEN1.15s, metadata/API5GREEN4.91s, CPUgates vàsnapshot/reopen49GREEN20.45s. run_export reserve trước sharedexecutor.enqueue đểchặnsecondexport ngay; leaseclaim/cancel/release đồngbộ. Queuedcancel/429/submiterror trảlease và khôngwriter; activecallercancel giữlease/slotđếnthreadfinally, khôngkillthread. RestartEngine mới khôngkhóa cũ. Local1process/1EngineDB; khôngmultiworker hoặcOSdeleteguard. Pin giữbằngDBrefs/descriptorimmutable/ownerlease, không thêm pintable hoặc cache.

**Ca race bổ sung:** RED3asyncHTTP banđầu requestwaitsauworkerexport rồi200/201, đúng là chưa chặn ngay tại thời điểm gửi. Thêm require_mutable preflight qua run_in_threadpool ởupload/render/detect trướcCPUqueue; servicepublish vẫnkiểm lại. GREEN3case2.99s: trả409SESSION_BUSY tronglúcworker vẫngiữlease, healthđọcđược.3CPUbarriercases render/detect/import đãbắtđầu trướcexport bịchặnlatepublish/khôngđổi filemetadata.8HTTPmutationcase dùngapp/DBtạm thậtkhôngmock DELETE; đọcnguồn/debug/health vàtài liệu khác khôngbịbusy-set chặn.

**Kiểm thử cuối:**54tests mới =19schema+3guards+16snapshot+16mutation/lifecycle. RED banđầu guards/snapshot modulemissing,11mutationtests khôngchặn,3asyncqueuedtests chạy muộn, missing-renderhandler500; thêmhandler409detailsđúngorder. MộttestKeyError đườngdẫnWindows đãsửa dùngstr(Path(...)) chứkhôngđổi storedpathhoặcnớiassert. Focuscuối63passed21.35s gồmreopen/executor. `backend/.venv/Scripts/python.exe -m pytest -c backend/pyproject.toml backend/tests -q --tb=short -W error --basetemp=.tmp/pytest11-01-02-full` → **1125passed171.02s**. Khôngskip/suppresswarning/thayalgorithm. Frontendkhôngđổi vàkhôngchạylạitest/build;87frontend/build làmốc10, khôngclaimlầnchạymới.

**Nghiệm thu isolated runtime:** `.tmp/verify11_export.py` tạo DB riêng với3ảnhsynthetic inPAGE1/2/3 lấyfileQA ignored đãcó; APIimport/config/renderColor0/Gray90/BWOtsu270. Requestsubset[3,1], run_export dùngsharedworker giữcallback;8mutationHTTP đều409SESSION_BUSY, secondexportservicebịchặn, GETdetail/health hoạtđộng. SnapshotfullIDs/run/rev/mode/rotation/hashđúng,26artifacthash/source/config/documentnguyên; sauworkerrename-noop200/unlocked. Callbackchỉverifytệp/metadata: exports_written0/export_encoder_usedfalse, khônggiảPNG/PDFđãxuất. Evidence `experiments/results/mvp11-01-02-verified/` ignored gồmrequest/snapshot/blocked-mutations/runtime-verification/DB tổnghợp; khôngảnh người dùngragit/dịch vụngoài.

**Nạp backend/bảo toàn:** `.tmp/verify11_product.py before` chụp **14tài liệu/49trang/147hash nguồn ởđầu lượt11**, cùngSQLitebackupAPI; sốliệu mới này khônglấy từsnapshotgiaiđoạn10. Gracefulstopphase10-final-reopened rồiStart-ProcessHidden backendcùngDB/8000, stopfilemới `.tmp/phase11-01-02.stop`. `after` sođúngtoànbộ14SessionDetail/147hash vàmọiSQLrow bằngnhau:14sessions/49pages/542artifacts/49page_configs/25detection_runs/13render_runs/0exports/schema_version, FKcheckrỗng.12hashcore/CLI/requirementskhớpM1, OpenAPI11path14methods/schema3khôngđổi, khôngendpointQA/export mới. Vite5173/browser củausergiữ. RuntimekhóamemorykhôngpersistquaEngine/lifespanmới.

**Bàn giao:** README/AGENTS/plan/todo/MVP/API/image/projectmap đồngbộ80main+10AUX,11.01–02checked và11.03–08pending; khôngtạo AUX/auditcảphasekhi mới2/8task. docs/export-snapshot.md ghi rõsingleprocess vàranhgiới01–02/03–08. Dataset6development1doc_01/test0/nợimg004/006giữ. Khôngcầnhoàn tác theo user; cleanupcrashorphan từ10 vẫngiữgiới hạn kỹthuật, khôngđánhđồng Undo vớiGC.

**QA cuối11.01–02:** `.tmp/qa11_final.py` đạt10tài liệu/212link nội bộ,80main/10AUX/110ID,11.01–02checked/03–08pending/checkpoint11-C1/cổng11pending/next11.03. Snapshotrequestorder[3,1],8mutation409/26hash nguyên,14productdocs49pages147sourcehash/allSQLrowsnguyên,11path14method/schema3/noexportendpoint vàcoreM1/ignoređạt. CentricMem card kỹ thuật shelfdocument-scanner: sessions/2026-10-18T092758Z-mcp-d3f74b.md, khôngảnh/bímật.

## 18/10/2026 — MVP11.03–04: encoder ảnh đơn và A4 một trang

**Kết quả:**82main+10AUX/110ID,11.03–04 đạt, checkpoint11-C1 (01schema/02snapshot/03imageencoder) đạt; nextMVP11.05 ghép/lưuPDF. Checkpoint11-C2/cổng11/M3 còn chờ05–08. Workflowusing-agent-skills/incremental/TDD/API/git/Ponytail/review/docs vàpdfskill đểrender/xemPDF; khôngspawnagent/commit/push/deploy. [Chi tiết](export-encoding.md). KhôngthêmHTTPexport/UI, chưaExportRecord hoặcPDFnhiềutrang; khôngđổi thuật toán/dataset/requirements/schema3.

**11.03/code:** thêmexport/__init__.py vàimages.py. EncodedImagefrozen(payload,mime,filename,width,height), encode_imagegrayHxW/BGRHxWx3uint8dims2..2400. PNGdùngencode_stage_pngcũ/RGB-L/pixel-exact/BW0–255/nét1pixel; JPEG95/subsampling0 từPILImageRGB-Lmới, khôngEXIF/ICC hoặcresize/filter/rotation. download_filenameNFKD/đ→d/ASCIIhyphen/slug80/fallback/extensionwhitelist/DOSreservedguard, khônguserpath. services/exports.load_export_pixels đọcfullStoredArtifactđãverify rồiSHA/sizecheckbytes, decode_full_pngformatPNG/modeRGB-L/frame1/dims/EXIF-ICCgate, BGRcopy/grayuint8. OSError/decodermismatch→ArtifactFileError. encode_snapshot_image chỉPNG-JPG1page/filenamefromsnapshottitle-ID-R, chuẩn bịbytesbêntronglease, khôngDBpublication.

**11.03/TDD:** RED ModuleNotFoundapp.export, GREEN23image+16snapshot=39passed8.56s. Mởrộng5decodegates palette/RGBA/16bitgray/ICC/EXIF nên28imagecases. Kiểm6mode-format/PNGexact/JPEGchannel/interiorerror/grayL/sourceimmutability/BW1pixel/safeleafnames/rasterlimits/decoderwrongsize-format và3servicecasesColor0/Gray90/BW270full>preview1000 khôngDB/tệpmutation. Khôngtuyên bốdownloadHTTPđãcó; encoderđãtrảbytes/têngợiýđể11.06nối.

**11.04/code:** export/pdf.py mm_to_points/layout_a4/PdfPageLayoutfrozen/append_pdf_page/encode_pdf_page. mm/25.4×72,A4portrait210×297/landscapeđảo;auto W>Hfullsauxoay→landscape, squareportrait;explicitoverridegiữ. Marginfinite0..30, dimsstrictint2..2400. Scale=minavailableW/W,availableH/H; dùngcùngscale/căn giữa vớiReportLabgốcdướitrái, khôngcrop/stretch/xoay thêm. appendsetPageSize/drawImage/showPageđúng1trang; encodeCanvas/BytesIO/savePDFthật. PNGembeddedlossless/JPEG95-0DCT quaImageReader; APIảnhL/RGB/BGR dùngchungcodec/validationhiệnhành, khôngmở rộng options. ReportLab5.0.1đãkhóa, JPEGImageReaderconstructor đượcđọc tại sourcevenv đểkiểmnhánhDCT.

**11.04/TDD/kiểm thử cuối:** REDpdfmodulemissing, GREEN23PDF+23image=46passed2.19s;23PDFcases coverunitmm/A4fit/auto-square/explicit/lề0-5-30/invalid/header-EOF/sourcekeep/mode-encoding/appendonepage. Khôngmockcanvasđểsoi thứtựimplementation; kiểmCanvasthật/pagecounter vàPDFparser/renderởQA. Focuscuối gồm28image/23PDF/16snapshot/16mutation → **83passed17.96s**. Full `backend/.venv/Scripts/python.exe -m pytest -c backend/pyproject.toml backend/tests -q --tb=short -W error --basetemp=.tmp/pytest11-03-04-full` → **1176passed167.56s**,51tests mới. Khôngskip/suppress/nớiassert hoặcđổi core. Frontendkhôngsửa/khôngchạylạitest-build, mốc87ở10làlịch sử.

**Nghiệm thu filethật:** pdfskillmarkoperationcreate/2expectedPDFdeliverablesđãchạytrướcauthoring. `.tmp/verify11_files.py` tạoDBriêng/synthetic1200×1600bốn gócmàu/chữViệt/highlight/nétmảnh, nhập/config/renderquathậtColor0/Gray90/BWOtsu270.6PNG-JPG ghi/mởPillow,full1199×1599hoặc1599×1199>previewcạnh1000;3PNGpixel-exactfull, JPEGMAE0.0536005354/0.0364181951/0.0201069163trên0..255/channel (khôngaccuracy). TênASCII/mime/mode/dims/EXIFrỗng đúng. Exportqua run_export/sharedworker/snapshotlease,0ExportRecord, tệpQAghiởresultsriêngchứkhôngartifactAPIgiả.

4PDFonepage:ColorportraitPNG5mm,Gray90auto-landscapePNG5mm,ColorforcedlandscapeJPEG30mm,BW270forcedportraitPNG0mm. `.tmp/inspect11_pdf.py` dùngbundledPython/Pypdf6.10/Poppler:4fileđúng1page,MediaBox595.2756×841.8898pointhoặcđảo,1fullimageXObjectđúngresolution/mode/Rotate0,matrixfit<.001point;3PNGnhúngexactfull,JPEGlossy. Render96dpi/16gócmẫutheofitrectmaxdelta2. Đãxemcontactsheet4render: khung/mép/chữ/highlightđủ, tỉlệđúng, forcedorientationcóletterboxnhưcôngthức, khôngautoxoayhướngchữ. HaiPDFmẫuportrait/landscapegiữlàdeliverables, haiPDFforcedchỉlàQA;6images/4PDF/4raster/contactsheet/JSON/DBtổnghợpởignored `experiments/results/mvp11-03-04-verified/`. KhôngcàiPypdf/Popplerintovenvhoặcthêmdependencyruntime.

**Restart/bảo toàn:** snapshottrướcnạpcode14tài liệu/49trang/147hashnguồn hiệncó vàSQLitebackupAPI vàoresultslượt03–04. Gracefulstopphase11-01-02, Start-ProcessHidden cùngDB/8000/stopfilemới `.tmp/phase11-03-04.stop`. Scriptverify11_03_04_productafter soSessionDetail/147hashvàmọirowDBbằngnhau:14sessions/49pages/542artifacts/49page_configs/25detection_runs/13render_runs/0exports/schema_version;FKcheckrỗng. Core/CLI/requirements12hashM1/OpenAPI11path14method/schema3giữ. Vite5173/usertabkhôngđụng, khônggửiảnh/DBrabênngoài.

**Bàn giao:** README/AGENTS/plan/todo/MVP/API/image/projectmap/export-snapshot/export-encodingđồngbộ82main+10AUX/11.01–04checked/checkpoint11-C1đạt/next11.05. KhôngAUX/auditcảphasekhimớixong4/8. Core/dataset6development1doc_01/test0/nợimg004-006vẫngiữ; khôngUndo theo yêu cầu. ExportPDFnhiềutrang/commitArtifact-ExportRecord/API/UI/downloadHTTPcòn05–08.

**QA cuối11.03–04:** `.tmp/qa11_encoders.py` đạt11tài liệu/224link nội bộ,82main/10AUX/110ID/11.01–04checked/05–08pending/checkpoint11-C1đạt/cổng11pending/next11.05.6ảnh/3PNGexactfull/4PDFonepageđọc-render/16corner samplesmaxdelta2/14productdocs49pages147sourcehash/allSQLrowsnguyên/coreM1/11path14method/schema3/ignore đềuđạt. CentricMem card kỹ thuật shelfdocument-scanner: sessions/2026-10-18T094524Z-mcp-5583ee.md, khôngảnh/bímật.



## 18/10/2026 — MVP11.05–07: ghép/lưu, API và UI tải ảnh/PDF

**Kết quả:**85main+10AUX/110ID,11.01–07 vàcheckpoint11-C2đạt;nextMVP11.08 kiểmchứngcuối/rà8task. Cổng11/M3chưađạt. Dùngusing-agent-skills/incremental/TDD/API/git/Ponytail/review/docs/frontend/browser vàpdfskill;khôngspawnagent/commit/push/deploy. [Luồng xuất](export-workflow.md) ghi hànhvi/giới hạn/bằng chứng.

**11.05:** services/exports.publish_export nhận immutable snapshot dưới lease,Canvasduynhất/lặpappendtheoorderrequest/fullPNG/rotationđãrender;PNG-JPGdùngencoderđãcó. Encodecomplete→ArtifactStoretemp/fsync/publish→writertransactionrecheckowner/R/config/fullreference→Artifact+ExportRecordorderedpagesnapshotcùngcommit→receipt. Khôngsửaconfig/revision/order/timestampphiên. Lỗirollback/cleanupchỉoutputmớichưa reference, giữfile/recordcũ;crashcóthểorphan. REDmissingpublish→7testsGREEN4.89s,3formats/4faultencode-write-register-commit.

**11.06:** api/exports.POST201qua run_export/sharedexecutor1active2waiting,maininclude/errorhandlerExportProcessingError500PROCESSING_FAILEDsanitized. GETartifactMIME/nosniff/private-no-storehiệnhành. 11HTTPtests mới gồmformats3,invalid6,429/failure/recovery,busybarrier/secondexport409/rename409/health200/unlock. RED10failed1passed(foreign404trùngroute404cũ);portaltestbanđầuawaitFutureholdbịblock,đãsửatestbằngtrảFuturetronglist,khôngnớiassert. Combined18passed13.45s. OpenAPIsettestthêmroute:12path15method/schema3.

**11.07:** DTOs/clientexport/details,exportFlow.ts+7tests,ExportPanel,ScannerPage/SourcePrevieweditingstate/locked,CSSvànpmtestscript. GETpreflightexactR/confirmed;chỉdefinitive409PAGE_NOT_RENDEREDhợplệmớirenderthiếuđúngrevisionrồiPOSTlạimộtlần;khôngPUT/auto-confirm/network-or-429retry. Chặndirtyselected/invalidoptions/duplicateclick/lateunmount;giữdirtyunselectedquaGETđốisoát. Receiptkiểmidentity/order/Rtrướckhilinkdownload. Linkcũclearquaselection/options/revision/selecteddirty. PendingkhóamutationUI. Clientwiretestthứ8kiểmexactpayload/details/noautoretry.

**Kiểm thử cuối:** backend/.venv/Scripts/python.exe -m pytest -c backend/pyproject.toml backend/tests -q --tb=short -W error --basetemp=.tmp/pytest11-05-07-full → **1194passed195.83s**. Frontend npm.cmd test → **95passed252.9859ms**;npm.cmd run build gồmtypecheck→39modules186ms,JS298.11kB/gzip92.09,CSS12.88/gzip3.22. BackendfullchạyxongtrướcsửaJSXkey/aria/effectvàdocstring,sauđókhôngđổilogicbackend;frontendtests/buildđãchạylạisaucácsửanày. Khôngskip/suppress/nớiassert.

**Browser/lỗiđãsửa:** QA3ảnh1120×1600PAGE1/2/3,Color0°/Gray90°/BWOtsu180°,r1/1/2. Chưaconfirmedtrang3bịchặn;chủđộngconfirmr2→export409→renderchỉ2+3→retry201,khôngrenderlại1. TảiPDF/PNG/JPGthậtsangDownloads/copyevidence. Dirtyselected270°bịchặn,trả180°cũxuấtPNG;dirtytrang3ngoàichọntrang1giữ270°sauxuấtJPG. RàconsolethấyduplicateReactkeydocument.idcủaUploadPanel/ExportPanel;rootcausesiblingscùngkey,đãprefixexport:vàchạylạitabmới→khôngerror/warning.320/768khôngtràn,resetviewport,tabproductgiữdeliverable;khôngcóharness/testhooktrongproduct.

**PDF/ảnhthật:** .tmp/verify11_exports_runtime.py đối chiếu4recordđầuvớiDB/exactorder/fullsource;APIPDForder[3,1,2],UI[1,2,3]. .tmp/inspect11_exports_pdf.py dùngbundledPypdf/Poppler72dpiđọcrenderđủ6trangvàxemcontactsheet;embeddedimagestrùngfulltừngpixel,MediaBoxA4/theoW-Hsauxoay/matrixfit/lề5đúng,khôngxoaythêm. FullColor/BW1119×1599,Gray1599×1119;PNGmodeLMAE0,JPGcolorRGBMAE0.0829946032/255,cùngdimensions/EXIF-ICC sạch. Các lầnxuấtlạikhiQAUIthêmrecordriêng;khôngcoiMAEảnhsyntheticlàaccuracy. PDFảnhkhôngOCR.

**Bảo toàn/bàn giao:** .tmp/verify11_exports_product.pybefore/aftervàSQLitebackupgiữ14docs49pages147sourcehash/alloldSQLrows (542artifact/25DetectionRun/13RenderRun),FKcheckrỗng;core/CLI/requirementsM1nguyên/schema3/12path15method. BackendgracefulrestartcùngDBđểloadroute,stopfilemới.tmp/phase11-05-07.stop;8000/5173đangchạy. Evidenceignored experiments/results/mvp11-05-07-verified/:runtime-checks/browser-checks/pdf-inspection/product-verification/images/PDF/contactsheet/export-ui. Khôngđưaảnh/DBrabênngoài. README/AGENTS/plan/todo/MVP/API/image/projectmap/snapshot/encoder/newexport-workflow/frontendsmokeđồngbộ. Dataset6development1doc_01/test0vànợimg004/006giữ. ChưaAUX/auditcảphase;11.08cònlượtkiểmchứngcuối/restart/lifecycletoànluồng.

**QA cuối11.05–07:** .tmp/qa11_exports.py đạt85main/10AUX/110ID,11.01–07checked/08pending/C1-C2đạt/M3pending;13tài liệu/246linknội bộ hợp lệ,12path15method/schema3,PDF6trangexactfull/order/A4,PNGexactfull vàbađịnhdạngđãtảithật. Sau sửaReactkey, kiểm lạinháp90°ởtrang1:chọntrang1bịchặn/linkcũbỏ;chỉchọn2+3xuấtPDFđược/nháp90°vẫngiữ;đặtlại0°khôngPOSTconfig. Consolecuốitrống,viewportreset,screenshotexport-ui.png mới/giữtabdeliverable;QA7ExportRecordriêng. Productaftercuốigiữmọidữliệucũ. CentricMemcardkỹthuật shelfdocument-scanner: sessions/2026-10-18T131523Z-mcp-f878ea.md;khôngảnh/DB/bímật.


## 18/10/2026 — MVP11.08/AUX11.01: nghiệm thu cuối và rà tám task

**Kết quả:**86main+11AUX/110ID,đủ11.01–08/checkpoint11-C1/C2/cổng11/M3đạt;nextMVP12.01. [Audit8task](audit-phase-11.md) cóma trận/nguồnbằngchứng/giới hạn. Dùngusing-agent-skills/TDD/review/Ponytail/browser/pdf/docs;khôngagents/commit/push/deploy. Khôngsửaapp/thuậttoán/deps/schema,mớithêm5integrationtests vàdocs.

**Tests mới:**test_export_api.py thêmhaioutcomeactualPOSTexportgiữbarrierđếnwriter/finally,9yêucầukhácbị409SESSION_BUSYgồm8mutation/secondexport;ownerJSON/filesnguyên,chưaDBExportRecord,GET/health/tàiliệukhácvẫnđược. InjectappendlỗiởpagePDF2khôngoutputfile/recorddở,sanitized500PROCESSING_FAILED;exportsaulạithànhcông. ThêmbadạngPDF/PNG/JPGđãcommit→configR2→đónglifespanapp1→mởapp2→cùngoldreceiptpages/fullhash/outputbytes→renderR2/exportmớimàtệpcũkhôngđổi. Banđầu15pass/1fail12.22sdohelperfilescóchứaSQLitebytesmàtestcốýrenameothertài liệuđượcphép;đãsửachụpbaselinechínhxácsaurename,giữmọichecktrước/owner/file/record. Focus16passed13.31s. Đây làbổsungnghiệmthu,hànhviappđãđúng,khôngpháappđểgiảRED.

**Kiểm thử cuối:** backend/.venv/Scripts/python.exe -m pytest -c backend/pyproject.toml backend/tests -q --tb=short -W error --basetemp=.tmp/pytest11-phase-final → **1199passed217.02s**. Frontend npm.cmd test → **95passed297.0281ms**;npm.cmd run buildgồmtypecheck →39modules173ms,JS298.11kB/gzip92.09,CSS12.88/gzip3.22. Giữkhôngskip/suppress/nớiassert;phase11thêm128backendtests/8frontendtests so1071/87ởphase10.

**Runtime/UI/PDF:** .tmp/seed11_final.py tạoQAriêng3ảnh1120×1600PAGE1/2/3,Color0/Gray90/BWOtsu270/fullquad/r1. UIđưa3lênhai lầnthành[3,1,2]. Tải4filethật:PDFautoPNG/lề5,PNG-JPGColor,PDFportraitJPEG/lề30. .tmp/verify11_final_runtime.pybefore-restartđốichiếubytesGETartifact/fourExportRecords/30artifactSHA/order/R/full. .tmp/inspect11_final_pdf.pydùngPypdf/Poppler72dpiđọc/render/xem6trang,fullPNG3embeddedpixel-exact;JPEG3cùngdimensions/mode/MAE.0668804956/.0988432411/.0780307844,A4MediaBox/matrixđúngoptions. PNG1119×1599RGBMAE0,JPGcùngsize/MAE.0829946032/255/EXIF-ICCsạch. KhôngcoiQA/MAElàaccuracy;PDFảnhkhôngOCR.

**Physicalrestart/mởlại:** gracefulphase11-05-07.stop→Start-ProcessHiddenrun_phase07_backend.pyphase11-final.stop/cùngDB. Runtimeafter-restartđủSessionDetail/4ExportRecord/30SHA bằngtrước/FKcheckrỗng. UIreload/chọn3trangchỉGET,hiệnfullr1vàdimensions1599×1119/1119×1599/1599×1119theoorder. POSTexportmớisauđó201,UIđọcDOMworkingtrue vàrename/delete/order/fullimage/render/uploaddisabled,sauđóTạotệpxuất/Tảikhảdụng. KhôngQAroute/harness/fetchmocktrongproduct.320/768/1440khôngtràn,viewportreset,consoletrống,screenshotproduct-view.png/giữtabdeliverable.

**Bảo toàn/bàn giao:** .tmp/verify11_final_product.pybefore/aftergiữ15old docs52pages156sourcehash/alloldSQLrows:15sessions/52pages/575artifacts/52configs/7exports/25DetectionRuns/16RenderRunsvàschema_version;FKcheckrỗng/core-CLI-requirementsM1nguyên/schema3/OpenAPI12path15method. QAriêngcó3pages/4exportsbanđầuvàmộtPDFsau restart. Evidenceignoredexperiments/results/mvp11-final-verified/runtime-checks/restart-checks/browser-checks/ui-image-bindings/pdf-inspection/product-verification/qa.jsonvàfiles. ĐồngbộREADME/AGENTS/plan/todo/MVP/API/image/projectmap/exportdocs/frontendsmoke;newaudit-phase-11.md,khôngtíchphase12hoặctasktùychọn. Dataset6development1doc_01/test0/nợimg004-006giữ;limitleaseoneprocess/crashorphan/noGCbền/noidempotency/history/noOCR/UUIDfilenameghi rõ. Backend8000/Vite5173giữchạy,stopfile.tmp/phase11-final.stop;khôngảnh/DBrabênngoài.

**QA bàn giao cuối:** .tmp/qa11_final.py đạt86main/11AUX/110ID,đủ8task11/M3passed/next12.01,14tài liệu/269linknội bộ hợp lệ. ĐốichiếusáutrangPDF/full/order/options,PNGexact/JPEGlossy/restart30SHA/bốnrecordcũ/ngũrecordQAhiệnhành,UIbusy/reopenchỉGET/consoletrống vàbảo toàn nguồn đềuđạt. Auditphase11đãviếtlạivới ma trận dễđọc;khôngthaylogic sau fullsuite. CentricMemcardkỹthuật shelfdocument-scanner lưu thànhcông,khôngảnh/DB/bímật.


## 18/10/2026 — AUX11.02: tự nhận diện vùng sau nhập một/nhiều ảnh

Theo yêu cầu người dùng, đã đổi mặc định UI thành upload→detect tuần tự từng ảnh mới để chỉ cần duyệt/chỉnh/xác nhận. Không đổi backend/thuật toán/API/schema hoặc tự confirmed/render.86main+12AUX, M3giữ,nextMVP12.01. [Hànhvi/giới hạn](auto-detect-on-import.md). Dùngusing-agent-skills/incremental/TDD/frontend/browser/Ponytail/review/docs;khôngagents/commit/push/deploy.

Tệp sửa: importDetection.ts/detectionProposal.ts,uploadBatch/UploadPanel,ScannerPage,PageList,pageRenderState,tests/package vàdocs. Sharedproposal gate tránhmỗiluồngvalidatekhácnhau. Detectlỗisauupload giữpage/quota,khôngretryPOST;báokếtquảrõ/tiếptụcbatch. Appendpage sau khi detectsettled tránheditortrangmớinhậnresponsemuộnlấnnháp. InitialhydratechỉfreshR0/null/false/đúnglatestsourceR0/chưaloaded;gócđãlưu/cấu hìnhcũ/liveeditor/nhápeditkhôngbịthay.

TDDRED thiếuimportmodule vàkhung5%khôngđượcproposal:23pass/2fail. GREENsaucodetừnglát; mộtassertmessage/chỉnh tayđãsửađúngngữnghĩa“bằng tay”,khôngruntimebug.7tests mới kiểmsequence/gate/quota/detecterrorcontinues/uploaderrornondetect/busy/doublebatch vàinitialrestore/manualrequired/preservedsaved-livecorners. npm.cmdtest→**102passed298.4506ms**;npm.cmdrunbuildgồmtypecheck→41modules178ms,JS299.66kB/gzip92.54. Backendkhôngsửa;focusedtest_import_api/test_detection_api/test_reopen-Werror→**36passed11.13s**. Full1199mốcM3làlịchsử,khôngrerunfull.

BrowserQAriêng có1Colorfull,đổinhápGrayrồichọnpaper/broken/blankcùnglượt. PaperproposedS.7820204972,broken415khôngpage,blankmanual_required;2newpages/2DetectionRuns/2POSTdetect,nhápGray/Colorfullcũgiữ. Duyệt/reloadđúngproposal/5%khôngdetectthêm;confignewR0/null/false/chưarender. Handlequadkhớpbackendnormalizedmaxdelta1.1102230246251565e-16<1e-12;assertbyteequalfloatbanđầuđãsửathànhdungsaicựcnhỏ,sốđothựctếghiJSON,khôngđổigeometry. Console0/responsive320-768khôngtràn/viewportreset/giữtabproduct.

.tmp/verify_auto_import.py vàverify_auto_import_product.pybefore/afterkiểm17old docs58pages174sourcehash/alloldSQLrowsnguyên;core/CLI/requirementsM1/schema3/OpenAPI12path15methodkhôngđổi. Evidenceignoredexperiments/results/auto-detect-import-verified/:seed/document/browser-checks/verification/product-verification/source/screenshot. Khôngảnh/DBrabênngoài. Đọc lại5.5.1–3 hướngthuậttoán;khôngthayCanny/Otsu/contour/scoring/heuristic hoặcchữconfirmed=false. Nợimg004/006vẫngiữ;auto orchestrationkhôngphảicải thiệnaccuracy.

QA bàn giao: .tmp/qa_auto_import.py đạt86main/12AUX/110ID/next12.01,11tài liệu/253linknội bộ,102frontend/36APIhồiquy vàmọicheckbatch/quota/proposal/reopen/nháp/bảotoàn. CentricMemcard kỹthuật đã lưu shelfdocument-scanner;khôngảnh/DB/bímật. Codefrontend khôngsửa sau test/build/browser;backendkhôngđổilogic.


## 18/10/2026 — Hồi quy callback nhập ảnh sau AUX11.02

Người dùng báo onDetecting is not a function. Tab đang mở hiện ảnh đã lưu nhưng không có POST detect. Runner cũ gọi onUpload(file) thiếu callback; useState giữ function implementation qua Fast Refresh là nguyên nhân phù hợp với trạng thái này. Test mới mô phỏng caller cũ tái hiện đúng TypeError tại importWithDetection sau upload trước detect (5pass/1fail). Sửa helper bằng callback mặc định và UploadPanel dùng useMemo(factory,[factory]); khóa batch bình thường vẫn giữ. Không sửa backend hoặc thuật toán.

Sau sửa103frontendtests359.4028ms/typecheck/build đạt,41modules203ms/JS299.67kB/gzip92.55. Browser QA riêng nhập một paper.png qua file chooser→done/đã đề xuất vùng,một trang/một DetectionRun,binding nguồn đúng,revision0/corners persistednull/confirmedfalse/chưarender. Quad UI bằng proposal (delta0),console0. Chọn tệp của công cụ browser phản hồi rất chậm dù đã đặt timeout; không gọi thời gian tool là thời gian xử lý CV.

Evidence ignored experiments/results/callback-upload-fix-verified: seed/browser-checks/product-view/verification/product-before-after/product-verification và SQLite backup. Đối soát giữ18old docs59pages177sourcehash cùng mọi row SQLite/FKcheckrỗng/coreM1/schema3/OpenAPI12path15method nguyên. Helper kiểm SQL ban đầu dùng UUID có gạch nối trong khi SQLAlchemy lưu hex nên đếm0; sửa phép bind về hex rồi xác nhận đúng1run,không đổi app. Ảnh người dùng ở lượt lỗi vẫn lưu; không tải trùng,không tự nhận diện lại hoặc thay nháp đang mở. Có thể dùng nút nhận diện cho đúng trang đó.

README/AGENTS/plan/todo/MVP/project-map/contracts cập nhật số test hiện hành; auto-detect-on-import và scanner-smoke ghi nguyên nhân/kiểm chứng. Giữ86main+12AUX,nextMVP12.01;không tính sửa lỗi này thành task mới. Bộ backend36focused/full1199 vẫn là mốc trước,không tuyên bố chạy lại. Không agent/commit/push/deploy hoặc gửi ảnh/DB ra ngoài.


## 18/10/2026 — Kiểm tra báo lỗi xác nhận vùng rồi xuất

User báo đã bấm xác nhận nhưng vẫn bị chặn xuất. Đọc tab hiện hữu và log: một trang tự có proposal, cấu hình vẫn revision0/confirmedfalse; chưa thấy PUT config từ các lần bấm trước, console không lỗi. Bấm Xác nhận vùng trên đúng tab/trang theo yêu cầu user: PUT200, revision1/confirmedtrue, nút Tạo tệp xuất mở. Bấm tạo: export409 PAGE_NOT_RENDERED → GET đối soát → render200 tại r1 → export201, UI hiện Tải PDF · 1 trang. GET lại xác nhận page/render cùngr1; PDF có header/EOF hợp lệ và byte/hash lưu verification.json. Không quy lỗi cho người dùng; chưa tái hiện được nguyên nhân khiến lần bấm trước không gửi PUT, không tuyên bố đã sửa bug khi chưa có chứng cứ. Không sửa code hoặc đổi điều kiện xác nhận, không chạy test lại vì không đổi implementation.

Evidence ignored experiments/results/confirm-export-check/:browser-checks/verification/export-ready và okoko.pdf. Chỉ xác nhận vùng user đã yêu cầu, tạo bản quét/PDF của đúng trang đang chọn; không xóa/nhập trùng ảnh hoặc gửi ra ngoài. Không thêm task/checkpoint,86main+12AUX/nextMVP12.01 giữ nguyên.


## 18/10/2026 — MVP13.01–02: chuẩn bị bộ ảnh và nhãn nhóm đầu

User chấp nhận giảm quy mô còn khoảng20ảnh/5tài liệu, ảnh bổ sung chưa có và sẽ cung cấp ngày mai. Giữ6ảnh hiện có/doc_01/development/test0; không tạo bản sao/ảnh tổng hợp để bù số tài liệu. Inventory9tệp trong experiments/data:7JPG đầu có1trùnghash,haiảnh anhtestnew/WrongEXIF đã dùng thử thuật toán và chưa xác nhận nhóm nên không nhận làm test. Bố trí đề xuất3development docs/2test docs; giữ toàn bộ6ảnh cũ dù số cuối chênh nhẹ20. README/MVP/plan/todo/dataset cập nhật quy mô. Không đánh dấu giai đoạn12 hoàn thành hoặc bỏ qua.

Đã triển khai experiments/annotations.json/schema1 và validate_annotations.py: dùng lại manifest validator/hash/path guards/validate_quad, kiểm nguồn PNG sau EXIF, W−1/H−1, dimensions, hash, IDcoverage, topology/status/reason/reviewed. CLI mặc định từ chối nhãn chưa duyệt; --allow-unreviewed chuẩn bị overlay; --output-dir tạo thư mục mới,PNG cùngdimensions/đánh số0–3/snapshotJSON ghi cuối. Không gọi detector,sort tay,warp hoặc sửa nguồn. Thêm tag wrinkled/cropped để giữ ca nhàu/cắt góc, img_002 thêm cropped theo quan sát góc dưới trái.

Đã xem cả6nguồn1536×2048; gán thủ công img_003/004/005 từ mép giấy thật, mở3overlay full và sheet6ảnh. Img_001/006 gấp lật gây mép trên gãy/nonplanar,002góc dưới trái sát/cắt khung: giữ unlabelable,cornersnull và reason,không suy diễn góc phẳng. Nhãn do codex_manual_visual_v1 chọn và tự rà,không lấy từ proposal; reviewed6/6 không đồng nghĩa được người thứhai xác minh hoặc sai số bằng0. Góc bo nhẹ có sai số gán tay chưa đo, chưaaccuracy/IoU/benchmark. Validator trên dữ liệu thật đạt6records/3labeled/3unlabelable/reviewed6,manifesthash/split đạt.

TDD: test_annotations mới ban đầu RED thiếu module; tag wrinkled/cropped RED với validator cũ rồi GREEN. Kiểm thử34ca lần đầu lỗi setup do pytest temp mặc định bị sandbox chặn; dùng --basetemp trong workspace,không sửa test để né validation. Focus35passed0.83s. Fullbackend -W error --basetemp=.tmp/pytest13-full →1216passed186.53s, thêm16annotations tests và1conditiontest so1199. Các ca kiểm binding/hash/dimensions/winding/crossing/foreign/coverage/duplicate/nhãnchưa duyệt/unlabelable/nguồnkhôngđổi/khôngghiđè overlay. Frontend không sửa,không chạy lại103tests/build cũ. Runtime app/API/DB/thuật toán/threshold/requirements không đổi,khôngrestartserver.

Evidence ignored experiments/results/mvp13-01-02-verified/:inventory,overlays-draft/overlays snapshots,review-sheet,verification,pytest.log. Hash nguồn đúngmanifest; không gửi ảnh/DB ra ngoài. Kỹ thuật đã sẵn sàng và nhãn nhóm hiện có đã rà; task13.01/02 vẫn unchecked để chờ bộ ảnh ngày mai rồi chuẩn hóa/đăngký/gánnhãn/duyệt bổ sung trước nghiệm thu toàn bộ. Giữ86main+12AUX/110ID; không làm13.03/metrics,không tự nhận test độc lập khi test0. Khôngagent/commit/push/deploy. Dataset.md ghi lệnh và cách nhóm tài liệu để tiếp tục.


## 26/10/2026 — Hoàn tất MVP13.01–02 với doc_ver2

User cung cấp experiments/data/doc_ver2 và chốt bộ hiện có là đủ, thay mục tiêu20ảnh/5tài liệu. Có8file/7SHA nguồn khác nhau; file (1) trùng img_009, giữ file gốc nhưng không đếm. User xác nhận7ảnh chụp cùng tờ hoặc cùng nội dung. Chốt13ảnh/2tài liệu:6doc_01/development đã dùng thuật toán và7doc_02/test mới,img007…013. Không chia ảnh cùng tài liệu giữa hai tập. Nhóm anhtestnew/WrongEXIF cũ chưa identity và đã dùng thử vẫn không thêm vào test.

Dùng normalize_one.py hiện có cho7JPEG vào thư mục mới,giữ rawbytes/PNGpayload/hash/thumbnail/metadata;6ảnh1536×2048, img0112048×1536. Không chạy detector hoặc tune trên test,không import vàoDB. Gán7quad thủ công theo nguồn sauEXIF/W−1/H−1,đã mở từng nguồn và từng overlayfull. Nếp/curl nhẹ nên quad là xấp xỉ4mốc,không groundtruthmask chính xác. Bộ nhãn13records/10labeled/3unlabelable/reviewed13; nhãn6ảnh cũ giữ nguyên,3ca gấp/cắt góc vẫn giữ lý do. Singleannotator chưa kiểm sai số nhiều người,không lấy outputdetector làm nhãn. Chưa accuracy/IoU/benchmark.

validate_dataset.py --check-files và validate_annotations.py đạt trên toàn13ảnh. Focused test_annotations/test_dataset_manifest -W error --basetemp=.tmp/pytest13-data-ver2-20261026→35passed1.62s. Không sửa implementation,fullbackend1216/frontend103/build là bằng chứng18/10,không chạy lại trong lượt dữ liệu này. Codehash validator/tests khớp snapshot18/10; all6old manifestrows/annotations nguyên,raw8file và13nguồnPNG đúnghash. Không đổi app/core/API/DB/requirements,không restart hoặc sửa dữ liệu người dùng trên app.

MVP13.01/02 checked theo quy mô được chốt26/10,88main+12AUX/110ID, next13.03;13-C1 chờ03/giai đoạn12 chưa nghiệm thu. README/AGENTS/plan/todo/MVP/dataset/projectmap/contracts cập nhật trạng thái hiện hành,giữ mốc cũ trong progress. Không coi13ảnh/2tài liệu là20/5; thiếu phủ nhàu rõ/glare/highlight, cùng nền và một tài liệu mỗi split được ghi rõ. Không làm13.03–08 hoặc chạy detector trên test trước frozen13.06.

Evidence ignored experiments/results/mvp13-doc-ver2-20261026/:inventory,snapshots manifest/annotations trước,normalized,overlays-draft/overlays,review-sheet và verification. Ảnh chứa thông tin riêng được giữ cục bộ/ngoàiGit,không chép nội dung cá nhân vào tài liệu và không gửi ra ngoài. Không agents/commit/push/deploy. Quy mô hiện tại đã được user chấp nhận;không yêu cầu thu thêm để ép kế hoạch cũ.


## 26/10/2026 — MVP13.03–04: metrics và đối chứng detector development

Đọc lại task/dependencies,hướngthuậttoán5.5.1–3,corepolygonIoU/detection vàartifactwriters. Dùngusing-agent-skills/incremental/TDD/review/docs/Ponytail; khôngagents. Dùng lại coreIoU đã có,không viết bộgiaođagiác khác. experiments/metrics.py chấpnhận8cycle matchingchỉởđánhgiá,sauvalidtopology;cornererror=minmean4sourceEuclidean/subpixel vàchiaD. ThiếuproposalGT→IoU0,mẫu sốgiữ;cornererrornull vàbáosốmẫu;3unlabelable khôngGT đượcbáoriêng. Fixture giống/đảo/đổiđiểmđầu/khác/invalid/thiếuproposal/aggregate/anisometric đềuđạt.

ThêmGaussian0/closingFalse explicit trongsharedhelpersdetection vàIDg0/provenance,default5/True khôngđổi. Collect/generate/describe/score/NMS/conditionalregion dùnglại;largest chỉmaxcontourarea trongcùngvalidpool trướcNMS,cùngstatusgate. Khôngthêmngưỡng/weight,khôngđưa thínghiệmvàoPageConfig/UI/HTTP. validate_annotations cósplitoptionalđểevaluator chỉmở/hash/decode development;defaultCLI toàn13giữ. Bốnconfig trongdetection_trials.json mỗiđốichứngchỉđổi1yếu tố. EvaluatorPNGdecode từBytesIO verifiedpayload,chặnnguồn/dims/label hashđổigiữavalidationvàđọc;giữsource readonly/hash,CSV/status/error/metrics/time/aefb,metadataallattempts/description/stages/rawCanny vàlegendGT/proposal/diagnostic đúng.

TDDRED metrics thiếu module,2ablation tests thấtbạivìchưaGaussian0/closingarg,1dev-split test thấtbạichưaarg. GREEN65ca rồi39/87/40ca theolát. CLIunit tạo4profile trênfixture vớiảnhheld-out khôngtồntại vẫnthànhcông,đọclạimetadatabinding/outputkhôngoverwrite;defaultheader13 củaannotationvẫnfailnếufiletestthiếu nhưđúnghợpđồng. Reviewcuốibổsungconfigschema list/boolversion/nullprofile RED3fail/1pass→guardtypes;nguồnthayđổisauvalidate bịchặn. Focus44passed3.00s; fullbackend+experiments cuối-Werror --basetemp=.tmp/pytest13-final-full →1244passed166.50s (1219backend+25experiments),khôngskip/nớigate. Trướcguardcuốiđãcó1240passed166.29s làmốc trunggian. Frontend103/build khôngrerun vìUI/typesHTTP khôngđổi.

Chạy6development×4profile=24runs/0error,bảnchínhmvp13-03-04-verified/final. Lượtdevelopment rồi development-final giữlịchsử,bảnfinal chạy lại sauguard/hash/docstring thayđổi đểsummary khớpcurrentcode;khôngtune hoặcchọnkếtquảtốtnhấtqua cáclượt. Tấtcảphânảnh/stagepixelsgiữquacáclượt,chỉtiming/codehash cậpnhật. Chưa benchmark/repetitions/cáchlytảimáy;timingscore quan sátsingle-run,khôngdùngsuytốcđộ/p95. Khôngchạy7ảnh test/modelselection;fixtureunitcótestrowschỉđểkiểm cáchly,khôngdatarealtest.

Đãxem6comparisonđủ4panel/ảnh.3GT meanIoUscoring.952871,largest.951532,noGaussian.901162,noClosing.951532;cảbốn2/3GT≥.90,proposal5/6ởscoring/large và6/6ởnogauss/noclose. img004vẫnregionănbànIoU.872497,error54.771px;nogaussCannyănbànnặnghơnIoU.716925/error155.015px. img005scoringe.512048/f.977604/S.501182 kháclargest e.490972/f.976260/S.493638:IoU.992319vs.988302,khôngsuyrộngvớimột tài liệu/GTthủcông. img001/006noclosing lấyôly/dòngchữ;khôngGTnênkhôngbịaIoU. [results.md](results.md) ghi bảng/mẫu số/casai/giới hạn vàlệnh.

Đối chiếu .tmp/detection-before13.py vớidefaultmới vàprofile scoring trên6development:result/status/corners/S/descriptions/candidates cùngrawCanny/closed-region/blur/overlay giốngnhau,sourcekhôngmutate. Codefiledetection.py cóthêmopt-in nênhashkhácM1;khôngsửa snapshot/requirementsM1 đểgiảunchanged. Defaultpixels giữ làbằngchứngthực,khônghứa codehashgiữ. Nhãn/manifesthashvà13nguồn giữ;PNGrawmaps/config/metrics/score đượcQAđốichiếutừmetadata. HTTP/DB/deps/UI khôngđổi,khôngrestartserver hoặcghiDBuser.

13.03/04 và13-C1checked,90main+12AUX/110ID,next13.05.13-C2/cổng13/13.05–08 cònchờ,giaiđoạn12 chưa nghiệmthu. ĐồngbộREADME/AGENTS/plan/todo/MVP/dataset/results/algorithmnotes/contracts/projectmap. Evidenceignoredmvp13-03-04-verified/final,default-parity,verification,pytestlog vàcode-before copy;khôngảnh/DBrabênngoài,khôngcommit/push/deploy. Khôngcoi24runs hoặctestcount làaccuracy.


## 26/10/2026 — MVP13.05–06: so nhị phân và khóa trước test

Đọc lại task/phụ thuộc, thuật toán enhancement/config/geometry và kết quả 13.03–04.
Dùng using-agent-skills, incremental implementation, TDD, Ponytail, review/docs;
browser skill cho hồi quy và PDF skill để đọc/render PDF QA. Không agents.
User chọn “Chạy hồi quy cần thiết trước khi khóa” khi phát hiện 13.06 phụ thuộc 12.07.
Điều chỉnh phụ thuộc chỉ cho cổng khóa thực nghiệm; các checkbox giai đoạn 12 giữ chưa xong.

Thêm evaluate_enhancement.py dùng validate_annotations(split=development), đọc đúng payload PNG
đã kiểm hash/dimensions rồi giải mã qua BytesIO. Chỉ dùng GT thủ công; warp một lần, hai lượt
enhance_document giữ BW/Median3/không CLAHE/rotation0/block31/C10, chỉ đổi threshold.method.
Kiểm prepared_gray bằng pixel; lưu actual filtered/gray/histogram/Otsu t/scope, full BW,
comparison/crop100%, config/hash và CSV. Không detector/auto-confirm/HTTP/DB trong evaluator.
Unlabelable báo lý do, lỗi giữ dòng/exit1, output mới và từ chối ghi đè; không mở ảnh test.

TDD RED thiếu module → 3 tests đạt 0,85s. Fixture đầu bị validator chặn vì dùng trùng hash
cho hai ảnh; sửa fixture tạo hai ảnh khác nhau, giữ nguyên validation. Ca kiểm chứng chứng minh
cùng warp/gray/config, khác đúng method, block quá nhỏ không clamp, skip có lý do,
test sources cố ý không tồn tại vẫn chạy development và chặn nguồn đổi sau validation.

Runtime 6 ảnh development → 3 cặp/3 unlabelable/0 lỗi, 9 dòng CSV. img_003 899×1290 t147,
img_004 1118×1229 t172, img_005 1368×813 t186. Otsu pixel đen 41,86/46,37/51,28%;
Adaptive 7,59/7,16/6,49%, không gọi đây là accuracy chữ. Đã xem đủ 6 BW full, warp/crop:
Otsu làm đen bóng và che chữ; Adaptive giữ nhiều dòng hơn nhưng còn ô ly/đứt nét.
Dataset chưa có highlight thật/sáng đều kiểm soát. Tạo riêng minh họa synthetic có chữ Việt,
dải màu/mực nhạt: mất màu ở cả hai, Otsu mất nét nhạt, Adaptive tạo viền dải highlight.
Synthetic không thêm vào manifest/accuracy; metadata ghi synthetic_full_frame và hash generator.

Thêm freeze_config.py: xuất cấu hình thật từ preset/default detector, versions/score,
91 hash mã app/helper, hash cấu hình/manifest/nhãn, 31 distribution Python và dependency frontend,
môi trường Python/Node/OpenCV build/threads. So package thực tế với requirements/package.json.
Yêu cầu bằng chứng hồi quy trước ghi, file mới không overwrite; verify_frozen chặn drift snapshot.
Không giả commit hoặc sửa snapshot M1 cũ. RED thiếu module → 8 focused ban đầu đạt9,68s;
thêm các ca tamper preset/source/dependency/dataset và environment drift trước full run.

Full backend+experiments -Werror --basetemp=.tmp/pytest13-05-06-full: 1255passed203.28s
(1219 backend + 36 experiments), không skip. npm test:103pass/0fail/0skip521.4369ms;
npm run build gồm typecheck:41modules631ms. Không thay core/API/UI/dependency để đạt test.

Vì localhost đã dừng, mở backend/Vite cục bộ. Browser tạo tài liệu QA mới, nhập batch
paper/fake/paper:2 trang/2 detect,415 riêng ở giữa,config r0/chưa confirmed.
Chủ động xác nhận trang1 Color/render, trang2 BW Otsu/confirm. Chọn cả hai/xuấtPDF:
POST409 thiếu render → render đúng trang2 → POST201; tải thật bằng link trong browser.
PDF đọc pypdf/render Poppler/xem đủ2trang; ảnh nhúng exact full và thứ tự PAGE1/2 đúng.
Hai PNG full bằng core fresh từng byte, browser download bằng bytes artifactGET.

Route5GET sai/data/ID trả404 không lộ đường dẫn/trace, OpenAPI12paths. Graceful stop/start
backend mới cùng DB rồi UIreload:document/export/config/r1 và38artifact hash giữ;
GET phục hồi full,khôngPOST/PUTsau restart,100%view/consoleerror-warn rỗng.
Giữ61oldSQLrows và49artifact cũ đúnghash,FKcheckrỗng. Probe ban đầu đọc nhầm field nguồn
source_artifact_id thay vì normalized_artifact_id; sửa script QA theo PageRead,không sửa app.
Hai lần CIM trong sandbox không có quyền đọc; đọc lại metadata CPU/RAM bằng escalation read-only.

Bản frozen.json được tạo04:45:10UTC, mvp13-freeze-v1/SHA
ce89a90e2fb9ca092350886276201f87e81cd09c90e6507f799fceca6a8d8109;
--check tiến trình mới đạt. OpenCL native probe ghi queue unavailable và false, được ghi đúng
trong môi trường,không che log hoặc tuyên bố GPU chạy. CPU i7-11700F8C16T,
RAMOS34.017.787.904byte,Python3.12.10/Node24.15.0/npm11.12.1/OpenCV4.14.0.
Chưa đo p50/p95/RAMđỉnh hoặc chạy7ảnh test;13.07runner phảiverify_frozen trước xử lý,
hash runner mới riêng và không thay helper đã khóa sau khi nhìn test.

13.05/06 checked,92main+12AUX/110ID;13-C2 đạt theo cổng hồi quy được user chấp nhận,
next13.07. Giai đoạn12/13.07–08/cổng13 còn chờ. README/plan/todo/MVP/AGENTS/dataset/
results/algorithm-notes/contracts/project-map và verification-matrix/experiment-environment
cập nhật. Evidence ignored experiments/results/mvp13-05-06-verified; nhãn/manifest/source giữ,
không ảnh/DB ra ngoài,không commit/push/deploy. Backend8000/Vite5173 giữ cho user xem;
stopfile .tmp/phase13-frozen.stop. Không coi số tests/độ phủ proposal là accuracy.


## 26/10/2026 — MVP13.07–08 và rà đủ8task13

Đọc task/phụ thuộc, bản khóa/environment, helper detection/render/metrics/artifacts và API thật.
Dùng using-agent-skills/incremental/TDD/Ponytail/review/docs và workflow đo trước kết luận.
Đối chiếu PSAPI với Microsoft Learn để lấy WorkingSetSize/PeakWorkingSetSize theo tiến trình,
không lấy tracemalloc đại diện buffer native. Không agents/commit/push/deploy.

Không sửa91tệp đã khóa: thêm benchmark.py và6tests. Runner verify snapshot trước dataset,
ghi protocol trước pixel, chọn7test theo manifest;load exact PNGpayload/hash/dims và rawhash.
Accuracy debugtrue giữstages thực/GT/selecteddescription/mẫu số. Benchmark debugfalse,
core BGR đãdecode vsHTTPthật/SQLite riêng,GT-BWpreset31/C10/Median3/khôngCLAHE/rotation0.
Mỗiảnh1warmup+5đo trên4đường,perf_counter_ns vàPSAPI10mssampling,báo baseline/end/lifetimepeak;
giữmẫu lỗi,khôngretry/tune;freshHTTPIDs chứng minh khôngreuse kếtquả. OS cache/allocator khôngtắt.

TDD RED thiếu module/helpers→GREEN4memory/quantile/hash/frozen-gate tests.
HTTPfixture RED thiếuhelper rồi childverifyfail: snapshotdiff duy nhấtOpenCLtrue ởprocessmới
sofalseđãkhóa. Runner tái lập cv2.ocl.setUseOpenCL(false) trước verify trongcảparent/child,
khôngnới/checkhoặcđổifrozen. Synthetic fullcase bắt lỗi UUID chưastr trongmetadatawriter,
sửa callerstr(uuid4)→6testsGREEN11.10s; khôngsửahelperđãkhóa.
Full1261passed212.11s trước lượt đầu; 1219backend+42experiments,khôngskip.

Lượt đầu mvp13-07-08-verified/test/ chạy7ảnh đúngkhóa,7/7IoU≥.90/mean.995347/error2.303px,
168samples0error. QA thấyRAMHTTP~4.7MiB bất hợp lý;đọcUvicornlogvàPIDCSV chứng minh đangđọc
venvredirectorPopen.pid. Thêmassertserver-process.pid vàPIDUvicorn vàofixture→REDFileNotFound,
sửarunner childghi os.getpid/trảactualPID thaylauncher. GiữinitialMEASUREMENT_INVALID.json,
khôngsửaảnh/GT/threshold/S hoặcbảnkhóa. Runner versionv1.1 ghi hashriêng.

Fullcuối1261passed173.10s-Werror--basetemp=.tmp/pytest13-07-08-final. Chỉ bắtđầubenchmark
khixongpytest đểtránhCPUtranhchấp. Lượtfinal168rows/140đo28warmup0error,
35success/operation. p50/p95ms core detect238.8527/297.31905,render16.8652/21.02552,
HTTPdetect313.193/340.87657,render178.4996/204.4952. Sampledmaxworking setB
core111071232/122912768,HTTP163463168/163422208;PIDactual286360 khớpUvicorn,
servergracefulclosed. KhônggộpRAM/core-HTTPhoặcgọiđâyexactpeak/lạnhcache/populationp95.
Khôngchọntimingsđẹpgiữalượt;finaldùngtrọnlượt,kháclatencykhôngphảiđãtốiưuthuậttoán.

7testdoc_02 đềuCanny,6proposed/1warning;IoU.994511… .996386,
mean.995347032005372/cornererror2.3031296606px/.0009001523D.
img009a.325122/e.727423/f.994234/b0→score.5997499034<.6 nênwarning dùIoU.994511.
Đãxem7cặp overlaycontactsheet vàảnh009 riêng,bámgiấy;khôngcopythôngtinriêng.
Phầnreportdevelopmentgiữ3GT/3unlabelable vàca004ăn bàn/Otsuđenbóng,
khônglấykếtquảtestin/dễhơnđểchegiớihạn. Khôngtune test;testđãquan sáttừinitial,
lượtfinalchỉsửa đoPID,khôngtạotậpđộclậpmới.

Verification:recomputeallmetrics/aggregates/quantiles,S và70PNGhash/dims,
replaygray/Gaussian/Canny/closing;7HTTPfull bằngcorePNG,84uniqueIDs,
source/manifest/annotation13ảnh nguyên,frozenSHAce89a90… giữ91source/config/deps/environment
trước/sau. Accuracy/full/comparisoninitial-final bằngbyte. Frontend103/build làmốc13.06,
khôngrerun source/UIunchanged. KhôngstartUIQAhoặcdùngDBusertrongbenchmark.

Docsresults/method/environment/dataset/algorithmnotes/auditphase13/AGENTS/plan/todo/README/contracts
cậpnhật. 13.07/08checked,94main+12AUX/110ID;checkpoint13C1/C2/cổng13đạt ởquymôMVP,
giaiđoạn12 giữchưa nghiệmthu toànbộ,next14.01chưa làm. Thiếunhàu mạnh/lóa/highlightthật,
mộttàiliệumỗisplit/nhãnmộtngười;khôngaccuracyOCR/dewarping hoặc100%mọitàiliệu.
Evidenceignoredmvp13-07-08-verified/finalprimary,testinitialinvalidRAM,verification/logs/review-sheet.
