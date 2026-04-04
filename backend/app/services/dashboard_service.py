"""
Dashboard Service — aggregated analytics for the dashboard.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.rider import Rider
from app.models.policy import Policy
from app.models.claim import Claim
from app.models.payout import Payout
from app.models.disruption_event import DisruptionEvent


class DashboardService:
    """Provides aggregated analytics for the dashboard."""

    @staticmethod
    def get_summary(db: Session) -> dict:
        total_riders = db.query(Rider).count()

        active_policies = db.query(Policy).filter(Policy.is_active == True).count()

        total_claims = db.query(Claim).count()
        approved_claims = db.query(Claim).filter(Claim.status.in_(["approve", "approved", "paid"])).count()
        rejected_claims = db.query(Claim).filter(Claim.status.in_(["reject", "rejected"])).count()
        review_claims = db.query(Claim).filter(Claim.status == "review").count()

        total_payouts_result = db.query(func.coalesce(func.sum(Payout.amount), 0.0)).scalar()
        total_payouts = float(total_payouts_result) if total_payouts_result else 0.0

        total_events = db.query(DisruptionEvent).count()
        active_events = db.query(DisruptionEvent).filter(DisruptionEvent.is_active == True).count()

        avg_premium_result = db.query(func.coalesce(func.avg(Policy.premium_amount), 0.0)).filter(
            Policy.is_active == True
        ).scalar()
        avg_premium = float(avg_premium_result) if avg_premium_result else 0.0

        avg_risk_result = db.query(func.coalesce(func.avg(Rider.risk_score), 0.0)).scalar()
        avg_risk = float(avg_risk_result) if avg_risk_result else 0.0

        return {
            "total_riders": total_riders,
            "active_policies": active_policies,
            "total_claims": total_claims,
            "approved_claims": approved_claims,
            "rejected_claims": rejected_claims,
            "review_claims": review_claims,
            "total_payouts": round(total_payouts, 2),
            "total_events": total_events,
            "active_events": active_events,
            "avg_premium": round(avg_premium, 2),
            "avg_risk_score": round(avg_risk, 4),
        }
