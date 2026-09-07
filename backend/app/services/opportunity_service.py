"""Discover, analyze, rank, and recover opportunities for a farmer lot."""

from __future__ import annotations

import json
import logging
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy.orm import Session, joinedload

from app.models import BuyerRequirement, FarmerLot, Opportunity
from app.repository import (
    AggregationGroupRepository,
    BuyerRequirementRepository,
    FarmerLotRepository,
    MarketPriceRepository,
    OpportunityRepository,
)
from app.services.feasibility_engine import (
    BuyerRequirementData,
    FarmerLotData,
    FeasibilityEngine,
    FeasibilityResult,
    RecoveryOverlay,
    TransportData,
    kg_from_quintals,
)

logger = logging.getLogger("krishix.opportunity_service")

DECISION_RANK = {
    "EXECUTABLE": 0,
    "RECOVERABLE": 1,
    "NOT_VIABLE": 2,
    "INSUFFICIENT_DATA": 3,
}


def _as_uuid(value) -> Optional[UUID]:
    if value is None:
        return None
    if isinstance(value, UUID):
        return value
    return UUID(str(value))


def lot_to_data(lot: FarmerLot) -> FarmerLotData:
    return FarmerLotData(
        quantity=Decimal(str(lot.quantity)),
        quality_grade=lot.quality_grade,
        minimum_price=Decimal(str(lot.minimum_price)) if lot.minimum_price else None,
        max_payment_days=int(lot.max_payment_days or 2),
        sell_by=lot.sell_by,
        available_from=lot.available_from,
        max_transport_budget=Decimal(str(lot.max_transport_budget)) if lot.max_transport_budget else None,
        location_state=lot.state,
        location_district=lot.district,
        latitude=Decimal(str(lot.latitude)) if lot.latitude else None,
        longitude=Decimal(str(lot.longitude)) if lot.longitude else None,
    )


def buyer_req_to_data(buyer_req: BuyerRequirement) -> BuyerRequirementData:
    buyer = buyer_req.buyer
    return BuyerRequirementData(
        minimum_quantity=Decimal(str(buyer_req.minimum_quantity)),
        maximum_quantity=Decimal(str(buyer_req.maximum_quantity)) if buyer_req.maximum_quantity else None,
        required_grade=buyer_req.required_grade,
        offered_price=Decimal(str(buyer_req.offered_price)),
        payment_days=int(buyer_req.payment_days),
        pickup_available=bool(buyer_req.pickup_available),
        pickup_location_state=buyer_req.pickup_location_state,
        pickup_location_district=buyer_req.pickup_location_district,
        buyer_latitude=Decimal(str(buyer.latitude)) if buyer and buyer.latitude else None,
        buyer_longitude=Decimal(str(buyer.longitude)) if buyer and buyer.longitude else None,
        active_until=buyer_req.active_until,
        transport_cost_total=Decimal(str(buyer_req.transport_cost_total)) if getattr(buyer_req, "transport_cost_total", None) is not None else None,
        transport_cost_source=getattr(buyer_req, "transport_cost_source", None) or "configured_demo",
    )


def transport_for(req: BuyerRequirementData) -> Optional[TransportData]:
    if req.pickup_available:
        return TransportData(Decimal("0"), Decimal("0"), "BUYER_PICKUP", "buyer_pickup")
    if req.transport_cost_total is None:
        return None
    return TransportData(
        distance_km=Decimal("0"),
        cost_total=req.transport_cost_total,
        method="CONFIGURED_ESTIMATE",
        provenance=req.transport_cost_source or "configured_demo",
    )


def result_to_payload(result: FeasibilityResult) -> Dict[str, Any]:
    econ = None
    if result.economics:
        e = result.economics
        econ = {
            "sale_value": float(e.sale_value),
            "transport": float(e.transport),
            "transport_source": e.transport_source,
            "market_charges": float(e.market_charges),
            "loading_handling": float(e.loading_handling),
            "estimated_net": float(e.estimated_net),
            "estimated_net_per_quintal": float(e.estimated_net_per_quintal),
            "labels": e.labels,
        }
    return {
        "feasibility_decision": result.decision,
        "blocking_constraints": result.blocking_constraints,
        "opportunity_gaps": [
            {
                "constraint_type": g.constraint_type,
                "required": g.required,
                "available": g.available,
                "gap": g.gap,
                "gap_unit": g.gap_unit,
                "explanation": g.explanation,
                "severity": g.severity,
            }
            for g in result.opportunity_gaps
        ],
        "minimum_viable_changes": [
            {
                "change_type": m.change_type,
                "description": m.description,
                "parameters": m.parameters,
                "feasible": m.feasible,
                "reason": m.reason,
                "resulting_feasibility": m.resulting_feasibility,
            }
            for m in result.minimum_viable_changes
        ],
        "explanation": result.explanation,
        "confidence_score": float(result.confidence),
        "warnings": result.warnings,
        "economics": econ,
        "effective_quantity": float(result.effective_quantity) if result.effective_quantity is not None else None,
    }


