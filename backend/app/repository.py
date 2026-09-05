"""Repository layer for database operations."""
from sqlalchemy.orm import Session, joinedload
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


# ============================================================================
# New Repositories
# ============================================================================

class FarmerLotRepository:
    """Farmer lot database operations."""

    @staticmethod
    def create(db: Session, farmer_id: UUID, **kwargs):
        from app.models import FarmerLot
        db_lot = FarmerLot(farmer_id=farmer_id, **kwargs)
        db.add(db_lot)
        db.commit()
        db.refresh(db_lot)
        return db_lot

    @staticmethod
    def get_by_id(db: Session, lot_id: UUID):
        from app.models import FarmerLot
        return db.query(FarmerLot).filter(FarmerLot.id == lot_id).first()

    @staticmethod
    def get_by_farmer(db: Session, farmer_id: UUID, status: Optional[str] = None, limit: int = 20, offset: int = 0):
        from app.models import FarmerLot
        query = db.query(FarmerLot).filter(FarmerLot.farmer_id == farmer_id)
        if status:
            query = query.filter(FarmerLot.status == status)
        total = query.count()
        items = query.order_by(desc(FarmerLot.created_at)).limit(limit).offset(offset).all()
        return total, items

    @staticmethod
    def update(db: Session, lot_id: UUID, **kwargs):
        from app.models import FarmerLot
        db_lot = db.query(FarmerLot).filter(FarmerLot.id == lot_id).first()
        if db_lot:
            for key, value in kwargs.items():
                if value is not None:
                    setattr(db_lot, key, value)
            db.commit()
            db.refresh(db_lot)
        return db_lot

    @staticmethod
    def delete(db: Session, lot_id: UUID) -> bool:
        from app.models import FarmerLot
        db_lot = db.query(FarmerLot).filter(FarmerLot.id == lot_id).first()
        if db_lot:
            db.delete(db_lot)
            db.commit()
            return True
        return False

    @staticmethod
    def find_compatible_for_aggregation(
        db: Session,
        commodity_id: UUID,
        quality_grade: Optional[str],
        state: str,
        district: str,
        exclude_lot_ids: List[UUID] = None
    ):
        """Find lots compatible for aggregation."""
        from app.models import FarmerLot
        query = db.query(FarmerLot).filter(
            and_(
                FarmerLot.commodity_id == commodity_id,
                FarmerLot.status == "available",
                FarmerLot.state == state,
                FarmerLot.district == district,
            )
        )
        if quality_grade:
            query = query.filter(FarmerLot.quality_grade == quality_grade)
        if exclude_lot_ids:
            query = query.filter(~FarmerLot.id.in_(exclude_lot_ids))
        return query.all()


class BuyerRequirementRepository:
    """Buyer requirement database operations."""

    @staticmethod
    def create(db: Session, **kwargs):
        from app.models import BuyerRequirement
        db_req = BuyerRequirement(**kwargs)
        db.add(db_req)
        db.commit()
        db.refresh(db_req)
        return db_req

    @staticmethod
    def get_by_id(db: Session, requirement_id: UUID):
        from app.models import BuyerRequirement
        return db.query(BuyerRequirement).filter(BuyerRequirement.id == requirement_id).first()

    @staticmethod
    def get_active_for_commodity(
        db: Session,
        commodity_id: UUID,
        state: Optional[str] = None,
        min_quantity: Optional[float] = None,
        limit: int = 20
    ):
        """Get active buyer requirements for a commodity."""
        from app.models import BuyerRequirement
        query = db.query(BuyerRequirement).options(joinedload(BuyerRequirement.buyer)).filter(
            and_(
                BuyerRequirement.commodity_id == commodity_id,
                BuyerRequirement.is_active == True,
            )
        )
        if state:
            query = query.filter(
                or_(
                    BuyerRequirement.pickup_location_state == state,
                    BuyerRequirement.pickup_location_state.is_(None),
                )
            )
        if min_quantity is not None:
            query = query.filter(
                or_(
                    BuyerRequirement.maximum_quantity.is_(None),
                    BuyerRequirement.maximum_quantity >= min_quantity,
                )
            )
        return query.limit(limit).all()


