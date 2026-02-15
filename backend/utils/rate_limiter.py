"""
Rate limiting utility using Redis
"""
import time
from typing import Optional
from backend.redis_client import get_redis
from backend.config import settings


class RateLimiter:
    """
    Token bucket rate limiter using Redis
    Implements sliding window rate limiting
    """
    
    def __init__(self, max_requests: int = None, window_seconds: int = 60):
        """
        Initialize rate limiter
        
        Args:
            max_requests: Maximum requests allowed per window (defaults to settings.RATE_LIMIT_PER_MINUTE)
            window_seconds: Time window in seconds (default: 60)
        """
        self.max_requests = max_requests or settings.RATE_LIMIT_PER_MINUTE
        self.window_seconds = window_seconds
        self.redis = get_redis()
    
    def is_allowed(self, key: str) -> tuple[bool, Optional[int]]:
        """
        Check if request is allowed under rate limit
        
        Args:
            key: Unique identifier for the rate limit (e.g., device_id)
        
        Returns:
            Tuple of (is_allowed, retry_after_seconds)
            - is_allowed: True if request is allowed, False if rate limited
            - retry_after_seconds: Seconds to wait before retry (None if allowed)
        """
        redis_key = f"rate_limit:{key}"
        current_time = time.time()
        window_start = current_time - self.window_seconds
        
        # Use Redis pipeline for atomic operations
        pipe = self.redis.pipeline()
        
        # Remove old entries outside the window
        pipe.zremrangebyscore(redis_key, 0, window_start)
        
        # Count requests in current window
        pipe.zcard(redis_key)
        
        # Add current request timestamp
        pipe.zadd(redis_key, {str(current_time): current_time})
        
        # Set expiry on the key
        pipe.expire(redis_key, self.window_seconds)
        
        # Execute pipeline
        results = pipe.execute()
        request_count = results[1]  # Count from zcard
        
        # Check if rate limit exceeded
        if request_count >= self.max_requests:
            # Calculate retry after time
            oldest_in_window = self.redis.zrange(redis_key, 0, 0, withscores=True)
            if oldest_in_window:
                oldest_timestamp = oldest_in_window[0][1]
                retry_after = int(oldest_timestamp + self.window_seconds - current_time) + 1
                return False, retry_after
            return False, self.window_seconds
        
        return True, None
    
    def get_remaining(self, key: str) -> int:
        """
        Get remaining requests allowed in current window
        
        Args:
            key: Unique identifier for the rate limit
        
        Returns:
            Number of remaining requests allowed
        """
        redis_key = f"rate_limit:{key}"
        current_time = time.time()
        window_start = current_time - self.window_seconds
        
        # Remove old entries and count
        pipe = self.redis.pipeline()
        pipe.zremrangebyscore(redis_key, 0, window_start)
        pipe.zcard(redis_key)
        results = pipe.execute()
        
        request_count = results[1]
        return max(0, self.max_requests - request_count)
