"""
Events API endpoints — disruption event management.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.schemas import DisruptionEventCreate, DisruptionEventResponse
from app.models.disruption_event import DisruptionEvent

router = APIRouter(prefix="/events", tags=["Events"])


@router.post("/create", response_model=DisruptionEventResponse)
def create_event(
    request: DisruptionEventCreate,
    db: Session = Depends(get_db),
):
    """Create a new disruption event."""
    # Determine severity based on disruption score
    severity = request.severity
    if request.disruption_score >= 0.80:
        severity = "extreme"
    elif request.disruption_score >= 0.60:
        severity = "high"
    elif request.disruption_score >= 0.35:
        severity = "moderate"

    # Set severity multiplier
    severity_multiplier = request.severity_multiplier or 0.5
    if severity == "extreme":
        severity_multiplier = 1.0
    elif severity == "high":
        severity_multiplier = 0.75
    elif severity == "moderate":
        severity_multiplier = 0.5

    event = DisruptionEvent(
        event_type=request.event_type,
        severity=severity,
        zone=request.zone,
        pin_code=request.pin_code or request.zone,
        city=request.city,
        disruption_score=request.disruption_score,
        description=request.description,
        duration_hours=request.duration_hours or 4.0,
        severity_multiplier=severity_multiplier,
        is_active=True,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return DisruptionEventResponse.model_validate(event)


@router.get("", response_model=List[DisruptionEventResponse])
def list_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """List all disruption events."""
    events = db.query(DisruptionEvent).order_by(
        DisruptionEvent.created_at.desc()
    ).offset(skip).limit(limit).all()
    return [DisruptionEventResponse.model_validate(e) for e in events]
