import { useCallback, useEffect, useRef, useState } from 'react'
import type { FormEvent } from 'react'
import { errorMessage, scannerApi } from '../api/client'
import { PageList } from '../components/PageList'
import { SourcePreview } from '../components/SourcePreview'
import { UploadPanel } from '../components/UploadPanel'
import { DocumentTitleForm } from '../components/DocumentTitleForm'
import { movePageIds,selectRemainingPage } from '../components/documentActions'
import {ConfirmDeletion} from '../components/ConfirmDeletion'
import {importWithDetection} from '../components/importDetection'
import {ExportPanel} from '../components/ExportPanel'
import type {EditorAvailability} from '../components/ExportPanel'
import type { PageRead, SessionDetail, SessionRead } from '../types/scanner'

export function ScannerPage() {
  const [sessions, setSessions] = useState<SessionRead[]>([])
  const [total, setTotal] = useState(0)
  const [offset, setOffset] = useState(0)
  const [listReload, setListReload] = useState(0)
  const [listLoading, setListLoading] = useState(true)
  const [listError, setListError] = useState('')
  const [sessionId, setSessionId] = useState<string | null>(() => new URLSearchParams(location.search).get('session'))
  const [pageId, setPageId] = useState<string | null>(() => new URLSearchParams(location.search).get('page'))
  const [loadedDocument, setDocument] = useState<SessionDetail | null>(null)
  const [detailLoading, setDetailLoading] = useState(false)
  const [detailReload, setDetailReload] = useState(0)
  const [detailError, setDetailError] = useState('')
  const [title, setTitle] = useState('')
  const [creating, setCreating] = useState(false)
  const [createError, setCreateError] = useState('')
  const [uploading, setUploading] = useState(false)
  const [renaming, setRenaming] = useState(false)
  const [exporting,setExporting]=useState(false)
  const [editor,setEditor]=useState<EditorAvailability|null>(null)
  const [managing,setManaging]=useState(false),[managementError,setManagementError]=useState('')
  const mutationPending=useRef(false)
  const [pendingDelete,setPendingDelete]=useState<{pageId?:string;message:string}|null>(null)
  const busy = creating || uploading || renaming || managing || exporting
  const pagePersisted = useCallback((saved: PageRead) => {
    setDocument(current => current?.id === saved.session_id ? { ...current, pages: current.pages.map(page =>
      page.id === saved.id && saved.revision >= page.revision ? { ...page, revision: saved.revision,
        render_revision: saved.render_revision, effective_config: saved.effective_config } : page) } : current)
  }, [])

  useEffect(() => {
    const controller = new AbortController()
    setListLoading(true)
    setListError('')
    scannerApi.list(offset, controller.signal).then(result => {
      if (controller.signal.aborted) return
      setSessions(result.items)
      setTotal(result.total)
      setSessionId(current => current ?? result.items[0]?.id ?? null)
    }).catch(error => { if (!controller.signal.aborted) setListError(errorMessage(error)) })
      .finally(() => { if (!controller.signal.aborted) setListLoading(false) })
    return () => controller.abort()
  }, [offset, listReload])

  useEffect(() => {
    if (!sessionId) return
    const controller = new AbortController()
    setDetailLoading(true)
    setDetailError('')
    setDocument(current => current?.id === sessionId ? current : null)
    scannerApi.detail(sessionId, controller.signal).then(result => {
      if (controller.signal.aborted) return
      setDocument(result)
      setPageId(current => result.pages.some(page => page.id === current) ? current : result.pages[0]?.id ?? null)
    }).catch(error => { if (!controller.signal.aborted) setDetailError(errorMessage(error)) })
      .finally(() => { if (!controller.signal.aborted) setDetailLoading(false) })
    return () => controller.abort()
  }, [sessionId, detailReload])

  useEffect(() => {
    const url = new URL(location.href)
    if (sessionId) url.searchParams.set('session', sessionId)
    else url.searchParams.delete('session')
    if (pageId) url.searchParams.set('page', pageId)
    else url.searchParams.delete('page')
    history.replaceState(null, '', url)
  }, [sessionId, pageId])

  async function createDocument(event: FormEvent) {
    event.preventDefault()
    if (busy) return
    setCreating(true)
    setCreateError('')
    try {
      const created = await scannerApi.create(title.trim() || 'Tài liệu chưa đặt tên')
      setSessionId(created.id)
      setPageId(null)
      setTitle('')
      setOffset(0)
      setListReload(value => value + 1)
    } catch (error) { setCreateError(errorMessage(error)) }
    finally { setCreating(false) }
  }

  async function upload(file: File,onDetecting:()=>void) {
    if (!sessionId) throw new Error('Hãy tạo hoặc chọn tài liệu trước.')
    const {page,message}=await importWithDetection(scannerApi,sessionId,file,onDetecting)
    setDocument(current => current?.id === sessionId ? { ...current, pages: [...current.pages, page] } : current)
    setPageId(current => current ?? page.id)
    return message
  }

  async function finishUploads() {
    setListReload(value => value + 1)
    if (!sessionId) return
    try {
      // Reconcile even a lost POST response without remounting the active editor.
      const fresh = await scannerApi.detail(sessionId)
      setDocument(current => current?.id === fresh.id ? fresh : current)
      setPageId(current => fresh.pages.some(page => page.id === current) ? current : fresh.pages[0]?.id ?? null)
      setDetailError('')
    } catch (error) { setDetailError(`Chưa kiểm tra được các trang đã lưu. ${errorMessage(error)}`) }
  }

  function renamed(saved: SessionRead) {
    setDocument(current => current?.id === saved.id ? { ...current, ...saved } : current)
    setSessions(current => current.map(item => item.id === saved.id ? saved : item))
    setListReload(value => value + 1)
  }

  async function changeDocument(action:()=>Promise<SessionDetail|null>) {
    if(busy||mutationPending.current||!document||detailLoading||detailError)return
    mutationPending.current=true;setManaging(true);setManagementError('')
    const sid=document.id,oldPages=document.pages
    const accept=(fresh:SessionDetail|null)=>{
      if(fresh){
        if(fresh.id!==sid)throw new Error('Phản hồi không khớp tài liệu.')
        setDocument(fresh);setPageId(current=>selectRemainingPage(current,oldPages,fresh.pages))
      } else {
        const remaining=sessions.filter(item=>item.id!==sid)
        setDocument(null);setSessions(remaining);setSessionId(remaining[0]?.id??null);setPageId(null);setOffset(0)
      }
      setListReload(value=>value+1)
    }
    try{accept(await action())}
    catch(error){
      setManagementError(`${errorMessage(error)} Đã yêu cầu đọc lại trạng thái đã lưu; không tự gửi lại thao tác.`)
      try{accept(await scannerApi.detail(sid))}
      catch(lookup){
        if(lookup instanceof Error&&'code' in lookup&&lookup.code==='SESSION_NOT_FOUND')accept(null)
        else setDetailError('Chưa xác định được trạng thái tài liệu. Dùng “Tải lại” để kiểm tra trước khi thao tác tiếp.')
      }
    }finally{mutationPending.current=false;setManaging(false)}
  }
  function movePage(id:string,direction:-1|1){
    if(!document)return
    const ids=movePageIds(document.pages,id,direction)
    if(ids)void changeDocument(()=>scannerApi.order(document.id,ids))
  }
  function deletePage(id:string){
    setPendingDelete({pageId:id,message:'Xóa trang này cùng ảnh nguồn và bản quét? Thao tác không thể hoàn tác; các trang khác được giữ lại.'})
  }

  const document = loadedDocument?.id === sessionId ? loadedDocument : null
  const selected = document?.pages.find(page => page.id === pageId)
  const reload = () => { setListReload(value => value + 1); setDetailReload(value => value + 1) }
  return <main className="app-shell">
    {pendingDelete&&<ConfirmDeletion message={pendingDelete.message} onCancel={()=>setPendingDelete(null)} onConfirm={()=>{
      const pid=pendingDelete.pageId;setPendingDelete(null)
      if(document)void changeDocument(async()=>{
        if(pid){await scannerApi.deletePage(document.id,pid);return scannerApi.detail(document.id)}
        await scannerApi.deleteSession(document.id);return null
      })
    }}/>}
    <header className="app-header"><span className="brand-mark" aria-hidden="true">DS</span>
      <div><h1>Document Scanner</h1><p className="muted small">Tài liệu của bạn, lưu ngay trên máy.</p></div>
      <button className="secondary refresh-button" disabled={busy || listLoading || detailLoading} onClick={reload}>Tải lại</button>
    </header>
    <div className="workspace">
      <aside className="documents-panel" aria-labelledby="documents-title">
        <div className="section-heading"><h2 id="documents-title">Tài liệu</h2><span className="count">{total}</span></div>
        <form onSubmit={event => void createDocument(event)}>
          <label htmlFor="document-title">Tên tài liệu mới</label>
          <input id="document-title" value={title} onChange={event => setTitle(event.target.value)} maxLength={200}
            placeholder="Ví dụ: Bài tập xử lý ảnh" disabled={busy} />
          <button type="submit" disabled={busy}>{creating ? 'Đang tạo…' : '+ Tạo tài liệu'}</button>
        </form>
        {createError && <p role="alert" className="error">{createError}</p>}
        {listError && <p role="alert" className="error">{listError}</p>}
        {listLoading && <p role="status" className="muted">Đang tải tài liệu…</p>}
        {!listLoading && !listError && sessions.length === 0 && <p className="muted">Chưa có tài liệu. Tạo tài liệu đầu tiên để bắt đầu.</p>}
        <ul className="document-list" aria-label="Danh sách tài liệu">
          {sessions.map(item => <li key={item.id}><button disabled={busy} className="document-button"
            aria-pressed={sessionId === item.id} onClick={() => {
              if (sessionId !== item.id) { setSessionId(item.id); setPageId(null) }
            }}>
            <strong>{item.title}</strong><small>{new Date(item.updated_at).toLocaleString('vi-VN')}</small>
          </button></li>)}
        </ul>
        {total > 20 && <nav aria-label="Phân trang tài liệu" className="pagination">
          <button className="secondary" disabled={busy || listLoading || offset === 0} onClick={() => setOffset(value => value - 20)}>Trước</button>
          <span>{Math.floor(offset / 20) + 1}/{Math.ceil(total / 20)}</span>
          <button className="secondary" disabled={busy || listLoading || offset + 20 >= total} onClick={() => setOffset(value => value + 20)}>Sau</button>
        </nav>}
      </aside>
      <section className="document-workspace" aria-label="Tài liệu đang mở">
        <div className="document-heading"><div><p className="eyebrow">Không gian tài liệu</p>
          <h2>{document?.title ?? (detailLoading ? 'Đang mở tài liệu…' : 'Bắt đầu với một tài liệu')}</h2>
          {document && <DocumentTitleForm key={document.id} document={document} disabled={busy || detailLoading} onBusy={setRenaming} onRenamed={renamed} />}</div>
          {document && <div className="document-tools"><span className="badge">{document.pages.length}/20 trang</span>
            <button className="secondary" disabled={busy||detailLoading||!!detailError} onClick={()=>{
              setPendingDelete({message:`Xóa tài liệu “${document.title}” và tất cả các trang? Thao tác không thể hoàn tác.`})
            }}>Xóa tài liệu</button></div>}</div>
        {managementError&&<p role="alert" className="error">{managementError}</p>}
        {detailError && <p role="alert" className="error">{detailError} Dùng “Tải lại” để thử lại.</p>}
        {detailLoading && <p role="status" className="loading-message">Đang tải trang và thông tin đã lưu…</p>}
        {!sessionId && !listLoading && <div className="empty-state"><span className="paper-symbol" aria-hidden="true">＋</span>
          <h3>Gom các trang vào một tài liệu</h3><p>Tạo tài liệu ở bên trái, rồi chọn những ảnh chụp cần nhập.</p></div>}
        {document && <>
          <UploadPanel key={document.id} disabled={creating || renaming || managing || exporting || detailLoading || !!detailError || document.pages.length >= 20} busy={uploading} remainingSlots={20-document.pages.length} onBusy={setUploading}
            onUpload={upload} onFinished={finishUploads} />
          <ExportPanel key={'export:'+document.id} document={document} disabled={busy||detailLoading||!!detailError} editor={editor}
            onBusy={setExporting} onFinished={finishUploads}/>
          <div className="page-workspace">
            <section className="pages-panel" aria-labelledby="pages-title"><h3 id="pages-title">Các trang <span className="count">{document.pages.length}</span></h3>
              {document.pages.length ? <PageList pages={document.pages} selected={pageId} onSelect={setPageId} disabled={busy||detailLoading||!!detailError} onMove={movePage} onDelete={deletePage}/> : <p className="muted small">Ảnh nhập thành công sẽ xuất hiện ở đây.</p>}
            </section>
            <section className="viewer" aria-label="Xem ảnh nguồn">
              {selected ? <SourcePreview key={`${selected.id}:${selected.normalized_artifact_id}:${detailReload}`} page={selected} onPersisted={pagePersisted} locked={exporting} onEditingState={setEditor} /> : <div className="empty-state">
                <span className="paper-symbol" aria-hidden="true">▤</span><h3>Tài liệu đang trống</h3><p>Chọn JPEG hoặc PNG ở phía trên để thêm trang đầu tiên.</p></div>}
            </section>
          </div>
        </>}
      </section>
    </div>
  </main>
}
