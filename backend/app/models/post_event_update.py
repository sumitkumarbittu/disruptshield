"""
PostEventUpdate model — updates triggered after payout processing.
Tracks risk score changes, premium recalculations, and zone risk updates.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class PostEventUpdate(Base):
    __tablename__ = "post_event_updates"

    id = Column(Integer, primary_key=True, index=True)
    rider_id = Column(Integer, ForeignKey("riders.id", ondelete="CASCADE"), nullable=False, index=True)
    claim_id = Column(Integer, ForeignKey("claims.id", ondelete="SET NULL"), nullable=True)
    payout_id = Column(Integer, ForeignKey("payouts.id", ondelete="SET NULL"), nullable=True)
    update_type = Column(String(50), nullable=False)  # risk_update / premium_recalc / zone_risk_update
    previous_risk_score = Column(Float, nullable=True)
    new_risk_score = Column(Float, nullable=True)
    previous_premium = Column(Float, nullable=True)
    new_premium = Column(Float, nullable=True)
    previous_zone_risk = Column(Float, nullable=True)
    new_zone_risk = Column(Float, nullable=True)
    impact_summary = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    rider = relationship("Rider", back_populates="post_event_updates")
