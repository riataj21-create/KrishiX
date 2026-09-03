"""Test fixtures and configuration."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import app
from app.models import User, Commodity, Market
from app.auth import hash_password
from datetime import date

# Use SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture
def db_session():
    """Create a test database session."""
    Base.metadata.create_all(bind=engine)
    yield TestingSessionLocal()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    user = User(
        email="test@krishix.com",
        password_hash=hash_password("testpass123")
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_commodities(db_session):
    """Create test commodities."""
    commodities = [
        Commodity(name="Rice", category="Cereals", unit="kg"),
        Commodity(name="Tomato", category="Vegetables", unit="kg"),
        Commodity(name="Mango", category="Fruits", unit="kg"),
    ]
    db_session.add_all(commodities)
    db_session.commit()
    return commodities


@pytest.fixture
def test_markets(db_session):
    """Create test markets."""
    markets = [
        Market(
            name="Ludhiana Central Market",
            state="Punjab",
            district="Ludhiana",
            village="Ludhiana City",
            market_type="APMC"
        ),
        Market(
            name="Nashik Agricultural Market",
            state="Maharashtra",
            district="Nashik",
            village="Nashik City",
            market_type="APMC"
        ),
    ]
    db_session.add_all(markets)
    db_session.commit()
    return markets
