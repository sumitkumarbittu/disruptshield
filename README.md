# DisruptShield — Parametric Income Protection Platform

> Event-aware, AI-verified parametric insurance for food delivery partners.

---

## 📐 Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     DisruptShield System                        │
├──────────────┬──────────────────┬───────────────────────────────┤
│   Frontend   │     Backend      │         Database              │
│  React SPA   │  FastAPI + JWT   │  PostgreSQL (Render Postgres) │
│  (nginx)     │  (gunicorn)      │                               │
│  Port: 3000  │  Port: 8000      │  Port: 5432                   │
└──────────────┴──────────────────┴───────────────────────────────┘
```

### Docker Architecture

```
docker-compose.yml
├── postgres       (postgres:15-alpine)    → Port 5432
│   └── Volume: pgdata (persistent)
├── backend        (python:3.11-slim)      → Port 8000
│   ├── Alembic migrations on startup
│   └── Gunicorn + Uvicorn workers
└── frontend       (node:18 → nginx:alpine) → Port 3000
    ├── Build stage: npm run build
    └── Serve stage: nginx with SPA routing
```

### System Flow

```
Riders Onboarded → Policies Created → Premium Calculated
        ↓
Disruption Events Detected (rain/flood/AQI/strike/curfew/outage)
        ↓
Claims Submitted → Fusion Engine Decision (approve/review/reject)
        ↓
Payout Processed → Post-Payout Engine → Risk Updated → Premium Recalculated
```

---

## 🚀 Quick Start (Local Docker)

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- Git

### Step 1 — Clone Repository

```bash
git clone https://github.com/sumitkumarbittu/disruptshield.git
cd disruptshield
```

### Step 2 — Create Environment File

A `.env` file is included with safe local defaults. Review and adjust if needed:

```bash
cat .env
```

Key variables:
| Variable | Default | Description |
|---|---|---|
| `POSTGRES_DB` | `disruptshield` | Database name |
| `POSTGRES_USER` | `dsuser` | Database user |
| `POSTGRES_PASSWORD` | `dspassword` | Database password |
| `SECRET_KEY` | `disruptshield-local-dev-...` | JWT signing secret |
| `VITE_API_URL` | `http://localhost:8000` | API URL for frontend build |

### Step 3 — Build & Start All Services

```bash
docker-compose up --build
```

This will:
1. Start PostgreSQL with persistent volume
2. Wait for database to be healthy
3. Run Alembic migrations automatically
4. Start the FastAPI backend on port 8000
5. Build and serve the React frontend on port 3000

### Step 4 — Seed Data (One Time Only)

Open a new terminal and run:

```bash
# Seed 5000 riders + 50 events + default admin user
docker exec disruptshield-backend python -m scripts.seed_data
```

### Step 5 — Access the Application

