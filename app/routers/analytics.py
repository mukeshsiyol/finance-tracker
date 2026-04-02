from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import require_analyst_plus, require_viewer_plus
from ..schemas import AnalyticsDashboard, FinancialSummary
from ..services import analytics_service as svc

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/summary", response_model=FinancialSummary)
def summary(
    db: Session = Depends(get_db),
    _=Depends(require_viewer_plus),
):
    """
    High-level financial summary: total income, total expenses, current balance.
    Accessible to all authenticated users.
    """
    return svc.get_summary(db)


@router.get("/categories", response_model=dict)
def category_breakdown(
    db: Session = Depends(get_db),
    _=Depends(require_analyst_plus),
):
    """
    Per-category breakdown split by income and expense types.
    **Analyst and Admin only.**
    """
    return svc.get_category_breakdown(db)


@router.get("/monthly", response_model=list)
def monthly_totals(
    db: Session = Depends(get_db),
    _=Depends(require_analyst_plus),
):
    """
    Monthly income, expense, and net totals. **Analyst and Admin only.**
    """
    return svc.get_monthly_totals(db)


@router.get("/dashboard", response_model=AnalyticsDashboard)
def dashboard(
    db: Session = Depends(get_db),
    _=Depends(require_analyst_plus),
):
    """
    Full analytics dashboard: summary + categories + monthly + recent transactions.
    **Analyst and Admin only.**
    """
    return svc.get_dashboard(db)
