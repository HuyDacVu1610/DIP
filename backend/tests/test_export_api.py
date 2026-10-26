from concurrent.futures import ThreadPoolExecutor
from threading import Event
from pathlib import Path
from hashlib import sha256
from uuid import UUID,uuid4
import pytest
from sqlalchemy import select,func
from app.storage.models import ExportRecord
from app.storage import repository
from app.services.session_guards import reserve_export
from test_reopen import saved_document
from test_render_service import files
from fastapi.testclient import TestClient
from app.main import create_app
from test_import_api import create,upload


def body(pages,format='pdf'):
    return {'format':format,'pages':[{'page_id':p['id'],'revision':1} for p in pages]}


@pytest.mark.parametrize('format',['pdf','png','jpg'])
def test_export_http_commits_receipt_and_returns_exact_completed_artifact(saved_document,format):
    c,_,sid,pages,_,_=saved_document;url='/api/v1/sessions/'+sid
    selected=[pages[i] for i in [2,0,1]] if format=='pdf' else pages[:1]
    request=body(selected,format);before=c.get(url).json()
    response=c.post(url+'/exports',json=request)
    assert response.status_code==201,response.text
    result=response.json();assert result['session_id']==sid and result['pages']==request['pages']
    artifact=c.get('/api/v1/artifacts/'+result['artifact_id'])
    assert artifact.status_code==200 and artifact.headers['x-content-type-options']=='nosniff'
    assert artifact.headers['content-type']=={'pdf':'application/pdf','png':'image/png','jpg':'image/jpeg'}[format]
    assert artifact.content.startswith(b'%PDF-' if format=='pdf' else b'\x89PNG' if format=='png' else b'\xff\xd8')
    assert c.get(url).json()==before
    with repository.transaction(c.app.state.engine) as db:
        record=db.get(ExportRecord,UUID(result['id']))
        assert record.page_snapshot_json==request['pages']


@pytest.mark.parametrize('case',['duplicate','invalid','stale','unconfirmed','foreign','missing'])
def test_invalid_export_is_explicit_and_keeps_metadata_and_files(saved_document,case):
    c,_,sid,pages,_,_=saved_document;url='/api/v1/sessions/'+sid;request=body(pages[:1]);status=400
    if case=='duplicate':request['pages']*=2
    elif case=='invalid':request['margin_mm']=31
    elif case=='stale':request['pages'][0]['revision']=0;status=409
    elif case=='foreign':request['pages'][0]['page_id']=str(uuid4());status=404
    else:
        c.put(url+'/pages/'+pages[0]['id']+'/config',json={'expected_revision':1,'config':{
            'mode':'gray','confirmed':case=='missing','corners':[[0,0],[1,0],[1,1],[0,1]]}})
        request['pages'][0]['revision']=2;status=409
    before=c.get(url).json();hashes=files(c.app.state.artifacts)
    response=c.post(url+'/exports',json=request);assert response.status_code==status,response.text
    if case=='missing':assert response.json()['error']['details']['pages']==request['pages']
    assert c.get(url).json()==before and files(c.app.state.artifacts)==hashes
    assert c.patch(url,json={'title':before['title']}).status_code==200


def test_export_http_overload_releases_lease_and_success_failure_keep_worker_usable(saved_document,monkeypatch):
    c,_,sid,pages,_,_=saved_document;engine=c.app.state.engine;url='/api/v1/sessions/'+sid+'/exports';request=body(pages)
    started,release=Event(),Event()
    def hold():started.set();assert release.wait(6)
    first=c.portal.call(lambda:[c.app.state.processing.submit(hold)])[0]
    try:
        assert started.wait(3)
        pending=c.portal.call(lambda:[c.app.state.processing.submit(lambda:None) for _ in range(2)])
        assert c.post(url,json=request).status_code==429
        reserve_export(engine,UUID(sid)).release()
        c.portal.call(lambda:[f.cancel() for f in pending])
    finally:release.set()
    c.portal.call(lambda:c.app.state.processing.run(lambda:None))
    def fail(*args,**kwargs):raise RuntimeError('private encoder failure')
    monkeypatch.setattr('app.services.exports.append_pdf_page',fail)
    hashes=files(c.app.state.artifacts);response=c.post(url,json=request)
    assert response.status_code==500 and response.json()['error']['code']=='PROCESSING_FAILED'
    assert 'private encoder' not in response.text and files(c.app.state.artifacts)==hashes
    monkeypatch.undo()
    assert c.post(url,json=request).status_code==201


