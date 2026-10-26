"""HTTP -> service -> actual SQLite, with isolated app lifespan per test."""
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.storage.models import Artifact, PageConfigRecord, ScanPage
from app.storage.repository import transaction
from app.processing.config import get_preset


@pytest.fixture
def client(tmp_path):
    app = create_app(tmp_path/'data/scanner.sqlite3')
    with TestClient(app,raise_server_exceptions=False) as value:
        yield value


def test_create_list_empty_detail_and_restart(client,tmp_path):
    assert client.get('/api/v1/sessions').json()=={'items':[],'limit':20,'offset':0,'total':0}
    response = client.post('/api/v1/sessions',json={'title':'  Bài tập tiếng Việt  '})
    assert response.status_code==201,response.text
    created = response.json()
    assert created['title']=='Bài tập tiếng Việt' and created['created_at'].endswith('Z')
    assert set(created)=={'id','title','created_at','updated_at'}
    sid = created['id']
    detail = client.get(f'/api/v1/sessions/{sid}')
    assert detail.status_code==200 and detail.json()==created|{'pages':[]}
    listing = client.get('/api/v1/sessions?limit=1&offset=0').json()
    assert listing=={'items':[created],'limit':1,'offset':0,'total':1}
    with TestClient(create_app(tmp_path/'data/scanner.sqlite3')) as reopened:
        assert reopened.get(f'/api/v1/sessions/{sid}').json()==detail.json()
    assert client.get('/api/v1/health').json()=={'status':'ok'}


@pytest.mark.parametrize('sid',['not-a-uuid',str(uuid4()),'00000000-0000-0000-0000-000000000000'])
def test_missing_or_invalid_session_has_uniform_404(client,sid):
    response = client.get(f'/api/v1/sessions/{sid}')
    assert response.status_code==404
    assert response.json()=={'error':{'code':'SESSION_NOT_FOUND','message':'Không tìm thấy tài liệu.','details':{}}}


@pytest.mark.parametrize('body',[{'title':''},{'title':None},{'title':123},{'unexpected':'secret'}])
def test_bad_create_returns_safe_error_envelope(client,body):
    response = client.post('/api/v1/sessions',json=body)
    assert response.status_code==400
    assert response.json()['error']['code']=='INVALID_REQUEST'
    assert 'secret' not in response.text and 'Traceback' not in response.text
    assert client.get('/api/v1/sessions').json()['total']==0


@pytest.mark.parametrize('query',['limit=0','limit=101','limit=no','offset=-1'])
def test_bad_pagination_is_rejected(client,query):
    response = client.get('/api/v1/sessions?'+query)
    assert response.status_code==400 and response.json()['error']['code']=='INVALID_REQUEST'


def test_default_title_pagination_and_stable_ties(client):
    ids = [client.post('/api/v1/sessions',json={}).json()['id'] for _ in range(3)]
    from datetime import UTC, datetime
    from app.storage.models import ScanSession
    with transaction(client.app.state.engine) as db:
        for sid in ids:
            from uuid import UUID
            db.get(ScanSession,UUID(sid)).updated_at = datetime(2026,10,17,tzinfo=UTC)
    first = client.get('/api/v1/sessions?limit=2&offset=0').json()
    second = client.get('/api/v1/sessions?limit=2&offset=2').json()
    assert [item['id'] for item in first['items']+second['items']]==sorted(ids)
    assert first['total']==second['total']==3
    assert all(item['title']=='Tài liệu chưa đặt tên' for item in first['items'])


def seed(db,sid,position):
    from uuid import UUID
    sid = UUID(sid)
    pid = uuid4()
    aids = [uuid4() for _ in range(3)]
    db.add(ScanPage(id=pid,session_id=sid,position=position,width=100,height=80,
        original_artifact_id=aids[0],normalized_artifact_id=aids[1],thumbnail_artifact_id=aids[2]))
    for aid,kind in zip(aids,('original','normalized','thumbnail')):
        db.add(Artifact(id=aid,session_id=sid,page_id=pid,kind=kind,path=f'sources/{aid}.png',
            mime='image/png',byte_size=20,sha256='a'*64,width=100,height=80))
    db.add(PageConfigRecord(page_id=pid,session_id=sid,revision=0,config_json=get_preset().model_dump(mode='json')))
    return str(pid)


