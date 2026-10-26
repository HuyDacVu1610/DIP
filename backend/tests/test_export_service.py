from copy import deepcopy
from uuid import UUID
import pytest
from sqlalchemy import select,event
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
from app.services.exports import export_snapshot,publish_export
from app.schemas.exports import ExportRequest
from app.storage import repository
from app.storage.models import Artifact,ExportRecord
from app.services.sessions import get_document
from test_export_snapshot import saved
from test_render_service import setup,files


@pytest.mark.parametrize('format',['pdf','png','jpg'])
def test_export_commits_completed_file_and_exact_ordered_snapshot_without_editing_pages(saved,format):
    engine,store,sid,_,_,request=saved
    if format!='pdf':request=ExportRequest(format=format,pages=request.pages[:1])
    before=get_document(engine,sid)
    with export_snapshot(engine,store,sid,request) as snapshot:result=publish_export(engine,store,snapshot)
    with repository.transaction(engine) as db:
        record=db.get(ExportRecord,result.id);artifact=db.get(Artifact,result.artifact_id)
        assert record.page_snapshot_json==request.model_dump(mode='json')['pages']
        assert record.session_id==sid and record.artifact_id==artifact.id
        assert artifact.kind==('pdf' if format=='pdf' else 'export_image')
        assert artifact.page_id is None and artifact.revision is None
        assert result.pages==request.pages and result.format==format
        payload=(store.root/artifact.path).read_bytes()
    assert payload.startswith(b'%PDF-' if format=='pdf' else b'\x89PNG' if format=='png' else b'\xff\xd8')
    assert get_document(engine,sid)==before


@pytest.mark.parametrize('failure',['encode','write','register','commit'])
def test_export_failure_preserves_existing_files_metadata_and_unlocks(saved,monkeypatch,failure):
    from app.services import exports
    engine,store,sid,_,_,request=saved
    with export_snapshot(engine,store,sid,request) as snapshot:publish_export(engine,store,snapshot)
    before=files(store)
    with repository.transaction(engine) as db:old_ids=set(db.scalars(select(ExportRecord.id)))
    def fail(*args,**kwargs):raise RuntimeError('controlled export failure')
    commit_hook=None
    if failure=='encode':monkeypatch.setattr(exports,'append_pdf_page',fail)
    elif failure=='write':monkeypatch.setattr(store,'write_bytes',fail)
    elif failure=='register':monkeypatch.setattr(repository,'register_artifact',fail)
    else:
        def commit_hook(db):raise OperationalError('private sql',{},Exception('secret'))
        event.listen(Session,'before_commit',commit_hook)
    try:
        with pytest.raises(Exception):
            with export_snapshot(engine,store,sid,request) as snapshot:publish_export(engine,store,snapshot)
    finally:
        if commit_hook:event.remove(Session,'before_commit',commit_hook)
    assert files(store)==before
    with repository.transaction(engine) as db:assert set(db.scalars(select(ExportRecord.id)))==old_ids
    from app.services.session_guards import reserve_export
    reserve_export(engine,sid).release()
