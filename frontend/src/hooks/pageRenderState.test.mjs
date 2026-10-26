import assert from 'node:assert/strict'
import { test } from 'node:test'
import { createPageRender } from './pageRenderState.ts'

const quad = [[.1,.1],[.9,.1],[.9,.9],[.1,.9]]
const config = { mode: 'color', corners: quad, confirmed: true, rotation: 90,
  denoise: { method: 'none', kernel: 5 }, contrast: { method: 'clahe', clip_limit: 3, tile_grid: [8,8] },
  threshold: { method: 'otsu', block_size: 51, c: 9 }, geometry: { aspect_policy: 'estimated', max_long_edge: 2400 } }
const page = { id: 'p', session_id: 's', normalized_artifact_id: 'source', width: 480, height: 640,
  revision: 4, render_revision: null, effective_config: config }
const result = revision => ({ page_id: 'p', revision, render_artifact_id: 'full', preview_artifact_id: 'preview',
  width: 511, height: 383, warnings: [], timings_ms: { 'core.total': 12 } })
function deferred() { let resolve, reject; const promise = new Promise((a,b) => { resolve=a; reject=b }); return {promise,resolve,reject} }
async function setup(overrides = {}) {
  let saved = structuredClone(page)
  const requests = []
  const api = {
    detail: async () => ({ id: 's', pages: [saved] }),
    saveConfig: async (sid,pid,revision,next) => {
      requests.push({sid,pid,revision,config:structuredClone(next)})
      assert.equal(revision, saved.revision)
      saved = {...saved, revision: revision + (JSON.stringify(next)!==JSON.stringify(saved.effective_config) ? 1 : 0), effective_config:structuredClone(next)}
      return {page_id:pid, revision:saved.revision, effective_config:saved.effective_config, inactive_fields:[]}
    },
    render: async (sid,pid,revision) => { requests.push({render:revision}); return result(revision) }, ...overrides,
  }
  const store = createPageRender(structuredClone(page), api)
  store.connect()
  await store.reload()
  return {store, requests}
}
const edit = store => store.editCorners([[.2,.1],...structuredClone(quad.slice(1))])

test('reopening hydrates saved render without POST and never copies detector corners into persisted draft',async()=>{
 const savedRender={...result(4),render_run_id:'stored-run'}
 const detection={page_id:'p',run_id:'detect-run',source_artifact_id:'source',source_revision:3,source_width:480,source_height:640,confirmed:false,corners:null}
 const {store,requests}=await setup({detail:async()=>({id:'s',pages:[{...page,render_revision:4,latest_render:savedRender,latest_detection:detection}]})})
 assert.deepEqual(store.getSnapshot().result,savedRender)
 assert.deepEqual(store.getSnapshot().draft,config)
 assert.equal(store.getSnapshot().detectionRun.run_id,'detect-run');assert.equal(store.getSnapshot().detection,null)
 assert.deepEqual(requests,[])
})

test('manual rotation edits only the draft, keeps corners/confirmation, then persists on explicit render',async()=>{
 const {store,requests}=await setup();store.editProcessing({rotation:270})
 assert.equal(store.getSnapshot().draft.rotation,270);assert.equal(store.getSnapshot().draft.confirmed,true)
 assert.deepEqual(store.getSnapshot().draft.corners,quad);assert.deepEqual(requests,[])
 await store.render();assert.equal(requests[0].config.rotation,270)
})

test('reopen rejects foreign render/detection and future revisions instead of displaying them',async()=>{
 for(const extra of [{latest_render:{...result(4),page_id:'other',render_run_id:'r'}},
   {latest_render:{...result(5),render_run_id:'r'}},
   {latest_detection:{page_id:'p',source_artifact_id:'foreign',source_width:480,source_height:640,source_revision:4,confirmed:false}}]){
  const {store}=await setup({detail:async()=>({id:'s',pages:[{...page,...extra}]})})
  assert.equal(store.getSnapshot().result,null);assert.equal(store.getSnapshot().needsReload,true)
 }
})

