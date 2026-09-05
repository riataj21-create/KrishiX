"""Pydantic schemas for request/response validation."""
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
from decimal import Decimal
from uuid import UUID


# ============================================================================
# User Schemas
# ============================================================================

class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    role: str = Field(default="farmer", pattern="^(farmer|buyer)$")


class LoginRequest(UserBase):
    password: str = Field(..., min_length=1)


class UserResponse(UserBase):
    id: UUID
    is_active: bool
    role: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None


class PasswordChange(BaseModel):
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8)


# ============================================================================
# Farmer Profile Schemas
# ============================================================================

class FarmerProfileBase(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=255)
    phone: Optional[str] = None
    state: str
    district: str
    village: Optional[str] = None
    postal_code: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    bio: Optional[str] = None


class FarmerProfileCreate(FarmerProfileBase):
    pass


class FarmerProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    village: Optional[str] = None
    postal_code: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    bio: Optional[str] = None


class FarmerProfileResponse(FarmerProfileBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Commodity Schemas
# ============================================================================

class CommodityBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    category: Optional[str] = None
    unit: str = Field(default="kg")
    description: Optional[str] = None


class CommodityCreate(CommodityBase):
    pass


class CommodityResponse(CommodityBase):
    id: UUID
    icon_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Market Schemas
# ============================================================================

class MarketBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    state: str
    district: str
    village: Optional[str] = None
    postal_code: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    market_type: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    website_url: Optional[str] = None
    description: Optional[str] = None


class MarketCreate(MarketBase):
    pass


class MarketResponse(MarketBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Market Price Schemas
# ============================================================================

class MarketPriceBase(BaseModel):
    min_price: Decimal = Field(..., gt=0)
    max_price: Decimal = Field(..., gt=0)
    modal_price: Optional[Decimal] = None
    quantity_traded: Optional[Decimal] = None
    source: str


class MarketPriceCreate(MarketPriceBase):
    market_id: UUID
    commodity_id: UUID
    price_date: str  # YYYY-MM-DD format


class MarketPriceResponse(BaseModel):
    id: UUID
    market_id: UUID
    commodity_id: UUID
    price_date: str
    min_price: Decimal
    max_price: Decimal
    modal_price: Optional[Decimal]
    quantity_traded: Optional[Decimal]
    source: str
    last_updated: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class MarketPriceWithDetails(MarketPriceResponse):
    market_name: Optional[str] = None
    commodity_name: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None


class PriceComparisonItem(BaseModel):
    market_id: UUID
    market_name: str
    state: str
    district: str
    modal_price: Decimal
    min_price: Decimal
    max_price: Decimal
    quantity_traded: Optional[Decimal]


class PriceComparisonResponse(BaseModel):
    commodity_id: UUID
    commodity_name: str
    date: str
    prices: list[PriceComparisonItem]


class PriceTrendItem(BaseModel):
    date: str
    min_price: Decimal
    max_price: Decimal
    modal_price: Optional[Decimal]


class PriceTrendResponse(BaseModel):
    market_id: UUID
    market_name: str
    commodity_id: UUID
    commodity_name: str
    trend: list[PriceTrendItem]


# ============================================================================
# Saved Market/Commodity Schemas
# ============================================================================

class SavedMarketBase(BaseModel):
    market_id: UUID


class SavedMarketResponse(BaseModel):
    id: UUID
    market_id: UUID
    market_name: str
    state: str
    district: str
    saved_at: datetime

    class Config:
        from_attributes = True


class SavedCommodityBase(BaseModel):
    commodity_id: UUID


class SavedCommodityResponse(BaseModel):
    id: UUID
    commodity_id: UUID
    commodity_name: str
    category: Optional[str]
    saved_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Pagination Schemas
# ============================================================================

class PaginatedResponse(BaseModel):
    total: int
    items: list


# ============================================================================
# Auth Schemas
# ============================================================================

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int


class TokenData(BaseModel):
    user_id: Optional[UUID] = None
    role: Optional[str] = None


# ============================================================================
# Farmer Lot Schemas
# ============================================================================

class FarmerLotBase(BaseModel):
    commodity_id: UUID
    quantity: Decimal = Field(..., gt=0)
    unit: str = "quintal"
    state: str
    district: str
    village: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    quality_status: Optional[str] = None
    quality_grade: Optional[str] = None
    quality_notes: Optional[str] = None
    available_from: str  # YYYY-MM-DD
    sell_by: str  # YYYY-MM-DD
    minimum_price: Optional[Decimal] = None
    max_payment_days: int = Field(default=2, ge=0, le=90)
    preferred_payment_method: Optional[str] = None
    transport_preference: Optional[str] = None
    max_transport_budget: Optional[Decimal] = None


class FarmerLotCreate(FarmerLotBase):
    pass


class FarmerLotUpdate(BaseModel):
    quantity: Optional[Decimal] = None
    quality_status: Optional[str] = None
    quality_grade: Optional[str] = None
    quality_notes: Optional[str] = None
    available_from: Optional[str] = None
    sell_by: Optional[str] = None
    minimum_price: Optional[Decimal] = None
    max_payment_days: Optional[int] = None
    preferred_payment_method: Optional[str] = None
    transport_preference: Optional[str] = None
    max_transport_budget: Optional[Decimal] = None
    status: Optional[str] = None


class FarmerLotResponse(FarmerLotBase):
    id: UUID
    farmer_id: UUID
    status: str
    reserved_by_offer_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Buyer Requirement Schemas
# ============================================================================

class BuyerRequirementBase(BaseModel):
    commodity_id: UUID
    minimum_quantity: Decimal = Field(..., gt=0)
    maximum_quantity: Optional[Decimal] = None
    required_grade: Optional[str] = None
    offered_price: Decimal = Field(..., gt=0)
    payment_days: int = Field(..., ge=0)
    payment_method: Optional[str] = None
    pickup_available: bool = False
    pickup_location_state: Optional[str] = None
    pickup_location_district: Optional[str] = None
    active_from: str  # YYYY-MM-DD
    active_until: str  # YYYY-MM-DD
    source_type: str = "reference"
    verification_status: Optional[str] = None
    notes: Optional[str] = None


class BuyerRequirementCreate(BuyerRequirementBase):
    buyer_id: UUID


class BuyerRequirementResponse(BuyerRequirementBase):
    id: UUID
    buyer_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Opportunity Schemas
# ============================================================================

class OpportunityBase(BaseModel):
    opportunity_type: str
    feasibility_decision: str
    blocking_constraints: Optional[str] = None
    opportunity_gap: Optional[str] = None
    minimum_viable_change: Optional[str] = None
    offered_price_per_unit: Optional[Decimal] = None
    estimated_net_realization: Optional[Decimal] = None
    source_type: str
    data_quality: Optional[str] = None
    rank: Optional[int] = None
    confidence_score: Optional[Decimal] = None


class OpportunityResponse(OpportunityBase):
    id: UUID
    lot_id: UUID
    buyer_requirement_id: Optional[UUID]
    market_id: Optional[UUID]
    analyzed_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class FeasibilityAnalysisRequest(BaseModel):
    lot_id: UUID
    consider_aggregation: bool = True
    farmer_priority: str = "maximize_realization"  # maximize_realization | fastest_payment | lower_risk


class FeasibilityAnalysisResponse(BaseModel):
    lot_id: UUID
    commodity_name: str
    quantity: Decimal
    opportunities: list[OpportunityResponse]
    recommendation: str
    data_caveat: str
    analyzed_at: datetime


# ============================================================================
# Aggregation Schemas
# ============================================================================

class AggregationGroupBase(BaseModel):
    commodity_id: UUID
    total_quantity: Decimal
    member_count: int
    quality_grade: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    status: str = "forming"


class AggregationGroupResponse(AggregationGroupBase):
    id: UUID
    buyer_requirement_id: Optional[UUID]
    earliest_available: Optional[str]
    latest_sell_by: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AggregationAnalysisRequest(BaseModel):
    lot_id: UUID
    target_buyer_requirement_id: Optional[UUID] = None


class AggregationAnalysisResponse(BaseModel):
    lot_id: UUID
    current_quantity: Decimal
    target_quantity: Optional[Decimal]
    quantity_gap: Optional[Decimal]
    compatible_lots: list
    can_aggregate: bool
    reason: str


# ============================================================================
# Offer (Negotiation) Schemas
# ============================================================================

class OfferBase(BaseModel):
    lot_id: UUID
    offered_price_per_quintal: Decimal = Field(..., gt=0)
    quantity_quintal: Decimal = Field(..., gt=0)
    payment_days: int = Field(..., ge=0)
    payment_method: Optional[str] = None
    pickup_date: Optional[str] = None
    quality_terms: Optional[str] = None
    transport_responsibility: Optional[str] = None


class OfferCreate(OfferBase):
    buyer_requirement_id: Optional[UUID] = None
    expires_in_hours: int = Field(default=48, ge=1, le=168)  # 1-168 hours


class OfferCounterCreate(BaseModel):
    offered_price_per_quintal: Decimal = Field(..., gt=0)
    quantity_quintal: Optional[Decimal] = None
    payment_days: Optional[int] = None
    payment_method: Optional[str] = None
    pickup_date: Optional[str] = None
    quality_terms: Optional[str] = None
    transport_responsibility: Optional[str] = None
    expires_in_hours: int = Field(default=48, ge=1, le=168)


class OfferResponse(OfferBase):
    id: UUID
    buyer_id: UUID
    buyer_requirement_id: Optional[UUID]
    parent_offer_id: Optional[UUID]
    status: str
    expires_at: datetime
    accepted_at: Optional[datetime]
    accepted_terms_snapshot: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Transaction Schemas
# ============================================================================

class TransactionBase(BaseModel):
    agreed_price_per_quintal: Decimal
    agreed_quantity: Decimal
    agreed_payment_days: int


class TransactionCreate(BaseModel):
    offer_id: UUID


class TransactionResponse(TransactionBase):
    id: UUID
    offer_id: UUID
    lot_id: UUID
    farmer_id: UUID
    buyer_id: UUID
    actual_quantity_delivered: Optional[Decimal]
    actual_quality_grade: Optional[str]
    delivery_date: Optional[str]
    delivery_location: Optional[str]
    payment_status: str
    payment_due_date: Optional[str]
    payment_reported_date: Optional[str]
    payment_confirmed_date: Optional[str]
    payment_amount: Optional[Decimal]
    status: str
    is_disputed: bool
    dispute_reason: Optional[str]
    dispute_resolved_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TransactionEventCreate(BaseModel):
    event_type: str
    event_data: Optional[str] = None


class TransactionEventResponse(BaseModel):
    id: UUID
    transaction_id: UUID
    event_type: str
    event_data: Optional[str]
    actor_id: Optional[UUID]
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Payment Schemas
# ============================================================================

class PaymentBase(BaseModel):
    payment_method: Optional[str] = None
    payment_amount: Decimal


class PaymentResponse(PaymentBase):
    id: UUID
    transaction_id: UUID
    payment_status: str
    payment_due_date: str
    buyer_reported_paid_at: Optional[datetime]
    buyer_payment_reference: Optional[str]
    farmer_confirmed_at: Optional[datetime]
    is_protected: bool
    protection_provider: Optional[str]
    is_disputed: bool
    dispute_details: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PaymentReportRequest(BaseModel):
    payment_reference: Optional[str] = None
    payment_date: Optional[str] = None  # YYYY-MM-DD


class PaymentConfirmRequest(BaseModel):
    confirmed: bool
    notes: Optional[str] = None


# ============================================================================
# Review Schemas
# ============================================================================

class ReviewBase(BaseModel):
    overall_rating: int = Field(..., ge=1, le=5)
    payment_reliability: Optional[int] = Field(None, ge=1, le=5)
    pickup_reliability: Optional[int] = Field(None, ge=1, le=5)
    communication_rating: Optional[int] = Field(None, ge=1, le=5)
    fair_negotiation_rating: Optional[int] = Field(None, ge=1, le=5)
    quantity_accuracy: Optional[int] = Field(None, ge=1, le=5)
    quality_accuracy: Optional[int] = Field(None, ge=1, le=5)
    review_text: Optional[str] = None


class ReviewCreate(ReviewBase):
    transaction_id: UUID


class ReviewResponse(ReviewBase):
    id: UUID
    transaction_id: UUID
    reviewer_id: UUID
    reviewee_id: UUID
    is_verified_transaction: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TrustMetricsResponse(BaseModel):
    user_id: UUID
    total_transactions: int
    successful_transactions: int
    disputed_transactions: int
    average_rating: Optional[Decimal]
    payment_reliability_avg: Optional[Decimal]
    communication_rating_avg: Optional[Decimal]
    on_time_delivery_rate: Optional[Decimal]
    total_reviews: int


# ============================================================================
# AI Copilot Schemas
# ============================================================================

class AIAskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000)
    context_lot_id: Optional[UUID] = None
    context_opportunity_id: Optional[UUID] = None
    context_transaction_id: Optional[UUID] = None


class AIAskResponse(BaseModel):
    answer: str
    sources: Optional[list] = None
    context_used: Optional[dict] = None
    provider_status: str  # AVAILABLE | DEGRADED | UNAVAILABLE


class AISearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    search_type: str = Field(default="agricultural_info")  # agricultural_info | market_info | scheme_info


class AISearchResponse(BaseModel):
    query: str
    results: list
    provider_status: str


# ============================================================================
# Demo Lab Schemas
# ============================================================================

class DemoScenarioResponse(BaseModel):
    id: str
    name: str
    description: str
    demonstrates: str
    parameters: dict


class DemoScenarioRunRequest(BaseModel):
    parameters: Optional[dict] = None


class DemoScenarioRunResponse(BaseModel):
    scenario_id: str
    scenario_name: str
    parameters_used: dict
    result: dict
    explanation: str
