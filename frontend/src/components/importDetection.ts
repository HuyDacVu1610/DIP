import type {DetectionRead,PageRead} from '../types/scanner'
import {errorMessage} from '../api/client.ts'
import {assertDetectionProposal} from './detectionProposal.ts'

interface ImportApi {
  upload:(sid:string,file:File)=>Promise<PageRead>
  detect:(sid:string,pid:string)=>Promise<DetectionRead>
}

export async function importWithDetection(api:ImportApi,sid:string,file:File,onDetecting:()=>void=()=>{}){
  const page=await api.upload(sid,file)
  if(page.session_id!==sid)throw new Error('Trang nhập không khớp tài liệu. Hãy tải lại để kiểm tra.')
  onDetecting()
  try{
    const detection=await api.detect(sid,page.id)
    assertDetectionProposal(detection,page)
    if(detection.source_revision!==page.revision)throw new Error('Phiên bản trang đã thay đổi trong lúc nhận diện.')
    return {page:{...page,latest_detection:detection},message:detection.status==='manual_required'
      ?'Đã lưu · cần chỉnh vùng bằng tay'
      :detection.status==='proposed_with_warning'?'Đã lưu · vùng có cảnh báo, cần kiểm tra'
        :'Đã lưu · đã đề xuất vùng, cần kiểm tra'}
  }catch(error){
    // The upload already committed: consume its slot and never re-upload on a detection error.
    return {page,message:'Đã lưu · nhận diện lỗi, có thể thử lại hoặc chỉnh tay. '+errorMessage(error)}
  }
}
