from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import require_analyst_plus, require_viewer_plus
from ..models import User
from ..schemas import AnalyticsDashboard, FinancialSummary
from ..services import analytics_service as svc

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/summary", response_model=FinancialSummary)
def summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_viewer_plus),
):
    #Return total income, expenses and balance
    return svc.get_summary(db, current_user)


@router.get("/categories", response_model=dict)
def category_breakdown(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst_plus),
):
    #Return per-category breakdown split by income and expense types
    return svc.get_category_breakdown(db, current_user)


@router.get("/monthly", response_model=list)
def monthly_totals(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst_plus),
):
    #Return monthly income, expense, and net totals
    return svc.get_monthly_totals(db, current_user)


@router.get("/dashboard", response_model=AnalyticsDashboard)
def dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_analyst_plus),
):
    #Return full analytics dashboard: summary + categories + monthly + recent transactions
    return svc.get_dashboard(db, current_user)
