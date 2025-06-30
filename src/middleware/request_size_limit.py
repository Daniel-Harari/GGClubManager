from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from fastapi import Request
import logging

logger = logging.getLogger(__name__)

class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        max_content_length: int = 1024 * 1024,  # 1MB default
        max_headers_length: int = 1024 * 8,          # 8KB default
    ):
        super().__init__(app)
        self.max_content_length = max_content_length
        self.max_headers_length = max_headers_length

    async def dispatch(self, request: Request, call_next):
        # Check headers size
        headers_length = len(str(request.headers))
        if headers_length > self.max_headers_length:
            logger.warning(f"Request headers too large: {headers_length} bytes")
            return JSONResponse(
                status_code=431,  # Request Header Fields Too Large
                content={
                    "detail": "Request header too large",
                    "max_size": self.max_headers_length
                }
            )

        # Check Content-Length header for POST/PUT/PATCH requests
        if request.method in ["POST", "PUT", "PATCH"]:
            content_length = request.headers.get("content-length")
            if content_length:
                content_length = int(content_length)
                if content_length > self.max_content_length:
                    logger.warning(f"Request content too large: {content_length} bytes")
                    return JSONResponse(
                        status_code=413,  # Payload Too Large
                        content={
                            "detail": "Request body too large",
                            "max_size": self.max_content_length
                        }
                    )

        try:
            # If we get here, the size checks passed
            response = await call_next(request)
            return response

        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error"}
            )