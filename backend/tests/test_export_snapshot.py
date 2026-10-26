from dataclasses import FrozenInstanceError
from copy import deepcopy
from pathlib import Path
from uuid import uuid4
from threading import Event
import asyncio
import pytest
from app.schemas.exports import ExportRequest
from app.schemas.pages import ConfigUpdateRequest
from app.schemas.sessions import SessionCreate
from app.services.exports import export_snapshot, run_export, PageNotRenderedError
from app.services.session_guards import SessionBusyError
from app.services.sessions import create_document,get_document,SessionNotFoundError
from app.services.imports import import_page
from app.services.renders import render_page,PageNotConfirmedError
from app.services.page_config import update_page_config,RevisionConflictError,PageNotFoundError
from app.services.processing_executor import ProcessingExecutor,ProcessingBusyError
from app.storage.files import ArtifactFileError
from app.storage import repository
from app.storage.models import RenderRun
from sqlalchemy import delete
from test_render_service import setup,QUAD,files


@pytest.fixture
def saved(setup):
    engine,store,sid,page,payload=setup
    pages=[page,import_page(engine,store,sid,payload),import_page(engine,store,sid,payload)]
    renders=[]
    for p,mode,rotation in zip(pages,['color','gray','bw'],[0,90,270]):
        update_page_config(engine,sid,p.id,ConfigUpdateRequest(expected_revision=0,
            config={'mode':mode,'rotation':rotation,'corners':QUAD,'confirmed':True,'threshold':{'method':'otsu'}}))
        renders.append(render_page(engine,store,sid,p.id,1,True))
    request=ExportRequest(pages=[{'page_id':pages[i].id,'revision':1} for i in [2,0]])
    return engine,store,sid,pages,renders,request


def test_ordered_subset_holds_exact_full_descriptors_and_config_without_processing_or_db_writes(saved,monkeypatch):
    engine,store,sid,pages,renders,request=saved;before=get_document(engine,sid);pixels=files(store)
    def forbidden(*args,**kwargs):pytest.fail('Snapshot must not render/detect')
    monkeypatch.setattr('app.services.renders.render_document',forbidden)
    monkeypatch.setattr('app.services.detection.detect_document',forbidden)
    with export_snapshot(engine,store,sid,request) as snapshot:
        assert snapshot.session_id==sid and snapshot.title==before.title and snapshot.request==request
        assert [p.page_id for p in snapshot.pages]==[pages[2].id,pages[0].id]
        for p,index in zip(snapshot.pages,[2,0]):
            assert p.revision==1 and p.render_run_id==renders[index].render_run_id
            assert p.full.id==renders[index].render_artifact_id and p.full.kind=='render'
            assert p.full.id!=renders[index].preview_artifact_id
            assert store.verify(p.full).read_bytes()==pixels[str(Path(p.full.path))]
            assert p.config.confirmed
        with pytest.raises(FrozenInstanceError):snapshot.title='changed'
        with pytest.raises(SessionBusyError):
            with export_snapshot(engine,store,sid,request):pytest.fail('second export entered')
        assert get_document(engine,sid)==before
    assert get_document(engine,sid)==before and files(store)==pixels


def test_missing_render_reports_all_requested_pages_in_request_order_and_unlocks(setup):
    engine,store,sid,page,payload=setup;second=import_page(engine,store,sid,payload)
    for p in [page,second]:update_page_config(engine,sid,p.id,ConfigUpdateRequest(expected_revision=0,config={'corners':QUAD,'confirmed':True}))
    request=ExportRequest(pages=[{'page_id':p.id,'revision':1} for p in [second,page]])
    with pytest.raises(PageNotRenderedError) as error:
        with export_snapshot(engine,store,sid,request):pytest.fail('missing full entered')
    assert error.value.pages==request.pages
    render_page(engine,store,sid,page.id,1)


@pytest.mark.parametrize('case',['older_revision','legacy_without_run','wrong_source','corrupt_file','invalid_request_copy'])
def test_never_exports_stale_legacy_corrupt_or_unvalidated_render(saved,case):
    engine,store,sid,pages,renders,request=saved;expected=PageNotRenderedError
    if case=='older_revision':
        config=get_document(engine,sid).pages[2].effective_config.model_dump(mode='json');config['rotation']=180
        update_page_config(engine,sid,pages[2].id,ConfigUpdateRequest(expected_revision=1,config=config))
        request=ExportRequest(pages=[{'page_id':pages[2].id,'revision':2}])
    elif case=='legacy_without_run':
        with repository.transaction(engine) as db:db.execute(delete(RenderRun).where(RenderRun.id==renders[2].render_run_id))
    elif case=='wrong_source':
        from app.services.sessions import SessionDataError
        with repository.transaction(engine) as db:
            run=db.get(RenderRun,renders[2].render_run_id);meta=deepcopy(run.metadata_json);meta['source']['sha256']='b'*64;run.metadata_json=meta
        expected=SessionDataError
    elif case=='corrupt_file':
        with export_snapshot(engine,store,sid,request) as snapshot:path=store.path_for(snapshot.pages[0].full)
        path.write_bytes(b'controlled invalid PNG');expected=ArtifactFileError
    else:
        from pydantic import ValidationError
        request=request.model_copy(update={'margin_mm':float('nan')});expected=ValidationError
    with pytest.raises(expected):
        with export_snapshot(engine,store,sid,request):pytest.fail('invalid snapshot entered')
    from app.services.session_guards import reserve_export
    reserve_export(engine,sid).release()


