"""
Trust Score Event model for NIRBHAYA application
"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from backend.database import Base


class TrustScoreEvent(Base):
    """
    Trust Score Event model for tracking trust score changes
    Provides audit trail for all trust score modifications
    """
    __tablename__ = "trust_score_events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, index=True)
    event_type = Column(String(50), nullable=False)
    score_change = Column(Integer, nullable=False)
    previous_score = Column(Integer, nullable=True)
    new_score = Column(Integer, nullable=True)
    related_entity_id = Column(UUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship to User
    user = relationship("User", backref="trust_score_events")
    
    def __repr__(self):
        return f"<TrustScoreEvent(id={self.id}, user_id={self.user_id}, event={self.event_type}, change={self.score_change})>"
