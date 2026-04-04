"""
Rider API endpoints — registration and listing.
"""

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.schemas import RiderResponse, RiderListResponse, UploadResponse
from app.services.registration_service import RegistrationService
from app.services.policy_service import PolicyService

router = APIRouter(prefix="/riders", tags=["Riders"])


@router.post("/upload_csv", response_model=UploadResponse)
async def upload_riders_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Upload CSV file to bulk-create riders and their policies."""
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    content = await file.read()
    riders_data, parse_errors = RegistrationService.parse_csv(content)

    if not riders_data:
        raise HTTPException(
            status_code=400,
            detail=f"No valid riders found. Errors: {parse_errors}"
        )

    riders_created, policies_created, create_errors = (
        RegistrationService.create_riders_and_policies(db, riders_data)
    )

    return UploadResponse(
        riders_created=riders_created,
        policies_created=policies_created,
        errors=parse_errors + create_errors,
    )


@router.get("", response_model=RiderListResponse)
def list_riders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """List all riders with pagination."""
    riders, total = PolicyService.get_all_riders(db, skip=skip, limit=limit)
    return RiderListResponse(
        riders=[RiderResponse.model_validate(r) for r in riders],
        total=total,
    )


@router.get("/{rider_id}", response_model=RiderResponse)
def get_rider(rider_id: int, db: Session = Depends(get_db)):
    """Get a rider's profile by ID."""
    rider = PolicyService.get_rider_profile(db, rider_id)
    if not rider:
        raise HTTPException(status_code=404, detail="Rider not found")
    return RiderResponse.model_validate(rider)
