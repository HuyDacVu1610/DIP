"""Production HTTP render dispatch, state errors and shared-worker backpressure."""
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
from pathlib import Path
from threading import Event
from uuid import UUID, uuid4

from fastapi.testclient import TestClient
import pytest
from sqlalchemy import delete

from app.main import create_app
from app.processing.normalize import normalize_image
from app.processing.render import encode_render_images, render_document
from app.services import renders
from app.storage import repository
from app.storage.models import ScanPage

FIXTURES = Path(__file__).resolve().parents[2]/'fixtures'
QUAD = [[0.,0.],[1.,0.],[1.,1.],[0.,1.]]


@pytest.fixture
def setup(tmp_path):
    with TestClient(create_app(tmp_path/'data/scanner.sqlite3'),raise_server_exceptions=False) as client:
        sid = client.post('/api/v1/sessions',json={'title':'HTTP render'}).json()['id']
        raw = (FIXTURES/'exif_6.jpg').read_bytes()
        page = client.post(f'/api/v1/sessions/{sid}/pages',files={'file':('x.jpg',raw)}).json()
        base = f"/api/v1/sessions/{sid}/pages/{page['id']}"
        yield client,sid,page,base,raw


def confirm(client,base,revision=0,**config):
    response = client.put(base+'/config',json={'expected_revision':revision,
        'config':{'corners':QUAD,'confirmed':True}|config})
    assert response.status_code==200,response.text
    return response.json()


@pytest.mark.parametrize('mode,rotation',[('color',0),('gray',90),('bw',270)])
def test_upload_config_render_get_exact_outputs_and_reopen(setup,tmp_path,mode,rotation):
    client,sid,page,base,raw = setup
    config = confirm(client,base,mode=mode,rotation=rotation,threshold={'method':'otsu'})
    response = client.post(base+'/render',json={'expected_revision':1})
    assert response.status_code==200,response.text
    result = response.json()
    assert result['page_id']==page['id'] and result['revision']==1
    assert result['warnings']==[]
    assert all(value>=0 for value in result['timings_ms'].values())
    expected = encode_render_images(render_document(normalize_image(raw),config['effective_config']).enhancement.image)
    assert (result['width'],result['height'])==(expected.full.width,expected.full.height)
    for name,payload in [('render',expected.full.png_bytes),('preview',expected.preview.png_bytes)]:
        aid = result[name+'_artifact_id']
        blob = client.get('/api/v1/artifacts/'+aid)
        assert blob.status_code==200 and blob.content==payload
        assert blob.headers['content-type']=='image/png'
        with repository.transaction(client.app.state.engine) as db:
            record = repository.get_artifact(db,UUID(sid),UUID(aid))
            assert record.kind==name and record.revision==1 and str(record.page_id)==page['id']
            assert record.sha256==sha256(blob.content).hexdigest()
    detail = client.get(f'/api/v1/sessions/{sid}').json()
    assert detail['pages'][0]['revision']==detail['pages'][0]['render_revision']==1
    with TestClient(create_app(tmp_path/'data/scanner.sqlite3')) as reopened:
        assert reopened.get(f'/api/v1/sessions/{sid}').json()==detail
        assert reopened.get('/api/v1/artifacts/'+result['render_artifact_id']).content==expected.full.png_bytes


def test_unconfirmed_and_stale_409_never_render(setup,monkeypatch):
    client,sid,page,base,_ = setup
    def forbidden(*args,**kwargs):
        pytest.fail('Unconfirmed or stale input entered core')
    monkeypatch.setattr(renders,'render_document',forbidden)
    response = client.post(base+'/render',json={'expected_revision':0})
    assert response.status_code==409 and response.json()['error']['code']=='PAGE_NOT_CONFIRMED'
    assert response.json()['error']['details']=={}
    confirm(client,base)
    stale = client.post(base+'/render',json={'expected_revision':0})
    assert stale.status_code==409 and stale.json()['error']['code']=='REVISION_CONFLICT'
    assert stale.json()['error']['details']=={'expected_revision':0,'actual_revision':1}
    assert client.get(f'/api/v1/sessions/{sid}').json()['pages'][0]['render_revision'] is None


@pytest.mark.parametrize('body',[{}, {'expected_revision':True},{'expected_revision':-1},
    {'expected_revision':'1'},{'expected_revision':0,'debug':'false'},
    {'expected_revision':0,'extra':1}])
def test_invalid_request_400(setup,body):
    client,_,_,base,_ = setup
    response = client.post(base+'/render',json=body)
    assert response.status_code==400 and response.json()['error']['code']=='INVALID_REQUEST'


