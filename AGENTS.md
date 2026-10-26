# Document Scanner — Quy tắc làm việc

## Sử dụng skill

Theo yêu cầu của người dùng ngày 10/10/2026, trước mỗi tác vụ phải dùng
`agent-skills:using-agent-skills` để xác định workflow và các skill phù hợp.

- Đọc SKILL.md trước lần áp dụng đầu tiên; dùng nội dung đã đọc trong phiên nếu còn đầy đủ và chưa thay đổi.
- Chọn skill theo công việc thực tế; không chạy toàn bộ danh mục cho mọi task.
- Thông báo ngắn cho người dùng khi lần đầu áp dụng một skill trong cuộc trao đổi.
- Tuân thủ các bước và kiểm chứng phù hợp của skill; ưu tiên chỉ dẫn hệ thống, developer và yêu cầu trực tiếp của người dùng khi có xung đột.
- Không tự mở rộng phạm vi, thêm bước phê duyệt hoặc suy ra quyền gửi tin nhắn bên ngoài từ việc dùng skill.
- Nêu giả định quan trọng; hỏi khi thiếu thông tin ảnh hưởng quyết định hoặc có xung đột chưa được giải quyết. Tiếp tục phần độc lập đã được cho phép.

Skill thường dùng: planning-and-task-breakdown cho kế hoạch; incremental-implementation
cho triển khai; api-and-interface-design cho API; frontend-ui-engineering cho UI;
test-driven-development cho logic; debugging-and-error-recovery cho lỗi;
code-review-and-quality cho rà soát; context-engineering cho ngữ cảnh dự án.
Đây là ví dụ, vẫn cần chọn theo catalog skill hiện có.

## Phạm vi và kiến trúc đã chấp nhận

- Nguồn phạm vi MVP hiện hành: `docs/MVP_Pham_Vi_Va_Ke_Hoach_4_Tuan.md`.
- Kế hoạch triển khai: `tasks/plan.md`; checklist tiến độ duy nhất: `tasks/todo.md`.
  Đọc task, phụ thuộc và bằng chứng tiến độ trước khi làm bước tiếp theo; ID MVPxx.yy
  độc lập ID Pxx.yy của kế hoạch gốc. Không suy ra task đã xong từ việc tài liệu đã tồn tại.
- Người dùng bỏ MVP01.08 ngày 14/10/2026 và chuyển giai đoạn 02; không yêu cầu
  tạo mẫu nhật ký hoặc changes.md. Giữ trạng thái bỏ qua và ID gốc trong checklist.
- Hai tài liệu `Document_Scanner_Dac_Ta_Kien_Truc_Thuat_Toan.md` và
  `Document_Scanner_Ke_Hoach_Trien_Khai_Chi_Tiet.md` là tham chiếu gốc;
  áp dụng các điều chỉnh MVP đã được người dùng chấp nhận.
- Đề tài giữa kỳ khoảng một tháng, trọng số 20%; ưu tiên luồng dùng được,
  ảnh trung gian thật, thực nghiệm và khả năng giải thích thuật toán.
- Web cục bộ, đơn khối chia mô-đun: React/TypeScript/Vite; Python/FastAPI;
  OpenCV/NumPy/Pillow; SQLite/SQLAlchemy; ReportLab.
- MVP gồm quản lý nhiều trang, lưu/mở lại tài liệu và xuất ảnh/PDF.
- Lõi xử lý ảnh độc lập HTTP, DB và UI; giữ nguồn; preview lấy từ full render;
  kiểm tra góc, revision và thứ tự trang xuất.
- Hợp đồng dùng chung khi làm normalize/geometry/config/API/canvas/revision:
  `docs/image-contract.md`. Các preset/đơn vị và thứ tự góc trong tài liệu này
  là quy ước triển khai; chưa phải chức năng đã được hiện thực.
- Lõi nguồn hiện có `validate_image` (metadata trước EXIF), `normalize_image`
  (BGR uint8 sau EXIF) và `encode_normalized_png` (PNG sạch EXIF, width/height,
  SHA-256 của đúng png_bytes). Storage phải ghi chính payload đó; không áp
  quota 15 MiB của upload lên PNG chuẩn hóa nội bộ có thể lớn hơn JPEG nhập.
- `resize_to_max_edge` nhận gray/BGR uint8, thu nhỏ bằng INTER_AREA với
  half-up tính nguyên chính xác (tương đương floor(x + 0.5)), không upscale,
  trả mảng độc lập. Display cho phép cạnh 1 pixel;
  analysis phải chặn trước geometry nếu dimensions <2. CLI normalize_one.py
  dùng thumbnail mặc định 320, ghi source/thumbnail/metadata vào thư mục mới,
  không ghi đè; ảnh thật/kết quả thử giữ ngoài Git.
- Dữ liệu theo `docs/dataset.md` và `experiments/dataset_manifest.csv`;
  validator kiểm tra ID/split/path/hash, không chứng nhận danh tính/nhãn.
  Bộ chốt26/10 có development6ảnh/doc_01 và test7ảnh/doc_02,13ảnh/2tài liệu;
  user xác nhận các ảnh trong mỗi nhóm cùng tờ/nội dung;
  không dùng một tài liệu này để kết luận khả năng tổng quát. Các góc gắn với
  nguồn PNG sau EXIF/hash/dimensions, không thumbnail. Cổng giai đoạn 02 và
  AUX02.01 đã đạt; đọc `docs/audit-phase-02.md` trước khi nối geometry.
- Khi làm detector/debug/thực nghiệm, đọc mục 5.5.1–5.5.3 của
  `docs/Phan_Tich_Huong_Thuat_Toan_Tu_Tai_Lieu.md`: quy ước biểu diễn,
  mô tả biên, đặc trưng vùng, đơn vị và các task nghiệm thu tương ứng.
- Geometry hiện có `pixel_to_normalized`/`normalized_to_pixel` theo W−1/H−1,
  giữ subpixel, chặn tọa độ sai; `validate_quad_points` nhận bốn điểm normalized,
  trả pixel theo thứ tự nhập. Ngưỡng gần trùng ≤1e−6·D, cạnh ngắn ≤1e−3·D
  với D=hypot(W−1,H−1); đo Euclid trên pixel, không trực tiếp trên u/v.
  Đây là gate điểm/cạnh; đầy đủ topology dùng `validate_quad` (trả pixel,
  không reorder): shoelace/cross/giao cạnh đối, chặn near-collinear/diện tích
  ≤1e−6·D²/lõm/ngược winding. Tính topology bằng pixel chia cùng D hai trục.
  `order_auto_corners` chỉ cho auto proposal: atan2 quanh tâm điểm nguồn,
  winding dương, min(x+y), tie y/x trên pixel nguồn; trả normalized và validate.
  Không chạy cyclic edge gate trước khi sắp; không dùng sorter cho handle tay.
  `estimate_warp_size` trả (W,H) từ max cạnh đối/half-up/min2/cap2400/5.76MP;
  cạnh là span nên toàn source101×51 ước lượng100×50, không cộng1.
  `compute_homography` trả (H,(W,H)), H source→đích float64 finite/invertible;
  `warp_document` nhận BGR uint8 HWC3 sau EXIF≤16MP, giữ nguồn, INTER_LINEAR/
  BORDER_REPLICATE. Không filter/xoay/preview hoặc tự xác nhận góc ở lõi warp.
  Với source có cạnh≥32767, warp dùng ROI gốc dưới SHRT_MAX theo inverse map
  và H dịch hệ tọa độ, có halo bilinear; không resize source để né giới hạnCV.
  `geometry_demo.py` nhận input gốc/quad normalized manual, tạo source/overlay
  đánh số/warp/metadata trong thư mục mới; không detector/auto-confirm/revision.
  Giai đoạn03 và AUX03.01 đạt; đọc `docs/audit-phase-03.md` khi nối processing.
- MVP04.01 có `PageConfig`, `get_preset` và `parse_config` trong config.py.
  Snapshot/nested models frozen; defaults theo mode/trường con, extra/null/
  sai kiểu-miền bị từ chối, giữ tham số inactive và có dotted inactive_fields.
  Góc khác null phải truyền source_size thật sau EXIF để validate_quad; trước
  filter truyền warp_size thật để kiểm block Adaptive active vừa warp.
  Chỉnh full JSON rồi parse_config lại; model_copy(update=...) không validation.
  Config không đọc/sửa ảnh, không tự confirmed/revision.
- MVP04.02 có `apply_denoise(warped_bgr, config.denoise)` trong enhancement.py:
  BGRuint8 HWC3 fullwarp2..2400, outputđộc lập/cùngshape-dtype-kênh; Nonecopy,
  Median3/5 (replicate), Gaussian3/5 sigma0/reflect101. Revalidateconfig,
  khôngmutate nguồn; chỉlọc trướcmodeconversion, khônganalysis/preview/threshold.
  Chấm/nét1pixel đãcó tests vàảnh chứng minh Median xóa nét, Gaussian mềm nét.
- MVP04.03 có `render_color(filtered_bgr)` và `render_gray(filtered_bgr, config.contrast)`:
  dùng BGR sau apply_denoise; Color copy giữ màu, Gray BGR2GRAY HxW uint8,
  CLAHE tùy chọn clip_limit1..4/grid8x8 (số tile, không phải kích thước pixel).
  Revalidate ContrastConfig kể cả inactive; nguồn/config không đổi. Không threshold/
  xoay/dispatcher; Color không gọi CLAHE. Checkpoint04-C1 đạt với132tests tập trung
  và ảnh synthetic chữ tiếng Việt/highlight.
- MVP04.04–05 có `apply_otsu(gray)` trả `(bw, actual_threshold)` và
  `apply_adaptive_gaussian(gray, config.threshold)` trả BW. Input fullwarp HxW
  uint8 mỗi chiều2..2400; output độc lập cùngdimensions/chỉ0/255, THRESH_BINARY.
  Không thêm blur/CLAHE; nhận gray đã chuẩn bị. Adaptive revalidate ThresholdConfig,
  yêu cầu method=adaptive_gaussian, blocklẻ3..151≤cạnhngắn thật, C nguyên−20..30.
  Quáblock báo INVALID_CONFIG; khôngclamp/fallback. Otsu không đọc block/C, trả
  ngưỡng thực0..255 (ảnhconstant có thể0); Adaptive không có một ngưỡng global.
  171tests tập trung vàảnh synthetic sángđều/bóng/ảnhnhỏ đã kiểm chứng.
- MVP04.06 có `enhance_document(warped_bgr, config, source_size=None)` và
  EnhancementResult(image,effective_config,otsu_threshold). Parse toànconfig với
  warp_size thật trướcfilter; source_size sauEXIF bắt buộc nếu cornersnonnull.
  Lọc→mode/contrast/threshold→rotate90 chiều kimđồnghồ; giữsource/config/corners,
  trảactualOtsut/null. Nhậnwarp đãcó; khôngHTTP/DB/confirmed-revision gating.
- MVP04.07/AUX04.01 có `experiments/enhancement_demo.py`, algorithm-notes và
  audit-phase-04. CLI xuấtColor/Gray/BWAdaptive/BWOtsu cùngwarp, PNGfullRGB/L,
  comparison thu từfull, config/inactive/t/hash/dims; quadmanual/draft, thưmụcmới.
  193tests config/enhancement+7CLI đạt;12rotation outputs và5runs real/synthetic
  đãxem. Otsu làmđenbóng, Adaptive vẫngiữôly/đứtnét; preset chưatune hoặcaccuracy.
  Giaiđoạn04/cổng04/C2 đạt; đọc audit/algorithm-notes khi nối detection.
- Mốc baseline MVP05.01–02 có `prepare_analysis(source_bgr)` và `create_edge_trials(blurred)`
  trong detection.py. Nguồn BGR sau EXIF≤16MP → maxedge1200 không upscale,
  INTER_AREA/half-up → gray → Gaussian5/sigma0/reflect101. AnalysisImages giữ
  source_size và analysis_size thực, stages độc lập; to_source dùng geometry
  W−1/H−1, không chỉ chia tỉ lệ r. Cạnh analysis<2 báo ANALYSIS_TOO_SMALL.
  EdgeTrial giữ ID/thresholds/edges raw/closed riêng: đúng3pairs50/150,75/200,
  100/250, aperture3/L2true, closingrect3×3/1lần/borderconstant trung tínhCV.
  Không dùng closed làm edge_support hoặc lấy derivatives làm nguồn render.
  33tests +4runs real/synthetic đã kiểm tại mốc05.02; contour/scoring nối bên dưới.
- MVP05.03 có `generate_candidates(analysis,trial)` trong detection.py:
  RETR_LIST/CHAIN_APPROX_SIMPLE, top30 contour/trial, Douglas–Peucker với
  epsilon/P=.015/.02/.03. CandidateBatch giữ contour/Q gốc, số đỉnh và reason
  cả lần nhận/loại. Area contour/quad≥10%WaHa, cạnh≥5%min(Wa,Ha); validate_quad
  kiểm cycle trước auto sorter, không sửa tự giao/lõm hoặc ép góc vuông.
  Canonical start dùng pixel nguồn thật; corners normalized theo W−1/H−1.
