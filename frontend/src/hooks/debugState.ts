import type { DebugRead } from '../types/scanner'
import { validateDebug } from '../components/pipelineData.ts'
import type { DebugTarget } from '../components/pipelineData.ts'

/** GET-only state owned by a single mounted run. Superseded requests cannot publish. */
export function createDebugState(target: DebugTarget, fetchDebug: (signal: AbortSignal) => Promise<DebugRead>) {
  let state: {data: DebugRead|null; busy:boolean; error:string}={data:null,busy:false,error:''}
  let active=false, sequence=0, controller:AbortController|undefined
  const listeners=new Set<()=>void>()
  const patch=(next:Partial<typeof state>)=>{state={...state,...next};listeners.forEach(fn=>fn())}
  async function load() {
    if(!active)return
    const id=++sequence;controller?.abort();controller=new AbortController()
    patch({data:null,busy:true,error:''})
    try {
      const data=await fetchDebug(controller.signal)
      if(active&&sequence===id)patch({data:validateDebug(data,target)})
    } catch(error) {
      if(active&&sequence===id)patch({error:error instanceof Error?error.message:'Không tải được debug.'})
    } finally {if(active&&sequence===id)patch({busy:false})}
  }
  return {getSnapshot:()=>state,subscribe:(fn:()=>void)=>{listeners.add(fn);return()=>{listeners.delete(fn)}},load,
    connect:()=>{active=true},disconnect:()=>{active=false;sequence++;controller?.abort()}}
}
