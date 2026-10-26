import type { ConfigRead, DetectionRead, PageConfig, PageRead, Quad, RenderRead, SessionDetail } from '../types/scanner'
import { validateDraftQuad } from '../components/cornerGeometry.ts'
import {assertDetectionProposal} from '../components/detectionProposal.ts'

interface PageApi {
  detail: (sid: string) => Promise<SessionDetail>
  saveConfig: (sid: string, pid: string, revision: number, config: PageConfig) => Promise<ConfigRead>
  render: (sid: string, pid: string, revision: number) => Promise<RenderRead>
  detect: (sid: string, pid: string) => Promise<DetectionRead>
}
interface EditorState {
  persisted: PageRead
  draft: PageConfig
  result: RenderRead | null
  detection: DetectionRead | null
  detectionRun: DetectionRead | null
  busy: 'reading' | 'saving' | 'rendering' | 'detecting' | null
  needsReload: boolean
  error: string
  message: string
}
export const sameConfig = (a: PageConfig, b: PageConfig) => JSON.stringify(a) === JSON.stringify(b)
function editable(config: PageConfig): PageConfig {
  return { ...structuredClone(config), corners: structuredClone(config.corners)
    ?? [[.05,.05],[.95,.05],[.95,.95],[.05,.95]], confirmed: config.corners !== null && config.confirmed }
}

