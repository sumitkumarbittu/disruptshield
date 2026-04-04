"""
DisruptionEvent model — external disruption event impacting a zone.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class DisruptionEvent(Base):
    __tablename__ = "disruption_events"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(50), nullable=False)  # heavy_rain / flood / aqi_spike / curfew
    severity = Column(String(20), nullable=False, default="moderate")  # moderate / high / extreme
    zone = Column(String(50), nullable=False)
    pin_code = Column(String(10), nullable=True)
    city = Column(String(100), nullable=True)
    disruption_score = Column(Float, nullable=False, default=0.0)
    description = Column(Text, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    duration_hours = Column(Float, nullable=True)
    severity_multiplier = Column(Float, nullable=False, default=0.5)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    claims = relationship("Claim", back_populates="disruption_event", lazy="dynamic")
    signals = relationship("DisruptionSignal", back_populates="disruption_event", lazy="dynamic")
