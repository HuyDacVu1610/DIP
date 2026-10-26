import assert from 'node:assert/strict'
import {test} from 'node:test'
import {createUploadBatch} from './uploadBatch.ts'
import {ApiError} from '../api/client.ts'
const file=name=>new File(['x'],name)
const deferred=()=>{let resolve;const promise=new Promise(r=>resolve=r);return{promise,resolve}}

test('one sequential batch holds its lock through reconciliation; duplicate call cannot start',async()=>{
 const run=createUploadBatch(),first=deferred(),reconcile=deferred(),calls=[],busy=[],states=[]
 const options={files:[file('a.png'),file('b.png')],remainingSlots:2,onBusy:v=>busy.push(v),onResults:v=>states.push(v),
  onUpload:async f=>{calls.push(f.name);if(f.name==='a.png')await first.promise},onFinished:()=>reconcile.promise}
 const pending=run(options);await run(options);assert.deepEqual(calls,['a.png'])
 first.resolve();await new Promise(resolve=>setImmediate(resolve));assert.deepEqual(calls,['a.png','b.png'])
 await run(options);assert.deepEqual(calls,['a.png','b.png']);assert.deepEqual(busy,[true])
 reconcile.resolve();await pending;assert.deepEqual(busy,[true,false])
 assert.deepEqual(states.at(-1).map(s=>s.state),['done','done'])
})

test('failed file does not consume a slot; excess files are reported without uploading',async()=>{
 const calls=[],states=[]
 await createUploadBatch()({files:[file('bad.jpg'),file('ok.png'),file('extra.png')],remainingSlots:1,onBusy:()=>{},onResults:v=>states.push(v),
  onUpload:async f=>{calls.push(f.name);if(f.name==='bad.jpg')throw new Error('Ảnh lỗi')},onFinished:async()=>{}})
 assert.deepEqual(calls,['bad.jpg','ok.png'])
 assert.deepEqual(states.at(-1).map(s=>s.state),['error','done','error'])
 assert.match(states.at(-1)[2].message,/20 trang/)
})

test('15MiB local rejection does not upload; subsequent valid files continue and reconcile once',async()=>{
 let calls=0,finished=0,last=[]
 await createUploadBatch()({files:[{name:'large.jpg',size:15*1024*1024+1},file('ok.png')],remainingSlots:20,onBusy:()=>{},onResults:v=>last=v,
  onUpload:async()=>{calls++},onFinished:async()=>{finished++}})
 assert.equal(calls,1);assert.equal(finished,1);assert.match(last[0].message,/15 MiB/);assert.equal(last[1].state,'done')
})

test('authoritative backend page limit stops remaining uploads and the batch can be used again',async()=>{
 let calls=0,last=[];const run=createUploadBatch()
 const options={files:[file('a.png'),file('b.png')],remainingSlots:2,onBusy:()=>{},onResults:v=>last=v,
  onUpload:async()=>{calls++;throw new ApiError('PAGE_LIMIT_EXCEEDED','Đã đủ 20 trang',413)},onFinished:async()=>{}}
 await run(options);assert.equal(calls,1);assert.deepEqual(last.map(s=>s.state),['error','error'])
 await run({...options,files:[file('next.png')],onUpload:async()=>{calls++}});assert.equal(calls,2);assert.equal(last[0].state,'done')
})
