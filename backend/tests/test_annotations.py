"""Ground-truth source binding, topology, coverage and visual review gates."""
import csv
import hashlib
import json
from pathlib import Path

from PIL import Image
import pytest

from experiments.validate_annotations import validate_annotations, write_overlays
from experiments.validate_dataset import FIELDS


def dataset(tmp_path):
    source=tmp_path/'experiments/data/original.png'
    source.parent.mkdir(parents=True)
    Image.new('RGB',(101,81),'white').save(source)
    normalized=tmp_path/'experiments/results/normalized/source.png'
    normalized.parent.mkdir(parents=True)
    normalized.write_bytes(source.read_bytes())
    digest=hashlib.sha256(source.read_bytes()).hexdigest()
    manifest=tmp_path/'manifest.csv'
    row=dict(zip(FIELDS,['img_001','doc_01','even_light','development',
        'experiments/data/original.png',digest,'experiments/results/normalized/source.png',digest]))
    with manifest.open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=FIELDS);writer.writeheader();writer.writerow(row)
    record={'image_id':'img_001','normalized_sha256':digest,'width':101,'height':81,
        'status':'labeled','corners':[[.1,.1],[.9,.1],[.9,.9],[.1,.9]],
        'reason':'','reviewed':True,'labeler':'manual_visual','notes':'Visible paper corners.'}
    payload={'schema_version':1,'coordinates':'normalized_w_minus_1_h_minus_1','records':[record]}
    path=tmp_path/'annotations.json'
    return manifest,path,payload,normalized


def check(tmp_path,payload=None,**options):
    manifest,path,base,_=dataset(tmp_path)
    path.write_text(json.dumps(payload or base),encoding='utf-8')
    return validate_annotations(path,manifest,tmp_path,**options)


def test_valid_bound_labels_and_independent_overlays_preserve_source(tmp_path):
    manifest,path,payload,source=dataset(tmp_path)
    path.write_text(json.dumps(payload),encoding='utf-8')
    before=source.read_bytes()
    report=validate_annotations(path,manifest,tmp_path)
    assert report['labeled']==1 and report['unlabelable']==0 and report['reviewed']==1
    output=tmp_path/'overlays'
    write_overlays(path,manifest,output,tmp_path)
    assert source.read_bytes()==before
    with Image.open(output/'img_001.png') as overlay:
        assert overlay.size==(101,81)
        assert overlay.convert('RGB').getpixel((10,8))!=(255,255,255)
    with pytest.raises(FileExistsError):write_overlays(path,manifest,output,tmp_path)


@pytest.mark.parametrize('change',[
    {'image_id':'foreign'},{'width':100},{'height':80},{'width':True},
    {'normalized_sha256':'a'*64},{'status':'pending'},{'corners':None},
    {'corners':[[0,0],[1,1],[1,0],[0,1]]},
    {'corners':[[0,0],[0,1],[1,1],[1,0]]},
    {'corners':[[0,0],[1.1,0],[1,1],[0,1]]},
    {'reviewed':'yes'},{'labeler':''},{'reason':'hidden corner'},
])
def test_invalid_labels_never_pass(tmp_path,change):
    manifest,path,payload,_=dataset(tmp_path)
    payload['records'][0].update(change)
    path.write_text(json.dumps(payload),encoding='utf-8')
    with pytest.raises(ValueError):validate_annotations(path,manifest,tmp_path)


def test_unlabelable_retains_sample_with_explicit_reason_and_no_invented_quad(tmp_path):
    manifest,path,payload,_=dataset(tmp_path)
    payload['records'][0].update(status='unlabelable',corners=None,reason='Corner folded out of sight.')
    path.write_text(json.dumps(payload),encoding='utf-8')
    assert validate_annotations(path,manifest,tmp_path)['unlabelable']==1
    payload['records'][0]['reason']=''
    path.write_text(json.dumps(payload),encoding='utf-8')
    with pytest.raises(ValueError):validate_annotations(path,manifest,tmp_path)


def test_coverage_duplicates_review_and_changed_source_are_rejected(tmp_path):
    manifest,path,payload,source=dataset(tmp_path)
    for records in [[],[payload['records'][0]]*2]:
        path.write_text(json.dumps({**payload,'records':records}),encoding='utf-8')
        with pytest.raises(ValueError):validate_annotations(path,manifest,tmp_path)
    payload['records'][0]['reviewed']=False
    path.write_text(json.dumps(payload),encoding='utf-8')
    with pytest.raises(ValueError):validate_annotations(path,manifest,tmp_path)
    assert validate_annotations(path,manifest,tmp_path,require_review=False)['reviewed']==0
    source.write_bytes(b'changed')
    with pytest.raises(ValueError):validate_annotations(path,manifest,tmp_path,require_review=False)


def test_development_only_validation_does_not_open_held_out_test_files(tmp_path):
    manifest,path,payload,_=dataset(tmp_path)
    with manifest.open(encoding='utf-8',newline='') as f:rows=list(csv.DictReader(f))
    rows.append({**rows[0],'image_id':'img_002','document_id':'doc_02','split':'test',
        'source_path':'experiments/data/held-out.jpg','source_sha256':'b'*64,
        'normalized_path':'experiments/results/held-out/source.png','normalized_sha256':'b'*64})
    with manifest.open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=FIELDS);writer.writeheader();writer.writerows(rows)
    payload['records'].append({**payload['records'][0],'image_id':'img_002','normalized_sha256':'b'*64})
    path.write_text(json.dumps(payload),encoding='utf-8')
    assert validate_annotations(path,manifest,tmp_path,split='development')['images']==1
    with pytest.raises(OSError):validate_annotations(path,manifest,tmp_path)
