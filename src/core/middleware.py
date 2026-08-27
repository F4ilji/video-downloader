from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response


class APIKeyMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, api_key: str | None = None):
        super().__init__(app)
        self.api_key = api_key

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        if not self.api_key:
            return await call_next(request)

        if request.url.path in ("/health", "/api/health"):
            return await call_next(request)

        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
        else:
            token = request.query_params.get("api_key", "")

        if not token:
            return JSONResponse({"detail": "Missing or invalid Authorization header"}, status_code=401)

        if token != self.api_key:
            return JSONResponse({"detail": "Invalid API key"}, status_code=401)

        return await call_next(request)
