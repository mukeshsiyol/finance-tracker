from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException, status
from jose import jwt, JWTError

from app.models import User
from app.database import SessionLocal
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

security = HTTPBearer()


def get_current_user_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") and payload.get("type") != "access":
            raise JWTError("Invalid token type")
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(
    payload=Depends(get_current_user_token),
):
    db = SessionLocal()
    user = db.query(User).filter(User.username == payload["sub"]).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


def require_role(required_role: str):
    def role_checker(user=Depends(get_current_user)):
        if user.role.value != required_role:
            raise HTTPException(
                status_code=403,
                detail="Access denied"
            )
        return user
    return role_checker
