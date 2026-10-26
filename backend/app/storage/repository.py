"""Small metadata queries/unit of work; services own quotas, CAS and file I/O."""
from contextlib import contextmanager
from dataclasses import asdict
from uuid import UUID

from sqlalchemy import func, or_, select, update
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from .models import Artifact, PageConfigRecord, ScanPage, ScanSession, utc_now
from .files import ArtifactStore, StoredArtifact


@contextmanager
def transaction(engine: Engine):
    with Session(engine) as db, db.begin():
        yield db


def create_session(db: Session, title: str = 'Tài liệu chưa đặt tên') -> ScanSession:
    record = ScanSession(title=title)  # boundary/service supplies the validated title
    db.add(record)
    db.flush()  # allocate ID, no implicit commit
    return record


def get_session(db: Session, session_id: UUID) -> ScanSession | None:
    return db.get(ScanSession,session_id)


def rename_session(db: Session, session_id: UUID, title: str) -> ScanSession | None:
    # Write before reading: serialize metadata writers without a read/upgrade race.
    # Repeating the same title is a no-op, including updated_at.
    db.execute(update(ScanSession).where(ScanSession.id==session_id,ScanSession.title!=title)
        .values(title=title,updated_at=utc_now()))
    return get_session(db,session_id)


def lock_import_session(db: Session, session_id: UUID) -> bool:
    # Acquire SQLite's writer lock BEFORE reading count/position; two imports
    # cannot both observe the same append slot. Image work happens beforehand.
    return db.execute(update(ScanSession).where(ScanSession.id==session_id)
        .values(updated_at=utc_now())).rowcount==1


def page_count_and_next_position(db: Session, session_id: UUID) -> tuple[int,int]:
    count,last = db.execute(select(func.count(),func.max(ScanPage.position))
        .where(ScanPage.session_id==session_id)).one()
    return count,0 if last is None else last+1


def add_source_page(db: Session, session_id: UUID, page_id: UUID, position: int,
                    sources: list[StoredArtifact], config: dict) -> ScanPage:
    original,normalized,thumbnail = sources
    page = ScanPage(id=page_id,session_id=session_id,position=position,
        width=normalized.width,height=normalized.height,original_artifact_id=original.id,
        normalized_artifact_id=normalized.id,thumbnail_artifact_id=thumbnail.id)
    db.add(page)
    db.add(PageConfigRecord(page_id=page_id,session_id=session_id,revision=0,config_json=config))
    return page


def list_sessions(db: Session, limit: int, offset: int) -> tuple[list[ScanSession],int]:
    total = db.scalar(select(func.count()).select_from(ScanSession))
    rows = db.scalars(select(ScanSession).order_by(ScanSession.updated_at.desc(),ScanSession.id.asc())
        .limit(limit).offset(offset))
    return list(rows),total


def session_page_rows(db: Session, session_id: UUID):
    latest = select(func.max(Artifact.revision)).where(Artifact.session_id==session_id,
        Artifact.page_id==ScanPage.id,Artifact.kind=='render').correlate(ScanPage).scalar_subquery()
    return db.execute(select(ScanPage,PageConfigRecord,latest).outerjoin(PageConfigRecord,
        (PageConfigRecord.page_id==ScanPage.id)&(PageConfigRecord.session_id==ScanPage.session_id))
        .where(ScanPage.session_id==session_id).order_by(ScanPage.position)).all()


def list_pages(db: Session, session_id: UUID) -> list[ScanPage]:
    return list(db.scalars(select(ScanPage).where(ScanPage.session_id==session_id).order_by(ScanPage.position)))


def set_page_positions(db: Session, pages: list[ScanPage]) -> bool:
    if all(page.position==i for i,page in enumerate(pages)):
        return False
    n=len(pages)
    occupied={page.position for page in pages}
    # Free slots above the final range avoid immediate UNIQUE collisions in SQLite.
    temporary=iter(i for i in range(n,3*n) if i not in occupied)
    for page in pages:page.position=next(temporary)
    db.flush()
    for i,page in enumerate(pages):page.position=i
    db.flush()
    return True


def get_page(db: Session, session_id: UUID, page_id: UUID) -> ScanPage | None:
    return db.scalar(select(ScanPage).where(ScanPage.session_id==session_id,ScanPage.id==page_id))


def lock_session(db: Session, session_id: UUID) -> bool:
    """Serialize short mutation/finalization transactions without touching timestamps."""
    return db.execute(update(ScanSession).where(ScanSession.id==session_id)
        .values(updated_at=ScanSession.updated_at)).rowcount==1


def get_page_config(db: Session, session_id: UUID, page_id: UUID) -> PageConfigRecord | None:
    return db.scalar(select(PageConfigRecord).where(PageConfigRecord.session_id==session_id,
        PageConfigRecord.page_id==page_id))


def get_artifact(db: Session, session_id: UUID, artifact_id: UUID) -> Artifact | None:
    return db.scalar(select(Artifact).where(Artifact.session_id==session_id,Artifact.id==artifact_id))


def find_artifact(db: Session, artifact_id: UUID) -> Artifact | None:
    return db.scalar(select(Artifact).join(ScanSession,ScanSession.id==Artifact.session_id)
        .outerjoin(ScanPage,(ScanPage.id==Artifact.page_id)&(ScanPage.session_id==Artifact.session_id))
        .where(Artifact.id==artifact_id,or_(Artifact.page_id.is_(None),ScanPage.id.is_not(None))))


def register_artifact(db: Session, store: ArtifactStore, stored: StoredArtifact) -> Artifact:
    """Register only a completed, hash-verified file; caller owns transaction."""
    store.verify(stored)
    record = Artifact(**asdict(stored))
    db.add(record)
    db.flush()
    return record


def discard_unreferenced(db: Session, store: ArtifactStore, stored: StoredArtifact) -> bool:
    """Use after rollback for this operation's newly written descriptors only.

    Check ownership/evidence in DB before touching a file; never remove an
    active artifact or recursively delete paths supplied by an upload.
    """
    if artifact_referenced(db,stored):
        return False
    store._discard(stored)
    return True


def artifact_referenced(db:Session,stored:StoredArtifact)->bool:
    return db.scalar(select(Artifact.id).where(or_(Artifact.id==stored.id,Artifact.path==stored.path))) is not None
