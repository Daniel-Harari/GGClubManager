from fastapi_cache.backends.inmemory import InMemoryBackend
import time


class InMemoryCache(InMemoryBackend):
    async def cleanup_expired(self):
        current_time = int(time.time())
        expired_keys = [
            key for key, value in self._store.items()
            if value.ttl_ts < current_time
        ]

        async with self._lock:
            for key in expired_keys:
                try:
                    del self._store[key]
                except KeyError:
                    pass