- MVP05.04 có `describe_candidate(candidate,trial)` và CandidateDescription:
  chu vi/cạnh px analysis, góc đổi hướng rad, geometry flags, a/e/f/b/score;
  candidate giữ trial/source/analysis dimensions. n=max(2,ceil(L/2)+1), lấy cả
  hai đầu cạnh, khoảng mẫu≤2px; hỗ trợ raw Canny cùng trial theo Euclid≤2px.
  b dùng cùng mẫu, cách mép≤2px; giữ counts/tỷ lệ từng cạnh. e=sum(m)/sum(n),
  S=clip(.45a+.35e+.20f−.15b,0,1); không lấy mean4 hoặc closed làm bằng chứng.
  64tests detection,10cases/30trials +controlled map đã kiểm; img_003 cóquad
  S≈.502372, img_004 khôngquad, frame lớn có thể thắng giấy. Không accuracy.
  Tại mốc05.04 chỉ đạt checkpoint05-C1; đọc phần05.05–06 dưới đây cho entry
  hiện hành, algorithm-notes/progress trước nối debug/API/UI.
- AUX05.01 là điều chỉnh được user chấp nhận15/10/2026; đọc
  `docs/detection-revision-01.md` trước khi làm tiếp detection/NMS/debug.
  Entry hiện hành `collect_candidates(analysis,preset='revised')` trả tuple
  TrialCandidates(trial,batch):3Canny20/60,50/150,75/200; nếu cả3khôngquad,
  thêm tối đa1RegionTrial Otsu. GiữGaussian5/sigma0/reflect101; kernel3 chỉ
  ablation explicit, AnalysisImages/EdgeTrial/Candidate giữ gaussian_kernel.
  Baseline vẫn50/150,75/200,100/250 và khôngregion; create_edge_trials gọi
  trực tiếp vẫndefaultbaseline để tái hiện. Kernel3 dùng IDcanny_g3_low_high.
  Region lấymask THRESH_BINARY|OTSU từanalysis.blurred, RETR_EXTERNAL lấy
  biên ngoài thànhphầntrắng/bỏbiênlỗ mà khôngfill/thêmclosing. Masktoàn0/255
  trảbatch rejection_reason=UNIFORM_REGION_MASK vàkhôngcontour, giữmaskthật.
  RegionTrial giữ actual otsu_threshold/support_trial_id/thresholds/kernel;
  thresholds là cặp Canny support20/60, edges copy từ raw của cùnganalysis.
  Candidate thêm method/kernel/otsu_threshold; describe revalidate với trial.
  Không dùng mask/boundary mask/closed làm e; gate10%/5%/geometry/score giữ.
  `experiments/compare_detection.py` so một ảnh baseline/revised, thư mục mới,
  source PNG đúngpayload/hash, stages/metadata thật; không tựconfirm/warp.
  30revision+5CLItests mới, toànbackend670đạt.16ca thực: anhtestnew cóquad
  S≈.634709; img_004/img_006 region ăn bàn S≈.468352/.448517, img_001 chưaquad;
  frame vẫnscorecao sai. Dataset6ảnh/1doc/test0 khôngđổi, newimage chưaidentity.
  Tại mốcAUX05.01:34main+4AUX; không gọi candidatecount hoặcscore làaccuracy.
- MVP05.05–06 đã có polygon_metrics.polygon_iou và detection.
  deduplicate_candidates/select_proposal/detect_document. IoU liên tục trên
  quad normalized cùng ảnh/dimensions, validate trước CV intersectConvexConvex
  handleNested=true; quad giống nhau/khác start trả1 chính xác, giao khác
  dùng float32. NMS greedy theo score giảm dần, tie input order; chỉ loại
  IoU>.95 với survivor, không trộn raw support. Caller giữ cùng nguồn/run,
  dimensions không chứng nhận danh tính nguồn. Candidate thêm support_trial_id
  của region; Canny null vì raw origin=trial_id; describe kiểm provenance.
  detect_document(source_bgr) chạy Gaussian5/revised→describe→NMS→proposal.
  DetectionResult frozen: status proposed khiS≥.60, proposed_with_warning
  khi.40≤S<.60, manual_required khiS<.40/khôngquad. Manual corners=null;
  score=null chỉ khi khôngquad. selected low-score chỉ chẩn đoán, không được
  lấy corners của nó thay result.corners. candidates là NMS survivors;
  confirmed luônfalse. Không giả inset/fullquad, warp hoặc đổi config.
  18metrics+28selection mới,140focused/716backend đạt;7runs đã xem ở
  experiments/results/mvp05-05-06-verified/. img_004 cảnh báoS.468352 nhưng
  vẫn ăn bàn; anhtestnew đề xuấtS.634709; img_001 manual. Khung giả vẫn có
  thể điểm cao/chọn sai; score/status khôngaccuracy. Chưa thêm gate từng
  cạnh/epsilon hoặc sửa phân vùng. Tại mốc05.06:36main+4AUX,05-C1/C2 đạt;
  đọc phần05.07–08 bên dưới cho trạng thái hiện hành.
- MVP05.07–08/AUX05.02 đạt: đọc docs/audit-phase-05.md trước nối pipeline.
  detect_document(source_bgr,debug=False,preset='revised') trả timings_ms thật;
  baseline explicit để đối chứng. DetectionTimings dùng perf_counter_ns với
  preprocess/candidates/describe/select/debug/total; candidates gộp Canny,
  closing/contours/region, select gồmNMS, không gồmdecode/encode/I/O.
  Debug opt-in giữanalysis/trials thật/selected_trial/overlay analysis vàkind
  proposal/diagnostic/none; khôngquad khôngvẽgiả, bestlow chỉdiagnostic.
  source_bgr_sha256 là hash BGR C-order, kháchashPNG; CLI gắn cảraw/PNGhash.
  Mặc định không giữstagearrays; dataclassfrozen khônglàmndarray bấtbiến.
  Service sau phải táchảnhkhỏiJSON, không asdict toàndebugndarray đểgửiAPI.
  detect_batch.py chỉ đọc development, so baseline/revised, ảnh --input thêm
  giữsplitunassigned; hash/EXIF/sourcePNG đúngpayload, thưmụcmới/khôngđè,
  error.json/CSV/summary/exit1 khi cólỗi vàtiếptục ảnhkhác. CLI khôngwarp.
  10debug+7batchCLI mới,733backend đạt47.01s.16ca/32runs/104trial/368PNG,
  xemđủ16comparison/QA replaystages và19survivors. img_001 manualdraft từ
  agent quaCLI cósẵn tạo951×1284warp/4mode/8PNG, khôngGT/userconfirmed/UI.
  docs/audit-phase-05.md nêu debt task03–04: thử capepsilon/fitdistance,
  cảnhbáocạnhyếu; khunggiả e=1/fitnhỏ nên cácgateđó khôngchữađược,
  cần đối chứng cảnhmơhồ/phânbiệtgiấy-nền vàthêmnhiềutàiliệudevelopment.
  Chưa đổi ngưỡng/phânvùng/score theođềxuất.38main+5AUX,cổng05 đạt ởmứcMVP;
  giữcasai côngkhai, khôngaccuracy. Đây là mốc05.08; đọc phần06 bên dưới.
- Mốc MVP06.01–03 đạt, checkpoint06-C1 đạt; cập nhật06.04 ở dưới.
  render.py có render_document(source_bgr,config,debug=False): parse config,
  giữ corners manual/skipdetect hoặc dùng result.corners của detector revised,
  không dùng selected diagnostic đểwarp. Noquad trảmanual_required, warp/
  enhancement/H=null. Chỉ ANALYSIS_TOO_SMALL được chuyển sang manual vớiwarning;
  lỗi input/CV khác vẫn báo lỗi. Manual vẫn phải qua geometry gate; nguồn
  40000×42 dùng tay được dùanalysis cao1, không nới gate cho40000×2.
  Warp từfullsource, enhancement/rotate rồiencode; khôngHTTP/DB/I/O ởlõi.
  RenderTimings validate/detect/warp/enhance/total, khôngnormalize/encode/I/O;
  detector timing đãnằmtrong detect, khôngcộnglặp. Khôngtựconfirmed/revision:
  auto vẫnfalse, manualconfig tườngminh giữstate; CLIđổicorners→draftfalse.
  encode_render_images nhậngray/BGRuint8 full2..2400, PNGfreshRGB/L/hashpayload;
  preview max1000/INTER_AREA/half-up/khôngupscale từfullsaurotation. PreviewBW
  đượcgray, cócạnh1; khôngthresholdlại. encode_stage_png cho stage/preview,
  source vẫnghi đúngencode_normalized_png payload, khôngquota15MiB nội bộ.
  EnhancementResult.stages optional: actualfiltered_bgr/prepared_gray/
  before_rotation từdispatcher mộtlần; Color prepared_gray=null. preparedgray
  củaBW làinputthreshold thật, khôngdùng detectionblur; histogram bổ sung ở06.04.
  scan_one.py normalize→pipeline→encode→source/config/metadata/detection/render;
  --mode hoặc--config, --corners ghiđèvàdraft. Outputmới, metadata cuối:
  exit0rendered/exit2manual_required/exit1error; rendered khônguserconfirmation.
  JSONsnapshot cóhashraw/PNG/BGR/dims/H/config/inactive/t/timing/version;
  configcógócđiđườngmanualkhitáichạy, khôngrerundetect. Sharedwriter
  experiments/detection_artifacts.py dùngactualresult cho scan/batch, entrypoint
  vàrun_id tườngminh; khôngtrộn stage detection/render hoặcJSONhóandarray.
  30render+6stages+8CLI mới,777backend đạt38.83s;7runs/92PNG/4detect/14trial,
  6render+1manual_required, source/fixturesgiữhash. ManualGray img_001 giữ
  hashoutput05; img_004vẫnănbàn/BWđenbàn, khôngsửa thuậttoán.41main+5AUX,
  giữ110ID,03a/b khôngcộng taskcha. Next06.04;06.05/06.06 vẫnchờ,chưascanUI.
- MVP06.04 đạt16/10/2026: histogram.py/compute_histogram nhận full gray uint8
  HxW2..2400, cv2.calcHist256bin/[0,256), trả tuple256int count, sum=W*H.
  Không mask/resize/probability, không mutate; INVALID_HISTOGRAM_INPUT hoặc
  HISTOGRAM_FAILED rõ. Giới hạn5.76MP giữ float32count chính xác (<2**24).
  EnhancementResult.histogram có counts BW sau denoise/CLAHE, trước threshold/
  rotation, kể cả debug=false; Color/Gray=null, manual_required khôngenhancement.
  Không chạy lại filter/threshold để tạo dữ liệu; Otsut vẫnactual của lượt render.
  scan_one metadata.histogram có counts/size/pixel_count/source_artifact=prepared_gray/
  source_png_sha256/threshold_method/threshold_scope/otsu_threshold; Otsu global/t,
  Adaptive local/t=null, khôngphải bảnđồngưỡng hoặc globalt. PageConfig khôngđổi,
  scan-v1 giữ vì chỉ thêm diagnostic, ảnh/config/pixels khôngđổi. Thời gian nằm
  trongenhance/total; service sau tácharray vàJSON theo hợpđồng11.2.
  16histogram/dispatcher+1CLI mới,794backend đạt95.24s; focused25 đạt23.56s.
  experiments/results/mvp06-04-histogram/ có2run thật img_004/cùngpreparedgray:
  1112x1358/sum1,510,096/213bin khác0; Otsu140/global, Adaptive local/null.
  Adaptive replayconfig corners bỏdetect, không tạo lạiwarningdetect; cảhai draft.
  Hash Otsufull/preview/stages khớpmốc03, vẫnănbàn; nguồn/22fixtures nguyên.
  42main+5AUX/110ID; next06.05,06.06/M1 vàUIhistogram vẫnchờ. Khôngsửa detector.
- MVP06.05–06/AUX06.01 đạt16/10/2026: giai đoạn06/M1 hoàn thành. Đọc
  docs/milestone-m1.md và docs/audit-phase-06.md trước nối API/UI.
  Thêm4core repeat/serialized snapshot và2CLI auto/manual_required repeat;
  focused45đạt30.73s, toànbackend800đạt99.97s. Không đổi core/preset/dependency.
  Runtime10ca×2tiến trình cùng rawsource/requestedconfig/scan-v1 trong cùng
  môi trường:20runs/230PNG,18render/2manual_required,8detect/28trials.
  So toàn metadata root/detection trừ run_id/timings_ms, kiểmPNG/hash/config/
  H/stages/histogram/threshold/rotation/preview từsource. Giữ6cặpmanifest và
  22fixtures; verification.json ở experiments/results/mvp06-m1-verified/ lưu
  hash code/requirements/source, environment. Khônghứa tấtđịnh trên máy khác.
  Configđầuvào cornersnull lặpauto; outputconfigcógóc điđườngmanual, không
  đòi debugdetect giốngauto. M1doc có smokePowerShell6CLI khôngcầnảnhriêng,
  đãchạy3mode EXIF/replayBW/blankmanual_required→retrytay vàkiểmhash.
  Đãxem goodoverlay/Color tay/Graybóng/Otsuănbàn/Adaptive90nhiễu; khôngGT/
  accuracy, khôngcoi repeatability làchọnđúnggiấy. Nợ05 giữnguyên,img004ănbàn.
  44main+6AUX/110IDgốc; next07.01schemaAPI. ChưaUI/confirmed-revision/lưubền/
  nhiềutrang/PDF/histogramUI. Cácphần06.01–04 phía trên làlịch sử từngmốc.
