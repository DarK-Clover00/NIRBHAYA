"""
Pydantic schemas for telemetry endpoints
"""
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional


class LocationPingRequest(BaseModel):
    """Request schema for location ping submission"""
    device_id: str = Field(..., description="Unique device identifier")
    latitude: float = Field(..., ge=-90, le=90, description="Latitude coordinate")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude coordinate")
    timestamp: datetime = Field(..., description="Timestamp of location ping")
    accuracy: float = Field(..., gt=0, description="Location accuracy in meters")
    
    @field_validator('device_id')
    @classmethod
    def validate_device_id(cls, v):
        """Validate device_id is not empty"""
        if not v or not v.strip():
            raise ValueError("device_id cannot be empty")
        return v.strip()
    
    class Config:
        json_schema_extra = {
            "example": {
                "device_id": "550e8400-e29b-41d4-a716-446655440000",
                "latitude": 37.7749,
                "longitude": -122.4194,
                "timestamp": "2024-01-15T10:30:00Z",
                "accuracy": 10.5
            }
        }


class LocationPingResponse(BaseModel):
    """Response schema for location ping submission"""
    status: str = Field(..., description="Status of the request")
    next_ping_interval: int = Field(..., description="Recommended interval for next ping in seconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "next_ping_interval": 45
            }
        }
