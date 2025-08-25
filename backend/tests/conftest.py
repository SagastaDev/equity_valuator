"""
Shared test fixtures for the backend tests.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from backend.main import app
from backend.db.base import Base
from backend.db.session import get_db
from backend.db.models.user import User, UserRole
from backend.db.models.company import Company
from backend.db.models.provider import Provider
from backend.db.models.field import CanonicalField, FieldCategory
from backend.auth.utils import get_password_hash
from datetime import date
from uuid import uuid4


# Use PostgreSQL test database (separate from main database)
import os
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres@db:5432/equity_valuation_test"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database session for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    # Create the database and tables
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Clean up - drop all tables after test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session):
    """Create a test client."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    user = User(
        email="testuser@example.com",
        hashed_password=get_password_hash("testpassword123"),
        role=UserRole.VIEWER
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def admin_user(db_session):
    """Create an admin user."""
    user = User(
        email="admin@example.com",
        hashed_password=get_password_hash("adminpassword123"),
        role=UserRole.ADMIN
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(client, test_user):
    """Get authentication headers for a test user."""
    response = client.post("/auth/token", data={
        "username": test_user.email,
        "password": "testpassword123"
    })
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers(client, admin_user):
    """Get authentication headers for an admin user."""
    response = client.post("/auth/token", data={
        "username": admin_user.email,
        "password": "adminpassword123"
    })
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_company(db_session):
    """Create a test company."""
    company = Company(
        ticker="AAPL",
        name="Apple Inc.",
        country="US",
        currency="USD"
    )
    db_session.add(company)
    db_session.commit()
    db_session.refresh(company)
    return company


@pytest.fixture
def test_provider(db_session):
    """Create a test data provider."""
    provider = Provider(name="Test Provider")
    db_session.add(provider)
    db_session.commit()
    db_session.refresh(provider)
    return provider


@pytest.fixture
def canonical_fields(db_session):
    """Create test canonical fields."""
    fields = [
        CanonicalField(
            code=1,
            name="total_revenue",
            display_name="Total Revenue",
            type="number",
            category=FieldCategory.FUNDAMENTAL
        ),
        CanonicalField(
            code=2,
            name="total_assets",
            display_name="Total Assets", 
            type="number",
            category=FieldCategory.FUNDAMENTAL
        ),
        CanonicalField(
            code=3,
            name="debt_to_equity",
            display_name="Debt to Equity Ratio",
            type="number",
            category=FieldCategory.RATIO,
            is_computed=True
        )
    ]
    
    for field in fields:
        db_session.add(field)
    db_session.commit()
    
    for field in fields:
        db_session.refresh(field)
    
    return fields