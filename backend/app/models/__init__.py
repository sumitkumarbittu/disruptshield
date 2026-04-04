"""
Central import point for all models.
Import this module to ensure all models are registered with SQLAlchemy.
"""

from app.models.rider import Rider
from app.models.policy import Policy
from app.models.premium_history import PremiumHistory
from app.models.claim import Claim
from app.models.payout import Payout
from app.models.disruption_event import DisruptionEvent
from app.models.disruption_signal import DisruptionSignal
from app.models.rider_behavior_log import RiderBehaviorLog
from app.models.fusion_decision import FusionDecision
from app.models.post_event_update import PostEventUpdate
from app.models.user import User
from app.models.admin_user import AdminUser

__all__ = [
    "Rider",
    "Policy",
    "PremiumHistory",
    "Claim",
    "Payout",
    "DisruptionEvent",
    "DisruptionSignal",
    "RiderBehaviorLog",
    "FusionDecision",
    "PostEventUpdate",
    "User",
    "AdminUser",
]
