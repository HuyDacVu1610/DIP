import type { DebugRead } from '../types/scanner'
import { readHistogram } from './pipelineData'

export function HistogramView({ data }: {data:DebugRead}) {
  const {histogram:h,error}=readHistogram(data)
  if(error)return <p role="alert" className="error">{error}</p>
  if(!h)return <p className="muted">Không có histogram trước threshold ở lượt này: Color/Gray không phân ngưỡng,
    hoặc lượt chạy chưa lưu debug. Không dùng histogram ảnh kết quả thay thế.</p>
  const max=Math.max(...h.counts)
  return <section className="histogram" aria-label="Histogram trước threshold">
    <h4>Histogram trước threshold</h4>
    <p className="small">{h.width} × {h.height} px · Tổng {h.pixel_count.toLocaleString('vi-VN')} pixel · 256 mức xám · trước xoay</p>
    <svg viewBox="0 0 560 190" role="img" aria-label={`Histogram 256 số đếm đã lưu, tổng ${h.pixel_count} pixel. ${h.threshold_scope==='global'?'Otsu '+h.otsu_threshold:'Adaptive không có ngưỡng toàn ảnh'}`}>
      <line x1="36" x2="548" y1="156" y2="156" stroke="currentColor" />
      {h.counts.map((count,i)=><rect key={i} x={36+i*2} y={156-count/max*140} width="2" height={count/max*140} className="hist-bar"><title>{i}: {count} pixel</title></rect>)}
      {h.otsu_threshold!==null&&<line data-otsu={h.otsu_threshold} x1={37+h.otsu_threshold*2} x2={37+h.otsu_threshold*2} y1="12" y2="156" className="hist-threshold" />}
      <text x="36" y="178">0</text><text x="518" y="178">255</text><text x="36" y="12">{max} pixel (đỉnh)</text>
    </svg>
    <p>{h.threshold_scope==='global'?`Otsu: ngưỡng toàn ảnh thực t = ${h.otsu_threshold}. Nét đứt đánh dấu t.`
      :'Adaptive Gaussian: ngưỡng cục bộ thay đổi theo vị trí; không có một ngưỡng t chung.'}</p>
    <p className="muted small">Các cột là số pixel ở từng mức xám của prepared_gray đã lưu, sau lọc/CLAHE và trước threshold.
      Histogram toàn ảnh không phải bản đồ ngưỡng Adaptive, không đo độ chính xác nhận diện giấy.</p>
    <details><summary>Đối chiếu 256 số đếm</summary><div className="debug-table-scroll"><table><caption>Số đếm gốc từ JSON của cùng run</caption>
      <thead><tr><th>Mức xám</th><th>Số pixel</th></tr></thead><tbody>{h.counts.map((count,i)=><tr key={i}><td>{i}</td><td>{count}</td></tr>)}</tbody>
    </table></div></details>
    <p className="hash-text small">SHA-256 prepared_gray: {h.source_png_sha256}</p>
  </section>
}
