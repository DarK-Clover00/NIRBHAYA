"""
Telemetry service for location ping ingestion and processing
"""
import logging
import random
from typing import Dict, Any
from datetime import datetime
from backend.redis_client import get_redis
from backend.config import settings
from backend.utils.error_handler import (
    with_database_retry,
    with_redis_fallback,
    ErrorLogger,
    CacheError
)

logger = logging.getLogger(__name__)


class TelemetryService:
    """
    Service for handling location telemetry data
    Stores location pings in Redis with geospatial indexing
    """
    
    LOCATION_PINGS_KEY = "location_pings"
    
    def __init__(self):
        self.redis = get_redis()
        self.ping_ttl = settings.LOCATION_PING_TTL
    
    def store_location_ping(
        self,
        device_id: str,
        latitude: float,
        longitude: float,
        timestamp: datetime,
        accuracy: float
    ) -> Dict[str, Any]:
        """
        Store location ping in Redis with geospatial indexing
        
        Args:
            device_id: Unique device identifier
            latitude: Latitude coordinate (-90 to 90)
            longitude: Longitude coordinate (-180 to 180)
            timestamp: Timestamp of the location ping
            accuracy: Location accuracy in meters
        
        Returns:
            Dictionary with storage status and next ping interval
        
        Raises:
            ValueError: If coordinates are invalid
            CacheError: If Redis operation fails
        """
        # Validate coordinates
        if not (-90 <= latitude <= 90):
            raise ValueError(f"Invalid latitude: {latitude}. Must be between -90 and 90")
        
        if not (-180 <= longitude <= 180):
            raise ValueError(f"Invalid longitude: {longitude}. Must be between -180 and 180")
        
        try:
            # Store location using GEOADD command
            # GEOADD key longitude latitude member
            result = self.redis.geoadd(
                self.LOCATION_PINGS_KEY,
                (longitude, latitude, device_id)
            )
            
            # Set TTL on individual device entry
            # We use a separate key for TTL tracking since GEOADD doesn't support per-member TTL
            device_ttl_key = f"{self.LOCATION_PINGS_KEY}:ttl:{device_id}"
            self.redis.setex(
                device_ttl_key,
                self.ping_ttl,
                timestamp.isoformat()
            )
            
            # Store additional metadata (accuracy, timestamp) in a hash
            metadata_key = f"{self.LOCATION_PINGS_KEY}:meta:{device_id}"
            self.redis.hset(
                metadata_key,
                mapping={
                    "accuracy": str(accuracy),
                    "timestamp": timestamp.isoformat(),
                    "latitude": str(latitude),
                    "longitude": str(longitude)
                }
            )
            self.redis.expire(metadata_key, self.ping_ttl)
            
            logger.info(
                f"Stored location ping for device {device_id} at ({latitude}, {longitude}) "
                f"with accuracy {accuracy}m"
            )
            
            # Calculate next ping interval (30-60 seconds as per requirements)
            next_interval = random.randint(30, 60)
            
            return {
                "status": "success",
                "stored": result > 0,
                "next_ping_interval": next_interval
            }
            
        except Exception as e:
            # Log error with sanitized data
            ErrorLogger.log_error(
                e,
                context={
                    "device_id": device_id,
                    "latitude": latitude,
                    "longitude": longitude
                }
            )
            raise CacheError(f"Failed to store location ping: {e}")
    
    def get_location_ping(self, device_id: str) -> Dict[str, Any] | None:
        """
        Retrieve location ping for a specific device
        
        Args:
            device_id: Unique device identifier
        
        Returns:
            Dictionary with location data or None if not found/expired
        """
        try:
            # Check if device still has valid TTL
            device_ttl_key = f"{self.LOCATION_PINGS_KEY}:ttl:{device_id}"
            if not self.redis.exists(device_ttl_key):
                return None
            
            # Get position from geospatial set
            position = self.redis.geopos(self.LOCATION_PINGS_KEY, device_id)
            if not position or not position[0]:
                return None
            
            longitude, latitude = position[0]
            
            # Get metadata
            metadata_key = f"{self.LOCATION_PINGS_KEY}:meta:{device_id}"
            metadata = self.redis.hgetall(metadata_key)
            
            if not metadata:
                return None
            
            return {
                "device_id": device_id,
                "latitude": float(latitude),
                "longitude": float(longitude),
                "accuracy": float(metadata.get("accuracy", 0)),
                "timestamp": metadata.get("timestamp")
            }
            
        except Exception as e:
            logger.error(f"Failed to retrieve location ping for device {device_id}: {e}")
            return None
    
    def cleanup_expired_pings(self) -> int:
        """
        Clean up expired location pings from the geospatial set
        This should be called periodically by a background task
        
        Returns:
            Number of expired pings removed
        """
        try:
            # Get all device IDs from the geospatial set
            all_devices = self.redis.zrange(self.LOCATION_PINGS_KEY, 0, -1)
            
            removed_count = 0
            for device_id in all_devices:
                device_ttl_key = f"{self.LOCATION_PINGS_KEY}:ttl:{device_id}"
                
                # If TTL key doesn't exist, the ping has expired
                if not self.redis.exists(device_ttl_key):
                    # Remove from geospatial set
                    self.redis.zrem(self.LOCATION_PINGS_KEY, device_id)
                    
                    # Remove metadata
                    metadata_key = f"{self.LOCATION_PINGS_KEY}:meta:{device_id}"
                    self.redis.delete(metadata_key)
                    
                    removed_count += 1
            
            if removed_count > 0:
                logger.info(f"Cleaned up {removed_count} expired location pings")
            
            return removed_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup expired pings: {e}")
            return 0
    
    def get_nearby_devices(
        self,
        latitude: float,
        longitude: float,
        radius_meters: float
    ) -> list[Dict[str, Any]]:
        """
        Get devices within a specified radius of a location
        
        Args:
            latitude: Center latitude
            longitude: Center longitude
            radius_meters: Search radius in meters
        
        Returns:
            List of nearby devices with their locations and distances
        """
        try:
            # Use GEORADIUS to find nearby devices
            # Returns list of (device_id, distance, coordinates)
            results = self.redis.georadius(
                self.LOCATION_PINGS_KEY,
                longitude,
                latitude,
                radius_meters,
                unit='m',
                withdist=True,
                withcoord=True
            )
            
            nearby_devices = []
            for result in results:
                device_id = result[0]
                distance = result[1]
                coords = result[2]  # (longitude, latitude)
                
                # Check if device ping is still valid (not expired)
                device_ttl_key = f"{self.LOCATION_PINGS_KEY}:ttl:{device_id}"
                if self.redis.exists(device_ttl_key):
                    nearby_devices.append({
                        "device_id": device_id,
                        "distance": distance,
                        "latitude": coords[1],
                        "longitude": coords[0]
                    })
            
            return nearby_devices
            
        except Exception as e:
            logger.error(f"Failed to get nearby devices: {e}")
            return []