- MVP07.01–02 đạt17/10/2026: docs/api-contract.md và schemas/common/pages/
  sessions/errors có UUIDv4/UTC/error/session/page/config/artifact/detect/render/
  order/export request. APIModel extra forbid; ConfigUpdateRequest chỉparse
  envelope rồiBẮTBUỘC validate_config(source_size thật,warp_size khi cần) trước
  persist. Dùng parse_config, không merge config cũ hoặc giả dimensions. PageRead
  validate PageConfig theo width/height thật bằngwrapvalidator, serialization
  khôngwarning; ConfigRead cócorners cầncontext source_size. Revisionmới=0 theo
  task07.05; đãsửa image-contract cũghi1. Chưa CAS/errorhandler/endpointmới.
  storage/database.py open_database(path) tạoenginefile, initialize_database
  khởi tạoDBtrống/schema_version1 hoặcchấpnhận đúng6bảng/version, khôngrepair/
  migrate unknown. FK bật mỗi connection, SQLAlchemy explicitBEGIN choDDL/
  SELECTrollback; UTCDateTime lưuISOtext/trảawareUTC. KhôngimportAPI/processing
  vào storage,khôngI/Oảnh vàkhôngsideeffecttạoDB lúcimport.
  models cósessions/pages/page_configs/artifacts/exports/schema_version.
  CompositeFK buộcconfig/artifact/session/page vàsourcepointer đúngpage;
  page↔source dùngdeferredFK, cấpUUIDtrước/commit cùngtransaction. Active source
  khôngxóariêngđược; sessioncascade chỉmetadata, chưa xóatệp. JSONconfig snapshot
  đầyđủ+revision; rawORM chỉgatecơbản, servicephảivalidateconfig/MIME/hash/tệp/
  role/snapshot/quota/CAS. Repository chỉunitofwork/create_session/truyvấn owner,
  titleđượcvalidatetạiboundary; khôngtựcommit/query hoặcchạyOpenCV.
  21schema+19storage tests mới,focused40 đạt1.62s/finalbackend840 đạt106.98s.
  Runtime2process write/reopen metadatafixture ở experiments/results/
  mvp07-01-02-verified/:6tables/version1/FKcheckrỗng/UTC/revision0/ownerblock;
  5JSONvídụđúng/13schemas sinhđược. Thamchiếuảnhfixture chưađượcghi, khônglà
  kiểmchứnglưuảnhthật. Khôngđổi processing/HTTPmain/frontend/dependencies.
  46main+6AUX/110ID;07.01a/b khôngcộngparent. Next07.03 filetemp→rename;
  checkpoint07-C1 chờ03,khôngtích07.04–09/UI/import từschema/DBmetadata.

- MVP07.03–04 đạt17/10/2026, supersede trạng thái chỉ-health/next07.03 ở mốc trước.
  ArtifactStore trong storage/files.py nhận immutable encoded bytes, không filename/path;
  UUIDv4/kind/MIME/owner/revision/dimensions kiểm trước ghi; temp cùng thư mục,
  flush/fsync/close rồi publish không ghi đè (Windows rename, POSIX hardlink).
  Giữ đúng PNG payload/hash từ encoder; không quota15MiB cho PNG nội bộ.
  path_for recompute UUID path, guard root/symlink/junction/reparse; trusted local
  root, không chống tiến trình OS thay directory đồng thời. register_artifact
  verify regular file/bytes/hash trước flush metadata, caller commit. Sau rollback
  discard_unreferenced chỉ dùng descriptor file MỚI của thao tác lỗi, queryID/path
  trước verify/unlink; không xóa file active/recursive. Crash giữa file/DB có thể
  để orphan; chưa GC hoặc chứng nhận mất điện. Không coi rawORM là import use case.
  create_app(database_path) lifespan khởi tạo DB/store rồi dispose; default
  data/scanner.sqlite3, không tạo DB lúc import. HTTP sync routes POST /sessions,
  GET /sessions, GET /sessions/{sid} đã nối SQLite; health giữ liveness. List
  updated_at DESC/id ASC +count cùng transaction; detail pages position/owner/
  config source dimensions thật, missing config fail. render_revision lấy max
  metadata full-render, chưa chứng nhận export. ErrorEnvelope body/query400,
  sid sai/thiếu404, DB/metadata500 STORAGE_FAILED, generic500 INTERNAL_ERROR;
  HTTP405 giữ Allow, không lộ input/SQL/path/trace; OpenAPI đúng3paths/no422 giả.
  19artifact+18API mới; focused78 đạt3.64s (-W error), full877 đạt105.79s.
  Runtime experiments/results/mvp07-03-04-verified/: localhost Uvicorn create/
  list/detail/rỗng/order/membership/errors, restart2tiếntrình cùngDB/9file fixture
  EXIF6 giữ byte/hash; fault rename/commit/cleanup active được kiểm. Trang seed
  lowerlayer, KHÔNG là import07.05/upload07.07. Checkpoint07-C1 đạt;48main+6AUX,
  07.04a/b không cộng parent. Next07.05; UI/worker/upload/CAS/PDF còn chờ.
  Không đổi processing/frontend/schemaVersion1/dependencies hoặc nợ detector05.

- MVP07.05–06 đạt17/10/2026, cập nhật mốc07.03–04 ở trên. imports.import_page
  là use case blocking, nhận UUIDsession/immutable bytes, không filename/config/
  góc hoặc auto-confirm. Kiểm session/quota trướcCPU; validate JPEG/PNG15MiB/
  16MP rồi normalizeEXIF/alpha/BGR, encode_normalized_png đúngpayload và
  encode_stage_png cho thumbnail320 (display side1 được phép) trước ghi3file.
  Original giữ bytes/MIME thực/dimensions trướcEXIF; source/thumbnail theo raster.
  Finaltransaction UPDATEsession lấy SQLite writerlock trước count/maxposition,
  kiểm lại session/quota20, append max+1 và commit page/3artifact/configrevision0/
  confirmedfalse/cornersnull; updated_at session thay đổi. CPU/encode ngoàiDB.
  DTO validate trướccommit, chỉ trả saucommit. Lỗi dọn descriptor mới unreferenced
  saurollback; nếu cleanup lỗi thì serverlog/giữ lỗi gốc, không xóa mù/activefile.
  KhôngGC saucrash hoặc transaction chungfile+DB.14importtests, có lastslotrace
  haiimport ngoàiexecutor vàsessiondeletedmidimport, giữ20page/60file/khôngorphan.
  ProcessingExecutor tạo mộtinstance app.state.processing tronglifespan, dùng
  asyncio Future/deque bounded2waiting vàThreadPoolExecutor1worker. submit/run
  từeventloopapp, FIFO; queuedcancel trảslot trướcnextsubmit/khôngchạy, active
  caller cancel giữslot chođếnthreadxong; thườngexception chuyểncaller/worker
  tiếp tục. Khôngsubmitđệquy hoặc tựtạopool cho từngroute. aclose từchốimới/
  cancelqueued/đợiactive/jointhread trướcdisposeDB. Handler429 PROCESSING_BUSY
  đãcó; 5tests kiểmquota/cancel/FIFO/error/shutdown/health. MộtUvicornprocess;
  onejob khôngđồngnghĩa mộtthreadnộibộOpenCV; khôngjobID/polling/hardkillthread.
  Runtime mvp07-05-06-verified/: privateprobe gọi usecase thật qua worker,2trang
  EXIF6/alpha→6file, lỗicommitcleanup/workerrecovery/429/cancel/health14.19ms
  lượtđo/restart2process/shutdownjoin. Probe khônglàAPIupload sảnphẩm.
  Focused97passed6.12s -W error, final896passed108.88s.50main+6AUX/110ID;
  checkpoint07-C2đạt, next07.07upload/artifactGET.07.08–09/UI/CAS/PDF cònchờ;
  processing/frontend/dependencies/schemaVersion1/nợdetector giữnguyên.

- MVP07.07–09/AUX07.01 đạt17/10/2026; docs/audit-phase-07.md rà đủ9task.
  API pages POST /sessions/{sid}/pages nhận đúng1multipartfile/0textfield,
  caprequeststream15MiB+64KiB envelope vàđếmfile64KiB/chunk15MiB, khôngtin
  Content-Length/clientMIME/filename. Starletteparser on_end kiểmcomplete;
  thiếuend phải raise bêntrong guardedparse loop đểđóng cảspoolfile chưa vào
  FormData. finally form.close; bytes vào app.state.processing.run(import_page).
  Lỗiảnh400corecode, unsupported/multiframe415UNSUPPORTED_IMAGE; byte/pixel/
  pagequota413, workerđầy429. Không đưa quota15MiB vào PNGnguồn nội bộ.
  GET /artifacts/{aid} lookup/join session/pageowner, đóngDBtransaction trước
  pathguard/regularfile/size/hashverify vàFileResponse. MIME metadata thực,
  inlineUUIDfilename/nosniff/private-no-store; thiếuID404, badblob500STORAGE_FAILED.
  Khôngpublicdata/pathquery; app localhost khôngaccount/multiuserauthorization.
  OpenAPI5path/6method thực, multipartbinary vàartifactbinary, không422 giả.
  Frontend client/types/ScannerPage/UploadPanel/PageList/SourcePreview/App/styles:
  nativefetch, Quad4điểm/enums, create/list/detail, uploadtuầntự/kếtquảtừngfile,
  thumbnails +fullsourcePNG đúngEXIF. URL giữsession/page, DBgiữnội dung; GETcũ
  abort khiđổidoc, POSTkhôngretry. Refreshmetadata khôngunmountUploadPanel,
  bấmlạidoc đangmở khôngresetpage. Kếtquảbatch khôngpersist quabrowserrefresh.
  Browserfilechooser EXIF6→fakeJPG→alphaPNG:2page/6file, lỗiởgiữa khôngmấttrang;
  refresh vàshutdownbackendv1/startv2 cùngdata +Tảilại giữname/order/config0/IDs/
  bytehash. Runtime mvp07-07-09-verified/ cósnapshot/verification/browserproof/
  4viewport/screenshots. img_004 thêmquaAPI sảnphẩm/xemnguồn1536×2048, hash
  sourcePNG khớpmanifest; khôngdetector/warp/render.320/768/1024/1440 khôngoverflow,
  keyboardfocus/label/consolecuốiđãkiểm; khôngclaimWCAGcertificate.
  20importAPItests mới (cóspoolleak RED→GREEN/15MiBexact/chunked/quota20/rollback/
  prod429). Full916passed125.89s; frontendtypecheck/buildđạt.53main+7AUX/110ID;
  07.07a/b và07.08a/b khôngcộngparent. Cổng07đạt, next08.01 fullconfig/góc/
  confirmed/revisionCAS. ChưaM2renderUI/detectUI/PDF; giữcore/dependencies/
  schemaVersion1/dataset6ảnh1doc/test0/nợdetector05. Dev8000/5173 đangchạylocal;
  helperstop `.tmp/phase07-backend-v2.stop` đóngbackend hiện tại gracefully.

- MVP08.01–02 đạt17/10/2026: supersede next08.01 ở lịch sử07. Có PUT
  /sessions/{sid}/pages/{pid}/config và render_page service; chưa renderHTTP/UI.
  Đọc docs/api-contract.md mục Config và render snapshot trước nối08.03.
  Full replacement/defaults/source_size thật/estimate_warp_size thật cho block
  Adaptive; no-op giữ revision và timestamps, thay bất cứ inactive field cũng
  tăng1 khi commit. Lấy SQLite writer lock bằng repository.lock_session trước
  read/CAS; hai cập nhật cùng revision chỉ1success/1conflict. Stale409 kể cả
  no-op; details expected_revision/actual_revision. Góc thiếu confirmed=false,
  true phải gửi rõ; không kế thừa xác nhận cũ hoặc tựsort góc tay.
  render_page(engine,store,sid,pid,expected_revision) blocking: snapshot
  frozen config/StoredArtifact/dimensions, gate confirmed/revision trước core.
  _load_source verify hash/role/size/RGB/singleframe/noEXIF/≤16MP; không gọi
  upload normalize_image trên PNG nội bộ>15MiB, không EXIF lần nữa. CPU/encode
  ngoài DB; final writer lock→owner/revision/snapshot gate→write encoded full/
  preview/register/commit. Stale/deleted không publish; lỗi rollback/dọn đúng
  file mới qua discard_unreferenced, giữ oldartifact/source/config; crash vẫn
  có orphan/chưaGC. Preview từ final full; core manual, không detector bypass.
  Render không tăng revision/timestamps; render_revision cũ giữ để nhận stale.
  Service PageNotConfirmedError/RenderProcessingError mapping HTTP còn08.03;
  chưa debug/histogram persistence09. Timings core.* +source_load/encode,
  core.total chỉ lõi, không tổng end-to-end. 25configAPI+21service mới;
  focused64 -Werror, backend962; schemaVersion1/core/dependencies/frontend giữ.
  Runtime mvp08-01-02-verified/ riêng: WrongEXIF480×640/full-framequad/rotation90
  →639×479, config revision2/render_revision1 giữ sau restart; không GT/detect.
  Dev backend đã reload,4session metadata nguyên; stopfile hiện tại
  `.tmp/phase08-backend.stop`, launcher88956. UI vẫn nhập/xem nguồn, task08.03
  kế tiếp, checkpoint08-C1/M2 chờ. 55main+7AUX/110ID,08.01a/b không cộngparent.

