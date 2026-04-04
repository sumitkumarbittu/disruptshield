"""
DisruptionSignal model — individual signal feeding into a disruption event.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class DisruptionSignal(Base):
    __tablename__ = "disruption_signals"

    id = Column(Integer, primary_key=True, index=True)
    disruption_event_id = Column(Integer, ForeignKey("disruption_events.id", ondelete="CASCADE"), nullable=False, index=True)
    signal_type = Column(String(50), nullable=False)  # rainfall / flood_alert / aqi / traffic / news / order_drop
    signal_value = Column(Float, nullable=False)
    normalized_value = Column(Float, nullable=True)
    confidence = Column(Float, nullable=True)
    source = Column(String(100), nullable=True)
    raw_data = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    disruption_event = relationship("DisruptionEvent", back_populates="signals")
