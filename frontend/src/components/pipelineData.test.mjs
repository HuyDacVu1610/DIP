import assert from 'node:assert/strict'
import {test} from 'node:test'
import {validateDebug,readHistogram,scoreParts} from './pipelineData.ts'
import {createDebugState} from '../hooks/debugState.ts'

const id='4fd61e37-8574-450e-bd24-2bba10500001',sha='a'.repeat(64)
const target={kind:'render',runId:'run',pageId:'p',sourceId:'source',width:3,height:3,revision:2,fullId:id}
const ref={id,sha256:sha,width:2,height:2,png_mode:'L'}
const data={page_id:'p',kind:'render',run_id:'run',current_revision:2,revision:2,status:'available',debug_persisted:true,created_at:'2026-10-18T00:00:00Z',
 metadata:{run_id:'run',revision:2,debug_persisted:true,source:{artifact_id:'source',sha256:sha,width:3,height:3},artifacts:{prepared_gray:ref,full:ref},
  histogram:{counts:[2,...Array(254).fill(0),2],width:2,height:2,pixel_count:4,source_artifact:'prepared_gray',source_png_sha256:sha,threshold_method:'otsu',threshold_scope:'global',otsu_threshold:123},otsu_threshold:123},
 artifacts:{prepared_gray:{...ref,kind:'debug',revision:2,mime:'image/png',byte_size:99,created_at:'2026-10-18T00:00:00Z'},full:{...ref,kind:'render',revision:2,mime:'image/png',byte_size:99,created_at:'2026-10-18T00:00:00Z'}},missing_stages:{}}

test('debug binds exact run/page/source/revision/full and safe artifacts; incomplete stays explicit',()=>{
 assert.equal(validateDebug(data,target),data)
 for(const change of [{run_id:'old'},{page_id:'other'},{kind:'detection'},{revision:1},
  {debug_persisted:false},
  {metadata:{...data.metadata,source:{...data.metadata.source,width:4}}},
  {artifacts:{...data.artifacts,full:{...data.artifacts.full,id:'https://bad'}}},
  {artifacts:{...data.artifacts,full:{...data.artifacts.full,kind:'debug'}}}]){
  assert.throws(()=>validateDebug({...data,...change},target))
 }
 const partial={...data,status:'incomplete',artifacts:{full:data.artifacts.full},missing_stages:{prepared_gray:'file_unavailable'}}
 assert.equal(validateDebug(partial,target).status,'incomplete')
 const detected={...data,kind:'detection',revision:null,metadata:{...data.metadata,source:{...data.metadata.source,revision:2}},artifacts:{prepared_gray:data.artifacts.prepared_gray}}
 assert.equal(validateDebug(detected,{...target,kind:'detection',fullId:undefined,sourceHash:sha}).kind,'detection')
 assert.throws(()=>validateDebug(detected,{...target,kind:'detection',sourceHash:'b'.repeat(64)}))
})
test('histogram consumes exact 256 raw counts and checks scope/hash/sum; Adaptive has no global t',()=>{
 assert.equal(readHistogram(data).histogram.otsu_threshold,123)
 for(const change of [{counts:[1,2]},{counts:[-1,...Array(255).fill(0)]},{pixel_count:99},{source_png_sha256:'b'.repeat(64)},{threshold_scope:'local'}]){
  assert.ok(readHistogram({...data,metadata:{...data.metadata,histogram:{...data.metadata.histogram,...change}}}).error)
 }
 const local={...data,metadata:{...data.metadata,otsu_threshold:null,histogram:{...data.metadata.histogram,threshold_method:'adaptive_gaussian',threshold_scope:'local',otsu_threshold:null}}}
 assert.equal(readHistogram(local).histogram.otsu_threshold,null)
 assert.equal(readHistogram({...data,metadata:{...data.metadata,histogram:null}}).histogram,null)
})
test('score components use stored features, never replace missing numbers with zero',()=>{
 assert.deepEqual(scoreParts({area_ratio:.5,edge_support:.8,fit_area_ratio:.9,border_penalty:.1}),[.225,.27999999999999997,.18000000000000002,-.015])
 assert.equal(scoreParts({area_ratio:.5}),null)
})
function deferred(){let resolve,reject;const promise=new Promise((a,b)=>{resolve=a;reject=b});return{promise,resolve,reject}}
test('debug GET can retry, but an older load or unmounted response cannot populate viewer',async()=>{
 const old=deferred(),fresh=deferred();let calls=0
 const store=createDebugState(target,()=>++calls===1?old.promise:fresh.promise)
 store.connect();const a=store.load();const b=store.load();fresh.resolve(data);await b;old.resolve({...data,run_id:'old'});await a
 assert.equal(store.getSnapshot().data.run_id,'run')
 const pending=deferred();const other=createDebugState(target,()=>pending.promise);other.connect();const c=other.load();other.disconnect();pending.resolve(data);await c
 assert.equal(other.getSnapshot().data,null)
})
test('invalid identity and GET errors have visible failure state and no substituted data',async()=>{
 let fail=true;const store=createDebugState(target,async()=>{if(fail)throw new Error('offline');return data})
 store.connect();await store.load();assert.match(store.getSnapshot().error,/offline/);assert.equal(store.getSnapshot().data,null)
 fail=false;await store.load();assert.equal(store.getSnapshot().data.run_id,'run')
 const bad=createDebugState(target,async()=>({...data,run_id:'old'}));bad.connect();await bad.load();assert.ok(bad.getSnapshot().error);assert.equal(bad.getSnapshot().data,null)
})