- MVP08.03–04 đạt17/10/2026, supersede next08.03/mapping HTTP còn chờ ở lịch sử trên.
  POST /sessions/{sid}/pages/{pid}/render nhận RenderRequest và gửi toàn bộ
  render_page vào app.state.processing cùng import, không tạo worker riêng.
  RenderRead giữ page/revision/full-preview IDs/dimensions sau rotation/timings;
  confirmed/revision/snapshot/cleanup gates ở service giữ nguyên. HTTP draft409
  PAGE_NOT_CONFIRMED, stale409 REVISION_CONFLICT(expected/actual), owner404,
  body400, queue429, core RenderProcessingError500 PROCESSING_FAILED sanitized;
  file/DB vẫn500 STORAGE_FAILED. debug=true hiện render bình thường +warning
  DEBUG_NOT_AVAILABLE, không bậtcoredebug hoặc dựngrefs; persistdebug09.05.
  21HTTP mới/focused90-Werror/full983passed139.55s; runtime API sản phẩm riêng
  upload→config→render→GET output/restart giữ metadata/hash. Checkpoint08-C1 đạt.
  frontend/components/cornerGeometry.ts có createContainTransform/source↔canvas↔
  normalized/clientToCanvas/getCanvasBackingSize. Contain dùngW/H, tọa độ dùng
  W−1/H−1; subpixel/source thật sauEXIF, CSSrectratios, không DPR vào pointer.
  Backing round(CSS×DPR)/min1, ctx.setTransform bằng actualbacking/CSS ratios
  sau mỗi resize, không scale tích lũy; contentbox không border/padding.
  Helpers đổi tọa độ liên tục, có thể ra normalized ngoài01; KHÔNG clamp/hittest/
  sort/validatequad, các gate đó thuộc editor08.05–06/backend. Invalid finite/
  dimensions/DPR némRangeError; collapsedCSS bỏ ở caller. Transform frozen.
  27native Node24 tests trong cornerGeometry.test.mjs, npm.cmd test; không
  @types/node/Vitest/dependency mới. Node24.15.0 đã kiểm cho nativeTS runner,
  không suy từ appengine range rằng Node20 chạy được npmtest trực tiếp.
  typecheck/build đạt,21modules/bundlehash giữ vì editor chưa consume helper.
  Browser probe compiled actualmodule:8tổhợp dọc/ngang×CSSsize×backingDPR1/2,
  22draw/5điểm, maxCSSerror5.684e−14<1/handlepixels đúng/consoletrống. DeviceDPR
  thực1, DPR1/2 là backing ép thử; không claim2thiếtbị thật. Evidence JSON/PNG
  ở experiments/results/mvp08-03-04-verified/; probe5184/tab đã đóng saukiểm.
  Dev8000 đã reload (4session metadata nguyên), launcher69104/stopfile
  `.tmp/phase08-api-backend.stop`; Vite5173 giữ. UI vẫn nhập/xem nguồn;
  next08.05 overlay/handles, chưa CornerEditor/renderbutton/M2/debug/PDF.
  57main+7AUX/110ID, schemaVersion1/core/CLI/dependencies/dataset/nợdetector giữ.

- MVP08.05–06 đạt17/10/2026: CornerEditor đã nối SourcePreview/styles; đọc
  docs/image-contract.md mục Editor và quad nháp trước nối08.07. img normalized
  native/object-fit contain +canvasmaskevenodd/stroke;4button44CSSpx ID0–3,
  không dùng thumbnail/đổi pixel/encode source. Init persisted corners hoặc
  inset5%, structuredClone; remount theo page/revision/sourceID. ResizeObserver
  contentbox/DPRmatchMedia/resize, ctx.setTransform actualbacking/CSS mỗi draw.
  Localcorners/dirty/drag snapshot hiện ở component; chưa PUT/confirmed/render.
  Pointer Events primary/button0/capture/offset điểm nắm; chỉpointerId active,
  moveCorner clampnormalized01/giữID, khôngsort. Hittest22CSSpx/nearest/tielowerID;
  blankletterbox không nhảy handle. Pointerup final/release; cancel/lostcapture/
  Escape/windowblur/focusout/resize/DPR phục hồi before corners+dirty. Dragref
  null trướcrelease nên lostcapture sauup khôngundo. Tiny delta≤1e−6CSSpx trước
  khi thật sựmove bỏqua, tránh click không kéo bịdirty doULP. Arrow1CSSpx,
  ShiftArrow10, Escapehủy. Không chỉcolor: role=status/message/quadcode rõ.
  validateDraftQuad preflight mirrorcore: pixelW−1/H−1/D, pair/cạnh/collinear/
  intersection/area/convex/winding theođúng thứtự; khôngdetector10% hoặc UVlength.
  Backend vẫnvalidate lầncuối khi08.07 save. Invaliddraft đượcgiữđểsửa, không
  persist hoặc auto-confirm. Task08.07 sẽ nối draft/persisted/fullconfig/CAS;
  không suy từ góc hợp lệ thành confirmed/rendered.
  51frontendtests/936quadparity(6sizes)/216coregeometry-Werror/typecheck/build
  đạt; backend không đổi, full983 là mốc08.03–04. Browsermouse/clamp/bowtie/
  keyboard/6responsivecases đạt, maxhandlealignment≈.021CSSpx. ForcedDPR1/2
  mask alpha140ngoài/0trong vànormalizedgóc nguyên. Touchsynthetic qua component
  thật/capture bằng activepointer thật kiểmmove/cancel/lost/Escape/blur/secondary;
  chưa physicaltouch/HiDPI. Sửa grid mobile minmax(0,1fr) để3page khôngtràn320px.
  Metadata4session/7page/21sourcehash trước/sau nguyên; evidence tại
  experiments/results/mvp08-05-06-verified/. Temporaryharness đãarchiveignored/
  xóa khỏifrontendroot; không testhooks hoặcdependency mới trong sản phẩm.
  Checkpoint08-C2 đạt;59main+7AUX/110ID, next08.07; chưa save-confirm/renderUI/M2.
  Dev8000/5173 giữ; stopfilebackend .tmp/phase08-api-backend.stop/launcher69104.

- MVP08.07–08 đạt17/10/2026: fullconfig draft/persisted trong
  frontend/src/hooks/pageRenderState.ts, hookusePageRender/useSyncExternalStore;
  SourcePreview nối controls và preview thật. CornerEditor controlled, sửa góc
  bỏ confirmed; cancel phục hồi full snapshot trước kéo (kể cả confirmed).
  Fullimage là draft; reset lấy config đã lưu; save-draft explicit false,
  confirm explicit true. PUTfullconfig/CAS rồi POST đúng revision trả về;
  configresponse phải đúng page/rev/payload, render đúng page/rev, operation/edit
  generation chặn response sau đổi trang/unmount/sửa góc. Edit trong PUT giữ
  draft mới và không POST tiếp; edit trong render bỏ kết quả muộn. Lỗi giữ
  oldpreview có nhãn, chặn mutation tới GET “Đọc lại cấu hình”; giữ góc draft
  nhưng bỏ confirmed. Không tự retry mutation hoặc giả abort là rollback.
  Mở lại page GET detail mới; đổi trang/refresh bỏ nháp chưa lưu có nhắc.
  GETdetail chưa có renderUUID nên mở lại phải render explicit để xem preview,
  không thêm history/cache API. Preview có loading/error/retry và nhãn fullsize.
  64frontendtests (51cũ+12state/race+1wire),67backend config/render -Werror,
  typecheck/build/browser API thật/held responses/unknown commit đạt; backend
  không đổi/full983 giữ03–04.5session cũ/21sourcehash nguyên; evidence ignored
  experiments/results/mvp08-07-08-verified/. Đọc progress/API/image-contract.
  61main+7AUX/110ID; next08.09 so sánh/phóng to,08.10 nghiệm thu;
  checkpoint08-C3/cổng08/M2 vẫn chờ09–10. Không đổi detector/thuật toán/dataset.

- MVP08.09–10/AUX08.01 đạt17/10/2026, cổng08/M2/checkpoint08-C3 đạt.
  Đọc docs/audit-phase-08.md và frontend/tests/scanner-smoke.md trước nối09.
  ComparisonView dùng normalizedsource/render_artifact_id fullPNG, kiểmnatural
  dimensions/loading/error/retry; fit/100%/200% nativeimg+scroll, không dùng
  preview đểzoom hoặc xửlý lạiảnh.100%=1pixelảnh/1CSSpx,200%gấpđôiCSS,
  không nhânDPR; nguồn giữfit. Returnedit focushandle0; dirty vẫn oldfullUUID
  nhưngstale/confirmedfalse/quétkhóa. Overlay/source/geometry/revisionguards
  không đổi. Nhãn “Hình học vùng hợp lệ” chỉ topology, có nhắc vùng thử chưa
  nhận diện mép giấy, khôngauto-confirm/defaultdetector.
  UIcreate/filechooser3files/portraitEXIF/ngang/detailmanual4corner→confirm→
  render→compare/zoom đãchạy thật.12mẫugócmàu4distinct/page projectH khớp0kênh,
  3previewbyteequal từfull. Full983tests-Werror142.37s,64frontend192.3675ms/
  typecheck/build26modules174ms đạt. Strictsuite đầu981pass2fail do test cũ
  test_detect_batch mởCSVkhôngđóng; sửacontextmanager (khôngcore/suppress),
  7batchtestsGREEN rồi full983GREEN.7session/10page/30sourcehash cũ nguyên.
  ForcedDPR1/2 backing653×432/1306×864,mask140–0,gócgiữ/maxerror.01685323CSSpx;
  deviceDPR thật1, khôngclaimphysicaltouch/HiDPI. Comparisonresponsive320/768/
  1440 đạt. Evidenceignored experiments/results/mvp08-final-verified/;
  privateDPRharness archive vàxóa khỏifrontendroot, console sạch.
  63main+8AUX/110ID; nextMVP09.01detectAPI. GETdetail chưa córenderUUID để
  tựmởkếtquả, cầnexplicitrender; hoànthiệnreopen10.07. Backend8000/Vite5173
  giữ/stopfilebackendnhưtrước; core/CLI/requirements/dataset/nợdetector giữ.

## Bàn giao MVP09.01–02 — 18/10/2026

- Đã có POSTdetect qua sharedexecutor và UI “Tự nhận diện vùng”;65main+8AUX,
  nextMVP09.03. Checkpoint09-C1 còn cần09.03, không đánh dấu cảgiai đoạn09.
- DBschema2/7table thêm DetectionRun. Migration tường minh đúngschema1/6table→2
  cùngtransaction, rollback/idempotent; DB lạ vẫn từchối. Runtimebackupignored
  experiments/results/mvp09-01-02-verified/database-before-v2.sqlite3 giữ lại;
 8session/13page/39sourcehash cũ nguyên, mọirow cũ còn nguyên sau migration.
- services/sources.py dùng chung load_normalized_source cho render/detect:
  verifyPNG/hash/RGB/dims/noEXIF rồi BGRcopy; khôngquota15MiB nguồn nội bộ.
  detect_page snapshot nguồn/revision, gọi detector đúngmột lần với debug nội bộ,
  requestdebug quyết định persistPNG/fullattempts; không đổi config/confirmed/
  revision/timestamps. Cuối kiểm source/page/dims; config đổi khiCPU giữ nguyên.
- DetectionRunRead mở rộng DetectRead:runID/sourceartifact/hash/revision/trial/
  stageUUIDs. Manual_required200;debugfalse vẫnrunprovenance/khôngPNG. Metadata
  version/preset/trials/descriptors/units/timing/artifacthash thật.09.06 phải lấy
  artifacts theo runID/metadata, không gom mọi kinddebug cùngpage/revision.
  GETdebug/viewer vàrenderdebugtrue vẫn chờ09.05–07, không suy đã có từ bảng.
- UI proposal→draftfalse, scoreheuristic/warnings, manual5%kéo được; không tự
  PUT/render/confirm/retry. Operation/editcounter/page guard bỏ kếtquảmuộn;
  rev mismatch yêu cầuGET; lỗidetect giữdraft. Thaygóc xóa noteproposal cũ.