def test_detail_returns_real_ordered_pages_only_from_its_session(client):
    sid = client.post('/api/v1/sessions',json={}).json()['id']
    other = client.post('/api/v1/sessions',json={}).json()['id']
    with transaction(client.app.state.engine) as db:
        second,first = seed(db,sid,1),seed(db,sid,0)
        unrelated = seed(db,other,0)
    response = client.get(f'/api/v1/sessions/{sid}')
    assert response.status_code==200,response.text
    pages = response.json()['pages']
    assert [p['id'] for p in pages]==[first,second] and unrelated not in response.text
    assert all(p['session_id']==sid and p['revision']==0 and p['render_revision'] is None for p in pages)
    assert all(p['effective_config']==get_preset().model_dump(mode='json') for p in pages)
    assert 'sources/' not in response.text and 'path' not in response.text


def test_db_failure_rolls_back_create_and_does_not_expose_sql(client,monkeypatch):
    from sqlalchemy.orm import Session
    from sqlalchemy.exc import OperationalError
    from sqlalchemy import event
    def fail(self):
        raise OperationalError('private SQL and path',{},Exception('secret'))
    event.listen(Session,'before_commit',fail)
    try:
        response = client.post('/api/v1/sessions',json={})
    finally:
        event.remove(Session,'before_commit',fail)
    assert response.status_code==500
    assert response.json()['error']['code']=='STORAGE_FAILED'
    assert 'private' not in response.text and 'secret' not in response.text
    assert client.get('/api/v1/sessions').json()['total']==0


def test_http_and_internal_errors_keep_safe_envelope_and_protocol_headers(client,monkeypatch):
    response = client.post('/api/v1/health')
    assert response.status_code==405 and response.headers['allow']=='GET'
    assert response.json()['error']['code']=='METHOD_NOT_ALLOWED'
    assert client.get('/not-a-route').json()['error']['code']=='NOT_FOUND'
    def fail(*args):
        raise RuntimeError('private path and secret')
    monkeypatch.setattr('app.services.sessions.create_document',fail)
    response = client.post('/api/v1/sessions',json={})
    assert response.status_code==500 and response.json()['error']['code']=='INTERNAL_ERROR'
    assert 'private' not in response.text and 'secret' not in response.text


def test_broken_page_metadata_fails_instead_of_silently_hiding_the_page(client):
    sid = client.post('/api/v1/sessions',json={}).json()['id']
    from uuid import UUID
    with transaction(client.app.state.engine) as db:
        pid = seed(db,sid,0)
    with transaction(client.app.state.engine) as db:
        db.delete(db.get(PageConfigRecord,UUID(pid)))
    response = client.get(f'/api/v1/sessions/{sid}')
    assert response.status_code==500 and response.json()['error']['code']=='STORAGE_FAILED'


def test_openapi_describes_only_implemented_paths_and_actual_error_shape(client):
    schema = client.get('/openapi.json').json()
    assert set(schema['paths'])=={'/api/v1/health','/api/v1/sessions','/api/v1/sessions/{sid}',
        '/api/v1/sessions/{sid}/pages','/api/v1/sessions/{sid}/pages/{pid}',
        '/api/v1/artifacts/{aid}','/api/v1/sessions/{sid}/page-order',
        '/api/v1/sessions/{sid}/exports',
        '/api/v1/sessions/{sid}/pages/{pid}/config',
        '/api/v1/sessions/{sid}/pages/{pid}/render',
        '/api/v1/sessions/{sid}/pages/{pid}/detect',
        '/api/v1/sessions/{sid}/pages/{pid}/debug'}
    for path in ('/api/v1/sessions','/api/v1/sessions/{sid}'):
        for operation in schema['paths'][path].values():
            responses = operation['responses']
            assert '400' in responses and '500' in responses and '422' not in responses
            assert responses['400']['content']['application/json']['schema']['$ref'].endswith('/ErrorEnvelope')


