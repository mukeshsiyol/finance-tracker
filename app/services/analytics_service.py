from collections import defaultdict

from sqlalchemy.orm import Session

from ..models import Transaction, TransactionType
from ..schemas import (
    AnalyticsDashboard,
    CategoryBreakdown,
    FinancialSummary,
    MonthlyTotal,
    TransactionOut,
)


def _round(value: float) -> float:
    return round(value, 2)


def get_summary(db: Session) -> FinancialSummary:
    transactions = db.query(Transaction).all()

    total_income   = sum(t.amount for t in transactions if t.type == TransactionType.income)
    total_expenses = sum(t.amount for t in transactions if t.type == TransactionType.expense)

    return FinancialSummary(
        total_income    = _round(total_income),
        total_expenses  = _round(total_expenses),
        current_balance = _round(total_income - total_expenses),
        total_records   = len(transactions),
        income_records  = sum(1 for t in transactions if t.type == TransactionType.income),
        expense_records = sum(1 for t in transactions if t.type == TransactionType.expense),
    )


def get_category_breakdown(db: Session) -> dict[str, list[CategoryBreakdown]]:
    """Returns a breakdown per transaction type → list of categories with totals."""
    transactions = db.query(Transaction).all()

    buckets: dict[str, dict[str, dict]] = {
        "income":  defaultdict(lambda: {"total": 0.0, "count": 0}),
        "expense": defaultdict(lambda: {"total": 0.0, "count": 0}),
    }

    for t in transactions:
        bucket = buckets[t.type.value]
        bucket[t.category]["total"] += t.amount
        bucket[t.category]["count"] += 1

    result = {}
    for tx_type, categories in buckets.items():
        grand_total = sum(v["total"] for v in categories.values()) or 1  # avoid /0
        result[tx_type] = [
            CategoryBreakdown(
                category   = cat,
                total      = _round(data["total"]),
                count      = data["count"],
                percentage = _round((data["total"] / grand_total) * 100),
            )
            for cat, data in sorted(categories.items(), key=lambda x: -x[1]["total"])
        ]

    return result


def get_monthly_totals(db: Session) -> list[MonthlyTotal]:
    transactions = db.query(Transaction).all()

    monthly: dict[tuple[int, int], dict] = defaultdict(
        lambda: {"income": 0.0, "expense": 0.0}
    )

    for t in transactions:
        key = (t.date.year, t.date.month)
        monthly[key][t.type.value] += t.amount

    return [
        MonthlyTotal(
            year          = year,
            month         = month,
            total_income  = _round(data["income"]),
            total_expense = _round(data["expense"]),
            net           = _round(data["income"] - data["expense"]),
        )
        for (year, month), data in sorted(monthly.items(), reverse=True)
    ]


def get_dashboard(db: Session) -> AnalyticsDashboard:
    recent = (
        db.query(Transaction)
        .order_by(Transaction.date.desc(), Transaction.id.desc())
        .limit(10)
        .all()
    )

    return AnalyticsDashboard(
        summary             = get_summary(db),
        category_breakdown  = get_category_breakdown(db),
        monthly_totals      = get_monthly_totals(db),
        recent_transactions = [TransactionOut.model_validate(t) for t in recent],
    )
