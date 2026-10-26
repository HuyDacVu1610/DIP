"""Actual multipart -> shared worker -> SQLite/files -> guarded binary GET."""
from hashlib import sha256
from pathlib import Path
from uuid import uuid4, UUID

from fastapi.testclient import TestClient
import pytest
from sqlalchemy import select

from app.main import create_app
from app.processing.normalize import normalize_image, encode_normalized_png
from app.settings import MAX_UPLOAD_BYTES
from app.storage.models import Artifact
from app.storage.repository import transaction

FIXTURES = Path(__file__).resolve().parents[2]/'fixtures'


@pytest.fixture
def client(tmp_path):
    with TestClient(create_app(tmp_path/'data/scanner.sqlite3'),raise_server_exceptions=False) as value:
        yield value


def create(client):
    return client.post('/api/v1/sessions',json={'title':'Kiểm tra nhập'}).json()['id']


def upload(client,sid,name='exif_6.jpg',payload=None):
    return client.post(f'/api/v1/sessions/{sid}/pages',files={'file':(name,
        (FIXTURES/name).read_bytes() if payload is None else payload,'application/octet-stream')})


@pytest.mark.parametrize('name',['exif_6.jpg','alpha_rgba.png','png_named_jpeg.jpg'])
def test_upload_read_source_thumbnail_original_and_restart(client,tmp_path,name):
    sid = create(client)
    raw = (FIXTURES/name).read_bytes()
    response = upload(client,sid,name)
    assert response.status_code==201,response.text
    page = response.json()
    source = encode_normalized_png(normalize_image(raw))
    assert (page['width'],page['height'])==(source.width,source.height)
    assert page['revision']==0 and not page['effective_config']['confirmed']
    expected = {'original_artifact_id':raw,'normalized_artifact_id':source.png_bytes}
    for field in ('original_artifact_id','normalized_artifact_id','thumbnail_artifact_id'):
        blob = client.get('/api/v1/artifacts/'+page[field])
        assert blob.status_code==200
        assert blob.headers['x-content-type-options']=='nosniff'
        assert blob.headers['cache-control']=='private, no-store'
        assert 'inline' in blob.headers['content-disposition']
        if field in expected:
            assert blob.content==expected[field]
        assert blob.headers['content-type']==('image/jpeg' if field=='original_artifact_id' and raw.startswith(b'\xff\xd8') else 'image/png')
    assert client.get(f'/api/v1/sessions/{sid}').json()['pages']==[page]
    with TestClient(create_app(tmp_path/'data/scanner.sqlite3')) as reopened:
        assert reopened.get(f'/api/v1/sessions/{sid}').json()['pages']==[page]
        assert reopened.get('/api/v1/artifacts/'+page['normalized_artifact_id']).content==source.png_bytes


@pytest.mark.parametrize('name,status,code',[
    ('fake.jpg',415,'UNSUPPORTED_IMAGE'),('truncated.png',400,'INVALID_IMAGE'),
    ('animated.png',415,'UNSUPPORTED_IMAGE'),('pixel_over.png',413,'TOO_MANY_PIXELS'),
    ('too_narrow.png',400,'IMAGE_TOO_SMALL')])
def test_invalid_upload_does_not_change_existing_document(client,name,status,code):
    sid = create(client)
    old = upload(client,sid,'minimum.png').json()
    response = upload(client,sid,name)
    assert response.status_code==status,response.text
    assert response.json()['error']['code']==code
    assert client.get(f'/api/v1/sessions/{sid}').json()['pages']==[old]


def test_file_limit_counted_independent_of_claimed_mime_or_length(client):
    sid = create(client)
    raw = (FIXTURES/'minimum.png').read_bytes()
    response = upload(client,sid,'oversize.png',raw+b'\0'*(MAX_UPLOAD_BYTES-len(raw)+1))
    assert response.status_code==413 and response.json()['error']['code']=='FILE_TOO_LARGE'
    assert client.get(f'/api/v1/sessions/{sid}').json()['pages']==[]


