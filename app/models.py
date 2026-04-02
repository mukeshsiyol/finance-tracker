import enum
from sqlalchemy import (
    Column, Integer, String, Float, Enum,
    Date, DateTime, ForeignKey, Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base


# ── Enums ──────────────────────────────────────────────────────────────────

class UserRole(str, enum.Enum):
    viewer  = "viewer"    # read-only: records + summaries
    analyst = "analyst"   # read + filter + detailed insights
    admin   = "admin"     # full CRUD + user management


class TransactionType(str, enum.Enum):
    income  = "income"
    expense = "expense"


# ── ORM Models ─────────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id            = Column(Integer, primary_key=True, index=True)
    username      = Column(String(50),  unique=True, index=True, nullable=False)
    email         = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role          = Column(Enum(UserRole), default=UserRole.viewer, nullable=False)
    created_at    = Column(DateTime(timezone=True), server_default=func.now())

    transactions  = relationship("Transaction", back_populates="owner", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User id={self.id} username={self.username!r} role={self.role}>"


class Transaction(Base):
    __tablename__ = "transactions"

    id         = Column(Integer, primary_key=True, index=True)
    amount     = Column(Float,       nullable=False)
    type       = Column(Enum(TransactionType), nullable=False)
    category   = Column(String(100), nullable=False)
    date       = Column(Date,        nullable=False)
    notes      = Column(Text,        nullable=True)
    user_id    = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    owner = relationship("User", back_populates="transactions")

    def __repr__(self):
        return f"<Transaction id={self.id} type={self.type} amount={self.amount}>"
