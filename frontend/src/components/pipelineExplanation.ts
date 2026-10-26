import { formatNumber as n, record } from './pipelineData'

export const stageLabel:Record<string,string>={analysis:'Ảnh phân tích',gray:'Xám cho detection',blurred:'Gaussian cho detection',contour_overlay:'Contour và đa giác được chọn',
  warp:'Trang sau biến đổi phối cảnh',filtered_bgr:'Sau lọc nhiễu',prepared_gray:'Xám sau tương phản, trước threshold',before_rotation:'Kết quả trước xoay',full:'Bản quét đầy đủ',preview:'Ảnh xem trước'}
export function explainStage(name:string,metadata:Record<string,unknown>,kind:'render'|'detection'):string {
  if(kind==='detection') {
    const trials=Array.isArray(metadata.trials)?metadata.trials.map(record):[]
    const trial=trials.find(t=>typeof t.trial_id==='string'&&name.startsWith(t.trial_id+'_'))
    if(name==='analysis')return 'Thu nhỏ nguồn sau EXIF về cạnh dài tối đa 1200 bằng INTER_AREA, không phóng lớn. Chỉ dùng để tìm trang; warp vẫn lấy nguồn đầy đủ.'
    if(name==='gray')return 'BGR → gray tạo mức sáng để tìm gradient. Màu của giấy và bàn có thể mất phân biệt sau bước này; gray không tự nhận biết đâu là giấy.'
    if(name==='blurred')return `Gaussian ${n(trials[0]?.gaussian_kernel,0)} × ${n(trials[0]?.gaussian_kernel,0)}, sigma=0, BORDER_REFLECT_101 giảm nhiễu trước Canny; quá mờ có thể làm mất mép yếu.`
    if(name==='contour_overlay')return 'Contour xanh là đường bao, Q đỏ là đa giác xấp xỉ của selected. Overlay ở hệ analysis; có thể chỉ là diagnostic dưới ngưỡng đề xuất. Chưa phải góc người dùng xác nhận.'
    if(trial&&name.endsWith('_region_mask'))return `Nhánh vùng dự phòng: Otsu actual t=${n(trial.otsu_threshold)} trên ảnh analysis đã blur, rồi RETR_EXTERNAL lấy contour ngoài. Chỉ chạy khi ba Canny không sinh quad hợp lệ. Bàn cùng sáng có thể bị nhập vào vùng giấy.`
    if(trial&&name.endsWith('_edges'))return `Raw Canny low/high ${Array.isArray(trial.thresholds)?trial.thresholds.join('/'):'không có dữ liệu'}, aperture3/L2. Gradient → non-maximum suppression → ngưỡng kép và liên kết hysteresis. Đây là map trước closing dùng đo hỗ trợ cạnh; nhánh vùng cũng dùng raw support này, không lấy mask làm edge.`
    if(trial&&name.endsWith('_closed'))return 'Closing = dilation rồi erosion, kernel3×3 một lần trên biên trắng giúp nối hở nhỏ. Nối quá mạnh có thể ghép chữ/bóng/nền; không bảo đảm tạo đúng vùng giấy.'
  } else {
    const config=record(metadata.effective_config),denoise=record(config.denoise),contrast=record(config.contrast),threshold=record(config.threshold)
    if(name==='warp')return 'Homography dùng bốn góc nguồn theo chu kỳ để đưa tứ giác phối cảnh thành trang chữ nhật. INTER_LINEAR/BORDER_REPLICATE, không dùng analysis/thumbnail. Cắt bounding box chỉ giữ độ xiên; homography không làm phẳng giấy cong/nhàu 3D.'
    if(name==='filtered_bgr')return `Lọc ${String(denoise.method??'không có dữ liệu')}, kernel ${n(denoise.kernel,0)}. None sao chép; Median có thể xóa nét/dấu nhỏ, Gaussian làm mềm nét. Mọi lần render bắt đầu từ nguồn/warp, không lọc chồng ảnh kết quả cũ.`
    if(name==='prepared_gray')return `Gray sau lọc và contrast=${String(contrast.method??'không có dữ liệu')}, CLAHE clip=${n(contrast.clip_limit)}, lưới8×8 ô khi active. CLAHE giới hạn khuếch đại histogram cục bộ; có thể tăng cả nhiễu. Đây là đầu vào threshold thật, trước xoay; Color không có stage này.`
    if(name==='before_rotation')return config.mode==='bw'?(threshold.method==='otsu'
      ?`Otsu chọn một ngưỡng toàn ảnh thực t=${n(metadata.otsu_threshold)} để cực đại phương sai giữa hai lớp. THRESH_BINARY: ≤t thành đen, >t thành trắng. Bóng mạnh có thể thành mảng đen.`
      :`Adaptive Gaussian dùng trung bình có trọng số lân cận block=${n(threshold.block_size,0)} trừ C=${n(threshold.c,0)}. Không có một t toàn ảnh; block lẻ3–151 phải vừa warp. Có thể giữ ô ly hoặc đứt nét.`)
      :'Color giữ màu sau lọc; Gray chuyển mức sáng và CLAHE nếu bật. Chưa phân ngưỡng, chưa xoay ở stage này.'
    if(name==='full')return `Kết quả cuối sau xoay ${n(config.rotation,0)}° theo chiều kim đồng hồ, PNG đầy đủ. Chữ và highlight có thể mất sắc độ trong BW; đây là ảnh dùng xuất/zoom, không phải overlay.`
    if(name==='preview')return 'Ảnh xem trước thu từ đúng full render bằng INTER_AREA, cạnh dài tối đa1000, không phóng lớn. Preview BW có thể xuất hiện mức xám do resize; full BW vẫn chỉ0/255.'
  }
  return 'Stage của đúng lượt đã lưu. Đối chiếu tên trial, hash và JSON; không dựng ảnh trung gian khi thiếu dữ liệu.'
}
