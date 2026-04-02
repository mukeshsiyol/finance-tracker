from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import create_access_token, get_current_user
from ..schemas import LoginRequest, RegisterRequest, TokenResponse, UserOut
from ..services.auth_service import authenticate_user, register_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserOut, status_code=201)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user. Default role is 'viewer'."""
    return register_user(db, data)


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate and receive a JWT bearer token."""
    user  = authenticate_user(db, data.username, data.password)
    token = create_access_token({"sub": user.id, "role": user.role})
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserOut)
def me(current_user=Depends(get_current_user)):
    """Return the currently authenticated user's profile."""
    return current_user
