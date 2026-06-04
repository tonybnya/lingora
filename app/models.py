"""
Script Name : models.py
Description : SQLAlchemy models for the Lingora translation service.
Author      : @tonybnya
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import os

Base = declarative_base()

# Determine database URL based on environment
# In development, use SQLite. In production, use PostgreSQL.
# The DATABASE_URL environment variable should be set in production.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./lingora.db")

engine = create_engine(DATABASE_URL)


class TranslationRequest(Base):
    """Model for a translation request."""

    __tablename__ = "translation_requests"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    languages = Column(String, nullable=False)
    status = Column(String, default="in progress", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<TranslationRequest(id={self.id}, status={self.status})>"


class TranslationResult(Base):
    """Model for a translation result."""

    __tablename__ = "translation_results"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("translation_requests.id"), nullable=False)
    language = Column(String, nullable=False)
    translated_text = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<TranslationResult(id={self.id}, language={self.language})>"


class IndividualTranslations(Base):
    """Model for individual translations."""

    __tablename__ = "individual_translations"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("translation_requests.id"), nullable=False)
    translated_text = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<IndividualTranslations(id={self.id}, request_id={self.request_id})>"


# Create all tables in the database
Base.metadata.create_all(engine)
