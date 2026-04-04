# DisruptShield — Technical Documentation

## Architecture & Setup Guide

---

## 1. System Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React + Vite)                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │ Dashboard │ │  Upload  │ │  Riders  │ │  Claims  │ │  Events  │  │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘  │
│       └──────────────┴──────────────┴──────────────┴──────────┘      │
│                          API Client (Axios)                          │
└──────────────────────────────────────┬───────────────────────────────┘
                                       │ HTTP REST
┌──────────────────────────────────────┴───────────────────────────────┐
│                       BACKEND (FastAPI + Python)                     │
│                                                                      │
│  ┌─────────────────── API Layer (Routers) ────────────────────┐     │
│  │  riders │ policies │ premium │ claims │ payouts │ events │ dash │ │
│  └───────────────────────────┬────────────────────────────────┘     │
│                              │                                       │
│  ┌──────────── Service Layer ─────────────┐ ┌─── Engine Layer ──┐  │
│  │ RegistrationService                     │ │ FusionEngine      │  │
│  │ PolicyService                           │ │ (rule-based)      │  │
│  │ PremiumService                          │ └───────────────────┘  │
│  │ ClaimService                            │                        │
│  │ PayoutService                           │                        │
│  │ PostEventService ← Critical feedback    │                        │
│  │ DashboardService                        │                        │
│  └──────────────────┬─────────────────────┘                        │
│                     │                                                │
│  ┌──── Data Layer ──┴───────────────────────────────────────────┐   │
│  │  SQLAlchemy ORM │ Alembic Migrations │ PostgreSQL (Render)    │   │
│  │  10 Tables: riders, policies, premium_history, claims,        │   │
│  │  payouts, disruption_events, disruption_signals,              │   │
│  │  rider_behavior_logs, fusion_decisions, post_event_updates    │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  ┌──── Task Layer (Celery + Redis) ─ PLACEHOLDER ──────────────┐   │
│  │  Async claim processing │ Disruption polling │ Premium deduct │   │
│  └──────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 2. Database Schema

```
┌─────────────────┐     ┌─────────────────┐     ┌──────────────────┐
│     riders       │────<│    policies      │     │ premium_history  │
│─────────────────│     │─────────────────│     │──────────────────│
│ id (PK)         │     │ id (PK)         │     │ id (PK)          │
│ rider_external_id│    │ rider_id (FK)   │────>│ rider_id (FK)    │
│ name            │     │ policy_number   │     │ policy_id (FK)   │
│ phone           │     │ status          │     │ previous_premium │
│ email           │     │ premium_amount  │     │ new_premium      │
│ platform        │     │ coverage_amount │     │ change_reason    │
│ city            │     │ city_tier       │     │ weekly_income    │
│ pin_code        │     │ base_premium_pct│     │ zone_risk        │
│ zone            │     │ effective_from  │     │ created_at       │
│ avg_weekly_income│    │ is_active       │     └──────────────────┘
│ risk_score      │     │ created_at      │
│ is_active       │     └─────────────────┘
│ created_at      │
└────────┬────────┘
         │
    ┌────┴────────────────────────────────────────┐
    │                    │                         │
    ▼                    ▼                         ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────────────┐
│   claims      │   │   payouts    │   │ rider_behavior_logs  │
│──────────────│   │──────────────│   │──────────────────────│
│ id (PK)      │   │ id (PK)      │   │ id (PK)              │
│ rider_id (FK)│   │ claim_id (FK)│   │ rider_id (FK)        │
│ event_id (FK)│   │ rider_id (FK)│   │ log_type             │
│ claim_number │   │ amount       │   │ temporal_score       │
│ status       │   │ status       │   │ spatial_score        │
│ scores...    │   │ txn_ref      │   │ activity_score       │
│ decision     │   │ processed_at │   │ overall_score        │
│ payout_amount│   └──────────────┘   └──────────────────────┘
│ reason       │
└──────┬───────┘
       │
       ├──────────────────┐
       ▼                  ▼
┌────────────────┐  ┌───────────────────┐
│fusion_decisions│  │post_event_updates │
│────────────────│  │───────────────────│
│ id (PK)       │  │ id (PK)           │
│ claim_id (FK) │  │ rider_id (FK)     │
│ scores...     │  │ claim_id (FK)     │
│ risk_weight   │  │ payout_id (FK)    │
│ final_score   │  │ update_type       │
│ decision      │  │ prev/new risk     │
│ reason        │  │ prev/new premium  │
└────────────────┘  │ prev/new zone    │
                    │ impact_summary   │
                    └───────────────────┘

┌────────────────────┐    ┌──────────────────┐
│ disruption_events  │───<│disruption_signals│
│────────────────────│    │──────────────────│
│ id (PK)           │    │ id (PK)          │
│ event_type        │    │ event_id (FK)    │
│ severity          │    │ signal_type      │
│ zone              │    │ signal_value     │
│ disruption_score  │    │ normalized_value │
│ duration_hours    │    │ confidence       │
│ severity_mult     │    │ source           │
│ is_active         │    └──────────────────┘
└────────────────────┘
```

---

## 3. API Documentation

