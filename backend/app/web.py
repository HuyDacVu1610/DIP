"""Serve only the built entry point/assets, with HTML navigation fallback."""
from pathlib import Path, PurePosixPath

from fastapi import FastAPI, Request
from starlette.exceptions import HTTPException
from starlette.staticfiles import StaticFiles


def install_frontend(app: FastAPI, directory: Path) -> None:
    files = StaticFiles(directory=directory, check_dir=False, follow_symlink=False)
    api_error = app.exception_handlers[HTTPException]

    @app.exception_handler(HTTPException)
    async def frontend_or_api_error(request: Request, error: HTTPException):
        # Intercept only routing 404s. Existing API routes and their 405/Allow
        # behavior keep precedence; no catch-all route shadows them.
        path = request.url.path.lstrip('/')
        parts = path.split('/')
        reserved = {'api', 'data', 'backend', 'frontend', 'experiments', 'docs', 'tasks', 'assets'}
        safe = not any(p.startswith('.') or '\\' in p or ':' in p for p in parts)
        target = None
        if error.status_code == 404 and request.method in ('GET', 'HEAD') and safe:
            if parts[0] == 'assets' and len(parts) > 1:
                target = path
            elif path in ('', 'index.html') or (
                parts[0] not in reserved and not PurePosixPath(path).suffix
                and 'text/html' in request.headers.get('accept', '')
            ):
                target = 'index.html'
        if target is not None:
            try:
                response = await files.get_response(target, request.scope)
                response.headers['X-Content-Type-Options'] = 'nosniff'
                if target == 'index.html':
                    response.headers['Cache-Control'] = 'no-cache'
                return response
            except HTTPException as missing:
                if missing.status_code != 404:
                    return await api_error(request, missing)
        return await api_error(request, error)
