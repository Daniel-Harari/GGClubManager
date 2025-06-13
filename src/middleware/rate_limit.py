import time

from fastapi_cache import FastAPICache
from jose import jwt
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from consts import PUBLIC_PATHS
from logger import GGLogger
from utils.auth_utils import auth_settings


logger = GGLogger(__name__)

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, auth_requests_per_minute: int = 60, public_requests_per_minute: int = 30):
        super().__init__(app)
        self.auth_requests_per_minute = auth_requests_per_minute
        self.public_requests_per_minute = public_requests_per_minute

    async def _check_rate_limit(self, key: str, limit: int) -> tuple[bool, list, int]:
        cache = FastAPICache.get_backend()
        current_time = int(time.time())
        window_start = current_time - 60

        requests_data = await cache.get(key) or []
        requests_data = [ts for ts in requests_data if ts > window_start]

        is_allowed = len(requests_data) < limit
        if is_allowed:
            requests_data.append(current_time)
            await cache.set(key, requests_data, expire=60)

        return is_allowed, requests_data, current_time

    async def dispatch(self, request, call_next):
        current_time = int(time.time())
        client_ip = request.client.host
        is_public_path = request.url.path in PUBLIC_PATHS
        requests_data = []

        try:
            if is_public_path:
                # IP-based rate limiting for public paths
                rate_limit_key = f"rate_limit:ip:{client_ip}"
                is_allowed, requests_data, _ = await self._check_rate_limit(
                    rate_limit_key,
                    self.public_requests_per_minute
                )

                if not is_allowed:
                    return JSONResponse(
                        status_code=429,
                        content={
                            "detail": "Too many requests. Please try again later.",
                            "requests_remaining": 0,
                            "reset_at": min(requests_data) + 60
                        }
                    )
            else:
                # Username-based rate limiting for authenticated paths
                token = request.headers.get("Authorization")
                if token:
                    token = token.split(" ")[1] if token.startswith("Bearer ") else token
                    try:
                        payload = jwt.decode(
                            token,
                            auth_settings.auth_secret_key,
                            algorithms=[auth_settings.auth_algorithm]
                        )
                        username = payload.get("username")
                        if username:
                            rate_limit_key = f"rate_limit:user:{username}"
                            is_allowed, requests_data, _ = await self._check_rate_limit(
                                rate_limit_key,
                                self.auth_requests_per_minute
                            )

                            if not is_allowed:
                                return JSONResponse(
                                    status_code=429,
                                    content={
                                        "detail": "Rate limit exceeded. Please try again in a minute.",
                                        "requests_remaining": 0,
                                        "reset_at": min(requests_data) + 60
                                    }
                                )
                    except Exception as e:
                        logger.error(f"Rate limiting error: {e}")
                        # Continue processing the request if there's an error with rate limiting

            # Process the request
            response = await call_next(request)

            # Add rate limit headers
            limit = self.public_requests_per_minute if is_public_path else self.auth_requests_per_minute
            response.headers["X-RateLimit-Limit"] = str(limit)
            response.headers["X-RateLimit-Remaining"] = str(limit - len(requests_data))
            response.headers["X-RateLimit-Reset"] = str(current_time + 60)

            return response

        except Exception as e:
            logger.error(f"Unexpected error in rate limiting middleware: {e}")
            return await call_next(request)