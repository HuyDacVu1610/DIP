import { artifactUrl } from '../api/client'
import type { PageRead } from '../types/scanner'

export function PageList({ pages, selected, onSelect, disabled, onMove, onDelete }: {
  pages: PageRead[]; selected: string | null; onSelect: (id: string) => void
  disabled:boolean; onMove:(id:string,direction:-1|1)=>void; onDelete:(id:string)=>void
}) {
  return <ol className="page-list" aria-label="Các trang tài liệu">
    {pages.map(page => <li key={page.id}>
      <button className="page-button" aria-pressed={selected === page.id} onClick={() => onSelect(page.id)}>
        <span className="thumbnail"><img src={artifactUrl(page.thumbnail_artifact_id)} alt="" loading="lazy" /></span>
        <span><strong>Trang {page.position + 1}</strong><small>{page.width} × {page.height} px</small></span>
      </button>
      <small className="page-state">{page.effective_config.mode.toUpperCase()} · {page.effective_config.rotation}° · {page.render_revision===null?'Chưa quét':`Đã quét r${page.render_revision}`}</small>
      {page.revision===0&&page.effective_config.corners===null&&page.latest_detection?.source_revision===0&&
        <small className="page-state">{page.latest_detection.status==='manual_required'?'Cần chỉnh vùng tay'
          :page.latest_detection.status==='proposed_with_warning'?'Vùng có cảnh báo · cần kiểm tra':'Đã nhận diện · chờ kiểm tra'}</small>}
      <div className="page-actions">
        <button className="secondary" disabled={disabled||page===pages[0]} aria-label={`Đưa trang ${page.position+1} lên`} onClick={()=>onMove(page.id,-1)}>↑</button>
        <button className="secondary" disabled={disabled||page===pages[pages.length-1]} aria-label={`Đưa trang ${page.position+1} xuống`} onClick={()=>onMove(page.id,1)}>↓</button>
        <button className="secondary" disabled={disabled} aria-label={`Xóa trang ${page.position+1}`} onClick={()=>onDelete(page.id)}>Xóa</button>
      </div>
    </li>)}
  </ol>
}
