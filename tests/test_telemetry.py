"""
Unit tests for telemetry service and API endpoints
"""
import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
from backend.main import app
from backend.services.telemetry_service import TelemetryService
from backend.utils.rate_limiter import RateLimiter

client = TestClient(app)


class TestTelemetryService:
    """Test cases for TelemetryService"""
    
    def test_store_location_ping_success(self, mock_redis):
        """Test successful location ping storage"""
        service = TelemetryService()
        service.redis = mock_redis
        
        result = service.store_location_ping(
            device_id="test-device-123",
            latitude=37.7749,
            longitude=-122.4194,
            timestamp=datetime.now(timezone.utc),
            accuracy=10.5
        )
        
        assert result["status"] == "success"
        assert 30 <= result["next_ping_interval"] <= 60
        
        # Verify GEOADD was called
        mock_redis.geoadd.assert_called_once()
        
        # Verify TTL was set
        mock_redis.setex.assert_called_once()
        
        # Verify metadata was stored
        mock_redis.hset.assert_called_once()
    
    def test_store_location_ping_invalid_latitude(self, mock_redis):
        """Test location ping with invalid latitude"""
        service = TelemetryService()
        service.redis = mock_redis
        
        with pytest.raises(ValueError, match="Invalid latitude"):
            service.store_location_ping(
                device_id="test-device-123",
                latitude=91.0,  # Invalid: > 90
                longitude=-122.4194,
                timestamp=datetime.now(timezone.utc),
                accuracy=10.5
            )
    
    def test_store_location_ping_invalid_longitude(self, mock_redis):
        """Test location ping with invalid longitude"""
        service = TelemetryService()
        service.redis = mock_redis
        
        with pytest.raises(ValueError, match="Invalid longitude"):
            service.store_location_ping(
                device_id="test-device-123",
                latitude=37.7749,
                longitude=-181.0,  # Invalid: < -180
                timestamp=datetime.now(timezone.utc),
                accuracy=10.5
            )
    
    def test_store_location_ping_boundary_values(self, mock_redis):
        """Test location ping with boundary coordinate values"""
        service = TelemetryService()
        service.redis = mock_redis
        
        # Test maximum valid values
        result = service.store_location_ping(
            device_id="test-device-123",
            latitude=90.0,
            longitude=180.0,
            timestamp=datetime.now(timezone.utc),
            accuracy=10.5
        )
        assert result["status"] == "success"
        
        # Test minimum valid values
        result = service.store_location_ping(
            device_id="test-device-123",
            latitude=-90.0,
            longitude=-180.0,
            timestamp=datetime.now(timezone.utc),
            accuracy=10.5
        )
        assert result["status"] == "success"
    
    def test_get_location_ping_success(self, mock_redis):
        """Test retrieving location ping for a device"""
        service = TelemetryService()
        service.redis = mock_redis
        
        # Mock Redis responses
        mock_redis.exists.return_value = True
        mock_redis.geopos.return_value = [(-122.4194, 37.7749)]
        mock_redis.hgetall.return_value = {
            "accuracy": "10.5",
            "timestamp": "2024-01-15T10:30:00Z",
            "latitude": "37.7749",
            "longitude": "-122.4194"
        }
        
        result = service.get_location_ping("test-device-123")
        
        assert result is not None
        assert result["device_id"] == "test-device-123"
        assert result["latitude"] == 37.7749
        assert result["longitude"] == -122.4194
        assert result["accuracy"] == 10.5
    
    def test_get_location_ping_expired(self, mock_redis):
        """Test retrieving expired location ping"""
        service = TelemetryService()
        service.redis = mock_redis
        
        # Mock TTL key doesn't exist (expired)
        mock_redis.exists.return_value = False
        
        result = service.get_location_ping("test-device-123")
        
        assert result is None
    
    def test_get_nearby_devices(self, mock_redis):
        """Test finding nearby devices within radius"""
        service = TelemetryService()
        service.redis = mock_redis
        
        # Mock GEORADIUS response
        mock_redis.georadius.return_value = [
            ("device-1", 25.5, (-122.4194, 37.7749)),
            ("device-2", 45.0, (-122.4200, 37.7750))
        ]
        mock_redis.exists.return_value = True
        
        nearby = service.get_nearby_devices(
            latitude=37.7749,
            longitude=-122.4194,
            radius_meters=50.0
        )
        
        assert len(nearby) == 2
        assert nearby[0]["device_id"] == "device-1"
        assert nearby[0]["distance"] == 25.5
        assert nearby[1]["device_id"] == "device-2"
        assert nearby[1]["distance"] == 45.0
    
    def test_cleanup_expired_pings(self, mock_redis):
        """Test cleanup of expired location pings"""
        service = TelemetryService()
        service.redis = mock_redis
        
        # Mock devices in geospatial set
        mock_redis.zrange.return_value = ["device-1", "device-2", "device-3"]
        
        # Mock TTL checks: device-1 and device-3 expired
        mock_redis.exists.side_effect = [False, True, False]
        
        removed_count = service.cleanup_expired_pings()
        
        assert removed_count == 2
        assert mock_redis.zrem.call_count == 2


