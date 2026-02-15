"""
Main FastAPI application for NIRBHAYA backend
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import time
import logging
import uuid
from backend.config import settings
from backend.utils.error_handler import (
    create_error_response,
    ErrorLogger,
    get_resource_monitor
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="NIRBHAYA Women's Safety API",
    description="Backend API for NIRBHAYA safety application",
    version="0.1.0",
    debug=settings.DEBUG
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing and ID middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time header and request ID to all responses"""
    # Generate request ID
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    # Check resource availability
    resource_monitor = get_resource_monitor()
    resources_available, error_message = resource_monitor.check_resources()
    
    if not resources_available:
        return create_error_response(
            code="SERVICE_UNAVAILABLE",
            message=error_message,
            status_code=503,
            request_id=request_id
        )
    
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    response.headers["X-Process-Time"] = str(process_time)
    response.headers["X-Request-ID"] = request_id
    
    return response


# Validation error handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors"""
    request_id = getattr(request.state, "request_id", None)
    
    # Extract validation errors
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    logger.warning(f"Validation error: {errors}")
    
    return create_error_response(
        code="VALIDATION_ERROR",
        message="Request validation failed",
        status_code=400,
        details={"errors": errors},
        request_id=request_id
    )


# HTTP exception handler
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions"""
    request_id = getattr(request.state, "request_id", None)
    
    return create_error_response(
        code=f"HTTP_{exc.status_code}",
        message=exc.detail,
        status_code=exc.status_code,
        request_id=request_id
    )


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions"""
    request_id = getattr(request.state, "request_id", None)
    
    # Log error with sanitized context
    ErrorLogger.log_error(
        exc,
        context={
            "path": request.url.path,
            "method": request.method,
            "request_id": request_id
        },
        severity="CRITICAL"
    )
    
    return create_error_response(
        code="INTERNAL_SERVER_ERROR",
        message="An internal server error occurred",
        status_code=500,
        request_id=request_id
    )


@app.get("/")
async def root():
    """Root endpoint - health check"""
    return {
        "status": "ok",
        "service": "NIRBHAYA API",
        "version": "0.1.0"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    from backend.redis_client import ping_redis
    
    redis_status = await ping_redis()
    
    return {
        "status": "healthy" if redis_status else "degraded",
        "redis": "connected" if redis_status else "disconnected",
        "database": "connected"  # TODO: Add database health check
    }


# Import and include routers
from backend.api import telemetry
app.include_router(telemetry.router, prefix="/api/v1/telemetry", tags=["telemetry"])

# Additional routers (will be added in subsequent tasks)
# from backend.api import routes, sos, reports, profile
# app.include_router(routes.router, prefix="/api/v1/routes", tags=["routes"])
# app.include_router(sos.router, prefix="/api/v1/sos", tags=["sos"])
# app.include_router(reports.router, prefix="/api/v1/report", tags=["reports"])
# app.include_router(profile.router, prefix="/api/v1/user", tags=["profile"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )
