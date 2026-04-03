import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./finance_tracker.db")

# SQLite requires this for multi-threaded FastAPI apps
connect_args = {"check_same_thread": False}if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=connect_args)

# Explicit transaction handling and controlled flushing
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for all ORM models
Base = declarative_base()


def get_db():
    """
    FastAPI dependency that provides a database session per request
    and ensures it is properly closed.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