@pytest.mark.parametrize('body,headers',[
    (b'bad',{'content-type':'application/json'}),
    (b'bad',{'content-type':'multipart/form-data'}),
    (b'--x\r\nwrong\r\n',{'content-type':'multipart/form-data; boundary=x'}),
])
def test_bad_multipart_has_safe_400(client,body,headers):
    response = client.post(f'/api/v1/sessions/{create(client)}/pages',content=body,headers=headers)
    assert response.status_code==400 and response.json()['error']['code']=='INVALID_REQUEST'


def test_one_file_field_only_and_empty_payload(client):
    sid = create(client)
    endpoint = f'/api/v1/sessions/{sid}/pages'
    raw = (FIXTURES/'minimum.png').read_bytes()
    for files in ([('file',('a.png',raw)),('file',('b.png',raw))],{'wrong':('a.png',raw)}):
        response = client.post(endpoint,files=files)
        assert response.status_code==400
    response = client.post(endpoint,files={'file':('a.png',raw)},data={'config':'private'})
    assert response.status_code==400 and 'private' not in response.text
    assert upload(client,sid,'empty.png',b'').status_code==400


def test_missing_bad_ids_and_private_paths_are_not_served(client):
    for sid in ('bad',str(uuid4())):
        assert upload(client,sid,'minimum.png').status_code==404
    for aid in ('bad',str(uuid4())):
        response = client.get('/api/v1/artifacts/'+aid)
        assert response.status_code==404 and response.json()['error']['code']=='ARTIFACT_NOT_FOUND'
    assert client.get('/data/scanner.sqlite3').status_code==404
    assert client.get('/api/v1/artifacts/..%2Fscanner.sqlite3').status_code==404


def test_upload_name_does_not_control_disk_path_and_file_corruption_is_not_served(client):
    sid = create(client)
    response = upload(client,sid,'../../escape.png',(FIXTURES/'minimum.png').read_bytes())
    assert response.status_code==201
    aid = response.json()['normalized_artifact_id']
    with transaction(client.app.state.engine) as db:
        artifact = db.get(Artifact,UUID(aid))
        assert artifact.path.startswith(f'sessions/{sid}/sources/') and 'escape' not in artifact.path
        path = client.app.state.artifacts.root/artifact.path
    path.write_bytes(b'corrupted')
    response = client.get('/api/v1/artifacts/'+aid)
    assert response.status_code==500 and response.json()['error']['code']=='STORAGE_FAILED'
    assert 'sessions/' not in response.text


def test_twenty_pages_limit_via_http(client):
    sid = create(client)
    for index in range(20):
        response = upload(client,sid,'minimum.png')
        assert response.status_code==201 and response.json()['position']==index
    response = upload(client,sid,'minimum.png')
    assert response.status_code==413 and response.json()['error']['code']=='PAGE_LIMIT_EXCEEDED'
    with transaction(client.app.state.engine) as db:
        assert len(db.scalars(select(Artifact)).all())==60


def test_append_and_bad_or_twenty_first_upload_preserve_existing_render_and_config(client):
    sid = create(client)
    old = upload(client,sid,'corners_rgb.png').json()
    path = f"/api/v1/sessions/{sid}/pages/{old['id']}"
    saved = client.put(path+'/config',json={'expected_revision':0,'config':{
        'mode':'gray','corners':[[0,0],[1,0],[1,1],[0,1]],'confirmed':True,'contrast':{'method':'clahe'}}}).json()
    rendered = client.post(path+'/render',json={'expected_revision':saved['revision'],'debug':True}).json()
    original = client.get(f'/api/v1/sessions/{sid}').json()['pages'][0]
    debug = client.get(path+'/debug?render_run_id='+rendered['render_run_id']).json()
    artifact_root = client.app.state.artifacts.root/'sessions'
    hashes = {p:sha256(p.read_bytes()).hexdigest() for p in artifact_root.rglob('*') if p.is_file()}
    bad = upload(client,sid,'broken.jpg',b'not an image')
    assert bad.status_code==415 and len(client.get(f'/api/v1/sessions/{sid}').json()['pages'])==1
    for index in range(1,20):
        response = upload(client,sid,'minimum.png')
        assert response.status_code==201 and response.json()['position']==index
    full = client.get(f'/api/v1/sessions/{sid}').json()
    assert full['pages'][0]==original and len(full['pages'])==20
    assert len({p['id'] for p in full['pages']})==20
    assert client.get(path+'/debug?render_run_id='+rendered['render_run_id']).json()==debug
    files_at_limit = {p:sha256(p.read_bytes()).hexdigest() for p in artifact_root.rglob('*') if p.is_file()}
    response = upload(client,sid,'minimum.png')
    assert response.status_code==413 and response.json()['error']['code']=='PAGE_LIMIT_EXCEEDED'
    assert client.get(f'/api/v1/sessions/{sid}').json()==full
    assert hashes=={p:sha256(p.read_bytes()).hexdigest() for p in hashes}
    assert files_at_limit=={p:sha256(p.read_bytes()).hexdigest() for p in artifact_root.rglob('*') if p.is_file()}