test('processing edits keep confirmed corners, full inactive values and persisted config until explicit render', async () => {
  const {store,requests} = await setup()
  const denoise={method:'gaussian',kernel:3}
  store.editProcessing({mode:'gray',denoise})
  denoise.kernel=5
  assert.equal(store.getSnapshot().draft.denoise.kernel,3)
  assert.equal(store.getSnapshot().draft.confirmed,true)
  assert.deepEqual(store.getSnapshot().draft.corners,quad)
  assert.deepEqual(store.getSnapshot().persisted.effective_config,config)
  assert.deepEqual(store.getSnapshot().draft.threshold,config.threshold)
  assert.equal(requests.length,0)
  await store.render()
  assert.equal(requests[0].revision,4)
  assert.equal(requests[0].config.mode,'gray')
  assert.deepEqual(requests[0].config,{...config,mode:'gray',denoise:{method:'gaussian',kernel:3}})
  assert.deepEqual(requests[0].config.threshold,config.threshold)
  assert.deepEqual(requests[1],{render:5})
  store.editProcessing({mode:'color'})
  assert.equal(store.getSnapshot().result.revision,5)
  assert.equal(store.getSnapshot().draft.contrast.method,'clahe')
  store.reset()
  assert.equal(store.getSnapshot().draft.mode,'gray')
})

test('rapid threshold changes send no requests and retain block/C across Otsu and mode switches', async () => {
  const {store,requests} = await setup()
  store.editProcessing({mode:'bw',threshold:{method:'adaptive_gaussian',block_size:3,c:-20}})
  store.editProcessing({threshold:{method:'adaptive_gaussian',block_size:151,c:30}})
  store.editProcessing({threshold:{method:'otsu',block_size:151,c:30}})
  store.editProcessing({mode:'color'})
  store.editProcessing({mode:'bw'})
  assert.equal(requests.length,0)
  assert.deepEqual(store.getSnapshot().draft.threshold,{method:'otsu',block_size:151,c:30})
  await store.render()
  assert.deepEqual(requests.map(r=>r.render ?? r.config.threshold),[{method:'otsu',block_size:151,c:30},5])
  edit(store)
  store.editProcessing({denoise:{method:'median',kernel:5}})
  assert.equal(store.getSnapshot().draft.confirmed,false)
  await store.render()
  assert.equal(requests.length,2)
})

test('processing edit while save or render is pending keeps the newer draft and ignores late output', async () => {
  for (const stage of ['saveConfig','render']) {
    const gate=deferred()
    const {store,requests}=await setup({[stage]:()=>gate.promise})
    const run=store.render();await Promise.resolve()
    store.editProcessing({mode:'bw',threshold:{method:'otsu',block_size:3,c:-20}})
    gate.resolve(stage==='saveConfig' ? {page_id:'p',revision:4,effective_config:config,inactive_fields:[]} : result(4))
    await run
    assert.equal(store.getSnapshot().draft.mode,'bw')
    assert.equal(store.getSnapshot().draft.confirmed,true)
    assert.equal(store.getSnapshot().result,null)
    assert.equal(requests.some(r=>r.render),false)
  }
})

