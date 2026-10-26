"""Read saved provenance only. Never rerun processing or mix stages by revision."""
from dataclasses import fields
from uuid import UUID

from sqlalchemy import select

from ..schemas.pages import ArtifactRead,DebugQuery,DebugRead
from ..storage import repository
from ..storage.files import ArtifactFileError,StoredArtifact
from ..storage.models import Artifact,DetectionRun,RenderRun
from .page_config import PageNotFoundError
from .sessions import SessionDataError,SessionNotFoundError


class DebugNotFoundError(LookupError):
    pass


def read_debug(engine,store,sid:UUID,pid:UUID,query:DebugQuery)->DebugRead:
    # Snapshot metadata/refs in one short read transaction. File verification is outside it.
    with repository.transaction(engine) as db:
        if repository.get_session(db,sid) is None:raise SessionNotFoundError()
        page=repository.get_page(db,sid,pid)
        if page is None:raise PageNotFoundError()
        config=repository.get_page_config(db,sid,pid)
        if config is None:raise SessionDataError('Thiếu cấu hình trang.')
        current=config.revision
        detection=query.detection_run_id is not None
        kind='detection' if detection else 'render'
        model=DetectionRun if detection else RenderRun
        statement=select(model).where(model.session_id==sid,model.page_id==pid)
        chosen=query.detection_run_id if detection else query.render_run_id
        revision=None if detection else query.revision if query.revision is not None else current
        if chosen is not None:statement=statement.where(model.id==chosen)
        else:statement=statement.where(RenderRun.revision==revision)
        run=db.scalar(statement.order_by(model.created_at.desc(),model.id.desc()).limit(1))
        if run is None:
            legacy=db.scalar(select(Artifact.id).where(Artifact.session_id==sid,Artifact.page_id==pid,
                Artifact.kind=='render',Artifact.revision==revision).limit(1)) if not detection else None
            if chosen is not None or (revision!=current and legacy is None):raise DebugNotFoundError()
            return DebugRead(page_id=pid,kind='render',current_revision=current,revision=revision,
                run_id=None,status='not_recorded',debug_persisted=False,created_at=None,metadata=None,artifacts={},missing_stages={})
        revision=None if detection else run.revision
        expected_revision=run.source_revision if detection else run.revision
        source=repository.get_artifact(db,sid,run.source_artifact_id)
        metadata=run.metadata_json
        if (source is None or source.page_id!=pid or source.kind!='normalized' or source.sha256!=run.source_sha256
                or source.id!=page.normalized_artifact_id or metadata.get('run_id')!=str(run.id)
                or metadata.get('source',{}).get('artifact_id')!=str(source.id)
                or metadata.get('source',{}).get('sha256')!=source.sha256
                or metadata.get('source',{}).get('width')!=page.width
                or metadata.get('source',{}).get('height')!=page.height
                or (not detection and metadata.get('revision')!=run.revision)):
            raise SessionDataError('Debug không khớp nguồn/run.')
        refs=metadata.get('artifacts')
        if not isinstance(refs,dict):raise SessionDataError('Debug thiếu danh sách artifact.')
        records={};missing={}
        for name,ref in refs.items():
            try:aid=UUID(ref['id'])
            except (ValueError,KeyError,TypeError):missing[name]='invalid_metadata';continue
            artifact=repository.get_artifact(db,sid,aid)
            if artifact is None:missing[name]='not_found';continue
            expected_kind='render' if not detection and name=='full' else 'preview' if not detection and name=='preview' else 'debug'
            if (artifact.page_id!=pid or artifact.kind!=expected_kind or artifact.revision!=expected_revision
                    or artifact.mime!='image/png' or artifact.sha256!=ref.get('sha256')
                    or artifact.width!=ref.get('width') or artifact.height!=ref.get('height')
                    or (not detection and name in ('full','preview') and artifact.id!=(run.render_artifact_id if name=='full' else run.preview_artifact_id))):
                missing[name]='invalid_metadata';continue
            records[name]=(StoredArtifact(**{f.name:getattr(artifact,f.name) for f in fields(StoredArtifact)}),
                ArtifactRead(**{key:getattr(artifact,key) for key in ArtifactRead.model_fields}))
        persisted=metadata.get('debug_persisted')
        if type(persisted) is not bool:raise SessionDataError('Debug không có trạng thái lưu.')
        expected=set()
        if not detection:
            expected={'full','preview'}
            if persisted:
                expected|={'warp','filtered_bgr','before_rotation'}
                if metadata.get('effective_config',{}).get('mode')!='color':expected.add('prepared_gray')
        elif persisted:
            expected={'analysis','gray','blurred','contour_overlay'}
            for trial in metadata.get('trials',[]):
                expected.add(trial['trial_id']+'_edges')
                expected.add(trial['trial_id']+('_region_mask' if trial['method']=='region_otsu' else '_closed'))
        for name in expected-refs.keys():missing[name]='not_found'
        response={'page_id':pid,'kind':kind,'current_revision':current,'revision':revision,'run_id':run.id,
            'created_at':run.created_at,'debug_persisted':persisted,'metadata':metadata}
    artifacts={}
    for name,(record,descriptor) in records.items():
        try:store.verify(record)
        except ArtifactFileError:missing[name]='file_unavailable';continue
        artifacts[name]=descriptor
    return DebugRead(**response,status='incomplete' if missing else 'available' if persisted else 'not_requested',
        artifacts=artifacts,missing_stages=missing)
