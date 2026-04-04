"""
Claim model — claim submitted against a disruption event.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class Claim(Base):
    __tablename__ = "claims"

    id = Column(Integer, primary_key=True, index=True)
    rider_id = Column(Integer, ForeignKey("riders.id", ondelete="CASCADE"), nullable=False, index=True)
    disruption_event_id = Column(Integer, ForeignKey("disruption_events.id", ondelete="SET NULL"), nullable=True, index=True)
    claim_number = Column(String(50), unique=True, nullable=False)
    status = Column(String(30), nullable=False, default="submitted")  # submitted / processing / approved / rejected / review
    disruption_score = Column(Float, nullable=True)
    behavior_score = Column(Float, nullable=True)
    final_score = Column(Float, nullable=True)
    decision = Column(String(30), nullable=True)  # AUTO_APPROVE / AUTO_REJECT / REVIEW
    payout_amount = Column(Float, nullable=True, default=0.0)
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    rider = relationship("Rider", back_populates="claims")
    disruption_event = relationship("DisruptionEvent", back_populates="claims")
    payouts = relationship("Payout", back_populates="claim", lazy="dynamic")
    fusion_decisions = relationship("FusionDecision", back_populates="claim", lazy="dynamic")
