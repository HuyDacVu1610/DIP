from hashlib import sha256
from uuid import UUID,uuid4
import pytest
from sqlalchemy import event
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
from app.storage.repository import transaction
from test_page_delete import document,files

def test_session_delete_removes_exact_files_and_its_pages_runs_only(document):
 c,sid,_,other,_=document;url='/api/v1/sessions/'+sid;store=c.app.state.artifacts
 before=files(store);other_before=c.get('/api/v1/sessions/'+other).json()
 expected={p:h for p,h in before.items() if '/'+sid+'/' not in p.replace('\\','/')}
 r=c.delete(url);assert r.status_code==204 and r.content==b''
 assert c.get(url).status_code==404 and c.delete(url).status_code==404
 assert c.get('/api/v1/sessions/'+other).json()==other_before and files(store)==expected
 with transaction(c.app.state.engine) as db:assert db.connection().exec_driver_sql('PRAGMA foreign_key_check').all()==[]
 empty=c.post('/api/v1/sessions',json={}).json()['id']
 assert c.delete('/api/v1/sessions/'+empty).status_code==204

def test_session_delete_commit_failure_keeps_data_and_files(document):
 c,sid,_,_,_=document;url='/api/v1/sessions/'+sid;before=c.get(url).json();hashes=files(c.app.state.artifacts)
 def fail(db):raise OperationalError('private',{},Exception('secret'))
 event.listen(Session,'before_commit',fail)
 try:r=c.delete(url)
 finally:event.remove(Session,'before_commit',fail)
 assert r.status_code==500 and 'secret' not in r.text
 assert c.get(url).json()==before and files(c.app.state.artifacts)==hashes

@pytest.mark.parametrize('sid',['invalid',str(uuid4())])
def test_session_delete_unknown_uniform404(document,sid):
 c,_,_,_,_=document;before=files(c.app.state.artifacts)
 assert c.delete('/api/v1/sessions/'+sid).status_code==404 and files(c.app.state.artifacts)==before
