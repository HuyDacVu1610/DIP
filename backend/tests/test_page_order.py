from uuid import uuid4
import pytest
from fastapi.testclient import TestClient
from app.main import create_app
from test_sessions_api import seed
from app.storage.repository import transaction

@pytest.fixture
def ordered(tmp_path):
    with TestClient(create_app(tmp_path/'data/scanner.sqlite3'),raise_server_exceptions=False) as client:
        sid=client.post('/api/v1/sessions',json={}).json()['id']
        other=client.post('/api/v1/sessions',json={}).json()['id']
        with transaction(client.app.state.engine) as db:
            ids=[seed(db,sid,i) for i in range(3)];foreign=seed(db,other,0)
        yield client,sid,ids,foreign

def test_permutation_preserves_page_config_and_revision_and_noop(ordered):
    c,sid,ids,_=ordered;url='/api/v1/sessions/'+sid
    before=c.get(url).json();expected=[ids[2],ids[0],ids[1]]
    response=c.put(url+'/page-order',json={'page_ids':expected})
    assert response.status_code==200,response.text
    after=response.json();assert [p['id'] for p in after['pages']]==expected
    assert [p['position'] for p in after['pages']]==[0,1,2]
    original={p['id']:p for p in before['pages']}
    for p in after['pages']:assert p==original[p['id']]|{'position':p['position']}
    assert after['updated_at']>before['updated_at']
    assert c.get(url).json()==after
    assert c.put(url+'/page-order',json={'page_ids':expected}).json()==after

@pytest.mark.parametrize('kind',['missing','duplicate','foreign','unknown','extra'])
def test_invalid_order_is_atomic(ordered,kind):
    c,sid,ids,foreign=ordered;url='/api/v1/sessions/'+sid;before=c.get(url).json()
    values={'missing':ids[:2],'duplicate':[ids[0],ids[0],ids[1]],'foreign':[ids[0],ids[1],foreign],
        'unknown':[ids[0],ids[1],str(uuid4())],'extra':ids+[str(uuid4())]}
    response=c.put(url+'/page-order',json={'page_ids':values[kind]})
    assert response.status_code==400,response.text
    assert c.get(url).json()==before

def test_order_commit_failure_rolls_back_both_position_passes(ordered):
    from sqlalchemy import event
    from sqlalchemy.orm import Session
    from sqlalchemy.exc import OperationalError
    c,sid,ids,_=ordered;url='/api/v1/sessions/'+sid;before=c.get(url).json()
    def fail(db):raise OperationalError('private SQL',{},Exception('secret'))
    event.listen(Session,'before_commit',fail)
    try:r=c.put(url+'/page-order',json={'page_ids':ids[::-1]})
    finally:event.remove(Session,'before_commit',fail)
    assert r.status_code==500 and 'secret' not in r.text
    assert c.get(url).json()==before

def test_empty_and_unknown_session_order(ordered):
    c,_,_,_=ordered;sid=c.post('/api/v1/sessions',json={}).json()['id']
    assert c.put('/api/v1/sessions/'+sid+'/page-order',json={'page_ids':[]}).status_code==200
    assert c.put('/api/v1/sessions/'+str(uuid4())+'/page-order',json={'page_ids':[]}).status_code==404
