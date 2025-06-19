import os
import redis
from redis import Redis

def get_redis() -> Redis:
    """Get Redis connection."""
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    return redis.from_url(redis_url)

def get_redis_conn() -> Redis:
    """Get Redis connection (alias for get_redis for backward compatibility)."""
    return get_redis()
