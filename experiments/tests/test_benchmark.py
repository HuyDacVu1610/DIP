from hashlib import sha256
import json
import os
from pathlib import Path
import time

import numpy as np
from PIL import Image
import pytest

from experiments.benchmark import load_case, measure, summarize_samples, main


@pytest.fixture
def runtime_snapshot(tmp_path):
    # Synthetic integration tests bind the current packaging revision, while
    # held-out CLI runs retain the original immutable stage-13 freeze by default.
    import cv2
    from experiments.freeze_config import capture_snapshot
    cv2.ocl.setUseOpenCL(False)
    path=tmp_path/'synthetic-runtime.json'
    path.write_text(json.dumps({'schema_version':1,'snapshot':capture_snapshot()}),encoding='utf-8')
    return path


def test_explicit_synthetic_snapshot_still_rejects_drift(runtime_snapshot):
    from experiments.benchmark import verify_runtime
    assert verify_runtime(runtime_snapshot)['schema_version']==1
    changed=json.loads(runtime_snapshot.read_text(encoding='utf-8'))
    changed['snapshot']['presets']['bw']['threshold']['c']=11
    runtime_snapshot.write_text(json.dumps(changed),encoding='utf-8')
    with pytest.raises(ValueError,match='snapshot'):
        verify_runtime(runtime_snapshot)


def test_percentiles_exclude_warmups_keep_errors_and_report_denominators():
    rows=[{'operation':'core_detect','phase':'measured','ok':True,'wall_ms':v,
        'rss_sampled_peak_bytes':100+v} for v in [1,2,3,4,5]]
    rows += [{'operation':'core_detect','phase':'warmup','ok':True,'wall_ms':999,
        'rss_sampled_peak_bytes':999}, {'operation':'core_detect','phase':'measured','ok':False,
        'wall_ms':50,'rss_sampled_peak_bytes':120}]
    stats=summarize_samples(rows)['core_detect']
    assert stats['attempted']==6 and stats['successful']==5 and stats['errors']==1
    assert stats['p50_ms']==3 and stats['p95_ms']==pytest.approx(4.8)
    assert stats['rss_sampled_peak_bytes']==120
    assert summarize_samples([])=={}


def test_native_memory_sampler_and_failed_call_are_recorded():
    image=np.zeros((128,128),np.uint8)
    result,stats,error=measure(lambda:(image.copy(),time.sleep(.025))[0],os.getpid())
    assert error is None and np.array_equal(result,image)
    assert stats['wall_ms']>=20 and stats['rss_samples']>=2
    assert stats['rss_sampled_peak_bytes']>=stats['rss_baseline_bytes']>0
    def fail():raise ValueError('controlled failure')
    result,stats,error=measure(fail,os.getpid())
    assert result is None and 'controlled failure' in error and stats['wall_ms']>=0


def test_verified_case_decodes_exact_payload_and_rejects_source_or_dimension_drift(tmp_path):
    raw=tmp_path/'raw.png';Image.new('RGB',(100,80),'white').save(raw)
    png=tmp_path/'source.png';png.write_bytes(raw.read_bytes());digest=sha256(raw.read_bytes()).hexdigest()
    row={'source_path':'raw.png','source_sha256':digest,'normalized_path':'source.png','normalized_sha256':digest}
    label={'normalized_sha256':digest,'width':100,'height':80}
    source,payload,original=load_case(row,label,tmp_path)
    assert source.shape==(80,100,3) and not source.flags.writeable
    assert payload==original==raw.read_bytes()
    with pytest.raises(ValueError):load_case(row,{**label,'width':101},tmp_path)
    png.write_bytes(b'changed')
    with pytest.raises(ValueError):load_case(row,label,tmp_path)


