import assert from 'node:assert/strict'
import {test} from 'node:test'
import {exportWithMissingRenders} from './exportFlow.ts'

const pages=[{id:'p1',revision:2,effective_config:{confirmed:true,corners:[[0,0],[1,0],[1,1],[0,1]]}},
 {id:'p2',revision:4,effective_config:{confirmed:true,corners:[[0,0],[1,0],[1,1],[0,1]]}}]
const request={format:'pdf',pages:[{page_id:'p2',revision:4},{page_id:'p1',revision:2}],paper_size:'a4',orientation:'auto',margin_mm:5,image_encoding:'png'}
const receipt={id:'export',session_id:'s',artifact_id:'artifact',format:'pdf',pages:request.pages,created_at:'2026-10-18T10:00:00Z'}
function api(overrides={}){
 const calls=[];return {calls,...{
 detail:async()=>{calls.push('GET');return {id:'s',pages:structuredClone(pages)}},
 export:async(s,r)=>{calls.push(['export',structuredClone(r)]);return receipt},
 render:async(s,p,r)=>{calls.push(['render',p,r]);return {page_id:p,revision:r}}
 },...overrides}
}
const missing=(p=request.pages)=>Object.assign(new Error('missing'),{code:'PAGE_NOT_RENDERED',status:409,details:{pages:p}})

test('success exports exact persisted subset/order and does not render or PUT config',async()=>{
 const a=api();assert.deepEqual(await exportWithMissingRenders(a,'s',request),receipt)
 assert.deepEqual(a.calls,['GET',['export',request]])
})
test('missing full renders only listed confirmed exact revisions then retries export once',async()=>{
 const a=api();let attempts=0
 a.export=async()=>{a.calls.push('export');if(!attempts++)throw missing(request.pages.slice(0,1));return receipt}
 assert.deepEqual(await exportWithMissingRenders(a,'s',request),receipt)
 assert.deepEqual(a.calls,['GET','export','GET',['render','p2',4],'export'])
})
test('repeated PAGE_NOT_RENDERED stops at second export instead of looping',async()=>{
 const a=api();let attempts=0;a.export=async()=>{attempts++;throw missing()}
 await assert.rejects(exportWithMissingRenders(a,'s',request),/missing/);assert.equal(attempts,2)
 assert.equal(a.calls.filter(c=>Array.isArray(c)&&c[0]==='render').length,2)
})
test('stale or unconfirmed pages never export and never confirm automatically',async()=>{
 for(const kind of ['stale','draft','foreign']){
  const a=api({detail:async()=>({id:'s',pages:pages.map(p=>p.id==='p2'?{...p,...(kind==='stale'?{revision:5}:kind==='foreign'?{id:'other'}:{effective_config:{confirmed:false,corners:null}})}:p)})})
  await assert.rejects(exportWithMissingRenders(a,'s',request))
  assert.deepEqual(a.calls,[])
 }
})
test('config changed before missing-render recovery stops without rendering new revision',async()=>{
 const a=api();let reads=0,attempts=0;a.export=async()=>{attempts++;throw missing()}
 a.detail=async()=>{const newer=reads++>0;return {id:'s',pages:pages.map(p=>newer?{...p,revision:99}:p)}}
 await assert.rejects(exportWithMissingRenders(a,'s',request));assert.equal(a.calls.length,0);assert.equal(attempts,1)
})
test('unknown outcome, 429 and malformed missing-list are never retried',async()=>{
 for(const error of [Object.assign(new Error('network'),{code:'NETWORK_ERROR'}),Object.assign(new Error('busy'),{code:'PROCESSING_BUSY',status:429}),missing([{page_id:'foreign',revision:4}])]){
  const a=api();let attempts=0;a.export=async()=>{attempts++;throw error}
  await assert.rejects(exportWithMissingRenders(a,'s',request));assert.equal(attempts,1)
  assert.equal(a.calls.filter(c=>Array.isArray(c)&&c[0]==='render').length,0)
 }
})
test('late/unmounted flow stops before mutations and wrong receipt order is rejected',async()=>{
 const a=api();await assert.rejects(exportWithMissingRenders(a,'s',request,()=>false));assert.deepEqual(a.calls,[])
 const wrong=api({export:async()=>({...receipt,pages:[...request.pages].reverse()})})
 await assert.rejects(exportWithMissingRenders(wrong,'s',request))
})
