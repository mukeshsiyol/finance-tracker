from datetime import date
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..models import Transaction, TransactionType, User, UserRole
from ..schemas import TransactionCreate, TransactionUpdate


def create_transaction(db: Session, data: TransactionCreate, user_id: int) -> Transaction:
    tx = Transaction(**data.model_dump(), user_id=user_id)
    db.add(tx)
    db.commit()
    db.refresh(tx)
    return tx


def get_transaction_by_id(db: Session, tx_id: int, user: User) -> Transaction:
    """Fetch a transaction by ID. All authenticated users can view any transaction."""
    query = db.query(Transaction).filter(Transaction.id == tx_id)
    tx = query.first()
    if not tx:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with id={tx_id} not found.",
        )
    return tx


def list_transactions(
    db:           Session,
    current_user: User,
    tx_type:      Optional[TransactionType] = None,
    category:     Optional[str] = None,
    start_date:   Optional[date] = None,
    end_date:     Optional[date] = None,
    skip:         int = 0,
    limit:        int = 50,
) -> list[Transaction]:
    """
    All authenticated users can see all transactions.
    Filters available to analyst+ roles.
    """
    query = db.query(Transaction)

    if tx_type:
        query = query.filter(Transaction.type == tx_type)
    if category:
        query = query.filter(Transaction.category.ilike(f"%{category}%"))
    if start_date:
        query = query.filter(Transaction.date >= start_date)
    if end_date:
        query = query.filter(Transaction.date <= end_date)

    return (
        query
        .order_by(Transaction.date.desc(), Transaction.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def update_transaction(db: Session, tx_id: int, data: TransactionUpdate, user: User) -> Transaction:
    tx = get_transaction_by_id(db, tx_id, user)           # reuses the 404 helper
    # exclude_unset=True → skip fields absent from the request body entirely
    # exclude_none=True  → skip fields explicitly sent as null, preventing
    #                      NOT NULL constraint violations on non-nullable columns
    updates = data.model_dump(exclude_unset=True, exclude_none=True)
    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided to update.",
        )
    for field, value in updates.items():
        setattr(tx, field, value)
    db.commit()
    db.refresh(tx)
    return tx


def delete_transaction(db: Session, tx_id: int, user: User) -> dict:
    tx = get_transaction_by_id(db, tx_id, user)
    db.delete(tx)
    db.commit()
    return {"detail": f"Transaction {tx_id} deleted successfully."}
