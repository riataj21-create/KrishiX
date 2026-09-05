"""SQLAlchemy ORM models."""
from sqlalchemy import Column, String, DateTime, Boolean, Numeric, Date, ForeignKey, Index, UniqueConstraint, Integer, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.database import Base


# ============================================================================
# Enums
# ============================================================================

class UserRole(str, enum.Enum):
    """User role types."""
    FARMER = "farmer"
    BUYER = "buyer"
    SERVICE_PARTNER = "service_partner"
    ADMIN = "admin"


class LotStatus(str, enum.Enum):
    """Farmer lot lifecycle states."""
    AVAILABLE = "available"
    OFFERED = "offered"
    NEGOTIATING = "negotiating"
    RESERVED = "reserved"
    SOLD = "sold"
    CANCELLED = "cancelled"


class SourceType(str, enum.Enum):
    """Data provenance types."""
    VERIFIED_ACTIVE = "verified_active"
    REFERENCE = "reference"
    DEMO = "demo"
    OBSERVED = "observed"
    USER_PROVIDED = "user_provided"
    ESTIMATED = "estimated"
    PREDICTED = "predicted"


class FeasibilityDecision(str, enum.Enum):
    """Core feasibility engine states."""
    EXECUTABLE = "executable"
    RECOVERABLE = "recoverable"
    NOT_VIABLE = "not_viable"
    INSUFFICIENT_DATA = "insufficient_data"


class OfferStatus(str, enum.Enum):
    """Negotiation offer states."""
    PENDING = "pending"
    COUNTER_OFFERED = "counter_offered"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"


class TransactionStatus(str, enum.Enum):
    """Transaction lifecycle states."""
    ACCEPTED = "accepted"
    PICKUP_SCHEDULED = "pickup_scheduled"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    PAYMENT_PENDING = "payment_pending"
    PAID = "paid"
    DISPUTED = "disputed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PaymentStatus(str, enum.Enum):
    """Payment tracking states."""
    NOT_AGREED = "not_agreed"
    AGREED = "agreed"
    PAYMENT_PENDING = "payment_pending"
    BUYER_REPORTED_PAID = "buyer_reported_paid"
    FARMER_CONFIRMED = "farmer_confirmed"
    PAYMENT_CONFIRMED = "payment_confirmed"
    DISPUTED = "disputed"


