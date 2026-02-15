"""
User model for NIRBHAYA application
"""
from sqlalchemy import Column, String, Integer, DateTime, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from backend.database import Base


class User(Base):
    """
    User model representing application users
    Tracks trust scores, device fingerprints, and user status
    """
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone_number = Column(String(15), unique=True, nullable=False, index=True)
    trust_score = Column(
        Integer, 
        default=50, 
        nullable=False,
        server_default="50"
    )
    classification = Column(
        String(20), 
        default="Normal", 
        nullable=False,
        server_default="Normal"
    )
    device_fingerprint = Column(String(255), unique=True, nullable=False, index=True)
    status = Column(
        String(20), 
        default="active", 
        nullable=False,
        server_default="active"
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        CheckConstraint('trust_score >= 0 AND trust_score <= 100', name='check_trust_score_range'),
        CheckConstraint("classification IN ('Normal', 'Suspected', 'Fraud')", name='check_classification'),
        CheckConstraint("status IN ('active', 'flagged', 'banned')", name='check_status'),
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, phone={self.phone_number}, trust_score={self.trust_score})>"
