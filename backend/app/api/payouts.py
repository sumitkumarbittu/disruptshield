"""
Payouts API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.schemas import PayoutResponse
from app.services.payout_service import PayoutService

router = APIRouter(prefix="/payouts", tags=["Payouts"])


@router.post("/process/{claim_id}", response_model=PayoutResponse)
def process_payout(
    claim_id: int,
    db: Session = Depends(get_db),
):
    """
    Process payout for an approved claim.
    Triggers the post-payout event-aware engine.
    """
    try:
        payout = PayoutService.process_payout(db, claim_id)
        return PayoutResponse.model_validate(payout)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