@pytest.mark.parametrize('which',['session','page','bad_session','bad_page','other_owner'])
def test_owner_and_uuid_404(setup,which):
    client,sid,page,base,_ = setup
    if which=='other_owner':
        other = client.post('/api/v1/sessions',json={}).json()['id']
        base = base.replace(sid,other)
    elif 'session' in which:
        base = base.replace(sid,'bad' if which.startswith('bad') else str(uuid4()))
    else:
        base = base.replace(page['id'],'bad' if which.startswith('bad') else str(uuid4()))
    response = client.post(base+'/render',json={'expected_revision':0})
    assert response.status_code==404,response.text
    assert response.json()['error']['code']==('SESSION_NOT_FOUND' if 'session' in which else 'PAGE_NOT_FOUND')


@pytest.mark.parametrize('mutation',['config','delete'])
def test_snapshot_changes_while_http_render_running(setup,monkeypatch,mutation):
    client,sid,page,base,_ = setup
    confirm(client,base)
    started,release = Event(),Event()
    original = renders.render_document
    def blocked(*args,**kwargs):
        started.set()
        assert release.wait(10)
        return original(*args,**kwargs)
    monkeypatch.setattr(renders,'render_document',blocked)
    with ThreadPoolExecutor(max_workers=1) as caller:
        future = caller.submit(client.post,base+'/render',json={'expected_revision':1})
        try:
            assert started.wait(5)
            assert client.get('/api/v1/health').json()=={'status':'ok'}
            if mutation=='config':
                confirm(client,base,revision=1,rotation=90)
            else:
                with repository.transaction(client.app.state.engine) as db:
                    db.execute(delete(ScanPage).where(ScanPage.id==UUID(page['id'])))
        finally:
            release.set()
        response = future.result(timeout=10)
    assert response.status_code==(409 if mutation=='config' else 404),response.text
    assert len(list(client.app.state.artifacts.root.rglob('*.png')))==2  # only source + thumbnail


def test_real_render_uses_shared_worker_and_does_not_block_health(setup,monkeypatch):
    import asyncio
    client,sid,page,base,raw = setup
    confirm(client,base)
    started,release = Event(),Event()
    original = renders.render_document
    def blocked(*args,**kwargs):
        started.set()
        assert release.wait(10)
        return original(*args,**kwargs)
    monkeypatch.setattr(renders,'render_document',blocked)
    with ThreadPoolExecutor(max_workers=1) as caller:
        active = caller.submit(client.post,base+'/render',json={'expected_revision':1})
        try:
            assert started.wait(5)
            pending = client.portal.call(lambda:[client.app.state.processing.submit(lambda:None) for _ in range(2)])
            overflow = client.post(base+'/render',json={'expected_revision':1})
            assert overflow.status_code==429 and overflow.json()['error']['code']=='PROCESSING_BUSY'
            upload = client.post(f'/api/v1/sessions/{sid}/pages',files={'file':('x.jpg',raw)})
            assert upload.status_code==429  # same executor instance as import
            assert client.get('/api/v1/health').json()=={'status':'ok'}
        finally:
            release.set()
        assert active.result(timeout=10).status_code==200
        async def finish():
            await asyncio.gather(*pending)
        client.portal.call(finish)


def test_processing_failure_sanitized_and_worker_recovers(setup,monkeypatch):
    client,sid,page,base,_ = setup
    confirm(client,base)
    before = client.get(f'/api/v1/sessions/{sid}').json()
    original = renders.render_document
    def fail(*args,**kwargs):
        raise renders.RenderProcessingError('private path C:/secret.png')
    monkeypatch.setattr(renders,'render_document',fail)
    response = client.post(base+'/render',json={'expected_revision':1})
    assert response.status_code==500 and response.json()['error']['code']=='PROCESSING_FAILED'
    assert 'secret' not in response.text and response.json()['error']['details']=={}
    assert client.get(f'/api/v1/sessions/{sid}').json()==before
    monkeypatch.setattr(renders,'render_document',original)
    assert client.post(base+'/render',json={'expected_revision':1}).status_code==200


def test_debug_request_returns_saved_run_without_deferred_warning(setup):
    client,sid,page,base,_ = setup
    confirm(client,base)
    response = client.post(base+'/render',json={'expected_revision':1,'debug':True})
    assert response.status_code==200,response.text
    assert response.json()['warnings']==[]
    assert response.json()['render_run_id']
    debug=client.get(base+'/debug',params={'render_run_id':response.json()['render_run_id']})
    assert debug.status_code==200 and debug.json()['status']=='available'
    assert 'debug' not in response.json()


def test_render_openapi_matches_response_and_envelope(setup):
    client,_,_,_,_ = setup
    schema = client.get('/openapi.json').json()
    op = schema['paths']['/api/v1/sessions/{sid}/pages/{pid}/render']['post']
    assert op['responses']['200']['content']['application/json']['schema']['$ref'].endswith('/RenderRead')
    assert op['responses']['400']['content']['application/json']['schema']['$ref'].endswith('/ErrorEnvelope')
    assert '422' not in op['responses']
