"""Confirmed snapshot rendering; CPU outside DB, revision gate before publication."""
from dataclasses import asdict, fields
import logging
import json
from time import perf_counter_ns
from uuid import UUID,uuid4

import cv2
from sqlalchemy.engine import Engine

from ..processing.config import ConfigValidationError, parse_config
from ..processing.enhancement import EnhancementValidationError
from ..processing.geometry import GeometryValidationError
from ..processing.render import RenderValidationError, encode_render_images, render_document
from ..schemas.pages import RenderRead
from ..storage import repository
from ..storage.files import ArtifactFileError, ArtifactStore, StoredArtifact
from ..storage.models import RenderRun
from .page_config import read_page_state
from .sessions import SessionDataError, SessionNotFoundError
from .sources import load_normalized_source as _load_source
from .render_debug import describe_render
from .session_guards import mutation

logger = logging.getLogger(__name__)


class PageNotConfirmedError(ValueError):
    pass


class RenderProcessingError(RuntimeError):
    pass


def render_page(engine: Engine, store: ArtifactStore, session_id: UUID, page_id: UUID,
                expected_revision: int, debug: bool = False) -> RenderRead:
    """Blocking use case; HTTP will dispatch the whole call via the shared executor.

    No detector fallback: offline render_document also permits drafts, so this
    boundary explicitly requires user-confirmed corners before entering it.
    """
    with mutation(engine,session_id), repository.transaction(engine) as db:
        page,record = read_page_state(db,session_id,page_id,expected_revision)
        size = (page.width,page.height)
        try:
            config = parse_config(record.config_json,source_size=size)
        except ConfigValidationError as error:
            raise SessionDataError('Config đã lưu không hợp lệ.') from error
        if not config.confirmed or config.corners is None:
            raise PageNotConfirmedError('Cần xác nhận bốn góc trước khi render.')
        artifact = repository.get_artifact(db,session_id,page.normalized_artifact_id)
        if (artifact is None or artifact.page_id!=page_id or artifact.kind!='normalized'
                or artifact.mime!='image/png' or artifact.revision is not None):
            raise SessionDataError('Metadata nguồn chuẩn hóa không hợp lệ.')
        source = StoredArtifact(**{field.name:getattr(artifact,field.name) for field in fields(StoredArtifact)})

    started = perf_counter_ns()
    pixels = _load_source(store,source,size)
    load_ms = (perf_counter_ns()-started)/1e6
    try:
        result = render_document(pixels,config,debug=debug)
        if result.status!='rendered' or result.enhancement is None:
            raise RenderProcessingError('Không tạo được full render từ góc đã xác nhận.')
        started = perf_counter_ns()
        images = encode_render_images(result.enhancement.image)
        run_id=uuid4()
        metadata,stages=describe_render(result,source,run_id,expected_revision,debug)
        encode_ms = (perf_counter_ns()-started)/1e6
        metadata['timings_ms']={**{f'core.{name}':value for name,value in asdict(result.timings_ms).items()},
            'source_load':load_ms,'encode':encode_ms}
        metadata=json.loads(json.dumps(metadata,allow_nan=False))
    except (ConfigValidationError,GeometryValidationError,EnhancementValidationError,
            RenderValidationError,cv2.error,ValueError) as error:
        raise RenderProcessingError('Không xử lý được ảnh với cấu hình đã lưu.') from error

    stored = []
    try:
        with mutation(engine,session_id), repository.transaction(engine) as db:
            if not repository.lock_session(db,session_id):
                raise SessionNotFoundError()
            current,current_config = read_page_state(db,session_id,page_id,expected_revision)
            if ((current.width,current.height)!=size or current.normalized_artifact_id!=source.id
                    or current_config.config_json!=config.model_dump(mode='json')):
                raise SessionDataError('Snapshot thay đổi mà không tăng revision.')
            # Only completed/encoded bytes enter this short write transaction.
            # The writer lock prevents edits/deletes between the gate and commit.
            for name,raster in (('full',images.full),('preview',images.preview),*stages.items()):
                kind='render' if name=='full' else 'preview' if name=='preview' else 'debug'
                stored.append(store.write_bytes(session_id=session_id,page_id=page_id,
                    kind=kind,revision=expected_revision,mime='image/png',payload=raster.png_bytes,
                    width=raster.width,height=raster.height))
                repository.register_artifact(db,store,stored[-1])
                descriptor=stored[-1]
                metadata['artifacts'][name]={'id':str(descriptor.id),'sha256':descriptor.sha256,
                    'width':descriptor.width,'height':descriptor.height,'png_mode':raster.png_mode}
            db.add(RenderRun(id=run_id,session_id=session_id,page_id=page_id,revision=expected_revision,
                source_artifact_id=source.id,source_sha256=source.sha256,
                render_artifact_id=stored[0].id,preview_artifact_id=stored[1].id,metadata_json=metadata))
            response = RenderRead(page_id=page_id,revision=expected_revision,
                render_artifact_id=stored[0].id,preview_artifact_id=stored[1].id,
                render_run_id=run_id,
                width=images.full.width,height=images.full.height,
                timings_ms=metadata['timings_ms'])
        return response
    except Exception:
        for artifact in stored:
            try:
                with repository.transaction(engine) as db:
                    repository.discard_unreferenced(db,store,artifact)
            except Exception:
                logger.exception('Cannot clean a newly written render artifact')
        raise
