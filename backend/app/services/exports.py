"""Confirmed snapshots, bounded execution and atomic export publication."""
from contextlib import contextmanager
from dataclasses import dataclass,fields
from uuid import UUID
from hashlib import sha256
from io import BytesIO
import logging
from reportlab.pdfgen.canvas import Canvas
from ..export.pdf import append_pdf_page
from ..export.images import decode_full_png,encode_image
from ..processing.config import PageConfig,parse_config
from ..schemas.exports import ExportRequest,ExportRead
from ..schemas.pages import PageSnapshot
from ..storage import repository
from ..storage.files import StoredArtifact,ArtifactFileError
from ..storage.models import ExportRecord
from .page_config import read_page_state
from .page_history import read_render_history
from .renders import PageNotConfirmedError
from .sessions import SessionDataError,SessionNotFoundError
from .session_guards import reserve_export

logger=logging.getLogger(__name__)


class ExportProcessingError(RuntimeError):
    pass


class PageNotRenderedError(ValueError):
    def __init__(self,pages:tuple[PageSnapshot,...]):
        super().__init__('Cần tạo bản quét đúng revision cho các trang đã chọn.')
        self.pages=pages


@dataclass(frozen=True,slots=True)
class ExportPage:
    page_id: UUID
    revision: int
    render_run_id: UUID
    config: PageConfig
    full: StoredArtifact


@dataclass(frozen=True,slots=True)
class ExportSnapshot:
    session_id: UUID
    title: str
    request: ExportRequest
    pages: tuple[ExportPage,...]


def load_export_pixels(store,page:ExportPage):
    """Read exact full bytes while the caller holds its export lease."""
    full=page.full
    try:payload=store.verify(full).read_bytes()
    except OSError as error:raise ArtifactFileError('Không đọc được full render.') from error
    if len(payload)!=full.byte_size or sha256(payload).hexdigest()!=full.sha256:
        raise ArtifactFileError('Full render đã thay đổi khi đọc.')
    try:return decode_full_png(payload,(full.width,full.height))
    except ValueError as error:raise ArtifactFileError('Full render không giải mã đúng metadata.') from error


def encode_snapshot_image(store,snapshot:ExportSnapshot):
    """Prepare bytes under export_snapshot/run_export; no DB/file publication yet."""
    if snapshot.request.format not in ('png','jpg') or len(snapshot.pages)!=1:
        raise ValueError('Xuất ảnh cần đúng một trang và formatPNG/JPG.')
    page=snapshot.pages[0]
    title=f'{snapshot.title}-{page.page_id.hex[:8]}-r{page.revision}'
    return encode_image(load_export_pixels(store,page),snapshot.request.format,title=title)


def publish_export(engine,store,snapshot:ExportSnapshot)->ExportRead:
    """Encode in request order, publish one complete file, commit artifact+receipt."""
    request=snapshot.request
    try:
        if request.format=='pdf':
            stream=BytesIO();canvas=Canvas(stream,pageCompression=1)
            for page in snapshot.pages:
                append_pdf_page(canvas,load_export_pixels(store,page),orientation=request.orientation,
                    margin_mm=request.margin_mm,image_encoding=request.image_encoding)
            canvas.save();payload=stream.getvalue();mime='application/pdf';width=height=None
        else:
            image=encode_snapshot_image(store,snapshot)
            payload,mime,width,height=image.payload,image.mime,image.width,image.height
    except ArtifactFileError:raise
    except Exception as error:raise ExportProcessingError('Không tạo được tệp xuất.') from error
    stored=None
    try:
        stored=store.write_bytes(session_id=snapshot.session_id,page_id=None,
            kind='pdf' if request.format=='pdf' else 'export_image',mime=mime,payload=payload,width=width,height=height)
        with repository.transaction(engine) as db:
            if not repository.lock_session(db,snapshot.session_id):raise SessionNotFoundError()
            for page in snapshot.pages:
                _,record=read_page_state(db,snapshot.session_id,page.page_id,page.revision)
                if record.config_json!=page.config.model_dump(mode='json'):
                    raise SessionDataError('Cấu hình snapshot đã thay đổi.')
                if repository.get_artifact(db,snapshot.session_id,page.full.id) is None:
                    raise SessionDataError('Full render snapshot không còn được tham chiếu.')
            repository.register_artifact(db,store,stored)
            record=ExportRecord(session_id=snapshot.session_id,artifact_id=stored.id,format=request.format,
                page_snapshot_json=[page.model_dump(mode='json') for page in request.pages])
            db.add(record);db.flush()
            response=ExportRead(id=record.id,session_id=record.session_id,artifact_id=stored.id,
                format=request.format,pages=request.pages,created_at=record.created_at)
        return response
    except Exception:
        if stored is not None:
            try:
                with repository.transaction(engine) as db:repository.discard_unreferenced(db,store,stored)
            except Exception:logger.exception('Cannot clean an unreferenced export artifact')
        raise


def _snapshot(engine,store,sid,request):
    # Revalidate a model too: model_copy(update=...) does not validate changes.
    request=ExportRequest.model_validate(request.model_dump(mode='json'))
    pages=[];missing=[]
    with repository.transaction(engine) as db:
        document=repository.get_session(db,sid)
        if document is None:raise SessionNotFoundError()
        title=document.title
        for item in request.pages:
            page,record=read_page_state(db,sid,item.page_id,item.revision)
            try:
                config=parse_config(record.config_json,source_size=(page.width,page.height))
                if not config.confirmed or config.corners is None:
                    raise PageNotConfirmedError('Cần xác nhận bốn góc trước khi xuất.')
                rendered=read_render_history(db,page,record)
                if rendered is None or rendered.revision!=item.revision:
                    missing.append(item)
                    continue
                artifact=repository.get_artifact(db,sid,rendered.render_artifact_id)
                full=StoredArtifact(**{f.name:getattr(artifact,f.name) for f in fields(StoredArtifact)})
            except (ValueError,KeyError,TypeError) as error:
                if isinstance(error,PageNotConfirmedError):raise
                raise SessionDataError('Metadata bản quét đã lưu không hợp lệ.') from error
            pages.append(ExportPage(page.id,item.revision,rendered.render_run_id,config,full))
    if missing:raise PageNotRenderedError(tuple(missing))
    # Hash/path/size verification outside the metadata read transaction.
    for page in pages:store.verify(page.full)
    return ExportSnapshot(sid,title,request,tuple(pages))


@contextmanager
def export_snapshot(engine,store,sid,request):
    """Keep the lease around snapshot AND the caller's complete write/publication."""
    lease=reserve_export(engine,sid)
    try:
        lease.start()
        yield _snapshot(engine,store,sid,request)
    finally:lease.release()


async def run_export(processing,engine,store,sid,request,writer):
    """Reserve before enqueue; cancelled queued work releases, active work retains."""
    lease=reserve_export(engine,sid)
    def work():
        if not lease.start():return None  # cancellation won before worker claim
        try:return writer(_snapshot(engine,store,sid,request))
        finally:lease.release()
    try:
        future=processing.submit(work)
        future.add_done_callback(lambda done:lease.cancel_waiting() if done.cancelled() else None)
        return await future
    finally:lease.cancel_waiting()  # includes 429/closed/queued cancellation
