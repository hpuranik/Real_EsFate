"""Simple in-memory caching layer for performance.

Phase 6 optimization.
Phase 7+: Replace with Redis.
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import hashlib
import json


class CachedValue:
    """A cached value with expiration."""
    def __init__(self, value: Any, ttl_seconds: int = 3600):
        self.value = value
        self.created_at = datetime.now()
        self.ttl = ttl_seconds
    
    def is_expired(self) -> bool:
        """Check if cache entry has expired."""
        age = (datetime.now() - self.created_at).total_seconds()
        return age > self.ttl


class CacheStore:
    """Simple in-memory cache."""
    
    def __init__(self):
        self.cache: Dict[str, CachedValue] = {}
        self.hits = 0
        self.misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired."""
        if key not in self.cache:
            self.misses += 1
            return None
        
        cached = self.cache[key]
        if cached.is_expired():
            del self.cache[key]
            self.misses += 1
            return None
        
        self.hits += 1
        return cached.value
    
    def set(self, key: str, value: Any, ttl_seconds: int = 3600) -> None:
        """Set value in cache."""
        self.cache[key] = CachedValue(value, ttl_seconds)
    
    def delete(self, key: str) -> None:
        """Delete cache entry."""
        if key in self.cache:
            del self.cache[key]
    
    def clear(self) -> None:
        """Clear all cache."""
        self.cache.clear()
    
    def stats(self) -> Dict[str, Any]:
        """Cache statistics."""
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
        return {
            "hits": self.hits,
            "misses": self.misses,
            "total_requests": total_requests,
            "hit_rate_pct": hit_rate,
            "cached_items": len(self.cache),
        }


# Global cache instance
_cache = CacheStore()


def cache_key(prefix: str, **kwargs) -> str:
    """Generate cache key from prefix and kwargs."""
    key_str = f"{prefix}:" + ":".join(f"{k}={v}" for k, v in sorted(kwargs.items()))
    return hashlib.md5(key_str.encode()).hexdigest()


def get_cached(key: str) -> Optional[Any]:
    """Get from global cache."""
    return _cache.get(key)


def set_cached(key: str, value: Any, ttl_seconds: int = 3600) -> None:
    """Set in global cache."""
    _cache.set(key, value, ttl_seconds)


def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics."""
    return _cache.stats()
