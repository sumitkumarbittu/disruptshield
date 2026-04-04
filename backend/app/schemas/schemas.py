"""
Pydantic schemas for all API request/response models.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ─── Rider Schemas ───────────────────────────────────────────

class RiderBase(BaseModel):
    rider_external_id: str
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    platform: str
    city: str
    pin_code: str
    zone: Optional[str] = None
    avg_weekly_income: float = 0.0


class RiderCreate(RiderBase):
    pass


class RiderResponse(RiderBase):
    id: int
    risk_score: float
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class RiderListResponse(BaseModel):
    riders: List[RiderResponse]
    total: int


# ─── Policy Schemas ──────────────────────────────────────────

class PolicyResponse(BaseModel):
    id: int
    rider_id: int
    policy_number: str
    status: str
    premium_amount: float
    coverage_amount: float
    city_tier: Optional[str] = None
    base_premium_pct: float
    effective_from: Optional[datetime] = None
    effective_to: Optional[datetime] = None
    is_active: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ─── Premium Schemas ─────────────────────────────────────────

class PremiumRecalcRequest(BaseModel):
    weekly_income: Optional[float] = None
    zone_risk: Optional[float] = None
    claim_history: Optional[int] = None
    risk_score: Optional[float] = None


class PremiumHistoryResponse(BaseModel):
    id: int
    rider_id: int
    previous_premium: Optional[float] = None
    new_premium: float
    change_reason: Optional[str] = None
    weekly_income: Optional[float] = None
    zone_risk: Optional[float] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ─── Claim Schemas ───────────────────────────────────────────

class ClaimSubmitRequest(BaseModel):
    rider_id: int
    disruption_event_id: int
    disruption_score: Optional[float] = None
    behavior_score: Optional[float] = None


class ClaimResponse(BaseModel):
    id: int
    rider_id: int
    disruption_event_id: Optional[int] = None
    claim_number: str
    status: str
    disruption_score: Optional[float] = None
    behavior_score: Optional[float] = None
    final_score: Optional[float] = None
    decision: Optional[str] = None
    payout_amount: Optional[float] = None
    reason: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ─── Payout Schemas ──────────────────────────────────────────

class PayoutResponse(BaseModel):
    id: int
    claim_id: int
    rider_id: int
    amount: float
    status: str
    transaction_ref: Optional[str] = None
    payment_method: Optional[str] = None
    processed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ─── DisruptionEvent Schemas ─────────────────────────────────

class DisruptionEventCreate(BaseModel):
    event_type: str = Field(..., description="heavy_rain / flood / aqi_spike / curfew")
    severity: str = Field(default="moderate", description="moderate / high / extreme")
    zone: str
    pin_code: Optional[str] = None
    city: Optional[str] = None
    disruption_score: float = Field(default=0.5, ge=0.0, le=1.0)
    description: Optional[str] = None
    duration_hours: Optional[float] = None
    severity_multiplier: Optional[float] = 0.5


class DisruptionEventResponse(BaseModel):
    id: int
    event_type: str
    severity: str
    zone: str
    pin_code: Optional[str] = None
    city: Optional[str] = None
    disruption_score: float
    description: Optional[str] = None
    duration_hours: Optional[float] = None
    severity_multiplier: float
    is_active: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ─── FusionDecision Schemas ──────────────────────────────────

class FusionDecisionResponse(BaseModel):
    id: int
    claim_id: int
    disruption_score: float
    behavior_score: float
    final_score: float
    decision: str
    reason: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ─── PostEventUpdate Schemas ─────────────────────────────────

class PostEventUpdateResponse(BaseModel):
    id: int
    rider_id: int
    claim_id: Optional[int] = None
    payout_id: Optional[int] = None
    update_type: str
    previous_risk_score: Optional[float] = None
    new_risk_score: Optional[float] = None
    previous_premium: Optional[float] = None
    new_premium: Optional[float] = None
    impact_summary: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ─── Dashboard Schemas ───────────────────────────────────────

class DashboardSummary(BaseModel):
    total_riders: int
    active_policies: int
    total_claims: int
    approved_claims: int
    rejected_claims: int
    review_claims: int
    total_payouts: float
    total_events: int
    active_events: int
    avg_premium: float
    avg_risk_score: float


# ─── Upload Schemas ──────────────────────────────────────────

class UploadResponse(BaseModel):
    riders_created: int
    policies_created: int
    errors: List[str]
