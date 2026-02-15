"""
Incident Report model for NIRBHAYA application
"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, CheckConstraint, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from geoalchemy2 import Geography
import uuid
from backend.database import Base


class IncidentReport(Base):
    """
    Incident Report model for storing reported incidents
    Includes geolocation, evidence, and government system integration
    """
    __tablename__ = "incident_reports"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reporter_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    suspect_device_id = Column(String(255), nullable=True, index=True)
    incident_type = Column(String(50), nullable=False)
    location = Column(Geography(geometry_type='POINT', srid=4326), nullable=False)
    description = Column(Text, nullable=True)
    evidence_urls = Column(ARRAY(Text), nullable=True)
    government_system_ref = Column(String(100), nullable=True)
    status = Column(String(20), default="submitted", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationship to User
    reporter = relationship("User", backref="filed_reports")
    
    __table_args__ = (
        CheckConstraint(
            "incident_type IN ('SOS_Trigger', 'Harassment', 'Poor_Lighting')", 
            name='check_incident_type'
        ),
    )
    
    def __repr__(self):
        return f"<IncidentReport(id={self.id}, type={self.incident_type}, reporter_id={self.reporter_id})>"
