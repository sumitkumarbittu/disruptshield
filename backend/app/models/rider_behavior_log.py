"""
RiderBehaviorLog model — behavioral profiling logs for riders.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class RiderBehaviorLog(Base):
    __tablename__ = "rider_behavior_logs"

    id = Column(Integer, primary_key=True, index=True)
    rider_id = Column(Integer, ForeignKey("riders.id", ondelete="CASCADE"), nullable=False, index=True)
    log_type = Column(String(50), nullable=False)  # gps_trail / order_activity / session / anomaly
    temporal_score = Column(Float, nullable=True)
    spatial_score = Column(Float, nullable=True)
    activity_score = Column(Float, nullable=True)
    overall_behavior_score = Column(Float, nullable=True)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    rider = relationship("Rider", back_populates="behavior_logs")
