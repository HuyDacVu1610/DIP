import { useCallback, useEffect, useId, useRef, useState } from 'react'
import type { KeyboardEvent, PointerEvent } from 'react'
import { artifactUrl } from '../api/client'
import type { PageConfig, PageRead, Point, Quad } from '../types/scanner'
import { clientToCanvas, createContainTransform, getCanvasBackingSize, hitTestCorner,
  moveCorner, normalizedToCanvas, validateDraftQuad } from './cornerGeometry'
import type { CornerId, Size } from './cornerGeometry'

interface Drag { pointerId: number; corner: CornerId; before: PageConfig; offset: Point; start: Point; moved: boolean }

export function CornerEditor({ page, draft, dirty, disabled, onChange, onRestore }: {
  page: PageRead; draft: PageConfig & { corners: Quad }; dirty: boolean
  disabled: boolean
  onChange: (corners: Quad) => void; onRestore: (config: PageConfig) => void
}) {
  const corners = draft.corners
  const [box, setBox] = useState<Size>({ width: 0, height: 0 })
  const [dpr, setDpr] = useState(window.devicePixelRatio || 1)
  const [imageState, setImageState] = useState<'loading' | 'ready' | 'error'>('loading')
  const [attempt, setAttempt] = useState(0)
  const [dragging, setDragging] = useState<CornerId | null>(null)
  const draftRef = useRef(corners)
  draftRef.current = corners
  const configRef = useRef(draft)
  configRef.current = draft
  const restoreRef = useRef(onRestore)
  restoreRef.current = onRestore
  const dragRef = useRef<Drag | null>(null)
  const handlesRef = useRef<(HTMLButtonElement | null)[]>([])
  const stageRef = useRef<HTMLDivElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const helpId = useId()
  const issue = validateDraftQuad(corners, page)
  const transform = box.width > 0 && box.height > 0
    ? createContainTransform(page, box) : null

  const cancelDrag = useCallback(() => {
    const drag = dragRef.current
    if (!drag) return
    dragRef.current = null
    draftRef.current = drag.before.corners!
    restoreRef.current(drag.before)
    setDragging(null)
    if (stageRef.current?.hasPointerCapture(drag.pointerId)) stageRef.current.releasePointerCapture(drag.pointerId)
  }, [])

  useEffect(() => { cancelDrag() }, [box.width, box.height, dpr, cancelDrag])
  useEffect(() => {
    window.addEventListener('blur', cancelDrag)
    return () => {
      window.removeEventListener('blur', cancelDrag)
      const drag = dragRef.current
      dragRef.current = null
      if (drag && stageRef.current?.hasPointerCapture(drag.pointerId)) stageRef.current.releasePointerCapture(drag.pointerId)
    }
  }, [cancelDrag])

  function updateDraft(next: Quad) {
    if (next.every((p, i) => p[0] === draftRef.current[i][0] && p[1] === draftRef.current[i][1])) return
    draftRef.current = next
    onChange(next)
  }

  function pointerDown(event: PointerEvent<HTMLDivElement>) {
    if (disabled || !transform || imageState !== 'ready' || !event.isPrimary || event.button !== 0 || dragRef.current) return
    const point = clientToCanvas([event.clientX, event.clientY], event.currentTarget.getBoundingClientRect(), transform)
    const corner = hitTestCorner(point, draftRef.current, transform)
    if (corner === null) return // Empty source/letterbox never jumps a handle.
    const center = normalizedToCanvas(draftRef.current[corner], transform)
    event.preventDefault()
    event.currentTarget.setPointerCapture(event.pointerId)
    dragRef.current = { pointerId: event.pointerId, corner, before: structuredClone(configRef.current),
      offset: [center[0] - point[0], center[1] - point[1]], start: point, moved: false }
    handlesRef.current[corner]?.focus({ preventScroll: true })
    setDragging(corner)
  }

  function pointerMove(event: PointerEvent<HTMLDivElement>) {
    const drag = dragRef.current
    if (!drag || drag.pointerId !== event.pointerId || !transform) return
    const [x, y] = clientToCanvas([event.clientX, event.clientY], event.currentTarget.getBoundingClientRect(), transform)
    if (!drag.moved && Math.hypot(x - drag.start[0], y - drag.start[1]) <= 1e-6) return
    drag.moved = true
    updateDraft(moveCorner(draftRef.current, drag.corner, [x + drag.offset[0], y + drag.offset[1]], transform))
  }

  function pointerUp(event: PointerEvent<HTMLDivElement>) {
    if (dragRef.current?.pointerId !== event.pointerId) return
    pointerMove(event)
    dragRef.current = null
    setDragging(null)
    if (event.currentTarget.hasPointerCapture(event.pointerId)) event.currentTarget.releasePointerCapture(event.pointerId)
  }

  function keyboardMove(event: KeyboardEvent<HTMLButtonElement>, id: CornerId) {
    const delta: Record<string, Point> = { ArrowLeft: [-1, 0], ArrowRight: [1, 0], ArrowUp: [0, -1], ArrowDown: [0, 1] }
    if (disabled || !delta[event.key] || !transform) return
    event.preventDefault()
    if (dragRef.current) return
    const [x, y] = normalizedToCanvas(draftRef.current[id], transform)
    const step = event.shiftKey ? 10 : 1
    updateDraft(moveCorner(draftRef.current, id, [x + step * delta[event.key][0], y + step * delta[event.key][1]], transform))
  }

  useEffect(() => {
    const stage = stageRef.current
    if (!stage) return
    const observer = new ResizeObserver(([entry]) => {
      setBox({ width: entry.contentRect.width, height: entry.contentRect.height })
    })
    observer.observe(stage)
    const updateDpr = () => setDpr(window.devicePixelRatio || 1)
    const resolution = window.matchMedia(`(resolution: ${dpr}dppx)`)
    resolution.addEventListener('change', updateDpr)
    window.addEventListener('resize', updateDpr)
    return () => {
      observer.disconnect()
      resolution.removeEventListener('change', updateDpr)
      window.removeEventListener('resize', updateDpr)
    }
  }, [dpr])

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas || !transform || imageState !== 'ready') return
    const backing = getCanvasBackingSize(box, dpr)
    canvas.width = backing.width
    canvas.height = backing.height
    const ctx = canvas.getContext('2d')
    if (!ctx) return
    ctx.setTransform(backing.scaleX, 0, 0, backing.scaleY, 0, 0)
    const points = corners.map(point => normalizedToCanvas(point, transform))
    const mask = new Path2D()
    mask.rect(transform.offsetX, transform.offsetY, transform.scale * page.width, transform.scale * page.height)
    mask.moveTo(...points[0])
    points.slice(1).forEach(point => mask.lineTo(...point))
    mask.closePath()
    ctx.fillStyle = 'rgba(12, 25, 20, .55)'
    ctx.fill(mask, 'evenodd')
    ctx.beginPath()
    ctx.moveTo(...points[0])
    points.slice(1).forEach(point => ctx.lineTo(...point))
    ctx.closePath()
    ctx.strokeStyle = getComputedStyle(canvas).getPropertyValue(issue ? '--error' : '--accent').trim()
    ctx.lineWidth = 2
    ctx.stroke()
  }, [box, dpr, corners, imageState, page.width, page.height, issue?.code])

  return <>
    <div className="corner-frame" aria-busy={imageState === 'loading'}>
      <div className="corner-stage" ref={stageRef} data-dragging={dragging !== null}
        onPointerDown={pointerDown} onPointerMove={pointerMove} onPointerUp={pointerUp}
        onPointerCancel={event => { if (dragRef.current?.pointerId === event.pointerId) cancelDrag() }}
        onLostPointerCapture={event => { if (dragRef.current?.pointerId === event.pointerId) cancelDrag() }}
        onBlur={event => { if (!event.currentTarget.contains(event.relatedTarget)) cancelDrag() }}
        onKeyDown={event => { if (event.key === 'Escape' && dragRef.current) { event.preventDefault(); cancelDrag() } }}>
        <img key={attempt} src={artifactUrl(page.normalized_artifact_id)} alt={`Ảnh nguồn trang ${page.position + 1}`}
          draggable={false} hidden={imageState !== 'ready'} onLoad={event => {
            const image = event.currentTarget
            setImageState(image.naturalWidth === page.width && image.naturalHeight === page.height ? 'ready' : 'error')
          }} onError={() => setImageState('error')} />
        {imageState === 'loading' && <p role="status">Đang tải ảnh nguồn…</p>}
        {imageState === 'error' && <div role="alert"><p>Không tải được ảnh nguồn đúng kích thước.</p>
          <button className="secondary" onClick={() => { setImageState('loading'); setAttempt(value => value + 1) }}>Thử lại ảnh</button></div>}
        <canvas ref={canvasRef} aria-hidden="true" hidden={imageState !== 'ready'} />
        {imageState === 'ready' && transform && corners.map((point, id) => {
          const [left, top] = normalizedToCanvas(point, transform)
          return <button key={id} type="button" className="corner-handle" data-corner-id={id} disabled={disabled}
            ref={node => { handlesRef.current[id] = node }} onKeyDown={event => keyboardMove(event, id as CornerId)}
            data-u={point[0]} data-v={point[1]} style={{ left, top }} aria-label={`Góc ${id}`}
            aria-describedby={helpId}><span>{id}</span></button>
        })}
      </div>
    </div>
    <p role="status" data-quad-code={issue?.code ?? 'VALID'} className={issue ? 'corner-status error' : 'corner-status'}>
      {issue ? issue.message : 'Hình học vùng hợp lệ.'} {dirty ? 'Bản nháp khác cấu hình đã lưu.'
        : 'Đang dùng góc đã lưu.'}
    </p>
    <p id={helpId} className="muted small corner-help">Kéo các góc 0–3 bằng chuột hoặc cảm ứng. Dùng phím mũi tên để dịch góc, Shift để dịch nhanh; Escape hủy lần kéo.
      {' '}Khung mặc định 5% là vùng thử. Nút “Tự nhận diện vùng” đưa góc đề xuất vào nháp; hãy kiểm tra theo mép giấy trước khi xác nhận.
      {' '}Sửa góc sẽ bỏ xác nhận. Chuyển trang hoặc tải lại sẽ bỏ thay đổi chưa lưu.</p>
  </>
}
