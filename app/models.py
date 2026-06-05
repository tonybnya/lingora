"""
Script Name : models.py
Description : SQLAlchemy models for the Lingora translation service.
Author      : @tonybnya
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from database import Base, _utcnow, engine


class TranslationRequest(Base):
    """Model for a translation request."""

    __tablename__ = "translation_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    text: Mapped[str] = mapped_column(String, nullable=False)
    languages: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, default="in progress", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=_utcnow,
        onupdate=_utcnow,
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<TranslationRequest(id={self.id}, status={self.status})>"


class TranslationResult(Base):
    """Model for a translation result."""

    __tablename__ = "translation_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    request_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("translation_requests.id"), nullable=False
    )
    language: Mapped[str] = mapped_column(String, nullable=False)
    translated_text: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )

    def __repr__(self) -> str:
        return f"<TranslationResult(id={self.id}, language={self.language})>"


class IndividualTranslations(Base):
    """Model for individual translations."""

    __tablename__ = "individual_translations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    request_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("translation_requests.id"), nullable=False
    )
    translated_text: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )

    def __repr__(self) -> str:
        return f"<IndividualTranslations(id={self.id}, request_id={self.request_id})>"


# Create all tables in the database
Base.metadata.create_all(bind=engine)
