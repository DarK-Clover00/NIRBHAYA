"""
Server-side error handling utilities

Handles:
- Database errors with retries
- Redis failures with database fallback
- External API errors with caching
- Validation error responses
- Resource exhaustion gracefully

Requirements: Error Handling section
"""
import asyncio
import logging
import time
import random
from typing import Optional, Callable, Any, Dict, Type
from functools import wraps
from datetime import datetime
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
import psycopg2
from redis.exceptions import RedisError

logger = logging.getLogger(__name__)


class DatabaseError(Exception):
    """Database-related errors"""
    pass


class CacheError(Exception):
    """Cache/Redis-related errors"""
    pass


class ExternalAPIError(Exception):
    """External API errors"""
    def __init__(self, message: str, service: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.service = service
        self.status_code = status_code


class ResourceExhaustedError(Exception):
    """Resource exhaustion errors"""
    pass


def create_error_response(
    code: str,
    message: str,
    status_code: int = 500,
    details: Optional[Dict] = None,
    request_id: Optional[str] = None
) -> JSONResponse:
    """
    Create standardized error response
    
    Args:
        code: Error code
        message: Human-readable error message
        status_code: HTTP status code
        details: Additional error details
        request_id: Request ID for tracing
    
    Returns:
        JSONResponse with error information
    """
    error_data = {
        "error": {
            "code": code,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
    }
    
    if details:
        error_data["error"]["details"] = details
    
    if request_id:
        error_data["error"]["request_id"] = request_id
    
    return JSONResponse(
        status_code=status_code,
        content=error_data
    )


def with_database_retry(
    max_retries: int = 3,
    initial_delay: float = 0.1,
    max_delay: float = 2.0,
    exponential_base: float = 2.0
):
    """
    Decorator for database operations with retry logic
    
    Handles:
    - Connection failures
    - Deadlocks
    - Temporary errors
    
    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay between retries (seconds)
        max_delay: Maximum delay between retries (seconds)
        exponential_base: Base for exponential backoff
    
    Returns:
        Decorated function with retry logic
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            delay = initial_delay
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                    
                except psycopg2.OperationalError as e:
                    # Connection error - retry
                    last_exception = e
                    logger.warning(
                        f"Database connection error (attempt {attempt + 1}/{max_retries + 1}): {e}"
                    )
                    
                except psycopg2.extensions.TransactionRollbackError as e:
                    # Deadlock - retry with random jitter
                    last_exception = e
                    logger.warning(
                        f"Database deadlock detected (attempt {attempt + 1}/{max_retries + 1}): {e}"
                    )
                    # Add random jitter to avoid thundering herd
                    jitter = random.uniform(0, delay * 0.5)
                    delay += jitter
                    
                except Exception as e:
                    # Other errors - don't retry
                    logger.error(f"Database error (non-retryable): {e}", exc_info=True)
                    raise
                
                # If not last attempt, wait before retry
                if attempt < max_retries:
                    await asyncio.sleep(min(delay, max_delay))
                    delay *= exponential_base
            
            # All retries failed
            logger.error(
                f"Database operation failed after {max_retries + 1} attempts: {last_exception}"
            )
            raise DatabaseError(f"Database operation failed: {last_exception}")
        
        return wrapper
    return decorator


async def with_redis_fallback(
    redis_func: Callable,
    fallback_func: Callable,
    *args,
    **kwargs
) -> Any:
    """
    Execute Redis operation with database fallback
    
    Args:
        redis_func: Redis operation function
        fallback_func: Fallback function (usually database query)
        *args: Arguments for functions
        **kwargs: Keyword arguments for functions
    
    Returns:
        Result from redis_func or fallback_func
    """
    try:
        result = await redis_func(*args, **kwargs)
        return result
        
    except RedisError as e:
        logger.warning(f"Redis error, falling back to database: {e}")
        
        try:
            result = await fallback_func(*args, **kwargs)
            logger.info("Successfully used database fallback")
            return result
            
        except Exception as fallback_error:
            logger.error(f"Fallback also failed: {fallback_error}", exc_info=True)
            raise CacheError(f"Both Redis and fallback failed: {e}, {fallback_error}")
    
    except Exception as e:
        logger.error(f"Unexpected error in Redis operation: {e}", exc_info=True)
        raise


async def with_external_api_retry(
    api_func: Callable,
    service_name: str,
    cache_func: Optional[Callable] = None,
    max_retries: int = 3,
    initial_delay: float = 1.0,
    *args,
    **kwargs
) -> Any:
    """
    Execute external API call with retry and caching fallback
    
    Args:
        api_func: API call function
        service_name: Name of external service
        cache_func: Function to retrieve cached data
        max_retries: Maximum retry attempts
        initial_delay: Initial delay between retries
        *args: Arguments for api_func
        **kwargs: Keyword arguments for api_func
    
    Returns:
        Result from api_func or cache_func
    """
    last_exception = None
    delay = initial_delay
    
    for attempt in range(max_retries + 1):
        try:
            result = await api_func(*args, **kwargs)
            return result
            
        except Exception as e:
            last_exception = e
            logger.warning(
                f"{service_name} API error (attempt {attempt + 1}/{max_retries + 1}): {e}"
            )
            
            # If last attempt, break
            if attempt >= max_retries:
                break
            
            # Exponential backoff
            await asyncio.sleep(delay)
            delay *= 2
    
    # All retries failed - try cache
    logger.error(f"{service_name} API failed after {max_retries + 1} attempts")
    
    if cache_func:
        try:
            logger.info(f"Attempting to use cached data for {service_name}")
            cached_result = await cache_func(*args, **kwargs)
            
            if cached_result is not None:
                logger.info(f"Successfully retrieved cached data for {service_name}")
                return cached_result
            else:
                logger.warning(f"No cached data available for {service_name}")
                
        except Exception as cache_error:
            logger.error(f"Cache retrieval also failed: {cache_error}")
    
    # No cache or cache failed
    raise ExternalAPIError(
        f"{service_name} API unavailable and no cached data",
        service=service_name
    )


def validate_request_data(data: Dict, required_fields: list[str]) -> tuple[bool, Optional[Dict]]:
    """
    Validate request data for required fields
    
    Args:
        data: Request data dictionary
        required_fields: List of required field names
    
    Returns:
        Tuple of (is_valid, error_details)
    """
    missing_fields = []
    
    for field in required_fields:
        if field not in data or data[field] is None:
            missing_fields.append(field)
    
    if missing_fields:
        return False, {
            "missing_fields": missing_fields,
            "message": f"Missing required fields: {', '.join(missing_fields)}"
        }
    
    return True, None


def validate_coordinates(latitude: float, longitude: float) -> tuple[bool, Optional[str]]:
    """
    Validate geographic coordinates
    
    Args:
        latitude: Latitude value
        longitude: Longitude value
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        lat = float(latitude)
        lng = float(longitude)
        
        if not (-90 <= lat <= 90):
            return False, f"Invalid latitude: {lat}. Must be between -90 and 90"
        
        if not (-180 <= lng <= 180):
            return False, f"Invalid longitude: {lng}. Must be between -180 and 180"
        
        return True, None
        
    except (ValueError, TypeError) as e:
        return False, f"Invalid coordinate format: {e}"


class ResourceMonitor:
    """
    Monitor resource usage and handle exhaustion gracefully
    """
    
    def __init__(
        self,
        max_cpu_percent: float = 90.0,
        max_memory_percent: float = 90.0,
        max_connections: int = 100
    ):
        """
        Initialize resource monitor
        
        Args:
            max_cpu_percent: Maximum CPU usage percentage
            max_memory_percent: Maximum memory usage percentage
            max_connections: Maximum database connections
        """
        self.max_cpu_percent = max_cpu_percent
        self.max_memory_percent = max_memory_percent
        self.max_connections = max_connections
        
        self.current_connections = 0
        self.throttle_until = 0
    
    def check_resources(self) -> tuple[bool, Optional[str]]:
        """
        Check if resources are available
        
        Returns:
            Tuple of (resources_available, error_message)
        """
        # Check if currently throttled
        if time.time() < self.throttle_until:
            remaining = int(self.throttle_until - time.time())
            return False, f"Service temporarily throttled. Retry in {remaining} seconds"
        
        # Check connection pool
        if self.current_connections >= self.max_connections:
            logger.warning("Connection pool exhausted")
            return False, "Service temporarily unavailable. Please try again later"
        
        # TODO: Add actual CPU and memory checks using psutil
        # For now, assume resources are available
        
        return True, None
    
    def acquire_connection(self) -> bool:
        """
        Acquire a connection from pool
        
        Returns:
            True if connection acquired, False otherwise
        """
        if self.current_connections < self.max_connections:
            self.current_connections += 1
            return True
        return False
    
    def release_connection(self):
        """Release a connection back to pool"""
        if self.current_connections > 0:
            self.current_connections -= 1
    
    def enable_throttle(self, duration_seconds: int = 60):
        """
        Enable request throttling
        
        Args:
            duration_seconds: Duration to throttle requests
        """
        self.throttle_until = time.time() + duration_seconds
        logger.warning(f"Request throttling enabled for {duration_seconds} seconds")


# Global resource monitor
_resource_monitor = ResourceMonitor()


def get_resource_monitor() -> ResourceMonitor:
    """Get global resource monitor instance"""
    return _resource_monitor


class ErrorLogger:
    """
    Centralized error logging with PII sanitization
    """
    
    @staticmethod
    def sanitize_pii(data: Any) -> Any:
        """
        Remove PII from data before logging
        
        Args:
            data: Data to sanitize
        
        Returns:
            Sanitized data
        """
        if isinstance(data, dict):
            sanitized = {}
            pii_fields = ['phone_number', 'phone', 'email', 'name', 'address']
            
            for key, value in data.items():
                if key.lower() in pii_fields:
                    sanitized[key] = "[REDACTED]"
                elif isinstance(value, (dict, list)):
                    sanitized[key] = ErrorLogger.sanitize_pii(value)
                else:
                    sanitized[key] = value
            
            return sanitized
            
        elif isinstance(data, list):
            return [ErrorLogger.sanitize_pii(item) for item in data]
        
        return data
    
    @staticmethod
    def log_error(
        error: Exception,
        context: Optional[Dict] = None,
        severity: str = "ERROR"
    ):
        """
        Log error with sanitized context
        
        Args:
            error: Exception to log
            context: Additional context (will be sanitized)
            severity: Log severity level
        """
        sanitized_context = ErrorLogger.sanitize_pii(context) if context else {}
        
        log_level = getattr(logging, severity, logging.ERROR)
        logger.log(
            log_level,
            f"Error: {error}",
            extra={"context": sanitized_context},
            exc_info=True
        )
    
    @staticmethod
    def log_api_error(
        service: str,
        error: Exception,
        request_data: Optional[Dict] = None
    ):
        """
        Log external API error
        
        Args:
            service: Service name
            error: Exception
            request_data: Request data (will be sanitized)
        """
        sanitized_data = ErrorLogger.sanitize_pii(request_data) if request_data else {}
        
        logger.error(
            f"External API error ({service}): {error}",
            extra={"service": service, "request_data": sanitized_data}
        )
