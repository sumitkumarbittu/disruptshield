"""
Payout Service — processes payouts for approved claims.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.payout import Payout
from app.models.claim import Claim
from app.models.rider import Rider
from app.services.post_event_service import PostEventService


class PayoutService:
    """Handles payout processing for approved claims."""

    @staticmethod
    def process_payout(db: Session, claim_id: int) -> Payout:
        """
        Process payout for a claim. Updates claim status and creates payout record.
        Then triggers the post-payout event-aware engine.
        """
        claim = db.query(Claim).filter(Claim.id == claim_id).first()
        if not claim:
            raise ValueError(f"Claim {claim_id} not found")

        if claim.status not in ("approve", "approved"):
            raise ValueError(f"Claim {claim_id} is not approved (status: {claim.status})")

        # Check if payout already exists
        existing = db.query(Payout).filter(Payout.claim_id == claim_id).first()
        if existing:
            raise ValueError(f"Payout already exists for claim {claim_id}")

        rider = db.query(Rider).filter(Rider.id == claim.rider_id).first()
        if not rider:
            raise ValueError(f"Rider {claim.rider_id} not found")

        # Create payout with mock transaction reference
        payout = Payout(
            claim_id=claim.id,
            rider_id=rider.id,
            amount=claim.payout_amount or 0.0,
            status="processed",
            transaction_ref=f"TXN-{uuid.uuid4().hex[:12].upper()}",
            payment_method="wallet_credit",
            processed_at=datetime.now(timezone.utc),
        )
        db.add(payout)

        # Update claim status
        claim.status = "paid"

        db.flush()

        # ── POST-PAYOUT EVENT-AWARE ENGINE ──
        # This is critical: after payout, update risk, zone, and premium
        PostEventService.run_post_payout_updates(
            db=db,
            rider=rider,
            claim=claim,
            payout=payout,
        )

        db.commit()
        db.refresh(payout)

        return payout