test('edit revokes confirmation; full image and reset preserve inactive full config', async () => {
  const {store} = await setup()
  edit(store)
  assert.equal(store.getSnapshot().draft.confirmed,false)
  assert.equal(store.getSnapshot().persisted.effective_config.confirmed,true)
  store.fullImage()
  assert.deepEqual(store.getSnapshot().draft.corners,[[0,0],[1,0],[1,1],[0,1]])
  assert.equal(store.getSnapshot().draft.confirmed,false)
  assert.deepEqual(store.getSnapshot().draft.threshold,config.threshold)
  store.reset()
  assert.deepEqual(store.getSnapshot().draft, config)
})
test('draft cannot render; explicit confirmation saves full config and render uses returned revision', async () => {
  const {store,requests} = await setup()
  edit(store)
  await store.render()
  assert.equal(requests.length,0)
  await store.save(true)
  assert.equal(store.getSnapshot().draft.confirmed,true)
  assert.deepEqual(requests[0].config.threshold,config.threshold)
  await store.render()
  assert.deepEqual(requests.at(-1),{render:5})
  assert.equal(store.getSnapshot().result.revision,5)
})
test('save draft persists false; invalid quad is never sent or confirmed', async () => {
  const {store,requests} = await setup()
  edit(store); await store.save(false)
  assert.equal(requests[0].config.confirmed,false)
  store.editCorners([quad[0],quad[2],quad[1],quad[3]])
  await store.save(true)
  assert.equal(requests.length,1)
  assert.equal(store.getSnapshot().draft.confirmed,false)
})
test('edit during config save preserves new draft and prevents automatic render', async () => {
  const gate = deferred()
  const {store,requests} = await setup({ saveConfig: () => gate.promise })
  const run = store.render()
  edit(store)
  gate.resolve({page_id:'p', revision:4,effective_config:config,inactive_fields:[]})
  await run
  assert.equal(store.getSnapshot().draft.confirmed,false)
  assert.equal(store.getSnapshot().draft.corners[0][0],.2)
  assert.equal(requests.length,0)
  assert.equal(store.getSnapshot().result,null)
})
test('late render after editing is ignored; previous successful result survives failure', async () => {
  let gate
  const {store} = await setup({render: () => gate ? gate.promise : Promise.resolve(result(4))})
  await store.render()
  const old = store.getSnapshot().result
  gate=deferred(); const run=store.render(); await Promise.resolve(); edit(store)
  gate.resolve({...result(4),preview_artifact_id:'late'}); await run
  assert.deepEqual(store.getSnapshot().result,old)
  store.reset(); gate=deferred(); const failed=store.render(); await Promise.resolve()
  gate.reject(new Error('PROCESSING_FAILED')); await failed
  assert.deepEqual(store.getSnapshot().result,old)
  assert.match(store.getSnapshot().error,/PROCESSING_FAILED/)
})
test('unmount/page switch invalidates pending save and render', async () => {
  for (const stage of ['saveConfig','render']) {
    const gate=deferred()
    const {store}=await setup({[stage]:()=>gate.promise})
    const run=store.render(); await Promise.resolve(); const before=store.getSnapshot()
    store.disconnect()
    gate.resolve(stage==='render' ? result(4) : {page_id:'p',revision:4,effective_config:config,inactive_fields:[]})
    await run
    assert.equal(store.getSnapshot(),before)
  }
})
test('foreign page or revision response is rejected, never displayed', async () => {
  for (const response of [{...result(4),page_id:'other'},result(3),result(5)]) {
    const {store}=await setup({render:async()=>response})
    await store.render()
    assert.equal(store.getSnapshot().result,null)
    assert.equal(store.getSnapshot().needsReload,true)
  }
})
test('unknown save outcome blocks retry until GET reconciliation; draft is kept unconfirmed', async () => {
  let attempts=0
  const {store}=await setup({saveConfig:async()=>{attempts++; throw new Error('NETWORK_ERROR')}})
  edit(store); await store.save(true); await store.save(true); await store.render()
  assert.equal(attempts,1)
  assert.equal(store.getSnapshot().needsReload,true)
  await store.reload()
  assert.equal(store.getSnapshot().draft.corners[0][0],.2)
  assert.equal(store.getSnapshot().draft.confirmed,false)
  assert.equal(store.getSnapshot().persisted.revision,4)
  assert.equal(store.getSnapshot().needsReload,false)
})
test('duplicate clicks send one mutation', async () => {
  const {store,requests}=await setup()
  const a=store.render(); const b=store.render(); await Promise.all([a,b])
  assert.equal(requests.filter(x=>'render' in x).length,1)
})
test('old GET after reconnect cannot overwrite a newer response', async () => {
  const gate=deferred(); let calls=0
  const store=createPageRender(page,{detail:()=> ++calls===1 ? gate.promise : Promise.resolve({id:'s',pages:[{...page,revision:7}]})})
  store.connect(); const old=store.reload(); store.disconnect(); store.connect(); await store.reload()
  gate.resolve({id:'s',pages:[page]}); await old
  assert.equal(store.getSnapshot().persisted.revision,7)
})
test('cancel restores confirmation and the exact full pre-drag snapshot', async () => {
  const {store}=await setup(), before=structuredClone(config)
  edit(store); store.restoreDraft(before)
  assert.deepEqual(store.getSnapshot().draft,config)
  before.corners[0][0]=.3
  assert.equal(store.getSnapshot().draft.corners[0][0],.1)
})
test('wrong config page/revision/payload never becomes persisted or starts render', async () => {
  for(const bad of [{page_id:'foreign',revision:4,effective_config:config},
    {page_id:'p',revision:6,effective_config:config},
    {page_id:'p',revision:4,effective_config:{...config,confirmed:false}}]) {
    const {store,requests}=await setup({saveConfig:async()=>bad})
    await store.render()
    assert.equal(store.getSnapshot().needsReload,true)
    assert.deepEqual(store.getSnapshot().persisted.effective_config,config)
    assert.equal(requests.length,0)
  }
})

const detected = {page_id:'p',run_id:'run',source_artifact_id:'source',source_revision:4,
  source_sha256:'a'.repeat(64),source_width:480,source_height:640,status:'proposed',corners:quad,
  confirmed:false,heuristic_score:.8,algorithm_version:'detect-v1',selected_trial_id:'canny_20_60',
  warnings:[],stage_artifacts:{},timings_ms:{'core.total':12}}

