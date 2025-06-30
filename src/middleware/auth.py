from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from consts import PUBLIC_PATHS
from gg_exceptions.auth import TokenExpired, AuthNotProvided, AuthenticationError, AuthorizationError
from utils.auth_utils import verify_token


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method == "OPTIONS":
            return await call_next(request)

        if request.url.path in PUBLIC_PATHS:
            return await call_next(request)

        try:
            auth_header = request.headers.get("Authorization")
            verify_token(auth_header)
            return await call_next(request)
        except TokenExpired:
            return JSONResponse(
                status_code=401,
                content={"detail": "Token has expired"},
                headers={"WWW-Authenticate": "Bearer"},
            )
        except AuthNotProvided:
            return JSONResponse(
                status_code=401,
                content={"detail": "Token not provided"}
            )
        except AuthenticationError:
            return JSONResponse(
                status_code=401,
                content={"detail": "Malformed token"},
                headers={"WWW-Authenticate": "Bearer"},
            )
        except AuthorizationError:
            return JSONResponse(
                status_code=403,
                content={"detail": "Not authorized to access this resource"},
            )