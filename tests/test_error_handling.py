"""
Unit tests for error handling scenarios

Tests:
- Network failure handling
- Invalid input handling
- API failure fallbacks
- Resource exhaustion scenarios

Requirements: Error Handling section
"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

# Client-side error handling tests
from mobile.utils.error_handler import (
    ErrorHandler,
    NetworkError,
    GPSError,
    APIError,
    ValidationError,
    RetryConfig,
    ErrorType,
    ErrorSeverity
)

# Server-side error handling tests
from backend.utils.error_handler import (
    with_database_retry,
    with_redis_fallback,
    with_external_api_retry,
    validate_request_data,
    validate_coordinates,
    ResourceMonitor,
    ErrorLogger,
    DatabaseError,
    CacheError,
    ExternalAPIError
)


class TestClientSideErrorHandling:
    """Test client-side error handling"""
    
    def test_error_handler_initialization(self):
        """Test error handler can be initialized"""
        handler = ErrorHandler()
        assert handler is not None
        assert handler.error_counts == {}
        assert handler.last_errors == {}
    
    @pytest.mark.asyncio
    async def test_retry_with_success(self):
        """Test retry logic succeeds on first attempt"""
        handler = ErrorHandler()
        
        async def successful_func():
            return "success"
        
        result = await handler.with_retry(
            successful_func,
            retry_config=RetryConfig(max_retries=3)
        )
        
        assert result == "success"
    
    @pytest.mark.asyncio
    async def test_retry_with_eventual_success(self):
        """Test retry logic succeeds after failures"""
        handler = ErrorHandler()
        attempts = []
        
        async def flaky_func():
            attempts.append(1)
            if len(attempts) < 3:
                raise NetworkError("Connection failed")
            return "success"
        
        result = await handler.with_retry(
            flaky_func,
            retry_config=RetryConfig(max_retries=5, initial_delay=0.01)
        )
        
        assert result == "success"
        assert len(attempts) == 3
    
    @pytest.mark.asyncio
    async def test_retry_with_fallback(self):
        """Test fallback is used when all retries fail"""
        handler = ErrorHandler()
        
        async def failing_func():
            raise NetworkError("Connection failed")
        
        async def fallback_func():
            return "fallback_result"
        
        result = await handler.with_retry(
            failing_func,
            retry_config=RetryConfig(max_retries=2, initial_delay=0.01),
            fallback=fallback_func
        )
        
        assert result == "fallback_result"
    
    @pytest.mark.asyncio
    async def test_retry_without_fallback_raises(self):
        """Test exception is raised when no fallback provided"""
        handler = ErrorHandler()
        
        async def failing_func():
            raise NetworkError("Connection failed")
        
        with pytest.raises(NetworkError):
            await handler.with_retry(
                failing_func,
                retry_config=RetryConfig(max_retries=2, initial_delay=0.01)
            )
    
    def test_handle_network_error(self):
        """Test network error handling"""
        handler = ErrorHandler()
        error = NetworkError("Connection timeout")
        
        message = handler.handle_network_error(error)
        
        assert "Network connection unavailable" in message
        assert ErrorType.NETWORK in handler.error_counts
        assert handler.error_counts[ErrorType.NETWORK] == 1
    
    def test_handle_gps_error_permission_denied(self):
        """Test GPS permission denied error"""
        handler = ErrorHandler()
        error = GPSError("Permission denied")
        
        message = handler.handle_gps_error(error, error_code="PERMISSION_DENIED")
        
        assert "Location permission denied" in message
        assert ErrorType.GPS in handler.error_counts
    
    def test_handle_gps_error_low_accuracy(self):
        """Test GPS low accuracy error"""
        handler = ErrorHandler()
        error = GPSError("Low accuracy")
        
        message = handler.handle_gps_error(error, error_code="LOW_ACCURACY")
        
        assert "GPS accuracy is low" in message
    
    def test_handle_api_error_rate_limit(self):
        """Test API rate limit error"""
        handler = ErrorHandler()
        error = APIError("Rate limit exceeded", status_code=429)
        
        result = handler.handle_api_error(error, status_code=429)
        
        assert result["error"] is True
        assert result["can_retry"] is True
        assert result["status_code"] == 429
        assert "Too many requests" in result["message"]
    
    def test_handle_api_error_server_error(self):
        """Test API server error"""
        handler = ErrorHandler()
        error = APIError("Internal server error", status_code=500)
        
        result = handler.handle_api_error(error, status_code=500)
        
        assert result["error"] is True
        assert result["can_retry"] is True
        assert result["status_code"] == 500
    
    def test_validate_phone_number_valid(self):
        """Test valid phone number validation"""
        handler = ErrorHandler()
        
        is_valid, error = handler.validate_phone_number("+1234567890")
        assert is_valid is True
        assert error is None
        
        is_valid, error = handler.validate_phone_number("1234567890")
        assert is_valid is True
        assert error is None
    
    def test_validate_phone_number_invalid(self):
        """Test invalid phone number validation"""
        handler = ErrorHandler()
        
        # Empty phone
        is_valid, error = handler.validate_phone_number("")
        assert is_valid is False
        assert "required" in error
        
        # Too short
        is_valid, error = handler.validate_phone_number("123")
        assert is_valid is False
        assert "between 10 and 15 digits" in error
        
        # Contains letters
        is_valid, error = handler.validate_phone_number("123abc7890")
        assert is_valid is False
        assert "only digits" in error
    
    def test_validate_coordinates_valid(self):
        """Test valid coordinate validation"""
        handler = ErrorHandler()
        
        is_valid, error = handler.validate_coordinates(37.7749, -122.4194)
        assert is_valid is True
        assert error is None
        
        # Boundary values
        is_valid, error = handler.validate_coordinates(90, 180)
        assert is_valid is True
        
        is_valid, error = handler.validate_coordinates(-90, -180)
        assert is_valid is True
    
    def test_validate_coordinates_invalid(self):
        """Test invalid coordinate validation"""
        handler = ErrorHandler()
        
        # Latitude out of range
        is_valid, error = handler.validate_coordinates(91, 0)
        assert is_valid is False
        assert "Latitude must be between -90 and 90" in error
        
        # Longitude out of range
        is_valid, error = handler.validate_coordinates(0, 181)
        assert is_valid is False
        assert "Longitude must be between -180 and 180" in error
        
        # Invalid type
        is_valid, error = handler.validate_coordinates("invalid", "invalid")
        assert is_valid is False
        assert "valid numbers" in error
    
    def test_validate_required_field(self):
        """Test required field validation"""
        handler = ErrorHandler()
        
        # Valid field
        is_valid, error = handler.validate_required_field("value", "field_name")
        assert is_valid is True
        assert error is None
        
        # Empty string
        is_valid, error = handler.validate_required_field("", "field_name")
        assert is_valid is False
        assert "required" in error
        
        # None value
        is_valid, error = handler.validate_required_field(None, "field_name")
        assert is_valid is False
        assert "required" in error
    
    def test_error_stats_tracking(self):
        """Test error statistics tracking"""
        handler = ErrorHandler()
        
        # Track multiple errors
        handler._track_error(ErrorType.NETWORK, "Error 1")
        handler._track_error(ErrorType.NETWORK, "Error 2")
        handler._track_error(ErrorType.GPS, "Error 3")
        
        stats = handler.get_error_stats()
        
        assert stats["error_counts"]["network"] == 2
        assert stats["error_counts"]["gps"] == 1
        assert "network" in stats["last_errors"]
        assert "gps" in stats["last_errors"]


class TestServerSideErrorHandling:
    """Test server-side error handling"""
    
    def test_validate_request_data_valid(self):
        """Test valid request data validation"""
        data = {"field1": "value1", "field2": "value2"}
        required_fields = ["field1", "field2"]
        
        is_valid, error = validate_request_data(data, required_fields)
        
        assert is_valid is True
        assert error is None
    
    def test_validate_request_data_missing_fields(self):
        """Test request data with missing fields"""
        data = {"field1": "value1"}
        required_fields = ["field1", "field2", "field3"]
        
        is_valid, error = validate_request_data(data, required_fields)
        
        assert is_valid is False
        assert "field2" in error["missing_fields"]
        assert "field3" in error["missing_fields"]
    
    def test_validate_coordinates_server(self):
        """Test server-side coordinate validation"""
        # Valid coordinates
        is_valid, error = validate_coordinates(37.7749, -122.4194)
        assert is_valid is True
        assert error is None
        
        # Invalid latitude
        is_valid, error = validate_coordinates(100, 0)
        assert is_valid is False
        assert "latitude" in error.lower()
        
        # Invalid longitude
        is_valid, error = validate_coordinates(0, 200)
        assert is_valid is False
        assert "longitude" in error.lower()
    
    def test_resource_monitor_initialization(self):
        """Test resource monitor initialization"""
        monitor = ResourceMonitor(
            max_cpu_percent=80.0,
            max_memory_percent=85.0,
            max_connections=50
        )
        
        assert monitor.max_cpu_percent == 80.0
        assert monitor.max_memory_percent == 85.0
        assert monitor.max_connections == 50
        assert monitor.current_connections == 0
    
    def test_resource_monitor_connection_management(self):
        """Test connection pool management"""
        monitor = ResourceMonitor(max_connections=2)
        
        # Acquire connections
        assert monitor.acquire_connection() is True
        assert monitor.current_connections == 1
        
        assert monitor.acquire_connection() is True
        assert monitor.current_connections == 2
        
        # Pool exhausted
        assert monitor.acquire_connection() is False
        assert monitor.current_connections == 2
        
        # Release connection
        monitor.release_connection()
        assert monitor.current_connections == 1
        
        # Can acquire again
        assert monitor.acquire_connection() is True
        assert monitor.current_connections == 2
    
    def test_resource_monitor_check_resources(self):
        """Test resource availability check"""
        monitor = ResourceMonitor(max_connections=2)
        
        # Resources available
        available, message = monitor.check_resources()
        assert available is True
        assert message is None
        
        # Exhaust connections
        monitor.acquire_connection()
        monitor.acquire_connection()
        
        available, message = monitor.check_resources()
        assert available is False
        assert "unavailable" in message
    
    def test_resource_monitor_throttling(self):
        """Test request throttling"""
        monitor = ResourceMonitor()
        
        # Enable throttling
        monitor.enable_throttle(duration_seconds=1)
        
        # Check resources - should be throttled
        available, message = monitor.check_resources()
        assert available is False
        assert "throttled" in message
        
        # Wait for throttle to expire
        import time
        time.sleep(1.1)
        
        # Should be available again
        available, message = monitor.check_resources()
        assert available is True
    
    def test_error_logger_sanitize_pii(self):
        """Test PII sanitization in logs"""
        data = {
            "phone_number": "+1234567890",
            "email": "user@example.com",
            "name": "John Doe",
            "latitude": 37.7749,
            "device_id": "device123"
        }
        
        sanitized = ErrorLogger.sanitize_pii(data)
        
        assert sanitized["phone_number"] == "[REDACTED]"
        assert sanitized["email"] == "[REDACTED]"
        assert sanitized["name"] == "[REDACTED]"
        assert sanitized["latitude"] == 37.7749  # Not PII
        assert sanitized["device_id"] == "device123"  # Not PII
    
    def test_error_logger_sanitize_nested_pii(self):
        """Test PII sanitization in nested structures"""
        data = {
            "user": {
                "phone": "+1234567890",
                "location": {"lat": 37.7749, "lng": -122.4194}
            },
            "contacts": [
                {"name": "Contact 1", "phone": "+9876543210"},
                {"name": "Contact 2", "phone": "+1111111111"}
            ]
        }
        
        sanitized = ErrorLogger.sanitize_pii(data)
        
        assert sanitized["user"]["phone"] == "[REDACTED]"
        assert sanitized["user"]["location"]["lat"] == 37.7749
        assert sanitized["contacts"][0]["name"] == "[REDACTED]"
        assert sanitized["contacts"][0]["phone"] == "[REDACTED]"
    
    @pytest.mark.asyncio
    async def test_with_redis_fallback_success(self):
        """Test Redis operation succeeds"""
        async def redis_func():
            return "redis_result"
        
        async def fallback_func():
            return "fallback_result"
        
        result = await with_redis_fallback(redis_func, fallback_func)
        
        assert result == "redis_result"
    
    @pytest.mark.asyncio
    async def test_with_redis_fallback_uses_fallback(self):
        """Test fallback is used when Redis fails"""
        from redis.exceptions import RedisError
        
        async def redis_func():
            raise RedisError("Connection failed")
        
        async def fallback_func():
            return "fallback_result"
        
        result = await with_redis_fallback(redis_func, fallback_func)
        
        assert result == "fallback_result"
    
    @pytest.mark.asyncio
    async def test_with_external_api_retry_success(self):
        """Test external API call succeeds"""
        async def api_func():
            return {"data": "success"}
        
        result = await with_external_api_retry(
            api_func,
            "TestService",
            max_retries=3
        )
        
        assert result == {"data": "success"}
    
    @pytest.mark.asyncio
    async def test_with_external_api_retry_uses_cache(self):
        """Test cache is used when API fails"""
        async def api_func():
            raise Exception("API unavailable")
        
        async def cache_func():
            return {"data": "cached"}
        
        result = await with_external_api_retry(
            api_func,
            "TestService",
            cache_func=cache_func,
            max_retries=2,
            initial_delay=0.01
        )
        
        assert result == {"data": "cached"}
    
    @pytest.mark.asyncio
    async def test_with_external_api_retry_no_cache_raises(self):
        """Test exception is raised when API fails and no cache"""
        async def api_func():
            raise Exception("API unavailable")
        
        with pytest.raises(ExternalAPIError):
            await with_external_api_retry(
                api_func,
                "TestService",
                max_retries=2,
                initial_delay=0.01
            )


class TestNetworkFailureHandling:
    """Test network failure scenarios"""
    
    @pytest.mark.asyncio
    async def test_location_ping_network_failure(self):
        """Test location ping handles network failure"""
        from mobile.services.location_service import LocationService
        
        failures = []
        
        def on_failure(message):
            failures.append(message)
        
        service = LocationService(
            device_id="test_device",
            on_ping_failure=on_failure
        )
        
        # Update location
        service.update_location(37.7749, -122.4194, 10.0)
        
        # Mock network failure
        with patch.object(service, '_send_ping_to_backend', side_effect=NetworkError("Connection failed")):
            await service._send_ping()
        
        # Should queue ping and notify failure
        assert len(service.offline_queue) > 0
        assert len(failures) > 0


class TestInvalidInputHandling:
    """Test invalid input handling"""
    
    def test_invalid_coordinates_rejected(self):
        """Test invalid coordinates are rejected"""
        handler = ErrorHandler()
        
        # Test various invalid coordinates
        invalid_coords = [
            (91, 0),      # Latitude too high
            (-91, 0),     # Latitude too low
            (0, 181),     # Longitude too high
            (0, -181),    # Longitude too low
            ("abc", 0),   # Invalid type
            (0, "xyz"),   # Invalid type
        ]
        
        for lat, lng in invalid_coords:
            is_valid, error = handler.validate_coordinates(lat, lng)
            assert is_valid is False
            assert error is not None
    
    def test_empty_required_fields_rejected(self):
        """Test empty required fields are rejected"""
        handler = ErrorHandler()
        
        # Test various empty values
        empty_values = ["", "   ", None]
        
        for value in empty_values:
            is_valid, error = handler.validate_required_field(value, "test_field")
            assert is_valid is False
            assert "required" in error


class TestAPIFailureFallbacks:
    """Test API failure fallback scenarios"""
    
    @pytest.mark.asyncio
    async def test_api_failure_uses_cache(self):
        """Test cached data is used when API fails"""
        call_count = []
        
        async def failing_api():
            call_count.append(1)
            raise Exception("API down")
        
        async def cache_fallback():
            return {"cached": True}
        
        result = await with_external_api_retry(
            failing_api,
            "TestAPI",
            cache_func=cache_fallback,
            max_retries=2,
            initial_delay=0.01
        )
        
        assert result == {"cached": True}
        assert len(call_count) == 3  # Initial + 2 retries


class TestResourceExhaustion:
    """Test resource exhaustion scenarios"""
    
    def test_connection_pool_exhaustion(self):
        """Test behavior when connection pool is exhausted"""
        monitor = ResourceMonitor(max_connections=2)
        
        # Exhaust pool
        assert monitor.acquire_connection() is True
        assert monitor.acquire_connection() is True
        assert monitor.acquire_connection() is False
        
        # Check resources
        available, message = monitor.check_resources()
        assert available is False
        assert "unavailable" in message
    
    def test_throttling_on_high_load(self):
        """Test throttling is enabled under high load"""
        monitor = ResourceMonitor()
        
        # Simulate high load
        monitor.enable_throttle(duration_seconds=2)
        
        # Requests should be throttled
        available, message = monitor.check_resources()
        assert available is False
        assert "throttled" in message.lower()
