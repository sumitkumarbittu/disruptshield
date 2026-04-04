"""
Policy model — insurance policy linked to a rider.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class Policy(Base):
    __tablename__ = "policies"

    id = Column(Integer, primary_key=True, index=True)
    rider_id = Column(Integer, ForeignKey("riders.id", ondelete="CASCADE"), nullable=False, index=True)
    policy_number = Column(String(50), unique=True, nullable=False)
    status = Column(String(20), nullable=False, default="active")  # active / expired / cancelled
    premium_amount = Column(Float, nullable=False, default=0.0)
    coverage_amount = Column(Float, nullable=False, default=0.0)
    city_tier = Column(String(10), nullable=True)  # tier_1 / tier_2 / tier_3
    base_premium_pct = Column(Float, nullable=False, default=2.0)
    effective_from = Column(DateTime(timezone=True), nullable=True)
    effective_to = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    rider = relationship("Rider", back_populates="policies")