| Service | URL |
|---|---|
| **Frontend** | [http://localhost:3000](http://localhost:3000) |
| **Backend API** | [http://localhost:8000](http://localhost:8000) |
| **API Docs (Swagger)** | [http://localhost:8000/docs](http://localhost:8000/docs) |
| **Health Check** | [http://localhost:8000/health](http://localhost:8000/health) |
| **System Health** | [http://localhost:8000/health/system](http://localhost:8000/health/system) |

### Default Login Credentials

| Role | Email | Password |
|---|---|---|
| **Admin** | `admin@disruptshield.in` | `admin123` |
| **Rider** | `rider1@disruptshield.in` | `rider123` |

---

## 🐳 Docker Commands Reference

```bash
# Build and start all services
docker-compose up --build

# Start in background (detached)
docker-compose up -d

# Stop all services
docker-compose down

# Stop and remove volumes (reset database)
docker-compose down -v

# Rebuild a specific service
docker-compose build backend
docker-compose build frontend

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres

# Run migrations manually
docker exec disruptshield-backend alembic upgrade head

# Seed data
docker exec disruptshield-backend python -m scripts.seed_data

# Open a shell in backend container
docker exec -it disruptshield-backend /bin/sh

# Connect to PostgreSQL
docker exec -it disruptshield-db psql -U dsuser -d disruptshield
```

---

## 🌐 Render Deployment Guide

### Option A — Backend as Web Service + Frontend as Static Site (Recommended)

#### Backend Deployment

1. **Create a Render Web Service**
   - Connect your GitHub repository
   - Set **Root Directory**: `backend`
   - Set **Environment**: `Docker`
   - Render will auto-detect the `Dockerfile`

2. **Set Environment Variables** on Render:

   | Variable | Value |
   |---|---|
   | `DATABASE_URL` | Your Render Postgres **Internal URL** (starts with `postgresql://`) |
   | `JWT_SECRET_KEY` | A strong random secret (use `openssl rand -hex 32`) |
   | `JWT_ALGORITHM` | `HS256` |
   | `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | `480` |
   | `ENVIRONMENT` | `production` |
   | `FRONTEND_URL` | `https://your-frontend.onrender.com` |
   | `CORS_ORIGINS` | `https://your-frontend.onrender.com` |

3. **Create a Render PostgreSQL Database**
   - Copy the **Internal Database URL**
   - Set it as `DATABASE_URL` in the backend service

4. **After first deploy**, run migrations and seed:
   ```bash
   # Via Render Shell (Dashboard → Shell tab)
   alembic upgrade head
   python -m scripts.seed_data
   ```

5. **Health Check Path**: Set to `/health` in Render dashboard

#### Frontend Deployment

1. **Create a Render Static Site**
   - Connect the same GitHub repository
   - Set **Root Directory**: `frontend`
   - Set **Build Command**: `npm install && npm run build`
   - Set **Publish Directory**: `dist`

2. **Set Environment Variable**:

   | Variable | Value |
   |---|---|
   | `VITE_API_URL` | `https://your-backend.onrender.com` |

### Option B — Both as Docker Web Services

#### Backend
Same as Option A above.

#### Frontend as Web Service

1. **Create a Render Web Service** (not Static Site)
   - Set **Root Directory**: `frontend`
   - Set **Environment**: `Docker`
   - Render auto-detects the multi-stage `Dockerfile`

2. **Set Build Arg** in Render:
   - Add Docker build arg: `VITE_API_URL=https://your-backend.onrender.com`

3. The nginx container will serve the built React app on port 80

> **Note**: Option A is recommended for Render Free Tier since Static Sites
> don't consume web service slots.

---

## 🔐 Authentication Flow

```
User → Login Page → Select Role (Rider/Admin)
  ↓
POST /auth/rider-login  OR  POST /auth/admin-login
  ↓
Backend verifies credentials → Returns JWT token
  ↓
Frontend stores token in localStorage (key: ds_token)
  ↓
All API calls include: Authorization: Bearer <token>
  ↓
Backend verifies JWT on protected routes
```

- Tokens expire after 8 hours (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`)
- Passwords are hashed with bcrypt (never stored in plaintext)
- Tokens are **NOT** stored in cookies — Bearer tokens only
- Role-based access: `require_rider` and `require_admin` dependencies

---

## 🗄️ Database Migrations

### Generate a New Migration

```bash
# Local (without Docker)
cd backend
alembic revision --autogenerate -m "describe_change"

# Docker
docker exec disruptshield-backend alembic revision --autogenerate -m "describe_change"
```

### Apply Migrations

```bash
# Local
alembic upgrade head

# Docker
docker exec disruptshield-backend alembic upgrade head

# Render (via Shell tab)
alembic upgrade head
```

### Rollback

```bash
alembic downgrade -1
```

---

## 🌱 Seed Data Guide

The seed script generates:
- **5000 riders** with realistic Indian names, tiered cities, beta-distributed incomes
- **5000 policies** with calculated premiums (1.5%–3% of weekly income)
- **5000 premium history** records
- **5000 user accounts** for rider login
- **50 disruption events** (rain, flood, AQI, strike, curfew, outage)
- **200 disruption signals** (4 per event)
- **1 admin user** (admin@disruptshield.in / admin123)

### Running the Seed

```bash
# Docker
docker exec disruptshield-backend python -m scripts.seed_data

# Local
cd backend
python -m scripts.seed_data

# Via protected API (requires admin JWT)
curl -X POST https://your-backend/admin/seed-data \
  -H "Authorization: Bearer <admin-jwt-token>"
```

> **Safety**: The seed script checks if riders already exist.
> It will **not** duplicate data on repeated runs.

---

## 🔧 Environment Variables Reference

### Backend Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `DATABASE_URL` | ✅ | — | PostgreSQL connection string |
| `JWT_SECRET_KEY` | ✅ | `disruptshield-secret...` | JWT signing key |
| `JWT_ALGORITHM` | No | `HS256` | JWT algorithm |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | No | `480` | Token TTL in minutes |
| `ENVIRONMENT` | No | `production` | `development` or `production` |
| `FRONTEND_URL` | No | `https://...onrender.com` | Frontend origin for CORS |
| `CORS_ORIGINS` | No | `http://localhost:5173,...` | Comma-separated allowed origins |

### Frontend Variables

| Variable | Required | Description |
|---|---|---|
| `VITE_API_URL` | ✅ | Backend API base URL (compile-time) |
| `REACT_APP_API_URL` | No | Alternative env key (Vite-compatible) |

### Docker Compose Variables

| Variable | Default | Description |
|---|---|---|
| `POSTGRES_DB` | `disruptshield` | Database name |
| `POSTGRES_USER` | `dsuser` | Database username |
| `POSTGRES_PASSWORD` | `dspassword` | Database password |

---

## 🏥 Health Endpoints

| Endpoint | Returns |
|---|---|
| `GET /health` | `{"api_status": "healthy"}` |
| `GET /health/db` | Database connection status |
| `GET /health/system` | API status + DB status + rider/event/claim/payout counts |

Use `/health` as the **Render health check path** for uptime monitoring.

---

## 🐛 Troubleshooting

### Database connection refused
```
ERROR: connection refused to postgres:5432
```
**Fix**: Ensure the `postgres` service is healthy before backend starts. Docker Compose handles this via `depends_on: condition: service_healthy`.

### Migrations fail on startup
```
alembic.util.exc.CommandError: Can't locate revision
```
**Fix**: Reset the Alembic version table:
```bash
docker exec disruptshield-db psql -U dsuser -d disruptshield -c "DROP TABLE IF EXISTS alembic_version;"
docker exec disruptshield-backend alembic upgrade head
```

### Frontend shows blank page
**Fix**: Ensure `VITE_API_URL` was set at **build time** (not runtime). Rebuild:
```bash
docker-compose build frontend
docker-compose up -d frontend
```

### CORS errors in browser
**Fix**: Add your frontend URL to `CORS_ORIGINS` in the backend environment:
```
CORS_ORIGINS=http://localhost:3000,https://your-frontend.onrender.com
```

### Render service sleeps (Free Tier)
**Expected behavior**: Render Free Tier services spin down after 15 minutes of inactivity. First request after sleep takes ~30s. Use [UptimeRobot](https://uptimerobot.com/) to ping `/health` every 14 minutes.

### bcrypt version warning
```
error reading bcrypt version
```
**Not critical**: This is a passlib compatibility warning with bcrypt 4.x. Authentication still works correctly.

### Seed data fails with duplicate key
**Fix**: Data already exists. The seed script is idempotent — it checks for existing riders before inserting.

---

## 📁 Project Structure

```
disruptshield/
├── docker-compose.yml          # Local development stack
├── .env                        # Environment variables
├── README.md                   # This file
├── TECHNICAL_DOCS.md           # Detailed technical documentation
│
├── backend/
│   ├── Dockerfile              # Production backend container
│   ├── .dockerignore
│   ├── requirements.txt        # Python dependencies
│   ├── main.py                 # FastAPI entry point
│   ├── alembic.ini             # Alembic configuration
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/           # Migration files
│   ├── app/
│   │   ├── core/
│   │   │   ├── config.py       # Pydantic settings
│   │   │   ├── security.py     # JWT + bcrypt utilities
│   │   │   └── deps.py         # Auth dependencies
│   │   ├── db/
│   │   │   ├── base.py         # Declarative base
│   │   │   └── session.py      # Engine + session factory
│   │   ├── models/             # SQLAlchemy models (10 tables)
│   │   ├── schemas/            # Pydantic request/response schemas
│   │   ├── services/           # Business logic layer
│   │   ├── engines/            # Fusion engine
│   │   └── api/                # FastAPI routers
│   └── scripts/
│       ├── seed_data.py        # One-time data generation
│       └── run_migrations.sh   # Docker startup script
│
└── frontend/
    ├── Dockerfile              # Multi-stage frontend container
    ├── .dockerignore
    ├── nginx.conf              # SPA routing configuration
    ├── package.json
    ├── vite.config.js
    ├── index.html
    └── src/
        ├── api/client.js       # Axios API client + JWT interceptor
        ├── hooks/useApi.js     # Data fetching hook
        ├── components/         # Sidebar, Loading
        └── pages/              # All application pages
```

---

## 🚢 Production Deployment Flow

```
Step 1:  Push code to GitHub
            ↓
Step 2:  Create Render PostgreSQL database
            ↓
Step 3:  Create Render Web Service (backend)
         - Docker environment
         - Set env vars (DATABASE_URL, JWT_SECRET_KEY, etc.)
         - Health check path: /health
            ↓
Step 4:  Backend auto-deploys, runs migrations
            ↓
Step 5:  Seed data via Render Shell:
         python -m scripts.seed_data
            ↓
Step 6:  Create Render Static Site (frontend)
         - Build: npm install && npm run build
         - Publish: dist
         - Set VITE_API_URL
            ↓
Step 7:  Frontend deploys, connects to backend
            ↓
Step 8:  System is live!
         Admin login → Manage events/claims
         Rider login → View premium/payouts
```

---

## 📝 License

MIT — Built for educational and demonstration purposes.
