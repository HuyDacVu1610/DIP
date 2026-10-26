from pathlib import Path
from copy import deepcopy
from uuid import UUID
import pytest
from fastapi.testclient import TestClient
from app.main import create_app
from app.storage.models import RenderRun
from app.storage.repository import transaction
from test_import_api import create,upload

@pytest.fixture
def saved_document(tmp_path):
 database=tmp_path/'data/scanner.sqlite3'
 with TestClient(create_app(database),raise_server_exceptions=False) as c:
  sid=create(c);pages=[];renders=[]
  for mode,rotation in [('color',0),('gray',90),('bw',270)]:
   page=upload(c,sid,'corners_rgb.png').json();path=f"/api/v1/sessions/{sid}/pages/{page['id']}"
   saved=c.put(path+'/config',json={'expected_revision':0,'config':{'mode':mode,'rotation':rotation,
    'corners':[[0,0],[1,0],[1,1],[0,1]],'confirmed':True,'threshold':{'method':'otsu'}}}).json()
   render=c.post(path+'/render',json={'expected_revision':saved['revision'],'debug':True}).json()
   pages.append(page);renders.append(render)
  detected=c.post(f"/api/v1/sessions/{sid}/pages/{pages[0]['id']}/detect",json={'debug':True}).json()
  yield c,database,sid,pages,renders,detected

def test_reopen_returns_exact_saved_runs_without_processing_and_after_restart(saved_document,monkeypatch):
 c,database,sid,pages,renders,detected=saved_document
 def forbidden(*args,**kwargs):pytest.fail('GET must not process images')
 monkeypatch.setattr('app.services.renders.render_document',forbidden)
 monkeypatch.setattr('app.services.detection.detect_document',forbidden)
 url='/api/v1/sessions/'+sid;before=c.get(url)
 assert before.status_code==200,before.text
 for p,r in zip(before.json()['pages'],renders):assert p.get('latest_render')==r
 assert before.json()['pages'][0].get('latest_detection')==detected
 ids=[pages[2]['id'],pages[0]['id'],pages[1]['id']]
 assert c.put(url+'/page-order',json={'page_ids':ids}).status_code==200
 after=c.get(url).json()
 with TestClient(create_app(database)) as reopened:
  assert reopened.get(url).json()==after
  for p in after['pages']:
   r=p['latest_render'];assert reopened.get('/api/v1/artifacts/'+r['render_artifact_id']).status_code==200
   debug=reopened.get(f"{url}/pages/{p['id']}/debug?render_run_id={r['render_run_id']}").json()
   assert debug['run_id']==r['render_run_id'] and debug['status']=='available'

def test_new_draft_retains_previous_render_as_old_revision_without_auto_confirmation(saved_document):
 c,_,sid,pages,renders,_=saved_document;path=f"/api/v1/sessions/{sid}/pages/{pages[0]['id']}"
 config=c.get('/api/v1/sessions/'+sid).json()['pages'][0]['effective_config'];config['confirmed']=False;config['mode']='gray'
 assert c.put(path+'/config',json={'expected_revision':1,'config':config}).status_code==200
 page=c.get('/api/v1/sessions/'+sid).json()['pages'][0]
 assert page.get('latest_render')==renders[0] and page['revision']==2 and not page['effective_config']['confirmed']

def test_same_revision_newest_render_including_debugoff_is_opened(saved_document):
 c,_,sid,pages,_,_=saved_document;path=f"/api/v1/sessions/{sid}/pages/{pages[0]['id']}"
 newest=c.post(path+'/render',json={'expected_revision':1,'debug':False}).json()
 assert c.get('/api/v1/sessions/'+sid).json()['pages'][0].get('latest_render')==newest

def test_wrong_source_snapshot_fails_instead_of_cross_run_fallback(saved_document):
 c,_,sid,_,renders,_=saved_document
 with transaction(c.app.state.engine) as db:
  run=db.get(RenderRun,UUID(renders[0]['render_run_id']));metadata=deepcopy(run.metadata_json);metadata['source']['sha256']='b'*64;run.metadata_json=metadata
 r=c.get('/api/v1/sessions/'+sid)
 assert r.status_code==500 and r.json()['error']['code']=='STORAGE_FAILED'