class TestRateLimiter:
    """Test cases for RateLimiter"""
    
    def test_rate_limit_allows_requests_under_limit(self, mock_redis):
        """Test that requests under limit are allowed"""
        limiter = RateLimiter(max_requests=100, window_seconds=60)
        limiter.redis = mock_redis
        
        # Mock Redis pipeline
        mock_pipeline = MagicMock()
        mock_pipeline.execute.return_value = [None, 50, None, None]  # 50 requests in window
        mock_redis.pipeline.return_value = mock_pipeline
        
        is_allowed, retry_after = limiter.is_allowed("test-device")
        
        assert is_allowed is True
        assert retry_after is None
    
    def test_rate_limit_blocks_requests_over_limit(self, mock_redis):
        """Test that requests over limit are blocked"""
        limiter = RateLimiter(max_requests=100, window_seconds=60)
        limiter.redis = mock_redis
        
        # Mock Redis pipeline
        mock_pipeline = MagicMock()
        mock_pipeline.execute.return_value = [None, 100, None, None]  # 100 requests (at limit)
        mock_redis.pipeline.return_value = mock_pipeline
        
        # Mock current time for consistent testing
        import time
        current_time = time.time()
        oldest_timestamp = current_time - 30  # 30 seconds ago
        mock_redis.zrange.return_value = [(b"timestamp", oldest_timestamp)]
        
        is_allowed, retry_after = limiter.is_allowed("test-device")
        
        assert is_allowed is False
        assert retry_after is not None
        assert retry_after > 0
        assert retry_after <= 60  # Should be within the window
    
    def test_get_remaining_requests(self, mock_redis):
        """Test getting remaining requests in window"""
        limiter = RateLimiter(max_requests=100, window_seconds=60)
        limiter.redis = mock_redis
        
        # Mock Redis pipeline
        mock_pipeline = MagicMock()
        mock_pipeline.execute.return_value = [None, 75]  # 75 requests used
        mock_redis.pipeline.return_value = mock_pipeline
        
        remaining = limiter.get_remaining("test-device")
        
        assert remaining == 25


class TestTelemetryAPI:
    """Test cases for telemetry API endpoints"""
    
    def test_submit_location_ping_success(self, mock_redis):
        """Test successful location ping submission via API"""
        with patch('backend.api.telemetry.telemetry_service') as mock_service:
            mock_service.store_location_ping.return_value = {
                "status": "success",
                "stored": True,
                "next_ping_interval": 45
            }
            
            with patch('backend.api.telemetry.rate_limiter') as mock_limiter:
                mock_limiter.is_allowed.return_value = (True, None)
                
                response = client.post(
                    "/api/v1/telemetry/ping",
                    json={
                        "device_id": "test-device-123",
                        "latitude": 37.7749,
                        "longitude": -122.4194,
                        "timestamp": "2024-01-15T10:30:00Z",
                        "accuracy": 10.5
                    }
                )
                
                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "success"
                assert data["next_ping_interval"] == 45
    
    def test_submit_location_ping_rate_limited(self, mock_redis):
        """Test location ping submission when rate limited"""
        with patch('backend.api.telemetry.rate_limiter') as mock_limiter:
            mock_limiter.is_allowed.return_value = (False, 30)
            
            response = client.post(
                "/api/v1/telemetry/ping",
                json={
                    "device_id": "test-device-123",
                    "latitude": 37.7749,
                    "longitude": -122.4194,
                    "timestamp": "2024-01-15T10:30:00Z",
                    "accuracy": 10.5
                }
            )
            
            assert response.status_code == 429
            assert "Retry-After" in response.headers
            data = response.json()
            assert data["error"]["code"] == "RATE_LIMIT_EXCEEDED"
    
    def test_submit_location_ping_invalid_latitude(self):
        """Test location ping with invalid latitude"""
        response = client.post(
            "/api/v1/telemetry/ping",
            json={
                "device_id": "test-device-123",
                "latitude": 91.0,  # Invalid
                "longitude": -122.4194,
                "timestamp": "2024-01-15T10:30:00Z",
                "accuracy": 10.5
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_submit_location_ping_invalid_longitude(self):
        """Test location ping with invalid longitude"""
        response = client.post(
            "/api/v1/telemetry/ping",
            json={
                "device_id": "test-device-123",
                "latitude": 37.7749,
                "longitude": -181.0,  # Invalid
                "timestamp": "2024-01-15T10:30:00Z",
                "accuracy": 10.5
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_submit_location_ping_empty_device_id(self):
        """Test location ping with empty device_id"""
        response = client.post(
            "/api/v1/telemetry/ping",
            json={
                "device_id": "",
                "latitude": 37.7749,
                "longitude": -122.4194,
                "timestamp": "2024-01-15T10:30:00Z",
                "accuracy": 10.5
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_submit_location_ping_negative_accuracy(self):
        """Test location ping with negative accuracy"""
        response = client.post(
            "/api/v1/telemetry/ping",
            json={
                "device_id": "test-device-123",
                "latitude": 37.7749,
                "longitude": -122.4194,
                "timestamp": "2024-01-15T10:30:00Z",
                "accuracy": -5.0  # Invalid
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_telemetry_health_endpoint(self):
        """Test telemetry health check endpoint"""
        with patch('backend.redis_client.ping_redis') as mock_ping:
            mock_ping.return_value = True
            
            response = client.get("/api/v1/telemetry/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data["service"] == "telemetry"
            assert data["status"] in ["healthy", "degraded", "unhealthy"]
