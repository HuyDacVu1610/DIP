"""Full config replacement and SQLite revision CAS; no raster processing."""
from uuid import UUID

from sqlalchemy.engine import Engine

from ..processing.geometry import estimate_warp_size
from ..schemas.pages import ConfigRead, ConfigUpdateRequest
from ..storage import repository
from ..storage.models import utc_now
from .sessions import SessionDataError, SessionNotFoundError
from .session_guards import mutation


class PageNotFoundError(LookupError):
    pass


class RevisionConflictError(ValueError):
    def __init__(self, expected_revision: int, actual_revision: int):
        super().__init__('Cấu hình đã thay đổi; tải lại trang.')
        self.expected_revision = expected_revision
        self.actual_revision = actual_revision


def read_page_state(db, session_id: UUID, page_id: UUID, expected_revision: int):
    if repository.get_session(db,session_id) is None:
        raise SessionNotFoundError()
    page = repository.get_page(db,session_id,page_id)
    if page is None:
        raise PageNotFoundError()
    record = repository.get_page_config(db,session_id,page_id)
    if record is None:
        raise SessionDataError('Trang thiếu config metadata.')
    if record.revision!=expected_revision:
        raise RevisionConflictError(expected_revision,record.revision)
    return page,record


def update_page_config(engine: Engine, session_id: UUID, page_id: UUID,
                       request: ConfigUpdateRequest) -> ConfigRead:
    with mutation(engine,session_id), repository.transaction(engine) as db:
        # First statement acquires SQLite writer lock, before any read snapshot.
        if not repository.lock_session(db,session_id):
            raise SessionNotFoundError()
        page,record = read_page_state(db,session_id,page_id,request.expected_revision)
        source_size = (page.width,page.height)
        config = request.validate_config(source_size=source_size)
        if config.corners is not None:
            warp_size = estimate_warp_size(config.corners,*source_size)
            config = request.validate_config(source_size=source_size,warp_size=warp_size)
        payload = config.model_dump(mode='json')
        if payload!=record.config_json:
            now = utc_now()
            record.config_json = payload
            record.revision += 1
            record.updated_at = page.updated_at = now
            repository.get_session(db,session_id).updated_at = now
        response = ConfigRead.model_validate({'page_id':page_id,'revision':record.revision,
            'effective_config':payload,'inactive_fields':config.inactive_fields},
            context={'source_size':source_size})
    return response
