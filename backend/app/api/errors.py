"""One sanitized envelope across request, lookup and internal failures."""
import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException

from ..schemas.errors import ErrorBody, ErrorEnvelope
from ..services.sessions import PageOrderError, SessionDataError, SessionNotFoundError
from ..services.session_guards import SessionBusyError
from ..services.exports import PageNotRenderedError,ExportProcessingError
from ..services.processing_executor import ProcessingBusyError
from ..services.imports import PageLimitError
from ..services.page_config import PageNotFoundError, RevisionConflictError
from ..services.detection import DetectionProcessingError
from ..services.debug import DebugNotFoundError
from ..services.renders import PageNotConfirmedError, RenderProcessingError
from ..processing.config import ConfigValidationError
from ..processing.geometry import GeometryValidationError
from ..processing.normalize import ImageValidationError
from ..storage.files import ArtifactFileError

logger = logging.getLogger(__name__)


def error_response(status: int, code: str, message: str, headers=None, details=None) -> JSONResponse:
    envelope = ErrorEnvelope(error=ErrorBody(code=code,message=message,details=details or {}))
    return JSONResponse(status_code=status,content=envelope.model_dump(mode='json'),headers=headers)


def install_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(ExportProcessingError)
    async def export_failed(request:Request,error):
        logger.error('Export encoding failed',exc_info=error)
        return error_response(500,'PROCESSING_FAILED','Không tạo được tệp xuất; dữ liệu đã lưu được giữ lại.')

    @app.exception_handler(PageNotRenderedError)
    async def page_not_rendered(request:Request,error):
        return error_response(409,'PAGE_NOT_RENDERED',str(error),
            details={'pages':[page.model_dump(mode='json') for page in error.pages]})

    @app.exception_handler(SessionBusyError)
    async def session_busy(request:Request,error):
        return error_response(409,'SESSION_BUSY','Tài liệu đang xuất; chờ hoàn tất rồi thử lại.')

    @app.exception_handler(PageOrderError)
    async def invalid_order(request:Request,error):
        return error_response(400,'INVALID_PAGE_ORDER','Thứ tự phải chứa đủ các trang của tài liệu, không trùng hoặc thừa ID.')

    @app.exception_handler(DebugNotFoundError)
    async def debug_missing(request:Request,error):
        return error_response(404,'DEBUG_NOT_FOUND','Không tìm thấy lượt xử lý hoặc revision đã yêu cầu.')

    @app.exception_handler(DetectionProcessingError)
    async def detection_failed(request:Request,error):
        logger.error('Page detection failed',exc_info=error)
        return error_response(500,'PROCESSING_FAILED','Không thể nhận diện vùng tài liệu.')

    @app.exception_handler(PageNotConfirmedError)
    async def page_not_confirmed(request: Request, error):
        return error_response(409,'PAGE_NOT_CONFIRMED','Cần xác nhận bốn góc trước khi render.')

    @app.exception_handler(RenderProcessingError)
    async def processing_failed(request: Request, error):
        logger.error('Page render processing failed',exc_info=error)
        return error_response(500,'PROCESSING_FAILED','Không thể xử lý ảnh với cấu hình đã lưu.')

    @app.exception_handler(PageNotFoundError)
    async def page_not_found(request: Request, error):
        return error_response(404,'PAGE_NOT_FOUND','Không tìm thấy trang.')

    @app.exception_handler(RevisionConflictError)
    async def revision_conflict(request: Request, error: RevisionConflictError):
        return error_response(409,'REVISION_CONFLICT',str(error),details={
            'expected_revision':error.expected_revision,'actual_revision':error.actual_revision})

    @app.exception_handler(ConfigValidationError)
    async def invalid_config(request: Request, error):
        return error_response(400,'INVALID_CONFIG','Cấu hình không hợp lệ.')

    @app.exception_handler(GeometryValidationError)
    async def invalid_quad(request: Request, error):
        return error_response(400,'INVALID_QUAD','Bốn góc không hợp lệ.')

    @app.exception_handler(ImageValidationError)
    async def invalid_image(request: Request, error: ImageValidationError):
        if error.code in ('UNSUPPORTED_FORMAT','MULTI_FRAME_IMAGE'):
            return error_response(415,'UNSUPPORTED_IMAGE','Chỉ hỗ trợ ảnh JPEG/PNG tĩnh hợp lệ.')
        status = 413 if error.code in ('FILE_TOO_LARGE','TOO_MANY_PIXELS') else 400
        return error_response(status,error.code,str(error))

    @app.exception_handler(PageLimitError)
    async def page_limit(request: Request, error):
        return error_response(413,'PAGE_LIMIT_EXCEEDED','Tài liệu đã đủ 20 trang.')

    @app.exception_handler(ProcessingBusyError)
    async def processing_busy(request: Request, error):
        return error_response(429,'PROCESSING_BUSY','Bộ xử lý đang bận; vui lòng thử lại sau.')

    @app.exception_handler(SessionNotFoundError)
    async def not_found(request: Request, error):
        return error_response(404,'SESSION_NOT_FOUND','Không tìm thấy tài liệu.')

    @app.exception_handler(RequestValidationError)
    async def invalid_request(request: Request, error: RequestValidationError):
        if any(item['loc'][:2]==('path','sid') for item in error.errors()):
            return error_response(404,'SESSION_NOT_FOUND','Không tìm thấy tài liệu.')
        if any(item['loc'][:2]==('path','aid') for item in error.errors()):
            return error_response(404,'ARTIFACT_NOT_FOUND','Không tìm thấy ảnh hoặc tệp.')
        if any(item['loc'][:2]==('path','pid') for item in error.errors()):
            return error_response(404,'PAGE_NOT_FOUND','Không tìm thấy trang.')
        return error_response(400,'INVALID_REQUEST','Yêu cầu không hợp lệ.')

    @app.exception_handler(HTTPException)
    async def http_error(request: Request, error: HTTPException):
        if error.status_code==404 and 'aid' in request.path_params:
            return error_response(404,'ARTIFACT_NOT_FOUND','Không tìm thấy ảnh hoặc tệp.')
        codes = {404:('NOT_FOUND','Không tìm thấy tài nguyên.'),405:('METHOD_NOT_ALLOWED','Phương thức không hỗ trợ.')}
        fallback = ('INTERNAL_ERROR','Không thể hoàn tất yêu cầu.') if error.status_code>=500 else ('INVALID_REQUEST','Yêu cầu không hợp lệ.')
        code,message = codes.get(error.status_code,fallback)
        return error_response(error.status_code,code,message,headers=error.headers)

    async def storage_error(request: Request, error):
        logger.error('Storage metadata operation failed',exc_info=error)
        return error_response(500,'STORAGE_FAILED','Không thể hoàn tất thao tác lưu trữ.')
    app.add_exception_handler(SQLAlchemyError,storage_error)
    app.add_exception_handler(SessionDataError,storage_error)
    app.add_exception_handler(ArtifactFileError,storage_error)

    @app.exception_handler(Exception)
    async def internal_error(request: Request, error):
        logger.error('Unhandled API error',exc_info=error)
        return error_response(500,'INTERNAL_ERROR','Không thể hoàn tất yêu cầu.')
