"""Minimal metadata schema. Image bytes remain on disk; no ORM file I/O."""
from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, ForeignKeyConstraint, Integer, JSON, String, UniqueConstraint, Uuid
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import TypeDecorator


class UTCDateTime(TypeDecorator):
    """SQLite stores UTC ISO text; callers always receive aware UTC datetime."""
    impl = String(32)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if not isinstance(value,datetime) or value.tzinfo is None or value.utcoffset() is None:
            raise ValueError('Timestamp phải có timezone.')
        return value.astimezone(UTC).isoformat(timespec='microseconds').replace('+00:00','Z')

    def process_result_value(self, value, dialect):
        return None if value is None else datetime.fromisoformat(value).astimezone(UTC)


def utc_now():
    return datetime.now(UTC)


class Base(DeclarativeBase):
    pass


class SchemaVersion(Base):
    __tablename__ = 'schema_version'
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    version: Mapped[int] = mapped_column(Integer,nullable=False)
    __table_args__ = (CheckConstraint('id = 1'),CheckConstraint('version >= 1'))


class ScanSession(Base):
    __tablename__ = 'sessions'
    id: Mapped[UUID] = mapped_column(Uuid,primary_key=True,default=uuid4)
    title: Mapped[str] = mapped_column(String(200),nullable=False)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime,default=utc_now,nullable=False)
    updated_at: Mapped[datetime] = mapped_column(UTCDateTime,default=utc_now,nullable=False)
    __table_args__ = (CheckConstraint('length(trim(title)) BETWEEN 1 AND 200'),)


class ScanPage(Base):
    __tablename__ = 'pages'
    id: Mapped[UUID] = mapped_column(Uuid,primary_key=True,default=uuid4)
    session_id: Mapped[UUID] = mapped_column(Uuid,ForeignKey('sessions.id',ondelete='CASCADE'),nullable=False)
    position: Mapped[int] = mapped_column(Integer,nullable=False)
    width: Mapped[int] = mapped_column(Integer,nullable=False)
    height: Mapped[int] = mapped_column(Integer,nullable=False)
    original_artifact_id: Mapped[UUID] = mapped_column(Uuid,nullable=False)
    normalized_artifact_id: Mapped[UUID] = mapped_column(Uuid,nullable=False)
    thumbnail_artifact_id: Mapped[UUID] = mapped_column(Uuid,nullable=False)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime,default=utc_now,nullable=False)
    updated_at: Mapped[datetime] = mapped_column(UTCDateTime,default=utc_now,nullable=False)
    __table_args__ = (
        UniqueConstraint('session_id','id'),UniqueConstraint('session_id','position'),
        CheckConstraint("typeof(position) = 'integer' AND position >= 0"),
        CheckConstraint("typeof(width) = 'integer' AND typeof(height) = 'integer' AND width >= 2 AND height >= 2 AND width*height <= 16000000"),
        # A source must belong to this exact page and session. Deferred cycles
        # allow allocating UUIDs and inserting page+source rows in one transaction.
        *(ForeignKeyConstraint(['session_id','id',name],['artifacts.session_id','artifacts.page_id','artifacts.id'],
            name=f'page_{name}_owner',deferrable=True,initially='DEFERRED')
          for name in ('original_artifact_id','normalized_artifact_id','thumbnail_artifact_id')),
    )


class PageConfigRecord(Base):
    __tablename__ = 'page_configs'
    page_id: Mapped[UUID] = mapped_column(Uuid,primary_key=True)
    session_id: Mapped[UUID] = mapped_column(Uuid,nullable=False)
    revision: Mapped[int] = mapped_column(Integer,nullable=False,default=0)
    config_json: Mapped[dict] = mapped_column(JSON(none_as_null=True),nullable=False)
    updated_at: Mapped[datetime] = mapped_column(UTCDateTime,default=utc_now,nullable=False)
    __table_args__ = (
        ForeignKeyConstraint(['session_id','page_id'],['pages.session_id','pages.id'],ondelete='CASCADE',
            deferrable=True,initially='DEFERRED'),
        CheckConstraint("typeof(revision) = 'integer' AND revision >= 0"),
        CheckConstraint("json_valid(config_json) AND json_type(config_json) = 'object'"),
    )


class Artifact(Base):
    __tablename__ = 'artifacts'
    id: Mapped[UUID] = mapped_column(Uuid,primary_key=True,default=uuid4)
    session_id: Mapped[UUID] = mapped_column(Uuid,ForeignKey('sessions.id',ondelete='CASCADE'),nullable=False)
    page_id: Mapped[UUID | None] = mapped_column(Uuid,nullable=True)
    kind: Mapped[str] = mapped_column(String(20),nullable=False)
    revision: Mapped[int | None] = mapped_column(Integer,nullable=True)
    path: Mapped[str] = mapped_column(String(500),nullable=False,unique=True)
    mime: Mapped[str] = mapped_column(String(32),nullable=False)
    byte_size: Mapped[int] = mapped_column(Integer,nullable=False)
    sha256: Mapped[str] = mapped_column(String(64),nullable=False)
    width: Mapped[int | None] = mapped_column(Integer,nullable=True)
    height: Mapped[int | None] = mapped_column(Integer,nullable=True)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime,default=utc_now,nullable=False)
    __table_args__ = (
        UniqueConstraint('session_id','id'),UniqueConstraint('session_id','page_id','id'),
        ForeignKeyConstraint(['session_id','page_id'],['pages.session_id','pages.id'],ondelete='CASCADE',
            deferrable=True,initially='DEFERRED'),
        CheckConstraint("(page_id IS NULL AND kind IN ('pdf','export_image')) OR (page_id IS NOT NULL AND kind IN ('original','normalized','thumbnail','render','preview','debug'))"),
        CheckConstraint("(kind IN ('original','normalized','thumbnail','pdf','export_image') AND revision IS NULL) OR (kind IN ('render','preview','debug') AND typeof(revision) = 'integer' AND revision >= 0)"),
        CheckConstraint("mime IN ('image/jpeg','image/png','application/pdf')"),
        CheckConstraint("typeof(byte_size) = 'integer' AND byte_size > 0"),
        CheckConstraint("length(sha256) = 64 AND sha256 NOT GLOB '*[^0-9a-f]*'"),
        CheckConstraint('(width IS NULL AND height IS NULL) OR (width >= 1 AND height >= 1 AND width IS NOT NULL AND height IS NOT NULL)'),
        CheckConstraint("length(path) BETWEEN 1 AND 500 AND path NOT LIKE '/%' AND instr(path,'..') = 0 AND instr(path,':') = 0 AND instr(path,char(92)) = 0"),
    )