- Full996backend-Werror130.56s,68frontend183.7648ms/typecheck/build26modules169ms
  đạt.11API+2migrationtests có rollbackfile/latecommit/executor429/health/reopen.
  Browser anhtestnew≈.635,img_004≈.468warning,blankmanual; confirm→render201×285;
  giữresponse thật rồi edit/đổi trang khôngoverwrite, lỗi500giữdraft.320/768đạt.
  Dataset/nợimg_004ăn bàn giữ; core/CLI/requirements khôngđổi, khôngaccuracy.
- Backend8000 đã restart cùngDBv2; stopfile mới .tmp/phase09-api-backend.stop;
  Vite5173 giữ. Privateharness đãarchive/dọnfrontendroot; ảnh/DB/evidenceignored.

## Bàn giao MVP09.03–04 — 18/10/2026

- 67main+8AUX/110ID; checkpoint09-C1 đạt sau rà09.01–03, nextMVP09.05.
  Cổng09 và09-C2 còn chờ. Không đổi backend/API/DB/core/detector/dependencies.
- FilterPanel.tsx native selects/ranges dùng actions.editProcessing trong store
  hiện hữu. Đổi mode giữ fullconfig/inactive và confirmed của góc; không tựpreset,
  khôngHTTP/auto-preview/debounce. Sửa góc vẫn bỏconfirmed. Resultcũ mangstale.
- None khóa kernel; Color khóa contrast/CLAHE; Color/Gray khóa threshold;
  BWOtsu khóa block/C. Kernel3/5, CLAHEclip1..4 step.1/grid8×8; blocklẻ3..151,
  Cnguyên−20..30. Backend PUT vẫn validate fullconfig/warpfit; khôngclamp.
  LỗiPUT giữdraft/needsReload; GET rồi sửablock/Otsu và xác nhận lại.
- Render explicitfullPUTCAS→POSTreturnedrevision từ normalizedsource; editcounter
  giữdraft mới/bỏoutput cũ khi action đến giữa save/render/detect. Panel khóa busy
  hoặcneedsReload; không tạo globalstate/formlib/duplicatewarp-sizevalidator.
- 71frontendtests189.2519ms/typecheck/build27modules173ms và273backendtests
  config/render/enhancement/detect/migration-Werror14.23s đạt. Full996 từ09.01–02
  không chạy lại/backend giữ. Lượt sandboxAPI đầu không tiến triển đã dừng,
  chạy lại cùngsuite với thread/IPC quyền cục bộ đạt, không sửa test/giảmassert.
- Browser17records:3mode cùnggóc/chữViệt/highlight,Gaussian5/Median3/CLAHE4,
  min/maxblock/C/noHTTPđổi nhanh/Otsuinactive; shadowimg_003; smallwarp95×63
  từchối151/400 rồi3/C−20đạt.9renderfull/previewbyteequal corefresh; Colorroundtrip
  byteequal.9session/48sourcehash cũ nguyên.320/768/1440 khôngtràn, console sạch.
- Evidenceignored experiments/results/mvp09-03-04-verified/; harness archive/dọn,
  producttab giữdeliverable/viewportreset. Stopfilebackend giữphase09 nhưtrên.
  Debugrender09.05/GETdebug09.06/viewer09.07 chưa có; nợdetector/dataset giữ.

## Bàn giao MVP09.05–06 — 18/10/2026

- 69main+8AUX/110ID, checkpoint09-C1/C2 đạt; nextMVP09.07UIviewer, cổng09chờ.
- RenderRun/schema3/8table thêm compositeFKsource/full/preview vàfullmetadataJSON.
  Migration đúngv1/6table hoặcv2/7table→v3 atomic/idempotent, lỗirollbackDDL/version;
  DBlạ khôngreset. Backupignored mvp09-05-06-verified/database-before-v3.sqlite3.
  10session/19page/295artifact/19config/17detectionrun/57sourcehash cũ nguyên.
- render_page(...,expected_revision,debug=False) gọi core1lần. Debugtrue encode
  warp/filtered_bgr/prepared_gray(nếucó)/before_rotation đúngbuffertrướcxoay;
  full/previewsauxoay. HistogramBW256countspreparedgray/sum/hash/actualOtsut/global
  hoặcAdaptive/local/null; ColorGraynull. Fullconfig/inactive/H/scan-v1/environment/
  timing/units/UUIDhashtruyvết; config/confirmed/revision/timestamps khôngđổi.
  EncodeCPU ngoàiDB, finalgate/writerlock cũ, full+preview+stage+run cùngcommit;
  lỗi dọnfilemới chưathamchiếu. Mỗi render trả render_run_id kểcảdebugfalse.
- Debugfalse lưu run cơ bản/fullpreview, khôngstage/histogram; legacychưarun
  khôngbackfill. Frontendrender hiệnvẫndebugfalse;09.07 cần gửi true và dùng
  render_run_id khi GETđểghép đúnglượt, cậpnhậtTS DTO khi nốiUI.
- GET /sessions/{sid}/pages/{pid}/debug nhận tốiđa1trongrevision/render_run_id/
  detection_run_id; defaultcurrentrevision. Revision chọn latestđúngR gồmdebugoff,
  khônglấyrundebugcũtrám. Available/not_requested/not_recorded/incomplete; refs
  ArtifactReadkhôngpath,owner/kind/revision/hash/dims/fileverifyngoàiDBtransaction.
  Metadata giữrefs lịch sử; UI dùngenvelopeartifacts/missing_stages đểhiểnthị.
  Missingfile/hash/DB/ref/owner→incomplete, corruptsourcebinding500sanitize;
  invalidquery400/rununknown404, GETkhôngprocessing hoặcDBmutation.
- 1031backend-Werror203.33s;55focused15.38s sau chỉnhmôtảtiming,71frontend345.1064ms
  đạt. Frontendkhôngđổi/typecheckbuildbrowsergiữ03–04.35casesmới/coredetectorCLI
  unchanged; testsone-dispatch/debugparity/2revision/samerev/history/legacy/
  proposedmanual/strictquery/missingstages/rollbackstages+latecommit/reopen.
- Runtime5debugJSON qua2restartnguyên/36artifacthash/2histogramNumPy/sum1,917,201,
  Otsu165global vsAdaptive51/C10/CLAHE/localnull; gray1199×1599trướcxoay,
  rev2full1599×1199. Evidenceignored experiments/results/mvp09-05-06-verified/.
- Backend8000 đãrestartẩn cùngDBv3; stopfile mới .tmp/phase09-debug-reopen.stop,
  Vite5173giữ. ChưaUIstage/histogram,PDF/nhiềutrang nhưkếhoạch; dataset/nợdetectorgiữ.

## Bàn giao MVP09.07–08/AUX09.01 — 18/10/2026

- Hiện hành71main+9AUX/110ID, đủ8task09/cổng09/checkpoint09-C1/C2; nextMVP10.01.
  Đọc docs/audit-phase-09.md và phần09.07–08 cuối docs/algorithm-notes.md.
- UI render luôn gửi debugtrue; PipelineViewer lazyGET theo exact render_run_id hoặc
  detection_run_id. Không query newest revision để ghép kết quả; thiếu ID báo chưa có.
  RunDebug sở hữu GET-only store keyedrun/page, AbortSignal+sequence/unmount guard,
  GETretry được, mutation khôngretry. Parser kiểm source/page/kind/run/revision/ref.
- Stage dùng envelopeartifacts/missing_stages, naturaldimensions/error/retry rõ;
  không lấy ảnh từ refs lịch sử đangmissing. Histogram SVG256rawcounts đã lưu ở
  prepared_gray trước threshold/xoay, kiểm hash/dims/sum/scope/actualt; Adaptive
  localt=null, Color/Gray null. Missing ảnh không làm giả snapshot số đã lưu.
- CandidateMetrics có trial/contour/nQ/cạnh/rad/a/e/f/b/S/đónggóp/cạnhsupported;
  thiếu trường báo rõ không thay0. DetectionRun diagnostic giữ sau edit riêng
  detectionnote, không biểu thị góctay làproposal. Rendercũ có nhãnstale.
- Stageexplanations/guide đối chiếu3PDF/SHA; phân biệt detection/representation/
  descriptor/region/selection, DP≠MPP/findContours khônggánMoore/khôngép90°.
  Detector/core/CLI/requirements nguyên M1, nợimg_004/006/6ảnh1doc/test0 giữ.
- 1031backend-Werror181.84s/76frontend346.4371ms, typecheck/build33modules262ms;
  JS282.67kB/gzip87.90,CSS11.48/gzip2.91.11run81artifact/6histogramNumPy,
  2descriptor/27snapshotUI,11oldsession22page66sourcehashnguyên,320/768/1440
  khôngtràn/console sạch. Evidenceignored mvp09-final-verified; harness đãgỡ.
- Backend8000/Vite5173 giữchạy, stopfile backend .tmp/phase09-debug-reopen.stop.
  Schema3/9path10method khôngđổi. Reopenauto-result/UIrunhistory chưa làm10.07;
  PDF11/đánhgiá13/góinộp14 chưađạt, khôngclaimaccuracy. Khôngcommit/push/deploy.

## Bàn giao MVP10.03–07/AUX10.01 —18/10/2026

- Hiện hành78main+10AUX/110ID; cổng02–10/checkpoint10-C1/C2 đạt, nextMVP11.01.
  Đọc docs/audit-phase-10.md/API/image-contract trước export; schema3/11path14method.
- Order PUT full permutation dưới writer gate; position tạm/final tránh UNIQUE,
  không tăng revision ảnh hoặc render lại; no-op giữ timestamp. UI giữ page_id,
  draft/result qua order; lost/error response GET reconcile, không retry mutation.
- DELETE page/session owner-scoped204, DBcascade/compact rồi cleanup từng UUID
  không còn reference sau commit. Verify/hash/path ngoài DBtransaction, không
  recursive-delete; lỗi/crash có thể còn orphan/log, chưa GC bền hoặc Undo.
  Finalize render/detect/import owner gate chặn publish sau xóa, có5race tests.
- PageRead.latest_render/latest_detection additive nullable, hydrate từ exact run
  metadata/source/hash/dims/revision/pair; GET không CV/I/O mọiPNG/ghiDB.
  Legacy không RenderRun đủ pair→null, không bịa/backfill; debugGET/artifactGET
  kiểm bytes. Reopen tự hiện full cũ, giữ diagnostic nguồn, không áp proposal
  vào persisted draft hoặc auto-confirm/render. Xoay UI0/90/180/270 dùng lõi cũ.
  PageList metadata cập nhật ngay sau lưu/render; chuyển trang/reload bỏ draft.
- 1071backend-Werror189.56s/87frontend380.9416ms/typecheck/build37modules262ms.
  23UIstates,3full-preview byteequal corefresh; restart3trangColor0/Gray90/BWOtsu270
  giữ order[2,1,3]/3debugJSON/17hash.14old docs50pages150sourcehash/alloldSQLrows nguyên.
  Browser DELETE chỉ mock; API thật chỉxóa newQA IDs, không tài liệu cũ.
  Harness archived/removed, console sạch, viewport reset; evidenceignored
  experiments/results/mvp10-final-verified. Core/CLI/requirements12hash khớpM1.
- Backend8000/Vite5173 giữchạy; stopfile .tmp/phase10-final-reopened.stop.
  Export snapshot/khóa mutation/PDF còn11; chưa đổi detector/dataset6ảnh1doc/test0
  hoặc nợimg_004/006. Khôngcommit/push/deploy hoặcảnhra ngoài.

## Bàn giao MVP11.01–02 —18/10/2026

- Hiện hành80main+10AUX/110ID; nextMVP11.03. Checkpoint11-C1 cần03,
  cổng11/M3 chưađạt. User xác nhận khôngcầnhoàn tác; không thêmUndo/Trash.
  Đọc docs/export-snapshot.md/API/image-contract trước nốiencoder.
- schemas/exports.py ExportRequest/ExportRead; alias sessions.ExportRequest giữ.
  pages subset/explicitorder/UUIDv4/exactrevision, PDF1..20/PNG-JPG1/unique;
  optionsA4/auto-portrait-landscape/margin0..30/encodingpng-jpeg, strict/frozen.
- services/exports.py export_snapshot context phải bao trọnencode/commit; snapshot
  fullRenderRun/currentconfirmedrevision/source/SHA/pair/config; khôngpreview.
  Missinglist→409PAGE_NOT_RENDERED details.pages theoorder; corrupt500/no fallback.
  run_export reserve trướcqueue, writer sync callback, không cóencoder giả.
- session_guards.py lease memoryperEngine/UUID vớiRLock/WeakKeyDictionary;
  mutation guard trướcDB, CPU ngoài;8mutationrename/config/order/deletepage/session/
  import/render/detect chặn409SESSION_BUSY. Asyncupload/render/detect preflight qua
  threadpool trướcqueue; prepublish giữgate. GET/health khôngkhóa.
  Queuedcancel/429/exception trảlease; activecancel giữlease/slotđếnworkerfinally.
  RestartEngine mới khôngbusy cũ; singleprocess/oneEngineDB, khôngmultiworker.
  Giữfullbằngdescriptorimmutable+DBrefs+ownerlease; chưapin table hoặcGC/OSguard.