def test_export_http_holds_session_until_commit_and_rejects_second_export(saved_document,monkeypatch):
    from app.api import exports
    c,_,sid,pages,_,_=saved_document;url='/api/v1/sessions/'+sid;started,release=Event(),Event();original=exports.publish_export
    def hold(*args):
        started.set();assert release.wait(8);return original(*args)
    monkeypatch.setattr(exports,'publish_export',hold)
    with ThreadPoolExecutor(max_workers=1) as pool:
        active=pool.submit(c.post,url+'/exports',json=body(pages))
        try:
            assert started.wait(3)
            assert c.post(url+'/exports',json=body(pages)).status_code==409
            assert c.patch(url,json={'title':'Blocked'}).status_code==409
            assert c.get('/api/v1/health').status_code==200
        finally:release.set()
        assert active.result(timeout=8).status_code==201
    assert c.patch(url,json={'title':'Unlocked'}).status_code==200


@pytest.mark.parametrize('fail_mid_pdf',[False,True])
def test_real_export_blocks_all_owner_mutations_until_success_or_partial_encode_failure(saved_document,monkeypatch,fail_mid_pdf):
    from app.api import exports as route
    from app.services import exports as service
    c,_,sid,pages,_,_=saved_document;url='/api/v1/sessions/'+sid;pageurl=url+'/pages/'+pages[0]['id']
    other=create(c);before=c.get(url).json();old_files=files(c.app.state.artifacts)
    started,release=Event(),Event();publish=route.publish_export;append=service.append_pdf_page;calls=[]
    def held(*args):
        started.set();assert release.wait(12);return publish(*args)
    def partial(*args,**kwargs):
        calls.append(True)
        if fail_mid_pdf and len(calls)==2:raise RuntimeError('controlled private mid-PDF failure')
        return append(*args,**kwargs)
    monkeypatch.setattr(route,'publish_export',held);monkeypatch.setattr(service,'append_pdf_page',partial)
    payload=(Path(__file__).resolve().parents[2]/'fixtures/corners_rgb.png').read_bytes()
    actions=[
        lambda:c.patch(url,json={'title':'Blocked'}),
        lambda:c.put(pageurl+'/config',json={'expected_revision':1,'config':{'mode':'gray'}}),
        lambda:c.put(url+'/page-order',json={'page_ids':[p['id'] for p in reversed(pages)]}),
        lambda:c.delete(pageurl),lambda:c.delete(url),
        lambda:c.post(url+'/pages',files={'file':('safe.png',payload,'image/png')}),
        lambda:c.post(pageurl+'/render',json={'expected_revision':1}),
        lambda:c.post(pageurl+'/detect',json={'debug':True}),
        lambda:c.post(url+'/exports',json=body(pages)),
    ]
    with ThreadPoolExecutor(max_workers=1) as pool:
        active=pool.submit(c.post,url+'/exports',json=body(list(reversed(pages))))
        try:
            assert started.wait(5)
            for action in actions:
                r=action();assert r.status_code==409,r.text
                assert r.json()['error']['code']=='SESSION_BUSY'
            assert not active.done() and c.get(url).json()==before
            assert files(c.app.state.artifacts)==old_files
            with repository.transaction(c.app.state.engine) as db:
                assert db.scalar(select(func.count()).select_from(ExportRecord))==0
            assert c.get('/api/v1/health').status_code==200
            assert c.patch('/api/v1/sessions/'+other,json={'title':'Other document remains writable'}).status_code==200
            assert c.get(url).json()==before
            # The allowed rename changes SQLite bytes; keep the exact post-rename
            # baseline when checking that the failing export itself writes nothing.
            old_files=files(c.app.state.artifacts)
        finally:release.set()
        r=active.result(timeout=12)
    assert c.get(url).json()==before
    if fail_mid_pdf:
        assert len(calls)==2 and r.status_code==500
        assert r.json()['error']['code']=='PROCESSING_FAILED' and 'private' not in r.text
        assert files(c.app.state.artifacts)==old_files
        with repository.transaction(c.app.state.engine) as db:
            assert db.scalar(select(func.count()).select_from(ExportRecord))==0
    else:
        assert r.status_code==201 and len(calls)==3
        artifact=c.get('/api/v1/artifacts/'+r.json()['artifact_id'])
        assert artifact.status_code==200 and artifact.content.endswith(b'%%EOF\n')
    monkeypatch.undo()
    assert c.patch(url,json={'title':'Unlocked after outcome'}).status_code==200
    assert c.post(url+'/exports',json=body(pages)).status_code==201


