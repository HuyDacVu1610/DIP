"""FastAPI entry point; image processing stays in separate modules."""

from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel

from .settings import API_PREFIX, APP_NAME, DATABASE_PATH, FRONTEND_DIST
from .web import install_frontend
from .api.errors import install_error_handlers
from .api.sessions import router as sessions_router
from .api.pages import router as pages_router
from .api.artifacts import router as artifacts_router
from .api.exports import router as exports_router
from .storage.database import initialize_database, open_database
from .storage.files import ArtifactStore
from .services.processing_executor import ProcessingExecutor


class HealthResponse(BaseModel):
    status: Literal["ok"]


async def health() -> HealthResponse:
    """Report API liveness; this does not check storage or image processing."""
    return HealthResponse(status="ok")


def create_app(database_path: Path = DATABASE_PATH, *, frontend_dir: Path | None = FRONTEND_DIST) -> FastAPI:
    @asynccontextmanager
    async def lifespan(application: FastAPI):
        engine = open_database(database_path)
        try:
            initialize_database(engine)
            application.state.engine = engine
            application.state.artifacts = ArtifactStore(Path(database_path).resolve().parent)
            application.state.processing = ProcessingExecutor()
            try:
                yield
            finally:
                # Finish the active use case before disposing its database.
                await application.state.processing.aclose()
        finally:
            engine.dispose()

    application = FastAPI(title=APP_NAME,version='0.1.0',lifespan=lifespan)
    install_error_handlers(application)
    application.include_router(sessions_router,prefix=API_PREFIX)
    application.include_router(pages_router,prefix=API_PREFIX)
    application.include_router(artifacts_router,prefix=API_PREFIX)
    application.include_router(exports_router,prefix=API_PREFIX)
    application.add_api_route(f'{API_PREFIX}/health',health,methods=['GET'],tags=['health'])
    if frontend_dir is not None:
        install_frontend(application, frontend_dir)
    return application


app = create_app()  # no database/file creation until lifespan startup