class User(Base):
    """User account model."""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    # Role: farmer | buyer | service_partner | admin
    role = Column(String(20), nullable=False, default="farmer", index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    farmer_profile = relationship("FarmerProfile", uselist=False, back_populates="user", cascade="all, delete-orphan")
    saved_markets = relationship("SavedMarket", back_populates="user", cascade="all, delete-orphan")
    saved_commodities = relationship("SavedCommodity", back_populates="user", cascade="all, delete-orphan")
    farmer_lots = relationship("FarmerLot", back_populates="user", foreign_keys="FarmerLot.farmer_id", cascade="all, delete-orphan")
    offers_made = relationship("Offer", back_populates="buyer_user", foreign_keys="Offer.buyer_id")
    reviews_written = relationship("Review", back_populates="reviewer", foreign_keys="Review.reviewer_id")
    reviews_received = relationship("Review", back_populates="reviewee", foreign_keys="Review.reviewee_id")


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
    
    # NEW: Payment and logistics
    payment_days = Column(Integer, default=7)        # Days after delivery for payment
    payment_method = Column(String(50))              # Cash | UPI | Bank Transfer | Cheque
    pickup_available = Column(Boolean, default=False)  # Can buyer pick up from farm?
    
    # Optional link to a platform user (demo counterparties use this)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)

    # NEW: Source type and verification
    source_type = Column(String(50), nullable=False, default="reference", index=True)  # VERIFIED_ACTIVE | REFERENCE | DEMO
    is_verified = Column(Boolean, default=False)
    verification_status = Column(String(50))         # UNVERIFIED | DOCUMENT_VERIFIED | TRANSACTION_VERIFIED
    active_until = Column(Date)                      # When does this buyer requirement expire?
    
    # Credibility signals
    years_active = Column(Integer)
    rating = Column(Numeric(3, 1))                  # 1.0 – 5.0
    payment_terms = Column(String(100))             # Deprecated - use payment_days instead
    notes = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    buyer_requirements = relationship("BuyerRequirement", back_populates="buyer", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_buyer_commodity", "commodity_name"),
        Index("idx_buyer_state_district", "state", "district"),
        Index("idx_buyer_source_type", "source_type"),
    )


# ============================================================================
# New Models - Farmer Lot
# ============================================================================

class FarmerLot(Base):
    """
    Farmer lot represents actual produce a farmer wants to sell.
    This is NOT the farmer profile — it's a specific batch of produce.
    """
    __tablename__ = "farmer_lots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farmer_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    commodity_id = Column(UUID(as_uuid=True), ForeignKey("commodities.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Quantity
    quantity = Column(Numeric(10, 2), nullable=False)   # In quintals
    unit = Column(String(20), default="quintal")
    
    # Location (can differ from farmer profile location)
    state = Column(String(100), nullable=False)
    district = Column(String(100), nullable=False)
    village = Column(String(100))
    latitude = Column(Numeric(10, 8))
    longitude = Column(Numeric(11, 8))
    
    # Quality
    quality_status = Column(String(50))              # Fresh | Grade A | Grade B | etc.
    quality_grade = Column(String(50))               # Standardized grade
    quality_notes = Column(Text)
    
    # Timing constraints (HARD)
    available_from = Column(Date, nullable=False)
    sell_by = Column(Date, nullable=False)           # HARD deadline
    
    # Farmer constraints (HARD)
    minimum_price = Column(Numeric(10, 2))           # ₹/quintal minimum acceptable
    max_payment_days = Column(Integer, default=2)    # HARD constraint
    
    # Preferences (SOFT)
    preferred_payment_method = Column(String(50))
    transport_preference = Column(String(50))        # FARMER_PROVIDED | BUYER_PICKUP | TRANSPORT_PROVIDER
    max_transport_budget = Column(Numeric(10, 2))    # ₹ total (optional)
    
    # State management
    status = Column(String(20), nullable=False, default="available", index=True)
    reserved_by_offer_id = Column(
        UUID(as_uuid=True),
        ForeignKey("offers.id", ondelete="SET NULL", use_alter=True, name="fk_lot_reserved_offer"),
        nullable=True,
    )
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="farmer_lots", foreign_keys=[farmer_id])
    commodity = relationship("Commodity")
    opportunities = relationship("Opportunity", back_populates="lot")
    aggregation_memberships = relationship("AggregationMember", back_populates="lot")

    __table_args__ = (
        Index("idx_lot_farmer", "farmer_id"),
        Index("idx_lot_commodity", "commodity_id"),
        Index("idx_lot_status", "status"),
        Index("idx_lot_location", "state", "district"),
    )


# ============================================================================
# New Models - Buyer Requirements
# ============================================================================

