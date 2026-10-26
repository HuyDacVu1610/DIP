import {useEffect,useState,useSyncExternalStore} from 'react'
import {artifactUrl,debugUrl,scannerApi} from '../api/client'
import {createDebugState} from '../hooks/debugState'
import type {DebugArtifact,DebugRead,DetectionRead,PageRead,RenderRead} from '../types/scanner'
import {record} from './pipelineData'
import type {DebugTarget} from './pipelineData'
import {explainStage,stageLabel} from './pipelineExplanation'
import {CandidateMetrics} from './CandidateMetrics'
import {HistogramView} from './HistogramView'

function StageImage({artifact,label}:{artifact:DebugArtifact;label:string}) {
  const [state,setState]=useState<'loading'|'ready'|'error'>('loading'),[attempt,setAttempt]=useState(0)
  return <figure className="debug-stage">
    {state==='loading'&&<p role="status">Đang tải stage đã lưu…</p>}
    <img key={attempt} src={artifactUrl(artifact.id)} alt={label} hidden={state!=='ready'}
      onLoad={e=>setState(e.currentTarget.naturalWidth===artifact.width&&e.currentTarget.naturalHeight===artifact.height?'ready':'error')}
      onError={()=>setState('error')} />
    {state==='error'&&<div role="alert"><p>Không tải được stage đúng kích thước. Không dùng ảnh khác thay thế.</p>
      <button className="secondary" onClick={()=>{setState('loading');setAttempt(n=>n+1)}}>Thử lại ảnh stage</button></div>}
    <figcaption className="small">{artifact.width} × {artifact.height} px · {artifact.kind} · revision {artifact.revision}
      <span className="hash-text">SHA-256: {artifact.sha256}</span></figcaption>
  </figure>
}

function RunContent({data,stale}:{data:DebugRead;stale:boolean}) {
  const meta=record(data.metadata),refs=record(meta.artifacts),[selected,setSelected]=useState('')
  const preferred=data.kind==='detection'?'contour_overlay':record(meta.effective_config).mode==='bw'?'prepared_gray':'full'
  const names=data.kind==='render'?['warp','filtered_bgr','prepared_gray','before_rotation','full','preview']
    :[...new Set(['analysis','gray','blurred','contour_overlay',...Object.keys(refs),...Object.keys(data.missing_stages)])]
  const name=names.includes(selected)?selected:preferred,artifact=data.artifacts[name]
  const reason=data.missing_stages[name]??record(meta.stage_status)[name]
  return <>
    <p className="hash-text small">Run {data.run_id} · {String(meta.pipeline_version??meta.algorithm_version??'version chưa lưu')}
      {' '}· {data.created_at} · {data.kind==='render'?`render revision ${data.revision}`:'nhận diện nguồn'} · config hiện hành {data.current_revision}</p>
    {data.kind==='render'&&(stale||data.revision!==data.current_revision)&&<p role="status" className="debug-warning">Debug của bản quét trước; chưa áp dụng bản nháp hiện tại. Các số dưới đây thuộc snapshot đã lưu.</p>}
    {data.kind==='detection'&&<p className="muted small">Lượt nhận diện nguồn trước warp. Chỉnh góc tay hoặc đổi bộ lọc không chạy lại các stage này.</p>}
    {data.status!=='available'&&<p role="status" className="debug-warning">Trạng thái debug: {data.status}.
      {' '}{data.status==='not_requested'?'Lượt này không yêu cầu lưu debug. Tạo lại bản quét để có stage mới.':'Một số stage thiếu hoặc không khớp; không ghép với run khác.'}</p>}
    {Object.keys(data.missing_stages).length>0&&<ul className="small">{Object.entries(data.missing_stages).map(([n,r])=><li key={n}>Stage {n}: {r}</li>)}</ul>}
    <label className="debug-stage-select">Bước xử lý đang xem
      <select aria-label="Bước xử lý đang xem" value={name} onChange={e=>setSelected(e.target.value)}>
        {names.map(n=><option key={n} value={n}>{stageLabel[n]??n}{data.artifacts[n]?'':' · chưa có ảnh'}</option>)}
      </select>
    </label>
    <p className="stage-explanation">{explainStage(name,meta,data.kind)}</p>
    <div className="pipeline-grid">
      {artifact?<StageImage key={artifact.id} artifact={artifact} label={`Stage ${stageLabel[name]??name}`} />
        :<div className="debug-stage" role="status">Không có ảnh stage “{stageLabel[name]??name}”: {String(reason??(data.debug_persisted?'chưa được lưu':'debug chưa được yêu cầu'))}. Không dựng ảnh minh họa thay thế.</div>}
      {data.kind==='detection'?<CandidateMetrics data={data}/>:<HistogramView data={data}/>}
    </div>
    <details><summary>Cấu hình, đơn vị và timing của run</summary><pre>{JSON.stringify({
      effective_config:meta.effective_config,inactive_fields:meta.inactive_fields,preset:meta.preset,
      source:meta.source,units:meta.units,homography_source_to_warp:meta.homography_source_to_warp,
      timings_ms:meta.timings_ms,timings_scope:meta.timings_scope},null,2)}</pre></details>
  </>
}

