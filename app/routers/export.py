"""
Export endpoints — download all transactions as CSV or JSON.
Accessible to analyst and admin roles.
"""

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import require_analyst_plus
from ..models import Transaction, TransactionType, User
from ..services.export_service import to_csv, to_json

router = APIRouter(prefix="/export", tags=["Export"])


def _filtered_transactions(
    db:         Session,
    tx_type:    Optional[TransactionType],
    category:   Optional[str],
    start_date: Optional[date],
    end_date:   Optional[date],
) -> list[Transaction]:
    query = db.query(Transaction)
    if tx_type:
        query = query.filter(Transaction.type == tx_type)
    if category:
        query = query.filter(Transaction.category.ilike(f"%{category}%"))
    if start_date:
        query = query.filter(Transaction.date >= start_date)
    if end_date:
        query = query.filter(Transaction.date <= end_date)
    return query.order_by(Transaction.date.desc()).all()


_FILTER_PARAMS = {
    "tx_type":    Query(None, alias="type"),
    "category":   Query(None),
    "start_date": Query(None),
    "end_date":   Query(None),
}


@router.get("/csv", summary="Export transactions as CSV")
def export_csv(
    tx_type:    Optional[TransactionType] = Query(None, alias="type"),
    category:   Optional[str]            = Query(None),
    start_date: Optional[date]           = Query(None),
    end_date:   Optional[date]           = Query(None),
    db:         Session                   = Depends(get_db),
    _:          User                      = Depends(require_analyst_plus),
):
    """
    Download all matching transactions as a **CSV** file.
    Supports the same filters as the transaction list endpoint.
    **Analyst and Admin only.**
    """
    transactions = _filtered_transactions(db, tx_type, category, start_date, end_date)
    return Response(
        content     = to_csv(transactions),
        media_type  = "text/csv",
        headers     = {"Content-Disposition": "attachment; filename=transactions.csv"},
    )


@router.get("/json", summary="Export transactions as JSON")
def export_json(
    tx_type:    Optional[TransactionType] = Query(None, alias="type"),
    category:   Optional[str]            = Query(None),
    start_date: Optional[date]           = Query(None),
    end_date:   Optional[date]           = Query(None),
    db:         Session                   = Depends(get_db),
    _:          User                      = Depends(require_analyst_plus),
):
    """
    Download all matching transactions as a **JSON** file.
    Supports the same filters as the transaction list endpoint.
    **Analyst and Admin only.**
    """
    transactions = _filtered_transactions(db, tx_type, category, start_date, end_date)
    return Response(
        content     = to_json(transactions),
        media_type  = "application/json",
        headers     = {"Content-Disposition": "attachment; filename=transactions.json"},
    )
