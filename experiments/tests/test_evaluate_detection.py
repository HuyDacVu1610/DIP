from dataclasses import replace
import cv2
import numpy as np
import pytest
from app.processing.detection import detect_document
from experiments.evaluate_detection import load_profiles,run_profile,choose_proposal


def source():
    im=np.zeros((400,600,3),np.uint8)
    im[30:360,30:300]=255;im[70:310,360:560]=255
    return im

def test_profiles_only_change_one_factor_against_reference():
    profiles=load_profiles()
    assert len(profiles)==4
    reference=profiles[0]
    for profile in profiles[1:]:
        assert sum(profile[k]!=reference[k] for k in ['selection','gaussian_kernel','closing'])==1


@pytest.mark.parametrize('change',['root_list','boolean_version','null_profile','wrong_kernel'])
def test_malformed_profile_schema_fails_explicitly(tmp_path,change):
    import json
    from experiments.evaluate_detection import CONFIG
    data=json.loads(CONFIG.read_text())
    if change=='root_list':data=[]
    elif change=='boolean_version':data['schema_version']=True
    elif change=='null_profile':data['profiles'][0]=None
    else:data['profiles'][2]['gaussian_kernel']=3
    path=tmp_path/'bad.json';path.write_text(json.dumps(data),encoding='utf-8')
    with pytest.raises(ValueError):load_profiles(path)

def test_reference_matches_production_output_and_raw_support_stays_independent():
    im=source();before=im.copy()
    result,analysis,runs,descriptions,timings=run_profile(im,load_profiles()[0])
    actual=detect_document(im,debug=True)
    assert result.corners==actual.corners and result.status==actual.status
    assert result.selected==actual.selected and result.candidates==actual.candidates
    assert np.array_equal(analysis.blurred,actual.debug.analysis.blurred)
    assert all(np.array_equal(a.trial.edges,b.trial.edges) for a,b in zip(runs,actual.debug.trials))
    assert np.array_equal(im,before) and timings['total']>=0

def test_largest_contour_and_score_selection_use_same_valid_candidates():
    _,_,_,descriptions,_=run_profile(source(),load_profiles()[0])
    area=lambda d:cv2.contourArea(np.asarray(d.candidate.contour_px,np.float32))
    small=replace(min(descriptions,key=area),heuristic_score=.9)
    large=replace(max(descriptions,key=area),heuristic_score=.45)
    assert area(small)<area(large)
    assert choose_proposal((small,large),'scoring').selected==small
    assert choose_proposal((small,large),'largest_contour').selected==large

def test_no_gaussian_and_no_closing_are_real_stage_changes_with_truthful_provenance():
    im=source()
    for profile in load_profiles()[2:]:
        _,analysis,runs,_,_=run_profile(im,profile)
        if profile['gaussian_kernel']==0:
            assert np.array_equal(analysis.gray,analysis.blurred)
            assert all(r.trial.gaussian_kernel==0 for r in runs)
        if not profile['closing']:
            assert all(np.array_equal(r.trial.edges,r.trial.closed) for r in runs if r.trial.method=='canny')

def test_invalid_profile_options_are_not_silently_coerced():
    for change in [{'closing':1},{'gaussian_kernel':True},{'selection':'unknown'}]:
        with pytest.raises(ValueError):run_profile(source(),{**load_profiles()[0],**change})


def test_cli_outputs_four_profiles_and_never_opens_unavailable_test_images(tmp_path,monkeypatch):
    import csv,hashlib,json
    from PIL import Image
    from experiments.evaluate_detection import main
    from experiments.validate_dataset import FIELDS
    raw=tmp_path/'experiments/data/dev.png';raw.parent.mkdir(parents=True)
    Image.fromarray(source()[:,:,::-1]).save(raw)
    normalized=tmp_path/'experiments/results/dev/source.png';normalized.parent.mkdir(parents=True)
    normalized.write_bytes(raw.read_bytes());digest=hashlib.sha256(raw.read_bytes()).hexdigest()
    manifest=tmp_path/'manifest.csv'
    values=['dev','doc_01','even_light','development','experiments/data/dev.png',digest,
            'experiments/results/dev/source.png',digest]
    row=dict(zip(FIELDS,values))
    with manifest.open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=FIELDS);writer.writeheader();writer.writerow(row)
        writer.writerow({**row,'image_id':'holdout','document_id':'doc_02','split':'test',
            'source_path':'experiments/data/not-available.jpg','source_sha256':'b'*64,
            'normalized_path':'experiments/results/test/source.png','normalized_sha256':'b'*64})
    record={'image_id':'dev','normalized_sha256':digest,'width':600,'height':400,
        'status':'labeled','corners':[[.05,.075],[.5,.075],[.5,.9],[.05,.9]],
        'reason':'','reviewed':True,'labeler':'fixture','notes':'Synthetic, never dataset evidence.'}
    annotations=tmp_path/'annotations.json'
    annotations.write_text(json.dumps({'schema_version':1,'coordinates':'normalized_w_minus_1_h_minus_1',
        'records':[record,{**record,'image_id':'holdout','normalized_sha256':'b'*64}]}),encoding='utf-8')
    output=tmp_path/'evaluation'
    args=['--project-root',str(tmp_path),'--manifest',str(manifest),'--annotations',str(annotations),
          '--output-dir',str(output)]
    assert main(args)==0
    summary=json.loads((output/'summary.json').read_text(encoding='utf-8'))
    assert summary['images']==1 and summary['profile_runs']==4 and summary['errors']==0
    assert summary['test_images_processed']==0
    with (output/'results.csv').open(encoding='utf-8',newline='') as f:rows=list(csv.DictReader(f))
    assert len(rows)==4 and {r['split'] for r in rows}=={'development'}
    assert raw.read_bytes()==normalized.read_bytes()
    for profile in load_profiles():
        meta=json.loads((output/'dev'/profile['id']/'metadata.json').read_text(encoding='utf-8'))
        assert meta['profile']==profile and meta['source']['normalized_sha256']==digest
        assert (output/'dev'/profile['id']/'overlay.png').exists()
    before=(output/'results.csv').read_bytes()
    assert main(args)==1 and (output/'results.csv').read_bytes()==before
    import experiments.evaluate_detection as module
    original=module.validate_annotations
    def changed_after_validation(*a,**kw):
        result=original(*a,**kw);normalized.write_bytes(b'changed after validation');return result
    monkeypatch.setattr(module,'validate_annotations',changed_after_validation)
    invalid=tmp_path/'changed-input'
    assert main(args[:-1]+[str(invalid)])==1
    assert not (invalid/'results.csv').exists()
