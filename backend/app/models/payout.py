"""
Payout model — payout record for an approved claim.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class Payout(Base):
    __tablename__ = "payouts"

    id = Column(Integer, primary_key=True, index=True)
    claim_id = Column(Integer, ForeignKey("claims.id", ondelete="CASCADE"), nullable=False, index=True)
    rider_id = Column(Integer, ForeignKey("riders.id", ondelete="CASCADE"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    status = Column(String(30), nullable=False, default="pending")  # pending / processed / failed
    transaction_ref = Column(String(100), nullable=True)  # Mock transaction reference
    payment_method = Column(String(50), nullable=True, default="wallet_credit")
    processed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    claim = relationship("Claim", back_populates="payouts")
    rider = relationship("Rider", back_populates="payouts")
