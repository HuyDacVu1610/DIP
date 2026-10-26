import type { DebugRead } from '../types/scanner'
import { formatNumber as n, record, scoreParts } from './pipelineData'

const array=(v:unknown)=>Array.isArray(v)?v:[]
const truth=(v:unknown)=>typeof v==='boolean'?(v?'Có':'Không'):'Không có dữ liệu'

export function CandidateMetrics({data}:{data:DebugRead}) {
  const meta=record(data.metadata),result=record(meta.result),selected=record(result.selected),candidate=record(selected.candidate)
  const trials=array(meta.trials).map(record),candidates=array(result.candidates).map(record)
  const parts=scoreParts(selected)
  return <section className="candidate-metrics" aria-label="Mô tả biên và xếp hạng">
    <h4>Mô tả biên và xếp hạng</h4>
    <p className="small">Analysis: {JSON.stringify(meta.analysis_size)??'không có dữ liệu'} px · Trial được chọn: {typeof meta.selected_trial_id==='string'?meta.selected_trial_id:'không có'}
      {' '}· Overlay: {typeof meta.overlay_kind==='string'?meta.overlay_kind:'không có dữ liệu'}</p>
    <p className="small">Trạng thái detector: {String(result.status??'không có dữ liệu')} · cảnh báo: {array(result.warnings).join(', ')||'không có'}.
      Lượt này chưa xác nhận; góc đang chỉnh trên ảnh nguồn có thể đã khác đề xuất.</p>
    <div className="debug-table-scroll"><table><caption>Trial thực đã chạy, không phải các bộ tham số giả định</caption>
      <thead><tr><th>Trial / phương pháp</th><th>Gaussian</th><th>Canny low/high</th><th>Otsu vùng</th><th>Contour xét / tổng</th><th>Lý do loại cả trial</th></tr></thead>
      <tbody>{trials.map((t,i)=><tr key={i}><td>{String(t.trial_id??'thiếu')} · {String(t.method??'thiếu')}</td><td>{n(t.gaussian_kernel,0)}</td><td>{array(t.thresholds).join(' / ')||'không có'}</td><td>{t.otsu_threshold===null?'Không áp dụng':n(t.otsu_threshold)}</td><td>{n(t.considered_contours,0)} / {n(t.total_contours,0)}</td><td>{String(t.rejection_reason??'không có')}</td></tr>)}</tbody>
    </table></div>
    {!Object.keys(selected).length?<p role="status">Không có mô tả ứng viên được chọn trong run này. Không suy chu vi hoặc điểm từ khung kéo tay 5%.</p>:<>
      <dl className="metric-grid">
        <div><dt>Chu vi contour (analysis px)</dt><dd data-metric="perimeter">{n(selected.contour_perimeter_px)}</dd></div>
        <div><dt>Số đỉnh đa giác Q</dt><dd>{n(selected.polygon_vertex_count,0)}</dd></div>
        <div><dt>Q lồi / tự giao</dt><dd>{truth(selected.is_convex)} / {truth(selected.self_intersects)}</dd></div>
        <div><dt>a = A(Q)/(Wa·Ha), đặc trưng vùng</dt><dd data-metric="area">{n(selected.area_ratio,6)}</dd></div>
        <div><dt>f = min(A(C),A(Q))/max(...), khớp diện tích</dt><dd>{n(selected.fit_area_ratio,6)}</dd></div>
        <div><dt>e = Σmᵢ/Σnᵢ, hỗ trợ raw Canny</dt><dd data-metric="support">{n(selected.edge_support,6)}</dd></div>
        <div><dt>b, tỷ lệ mẫu sát khung ảnh</dt><dd>{n(selected.border_penalty,6)}</dd></div>
        <div><dt>S heuristic đã lưu, không phải accuracy</dt><dd data-metric="score">{n(selected.heuristic_score,6)}</dd></div>
      </dl>
      <p className="small">S = clip(0.45a + 0.35e + 0.20f − 0.15b, 0, 1).
        {' '}{parts?`Đóng góp từ các số đã lưu: ${parts.map(v=>v.toFixed(6)).join(' ; ')}.`:'Thiếu thành phần score; không thay bằng 0.'}</p>
      <div className="debug-table-scroll"><table><caption>Bốn cạnh của Q được chọn · độ dài trên analysis, góc đổi hướng (radian)</caption>
        <thead><tr><th>Cạnh</th><th>Độ dài (px)</th><th>Góc đổi hướng (rad)</th><th>mᵢ / nᵢ</th><th>Hỗ trợ cạnh</th></tr></thead>
        <tbody>{[0,1,2,3].map(i=><tr key={i}><td>{i} → {(i+1)%4}</td><td>{n(array(selected.quad_edge_lengths_px)[i])}</td><td>{n(array(selected.quad_turn_angles_rad)[i],6)}</td><td>{n(array(selected.edge_supported_counts)[i],0)} / {n(array(selected.edge_sample_counts)[i],0)}</td><td>{n(array(selected.edge_support_per_side)[i],6)}</td></tr>)}</tbody>
      </table></div>
      <p className="muted small">mᵢ là số mẫu có raw edge cùng trial trong bán kính Euclid ≤2 analysis px;
        nᵢ = max(2, ceil(Lᵢ/2)+1). e là tỷ lệ gộp theo số mẫu, không lấy trung bình bốn tỷ lệ.
        Góc đổi hướng tại đỉnh i không cần bằng π/2 khi chụp phối cảnh.</p>
      <details><summary>Biểu diễn đa giác Q và góc nguồn</summary><pre>{JSON.stringify({trial_id:candidate.trial_id,contour_index:candidate.contour_index,epsilon_ratio:candidate.epsilon_ratio,
        polygon_analysis_px:candidate.polygon_px,corners_source_normalized:candidate.corners},null,2)}</pre></details>
    </>}
    <details><summary>Các ứng viên sau NMS ({candidates.length})</summary><div className="debug-table-scroll"><table>
      <caption>Ứng viên đã qua geometry/NMS; overlay chỉ đánh dấu selected, không phải mọi dòng</caption>
      <thead><tr><th>Trial / contour / ε/P</th><th>Chu vi (px)</th><th>Đỉnh</th><th>a</th><th>f</th><th>e</th><th>b</th><th>S heuristic</th></tr></thead>
      <tbody>{candidates.map((c,i)=>{const q=record(c.candidate);return <tr key={i}><td>{String(q.trial_id??'thiếu')} / {n(q.contour_index,0)} / {n(q.epsilon_ratio)}</td><td>{n(c.contour_perimeter_px)}</td><td>{n(c.polygon_vertex_count,0)}</td><td>{n(c.area_ratio,6)}</td><td>{n(c.fit_area_ratio,6)}</td><td>{n(c.edge_support,6)}</td><td>{n(c.border_penalty,6)}</td><td>{n(c.heuristic_score,6)}</td></tr>})}</tbody>
    </table></div></details>
  </section>
}
