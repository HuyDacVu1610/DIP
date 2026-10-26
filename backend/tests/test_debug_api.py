"""Selection, history, ownership and missing-stage semantics of saved debug."""
from io import BytesIO
from uuid import UUID,uuid4

from fastapi.testclient import TestClient
import numpy as np
from PIL import Image
import pytest
from sqlalchemy import delete

from app.main import create_app
from app.storage import repository
from app.storage.models import Artifact,RenderRun


@pytest.fixture
def setup(tmp_path):
    with TestClient(create_app(tmp_path/'data/scanner.sqlite3'),raise_server_exceptions=False) as client:
        sid=client.post('/api/v1/sessions',json={}).json()['id']
        pixels=np.full((240,320,3),25,np.uint8);pixels[25:216,30:291]=240
        def upload(pixels):
            stream=BytesIO();Image.fromarray(pixels).save(stream,format='PNG')
            return client.post(f'/api/v1/sessions/{sid}/pages',files={'file':('p.png',stream.getvalue())}).json()
        page=upload(pixels);base=f"/api/v1/sessions/{sid}/pages/{page['id']}"
        yield client,sid,page,base,upload,tmp_path


def render(client,base,revision=0,debug=True,**overrides):
    saved=client.put(base+'/config',json={'expected_revision':revision,'config':{
        'corners':[[0,0],[1,0],[1,1],[0,1]],'confirmed':True,'mode':'bw','threshold':{'method':'otsu'}}|overrides})
    assert saved.status_code==200,saved.text
    result=client.post(base+'/render',json={'expected_revision':saved.json()['revision'],'debug':debug})
    assert result.status_code==200,result.text
    return result.json()


def test_two_revisions_and_same_revision_runs_never_mix(setup,monkeypatch):
    client,sid,page,base,_,_=setup
    first=render(client,base)
    second=render(client,base,1,threshold={'method':'adaptive_gaussian','block_size':51,'c':7},rotation=90)
    old=client.get(base+'/debug',params={'revision':1}).json()
    current=client.get(base+'/debug').json()
    assert old['run_id']==first['render_run_id'] and old['current_revision']==2
    assert current['run_id']==second['render_run_id'] and current['revision']==2
    assert old['metadata']['histogram']['threshold_scope']=='global'
    assert current['metadata']['histogram']['threshold_scope']=='local'
    assert old['metadata']['effective_config']['rotation']==0 and current['metadata']['effective_config']['rotation']==90
    assert set(a['id'] for a in old['artifacts'].values()).isdisjoint(a['id'] for a in current['artifacts'].values())
    plain=render(client,base,2,debug=False,threshold={'method':'adaptive_gaussian','block_size':51,'c':7},rotation=90)
    latest=client.get(base+'/debug',params={'revision':2}).json()
    assert latest['status']=='not_requested' and latest['run_id']==plain['render_run_id']
    assert set(latest['artifacts'])=={'full','preview'}
    specific=client.get(base+'/debug',params={'render_run_id':second['render_run_id']}).json()
    assert specific['status']=='available' and specific['run_id']==second['render_run_id']
    assert client.get('/api/v1/artifacts/'+plain['render_artifact_id']).content==client.get('/api/v1/artifacts/'+second['render_artifact_id']).content
    before=client.get('/api/v1/sessions/'+sid).json()
    def forbidden(*args,**kwargs):pytest.fail('Debug GET reran processing')
    monkeypatch.setattr('app.services.renders.render_document',forbidden)
    monkeypatch.setattr('app.services.detection.detect_document',forbidden)
    assert client.get(base+'/debug',params={'revision':1}).json()==old
    assert client.get('/api/v1/sessions/'+sid).json()==before


def test_detection_quad_manual_and_debug_off_keep_own_run(setup):
    client,_,page,base,upload,_=setup
    proposed=client.post(base+'/detect',json={'debug':True}).json()
    assert proposed['status']=='proposed'
    reply=client.get(base+'/debug',params={'detection_run_id':proposed['run_id']})
    assert reply.status_code==200,reply.text
    data=reply.json();assert data['kind']=='detection' and data['revision'] is None and data['status']=='available'
    assert data['metadata']['selected_trial_id']==proposed['selected_trial_id']
    assert {k:v['id'] for k,v in data['artifacts'].items()}==proposed['stage_artifacts']
    assert all(a['revision']==0 for a in data['artifacts'].values())
    blank=upload(np.full((240,320,3),255,np.uint8));other=base.replace(page['id'],blank['id'])
    manual=client.post(other+'/detect',json={'debug':True}).json()
    assert manual['status']=='manual_required'
    diagnostic=client.get(other+'/debug',params={'detection_run_id':manual['run_id']}).json()
    assert diagnostic['metadata']['result']['corners'] is None and diagnostic['metadata']['selected_trial_id'] is None
    assert diagnostic['artifacts'] and diagnostic['metadata']['trials']
    assert client.get(base+'/debug',params={'detection_run_id':manual['run_id']}).status_code==404
    off=client.post(other+'/detect',json={}).json()
    offdebug=client.get(other+'/debug',params={'detection_run_id':off['run_id']}).json()
    assert offdebug['status']=='not_requested' and offdebug['artifacts']=={}
    assert offdebug['metadata']['result']['status']=='manual_required'


