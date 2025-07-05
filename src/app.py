from contextlib import asynccontextmanager
import asyncio

import uvicorn
from fastapi import FastAPI
from fastapi.params import Depends
from fastapi.responses import RedirectResponse
from fastapi_cache import FastAPICache
from starlette.middleware.cors import CORSMiddleware

from consts import CACHE_CLEANUP_INTERVAL, ALLOW_ORIGINS, MAX_CONTENT_LENGTH, \
    MAX_HEADER_LENGTH, ALLOW_METHODS, ALLOW_HEADERS
from logger import GGLogger
from clients.memory_cache import InMemoryCache
from db import Base, engine
from middleware.auth import AuthMiddleware
from middleware.rate_limit import RateLimitMiddleware
from routers.auth import router as auth_router
from routers.transactions import router as transaction_router
from routers.players import router as player_router
from utils.auth_utils import get_current_user
from middleware.request_size_limit import RequestSizeLimitMiddleware

logger = GGLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    cache = InMemoryCache()
    FastAPICache.init(cache, prefix="fastapi-cache")

    async def cleanup_expired_keys():
        while True:
            try:
                logger.info(cache._store.items())
                await asyncio.sleep(CACHE_CLEANUP_INTERVAL)
                await cache.cleanup_expired()
                logger.info("Cache cleanup completed")
            except asyncio.CancelledError:
                logger.info("Cache cleanup task cancelled")
                break
            except Exception as e:
                logger.error(f"Error during cache cleanup: {e}")
                await asyncio.sleep(60)  # Wait a bit before retrying

    cleanup_task = asyncio.create_task(cleanup_expired_keys())

    try:
        yield
    finally:
        cleanup_task.cancel()
        try:
            await cleanup_task
        except asyncio.CancelledError:
            pass


app = FastAPI(lifespan=lifespan)

# Add this before other middleware
app.add_middleware(
    RequestSizeLimitMiddleware,
    max_content_length=MAX_CONTENT_LENGTH,
    max_headers_length=MAX_HEADER_LENGTH,
)
app.add_middleware(AuthMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(CORSMiddleware,
                   allow_origins=ALLOW_ORIGINS,
                   allow_credentials=True,
                   allow_methods=ALLOW_METHODS,
                   allow_headers=ALLOW_HEADERS,
                   expose_headers=["*"]
                   )


app.include_router(auth_router)
app.include_router(transaction_router)
app.include_router(player_router)
Base.metadata.create_all(bind=engine)

@app.get("/keves")
def get_keves(_ = Depends(get_current_user)):
    return {"Keves Name": "David Ha-Antishemi"}

@app.get("/harari")
def get_harari(_ = Depends(get_current_user)):
    return ["top-reg"]

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8081)