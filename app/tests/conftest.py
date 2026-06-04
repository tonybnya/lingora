"""
Script Name : conftest.py
Description : Pytest configuration and shared fixtures for Lingora tests.
Author      : @tonybnya
"""

import os
import sys
import tempfile
from pathlib import Path

# Configure environment BEFORE importing app modules so module-level
# engine/client construction picks up the test configuration.
_test_db_fd, _test_db_path = tempfile.mkstemp(suffix=".db")
os.environ["DATABASE_URL"] = f"sqlite:///{_test_db_path}"
os.environ.setdefault("GEMINI_API_KEY", "test-fake-key")
os.environ.setdefault("TRANSLATION_PROVIDER", "gemini")

# Make sure the project root (parent of app/) is importable so that
# `from database import ...` works the same as in `fastapi dev` mode.
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))


import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from main import app  # noqa: E402
from database import Base, engine, SessionLocal  # noqa: E402


@pytest.fixture(autouse=True)
def reset_db():
    """Drop and recreate all tables between tests for full isolation."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    """FastAPI test client. Background tasks run synchronously."""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def db_session():
    """A standalone SessionLocal instance for direct DB assertions."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