@pytest.mark.parametrize('format',['pdf','png','jpg'])
def test_committed_exports_keep_exact_snapshot_bytes_after_config_change_and_sequential_app_restart(tmp_path,format):
    database=tmp_path/'data/scanner.sqlite3'
    with TestClient(create_app(database),raise_server_exceptions=False) as c:
        sid=create(c);url='/api/v1/sessions/'+sid;pages=[]
        for mode,rotation in [('color',0),('gray',90),('bw',270)]:
            p=upload(c,sid,'corners_rgb.png').json();pageurl=url+'/pages/'+p['id']
            assert c.put(pageurl+'/config',json={'expected_revision':0,'config':{'mode':mode,'rotation':rotation,
                'confirmed':True,'corners':[[0,0],[1,0],[1,1],[0,1]],'threshold':{'method':'otsu'}}}).status_code==200
            assert c.post(pageurl+'/render',json={'expected_revision':1,'debug':True}).status_code==200
            pages.append(p)
        ordered=[pages[i] for i in [2,0,1]]
        assert c.put(url+'/page-order',json={'page_ids':[p['id'] for p in ordered]}).status_code==200
        request=body(ordered if format=='pdf' else ordered[:1],format)
        r=c.post(url+'/exports',json=request);assert r.status_code==201,r.text
        receipt=r.json();artifact_url='/api/v1/artifacts/'+receipt['artifact_id']
        payload=c.get(artifact_url).content;digest=sha256(payload).hexdigest()
        old=c.get(url).json();changed=old['pages'][0];config=changed['effective_config'];config['rotation']=180
        assert c.put(url+'/pages/'+changed['id']+'/config',json={'expected_revision':1,'config':config}).status_code==200
        assert c.post(url+'/exports',json=request).json()['error']['code']=='REVISION_CONFLICT'
        fresh=c.get(url).json()
        fulls={p['latest_render']['render_artifact_id']:sha256(c.get('/api/v1/artifacts/'+p['latest_render']['render_artifact_id']).content).hexdigest() for p in fresh['pages']}
    # The first app lifespan and its executor/Engine have closed before reopening.
    with TestClient(create_app(database),raise_server_exceptions=False) as reopened:
        assert reopened.get(url).json()==fresh
        assert sha256(reopened.get(artifact_url).content).hexdigest()==digest
        for aid,expected in fulls.items():
            assert sha256(reopened.get('/api/v1/artifacts/'+aid).content).hexdigest()==expected
        with repository.transaction(reopened.app.state.engine) as db:
            record=db.get(ExportRecord,UUID(receipt['id']))
            assert record.page_snapshot_json==request['pages'] and str(record.artifact_id)==receipt['artifact_id']
        pageurl=url+'/pages/'+changed['id']
        assert reopened.post(pageurl+'/render',json={'expected_revision':2}).status_code==200
        request['pages'][0]['revision']=2
        assert reopened.post(url+'/exports',json=request).status_code==201
        assert sha256(reopened.get(artifact_url).content).hexdigest()==digest
