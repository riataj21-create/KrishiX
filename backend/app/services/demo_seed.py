"""Idempotent demo seed for the hackathon tomato scenario."""

from datetime import date, timedelta
from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from app.models import Buyer, BuyerRequirement, Commodity, FarmerLot, FarmerProfile, Market, MarketPrice, User
from app.auth import hash_password

TOMATO_ID = UUID("750e8400-e29b-41d4-a716-446655440010")
FARMER1 = UUID("550e8400-e29b-41d4-a716-446655440000")
FARMER2 = UUID("550e8400-e29b-41d4-a716-446655440001")
FARMER3 = UUID("550e8400-e29b-41d4-a716-446655440002")
BUYER_USER = UUID("550e8400-e29b-41d4-a716-446655440010")
GULF_BUYER = UUID("b10e8400-e29b-41d4-a716-446655440001")
AGG_BUYER = UUID("b10e8400-e29b-41d4-a716-446655440002")
GATE_BUYER = UUID("b10e8400-e29b-41d4-a716-446655440003")
FAR_BUYER = UUID("b10e8400-e29b-41d4-a716-446655440004")
QUALITY_BUYER = UUID("b10e8400-e29b-41d4-a716-446655440005")
DEADLINE_BUYER = UUID("b10e8400-e29b-41d4-a716-446655440006")
PAY_BUYER = UUID("b10e8400-e29b-41d4-a716-446655440007")
MARKET_MP = UUID("850e8400-e29b-41d4-a716-446655440030")

LOT1 = UUID("c10e8400-e29b-41d4-a716-446655440001")
LOT2 = UUID("c10e8400-e29b-41d4-a716-446655440002")
LOT3 = UUID("c10e8400-e29b-41d4-a716-446655440003")

PW = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5YmMxSUmmS46m"


def _upsert_user(db: Session, user_id: UUID, email: str, role: str):
    row = db.query(User).filter(User.id == user_id).first()
    if row:
        row.role = role
        return row
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        return existing
    row = User(id=user_id, email=email, password_hash=PW, is_active=True, role=role)
    db.add(row)
    return row


