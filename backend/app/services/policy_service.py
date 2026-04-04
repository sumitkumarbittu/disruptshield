"""
Policy Service — rider profile and policy management.
"""

from sqlalchemy.orm import Session
from typing import Optional

from app.models.rider import Rider
from app.models.policy import Policy
from app.models.premium_history import PremiumHistory
from app.models.claim import Claim
from app.models.payout import Payout


class PolicyService:
    """Policy and rider profile management."""

    @staticmethod
    def get_rider_profile(db: Session, rider_id: int) -> Optional[dict]:
        rider = db.query(Rider).filter(Rider.id == rider_id).first()
        if not rider:
            return None
        return rider

    @staticmethod
    def get_policy_by_rider(db: Session, rider_id: int) -> Optional[Policy]:
        return db.query(Policy).filter(
            Policy.rider_id == rider_id,
            Policy.is_active == True
        ).first()

    @staticmethod
    def get_premium_history(db: Session, rider_id: int):
        return db.query(PremiumHistory).filter(
            PremiumHistory.rider_id == rider_id
        ).order_by(PremiumHistory.created_at.desc()).all()

    @staticmethod
    def get_claim_history(db: Session, rider_id: int):
        return db.query(Claim).filter(
            Claim.rider_id == rider_id
        ).order_by(Claim.created_at.desc()).all()

    @staticmethod
    def get_payout_history(db: Session, rider_id: int):
        return db.query(Payout).filter(
            Payout.rider_id == rider_id
        ).order_by(Payout.created_at.desc()).all()

    @staticmethod
    def get_all_riders(db: Session, skip: int = 0, limit: int = 100):
        riders = db.query(Rider).offset(skip).limit(limit).all()
        total = db.query(Rider).count()
        return riders, total
