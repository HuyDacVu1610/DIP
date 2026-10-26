"""One bounded multipart file, then the existing shared import use case."""
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, Request, Response
from pydantic import UUID4
from starlette.datastructures import UploadFile
from starlette.formparsers import MultiPartException, MultiPartParser
from starlette.concurrency import run_in_threadpool

from ..processing.normalize import ImageValidationError
from ..schemas.errors import ErrorEnvelope
from ..schemas.pages import ConfigRead, ConfigUpdateRequest, DetectRequest, DetectionRunRead, PageRead, RenderRead, RenderRequest
from ..services.detection import detect_page
from ..schemas.pages import DebugQuery,DebugRead
from ..services.debug import read_debug
from ..services.imports import import_page
from ..services.deletions import delete_document_part
from ..services.session_guards import require_mutable
from ..services.page_config import update_page_config
from ..services.renders import render_page
from ..settings import MAX_UPLOAD_BYTES

CHUNK_SIZE = 64*1024
MULTIPART_ALLOWANCE = 64*1024
router = APIRouter(tags=['pages'],responses={400:{'model':ErrorEnvelope},'4XX':{'model':ErrorEnvelope},500:{'model':ErrorEnvelope}})


@router.delete('/sessions/{sid}/pages/{pid}',status_code=204)
def delete_page(sid:UUID4,pid:UUID4,request:Request)->Response:
    delete_document_part(request.app.state.engine,request.app.state.artifacts,sid,pid)
    return Response(status_code=204)


@router.put('/sessions/{sid}/pages/{pid}/config')
def save_config(sid: UUID4, pid: UUID4, body: ConfigUpdateRequest, request: Request) -> ConfigRead:
    return update_page_config(request.app.state.engine,sid,pid,body)


@router.post('/sessions/{sid}/pages/{pid}/detect')
async def detect(sid:UUID4,pid:UUID4,body:DetectRequest,request:Request)->DetectionRunRead:
    await run_in_threadpool(require_mutable,request.app.state.engine,sid)
    return await request.app.state.processing.run(detect_page,request.app.state.engine,
        request.app.state.artifacts,sid,pid,body.debug)


@router.post('/sessions/{sid}/pages/{pid}/render')
async def render(sid: UUID4, pid: UUID4, body: RenderRequest, request: Request) -> RenderRead:
    await run_in_threadpool(require_mutable,request.app.state.engine,sid)
    result = await request.app.state.processing.run(render_page,request.app.state.engine,
        request.app.state.artifacts,sid,pid,body.expected_revision,body.debug)
    return result


@router.get('/sessions/{sid}/pages/{pid}/debug')
def debug_page(sid:UUID4,pid:UUID4,query:Annotated[DebugQuery,Query()],request:Request)->DebugRead:
    return read_debug(request.app.state.engine,request.app.state.artifacts,sid,pid,query)


class UploadBodyTooLarge(MultiPartException):
    pass


class ImageUploadParser(MultiPartParser):
    finished = False

    def on_end(self) -> None:
        self.finished = True

@router.post('/sessions/{sid}/pages',status_code=201,openapi_extra={
    'requestBody':{'required':True,'content':{'multipart/form-data':{'schema':{
        'type':'object','required':['file'],'additionalProperties':False,
        'properties':{'file':{'type':'string','format':'binary'}}}}}}})
async def upload_page(sid: UUID4, request: Request) -> PageRead:
    await run_in_threadpool(require_mutable,request.app.state.engine,sid)
    if request.headers.get('content-type','').split(';',1)[0].strip().lower()!='multipart/form-data':
        raise HTTPException(400)

    async def bounded_stream():
        total = 0
        async for chunk in request.stream():
            total += len(chunk)
            if total>MAX_UPLOAD_BYTES+MULTIPART_ALLOWANCE:
                raise UploadBodyTooLarge('Upload body too large.')
            yield chunk
        # Raise while inside the parser's guarded loop, so it also closes a
        # partial file which has not yet been added to the returned FormData.
        if not parser.finished:
            raise MultiPartException('Incomplete multipart body.')

    try:
        parser = ImageUploadParser(request.headers,bounded_stream(),max_files=1,max_fields=0)
        form = await parser.parse()
    except UploadBodyTooLarge as error:
        raise ImageValidationError('FILE_TOO_LARGE','Tệp ảnh vượt giới hạn 15 MiB.') from error
    except MultiPartException as error:
        raise HTTPException(400) from error
    try:
        parts = form.multi_items()
        if len(parts)!=1 or parts[0][0]!='file' or not isinstance(parts[0][1],UploadFile):
            raise HTTPException(400)
        upload = parts[0][1]
        payload = bytearray()
        while chunk := await upload.read(CHUNK_SIZE):
            if len(payload)+len(chunk)>MAX_UPLOAD_BYTES:
                raise ImageValidationError('FILE_TOO_LARGE','Tệp ảnh vượt giới hạn 15 MiB.')
            payload.extend(chunk)
        # Filename and client MIME never choose a path or certify image content.
        return await request.app.state.processing.run(import_page,request.app.state.engine,
            request.app.state.artifacts,sid,bytes(payload))
    finally:
        await form.close()
