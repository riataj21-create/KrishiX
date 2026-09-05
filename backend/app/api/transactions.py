"""Offers, transactions, and payment status (no real payments)."""

import json
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Buyer, BuyerRequirement, Offer, Opportunity, Payment, Transaction
from app.repository import (
    FarmerLotRepository,
    OfferRepository,
    PaymentRepository,
    TransactionEventRepository,
    TransactionRepository,
)
from app.schemas import OfferCreate, TokenData

router = APIRouter()

ALLOWED_TRANSITIONS = {
    "accepted": "pickup_scheduled",
    "pickup_scheduled": "delivered",
    "delivered": "payment_pending",
    "payment_pending": "payment_pending",
}

PAYMENT_NOTE = "KrishiX does not move money. Status is reported by the parties. Nothing here is protected, escrowed, or guaranteed."


class AdvanceRequest(BaseModel):
    event_type: Optional[str] = None


class PaymentReportBody(BaseModel):
    payment_reference: Optional[str] = None
    notes: Optional[str] = None
    demo_as_buyer: bool = Field(
        default=False,
        description="Allowed only for DEMO counterparties so the farmer can walk the full demo flow.",
    )


class PaymentConfirmBody(BaseModel):
    confirmed: bool = True
    notes: Optional[str] = None


def _lot_owner(db, lot_id, user_id):
    lot = FarmerLotRepository.get_by_id(db, lot_id)
    if not lot:
        raise HTTPException(status_code=404, detail="Lot not found")
    if lot.farmer_id != user_id:
        raise HTTPException(status_code=403, detail="You cannot access another farmer's data")
    return lot


def _serialize_offer(o: Offer) -> dict:
    return {
        "id": str(o.id),
        "lot_id": str(o.lot_id),
        "buyer_id": str(o.buyer_id),
        "buyer_requirement_id": str(o.buyer_requirement_id) if o.buyer_requirement_id else None,
        "parent_offer_id": str(o.parent_offer_id) if o.parent_offer_id else None,
        "offered_price_per_quintal": float(o.offered_price_per_quintal),
        "quantity_quintal": float(o.quantity_quintal),
        "payment_days": o.payment_days,
        "payment_method": o.payment_method,
        "pickup_date": str(o.pickup_date) if o.pickup_date else None,
        "quality_terms": o.quality_terms,
        "transport_responsibility": o.transport_responsibility,
        "status": o.status,
        "expires_at": o.expires_at,
        "accepted_at": o.accepted_at,
        "accepted_terms_snapshot": json.loads(o.accepted_terms_snapshot) if o.accepted_terms_snapshot else None,
        "created_at": o.created_at,
    }


def _serialize_txn(t: Transaction) -> dict:
    events = [
        {
            "id": str(e.id),
            "event_type": e.event_type,
            "event_data": e.event_data,
            "created_at": e.created_at,
        }
        for e in (t.events or [])
    ]
    payment = None
    if t.payment:
        p = t.payment
        payment = {
            "id": str(p.id),
            "payment_status": p.payment_status,
            "payment_method": p.payment_method,
            "payment_amount": float(p.payment_amount),
            "payment_due_date": str(p.payment_due_date),
            "buyer_reported_paid_at": p.buyer_reported_paid_at,
            "buyer_payment_reference": p.buyer_payment_reference,
            "farmer_confirmed_at": p.farmer_confirmed_at,
            "is_protected": bool(p.is_protected),
            "protection_provider": p.protection_provider,
            "is_disputed": bool(p.is_disputed),
            "disclaimer": PAYMENT_NOTE,
        }
    return {
        "id": str(t.id),
        "offer_id": str(t.offer_id),
        "lot_id": str(t.lot_id),
        "farmer_id": str(t.farmer_id),
        "buyer_id": str(t.buyer_id),
        "agreed_price_per_quintal": float(t.agreed_price_per_quintal),
        "agreed_quantity": float(t.agreed_quantity),
        "agreed_payment_days": t.agreed_payment_days,
        "payment_status": t.payment_status,
        "status": t.status,
        "is_disputed": t.is_disputed,
        "created_at": t.created_at,
        "updated_at": t.updated_at,
        "events": events,
        "payment": payment,
        "disclaimer": PAYMENT_NOTE,
    }


