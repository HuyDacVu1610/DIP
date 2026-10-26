"""Frozen held-out evaluation and sequential core/HTTP benchmark on Windows."""
import argparse
import ctypes as ct
from ctypes import wintypes
import csv
from contextlib import contextmanager
from datetime import datetime,timezone
from dataclasses import asdict
from hashlib import sha256
from io import BytesIO
import json
import os
from pathlib import Path
import sys
import socket
import subprocess
import time
from threading import Event,Thread
from time import perf_counter_ns
import urllib.request
import urllib.error
from uuid import uuid4

import cv2
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'backend')]
from experiments.freeze_config import verify_frozen
from experiments.validate_annotations import validate_annotations
from experiments.detection_artifacts import save_png,write_json,write_detection_artifacts
from experiments.metrics import evaluate_quad,aggregate_metrics
from app.processing.detection import detect_document
from app.processing.render import render_document,encode_render_images
from app.processing.image_sizes import resize_to_max_edge


def verify_runtime(path=None):
    # Elevated/child Windows processes can enable OpenCL automatically. Recreate
    # the frozen CPU setting locally; never rewrite or relax the frozen gate.
    path=Path(path) if path is not None else ROOT/'experiments/configs/frozen.json'
    enabled=json.loads(path.read_text(encoding='utf-8'))['snapshot']['environment']['opencv_opencl']
    if type(enabled) is not bool:raise ValueError('OpenCL setting trong snapshot không hợp lệ.')
    cv2.ocl.setUseOpenCL(enabled)
    return verify_frozen(path)


class _MemoryCounters(ct.Structure):
    _fields_=[('cb',wintypes.DWORD),('PageFaultCount',wintypes.DWORD)]+[
        (name,ct.c_size_t) for name in ('PeakWorkingSetSize','WorkingSetSize','QuotaPeakPagedPoolUsage',
        'QuotaPagedPoolUsage','QuotaPeakNonPagedPoolUsage','QuotaNonPagedPoolUsage','PagefileUsage','PeakPagefileUsage')]


def process_memory(pid):
    """Current and lifetime peak working set in bytes (Win32 PSAPI, not tracemalloc)."""
    if os.name!='nt':raise OSError('Benchmark RAM này yêu cầu Windows như môi trường đã khóa.')
    kernel=ct.WinDLL('kernel32',use_last_error=True);psapi=ct.WinDLL('psapi',use_last_error=True)
    kernel.OpenProcess.argtypes=[wintypes.DWORD,wintypes.BOOL,wintypes.DWORD]
    kernel.OpenProcess.restype=wintypes.HANDLE
    kernel.CloseHandle.argtypes=[wintypes.HANDLE];kernel.CloseHandle.restype=wintypes.BOOL
    psapi.GetProcessMemoryInfo.argtypes=[wintypes.HANDLE,ct.POINTER(_MemoryCounters),wintypes.DWORD]
    psapi.GetProcessMemoryInfo.restype=wintypes.BOOL
    handle=kernel.OpenProcess(0x1000,False,pid)  # PROCESS_QUERY_LIMITED_INFORMATION
    if not handle:raise ct.WinError(ct.get_last_error())
    try:
        counters=_MemoryCounters();counters.cb=ct.sizeof(counters)
        if not psapi.GetProcessMemoryInfo(handle,ct.byref(counters),counters.cb):raise ct.WinError(ct.get_last_error())
        return int(counters.WorkingSetSize),int(counters.PeakWorkingSetSize)
    finally:kernel.CloseHandle(handle)


def measure(call,pid):
    baseline=process_memory(pid);samples=[baseline];stop=Event();memory_errors=[]
    def sample():
        while not stop.wait(.01):
            try:samples.append(process_memory(pid))
            except OSError as error:memory_errors.append(str(error));return
    thread=Thread(target=sample,daemon=True);thread.start()
    started=perf_counter_ns();result=None;error=None
    try:result=call()
    except Exception as caught:error=type(caught).__name__+': '+str(caught)
    finally:
        elapsed=(perf_counter_ns()-started)/1e6;stop.set();thread.join()
        samples.append(process_memory(pid))
    if memory_errors:error='RAM sampler: '+memory_errors[0]+('; '+error if error else '')
    return result,{'wall_ms':elapsed,'rss_baseline_bytes':baseline[0],
        'rss_sampled_peak_bytes':max(p[0] for p in samples),'rss_end_bytes':samples[-1][0],
        'process_lifetime_peak_bytes':max(p[1] for p in samples),'rss_samples':len(samples)},error


