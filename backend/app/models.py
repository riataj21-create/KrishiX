"""SQLAlchemy ORM models."""
from sqlalchemy import Column, String, DateTime, Boolean, Numeric, Date, ForeignKey, Index, UniqueConstraint, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class User(Base):
    """User account model."""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    # Role: farmer | buyer | admin
    role = Column(String(20), nullable=False, default="farmer", index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    farmer_profile = relationship("FarmerProfile", uselist=False, back_populates="user", cascade="all, delete-orphan")
    saved_markets = relationship("SavedMarket", back_populates="user", cascade="all, delete-orphan")
    saved_commodities = relationship("SavedCommodity", back_populates="user", cascade="all, delete-orphan")


class FarmerProfile(Base):
    """Farmer profile model."""
    __tablename__ = "farmer_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(20))
    state = Column(String(100), nullable=False, index=True)
    district = Column(String(100), nullable=False, index=True)
    village = Column(String(100))
    postal_code = Column(String(10))
    latitude = Column(Numeric(10, 8))
    longitude = Column(Numeric(11, 8))
    bio = Column(String(500))
    profile_image_url = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="farmer_profile")

    __table_args__ = (
        Index("idx_profile_state_district", "state", "district"),
        Index("idx_profile_coordinates", "latitude", "longitude"),
    )


class Commodity(Base):
    """Commodity model."""
    __tablename__ = "commodities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False, index=True)
    category = Column(String(50), index=True)
    unit = Column(String(20), nullable=False, default="kg")
    description = Column(String(500))
    icon_url = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    market_prices = relationship("MarketPrice", back_populates="commodity", cascade="all, delete-orphan")
    saved_commodities = relationship("SavedCommodity", back_populates="commodity", cascade="all, delete-orphan")


class Market(Base):
    """Market model."""
    __tablename__ = "markets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    state = Column(String(100), nullable=False, index=True)
    district = Column(String(100), nullable=False, index=True)
    village = Column(String(100))
    postal_code = Column(String(10))
    latitude = Column(Numeric(10, 8))
    longitude = Column(Numeric(11, 8))
    market_type = Column(String(50))
    contact_phone = Column(String(20))
    contact_email = Column(String(255))
    website_url = Column(String(500))
    description = Column(String(1000))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    market_prices = relationship("MarketPrice", back_populates="market", cascade="all, delete-orphan")
    saved_markets = relationship("SavedMarket", back_populates="market", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_market_state_district", "state", "district"),
        Index("idx_market_name", "name"),
        Index("idx_market_coordinates", "latitude", "longitude"),
        UniqueConstraint("name", "state", "district", name="uq_market_location"),
    )


class MarketPrice(Base):
    """Market price model (time-series data)."""
    __tablename__ = "market_prices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    market_id = Column(UUID(as_uuid=True), ForeignKey("markets.id", ondelete="CASCADE"), nullable=False, index=True)
    commodity_id = Column(UUID(as_uuid=True), ForeignKey("commodities.id", ondelete="CASCADE"), nullable=False, index=True)
    price_date = Column(Date, nullable=False, index=True)
    min_price = Column(Numeric(10, 2), nullable=False)
    max_price = Column(Numeric(10, 2), nullable=False)
    modal_price = Column(Numeric(10, 2))
    quantity_traded = Column(Numeric(15, 2))
    source = Column(String(100), nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    market = relationship("Market", back_populates="market_prices")
    commodity = relationship("Commodity", back_populates="market_prices")

    __table_args__ = (
        Index("idx_market_commodity_date", "market_id", "commodity_id", "price_date"),
        UniqueConstraint("market_id", "commodity_id", "price_date", name="uq_market_commodity_date"),
    )


class SavedMarket(Base):
    """User's saved markets model."""
    __tablename__ = "saved_markets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    market_id = Column(UUID(as_uuid=True), ForeignKey("markets.id", ondelete="CASCADE"), nullable=False, index=True)
    saved_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="saved_markets")
    market = relationship("Market", back_populates="saved_markets")

    __table_args__ = (
        UniqueConstraint("user_id", "market_id", name="uq_user_market"),
    )


class SavedCommodity(Base):
    """User's saved commodities model."""
    __tablename__ = "saved_commodities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    commodity_id = Column(UUID(as_uuid=True), ForeignKey("commodities.id", ondelete="CASCADE"), nullable=False, index=True)
    saved_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="saved_commodities")
    commodity = relationship("Commodity", back_populates="saved_commodities")

    __table_args__ = (
        UniqueConstraint("user_id", "commodity_id", name="uq_user_commodity"),
    )


class Buyer(Base):
    """Buyer profile — traders, exporters, FPOs, processors."""
    __tablename__ = "buyers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    buyer_type = Column(String(50), nullable=False)   # Trader | Exporter | FPO | Processor | Retailer
    contact_name = Column(String(255))
    contact_phone = Column(String(20))
    contact_email = Column(String(255))
    state = Column(String(100), nullable=False, index=True)
    district = Column(String(100), nullable=False, index=True)
    city = Column(String(100))
    latitude = Column(Numeric(10, 8))
    longitude = Column(Numeric(11, 8))
    # What they buy
    commodity_name = Column(String(100), nullable=False, index=True)
    min_quantity_quintal = Column(Numeric(10, 2))   # minimum purchase quantity
    max_quantity_quintal = Column(Numeric(10, 2))   # maximum they can absorb
    quality_grade = Column(String(50))              # Grade A | Grade B | Any
    price_premium_pct = Column(Numeric(5, 2), default=0)  # % above mandi modal price they'll pay
    # Credibility signals
    is_verified = Column(Boolean, default=False)
    years_active = Column(Integer)
    rating = Column(Numeric(3, 1))                  # 1.0 – 5.0
    payment_terms = Column(String(100))             # "Immediate" | "7 days" | "14 days"
    notes = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("idx_buyer_commodity", "commodity_name"),
        Index("idx_buyer_state_district", "state", "district"),
    )
