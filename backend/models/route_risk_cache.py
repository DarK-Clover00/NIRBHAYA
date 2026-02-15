"""
Route Risk Cache model for NIRBHAYA application
"""
from sqlalchemy import Column, String, Integer, Float, Text, DateTime
from sqlalchemy.sql import func
from geoalchemy2 import Geography
from backend.database import Base


class RouteRiskCache(Base):
    """
    Route Risk Cache model for caching route safety analysis results
    Reduces computation by storing previously calculated routes
    """
    __tablename__ = "route_risk_cache"
    
    route_hash = Column(String(64), primary_key=True)
    origin_location = Column(Geography(geometry_type='POINT', srid=4326), nullable=False)
    destination_location = Column(Geography(geometry_type='POINT', srid=4326), nullable=False)
    safety_score = Column(Integer, nullable=False)
    risk_classification = Column(String(20), nullable=False)
    crime_score = Column(Float, nullable=False)
    crowd_score = Column(Float, nullable=False)
    commercial_score = Column(Float, nullable=False)
    lighting_score = Column(Float, nullable=False)
    polyline = Column(Text, nullable=False)
    last_updated = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    
    def __repr__(self):
        return f"<RouteRiskCache(hash={self.route_hash}, safety_score={self.safety_score})>"