- 54tests mới;63focused21.35s, full1125-Werror171.02s. Frontend khôngsửa/chạy lại;
  mốc87tests/build ở10 giữlịch sử. RuntimeDBriêng3syntheticpages→subset[3,1],
  8mutation409/secondexportblocked/26hash nguyên/unlock. Callbackchỉverify,
  exports_written0; encoder/ExportRecord/API/UI/PDF còn11.03–08.
- Restartbackend cùngDBschema3 giữ14docs49pages147sourcehash vàtấtcảSQLrowsnguyên,
  core/CLI/requirementsM1khôngđổi, OpenAPI11path14method. Evidenceignored
  experiments/results/mvp11-01-02-verified. Backend8000/Vite5173giữchạy,
  stopfilemới.tmp/phase11-01-02.stop. Khôngcommit/push/deploy/ảnhra ngoài.

## Bàn giao MVP11.03–04 —18/10/2026

- Ởmốc11.03–04:82main+10AUX/110ID;checkpoint11-C1đạt,khiđónextMVP11.05 ghép/lưuPDF,
  checkpoint11-C2/cổng11/M3cònchờ. Đọc docs/export-encoding.md trước task05.
- export/images.py encode_image gray/BGRuint8→PNGpixel-exact/JPEG95/0,
  RGB/L/noEXIF-ICC/noscale/filter/rotation. DownloadfilenameASCIIleaf≤bounded,
  whitelistpng/jpg/pdf/DOSreservedguard;khôngclientpathvật lý.
- services/exports.load_export_pixels verify/hash/size/decodePNGmodeRGB-L/dims,
  encode_snapshot_image nhậnPNG-JPG1page vàdùngfullsnapshot/lease, khôngpreview.
  EncodedImagefrozen payload/mime/filename/width/height;chưapersistExportRecord.
- export/pdf.py mm_to_points/layout_a4/append_pdf_page/encode_pdf_page:
  A4210×297mm×72/25.4,auto theoW/Hfullsauxoay/squareportrait/explicitoverride,
  marginfinite0..30,cùngscale/căn giữa/khôngstretch-crop. appendshowPage1lần,
  encode1pagePDFbytes;PNGnhúnglossless hoặcJPEG95/0DCT;khôngxoaythêm.
- 51tests mới(28image/23PDF),83focused17.96s,full1176-Werror167.56s.
  DBQAriêng3syntheticsources→6PNG-JPG/4PDFonepage;3PNGexactfull1199×1599/
  1599×1199>preview1000. PypdfMediaBox/fullXObject/matrix đúng,Poppler96dpi/
  16corner samples maxdelta2;đãxem4render/contactsheetkhôngmấtmép.
  0ExportRecord/HTTPdownload/UI;ghép/lưu/route/UIcòn11.05–08.
- Restartbackend cùngDBschema3 giữ14docs49pages147sourcehash/allSQLrowsnguyên;
  core/CLI/requirementsM1/OpenAPI11path14methodkhôngđổi. Frontendkhôngđổi/
  khôngrerun;mốc87tests-build ở10. Evidenceignored mvp11-03-04-verified.
  Backend8000/Vite5173giữchạy,stopfile.tmp/phase11-03-04.stop;khôngcommit/push/deploy.

## Bàn giao MVP11.05–07 —18/10/2026

- Ởmốc11.05–07:85main+10AUX/110ID,11.01–07 vàcheckpoint11-C1/C2đạt;
  nextMVP11.08 kiểmchứngcuối/rà8task; cổng11/M3chưađạt.
  Đọc docs/export-workflow.md/API/image-contract vàtasks/todo trước làmtiếp.
- publish_export chỉdùngfullsnapshot/lease,PDFtheoorderrequest/appendA4từngtrang,
  PNG-JPGmộttrang;encodecomplete→storetemp/fsync/publish→DBArtifact+ExportRecord
  cùngcommit→receipt. Recheckowner/exactR/config/fullreference;khôngbumpconfig/
  revision/order/sessiontimestamp. Rollback/cleanupchỉoutputmớikhôngreference;
  filesystemcrashcóthểorphan,khôngGCbền.
- POST/sessions/{sid}/exports dùngsharedexecutor1active2waiting/lease,
  trả201ExportRead;GETartifacthiệnhànhMIMEthật/inline/UUIDfilename/nosniff/
  private-no-store. Khôngthêmdownloadroute/migration/idempotency.
  429/409/encode500PROCESSING_FAILED/storage500STORAGE_FAILED đãkiểm.
- ExportPanel chọnsubsettheoorderpagelist/optionsA4/margin/encoding vàdownload.
  Dirtyselected/chưaconfirmedbịchặn;dirtyunselectedđượcgiữ;khôngPUT/auto-confirm.
  GETpreflight exactR;chỉ409PAGE_NOT_RENDERED hợp lệ→GETvalidate→renderđúng
  trangthiếu→POSTlạimộtlần;network/429/unknownoutcome/lỗi2khôngautoretry.
  PendingkhóamutationUI, doubleclickref/late-unmountedguard.
  ExportPanelkeyprefixexport: tránhtrùngUploadPanelkeycùngdocument.id.
- 18backendtests mới/1194full-Werror195.83s;95frontendtests252.9859ms/typecheck/
  build39modules186ms. TảiPDF/PNG/JPGthật;2PDF3trangorder[1,2,3]/[3,1,2]
  đọcPypdf/renderPoppler/xem6trang,embeddedfullpixel/A4matrixđúng.
  PNG1119×1599modeLexactfull;JPGcolorMAE.0829946032lossy.
  Browser320/768khôngtràn,tabfinalconsolekhôngwarning/error;sửaReactkeyđãkiểm.
- Giữ14docs49pages147sourcehash/alloldSQLrows/FKcheckrỗng,
  core/CLI/requirementsM1khôngđổi;schema3/OpenAPI12path15method.
  Evidenceignoredexperiments/results/mvp11-05-07-verified.
  Backend8000/Vite5173giữchạy;stopfile.tmp/phase11-05-07.stop.
  Khôngcommit/push/deploy/ảnhhoặcDBra ngoài. Dataset6development/1doc_01/test0,
  nợdetectorimg004/006vẫngiữ. Khôngtích11.08từviệcđãcóPDF/UI.

## Bàn giao MVP11.08/AUX11.01 —18/10/2026

- Giaiđoạn11đủ8task/checkpoint11-C1/C2/cổng11/M3đạt;86main+11AUX/110ID.
  NextMVP12.01, đọcdocs/audit-phase-11.md/API/image-contract/tasks/todo.
- Chỉthêm5integrationtests vàdocs ởlượtnghiệmthu;khôngsửaapp/thuậttoán/deps.
  ActualPOSTexportgiữqua barrier chặn8mutation+secondexport409SESSION_BUSY;
  GET/health/tàiliệukhácvẫnđược. LỗiởPDFpage2khôngfile/recorddở, giữdữliệu
  vàexportsauthànhcông. PNG/JPG/PDFđãcommitgiữsnapshot/byteskhiR2/restart.
- Full1199backend-Werror217.02s,95frontend297.0281ms/typecheck/build173ms.
  Focus16HTTPtests13.31s;5mới, banđầulỗioracleSQLitebytesdođổitênsidkhác
  đượcphép,đãsửabaselinesauđổitên;khôngnớiownerJSON/file/recordchecks.
- QAriêng3nguồn1120×1600/Color0-Gray90-BWOtsu270/r1/orderUI[3,1,2].
  TảiPNG/JPG vàPDFautoPNG5/portraitJPEG30thật. HaiPDFđọcrenderxem6pages,
  PNGembeddedexactfull/JPEGMAE<.1,A4matrix/options/orderđúng.
  PhysicalrestartgiữSessionDetail/4ExportRecord/30artifactSHA;UIreopen3full
  chỉGETvàxuấtPDFmớithànhcông;UIbusybuttons/uploaddisabled,consoletrống.
- Giữ15old docs52pages156sourcehash/alloldSQLrows/7exports/FKcheckrỗng;
  core/CLI/requirementsM1/schema3/OpenAPI12path15methodkhôngđổi.
  Evidenceignoredexperiments/results/mvp11-final-verified/qa.json.
  Dataset6development/1doc_01/test0/nợimg004-006giữ,khôngclaimaccuracy.
- Leaseoneprocess/mộtEngine,crach-I/Oorphan/noGCbền/noidempotency/exporthistory,
  PDFảnh/noOCR vàfilenameUUID làgiớihạnđãghi. Khôngmởrộngởlượtaudit.
  Backend8000/Vite5173đangchạy,stopfile.tmp/phase11-final.stop;tabQAgiữ.
  Khôngagents/commit/push/deploy hoặcảnh-DBrabênngoài.

## Bàn giao hiện hành AUX11.02 — tự nhận diện sau nhập ảnh

- Hồi quy callback18/10 đã sửa: runner giữ trong useState có thể sống qua Fast Refresh
  và gọi onUpload(file) kiểu cũ, thiếu onDetecting sau upload commit. Helper có
  callback mặc định; UploadPanel dùng useMemo(factory,[factory]) để cập nhật code.
  Unit RED đúng TypeError→GREEN; browser một ảnh/một DetectionRun/console sạch.
  Evidence callback-upload-fix-verified;18old docs59pages177sourcehash/SQL nguyên.
  Ảnh của lượt lỗi đã lưu: không re-upload hoặc tự thay nháp người dùng.


- Theo yêu cầuuser18/10: mọiảnhnhậpmớiUI tựupload→detect tuần tự,debugtrue.
  Chỉfrontendorchestration,khôngđổiAPI/DB/thuậttoán. Đọcdocs/auto-detect-on-import.md.
- importWithDetection giữpageđãcommitnếudetectlỗi,quota vẫntrừ1/batchtiếp tục;
  khôngretryupload/detect. CallbackonDetectingphânbiệtprogress;appendpage sau
  detectkếtthúc. Không autoPUT/confirm/render/export;buttondetecttaycòndùng.
- Initialreloaduntouchedpage revision0/cornersnull/confirmedfalse đượcadopt
  latest_detection đúngsource/revision0 vào draft mộtlần;manual_required5%.
  assertDetectionProposal gate dùngchungvớimanualdetect. Gócđãlưu/revision>0/
  liveeditorloaded hoặcnhápeditedkhôngbịproposalcũthay. PageListnhãnchờcheck.
-103frontendtests359.4028ms/typecheck/build41modules203ms;36backendAPItests
  import/detection/reopen-Werror11.13s. Backendkhôngsửa/full1199mốc11khôngrerun.
  Browserpaper/broken/blankbatch→2newpages/2detectruns,415riêng,nhápGraytrangcũ
  vàColorfullgiữ;reopenkhôngdetectthêm,confignewR0/null/false.
-86main+12AUX/110ID,M3giữ,nextMVP12.01chưalàm. Giữ17old docs58pages174hash/
  alloldSQLrows/coreM1;OpenAPI12path15method/schema3khôngđổi.
  Evidenceignoredexperiments/results/auto-detect-import-verified.
  Console0/320-768khôngtràn/viewportreset/tabQAgiữ. Detectornợimg004-006giữ;
  tựđộngkhôngcónghĩalàtựnhậnđúng. Khôngchạybackfilltựđộngtài liệu cũ.
  Backend8000/Vite5173/stopfile.tmp/phase11-final.stopgiữ.

## Lịch sử chuẩn bị MVP13.01–02 — 18/10/2026 (đã cập nhật26/10 bên dưới)

- User chốt khoảng20ảnh/5tài liệu, thay mục tiêu40/10; ảnh bổ sung chưa có,
  user sẽ cung cấp ngày mai. Phương án3development docs/2test docs theo dataset.md.
  Không tự tạo ảnh/số liệu, không chuyển doc_01 hoặc ảnh đã dùng thử thành test.
- Manifest vẫn6development/1doc_01,test0;7tệp ban đầu có1trùnghash.
  anhtestnew.jpg/WrongEXIF.jpg chưa xác nhận nhóm, đã từng dùng thử nên không test.
  Thêm tag wrinkled/cropped; img_002 có cropped theo quan sát mép dưới trái.
- experiments/annotations.json schema1/W−1/H−1 có6record bind normalized_sha256
  vàdimensions1536×2048; img003/004/005quad thủ công,001/006gấp/nonplanar và
  002sát-cắt khung→unlabelable/cornersnull/reason. Không lấy proposal làm nhãn.
  reviewed6/6 do Codex xem nguồn/overlay, chưa có người thứhai xác minh nhãn.
