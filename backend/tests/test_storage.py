"""SQLite durability/ownership constraints; no image-file publication yet."""
from datetime import UTC, datetime, timedelta, timezone
from uuid import uuid4

import pytest
from sqlalchemy import inspect, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.processing.config import get_preset
from app.storage.database import SchemaVersionError, initialize_database, open_database
from app.storage.models import Artifact, Base, ExportRecord, PageConfigRecord, ScanPage, ScanSession
from app.storage.repository import create_session, get_artifact, get_page, list_pages, transaction


@pytest.fixture
def engine(tmp_path):
    value = open_database(tmp_path/'metadata.sqlite3')
    initialize_database(value)
    yield value
    value.dispose()


def seed_page(db, sid, position=0):
    page_id = uuid4()
    ids = [uuid4() for _ in range(3)]
    page = ScanPage(id=page_id,session_id=sid,position=position,width=100,height=80,
        original_artifact_id=ids[0],normalized_artifact_id=ids[1],thumbnail_artifact_id=ids[2])
    db.add(page)
    for aid,kind in zip(ids,('original','normalized','thumbnail')):
        db.add(Artifact(id=aid,session_id=sid,page_id=page_id,kind=kind,
            path=f'sources/{aid}.png',mime='image/png',byte_size=20,sha256='a'*64,width=100,height=80))
    db.add(PageConfigRecord(page_id=page_id,session_id=sid,revision=0,
        config_json=get_preset().model_dump(mode='json')))
    db.flush()
    return page


def test_initialization_is_idempotent_foreign_keys_on_every_connection_and_reopens(tmp_path):
    path = tmp_path/'storage'/'metadata.sqlite3'
    first = open_database(path)
    initialize_database(first)
    initialize_database(first)
    with transaction(first) as db:
        sid = create_session(db,'Bài tập').id
        page = seed_page(db,sid)
        pid,aid = page.id,page.normalized_artifact_id
    first.dispose()
    reopened = open_database(path)
    initialize_database(reopened)
    with reopened.connect() as conn:
        assert conn.exec_driver_sql('PRAGMA foreign_keys').scalar_one()==1
        assert conn.exec_driver_sql('PRAGMA foreign_key_check').all()==[]
    with transaction(reopened) as db:
        assert get_page(db,sid,pid).width==100 and get_artifact(db,sid,aid).page_id==pid
        config = db.get(PageConfigRecord,pid)
        assert config.revision==0 and config.config_json==get_preset().model_dump(mode='json')
        assert db.get(ScanSession,sid).created_at.tzinfo is UTC
    reopened.dispose()


def test_page_order_and_repository_membership(engine):
    with transaction(engine) as db:
        sid = create_session(db,'One').id
        other = create_session(db,'Two').id
        second = seed_page(db,sid,1)
        first = seed_page(db,sid,0)
        assert [p.id for p in list_pages(db,sid)]==[first.id,second.id]
        assert get_page(db,other,first.id) is None
        assert get_artifact(db,other,first.normalized_artifact_id) is None


def test_partial_transaction_rolls_back_all_metadata(engine):
    sid = uuid4()
    with pytest.raises(RuntimeError):
        with transaction(engine) as db:
            db.add(ScanSession(id=sid,title='rollback'))
            db.flush()
            seed_page(db,sid)
            raise RuntimeError('controlled failure before commit')
    with transaction(engine) as db:
        assert db.get(ScanSession,sid) is None
        assert db.scalars(select(ScanPage)).all()==[]
        assert db.scalars(select(Artifact)).all()==[]


@pytest.mark.parametrize('kind',['artifact','config','source_reference','export'])
def test_cross_session_links_are_rejected_even_without_repository(engine,kind):
    with transaction(engine) as db:
        sid = create_session(db,'One').id
        other = create_session(db,'Two').id
        page = seed_page(db,sid)
        pid,aid = page.id,page.normalized_artifact_id
    with pytest.raises(IntegrityError):
        with transaction(engine) as db:
            if kind=='artifact':
                db.add(Artifact(session_id=other,page_id=pid,kind='render',revision=0,
                    path='renders/new.png',mime='image/png',byte_size=20,sha256='b'*64))
            elif kind=='config':
                db.execute(text('UPDATE page_configs SET session_id=:other WHERE page_id=:pid'),
                    {'other':other.hex,'pid':pid.hex})
            elif kind=='source_reference':
                new = seed_page(db,other)
                new.normalized_artifact_id = aid
            else:
                db.add(ExportRecord(session_id=other,artifact_id=aid,
                    page_snapshot_json=[{'page_id':str(pid),'revision':0}],format='pdf'))


def test_duplicate_position_missing_source_and_active_source_deletion_fail(engine):
    with transaction(engine) as db:
        sid = create_session(db,'One').id
        page = seed_page(db,sid)
        aid = page.normalized_artifact_id
    with pytest.raises(IntegrityError):
        with transaction(engine) as db:
            seed_page(db,sid,0)
    with pytest.raises(IntegrityError):
        with transaction(engine) as db:
            db.delete(db.get(Artifact,aid))
    with pytest.raises(IntegrityError):
        with transaction(engine) as db:
            db.add(ScanPage(session_id=sid,position=1,width=100,height=80,
                original_artifact_id=uuid4(),normalized_artifact_id=uuid4(),thumbnail_artifact_id=uuid4()))


