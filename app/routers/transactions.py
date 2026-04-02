from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import require_admin, require_analyst_plus, require_viewer_plus
from ..models import TransactionType, User, UserRole
from ..schemas import TransactionCreate, TransactionOut, TransactionUpdate
from ..services import transaction_service as svc

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.get("/", response_model=list[TransactionOut])
def list_transactions(
    tx_type:    Optional[TransactionType] = Query(None,  alias="type",       description="Filter by income or expense"),
    category:   Optional[str]            = Query(None,                       description="Filter by category name (partial match)"),
    start_date: Optional[date]            = Query(None,                       description="Filter from this date (YYYY-MM-DD)"),
    end_date:   Optional[date]            = Query(None,                       description="Filter up to this date (YYYY-MM-DD)"),
    skip:       int                       = Query(0,     ge=0,                description="Pagination offset"),
    limit:      int                       = Query(50,    ge=1, le=200,        description="Max records to return"),
    db:         Session                   = Depends(get_db),
    current_user: User                    = Depends(require_viewer_plus),
):
    """
    List transactions with optional filters.
    - **Viewers** can list without filters.
    - **Analysts and Admins** can use all filter parameters.
    """
    # Restrict filter usage to analyst+ roles
    if current_user.role == UserRole.viewer and any([tx_type, category, start_date, end_date]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Viewers cannot apply filters. Upgrade to Analyst role for filtering.",
        )
    return svc.list_transactions(db, current_user, tx_type, category, start_date, end_date, skip, limit)


@router.get("/{tx_id}", response_model=TransactionOut)
def get_transaction(
    tx_id: int,
    db:    Session = Depends(get_db),
    _:     User    = Depends(require_viewer_plus),
):
    """Fetch a single transaction by ID."""
    return svc.get_transaction_by_id(db, tx_id)


@router.post("/", response_model=TransactionOut, status_code=201)
def create_transaction(
    data:         TransactionCreate,
    db:           Session = Depends(get_db),
    current_user: User    = Depends(require_admin),
):
    """Create a new transaction. **Admin only.**"""
    return svc.create_transaction(db, data, current_user.id)


@router.patch("/{tx_id}", response_model=TransactionOut)
def update_transaction(
    tx_id: int,
    data:  TransactionUpdate,
    db:    Session = Depends(get_db),
    _:     User    = Depends(require_admin),
):
    """Partially update a transaction. **Admin only.**"""
    return svc.update_transaction(db, tx_id, data)


@router.delete("/{tx_id}")
def delete_transaction(
    tx_id: int,
    db:    Session = Depends(get_db),
    _:     User    = Depends(require_admin),
):
    """Delete a transaction. **Admin only.**"""
    return svc.delete_transaction(db, tx_id)
