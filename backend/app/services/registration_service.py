"""
Registration Service — handles CSV upload, rider creation, and auto policy creation.
"""

import csv
import io
import uuid
from datetime import datetime, timezone
from typing import Tuple, List

from sqlalchemy.orm import Session

from app.models.rider import Rider
from app.models.policy import Policy
from app.models.premium_history import PremiumHistory
from app.services.premium_service import PremiumService


class RegistrationService:
    """Handles rider registration from CSV and auto-creates policies."""

    CITY_TIER_MAP = {
        "mumbai": "tier_1", "chennai": "tier_1", "kolkata": "tier_1",
        "delhi": "tier_2", "bengaluru": "tier_2", "hyderabad": "tier_2", "bangalore": "tier_2",
        "pune": "tier_3", "ahmedabad": "tier_3", "jaipur": "tier_3",
    }

    TIER_BASE_PREMIUM_PCT = {
        "tier_1": 2.5,
        "tier_2": 2.0,
        "tier_3": 1.5,
    }

    @staticmethod
    def parse_csv(file_content: bytes) -> Tuple[List[dict], List[str]]:
        """Parse CSV content and return list of rider dicts + errors."""
        errors = []
        riders_data = []
        try:
            decoded = file_content.decode("utf-8")
            reader = csv.DictReader(io.StringIO(decoded))
            for i, row in enumerate(reader, start=2):  # row 1 is header
                try:
                    rider_data = {
                        "rider_external_id": row.get("rider_id", "").strip(),
                        "name": row.get("name", "").strip(),
                        "phone": row.get("phone", "").strip(),
                        "email": row.get("email", "").strip(),
                        "platform": row.get("platform", "").strip().lower(),
                        "city": row.get("city", "").strip(),
                        "pin_code": row.get("pin_code", "").strip(),
                        "zone": row.get("zone", "").strip() or row.get("pin_code", "").strip(),
                        "avg_weekly_income": float(row.get("avg_weekly_income", 0)),
                    }
                    if not rider_data["rider_external_id"] or not rider_data["name"]:
                        errors.append(f"Row {i}: Missing rider_id or name")
                        continue
                    riders_data.append(rider_data)
                except (ValueError, KeyError) as e:
                    errors.append(f"Row {i}: {str(e)}")
        except Exception as e:
            errors.append(f"CSV parse error: {str(e)}")
        return riders_data, errors

    @classmethod
    def get_city_tier(cls, city: str) -> str:
        return cls.CITY_TIER_MAP.get(city.lower(), "tier_3")

    @classmethod
    def create_riders_and_policies(cls, db: Session, riders_data: List[dict]) -> Tuple[int, int, List[str]]:
        """Create riders and their policies from parsed CSV data."""
        riders_created = 0
        policies_created = 0
        errors = []

        for data in riders_data:
            try:
                # Check if rider already exists
                existing = db.query(Rider).filter(
                    Rider.rider_external_id == data["rider_external_id"]
                ).first()
                if existing:
                    errors.append(f"Rider {data['rider_external_id']} already exists, skipped")
                    continue

                # Create rider
                rider = Rider(**data)
                db.add(rider)
                db.flush()  # Get the ID
                riders_created += 1

                # Determine city tier and base premium
                city_tier = cls.get_city_tier(data["city"])
                base_pct = cls.TIER_BASE_PREMIUM_PCT.get(city_tier, 1.5)

                # Calculate initial premium
                premium_amount = PremiumService.calculate_premium(
                    weekly_income=data["avg_weekly_income"],
                    zone_risk=0.5,
                    claim_history=0,
                    risk_score=0.0,
                    base_premium_pct=base_pct,
                )

                # Create policy
                policy = Policy(
                    rider_id=rider.id,
                    policy_number=f"DS-POL-{uuid.uuid4().hex[:8].upper()}",
                    status="active",
                    premium_amount=premium_amount,
                    coverage_amount=data["avg_weekly_income"] * 0.30,
                    city_tier=city_tier,
                    base_premium_pct=base_pct,
                    effective_from=datetime.now(timezone.utc),
                    is_active=True,
                )
                db.add(policy)
                db.flush()
                policies_created += 1

                # Log initial premium
                premium_log = PremiumHistory(
                    rider_id=rider.id,
                    policy_id=policy.id,
                    previous_premium=0.0,
                    new_premium=premium_amount,
                    change_reason="initial",
                    weekly_income=data["avg_weekly_income"],
                    zone_risk=0.5,
                    claim_history_count=0,
                    risk_score=0.0,
                )
                db.add(premium_log)

            except Exception as e:
                errors.append(f"Rider {data.get('rider_external_id', '?')}: {str(e)}")

        db.commit()
        return riders_created, policies_created, errors
