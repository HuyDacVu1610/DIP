import {useEffect,useRef} from 'react'

export function ConfirmDeletion({message,onCancel,onConfirm}:{message:string;onCancel:()=>void;onConfirm:()=>void}) {
  const dialog=useRef<HTMLDialogElement>(null)
  useEffect(()=>{const element=dialog.current!;element.showModal();return()=>element.close()},[])
  return <dialog ref={dialog} aria-labelledby="delete-title" aria-describedby="delete-message" onCancel={event=>{event.preventDefault();onCancel()}}>
    <h2 id="delete-title">Xác nhận xóa</h2><p id="delete-message">{message}</p>
    <div className="scan-actions"><button autoFocus className="secondary" onClick={onCancel}>Giữ lại</button>
      <button className="danger" onClick={onConfirm}>Xóa vĩnh viễn</button></div>
  </dialog>
}