def _counterparty_user_id(db: Session, requirement_id: Optional[UUID], farmer_id: UUID) -> UUID:
    if requirement_id:
        req = db.query(BuyerRequirement).filter(BuyerRequirement.id == requirement_id).first()
        if req:
            buyer = db.query(Buyer).filter(Buyer.id == req.buyer_id).first()
            if buyer and buyer.user_id:
                return buyer.user_id
    # Fallback demo buyer user
    from app.models import User
    demo = db.query(User).filter(User.email == "buyer1@krishix.com").first()
    if demo:
        return demo.id
    raise HTTPException(status_code=400, detail="No buyer user is linked to this opportunity")


def _create_transaction_from_offer(db: Session, offer: Offer, actor_id: UUID) -> Transaction:
    existing = TransactionRepository.get_by_offer(db, offer.id)
    if existing:
        raise HTTPException(status_code=409, detail="A transaction already exists for this offer")
    amount = Decimal(str(offer.offered_price_per_quintal)) * Decimal(str(offer.quantity_quintal))
    due = date.today() + timedelta(days=int(offer.payment_days or 0))
    snapshot = {
        "price_per_quintal": float(offer.offered_price_per_quintal),
        "quantity_quintal": float(offer.quantity_quintal),
        "quality_terms": offer.quality_terms,
        "payment_days": offer.payment_days,
        "payment_method": offer.payment_method,
        "pickup_responsibility": offer.transport_responsibility,
        "transport_responsibility": offer.transport_responsibility,
        "expires_at": offer.expires_at.isoformat() if offer.expires_at else None,
    }
    offer.status = "accepted"
    offer.accepted_at = datetime.utcnow()
    offer.accepted_terms_snapshot = json.dumps(snapshot)
    db.commit()

    lot = FarmerLotRepository.get_by_id(db, offer.lot_id)
    txn = TransactionRepository.create(
        db,
        offer_id=offer.id,
        lot_id=offer.lot_id,
        farmer_id=lot.farmer_id,
        buyer_id=offer.buyer_id,
        agreed_price_per_quintal=offer.offered_price_per_quintal,
        agreed_quantity=offer.quantity_quintal,
        agreed_payment_days=offer.payment_days,
        payment_status="agreed",
        payment_due_date=due,
        payment_amount=amount,
        status="accepted",
    )
    FarmerLotRepository.update(db, offer.lot_id, status="reserved", reserved_by_offer_id=offer.id)
    TransactionEventRepository.create(db, txn.id, "OFFER_ACCEPTED", json.dumps(snapshot), actor_id)
    PaymentRepository.create(
        db,
        transaction_id=txn.id,
        payment_status="agreed",
        payment_method=offer.payment_method,
        payment_amount=amount,
        payment_due_date=due,
        is_protected=False,
        protection_provider=None,
    )
    return TransactionRepository.get_by_id(db, txn.id)


