# DisruptShield
### Parametric Income Protection for Food Delivery Partners

> *You showed up. The rain didn't stop you — the orders did. DisruptShield makes sure you never go home empty-handed because of it.*

---

## Table of Contents

1. [The Problem](#1-the-problem)
2. [The Business Model](#2-the-business-model)
3. [How It Works — User-Facing Flow](#3-how-it-works--user-facing-flow)
4. [System Architecture](#4-system-architecture)
5. [External Disruption Engine](#5-external-disruption-engine)
6. [Behavioral Profiling Engine](#6-behavioral-profiling-engine)
7. [Fusion & Decision Engine](#7-fusion--decision-engine)
8. [AI Oversight Layer](#8-ai-oversight-layer)
9. [Cap System — Sustainability by Design](#9-cap-system--sustainability-by-design)
10. [Premium Model](#10-premium-model)
11. [Tech Stack](#11-tech-stack)
12. [Project Structure](#12-project-structure)
13. [API Reference](#13-api-reference)
14. [Pilot Plan](#14-pilot-plan)
15. [Unit Economics](#15-unit-economics)

---

## 1. The Problem

Every disruption — heavy rain, AQI spikes, curfews, floods — silently costs delivery partners 20–30% of their weekly income. There is no warning, no claim process, and no safety net.

For platforms like Swiggy and Zomato, this creates a supply crisis at exactly the worst time: when customer demand is highest (monsoon surges, post-flood order spikes), rider availability collapses. Riders who can't count on earning can't count on staying.

**The cost of doing nothing:**

| Problem | Platform Impact | Rider Impact |
|---|---|---|
| Disruption drops supply | Order cancellation rate spikes | ₹300–₹800 income lost per event |
| Riders churn after bad weeks | ₹800–₹2,000 replacement cost per rider | No safety net, no alternatives |
| Manual claim systems | High fraud, high ops cost | Slow, demoralizing |

DisruptShield solves both sides with one embedded system: a small weekly premium (₹18–₹35) that pays out automatically when a verified disruption occurs and the rider was genuinely present and working.

---

## 2. The Business Model

### 2.1 Distribution: B2B2C — Platform-Embedded

DisruptShield is **not a standalone insurance app**. It is embedded inside Swiggy and Zomato as a retention and welfare feature. The platform pays no upfront license fee — the product funds itself through rider premiums collected at source (weekly earnings deduction).

```
Platform (Swiggy / Zomato)
        │
        │  Weekly premium auto-deducted from rider earnings
        ▼
  DisruptShield Engine
        │
        │  Verified payout credited to rider wallet
        ▼
  Delivery Partner
```

**Why platforms adopt it:**

- Retaining one rider costs ₹18–₹35/week
- Replacing one rider costs ₹800–₹2,000
- During monsoon, rider churn spikes 18–25%
- DisruptShield is a measurable retention lever, not a charity program

**Why riders opt in:**

- ₹18–₹35/week is less than one skipped order
- No claim forms — automatic
- Wallet credit same day as disruption
- No bureaucracy, no rejection surprises

---

### 2.2 Revenue Model

| Stream | Description | Margin |
|---|---|---|
| Premium float | Weekly premiums collected, held until payout or expiry | ~60–70% retained in non-disruption weeks |
| Platform SaaS fee | ₹2–₹5 per active rider/week for analytics dashboard + compliance reporting | High margin |
| Unused premium reinvestment | Float invested in liquid instruments (RBI-compliant) | Incremental |

**Actuarial logic:** DisruptShield is parametric — payouts are triggered by verified external events, not subjective claims. This makes the loss ratio predictable and modelable from day one.

---

### 2.3 Why This Is Not Insurance (Yet)

DisruptShield operates as a **parametric income stabilization scheme**, not a regulated insurance product, during the pilot phase. This avoids IRDAI licensing friction while proving unit economics. The architecture is built to upgrade to a licensed product once actuarial data is validated.

---

## 3. How It Works — User-Facing Flow

```
Step 1 — Weekly Premium Collected
  ₹18–₹35 auto-deducted from rider earnings each Monday.
  No action required. No opt-in friction beyond one-time enrollment.

Step 2 — Disruption Detected
  External Disruption Engine monitors weather (rain, flood), AQI,
  traffic closure, and curfew signals in real time.
  A Disruption Score (0–1) is computed for each zone.

Step 3 — Behavior Validated
  Behavioral Profiling Engine checks GPS trail, order history,
  and session data to confirm the rider was present and working
  during the disruption window.

Step 4 — Payout Triggered
  Fusion Engine combines both scores.
  AI Oversight Layer validates the decision.
  Wallet credited same day. No claim form. No call center.
```

---

## 4. System Architecture

### 4.1 Four-Engine Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                     DisruptShield Core                      │
│                                                             │
│  [External Disruption Engine]                               │
│         │  Disruption Score (0–1)                          │
│         ▼                                                   │
│  [Behavioral Profiling Engine]                              │
│         │  Risk Score (0–1)                                │
│         ▼                                                   │
│  [Fusion & Decision Engine]                                 │
│         │  Final Score + Decision                          │
│         ▼                                                   │
│  [AI Oversight Layer]  ──────────────────────── RETRY loop │
│         │                                                   │
│         ▼                                                   │
│  APPROVE / REVIEW / REJECT → Payout / Queue / Dismiss      │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 Layer Summary

| Layer | Engine | Input | Output |
|---|---|---|---|
| L1 | Premium Engine | Rider tier, city, claims history | Weekly premium (₹) |
| L2 | External Disruption Engine | Weather, AQI, traffic, news APIs | Disruption Score 0–1 |
| L3 | Behavioral Profiling Engine | GPS, orders, session logs | Risk Score 0–1 |
| L4 | Fusion + AI Oversight | L2 + L3 scores | Final decision + reason |

---

## 5. External Disruption Engine

The disruption engine answers one question: **Did an objective, verifiable external event reduce the ability to earn in this zone today?**

It does not ask the rider. It does not rely on self-reporting. It pulls from external sources and scores them independently.

### 5.1 Data Sources

| Signal | Source | Refresh Rate |
|---|---|---|
| Rainfall (mm/hr) | OpenWeatherMap API | Every 10 minutes |
| Flood alerts | IMD + NDMA RSS feeds | Every 30 minutes |
| AQI | OpenAQ API + CPCB scrape | Every 15 minutes |
| Road closures | Google Maps Directions API (congestion delta) | Every 15 minutes |
| Curfew / strike | NewsAPI + Google News RSS scrape | Every 30 minutes |
| Platform order drop | Internal Swiggy/Zomato webhook (zone-level) | Real-time |

### 5.2 Signal Processing

Each raw signal passes through three stages before being used in scoring:

**Stage 1 — Normalization**

All signals are normalized to a 0–1 scale using thresholds derived from 3 years of historical IMD data.

```python
# Example: Rainfall normalization
def normalize_rain(mm_per_hour: float) -> float:
    """
    0    mm/hr → 0.0  (no disruption)
    15   mm/hr → 0.3  (moderate)
    35   mm/hr → 0.7  (heavy — triggers threshold)
    60+  mm/hr → 1.0  (extreme)
    """
    thresholds = [(0, 0.0), (15, 0.3), (35, 0.7), (60, 1.0)]
    return interpolate_linear(mm_per_hour, thresholds)
```

**Stage 2 — Confidence Scoring**

Each signal is assigned a confidence score based on source reliability and data freshness.

```python
confidence_weights = {
    "openweather_rain":  0.90,   # High — API, real-time
    "imd_flood_alert":   0.85,   # High — official gov source
    "openaq_aqi":        0.80,   # High — API
    "google_traffic":    0.75,   # Medium — inferred from routing
    "news_curfew":       0.60,   # Medium — text classification required
    "platform_orderdrop": 0.95,  # Highest — direct behavioral signal
}
```

**Stage 3 — Disruption Score Aggregation**

```
D = Σ ( signal_value × signal_weight × confidence )
      normalized to [0, 1]
```

Signal weights are set per disruption type:

| Disruption Type | Primary Signals | Secondary Signals |
|---|---|---|
| Heavy Rain | Rainfall (0.40), Order Drop (0.30) | Traffic (0.20), AQI (0.10) |
| Flood | Flood Alert (0.50), Traffic (0.25) | Order Drop (0.25) |
| AQI Spike | AQI (0.60), Order Drop (0.30) | News (0.10) |
| Curfew/Strike | News (0.50), Traffic (0.35) | Order Drop (0.15) |

### 5.3 Zone-Level Scoring

Disruption is scored at **PIN code zone level** (not city level). A flood in one zone does not trigger payouts in another zone 10 km away. Zone assignment uses rider's last known GPS position during the disruption window (±90 min).

### 5.4 Disruption Score Thresholds

| Score Range | Label | System Action |
|---|---|---|
| 0.0 – 0.35 | None | No disruption event created |
| 0.35 – 0.60 | Moderate | Event logged, behavioral check triggered |
| 0.60 – 0.80 | High | Auto-eligible, behavioral check triggered |
| 0.80 – 1.00 | Extreme | Auto-eligible, expedited behavioral check |

### 5.5 Multi-Source Conflict Resolution

When signals disagree (e.g., OpenWeather shows heavy rain but order drop is low), the engine applies a conflict flag:

```python
if max_signal - min_signal > 0.4:
    flag_conflict = True
    # Defer to highest-confidence source
    # Pass conflict flag to AI Oversight Layer
```

---

## 6. Behavioral Profiling Engine

The behavioral engine answers one question: **Was this rider genuinely present and working during the disruption window — and is this a legitimate claimant?**

This is the anti-fraud layer. A disruption score of 0.90 means nothing if the rider was at home or their GPS was spoofed.

### 6.1 Data Inputs

| Input | Source | Purpose |
|---|---|---|
| GPS trail | Rider app (sampled every 5 min) | Presence verification |
| Orders attempted | Platform order log | Activity verification |
| Session start/end | App session timestamps | Online time validation |
| Order completion rate | Platform log | Genuine effort vs. idle |
| Historical claim count | DisruptShield DB | Fraud pattern detection |
| Device fingerprint | App metadata | Multi-account detection |
| Peer behavior | Zone-level aggregate | Mass fraud detection |

### 6.2 Validation Dimensions

**Dimension 1 — Temporal Validation**

Was the rider online and active during the disruption window (±90 min of peak disruption)?

```python
online_overlap_score = overlap_minutes(session_window, disruption_window) / disruption_window_minutes
# Required minimum: 0.40 (at least 40% of disruption window active)
```

**Dimension 2 — Spatial Validation**

Was the rider's GPS position within the disrupted zone?

```python
def spatial_score(gps_trail: List[Coordinate], disrupted_zone: GeoPolygon) -> float:
    points_in_zone = [p for p in gps_trail if disrupted_zone.contains(p)]
    return len(points_in_zone) / len(gps_trail)
# Required minimum: 0.50 (majority of GPS pings within disrupted zone)
```

GPS anomaly detection runs in parallel:
- Speed > 120 km/h between consecutive pings → spoofing flag
- Teleportation (>5 km in <2 min) → spoofing flag
- Static GPS (same coord for >60 min while "active") → spoofing flag

**Dimension 3 — Activity Validation**

Did the rider make genuine delivery attempts?

```python
activity_score = (
    0.40 * (orders_attempted / expected_orders_in_disruption_window) +
    0.30 * (session_minutes / disruption_window_minutes) +
    0.30 * (1 - idle_ratio)  # idle = online but no movement for >20 min
)
```

**Dimension 4 — Group / Mass Fraud Detection**

If >60% of riders in the same zone claim the same disruption window with >0.95 behavioral similarity, the system flags a potential coordinated fraud attempt.

```python
zone_claim_rate = active_claimants_in_zone / total_active_riders_in_zone
if zone_claim_rate > 0.60:
    flag_mass_fraud = True
    # Escalate to manual review queue regardless of individual scores
```

**Dimension 5 — Historical Behavior**

Riders with prior claim anomalies receive a risk surcharge on their behavior risk score:

| Prior History | Risk Adjustment |
|---|---|
| 0 prior claims | 0.00 (baseline) |
| 1–2 approved claims | -0.05 (trusted) |
| 1 rejected claim | +0.10 |
| 2+ rejected claims | +0.25 |
| Fraud flag on file | +0.50 (near-certain rejection) |

**Dimension 6 — Device Fingerprint**

DisruptShield checks for multiple accounts sharing the same device:

```python
if count(device_id) > 1:
    flag_multi_account = True
    risk_score += 0.30
```

### 6.3 Risk Score Computation

```
Risk Score = weighted_average(
    temporal_score     × 0.25,
    spatial_score      × 0.25,
    activity_score     × 0.25,
    historical_score   × 0.15,
    device_score       × 0.10
) + fraud_flags_penalty
```

### 6.4 Risk Score Thresholds

| Risk Score | Label | System Action |
|---|---|---|
| 0.0 – 0.25 | Low Risk | Pass to Fusion Engine |
| 0.25 – 0.50 | Moderate Risk | Pass with warning flag |
| 0.50 – 0.75 | High Risk | Escalate to manual review |
| 0.75 – 1.00 | Fraud Suspected | Auto-reject, flag account |

---

## 7. Fusion & Decision Engine

The fusion engine combines the disruption score and behavioral risk score into a single final decision.

### 7.1 Core Formula

```
Final Score = Disruption Score − (Behavior Risk Score × risk_weight)
```

Default `risk_weight = 0.60`. This weight is tunable per city/season after actuarial calibration.

**Example — Flood Event, Low-Risk Rider:**
```
Disruption Score = 0.82  (flood detected, road closures active)
Behavior Risk    = 0.21  (120 rides prior month, 0 prior claims, GPS valid)
Final Score      = 0.82 − (0.21 × 0.60) = 0.694 → AUTO-APPROVE
```

**Example — Rain Event, High-Risk Rider:**
```
Disruption Score = 0.55  (moderate rain)
Behavior Risk    = 0.72  (2 prior rejected claims, GPS anomaly)
Final Score      = 0.55 − (0.72 × 0.60) = 0.118 → AUTO-REJECT
```

### 7.2 Decision Table

| Final Score | Decision | Action |
|---|---|---|
| ≥ 0.60 | AUTO-APPROVE | Compute payout, pass to AI Oversight |
| 0.40 – 0.59 | REVIEW | Pass to AI Oversight for edge analysis |
| < 0.40 | AUTO-REJECT | Reject, log reason, notify rider |

### 7.3 Payout Computation

Payout is computed as a function of estimated income loss, capped at every stage (see Section 9):

```python
def compute_payout(rider: Rider, disruption: DisruptionEvent) -> float:
    estimated_hourly = rider.avg_hourly_earnings_last_4_weeks
    disruption_hours = disruption.duration_hours
    raw_loss = estimated_hourly × disruption_hours
    
    # Apply disruption severity multiplier (0.5 for moderate, 1.0 for extreme)
    adjusted_loss = raw_loss × disruption.severity_multiplier
    
    # Apply payout cap (30% of weekly income)
    weekly_income = rider.avg_weekly_earnings_last_4_weeks
    payout = min(adjusted_loss, weekly_income × 0.30)
    
    return round(payout, 2)
```

---

## 8. AI Oversight Layer

The AI Oversight Layer is a language model acting as a final auditor. It reviews decisions that are borderline, conflicted, or involve unusual signals before they are finalized.

### 8.1 When It Activates

The AI Oversight Layer activates on any of these conditions:

- Final Score in the REVIEW band (0.40–0.59)
- Disruption signals are conflicting (conflict flag from Section 5.5)
- First-time extreme disruption event type (novel event, no historical baseline)
- Mass fraud flag raised (Section 6.2, Dimension 4)
- Payout exceeds ₹500 (high-value review trigger)

It does **not** activate on clean AUTO-APPROVE or AUTO-REJECT decisions. This keeps compute cost bounded.

### 8.2 LLM Prompt Architecture

The model receives a structured JSON payload — never raw logs — containing:

```json
{
  "disruption": {
    "score": 0.72,
    "type": "heavy_rain",
    "signals": {
      "rainfall_mm_hr": 42,
      "order_drop_pct": 38,
      "road_closures": true
    },
    "conflict_flag": false
  },
  "behavior": {
    "risk_score": 0.48,
    "temporal_overlap": 0.71,
    "spatial_score": 0.63,
    "activity_score": 0.55,
    "prior_claims": 1,
    "prior_rejections": 0,
    "fraud_flags": []
  },
  "fusion_score": 0.43,
  "proposed_decision": "REVIEW",
  "payout_amount": 310
}
```

The model is instructed to:

1. Validate logical consistency between disruption evidence and behavioral evidence
2. Identify any anomalies not captured by numeric scoring
3. Return a structured decision with a human-readable reason

### 8.3 Output Schema

```json
{
  "decision": "APPROVE" | "REJECT" | "RETRY",
  "confidence": 0.0–1.0,
  "reason": "Heavy rain confirmed. Rider GPS shows 71% zone overlap. Single prior approved claim — no fraud risk.",
  "override_flag": false
}
```

### 8.4 Self-Correcting Loop

```python
def ai_oversight_loop(payload: dict, max_retries: int = 2) -> Decision:
    for attempt in range(max_retries + 1):
        result = llm_judge(payload)
        if result.decision == "RETRY":
            payload["retry_context"] = result.reason
            continue
        return result
    # If RETRY persists after max attempts, escalate to human queue
    return escalate_to_human(payload)
```

### 8.5 Model Used

- **Model:** Claude claude-sonnet-4-20250514 (via Anthropic API)
- **Invocation:** Only on flagged decisions (not every claim)
- **Latency budget:** 3 seconds max; if exceeded, fallback to rule-based decision
- **Cost control:** Estimated 1–5% of all claims reach AI Oversight; ~₹0.10–₹0.25 per AI call

---

## 9. Cap System — Sustainability by Design

Every financial exposure in DisruptShield is bounded by a hard cap. The system cannot pay out more than it collected, and cannot be exploited by a single rider, zone, or event at any scale.

### 9.1 Four-Level Cap Architecture

```
Level 1 — Premium Cap
  Maximum weekly premium = 3.5% of weekly earnings
  Prevents unaffordable deductions for low-income riders

Level 2 — Payout Cap (Per Rider, Per Event)
  Maximum single payout = 30% of rider's 4-week average weekly income
  Prevents windfall claims from inflated loss estimates

Level 3 — Event Cap (Per Zone, Per Disruption Event)
  Maximum total payout for one disruption event in one zone
  = [active enrolled riders in zone] × [avg weekly income] × 0.15
  Prevents a single catastrophic event from exhausting the fund

Level 4 — City Exposure Cap
  Total payouts in any city in any calendar month
  ≤ 25% of total premiums collected from that city in the prior 8 weeks
  Maintains a minimum reserve buffer at all times
```

### 9.2 Reserve Fund Rules

| Metric | Threshold | Action |
|---|---|---|
| Reserve / 8-week premium < 50% | Warning | Increase new-enrollment premium by 10% |
| Reserve / 8-week premium < 35% | Alert | Pause new enrollments in that city |
| Reserve / 8-week premium < 20% | Critical | Cap all payouts at 50% of computed amount until restored |

### 9.3 NCB (No-Claim Bonus) System

Riders who do not claim for 8 consecutive weeks receive a 10% premium reduction, capped at 25% total reduction. This incentivizes genuine use and reduces adverse selection.

---

## 10. Premium Model

### 10.1 Base Premium by City Tier

| City Tier | Example Cities | Base Premium (% of weekly income) |
|---|---|---|
| Tier 1 — High Disruption | Mumbai, Chennai, Kolkata | 2.5% |
| Tier 2 — Medium Disruption | Delhi, Bengaluru, Hyderabad | 2.0% |
| Tier 3 — Low Disruption | Pune, Ahmedabad, Jaipur | 1.5% |

Weekly income bands (approximate, Swiggy/Zomato data):

| Rider Income Band | Weekly Income | Tier 1 Premium | Tier 2 Premium |
|---|---|---|---|
| Low | ₹1,200–₹1,800 | ₹30–₹45 | ₹24–₹36 |
| Mid | ₹1,800–₹2,800 | ₹45–₹70 | ₹36–₹56 |
| High | ₹2,800–₹4,500 | ₹70–₹112 | ₹56–₹90 |

### 10.2 Dynamic Adjustment

Premium is recalculated weekly using:

```
Weekly Premium = Base% × avg_weekly_income_last_4_weeks
              + NCB_surcharge (if recent claims exist)
              − NCB_discount (if no claims for 8+ weeks)
              Hard cap: max(premium, 3.5% × weekly_income)
```

---

## 11. Tech Stack

All technology choices are project-specific, battle-tested, and scoped to a 4-person engineering team. No infrastructure-level components are listed — only application-layer tools that map directly to project modules.

### 11.1 Backend — Core API

| Component | Technology | Why |
|---|---|---|
| API framework | **FastAPI (Python 3.11)** | Async-native, OpenAPI docs auto-generated, fast |
| Task queue | **Celery + Redis** | Async disruption scoring, payout jobs |
| Scheduler | **APScheduler** | Periodic API polling (weather, AQI every 10–15 min) |
| ORM | **SQLAlchemy 2.0 + Alembic** | Type-safe queries, schema migrations |

### 11.2 Data Ingestion

| Component | Technology | Why |
|---|---|---|
| Weather | **OpenWeatherMap API** (httpx async client) | Real-time rain, flood data |
| AQI | **OpenAQ REST API** | Free, reliable, Indian city coverage |
| Traffic | **Google Maps Directions API** | Road closure detection via congestion delta |
| News/Curfew | **NewsAPI + Scrapy** | Text-based disruption detection |
| Platform webhook | **FastAPI webhook endpoint** | Receives Swiggy/Zomato order-drop events |

### 11.3 Disruption Engine

| Component | Technology | Why |
|---|---|---|
| Signal processing | **NumPy + Pandas** | Fast vectorized signal normalization |
| Zone mapping | **Shapely + GeoPandas** | GPS point-in-polygon for zone assignment |
| Score aggregation | **Pure Python (weighted avg)** | No ML needed; rule-based, auditable |

### 11.4 Behavioral Profiling Engine

| Component | Technology | Why |
|---|---|---|
| GPS validation | **Shapely** (spatial ops) | Point containment, spoofing detection |
| Anomaly detection | **scikit-learn IsolationForest** | Unsupervised GPS/session anomaly detection |
| Fraud scoring | **XGBoost (binary classifier)** | Trained on historical labeled fraud cases |
| Feature store | **Redis Hash** | Fast per-rider feature lookups during scoring |

### 11.5 AI Oversight Layer

| Component | Technology | Why |
|---|---|---|
| LLM | **Claude claude-sonnet-4-20250514 (Anthropic API)** | Structured output, low latency, cost-efficient |
| Prompt management | **Jinja2 templates** | Version-controlled prompts, easy A/B testing |
| Fallback | **Rule-based decision tree** | If LLM times out or returns RETRY ×2 |

### 11.6 Database Layer

| Component | Technology | Purpose |
|---|---|---|
| Primary DB | **PostgreSQL 15** | Riders, claims, payouts, premiums |
| Event log | **MongoDB 7.0** | Raw signal logs, GPS trails, audit events |
| Cache | **Redis 7.2** | Session state, feature store, rate limits |

### 11.7 Frontend

| Component | Technology | Purpose |
|---|---|---|
| Admin dashboard | **React 18 + Vite + TailwindCSS** | Claim queue, zone map, analytics |
| Rider mobile | **Flutter 3** | Premium status, payout history, notifications |

### 11.8 Payments

| Component | Technology | Note |
|---|---|---|
| Wallet credit | **Razorpay Payouts API** | Instant wallet credit, test mode for pilot |
| Premium deduction | **Platform payroll hook** | Weekly deduction via Swiggy/Zomato earnings API |

### 11.9 Testing & Quality

| Component | Technology | Purpose |
|---|---|---|
| Unit tests | **pytest + pytest-asyncio** | All engine logic, scoring functions |
| API tests | **HTTPX + pytest** | Full endpoint coverage |
| Load testing | **Locust** | Simulate 500 concurrent rider scoring |
| Synthetic data | **Faker + custom simulator** | Generate realistic DP scenarios for testing |

---

## 12. Project Structure

```
disruptshield/
├── api/
│   ├── main.py                  # FastAPI app entry point
│   ├── routers/
│   │   ├── riders.py            # Rider enrollment, profile
│   │   ├── claims.py            # Claim lifecycle
│   │   ├── payouts.py           # Payout trigger + Razorpay
│   │   └── webhooks.py          # Platform order-drop webhook
│   └── dependencies.py          # Auth, DB session
│
├── engines/
│   ├── disruption/
│   │   ├── sources/
│   │   │   ├── weather.py       # OpenWeatherMap client
│   │   │   ├── aqi.py           # OpenAQ client
│   │   │   ├── traffic.py       # Google Maps client
│   │   │   └── news.py          # NewsAPI + Scrapy spider
│   │   ├── normalizer.py        # Signal → 0–1 normalization
│   │   ├── scorer.py            # Disruption score aggregation
│   │   └── zone_mapper.py       # GPS → zone assignment (Shapely)
│   │
│   ├── behavioral/
│   │   ├── temporal.py          # Session overlap scoring
│   │   ├── spatial.py           # GPS validation + spoofing detection
│   │   ├── activity.py          # Order/idle scoring
│   │   ├── fraud_detector.py    # XGBoost fraud classifier
│   │   ├── group_detector.py    # Mass fraud detection
│   │   └── risk_scorer.py       # Final risk score aggregation
│   │
│   ├── fusion/
│   │   ├── engine.py            # Final Score formula
│   │   ├── payout_calculator.py # Loss estimate + cap logic
│   │   └── decision.py          # APPROVE / REVIEW / REJECT
│   │
│   └── oversight/
│       ├── llm_judge.py         # Anthropic API call + structured output
│       ├── prompts/
│       │   └── judge_v1.j2      # Jinja2 prompt template
│       ├── retry_loop.py        # RETRY handling
│       └── fallback.py          # Rule-based fallback
│
├── models/
│   ├── rider.py                 # SQLAlchemy Rider model
│   ├── claim.py                 # Claim + status lifecycle
│   ├── disruption_event.py      # DisruptionEvent model
│   └── payout.py                # Payout record
│
├── tasks/
│   ├── celery_app.py            # Celery config + Redis broker
│   ├── poll_disruption.py       # Scheduled: every 10–15 min
│   ├── process_claims.py        # Async claim processing queue
│   └── weekly_premium.py        # Monday: deduct premiums
│
├── simulator/
│   ├── dp_generator.py          # Synthetic rider data (Faker)
│   ├── scenarios/
│   │   ├── normal_week.py
│   │   ├── rain_disruption.py
│   │   ├── fraud_attempt.py
│   │   └── mass_claim.py
│   └── api.py                   # Simulator endpoints
│
├── tests/
│   ├── unit/
│   │   ├── test_disruption_scorer.py
│   │   ├── test_behavioral_risk.py
│   │   └── test_fusion_engine.py
│   ├── integration/
│   │   └── test_claim_pipeline.py
│   └── load/
│       └── locustfile.py
│
├── migrations/                  # Alembic migrations
├── config.py                    # Environment-based config (Pydantic Settings)
├── requirements.txt
└── README.md
```

---

## 13. API Reference

### Rider Enrollment

```http
POST /api/v1/riders/enroll
Content-Type: application/json

{
  "rider_id": "ZOM-4923",
  "platform": "zomato",
  "city": "Mumbai",
  "pin_code": "400001",
  "avg_weekly_income": 2400
}
```

Response:
```json
{
  "enrollment_id": "DS-ENR-0041",
  "weekly_premium": 48,
  "effective_from": "2026-03-24",
  "tier": "tier_1"
}
```

---

### Disruption Score Query

```http
GET /api/v1/disruption/score?zone=400001&platform=zomato
```

Response:
```json
{
  "zone": "400001",
  "score": 0.82,
  "label": "extreme",
  "type": "flood",
  "active_since": "2026-03-21T14:30:00Z",
  "signals": {
    "rainfall_mm_hr": 58,
    "flood_alert": true,
    "road_closures": 3,
    "order_drop_pct": 44
  },
  "confidence": 0.91
}
```

---

### Claim Processing

```http
POST /api/v1/claims/process
Content-Type: application/json

{
  "rider_id": "ZOM-4923",
  "disruption_event_id": "DE-2026-0341",
  "session_start": "2026-03-21T14:00:00Z",
  "session_end": "2026-03-21T17:30:00Z"
}
```

Response (async — returns job ID):
```json
{
  "claim_id": "CLM-0819",
  "status": "processing",
  "estimated_completion": "2026-03-21T17:35:00Z"
}
```

---

### Claim Status

```http
GET /api/v1/claims/CLM-0819/status
```

Response:
```json
{
  "claim_id": "CLM-0819",
  "status": "approved",
  "decision": "AUTO_APPROVE",
  "disruption_score": 0.82,
  "risk_score": 0.21,
  "final_score": 0.694,
  "payout_amount": 340,
  "payout_status": "credited",
  "reason": "Flood event confirmed. Rider GPS validated in zone. No prior fraud flags."
}
```

---

### Simulator Endpoints

```http
POST /simulator/dp              # Generate synthetic rider with scenario
GET  /simulator/dp/{id}/weekly  # Get weekly summary for synthetic rider
GET  /simulator/stream          # Server-sent event stream of simulated claims
```

---

## 14. Pilot Plan

**500 riders. One city. Four weeks. One monsoon.**

### Phase 1 — Pre-Pilot (Week 0)

- Onboard one platform (Zomato or Swiggy) via API partnership agreement
- Enroll 500 riders in one Tier 1 city (Mumbai recommended — highest disruption frequency)
- Collect baseline 2-week premium (no payouts) to establish initial reserve
- Validate all engine outputs against simulator-generated ground truth

### Phase 2 — Live Pilot (Weeks 1–4)

- Real disruption events processed end-to-end
- All payouts capped to 15% of reserve per event (conservative for pilot)
- Daily review of AI Oversight decisions by human analyst
- Weekly actuarial report: claims vs. premiums, loss ratio, fraud rate

### Phase 3 — Evaluation (Week 5)

| Metric | Target | Green |
|---|---|---|
| Loss ratio (payouts / premiums) | < 70% | < 55% |
| Fraud rejection rate | > 95% of fraud attempts blocked | > 98% |
| Rider satisfaction (post-payout survey) | > 80% positive | > 90% |
| Payout latency (disruption → wallet) | < 6 hours | < 3 hours |
| AI Oversight false positive rate | < 5% | < 2% |

---

## 15. Unit Economics

### Per-Rider Weekly (Tier 1 City, Mid-Income Rider)

| Item | Amount |
|---|---|
| Weekly premium collected | ₹52 |
| Expected claims (actuarial — 1 event per 6 weeks) | ₹340 / 6 = ₹57 expected weekly cost |
| Premium float (non-claim weeks) | ₹52 retained |
| Net margin (non-disruption weeks) | ~₹42–₹47 (after ops cost) |

**At scale (10,000 enrolled riders, Tier 1):**

| Item | Monthly |
|---|---|
| Premium collected | ₹20.8L |
| Expected payouts (assuming 1 major event/month) | ₹8–₹12L |
| Platform SaaS fee | ₹4–₹8L |
| Gross contribution | ₹12–₹17L/month |

### Platform ROI

| Item | Cost |
|---|---|
| DisruptShield per rider per week | ₹18–₹35 |
| Rider replacement cost (churn) | ₹800–₹2,000 |
| Break-even (DisruptShield prevents 1 churn per N riders) | N = 23–57 riders |

At any churn reduction of even 5% during monsoon season (typical 18–25% churn), DisruptShield pays for itself across the enrolled rider base.

---

## Summary

DisruptShield is not a claims system. It is a parametric income stabilization engine that operates transparently, automatically, and at scale — with every decision traceable to verifiable external data and validated behavioral signals.

**For riders:** ₹18–₹35 a week buys same-day income protection without a single form to fill.

**For platforms:** A sub-₹35/week retention lever prevents ₹800–₹2,000 replacement costs at the worst possible time.

**For the system:** Hard caps at every stage — premium, payout, event, city — ensure sustainability is built in, not bolted on.

> *You showed up. We've got you.*

---

*DisruptShield — Parametric Income Protection for Food Delivery Partners*
*Pilot launch: Monsoon 2026 | Target: 500 riders, 1 city, 4 weeks*
