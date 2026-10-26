"""Offline detector batch: genuine stages, development split and visible failures."""
import csv
import json
import subprocess
import sys
from hashlib import sha256
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from app.processing.normalize import encode_normalized_png, normalize_image

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT/'experiments/detect_batch.py'
FIELDS = ('image_id','document_id','condition','split','source_path','source_sha256',
          'normalized_path','normalized_sha256')


def manifest_at(tmp_path, rows=()):
    path = tmp_path/'manifest.csv'
    with path.open('w',encoding='utf-8',newline='') as stream:
        writer = csv.DictWriter(stream,fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    return path


def run_cli(tmp_path,manifest,output,*inputs):
    command = [sys.executable,str(SCRIPT),'--project-root',str(tmp_path),
        '--manifest',str(manifest),'--output-dir',str(output)]
    for source in inputs:
        command += ['--input',str(source)]
    return subprocess.run(command,cwd=tmp_path,capture_output=True,text=True,encoding='utf-8',timeout=60)


def make_page(path,background=25,paper=240):
    source = np.full((240,320,3),background,dtype=np.uint8)
    source[25:216,30:291]=paper
    path.parent.mkdir(parents=True,exist_ok=True)
    Image.fromarray(source).save(path)
    return path


@pytest.mark.parametrize('background,paper,method',[(25,240,'canny'),(235,243,'region_otsu')])
def test_batch_saves_both_detector_decisions_actual_stages_and_timings(tmp_path,background,paper,method):
    source = make_page(tmp_path/'ảnh.png',background,paper)
    original = source.read_bytes()
    output = tmp_path/'run'
    result = run_cli(tmp_path,manifest_at(tmp_path),output,source)
    assert result.returncode==0,result.stderr
    summary = json.loads((output/'summary.json').read_text(encoding='utf-8'))
    assert summary['entry_point']=='detect_batch' and summary['run_id']
    assert summary['errors']==0 and summary['images']==1 and summary['profile_runs']==2
    assert summary['cases'][0]['split']=='supplemental_unassigned'
    for preset in ('baseline','revised'):
        folder = output/'supplemental_001'/preset
        info = json.loads((folder/'metadata.json').read_text(encoding='utf-8'))
        assert info['preset']==preset and info['result']['confirmed'] is False
        assert info['source']['bgr_sha256']==sha256(normalize_image(original).tobytes()).hexdigest()
        assert info['source']['normalized_png_sha256']==sha256((output/'supplemental_001/source.png').read_bytes()).hexdigest()
        timing = info['timings_ms']
        assert timing['total']==pytest.approx(sum(v for k,v in timing.items() if k!='total'))
        assert all(v>=0 and np.isfinite(v) for v in timing.values())
        for name,record in info['artifacts'].items():
            payload = (folder/record['file']).read_bytes()
            assert sha256(payload).hexdigest()==record['sha256']
            with Image.open(folder/record['file']) as image:
                assert image.size==(record['width'],record['height']) and image.mode==record['png_mode']
                assert not image.getexif()
                if name.endswith(('_edges','_closed','_region_mask')):
                    assert set(np.unique(np.array(image))) <= {0,255}
        if preset=='revised':
            chosen = info['result']['selected']
            assert chosen['candidate']['method']==method
            assert info['selected_trial']['trial_id']==chosen['candidate']['trial_id']
            if method=='region_otsu':
                assert info['selected_trial']['support_trial_id']=='canny_20_60'
                assert chosen['edge_support']==0
                assert info['result']['status']=='proposed_with_warning'
    with (output/'results.csv').open(encoding='utf-8',newline='') as stream:
        assert len(list(csv.DictReader(stream)))==2
    assert (output/'supplemental_001/comparison.png').is_file()
    assert source.read_bytes()==original and not list(output.rglob('warp.png'))


def test_batch_reads_only_development_not_test_and_verifies_exif_hash(tmp_path):
    raw = (ROOT/'fixtures/exif_6.jpg').read_bytes()
    source = tmp_path/'experiments/data/dev.jpg'
    source.parent.mkdir(parents=True)
    source.write_bytes(raw)
    row = dict(zip(FIELDS,('img_dev','doc_dev','even_light','development',
        'experiments/data/dev.jpg',sha256(raw).hexdigest(),
        'experiments/results/dev/source.png',encode_normalized_png(normalize_image(raw)).sha256)))
    test = dict(zip(FIELDS,('img_test','doc_test','even_light','test',
        'experiments/data/absent-test.jpg','f'*64,'','')))
    output = tmp_path/'run'
    result = run_cli(tmp_path,manifest_at(tmp_path,(row,test)),output)
    assert result.returncode==0,result.stderr
    info = json.loads((output/'img_dev/revised/metadata.json').read_text(encoding='utf-8'))
    assert (info['source']['width'],info['source']['height'])==(64,96)
    assert not (output/'img_test').exists()
    assert json.loads((output/'summary.json').read_text(encoding='utf-8'))['images']==1


def test_batch_records_bad_image_and_continues_without_fake_success(tmp_path):
    good = make_page(tmp_path/'good.png')
    result = run_cli(tmp_path,manifest_at(tmp_path),tmp_path/'run',ROOT/'fixtures/fake.jpg',good)
    assert result.returncode==1 and 'Traceback' not in result.stderr
    summary = json.loads((tmp_path/'run/summary.json').read_text(encoding='utf-8'))
    assert summary['errors']==1 and summary['images']==2 and summary['profile_runs']==2
    assert summary['cases'][0]['error']['code']=='UNSUPPORTED_FORMAT'
    assert (tmp_path/'run/supplemental_001/error.json').is_file()
    assert not (tmp_path/'run/supplemental_001/revised/metadata.json').exists()
    assert (tmp_path/'run/supplemental_002/revised/metadata.json').is_file()


@pytest.mark.parametrize('normalized',[False,True])
def test_batch_rejects_source_or_normalized_hash_mismatch(tmp_path,normalized):
    source = make_page(tmp_path/'experiments/data/dev.png')
    raw = source.read_bytes()
    row = dict(zip(FIELDS,('img_dev','doc_dev','even_light','development',
        'experiments/data/dev.png',sha256(raw).hexdigest() if normalized else 'f'*64,
        'experiments/results/dev/source.png','f'*64)))
    result = run_cli(tmp_path,manifest_at(tmp_path,(row,)),tmp_path/'run')
    assert result.returncode==1
    error = json.loads((tmp_path/'run/img_dev/error.json').read_text(encoding='utf-8'))
    assert error['code']==('NORMALIZED_HASH_MISMATCH' if normalized else 'SOURCE_HASH_MISMATCH')
    assert not (tmp_path/'run/img_dev/revised/metadata.json').exists()


def test_batch_never_overwrites_and_empty_selection_creates_no_output(tmp_path):
    manifest = manifest_at(tmp_path)
    result = run_cli(tmp_path,manifest,tmp_path/'empty')
    assert result.returncode==1 and 'INPUTS_REQUIRED' in result.stderr
    assert not (tmp_path/'empty').exists()
    output = tmp_path/'existing'
    output.mkdir()
    marker = output/'keep.txt'
    marker.write_text('keep')
    result = run_cli(tmp_path,manifest,output,ROOT/'fixtures/corners_rgb.png')
    assert result.returncode==1 and 'OUTPUT_EXISTS' in result.stderr
    assert list(output.iterdir())==[marker] and marker.read_text()=='keep'
