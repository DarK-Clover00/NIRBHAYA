"""
Offline queue management for storing data when network is unavailable
"""
import asyncio
from typing import List, Dict, Optional, Callable
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


class OfflineQueue:
    """
    Manages offline queue for location pings, incident reports, and other data
    that needs to be synchronized when connection is restored.
    
    Requirements: 15.2, 15.7
    """
    
    def __init__(
        self,
        max_size: int = 1000,
        on_sync_complete: Optional[Callable] = None
    ):
        """
        Initialize offline queue
        
        Args:
            max_size: Maximum number of items to queue
            on_sync_complete: Callback when synchronization completes
        """
        self.max_size = max_size
        self.on_sync_complete = on_sync_complete
        
        self.location_pings = []
        self.incident_reports = []
        self.other_data = []
        
        self.is_syncing = False
        self.last_sync_time = None
    
    def queue_location_ping(self, ping_data: Dict):
        """
        Queue a location ping for later synchronization
        
        Args:
            ping_data: Location ping data
        """
        self._add_to_queue(self.location_pings, ping_data)
    
    def queue_incident_report(self, report_data: Dict):
        """
        Queue an incident report for later synchronization
        
        Args:
            report_data: Incident report data
        """
        self._add_to_queue(self.incident_reports, report_data)
    
    def queue_data(self, data_type: str, data: Dict):
        """
        Queue generic data for later synchronization
        
        Args:
            data_type: Type of data being queued
            data: Data to queue
        """
        item = {
            "type": data_type,
            "data": data,
            "queued_at": datetime.utcnow().isoformat()
        }
        self._add_to_queue(self.other_data, item)
    
    def _add_to_queue(self, queue: List, item: Dict):
        """
        Add item to queue with size limit enforcement
        
        Args:
            queue: Queue to add to
            item: Item to add
        """
        # Add timestamp if not present
        if "queued_at" not in item:
            item["queued_at"] = datetime.utcnow().isoformat()
        
        queue.append(item)
        
        # Enforce size limit (FIFO)
        if len(queue) > self.max_size:
            queue.pop(0)
    
    async def synchronize(self, send_callback: Callable) -> Dict:
        """
        Synchronize all queued data with backend
        
        Args:
            send_callback: Async function to send data to backend
                          Should accept (data_type, data) and return bool
        
        Returns:
            Dictionary with sync results
        """
        if self.is_syncing:
            return {"status": "already_syncing"}
        
        self.is_syncing = True
        start_time = datetime.utcnow()
        
        results = {
            "location_pings": {"sent": 0, "failed": 0},
            "incident_reports": {"sent": 0, "failed": 0},
            "other_data": {"sent": 0, "failed": 0},
            "total_time_seconds": 0
        }
        
        try:
            # Synchronize location pings
            results["location_pings"] = await self._sync_queue(
                self.location_pings,
                "location_ping",
                send_callback
            )
            
            # Synchronize incident reports
            results["incident_reports"] = await self._sync_queue(
                self.incident_reports,
                "incident_report",
                send_callback
            )
            
            # Synchronize other data
            results["other_data"] = await self._sync_other_data(send_callback)
            
            # Calculate total time
            end_time = datetime.utcnow()
            results["total_time_seconds"] = (end_time - start_time).total_seconds()
            
            self.last_sync_time = end_time
            
            if self.on_sync_complete:
                self.on_sync_complete(results)
            
        finally:
            self.is_syncing = False
        
        return results
    
    async def _sync_queue(
        self,
        queue: List,
        data_type: str,
        send_callback: Callable
    ) -> Dict:
        """
        Synchronize a specific queue with exponential backoff
        
        Args:
            queue: Queue to synchronize
            data_type: Type of data in queue
            send_callback: Callback to send data
        
        Returns:
            Dictionary with sent and failed counts
        """
        sent = 0
        failed = 0
        
        # Process with exponential backoff (1s, 2s, 4s, 8s, max 60s)
        retry_delay = 1
        max_retry_delay = 60
        consecutive_failures = 0
        max_consecutive_failures = 5
        
        while queue and consecutive_failures < max_consecutive_failures:
            item = queue[0]
            
            try:
                success = await send_callback(data_type, item)
                
                if success:
                    queue.pop(0)
                    sent += 1
                    retry_delay = 1  # Reset delay on success
                    consecutive_failures = 0
                    logger.info(f"Successfully synced {data_type} item")
                else:
                    failed += 1
                    consecutive_failures += 1
                    # Exponential backoff
                    await asyncio.sleep(retry_delay)
                    retry_delay = min(retry_delay * 2, max_retry_delay)
                    logger.warning(
                        f"Failed to sync {data_type} item, "
                        f"retry in {retry_delay}s (attempt {consecutive_failures})"
                    )
                    
            except Exception as e:
                failed += 1
                consecutive_failures += 1
                logger.error(f"Error syncing {data_type}: {e}")
                await asyncio.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, max_retry_delay)
        
        if consecutive_failures >= max_consecutive_failures:
            logger.error(
                f"Stopped syncing {data_type} after {max_consecutive_failures} "
                f"consecutive failures"
            )
        
        return {"sent": sent, "failed": failed}
    
    async def _sync_other_data(self, send_callback: Callable) -> Dict:
        """Synchronize other queued data"""
        sent = 0
        failed = 0
        
        while self.other_data:
            item = self.other_data[0]
            data_type = item.get("type", "unknown")
            data = item.get("data", {})
            
            try:
                success = await send_callback(data_type, data)
                
                if success:
                    self.other_data.pop(0)
                    sent += 1
                else:
                    failed += 1
                    break
                    
            except Exception:
                failed += 1
                break
        
        return {"sent": sent, "failed": failed}
    
    def get_queue_sizes(self) -> Dict:
        """
        Get sizes of all queues
        
        Returns:
            Dictionary with queue sizes
        """
        return {
            "location_pings": len(self.location_pings),
            "incident_reports": len(self.incident_reports),
            "other_data": len(self.other_data),
            "total": len(self.location_pings) + len(self.incident_reports) + len(self.other_data)
        }
    
    def clear_all(self):
        """Clear all queues"""
        self.location_pings.clear()
        self.incident_reports.clear()
        self.other_data.clear()
    
    def has_pending_data(self) -> bool:
        """Check if there is pending data to synchronize"""
        return bool(self.location_pings or self.incident_reports or self.other_data)
    
    def save_to_disk(self, filepath: str):
        """
        Save queues to disk for persistence
        
        Args:
            filepath: Path to save file
        """
        data = {
            "location_pings": self.location_pings,
            "incident_reports": self.incident_reports,
            "other_data": self.other_data,
            "last_sync_time": self.last_sync_time.isoformat() if self.last_sync_time else None
        }
        
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f)
            logger.info(f"Saved offline queue to {filepath}")
        except Exception as e:
            # Silently fail - don't crash app
            logger.error(f"Failed to save offline queue: {e}")
    
    def load_from_disk(self, filepath: str):
        """
        Load queues from disk
        
        Args:
            filepath: Path to load file
        """
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            self.location_pings = data.get("location_pings", [])
            self.incident_reports = data.get("incident_reports", [])
            self.other_data = data.get("other_data", [])
            
            last_sync = data.get("last_sync_time")
            if last_sync:
                self.last_sync_time = datetime.fromisoformat(last_sync)
            
            logger.info(f"Loaded offline queue from {filepath}")
                
        except FileNotFoundError:
            logger.info(f"No offline queue file found at {filepath}")
        except Exception as e:
            # Silently fail - start with empty queues
            logger.error(f"Failed to load offline queue: {e}")
