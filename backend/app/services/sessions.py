"""Document metadata use cases; no image loading or long processing in DB."""
from uuid import UUID

from sqlalchemy.engine import Engine

from ..schemas.pages import PageRead
from ..schemas.sessions import PageOrderRequest, SessionCreate, SessionDetail, SessionList, SessionRead, SessionRename
from ..storage import repository
from ..storage.models import utc_now
from .session_guards import mutation


class SessionNotFoundError(LookupError):
    pass


class SessionDataError(RuntimeError):
    pass


class PageOrderError(ValueError):
    pass


def create_document(engine: Engine, request: SessionCreate) -> SessionRead:
    with repository.transaction(engine) as db:
        record = repository.create_session(db,request.title)
        response = SessionRead.model_validate(record,from_attributes=True)
    return response  # commit succeeded before returning to HTTP


def list_documents(engine: Engine, limit: int, offset: int) -> SessionList:
    with repository.transaction(engine) as db:
        rows,total = repository.list_sessions(db,limit,offset)
        return SessionList(items=[SessionRead.model_validate(row,from_attributes=True) for row in rows],
            limit=limit,offset=offset,total=total)


def rename_document(engine: Engine, session_id: UUID, request: SessionRename) -> SessionRead:
    with mutation(engine,session_id), repository.transaction(engine) as db:
        record = repository.rename_session(db,session_id,request.title)
        if record is None:
            raise SessionNotFoundError()
        response = SessionRead.model_validate(record,from_attributes=True)
    return response


def get_document(engine: Engine, session_id: UUID) -> SessionDetail:
    with repository.transaction(engine) as db:
        return _get_document(db,session_id)


def _get_document(db,session_id:UUID)->SessionDetail:
    from .page_history import read_page_history
    record = repository.get_session(db,session_id)
    if record is None:raise SessionNotFoundError()
    pages = []
    for page,config,render_revision in repository.session_page_rows(db,session_id):
        if config is None:raise SessionDataError('Trang thiếu config metadata.')
        try:
            rendered,detected=read_page_history(db,page,config)
            pages.append(PageRead(id=page.id,session_id=page.session_id,position=page.position,
                width=page.width,height=page.height,original_artifact_id=page.original_artifact_id,
                normalized_artifact_id=page.normalized_artifact_id,thumbnail_artifact_id=page.thumbnail_artifact_id,
                revision=config.revision,render_revision=render_revision,effective_config=config.config_json,
                latest_render=rendered,latest_detection=detected,
                created_at=page.created_at,updated_at=page.updated_at))
        except (ValueError,KeyError,TypeError) as error:
            raise SessionDataError('Metadata trang không hợp lệ.') from error
    data = SessionRead.model_validate(record,from_attributes=True).model_dump()
    return SessionDetail(**data,pages=pages)


def order_document(engine:Engine,session_id:UUID,request:PageOrderRequest)->SessionDetail:
    with mutation(engine,session_id), repository.transaction(engine) as db:
        if not repository.lock_session(db,session_id):raise SessionNotFoundError()
        pages=repository.list_pages(db,session_id)
        by_id={page.id:page for page in pages}
        if set(request.page_ids)!=set(by_id):raise PageOrderError('Phải gửi đủ trang của tài liệu, không thừa hoặc thiếu.')
        if repository.set_page_positions(db,[by_id[pid] for pid in request.page_ids]):
            repository.get_session(db,session_id).updated_at=utc_now()
        response=_get_document(db,session_id)
    return response
