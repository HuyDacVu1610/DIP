from sqlalchemy import select
import pytest

from app.storage.database import initialize_database,open_database,SchemaVersionError
from app.storage.models import Base,DetectionRun,SchemaVersion
from app.storage import repository


def test_version1_adds_only_run_table_and_keeps_existing_rows(tmp_path):
    engine=open_database(tmp_path/'old.sqlite3')
    try:
        with engine.begin() as conn:
            Base.metadata.create_all(conn,tables=[t for t in Base.metadata.tables.values() if t.name not in ('detection_runs','render_runs')])
            conn.execute(SchemaVersion.__table__.insert().values(id=1,version=1))
        with repository.transaction(engine) as db:sid=repository.create_session(db,'Giữ tài liệu').id
        initialize_database(engine);initialize_database(engine)
        with repository.transaction(engine) as db:
            assert repository.get_session(db,sid).title=='Giữ tài liệu'
            assert db.get(SchemaVersion,1).version==3
            assert list(db.scalars(select(DetectionRun)))==[]
    finally:engine.dispose()


def test_failed_migration_rolls_back_ddl_and_version(tmp_path):
    from sqlalchemy import event,inspect
    engine=open_database(tmp_path/'rollback.sqlite3')
    try:
        with engine.begin() as conn:
            Base.metadata.create_all(conn,tables=[t for t in Base.metadata.tables.values() if t.name not in ('detection_runs','render_runs')])
            conn.execute(SchemaVersion.__table__.insert().values(id=1,version=1))
        def fail(conn,cursor,statement,parameters,context,executemany):
            if statement.startswith('UPDATE schema_version'):raise RuntimeError('migration fault')
        event.listen(engine,'before_cursor_execute',fail)
        try:
            with pytest.raises(RuntimeError,match='migration fault'):initialize_database(engine)
        finally:event.remove(engine,'before_cursor_execute',fail)
        assert 'detection_runs' not in inspect(engine).get_table_names()
        assert 'render_runs' not in inspect(engine).get_table_names()
        with engine.connect() as conn:assert conn.exec_driver_sql('SELECT version FROM schema_version').scalar_one()==1
        initialize_database(engine)
    finally:engine.dispose()


@pytest.mark.parametrize('fail_update',[False,True])
def test_version2_render_run_migration_atomic_and_idempotent(tmp_path,fail_update):
    from sqlalchemy import event,inspect
    engine=open_database(tmp_path/'v2.sqlite3')
    try:
        with engine.begin() as conn:
            Base.metadata.create_all(conn,tables=[t for t in Base.metadata.tables.values() if t.name!='render_runs'])
            conn.execute(SchemaVersion.__table__.insert().values(id=1,version=2))
        with repository.transaction(engine) as db:sid=repository.create_session(db,'Keep v2').id
        def fail(conn,cursor,statement,parameters,context,executemany):
            if statement.startswith('UPDATE schema_version'):raise RuntimeError('v2 fault')
        if fail_update:
            event.listen(engine,'before_cursor_execute',fail)
            try:
                with pytest.raises(RuntimeError,match='v2 fault'):initialize_database(engine)
            finally:event.remove(engine,'before_cursor_execute',fail)
            assert 'render_runs' not in inspect(engine).get_table_names()
            with engine.connect() as conn:assert conn.exec_driver_sql('SELECT version FROM schema_version').scalar_one()==2
        initialize_database(engine);initialize_database(engine)
        with repository.transaction(engine) as db:
            assert db.get(SchemaVersion,1).version==3
            assert repository.get_session(db,sid).title=='Keep v2'
    finally:engine.dispose()
