"""One actual render owns its stages, histogram and immutable metadata snapshot."""
from io import BytesIO
from pathlib import Path
from uuid import UUID

from fastapi.testclient import TestClient
import numpy as np
from PIL import Image
import pytest
from sqlalchemy import select

from app.main import create_app
from app.storage import repository
from app.storage.models import RenderRun

FIXTURES=Path(__file__).resolve().parents[2]/'fixtures'
QUAD=[[0.,0.],[1.,0.],[1.,1.],[0.,1.]]


@pytest.fixture
def setup(tmp_path):
    with TestClient(create_app(tmp_path/'data/scanner.sqlite3'),raise_server_exceptions=False) as client:
        sid=client.post('/api/v1/sessions',json={'title':'Debug render'}).json()['id']
        page=client.post(f'/api/v1/sessions/{sid}/pages',files={'file':('x.jpg',(FIXTURES/'exif_6.jpg').read_bytes())}).json()
        base=f"/api/v1/sessions/{sid}/pages/{page['id']}"
        yield client,sid,page,base


@pytest.mark.parametrize('mode,method',[('color','otsu'),('gray','otsu'),('bw','otsu'),('bw','adaptive_gaussian')])
def test_exact_stages_histogram_snapshot_and_reopen(setup,tmp_path,mode,method):
    client,sid,page,base=setup
    config=client.put(base+'/config',json={'expected_revision':0,'config':{
        'mode':mode,'corners':QUAD,'confirmed':True,'rotation':90,'threshold':{'method':method}}}).json()
    before=client.get('/api/v1/sessions/'+sid).json()
    response=client.post(base+'/render',json={'expected_revision':1,'debug':True})
    assert response.status_code==200,response.text
    result=response.json();assert result['warnings']==[] and result['render_run_id']
    with repository.transaction(client.app.state.engine) as db:
        run=db.get(RenderRun,UUID(result['render_run_id']));meta=run.metadata_json
        assert meta['effective_config']==config['effective_config'] and run.revision==1
        assert meta['source']['sha256']==run.source_sha256
        assert str(run.render_artifact_id)==result['render_artifact_id']
    assert set(meta['artifacts'])==({'full','preview','warp','filtered_bgr','before_rotation'}|({'prepared_gray'} if mode!='color' else set()))
    images={}
    for name,ref in meta['artifacts'].items():
        data=client.get('/api/v1/artifacts/'+ref['id']).content
        from hashlib import sha256
        assert sha256(data).hexdigest()==ref['sha256']
        with Image.open(BytesIO(data)) as image:images[name]=np.asarray(image)
    assert images['warp'].shape[:2]==(95,63)
    assert images['full'].shape[:2]==(63,95)
    assert np.array_equal(images['full'],np.rot90(images['before_rotation'],k=-1))
    if mode=='bw':
        hist=meta['histogram'];gray=images['prepared_gray']
        assert hist['counts']==np.bincount(gray.ravel(),minlength=256).tolist()
        assert hist['pixel_count']==gray.size and hist['source_png_sha256']==meta['artifacts']['prepared_gray']['sha256']
        assert hist['threshold_scope']==('global' if method=='otsu' else 'local')
        assert (hist['otsu_threshold'] is None)==(method!='otsu')
    else:assert meta['histogram'] is None and meta['histogram_unavailable_reason']=='mode_has_no_threshold'
    after=client.get('/api/v1/sessions/'+sid).json()
    before['pages'][0]['render_revision']=1;before['pages'][0]['latest_render']=result
    assert after==before
    with TestClient(create_app(tmp_path/'data/scanner.sqlite3')) as reopened:
        debug=reopened.get(base+'/debug',params={'render_run_id':result['render_run_id']})
        assert debug.status_code==200 and debug.json()['metadata']==meta


def test_no_debug_run_is_recorded_without_fake_stages(setup):
    client,_,_,base=setup
    client.put(base+'/config',json={'expected_revision':0,'config':{'corners':QUAD,'confirmed':True}})
    response=client.post(base+'/render',json={'expected_revision':1})
    assert response.status_code==200,response.text
    with repository.transaction(client.app.state.engine) as db:
        row=db.get(RenderRun,UUID(response.json()['render_run_id']))
        assert not row.metadata_json['debug_persisted']
        assert set(row.metadata_json['artifacts'])=={'full','preview'}
        assert row.metadata_json['histogram'] is None
        assert row.metadata_json['histogram_unavailable_reason']=='debug_not_requested'


@pytest.mark.parametrize('fault',['stage_write','late_commit'])
def test_debug_publish_failure_rolls_back_all_new_files_and_run(setup,monkeypatch,fault):
    from sqlalchemy import event
    from app.storage.files import ArtifactStore,ArtifactFileError
    client,sid,page,base=setup
    client.put(base+'/config',json={'expected_revision':0,'config':{'corners':QUAD,'confirmed':True}})
    assert client.post(base+'/render',json={'expected_revision':1}).status_code==200
    root=client.app.state.artifacts.root
    paths={p:p.read_bytes() for p in root.rglob('*') if p.is_file()}
    before=client.get('/api/v1/sessions/'+sid).json();inserted=[]
    def observe(conn,cursor,statement,parameters,context,executemany):
        if statement.startswith('INSERT INTO render_runs'):inserted.append(True);conn.info['fail_render_commit']=True
    def broken_commit(conn):
        if conn.info.pop('fail_render_commit',False):raise RuntimeError('late render fault')
    if fault=='stage_write':
        original=ArtifactStore.write_bytes;calls=[]
        def broken(self,**kwargs):
            calls.append(kwargs['kind'])
            if len(calls)==4:raise ArtifactFileError('private write fault')
            return original(self,**kwargs)
        monkeypatch.setattr(ArtifactStore,'write_bytes',broken)
    else:
        event.listen(client.app.state.engine,'before_cursor_execute',observe)
        event.listen(client.app.state.engine,'commit',broken_commit)
    try:reply=client.post(base+'/render',json={'expected_revision':1,'debug':True})
    finally:
        if fault=='late_commit':
            event.remove(client.app.state.engine,'before_cursor_execute',observe)
            event.remove(client.app.state.engine,'commit',broken_commit)
    assert reply.status_code==500
    if fault=='late_commit':assert inserted
    assert {p:p.read_bytes() for p in root.rglob('*') if p.is_file()}==paths
    assert client.get('/api/v1/sessions/'+sid).json()==before
    with repository.transaction(client.app.state.engine) as db:assert len(list(db.scalars(select(RenderRun))))==1


def test_debug_captures_single_actual_dispatch_and_has_same_full_bytes(setup,monkeypatch):
    from app.processing import enhancement
    client,_,_,base=setup
    client.put(base+'/config',json={'expected_revision':0,'config':{'corners':QUAD,'confirmed':True,'mode':'bw','threshold':{'method':'otsu'}}})
    plain=client.post(base+'/render',json={'expected_revision':1}).json()
    actual=enhancement.apply_denoise;calls=[]
    def observe(*args,**kwargs):calls.append(True);return actual(*args,**kwargs)
    monkeypatch.setattr(enhancement,'apply_denoise',observe)
    debug=client.post(base+'/render',json={'expected_revision':1,'debug':True}).json()
    assert len(calls)==1
    assert plain['render_run_id']!=debug['render_run_id']
    assert client.get('/api/v1/artifacts/'+plain['render_artifact_id']).content==client.get('/api/v1/artifacts/'+debug['render_artifact_id']).content