- validate_annotations.py dùng lại validate_manifest/validate_quad; default
  kiểmhashfiles/dimensions/EXIF/IDcoverage/hìnhhọc/review. --allow-unreviewed chỉ
  chuẩn bị; --output-dir tạo thư mục mới/PNG/snapshot, không sửa nguồn hoặc CV.
  Evidence ignored experiments/results/mvp13-01-02-verified/ có inventory,
  overlays/review-sheet và validation. Dataset.md có quy trình bổ sung ngày mai.
- Kiểm chứng13:35focused/1216backend-Werror186.53s đạt; frontend103 là mốc
  trước,khôngrerun vì không sửa UI. verification/pytest.log lưu trong evidence.
-13.01/02 vẫn unchecked,86main+12AUX không tăng; công cụ/nhãn nhóm hiện có đã làm,
  chưa nghiệm thu toàn bộ khi thiếu bộ cuối. Không tự tick/skip giai đoạn12.

## Mốc dữ liệu MVP13.01–02 — 26/10/2026 (tiếp13.03–04 bên dưới)

- User chốt bộ hiện có là đủ, thay mục tiêu20ảnh/5tài liệu:13ảnh/2tài liệu.
  doc_ver2 có8file/7ảnh khác nhau, một bản sao img_009 giữ ngoài manifest.
  User xác nhận cùng một tờ/nội dung; tất cả img007…013 là doc_02/test.
  Giữ doc_01/6ảnh development. Không chia cùng nội dung sang hai split.
-13.01–02 đã checked theo quy mô mới,88main+12AUX/110ID;next13.03.
  Giai đoạn12 chưa nghiệm thu/skip;13-C1 còn chờ13.03,không tick cảphase13.
- annotations có13record/10labeled/3unlabelable/reviewed13. Nhãn6ảnh cũ nguyên;
 7nhãn mới thủ công trên nguồn chuẩn hóa,đã mở từng nguồn và overlay full.
  Source1536×2048 trừimg011 là2048×1536. BindPNGhash/dims/W−1/H−1.
  Nếp/curl nhẹ có quad xấp xỉ4mốc,không mask phân đoạn hoặc nhãn subpixel chuẩn.
-7ảnh test chỉ normalize/gánnhãn,CHƯA chạy detector/tune/so kết quả trên test.
  Đợi frozen13.06 rồi13.07 mới đánh giá. Một tài liệu mỗi split/cùng nền bàn,
  thiếu đa dạng nhàu rõ/lóa/highlight và một người gán là giới hạn phải ghi.
  Không coi10/13nhãn hoặc score là accuracy. Không tự đòi thêm data sau user chốt.
- Validatorfiles/hash/split/annotations đạt,35focusedtests1.62s. Fullbackend1216
  vàfrontend103 là mốc18/10,khôngrerun vì không đổi implementation. App/core/API/
  DB/deps giữ nguyên. Không thêm metrics13.03 trong lượt này.
- Evidence ignored experiments/results/mvp13-doc-ver2-20261026/:inventory,
  normalized/overlays/snapshots/review-sheet/verification. Hai ảnh thử cũ
  anhtestnew/WrongEXIF chưa nhóm,không thêm vào test. Ảnh in có thông tin riêng,
  không chép nội dung cá nhân vào docs/manifest/notes hoặc gửi ảnh ra ngoài.

## Mốc MVP13.03–04 — 26/10/2026 (tiếp 13.05–06 bên dưới)

-13.03/04 đã checked,90main+12AUX/110ID,13-C1 đạt;next13.05.
  Giai đoạn12 chưa nghiệm thu;13-C2/cổng13 chưa đạt. Dataset13ảnh/2doc giữ.
- experiments/metrics.py dùng lại corepolygonIoU, chỉ canonical reversedcycle
  trong đánh giá sau topology,không sortcrossing. Cornererror=minmean4khoảngcách
  sourcepixel qua8ghép/chiaD. Thiếuproposal trênGT:IoU0,cornernull vàbáosốmẫu;
  unlabelable táchriêng,mẫu sốIoU3ảnh,counterproposal toàn6development.
- evaluate_detection.py/configsdetection_trials.json:4profiles cùngrevised:
  scoring,largest_contour,no_gaussian,no_closing. Largest chọnmaxcontourarea trong
  validpool trướcNMS,cùngscorestatusgate;không coi làbaseline bỏ mọi gate.
  Chỉdevelopment; test7ảnh chưa chạy detector/tune. Summary+CSV24dòng/0error,
  metadata allattempts/descriptions/aefb/timing/stages/provenance và6comparison đãxem.
- detection.py có opt-in gaussian_kernel=0 (graycopy,IDg0) vàclosing=False
  (rawedgescopy) đểablation. Defaultapp vẫnGaussian5/closingTrue/detect-v1;
  status/góc/score/description/candidates/rawmaps/blur/overlay bằngmãtrướcsửa trên6nguồn.
  CODEHASH detection đãthayđổi; snapshotM1 cũ làlịch sử,không sửa hash đểgiảunchanged.
  Khi13.06 khóa dùng currentcodehash. HTTP/DB/UI/config/deps khôngđổi.
- validate_annotations thêm Python split optional;dev-only khôngmởtestfiles,
  defaultCLI vẫnkiểm13. Evaluator decode verifiedPNGBytesIO/chặnhash/dims thaygiữa
  validatevàđọc. Schema bool/null/list sai từchối;outputmới,khôngoverwrite/retry.
- MeanIoU trên3GT:scoring.952871,largest.951532,noGauss.901162,noClosing.951532;
  cảbốn2/3≥.90. img004 vẫnănbàn(.872497;noGauss.716925),img001/006 bỏclosing
  tăngproposal nhưngchọndòngchữ/thiếugiấy. Khôngaccuracytest/generalization;
  mặcđịnh khôngtune từquan sát một tài liệu. Timingmộtlượt khôngbenchmark13.07.
-1244backend+experiments tests-Werror166.50s đạt (1219backend+25experiment).
  Frontend103 làmốctrước,khôngrerun UIunchanged. Evidenceignored
  experiments/results/mvp13-03-04-verified/final làbảnchính;development và
  development-final làlượttrunggiannhậthash,khôngtrộn sốđo. default-parity,
  verification/pytest.log ởparent. docs/results.md giải thích mẫu số/giới hạn.
- Khôngagent/commit/push/deploy hoặcảnh/DBrabênngoài. Không13.05–08/frozen/test.

## Mốc MVP13.05–06 — 26/10/2026 (tiếp13.07–08 bên dưới)

- 13.05/06 checked, 92 main + 12 AUX/110 ID; 13-C1/C2 đạt, next 13.07.
  User chọn chạy hồi quy cần thiết trước khóa, nên phụ thuộc 12.07 của 13.06
  đã điều chỉnh sang cổng hồi quy giới hạn được ghi docs/verification-matrix.md.
  Không tick 12.01–12.07 hoặc cổng 12; không coi cổng 13 đã đạt.
- evaluate_enhancement.py chỉ development, 6 ảnh/3 cặp GT/3 unlabelable/0 lỗi.
  Mỗi ảnh warp một lần, hai dispatcher chỉ khác threshold.method; prepared_gray
  và histogram bằng nhau. Median3/không CLAHE/rotation0/Adaptive31 C10; Otsu t147/172/186.
  Đã xem 6 BW full/warp/crop. Otsu đen bóng, Adaptive còn ô ly/đứt nét.
  Không accuracy chữ; thiếu highlight thật. Synthetic highlight giữ riêng ngoài manifest.
- frozen.json/mvp13-freeze-v1 schema1 lưu detect-v1/scan-v1/preset/score,
  91 source hashes, config/dataset metadata/dependency/environment. --check tiến trình mới đạt.
  SHA ce89a90e2fb9ca092350886276201f87e81cd09c90e6507f799fceca6a8d8109.
  Không sửa helper đã khóa theo test; runner benchmark mới lưu hash riêng và verify_frozen
  trước đọc ảnh/xử lý. Chưa thêm CLI test/benchmark 13.07, không ghi đè bản khóa.
- 1.255 backend+experiments tests -Werror 203.28s; 103 frontend 521.4369ms;
  typecheck/build 41 modules 631ms đạt. Browser QA 2 ảnh/415 giữa batch/auto detect,
  confirm/render Color-BWOtsu/PDF2/download; 409 thiếu render được hồi phục đúng.
  Pypdf/Poppler đọc/render 2 trang, embedded exact full; physical restart giữ 38hash,
  doc/export/config/r1; UI reopen chỉ GET/100%, console sạch. 61 old SQL rows/49old artifacts nguyên.
- Core/API/UI/deps không sửa ở lượt này. Data 13 ảnh/2doc và hash nhãn/manifest nguyên;
  7 test chưa chạy detector/enhancement/tune. Giữ nợ img_004/006 và giới hạn một doc mỗi split.
  OpenCL probe báo queue unavailable và trả false, snapshot ghi thực trạng; không benchmark GPU.
- Evidence ignored experiments/results/mvp13-05-06-verified/: enhancement, synthetic-highlight,
  regression-proof/pytest/frontend logs, runtime-before/restart/pdf-checks/browser-reopen.
  Docs/results và experiment-environment ghi quan sát/lệnh/giới hạn. Không agents/commit/push/deploy.
  Backend8000/Vite5173 đang chạy; stopfile backend .tmp/phase13-frozen.stop.

## Bàn giao hiện hành MVP13.07–08 — 26/10/2026

- 13.07/08 checked,94main+12AUX/110ID;13-C1/C2/cổng13 đạt,next14.01.
  Audit8task docs/audit-phase-13.md;giaiđoạn12 vẫn chưa nghiệm thu toàn bộ theo cổng hồi quy
  giới hạn user chọn cho13.06. Không làm14 hoặc tự tick12.
- Thêm experiments/benchmark.py ngoài91sourcefrozen,không sửa helper/core/API/UI/deps/nhãn.
  FrozenSHA ce89a90e2fb9ca092350886276201f87e81cd09c90e6507f799fceca6a8d8109 giữ.
  Runnerfinalv1.1 SHA b881679641ccd7f54de5708c9f6ef72f0657e72b15384ab8293633b05d05b7ec.
  verify trước pixel/trongserver/sauđo;OpenCLfalse được tái lập trong process trước gate,
  vì child/elevatedWindows cóthểtựbậttrue. Không nới snapshotcheck.
- 7test/doc_02 đã quan sát:7/7IoU≥.90,meanIoU.995347032005372,
  mean cornererror2.3031296606px/.0009001523D,6proposed/1warning,đềuCanny.
  img009score.5997499034 cảnhbáo dùIoU.994511;không tune ngưỡng hoặc coiS làaccuracy.
  Dataset13ảnh/2doc,10GT/3unlabelable vàhash nguồn/manifest/nhãn giữ.
  Test1doc/7ảnh liênquan,cùngnền;khônggeneralization hoặcOCR/dewarping.
- 1warmup+5đo/ảnh×4đường=168rows,140measured/28warmup,35mẫu/đường/0lỗi.
  Finalp50/p95ms:core detect238.8527/297.31905;render16.8652/21.02552;
  HTTPdetect313.193/340.87657;render178.4996/204.4952.
  Working set sampled max:core detect111071232B/render122912768B;
  HTTPdetect163463168B/render163422208B,PIDserver thật. Khôngsum RAM cảmáy/exactper-callpeak.
  Cachekếtquảappoff/84HTTPfreshIDs;OS cache/allocator giữ,warm-cache,khôngSLA/populationp95.
- Windowsvenv Popen.pid cóthểlàredirector4.7MiB;đãtái hiện/sửa quaos.getpidserver-process.json
  vàđối chiếu logUvicorn,testgreen. Initialtest/ giữnguyên,gắnMEASUREMENT_INVALID.json;
  khôngdùngRAMHTTPinitial hoặctrộnsốgiữalượt. Full/metrics/comparison7ảnh hai lượt bằng byte,
  không đổi thuậttoán/nhãn.Test đã thấy từinitial;retiming khôngtạo test độc lập mới.
- 1261backend+experiments -Werror173.10s đạt (1219+42),6runner tests gồmfalseproposal,
  quantilewarmup/errors/hashdrift/frozengate/HTTPisolatedfresh/PIDactual.103frontend/build
  làbằngchứng13.06,khôngrerun vìsourcefrozenunchanged. Initialfull212.11s/lượtđầugiữlịchsử.
- Verificationreplay70detectorPNG/hash/dims/gray/Gaussian/Canny/closing/S/metrics;
  7HTTPfull bằngcorebytes,84uniqueIDs,servergracefulshutdown,đãxem7overlaycontactsheet/img009.
  Bằngchứng ignored experiments/results/mvp13-07-08-verified/final làprimary;
  test/initial invalidRAM giữ;verification/pytest/log/review-sheet ởparent.
- Giữ nợimg004/006ănbàn vàthiếuphủnhàu mạnh/lóa/highlightthật. Khôngcopy nội dung riêng
  củaảnhin vào docs hoặcảnh/DB ra ngoài/Git. Không agents/commit/push/deploy.
