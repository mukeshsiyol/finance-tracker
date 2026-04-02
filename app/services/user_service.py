from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..models import User, UserRole


def list_users(db: Session) -> list[User]:
    return db.query(User).order_by(User.id).all()


def get_user_by_id(db: Session, user_id: int) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id={user_id} not found.",
        )
    return user


def update_user_role(db: Session, user_id: int, new_role: UserRole, acting_user_id: int) -> User:
    if user_id == acting_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admins cannot change their own role.",
        )
    user = get_user_by_id(db, user_id)
    user.role = new_role
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int, acting_user_id: int) -> dict:
    if user_id == acting_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account.",
        )
    user = get_user_by_id(db, user_id)
    db.delete(user)
    db.commit()
    return {"detail": f"User {user_id} ({user.username}) deleted."}
