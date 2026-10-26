import {useEffect,useRef,useState} from 'react'
import {artifactUrl,errorMessage,scannerApi} from '../api/client'
import type {ExportRead,ExportRequest,SessionDetail} from '../types/scanner'
import {exportWithMissingRenders} from './exportFlow'

export interface EditorAvailability {pageId:string;dirty:boolean;busy:boolean;needsReload:boolean}

function downloadName(title:string,format:ExportRequest['format']){
  const stem=title.replaceAll('Đ','D').replaceAll('đ','d').normalize('NFKD').replace(/[\u0300-\u036f]/g,'')
    .replace(/[^a-zA-Z0-9_-]+/g,'-').replace(/^-+|-+$/g,'').slice(0,70)||'document'
  return 'scan-'+stem+'.'+format
}

export function ExportPanel({document,disabled,editor,onBusy,onFinished}:{
  document:SessionDetail;disabled:boolean;editor:EditorAvailability|null;
  onBusy:(busy:boolean)=>void;onFinished:()=>Promise<void>
}){
  const [selected,setSelected]=useState(()=>document.pages.map(p=>p.id))
  const [format,setFormat]=useState<ExportRequest['format']>('pdf')
  const [orientation,setOrientation]=useState<ExportRequest['orientation']>('auto')
  const [margin,setMargin]=useState(5)
  const [encoding,setEncoding]=useState<ExportRequest['image_encoding']>('png')
  const [working,setWorking]=useState(false),[error,setError]=useState('')
  const [result,setResult]=useState<{receipt:ExportRead;filename:string}|null>(null)
  const active=useRef(true),pending=useRef(false)
  const ids=document.pages.map(p=>p.id).join(',')
  useEffect(()=>{active.current=true;return()=>{active.current=false}},[])
  useEffect(()=>{setSelected(current=>current.filter(id=>ids.split(',').includes(id)));setResult(null)},[ids])
  const chosen=document.pages.filter(p=>selected.includes(p.id))
  const currentEditor=document.pages.some(p=>p.id===editor?.pageId)?editor:null
  const revisions=chosen.map(p=>p.id+':'+p.revision).join(',')
  const selectedDirty=Boolean(currentEditor?.dirty&&selected.includes(currentEditor.pageId))
  useEffect(()=>{setResult(null)},[revisions,selectedDirty])
  const reason=!chosen.length?'Chọn ít nhất một trang để xuất.'
    :format!=='pdf'&&chosen.length!==1?'PNG và JPG chỉ xuất một trang mỗi lần.'
    :!Number.isFinite(margin)||margin<0||margin>30?'Lề PDF phải từ 0 đến 30 mm.'
    :chosen.some(p=>!p.effective_config.confirmed||!p.effective_config.corners)?'Có trang chưa xác nhận vùng. Kiểm tra và xác nhận trước khi xuất.'
    :currentEditor?.busy||currentEditor?.needsReload?'Chờ thao tác trang hoàn tất hoặc đọc lại cấu hình trước khi xuất.'
    :selectedDirty?'Trang đang chọn có thay đổi chưa lưu. Tạo bản quét hoặc đặt lại cấu hình đã lưu trước khi xuất.':''
  async function submit(){
    if(disabled||pending.current||reason)return
    pending.current=true;setWorking(true);onBusy(true);setError('');setResult(null)
    const request:ExportRequest={pages:chosen.map(p=>({page_id:p.id,revision:p.revision})),format,
      paper_size:'a4',orientation,margin_mm:margin,image_encoding:encoding}
    const filename=downloadName(document.title,format)
    try{
      const receipt=await exportWithMissingRenders(scannerApi,document.id,request,()=>active.current)
      if(active.current){setResult({receipt,filename});await onFinished()}
    }catch(e){if(active.current)setError(errorMessage(e))}
    finally{pending.current=false;if(active.current){setWorking(false);onBusy(false)}}
  }
  return <section className="export-panel" aria-labelledby="export-title">
    <div className="section-heading"><h3 id="export-title">Xuất tài liệu</h3><span className="count">{chosen.length} trang</span></div>
    <p className="muted small">Xuất theo thứ tự danh sách trang. Chỉ dùng cấu hình đã lưu và vùng đã xác nhận; app sẽ tạo bản quét còn thiếu.</p>
    <fieldset disabled={disabled||working}>
      <legend>Chọn trang xuất</legend>
      <div className="export-pages">{document.pages.map(p=><label key={p.id}>
        <input type="checkbox" aria-label={'Xuất trang '+(p.position+1)} checked={selected.includes(p.id)} onChange={e=>{
          setSelected(current=>e.target.checked?[...current,p.id]:current.filter(id=>id!==p.id));setResult(null)
        }}/>Trang {p.position+1} · {p.effective_config.mode.toUpperCase()} · r{p.revision}
      </label>)}</div>
      <div className="scan-actions"><button className="secondary" onClick={()=>{setSelected(document.pages.map(p=>p.id));setResult(null)}}>Chọn tất cả</button>
        <button className="secondary" onClick={()=>{setSelected([]);setResult(null)}}>Bỏ chọn</button></div>
      <div className="filter-grid">
        <label>Định dạng xuất<select aria-label="Định dạng xuất" value={format} onChange={e=>{setFormat(e.target.value as ExportRequest['format']);setResult(null)}}>
          <option value="pdf">PDF nhiều trang</option><option value="png">Ảnh PNG</option><option value="jpg">Ảnh JPG</option></select></label>
        <label>Hướng giấy A4<select aria-label="Hướng giấy A4" disabled={format!=='pdf'} value={orientation} onChange={e=>{setOrientation(e.target.value as ExportRequest['orientation']);setResult(null)}}>
          <option value="auto">Tự động theo bản quét</option><option value="portrait">Dọc</option><option value="landscape">Ngang</option></select></label>
        <label>Lề PDF (mm)<input type="number" min="0" max="30" step="1" disabled={format!=='pdf'} value={Number.isFinite(margin)?margin:''}
          onChange={e=>{setMargin(e.target.valueAsNumber);setResult(null)}}/></label>
        <label>Ảnh nhúng trong PDF<select aria-label="Ảnh nhúng trong PDF" disabled={format!=='pdf'} value={encoding} onChange={e=>{setEncoding(e.target.value as ExportRequest['image_encoding']);setResult(null)}}>
          <option value="png">PNG · giữ nét</option><option value="jpeg">JPEG · nén mất dữ liệu</option></select></label>
      </div>
    </fieldset>
    {reason&&!working&&<p role="status" className="muted small">{reason}</p>}
    <div className="scan-actions"><button disabled={disabled||working||!!reason} onClick={()=>void submit()}>{working?'Đang tạo tệp…':'Tạo tệp xuất'}</button>
      {result&&<a className="download-link" href={artifactUrl(result.receipt.artifact_id)} download={result.filename}>
        {'Tải '+result.receipt.format.toUpperCase()+' · '+result.receipt.pages.length+' trang'}</a>}</div>
    {working&&<p role="status">Đang tạo và lưu tệp xuất…</p>}
    {result&&!working&&<p role="status" className="small">Tệp đã lưu trên máy. Bấm Tải để lưu một bản vào thư mục tải xuống.</p>}
    {error&&<p role="alert" className="error">{error}</p>}
  </section>
}
