import { CornerEditor } from './CornerEditor'
import { ComparisonView } from './ComparisonView'
import { FilterPanel } from './FilterPanel'
import { PipelineViewer } from './PipelineViewer'
import { usePageRender } from '../hooks/usePageRender'
import { sameConfig } from '../hooks/pageRenderState'
import { validateDraftQuad } from './cornerGeometry'
import { useEffect, useRef } from 'react'
import type { PageRead } from '../types/scanner'
import type {EditorAvailability} from './ExportPanel'

export function SourcePreview({ page, onPersisted, locked, onEditingState }: {
  page: PageRead; onPersisted: (saved: PageRead) => void; locked:boolean;
  onEditingState:(state:EditorAvailability)=>void
}) {
  const editorRef = useRef<HTMLDivElement>(null)
  const { persisted, draft, result, detection, detectionRun, busy, needsReload, error, message, actions } = usePageRender(page)
  useEffect(() => { if (!needsReload) onPersisted(persisted) }, [persisted, needsReload, onPersisted])
  const dirty = !sameConfig(draft, persisted.effective_config)
  useEffect(()=>{onEditingState({pageId:page.id,dirty,busy:Boolean(busy),needsReload})},
    [page.id,dirty,busy,needsReload,onEditingState])
  const invalid = !draft.corners || Boolean(validateDraftQuad(draft.corners, page))
  const blocked = locked || Boolean(busy) || needsReload || invalid
  const stale = dirty || !draft.confirmed || needsReload || result?.revision !== persisted.revision
  return <>
    <div className="viewer-heading">
      <div><p className="eyebrow">Ảnh nguồn</p><h2>Trang {page.position + 1}</h2></div>
      <span className="badge">Đã lưu trên máy</span>
    </div>
    <div ref={editorRef}>{draft.corners && <CornerEditor page={page} draft={{ ...draft, corners: draft.corners }} dirty={dirty} disabled={locked || busy === 'reading'}
      onChange={actions.editCorners} onRestore={actions.restoreDraft} />}</div>
    <p className="source-caption">Nguồn PNG sau chuẩn hóa · {page.width} × {page.height} px · Giữ nguyên ảnh gốc</p>
    <FilterPanel config={draft} disabled={locked || Boolean(busy) || needsReload} onChange={actions.editProcessing} />
    <div className="scan-actions" aria-label="Chọn vùng và tạo bản quét">
      <button className="secondary" disabled={locked || Boolean(busy) || needsReload} onClick={() => void actions.detect()}>
        {busy === 'detecting' ? 'Đang nhận diện…' : 'Tự nhận diện vùng'}</button>
      <button className="secondary" disabled={locked || busy === 'reading'} onClick={actions.fullImage}>Dùng toàn ảnh</button>
      <button className="secondary" disabled={locked || busy === 'reading'} onClick={actions.reset}>Đặt lại góc đã lưu</button>
      <button className="secondary" disabled={blocked || !dirty} onClick={() => void actions.save(false)}>Lưu nháp</button>
      <button disabled={blocked} onClick={() => void actions.save(true)}>Xác nhận vùng</button>
      <button disabled={blocked || !draft.confirmed} onClick={() => void actions.render()}>
        {busy === 'rendering' ? 'Đang tạo bản quét…' : 'Tạo bản quét'}</button>
    </div>
    <p role="status" className="scan-status" data-confirmed={draft.confirmed} data-revision={persisted.revision}>
      {busy === 'reading' ? 'Đang đọc cấu hình đã lưu…' : busy === 'saving' ? 'Đang lưu cấu hình…'
        : draft.confirmed ? 'Vùng đã xác nhận.' : 'Vùng chưa xác nhận.'} Phiên bản đã lưu: {persisted.revision}.
      {' '}{message}
    </p>
    {detection && <div className="detection-note" role="status">
      <p>{detection.status === 'manual_required' ? 'Lượt nhận diện cần chọn vùng bằng tay.'
        : draft.confirmed ? 'Đã xác nhận vùng từ đề xuất nhận diện.'
          : detection.status === 'proposed_with_warning' ? 'Đề xuất cần kiểm tra kỹ.' : 'Đề xuất tự động, chưa xác nhận.'}</p>
      <p className="small">Điểm heuristic: {detection.heuristic_score === null ? 'không có' : detection.heuristic_score.toFixed(3)}.
        {' '}Điểm này không phải xác suất đúng hoặc độ chính xác; nền bàn/khung ảnh vẫn có thể bị chọn nhầm.</p>
      <p className="muted small">{detection.algorithm_version} · run {detection.run_id}
        {detection.warnings.length > 0 && ` · Cảnh báo: ${detection.warnings.join(', ')}`}</p>
    </div>}
    {error && <p role="alert" className="error">{error}</p>}
    {needsReload && !busy && <button className="secondary" disabled={locked} onClick={() => void actions.reload()}>Đọc lại cấu hình</button>}
    <PipelineViewer page={page} detection={detectionRun} result={result} stale={stale}/>
    {result ? <ComparisonView key={result.render_artifact_id} page={page} result={result} stale={stale}
      onEdit={() => editorRef.current?.querySelector<HTMLButtonElement>('[data-corner-id="0"]')?.focus()} />
      : <p className="muted small">{persisted.render_revision !== null
      ? 'Trang có metadata bản quét cũ nhưng chưa có run đủ cặp ảnh để mở lại. Tạo bản quét mới để xem kết quả; không ghép ảnh từ lượt khác.'
      : 'Chỉnh bốn góc → xác nhận vùng → tạo bản quét.'}</p>}
  </>
}
