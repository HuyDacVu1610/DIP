import type {ExportRequest,ExportRead,SessionDetail,RenderRead} from '../types/scanner'

interface ExportApi {
  detail:(sid:string)=>Promise<SessionDetail>
  export:(sid:string,body:ExportRequest)=>Promise<ExportRead>
  render:(sid:string,pid:string,revision:number)=>Promise<RenderRead>
}

/** Only a definitive missing-render409 permits one retry; never PUT/confirm drafts. */
export async function exportWithMissingRenders(api:ExportApi,sid:string,input:ExportRequest,alive=()=>true):Promise<ExportRead> {
  const request=structuredClone(input)
  const check=()=>{if(!alive())throw new Error('Đã rời tài liệu; bỏ phản hồi xuất cũ.')}
  async function validateSaved(){
    check();const detail=await api.detail(sid);check()
    if(detail.id!==sid)throw new Error('Tài liệu phản hồi không khớp.')
    for(const chosen of request.pages){
      const page=detail.pages.find(p=>p.id===chosen.page_id)
      if(!page||page.revision!==chosen.revision)throw new Error('Trang hoặc phiên bản đã thay đổi. Đọc lại tài liệu rồi chọn xuất lại.')
      if(!page.effective_config.confirmed||!page.effective_config.corners)throw new Error('Có trang chưa xác nhận vùng. Kiểm tra và xác nhận trước khi xuất.')
    }
  }
  await validateSaved()
  let receipt:ExportRead
  try{check();receipt=await api.export(sid,request)}
  catch(error){
    const e=error as {code?:string;status?:number;details?:{pages?:unknown}}
    if(e.code!=='PAGE_NOT_RENDERED'||e.status!==409)throw error
    check();const missing=e.details?.pages
    if(!Array.isArray(missing)||!missing.length||new Set(missing.map(p=>p?.page_id)).size!==missing.length
      ||missing.some(p=>!request.pages.some(w=>w.page_id===p?.page_id&&w.revision===p?.revision)))throw new Error('Danh sách trang thiếu bản quét không khớp yêu cầu.')
    await validateSaved()
    for(const page of missing){
      check();const rendered=await api.render(sid,page.page_id,page.revision);check()
      if(rendered.page_id!==page.page_id||rendered.revision!==page.revision)throw new Error('Bản quét phục hồi không khớp trang/phiên bản.')
    }
    check();receipt=await api.export(sid,request) // a second missing/error is surfaced, not retried
  }
  check()
  if(receipt.session_id!==sid||receipt.format!==request.format||!receipt.id||!receipt.artifact_id
    ||!Array.isArray(receipt.pages)||receipt.pages.length!==request.pages.length
    ||receipt.pages.some((p,i)=>p.page_id!==request.pages[i].page_id||p.revision!==request.pages[i].revision))throw new Error('Tệp xuất trả về không khớp snapshot đã chọn.')
  return receipt
}