def test_rename_preserves_pages_revision_render_and_survives_restart(client,tmp_path):
    from pathlib import Path
    from hashlib import sha256
    sid = client.post('/api/v1/sessions',json={'title':'Tên cũ'}).json()['id']
    fixtures = Path(__file__).resolve().parents[2]/'fixtures'
    page = client.post(f'/api/v1/sessions/{sid}/pages',files={'file':('page.png',(fixtures/'corners_rgb.png').read_bytes())}).json()
    path = f"/api/v1/sessions/{sid}/pages/{page['id']}"
    saved = client.put(path+'/config',json={'expected_revision':0,'config':{'corners':[[0,0],[1,0],[1,1],[0,1]],'confirmed':True}}).json()
    rendered = client.post(path+'/render',json={'expected_revision':saved['revision'],'debug':True}).json()
    before = client.get('/api/v1/sessions/'+sid).json()
    debug = client.get(path+'/debug?render_run_id='+rendered['render_run_id']).json()
    hashes = {p:sha256(p.read_bytes()).hexdigest() for p in (client.app.state.artifacts.root/'sessions').rglob('*') if p.is_file()}
    response = client.patch('/api/v1/sessions/'+sid,json={'title':'  Tài liệu tiếng Việt mới  '})
    assert response.status_code==200,response.text
    renamed = response.json()
    assert renamed['title']=='Tài liệu tiếng Việt mới' and renamed['id']==sid
    assert renamed['created_at']==before['created_at'] and renamed['updated_at']>before['updated_at']
    after = client.get('/api/v1/sessions/'+sid).json()
    assert after==renamed|{'pages':before['pages']}
    assert client.get(path+'/debug?render_run_id='+rendered['render_run_id']).json()==debug
    assert hashes=={p:sha256(p.read_bytes()).hexdigest() for p in hashes}
    assert client.patch('/api/v1/sessions/'+sid,json={'title':'Tài liệu tiếng Việt mới'}).json()==renamed
    assert client.get('/api/v1/sessions').json()['items'][0]==renamed
    with TestClient(create_app(tmp_path/'data/scanner.sqlite3')) as reopened:
        assert reopened.get('/api/v1/sessions/'+sid).json()==after


@pytest.mark.parametrize('body',[{}, {'title':None}, {'title':123}, {'title':''}, {'title':'  '}, {'title':'x'*201}, {'title':'Valid','revision':1}])
def test_rename_rejects_invalid_title_without_changing_metadata(client,body):
    created = client.post('/api/v1/sessions',json={}).json()
    response = client.patch('/api/v1/sessions/'+created['id'],json=body)
    assert response.status_code==400 and response.json()['error']['code']=='INVALID_REQUEST'
    assert client.get('/api/v1/sessions/'+created['id']).json()==created|{'pages':[]}


@pytest.mark.parametrize('sid',['bad-id',str(uuid4())])
def test_rename_missing_document_returns_uniform_404(client,sid):
    response = client.patch('/api/v1/sessions/'+sid,json={'title':'Tên mới'})
    assert response.status_code==404 and response.json()['error']['code']=='SESSION_NOT_FOUND'


def test_rename_commit_failure_rolls_back_and_sanitizes(client):
    from sqlalchemy import event
    from sqlalchemy.orm import Session
    from sqlalchemy.exc import OperationalError
    created = client.post('/api/v1/sessions',json={}).json()
    def fail(db):raise OperationalError('private SQL',{},Exception('secret'))
    event.listen(Session,'before_commit',fail)
    try:response = client.patch('/api/v1/sessions/'+created['id'],json={'title':'Tên mới'})
    finally:event.remove(Session,'before_commit',fail)
    assert response.status_code==500 and response.json()['error']['code']=='STORAGE_FAILED'
    assert 'secret' not in response.text and 'private' not in response.text
    assert client.get('/api/v1/sessions/'+created['id']).json()==created|{'pages':[]}
