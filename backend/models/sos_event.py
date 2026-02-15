"""
SOS Event model for NIRBHAYA application
"""
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from geoalchemy2 import Geography
import uuid
from backend.database import Base


class SOSEvent(Base):
    """
    SOS Event model for tracking emergency activations
    Stores activation/deactivation locations, geofence data, and nearby devices
    """
    __tablename__ = "sos_events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    activation_location = Column(Geography(geometry_type='POINT', srid=4326), nullable=False)
    deactivation_location = Column(Geography(geometry_type='POINT', srid=4326), nullable=True)
    geofence_radius = Column(Integer, default=50, nullable=False)
    video_stream_url = Column(Text, nullable=True)
    activated_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    deactivated_at = Column(DateTime(timezone=True), nullable=True)
    deactivation_reason = Column(String(50), nullable=True)
    nearby_devices_snapshot = Column(JSONB, nullable=True)
    
    # Relationship to User
    user = relationship("User", backref="sos_events")
    
    def __repr__(self):
        return f"<SOSEvent(id={self.id}, user_id={self.user_id}, activated_at={self.activated_at})>"
