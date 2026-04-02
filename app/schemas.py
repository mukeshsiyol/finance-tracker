from __future__ import annotations
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from .models import TransactionType, UserRole


# ── Auth ───────────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email:    EmailStr
    password: str = Field(..., min_length=6)
    role:     UserRole = UserRole.viewer


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type:   str = "bearer"


# ── User ───────────────────────────────────────────────────────────────────

class UserOut(BaseModel):
    id:         int
    username:   str
    email:      str
    role:       UserRole
    created_at: datetime

    model_config = {"from_attributes": True}


class UserRoleUpdate(BaseModel):
    role: UserRole


# ── Transaction ────────────────────────────────────────────────────────────

class TransactionCreate(BaseModel):
    amount:   float       = Field(..., gt=0, description="Must be a positive number")
    type:     TransactionType
    category: str         = Field(..., min_length=1, max_length=100)
    date:     date
    notes:    Optional[str] = Field(None, max_length=500)

    @field_validator("category")
    @classmethod
    def strip_category(cls, v: str) -> str:
        return v.strip().title()


class TransactionUpdate(BaseModel):
    amount:   Optional[float]           = Field(None, gt=0)
    type:     Optional[TransactionType] = None
    category: Optional[str]            = Field(None, min_length=1, max_length=100)
    date:     Optional[date]            = None
    notes:    Optional[str]             = Field(None, max_length=500)

    @field_validator("category")
    @classmethod
    def strip_category(cls, v: Optional[str]) -> Optional[str]:
        return v.strip().title() if v else v


class TransactionOut(BaseModel):
    id:         int
    amount:     float
    type:       TransactionType
    category:   str
    date:       date
    notes:      Optional[str]
    user_id:    int
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}


# ── Analytics ──────────────────────────────────────────────────────────────

class CategoryBreakdown(BaseModel):
    category:      str
    total:         float
    count:         int
    percentage:    float


class MonthlyTotal(BaseModel):
    year:          int
    month:         int
    total_income:  float
    total_expense: float
    net:           float


class FinancialSummary(BaseModel):
    total_income:    float
    total_expenses:  float
    current_balance: float
    total_records:   int
    income_records:  int
    expense_records: int


class AnalyticsDashboard(BaseModel):
    summary:             FinancialSummary
    category_breakdown:  dict[str, list[CategoryBreakdown]]
    monthly_totals:      list[MonthlyTotal]
    recent_transactions: list[TransactionOut]
