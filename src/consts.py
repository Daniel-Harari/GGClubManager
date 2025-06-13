PUBLIC_PATHS = [
    "/docs",
    "/redoc",
    "/auth/login",
    "/auth/register",
    "/openapi.json",
]

CURRENT_USER_CACHE_TTL = 60 * 60
CACHE_CLEANUP_INTERVAL = 60

ALLOW_ORIGINS = [
    "http://localhost:8080",
    "http://sheepit.club"]

ALLOW_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
MAX_AGE = 60 * 60

ALLOW_HEADERS = ["Accept", "Authorization", "Content-Type", "X-Requested-With", "User-Agent"]

MAX_CONTENT_LENGTH = 1024 * 1024
MAX_HEADER_LENGTH = 8 * 1024