def test_http_import_commit_failure_keeps_old_files_and_pages(client):
    from sqlalchemy import event
    from sqlalchemy.exc import OperationalError
    from sqlalchemy.orm import Session
    sid = create(client)
    old = upload(client,sid,'minimum.png').json()
    root = client.app.state.artifacts.root/'sessions'
    before = {p:sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file()}
    def mark(db,context):
        db.info['wrote'] = True
    def fail(db):
        if db.info.get('wrote'):
            raise OperationalError('private path/SQL',{},Exception('private'))
    event.listen(Session,'after_flush',mark)
    event.listen(Session,'before_commit',fail)
    try:
        response = upload(client,sid,'minimum.png')
    finally:
        event.remove(Session,'after_flush',mark)
        event.remove(Session,'before_commit',fail)
    assert response.status_code==500 and response.json()['error']['code']=='STORAGE_FAILED'
    assert 'private' not in response.text
    assert before=={p:sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file()}
    assert client.get(f'/api/v1/sessions/{sid}').json()['pages']==[old]


def test_incomplete_multipart_closes_even_an_unfinished_file(client,monkeypatch):
    import starlette.formparsers as parser
    files = []
    original = parser.SpooledTemporaryFile
    def capture(*args,**kwargs):
        stream = original(*args,**kwargs)
        files.append(stream)
        return stream
    monkeypatch.setattr(parser,'SpooledTemporaryFile',capture)
    body = b'--x\r\nContent-Disposition: form-data; name="file"; filename="a.png"\r\n\r\n'+(FIXTURES/'minimum.png').read_bytes()
    response = client.post(f'/api/v1/sessions/{create(client)}/pages',content=body,
        headers={'Content-Type':'multipart/form-data; boundary=x'})
    try:
        assert response.status_code==400
        assert files and all(f.closed for f in files)
    finally:
        for stream in files:
            stream.close()


def test_exact_file_limit_and_streamed_body_limit(client):
    sid = create(client)
    raw = (FIXTURES/'minimum.png').read_bytes()
    response = upload(client,sid,'limit.png',raw+b'\0'*(MAX_UPLOAD_BYTES-len(raw)))
    assert response.status_code==201,response.text
    body = b'--x\r\nContent-Disposition: form-data; name="file"; filename="a.png"\r\n\r\n'
    response = client.post(f'/api/v1/sessions/{sid}/pages',content=iter([body,*([b'x'*(1024*1024)]*16),b'\r\n--x--\r\n']),
        headers={'Content-Type':'multipart/form-data; boundary=x'})
    assert response.status_code==413
    assert len(client.get(f'/api/v1/sessions/{sid}').json()['pages'])==1


def test_real_upload_route_respects_shared_executor_overload(client):
    from threading import Event
    started,release = Event(),Event()
    sid = create(client)
    def blocking():
        started.set()
        assert release.wait(5)
    jobs = client.portal.call(lambda:[client.app.state.processing.submit(blocking),
        client.app.state.processing.submit(lambda:None),client.app.state.processing.submit(lambda:None)])
    try:
        assert started.wait(2)
        response = upload(client,sid,'minimum.png')
        assert response.status_code==429 and response.json()['error']['code']=='PROCESSING_BUSY'
        assert client.get('/api/v1/health').json()=={'status':'ok'}
        assert client.get(f'/api/v1/sessions/{sid}').json()['pages']==[]
    finally:
        release.set()
        import asyncio
        async def finish():
            await asyncio.gather(*jobs)
        client.portal.call(finish)
