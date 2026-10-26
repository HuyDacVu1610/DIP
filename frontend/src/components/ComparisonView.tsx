import { useId, useState } from 'react'
import { artifactUrl } from '../api/client'
import type { PageRead, RenderRead } from '../types/scanner'

/** Native scroll/zoom of the actual raster; no canvas resampling or processing. */
function Raster({ id, width, height, alt, zoom = 'fit' }: {
  id: string; width: number; height: number; alt: string; zoom?: 'fit' | 1 | 2
}) {
  const [state, setState] = useState<'loading' | 'ready' | 'error'>('loading')
  const [attempt, setAttempt] = useState(0)
  return <div className="comparison-viewport" role="region" aria-label={alt} tabIndex={0}
    aria-busy={state === 'loading'} data-zoom={zoom}>
    {state === 'loading' && <p role="status">Đang tải {alt.toLowerCase()}…</p>}
    <img key={attempt} src={artifactUrl(id)} alt={alt} hidden={state !== 'ready'} draggable={false}
      style={zoom === 'fit' ? undefined : { width: width * zoom, height: height * zoom }}
      onLoad={event => {
        const image = event.currentTarget
        setState(image.naturalWidth === width && image.naturalHeight === height ? 'ready' : 'error')
      }} onError={() => setState('error')} />
    {state === 'error' && <div role="alert"><p>Không tải được {alt.toLowerCase()} đúng kích thước.</p>
      <button className="secondary" onClick={() => { setState('loading'); setAttempt(n => n + 1) }}>Thử lại {alt.toLowerCase()}</button></div>}
  </div>
}

export function ComparisonView({ page, result, stale, onEdit }: {
  page: PageRead; result: RenderRead; stale: boolean; onEdit: () => void
}) {
  const [zoom, setZoom] = useState<'fit' | 1 | 2>('fit')
  const helpId = useId()
  return <section className="scan-result" aria-label="So sánh nguồn và bản quét" data-stale={stale}>
    <div className="comparison-heading"><h3>{stale ? 'Kết quả cũ — chưa áp dụng thay đổi hiện tại' : 'Bản quét đã tạo'}</h3>
      <button className="secondary" onClick={onEdit}>Quay lại chỉnh góc</button></div>
    <p className="muted small">Phiên bản {result.revision} · {result.width} × {result.height} px · Bản quét đầy đủ</p>
    <div className="scan-actions" role="group" aria-label="Phóng to bản quét" aria-describedby={helpId}>
      <button className="secondary" aria-pressed={zoom === 'fit'} onClick={() => setZoom('fit')}>Vừa khung</button>
      <button className="secondary" aria-pressed={zoom === 1} onClick={() => setZoom(1)}>100%</button>
      <button className="secondary" aria-pressed={zoom === 2} onClick={() => setZoom(2)}>200%</button>
    </div>
    <p id={helpId} className="muted small">100%: mỗi pixel ảnh tương ứng một pixel CSS. Dùng thanh cuộn hoặc phím mũi tên trong khung bản quét để xem chữ.</p>
    <div className="comparison-grid">
      <figure><figcaption><strong>Ảnh nguồn sau chuẩn hóa</strong><span>{page.width} × {page.height} px · Giữ nguyên nguồn</span></figcaption>
        <Raster key={page.normalized_artifact_id} id={page.normalized_artifact_id} width={page.width} height={page.height}
          alt={`Ảnh nguồn đối chiếu trang ${page.position + 1}`} /></figure>
      <figure><figcaption><strong>Bản quét đầy đủ{stale ? ' (cũ)' : ''}</strong><span>Phiên bản {result.revision} · {result.width} × {result.height} px</span></figcaption>
        <Raster key={result.render_artifact_id} id={result.render_artifact_id} width={result.width} height={result.height}
          alt={`Ảnh bản quét đầy đủ trang ${page.position + 1}, phiên bản ${result.revision}`} zoom={zoom} /></figure>
    </div>
    {result.warnings.length > 0 && <p role="status">Cảnh báo: {result.warnings.join(', ')}</p>}
  </section>
}
