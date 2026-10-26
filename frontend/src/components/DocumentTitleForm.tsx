import { useEffect, useRef, useState } from 'react'
import type { FormEvent } from 'react'
import { errorMessage, scannerApi } from '../api/client'
import type { SessionRead } from '../types/scanner'

interface Props {
  document: SessionRead; disabled: boolean
  onBusy: (busy:boolean)=>void; onRenamed: (document:SessionRead)=>void
}
export function DocumentTitleForm({document,disabled,onBusy,onRenamed}:Props) {
  const [editing,setEditing]=useState(false),[title,setTitle]=useState(document.title)
  const [error,setError]=useState(''),[message,setMessage]=useState('')
  const pending=useRef(false),mounted=useRef(true),button=useRef<HTMLButtonElement>(null),restoreFocus=useRef(false)
  useEffect(()=>{mounted.current=true;return()=>{mounted.current=false}},[])
  useEffect(()=>{if(!editing&&restoreFocus.current){button.current?.focus();restoreFocus.current=false}},[editing])
  function close(){restoreFocus.current=true;setEditing(false);setError('')}
  async function save(event:FormEvent) {
    event.preventDefault()
    if(disabled||pending.current)return
    const trimmed=title.trim()
    if(!trimmed){setError('Tên tài liệu cần có 1–200 ký tự sau khi bỏ khoảng trắng hai đầu.');return}
    pending.current=true;onBusy(true);setError('');setMessage('')
    try {
      const saved=await scannerApi.rename(document.id,trimmed)
      if(saved.id!==document.id||saved.title!==trimmed)throw new Error('Phản hồi đổi tên không khớp tài liệu. Hãy tải lại để kiểm tra tên đã lưu.')
      if(mounted.current){onRenamed(saved);setMessage('Đã lưu tên tài liệu.');close()}
    } catch(error) {
      if(mounted.current)setError(`${errorMessage(error)} Nếu mất kết nối, dùng “Tải lại” để kiểm tra tên đã lưu.`)
    } finally {pending.current=false;if(mounted.current)onBusy(false)}
  }
  return <div className="document-title-editor">
    <button ref={button} className="secondary" disabled={disabled||editing} onClick={()=>{setTitle(document.title);setEditing(true);setError('');setMessage('')}}>Đổi tên tài liệu</button>
    {editing&&<form onSubmit={event=>void save(event)}>
      <label htmlFor="rename-title">Tên tài liệu</label>
      <input id="rename-title" autoFocus required maxLength={200} value={title} disabled={disabled} onChange={e=>setTitle(e.target.value)} />
      <div className="scan-actions"><button type="submit" disabled={disabled}>Lưu tên</button>
        <button type="button" className="secondary" disabled={disabled} onClick={close}>Hủy đổi tên</button></div>
    </form>}
    {error&&<p role="alert" className="error">{error}</p>}
    {message&&<p role="status" className="small">{message}</p>}
  </div>
}
