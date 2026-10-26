"""Hydrate DTOs from saved run metadata; no file I/O, CV, writes, or invented run pairing."""
from sqlalchemy import select
from uuid import UUID
from ..processing.config import parse_config
from ..schemas.pages import RenderRead,DetectionRunRead
from ..storage import repository
from ..storage.models import RenderRun,DetectionRun

def _binding(db,page,run):
    source=repository.get_artifact(db,page.session_id,page.normalized_artifact_id)
    meta=run.metadata_json;s=meta.get('source',{})
    if not isinstance(s,dict):raise ValueError('Invalid source snapshot')
    if (source is None or source.page_id!=page.id or source.kind!='normalized' or source.mime!='image/png'
            or run.source_artifact_id!=source.id or run.source_sha256!=source.sha256
            or meta.get('run_id')!=str(run.id) or s.get('artifact_id')!=str(source.id)
            or s.get('sha256')!=source.sha256 or (s.get('width'),s.get('height'))!=(page.width,page.height)):
        raise ValueError('Stored run/source mismatch')
    return meta,source

def _artifact(db,page,ref,kind,revision):
    if not isinstance(ref,dict):raise ValueError('Invalid artifact snapshot')
    aid=UUID(ref['id'])
    if aid.version!=4:raise ValueError('Invalid artifact UUID')
    artifact=repository.get_artifact(db,page.session_id,aid)
    if (artifact is None or artifact.page_id!=page.id or artifact.kind!=kind or artifact.revision!=revision
            or artifact.mime!='image/png' or artifact.sha256!=ref.get('sha256')
            or (artifact.width,artifact.height)!=(ref.get('width'),ref.get('height'))):
        raise ValueError('Stored run/artifact mismatch')
    return artifact

def read_render_history(db,page,config):
    sid,pid=page.session_id,page.id
    rendered=None
    run=db.scalar(select(RenderRun).where(RenderRun.session_id==sid,RenderRun.page_id==pid)
        .order_by(RenderRun.revision.desc(),RenderRun.created_at.desc(),RenderRun.id.desc()).limit(1))
    if run is not None:
        meta,_=_binding(db,page,run)
        if meta.get('revision')!=run.revision or run.revision>config.revision:raise ValueError('Stored revision mismatch')
        refs=meta['artifacts'];full=_artifact(db,page,refs['full'],'render',run.revision)
        preview=_artifact(db,page,refs['preview'],'preview',run.revision)
        snapshot=parse_config(meta['effective_config'],source_size=(page.width,page.height),warp_size=(full.width,full.height))
        if (full.id!=run.render_artifact_id or preview.id!=run.preview_artifact_id
                or (run.revision==config.revision and snapshot.model_dump(mode='json')!=config.config_json)):
            raise ValueError('Stored render snapshot mismatch')
        rendered=RenderRead(page_id=pid,revision=run.revision,render_run_id=run.id,
            render_artifact_id=full.id,preview_artifact_id=preview.id,width=full.width,height=full.height,timings_ms=meta['timings_ms'])
    return rendered


def read_page_history(db,page,config):
    rendered=read_render_history(db,page,config)
    sid,pid=page.session_id,page.id
    detected=None
    run=db.scalar(select(DetectionRun).where(DetectionRun.session_id==sid,DetectionRun.page_id==pid)
        .order_by(DetectionRun.created_at.desc(),DetectionRun.id.desc()).limit(1))
    if run is not None:
        meta,source=_binding(db,page,run);result=meta['result'];stages={}
        if meta['source'].get('revision')!=run.source_revision or meta.get('algorithm_version')!=run.algorithm_version:
            raise ValueError('Stored detector snapshot mismatch')
        for name,ref in meta['artifacts'].items():
            try:stages[name]=_artifact(db,page,ref,'debug',run.source_revision).id
            except (ValueError,KeyError,TypeError):pass # debug GET reports missing stages; never substitute another artifact
        detected=DetectionRunRead(page_id=pid,run_id=run.id,source_artifact_id=source.id,source_sha256=source.sha256,
            source_width=page.width,source_height=page.height,source_revision=run.source_revision,
            status=result['status'],corners=result['corners'],heuristic_score=result['heuristic_score'],confirmed=result['confirmed'],
            algorithm_version=run.algorithm_version,warnings=result['warnings'],timings_ms=meta['timings_ms'],
            selected_trial_id=meta['selected_trial_id'],stage_artifacts=stages)
    return rendered,detected