class DetectionRun(Base):
    __tablename__ = 'detection_runs'
    id: Mapped[UUID] = mapped_column(Uuid,primary_key=True,default=uuid4)
    session_id: Mapped[UUID] = mapped_column(Uuid,nullable=False)
    page_id: Mapped[UUID] = mapped_column(Uuid,nullable=False)
    source_artifact_id: Mapped[UUID] = mapped_column(Uuid,nullable=False)
    source_revision: Mapped[int] = mapped_column(Integer,nullable=False)
    source_sha256: Mapped[str] = mapped_column(String(64),nullable=False)
    algorithm_version: Mapped[str] = mapped_column(String(100),nullable=False)
    metadata_json: Mapped[dict] = mapped_column(JSON(none_as_null=True),nullable=False)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime,default=utc_now,nullable=False)
    __table_args__ = (
        ForeignKeyConstraint(['session_id','page_id'],['pages.session_id','pages.id'],ondelete='CASCADE'),
        ForeignKeyConstraint(['session_id','page_id','source_artifact_id'],
            ['artifacts.session_id','artifacts.page_id','artifacts.id'],ondelete='CASCADE'),
        CheckConstraint("typeof(source_revision) = 'integer' AND source_revision >= 0"),
        CheckConstraint("length(source_sha256) = 64 AND source_sha256 NOT GLOB '*[^0-9a-f]*'"),
        CheckConstraint("length(algorithm_version) BETWEEN 1 AND 100"),
        CheckConstraint("json_valid(metadata_json) AND json_type(metadata_json) = 'object'"),
    )


class RenderRun(Base):
    __tablename__ = 'render_runs'
    id: Mapped[UUID] = mapped_column(Uuid,primary_key=True,default=uuid4)
    session_id: Mapped[UUID] = mapped_column(Uuid,nullable=False)
    page_id: Mapped[UUID] = mapped_column(Uuid,nullable=False)
    revision: Mapped[int] = mapped_column(Integer,nullable=False)
    source_artifact_id: Mapped[UUID] = mapped_column(Uuid,nullable=False)
    source_sha256: Mapped[str] = mapped_column(String(64),nullable=False)
    render_artifact_id: Mapped[UUID] = mapped_column(Uuid,nullable=False)
    preview_artifact_id: Mapped[UUID] = mapped_column(Uuid,nullable=False)
    metadata_json: Mapped[dict] = mapped_column(JSON(none_as_null=True),nullable=False)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime,default=utc_now,nullable=False)
    __table_args__ = (
        ForeignKeyConstraint(['session_id','page_id'],['pages.session_id','pages.id'],ondelete='CASCADE'),
        *(ForeignKeyConstraint(['session_id','page_id',name],
            ['artifacts.session_id','artifacts.page_id','artifacts.id'],ondelete='CASCADE')
            for name in ('source_artifact_id','render_artifact_id','preview_artifact_id')),
        CheckConstraint("typeof(revision) = 'integer' AND revision >= 0"),
        CheckConstraint("length(source_sha256) = 64 AND source_sha256 NOT GLOB '*[^0-9a-f]*'"),
        CheckConstraint("json_valid(metadata_json) AND json_type(metadata_json) = 'object'"),
    )


class ExportRecord(Base):
    __tablename__ = 'exports'
    id: Mapped[UUID] = mapped_column(Uuid,primary_key=True,default=uuid4)
    session_id: Mapped[UUID] = mapped_column(Uuid,ForeignKey('sessions.id',ondelete='CASCADE'),nullable=False)
    artifact_id: Mapped[UUID] = mapped_column(Uuid,nullable=False)
    format: Mapped[str] = mapped_column(String(4),nullable=False)
    page_snapshot_json: Mapped[list] = mapped_column(JSON(none_as_null=True),nullable=False)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime,default=utc_now,nullable=False)
    __table_args__ = (
        ForeignKeyConstraint(['session_id','artifact_id'],['artifacts.session_id','artifacts.id'],ondelete='CASCADE',
            deferrable=True,initially='DEFERRED'),
        CheckConstraint("format IN ('pdf','png','jpg')"),
        CheckConstraint("json_valid(page_snapshot_json) AND json_type(page_snapshot_json) = 'array' AND json_array_length(page_snapshot_json) BETWEEN 1 AND 20"),
    )
