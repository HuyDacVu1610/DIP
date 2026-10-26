from concurrent.futures import ThreadPoolExecutor
from threading import Event
from pathlib import Path
from uuid import UUID
import pytest
from app.schemas.exports import ExportRequest
from app.schemas.sessions import SessionRename
from app.services.exports import export_snapshot,run_export,PageNotRenderedError
from app.services.session_guards import SessionBusyError
from app.services.sessions import get_document,rename_document
from app.services import renders,detection,imports
from app.storage.database import open_database,initialize_database
from test_reopen import saved_document
from test_export_snapshot import saved
from test_render_service import setup,descriptor,files


@pytest.mark.parametrize('operation',['rename','config','order','delete_page','delete_session','import','render','detect'])
def test_http_mutations_reject_exporting_owner_and_preserve_reads(saved_document,operation):
    c,_,sid,pages,_,_=saved_document;engine=c.app.state.engine;store=c.app.state.artifacts
    url='/api/v1/sessions/'+sid;pageurl=url+'/pages/'+pages[0]['id'];before=c.get(url).json();pixels=files(store)
    request=ExportRequest(pages=[{'page_id':p['id'],'revision':1} for p in pages])
    actions={
        'rename':lambda:c.patch(url,json={'title':'Must be blocked'}),
        'config':lambda:c.put(pageurl+'/config',json={'expected_revision':1,'config':{'mode':'gray'}}),
        'order':lambda:c.put(url+'/page-order',json={'page_ids':[p['id'] for p in reversed(pages)]}),
        'delete_page':lambda:c.delete(pageurl),
        'delete_session':lambda:c.delete(url),
        'import':lambda:c.post(url+'/pages',files={'file':('safe.png',(Path(__file__).resolve().parents[2]/'fixtures/corners_rgb.png').read_bytes(),'image/png')}),
        'render':lambda:c.post(pageurl+'/render',json={'expected_revision':1}),
        'detect':lambda:c.post(pageurl+'/detect',json={'debug':True}),
    }
    with export_snapshot(engine,store,UUID(sid),request):
        response=actions[operation]()
        assert response.status_code==409,response.text
        assert response.json()['error']['code']=='SESSION_BUSY'
        assert c.get(url).json()==before and files(store)==pixels
    assert c.patch(url,json={'title':'Unlocked'}).status_code==200


@pytest.mark.parametrize('operation',['render','detect','import'])
def test_async_http_rejects_busy_owner_before_joining_occupied_cpu_queue(saved_document,operation):
    c,_,sid,pages,_,_=saved_document;started,release=Event(),Event()
    request=ExportRequest(pages=[{'page_id':pages[0]['id'],'revision':1}])
    def writer(snapshot):
        started.set();release.wait(4)
        return snapshot.title
    url='/api/v1/sessions/'+sid+'/pages'
    with ThreadPoolExecutor(max_workers=1) as pool:
        active=pool.submit(c.portal.call,run_export,c.app.state.processing,c.app.state.engine,c.app.state.artifacts,UUID(sid),request,writer)
        try:
            assert started.wait(3)
            if operation=='import':response=c.post(url,files={'file':('test.png',(Path(__file__).resolve().parents[2]/'fixtures/corners_rgb.png').read_bytes(),'image/png')})
            else:response=c.post(url+'/'+pages[0]['id']+'/'+operation,json={'expected_revision':1} if operation=='render' else {'debug':False})
            assert response.status_code==409,response.text
            assert not release.is_set() and not active.done()
            assert c.get('/api/v1/health').status_code==200
        finally:release.set()
        assert active.result(timeout=4)


@pytest.mark.parametrize('operation',['render','detect','import'])
def test_work_started_before_export_cannot_publish_into_its_snapshot(saved,monkeypatch,operation):
    engine,store,sid,pages,_,request=saved;started,release=Event(),Event()
    source=descriptor(engine,sid,pages[0].original_artifact_id);payload=store.verify(source).read_bytes()
    module,name={'render':(renders,'render_document'),'detect':(detection,'detect_document'),'import':(imports,'normalize_image')}[operation]
    original=getattr(module,name)
    def hold(*args,**kwargs):
        started.set();assert release.wait(8);return original(*args,**kwargs)
    monkeypatch.setattr(module,name,hold)
    work={'render':lambda:renders.render_page(engine,store,sid,pages[0].id,1,True),
          'detect':lambda:detection.detect_page(engine,store,sid,pages[0].id,True),
          'import':lambda:imports.import_page(engine,store,sid,payload)}[operation]
    before=get_document(engine,sid);pixels=files(store)
    with ThreadPoolExecutor(max_workers=1) as pool:
        future=pool.submit(work)
        try:
            assert started.wait(5)
            with export_snapshot(engine,store,sid,request) as snapshot:
                release.set()
                with pytest.raises(SessionBusyError):future.result(timeout=8)
                for page in snapshot.pages:assert store.verify(page.full).exists()
        finally:release.set()
    assert get_document(engine,sid)==before and files(store)==pixels


def test_new_app_engine_does_not_restore_old_in_memory_export_lock(saved):
    engine,store,sid,_,_,request=saved
    other=open_database(Path(engine.url.database))
    try:
        initialize_database(other)
        with export_snapshot(engine,store,sid,request):
            # A new lifespan creates a new Engine. No busy marker was persisted.
            rename_document(other,sid,SessionRename(title='New app lifecycle'))
        with export_snapshot(other,store,sid,request) as snapshot:assert snapshot.title=='New app lifecycle'
    finally:other.dispose()


def test_missing_render_http_envelope_contains_ordered_page_revision_list(saved_document):
    c,_,_,pages,_,_=saved_document
    requested=ExportRequest(pages=[{'page_id':p['id'],'revision':1} for p in reversed(pages)])
    @c.app.post('/test-only/missing-render')
    def missing():raise PageNotRenderedError(requested.pages)
    response=c.post('/test-only/missing-render')
    assert response.status_code==409
    assert response.json()['error']=={'code':'PAGE_NOT_RENDERED','message':'Cần tạo bản quét đúng revision cho các trang đã chọn.',
        'details':{'pages':requested.model_dump(mode='json')['pages']}}
