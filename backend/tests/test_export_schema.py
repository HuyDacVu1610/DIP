from copy import deepcopy
from uuid import uuid4
import pytest
from pydantic import ValidationError

from app.schemas.exports import ExportRequest, ExportRead
from app.schemas.sessions import ExportRequest as PreviousExportRequest


def payload():
    return {'pages':[{'page_id':str(uuid4()),'revision':3},{'page_id':str(uuid4()),'revision':1}]}


def test_export_is_an_immutable_ordered_subset_contract_and_keeps_previous_import():
    data=payload();before=deepcopy(data);request=ExportRequest.model_validate(data)
    assert PreviousExportRequest is ExportRequest
    assert request.model_dump(mode='json')['pages']==data['pages'] and data==before
    assert (request.format,request.paper_size,request.orientation,request.margin_mm,request.image_encoding)==('pdf','a4','auto',5,'png')
    with pytest.raises(ValidationError):request.format='jpg'
    with pytest.raises(ValidationError):request.pages[0].revision=4


@pytest.mark.parametrize('change',[
    {'pages':[]},{'pages':None},{'format':'zip'},{'format':None},{'paper_size':'letter'},
    {'orientation':'sideways'},{'margin_mm':-1},{'margin_mm':31},{'margin_mm':True},
    {'margin_mm':'5'},{'margin_mm':float('nan')},{'margin_mm':float('inf')},
    {'image_encoding':'jpg'},{'unknown':True},
])
def test_export_rejects_invalid_options_without_coercing(change):
    with pytest.raises(ValidationError):ExportRequest.model_validate(payload()|change)


def test_invalid_pages_and_duplicate_id_even_with_different_revision():
    data=payload();page=data['pages'][0]
    for pages in [[page,page|{'revision':4}],[page]*21,[page|{'revision':True}],
                  [page|{'revision':-1}],[page|{'revision':'3'}],[page|{'path':'private'}],
                  [page|{'page_id':'bad'}],[{'page_id':page['page_id']}]]:
        with pytest.raises(ValidationError):ExportRequest(pages=pages)
    assert len(ExportRequest(pages=[{'page_id':str(uuid4()),'revision':i} for i in range(20)]).pages)==20


@pytest.mark.parametrize('format',['png','jpg'])
def test_images_require_one_page_and_pdf_options_are_retained_inactive(format):
    data=payload()
    with pytest.raises(ValidationError):ExportRequest.model_validate(data|{'format':format})
    request=ExportRequest(pages=data['pages'][:1],format=format,orientation='landscape',margin_mm=30,image_encoding='jpeg')
    assert len(request.pages)==1 and request.orientation=='landscape' and request.margin_mm==30


def test_response_records_only_server_artifact_and_ordered_revision_snapshot():
    request=ExportRequest.model_validate(payload())
    data={'id':str(uuid4()),'session_id':str(uuid4()),'artifact_id':str(uuid4()),'format':'pdf',
          'pages':request.model_dump(mode='json')['pages'],'created_at':'2026-10-18T08:00:00Z'}
    result=ExportRead.model_validate(data)
    assert result.model_dump(mode='json')==data
    with pytest.raises(ValidationError):ExportRead.model_validate(data|{'path':'private.pdf'})
    with pytest.raises(ValidationError):ExportRead.model_validate(data|{'created_at':'2026-10-18T08:00:00'})
