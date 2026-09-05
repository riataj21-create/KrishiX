"""Repository layer for database operations."""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from datetime import date, timedelta
from uuid import UUID
from typing import Optional, List

from app.models import (
    User, FarmerProfile, Commodity, Market, MarketPrice,
    SavedMarket, SavedCommodity, Buyer
)
from app.auth import hash_password


class UserRepository:
    """User database operations."""

    @staticmethod
    def create(db: Session, email: str, password: str, role: str = "farmer") -> User:
        db_user = User(email=email, password_hash=hash_password(password), role=role)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_by_id(db: Session, user_id: UUID) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def update(db: Session, user_id: UUID, email: Optional[str] = None) -> Optional[User]:
        db_user = db.query(User).filter(User.id == user_id).first()
        if db_user:
            if email:
                db_user.email = email
            db.commit()
            db.refresh(db_user)
        return db_user


class FarmerProfileRepository:
    """Farmer profile database operations."""

    @staticmethod
    def create(db: Session, user_id: UUID, **kwargs) -> FarmerProfile:
        db_profile = FarmerProfile(user_id=user_id, **kwargs)
        db.add(db_profile)
        db.commit()
        db.refresh(db_profile)
        return db_profile

    @staticmethod
    def get_by_user_id(db: Session, user_id: UUID) -> Optional[FarmerProfile]:
        return db.query(FarmerProfile).filter(FarmerProfile.user_id == user_id).first()

    @staticmethod
    def update(db: Session, user_id: UUID, **kwargs) -> Optional[FarmerProfile]:
        db_profile = db.query(FarmerProfile).filter(FarmerProfile.user_id == user_id).first()
        if db_profile:
            for key, value in kwargs.items():
                if value is not None:
                    setattr(db_profile, key, value)
            db.commit()
            db.refresh(db_profile)
        return db_profile


class CommodityRepository:
    """Commodity database operations."""

    @staticmethod
    def create(db: Session, **kwargs) -> Commodity:
        db_commodity = Commodity(**kwargs)
        db.add(db_commodity)
        db.commit()
        db.refresh(db_commodity)
        return db_commodity

    @staticmethod
    def get_by_id(db: Session, commodity_id: UUID) -> Optional[Commodity]:
        return db.query(Commodity).filter(Commodity.id == commodity_id).first()

    @staticmethod
    def get_all(db: Session, category: Optional[str] = None, limit: int = 20, offset: int = 0):
        query = db.query(Commodity)
        if category:
            query = query.filter(Commodity.category == category)
        total = query.count()
        items = query.limit(limit).offset(offset).all()
        return total, items


class MarketRepository:
    """Market database operations."""

    @staticmethod
    def create(db: Session, **kwargs) -> Market:
        db_market = Market(**kwargs)
        db.add(db_market)
        db.commit()
        db.refresh(db_market)
        return db_market

    @staticmethod
    def get_by_id(db: Session, market_id: UUID) -> Optional[Market]:
        return db.query(Market).filter(Market.id == market_id).first()

    @staticmethod
    def get_by_location(db: Session, state: str, district: Optional[str] = None, limit: int = 20, offset: int = 0):
        query = db.query(Market).filter(Market.state == state)
        if district:
            query = query.filter(Market.district == district)
        total = query.count()
        items = query.limit(limit).offset(offset).all()
        return total, items

    @staticmethod
    def get_all(db: Session, limit: int = 20, offset: int = 0):
        query = db.query(Market)
        total = query.count()
        items = query.limit(limit).offset(offset).all()
        return total, items


class MarketPriceRepository:
    """Market price database operations."""

    @staticmethod
    def create(db: Session, **kwargs) -> MarketPrice:
        db_price = MarketPrice(**kwargs)
        db.add(db_price)
        db.commit()
        db.refresh(db_price)
        return db_price

    @staticmethod
    def get_by_id(db: Session, price_id: UUID) -> Optional[MarketPrice]:
        return db.query(MarketPrice).filter(MarketPrice.id == price_id).first()

    @staticmethod
    def get_latest_prices(db: Session, state: Optional[str] = None, district: Optional[str] = None,
                         market_id: Optional[UUID] = None, commodity_id: Optional[UUID] = None,
                         price_date: Optional[date] = None, limit: int = 20, offset: int = 0):
        query = db.query(MarketPrice).join(Market).join(Commodity)
        
        if state:
            query = query.filter(Market.state == state)
        if district:
            query = query.filter(Market.district == district)
        if market_id:
            query = query.filter(MarketPrice.market_id == market_id)
        if commodity_id:
            query = query.filter(MarketPrice.commodity_id == commodity_id)
        if price_date:
            query = query.filter(MarketPrice.price_date == price_date)
        else:
            # Fall back to the most recent date available in the database
            latest_date = db.query(func.max(MarketPrice.price_date)).scalar()
            if latest_date:
                query = query.filter(MarketPrice.price_date == latest_date)

        total = query.count()
        items = query.order_by(desc(MarketPrice.price_date)).limit(limit).offset(offset).all()
        return total, items

    @staticmethod
    def get_price_history(db: Session, market_id: UUID, commodity_id: UUID, days: int = 30) -> List[MarketPrice]:
        # Anchor to the latest available date, not today, so sample data always works
        latest_date = db.query(func.max(MarketPrice.price_date)).filter(
            and_(
                MarketPrice.market_id == market_id,
                MarketPrice.commodity_id == commodity_id,
            )
        ).scalar() or date.today()
        start_date = latest_date - timedelta(days=days)
        return db.query(MarketPrice).filter(
            and_(
                MarketPrice.market_id == market_id,
                MarketPrice.commodity_id == commodity_id,
                MarketPrice.price_date >= start_date,
                MarketPrice.price_date <= latest_date,
            )
        ).order_by(MarketPrice.price_date.asc()).all()

    @staticmethod
    def get_commodity_prices_by_date(db: Session, commodity_id: UUID, price_date: Optional[date],
                                    state: Optional[str] = None, limit: int = 20):
        # If no date given, use the most recent date available for this commodity
        if price_date is None:
            price_date = db.query(func.max(MarketPrice.price_date)).filter(
                MarketPrice.commodity_id == commodity_id
            ).scalar() or date.today()
        query = db.query(MarketPrice).join(Market).filter(
            and_(
                MarketPrice.commodity_id == commodity_id,
                MarketPrice.price_date == price_date
            )
        )
        if state:
            query = query.filter(Market.state == state)
        return query.order_by(desc(MarketPrice.modal_price)).limit(limit).all()


