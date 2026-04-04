"""
Claims API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.schemas import ClaimSubmitRequest, ClaimResponse
from app.services.claim_service import ClaimService

router = APIRouter(prefix="/claims", tags=["Claims"])


@router.post("/submit", response_model=ClaimResponse)
def submit_claim(
    request: ClaimSubmitRequest,
    db: Session = Depends(get_db),
):
    """Submit a new claim. Runs the fusion engine to evaluate."""
    try:
        claim = ClaimService.submit_claim(
            db=db,
            rider_id=request.rider_id,
            disruption_event_id=request.disruption_event_id,
            disruption_score=request.disruption_score,
            behavior_score=request.behavior_score,
        )
        return ClaimResponse.model_validate(claim)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{rider_id}", response_model=List[ClaimResponse])
def get_claims(rider_id: int, db: Session = Depends(get_db)):
    """Get all claims for a rider."""
    claims = ClaimService.get_claims_by_rider(db, rider_id)
    return [ClaimResponse.model_validate(c) for c in claims]