- Benchmarkserver/SQLite cô lập,đãđóng;khôngdùngDBappngườidùng.Backend8000/Vite5173 cũ giữ,
  stopfile.tmp/phase13-frozen.stop.Nếu14đónggói đổiappsource:giữsnapshotbảnđo làm lịch sử,
  version/hashbảnđónggói mới vàkiểmchứngtươngứng,khôngghìđèfrozenđểgiảcùngbảnđãđo.

## MVP14.01–02 — Bản chạy cùng origin, 26/10/2026

- Đã đạt14.01–02:96main+12AUX/110ID; next14.03. Checkpoint14-C1 chờ14.03,
  chưaM4/gói nộp;stage12 khôngtựnghiệmthu. Đọc docs/local-runtime.md và progress đầu file.
- main.create_app(database_path,*,frontend_dir=FRONTEND_DIST); None choAPIriêng.
  settings.FRONTEND_DIST=root/frontend/dist; web.install_frontend dùngStaticFiles,
  HTTP404handler chỉindex/assets/HTMLextensionlessnavigation. Khôngcatchallroute,
  giữAPI405/Allow/OpenAPI12path/schema3; data/source/dotpath/missingasset trảJSON404.
  index no-cache/staticnosniff/realpathguard; khôngmount project/data.
- Giữ30requirements pins/npm lock/frozen13 nguyên. Cleanvenv3.12.10nosystempackages,
  pipinstall/check/imports; npmci sạch24package/103tests/typecheck/build41module,
  3distfiles bằngbyte buildphục vụ. Full1279passed233.16s-Werror từcleanvenv
  (1236backend+43experiments);17static tests +1snapshotdrift mới,khôngskip.
- Cleanbackend8001SQLite riêng:browser2syntheticpages/detect/confirm/Color-BWOtsu/full590×790/
  PDF2page/root-deepreload/restart2actualPID;38artifactSHA giữ/full bằngcorebytes.
  Không test/tune ảnhheldout. Server8001 đãdừng;QAevidenceignoredmvp14-01-02-verified/.
- Frozen13 vẫnSHAce89a90…; chỉmain/settings đổi trong91source,thêmweb;processing/preset/
  algorithms/10inputs unchanged. Gate13 bâygiờphảibáodrift,bảnđónggóimvp14-local-v1hashriêng.
  Frozen-source/ lưu91source/10input/runnerb8816796… cũđúngbyte/hash,khôngghiđèfrozen.
  benchmark.isolated_server(...,frozen_path=...) choHTTPsynthetic tests;verify_runtime vẫn
  fullstrictgate vàdefaultCLI13 khôngđổi. Snapshot temporary khônglà lượtđánhgiátestmới.
- Backend8000 hiệnphụcvụbuild/API cùngorigin,PID269772,stopfile.tmp/phase14-local.stop;
  SQLdump/87datafiles giữhash trước/saurestart. Vite5173 cũgiữchạy. Browserdeliverable8000
  mởQA13cũ chỉđọc/100%full/console0; khôngsửauserdata. Dùngdocs/local-runtime lệnhchạy1worker.
- KhôngđổiReact/Vite/core/API/schema/dependency/dataset; giữnợimg004/006ănbàn.
  Khôngagents/commit/push/deploy. READMEfull/userguide/report/demo/góinộp14.03–08chưalàm.

## MVP14.03–06 — README, hướng dẫn và báo cáo, 26/10/2026

- Supersede next14.03 ởmốc14.01–02:đãđạt14.03/04/05/06 vàcheckpoint14-C1/C2,
  100main+12AUX/110ID;14.04a/b taskconkhôngcộngparent. Next14.07demo/14.08góinộp/M4 chờ;
  stage12giữchưa nghiệmthu toànbộ. Đọc README/docs/user-guide.md/docs/report.md vàprogressđầufile.
- READMEđãviếtlạitheobuildcùngorigin,giữroot/venv/npmci/build/CLI1worker/health/Ctrl+C/data/
  lỗi/localhost/dev/tests. Cleanproject.tmp/mvp14-guide-clean/project/Python3.12.10nosystempackages/
  Node24.15/npm11.12.1 cài30pin/npmci24/build41/imports/healthCLI8002đạt;3distbytes khớp8000.
  17statictests từsourcecopy/venv mới đạt4.51s-Werror,full1279/103mốc14.01–02khôngrerun vìdocs-only.
- Userguide4ảnhUIthật+2samplePNG(QAPAGE)safe trongdocs/images/user-guide/;dirty/confirmed/busy/
  stale/needsReload/Lưunháp luônunconfirmed. Tài liệumới2ảnh→auto detect→keyboardcorner/saveDraftr1/
  confirmr2/BWMedianOtsu/render3→trang2Colorconfirm1/norender→exporttựrendertrangthiếu/PDF2/
  downloadthật/PNG1→reload/Ctrl+Cgraceful/restart2actualPID→39artifact+metadata giữhash.
  PNGbằngfull;PDFtảiđúngbyte/Poppler2pagesđãxem;console0.Servertest8002đãdừng,8000usergiữ.
- Reportmục1–7thuậttoán/đơnvị/params/biểu diễn-mô tảbiên/sai sốfitarea-vsdistance/
  Canny-closing-contour/DPkhôngMPP/scoringNMS/homography/CLAHE/Otsu/Adaptive vàthưviện-vstựviết.
  Đốichiếu3PDFSHA,slide5p21/35,slide6p17–19,giáotrìnhcácphầnliênquan vàdocsOpenCVchínhthức.
  Mục8–14dataset/metrics/ablation/BW/test/time-RAM/targets/limits/debt.4bảng+hashledger sinh từCSV;
  p50/p95/RSSđãtínhlại140measured/28warmup,giữinvalidlauncherRAMhistory/one-testdocbounds.
- 4hìnhreportdocs/images/report chỉvectorbiên/hist/metrics/barplots,khôngpixelbodytranguser.
  Linklocaldevelopmentignored cóCanny/closing/overlay/warp/Gray/BWđểtựxem;khôngcopyảnhuservàoGit.
  SupplementCLAHE2/grid8x8trênpreparedgrayimg003ở14.05đượcghi riêng,khôngretune/retesttest.
- Khôngđổiappsource/schema/preset/dependency/manifest/nhãn/frozen13;hashcodepackaging14vẫnkhớp.
  Frozen13gatevẫnphảibáodrift,khônggọilạibenchmarkCLIvớisource14đểcốlàmxanh.
  ToolenvMatplotlib3.11.2/.tmp/report-tools-venv cáchbiệtappvenv,requirementsappgiữ30pin/Pillow12.3.
- Evidenceignoredmvp14-03-04-verified/ vàmvp14-05-06-verified/,helpers.tmp/verify14_guide.py/
  collect14_report.py/plot14_report.py/fill14_report.py;progresscóscope/count/giớihạn.
  Backend8000vẫnstopfile.tmp/phase14-local.stop/Vite5173cũ;khôngsửauserdata/agents/commit/push/deploy.
- Ràcuối321Markdownlinks/4resulttables/hashledger/10PNG/code/pin/frozen đạt;verification.json đãghi.
  87tệpdata thamchiếu14.01–02giữhash;SQLrootlive khácphiêntrước,nguồnthayđổichưaxácđịnh.
  KhôngkhẳngđịnhSQLbấtbiếnqua2phiên/khôngrestore;walkthroughchỉmutationDBcopy8002.

## MVP14.07–08/AUX14.01 — gói nộp và M4, 26/10/2026

- Supersede next14.07/M4chờ ởmốc trước:14.01–08/AUX14.01 đạt,102main+13AUX/110ID.
  Checkpoint14-C3/cổng14/M4 kỹthuật đạt;7taskstage12/5optional chưa nghiệmthu,01.08 giữbỏqua.
  Khôngtựnộp bài/publish; tênnhóm/mãsinhviên/bìa/ngàynộp/địnhdạngbắtbuộc/tậpnói chưa có.
- Đọc docs/demo-script.md/defense-questions.md/submission-checklist.md/audit-phase-14.md vàSUBMISSION.md.
 34Q&A,5mẫu900×1100 tổnghợp ởfixtures/demo (generator/manifest/repeatexact/nooverwrite),khôngtínhdataset.
 05chỉilluminationstripe/planar,không3Dfold. 3hìnhUI/threshold/PDFactual trongdocs/images/demo.
- ZIPallowlist experiments/package_submission.py,manifestSHA từngfile/x-mode/khôngoverwrite;
 output/submission/DocumentScanner-MVP-20261026.zip và.sha256 ignored. Khôngprivatephotos/DB/log/
 deps/dist/coursePDF. Cósource/tests/locks/docs/syntheticfixtures và5CSV-summary13;ảnhriêng/evidence/
 PDFmôn học làlocal-only referencesđãghi rõ. Khôngofflineinstaller/táilậpbenchmark13thiếuảnh.
- CleanZIPcandidate252files→extract/venvnosystem/Python3.12.10/Node24.15/npm11.12.1/pip30pin/npmci/
 imports/health/build41/103frontendtests/typecheck đạt. Full1279passed144.66s-Werror sauđổibasetempngắn.
 Lượtđầu1217pass/62errors143.23s doWindowsmkstemp262char,parentexists;repro112charsuccess.
 Giữlog,khôngskip/sửaassert/storage/registry;READMEghiđườngdẫnngắn. Nguồn/inputZIPcuối bằngbytecodeđãtest.
- Chỉmột dòngtextPipelineViewer sửa “test0”→1doc/split; khôngfrontendlogic/API/schema3/core/preset/
 locks/manifest/nhãn. Buildroot3files bằngbyte cleanbuild. Oldpackaging14v1 giữ,freeze13ce89a90…
 nguyên/checkcũđúngphảitừchốisourceđónggói;khôngretune/retestpixelheldout hoặcoverwritefreeze.
- Browser8002create/import3PNG thật/autodetect2proposal1manual/draft→Colorr1/BWOtsur2→Adaptiver3/
 manualwholeimage+keyboard/Grayr1/PDF3/reloaddebug. Rehearsalpostimport320.984s,PDFready229.785s,
 console0;filechoosertool434.907s ghi riêng,khôngCPUbenchmark/narrationspeech. 34Q&A nêu rõchưađo.
- Samewarp/preparedgraySHA204d08fa…/555901hist;BWchỉthreshold.method khác;Otsu156/Adaptivenull.
 3fullPNG bằngbytecore/rawCannyUIpixelmatch. PDF3imagespixelmatch/full/A4contain/lề5mm/Poppler3pages
 đãxem;page3uniform cốý,Adaptive cònmép/đốm. Process298300Ctrl+Cshutdowncomplete→296284;
 65artifact+detail/SQL/hash bằngnhau,UIreopenBW/hist/100%/console0. QA8002đãdừng,8000/5173giữ.
- docs/submission-verification.json làproofpublic;ignoredmvp14-07-08-verified giữlogs/candidate/runtime/
 PDF/png/rehearsal/pixelchecks/finalverification. SQLroot+197datafiles ởđầulượt này giữhash,
 khôngmutationuserdoc;khôngsuyngượcDBbấtbiếnquacácphiên. Khôngagents/commit/push/deploy/sendexternal.

## Kiểm chứng và giới hạn

- Đọc file liên quan trước khi sửa; giữ thay đổi đúng phạm vi tác vụ.
- Chỉ đánh dấu hoàn thành sau khi có bằng chứng đạt tiêu chí tương ứng.
- Kiểm thử tập trung vào EXIF/alpha, hình học, canvas mapping, revision,
  lưu bền và PDF; không tạo test cho thao tác tạo thư mục hay sửa văn bản đơn giản.
- Ghi số đo thực tế, không dùng số minh họa hay heuristic score làm accuracy.
- Không đưa ảnh cá nhân, DB runtime hoặc bí mật vào Git; không gửi ảnh ra dịch vụ ngoài.
- Lệnh dev/pytest/typecheck/build đã được kiểm chứng, xem README. Từ root dùng
  `backend/.venv/Scripts/python.exe -m pytest -c backend/pyproject.toml backend/tests`;
  từ frontend dùng `npm.cmd test` (Node24), `npm.cmd run typecheck` và `npm.cmd run build`.
  Hiện có lõi ảnh/schema/SQLite/artifact/import/executor, upload/artifactGET/configCAS/renderHTTP và UI nguồn/cornereditor/save-confirm/render/comparison/zoom (1199backend-Werror mốc11;103frontend/typecheck/build/browser và36APIhồiquy AUX11.02;936parity kiểm05–06);
  không suy ra thuật toán scan đã được kiểm chứng. `validate_image` chỉ kiểm tra
  header/cấu trúc; `normalize_image` đã mở lại/load để bắt lỗi decoder trước
  EXIF/alpha/BGR. Không bật LOAD_TRUNCATED_IMAGES hoặc tắt bảo vệ Pillow.
- Môi trường backend đã có Python 3.12.10 64-bit tại `backend/.venv`;
  dependency đã khóa trong `backend/requirements.txt`. Gọi Python trong venv
  để tránh cài vào hệ thống; lệnh setup và bằng chứng ở README/docs/progress.md.
- Tài liệu kế hoạch không chứng minh sản phẩm đã được triển khai.
