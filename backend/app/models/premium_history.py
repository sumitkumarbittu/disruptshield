"""
PremiumHistory model — tracks every premium change for a rider.
"""

from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class PremiumHistory(Base):
    __tablename__ = "premium_history"

    id = Column(Integer, primary_key=True, index=True)
    rider_id = Column(Integer, ForeignKey("riders.id", ondelete="CASCADE"), nullable=False, index=True)
    policy_id = Column(Integer, ForeignKey("policies.id", ondelete="SET NULL"), nullable=True)
    previous_premium = Column(Float, nullable=True)
    new_premium = Column(Float, nullable=False)
    change_reason = Column(String(200), nullable=True)  # initial / recalculation / ncb_discount / risk_update
    weekly_income = Column(Float, nullable=True)
    zone_risk = Column(Float, nullable=True)
    claim_history_count = Column(Integer, nullable=True)
    risk_score = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    rider = relationship("Rider", back_populates="premium_history")
