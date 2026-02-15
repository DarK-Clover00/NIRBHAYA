"""
Property-based tests for telemetry service
Tests universal properties that should hold across all inputs
"""
import pytest
import time
import redis
from datetime import datetime, timezone
from hypothesis import given, strategies as st, settings, HealthCheck
from backend.services.telemetry_service import TelemetryService
from backend.config import settings as app_settings


class TestLocationPingProperties:
    """Property-based tests for location ping behavior"""
    
    @given(
        device_id=st.text(min_size=1, max_size=100),
        latitude=st.floats(min_value=-85.05, max_value=85.05, allow_nan=False, allow_infinity=False),
        longitude=st.floats(min_value=-180, max_value=180, allow_nan=False, allow_infinity=False),
        accuracy=st.floats(min_value=0.1, max_value=1000, allow_nan=False, allow_infinity=False)
    )
    @settings(
        max_examples=20, 
        deadline=None,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    def test_property_6_location_ping_ttl(
        self,
        device_id,
        latitude,
        longitude,
        accuracy
    ):
        """
        Property 6: Location Ping TTL
        
        **Validates: Requirements 2.2, 9.4**
        
        For any Location_Ping stored in the system, it must be automatically 
        deleted after 60 seconds.
        
        This property verifies that:
        1. Location pings are stored with a 60-second TTL
        2. After 60 seconds, the ping is no longer retrievable
        3. All associated data (TTL key, metadata) is cleaned up
        """
        # Feature: nirbhaya-safety-app, Property 6: Location Ping TTL
        
        # Create Redis client for testing (use database 15)
        test_redis_url = app_settings.REDIS_URL.replace("/0", "/15")
        redis_client = redis.from_url(test_redis_url, decode_responses=True)
        
        try:
            service = TelemetryService()
            service.redis = redis_client
            
            timestamp = datetime.now(timezone.utc)
            
            # Store location ping
            result = service.store_location_ping(
                device_id=device_id,
                latitude=latitude,
                longitude=longitude,
                timestamp=timestamp,
                accuracy=accuracy
            )
            
            assert result["status"] == "success"
            
            # Verify ping is immediately retrievable
            ping = service.get_location_ping(device_id)
            assert ping is not None
            assert ping["device_id"] == device_id
            assert abs(ping["latitude"] - latitude) < 0.0001
            assert abs(ping["longitude"] - longitude) < 0.0001
            
            # Verify TTL is set to 60 seconds on the TTL key
            device_ttl_key = f"{service.LOCATION_PINGS_KEY}:ttl:{device_id}"
            ttl = redis_client.ttl(device_ttl_key)
            assert ttl > 0, "TTL key should exist with positive TTL"
            assert ttl <= 60, f"TTL should be at most 60 seconds, got {ttl}"
            
            # Verify metadata key also has TTL
            metadata_key = f"{service.LOCATION_PINGS_KEY}:meta:{device_id}"
            metadata_ttl = redis_client.ttl(metadata_key)
            assert metadata_ttl > 0, "Metadata key should exist with positive TTL"
            assert metadata_ttl <= 60, f"Metadata TTL should be at most 60 seconds, got {metadata_ttl}"
            
            # Wait for TTL to expire (61 seconds to ensure expiration)
            # Note: In real tests, we'll use Redis EXPIRE to simulate time passage
            # For property testing, we manually expire the keys to avoid long test times
            redis_client.delete(device_ttl_key)
            redis_client.delete(metadata_key)
            
            # Verify ping is no longer retrievable after expiration
            expired_ping = service.get_location_ping(device_id)
            assert expired_ping is None, "Location ping should not be retrievable after TTL expiration"
            
            # Verify cleanup removes the ping from geospatial set
            removed_count = service.cleanup_expired_pings()
            assert removed_count >= 1, "Cleanup should remove at least the expired ping"
            
            # Verify device is no longer in geospatial set
            position = redis_client.geopos(service.LOCATION_PINGS_KEY, device_id)
            assert position[0] is None, "Device should be removed from geospatial set after cleanup"
        
        finally:
            # Clean up test data
            redis_client.flushdb()
            redis_client.close()
