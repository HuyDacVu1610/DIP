import type { DebugRead } from '../types/scanner'

export interface DebugTarget {
  kind: 'render' | 'detection'; runId: string; pageId: string; sourceId: string
  width: number; height: number; revision: number
  sourceHash?: string; fullId?: string; previewId?: string
}
export function record(value: unknown): Record<string, unknown> {
  return value !== null && typeof value === 'object' && !Array.isArray(value) ? value as Record<string, unknown> : {}
}
export const numeric = (value: unknown): value is number => typeof value === 'number' && Number.isFinite(value)
export const formatNumber = (value: unknown, digits = 3) => numeric(value) ? value.toFixed(digits) : 'Không có dữ liệu'
const uuid = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i
const hash = /^[0-9a-f]{64}$/

export function validateDebug(data: DebugRead, target: DebugTarget): DebugRead {
  if(!data||typeof data!=='object')throw new Error('Không có debug hợp lệ của lượt xử lý này.')
  const meta=record(data.metadata), source=record(meta.source), refs=record(meta.artifacts)
  if (data.page_id!==target.pageId || data.kind!==target.kind || data.run_id!==target.runId || meta.run_id!==target.runId
    || source.artifact_id!==target.sourceId || source.width!==target.width || source.height!==target.height
    || typeof source.sha256!=='string' || !hash.test(source.sha256) || (target.sourceHash && source.sha256!==target.sourceHash)
    || (target.kind==='render' && (data.revision!==target.revision || meta.revision!==target.revision))
    || (target.kind==='detection' && (data.revision!==null || source.revision!==target.revision))
    || !['available','not_requested','incomplete'].includes(data.status)
    || typeof data.debug_persisted!=='boolean' || data.debug_persisted!==meta.debug_persisted || !data.artifacts || !data.missing_stages) {
    throw new Error('Debug không khớp trang, nguồn, revision hoặc đúng lượt xử lý đang xem.')
  }
  for (const [name,artifact] of Object.entries(data.artifacts)) {
    const ref=record(refs[name])
    const expectedKind=target.kind==='render'&&name==='full'?'render':target.kind==='render'&&name==='preview'?'preview':'debug'
    if (!uuid.test(artifact.id) || !hash.test(artifact.sha256) || artifact.mime!=='image/png'
      || artifact.kind!==expectedKind || artifact.revision!==target.revision
      || !Number.isInteger(artifact.width) || !Number.isInteger(artifact.height) || artifact.width<1 || artifact.height<1
      || artifact.width>2400 || artifact.height>2400 || ref.id!==artifact.id || ref.sha256!==artifact.sha256
      || ref.width!==artifact.width || ref.height!==artifact.height || name in data.missing_stages) {
      throw new Error('Artifact debug không khớp provenance; không hiển thị ảnh hoặc số thay thế.')
    }
  }
  for (const [name,id] of [['full',target.fullId],['preview',target.previewId]] as [string,string|undefined][]) {
    if (id && refs[name] && record(refs[name]).id!==id) throw new Error('Debug thuộc ảnh render khác trong cùng revision.')
  }
  return data
}

export interface SavedHistogram {
  counts: number[]; width: number; height: number; pixel_count: number
  threshold_method: 'otsu' | 'adaptive_gaussian'; threshold_scope: 'global' | 'local'
  otsu_threshold: number | null; source_png_sha256: string
}
export function readHistogram(data: DebugRead): { histogram: SavedHistogram | null; error?: string } {
  const meta=record(data.metadata)
  if (meta.histogram===null || meta.histogram===undefined) return {histogram:null}
  const h=record(meta.histogram), gray=record(record(meta.artifacts).prepared_gray)
  const counts=h.counts
  if (!Array.isArray(counts) || counts.length!==256 || !counts.every(n=>Number.isSafeInteger(n)&&n>=0)
    || !Number.isInteger(h.width) || !Number.isInteger(h.height) || h.width!==gray.width || h.height!==gray.height
    || !numeric(h.width) || !numeric(h.height) || h.width<2 || h.height<2 || h.width>2400 || h.height>2400
    || h.pixel_count!==h.width*h.height || counts.reduce((a,b)=>a+b,0)!==h.pixel_count
    || h.source_artifact!=='prepared_gray' || h.source_png_sha256!==gray.sha256
    || (h.threshold_method==='otsu' ? h.threshold_scope!=='global' || !numeric(h.otsu_threshold) || h.otsu_threshold<0 || h.otsu_threshold>255
      : h.threshold_method!=='adaptive_gaussian' || h.threshold_scope!=='local' || h.otsu_threshold!==null)
    || h.otsu_threshold!==meta.otsu_threshold) return {histogram:null,error:'Histogram thiếu hoặc không khớp ảnh xám trước threshold; không vẽ dữ liệu thay thế.'}
  return {histogram:h as unknown as SavedHistogram}
}
export function scoreParts(value: Record<string,unknown>): number[] | null {
  const features=[value.area_ratio,value.edge_support,value.fit_area_ratio,value.border_penalty]
  return features.every(numeric) ? features.map((n,i)=>n*[.45,.35,.20,-.15][i]!) : null
}
