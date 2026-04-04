"""
Policy API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.schemas import PolicyResponse, PremiumHistoryResponse, ClaimResponse, PayoutResponse
from app.services.policy_service import PolicyService

router = APIRouter(prefix="/policies", tags=["Policies"])


@router.get("/{rider_id}", response_model=PolicyResponse)
def get_policy(rider_id: int, db: Session = Depends(get_db)):
    """Get the active policy for a rider."""
    policy = PolicyService.get_policy_by_rider(db, rider_id)
    if not policy:
        raise HTTPException(status_code=404, detail="No active policy found for this rider")
    return PolicyResponse.model_validate(policy)


@router.get("/{rider_id}/premium_history", response_model=List[PremiumHistoryResponse])
def get_premium_history(rider_id: int, db: Session = Depends(get_db)):
    """Get the premium history for a rider."""
    history = PolicyService.get_premium_history(db, rider_id)
    return [PremiumHistoryResponse.model_validate(h) for h in history]


@router.get("/{rider_id}/claims", response_model=List[ClaimResponse])
def get_claim_history(rider_id: int, db: Session = Depends(get_db)):
    """Get the claim history for a rider."""
    claims = PolicyService.get_claim_history(db, rider_id)
    return [ClaimResponse.model_validate(c) for c in claims]


@router.get("/{rider_id}/payouts", response_model=List[PayoutResponse])
def get_payout_history(rider_id: int, db: Session = Depends(get_db)):
    """Get the payout history for a rider."""
    payouts = PolicyService.get_payout_history(db, rider_id)
    return [PayoutResponse.model_validate(p) for p in payouts]
