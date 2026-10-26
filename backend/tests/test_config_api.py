"""Full config replacement, real SQLite CAS and confirmation at the HTTP boundary."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier
from uuid import uuid4

from fastapi.testclient import TestClient
import pytest
from sqlalchemy import event

from app.main import create_app

FIXTURES = Path(__file__).resolve().parents[2]/'fixtures'
QUAD = [[0.,0.],[1.,0.],[1.,1.],[0.,1.]]


@pytest.fixture
def setup(tmp_path):
    with TestClient(create_app(tmp_path/'data/scanner.sqlite3'),raise_server_exceptions=False) as client:
        sid = client.post('/api/v1/sessions',json={'title':'Config CAS'}).json()['id']
        page = client.post(f'/api/v1/sessions/{sid}/pages',files={'file':('x.jpg',
            (FIXTURES/'exif_6.jpg').read_bytes(),'image/jpeg')}).json()
        yield client,sid,page,f"/api/v1/sessions/{sid}/pages/{page['id']}/config"


def test_full_config_defaults_noop_confirmation_and_persistence(setup,tmp_path):
    client,sid,page,url = setup
    before = client.get(f'/api/v1/sessions/{sid}').json()
    noop = client.put(url,json={'expected_revision':0,'config':{}})
    assert noop.status_code==200,noop.text
    assert noop.json()['revision']==0
    assert client.get(f'/api/v1/sessions/{sid}').json()==before
    draft = client.put(url,json={'expected_revision':0,'config':{'corners':QUAD}})
    assert draft.status_code==200,draft.text
    assert draft.json()['revision']==1
    assert draft.json()['effective_config']['confirmed'] is False
    confirmed = {'corners':QUAD,'confirmed':True,'mode':'gray','rotation':90}
    saved = client.put(url,json={'expected_revision':1,'config':confirmed})
    assert saved.status_code==200,saved.text
    assert saved.json()['revision']==2
    assert saved.json()['effective_config']['contrast']['method']=='clahe'
    assert 'threshold.method' in saved.json()['inactive_fields']
    assert client.put(url,json={'expected_revision':2,'config':saved.json()['effective_config']}).json()==saved.json()
    with TestClient(create_app(tmp_path/'data/scanner.sqlite3')) as reopened:
        row = reopened.get(f'/api/v1/sessions/{sid}').json()['pages'][0]
        assert row['revision']==2 and row['effective_config']==saved.json()['effective_config']
        assert row['normalized_artifact_id']==page['normalized_artifact_id']
    # Full replacement does not merge the old confirmed/rotation/corners.
    reset = client.put(url,json={'expected_revision':2,'config':{'mode':'color'}}).json()
    assert reset['revision']==3 and reset['effective_config']['corners'] is None
    assert reset['effective_config']['rotation']==0 and not reset['effective_config']['confirmed']


@pytest.mark.parametrize('config',[
    {'confirmed':True},{'rotation':True},{'mode':None},{'extra':'secret'},
    {'corners':[[0.,0.],[1.,1.],[1.,0.],[0.,1.]]},
    {'corners':[[0.,0.],[0.,1.],[1.,1.],[1.,0.]]},
    {'corners':[[0.,0.],[0.,0.],[1.,1.],[0.,1.]]},
    {'corners':[[0.,0.],[1.1,0.],[1.,1.],[0.,1.]]},
    {'threshold':{'block_size':4}},
    {'corners':[[.1,.1],[.2,.1],[.2,.2],[.1,.2]],'mode':'bw'},
])
def test_bad_config_cannot_change_page(setup,config):
    client,sid,page,url = setup
    before = client.get(f'/api/v1/sessions/{sid}').json()
    response = client.put(url,json={'expected_revision':0,'config':config})
    assert response.status_code==400,response.text
    assert response.json()['error']['code'] in ('INVALID_CONFIG','INVALID_QUAD')
    assert client.get(f'/api/v1/sessions/{sid}').json()==before


@pytest.mark.parametrize('body',[
    '{"expected_revision":0,"config":{"corners":[[NaN,0],[1,0],[1,1],[0,1]]}}',
    '{"expected_revision":0,"config":{"corners":[[Infinity,0],[1,0],[1,1],[0,1]]}}',
    '{"expected_revision":true,"config":{}}','{"expected_revision":-1,"config":{}}',
    '{"config":{}}','{"expected_revision":0,"config":{},"revision":5}',
])
def test_bad_envelope_or_nonfinite_has_sanitized_400(setup,body):
    client,sid,page,url = setup
    response = client.put(url,content=body,headers={'content-type':'application/json'})
    assert response.status_code==400,response.text
    assert response.json()['error']['code'] in ('INVALID_REQUEST','INVALID_CONFIG')
    assert response.json()['error']['details']=={}
    assert client.get(f'/api/v1/sessions/{sid}').json()['pages'][0]==page


def test_stale_even_noop_and_two_concurrent_updates(setup):
    client,sid,page,url = setup
    barrier = Barrier(2)
    def change(rotation):
        barrier.wait(timeout=10)
        return client.put(url,json={'expected_revision':0,'config':{'rotation':rotation}})
    with ThreadPoolExecutor(max_workers=2) as pool:
        responses = list(pool.map(change,[90,180]))
    assert sorted(r.status_code for r in responses)==[200,409]
    conflict = next(r for r in responses if r.status_code==409)
    assert conflict.json()['error']=={'code':'REVISION_CONFLICT',
        'message':'Cấu hình đã thay đổi; tải lại trang.',
        'details':{'expected_revision':0,'actual_revision':1}}
    current = client.get(f'/api/v1/sessions/{sid}').json()['pages'][0]
    assert current['revision']==1
    assert client.put(url,json={'expected_revision':0,'config':current['effective_config']}).status_code==409


@pytest.mark.parametrize('which',['missing_page','bad_page','other_owner','missing_session','bad_session'])
def test_owner_and_uuid_404(setup,which):
    client,sid,page,url = setup
    if which=='other_owner':
        other = client.post('/api/v1/sessions',json={}).json()['id']
        url = url.replace(sid,other)
    elif 'page' in which:
        url = url.replace(page['id'],'bad' if which=='bad_page' else str(uuid4()))
    else:
        url = url.replace(sid,'bad' if which=='bad_session' else str(uuid4()))
    response = client.put(url,json={'expected_revision':0,'config':{}})
    assert response.status_code==404,response.text
    assert response.json()['error']['code']==('SESSION_NOT_FOUND' if 'session' in which else 'PAGE_NOT_FOUND')


def test_commit_failure_rolls_back_all_state(setup):
    client,sid,page,url = setup
    before = client.get(f'/api/v1/sessions/{sid}').json()
    def fail(conn):
        raise RuntimeError('private commit fault')
    engine = client.app.state.engine
    event.listen(engine,'commit',fail)
    try:
        response = client.put(url,json={'expected_revision':0,'config':{'rotation':90}})
        assert response.status_code==500 and 'private' not in response.text
    finally:
        event.remove(engine,'commit',fail)
    assert client.get(f'/api/v1/sessions/{sid}').json()==before


def test_inactive_change_is_persisted_and_config_openapi_has_real_envelope(setup):
    client,sid,page,url = setup
    saved = client.put(url,json={'expected_revision':0,'config':{
        'mode':'color','threshold':{'c':19}}})
    assert saved.status_code==200,saved.text
    assert saved.json()['revision']==1
    assert saved.json()['effective_config']['threshold']['c']==19
    assert 'threshold.c' in saved.json()['inactive_fields']
    spec = client.get('/openapi.json').json()['paths']['/api/v1/sessions/{sid}/pages/{pid}/config']['put']
    assert '422' not in spec['responses']
    assert spec['responses']['400']['content']['application/json']['schema']['$ref'].endswith('/ErrorEnvelope')
