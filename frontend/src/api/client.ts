import type { ConfigRead, DebugRead, DetectionRead, ExportRequest, ExportRead, PageConfig, PageRead, RenderRead, SessionDetail, SessionList, SessionRead } from '../types/scanner'

export class ApiError extends Error {
  readonly code: string
  readonly status: number
  readonly details: Record<string,unknown>
  constructor(code: string, message: string, status = 0, details:Record<string,unknown>={}) {
    super(message)
    this.code = code
    this.status = status
    this.details = details
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  let response: Response
  try {
    response = await fetch(`/api/v1${path}`, { cache: 'no-store', ...options })
  } catch (error) {
    if (options.signal?.aborted) throw error
    throw new ApiError('NETWORK_ERROR', 'Không nhận được phản hồi. Hãy đọc lại trạng thái đã lưu trước khi thử lại.')
  }
  if(response.ok&&response.status===204)return undefined as T
  let body: unknown
  try { body = await response.json() } catch {
    throw new ApiError('INVALID_RESPONSE', 'Máy xử lý chưa sẵn sàng. Hãy thử tải lại.', response.status)
  }
  if (!response.ok) {
    const envelope = body as { error?: { code?: string; message?: string;details?:Record<string,unknown> } }
    throw new ApiError(envelope?.error?.code ?? 'REQUEST_FAILED',
      envelope?.error?.message ?? 'Không thể hoàn tất yêu cầu.', response.status,envelope?.error?.details??{})
  }
  // Backend response models validate DTOs. Mutations are never auto-retried.
  return body as T
}

export const scannerApi = {
  export: (sid:string,body:ExportRequest)=>request<ExportRead>(`/sessions/${encodeURIComponent(sid)}/exports`,{
    method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body),
  }),
  list: (offset = 0, signal?: AbortSignal) => request<SessionList>(`/sessions?limit=20&offset=${offset}`, { signal }),
  create: (title: string) => request<SessionRead>('/sessions', {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ title }),
  }),
  detail: (id: string, signal?: AbortSignal) => request<SessionDetail>(`/sessions/${encodeURIComponent(id)}`, { signal }),
  rename: (id: string, title: string) => request<SessionRead>(`/sessions/${encodeURIComponent(id)}`, {
    method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ title }),
  }),
  order: (id:string,pageIds:string[])=>request<SessionDetail>(`/sessions/${encodeURIComponent(id)}/page-order`,{
    method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify({page_ids:pageIds}),
  }),
  deletePage: (sid:string,pid:string)=>request<void>(`/sessions/${encodeURIComponent(sid)}/pages/${encodeURIComponent(pid)}`,{method:'DELETE'}),
  deleteSession: (sid:string)=>request<void>(`/sessions/${encodeURIComponent(sid)}`,{method:'DELETE'}),
  upload: (id: string, file: File) => {
    const body = new FormData()
    body.append('file', file)
    return request<PageRead>(`/sessions/${encodeURIComponent(id)}/pages`, { method: 'POST', body })
  },
  saveConfig: (sid: string, pid: string, revision: number, config: PageConfig) => request<ConfigRead>(
    `/sessions/${encodeURIComponent(sid)}/pages/${encodeURIComponent(pid)}/config`, {
      method: 'PUT', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ expected_revision: revision, config }),
    }),
  render: (sid: string, pid: string, revision: number) => request<RenderRead>(
    `/sessions/${encodeURIComponent(sid)}/pages/${encodeURIComponent(pid)}/render`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ expected_revision: revision, debug: true }),
    }),
  detect: (sid: string, pid: string) => request<DetectionRead>(
    `/sessions/${encodeURIComponent(sid)}/pages/${encodeURIComponent(pid)}/detect`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ debug: true }),
    }),
  debug: (sid: string, pid: string, kind: 'render' | 'detection', runId: string, signal?: AbortSignal) =>
    request<DebugRead>(debugPath(sid,pid,kind,runId), { signal }),
}

const debugPath = (sid: string, pid: string, kind: 'render' | 'detection', runId: string) =>
  `/sessions/${encodeURIComponent(sid)}/pages/${encodeURIComponent(pid)}/debug?${kind}_run_id=${encodeURIComponent(runId)}`
export const debugUrl = (sid: string, pid: string, kind: 'render' | 'detection', runId: string) =>
  `/api/v1${debugPath(sid,pid,kind,runId)}`

export const artifactUrl = (id: string) => `/api/v1/artifacts/${encodeURIComponent(id)}`
export const errorMessage = (error: unknown) => error instanceof Error ? error.message : 'Không thể hoàn tất yêu cầu.'
