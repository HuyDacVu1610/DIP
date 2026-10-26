export interface SessionRead {
  id: string
  title: string
  created_at: string
  updated_at: string
}

export type Point = [number, number]
export type Quad = [Point, Point, Point, Point]

export interface PageConfig {
  mode: 'color' | 'gray' | 'bw'
  corners: Quad | null
  confirmed: boolean
  rotation: 0 | 90 | 180 | 270
  denoise: { method: 'none' | 'median' | 'gaussian'; kernel: number }
  contrast: { method: 'none' | 'clahe'; clip_limit: number; tile_grid: [number, number] }
  threshold: { method: 'otsu' | 'adaptive_gaussian'; block_size: number; c: number }
  geometry: { aspect_policy: 'estimated'; max_long_edge: number }
}

export interface PageRead {
  id: string
  session_id: string
  position: number
  width: number
  height: number
  original_artifact_id: string
  normalized_artifact_id: string
  thumbnail_artifact_id: string
  revision: number
  render_revision: number | null
  latest_render?: RenderRead | null
  latest_detection?: DetectionRead | null
  effective_config: PageConfig
  created_at: string
  updated_at: string
}

export interface SessionDetail extends SessionRead { pages: PageRead[] }
export interface ExportRequest {
  pages: {page_id:string;revision:number}[]
  format:'pdf'|'png'|'jpg'
  paper_size:'a4'
  orientation:'auto'|'portrait'|'landscape'
  margin_mm:number
  image_encoding:'png'|'jpeg'
}
export interface ExportRead {
  id:string;session_id:string;artifact_id:string;format:ExportRequest['format']
  pages:ExportRequest['pages'];created_at:string
}
export interface SessionList { items: SessionRead[]; limit: number; offset: number; total: number }

export interface ConfigRead {
  page_id: string
  revision: number
  effective_config: PageConfig
  inactive_fields: string[]
}

export interface RenderRead {
  page_id: string
  revision: number
  render_artifact_id: string
  preview_artifact_id: string
  render_run_id?: string | null
  width: number
  height: number
  warnings: string[]
  timings_ms: Record<string, number>
}

export interface DebugArtifact {
  id: string; kind: 'render' | 'preview' | 'debug'; revision: number
  mime: 'image/png'; byte_size: number; sha256: string
  width: number; height: number; created_at: string
}
export interface DebugRead {
  page_id: string; kind: 'render' | 'detection'; current_revision: number
  revision: number | null; run_id: string | null; created_at: string | null
  status: 'available' | 'not_requested' | 'not_recorded' | 'incomplete'
  debug_persisted: boolean; metadata: Record<string, unknown> | null
  artifacts: Record<string, DebugArtifact>
  missing_stages: Record<string, 'not_found' | 'invalid_metadata' | 'file_unavailable'>
}

export interface DetectionRead {
  page_id: string
  run_id: string
  source_artifact_id: string
  source_revision: number
  source_sha256: string
  source_width: number
  source_height: number
  status: 'proposed' | 'proposed_with_warning' | 'manual_required'
  corners: Quad | null
  confirmed: false
  heuristic_score: number | null
  algorithm_version: string
  selected_trial_id: string | null
  stage_artifacts: Record<string, string>
  warnings: string[]
  timings_ms: Record<string, number>
}
