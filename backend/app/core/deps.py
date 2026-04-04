"""
Authentication dependencies — extract current user from JWT token.
Provides role-based access control middleware for FastAPI routes.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User
from app.models.admin_user import AdminUser

security_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: Session = Depends(get_db),
) -> dict:
    """
    Decode JWT and return the user payload.
    Works for both rider and admin tokens.
    """
    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    return payload


def require_rider(
    payload: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Dependency that requires the caller to be a rider."""
    if payload.get("role") != "rider":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Rider access required",
        )
    user = db.query(User).filter(User.id == payload.get("user_id")).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")
    return user


def require_admin(
    payload: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Dependency that requires the caller to be an admin."""
    if payload.get("role") not in ("admin", "superadmin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    admin = db.query(AdminUser).filter(AdminUser.id == payload.get("user_id")).first()
    if not admin or not admin.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Admin not found or inactive")
    return admin
