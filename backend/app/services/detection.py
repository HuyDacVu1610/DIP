"""Source-bound detector runs; never write page config/confirmation or render pixels."""
from dataclasses import asdict,fields
import json
import logging
from time import perf_counter_ns
from uuid import UUID,uuid4

from sqlalchemy.engine import Engine

from ..processing.detection import RegionTrial,detect_document
from ..processing.render import encode_stage_png
from ..schemas.pages import DetectionRunRead
from ..storage import repository
from ..storage.files import ArtifactStore,StoredArtifact
from ..storage.models import DetectionRun
from .page_config import PageNotFoundError
from .sessions import SessionDataError,SessionNotFoundError
from .sources import load_normalized_source
from .session_guards import mutation

logger=logging.getLogger(__name__)


class DetectionProcessingError(RuntimeError):
    pass


def _describe(result,source,revision,run_id,debug):
    """Separate actual stage arrays from JSON, referring to contours once per trial."""
    details=result.debug
    if details is None:raise DetectionProcessingError('Thiếu provenance của detector.')
    images={'analysis':details.analysis.bgr,'gray':details.analysis.gray,
        'blurred':details.analysis.blurred,'contour_overlay':details.overlay}
    trials=[]
    for run in details.trials:
        trial=run.trial;region=isinstance(trial,RegionTrial)
        images[trial.trial_id+'_edges']=trial.edges
        images[trial.trial_id+('_region_mask' if region else '_closed')]=trial.mask if region else trial.closed
        item={'trial_id':trial.trial_id,'method':trial.method,'thresholds':trial.thresholds,
            'gaussian_kernel':trial.gaussian_kernel,'otsu_threshold':trial.otsu_threshold if region else None,
            'support_trial_id':trial.support_trial_id if region else None,'total_contours':run.batch.total_contours,
            'considered_contours':run.batch.considered_contours,'rejection_reason':run.batch.rejection_reason}
        if debug:
            contours={};attempts=[]
            for candidate in run.batch.attempts:
                record=asdict(candidate);contours[str(candidate.contour_index)]=record.pop('contour_px')
                attempts.append(record)
            item|={'contours':contours,'attempts':attempts}
        trials.append(item)
    def description(candidate):
        if candidate is None:return None
        value=asdict(candidate)
        # Full contours are already stored once by trial/index in debug metadata.
        value['candidate'].pop('contour_px')
        return value
    metadata={'run_id':str(run_id),'algorithm_version':details.algorithm_version,'preset':details.preset,
        'source':{'artifact_id':str(source.id),'sha256':source.sha256,'revision':revision,
            'width':source.width,'height':source.height,'bgr_sha256':details.source_bgr_sha256},
        'analysis_size':details.analysis.analysis_size,'overlay_kind':details.overlay_kind,
        'selected_trial_id':details.selected_trial.trial_id if details.selected_trial else None,
        'trials':trials,'result':{'status':result.status,'corners':result.corners,'confirmed':False,
            'heuristic_score':result.heuristic_score,'warnings':result.warnings,
            'selected':description(result.selected),'candidates':[description(c) for c in result.candidates]},
        'units':{'length':'analysis px','turn_angle':'radian','corners':'normalized W-1/H-1',
            'support':'raw Canny Euclidean radius2px; n=max(2,ceil(L/2)+1)'},
        'timings_ms':asdict(result.timings_ms),'debug_persisted':debug,'artifacts':{}}
    return metadata,images if debug else {}


def detect_page(engine:Engine,store:ArtifactStore,sid:UUID,pid:UUID,debug:bool=False)->DetectionRunRead:
    with mutation(engine,sid), repository.transaction(engine) as db:
        if repository.get_session(db,sid) is None:raise SessionNotFoundError()
        page=repository.get_page(db,sid,pid)
        if page is None:raise PageNotFoundError()
        config=repository.get_page_config(db,sid,pid)
        artifact=repository.get_artifact(db,sid,page.normalized_artifact_id)
        if config is None or artifact is None or artifact.page_id!=pid or artifact.kind!='normalized' or artifact.mime!='image/png' or artifact.revision is not None:
            raise SessionDataError('Metadata nguồn không hợp lệ.')
        size=(page.width,page.height);revision=config.revision
        source=StoredArtifact(**{f.name:getattr(artifact,f.name) for f in fields(StoredArtifact)})
    started=perf_counter_ns();pixels=load_normalized_source(store,source,size)
    load_ms=(perf_counter_ns()-started)/1e6
    run_id=uuid4()
    try:
        # One actual call, even when only provenance (without stage PNGs) is requested.
        result=detect_document(pixels,debug=True)
        metadata,images=_describe(result,source,revision,run_id,debug)
        started=perf_counter_ns();encoded={name:encode_stage_png(array) for name,array in images.items()}
        encode_ms=(perf_counter_ns()-started)/1e6
        metadata['timings_ms']={**{f'core.{key}':value for key,value in asdict(result.timings_ms).items()},
            'source_load':load_ms,'encode':encode_ms}
        metadata=json.loads(json.dumps(metadata,allow_nan=False))
    except Exception as error:
        raise DetectionProcessingError('Không tạo được kết quả nhận diện.') from error
    stored=[]
    try:
        with mutation(engine,sid), repository.transaction(engine) as db:
            if not repository.lock_session(db,sid):raise SessionNotFoundError()
            page=repository.get_page(db,sid,pid)
            if page is None:raise PageNotFoundError()
            if page.normalized_artifact_id!=source.id or (page.width,page.height)!=size:
                raise SessionDataError('Nguồn thay đổi trong khi nhận diện.')
            for name,raster in encoded.items():
                record=store.write_bytes(session_id=sid,page_id=pid,kind='debug',revision=revision,
                    mime='image/png',payload=raster.png_bytes,width=raster.width,height=raster.height)
                stored.append(record);repository.register_artifact(db,store,record)
                metadata['artifacts'][name]={'id':str(record.id),'sha256':record.sha256,
                    'width':record.width,'height':record.height,'png_mode':raster.png_mode}
            response=DetectionRunRead(page_id=pid,run_id=run_id,source_artifact_id=source.id,source_revision=revision,
                source_sha256=source.sha256,source_width=size[0],source_height=size[1],status=result.status,
                corners=result.corners,heuristic_score=result.heuristic_score,algorithm_version=metadata['algorithm_version'],
                confirmed=False,warnings=result.warnings,selected_trial_id=metadata['selected_trial_id'],
                stage_artifacts={name:record['id'] for name,record in metadata['artifacts'].items()},
                timings_ms=metadata['timings_ms'])
            db.add(DetectionRun(id=run_id,session_id=sid,page_id=pid,source_artifact_id=source.id,
                source_revision=revision,source_sha256=source.sha256,algorithm_version=metadata['algorithm_version'],metadata_json=metadata))
        return response
    except Exception:
        for record in stored:
            try:
                with repository.transaction(engine) as db:repository.discard_unreferenced(db,store,record)
            except Exception:logger.exception('Cannot clean new detection artifact')
        raise
