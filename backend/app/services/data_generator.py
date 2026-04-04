"""
Data Generator Service — generates 5000 realistic Indian rider records.
Uses Faker for names and deterministic ranges for financial data.
Inserts in batches of 500 for performance.
"""

import random
import uuid
from datetime import datetime, timezone

from faker import Faker
from sqlalchemy.orm import Session

from app.models.rider import Rider
from app.models.policy import Policy
from app.models.premium_history import PremiumHistory
from app.models.user import User
from app.core.security import hash_password

fake = Faker("en_IN")  # Indian locale

# ── City & zone configuration ──

TIER_1_CITIES = ["Mumbai", "Chennai", "Kolkata"]
TIER_2_CITIES = ["Delhi", "Bengaluru", "Hyderabad"]
TIER_3_CITIES = ["Pune", "Ahmedabad", "Jaipur", "Lucknow", "Chandigarh"]

CITY_TIER_MAP = {}
for c in TIER_1_CITIES:
    CITY_TIER_MAP[c] = "tier_1"
for c in TIER_2_CITIES:
    CITY_TIER_MAP[c] = "tier_2"
for c in TIER_3_CITIES:
    CITY_TIER_MAP[c] = "tier_3"

ALL_CITIES = TIER_1_CITIES + TIER_2_CITIES + TIER_3_CITIES

CITY_WEIGHTS = (
    [0.15, 0.10, 0.08]        # Tier 1: more riders
    + [0.14, 0.13, 0.10]      # Tier 2
    + [0.06, 0.06, 0.06, 0.06, 0.06]  # Tier 3
)

PLATFORMS = ["swiggy", "zomato"]

TIER_BASE_PREMIUM_PCT = {
    "tier_1": 2.5,
    "tier_2": 2.0,
    "tier_3": 1.5,
}

# Income bands per tier (weighted distribution)
INCOME_RANGES = {
    "tier_1": (1600, 4500),
    "tier_2": (1400, 3800),
    "tier_3": (1200, 3200),
}


def _generate_zone(city: str) -> str:
    """Generate a zone ID for a city like 'mumbai_zone_3'."""
    zone_num = random.randint(1, 8)
    return f"{city.lower()}_zone_{zone_num}"


def _generate_income(tier: str) -> float:
    """Generate realistic weekly income using a beta distribution within tier range."""
    low, high = INCOME_RANGES.get(tier, (1200, 3200))
    # Beta distribution skews towards lower-mid range (realistic for delivery workers)
    raw = random.betavariate(2.5, 3.0)
    income = low + raw * (high - low)
    return round(income, 2)


def _generate_risk_score() -> float:
    """Risk score 0.1–0.9, weighted towards lower risk (most riders are low risk)."""
    raw = random.betavariate(2.0, 5.0)
    score = 0.1 + raw * 0.8
    return round(score, 4)


def _calc_premium(weekly_income: float, tier: str, risk_score: float) -> float:
    """Calculate premium: 1.5%–3% of weekly income based on tier and risk."""
    base_pct = TIER_BASE_PREMIUM_PCT.get(tier, 1.5)
    risk_adj = risk_score * 0.5  # small risk adjustment
    pct = base_pct + risk_adj
    pct = max(1.5, min(3.0, pct))  # clamp to 1.5%–3%
    return round((pct / 100.0) * weekly_income, 2)


def generate_riders(db: Session, count: int = 5000, batch_size: int = 500) -> dict:
    """
    Generate `count` rider records with policies and premium history.
    Inserts in batches for performance. Also creates user accounts.
    Returns a summary dict.
    """
    total_created = 0
    total_policies = 0
    total_premium = 0.0
    total_income = 0.0
    errors = []

    # Pre-generate a default password hash (all generated riders get same default password)
    default_pwd_hash = hash_password("rider123")

    for batch_start in range(0, count, batch_size):
        batch_end = min(batch_start + batch_size, count)

        for i in range(batch_start, batch_end):
            try:
                city = random.choices(ALL_CITIES, weights=CITY_WEIGHTS, k=1)[0]
                tier = CITY_TIER_MAP[city]
                platform = random.choice(PLATFORMS)
                income = _generate_income(tier)
                risk = _generate_risk_score()
                zone = _generate_zone(city)

                ext_id = f"{platform[:3].upper()}-{i+1:05d}"
                name = fake.name()
                phone = fake.phone_number()
                email = f"rider{i+1}@disruptshield.in"

                rider = Rider(
                    rider_external_id=ext_id,
                    name=name,
                    phone=phone,
                    email=email,
                    platform=platform,
                    city=city,
                    pin_code=str(random.randint(100000, 999999)),
                    zone=zone,
                    avg_weekly_income=income,
                    risk_score=risk,
                    is_active=True,
                )
                db.add(rider)
                db.flush()

                # Create policy
                premium = _calc_premium(income, tier, risk)
                coverage = round(income * 0.30, 2)

                policy = Policy(
                    rider_id=rider.id,
                    policy_number=f"DS-POL-{uuid.uuid4().hex[:8].upper()}",
                    status="active",
                    premium_amount=premium,
                    coverage_amount=coverage,
                    city_tier=tier,
                    base_premium_pct=TIER_BASE_PREMIUM_PCT[tier],
                    effective_from=datetime.now(timezone.utc),
                    is_active=True,
                )
                db.add(policy)
                db.flush()

                # Premium history
                ph = PremiumHistory(
                    rider_id=rider.id,
                    policy_id=policy.id,
                    previous_premium=0.0,
                    new_premium=premium,
                    change_reason="initial",
                    weekly_income=income,
                    zone_risk=0.5,
                    claim_history_count=0,
                    risk_score=risk,
                )
                db.add(ph)

                # Create user account for login
                user = User(
                    rider_id=rider.id,
                    email=email,
                    password_hash=default_pwd_hash,
                    role="rider",
                    is_active=True,
                )
                db.add(user)

                total_created += 1
                total_policies += 1
                total_premium += premium
                total_income += income

            except Exception as e:
                errors.append(f"Rider {i+1}: {str(e)}")

        # Commit each batch
        db.commit()

    avg_premium = round(total_premium / total_created, 2) if total_created else 0
    avg_income = round(total_income / total_created, 2) if total_created else 0

    return {
        "total_riders_created": total_created,
        "total_policies_created": total_policies,
        "avg_premium": avg_premium,
        "avg_income": avg_income,
        "batch_size": batch_size,
        "errors_count": len(errors),
        "errors": errors[:10],  # return first 10 errors only
    }
