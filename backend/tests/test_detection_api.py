"""Actual detector runs, immutable page state, and source-bound debug publication."""
from io import BytesIO
from hashlib import sha256
from uuid import UUID, uuid4

import numpy as np
from PIL import Image
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.main import create_app
from app.storage import repository
from app.storage.models import DetectionRun


@pytest.fixture
def setup(tmp_path):
    with TestClient(create_app(tmp_path/'data/scanner.sqlite3'),raise_server_exceptions=False) as client:
        sid=client.post('/api/v1/sessions',json={'title':'Detect test'}).json()['id']
        image=np.full((240,320,3),25,np.uint8);image[25:216,30:291]=240
        stream=BytesIO();Image.fromarray(image).save(stream,format='PNG')
        page=client.post(f'/api/v1/sessions/{sid}/pages',files={'file':('page.png',stream.getvalue())}).json()
        yield client,sid,page,f"/api/v1/sessions/{sid}/pages/{page['id']}",tmp_path


def test_two_runs_keep_config_and_own_actual_stages(setup):
    client,sid,page,base,_=setup
    config=page['effective_config']|{'corners':[[0,0],[1,0],[1,1],[0,1]],'confirmed':True}
    assert client.put(base+'/config',json={'expected_revision':0,'config':config}).status_code==200
    before=client.get('/api/v1/sessions/'+sid).json()
    runs=[client.post(base+'/detect',json={'debug':True}) for _ in range(2)]
    assert all(r.status_code==200 for r in runs),[r.text for r in runs]
    first,second=[r.json() for r in runs]
    assert first['run_id']!=second['run_id'] and first['status']=='proposed'
    assert first['confirmed'] is False and first['source_revision']==1
    assert first['source_artifact_id']==page['normalized_artifact_id']
    assert first['source_sha256']==sha256(client.get('/api/v1/artifacts/'+page['normalized_artifact_id']).content).hexdigest()
    assert first['selected_trial_id'] and first['stage_artifacts']
    assert set(first['stage_artifacts'].values()).isdisjoint(second['stage_artifacts'].values())
    with repository.transaction(client.app.state.engine) as db:
        records=list(db.scalars(select(DetectionRun).order_by(DetectionRun.created_at)))
        assert len(records)==2
        for record,response in zip(records,[first,second]):
            metadata=record.metadata_json
            assert metadata['run_id']==str(record.id)==response['run_id']
            assert metadata['source']['sha256']==response['source_sha256']
            assert metadata['timings_ms']==response['timings_ms']
            assert metadata['selected_trial_id']==response['selected_trial_id']
            assert response['selected_trial_id'] in [t['trial_id'] for t in metadata['trials']]
            for stage in metadata['artifacts'].values():
                body=client.get('/api/v1/artifacts/'+stage['id'])
                assert body.status_code==200 and sha256(body.content).hexdigest()==stage['sha256']
    before['pages'][0]['latest_detection']=second
    assert client.get('/api/v1/sessions/'+sid).json()==before


def test_manual_required_is_200_and_debug_false_still_records_provenance(setup):
    client,sid,_,_,_=setup
    stream=BytesIO();Image.new('RGB',(80,60),'white').save(stream,format='PNG')
    page=client.post(f'/api/v1/sessions/{sid}/pages',files={'file':('blank.png',stream.getvalue())}).json()
    result=client.post(f"/api/v1/sessions/{sid}/pages/{page['id']}/detect",json={})
    assert result.status_code==200,result.text
    body=result.json();assert body['status']=='manual_required' and body['corners'] is None
    assert not body['confirmed'] and body['warnings']==['NO_VALID_QUAD'] and body['stage_artifacts']=={}
    with repository.transaction(client.app.state.engine) as db:
        row=db.get(DetectionRun,UUID(body['run_id']))
        assert row.source_artifact_id==UUID(page['normalized_artifact_id'])
        assert len(row.metadata_json['trials'])==4


@pytest.mark.parametrize('body',[{'debug':1},{'debug':None},{'preset':'baseline'},[]])
def test_bad_request_and_foreign_page(setup,body):
    client,sid,page,base,_=setup
    assert client.post(base+'/detect',json=body).status_code==400
    other=client.post('/api/v1/sessions',json={}).json()['id']
    assert client.post(f"/api/v1/sessions/{other}/pages/{page['id']}/detect",json={}).status_code==404
    assert client.post(f'/api/v1/sessions/{sid}/pages/{uuid4()}/detect',json={}).status_code==404


