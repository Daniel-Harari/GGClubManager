from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from starlette.types import ASGIApp, Receive, Scope, Send


class CorsMiddleware(CORSMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        allow_origins: List[str] = None,
        allow_methods: List[str] = None,
        allow_headers: List[str] = None,
        expose_headers: List[str] = None,
        max_age: int = 600
    ) -> None:
        if allow_origins is None:
            allow_origins = ["*"]
        if allow_methods is None:
            allow_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
        if allow_headers is None:
            allow_headers = ["Authorization", "Content-Type"]
        if expose_headers is None:
            expose_headers = ["Content-Length"]

        super().__init__(
            app=app,
            allow_origins=allow_origins,
            allow_credentials=True,
            allow_methods=allow_methods,
            allow_headers=allow_headers,
            expose_headers=expose_headers,
            max_age=max_age
        )

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":  # Skip non-HTTP requests
            await self.app(scope, receive, send)
            return

        await super().__call__(scope, receive, send)

    async def dispatch(self, request, call_next):
        response = await call_next(request)
        
        # Set CORS headers
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = ", ".join(self.allow_methods)
        response.headers["Access-Control-Allow-Headers"] = ", ".join(self.allow_headers)
        response.headers["Access-Control-Expose-Headers"] = ", ".join(self.expose_headers)
        response.headers["Access-Control-Max-Age"] = str(self.max_age)

        return response