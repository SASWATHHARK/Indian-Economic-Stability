"""In-memory cache for market data and stability (avoid repeated API calls)."""
from datetime import datetime
from typing import Any, Optional
from app.config import settings

# Simple dict cache with TTL
_cache: dict = {}
_cache_ts: dict = {}

def cache_get(key: str, ttl_sec: Optional[int] = None) -> Optional[Any]:
    ttl = ttl_sec or settings.MARKET_CACHE_TTL
    if key not in _cache or key not in _cache_ts:
        return None
    if (datetime.now() - _cache_ts[key]).total_seconds() > ttl:
        del _cache[key]
        del _cache_ts[key]
        return None
    return _cache[key]

def cache_set(key: str, value: Any) -> None:
    _cache[key] = value
    _cache_ts[key] = datetime.now()

def cache_clear(key: Optional[str] = None) -> None:
    global _cache, _cache_ts
    if key is None:
        _cache.clear()
        _cache_ts.clear()
    else:
        _cache.pop(key, None)
        _cache_ts.pop(key, None)

# Alias for dependency
cache = type("Cache", (), {"get": staticmethod(cache_get), "set": staticmethod(cache_set), "clear": staticmethod(cache_clear)})()
