from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Response
from starlette.types import ASGIApp
from fastapi import status

from consts import ALLOW_METHODS, ALLOW_HEADERS, MAX_AGE, PUBLIC_PATHS


class CORSMiddleware(BaseHTTPMiddleware):
    def __init__(
            self,
            app: ASGIApp,
            allow_origins: list[str] = None,
    ) -> None:
        super().__init__(app)
        self.allow_origins = allow_origins or ["http://localhost:8080"]


    async def dispatch(self, request, call_next):
        origin = request.headers.get('origin')
        if origin and origin not in self.allow_origins:
            return Response(
                status_code=status.HTTP_403_FORBIDDEN,
                content="CORS policy: Origin not allowed")
        if request.method == "OPTIONS":
            response = Response()
        else:
            response = await call_next(request)
        response.headers['Access-Control-Allow-Origin'] = origin or "http://localhost:8080"
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Methods'] = ', '.join(ALLOW_METHODS)
        response.headers['Access-Control-Allow-Headers'] = ', '.join(ALLOW_HEADERS)
        response.headers['Access-Control-Expose-Headers'] = '*'
        response.headers['Access-Control-Max-Age'] = str(MAX_AGE)
        return response


