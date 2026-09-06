"""Test fixtures and configuration."""
import os
# Set before any app module imports
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_krishix.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-unit-tests-only")

import pytest
from decimal import Decimal
from datetime import date, timedelta
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import app as fastapi_app
from app.auth import hash_password

# Import ALL models so SQLite test DB creates every table
import app.models  # noqa: F401

SQLALCHEMY_DATABASE_URL = os.environ["DATABASE_URL"]  # already set to sqlite above

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


fastapi_app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def fresh_db():
    """Recreate all tables before every test, drop after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True, scope="session")
def mock_external_apis():
    """
    Mock all external HTTP calls for the entire test session.
    Prevents OSRM and Open-Meteo from being called during tests.
    """
    from unittest.mock import AsyncMock, patch

    # Only patch the OSRM function in net_realization engine (the one that makes real HTTP calls)
    osrm_mock = AsyncMock(return_value=None)   # None → triggers Haversine fallback

    with patch("app.engines.net_realization._osrm_road_distance_km", new=osrm_mock):
        yield


@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client():
    return TestClient(fastapi_app)


# ── Reusable data factories ───────────────────────────────────────────────────

@pytest.fixture
def farmer_user(db):
    from app.models import User
    u = User(
        id=uuid4(),
        email="farmer@test.com",
        password_hash=hash_password("password123"),
        role="farmer",
        is_active=True,
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


@pytest.fixture
def buyer_user(db):
    from app.models import User
    u = User(
        id=uuid4(),
        email="buyer@test.com",
        password_hash=hash_password("password123"),
        role="buyer",
        is_active=True,
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


@pytest.fixture
def farmer_token(client, farmer_user):
    """Return a valid Bearer token for the farmer user."""
    resp = client.post(
        "/api/auth/login",
        json={"email": "farmer@test.com", "password": "password123"},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


@pytest.fixture
def tomato_commodity(db):
    from app.models import Commodity
    c = Commodity(
        id=uuid4(),
        name="Tomato",
        category="Vegetables",
        unit="quintal",
    )
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


@pytest.fixture
def madanapalle_market(db):
    from app.models import Market
    m = Market(
        id=uuid4(),
        name="Madanapalle Tomato Market",
        state="Andhra Pradesh",
        district="Madanapalle",
        market_type="APMC",
        latitude=Decimal("13.5504"),
        longitude=Decimal("78.5024"),
    )
    db.add(m)
    db.commit()
    db.refresh(m)
    return m


@pytest.fixture
def tomato_lot_80kg(db, farmer_user, tomato_commodity):
    """80 kg Grade B tomato lot — the primary demo lot."""
    from app.models import FarmerLot
    today = date.today()
    lot = FarmerLot(
        id=uuid4(),
        farmer_id=farmer_user.id,
        commodity_id=tomato_commodity.id,
        quantity=Decimal("0.8"),   # 0.8 quintals = 80 kg
        unit="quintal",
        state="Andhra Pradesh",
        district="Madanapalle",
        latitude=Decimal("13.5504"),
        longitude=Decimal("78.5024"),
        quality_status="Grade B",
        quality_grade="Grade B",
        available_from=today,
        sell_by=today,
        minimum_price=Decimal("2800"),   # ₹28/kg → ₹2800/quintal
        max_payment_days=2,
        status="available",
    )
    db.add(lot)
    db.commit()
    db.refresh(lot)
    return lot


@pytest.fixture
def gulf_buyer_requirement(db, tomato_commodity):
    """₹34/kg, 300 kg min, Grade A, 7-day payment — the primary failing buyer."""
    from app.models import Buyer, BuyerRequirement
    today = date.today()

    buyer = Buyer(
        id=uuid4(),
        name="Gulf Exports Demo",
        buyer_type="Exporter",
        state="Andhra Pradesh",
        district="Madanapalle",
        commodity_name="Tomato",
        source_type="demo",
        payment_days=7,
        pickup_available=False,
    )
    db.add(buyer)
    db.flush()

    req = BuyerRequirement(
        id=uuid4(),
        buyer_id=buyer.id,
        commodity_id=tomato_commodity.id,
        minimum_quantity=Decimal("3.0"),   # 300 kg
        maximum_quantity=Decimal("50.0"),
        required_grade="Grade A",
        offered_price=Decimal("3400"),     # ₹34/kg → ₹3400/quintal
        payment_days=7,
        payment_method="Bank Transfer",
        pickup_available=False,
        active_from=today,
        active_until=today + timedelta(days=14),
        is_active=True,
        source_type="demo",
        transport_cost_total=Decimal("1500"),
        transport_cost_source="configured_demo",
    )
    db.add(req)
    db.commit()
    db.refresh(req)
    return req


@pytest.fixture
def gate_buyer_requirement(db, tomato_commodity, buyer_user):
    """Farm-gate buyer — Grade B, 50 kg min, immediate payment, buyer pickup → EXECUTABLE."""
    from app.models import Buyer, BuyerRequirement
    today = date.today()

    buyer = Buyer(
        id=uuid4(),
        name="Farm-gate Trader Demo",
        buyer_type="Trader",
        state="Andhra Pradesh",
        district="Madanapalle",
        commodity_name="Tomato",
        source_type="demo",
        payment_days=0,
        pickup_available=True,
        user_id=buyer_user.id,   # linked so offer_from_opportunity can find the buyer user
    )
    db.add(buyer)
    db.flush()

    req = BuyerRequirement(
        id=uuid4(),
        buyer_id=buyer.id,
        commodity_id=tomato_commodity.id,
        minimum_quantity=Decimal("0.5"),
        maximum_quantity=Decimal("5.0"),
        required_grade="Grade B",
        offered_price=Decimal("3000"),
        payment_days=0,
        payment_method="Cash",
        pickup_available=True,
        active_from=today,
        active_until=today + timedelta(days=14),
        is_active=True,
        source_type="demo",
        transport_cost_total=Decimal("0"),
        transport_cost_source="buyer_pickup",
    )
    db.add(req)
    db.commit()
    db.refresh(req)
    return req