/** One mounted page owns one store. HTTP cancellation cannot undo a committed mutation. */
export function createPageRender(page: PageRead, api: PageApi) {
  let state: EditorState = { persisted: structuredClone(page), draft: editable(page.effective_config),
    result: null, detection: null, detectionRun: null, busy: null, needsReload: true, error: '', message: '' }
  let active = false, operation = 0, edits = 0, loaded = false
  const listeners = new Set<() => void>()
  const patch = (next: Partial<EditorState>) => { state = { ...state, ...next }; listeners.forEach(fn => fn()) }
  const current = (id: number) => active && operation === id
  const canWrite = () => active && !state.busy && !state.needsReload
  const valid = () => state.draft.corners !== null && !validateDraftQuad(state.draft.corners, page)
  function replaceDraft(draft: PageConfig) {
    edits++
    patch({ draft: structuredClone(draft), detection: null, message: '' })
  }
  async function reload() {
    if (!active || (state.busy && state.busy !== 'reading')) return
    const id = ++operation
    patch({ busy: 'reading', error: '' })
    try {
      const detail = await api.detail(page.session_id)
      if (!current(id)) return
      const fresh = detail.pages.find(p => p.id === page.id)
      if (detail.id !== page.session_id || !fresh || fresh.session_id !== page.session_id
        || fresh.normalized_artifact_id !== page.normalized_artifact_id
        || fresh.width !== page.width || fresh.height !== page.height) throw new Error('Thông tin trang không khớp. Hãy tải lại tài liệu.')
      const restored=fresh.latest_render??null,diagnostic=fresh.latest_detection??null
      if(restored&&(restored.page_id!==page.id||restored.revision>fresh.revision||!restored.render_run_id
          ||restored.width<2||restored.height<2||restored.width>2400||restored.height>2400))throw new Error('Bản quét đã lưu không khớp trang/revision.')
      if(diagnostic&&(diagnostic.page_id!==page.id||diagnostic.source_artifact_id!==page.normalized_artifact_id
          ||diagnostic.source_width!==page.width||diagnostic.source_height!==page.height
          ||diagnostic.source_revision>fresh.revision||diagnostic.confirmed!==false))throw new Error('Nhận diện đã lưu không khớp nguồn.')
      let initial=editable(fresh.effective_config),proposal:DetectionRead|null=null
      // Adopt once for untouched imports; saved manual corners and live drafts always win.
      if(!loaded&&fresh.revision===0&&fresh.effective_config.corners===null&&!fresh.effective_config.confirmed
          &&diagnostic?.source_revision===0){
        assertDetectionProposal(diagnostic,fresh)
        initial={...initial,corners:structuredClone(diagnostic.corners)??initial.corners,confirmed:false}
        proposal=diagnostic
      }
      patch({ persisted: structuredClone(fresh), needsReload: false,
        draft: loaded ? { ...state.draft, confirmed: false } : initial, detection: proposal,
        result:restored,detectionRun:diagnostic,
        message: loaded ? 'Đã đọc lại cấu hình đã lưu. Giữ góc nháp; cần xác nhận lại.'
          :proposal?'Đã nhận diện khi nhập ảnh. Kiểm tra vùng trước khi xác nhận.':'' })
      loaded = true
      edits++
    } catch (error) {
      if (current(id)) patch({ needsReload: true, error: error instanceof Error ? error.message : 'Không đọc được cấu hình.' })
    } finally { if (current(id)) patch({ busy: null }) }
  }
  async function detect() {
    if (!canWrite()) return
    const id = ++operation, version = edits
    patch({ busy: 'detecting', error: '', detection: null, detectionRun: null, message: 'Đang tìm vùng tài liệu… Bạn vẫn có thể chỉnh góc tay.' })
    try {
      const result = await api.detect(page.session_id, page.id)
      if (!current(id)) return
      if (edits !== version) { patch({ message: 'Bản nháp đã được chỉnh; bỏ qua đề xuất nhận diện trả về muộn.' }); return }
      assertDetectionProposal(result,page)
      if (result.source_revision !== state.persisted.revision) {
        patch({ needsReload: true })
        throw new Error('Cấu hình đã lưu đã thay đổi. Hãy đọc lại cấu hình trước khi nhận đề xuất.')
      }
      edits++
      patch({ draft: { ...state.draft, corners: structuredClone(result.corners)
          ?? [[.05,.05],[.95,.05],[.95,.95],[.05,.95]], confirmed: false }, detection: result, detectionRun: result,
        message: result.status === 'manual_required' ? 'Chưa tìm được vùng phù hợp. Dùng khung thử cách mép 5% để kéo tay; chưa xác nhận.'
          : 'Đã đưa đề xuất vào bản nháp. Kiểm tra và chỉnh bốn góc theo mép giấy trước khi xác nhận.' })
    } catch (error) {
      if (current(id)) patch({ error: error instanceof Error ? error.message : 'Không thể nhận diện.',
        message: state.needsReload ? 'Giữ nguyên vùng đang có. Hãy đọc lại cấu hình để đối soát trước khi thử tiếp.'
          : 'Giữ nguyên vùng đang có. Bạn có thể thử lại nhận diện hoặc chỉnh tay.' })
    } finally { if (current(id)) patch({ busy: null }) }
  }
  async function write(confirm: boolean, render: boolean) {
    if (!canWrite() || !valid() || (render && !state.draft.confirmed)) return
    const id = ++operation, version = edits
    const config = structuredClone({ ...state.draft, confirmed: confirm })
    const revision = state.persisted.revision
    patch({ busy: 'saving', error: '', message: '' })
    try {
      // Send the complete config, including inactive fields. The PUT is CAS, even for a no-op.
      const saved = await api.saveConfig(page.session_id, page.id, revision, config)
      if (!current(id)) return
      const expected = revision + (sameConfig(config, state.persisted.effective_config) ? 0 : 1)
      if (saved.page_id !== page.id || saved.revision !== expected || !sameConfig(saved.effective_config, config)) {
        throw new Error('Phản hồi cấu hình không khớp trang hoặc phiên bản. Cần đọc lại cấu hình.')
      }
      patch({ persisted: { ...state.persisted, revision: saved.revision, effective_config: structuredClone(saved.effective_config) },
        ...(edits === version ? { draft: structuredClone(saved.effective_config) } : {}),
        message: edits === version ? (confirm ? 'Đã xác nhận và lưu vùng cắt.' : 'Đã lưu bản nháp chưa xác nhận.')
          : 'Đã lưu cấu hình trước đó; thay đổi mới vẫn đang ở bản nháp.' })
      if (!render || edits !== version) return
      patch({ busy: 'rendering', message: 'Đang tạo bản quét từ ảnh nguồn đầy đủ…' })
      const result = await api.render(page.session_id, page.id, saved.revision)
      if (!current(id)) return
      if (result.page_id !== page.id || result.revision !== saved.revision) throw new Error('Kết quả không khớp trang hoặc phiên bản. Cần đọc lại cấu hình.')
      if (edits !== version) { patch({ message: 'Cấu hình đã thay đổi. Kết quả trả về của cấu hình trước không được hiển thị.' }); return }
      patch({ result, persisted: { ...state.persisted, render_revision: result.revision }, message: 'Đã tạo bản quét.' })
    } catch (error) {
      if (current(id)) patch({ needsReload: true, error: error instanceof Error ? error.message : 'Không thể lưu hoặc tạo bản quét.',
        message: 'Cần đọc lại cấu hình trước khi thử tiếp. Kết quả lần trước được giữ lại nếu có.' })
    } finally { if (current(id)) patch({ busy: null }) }
  }
  return {
    getSnapshot: () => state,
    subscribe: (listener: () => void) => { listeners.add(listener); return () => { listeners.delete(listener) } },
    connect: () => { active = true },
    disconnect: () => { active = false; operation++ },
    reload,
    detect,
    editProcessing: (settings: Partial<Pick<PageConfig, 'mode' | 'denoise' | 'contrast' | 'threshold' | 'rotation'>>) =>
      replaceDraft({ ...state.draft, ...settings }),
    editCorners: (corners: Quad) => replaceDraft({ ...state.draft, corners, confirmed: false }),
    restoreDraft: replaceDraft, // Pointer cancel restores the entire pre-drag config, including confirmation.
    fullImage: () => replaceDraft({ ...state.draft, corners: [[0,0],[1,0],[1,1],[0,1]], confirmed: false }),
    reset: () => replaceDraft(editable(state.persisted.effective_config)),
    save: (confirm: boolean) => write(confirm, false),
    render: () => write(true, true),
  }
}
