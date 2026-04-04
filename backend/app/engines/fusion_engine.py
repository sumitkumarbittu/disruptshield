"""
Fusion Engine — rule-based decision engine combining disruption score and behavior score.

Formula: Final Score = Disruption Score − (Behavior Risk Score × risk_weight)
Default risk_weight = 0.60

Decision Table:
  >= 0.60 → AUTO-APPROVE
  0.40 – 0.59 → REVIEW
  < 0.40 → AUTO-REJECT
"""

from sqlalchemy.orm import Session

from app.core.config import settings


class FusionEngine:
    """Rule-based fusion and decision engine."""

    @staticmethod
    def evaluate(
        db: Session,
        disruption_score: float,
        behavior_score: float,
        past_claims: int,
        zone_risk: float,
    ) -> dict:
        """
        Evaluate claim using the fusion formula.

        Inputs:
            disruption_score: 0-1, from external disruption engine
            behavior_score: 0-1, from behavioral profiling engine (risk)
            past_claims: number of prior claims
            zone_risk: 0-1, zone-level risk

        Output:
            decision dict with: decision, decision_label, final_score, reason, risk_weight
        """
        risk_weight = settings.DEFAULT_RISK_WEIGHT  # 0.60

        # Apply past claims penalty
        claim_penalty = 0.0
        if past_claims >= 5:
            claim_penalty = 0.10
        elif past_claims >= 3:
            claim_penalty = 0.05
        elif past_claims >= 1:
            claim_penalty = 0.02

        # Compute final score
        adjusted_behavior = behavior_score + claim_penalty
        adjusted_behavior = min(adjusted_behavior, 1.0)

        final_score = disruption_score - (adjusted_behavior * risk_weight)
        final_score = round(final_score, 4)

        # Decision table
        if final_score >= 0.60:
            decision = "approve"
            decision_label = "AUTO_APPROVE"
            reason = (
                f"Auto-approved. Disruption score ({disruption_score:.2f}) is high. "
                f"Behavior risk ({behavior_score:.2f}) is acceptable. "
                f"Final score: {final_score:.3f}."
            )
        elif final_score >= 0.40:
            decision = "review"
            decision_label = "REVIEW"
            reason = (
                f"Sent for review. Final score ({final_score:.3f}) is borderline. "
                f"Disruption: {disruption_score:.2f}, Behavior risk: {behavior_score:.2f}, "
                f"Past claims: {past_claims}."
            )
        else:
            decision = "reject"
            decision_label = "AUTO_REJECT"
            reason = (
                f"Auto-rejected. Final score ({final_score:.3f}) below threshold. "
                f"Disruption: {disruption_score:.2f}, Behavior risk: {behavior_score:.2f}, "
                f"Past claims: {past_claims}."
            )

        return {
            "decision": decision,
            "decision_label": decision_label,
            "final_score": final_score,
            "disruption_score": disruption_score,
            "behavior_score": behavior_score,
            "risk_weight": risk_weight,
            "past_claims": past_claims,
            "zone_risk": zone_risk,
            "reason": reason,
        }
