"""
Authentication API endpoints.
POST /auth/rider-login
POST /auth/admin-login
POST /auth/logout
GET  /auth/me
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.auth_service import AuthService
from app.core.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    role: str
    user_id: int
    email: str
    rider_id: int | None = None


class MeResponse(BaseModel):
    user_id: int
    email: str
    role: str
    rider_id: int | None = None


@router.post("/rider-login", response_model=TokenResponse)
def rider_login(request: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate a rider and return JWT token."""
    result = AuthService.rider_login(db, request.email, request.password)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    return result


@router.post("/admin-login", response_model=TokenResponse)
def admin_login(request: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate an admin and return JWT token."""
    result = AuthService.admin_login(db, request.email, request.password)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    return result


@router.post("/logout")
def logout():
    """
    Logout endpoint. JWT is stateless so the client simply discards the token.
    This endpoint exists for API completeness.
    """
    return {"message": "Logged out successfully. Discard the token on client side."}


@router.get("/me", response_model=MeResponse)
def get_me(payload: dict = Depends(get_current_user)):
    """Return the current authenticated user info from the JWT token."""
    return MeResponse(
        user_id=payload.get("user_id"),
        email=payload.get("email"),
        role=payload.get("role"),
        rider_id=payload.get("rider_id"),
    )