@pytest.mark.parametrize('case',['unconfirmed','stale','foreign','unknown','session','file','writer'])
def test_snapshot_errors_do_not_keep_lock_or_change_saved_files(saved,case):
    engine,store,sid,pages,_,request=saved
    target=sid;expected=RuntimeError
    if case=='unconfirmed':
        p=pages[2];update_page_config(engine,sid,p.id,ConfigUpdateRequest(expected_revision=1,config={'mode':'bw','corners':QUAD,'confirmed':False}))
        request=ExportRequest(pages=[{'page_id':p.id,'revision':2}]);expected=PageNotConfirmedError
    elif case=='stale':request=ExportRequest(pages=[{'page_id':pages[2].id,'revision':0}]);expected=RevisionConflictError
    elif case in ('foreign','unknown'):
        other=create_document(engine,SessionCreate()).id
        pid=uuid4()
        if case=='foreign':
            pid=pages[0].id
            target=other
        request=ExportRequest(pages=[{'page_id':pid,'revision':1}]);expected=PageNotFoundError
    elif case=='session':target=uuid4();expected=SessionNotFoundError
    elif case=='file':
        with export_snapshot(engine,store,sid,request) as snapshot:path=store.path_for(snapshot.pages[0].full)
        path.unlink();expected=ArtifactFileError
    before=get_document(engine,sid);pixels=files(store)
    with pytest.raises(expected):
        with export_snapshot(engine,store,target,request):raise RuntimeError('controlled writer failure')
    # A new mutation proves all exception paths released the guard.
    from app.services.sessions import rename_document
    from app.schemas.sessions import SessionRename
    rename_document(engine,target if case=='foreign' else sid,SessionRename(title='Unlocked'))
    assert get_document(engine,sid).pages==before.pages and files(store)==pixels


def test_export_executor_releases_lease_on_success_failure_overload_and_cancel(saved):
    engine,store,sid,_,_,request=saved
    async def scenario():
        executor=ProcessingExecutor();started,release=Event(),Event()
        def hold():started.set();assert release.wait(5)
        try:
            assert await run_export(executor,engine,store,sid,request,lambda snap:len(snap.pages))==2
            def fail(snapshot):raise RuntimeError('controlled encoder failure')
            with pytest.raises(RuntimeError):await run_export(executor,engine,store,sid,request,fail)
            first=executor.submit(hold);assert await asyncio.to_thread(started.wait,3)
            second=executor.submit(lambda:None);third=executor.submit(lambda:None)
            with pytest.raises(ProcessingBusyError):await run_export(executor,engine,store,sid,request,lambda snap:None)
            second.cancel();third.cancel()
            called=[]
            waiting=asyncio.create_task(run_export(executor,engine,store,sid,request,lambda snap:called.append(snap)))
            await asyncio.sleep(0)
            with pytest.raises(SessionBusyError):await run_export(executor,engine,store,sid,request,lambda snap:None)
            waiting.cancel()
            with pytest.raises(asyncio.CancelledError):await waiting
            release.set();await first
            assert await run_export(executor,engine,store,sid,request,lambda snap:True)
            assert called==[]
        finally:release.set();await executor.aclose()
    asyncio.run(scenario())


def test_cancelling_active_export_keeps_files_and_lock_until_thread_finishes(saved):
    engine,store,sid,_,_,request=saved
    async def scenario():
        executor=ProcessingExecutor();started,release=Event(),Event();held=[]
        def writer(snapshot):
            held.extend(snapshot.pages);started.set();assert release.wait(5)
            for page in snapshot.pages:assert store.verify(page.full).exists()
        try:
            caller=asyncio.create_task(run_export(executor,engine,store,sid,request,writer))
            assert await asyncio.to_thread(started.wait,3)
            caller.cancel()
            with pytest.raises(asyncio.CancelledError):await caller
            with pytest.raises(SessionBusyError):
                with export_snapshot(engine,store,sid,request):pytest.fail('unlocked early')
            release.set();await executor.run(lambda:None)
            with export_snapshot(engine,store,sid,request) as snapshot:assert len(snapshot.pages)==2
        finally:release.set();await executor.aclose()
    asyncio.run(scenario())
