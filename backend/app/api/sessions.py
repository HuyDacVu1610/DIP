"""Only document metadata endpoints; upload and image work arrive later."""
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request, Response
from pydantic import UUID4
from sqlalchemy.engine import Engine

from ..schemas.sessions import PageOrderRequest, SessionCreate, SessionDetail, SessionList, SessionRead, SessionRename
from ..schemas.errors import ErrorEnvelope
from ..services import sessions as service
from ..services.deletions import delete_document_part

router = APIRouter(prefix='/sessions',tags=['sessions'],responses={
    400:{'model':ErrorEnvelope,'description':'Invalid request'},
    '4XX':{'model':ErrorEnvelope,'description':'Client error'},
    500:{'model':ErrorEnvelope,'description':'Storage or internal failure'}})


def get_engine(request: Request) -> Engine:
    return request.app.state.engine


@router.post('',status_code=201)
def create_session(payload: SessionCreate, engine: Annotated[Engine,Depends(get_engine)]) -> SessionRead:
    return service.create_document(engine,payload)


@router.get('')
def list_sessions(engine: Annotated[Engine,Depends(get_engine)],
                  limit: Annotated[int,Query(ge=1,le=100)] = 20,
                  offset: Annotated[int,Query(ge=0)] = 0) -> SessionList:
    return service.list_documents(engine,limit,offset)


@router.get('/{sid}',responses={404:{'model':ErrorEnvelope,'description':'Session not found'}})
def get_session(sid: UUID4, engine: Annotated[Engine,Depends(get_engine)]) -> SessionDetail:
    return service.get_document(engine,sid)


@router.patch('/{sid}',responses={404:{'model':ErrorEnvelope,'description':'Session not found'}})
def rename_session(sid: UUID4, payload: SessionRename, engine: Annotated[Engine,Depends(get_engine)]) -> SessionRead:
    return service.rename_document(engine,sid,payload)


@router.put('/{sid}/page-order',responses={404:{'model':ErrorEnvelope}})
def order_pages(sid:UUID4,payload:PageOrderRequest,engine:Annotated[Engine,Depends(get_engine)])->SessionDetail:
    return service.order_document(engine,sid,payload)


@router.delete('/{sid}',status_code=204,responses={404:{'model':ErrorEnvelope}})
def delete_session(sid:UUID4,request:Request)->Response:
    delete_document_part(request.app.state.engine,request.app.state.artifacts,sid)
    return Response(status_code=204)
