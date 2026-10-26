"""Run the comparison CLI and inspect genuine stages, origins and failures."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
SCRIPT=ROOT/'experiments/compare_detection.py'


def run_cli(source,output,cwd,*options):
    return subprocess.run([sys.executable,str(SCRIPT),str(source),'--output-dir',str(output),*options],
        cwd=cwd,capture_output=True,text=True,encoding='utf-8',timeout=30)


@pytest.mark.parametrize('background,paper,method',[(220,248,'canny'),(235,243,'region_otsu')])
def test_cli_compares_presets_with_real_stages_and_keeps_source(tmp_path,background,paper,method):
    source=np.full((240,320,3),background,dtype=np.uint8)
    source[25:216,30:291]=paper
    input_file=tmp_path/'ảnh mới.png'
    Image.fromarray(source).save(input_file)
    original=input_file.read_bytes()
    output=tmp_path/'comparison'
    result=run_cli(input_file,output,tmp_path)
    assert result.returncode==0,result.stderr
    info=json.loads((output/'metadata.json').read_text(encoding='utf-8'))
    assert info['input']['sha256']==hashlib.sha256(original).hexdigest()
    assert info['source_size']==[320,240] and info['source_unchanged'] is True
    assert info['profiles']['baseline']['candidate_count']==0
    revised=info['profiles']['revised']
    assert revised['candidate_count']>0 and revised['example']['candidate']['method']==method
    assert info['confirmed'] is False and not (output/'warp.png').exists()
    assert len(revised['trials'])==(3 if method=='canny' else 4)
    for record in info['artifacts'].values():
        path=output/record['file']
        assert hashlib.sha256(path.read_bytes()).hexdigest()==record['sha256']
        with Image.open(path) as image:
            assert image.size==(record['width'],record['height']) and not image.getexif()
            assert image.mode==record['png_mode']
            if path.stem.endswith(('_edges','_closed','_mask')):
                assert set(np.unique(np.array(image))) <= {0,255}
    with Image.open(output/'source.png') as image:
        assert np.array_equal(np.array(image),source)
    if method=='region_otsu':
        assert revised['example']['edge_support']==0
    assert input_file.read_bytes()==original


def test_cli_applies_exif_and_records_gaussian_ablation_without_changing_baseline(tmp_path):
    source=ROOT/'fixtures/exif_6.jpg'
    original=source.read_bytes()
    result=run_cli(source,tmp_path/'out',tmp_path,'--gaussian-kernel','3')
    assert result.returncode==0,result.stderr
    info=json.loads((tmp_path/'out/metadata.json').read_text(encoding='utf-8'))
    assert info['source_size']==[64,96]
    assert info['profiles']['baseline']['gaussian_kernel']==5
    assert info['profiles']['revised']['gaussian_kernel']==3
    assert source.read_bytes()==original


def test_cli_never_overwrites_previous_evidence(tmp_path):
    output=tmp_path/'existing'
    output.mkdir()
    marker=output/'keep.txt'
    marker.write_text('keep',encoding='utf-8')
    result=run_cli(ROOT/'fixtures/corners_rgb.png',output,tmp_path)
    assert result.returncode==1 and 'OUTPUT_EXISTS' in result.stderr
    assert list(output.iterdir())==[marker] and marker.read_text()=='keep'


def test_cli_invalid_image_has_reason_without_success_artifacts(tmp_path):
    result=run_cli(ROOT/'fixtures/fake.jpg',tmp_path/'out',tmp_path)
    assert result.returncode==1 and 'UNSUPPORTED_FORMAT' in result.stderr
    assert 'Traceback' not in result.stderr and not (tmp_path/'out').exists()
