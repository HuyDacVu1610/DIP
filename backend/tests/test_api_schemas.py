"""Public data contracts before routes; source geometry is checked by the core."""
import json
from datetime import UTC, datetime, timedelta, timezone
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.processing.config import ConfigValidationError
from app.schemas.errors import ErrorEnvelope
from app.schemas.pages import ArtifactRead, ConfigRead, ConfigUpdateRequest, DetectRead, PageRead, RenderRequest
from app.schemas.sessions import ExportRequest, PageOrderRequest, SessionCreate, SessionDetail, SessionRead


def session_data():
    return {'id':str(uuid4()),'title':'Bài tập','created_at':'2026-10-17T09:00:00Z',
        'updated_at':'2026-10-17T09:00:00Z'}


def test_session_defaults_uuid_and_utc_round_trip():
    assert SessionCreate().title=='Tài liệu chưa đặt tên'
    assert SessionCreate(title='  Bài tập  ').title=='Bài tập'
    value = session_data()
    value['created_at'] = datetime(2026,10,17,16,tzinfo=timezone(timedelta(hours=7)))
    response = SessionRead.model_validate(value)
    assert response.created_at==datetime(2026,10,17,9,tzinfo=UTC)
    assert json.loads(response.model_dump_json())['created_at'].endswith('Z')
    assert SessionDetail.model_validate(session_data()).pages==()


@pytest.mark.parametrize('value',[{'title':''},{'title':' '*3},{'title':None},{'title':123},
    {'title':'a'*201},{'title':'ok','extra':True}])
def test_bad_session_request_is_rejected(value):
    with pytest.raises(ValidationError):
        SessionCreate.model_validate(value)


@pytest.mark.parametrize('change',[{'id':'not-a-uuid'},{'created_at':'2026-10-17T09:00:00'},
    {'updated_at':None}])
def test_bad_response_ids_and_naive_timestamps_are_rejected(change):
    with pytest.raises(ValidationError):
        SessionRead.model_validate(session_data()|change)


def test_config_replace_defaults_do_not_inherit_old_parameters_and_use_source_dimensions():
    request = ConfigUpdateRequest.model_validate({'expected_revision':2,'config':{'mode':'bw'}})
    result = request.validate_config(source_size=(100,80))
    assert result.mode=='bw' and result.denoise.method=='median' and result.threshold.c==10
    assert result.corners is None and result.confirmed is False
    data = {'expected_revision':2,'config':{'corners':[[0,0],[1,0],[1,1],[0,1]],'confirmed':True}}
    assert ConfigUpdateRequest.model_validate(data).validate_config(source_size=(100,80)).confirmed
    with pytest.raises(ConfigValidationError):
        ConfigUpdateRequest.model_validate(data|{'config':data['config']|{'corners':[[0,0]]}}).validate_config(source_size=(100,80))
    with pytest.raises(ConfigValidationError):
        ConfigUpdateRequest.model_validate({'expected_revision':0,'config':{'mode':'bw'}}).validate_config(
            source_size=(100,80),warp_size=(10,10))


@pytest.mark.parametrize('data',[{'expected_revision':True,'config':{}},
    {'expected_revision':-1,'config':{}},{'config':{}},
    {'expected_revision':0,'config':None},{'expected_revision':0,'config':[]},
    {'expected_revision':0,'config':{},'revision':2}])
def test_invalid_config_envelope_is_rejected(data):
    with pytest.raises(ValidationError):
        ConfigUpdateRequest.model_validate(data)


def test_render_request_and_error_envelope_are_strict_and_serializable():
    assert RenderRequest(expected_revision=0).debug is False
    with pytest.raises(ValidationError):
        RenderRequest(expected_revision=0,debug=1)
    error = ErrorEnvelope.model_validate({'error':{'code':'REVISION_CONFLICT','message':'Tải lại trang.',
        'details':{'expected_revision':0,'actual_revision':1}}})
    assert json.loads(error.model_dump_json())['error']['details']['actual_revision']==1
    assert 'path' not in error.model_dump_json()


def page_data(sid):
    return {'id':str(uuid4()),'session_id':sid,'position':0,'width':100,'height':80,
        'original_artifact_id':str(uuid4()),'normalized_artifact_id':str(uuid4()),
        'thumbnail_artifact_id':str(uuid4()),'revision':0,'effective_config':{
            'corners':[[0,0],[1,0],[1,1],[0,1]],'confirmed':True},
        'created_at':'2026-10-17T09:00:00Z','updated_at':'2026-10-17T09:00:00Z'}


def test_page_response_validates_config_with_its_own_source_dimensions_and_session_membership():
    data = session_data()
    page = PageRead.model_validate(page_data(data['id']))
    detail = SessionDetail.model_validate(data|{'pages':[page]})
    assert detail.pages[0].effective_config.confirmed
    full = json.loads(detail.model_dump_json(warnings='error'))['pages'][0]['effective_config']
    assert 'geometry' in full and full['threshold']['block_size']==31
    config = ConfigRead.model_validate({'page_id':page.id,'revision':0,'effective_config':full,
        'inactive_fields':page.effective_config.inactive_fields},context={'source_size':(100,80)})
    assert config.effective_config==page.effective_config
    with pytest.raises(ValidationError):
        SessionDetail.model_validate(data|{'pages':[PageRead.model_validate(page_data(str(uuid4())))]})
    with pytest.raises(ValidationError):
        PageRead.model_validate(page_data(data['id'])|{'render_revision':1})


def test_export_order_duplicate_and_quota_are_checked_without_reordering():
    ids = [str(uuid4()),str(uuid4())]
    pages = [{'page_id':value,'revision':index} for index,value in enumerate(ids)]
    request = ExportRequest(pages=pages)
    assert [str(p.page_id) for p in request.pages]==ids
    assert [str(p) for p in PageOrderRequest(page_ids=ids).page_ids]==ids
    for bad in ([],pages+pages,[{'page_id':str(uuid4()),'revision':0} for _ in range(21)]):
        with pytest.raises(ValidationError):
            ExportRequest(pages=bad)
    with pytest.raises(ValidationError):
        PageOrderRequest(page_ids=ids+ids)
    assert ExportRequest(pages=pages[:1],format='png').format=='png'
    with pytest.raises(ValidationError):
        ExportRequest(pages=pages,format='png')


def test_artifact_dto_hides_paths_and_detection_dto_never_confirms_or_returns_manual_corners():
    artifact = {'id':str(uuid4()),'kind':'normalized','mime':'image/png','byte_size':20,
        'sha256':'a'*64,'width':100,'height':80,'created_at':'2026-10-17T09:00:00Z'}
    assert ArtifactRead.model_validate(artifact).revision is None
    for change in ({'path':'data/private.png'},{'width':None},{'sha256':'bad'},{'revision':0}):
        with pytest.raises(ValidationError):
            ArtifactRead.model_validate(artifact|change)
    detection = {'page_id':str(uuid4()),'source_width':100,'source_height':80,
        'status':'proposed','corners':[[0,0],[1,0],[1,1],[0,1]],'heuristic_score':.8,
        'algorithm_version':'detect-v1','timings_ms':{'total':0.5}}
    assert DetectRead.model_validate(detection).confirmed is False
    for change in ({'confirmed':True},{'status':'manual_required'},{'timings_ms':{'total':-1}}):
        with pytest.raises(ValidationError):
            DetectRead.model_validate(detection|change)
