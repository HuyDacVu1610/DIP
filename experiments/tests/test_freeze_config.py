import json
from pathlib import Path

import pytest

from experiments.freeze_config import freeze, verify_frozen


def proof(tmp_path, **changes):
    data={'status':'passed','backend_experiments_tests':1244,'frontend_tests':103,
          'frontend_build_typecheck':True,'browser_smoke':True,'route_checks':True}
    data.update(changes)
    path=tmp_path/'proof.json';path.write_text(json.dumps(data),encoding='utf-8')
    return path


@pytest.mark.parametrize('tamper',['preset','source','dependency','dataset'])
def test_freeze_verifies_real_sources_presets_and_dependencies_and_refuses_overwrite(tmp_path,tamper):
    output=tmp_path/'frozen.json'
    freeze(output,proof(tmp_path))
    snapshot=verify_frozen(output)['snapshot']
    assert snapshot['algorithms']['detection']['version']=='detect-v1'
    assert snapshot['presets']['bw']['threshold']['method']=='adaptive_gaussian'
    assert snapshot['python_dependencies']['opencv-python-headless']=='4.14.0.94'
    assert 'backend/app/processing/enhancement.py' in snapshot['source_sha256']
    assert snapshot['data_policy']['test_images_processed_before_freeze']==0
    original=output.read_bytes()
    with pytest.raises(FileExistsError):freeze(output,proof(tmp_path))
    assert output.read_bytes()==original
    data=json.loads(original)
    if tamper=='preset':data['snapshot']['presets']['bw']['threshold']['c']=11
    elif tamper=='source':data['snapshot']['source_sha256']['backend/app/processing/detection.py']='0'*64
    elif tamper=='dependency':data['snapshot']['python_dependencies']['numpy']='0'
    else:data['snapshot']['input_sha256']['experiments/dataset_manifest.csv']='0'*64
    output.write_text(json.dumps(data),encoding='utf-8')
    with pytest.raises(ValueError,match='snapshot'):verify_frozen(output)


@pytest.mark.parametrize('change',[{'status':'failed'},{'browser_smoke':False},{'backend_experiments_tests':True}])
def test_freeze_requires_completed_regression_before_writing(tmp_path,change):
    with pytest.raises(ValueError):freeze(tmp_path/'frozen.json',proof(tmp_path,**change))
    assert not (tmp_path/'frozen.json').exists()


def test_source_and_environment_drift_are_rejected(tmp_path,monkeypatch):
    import experiments.freeze_config as module
    output=tmp_path/'frozen.json';freeze(output,proof(tmp_path))
    original=module.capture_snapshot
    def drift():
        state=original();state['environment']['python']='changed';return state
    monkeypatch.setattr(module,'capture_snapshot',drift)
    with pytest.raises(ValueError,match='snapshot'):verify_frozen(output)
