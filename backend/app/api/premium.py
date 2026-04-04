"""
Premium API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.schemas import PremiumRecalcRequest
from app.services.premium_service import PremiumService

router = APIRouter(prefix="/premium", tags=["Premium"])


@router.post("/recalculate/{rider_id}")
def recalculate_premium(
    rider_id: int,
    request: PremiumRecalcRequest = None,
    db: Session = Depends(get_db),
):
    """Recalculate premium for a rider. Stores change in premium_history."""
    try:
        body = request or PremiumRecalcRequest()
        result = PremiumService.recalculate_and_store(
            db=db,
            rider_id=rider_id,
            weekly_income=body.weekly_income,
            zone_risk=body.zone_risk,
            claim_history=body.claim_history,
            risk_score=body.risk_score,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
