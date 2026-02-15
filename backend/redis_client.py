"""
Redis client configuration for geospatial indexing and caching
"""
import redis
from redis.connection import ConnectionPool
from backend.config import settings

# Create Redis connection pool
redis_pool = ConnectionPool.from_url(
    settings.REDIS_URL,
    max_connections=settings.REDIS_MAX_CONNECTIONS,
    decode_responses=True
)

# Create Redis client
redis_client = redis.Redis(connection_pool=redis_pool)


def get_redis():
    """
    Get Redis client instance
    Returns the global Redis client
    """
    return redis_client


async def ping_redis():
    """
    Check Redis connection health
    Returns True if Redis is accessible, False otherwise
    """
    try:
        return redis_client.ping()
    except redis.ConnectionError:
        return False
