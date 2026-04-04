"""
DisruptShield — FastAPI Application Entry Point
Parametric Income Protection for Food Delivery Partners
"""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import app.db.session as app_db_session

from app.core.config import settings
from app.api import riders, policies, premium, claims, payouts, events, dashboard, auth, admin

# Import all models so they are registered with SQLAlchemy
import app.models  # noqa: F401


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Parametric Income Protection Platform for Delivery Workers",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS middleware
    origins = [o.strip() for o in settings.CORS_ORIGINS.split(",")]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routers
    app.include_router(riders.router)
    app.include_router(policies.router)
    app.include_router(premium.router)
    app.include_router(claims.router)
    app.include_router(payouts.router)
    app.include_router(events.router)
    app.include_router(dashboard.router)
    app.include_router(auth.router)
    app.include_router(admin.router)

    # Required health checks for Render Platform constraints
    @app.get("/health", tags=["Health"])
    def basic_health_check():
        return {"api_status": "healthy"}

    @app.get("/health/db", tags=["Health"])
    def db_health_check(db=Depends(app_db_session.get_db)):
        try:
            db.execute(app_db_session.text("SELECT 1"))
            return {"db_status": "connected"}
        except Exception as e:
            return {"db_status": "disconnected", "error": str(e)}

    @app.get("/health/system", tags=["Health"])
    def system_health_check(db=Depends(app_db_session.get_db)):
        from app.models.rider import Rider
        from app.models.disruption_event import DisruptionEvent
        from app.models.claim import Claim
        from app.models.payout import Payout
        
        try:
            total_riders = db.query(Rider).count()
            total_events = db.query(DisruptionEvent).count()
            total_claims = db.query(Claim).count()
            total_payouts = db.query(Payout).count()
            
            return {
                "api_status": "healthy",
                "db_status": "connected",
                "metrics": {
                    "total_riders": total_riders,
                    "total_events": total_events,
                    "total_claims": total_claims,
                    "total_payouts": total_payouts
                }
            }
        except Exception as e:
            return {"api_status": "healthy", "db_status": "disconnected", "error": str(e)}

    return app


app = create_app()