def summarize_samples(rows):
    measured=[r for r in rows if r['phase']=='measured'];summary={}
    for operation in sorted({r['operation'] for r in measured}):
        group=[r for r in measured if r['operation']==operation];success=[r for r in group if r['ok']]
        times=[r['wall_ms'] for r in success]
        summary[operation]={'attempted':len(group),'successful':len(success),'errors':len(group)-len(success),
            'p50_ms':float(np.quantile(times,.5,method='linear')) if times else None,
            'p95_ms':float(np.quantile(times,.95,method='linear')) if times else None,
            'rss_sampled_peak_bytes':max(r['rss_sampled_peak_bytes'] for r in group)}
    return summary


def load_case(row,label,project_root=ROOT):
    original=(project_root/row['source_path']).read_bytes()
    payload=(project_root/row['normalized_path']).read_bytes()
    if (sha256(original).hexdigest()!=row['source_sha256']
            or sha256(payload).hexdigest()!=row['normalized_sha256']
            or row['normalized_sha256']!=label['normalized_sha256']):
        raise ValueError('Nguồn/nhãn thay đổi sau kiểm tra hash.')
    with Image.open(BytesIO(payload)) as im:
        if im.size!=(label['width'],label['height']):raise ValueError('Dimensions nguồn/nhãn không khớp.')
        source=cv2.cvtColor(np.array(im.convert('RGB')),cv2.COLOR_RGB2BGR)
    source.setflags(write=False)
    return source,payload,original


def http_json(base,method,path,data=None,*,file=None):
    headers={};body=None
    if file is not None:
        boundary='benchmark'+uuid4().hex
        body=('--'+boundary+'\r\nContent-Disposition: form-data; name="file"; filename="input.jpg"\r\n'
              'Content-Type: application/octet-stream\r\n\r\n').encode()+file+('\r\n--'+boundary+'--\r\n').encode()
        headers['Content-Type']='multipart/form-data; boundary='+boundary
    elif data is not None:
        body=json.dumps(data).encode();headers['Content-Type']='application/json'
    request=urllib.request.Request(base+'/api/v1'+path,data=body,headers=headers,method=method)
    try:
        with urllib.request.urlopen(request,timeout=90) as response:return json.load(response)
    except urllib.error.HTTPError as error:
        with error:detail=error.read().decode('utf-8',errors='replace')
        raise ValueError('HTTP '+str(error.code)+': '+detail) from error