class OpportunityRepository:
    """Opportunity database operations."""

    @staticmethod
    def create(db: Session, **kwargs):
        from app.models import Opportunity
        db_opp = Opportunity(**kwargs)
        db.add(db_opp)
        db.commit()
        db.refresh(db_opp)
        return db_opp

    @staticmethod
    def get_by_id(db: Session, opportunity_id: UUID):
        from app.models import Opportunity
        return db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()

    @staticmethod
    def get_by_lot(db: Session, lot_id: UUID):
        from app.models import Opportunity
        return db.query(Opportunity).filter(Opportunity.lot_id == lot_id).order_by(Opportunity.rank).all()

    @staticmethod
    def delete_by_lot(db: Session, lot_id: UUID):
        """Delete all opportunities for a lot (e.g., before re-analysis)."""
        from app.models import Opportunity
        db.query(Opportunity).filter(Opportunity.lot_id == lot_id).delete()
        db.commit()


class OfferRepository:
    """Offer database operations."""

    @staticmethod
    def create(db: Session, **kwargs):
        from app.models import Offer
        db_offer = Offer(**kwargs)
        db.add(db_offer)
        db.commit()
        db.refresh(db_offer)
        return db_offer

    @staticmethod
    def get_by_id(db: Session, offer_id: UUID):
        from app.models import Offer
        return db.query(Offer).filter(Offer.id == offer_id).first()

    @staticmethod
    def get_by_lot(db: Session, lot_id: UUID):
        from app.models import Offer
        return db.query(Offer).filter(Offer.lot_id == lot_id).order_by(desc(Offer.created_at)).all()

    @staticmethod
    def get_by_buyer(db: Session, buyer_id: UUID, status: Optional[str] = None):
        from app.models import Offer
        query = db.query(Offer).filter(Offer.buyer_id == buyer_id)
        if status:
            query = query.filter(Offer.status == status)
        return query.order_by(desc(Offer.created_at)).all()

    @staticmethod
    def update(db: Session, offer_id: UUID, **kwargs):
        from app.models import Offer
        db_offer = db.query(Offer).filter(Offer.id == offer_id).first()
        if db_offer:
            for key, value in kwargs.items():
                setattr(db_offer, key, value)
            db.commit()
            db.refresh(db_offer)
        return db_offer


class TransactionRepository:
    """Transaction database operations."""

    @staticmethod
    def create(db: Session, **kwargs):
        from app.models import Transaction
        db_txn = Transaction(**kwargs)
        db.add(db_txn)
        db.commit()
        db.refresh(db_txn)
        return db_txn

    @staticmethod
    def get_by_id(db: Session, transaction_id: UUID):
        from app.models import Transaction
        return db.query(Transaction).filter(Transaction.id == transaction_id).first()

    @staticmethod
    def get_by_farmer(db: Session, farmer_id: UUID):
        from app.models import Transaction
        return db.query(Transaction).filter(Transaction.farmer_id == farmer_id).order_by(desc(Transaction.created_at)).all()

    @staticmethod
    def get_by_offer(db: Session, offer_id: UUID):
        from app.models import Transaction
        return db.query(Transaction).filter(Transaction.offer_id == offer_id).first()

    @staticmethod
    def get_by_buyer(db: Session, buyer_id: UUID):
        from app.models import Transaction
        return db.query(Transaction).filter(Transaction.buyer_id == buyer_id).order_by(desc(Transaction.created_at)).all()

    @staticmethod
    def update(db: Session, transaction_id: UUID, **kwargs):
        from app.models import Transaction
        db_txn = db.query(Transaction).filter(Transaction.id == transaction_id).first()
        if db_txn:
            for key, value in kwargs.items():
                setattr(db_txn, key, value)
            db.commit()
            db.refresh(db_txn)
        return db_txn


class TransactionEventRepository:
    """Transaction event database operations."""

    @staticmethod
    def create(db: Session, transaction_id: UUID, event_type: str, event_data: Optional[str], actor_id: Optional[UUID]):
        from app.models import TransactionEvent
        db_event = TransactionEvent(
            transaction_id=transaction_id,
            event_type=event_type,
            event_data=event_data,
            actor_id=actor_id
        )
        db.add(db_event)
        db.commit()
        db.refresh(db_event)
        return db_event

    @staticmethod
    def get_by_transaction(db: Session, transaction_id: UUID):
        from app.models import TransactionEvent
        return db.query(TransactionEvent).filter(
            TransactionEvent.transaction_id == transaction_id
        ).order_by(TransactionEvent.created_at).all()


