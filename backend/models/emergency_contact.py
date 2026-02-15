"""
Emergency Contact model for NIRBHAYA application
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from backend.database import Base


class EmergencyContact(Base):
    """
    Emergency Contact model for storing user's emergency contacts
    Maximum 5 contacts per user
    """
    __tablename__ = "emergency_contacts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    name = Column(String(100), nullable=True)
    phone_number = Column(String(15), nullable=False)
    priority = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship to User
    user = relationship("User", backref="emergency_contacts")
    
    def __repr__(self):
        return f"<EmergencyContact(id={self.id}, user_id={self.user_id}, phone={self.phone_number})>"