@contextmanager
def isolated_server(output, *, frozen_path=None):
    """One real Uvicorn process, loopback only, fresh private DB; graceful shutdown."""
    with socket.socket() as sock:
        sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
    stop=output/'http.stop';database=output/'http-data/scanner.sqlite3'
    if stop.exists() or database.exists():raise FileExistsError('Cần thư mục HTTP mới.')
    base='http://127.0.0.1:'+str(port)
    with (output/'http-server.log').open('x',encoding='utf-8') as log:
        arguments=[sys.executable,'-u',str(Path(__file__).resolve()),'_serve',str(database),str(stop),str(port)]
        if frozen_path is not None:arguments.append(str(Path(frozen_path).resolve()))
        process=subprocess.Popen(arguments,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
        try:
            deadline=time.monotonic()+45
            while True:
                if process.poll() is not None:raise RuntimeError('HTTP benchmark server dừng khi khởi động; xem log.')
                try:
                    with urllib.request.urlopen(base+'/api/v1/health',timeout=.5) as response:
                        if json.load(response)=={'status':'ok'}:break
                except (OSError,ValueError):pass
                if time.monotonic()>deadline:raise TimeoutError('HTTP benchmark server chưa sẵn sàng.')
                time.sleep(.05)
            server_info=json.loads((output/'server-process.json').read_text(encoding='utf-8'))
            server_pid=server_info['pid']
            if type(server_pid) is not int or server_pid<1:raise ValueError('PID server không hợp lệ.')
            yield base,server_pid
        finally:
            stop.touch()
            try:process.wait(timeout=30)
            except subprocess.TimeoutExpired:
                process.terminate();process.wait(timeout=10)
                raise RuntimeError('Server không dừng gracefully; không chứng nhận lượt benchmark.')


def serve(database,stop,port,frozen_path=None):
    verify_runtime(frozen_path)
    # Windows venv python.exe may be a ~5MiB redirector. The HTTP worker's
    # actual process reports its PID; Popen.pid is only the launcher identity.
    write_json(Path(stop).parent/'server-process.json',{'pid':os.getpid(),
        'parent_pid':os.getppid(),'executable':sys.executable})
    import uvicorn
    from app.main import create_app
    server=uvicorn.Server(uvicorn.Config(create_app(Path(database)),host='127.0.0.1',port=int(port),log_level='info'))
    def wait_stop():
        while not Path(stop).exists():time.sleep(.05)
        server.should_exit=True
    Thread(target=wait_stop,daemon=True).start();server.run()


def _detection_identity(result):
    if not isinstance(result,dict):
        return {'status':result.status,'corners':json.loads(json.dumps(result.corners)),
                'heuristic_score':result.heuristic_score}
    return {k:result[k] for k in ('status','corners','heuristic_score')}


def evaluate_case(case,label,output,base,server_pid,session_id,preset,*,repeats=5,warmups=1,project_root=ROOT):
    """One accuracy observation, then unchanged operations; no tuning from truth."""
    source,payload,original=load_case(case,label,project_root)
    source_hash=sha256(source.tobytes()).hexdigest();folder=output/case['image_id'];folder.mkdir()
    (folder/'source.png').write_bytes(payload)
    identity={k:case[k] for k in ('image_id','document_id','split','condition')}
    source_info={**identity,'width':label['width'],'height':label['height'],
        'normalized_sha256':case['normalized_sha256'],'raw_sha256':case['source_sha256']}
    result=detect_document(source,debug=True)
    details,diagnostic_panel=write_detection_artifacts(result,source_info,folder/'detection',str(uuid4()),entry_point='frozen-benchmark')
    accuracy={**identity,**evaluate_quad(result.corners,label['corners'],label['width'],label['height']),
              'status':result.status,'heuristic_score':result.heuristic_score,'error':''}
    overlay=result.debug.analysis.bgr.copy();h,w=overlay.shape[:2]
    for corners,color in [(label['corners'],(0,220,0)),(result.corners,(0,0,255))]:
        if corners is not None:
            points=np.rint(np.asarray(corners)*[w-1,h-1]).astype(np.int32)
            cv2.polylines(overlay,[points],True,color,2)
    save_png(folder/'ground-truth-proposal.png',overlay)
    save_png(folder/'comparison.png',np.concatenate([
        resize_to_max_edge(overlay,720),resize_to_max_edge(result.debug.overlay,720)],axis=1))
    expected_detection=_detection_identity(result)
    selected=result.selected
    write_json(folder/'accuracy.json',{'source':source_info,'ground_truth':label,'metrics':accuracy,
        'result':expected_detection,'warnings':result.warnings,'selected_description':asdict(selected) if selected else None,
        'note':'green=manual GT, red=result.corners; right panel=actual core debug; no diagnostic used as proposal'})
    del result,overlay,diagnostic_panel,selected
    config=json.loads(json.dumps(preset));config.update(corners=label['corners'],confirmed=True)
    if label['corners'] is None:raise ValueError('Không có GT đáng tin để benchmark render; không tạo góc giả.')
    config_hash=sha256(json.dumps(config,sort_keys=True).encode()).hexdigest()
    setup_error=None;path=None
    try:
        page=http_json(base,'POST','/sessions/'+session_id+'/pages',file=original)
        if (page['width'],page['height'])!=(label['width'],label['height']):raise ValueError('HTTP source dimensions khác nguồn đã khóa.')
        with urllib.request.urlopen(base+'/api/v1/artifacts/'+page['normalized_artifact_id']) as response:
            if sha256(response.read()).hexdigest()!=case['normalized_sha256']:raise ValueError('HTTP normalized hash khác manifest.')
        path='/sessions/'+session_id+'/pages/'+page['id']
        saved=http_json(base,'PUT',path+'/config',{'expected_revision':0,'config':config})
        if saved['revision']!=1:raise ValueError('HTTP config revision phải bằng 1.')
    except Exception as error:setup_error=type(error).__name__+': '+str(error)
    def http_call(operation):
        if setup_error:raise ValueError('HTTP setup: '+setup_error)
        body={'debug':False} if operation=='detect' else {'debug':False,'expected_revision':1}
        return http_json(base,'POST',path+'/'+operation,body)
    calls={'core_detect':(lambda:detect_document(source,debug=False),os.getpid()),
           'core_render':(lambda:render_document(source,config,debug=False),os.getpid()),
           'http_detect':(lambda:http_call('detect'),server_pid),
           'http_render':(lambda:http_call('render'),server_pid)}
    rows=[];run_ids=set();expected_render=None;latest_http_render=None
    for operation,(call,pid) in calls.items():
        for iteration in range(warmups+repeats):
            measured,stats,error=measure(call,pid)
            row={**identity,'source_width':label['width'],'source_height':label['height'],
                 'operation':operation,'phase':'warmup' if iteration<warmups else 'measured',
                 'iteration':iteration,'pid':pid,'debug':False,'config_sha256':config_hash,**stats,
                 'response_run_id':'','core_reported_ms':None,'result_status':'','error':error or ''}
            try:
                if error:raise ValueError(error)
                if operation.endswith('detect'):
                    if _detection_identity(measured)!=expected_detection:raise ValueError('Detection drift giữa accuracy/core/HTTP.')
                    row['result_status']=measured['status'] if isinstance(measured,dict) else measured.status
                if operation.startswith('core_'):
                    row['core_reported_ms']=measured.timings_ms.total
                    if operation=='core_render':
                        if measured.enhancement is None:raise ValueError('Core render không có full output.')
                        fingerprint=sha256(measured.enhancement.image.tobytes()).hexdigest()
                        if expected_render is not None and fingerprint!=expected_render:raise ValueError('Full render drift.')
                        expected_render=fingerprint
                        if iteration==warmups+repeats-1:
                            images=encode_render_images(measured.enhancement.image)
                            (folder/'full.png').write_bytes(images.full.png_bytes)
                            (folder/'preview.png').write_bytes(images.preview.png_bytes)
                else:
                    key='run_id' if operation=='http_detect' else 'render_run_id'
                    row['response_run_id']=measured[key]
                    if measured[key] in run_ids:raise ValueError('HTTP dùng lại run ID; không xác minh được cache off.')
                    run_ids.add(measured[key]);row['core_reported_ms']=measured['timings_ms']['core.total']
                    if operation=='http_render':latest_http_render=measured
            except Exception as caught:row['error']=str(caught)
            row['ok']=not row['error'];rows.append(row)
            del measured
    write_json(folder/'benchmark.json',{'source':source_info,'config':config,'config_sha256':config_hash,
        'samples':rows,'http_fresh_run_ids':sorted(run_ids)})
    full_equal=False
    if latest_http_render and (folder/'full.png').exists():
        with urllib.request.urlopen(base+'/api/v1/artifacts/'+latest_http_render['render_artifact_id']) as response:
            if response.read()!=(folder/'full.png').read_bytes():raise ValueError('HTTP full PNG khác core full PNG.')
        full_equal=True
    if sha256(source.tobytes()).hexdigest()!=source_hash:raise ValueError('Nguồn bị mutate.')
    write_json(folder/'checks.json',{'http_full_equals_core':full_equal,'source_unchanged':True})
    return accuracy,rows


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',type=Path,required=True)
    args=parser.parse_args(argv)
    created=False
    try:
        frozen=verify_runtime();snapshot=frozen['snapshot']
        frozen_hash=sha256((ROOT/'experiments/configs/frozen.json').read_bytes()).hexdigest()
        runner_hash=sha256(Path(__file__).read_bytes()).hexdigest()
        args.output_dir.mkdir(parents=True);created=True
        protocol={'benchmark_version':'frozen-benchmark-v1.1','declared_before_test_pixels':True,
            'started_at_utc':datetime.now(timezone.utc).isoformat(),'frozen_sha256':frozen_hash,
            'frozen_at_utc':frozen['frozen_at_utc'],'runner_sha256':runner_hash,
            'split':'test','repeats':5,'warmups':1,'debug':False,'concurrency':1,
            'operations':['core_detect','core_render','http_detect','http_render'],
            'render_input':'frozen BW preset with per-image manual GT, confirmed solely in isolated benchmark',
            'core_scope':'decoded normalized source -> function return; excludes decode/encode/files',
            'http_scope':'fresh loopback TCP request -> parsed JSON, includes queue/load/CPU/encode/persist; excludes upload/config and output download',
            'cache':'no application result reuse; unique HTTP run IDs; OS page cache/allocator retained, not cold-cache',
            'memory':'Win32 working set sampled every 10ms plus endpoints; per-process baseline/peak/end and lifetime peak, not exact per-call peak',
            'percentiles':'NumPy quantile linear, successful measured samples only, report errors/attempted separately',
            'environment':snapshot['environment'],'hardware':'i7-11700F, 8 cores/16 threads, OS RAM 34017787904 bytes (13.06)',
            'limits':'7 related photos/1 test document; sequential warm-cache local observations, not independent population p95'}
        write_json(args.output_dir/'protocol.json',protocol)
        manifest=ROOT/'experiments/dataset_manifest.csv';annotations=ROOT/'experiments/annotations.json'
        validate_annotations(annotations,manifest,ROOT,split='test')
        with manifest.open(encoding='utf-8-sig',newline='') as file:
            cases=[r for r in csv.DictReader(file) if r['split']=='test']
        labels={r['image_id']:r for r in json.loads(annotations.read_text(encoding='utf-8'))['records']}
        if len(cases)!=snapshot['data_policy']['test_images']:raise ValueError('Số ảnh test khác bản khóa.')
        accuracy=[];samples=[];case_errors=[]
        with isolated_server(args.output_dir) as (base,pid):
            session=http_json(base,'POST','/sessions',{'title':'Frozen test benchmark, isolated'})['id']
            for case in cases:
                try:
                    metrics,measured=evaluate_case(case,labels[case['image_id']],args.output_dir,base,pid,
                        session,snapshot['presets']['bw'])
                except Exception as error:
                    folder=args.output_dir/case['image_id'];label=labels[case['image_id']]
                    saved=folder/'accuracy.json';partial=folder/'benchmark.json'
                    metrics=json.loads(saved.read_text(encoding='utf-8'))['metrics'] if saved.exists() else {
                        **{k:case[k] for k in ('image_id','document_id','split','condition')},
                        **evaluate_quad(None,label['corners'],label['width'],label['height']),
                        'status':'error','heuristic_score':None,'error':''}
                    metrics['error']=type(error).__name__+': '+str(error)
                    measured=json.loads(partial.read_text(encoding='utf-8'))['samples'] if partial.exists() else []
                    case_errors.append({'image_id':case['image_id'],'error':metrics['error']})
                    write_json(args.output_dir/(case['image_id']+'-error.json'),case_errors[-1])
                accuracy.append(metrics);samples.extend(measured)
                print(json.dumps({'image_id':case['image_id'],'status':metrics['status'],
                    'iou':metrics['iou'],'samples':len(measured),'error':metrics['error']}),flush=True)
        verify_runtime()
        if sha256((ROOT/'experiments/configs/frozen.json').read_bytes()).hexdigest()!=frozen_hash:
            raise ValueError('File frozen đã thay đổi trong khi đo.')
        if sha256(Path(__file__).read_bytes()).hexdigest()!=runner_hash:raise ValueError('Runner đã thay đổi trong khi đo.')
        for name,rows in [('accuracy.csv',accuracy),('samples.csv',samples)]:
            with (args.output_dir/name).open('x',encoding='utf-8',newline='') as file:
                writer=csv.DictWriter(file,fieldnames=list(rows[0]) if rows else ['no_samples'])
                writer.writeheader();writer.writerows(rows)
        sample_errors=sum(not r['ok'] for r in samples)
        complete=len(samples)==len(cases)*4*6
        summary={'benchmark_version':'frozen-benchmark-v1.1','frozen_sha256':frozen_hash,'runner_sha256':runner_hash,
            'split':'test','images':len(cases),'documents':len({r['document_id'] for r in cases}),
            'accuracy':aggregate_metrics(accuracy),'benchmark':summarize_samples(samples),
            'samples_total':len(samples),'measured_samples':sum(r['phase']=='measured' for r in samples),
            'warmup_samples':sum(r['phase']=='warmup' for r in samples),'sample_errors':sample_errors,
            'case_errors':case_errors,'complete':complete,'core_and_http_frozen_verified_before_after':True,
            'environment':snapshot['environment'],'protocol_sha256':sha256((args.output_dir/'protocol.json').read_bytes()).hexdigest(),
            'finished_at_utc':datetime.now(timezone.utc).isoformat(),'test_tuning':False,
            'limits':protocol['limits']}
        write_json(args.output_dir/'summary.json',summary)
        print(json.dumps(summary),flush=True)
        return 1 if sample_errors or case_errors or not complete else 0
    except (ValueError,OSError,RuntimeError) as error:
        if created:write_json(args.output_dir/'fatal-error.json',{'error':type(error).__name__+': '+str(error)})
        print('Lỗi benchmark: '+str(error),file=sys.stderr);return 1


if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8');sys.stderr.reconfigure(encoding='utf-8')
    if len(sys.argv)>1 and sys.argv[1]=='_serve':serve(*sys.argv[2:])
    else:raise SystemExit(main())
