"""
Admin management endpoints.
POST /admin/seed-data
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.deps import require_admin
# For seeding in the API endpoint
from scripts.seed_data import run_seed
from app.models.rider import Rider


router = APIRouter(prefix="/admin", tags=["Admin Management"])


@router.post("/seed-data")
def seed_system_data(
    db: Session = Depends(get_db),
    admin_payload: dict = Depends(require_admin)
):
    """
    Seed 5000 riders and 50 events.
    Fails safely if data is already present.
    Authorized for admin roles only.
    """
    count = db.query(Rider).count()
    if count > 0:
        return {"message": "Data already seeded", "riders_found": count}
    
    try:
        success = run_seed()
        if not success:
            return {"message": "Data already seeded"}
            
        return {"message": "System successfully seeded with dummy data."}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Seeding failed: {str(e)}"
        )
