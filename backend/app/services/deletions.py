"""Commit owner-scoped metadata deletion, then remove exact unreferenced UUID files."""
from dataclasses import fields
import logging
from sqlalchemy import delete,select
from ..storage import repository
from ..storage.files import StoredArtifact
from ..storage.models import Artifact,ScanPage,ScanSession,utc_now
from .sessions import SessionNotFoundError
from .page_config import PageNotFoundError
from .session_guards import mutation

logger=logging.getLogger(__name__)

def _cleanup(engine,store,artifacts):
    for artifact in artifacts:
        try:
            with repository.transaction(engine) as db:
                referenced=repository.artifact_referenced(db,artifact)
            # Immutable server UUIDs are never reused. Verify/hash/unlink outside DB reads.
            if not referenced:store._discard(artifact)
        except Exception:
            # Metadata is already committed; retaining an orphan is safer than deleting an uncertain file.
            logger.exception('Cannot clean an unreferenced deleted artifact')

def delete_document_part(engine,store,sid,pid=None):
    with mutation(engine,sid), repository.transaction(engine) as db:
        if not repository.lock_session(db,sid):raise SessionNotFoundError()
        if pid is not None and repository.get_page(db,sid,pid) is None:raise PageNotFoundError()
        query=select(Artifact).where(Artifact.session_id==sid)
        if pid is not None:query=query.where(Artifact.page_id==pid)
        artifacts=[StoredArtifact(**{f.name:getattr(row,f.name) for f in fields(StoredArtifact)}) for row in db.scalars(query)]
        if pid is None:
            db.execute(delete(ScanSession).where(ScanSession.id==sid))
        else:
            db.execute(delete(ScanPage).where(ScanPage.session_id==sid,ScanPage.id==pid))
            repository.set_page_positions(db,repository.list_pages(db,sid))
            repository.get_session(db,sid).updated_at=utc_now()
    _cleanup(engine,store,artifacts)