def seed_demo(db: Session) -> dict:
    today = date.today()
    tomato = db.query(Commodity).filter(Commodity.id == TOMATO_ID).first()
    if not tomato:
        tomato = db.query(Commodity).filter(Commodity.name == "Tomato").first()
    if not tomato:
        raise ValueError("Tomato commodity missing — load sample_data.sql first")

    commodity_id = tomato.id
    _upsert_user(db, FARMER1, "farmer1@krishix.com", "farmer")
    _upsert_user(db, FARMER2, "farmer2@krishix.com", "farmer")
    _upsert_user(db, FARMER3, "farmer3@krishix.com", "farmer")
    _upsert_user(db, BUYER_USER, "buyer1@krishix.com", "buyer")
    db.flush()

    profile = db.query(FarmerProfile).filter(FarmerProfile.user_id == FARMER1).first()
    if profile:
        profile.state = "Andhra Pradesh"
        profile.district = "Madanapalle"
        profile.village = "Madanapalle"
        profile.latitude = Decimal("13.5504")
        profile.longitude = Decimal("78.5024")
        profile.full_name = profile.full_name or "Ravi Reddy"

    market = db.query(Market).filter(Market.id == MARKET_MP).first()
    if not market:
        market = Market(
            id=MARKET_MP,
            name="Madanapalle Tomato Market",
            state="Andhra Pradesh",
            district="Madanapalle",
            village="Madanapalle",
            market_type="APMC",
            latitude=Decimal("13.5504"),
            longitude=Decimal("78.5024"),
            description="DEMO/sample market for the hackathon tomato scenario.",
        )
        db.add(market)
        db.flush()
        db.add(MarketPrice(
            market_id=market.id,
            commodity_id=commodity_id,
            price_date=today,
            min_price=Decimal("2400"),
            max_price=Decimal("3200"),
            modal_price=Decimal("2800"),
            quantity_traded=Decimal("400"),
            source="Sample Data",
        ))

    buyers = [
        dict(id=GULF_BUYER, name="Rayalaseema Gulf Exports (DEMO)", buyer_type="Exporter",
             notes="DEMO. High advertised price with Grade A, 300 kg min, 7-day payment, ₹1,500 configured transport estimate."),
        dict(id=AGG_BUYER, name="Madanapalle Packhouse Co-op (DEMO)", buyer_type="FPO",
             notes="DEMO. Grade B accepted. 300 kg min. Recoverable via aggregation + payment negotiation."),
        dict(id=GATE_BUYER, name="Chittoor Farm-gate Trader (DEMO)", buyer_type="Trader",
             notes="DEMO. Executable standing offer: Grade B, 50 kg min, same-day pay, buyer pickup."),
        dict(id=FAR_BUYER, name="Bengaluru Distant Buyer (DEMO)", buyer_type="Retailer",
             notes="DEMO. Grade B ok but ₹5,000 configured transport estimate makes net uneconomic."),
        dict(id=QUALITY_BUYER, name="Export Grader Pvt Ltd (DEMO)", buyer_type="Exporter",
             notes="DEMO. Small quantity ok but Grade A only."),
        dict(id=DEADLINE_BUYER, name="Expired Contract Desk (DEMO)", buyer_type="Trader",
             notes="DEMO. Requirement already expired."),
        dict(id=PAY_BUYER, name="Slow-pay Local Mandi Agent (DEMO)", buyer_type="Trader",
             notes="DEMO. Quantity and grade ok; payment is 7 days vs farmer 2-day limit."),
    ]
    for spec in buyers:
        row = db.query(Buyer).filter(Buyer.id == spec["id"]).first()
        if not row:
            row = Buyer(
                id=spec["id"],
                name=spec["name"],
                buyer_type=spec["buyer_type"],
                contact_name="Demo desk",
                contact_phone="9000000001",
                contact_email="demo@krishix.example",
                state="Andhra Pradesh",
                district="Madanapalle",
                city="Madanapalle",
                latitude=Decimal("13.55"),
                longitude=Decimal("78.50"),
                commodity_name="Tomato",
                min_quantity_quintal=Decimal("0.5"),
                quality_grade="Grade B",
                source_type="demo",
                is_verified=False,
                verification_status="UNVERIFIED",
                payment_days=7,
                pickup_available=False,
                user_id=BUYER_USER,
                notes=spec["notes"],
            )
            db.add(row)

    db.flush()

    def ensure_req(rid: UUID, buyer_id: UUID, **kwargs):
        row = db.query(BuyerRequirement).filter(BuyerRequirement.id == rid).first()
        if row:
            for k, v in kwargs.items():
                setattr(row, k, v)
            return row
        row = BuyerRequirement(id=rid, buyer_id=buyer_id, commodity_id=commodity_id, **kwargs)
        db.add(row)
        return row

    ensure_req(
        UUID("d10e8400-e29b-41d4-a716-446655440001"), GULF_BUYER,
        minimum_quantity=Decimal("3.0"), maximum_quantity=Decimal("50"),
        required_grade="Grade A", offered_price=Decimal("3400"),
        payment_days=7, payment_method="Bank Transfer", pickup_available=False,
        pickup_location_state="Andhra Pradesh", pickup_location_district="Madanapalle",
        active_from=today, active_until=today + timedelta(days=14), is_active=True,
        source_type="demo",
        transport_cost_total=Decimal("1500"), transport_cost_source="configured_demo",
        notes="₹34/kg advertised. 300 kg min. Grade A. 7-day pay. ₹1,500 configured/demo transport.",
    )
    ensure_req(
        UUID("d10e8400-e29b-41d4-a716-446655440002"), AGG_BUYER,
        minimum_quantity=Decimal("3.0"), maximum_quantity=Decimal("20"),
        required_grade="Grade B", offered_price=Decimal("3200"),
        payment_days=7, payment_method="UPI", pickup_available=False,
        pickup_location_state="Andhra Pradesh", pickup_location_district="Madanapalle",
        active_from=today, active_until=today + timedelta(days=14), is_active=True,
        source_type="demo",
        transport_cost_total=Decimal("400"), transport_cost_source="configured_demo",
        notes="Recoverable: aggregate to 300 kg and negotiate payment to 2 days.",
    )
    ensure_req(
        UUID("d10e8400-e29b-41d4-a716-446655440003"), GATE_BUYER,
        minimum_quantity=Decimal("0.5"), maximum_quantity=Decimal("5"),
        required_grade="Grade B", offered_price=Decimal("3000"),
        payment_days=0, payment_method="Cash", pickup_available=True,
        pickup_location_state="Andhra Pradesh", pickup_location_district="Madanapalle",
        active_from=today, active_until=today + timedelta(days=14), is_active=True,
        source_type="demo",
        transport_cost_total=Decimal("0"), transport_cost_source="buyer_pickup",
        notes="Executable farm-gate purchase.",
    )
    ensure_req(
        UUID("d10e8400-e29b-41d4-a716-446655440004"), FAR_BUYER,
        minimum_quantity=Decimal("0.5"), maximum_quantity=Decimal("10"),
        required_grade="Grade B", offered_price=Decimal("3600"),
        payment_days=1, payment_method="UPI", pickup_available=False,
        pickup_location_state="Karnataka", pickup_location_district="Bengaluru",
        active_from=today, active_until=today + timedelta(days=14), is_active=True,
        source_type="demo",
        transport_cost_total=Decimal("5000"), transport_cost_source="configured_demo",
        notes="High price but transport estimate destroys net realization.",
    )
    ensure_req(
        UUID("d10e8400-e29b-41d4-a716-446655440005"), QUALITY_BUYER,
        minimum_quantity=Decimal("0.5"), maximum_quantity=Decimal("10"),
        required_grade="Grade A", offered_price=Decimal("3300"),
        payment_days=1, payment_method="UPI", pickup_available=True,
        pickup_location_state="Andhra Pradesh", pickup_location_district="Madanapalle",
        active_from=today, active_until=today + timedelta(days=14), is_active=True,
        source_type="demo",
        transport_cost_total=Decimal("0"), transport_cost_source="buyer_pickup",
        notes="Quality mismatch only.",
    )
    ensure_req(
        UUID("d10e8400-e29b-41d4-a716-446655440006"), DEADLINE_BUYER,
        minimum_quantity=Decimal("0.5"), maximum_quantity=Decimal("10"),
        required_grade="Grade B", offered_price=Decimal("3100"),
        payment_days=1, payment_method="UPI", pickup_available=True,
        pickup_location_state="Andhra Pradesh", pickup_location_district="Madanapalle",
        active_from=today - timedelta(days=20), active_until=today - timedelta(days=1), is_active=True,
        source_type="demo",
        transport_cost_total=Decimal("0"), transport_cost_source="buyer_pickup",
        notes="Expired opportunity.",
    )
    ensure_req(
        UUID("d10e8400-e29b-41d4-a716-446655440007"), PAY_BUYER,
        minimum_quantity=Decimal("0.5"), maximum_quantity=Decimal("5"),
        required_grade="Grade B", offered_price=Decimal("3100"),
        payment_days=7, payment_method="Cheque", pickup_available=True,
        pickup_location_state="Andhra Pradesh", pickup_location_district="Madanapalle",
        active_from=today, active_until=today + timedelta(days=14), is_active=True,
        source_type="demo",
        transport_cost_total=Decimal("0"), transport_cost_source="buyer_pickup",
        notes="Payment mismatch only.",
    )

    def ensure_lot(lid, farmer_id, qty, grade):
        row = db.query(FarmerLot).filter(FarmerLot.id == lid).first()
        if row:
            row.quantity = qty
            row.quality_grade = grade
            row.state = "Andhra Pradesh"
            row.district = "Madanapalle"
            row.available_from = today
            row.sell_by = today
            row.minimum_price = Decimal("2800")
            row.max_payment_days = 2
            row.status = "available"
            row.commodity_id = commodity_id
            return row
        row = FarmerLot(
            id=lid, farmer_id=farmer_id, commodity_id=commodity_id,
            quantity=qty, unit="quintal",
            state="Andhra Pradesh", district="Madanapalle", village="Madanapalle",
            latitude=Decimal("13.5504"), longitude=Decimal("78.5024"),
            quality_status=grade, quality_grade=grade,
            available_from=today, sell_by=today,
            minimum_price=Decimal("2800"), max_payment_days=2,
            transport_preference="BUYER_PICKUP",
            status="available",
        )
        db.add(row)
        return row

    ensure_lot(LOT1, FARMER1, Decimal("0.8"), "Grade B")
    ensure_lot(LOT2, FARMER2, Decimal("1.2"), "Grade B")
    ensure_lot(LOT3, FARMER3, Decimal("1.0"), "Grade B")
    db.commit()
    return {
        "tomato_lot_id": str(LOT1),
        "farmer_login": "farmer1@krishix.com",
        "password": "password123",
        "note": "80 kg Grade B Madanapalle tomato lot is ready. Demo buyers are labelled DEMO.",
    }
