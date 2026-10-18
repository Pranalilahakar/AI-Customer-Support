
import os
import sys
from pathlib import Path

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy import URL, create_engine, text
from sqlalchemy.orm import sessionmaker

# Add the backend folder to Python's import path.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

# Load the existing configuration without displaying secrets.
load_dotenv(BACKEND_DIR / ".env")

# Always connect tests to the dedicated test database.
TEST_DATABASE_URL = URL.create(
    drivername="postgresql+psycopg2",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", "5432")),
    database="customer_support_test_db",
)

test_engine = create_engine(
    TEST_DATABASE_URL,
    pool_pre_ping=True,
)

TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False,
)

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import User, Ticket, TicketComment


@pytest.fixture(scope="session", autouse=True)
def prepare_test_database():
    """Create tables in the dedicated test database."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()


@pytest.fixture(autouse=True)
def clean_test_records(prepare_test_database):
    """Keep each test independent of records from previous tests."""
    with test_engine.begin() as connection:
        connection.execute(text("DELETE FROM ticket_comments"))
        connection.execute(text("DELETE FROM tickets"))
        connection.execute(text("DELETE FROM users"))
    yield


@pytest.fixture()
def db_session():
    """Provide a database session for test setup and assertions."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client():
    """Provide a FastAPI client using the test database."""
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
