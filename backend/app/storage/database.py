"""Explicit SQLite setup; importing this module never creates runtime data."""
from pathlib import Path

from sqlalchemy import URL, create_engine, event, inspect, select
from sqlalchemy.engine import Engine

from ..settings import DATABASE_PATH
from .models import Base, DetectionRun, RenderRun, SchemaVersion

SCHEMA_VERSION = 3


class SchemaVersionError(RuntimeError):
    pass


def open_database(path: Path = DATABASE_PATH) -> Engine:
    """File-backed SQLite engine. Call initialize_database explicitly."""
    target = Path(path).resolve()
    target.parent.mkdir(parents=True,exist_ok=True)
    engine = create_engine(URL.create('sqlite+pysqlite',database=str(target)),
        connect_args={'check_same_thread':False,'timeout':5})

    @event.listens_for(engine,'connect')
    def configure_connection(connection, record):
        # Compatible with Python3.11/3.12: SQLAlchemy owns BEGIN, including DDL.
        # https://docs.sqlalchemy.org/en/21/dialects/sqlite.html
        connection.isolation_level = None
        cursor = connection.cursor()
        cursor.execute('PRAGMA foreign_keys=ON')
        cursor.close()

    @event.listens_for(engine,'begin')
    def explicit_begin(connection):
        connection.exec_driver_sql('BEGIN')

    return engine


def initialize_database(engine: Engine) -> None:
    """Initialize or explicitly expand v1/v2→v3 atomically; refuse unknown schemas."""
    with engine.begin() as connection:
        tables = set(inspect(connection).get_table_names())
        if not tables:
            Base.metadata.create_all(connection)
            connection.execute(SchemaVersion.__table__.insert().values(id=1,version=SCHEMA_VERSION))
            return
        expected = set(Base.metadata.tables)
        if 'schema_version' not in tables:
            raise SchemaVersionError('Schema SQLite không có version; không tự sửa dữ liệu.')
        rows = connection.execute(select(SchemaVersion.id,SchemaVersion.version)).all()
        if rows==[(1,1)] and tables==expected-{'detection_runs','render_runs'}:
            # Additive migration only: existing pages/config/artifacts remain untouched.
            DetectionRun.__table__.create(connection)
            RenderRun.__table__.create(connection)
            connection.execute(SchemaVersion.__table__.update().where(SchemaVersion.id==1).values(version=SCHEMA_VERSION))
            return
        if rows==[(1,2)] and tables==expected-{'render_runs'}:
            RenderRun.__table__.create(connection)
            connection.execute(SchemaVersion.__table__.update().where(SchemaVersion.id==1).values(version=SCHEMA_VERSION))
            return
        if tables!=expected:
            raise SchemaVersionError('Schema SQLite không khớp; không tự sửa hoặc xóa dữ liệu.')
        if rows!=[(1,SCHEMA_VERSION)]:
            raise SchemaVersionError('Schema version không hỗ trợ; cần migration rõ ràng.')
