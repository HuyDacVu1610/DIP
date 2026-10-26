"""Binary artifacts by UUID only; metadata ownership and exact file verified."""
from dataclasses import fields

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse
from pydantic import UUID4

from ..schemas.errors import ErrorEnvelope
from ..storage.files import StoredArtifact
from ..storage.repository import find_artifact, transaction

router = APIRouter(tags=['artifacts'],responses={404:{'model':ErrorEnvelope},'4XX':{'model':ErrorEnvelope},500:{'model':ErrorEnvelope}})


@router.get('/artifacts/{aid}',response_class=FileResponse,responses={200:{'content':{
    'image/png':{'schema':{'type':'string','format':'binary'}},
    'image/jpeg':{'schema':{'type':'string','format':'binary'}},
    'application/pdf':{'schema':{'type':'string','format':'binary'}}}}})
def read_artifact(aid: UUID4, request: Request):
    with transaction(request.app.state.engine) as db:
        record = find_artifact(db,aid)
        if record is None:
            raise HTTPException(404)
        stored = StoredArtifact(**{field.name:getattr(record,field.name) for field in fields(StoredArtifact)})
    path = request.app.state.artifacts.verify(stored)
    return FileResponse(path,media_type=stored.mime,filename=path.name,content_disposition_type='inline',
        headers={'X-Content-Type-Options':'nosniff','Cache-Control':'private, no-store'})
