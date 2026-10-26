"""Export one immutable revision snapshot through the shared bounded worker."""
from fastapi import APIRouter,Request
from pydantic import UUID4
from ..schemas.exports import ExportRequest,ExportRead
from ..schemas.errors import ErrorEnvelope
from ..services.exports import run_export,publish_export

router=APIRouter(tags=['exports'],responses={400:{'model':ErrorEnvelope},'4XX':{'model':ErrorEnvelope},500:{'model':ErrorEnvelope}})


@router.post('/sessions/{sid}/exports',status_code=201)
async def export_document(sid:UUID4,body:ExportRequest,request:Request)->ExportRead:
    engine,store=request.app.state.engine,request.app.state.artifacts
    return await run_export(request.app.state.processing,engine,store,sid,body,
        lambda snapshot:publish_export(engine,store,snapshot))
