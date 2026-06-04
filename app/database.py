"""
Script Name : database.py
Description : Database configuration for Lingora.
Author      : @tonybnya
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

# Determine database URL based on environment
# In development, use SQLite. In production, use PostgreSQL.
# The DATABASE_URL environment variable should be set in production.
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./lingora.db")

engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Session = scoped_session(session_factory) # Uncomment this line and comment the above when in production
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
