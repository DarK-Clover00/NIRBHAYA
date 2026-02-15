"""
Telemetry API endpoints for location ping ingestion
"""
from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import JSONResponse
import logging
from backend.schemas.telemetry import LocationPingRequest, LocationPingResponse
from backend.services.telemetry_service import TelemetryService
from backend.utils.rate_limiter import RateLimiter
from backend.utils.error_handler import (
    create_error_response,
    validate_coordinates,
    CacheError,
    ErrorLogger
)

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize services
telemetry_service = TelemetryService()
rate_limiter = RateLimiter(max_requests=100, window_seconds=60)


@router.post("/ping", response_model=LocationPingResponse, status_code=status.HTTP_200_OK)
async def submit_location_ping(
    request: LocationPingRequest,
    http_request: Request
) -> LocationPingResponse:
    """
    Submit location ping for crowd density tracking
    
    This endpoint receives location data from mobile devices and stores it
    in Redis with geospatial indexing for efficient proximity queries.
    
    **Rate Limit**: 100 requests per minute per device
    
    **Requirements**: 2.1, 2.2, 2.8
    
    Args:
        request: Location ping data including device_id, coordinates, timestamp, and accuracy
        http_request: FastAPI request object for accessing client info
    
    Returns:
        LocationPingResponse with status and next ping interval
    
    Raises:
        HTTPException 429: Rate limit exceeded
        HTTPException 400: Invalid location data
        HTTPException 500: Internal server error
    """
    device_id = request.device_id
    request_id = getattr(http_request.state, "request_id", None)
    
    try:
        # Check rate limit
        is_allowed, retry_after = rate_limiter.is_allowed(device_id)
        
        if not is_allowed:
            logger.warning(
                f"Rate limit exceeded for device {device_id}. "
                f"Retry after {retry_after} seconds"
            )
            return create_error_response(
                code="RATE_LIMIT_EXCEEDED",
                message=f"Rate limit exceeded. Maximum 100 requests per minute allowed.",
                status_code=429,
                details={"retry_after": retry_after},
                request_id=request_id
            )
        
        # Validate coordinates
        is_valid, error_message = validate_coordinates(request.latitude, request.longitude)
        if not is_valid:
            logger.warning(f"Invalid coordinates for device {device_id}: {error_message}")
            return create_error_response(
                code="INVALID_COORDINATES",
                message=error_message,
                status_code=400,
                request_id=request_id
            )
        
        # Store location ping
        result = telemetry_service.store_location_ping(
            device_id=device_id,
            latitude=request.latitude,
            longitude=request.longitude,
            timestamp=request.timestamp,
            accuracy=request.accuracy
        )
        
        logger.info(
            f"Location ping submitted successfully for device {device_id} "
            f"at ({request.latitude}, {request.longitude})"
        )
        
        return LocationPingResponse(
            status=result["status"],
            next_ping_interval=result["next_ping_interval"]
        )
        
    except ValueError as e:
        # Invalid coordinates or validation error
        ErrorLogger.log_error(e, context={"device_id": device_id})
        return create_error_response(
            code="INVALID_LOCATION_DATA",
            message=str(e),
            status_code=400,
            request_id=request_id
        )
    
    except CacheError as e:
        # Redis error
        ErrorLogger.log_error(e, context={"device_id": device_id}, severity="ERROR")
        return create_error_response(
            code="CACHE_ERROR",
            message="Failed to store location ping. Please try again.",
            status_code=500,
            request_id=request_id
        )
    
    except Exception as e:
        # Internal server error
        ErrorLogger.log_error(e, context={"device_id": device_id}, severity="CRITICAL")
        return create_error_response(
            code="INTERNAL_SERVER_ERROR",
            message="Failed to process location ping",
            status_code=500,
            request_id=request_id
        )


@router.get("/health")
async def telemetry_health():
    """
    Health check endpoint for telemetry service
    
    Returns:
        Service health status
    """
    try:
        # Test Redis connection
        from backend.redis_client import ping_redis
        redis_healthy = await ping_redis()
        
        return {
            "service": "telemetry",
            "status": "healthy" if redis_healthy else "degraded",
            "redis": "connected" if redis_healthy else "disconnected"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "service": "telemetry",
            "status": "unhealthy",
            "error": str(e)
        }
