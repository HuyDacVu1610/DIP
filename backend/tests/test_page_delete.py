from hashlib import sha256
from uuid import UUID,uuid4
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select,func,event
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
from app.main import create_app
from app.storage.models import Artifact,RenderRun,DetectionRun
from app.storage.repository import transaction
from test_import_api import create,upload

def files(store):return {str(p):sha256(p.read_bytes()).hexdigest() for p in (store.root/'sessions').rglob('*') if p.is_file()}

@pytest.fixture
def document(tmp_path):
 with TestClient(create_app(tmp_path/'data/scanner.sqlite3'),raise_server_exceptions=False) as c:
  sid=create(c);pages=[upload(c,sid,'corners_rgb.png').json() for _ in range(3)]
  other=create(c);foreign=upload(c,other,'minimum.png').json()
  path=f"/api/v1/sessions/{sid}/pages/{pages[0]['id']}"
  saved=c.put(path+'/config',json={'expected_revision':0,'config':{'corners':[[0,0],[1,0],[1,1],[0,1]],'confirmed':True}}).json()
  assert c.post(path+'/render',json={'expected_revision':saved['revision'],'debug':True}).status_code==200
  assert c.post(path+'/detect',json={'debug':True}).status_code==200
  yield c,sid,pages,other,foreign

def test_page_delete_cascades_exact_owner_compacts_and_keeps_other_sources(document):
 c,sid,pages,other,foreign=document;url='/api/v1/sessions/'+sid
 before=c.get(url).json();other_before=c.get('/api/v1/sessions/'+other).json();store=c.app.state.artifacts
 with transaction(c.app.state.engine) as db:
  doomed=list(db.scalars(select(Artifact).where(Artifact.page_id==UUID(pages[0]['id']))))
  doomed_ids=[str(a.id) for a in doomed]
  doomed_paths={str(store.root/a.path) for a in doomed}
 hashes=files(store)
 r=c.delete(url+'/pages/'+pages[0]['id']);assert r.status_code==204 and r.content==b''
 after=c.get(url).json();assert [p['id'] for p in after['pages']]==[p['id'] for p in pages[1:]]
 assert [p['position'] for p in after['pages']]==[0,1]
 for index,p in enumerate(after['pages']):assert p==before['pages'][index+1]|{'position':index}
 assert c.get('/api/v1/sessions/'+other).json()==other_before
 assert files(store)=={p:h for p,h in hashes.items() if p not in doomed_paths}
 for aid in doomed_ids:assert c.get('/api/v1/artifacts/'+aid).status_code==404
 with transaction(c.app.state.engine) as db:
  assert db.scalar(select(func.count()).select_from(RenderRun))==0
  assert db.scalar(select(func.count()).select_from(DetectionRun))==0
  assert db.connection().exec_driver_sql('PRAGMA foreign_key_check').all()==[]
 assert c.delete(url+'/pages/'+pages[0]['id']).status_code==404

@pytest.mark.parametrize('target',['foreign','unknown','bad'])
def test_page_delete_refuses_wrong_owner_and_unknown_without_file_changes(document,target):
 c,sid,_,_,foreign=document;pid={'foreign':foreign['id'],'unknown':str(uuid4()),'bad':'not-uuid'}[target]
 before=files(c.app.state.artifacts)
 r=c.delete(f'/api/v1/sessions/{sid}/pages/{pid}')
 assert r.status_code==404 and r.json()['error']['code']=='PAGE_NOT_FOUND' and files(c.app.state.artifacts)==before

def test_delete_commit_rollback_keeps_every_file_and_metadata(document):
 c,sid,pages,_,_=document;url='/api/v1/sessions/'+sid;before=c.get(url).json();hashes=files(c.app.state.artifacts)
 def fail(db):raise OperationalError('private path',{},Exception('secret'))
 event.listen(Session,'before_commit',fail)
 try:r=c.delete(url+'/pages/'+pages[0]['id'])
 finally:event.remove(Session,'before_commit',fail)
 assert r.status_code==500 and 'secret' not in r.text
 assert c.get(url).json()==before and files(c.app.state.artifacts)==hashes

def test_cleanup_failure_does_not_restore_deleted_metadata_or_touch_other_files(document,monkeypatch,caplog):
 c,sid,pages,_,_=document;hashes=files(c.app.state.artifacts)
 def fail(stored):raise OSError('controlled cleanup failure')
 monkeypatch.setattr(c.app.state.artifacts,'_discard',fail)
 assert c.delete(f"/api/v1/sessions/{sid}/pages/{pages[0]['id']}").status_code==204
 assert len(c.get('/api/v1/sessions/'+sid).json()['pages'])==2
 assert files(c.app.state.artifacts)==hashes
 assert 'clean' in caplog.text.lower()

def test_cleanup_never_unlinks_a_still_referenced_artifact(document):
 from dataclasses import fields
 from app.services.deletions import _cleanup
 from app.storage.files import StoredArtifact
 c,_,_,_,foreign=document;before=files(c.app.state.artifacts)
 with transaction(c.app.state.engine) as db:
  row=db.get(Artifact,UUID(foreign['normalized_artifact_id']))
  record=StoredArtifact(**{f.name:getattr(row,f.name) for f in fields(StoredArtifact)})
 _cleanup(c.app.state.engine,c.app.state.artifacts,[record])
 assert files(c.app.state.artifacts)==before