class BuyerRequirement(Base):
    """
    Structured buyer demand/requirement.
    Separates buyer profile from what they're actively buying.
    """
    __tablename__ = "buyer_requirements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    buyer_id = Column(UUID(as_uuid=True), ForeignKey("buyers.id", ondelete="CASCADE"), nullable=False, index=True)
    commodity_id = Column(UUID(as_uuid=True), ForeignKey("commodities.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Quantity (HARD constraints)
    minimum_quantity = Column(Numeric(10, 2), nullable=False)   # quintals
    maximum_quantity = Column(Numeric(10, 2))                   # quintals (can be NULL = unlimited)
    
    # Quality (HARD constraint)
    required_grade = Column(String(50))                         # Grade A | Grade B | Any
    
    # Price
    offered_price = Column(Numeric(10, 2), nullable=False)      # ₹/quintal
    
    # Payment terms (HARD constraint)
    payment_days = Column(Integer, nullable=False)              # Days after delivery
    payment_method = Column(String(50))                         # Cash | UPI | Bank Transfer
    
    # Logistics
    pickup_available = Column(Boolean, default=False)
    pickup_location_state = Column(String(100))
    pickup_location_district = Column(String(100))

    # Transport — estimates must retain source; never presented as a live quote
    transport_cost_total = Column(Numeric(12, 2))
    transport_cost_source = Column(String(50), default="configured_demo")  # configured_demo | estimated | buyer_pickup | user_provided
    
    # Validity
    active_from = Column(Date, nullable=False)
    active_until = Column(Date, nullable=False)
    is_active = Column(Boolean, default=True, index=True)
    
    # Provenance
    source_type = Column(String(50), nullable=False, default="reference")  # VERIFIED_ACTIVE | REFERENCE | DEMO
    verification_status = Column(String(50))
    
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    buyer = relationship("Buyer", back_populates="buyer_requirements")
    commodity = relationship("Commodity")
    opportunities = relationship("Opportunity", back_populates="buyer_requirement")

    __table_args__ = (
        Index("idx_buyer_req_buyer", "buyer_id"),
        Index("idx_buyer_req_commodity", "commodity_id"),
        Index("idx_buyer_req_active", "is_active"),
    )


# ============================================================================
# New Models - Opportunities
# ============================================================================

class Opportunity(Base):
    """
    A discovered opportunity (buyer, market, FPO route, etc.) for a farmer lot.
    Retains full provenance.
    """
    __tablename__ = "opportunities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lot_id = Column(UUID(as_uuid=True), ForeignKey("farmer_lots.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Source of opportunity
    opportunity_type = Column(String(50), nullable=False, index=True)   # BUYER | MARKET | FPO | FALLBACK
    buyer_requirement_id = Column(UUID(as_uuid=True), ForeignKey("buyer_requirements.id", ondelete="CASCADE"))
    market_id = Column(UUID(as_uuid=True), ForeignKey("markets.id", ondelete="CASCADE"))
    
    # Feasibility result
    feasibility_decision = Column(String(50), nullable=False, index=True)  # EXECUTABLE | RECOVERABLE | NOT_VIABLE | INSUFFICIENT_DATA
    blocking_constraints = Column(Text)                # JSON array of constraint types
    opportunity_gap = Column(Text)                     # JSON object with gap details
    minimum_viable_change = Column(Text)               # JSON object with recovery options
    
    # Financial
    offered_price_per_unit = Column(Numeric(10, 2))
    estimated_net_realization = Column(Numeric(15, 2))
    
    # Provenance
    source_type = Column(String(50), nullable=False)   # VERIFIED | REFERENCE | DEMO | OBSERVED
    data_quality = Column(String(20))                  # HIGH | MEDIUM | LOW
    
    # Ranking
    rank = Column(Integer)
    confidence_score = Column(Numeric(5, 2))           # 0.00 – 100.00 (explainable, not opaque AI)
    explanation = Column(Text)
    applied_recovery = Column(Text)                    # JSON overlay used for re-evaluation
    title = Column(String(255))
    warnings = Column(Text)                            # JSON array
    
    analyzed_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    lot = relationship("FarmerLot", back_populates="opportunities")
    buyer_requirement = relationship("BuyerRequirement", back_populates="opportunities")
    market = relationship("Market")

    __table_args__ = (
        Index("idx_opportunity_lot", "lot_id"),
        Index("idx_opportunity_type", "opportunity_type"),
        Index("idx_opportunity_feasibility", "feasibility_decision"),
    )


# ============================================================================
# New Models - Aggregation
# ============================================================================

class AggregationGroup(Base):
    """
    A group of compatible farmer lots aggregated to meet buyer requirements.
    """
    __tablename__ = "aggregation_groups"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    commodity_id = Column(UUID(as_uuid=True), ForeignKey("commodities.id", ondelete="CASCADE"), nullable=False)
    buyer_requirement_id = Column(UUID(as_uuid=True), ForeignKey("buyer_requirements.id", ondelete="CASCADE"))
    
    # Aggregated totals
    total_quantity = Column(Numeric(15, 2), nullable=False)
    member_count = Column(Integer, nullable=False)
    
    # Constraints that must match
    quality_grade = Column(String(50))
    state = Column(String(100))
    district = Column(String(100))
    
    # Timing
    earliest_available = Column(Date)
    latest_sell_by = Column(Date)
    
    # Status
    status = Column(String(20), default="forming")    # FORMING | COMMITTED | EXECUTING | COMPLETED | DISSOLVED
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    commodity = relationship("Commodity")
    buyer_requirement = relationship("BuyerRequirement")
    members = relationship("AggregationMember", back_populates="group", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_agg_commodity", "commodity_id"),
        Index("idx_agg_status", "status"),
    )


class AggregationMember(Base):
    """
    Individual farmer lot participation in an aggregation group.
    """
    __tablename__ = "aggregation_members"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    group_id = Column(UUID(as_uuid=True), ForeignKey("aggregation_groups.id", ondelete="CASCADE"), nullable=False)
    lot_id = Column(UUID(as_uuid=True), ForeignKey("farmer_lots.id", ondelete="CASCADE"), nullable=False)
    
    committed_quantity = Column(Numeric(10, 2), nullable=False)   # May be less than lot's total quantity
    
    joined_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    group = relationship("AggregationGroup", back_populates="members")
    lot = relationship("FarmerLot", back_populates="aggregation_memberships")

    __table_args__ = (
        Index("idx_agg_member_group", "group_id"),
        Index("idx_agg_member_lot", "lot_id"),
        UniqueConstraint("group_id", "lot_id", name="uq_group_lot"),
    )


# ============================================================================
# New Models - Negotiation (Offers)
# ============================================================================

class Offer(Base):
    """
    Negotiation offer between buyer and farmer.
    Supports offer → counter-offer → accept/reject flow.
    """
    __tablename__ = "offers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lot_id = Column(UUID(as_uuid=True), ForeignKey("farmer_lots.id", ondelete="CASCADE"), nullable=False, index=True)
    buyer_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    buyer_requirement_id = Column(UUID(as_uuid=True), ForeignKey("buyer_requirements.id", ondelete="SET NULL"))
    
    # Parent offer (for counter-offers)
    parent_offer_id = Column(UUID(as_uuid=True), ForeignKey("offers.id", ondelete="CASCADE"))
    
    # Terms
    offered_price_per_quintal = Column(Numeric(10, 2), nullable=False)
    quantity_quintal = Column(Numeric(10, 2), nullable=False)
    payment_days = Column(Integer, nullable=False)
    payment_method = Column(String(50))
    pickup_date = Column(Date)
    quality_terms = Column(Text)
    transport_responsibility = Column(String(50))     # FARMER | BUYER | SHARED
    
    # Status
    status = Column(String(20), nullable=False, default="pending", index=True)
    expires_at = Column(DateTime, nullable=False)
    
    # Snapshot of accepted terms
    accepted_at = Column(DateTime)
    accepted_terms_snapshot = Column(Text)            # JSON snapshot of final terms
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    lot = relationship("FarmerLot")
    buyer_user = relationship("User", back_populates="offers_made", foreign_keys=[buyer_id])
    buyer_requirement = relationship("BuyerRequirement")
    parent_offer = relationship("Offer", remote_side=[id])
    transactions = relationship("Transaction", back_populates="offer")

    __table_args__ = (
        Index("idx_offer_lot", "lot_id"),
        Index("idx_offer_buyer", "buyer_id"),
        Index("idx_offer_status", "status"),
    )


# ============================================================================
# New Models - Transactions
# ============================================================================

class Transaction(Base):
    """
    Tracks the lifecycle of an accepted offer from pickup to payment.
    """
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    offer_id = Column(UUID(as_uuid=True), ForeignKey("offers.id", ondelete="CASCADE"), nullable=False, index=True)
    lot_id = Column(UUID(as_uuid=True), ForeignKey("farmer_lots.id", ondelete="CASCADE"), nullable=False)
    farmer_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    buyer_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Agreed terms (snapshot from offer)
    agreed_price_per_quintal = Column(Numeric(10, 2), nullable=False)
    agreed_quantity = Column(Numeric(10, 2), nullable=False)
    agreed_payment_days = Column(Integer, nullable=False)
    
    # Actual delivery details
    actual_quantity_delivered = Column(Numeric(10, 2))
    actual_quality_grade = Column(String(50))
    delivery_date = Column(Date)
    delivery_location = Column(String(255))
    
    # Payment tracking
    payment_status = Column(String(50), default="payment_pending", index=True)
    payment_due_date = Column(Date)
    payment_reported_date = Column(Date)
    payment_confirmed_date = Column(Date)
    payment_amount = Column(Numeric(15, 2))
    
    # Status
    status = Column(String(20), nullable=False, default="accepted", index=True)
    
    # Dispute handling
    is_disputed = Column(Boolean, default=False)
    dispute_reason = Column(Text)
    dispute_resolved_at = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    offer = relationship("Offer", back_populates="transactions")
    lot = relationship("FarmerLot")
    farmer = relationship("User", foreign_keys=[farmer_id])
    buyer = relationship("User", foreign_keys=[buyer_id])
    events = relationship("TransactionEvent", back_populates="transaction", cascade="all, delete-orphan", order_by="TransactionEvent.created_at")
    payment = relationship("Payment", uselist=False, back_populates="transaction", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="transaction")

    __table_args__ = (
        Index("idx_transaction_offer", "offer_id"),
        Index("idx_transaction_farmer", "farmer_id"),
        Index("idx_transaction_buyer", "buyer_id"),
        Index("idx_transaction_status", "status"),
    )


class TransactionEvent(Base):
    """
    Immutable event log for transaction lifecycle.
    """
    __tablename__ = "transaction_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_id = Column(UUID(as_uuid=True), ForeignKey("transactions.id", ondelete="CASCADE"), nullable=False, index=True)
    
    event_type = Column(String(50), nullable=False, index=True)   # OFFER_ACCEPTED | PICKUP_SCHEDULED | DELIVERED | etc.
    event_data = Column(Text)                                      # JSON with event-specific details
    actor_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    transaction = relationship("Transaction", back_populates="events")
    actor = relationship("User")

    __table_args__ = (
        Index("idx_event_transaction", "transaction_id"),
        Index("idx_event_type", "event_type"),
    )


# ============================================================================
# New Models - Payments
# ============================================================================

class Payment(Base):
    """
    Payment tracking and confirmation for transactions.
    """
    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_id = Column(UUID(as_uuid=True), ForeignKey("transactions.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    
    # Payment details
    payment_status = Column(String(50), nullable=False, default="agreed", index=True)
    payment_method = Column(String(50))
    payment_amount = Column(Numeric(15, 2), nullable=False)
    payment_due_date = Column(Date, nullable=False)
    
    # Confirmation flow
    buyer_reported_paid_at = Column(DateTime)
    buyer_payment_reference = Column(String(255))
    farmer_confirmed_at = Column(DateTime)
    
    # Protection (only if actual provider integrated)
    is_protected = Column(Boolean, default=False)
    protection_provider = Column(String(100))          # NULL unless real escrow integrated
    
    # Dispute
    is_disputed = Column(Boolean, default=False)
    dispute_details = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    transaction = relationship("Transaction", back_populates="payment")

    __table_args__ = (
        Index("idx_payment_status", "payment_status"),
    )


# ============================================================================
# New Models - Reviews and Trust
# ============================================================================

class Review(Base):
    """
    Post-transaction reviews for trust metrics.
    """
    __tablename__ = "reviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_id = Column(UUID(as_uuid=True), ForeignKey("transactions.id", ondelete="CASCADE"), nullable=False, index=True)
    reviewer_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    reviewee_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Ratings (1-5 scale)
    overall_rating = Column(Integer, nullable=False)
    payment_reliability = Column(Integer)              # For buyer reviews
    pickup_reliability = Column(Integer)
    communication_rating = Column(Integer)
    fair_negotiation_rating = Column(Integer)
    quantity_accuracy = Column(Integer)                # For farmer reviews
    quality_accuracy = Column(Integer)
    
    # Text feedback
    review_text = Column(Text)
    
    # Verification
    is_verified_transaction = Column(Boolean, default=True)   # Only reviews from actual transactions
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    transaction = relationship("Transaction", back_populates="reviews")
    reviewer = relationship("User", back_populates="reviews_written", foreign_keys=[reviewer_id])
    reviewee = relationship("User", back_populates="reviews_received", foreign_keys=[reviewee_id])

    __table_args__ = (
        Index("idx_review_transaction", "transaction_id"),
        Index("idx_review_reviewee", "reviewee_id"),
        UniqueConstraint("transaction_id", "reviewer_id", name="uq_transaction_reviewer"),
    )


# ============================================================================
# Keep existing Buyer model above this line
# ============================================================================

