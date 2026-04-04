"""
Claim Service — handles claim submission and lifecycle.
"""

import uuid
from sqlalchemy.orm import Session

from app.models.claim import Claim
from app.models.rider import Rider
from app.models.disruption_event import DisruptionEvent
from app.engines.fusion_engine import FusionEngine


class ClaimService:
    """Handles claim submission, processing, and status management."""

    @staticmethod
    def submit_claim(
        db: Session,
        rider_id: int,
        disruption_event_id: int,
        disruption_score: float = None,
        behavior_score: float = None,
    ) -> Claim:
        """
        Submit a new claim. Runs the fusion engine to get a decision.
        """
        rider = db.query(Rider).filter(Rider.id == rider_id).first()
        if not rider:
            raise ValueError(f"Rider {rider_id} not found")

        event = db.query(DisruptionEvent).filter(
            DisruptionEvent.id == disruption_event_id
        ).first()
        if not event:
            raise ValueError(f"Disruption event {disruption_event_id} not found")

        # Use event's disruption score if not provided
        d_score = disruption_score if disruption_score is not None else event.disruption_score

        # Use rider's risk score as behavior score if not provided
        b_score = behavior_score if behavior_score is not None else rider.risk_score

        # Get past claims count
        past_claims = db.query(Claim).filter(Claim.rider_id == rider_id).count()

        # Run fusion engine
        fusion_result = FusionEngine.evaluate(
            db=db,
            disruption_score=d_score,
            behavior_score=b_score,
            past_claims=past_claims,
            zone_risk=0.5,  # TODO: get actual zone risk from signals
        )

        # Compute payout amount for approved claims
        payout_amount = 0.0
        if fusion_result["decision"] == "approve":
            payout_amount = ClaimService._compute_payout(rider, event)

        # Create claim record
        claim = Claim(
            rider_id=rider_id,
            disruption_event_id=disruption_event_id,
            claim_number=f"CLM-{uuid.uuid4().hex[:8].upper()}",
            status=fusion_result["decision"],  # approved / rejected / review
            disruption_score=d_score,
            behavior_score=b_score,
            final_score=fusion_result["final_score"],
            decision=fusion_result["decision_label"],
            payout_amount=payout_amount,
            reason=fusion_result["reason"],
        )
        db.add(claim)

        # Store fusion decision
        from app.models.fusion_decision import FusionDecision
        fd = FusionDecision(
            claim_id=0,  # will be set after flush
            disruption_score=d_score,
            behavior_score=b_score,
            risk_weight=fusion_result["risk_weight"],
            final_score=fusion_result["final_score"],
            decision=fusion_result["decision"],
            past_claims_count=past_claims,
            zone_risk=0.5,
            reason=fusion_result["reason"],
        )

        db.flush()
        fd.claim_id = claim.id
        db.add(fd)
        db.commit()
        db.refresh(claim)

        return claim

    @staticmethod
    def _compute_payout(rider: Rider, event: DisruptionEvent) -> float:
        """
        Compute payout based on estimated income loss.
        Payout = hourly_estimate × disruption_hours × severity_multiplier
        Capped at 30% of weekly income.
        """
        # Estimate hourly earnings (assume 8-hour day, 6-day week)
        estimated_hourly = rider.avg_weekly_income / 48.0 if rider.avg_weekly_income > 0 else 0.0
        duration = event.duration_hours or 4.0  # default 4 hours

        raw_loss = estimated_hourly * duration
        adjusted_loss = raw_loss * (event.severity_multiplier or 0.5)

        # Cap at 30% of weekly income
        max_payout = rider.avg_weekly_income * 0.30
        payout = min(adjusted_loss, max_payout)

        return round(payout, 2)

    @staticmethod
    def get_claims_by_rider(db: Session, rider_id: int):
        return db.query(Claim).filter(
            Claim.rider_id == rider_id
        ).order_by(Claim.created_at.desc()).all()