@router.post("/lots/{lot_id}/offers", status_code=status.HTTP_201_CREATED)
def create_offer(
    lot_id: UUID,
    body: OfferCreate,
    token_data: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = UUID(str(token_data.user_id))
    if body.lot_id != lot_id:
        raise HTTPException(status_code=400, detail="lot_id mismatch")
    lot = _lot_owner(db, lot_id, user_id)
    buyer_user_id = _counterparty_user_id(db, body.buyer_requirement_id, user_id)
    offer = OfferRepository.create(
        db,
        lot_id=lot.id,
        buyer_id=buyer_user_id,
        buyer_requirement_id=body.buyer_requirement_id,
        offered_price_per_quintal=body.offered_price_per_quintal,
        quantity_quintal=body.quantity_quintal,
        payment_days=body.payment_days,
        payment_method=body.payment_method,
        pickup_date=date.fromisoformat(body.pickup_date) if body.pickup_date else date.today(),
        quality_terms=body.quality_terms,
        transport_responsibility=body.transport_responsibility,
        status="pending",
        expires_at=datetime.utcnow() + timedelta(hours=body.expires_in_hours),
    )
    FarmerLotRepository.update(db, lot.id, status="offered")
    return _serialize_offer(offer)


@router.post("/opportunities/{opportunity_id}/offer", status_code=status.HTTP_201_CREATED)
def offer_from_opportunity(
    opportunity_id: UUID,
    token_data: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = UUID(str(token_data.user_id))
    opp = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    lot = _lot_owner(db, opp.lot_id, user_id)
    if opp.feasibility_decision not in ("EXECUTABLE", "executable"):
        raise HTTPException(
            status_code=400,
            detail="Only EXECUTABLE opportunities can be accepted. Apply recovery and re-check first.",
        )
    qty = lot.quantity
    pay_days = lot.max_payment_days
    if opp.applied_recovery:
        rec = json.loads(opp.applied_recovery)
        if rec.get("negotiated_payment_days") is not None:
            pay_days = rec["negotiated_payment_days"]
    buyer_user_id = _counterparty_user_id(db, opp.buyer_requirement_id, user_id)
    offer = OfferRepository.create(
        db,
        lot_id=lot.id,
        buyer_id=buyer_user_id,
        buyer_requirement_id=opp.buyer_requirement_id,
        offered_price_per_quintal=opp.offered_price_per_unit,
        quantity_quintal=qty,
        payment_days=pay_days,
        payment_method="UPI",
        pickup_date=date.today(),
        quality_terms=lot.quality_grade,
        transport_responsibility="BUYER" if opp.applied_recovery and json.loads(opp.applied_recovery).get("assume_buyer_pickup") else "FARMER",
        status="pending",
        expires_at=datetime.utcnow() + timedelta(hours=48),
    )
    FarmerLotRepository.update(db, lot.id, status="offered")
    return _serialize_offer(offer)


@router.post("/offers/{offer_id}/accept")
def accept_offer(
    offer_id: UUID,
    token_data: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = UUID(str(token_data.user_id))
    offer = OfferRepository.get_by_id(db, offer_id)
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    lot = FarmerLotRepository.get_by_id(db, offer.lot_id)
    if lot.farmer_id != user_id and offer.buyer_id != user_id:
        raise HTTPException(status_code=403, detail="Not a party to this offer")
    if offer.status == "accepted":
        txn = TransactionRepository.get_by_offer(db, offer.id)
        return _serialize_txn(txn)
    if offer.expires_at and offer.expires_at < datetime.utcnow():
        OfferRepository.update(db, offer.id, status="expired")
        raise HTTPException(status_code=400, detail="Offer has expired")
    txn = _create_transaction_from_offer(db, offer, user_id)
    return _serialize_txn(txn)


@router.get("/lots/{lot_id}/offers")
def list_offers(
    lot_id: UUID,
    token_data: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _lot_owner(db, lot_id, UUID(str(token_data.user_id)))
    return {"items": [_serialize_offer(o) for o in OfferRepository.get_by_lot(db, lot_id)]}


@router.get("/transactions")
def list_transactions(
    token_data: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = UUID(str(token_data.user_id))
    rows = TransactionRepository.get_by_farmer(db, user_id)
    return {"items": [_serialize_txn(t) for t in rows], "disclaimer": PAYMENT_NOTE}


@router.get("/transactions/{transaction_id}")
def get_transaction(
    transaction_id: UUID,
    token_data: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = UUID(str(token_data.user_id))
    txn = TransactionRepository.get_by_id(db, transaction_id)
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")
    if txn.farmer_id != user_id and txn.buyer_id != user_id:
        raise HTTPException(status_code=403, detail="Not a party to this transaction")
    return _serialize_txn(txn)


@router.post("/transactions/{transaction_id}/advance")
def advance_transaction(
    transaction_id: UUID,
    token_data: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = UUID(str(token_data.user_id))
    txn = TransactionRepository.get_by_id(db, transaction_id)
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")
    if txn.farmer_id != user_id and txn.buyer_id != user_id:
        raise HTTPException(status_code=403, detail="Not a party to this transaction")

    nxt = ALLOWED_TRANSITIONS.get(txn.status)
    if txn.status in ("paid", "completed", "cancelled"):
        raise HTTPException(status_code=400, detail="Transaction is already finished")
    if not nxt or nxt == txn.status:
        if txn.status == "payment_pending":
            raise HTTPException(status_code=400, detail="Use payment report/confirm endpoints")
        raise HTTPException(status_code=400, detail=f"Cannot advance from {txn.status}")

    event_map = {
        "pickup_scheduled": "PICKUP_SCHEDULED",
        "delivered": "DELIVERED",
        "payment_pending": "PAYMENT_PENDING",
    }
    TransactionRepository.update(db, txn.id, status=nxt)
    if nxt == "delivered":
        TransactionRepository.update(db, txn.id, delivery_date=date.today(), payment_status="payment_pending")
        PaymentRepository.update(db, txn.id, payment_status="payment_pending")
        TransactionRepository.update(db, txn.id, status="payment_pending")
        nxt = "payment_pending"
    TransactionEventRepository.create(db, txn.id, event_map.get(nxt, nxt.upper()), None, user_id)
    return _serialize_txn(TransactionRepository.get_by_id(db, txn.id))


@router.post("/transactions/{transaction_id}/payment/report")
def report_payment(
    transaction_id: UUID,
    body: PaymentReportBody,
    token_data: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = UUID(str(token_data.user_id))
    txn = TransactionRepository.get_by_id(db, transaction_id)
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")
    is_buyer = txn.buyer_id == user_id
    is_farmer = txn.farmer_id == user_id
    if not is_buyer and not (is_farmer and body.demo_as_buyer):
        raise HTTPException(status_code=403, detail="Only the buyer can report payment")
    PaymentRepository.update(
        db,
        txn.id,
        payment_status="buyer_reported_paid",
        buyer_reported_paid_at=datetime.utcnow(),
        buyer_payment_reference=body.payment_reference,
    )
    TransactionRepository.update(db, txn.id, payment_status="buyer_reported_paid")
    TransactionEventRepository.create(
        db, txn.id, "BUYER_REPORTED_PAID",
        json.dumps({"demo_as_buyer": body.demo_as_buyer, "reference": body.payment_reference}),
        user_id,
    )
    return _serialize_txn(TransactionRepository.get_by_id(db, txn.id))


@router.post("/transactions/{transaction_id}/payment/confirm")
def confirm_payment(
    transaction_id: UUID,
    body: PaymentConfirmBody,
    token_data: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = UUID(str(token_data.user_id))
    txn = TransactionRepository.get_by_id(db, transaction_id)
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")
    if txn.farmer_id != user_id:
        raise HTTPException(status_code=403, detail="Only the farmer can confirm receipt")
    if not body.confirmed:
        PaymentRepository.update(db, txn.id, payment_status="disputed", is_disputed=True, dispute_details=body.notes)
        TransactionRepository.update(db, txn.id, payment_status="disputed", is_disputed=True, dispute_reason=body.notes, status="disputed")
        TransactionEventRepository.create(db, txn.id, "PAYMENT_DISPUTED", body.notes, user_id)
        return _serialize_txn(TransactionRepository.get_by_id(db, txn.id))

    PaymentRepository.update(
        db, txn.id,
        payment_status="payment_confirmed",
        farmer_confirmed_at=datetime.utcnow(),
    )
    TransactionRepository.update(
        db, txn.id,
        payment_status="payment_confirmed",
        payment_confirmed_date=date.today(),
        status="completed",
    )
    FarmerLotRepository.update(db, txn.lot_id, status="sold")
    TransactionEventRepository.create(db, txn.id, "FARMER_CONFIRMED", None, user_id)
    TransactionEventRepository.create(db, txn.id, "PAYMENT_CONFIRMED", json.dumps({"note": PAYMENT_NOTE}), user_id)
    return _serialize_txn(TransactionRepository.get_by_id(db, txn.id))
