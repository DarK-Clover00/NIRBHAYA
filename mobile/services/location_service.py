"""
Background location service for sending location pings
"""
import asyncio
import random
import time
from typing import Optional, Callable
from datetime import datetime
from ..config import (
    LOCATION_PING_INTERVAL_MIN,
    LOCATION_PING_INTERVAL_MAX,
    API_BASE_URL
)
from ..utils.error_handler import (
    ErrorHandler,
    NetworkError,
    GPSError,
    RetryConfig,
    ErrorType
)


class LocationService:
    """
    Background service for sending location pings every 30-60 seconds.
    Handles online/offline queue management and respects battery optimization.
    
    Requirements: 2.1, 2.8
    """
    
    def __init__(
        self,
        device_id: str,
        on_ping_success: Optional[Callable] = None,
        on_ping_failure: Optional[Callable] = None
    ):
        """
        Initialize location service
        
        Args:
            device_id: Unique device identifier
            on_ping_success: Callback when ping succeeds
            on_ping_failure: Callback when ping fails
        """
        self.device_id = device_id
        self.on_ping_success = on_ping_success
        self.on_ping_failure = on_ping_failure
        
        self.is_running = False
        self.is_enabled = True
        self.current_location = None
        self.ping_task = None
        self.offline_queue = []
        
        # Initialize error handler
        self.error_handler = ErrorHandler(
            on_error=self._handle_error_notification
        )
        
    async def start(self):
        """Start the background location service"""
        if self.is_running:
            return
        
        self.is_running = True
        self.ping_task = asyncio.create_task(self._ping_loop())
    
    async def stop(self):
        """Stop the background location service"""
        self.is_running = False
        if self.ping_task:
            self.ping_task.cancel()
            try:
                await self.ping_task
            except asyncio.CancelledError:
                pass
    
    def enable_location_sharing(self):
        """Enable location sharing - starts sending pings"""
        self.is_enabled = True
    
    def disable_location_sharing(self):
        """
        Disable location sharing - stops sending pings immediately
        
        Requirements: 2.8 - Stop pings when location sharing is disabled
        """
        self.is_enabled = False
    
    def update_location(self, latitude: float, longitude: float, accuracy: float):
        """
        Update current location
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            accuracy: GPS accuracy in meters
        """
        self.current_location = {
            "latitude": latitude,
            "longitude": longitude,
            "accuracy": accuracy,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _ping_loop(self):
        """
        Main loop for sending location pings at 30-60 second intervals
        
        Requirements: 2.1 - Send location pings every 30-60 seconds
        """
        while self.is_running:
            try:
                # Only send ping if location sharing is enabled
                if self.is_enabled and self.current_location:
                    await self._send_ping()
                
                # Random interval between 30-60 seconds
                interval = random.randint(
                    LOCATION_PING_INTERVAL_MIN,
                    LOCATION_PING_INTERVAL_MAX
                )
                await asyncio.sleep(interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                # Log error and continue
                if self.on_ping_failure:
                    self.on_ping_failure(str(e))
                await asyncio.sleep(5)  # Wait before retry
    
    async def _send_ping(self):
        """
        Send location ping to backend with retry logic and error handling
        
        Handles online/offline queue management
        """
        if not self.current_location:
            return
        
        ping_data = {
            "device_id": self.device_id,
            "latitude": self.current_location["latitude"],
            "longitude": self.current_location["longitude"],
            "accuracy": self.current_location["accuracy"],
            "timestamp": self.current_location["timestamp"]
        }
        
        try:
            # Use error handler with retry logic
            success = await self.error_handler.with_retry(
                self._send_ping_to_backend,
                ping_data,
                retry_config=RetryConfig(
                    max_retries=3,
                    initial_delay=1.0,
                    max_delay=8.0
                ),
                error_type=ErrorType.NETWORK
            )
            
            if success:
                if self.on_ping_success:
                    self.on_ping_success(ping_data)
                
                # Process offline queue if any
                await self._process_offline_queue()
            else:
                # Queue for later if offline
                self._queue_ping(ping_data)
                
        except NetworkError as e:
            # Network error - queue ping for later
            self._queue_ping(ping_data)
            self.error_handler.handle_network_error(e)
        except Exception as e:
            # Other errors - queue ping and notify
            self._queue_ping(ping_data)
            if self.on_ping_failure:
                self.on_ping_failure(str(e))
    
    async def _send_ping_to_backend(self, ping_data: dict) -> bool:
        """
        Send ping to backend API
        
        Args:
            ping_data: Location ping data
            
        Returns:
            True if successful, False otherwise
        """
        # TODO: Implement actual HTTP request
        # import aiohttp
        # async with aiohttp.ClientSession() as session:
        #     async with session.post(
        #         f"{API_BASE_URL}/telemetry/ping",
        #         json=ping_data
        #     ) as response:
        #         return response.status == 200
        
        # Simulate success for now
        await asyncio.sleep(0.1)
        return True
    
    def _queue_ping(self, ping_data: dict):
        """
        Queue ping for later when offline
        
        Requirements: 15.2 - Queue location pings when offline
        """
        self.offline_queue.append(ping_data)
        
        # Limit queue size to prevent memory issues
        if len(self.offline_queue) > 100:
            self.offline_queue.pop(0)
    
    async def _process_offline_queue(self):
        """
        Process queued pings when connection is restored
        
        Requirements: 15.7 - Synchronize queued data within 30 seconds
        """
        if not self.offline_queue:
            return
        
        # Process queue with exponential backoff
        retry_count = 0
        max_retries = 3
        
        while self.offline_queue and retry_count < max_retries:
            ping_data = self.offline_queue[0]
            
            try:
                success = await self._send_ping_to_backend(ping_data)
                if success:
                    self.offline_queue.pop(0)
                    retry_count = 0  # Reset on success
                else:
                    retry_count += 1
                    await asyncio.sleep(2 ** retry_count)  # Exponential backoff
                    
            except Exception:
                retry_count += 1
                await asyncio.sleep(2 ** retry_count)
    
    def get_queue_size(self) -> int:
        """Get number of queued pings"""
        return len(self.offline_queue)
    
    def is_location_sharing_enabled(self) -> bool:
        """Check if location sharing is enabled"""
        return self.is_enabled
    
    def _handle_error_notification(self, error_type, message, severity):
        """
        Handle error notifications from error handler
        
        Args:
            error_type: Type of error
            message: Error message
            severity: Error severity
        """
        # Log error
        import logging
        logger = logging.getLogger(__name__)
        logger.log(
            logging.ERROR if severity.value == "error" else logging.WARNING,
            f"[{error_type.value}] {message}"
        )
        
        # Notify callback if provided
        if self.on_ping_failure:
            self.on_ping_failure(message)


class BatteryOptimizer:
    """
    Helper class for battery optimization
    
    Adjusts ping frequency based on battery level and charging state
    """
    
    def __init__(self):
        self.battery_level = 100
        self.is_charging = False
    
    def update_battery_status(self, level: int, is_charging: bool):
        """
        Update battery status
        
        Args:
            level: Battery level (0-100)
            is_charging: Whether device is charging
        """
        self.battery_level = level
        self.is_charging = is_charging
    
    def get_recommended_interval(self) -> int:
        """
        Get recommended ping interval based on battery status
        
        Returns:
            Recommended interval in seconds
        """
        # If charging, use minimum interval
        if self.is_charging:
            return LOCATION_PING_INTERVAL_MIN
        
        # Adjust based on battery level
        if self.battery_level > 50:
            return LOCATION_PING_INTERVAL_MIN
        elif self.battery_level > 20:
            return (LOCATION_PING_INTERVAL_MIN + LOCATION_PING_INTERVAL_MAX) // 2
        else:
            # Low battery - use maximum interval
            return LOCATION_PING_INTERVAL_MAX
    
    def should_reduce_frequency(self) -> bool:
        """
        Check if ping frequency should be reduced
        
        Returns:
            True if frequency should be reduced
        """
        return self.battery_level < 20 and not self.is_charging