def test_export_metadata_round_trip_and_session_cascade(engine):
    with transaction(engine) as db:
        sid = create_session(db,'One').id
        page = seed_page(db,sid)
        artifact = Artifact(session_id=sid,kind='pdf',path='exports/result.pdf',mime='application/pdf',
            byte_size=50,sha256='c'*64)
        db.add(artifact)
        db.flush()
        export = ExportRecord(session_id=sid,artifact_id=artifact.id,format='pdf',
            page_snapshot_json=[{'page_id':str(page.id),'revision':0}])
        db.add(export)
        db.flush()
        eid = export.id
    with transaction(engine) as db:
        assert db.get(ExportRecord,eid).page_snapshot_json[0]['revision']==0
        db.delete(db.get(ScanSession,sid))
    with transaction(engine) as db:
        assert db.scalars(select(Artifact)).all()==[]
        assert db.scalars(select(ScanPage)).all()==[]
        assert db.scalars(select(PageConfigRecord)).all()==[]
        assert db.scalars(select(ExportRecord)).all()==[]


def test_utc_timestamp_round_trip_rejects_naive_datetime(engine):
    with transaction(engine) as db:
        record = ScanSession(title='UTC',created_at=datetime(2026,10,17,16,tzinfo=timezone(timedelta(hours=7))))
        db.add(record)
        db.flush()
        sid = record.id
    with transaction(engine) as db:
        assert db.get(ScanSession,sid).created_at==datetime(2026,10,17,9,tzinfo=UTC)
    from sqlalchemy.exc import StatementError
    with pytest.raises(StatementError):
        with transaction(engine) as db:
            db.add(ScanSession(title='naive',created_at=datetime(2026,10,17)))


def test_unknown_version_is_refused_without_repairing_or_resetting_db(engine):
    with engine.begin() as conn:
        conn.exec_driver_sql('UPDATE schema_version SET version=99')
    tables = set(inspect(engine).get_table_names())
    with pytest.raises(SchemaVersionError):
        initialize_database(engine)
    with engine.connect() as conn:
        assert conn.exec_driver_sql('SELECT version FROM schema_version').scalar_one()==99
    assert set(inspect(engine).get_table_names())==tables


def test_same_session_source_cannot_reference_a_different_page(engine):
    with transaction(engine) as db:
        sid = create_session(db).id
        first,second = seed_page(db,sid,0),seed_page(db,sid,1)
        pid,aid = first.id,second.normalized_artifact_id
    with pytest.raises(IntegrityError):
        with transaction(engine) as db:
            db.get(ScanPage,pid).normalized_artifact_id = aid


@pytest.mark.parametrize('change',[{'path':'../private.png'},{'sha256':'bad'},
    {'revision':0},{'byte_size':-1}])
def test_invalid_artifact_metadata_is_rejected_by_sqlite(engine,change):
    with transaction(engine) as db:
        sid = create_session(db).id
        pid = seed_page(db,sid).id
    with pytest.raises(IntegrityError):
        with transaction(engine) as db:
            db.add(Artifact(**({'session_id':sid,'page_id':pid,'kind':'original',
                'path':'sources/extra.png','mime':'image/png','byte_size':20,'sha256':'a'*64}|change)))


def test_config_revision_cannot_be_negative(engine):
    with transaction(engine) as db:
        sid = create_session(db).id
        pid = seed_page(db,sid).id
    with pytest.raises(IntegrityError):
        with transaction(engine) as db:
            db.get(PageConfigRecord,pid).revision = -1


def test_initialization_ddl_rolls_back_on_failure(tmp_path,monkeypatch):
    engine = open_database(tmp_path/'atomic.sqlite3')
    original = Base.metadata.create_all
    def fail_after_ddl(connection):
        original(connection)
        raise RuntimeError('controlled failure after DDL')
    monkeypatch.setattr(Base.metadata,'create_all',fail_after_ddl)
    with pytest.raises(RuntimeError):
        initialize_database(engine)
    assert inspect(engine).get_table_names()==[]
    engine.dispose()


def test_nonempty_unknown_database_is_not_silently_adopted(tmp_path):
    engine = open_database(tmp_path/'unknown.sqlite3')
    with engine.begin() as conn:
        conn.exec_driver_sql('CREATE TABLE user_data(value TEXT)')
        conn.exec_driver_sql("INSERT INTO user_data VALUES ('keep')")
    with pytest.raises(SchemaVersionError):
        initialize_database(engine)
    with engine.connect() as conn:
        assert conn.exec_driver_sql('SELECT value FROM user_data').scalar_one()=='keep'
    assert inspect(engine).get_table_names()==['user_data']
    engine.dispose()
