"""
Premium Service — dynamic premium calculation engine.

Inputs: weekly_income, zone_risk, claim_history, risk_score
Output: premium_amount

Every premium change is stored in premium_history.
"""

from sqlalchemy.orm import Session

from app.models.rider import Rider
from app.models.policy import Policy
from app.models.premium_history import PremiumHistory


class PremiumService:
    """Dynamic premium calculation engine."""

    # Premium cap: max 3.5% of weekly income
    MAX_PREMIUM_PCT = 3.5

    @staticmethod
    def calculate_premium(
        weekly_income: float,
        zone_risk: float,
        claim_history: int,
        risk_score: float,
        base_premium_pct: float = 2.0,
    ) -> float:
        """
        Calculate premium amount using rule-based formula.

        Premium = base_pct * weekly_income
               + zone_risk_surcharge
               + claim_history_surcharge
               + risk_score_adjustment
        Capped at 3.5% of weekly_income.
        """
        # Base premium
        base_premium = (base_premium_pct / 100.0) * weekly_income

        # Zone risk surcharge: higher risk zones pay more
        zone_surcharge = zone_risk * 0.005 * weekly_income

        # Claim history surcharge: more past claims → higher premium
        claim_surcharge = 0.0
        if claim_history >= 3:
            claim_surcharge = 0.005 * weekly_income
        elif claim_history >= 1:
            claim_surcharge = 0.002 * weekly_income

        # Risk score adjustment
        risk_adjustment = risk_score * 0.003 * weekly_income

        # Total premium
        premium = base_premium + zone_surcharge + claim_surcharge + risk_adjustment

        # NCB discount placeholder: if no claims for 8+ weeks, reduce by 10%
        # TODO: implement NCB tracking (requires claim date history)

        # Apply cap
        max_premium = (PremiumService.MAX_PREMIUM_PCT / 100.0) * weekly_income
        premium = min(premium, max_premium)

        return round(premium, 2)

    @staticmethod
    def recalculate_and_store(
        db: Session,
        rider_id: int,
        weekly_income: float = None,
        zone_risk: float = None,
        claim_history: int = None,
        risk_score: float = None,
    ) -> dict:
        """
        Recalculate premium for a rider and store the change.
        Returns the new premium details.
        """
        rider = db.query(Rider).filter(Rider.id == rider_id).first()
        if not rider:
            raise ValueError(f"Rider {rider_id} not found")

        policy = db.query(Policy).filter(
            Policy.rider_id == rider_id,
            Policy.is_active == True
        ).first()
        if not policy:
            raise ValueError(f"No active policy for rider {rider_id}")

        # Use provided values or fall back to stored values
        w_income = weekly_income if weekly_income is not None else rider.avg_weekly_income
        z_risk = zone_risk if zone_risk is not None else 0.5
        c_history = claim_history if claim_history is not None else rider.claims.count()
        r_score = risk_score if risk_score is not None else rider.risk_score

        previous_premium = policy.premium_amount

        new_premium = PremiumService.calculate_premium(
            weekly_income=w_income,
            zone_risk=z_risk,
            claim_history=c_history,
            risk_score=r_score,
            base_premium_pct=policy.base_premium_pct,
        )

        # Update policy
        policy.premium_amount = new_premium

        # Update rider income if provided
        if weekly_income is not None:
            rider.avg_weekly_income = weekly_income

        # Log premium change
        premium_log = PremiumHistory(
            rider_id=rider_id,
            policy_id=policy.id,
            previous_premium=previous_premium,
            new_premium=new_premium,
            change_reason="recalculation",
            weekly_income=w_income,
            zone_risk=z_risk,
            claim_history_count=c_history,
            risk_score=r_score,
        )
        db.add(premium_log)
        db.commit()

        return {
            "rider_id": rider_id,
            "previous_premium": previous_premium,
            "new_premium": new_premium,
            "weekly_income": w_income,
            "zone_risk": z_risk,
            "claim_history": c_history,
            "risk_score": r_score,
        }
