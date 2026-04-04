"""
FusionDecision model — decision made by the fusion engine for a claim.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class FusionDecision(Base):
    __tablename__ = "fusion_decisions"

    id = Column(Integer, primary_key=True, index=True)
    claim_id = Column(Integer, ForeignKey("claims.id", ondelete="CASCADE"), nullable=False, index=True)
    disruption_score = Column(Float, nullable=False)
    behavior_score = Column(Float, nullable=False)
    risk_weight = Column(Float, nullable=False, default=0.60)
    final_score = Column(Float, nullable=False)
    decision = Column(String(30), nullable=False)  # approve / reject / review
    past_claims_count = Column(Integer, nullable=True)
    zone_risk = Column(Float, nullable=True)
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    claim = relationship("Claim", back_populates="fusion_decisions")