### Registration
| Method | Endpoint              | Description                    |
|--------|----------------------|--------------------------------|
| POST   | `/riders/upload_csv` | Upload CSV to bulk create riders & policies |
| GET    | `/riders`            | List all riders (paginated)    |
| GET    | `/riders/{rider_id}` | Get rider profile by ID        |

### Policies
| Method | Endpoint                          | Description                |
|--------|----------------------------------|----------------------------|
| GET    | `/policies/{rider_id}`           | Get active policy          |
| GET    | `/policies/{rider_id}/premium_history` | Premium change history |
| GET    | `/policies/{rider_id}/claims`    | Claim history              |
| GET    | `/policies/{rider_id}/payouts`   | Payout history             |

### Premium
| Method | Endpoint                          | Description              |
|--------|----------------------------------|--------------------------|
| POST   | `/premium/recalculate/{rider_id}` | Recalculate premium      |

### Claims
| Method | Endpoint              | Description                    |
|--------|----------------------|--------------------------------|
| POST   | `/claims/submit`     | Submit claim (runs fusion)     |
| GET    | `/claims/{rider_id}` | Get claims for a rider         |

### Payouts
| Method | Endpoint                     | Description                 |
|--------|-----------------------------|-----------------------------|
| POST   | `/payouts/process/{claim_id}` | Process payout (triggers post-event engine) |

### Events
| Method | Endpoint          | Description                  |
|--------|--------------------|------------------------------|
| POST   | `/events/create`  | Create disruption event      |
| GET    | `/events`         | List all events              |

### Dashboard
| Method | Endpoint              | Description              |
|--------|-----------------------|--------------------------|
| GET    | `/dashboard/summary` | Aggregated analytics     |

### Health
| Method | Endpoint    | Description |
|--------|------------|-------------|
| GET    | `/`        | App info    |
| GET    | `/health`  | Health check|

---

## 4. System Flow

```
CSV Upload
    │
    ▼
Riders Created ──> Policies Created ──> Initial Premium Calculated
                                            │
                                            ▼
                                    Premium History Logged
    
                    ┌──────────────────────────┐
                    │  Disruption Event Created │
                    │  (e.g., heavy rain)       │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │  Claim Submitted          │
                    │  rider_id + event_id      │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │  FUSION ENGINE            │
                    │  Score = D - (B × 0.60)   │
                    │  ≥0.60 → APPROVE          │
                    │  0.40-0.59 → REVIEW       │
                    │  <0.40 → REJECT           │
                    └────────────┬─────────────┘
                                 │
                          ┌──────┴──────┐
                          │             │
                    ┌─────┴─────┐ ┌─────┴─────┐
                    │  APPROVE  │ │  REJECT   │
                    └─────┬─────┘ └───────────┘
                          │
                          ▼
                    ┌──────────────────────────┐
                    │  PAYOUT PROCESSED         │
                    │  Mock wallet credit       │
                    └────────────┬─────────────┘
                                 │
                                 ▼
              ┌──────────────────────────────────────┐
              │  POST-PAYOUT ENGINE (Critical)       │
              │  1. Update rider risk score           │
              │  2. Update zone risk                  │
              │  3. Recalculate premium               │
              │  4. Log in post_event_updates         │
              │  5. Log premium change                │
              └──────────────────────────────────────┘
```

---

## 5. Environment Variables

| Variable         | Required | Default                              | Description                     |
|-----------------|----------|--------------------------------------|---------------------------------|
| `DATABASE_URL`  | ✅ Yes   | —                                    | PostgreSQL connection string    |
| `REDIS_URL`     | No       | `redis://localhost:6379/0`           | Redis for Celery (placeholder)  |
| `DEBUG`         | No       | `false`                              | Enable debug mode               |
| `CORS_ORIGINS`  | No       | `http://localhost:5173,...`           | Allowed CORS origins            |
| `VITE_API_URL`  | No       | `http://localhost:8000`              | Backend API URL for frontend    |

---

## 6. Setup Instructions

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL (or Render Postgres)

### Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and set your DATABASE_URL

# Run Alembic migrations
alembic revision --autogenerate -m "initial_migration"
alembic upgrade head

# Start the server
uvicorn main:app --reload --port 8000
```

### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

### Full System Test Flow
1. Start backend on port 8000
2. Start frontend on port 5173
3. Upload riders CSV via Upload page
4. Create a disruption event via Events page
5. Submit a claim via Claims page
6. Process payout via Payouts page (triggers post-event engine)
7. View dashboard for aggregated analytics
8. Check rider profile for updated risk score and premium

---

## 7. Fusion Engine Logic

```
Final Score = Disruption Score − (Behavior Risk Score × 0.60)

Decision Table:
  ≥ 0.60 → AUTO-APPROVE → Compute payout
  0.40 – 0.59 → REVIEW → Manual review queue
  < 0.40 → AUTO-REJECT → Log reason

Payout = min(hourly_estimate × duration_hours × severity_multiplier,
             weekly_income × 0.30)
```

---

## 8. Post-Payout Engine

After every payout, the system automatically:
1. **Updates rider risk score** — based on claim outcome
2. **Updates zone risk** — based on disruption severity
3. **Recalculates premium** — using new risk inputs
4. **Logs everything** — in `post_event_updates` table
5. **Logs premium change** — in `premium_history` table

This creates a complete feedback loop maintaining the event-aware architecture.
