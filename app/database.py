"""
Script Name : database.py
Description : Database configuration and declarative base for Lingora.
Author      : @tonybnya
"""

import os
from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class Base(DeclarativeBase):
    """Declarative base for all Lingora models."""


def _utcnow() -> datetime:
    """Timezone-aware UTC now. Used as SQLAlchemy default/onupdate."""
    return datetime.now(timezone.utc)


# Determine database URL based on environment.
# In development, use SQLite. In production, use PostgreSQL.
# The DATABASE_URL environment variable should be set in production.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./lingora.db")

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