function RunDebug({target,sid,stale}:{target:DebugTarget;sid:string;stale:boolean}) {
  const [store]=useState(()=>createDebugState(target,signal=>scannerApi.debug(sid,target.pageId,target.kind,target.runId,signal)))
  const {data,busy,error}=useSyncExternalStore(store.subscribe,store.getSnapshot)
  useEffect(()=>{store.connect();void store.load();return store.disconnect},[store])
  return <div className="run-debug" aria-busy={busy} data-run-id={target.runId} data-debug-kind={target.kind}>
    <div className="debug-tools"><button className="secondary" disabled={busy} onClick={()=>void store.load()}>Đọc lại debug</button>
      <a href={debugUrl(sid,target.pageId,target.kind,target.runId)} target="_blank" rel="noreferrer">Mở JSON của lượt này</a></div>
    {busy&&<p role="status">Đang đọc debug của đúng lượt xử lý…</p>}
    {error&&<p role="alert" className="error">{error}</p>}
    {data&&<RunContent data={data} stale={stale}/>}
  </div>
}

export function PipelineViewer({page,detection,result,stale}:{page:PageRead;detection:DetectionRead|null;result:RenderRead|null;stale:boolean}) {
  const [expanded,setExpanded]=useState(false),[choice,setChoice]=useState<'render'|'detection'>('render')
  useEffect(()=>{if(result)setChoice('render')},[result?.render_run_id])
  const kind=choice==='detection'&&detection?'detection':result?'render':'detection'
  const runId=kind==='render'?result?.render_run_id:detection?.run_id
  const target:DebugTarget|undefined=runId?{kind,runId,pageId:page.id,sourceId:page.normalized_artifact_id,width:page.width,height:page.height,
    revision:kind==='render'?result!.revision:detection!.source_revision,
    sourceHash:kind==='detection'?detection!.source_sha256:undefined,
    fullId:kind==='render'?result!.render_artifact_id:undefined,previewId:kind==='render'?result!.preview_artifact_id:undefined}:undefined
  return <details className="pipeline-viewer" open={expanded} onToggle={e=>setExpanded(e.currentTarget.open)}>
    <summary>Xem các bước xử lý và histogram</summary>
    <div className="scan-actions" role="group" aria-label="Chọn nhóm debug">
      <button className="secondary" disabled={!detection} aria-pressed={kind==='detection'} onClick={()=>setChoice('detection')}>Nhận diện vùng</button>
      <button className="secondary" disabled={!result} aria-pressed={kind==='render'} onClick={()=>setChoice('render')}>Xử lý bản quét</button>
    </div>
    {expanded&&(target?<RunDebug key={`${target.kind}:${target.runId}`} target={target} sid={page.session_id} stale={stale}/>
      :<p role="status">Chưa có run ID cho nhóm này. Hãy tự nhận diện hoặc tạo bản quét mới; không lấy debug của một revision khác thay thế.</p>)}
    <details className="algorithm-guide"><summary>Thuật toán, biểu diễn và giới hạn</summary>
      <ol>
        <li><strong>Phát hiện:</strong> Gaussian giảm nhiễu, Canny tìm gián đoạn mức sáng, closing nối hở nhỏ. Edge map chưa phải vùng giấy; chữ/nếp gấp/bóng cũng sinh biên.</li>
        <li><strong>Biểu diễn:</strong> findContours lấy chuỗi điểm có thứ tự (CHAIN_APPROX_SIMPLE); Douglas–Peucker xấp xỉ Q với ε/P=.015/.02/.03. Đây không phải thuật toán đa giác chu vi tối thiểu MPP trong slide. Không tự nhận findContours chính là Moore.</li>
        <li><strong>Mô tả biên:</strong> chu vi, số đỉnh, độ dài cạnh, góc đổi hướng và độ lồi/tự giao. Độ dài đo ở analysis px; tọa độ Q và góc normalized nguồn là dữ liệu biểu diễn, không phải cùng loại với descriptor.</li>
        <li><strong>Vùng và chọn ứng viên:</strong> a là diện tích tương đối, f khớp diện tích, e hỗ trợ raw edge, b sát khung. S/trọng số là heuristic dự án; NMS loại trùng khi IoU&gt;.95. S≥.60 đề xuất, .40≤S&lt;.60 cảnh báo, dưới.40/không có quad yêu cầu tay; mọi đề xuất vẫn cần xác nhận.</li>
        <li><strong>Nhánh vùng:</strong> chỉ khi ba Canny không sinh quad hợp lệ mới thử Otsu vùng sáng. Vùng bàn có thể dính giấy. Otsu trước warp tìm vùng giấy khác Otsu sau warp tách chữ.</li>
        <li><strong>Hiệu chỉnh:</strong> homography dùng nguồn đầy đủ/bốn góc đúng chu kỳ; giấy chữ nhật trong cảnh có thể có góc xiên. Không ép 90°, không dewarp giấy cong/nhàu bằng một homography.</li>
        <li><strong>Độ đọc:</strong> None/Median/Gaussian → Color hoặc Gray/CLAHE → BW Otsu/Adaptive nếu chọn → xoay. Color giữ highlight; BW có thể mất sắc độ/dấu mảnh. Histogram không chứng minh đã chọn đúng giấy.</li>
      </ol>
      <p className="muted small">Đối chiếu giáo trình chương5–6 và slide Ch05/Ch06 trong docs. Bộ thực nghiệm còn ít, mỗi tập development/test chỉ có một tài liệu; xem báo cáo để biết phạm vi số đo. Chưa có accuracy tổng quát. Trường hợp img_004/006 vẫn có thể ăn bàn, cần chỉnh góc tay.</p>
    </details>
  </details>
}
