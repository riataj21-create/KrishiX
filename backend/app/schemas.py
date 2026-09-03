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


class LoginRequest(UserBase):
    password: str = Field(..., min_length=1)


class UserResponse(UserBase):
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None


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
