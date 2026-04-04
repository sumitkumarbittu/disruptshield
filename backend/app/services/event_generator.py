"""
Event Generator Service — generates 50 realistic disruption events
with AI-verified rule-based logic.

Rules:
  heavy_rain  → rainfall > 30 mm/hr
  flood       → rainfall > 50 AND traffic_index high
  high_aqi    → AQI > 250
  traffic_strike → traffic_index high AND order_drop high
  curfew      → order_drop > 70%
  platform_outage → order_drop > 80%
"""

import random
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.disruption_event import DisruptionEvent
from app.models.disruption_signal import DisruptionSignal


ALL_CITIES = [
    "Mumbai", "Chennai", "Kolkata",
    "Delhi", "Bengaluru", "Hyderabad",
    "Pune", "Ahmedabad", "Jaipur", "Lucknow", "Chandigarh",
]

EVENT_CONFIGS = {
    "heavy_rain": {
        "weight": 0.25,
        "rainfall_range": (31, 65),
        "aqi_range": (50, 180),
        "traffic_range": (0.3, 0.7),
        "order_drop_range": (20, 55),
    },
    "flood": {
        "weight": 0.12,
        "rainfall_range": (51, 90),
        "aqi_range": (80, 200),
        "traffic_range": (0.7, 1.0),
        "order_drop_range": (40, 75),
    },
    "high_aqi": {
        "weight": 0.18,
        "rainfall_range": (0, 10),
        "aqi_range": (251, 500),
        "traffic_range": (0.2, 0.5),
        "order_drop_range": (15, 45),
    },
    "traffic_strike": {
        "weight": 0.15,
        "rainfall_range": (0, 10),
        "aqi_range": (50, 200),
        "traffic_range": (0.7, 1.0),
        "order_drop_range": (50, 80),
    },
    "curfew": {
        "weight": 0.15,
        "rainfall_range": (0, 5),
        "aqi_range": (40, 150),
        "traffic_range": (0.5, 0.9),
        "order_drop_range": (71, 95),
    },
    "platform_outage": {
        "weight": 0.15,
        "rainfall_range": (0, 5),
        "aqi_range": (40, 150),
        "traffic_range": (0.1, 0.4),
        "order_drop_range": (81, 98),
    },
}


def _random_in(lo: float, hi: float) -> float:
    return round(random.uniform(lo, hi), 2)


def _compute_disruption_score(event_type: str, rainfall: float, aqi: float,
                               traffic_idx: float, order_drop: float) -> float:
    """Rule-based disruption score computation matched to event type."""
    score = 0.0

    if event_type == "heavy_rain":
        score = (
            0.40 * min(rainfall / 60.0, 1.0) +
            0.30 * (order_drop / 100.0) +
            0.20 * traffic_idx +
            0.10 * min(aqi / 400.0, 1.0)
        )
    elif event_type == "flood":
        score = (
            0.50 * min(rainfall / 80.0, 1.0) +
            0.25 * traffic_idx +
            0.25 * (order_drop / 100.0)
        )
    elif event_type == "high_aqi":
        score = (
            0.60 * min(aqi / 500.0, 1.0) +
            0.30 * (order_drop / 100.0) +
            0.10 * traffic_idx
        )
    elif event_type == "traffic_strike":
        score = (
            0.45 * traffic_idx +
            0.35 * (order_drop / 100.0) +
            0.20 * min(rainfall / 30.0, 1.0)
        )
    elif event_type == "curfew":
        score = (
            0.50 * (order_drop / 100.0) +
            0.35 * traffic_idx +
            0.15 * min(aqi / 300.0, 1.0)
        )
    elif event_type == "platform_outage":
        score = (
            0.70 * (order_drop / 100.0) +
            0.20 * traffic_idx +
            0.10 * min(rainfall / 30.0, 1.0)
        )

    return round(max(0.0, min(1.0, score)), 4)


def _severity_from_score(score: float) -> tuple[str, float]:
    """Determine severity label and multiplier from score."""
    if score >= 0.80:
        return "extreme", 1.0
    elif score >= 0.60:
        return "high", 0.75
    elif score >= 0.35:
        return "moderate", 0.5
    else:
        return "low", 0.25


def generate_events(db: Session, count: int = 50) -> dict:
    """
    Generate `count` realistic disruption events with signals.
    Returns summary statistics.
    """
    event_types = list(EVENT_CONFIGS.keys())
    weights = [EVENT_CONFIGS[t]["weight"] for t in event_types]

    created = 0
    signals_created = 0
    by_type = {}
    by_severity = {}
    total_score = 0.0

    for i in range(count):
        etype = random.choices(event_types, weights=weights, k=1)[0]
        cfg = EVENT_CONFIGS[etype]
        city = random.choice(ALL_CITIES)
        zone = f"{city.lower()}_zone_{random.randint(1, 8)}"

        # Generate signal values within rule-verified ranges
        rainfall = _random_in(*cfg["rainfall_range"])
        aqi = _random_in(*cfg["aqi_range"])
        traffic_idx = _random_in(*cfg["traffic_range"])
        order_drop = _random_in(*cfg["order_drop_range"])

        # Compute disruption score
        d_score = _compute_disruption_score(etype, rainfall, aqi, traffic_idx, order_drop)
        severity, sev_mult = _severity_from_score(d_score)

        # Timing
        start_time = datetime.now(timezone.utc) - timedelta(
            days=random.randint(0, 30),
            hours=random.randint(0, 12),
        )
        duration = round(random.uniform(2.0, 12.0), 1)
        end_time = start_time + timedelta(hours=duration)

        description = (
            f"{etype.replace('_', ' ').title()} event in {city} ({zone}). "
            f"Rainfall: {rainfall}mm/hr, AQI: {aqi}, Traffic: {traffic_idx:.2f}, "
            f"Order drop: {order_drop}%."
        )

        event = DisruptionEvent(
            event_type=etype,
            severity=severity,
            zone=zone,
            pin_code=str(random.randint(100000, 999999)),
            city=city,
            disruption_score=d_score,
            description=description,
            started_at=start_time,
            ended_at=end_time,
            duration_hours=duration,
            severity_multiplier=sev_mult,
            is_active=random.random() > 0.3,  # 70% still active
        )
        db.add(event)
        db.flush()

        # Insert signals for each event
        signal_defs = [
            ("rainfall", rainfall, min(rainfall / 60.0, 1.0), 0.90, "OpenWeatherMap"),
            ("aqi", aqi, min(aqi / 500.0, 1.0), 0.80, "OpenAQ"),
            ("traffic_index", traffic_idx * 100, traffic_idx, 0.75, "Google Maps"),
            ("order_drop", order_drop, order_drop / 100.0, 0.95, "Platform Webhook"),
        ]
        for sig_type, sig_val, norm_val, confidence, source in signal_defs:
            signal = DisruptionSignal(
                disruption_event_id=event.id,
                signal_type=sig_type,
                signal_value=round(sig_val, 2),
                normalized_value=round(norm_val, 4),
                confidence=confidence,
                source=source,
                raw_data=f"{sig_type}={sig_val:.2f}",
            )
            db.add(signal)
            signals_created += 1

        created += 1
        total_score += d_score
        by_type[etype] = by_type.get(etype, 0) + 1
        by_severity[severity] = by_severity.get(severity, 0) + 1

    db.commit()

    return {
        "total_events_created": created,
        "total_signals_created": signals_created,
        "avg_disruption_score": round(total_score / created, 4) if created else 0,
        "by_type": by_type,
        "by_severity": by_severity,
    }