def test_processing_error_and_commit_fault_do_not_publish_or_mutate(setup,monkeypatch):
    from app.services import detection
    from sqlalchemy import event
    client,sid,_,base,tmp=setup
    before=client.get('/api/v1/sessions/'+sid).json()
    files={p:p.read_bytes() for p in (tmp/'data/sessions').rglob('*.png')}
    original=detection.detect_document
    def fail(*args,**kwargs):raise RuntimeError('private C:/secret.png')
    monkeypatch.setattr(detection,'detect_document',fail)
    response=client.post(base+'/detect',json={'debug':True})
    assert response.status_code==500 and response.json()['error']['code']=='PROCESSING_FAILED'
    assert 'secret' not in response.text
    monkeypatch.setattr(detection,'detect_document',original)
    inserted=[]
    def observe_insert(connection,cursor,statement,parameters,context,executemany):
        if statement.startswith('INSERT INTO detection_runs'):
            inserted.append(True);connection.info['fail_detect_commit']=True
    def fail_commit(connection):
        if connection.info.pop('fail_detect_commit',False):raise RuntimeError('commit fault')
    event.listen(client.app.state.engine,'before_cursor_execute',observe_insert)
    event.listen(client.app.state.engine,'commit',fail_commit)
    try:assert client.post(base+'/detect',json={'debug':True}).status_code==500
    finally:
        event.remove(client.app.state.engine,'commit',fail_commit)
        event.remove(client.app.state.engine,'before_cursor_execute',observe_insert)
    assert inserted  # fault occurred after stage publication/run INSERT, not the initial read transaction
    assert {p:p.read_bytes() for p in (tmp/'data/sessions').rglob('*.png')}==files
    assert client.get('/api/v1/sessions/'+sid).json()==before
    with repository.transaction(client.app.state.engine) as db:assert list(db.scalars(select(DetectionRun)))==[]


def test_second_stage_write_fault_cleans_first_stage(setup,monkeypatch):
    from app.storage.files import ArtifactStore,ArtifactFileError
    client,sid,_,base,tmp=setup
    before=client.get('/api/v1/sessions/'+sid).json()
    paths={p:p.read_bytes() for p in (tmp/'data/sessions').rglob('*') if p.is_file()}
    actual=ArtifactStore.write_bytes;calls=[]
    def broken(self,**kwargs):
        calls.append(kwargs['kind'])
        if len(calls)==2:raise ArtifactFileError('private disk fault')
        return actual(self,**kwargs)
    monkeypatch.setattr(ArtifactStore,'write_bytes',broken)
    response=client.post(base+'/detect',json={'debug':True})
    assert response.status_code==500 and response.json()['error']['code']=='STORAGE_FAILED'
    assert calls==['debug','debug']
    assert {p:p.read_bytes() for p in (tmp/'data/sessions').rglob('*') if p.is_file()}==paths
    assert client.get('/api/v1/sessions/'+sid).json()==before


def test_config_edit_during_detection_is_preserved_and_runs_can_survive_restart(setup,monkeypatch):
    from app.services import detection
    from app.storage.models import PageConfigRecord
    client,sid,page,base,tmp=setup
    actual=detection.detect_document
    def edit_config(pixels,**kwargs):
        with repository.transaction(client.app.state.engine) as db:
            row=db.get(PageConfigRecord,UUID(page['id']))
            row.config_json=row.config_json|{'rotation':90}
            row.revision=1
        return actual(pixels,**kwargs)
    monkeypatch.setattr(detection,'detect_document',edit_config)
    response=client.post(base+'/detect',json={'debug':True})
    assert response.status_code==200,response.text
    assert response.json()['source_revision']==0
    current=client.get('/api/v1/sessions/'+sid).json()['pages'][0]
    assert current['revision']==1 and current['effective_config']['rotation']==90
    with TestClient(create_app(tmp/'data/scanner.sqlite3')) as reopened:
        with repository.transaction(reopened.app.state.engine) as db:
            run=db.get(DetectionRun,UUID(response.json()['run_id']))
            assert run.source_sha256==response.json()['source_sha256']
            assert run.metadata_json['trials']
        aid=next(iter(response.json()['stage_artifacts'].values()))
        assert reopened.get('/api/v1/artifacts/'+aid).status_code==200


def test_deleted_page_during_cpu_never_publishes(setup,monkeypatch):
    from app.services import detection
    from app.storage.models import ScanPage
    from sqlalchemy import delete
    client,_,page,base,tmp=setup
    paths={p for p in (tmp/'data/sessions').rglob('*') if p.is_file()}
    actual=detection.detect_document
    def remove(pixels,**kwargs):
        with repository.transaction(client.app.state.engine) as db:db.execute(delete(ScanPage).where(ScanPage.id==UUID(page['id'])))
        return actual(pixels,**kwargs)
    monkeypatch.setattr(detection,'detect_document',remove)
    assert client.post(base+'/detect',json={'debug':True}).status_code==404
    assert {p for p in (tmp/'data/sessions').rglob('*') if p.is_file()}==paths
    with repository.transaction(client.app.state.engine) as db:assert list(db.scalars(select(DetectionRun)))==[]


def test_shared_executor_overload_and_health_during_detection(setup,monkeypatch):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Event
    from app.services import detection
    from app.services.processing_executor import ProcessingBusyError
    client,_,_,base,_=setup
    entered=Event();release=Event();actual=detection.detect_document
    def block(*args,**kwargs):
        entered.set();assert release.wait(8);return actual(*args,**kwargs)
    monkeypatch.setattr(detection,'detect_document',block)
    with ThreadPoolExecutor(max_workers=1) as pool:
        future=pool.submit(client.post,base+'/detect',json={})
        try:
            assert entered.wait(5)
            assert client.get('/api/v1/health').status_code==200
            # Saturate the same executor's two waiting slots while the real run is active.
            async def saturate():
                processing=client.app.state.processing
                a=processing.submit(lambda:None);b=processing.submit(lambda:None)
                return a,b
            queued=client.portal.call(saturate)
            assert client.post(base+'/detect',json={}).status_code==429
            for item in queued:client.portal.call(item.cancel)
        finally:release.set()
        assert future.result(timeout=8).status_code==200
