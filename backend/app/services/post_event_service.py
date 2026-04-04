"""
Post-Event Service — event-aware engine that runs after payout processing.

After payout:
1. Update rider risk score
2. Update zone risk
3. Recalculate premium
4. Insert record into post_event_updates
5. Log event impact
"""

from sqlalchemy.orm import Session

from app.models.rider import Rider
from app.models.claim import Claim
from app.models.payout import Payout
from app.models.policy import Policy
from app.models.post_event_update import PostEventUpdate
from app.models.premium_history import PremiumHistory
from app.services.premium_service import PremiumService


class PostEventService:
    """
    Post-payout event-aware engine.
    This is the critical feedback loop that maintains the event-aware architecture.
    """

    @staticmethod
    def run_post_payout_updates(
        db: Session,
        rider: Rider,
        claim: Claim,
        payout: Payout,
    ) -> PostEventUpdate:
        """
        Execute all post-payout updates:
        1. Update rider risk score based on claim outcome
        2. Update zone risk (simplified model)
        3. Recalculate premium
        4. Log everything in post_event_updates
        """
        previous_risk = rider.risk_score
        previous_premium = 0.0

        # Get active policy
        policy = db.query(Policy).filter(
            Policy.rider_id == rider.id,
            Policy.is_active == True
        ).first()

        if policy:
            previous_premium = policy.premium_amount

        # ── Step 1: Update rider risk score ──
        new_risk = PostEventService._update_rider_risk(
            current_risk=rider.risk_score,
            claim=claim,
        )
        rider.risk_score = new_risk

        # ── Step 2: Update zone risk (simplified) ──
        # In production, this would aggregate across all riders in the zone
        previous_zone_risk = 0.5
        new_zone_risk = PostEventService._update_zone_risk(
            current_zone_risk=previous_zone_risk,
            claim=claim,
        )

        # ── Step 3: Recalculate premium ──
        new_premium = previous_premium
        if policy:
            past_claims = db.query(Claim).filter(Claim.rider_id == rider.id).count()
            new_premium = PremiumService.calculate_premium(
                weekly_income=rider.avg_weekly_income,
                zone_risk=new_zone_risk,
                claim_history=past_claims,
                risk_score=new_risk,
                base_premium_pct=policy.base_premium_pct,
            )
            policy.premium_amount = new_premium

            # Log premium change
            premium_log = PremiumHistory(
                rider_id=rider.id,
                policy_id=policy.id,
                previous_premium=previous_premium,
                new_premium=new_premium,
                change_reason="post_payout_recalculation",
                weekly_income=rider.avg_weekly_income,
                zone_risk=new_zone_risk,
                claim_history_count=past_claims,
                risk_score=new_risk,
            )
            db.add(premium_log)

        # ── Step 4: Insert post_event_update record ──
        impact_summary = (
            f"Post-payout update for claim {claim.claim_number}. "
            f"Risk: {previous_risk:.3f} → {new_risk:.3f}. "
            f"Premium: ₹{previous_premium:.2f} → ₹{new_premium:.2f}. "
            f"Zone risk: {previous_zone_risk:.3f} → {new_zone_risk:.3f}. "
            f"Payout amount: ₹{payout.amount:.2f}."
        )

        post_update = PostEventUpdate(
            rider_id=rider.id,
            claim_id=claim.id,
            payout_id=payout.id,
            update_type="post_payout_full_update",
            previous_risk_score=previous_risk,
            new_risk_score=new_risk,
            previous_premium=previous_premium,
            new_premium=new_premium,
            previous_zone_risk=previous_zone_risk,
            new_zone_risk=new_zone_risk,
            impact_summary=impact_summary,
        )
        db.add(post_update)

        return post_update

    @staticmethod
    def _update_rider_risk(current_risk: float, claim: Claim) -> float:
        """
        Update rider risk score based on claim outcome.
        - Approved claim with low disruption → risk increases slightly
        - Approved claim with high disruption → risk stays or decreases
        - Rejected claim → risk increases significantly
        """
        adjustment = 0.0

        if claim.decision in ("AUTO_REJECT", "reject"):
            # Rejected claims increase risk
            adjustment = 0.10
        elif claim.decision in ("AUTO_APPROVE", "approve"):
            if claim.disruption_score and claim.disruption_score >= 0.60:
                # Legitimate high-disruption claim — lower risk slightly
                adjustment = -0.02
            else:
                # Moderate disruption claim — slight risk increase
                adjustment = 0.03
        elif claim.decision in ("REVIEW", "review"):
            adjustment = 0.05

        new_risk = max(0.0, min(1.0, current_risk + adjustment))
        return round(new_risk, 4)

    @staticmethod
    def _update_zone_risk(current_zone_risk: float, claim: Claim) -> float:
        """
        Simplified zone risk update.
        In production, this aggregates across all riders in the zone.
        """
        if claim.disruption_score and claim.disruption_score >= 0.60:
            # High disruption events increase zone risk
            new_risk = min(1.0, current_zone_risk + 0.05)
        else:
            new_risk = current_zone_risk

        return round(new_risk, 4)
