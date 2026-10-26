import assert from 'node:assert/strict'
import {test} from 'node:test'
import {scannerApi} from './client.ts'

test('export sends exact snapshot/options and preserves missing-render details without retry',async()=>{
 const original=globalThis.fetch,calls=[]
 const body={pages:[{page_id:'b',revision:3},{page_id:'a',revision:2}],format:'pdf',paper_size:'a4',orientation:'auto',margin_mm:5,image_encoding:'png'}
 const pages=[body.pages[0]]
 globalThis.fetch=async(url,options)=>{calls.push({url,options});return new Response(JSON.stringify({
   error:{code:'PAGE_NOT_RENDERED',message:'Missing',details:{pages}}}),{status:409})}
 try{
  await assert.rejects(scannerApi.export('s',body),e=>e.code==='PAGE_NOT_RENDERED'&&e.status===409&&JSON.stringify(e.details.pages)===JSON.stringify(pages))
  assert.equal(calls.length,1);assert.equal(calls[0].url,'/api/v1/sessions/s/exports')
  assert.equal(calls[0].options.method,'POST');assert.deepEqual(JSON.parse(calls[0].options.body),body)
 }finally{globalThis.fetch=original}
})

test('config sends full payload/CAS; render sends exactly its returned revision; no mutation retry', async()=> {
  const original=globalThis.fetch, calls=[]
  globalThis.fetch=async(url,options)=>{calls.push({url,options});return new Response(JSON.stringify({page_id:'p',revision:8}),{status:200})}
  try {
    const full={mode:'color',corners:[[0,0],[1,0],[1,1],[0,1]],confirmed:true,rotation:0,
      denoise:{method:'none',kernel:5},contrast:{method:'clahe',clip_limit:2,tile_grid:[8,8]},
      threshold:{method:'otsu',block_size:51,c:9},geometry:{aspect_policy:'estimated',max_long_edge:2400}}
    const saved=await scannerApi.saveConfig('s','p',7,full)
    await scannerApi.render('s','p',saved.revision)
    await scannerApi.detect('s','p')
    assert.deepEqual(JSON.parse(calls[0].options.body),{expected_revision:7,config:full})
    assert.deepEqual(JSON.parse(calls[1].options.body),{expected_revision:8,debug:true})
    assert.equal(calls[0].options.method,'PUT');assert.equal(calls[1].options.method,'POST')
    assert.equal(calls[2].url,'/api/v1/sessions/s/pages/p/detect')
    assert.deepEqual(JSON.parse(calls[2].options.body),{debug:true})
    const controller=new AbortController()
    await scannerApi.debug('s','p','render','render-run',controller.signal)
    await scannerApi.debug('s','p','detection','detect-run',controller.signal)
    assert.equal(calls[3].url,'/api/v1/sessions/s/pages/p/debug?render_run_id=render-run')
    assert.equal(calls[4].url,'/api/v1/sessions/s/pages/p/debug?detection_run_id=detect-run')
    assert.equal(calls[3].options.signal,controller.signal)
    let attempts=0;globalThis.fetch=async()=>{attempts++;throw new Error('offline')}
    await assert.rejects(scannerApi.saveConfig('s','p',7,full),error=>error.code==='NETWORK_ERROR')
    assert.equal(attempts,1)
  } finally {globalThis.fetch=original}
})

test('rename PATCH sends only the title and never retries a failed mutation',async()=>{
 const original=globalThis.fetch,calls=[]
 globalThis.fetch=async(url,options)=>{calls.push({url,options});return new Response(JSON.stringify({id:'s',title:'Tên mới'}),{status:200})}
 try{
  await scannerApi.rename('s','Tên mới')
  assert.equal(calls[0].url,'/api/v1/sessions/s')
  assert.equal(calls[0].options.method,'PATCH')
  assert.deepEqual(JSON.parse(calls[0].options.body),{title:'Tên mới'})
  let attempts=0;globalThis.fetch=async()=>{attempts++;throw new Error('offline')}
  await assert.rejects(scannerApi.rename('s','Tên mới'));assert.equal(attempts,1)
 }finally{globalThis.fetch=original}
})

test('order sends full IDs and DELETE accepts empty204 without parsing JSON',async()=>{
 const original=globalThis.fetch,calls=[]
 globalThis.fetch=async(url,options)=>{calls.push({url,options});return options.method==='DELETE'?new Response(null,{status:204}):new Response(JSON.stringify({id:'s',pages:[]}),{status:200})}
 try{
  await scannerApi.order('s',['c','a','b']);await scannerApi.deletePage('s','b');await scannerApi.deleteSession('s')
  assert.equal(calls[0].url,'/api/v1/sessions/s/page-order');assert.equal(calls[0].options.method,'PUT')
  assert.deepEqual(JSON.parse(calls[0].options.body),{page_ids:['c','a','b']})
  assert.equal(calls[1].url,'/api/v1/sessions/s/pages/b');assert.equal(calls[2].url,'/api/v1/sessions/s')
  assert.equal(calls[1].options.method,'DELETE');assert.equal(calls[2].options.method,'DELETE')
 }finally{globalThis.fetch=original}
})