test('new imports open saved auto detection as an unconfirmed draft without PUT/render/detect',async()=>{
 for(const status of ['proposed','proposed_with_warning','manual_required']){
  const fresh={...structuredClone(page),revision:0,effective_config:{...structuredClone(config),corners:null,confirmed:false},
   latest_detection:{...structuredClone(detected),source_revision:0,status,
    corners:status==='manual_required'?null:structuredClone(quad),heuristic_score:status==='manual_required'?null:.8}}
  const requests=[]
  const store=createPageRender(fresh,{detail:async()=>({id:'s',pages:[fresh]}),
   saveConfig:async()=>requests.push('PUT'),render:async()=>requests.push('render'),detect:async()=>requests.push('detect')})
  store.connect();await store.reload()
  assert.deepEqual(store.getSnapshot().draft.corners,status==='manual_required'?[[.05,.05],[.95,.05],[.95,.95],[.05,.95]]:quad)
  assert.equal(store.getSnapshot().draft.confirmed,false)
  assert.equal(store.getSnapshot().persisted.effective_config.corners,null)
  assert.equal(store.getSnapshot().detection.status,status)
  store.editCorners([[.2,.1],...structuredClone(quad.slice(1))]);await store.reload()
  assert.equal(store.getSnapshot().draft.corners[0][0],.2);assert.equal(store.getSnapshot().detection,null)
  assert.deepEqual(requests,[])
 }
})

test('saved manual corners and later revisions are not replaced by old auto detection',async()=>{
 for(const change of [{revision:1,effective_config:{...config,corners:null,confirmed:false}},
  {revision:0,effective_config:{...config,corners:quad,confirmed:false}}]){
  const fresh={...structuredClone(page),...structuredClone(change),latest_detection:{...detected,source_revision:0,
   corners:[[.2,.2],[.8,.2],[.8,.8],[.2,.8]]}}
  const store=createPageRender(fresh,{detail:async()=>({id:'s',pages:[fresh]})})
  store.connect();await store.reload()
  assert.deepEqual(store.getSnapshot().draft.corners,change.effective_config.corners??[[.05,.05],[.95,.05],[.95,.95],[.05,.95]])
  assert.equal(store.getSnapshot().detection,null)
 }
})
test('detect proposal changes only draft corners, never confirms or sends config/render',async()=>{
 const {store,requests}=await setup({detect:async()=>detected})
 await store.detect()
 assert.equal(store.getSnapshot().draft.confirmed,false)
 assert.deepEqual(store.getSnapshot().draft.corners,quad)
 assert.deepEqual(store.getSnapshot().draft.threshold,config.threshold)
 assert.deepEqual(store.getSnapshot().persisted.effective_config,config)
 assert.equal(store.getSnapshot().detection.run_id,'run')
 store.editProcessing({mode:'gray'})
 assert.equal(store.getSnapshot().detection,null)
 assert.equal(store.getSnapshot().detectionRun.run_id,'run')
 assert.equal(requests.length,0)
})
test('manual_required uses editable 5 percent fallback; API failure preserves draft',async()=>{
 const {store}=await setup({detect:async()=>({...detected,status:'manual_required',corners:null,heuristic_score:null,warnings:['NO_VALID_QUAD']})})
 await store.detect()
 assert.deepEqual(store.getSnapshot().draft.corners,[[.05,.05],[.95,.05],[.95,.95],[.05,.95]])
 assert.equal(store.getSnapshot().draft.confirmed,false)
 const other=await setup({detect:async()=>{throw new Error('PROCESSING_BUSY')}})
 await other.store.detect()
 assert.deepEqual(other.store.getSnapshot().draft,config)
 assert.equal(other.store.getSnapshot().needsReload,false)
})
test('detect delayed after edit, processing change, reset or unmount cannot replace current draft',async()=>{
 for(const action of ['edit','processing','reset','unmount']) {
  const gate=deferred();const {store}=await setup({detect:()=>gate.promise})
  const run=store.detect()
  if(action==='edit')edit(store)
  if(action==='processing')store.editProcessing({mode:'gray'})
  if(action==='reset')store.reset()
  if(action==='unmount')store.disconnect()
  const before=structuredClone(store.getSnapshot().draft)
  gate.resolve(detected);await run
  assert.deepEqual(store.getSnapshot().draft,before)
  assert.equal(store.getSnapshot().detection,null)
 }
})
test('wrong detection source/page/dimensions or confirmed result is rejected',async()=>{
 for(const change of [{page_id:'foreign'},{source_artifact_id:'other'},{source_width:481},{source_revision:5},{confirmed:true},
  {status:'proposed',corners:[[0,0],[1,1],[1,0],[0,1]]}]) {
  const {store}=await setup({detect:async()=>({...detected,...change})})
  await store.detect()
  assert.deepEqual(store.getSnapshot().draft,config)
  assert.equal(store.getSnapshot().detection,null)
  assert.ok(store.getSnapshot().error)
  if(change.source_revision) assert.equal(store.getSnapshot().needsReload,true)
 }
})
