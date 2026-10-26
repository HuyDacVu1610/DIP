import assert from 'node:assert/strict'
import {test} from 'node:test'
import {importWithDetection} from './importDetection.ts'
import {createUploadBatch} from './uploadBatch.ts'
const page={id:'p',session_id:'s',normalized_artifact_id:'source',width:480,height:640,revision:0,
 effective_config:{corners:null,confirmed:false}}
const proposal={page_id:'p',source_artifact_id:'source',source_width:480,source_height:640,source_revision:0,
 status:'proposed',corners:[[.1,.1],[.9,.1],[.9,.9],[.1,.9]],confirmed:false,heuristic_score:.8}
const file=new File(['x'],'safe.png')

test('upload then detect exactly once, keeping the persisted config/revision unconfirmed',async()=>{
 const calls=[],before=structuredClone(page)
 const result=await importWithDetection({upload:async()=>{calls.push('upload');return page},
  detect:async(sid,pid)=>{calls.push([sid,pid]);return proposal}},'s',file,()=>calls.push('detecting'))
 assert.deepEqual(calls,['upload','detecting',['s','p']])
 assert.deepEqual(page,before);assert.deepEqual(result.page.latest_detection,proposal)
 assert.equal(result.page.revision,0);assert.equal(result.page.effective_config.corners,null)
 assert.match(result.message,/kiểm tra/i)
})

test('a legacy upload caller without progress still detects once and returns its committed page',async()=>{
 const calls=[]
 // A runner retained before Fast Refresh calls onUpload(file), without a progress callback.
 const onUpload=async(f,onDetecting)=>importWithDetection({
  upload:async()=>{calls.push('upload');return page},
  detect:async(sid,pid)=>{calls.push(['detect',sid,pid]);return proposal},
 },'s',f,onDetecting)
 const result=await onUpload(file)
 assert.deepEqual(calls,['upload',['detect','s','p']])
 assert.deepEqual(result.page.latest_detection,proposal)
 assert.equal(result.page.revision,0);assert.equal(result.page.effective_config.confirmed,false)
 assert.match(result.message,/Đã lưu.*kiểm tra/)
})

test('manual-required and warning remain reviewable, never auto-confirmed',async()=>{
 for(const detection of [{...proposal,status:'manual_required',corners:null,heuristic_score:null},
  {...proposal,status:'proposed_with_warning'}]){
  const result=await importWithDetection({upload:async()=>page,detect:async()=>detection},'s',file,()=>{})
  assert.equal(result.page.latest_detection.confirmed,false)
  assert.match(result.message,detection.status==='manual_required'?/bằng tay/i:/cảnh báo/i)
 }
})

test('a detection failure still consumes the imported slot and the next file continues',async()=>{
 let n=0,last=[],finished=0;const calls=[]
 await createUploadBatch()({files:[file,file,new File(['x'],'excess.png')],remainingSlots:2,onBusy:()=>{},onResults:r=>last=r,
  onUpload:async(f,onDetecting)=>{
   const result=await importWithDetection({upload:async()=>{calls.push('upload');return {...page,id:'p'+(++n)}},
    detect:async(sid,pid)=>{calls.push(pid);if(n===1)throw new Error('CPU busy');return {...proposal,page_id:pid}}},
    's',f,onDetecting)
   return result.message
  },onFinished:async()=>{finished++}})
 assert.deepEqual(calls,['upload','p1','upload','p2']);assert.equal(finished,1)
 assert.deepEqual(last.map(r=>r.state),['done','done','error'])
 assert.match(last[0].message,/đã lưu/i);assert.match(last[0].message,/CPU busy/)
 assert.match(last[2].message,/20 trang/)
})

test('upload failure never starts detection; wrong bindings never become proposals',async()=>{
 let calls=0
 await assert.rejects(importWithDetection({upload:async()=>{throw new Error('Bad file')},detect:async()=>{calls++}},'s',file,()=>{}))
 assert.equal(calls,0)
 for(const change of [{page_id:'other'},{source_revision:1},{confirmed:true},{source_artifact_id:'foreign'},
  {source_width:481},{heuristic_score:NaN},{status:'unknown'},
  {corners:[[0,0],[1,1],[1,0],[0,1]]}]){
  const result=await importWithDetection({upload:async()=>page,detect:async()=>({...proposal,...change})},'s',file,()=>{})
  assert.equal(result.page.latest_detection,undefined);assert.match(result.message,/nhận diện lỗi/i)
 }
})

test('the batch stays busy during detection and starts the next upload only after detection settles',async()=>{
 let release;const gate=new Promise(r=>release=r),calls=[],states=[],busy=[]
 const run=createUploadBatch()
 const options={files:[file,new File(['x'],'next.png')],remainingSlots:2,onBusy:b=>busy.push(b),onResults:r=>states.push(r),
  onUpload:async(f,onDetecting)=>{
   const result=await importWithDetection({upload:async()=>{calls.push(f.name);return page},detect:async()=>{
    if(f===file)await gate;return proposal}},'s',f,onDetecting)
   return result.message
  },onFinished:async()=>{}}
 const pending=run(options)
 await new Promise(r=>setImmediate(r))
 assert.equal(states.at(-1)[0].state,'detecting');assert.deepEqual(calls,['safe.png']);assert.deepEqual(busy,[true])
 await run(options);assert.deepEqual(calls,['safe.png'])
 release();await pending
 assert.deepEqual(calls,['safe.png','next.png']);assert.deepEqual(busy,[true,false])
 assert.ok(states.at(-1).every(r=>r.state==='done'))
})