def overlay_from_dict(data: Optional[dict]) -> RecoveryOverlay:
    data = data or {}
    extra = data.get("extra_quantity") or data.get("extra_quantity_quintals") or 0
    return RecoveryOverlay(
        extra_quantity=Decimal(str(extra)),
        negotiated_payment_days=data.get("negotiated_payment_days"),
        negotiated_price=Decimal(str(data["negotiated_price"])) if data.get("negotiated_price") is not None else None,
        transport_cost_override=Decimal(str(data["transport_cost_override"])) if data.get("transport_cost_override") is not None else None,
        assume_buyer_pickup=bool(data.get("assume_buyer_pickup")),
    )


class OpportunityService:
    def __init__(self, db: Session):
        self.db = db
        self.engine = FeasibilityEngine()

    def discover_and_analyze(
        self,
        lot_id: UUID,
        farmer_priority: str = "maximize_realization",
        consider_markets: bool = True,
        consider_buyers: bool = True,
        overlay: Optional[RecoveryOverlay] = None,
    ) -> List[Dict[str, Any]]:
        lot = FarmerLotRepository.get_by_id(self.db, lot_id)
        if not lot:
            raise ValueError(f"Lot {lot_id} not found")

        farmer_lot_data = lot_to_data(lot)
        opportunities: List[Dict[str, Any]] = []

        if consider_buyers:
            opportunities.extend(self._discover_from_buyers(lot, farmer_lot_data, overlay))
        if consider_markets:
            opportunities.extend(self._discover_from_markets(lot, farmer_lot_data, overlay))

        ranked = self._rank_opportunities(opportunities, farmer_priority)
        self._save_opportunities(lot_id, ranked)
        return ranked

    def analyze_existing(self, opportunity_id: UUID, overlay: Optional[RecoveryOverlay] = None) -> Dict[str, Any]:
        opp = self.db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
        if not opp:
            raise ValueError("Opportunity not found")
        lot = FarmerLotRepository.get_by_id(self.db, opp.lot_id)
        if not lot:
            raise ValueError("Lot not found")
        farmer_data = lot_to_data(lot)
        if opp.buyer_requirement_id:
            req = (
                self.db.query(BuyerRequirement)
                .options(joinedload(BuyerRequirement.buyer))
                .filter(BuyerRequirement.id == opp.buyer_requirement_id)
                .first()
            )
            if not req:
                raise ValueError("Buyer requirement not found")
            req_data = buyer_req_to_data(req)
            result = self.engine.evaluate(farmer_data, req_data, transport_for(req_data), overlay=overlay)
            payload = self._buyer_payload(req, result, overlay)
        else:
            payload = self._market_reanalyze(opp, lot, farmer_data, overlay)
        payload["id"] = str(opp.id)
        payload["lot_id"] = str(lot.id)
        if overlay:
            opp.applied_recovery = json.dumps(self._overlay_dict(overlay))
            opp.feasibility_decision = payload["feasibility_decision"]
            opp.blocking_constraints = json.dumps(payload["blocking_constraints"])
            opp.opportunity_gap = json.dumps(payload["opportunity_gaps"])
            opp.minimum_viable_change = json.dumps(payload["minimum_viable_changes"])
            opp.explanation = payload["explanation"]
            if payload.get("economics"):
                opp.estimated_net_realization = Decimal(str(payload["economics"]["estimated_net"]))
            self.db.commit()
            self.db.refresh(opp)
        payload["applied_recovery"] = json.loads(opp.applied_recovery) if opp.applied_recovery else None
        return payload

    def aggregation_plan(self, lot: FarmerLot, buyer_req: BuyerRequirement) -> Dict[str, Any]:
        needed = Decimal(str(buyer_req.minimum_quantity)) - Decimal(str(lot.quantity))
        if needed <= 0:
            return {
                "needed_quintals": 0,
                "needed_kg": 0,
                "can_aggregate": True,
                "members": [],
                "combined_quintals": float(lot.quantity),
                "reason": "This lot already meets the quantity requirement.",
            }
        others = FarmerLotRepository.find_compatible_for_aggregation(
            self.db,
            commodity_id=lot.commodity_id,
            quality_grade=buyer_req.required_grade if buyer_req.required_grade and buyer_req.required_grade.lower() != "any" else lot.quality_grade,
            state=lot.state,
            district=lot.district,
            exclude_lot_ids=[lot.id],
        )
        # Prefer lots that satisfy the buyer's grade
        members = []
        total = Decimal(str(lot.quantity))
        for other in others:
            if other.farmer_id == lot.farmer_id:
                continue
            if not self._grades_compatible(other.quality_grade, buyer_req.required_grade):
                continue
            if other.available_from > lot.sell_by or lot.available_from > other.sell_by:
                continue
            take = Decimal(str(other.quantity))
            members.append({
                "lot_id": str(other.id),
                "farmer_id": str(other.farmer_id),
                "quantity_quintals": float(take),
                "quantity_kg": float(kg_from_quintals(take)),
                "quality_grade": other.quality_grade,
                "district": other.district,
                "participant_type": "demo_simulated",
                "label": "Demo / simulated participant — not a live nationwide farmer network",
            })
            total += take
            if total >= Decimal(str(buyer_req.minimum_quantity)):
                break
        can = total >= Decimal(str(buyer_req.minimum_quantity))
        return {
            "needed_quintals": float(needed),
            "needed_kg": float(kg_from_quintals(needed)),
            "can_aggregate": can,
            "members": members,
            "combined_quintals": float(total),
            "combined_kg": float(kg_from_quintals(total)),
            "reason": (
                f"Compatible demo lots can supply {kg_from_quintals(total)} kg together."
                if can
                else f"Compatible lots only reach {kg_from_quintals(total)} kg; buyer needs {kg_from_quintals(Decimal(str(buyer_req.minimum_quantity)))} kg."
            ),
        }

    def apply_recovery(self, opportunity_id: UUID, change_types: List[str]) -> Dict[str, Any]:
        opp = self.db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
        if not opp or not opp.buyer_requirement_id:
            raise ValueError("Recovery is only available on buyer opportunities")
        lot = FarmerLotRepository.get_by_id(self.db, opp.lot_id)
        req = (
            self.db.query(BuyerRequirement)
            .options(joinedload(BuyerRequirement.buyer))
            .filter(BuyerRequirement.id == opp.buyer_requirement_id)
            .first()
        )
        overlay = RecoveryOverlay()
        aggregation = None
        types = {t.upper() for t in change_types}
        if "AGGREGATION" in types:
            aggregation = self.aggregation_plan(lot, req)
            extra = Decimal(str(aggregation["combined_quintals"])) - Decimal(str(lot.quantity))
            overlay.extra_quantity = extra if aggregation["can_aggregate"] else Decimal("0")
            if aggregation["can_aggregate"] and aggregation["members"]:
                group = AggregationGroupRepository.create(
                    self.db,
                    commodity_id=lot.commodity_id,
                    buyer_requirement_id=req.id,
                    total_quantity=Decimal(str(aggregation["combined_quintals"])),
                    member_count=len(aggregation["members"]) + 1,
                    quality_grade=req.required_grade or lot.quality_grade,
                    state=lot.state,
                    district=lot.district,
                    earliest_available=lot.available_from,
                    latest_sell_by=lot.sell_by,
                    status="forming",
                )
                AggregationGroupRepository.add_member(self.db, group.id, lot.id, float(lot.quantity))
                for member in aggregation["members"]:
                    AggregationGroupRepository.add_member(
                        self.db, group.id, UUID(member["lot_id"]), member["quantity_quintals"]
                    )
        if "NEGOTIATE_PAYMENT" in types:
            overlay.negotiated_payment_days = lot.max_payment_days
        if "NEGOTIATE_PRICE" in types and lot.minimum_price:
            overlay.negotiated_price = Decimal(str(lot.minimum_price))
        if "TRANSPORT_OPTIMIZATION" in types:
            overlay.assume_buyer_pickup = True
        analyzed = self.analyze_existing(opportunity_id, overlay)
        analyzed["aggregation"] = aggregation
        analyzed["applied_recovery"] = self._overlay_dict(overlay)
        return analyzed

    def _discover_from_buyers(self, lot, farmer_lot_data: FarmerLotData, overlay: Optional[RecoveryOverlay]):
        reqs = BuyerRequirementRepository.get_active_for_commodity(
            self.db, commodity_id=lot.commodity_id, state=None, min_quantity=None, limit=50
        )
        out = []
        for buyer_req in reqs:
            req_data = buyer_req_to_data(buyer_req)
            result = self.engine.evaluate(farmer_lot_data, req_data, transport_for(req_data), overlay=overlay)
            out.append(self._buyer_payload(buyer_req, result, overlay))
        return out

    def _buyer_payload(self, buyer_req: BuyerRequirement, result: FeasibilityResult, overlay: Optional[RecoveryOverlay]):
        payload = result_to_payload(result)
        buyer = buyer_req.buyer
        payload.update({
            "opportunity_type": "BUYER",
            "buyer_requirement_id": str(buyer_req.id),
            "market_id": None,
            "buyer_name": buyer.name if buyer else "Unknown",
            "buyer_type": buyer.buyer_type if buyer else None,
            "title": buyer.name if buyer else "Buyer opportunity",
            "offered_price": float(buyer_req.offered_price),
            "payment_days": buyer_req.payment_days,
            "required_grade": buyer_req.required_grade,
            "minimum_quantity": float(buyer_req.minimum_quantity),
            "pickup_available": bool(buyer_req.pickup_available),
            "source_type": (buyer_req.source_type or "demo").lower(),
            "data_quality": "DEMO" if (buyer_req.source_type or "").lower() in ("demo", "reference") else "MEDIUM",
            "price_kind": "buyer_offer",
            "price_note": "This is a demo/reference buyer offer, not a guaranteed sale price.",
            "applied_recovery": self._overlay_dict(overlay) if overlay else None,
        })
        if payload.get("economics"):
            payload["estimated_net_realization"] = payload["economics"]["estimated_net"]
        else:
            payload["estimated_net_realization"] = None
        return payload

    def _discover_from_markets(self, lot, farmer_lot_data: FarmerLotData, overlay: Optional[RecoveryOverlay]):
        prices = MarketPriceRepository.get_commodity_prices_by_date(
            self.db, commodity_id=lot.commodity_id, price_date=None, state=None, limit=10
        )
        out = []
        for price_record in prices:
            if not price_record.modal_price or not price_record.market:
                continue
            market = price_record.market
            market_as_buyer = BuyerRequirementData(
                minimum_quantity=Decimal("0.01"),
                maximum_quantity=None,
                required_grade=None,
                offered_price=Decimal(str(price_record.modal_price)),
                payment_days=0,
                pickup_available=False,
                pickup_location_state=market.state,
                pickup_location_district=market.district,
                buyer_latitude=Decimal(str(market.latitude)) if market.latitude else None,
                buyer_longitude=Decimal(str(market.longitude)) if market.longitude else None,
                active_until=date.today(),
                transport_cost_total=None,
                transport_cost_source="not_provided",
            )
            result = self.engine.evaluate(farmer_lot_data, market_as_buyer, overlay=overlay)
            payload = result_to_payload(result)
            payload.update({
                "opportunity_type": "MARKET",
                "buyer_requirement_id": None,
                "market_id": str(market.id),
                "buyer_name": None,
                "title": market.name,
                "market_name": market.name,
                "offered_price": float(price_record.modal_price),
                "payment_days": 0,
                "required_grade": None,
                "minimum_quantity": 0.01,
                "pickup_available": False,
                "source_type": "observed",
                "data_quality": "DEMO" if "sample" in (price_record.source or "").lower() else "MEDIUM",
                "price_kind": "market_price",
                "price_note": (
                    f"Mandi/modal price from {price_record.source} on {price_record.price_date}. "
                    "This is not the amount you are guaranteed to receive."
                ),
                "price_date": str(price_record.price_date),
                "price_source": price_record.source,
                "estimated_net_realization": payload["economics"]["estimated_net"] if payload.get("economics") else None,
                "applied_recovery": self._overlay_dict(overlay) if overlay else None,
            })
            out.append(payload)
        if not out:
            commodity_name = lot.commodity.name if lot.commodity else "this crop"
            out.append({
                "feasibility_decision": "INSUFFICIENT_DATA",
                "blocking_constraints": ["No verified market price is available for this crop in the selected markets."],
                "opportunity_gaps": [],
                "minimum_viable_changes": [],
                "explanation": (
                    f"KrishiX accepted {commodity_name}, but cannot calculate a sale price yet because "
                    "the backend has no observed mandi or buyer price for it. Add an approved market-price "
                    "source before treating any estimate as a real opportunity."
                ),
                "confidence_score": 0.0,
                "warnings": ["No verified price data; no price was invented."],
                "opportunity_type": "MARKET",
                "buyer_requirement_id": None,
                "market_id": None,
                "title": f"No verified price data for {commodity_name}",
                "offered_price": None,
                "estimated_net_realization": None,
                "source_type": "insufficient_data",
                "data_quality": "INSUFFICIENT_DATA",
                "price_kind": "market_price",
                "price_note": "No verified market price is available for this crop.",
                "applied_recovery": self._overlay_dict(overlay) if overlay else None,
            })
        return out

    def _market_reanalyze(self, opp: Opportunity, lot, farmer_data, overlay):
        # Recreate a market-style requirement from stored price
        req = BuyerRequirementData(
            minimum_quantity=Decimal("0.01"),
            maximum_quantity=None,
            required_grade=None,
            offered_price=Decimal(str(opp.offered_price_per_unit or 0)),
            payment_days=0,
            pickup_available=False,
            pickup_location_state=lot.state,
            pickup_location_district=lot.district,
            buyer_latitude=None,
            buyer_longitude=None,
            active_until=date.today(),
        )
        result = self.engine.evaluate(farmer_data, req, overlay=overlay)
        payload = result_to_payload(result)
        payload.update({
            "opportunity_type": "MARKET",
            "market_id": str(opp.market_id) if opp.market_id else None,
            "title": opp.title,
            "offered_price": float(opp.offered_price_per_unit or 0),
            "source_type": opp.source_type,
            "price_kind": "market_price",
        })
        return payload

    def _rank_opportunities(self, opportunities: List[Dict[str, Any]], farmer_priority: str):
        def sort_key(o):
            decision = DECISION_RANK.get(o.get("feasibility_decision"), 9)
            net = o.get("estimated_net_realization")
            if net is None:
                net = -10**12
            price = o.get("offered_price") or 0
            pay = o.get("payment_days", 99)
            if farmer_priority == "fastest_payment":
                return (decision, pay, -float(net))
            if farmer_priority == "lower_risk":
                return (decision, -float(o.get("confidence_score") or 0), -float(net))
            # maximize executable realization — never rank by advertised price alone
            return (decision, -float(net), -float(price))

        ranked = sorted(opportunities, key=sort_key)
        for i, opp in enumerate(ranked):
            opp["rank"] = i + 1
        return ranked

    def _save_opportunities(self, lot_id: UUID, opportunities: List[Dict[str, Any]]):
        OpportunityRepository.delete_by_lot(self.db, lot_id)
        saved = []
        for opp in opportunities:
            row = OpportunityRepository.create(
                self.db,
                lot_id=lot_id,
                opportunity_type=opp["opportunity_type"],
                buyer_requirement_id=_as_uuid(opp.get("buyer_requirement_id")),
                market_id=_as_uuid(opp.get("market_id")),
                feasibility_decision=opp["feasibility_decision"],
                blocking_constraints=json.dumps(opp.get("blocking_constraints") or []),
                opportunity_gap=json.dumps(opp.get("opportunity_gaps") or []),
                minimum_viable_change=json.dumps(opp.get("minimum_viable_changes") or []),
                offered_price_per_unit=Decimal(str(opp.get("offered_price") or 0)),
                estimated_net_realization=(
                    Decimal(str(opp["estimated_net_realization"]))
                    if opp.get("estimated_net_realization") is not None
                    else None
                ),
                source_type=opp.get("source_type") or "demo",
                data_quality=opp.get("data_quality") or "MEDIUM",
                rank=opp.get("rank"),
                confidence_score=Decimal(str(opp.get("confidence_score") or 0)),
                explanation=opp.get("explanation"),
                applied_recovery=json.dumps(opp["applied_recovery"]) if opp.get("applied_recovery") else None,
                title=opp.get("title"),
                warnings=json.dumps(opp.get("warnings") or []),
            )
            opp["id"] = str(row.id)
            opp["lot_id"] = str(lot_id)
            saved.append(opp)
        return saved

    @staticmethod
    def _overlay_dict(overlay: RecoveryOverlay) -> dict:
        return {
            "extra_quantity": float(overlay.extra_quantity),
            "negotiated_payment_days": overlay.negotiated_payment_days,
            "negotiated_price": float(overlay.negotiated_price) if overlay.negotiated_price is not None else None,
            "transport_cost_override": float(overlay.transport_cost_override) if overlay.transport_cost_override is not None else None,
            "assume_buyer_pickup": overlay.assume_buyer_pickup,
        }

    @staticmethod
    def _grades_compatible(lot_grade: Optional[str], required: Optional[str]) -> bool:
        if not required or required.lower() == "any":
            return True
        from app.services.feasibility_engine import _grade_rank
        have = _grade_rank(lot_grade)
        need = _grade_rank(required)
        if have is None or need is None:
            return False
        return have >= need
