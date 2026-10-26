import { ApiError, errorMessage } from '../api/client.ts'

export interface Outcome { name: string; state: 'waiting' | 'uploading' | 'detecting' | 'done' | 'error'; message: string }
interface Batch {
  files: File[]; remainingSlots: number
  onUpload: (file: File,onDetecting:()=>void) => Promise<string|void>
  onResults: (results: Outcome[]) => void
  onBusy: (busy: boolean) => void
  onFinished: () => Promise<void>
}

/** The lock includes the final GET, so an uncertain upload is reconciled before another batch. */
export function createUploadBatch() {
  let active=false
  return async ({files,remainingSlots,onUpload,onResults,onBusy,onFinished}:Batch) => {
    if(active||!files.length)return
    active=true;onBusy(true)
    let results:Outcome[]=files.map(file=>({name:file.name,state:'waiting',message:'Đang chờ'}))
    onResults(results)
    const report=(index:number,state:Outcome['state'],message:string)=>{
      results=results.map((item,i)=>i===index?{...item,state,message}:item);onResults(results)
    }
    try {
      for(const [index,file] of files.entries()) {
        report(index,'uploading','Đang nhập…')
        try {
          if(remainingSlots<=0)throw new Error('Tài liệu đã đủ 20 trang; tệp này chưa được nhập.')
          if(file.size>15*1024*1024)throw new Error('Tệp ảnh vượt giới hạn 15 MiB.')
          const message=await onUpload(file,()=>report(index,'detecting','Đã lưu · đang nhận diện vùng…'))
          remainingSlots--;report(index,'done',message??'Đã lưu')
        } catch(error) {
          if(error instanceof ApiError&&error.code==='PAGE_LIMIT_EXCEEDED')remainingSlots=0
          report(index,'error',errorMessage(error))
        }
      }
    } finally {
      try {await onFinished()} finally {active=false;onBusy(false)}
    }
  }
}
