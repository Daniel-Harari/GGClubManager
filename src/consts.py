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
    "http://127.0.0.1:8080",
    "http://localhost:8080",
    "http://192.168.1.17:8080",
    "http://sheepit.club"]

ALLOW_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
MAX_AGE = 60 * 60

ALLOW_HEADERS = [
    "Content-Type",
    "Authorization",
    "Accept",
    "Origin",
    "X-Requested-With",
]

MAX_CONTENT_LENGTH = 1024 * 1024 * 10
MAX_HEADER_LENGTH = 1024 * 1024

ACCESS_TOKEN_EXPIRE_MINUTES = 120