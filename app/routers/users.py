from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import require_admin
from ..models import User
from ..schemas import UserOut, UserRoleUpdate
from ..services import user_service as svc

router = APIRouter(prefix="/users", tags=["Users (Admin)"])


@router.get("/", response_model=list[UserOut])
def list_users(
    db: Session = Depends(get_db),
    _: User     = Depends(require_admin),
):
    """List all users. **Admin only.**"""
    return svc.list_users(db)


@router.get("/{user_id}", response_model=UserOut)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    _:  User    = Depends(require_admin),
):
    """Fetch a single user by ID. **Admin only.**"""
    return svc.get_user_by_id(db, user_id)


@router.patch("/{user_id}/role", response_model=UserOut)
def change_user_role(
    user_id:      int,
    data:         UserRoleUpdate,
    db:           Session = Depends(get_db),
    current_user: User    = Depends(require_admin),
):
    """Change a user's role. **Admin only.** Admins cannot change their own role."""
    return svc.update_user_role(db, user_id, data.role, current_user.id)


@router.delete("/{user_id}")
def delete_user(
    user_id:      int,
    db:           Session = Depends(get_db),
    current_user: User    = Depends(require_admin),
):
    """Delete a user. **Admin only.** Cannot self-delete."""
    return svc.delete_user(db, user_id, current_user.id)
