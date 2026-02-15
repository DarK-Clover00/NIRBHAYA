"""
Pydantic schemas for request/response validation
"""
from backend.schemas.telemetry import LocationPingRequest, LocationPingResponse

__all__ = [
    "LocationPingRequest",
    "LocationPingResponse"
]