@pytest.mark.parametrize('query',[
    'revision=-1','revision=true','revision=1.0','revision=1.2','revision=9223372036854775808',
    'revision=','revision=abc','detection_run_id=bad','render_run_id=bad','extra=1',
    f'revision=1&detection_run_id={uuid4()}',f'render_run_id={uuid4()}&detection_run_id={uuid4()}',
])
def test_invalid_debug_query_400(setup,query):
    client,_,_,base,_,_=setup
    reply=client.get(base+'/debug?'+query)
    assert reply.status_code==400,reply.text
    assert reply.json()['error']['code']=='INVALID_REQUEST'


def test_no_record_legacy_and_not_found_are_explicit(setup):
    client,sid,page,base,_,_=setup
    empty=client.get(base+'/debug').json()
    assert empty['status']=='not_recorded' and empty['metadata'] is None and empty['run_id'] is None
    for query in ({'revision':9},{'render_run_id':str(uuid4())},{'detection_run_id':str(uuid4())}):
        response=client.get(base+'/debug',params=query)
        assert response.status_code==404 and response.json()['error']['code']=='DEBUG_NOT_FOUND'
    other=client.post('/api/v1/sessions',json={}).json()['id']
    assert client.get(base.replace(sid,other)+'/debug').status_code==404
    assert client.get(base.replace(page['id'],str(uuid4()))+'/debug').status_code==404
    first=render(client,base)
    with repository.transaction(client.app.state.engine) as db:db.execute(delete(RenderRun))
    legacy=client.get(base+'/debug',params={'revision':1}).json()
    assert legacy['status']=='not_recorded' and legacy['artifacts']=={} and legacy['metadata'] is None
    assert client.get('/api/v1/artifacts/'+first['render_artifact_id']).status_code==200


@pytest.mark.parametrize('fault',['file','hash','database','metadata_ref','metadata_missing','foreign_owner'])
def test_missing_or_wrong_stage_is_incomplete_without_substitution(setup,fault):
    client,sid,page,base,upload,tmp=setup
    result=render(client,base)
    if fault=='foreign_owner':
        second=upload(np.full((240,320,3),255,np.uint8))
        foreign=render(client,base.replace(page['id'],second['id']))
    with repository.transaction(client.app.state.engine) as db:
        run=db.get(RenderRun,UUID(result['render_run_id']));meta=run.metadata_json
        ref=meta['artifacts']['prepared_gray'];artifact=db.get(Artifact,UUID(ref['id']))
        if fault=='file':(tmp/'data'/artifact.path).unlink()
        elif fault=='hash':(tmp/'data'/artifact.path).write_bytes(b'corrupt')
        elif fault=='database':db.delete(artifact)
        elif fault=='metadata_ref':meta['artifacts']['prepared_gray']['id']=str(uuid4())
        elif fault=='metadata_missing':del meta['artifacts']['prepared_gray']
        else:
            other=db.get(RenderRun,UUID(foreign['render_run_id']))
            meta['artifacts']['prepared_gray']=other.metadata_json['artifacts']['prepared_gray']
        # JSON is immutable-at-commit: assign a new value, rather than in-place mutation tracking.
        import json
        from sqlalchemy.orm.attributes import flag_modified
        run.metadata_json=json.loads(json.dumps(meta));flag_modified(run,'metadata_json')
    reply=client.get(base+'/debug',params={'render_run_id':result['render_run_id']})
    assert reply.status_code==200,reply.text
    data=reply.json();assert data['status']=='incomplete' and 'prepared_gray' in data['missing_stages']
    assert 'prepared_gray' not in data['artifacts']
    assert data['run_id']==result['render_run_id'] and data['artifacts']['full']['id']==result['render_artifact_id']
    assert 'path' not in str(data['artifacts'])


def test_corrupt_source_binding_is_sanitized_and_never_returns_wrong_metadata(setup):
    client,_,_,base,_,_=setup
    result=render(client,base)
    with repository.transaction(client.app.state.engine) as db:
        row=db.get(RenderRun,UUID(result['render_run_id']))
        row.metadata_json=row.metadata_json|{'source':{'artifact_id':str(uuid4()),'sha256':'private path'}}
    response=client.get(base+'/debug')
    assert response.status_code==500 and response.json()['error']['code']=='STORAGE_FAILED'
    assert 'private' not in response.text
