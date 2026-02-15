"""
Client-side error handling utilities for mobile application

Handles:
- Network failures with retry logic
- GPS/location errors gracefully
- API errors with fallbacks
- User input validation with inline errors

Requirements: Error Handling section
"""
import asyncio
import logging
from typing import Optional, Callable, Any, Dict
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class ErrorType(Enum):
    """Error type classification"""
    NETWORK = "network"
    GPS = "gps"
    API = "api"
    VALIDATION = "validation"
    PERMISSION = "permission"
    UNKNOWN = "unknown"


class ErrorSeverity(Enum):
    """Error severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class NetworkError(Exception):
    """Network-related errors"""
    pass


class GPSError(Exception):
    """GPS/Location-related errors"""
    pass


class APIError(Exception):
    """API-related errors"""
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class ValidationError(Exception):
    """Input validation errors"""
    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(message)
        self.field = field


class RetryConfig:
    """Configuration for retry logic"""
    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True
    ):
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter


class ErrorHandler:
    """
    Centralized error handling for mobile client
    
    Provides:
    - Retry logic with exponential backoff
    - Error classification and logging
    - User-friendly error messages
    - Fallback strategies
    """
    
    def __init__(
        self,
        on_error: Optional[Callable[[ErrorType, str, ErrorSeverity], None]] = None
    ):
        """
        Initialize error handler
        
        Args:
            on_error: Callback for error notifications (error_type, message, severity)
        """
        self.on_error = on_error
        self.error_counts = {}
        self.last_errors = {}
    
    async def with_retry(
        self,
        func: Callable,
        *args,
        retry_config: Optional[RetryConfig] = None,
        fallback: Optional[Callable] = None,
        error_type: ErrorType = ErrorType.UNKNOWN,
        **kwargs
    ) -> Any:
        """
        Execute function with retry logic and exponential backoff
        
        Args:
            func: Async function to execute
            *args: Positional arguments for func
            retry_config: Retry configuration
            fallback: Fallback function if all retries fail
            error_type: Type of error for classification
            **kwargs: Keyword arguments for func
        
        Returns:
            Result from func or fallback
        
        Raises:
            Exception: If all retries fail and no fallback provided
        """
        if retry_config is None:
            retry_config = RetryConfig()
        
        last_exception = None
        delay = retry_config.initial_delay
        
        for attempt in range(retry_config.max_retries + 1):
            try:
                result = await func(*args, **kwargs)
                
                # Reset error count on success
                if error_type in self.error_counts:
                    self.error_counts[error_type] = 0
                
                return result
                
            except Exception as e:
                last_exception = e
                
                # Track error
                self._track_error(error_type, str(e))
                
                # Log attempt
                logger.warning(
                    f"Attempt {attempt + 1}/{retry_config.max_retries + 1} failed: {e}"
                )
                
                # If last attempt, break
                if attempt >= retry_config.max_retries:
                    break
                
                # Calculate delay with exponential backoff
                if retry_config.jitter:
                    import random
                    jitter_factor = random.uniform(0.5, 1.5)
                    actual_delay = min(delay * jitter_factor, retry_config.max_delay)
                else:
                    actual_delay = min(delay, retry_config.max_delay)
                
                await asyncio.sleep(actual_delay)
                
                # Increase delay for next attempt
                delay *= retry_config.exponential_base
        
        # All retries failed
        error_message = f"Operation failed after {retry_config.max_retries + 1} attempts: {last_exception}"
        logger.error(error_message)
        
        # Notify error
        if self.on_error:
            self.on_error(error_type, error_message, ErrorSeverity.ERROR)
        
        # Try fallback if provided
        if fallback:
            try:
                logger.info("Attempting fallback strategy")
                return await fallback(*args, **kwargs)
            except Exception as fallback_error:
                logger.error(f"Fallback also failed: {fallback_error}")
        
        # Re-raise last exception
        raise last_exception
    
    def handle_network_error(self, error: Exception) -> str:
        """
        Handle network-related errors
        
        Args:
            error: Network error exception
        
        Returns:
            User-friendly error message
        """
        self._track_error(ErrorType.NETWORK, str(error))
        
        message = "Network connection unavailable. Please check your internet connection."
        
        if self.on_error:
            self.on_error(ErrorType.NETWORK, message, ErrorSeverity.WARNING)
        
        logger.warning(f"Network error: {error}")
        return message
    
    def handle_gps_error(self, error: Exception, error_code: Optional[str] = None) -> str:
        """
        Handle GPS/location errors gracefully
        
        Args:
            error: GPS error exception
            error_code: Specific GPS error code
        
        Returns:
            User-friendly error message
        """
        self._track_error(ErrorType.GPS, str(error))
        
        # Provide specific messages based on error type
        if error_code == "PERMISSION_DENIED":
            message = "Location permission denied. Please enable location access in settings."
            severity = ErrorSeverity.ERROR
        elif error_code == "GPS_UNAVAILABLE":
            message = "GPS is currently unavailable. Please ensure location services are enabled."
            severity = ErrorSeverity.WARNING
        elif error_code == "LOW_ACCURACY":
            message = "GPS accuracy is low. Some features may be degraded."
            severity = ErrorSeverity.INFO
        elif error_code == "TIMEOUT":
            message = "Location request timed out. Retrying..."
            severity = ErrorSeverity.WARNING
        else:
            message = "Unable to determine your location. Please try again."
            severity = ErrorSeverity.WARNING
        
        if self.on_error:
            self.on_error(ErrorType.GPS, message, severity)
        
        logger.warning(f"GPS error ({error_code}): {error}")
        return message
    
    def handle_api_error(
        self,
        error: Exception,
        status_code: Optional[int] = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Handle API errors with fallbacks
        
        Args:
            error: API error exception
            status_code: HTTP status code
            use_cache: Whether to suggest using cached data
        
        Returns:
            Dictionary with error info and fallback suggestions
        """
        self._track_error(ErrorType.API, str(error))
        
        # Classify error by status code
        if status_code == 429:
            message = "Too many requests. Please wait a moment and try again."
            severity = ErrorSeverity.WARNING
            can_retry = True
        elif status_code == 401 or status_code == 403:
            message = "Authentication failed. Please log in again."
            severity = ErrorSeverity.ERROR
            can_retry = False
        elif status_code == 404:
            message = "Requested resource not found."
            severity = ErrorSeverity.WARNING
            can_retry = False
        elif status_code and 500 <= status_code < 600:
            message = "Server error. Please try again later."
            severity = ErrorSeverity.ERROR
            can_retry = True
        else:
            message = "Unable to connect to server. Using cached data if available."
            severity = ErrorSeverity.WARNING
            can_retry = True
        
        if self.on_error:
            self.on_error(ErrorType.API, message, severity)
        
        logger.error(f"API error (status {status_code}): {error}")
        
        return {
            "error": True,
            "message": message,
            "status_code": status_code,
            "can_retry": can_retry,
            "use_cache": use_cache,
            "severity": severity.value
        }
    
    def validate_phone_number(self, phone: str) -> tuple[bool, Optional[str]]:
        """
        Validate phone number format
        
        Args:
            phone: Phone number to validate
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not phone:
            return False, "Phone number is required"
        
        # Remove spaces and dashes
        cleaned = phone.replace(" ", "").replace("-", "")
        
        # Check if starts with + for international format
        if cleaned.startswith("+"):
            cleaned = cleaned[1:]
        
        # Check if all remaining characters are digits
        if not cleaned.isdigit():
            return False, "Phone number must contain only digits"
        
        # Check length (10-15 digits is typical)
        if len(cleaned) < 10 or len(cleaned) > 15:
            return False, "Phone number must be between 10 and 15 digits"
        
        return True, None
    
    def validate_coordinates(
        self,
        latitude: float,
        longitude: float
    ) -> tuple[bool, Optional[str]]:
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
                return False, f"Latitude must be between -90 and 90 (got {lat})"
            
            if not (-180 <= lng <= 180):
                return False, f"Longitude must be between -180 and 180 (got {lng})"
            
            return True, None
            
        except (ValueError, TypeError):
            return False, "Coordinates must be valid numbers"
    
    def validate_required_field(
        self,
        value: Any,
        field_name: str
    ) -> tuple[bool, Optional[str]]:
        """
        Validate required field is not empty
        
        Args:
            value: Field value
            field_name: Name of field for error message
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if value is None or (isinstance(value, str) and not value.strip()):
            return False, f"{field_name} is required"
        
        return True, None
    
    def _track_error(self, error_type: ErrorType, message: str):
        """
        Track error occurrence for monitoring
        
        Args:
            error_type: Type of error
            message: Error message
        """
        # Increment error count
        if error_type not in self.error_counts:
            self.error_counts[error_type] = 0
        self.error_counts[error_type] += 1
        
        # Store last error
        self.last_errors[error_type] = {
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
            "count": self.error_counts[error_type]
        }
    
    def get_error_stats(self) -> Dict[str, Any]:
        """
        Get error statistics
        
        Returns:
            Dictionary with error counts and last errors
        """
        return {
            "error_counts": {k.value: v for k, v in self.error_counts.items()},
            "last_errors": {k.value: v for k, v in self.last_errors.items()}
        }
    
    def reset_error_stats(self):
        """Reset error statistics"""
        self.error_counts.clear()
        self.last_errors.clear()


# Global error handler instance
_global_error_handler: Optional[ErrorHandler] = None


def get_error_handler() -> ErrorHandler:
    """Get global error handler instance"""
    global _global_error_handler
    if _global_error_handler is None:
        _global_error_handler = ErrorHandler()
    return _global_error_handler


def set_error_handler(handler: ErrorHandler):
    """Set global error handler instance"""
    global _global_error_handler
    _global_error_handler = handler
