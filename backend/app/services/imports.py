"""Import one encoded image; CPU/encoding/file writes precede metadata commit."""
import logging
from uuid import UUID, uuid4

from sqlalchemy.engine import Engine

from ..processing.config import get_preset
from ..processing.image_sizes import resize_to_max_edge
from ..processing.normalize import encode_normalized_png, normalize_image, validate_image
from ..processing.render import encode_stage_png
from ..schemas.pages import PageRead
from ..settings import MAX_PAGES_PER_SESSION
from ..storage import repository
from ..storage.files import ArtifactStore
from .sessions import SessionNotFoundError
from .session_guards import mutation

logger = logging.getLogger(__name__)


class PageLimitError(ValueError):
    code = 'PAGE_LIMIT_EXCEEDED'


def import_page(engine: Engine, store: ArtifactStore, session_id: UUID, payload: bytes) -> PageRead:
    """Blocking use case: submit to the app's ProcessingExecutor from async HTTP.

    No filename, caller config, auto-detection or confirmation is accepted.
    The returned revision-zero DTO is built before commit, returned afterwards.
    """
    if not isinstance(session_id,UUID) or session_id.version!=4:
        raise SessionNotFoundError()
    if type(payload) is not bytes:
        raise TypeError('Import cần immutable bytes của ảnh tải lên.')
    with mutation(engine,session_id), repository.transaction(engine) as db:
        if repository.get_session(db,session_id) is None:
            raise SessionNotFoundError()
        count,_ = repository.page_count_and_next_position(db,session_id)
        if count>=MAX_PAGES_PER_SESSION:
            raise PageLimitError('Tài liệu đã đủ 20 trang.')

    info = validate_image(payload)
    source = normalize_image(payload)
    normalized = encode_normalized_png(source)
    # Reuse the display encoder: valid skinny sources may yield a side1 thumbnail.
    thumbnail = encode_stage_png(resize_to_max_edge(source,320))
    config = get_preset()
    page_id = uuid4()
    stored = []
    try:
        for kind,mime,data,width,height in (
            ('original','image/jpeg' if info.format=='JPEG' else 'image/png',payload,info.width,info.height),
            ('normalized','image/png',normalized.png_bytes,normalized.width,normalized.height),
            ('thumbnail','image/png',thumbnail.png_bytes,thumbnail.width,thumbnail.height)):
            stored.append(store.write_bytes(session_id=session_id,page_id=page_id,kind=kind,mime=mime,
                payload=data,width=width,height=height))
        with mutation(engine,session_id), repository.transaction(engine) as db:
            if not repository.lock_import_session(db,session_id):
                raise SessionNotFoundError()
            count,position = repository.page_count_and_next_position(db,session_id)
            if count>=MAX_PAGES_PER_SESSION:
                raise PageLimitError('Tài liệu đã đủ 20 trang.')
            page = repository.add_source_page(db,session_id,page_id,position,stored,config.model_dump(mode='json'))
            for artifact in stored:
                repository.register_artifact(db,store,artifact)
            response = PageRead(id=page.id,session_id=session_id,position=position,width=page.width,height=page.height,
                original_artifact_id=page.original_artifact_id,normalized_artifact_id=page.normalized_artifact_id,
                thumbnail_artifact_id=page.thumbnail_artifact_id,revision=0,render_revision=None,effective_config=config,
                created_at=page.created_at,updated_at=page.updated_at)
        return response
    except Exception:
        # A commit error can be ambiguous: query fresh DB state before removing
        # only this operation's descriptors. Preserve the original exception.
        for artifact in stored:
            try:
                with repository.transaction(engine) as db:
                    repository.discard_unreferenced(db,store,artifact)
            except Exception:
                logger.exception('Cannot clean a newly written import artifact')
        raise
