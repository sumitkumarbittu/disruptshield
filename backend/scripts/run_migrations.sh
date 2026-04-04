#!/bin/sh
# ── DisruptShield — Migration & Startup Script ──
# Waits for the database, runs Alembic migrations, then starts gunicorn.
# Used inside Docker container entrypoint.

set -e

echo "============================================"
echo "  DisruptShield — Backend Startup"
echo "============================================"

# ── Step 1: Wait for PostgreSQL ──
echo "⏳ Waiting for database to be ready..."

MAX_RETRIES=30
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    python3 -c "
from app.db.session import engine
from sqlalchemy import text
with engine.connect() as conn:
    conn.execute(text('SELECT 1'))
    print('✅ Database connection established.')
" 2>/dev/null && break

    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "  Attempt $RETRY_COUNT/$MAX_RETRIES — database not ready, retrying in 2s..."
    sleep 2
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "❌ Could not connect to database after $MAX_RETRIES attempts. Exiting."
    exit 1
fi

# ── Step 2: Run Alembic Migrations ──
echo ""
echo "⏳ Running database migrations..."
alembic upgrade head
echo "✅ Migrations complete."

# ── Step 3: Start Gunicorn ──
echo ""
echo "🚀 Starting DisruptShield backend..."
echo "============================================"
exec gunicorn main:app \
    -k uvicorn.workers.UvicornWorker \
    -w 2 \
    -b 0.0.0.0:8000 \
    --timeout 120 \
    --access-logfile -
