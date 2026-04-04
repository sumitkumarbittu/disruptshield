"""
Authentication service — handles rider login, admin login, and user creation.
"""

from sqlalchemy.orm import Session
from typing import Optional

from app.models.user import User
from app.models.admin_user import AdminUser
from app.core.security import hash_password, verify_password, create_access_token


class AuthService:
    """Handles authentication logic for riders and admins."""

    # ── Rider Auth ──

    @staticmethod
    def create_rider_user(db: Session, email: str, password: str, rider_id: int) -> User:
        """Create a new rider user account."""
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            raise ValueError(f"User with email {email} already exists")

        user = User(
            rider_id=rider_id,
            email=email,
            password_hash=hash_password(password),
            role="rider",
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def rider_login(db: Session, email: str, password: str) -> Optional[dict]:
        """Authenticate a rider. Returns token dict or None."""
        user = db.query(User).filter(User.email == email, User.role == "rider").first()
        if not user or not user.is_active:
            return None
        if not verify_password(password, user.password_hash):
            return None

        token = create_access_token({
            "user_id": user.id,
            "rider_id": user.rider_id,
            "email": user.email,
            "role": "rider",
        })
        return {
            "access_token": token,
            "token_type": "bearer",
            "role": "rider",
            "user_id": user.id,
            "rider_id": user.rider_id,
            "email": user.email,
        }

    # ── Admin Auth ──

    @staticmethod
    def create_admin_user(db: Session, email: str, password: str, role: str = "admin") -> AdminUser:
        """Create a new admin user account."""
        existing = db.query(AdminUser).filter(AdminUser.email == email).first()
        if existing:
            raise ValueError(f"Admin with email {email} already exists")

        admin = AdminUser(
            email=email,
            password_hash=hash_password(password),
            role=role,
            is_active=True,
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        return admin

    @staticmethod
    def admin_login(db: Session, email: str, password: str) -> Optional[dict]:
        """Authenticate an admin. Returns token dict or None."""
        admin = db.query(AdminUser).filter(AdminUser.email == email).first()
        if not admin or not admin.is_active:
            return None
        if not verify_password(password, admin.password_hash):
            return None

        token = create_access_token({
            "user_id": admin.id,
            "email": admin.email,
            "role": admin.role,
        })
        return {
            "access_token": token,
            "token_type": "bearer",
            "role": admin.role,
            "user_id": admin.id,
            "email": admin.email,
        }

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_admin_by_id(db: Session, admin_id: int) -> Optional[AdminUser]:
        return db.query(AdminUser).filter(AdminUser.id == admin_id).first()
