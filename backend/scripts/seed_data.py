"""
Seed data script — isolated execution inside backend for initial setup.
Generates exactly 5000 riders and exactly 50 disruption events.
Must only be called if the database is empty.
"""

from app.db.session import SessionLocal
from app.services.data_generator import generate_riders
from app.services.event_generator import generate_events
from app.services.auth_service import AuthService
from app.models.rider import Rider


def run_seed():
    db = SessionLocal()
    try:
        # Check for existing data
        if db.query(Rider).count() > 0:
            print("Data already exists. Skipping seed script.")
            return False

        print("Generating 5000 riders in batches... (this may take a minute)")
        rider_res = generate_riders(db, count=5000, batch_size=500)
        print(f"✅ Generated {rider_res['total_riders_created']} riders. Avg Premium: {rider_res['avg_premium']}")

        print("Generating 50 verified AI-rule disruption events...")
        event_res = generate_events(db, count=50)
        print(f"✅ Generated {event_res['total_events_created']} events with {event_res['total_signals_created']} signals. Avg Score: {event_res['avg_disruption_score']:.3f}")

        print("Seeding default admin user (admin@disruptshield.in / admin123)...")
        try:
            admin = AuthService.create_admin_user(db, email="admin@disruptshield.in", password="admin123", role="superadmin")
            print("✅ Default admin created successfully.")
        except Exception as e:
            print(f"⚠️ Admin creation skipped or failed: {e}")

        print("✅ Data seeding complete.")
        return True
    except Exception as e:
        print(f"❌ Error during data seeding: {e}")
        db.rollback()
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    print("\n--- DisruptShield Database Seed Script ---")
    run_seed()
    print("------------------------------------------\n")