class SavedMarketRepository:
    """Saved market database operations."""

    @staticmethod
    def create(db: Session, user_id: UUID, market_id: UUID) -> SavedMarket:
        db_saved = SavedMarket(user_id=user_id, market_id=market_id)
        db.add(db_saved)
        db.commit()
        db.refresh(db_saved)
        return db_saved

    @staticmethod
    def get_by_user(db: Session, user_id: UUID, limit: int = 20, offset: int = 0):
        query = db.query(SavedMarket).filter(SavedMarket.user_id == user_id)
        total = query.count()
        items = query.limit(limit).offset(offset).all()
        return total, items

    @staticmethod
    def get_by_user_and_market(db: Session, user_id: UUID, market_id: UUID) -> Optional[SavedMarket]:
        return db.query(SavedMarket).filter(
            and_(SavedMarket.user_id == user_id, SavedMarket.market_id == market_id)
        ).first()

    @staticmethod
    def delete(db: Session, user_id: UUID, market_id: UUID) -> bool:
        saved = db.query(SavedMarket).filter(
            and_(SavedMarket.user_id == user_id, SavedMarket.market_id == market_id)
        ).first()
        if saved:
            db.delete(saved)
            db.commit()
            return True
        return False


class SavedCommodityRepository:
    """Saved commodity database operations."""

    @staticmethod
    def create(db: Session, user_id: UUID, commodity_id: UUID) -> SavedCommodity:
        db_saved = SavedCommodity(user_id=user_id, commodity_id=commodity_id)
        db.add(db_saved)
        db.commit()
        db.refresh(db_saved)
        return db_saved

    @staticmethod
    def get_by_user(db: Session, user_id: UUID, limit: int = 20, offset: int = 0):
        query = db.query(SavedCommodity).filter(SavedCommodity.user_id == user_id)
        total = query.count()
        items = query.limit(limit).offset(offset).all()
        return total, items

    @staticmethod
    def get_by_user_and_commodity(db: Session, user_id: UUID, commodity_id: UUID) -> Optional[SavedCommodity]:
        return db.query(SavedCommodity).filter(
            and_(SavedCommodity.user_id == user_id, SavedCommodity.commodity_id == commodity_id)
        ).first()

    @staticmethod
    def delete(db: Session, user_id: UUID, commodity_id: UUID) -> bool:
        saved = db.query(SavedCommodity).filter(
            and_(SavedCommodity.user_id == user_id, SavedCommodity.commodity_id == commodity_id)
        ).first()
        if saved:
            db.delete(saved)
            db.commit()
            return True
        return False


class BuyerRepository:
    """Buyer database operations."""

    @staticmethod
    def get_all(
        db: Session,
        commodity_name: Optional[str] = None,
        state: Optional[str] = None,
        buyer_type: Optional[str] = None,
        min_quantity: Optional[float] = None,
        limit: int = 20,
        offset: int = 0,
    ):
        """
        List buyers with optional filters.
        commodity_name match is case-insensitive contains search.
        """
        query = db.query(Buyer)

        if commodity_name:
            query = query.filter(
                Buyer.commodity_name.ilike(f"%{commodity_name}%")
            )
        if state:
            query = query.filter(Buyer.state == state)
        if buyer_type:
            query = query.filter(Buyer.buyer_type == buyer_type)
        if min_quantity is not None:
            # Buyer's max_quantity_quintal must cover the farmer's minimum
            query = query.filter(
                Buyer.max_quantity_quintal >= min_quantity
            )

        total = query.count()
        items = (
            query
            .order_by(desc(Buyer.is_verified), desc(Buyer.rating))
            .limit(limit)
            .offset(offset)
            .all()
        )
        return total, items

    @staticmethod
    def get_by_id(db: Session, buyer_id: UUID) -> Optional[Buyer]:
        return db.query(Buyer).filter(Buyer.id == buyer_id).first()
