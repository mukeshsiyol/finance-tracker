from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_user
from ..models import User
from ..schemas import LoginRequest, RegisterRequest, TokenResponse, AccessTokenResponse, UserOut, RefreshRequest
from ..services.auth_service import authenticate_user, register_user, create_access_token, create_refresh_token, verify_refresh_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserOut, status_code=201)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    #Register a new user (default role is 'viewer')
    return register_user(db, data)


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    #Authenticate user and return access and refresh tokens
    user = authenticate_user(db, data.username, data.password)
    access_token = create_access_token({
        "sub": user.username,
        "role": user.role.value
    })
    refresh_token = create_refresh_token({
        "sub": user.username,
        "role": user.role.value
    })

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=AccessTokenResponse)
def refresh(data: RefreshRequest, db: Session = Depends(get_db)):
    #Generate a new access token using a valid refresh token
    payload = verify_refresh_token(data.refresh_token)
    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    access_token = create_access_token({
        "sub": user.username,
        "role": user.role.value
    })

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=UserOut)
def me(current_user=Depends(get_current_user)):
    #Return the currently authenticated user's profile
    return current_user