def test_frozen_gate_precedes_any_dataset_read_or_output_creation(tmp_path,monkeypatch):
    import experiments.benchmark as module
    called=[]
    def refuse(path):called.append(path);raise ValueError('snapshot drift')
    monkeypatch.setattr(module,'verify_frozen',refuse)
    def never(*args,**kwargs):raise AssertionError('dataset opened before gate')
    monkeypatch.setattr(module,'validate_annotations',never)
    output=tmp_path/'result'
    assert main(['--output-dir',str(output)])==1
    assert len(called)==1 and not output.exists()


def test_isolated_http_runner_imports_and_recomputes_without_touching_product_db(tmp_path,runtime_snapshot):
    from io import BytesIO
    from experiments.benchmark import isolated_server,http_json
    from app.processing.config import get_preset
    stream=BytesIO();Image.new('RGB',(140,180),'white').save(stream,format='PNG')
    with isolated_server(tmp_path,frozen_path=runtime_snapshot) as (base,pid):
        assert pid!=os.getpid()
        assert json.loads((tmp_path/'server-process.json').read_text())['pid']==pid
        sid=http_json(base,'POST','/sessions',{'title':'Synthetic benchmark fixture'})['id']
        page=http_json(base,'POST','/sessions/'+sid+'/pages',file=stream.getvalue())
        path='/sessions/'+sid+'/pages/'+page['id']
        config=get_preset('bw').model_dump(mode='json')
        config.update(corners=[[0,0],[1,0],[1,1],[0,1]],confirmed=True)
        saved=http_json(base,'PUT',path+'/config',{'expected_revision':0,'config':config})
        assert saved['revision']==1
        detections=[http_json(base,'POST',path+'/detect',{'debug':False}) for _ in range(2)]
        renders=[http_json(base,'POST',path+'/render',{'expected_revision':1,'debug':False}) for _ in range(2)]
        assert detections[0]['run_id']!=detections[1]['run_id']
        assert all(r['status']=='manual_required' for r in detections)
        assert renders[0]['render_run_id']!=renders[1]['render_run_id']
        assert renders[0]['width']==139 and renders[0]['height']==179
    assert (tmp_path/'http-data/scanner.sqlite3').exists()
    import re
    actual=re.search(r'Started server process \[(\d+)\]',(tmp_path/'http-server.log').read_text())
    assert actual and int(actual.group(1))==pid


def test_full_case_retains_missing_detection_as_failure_and_benchmarks_all_four_paths(tmp_path,runtime_snapshot):
    from experiments.benchmark import evaluate_case,isolated_server,http_json
    from app.processing.config import get_preset
    source=tmp_path/'source.png';Image.new('RGB',(140,180),'white').save(source)
    digest=sha256(source.read_bytes()).hexdigest()
    case={'image_id':'fixture','document_id':'synthetic_doc','split':'test','condition':'even_light',
          'source_path':'source.png','source_sha256':digest,'normalized_path':'source.png','normalized_sha256':digest}
    label={'image_id':'fixture','normalized_sha256':digest,'width':140,'height':180,
           'status':'labeled','corners':[[0,0],[1,0],[1,1],[0,1]]}
    with isolated_server(tmp_path,frozen_path=runtime_snapshot) as (base,pid):
        sid=http_json(base,'POST','/sessions',{'title':'Fixture, not dataset'})['id']
        accuracy,rows=evaluate_case(case,label,tmp_path,base,pid,sid,get_preset('bw').model_dump(mode='json'),
            repeats=1,warmups=0,project_root=tmp_path)
    assert accuracy['iou']==0 and accuracy['corner_error_px'] is None and not accuracy['has_proposal']
    assert {r['operation'] for r in rows}=={'core_detect','core_render','http_detect','http_render'}
    assert len(rows)==4 and all(r['ok'] for r in rows)
    meta=json.loads((tmp_path/'fixture/benchmark.json').read_text())
    assert json.loads((tmp_path/'fixture/checks.json').read_text())['http_full_equals_core']
    assert len(meta['http_fresh_run_ids'])==2
    assert (tmp_path/'fixture/detection/metadata.json').exists()
