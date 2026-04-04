"""
Rider model — delivery partner enrolled in DisruptShield.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class Rider(Base):
    __tablename__ = "riders"

    id = Column(Integer, primary_key=True, index=True)
    rider_external_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    phone = Column(String(20), nullable=True)
    email = Column(String(200), nullable=True)
    platform = Column(String(50), nullable=False)  # swiggy / zomato
    city = Column(String(100), nullable=False)
    pin_code = Column(String(10), nullable=False)
    zone = Column(String(50), nullable=True)
    avg_weekly_income = Column(Float, nullable=False, default=0.0)
    risk_score = Column(Float, nullable=False, default=0.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    policies = relationship("Policy", back_populates="rider", lazy="dynamic")
    premium_history = relationship("PremiumHistory", back_populates="rider", lazy="dynamic")
    claims = relationship("Claim", back_populates="rider", lazy="dynamic")
    payouts = relationship("Payout", back_populates="rider", lazy="dynamic")
    behavior_logs = relationship("RiderBehaviorLog", back_populates="rider", lazy="dynamic")
    post_event_updates = relationship("PostEventUpdate", back_populates="rider", lazy="dynamic")