class PaymentRepository:
    """Payment database operations."""

    @staticmethod
    def create(db: Session, **kwargs):
        from app.models import Payment
        db_payment = Payment(**kwargs)
        db.add(db_payment)
        db.commit()
        db.refresh(db_payment)
        return db_payment

    @staticmethod
    def get_by_transaction(db: Session, transaction_id: UUID):
        from app.models import Payment
        return db.query(Payment).filter(Payment.transaction_id == transaction_id).first()

    @staticmethod
    def update(db: Session, transaction_id: UUID, **kwargs):
        from app.models import Payment
        db_payment = db.query(Payment).filter(Payment.transaction_id == transaction_id).first()
        if db_payment:
            for key, value in kwargs.items():
                setattr(db_payment, key, value)
            db.commit()
            db.refresh(db_payment)
        return db_payment


class ReviewRepository:
    """Review database operations."""

    @staticmethod
    def create(db: Session, **kwargs):
        from app.models import Review
        db_review = Review(**kwargs)
        db.add(db_review)
        db.commit()
        db.refresh(db_review)
        return db_review

    @staticmethod
    def get_by_reviewee(db: Session, reviewee_id: UUID):
        from app.models import Review
        return db.query(Review).filter(Review.reviewee_id == reviewee_id).order_by(desc(Review.created_at)).all()

    @staticmethod
    def get_trust_metrics(db: Session, user_id: UUID) -> dict:
        """Calculate trust metrics for a user."""
        from app.models import Review, Transaction
        
        # Get all reviews received by this user
        reviews = db.query(Review).filter(Review.reviewee_id == user_id).all()
        
        # Get transaction counts
        transactions_as_farmer = db.query(Transaction).filter(Transaction.farmer_id == user_id).all()
        transactions_as_buyer = db.query(Transaction).filter(Transaction.buyer_id == user_id).all()
        all_transactions = transactions_as_farmer + transactions_as_buyer
        
        total_transactions = len(all_transactions)
        successful = len([t for t in all_transactions if t.status == "completed"])
        disputed = len([t for t in all_transactions if t.is_disputed])
        
        if not reviews:
            return {
                "total_transactions": total_transactions,
                "successful_transactions": successful,
                "disputed_transactions": disputed,
                "total_reviews": 0,
                "average_rating": None,
                "payment_reliability_avg": None,
                "communication_rating_avg": None,
            }
        
        avg_rating = sum(r.overall_rating for r in reviews) / len(reviews)
        payment_ratings = [r.payment_reliability for r in reviews if r.payment_reliability]
        comm_ratings = [r.communication_rating for r in reviews if r.communication_rating]
        
        return {
            "total_transactions": total_transactions,
            "successful_transactions": successful,
            "disputed_transactions": disputed,
            "total_reviews": len(reviews),
            "average_rating": round(avg_rating, 2),
            "payment_reliability_avg": round(sum(payment_ratings) / len(payment_ratings), 2) if payment_ratings else None,
            "communication_rating_avg": round(sum(comm_ratings) / len(comm_ratings), 2) if comm_ratings else None,
        }


class AggregationGroupRepository:
    """Aggregation group database operations."""

    @staticmethod
    def create(db: Session, **kwargs):
        from app.models import AggregationGroup
        db_group = AggregationGroup(**kwargs)
        db.add(db_group)
        db.commit()
        db.refresh(db_group)
        return db_group

    @staticmethod
    def get_by_id(db: Session, group_id: UUID):
        from app.models import AggregationGroup
        return db.query(AggregationGroup).filter(AggregationGroup.id == group_id).first()

    @staticmethod
    def add_member(db: Session, group_id: UUID, lot_id: UUID, committed_quantity: float):
        from app.models import AggregationMember
        db_member = AggregationMember(
            group_id=group_id,
            lot_id=lot_id,
            committed_quantity=committed_quantity
        )
        db.add(db_member)
        db.commit()
        db.refresh(db_member)
        return db_member
