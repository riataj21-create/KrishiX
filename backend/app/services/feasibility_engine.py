"""
KrishiX Feasibility Engine

Deterministic source of truth for whether a farmer can execute an opportunity.
AI must never override these decisions.
"""

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Any, Dict, List, Optional


class ConstraintType:
    QUANTITY = "QUANTITY"
    PRICE = "PRICE"
    TRANSPORT = "TRANSPORT"
    PAYMENT = "PAYMENT"
    QUALITY = "QUALITY"
    TIMING = "TIMING"
    DEADLINE = "DEADLINE"
    MISSING_DATA = "MISSING_DATA"


class ConstraintSeverity:
    HARD = "HARD"
    SOFT = "SOFT"


GRADE_RANK = {
    "a": 3,
    "grade a": 3,
    "grade_a": 3,
    "b": 2,
    "grade b": 2,
    "grade_b": 2,
    "c": 1,
    "grade c": 1,
    "grade_c": 1,
}

UNRECOVERABLE = {ConstraintType.QUALITY, ConstraintType.DEADLINE, ConstraintType.TIMING, ConstraintType.MISSING_DATA}


def _grade_rank(value: Optional[str]) -> Optional[int]:
    if not value:
        return None
    key = value.strip().lower()
    if key in ("any", "all", "unspecified"):
        return 0
    return GRADE_RANK.get(key)


def kg_from_quintals(qty: Decimal) -> Decimal:
    return (qty * Decimal("100")).quantize(Decimal("0.01"))


@dataclass
class FarmerLotData:
    quantity: Decimal
    quality_grade: Optional[str]
    minimum_price: Optional[Decimal]
    max_payment_days: int
    sell_by: date
    available_from: date
    max_transport_budget: Optional[Decimal]
    location_state: str
    location_district: str
    latitude: Optional[Decimal]
    longitude: Optional[Decimal]


@dataclass
class BuyerRequirementData:
    minimum_quantity: Decimal
    maximum_quantity: Optional[Decimal]
    required_grade: Optional[str]
    offered_price: Decimal
    payment_days: int
    pickup_available: bool
    pickup_location_state: Optional[str]
    pickup_location_district: Optional[str]
    buyer_latitude: Optional[Decimal]
    buyer_longitude: Optional[Decimal]
    active_until: date
    transport_cost_total: Optional[Decimal] = None
    transport_cost_source: str = "configured_demo"


@dataclass
class TransportData:
    distance_km: Decimal
    cost_total: Decimal
    method: str
    provenance: str


@dataclass
class RecoveryOverlay:
    extra_quantity: Decimal = Decimal("0")
    negotiated_payment_days: Optional[int] = None
    negotiated_price: Optional[Decimal] = None
    transport_cost_override: Optional[Decimal] = None
    assume_buyer_pickup: bool = False


@dataclass
class OpportunityGap:
    constraint_type: str
    required: Any
    available: Any
    gap: Any
    gap_unit: str
    explanation: str
    severity: str = ConstraintSeverity.HARD


@dataclass
class MinimumViableChange:
    change_type: str
    description: str
    parameters: Dict[str, Any]
    feasible: bool
    reason: str
    resulting_feasibility: str


@dataclass
class EconomicsBreakdown:
    sale_value: Decimal
    transport: Decimal
    transport_source: str
    market_charges: Decimal
    loading_handling: Decimal
    estimated_net: Decimal
    estimated_net_per_quintal: Decimal
    labels: Dict[str, str]


@dataclass
class FeasibilityResult:
    decision: str
    blocking_constraints: List[str]
    opportunity_gaps: List[OpportunityGap]
    minimum_viable_changes: List[MinimumViableChange]
    explanation: str
    confidence: Decimal
    warnings: List[str]
    economics: Optional[EconomicsBreakdown] = None
    effective_quantity: Optional[Decimal] = None


class FeasibilityEngine:
    def __init__(self):
        self._reset()

    def evaluate(
        self,
        farmer_lot: FarmerLotData,
        buyer_req: BuyerRequirementData,
        transport: Optional[TransportData] = None,
        market_charges: Optional[Decimal] = None,
        overlay: Optional[RecoveryOverlay] = None,
        today: Optional[date] = None,
    ) -> FeasibilityResult:
        self._reset()
        today = today or date.today()
        overlay = overlay or RecoveryOverlay()

        lot, req, transport = self._apply_overlay(farmer_lot, buyer_req, transport, overlay)
        # Realization is for THIS farmer's original quantity, not the aggregated pool.
        econ_lot = FarmerLotData(
            quantity=farmer_lot.quantity,
            quality_grade=lot.quality_grade,
            minimum_price=lot.minimum_price,
            max_payment_days=lot.max_payment_days,
            sell_by=lot.sell_by,
            available_from=lot.available_from,
            max_transport_budget=lot.max_transport_budget,
            location_state=lot.location_state,
            location_district=lot.location_district,
            latitude=lot.latitude,
            longitude=lot.longitude,
        )

        self._check_missing_data(lot, req)
        if ConstraintType.MISSING_DATA in self.blocking_constraints:
            return self._build_result("INSUFFICIENT_DATA", lot)

        self._check_deadline(lot, req, today)
        self._check_quantity(lot, req)
        self._check_quality(lot, req)
        self._check_payment(lot, req)
        self._check_timing(lot, req)
        self._check_price_and_transport(econ_lot, req, transport, market_charges)

        economics = self._economics(econ_lot, req, transport, market_charges)

        if not self.blocking_constraints:
            return self._build_result("EXECUTABLE", lot, economics)

        if self._is_recoverable():
            return self._build_result("RECOVERABLE", lot, economics)
        return self._build_result("NOT_VIABLE", lot, economics)

    def _reset(self):
        self.blocking_constraints: List[str] = []
        self.opportunity_gaps: List[OpportunityGap] = []
        self.minimum_viable_changes: List[MinimumViableChange] = []
        self.warnings: List[str] = []
        self.confidence = Decimal("100.0")
        self.unrecoverable_hard: List[str] = []

    def _apply_overlay(
        self,
        farmer_lot: FarmerLotData,
        buyer_req: BuyerRequirementData,
        transport: Optional[TransportData],
        overlay: RecoveryOverlay,
    ):
        qty = farmer_lot.quantity + (overlay.extra_quantity or Decimal("0"))
        lot = FarmerLotData(
            quantity=qty,
            quality_grade=farmer_lot.quality_grade,
            minimum_price=farmer_lot.minimum_price,
            max_payment_days=farmer_lot.max_payment_days,
            sell_by=farmer_lot.sell_by,
            available_from=farmer_lot.available_from,
            max_transport_budget=farmer_lot.max_transport_budget,
            location_state=farmer_lot.location_state,
            location_district=farmer_lot.location_district,
            latitude=farmer_lot.latitude,
            longitude=farmer_lot.longitude,
        )
        offered = overlay.negotiated_price if overlay.negotiated_price is not None else buyer_req.offered_price
        pay_days = overlay.negotiated_payment_days if overlay.negotiated_payment_days is not None else buyer_req.payment_days
        pickup = buyer_req.pickup_available or overlay.assume_buyer_pickup
        req = BuyerRequirementData(
            minimum_quantity=buyer_req.minimum_quantity,
            maximum_quantity=buyer_req.maximum_quantity,
            required_grade=buyer_req.required_grade,
            offered_price=offered,
            payment_days=pay_days,
            pickup_available=pickup,
            pickup_location_state=buyer_req.pickup_location_state,
            pickup_location_district=buyer_req.pickup_location_district,
            buyer_latitude=buyer_req.buyer_latitude,
            buyer_longitude=buyer_req.buyer_longitude,
            active_until=buyer_req.active_until,
            transport_cost_total=buyer_req.transport_cost_total,
            transport_cost_source=buyer_req.transport_cost_source,
        )
        if overlay.assume_buyer_pickup:
            transport = TransportData(
                distance_km=Decimal("0"),
                cost_total=Decimal("0"),
                method="BUYER_PICKUP",
                provenance="buyer_pickup",
            )
        elif overlay.transport_cost_override is not None:
            transport = TransportData(
                distance_km=transport.distance_km if transport else Decimal("0"),
                cost_total=overlay.transport_cost_override,
                method=transport.method if transport else "CONFIGURED_OVERRIDE",
                provenance="recovery_override",
            )
        return lot, req, transport

    def _add_block(self, constraint: str, recoverable: bool):
        if constraint not in self.blocking_constraints:
            self.blocking_constraints.append(constraint)
        if not recoverable and constraint not in self.unrecoverable_hard:
            self.unrecoverable_hard.append(constraint)

    def _check_missing_data(self, lot: FarmerLotData, req: BuyerRequirementData):
        missing = []
        if req.offered_price is None or req.offered_price <= 0:
            missing.append("buyer offered price")
        if req.minimum_quantity is None or req.minimum_quantity <= 0:
            missing.append("buyer minimum quantity")
        if lot.quantity is None or lot.quantity <= 0:
            missing.append("farmer lot quantity")
        if missing:
            self._add_block(ConstraintType.MISSING_DATA, False)
            self.opportunity_gaps.append(OpportunityGap(
                constraint_type=ConstraintType.MISSING_DATA,
                required="complete data",
                available="partial data",
                gap=", ".join(missing),
                gap_unit="fields",
                explanation=f"Cannot decide without: {', '.join(missing)}.",
                severity=ConstraintSeverity.HARD,
            ))

    def _check_deadline(self, lot: FarmerLotData, req: BuyerRequirementData, today: date):
        if lot.sell_by < lot.available_from:
            self._add_block(ConstraintType.DEADLINE, False)
            self.opportunity_gaps.append(OpportunityGap(
                constraint_type=ConstraintType.DEADLINE,
                required=str(lot.available_from),
                available=str(lot.sell_by),
                gap="invalid window",
                gap_unit="dates",
                explanation="This lot's sell-by date is before it becomes available.",
            ))
            return
        if lot.sell_by < today:
            self._add_block(ConstraintType.DEADLINE, False)
            self.opportunity_gaps.append(OpportunityGap(
                constraint_type=ConstraintType.DEADLINE,
                required=str(today),
                available=str(lot.sell_by),
                gap=(today - lot.sell_by).days,
                gap_unit="days",
                explanation=f"The selling window ended on {lot.sell_by}. This opportunity can no longer be used.",
            ))
        if req.active_until < today:
            self._add_block(ConstraintType.TIMING, False)
            self.opportunity_gaps.append(OpportunityGap(
                constraint_type=ConstraintType.TIMING,
                required=str(today),
                available=str(req.active_until),
                gap=(today - req.active_until).days,
                gap_unit="days",
                explanation=f"This opportunity expired on {req.active_until}.",
            ))

    def _check_quantity(self, lot: FarmerLotData, req: BuyerRequirementData):
        if lot.quantity < req.minimum_quantity:
            gap = req.minimum_quantity - lot.quantity
            self._add_block(ConstraintType.QUANTITY, True)
            self.opportunity_gaps.append(OpportunityGap(
                constraint_type=ConstraintType.QUANTITY,
                required=float(req.minimum_quantity),
                available=float(lot.quantity),
                gap=float(gap),
                gap_unit="quintals",
                explanation=(
                    f"Buyer needs at least {kg_from_quintals(req.minimum_quantity)} kg "
                    f"({req.minimum_quantity} quintals). This lot has "
                    f"{kg_from_quintals(lot.quantity)} kg ({lot.quantity} quintals) — "
                    f"short by {kg_from_quintals(gap)} kg."
                ),
            ))
            self.minimum_viable_changes.append(MinimumViableChange(
                change_type="AGGREGATION",
                description=f"Combine with other compatible lots totaling at least {kg_from_quintals(gap)} kg more.",
                parameters={
                    "additional_quantity_quintals": float(gap),
                    "additional_quantity_kg": float(kg_from_quintals(gap)),
                    "target_quantity_quintals": float(req.minimum_quantity),
                },
                feasible=True,
                reason="Quantity shortfalls can be closed by aggregating compatible lots.",
                resulting_feasibility="RECOVERABLE",
            ))
        if req.maximum_quantity and lot.quantity > req.maximum_quantity:
            extra = lot.quantity - req.maximum_quantity
            self._add_block(ConstraintType.QUANTITY, True)
            self.opportunity_gaps.append(OpportunityGap(
                constraint_type=ConstraintType.QUANTITY,
                required=float(req.maximum_quantity),
                available=float(lot.quantity),
                gap=float(extra),
                gap_unit="quintals",
                explanation=(
                    f"Buyer can take at most {kg_from_quintals(req.maximum_quantity)} kg; "
                    f"this lot is {kg_from_quintals(lot.quantity)} kg."
                ),
            ))
            self.minimum_viable_changes.append(MinimumViableChange(
                change_type="SPLIT_LOT",
                description=f"Sell only {kg_from_quintals(req.maximum_quantity)} kg to this buyer.",
                parameters={"sell_quantity_quintals": float(req.maximum_quantity)},
                feasible=True,
                reason="The extra quantity can be held back or sold elsewhere.",
                resulting_feasibility="RECOVERABLE",
            ))

    def _check_quality(self, lot: FarmerLotData, req: BuyerRequirementData):
        required = _grade_rank(req.required_grade)
        if required is None or required == 0:
            return
        available = _grade_rank(lot.quality_grade)
        if available is None:
            self.warnings.append("Lot grade is not specified; quality cannot be confirmed.")
            self.confidence -= Decimal("15")
            self._add_block(ConstraintType.QUALITY, False)
            self.opportunity_gaps.append(OpportunityGap(
                constraint_type=ConstraintType.QUALITY,
                required=req.required_grade,
                available=None,
                gap="UNSPECIFIED",
                gap_unit="grade",
                explanation=f"Buyer requires {req.required_grade}, but this lot has no recorded grade.",
            ))
            return
        if available < required:
            self._add_block(ConstraintType.QUALITY, False)
            self.opportunity_gaps.append(OpportunityGap(
                constraint_type=ConstraintType.QUALITY,
                required=req.required_grade,
                available=lot.quality_grade,
                gap="MISMATCH",
                gap_unit="grade",
                explanation=f"Buyer requires {req.required_grade}. This lot is {lot.quality_grade}, which does not meet that requirement.",
            ))
            self.minimum_viable_changes.append(MinimumViableChange(
                change_type="QUALITY_UPGRADE",
                description="Grade cannot be raised after harvest without sorting/processing that this platform does not perform.",
                parameters={"required_grade": req.required_grade, "current_grade": lot.quality_grade},
                feasible=False,
                reason="Quality is a hard constraint for already-harvested produce.",
                resulting_feasibility="NOT_VIABLE",
            ))

    def _check_payment(self, lot: FarmerLotData, req: BuyerRequirementData):
        if req.payment_days > lot.max_payment_days:
            gap = req.payment_days - lot.max_payment_days
            self._add_block(ConstraintType.PAYMENT, True)
            self.opportunity_gaps.append(OpportunityGap(
                constraint_type=ConstraintType.PAYMENT,
                required=lot.max_payment_days,
                available=req.payment_days,
                gap=gap,
                gap_unit="days",
                explanation=(
                    f"You need payment within {lot.max_payment_days} day(s). "
                    f"This buyer pays in {req.payment_days} days ({gap} days too slow)."
                ),
            ))
            self.minimum_viable_changes.append(MinimumViableChange(
                change_type="NEGOTIATE_PAYMENT",
                description=f"Ask the buyer to pay within {lot.max_payment_days} day(s) instead of {req.payment_days}.",
                parameters={
                    "current_payment_days": req.payment_days,
                    "target_payment_days": lot.max_payment_days,
                    "reduction_needed": gap,
                },
                feasible=True,
                reason="Payment timing can be negotiated; it is not guaranteed.",
                resulting_feasibility="RECOVERABLE",
            ))

    def _check_timing(self, lot: FarmerLotData, req: BuyerRequirementData):
        if lot.available_from > req.active_until:
            gap = (lot.available_from - req.active_until).days
            self._add_block(ConstraintType.TIMING, False)
            self.opportunity_gaps.append(OpportunityGap(
                constraint_type=ConstraintType.TIMING,
                required=str(req.active_until),
                available=str(lot.available_from),
                gap=gap,
                gap_unit="days",
                explanation=(
                    f"This lot is available from {lot.available_from}, but the opportunity closes on {req.active_until}."
                ),
            ))

    def _check_price_and_transport(
        self,
        lot: FarmerLotData,
        req: BuyerRequirementData,
        transport: Optional[TransportData],
        market_charges: Optional[Decimal],
    ):
        econ = self._economics(lot, req, transport, market_charges)

        if lot.minimum_price and req.offered_price < lot.minimum_price:
            gap = lot.minimum_price - req.offered_price
            self._add_block(ConstraintType.PRICE, True)
            self.opportunity_gaps.append(OpportunityGap(
                constraint_type=ConstraintType.PRICE,
                required=float(lot.minimum_price),
                available=float(req.offered_price),
                gap=float(gap),
                gap_unit="₹/quintal",
                explanation=(
                    f"You need at least ₹{lot.minimum_price}/quintal (₹{lot.minimum_price / 100}/kg). "
                    f"This opportunity offers ₹{req.offered_price}/quintal."
                ),
            ))
            self.minimum_viable_changes.append(MinimumViableChange(
                change_type="NEGOTIATE_PRICE",
                description=f"Negotiate a price of at least ₹{lot.minimum_price}/quintal.",
                parameters={"current_price": float(req.offered_price), "target_price": float(lot.minimum_price)},
                feasible=True,
                reason="Advertised price can be negotiated; it is not a guaranteed sale price.",
                resulting_feasibility="RECOVERABLE",
            ))

        transport_cost = econ.transport
        if lot.max_transport_budget is not None and transport_cost > lot.max_transport_budget:
            gap = transport_cost - lot.max_transport_budget
            self._add_block(ConstraintType.TRANSPORT, True)
            self.opportunity_gaps.append(OpportunityGap(
                constraint_type=ConstraintType.TRANSPORT,
                required=float(lot.max_transport_budget),
                available=float(transport_cost),
                gap=float(gap),
                gap_unit="₹",
                severity=ConstraintSeverity.HARD,
                explanation=(
                    f"Logistics cost ₹{transport_cost} ({econ.transport_source}) exceeds your ₹{lot.max_transport_budget} budget."
                ),
            ))
            self._transport_recovery(req, transport_cost, lot.max_transport_budget)

        if lot.minimum_price and econ.estimated_net_per_quintal < lot.minimum_price and req.offered_price >= lot.minimum_price:
            self._add_block(ConstraintType.TRANSPORT, True)
            self.opportunity_gaps.append(OpportunityGap(
                constraint_type=ConstraintType.TRANSPORT,
                required=float(lot.minimum_price),
                available=float(econ.estimated_net_per_quintal),
                gap=float(lot.minimum_price - econ.estimated_net_per_quintal),
                gap_unit="₹/quintal",
                explanation=(
                    f"After estimated logistics and known charges, expected realization is "
                    f"₹{econ.estimated_net_per_quintal}/quintal — below your ₹{lot.minimum_price}/quintal floor. "
                    f"This is not profit; it is estimated net after labelled costs."
                ),
            ))
            self._transport_recovery(req, transport_cost, None)

    def _transport_recovery(self, req: BuyerRequirementData, current_cost: Decimal, budget: Optional[Decimal]):
        if req.pickup_available:
            desc = "Use buyer pickup (this buyer already offers pickup)."
            pickup = True
        else:
            desc = "Ask for buyer pickup or shared transport so logistics cost falls enough to clear your price floor."
            pickup = False
        self.minimum_viable_changes.append(MinimumViableChange(
            change_type="TRANSPORT_OPTIMIZATION",
            description=desc,
            parameters={
                "current_cost": float(current_cost),
                "budget": float(budget) if budget is not None else None,
                "buyer_pickup_available": req.pickup_available,
                "cost_is": req.transport_cost_source or "configured_demo",
            },
            feasible=True,
            reason="Logistics cost here is a configured/demo estimate, not a live transporter quote.",
            resulting_feasibility="RECOVERABLE",
        ))
        if pickup:
            pass

    def _economics(
        self,
        lot: FarmerLotData,
        req: BuyerRequirementData,
        transport: Optional[TransportData],
        market_charges: Optional[Decimal],
    ) -> EconomicsBreakdown:
        qty = lot.quantity if lot.quantity > 0 else Decimal("1")
        sale = req.offered_price * lot.quantity
        if req.pickup_available:
            tcost = Decimal("0")
            tsrc = "buyer_pickup"
        elif transport:
            tcost = Decimal(str(transport.cost_total))
            tsrc = transport.provenance
        elif req.transport_cost_total is not None:
            tcost = Decimal(str(req.transport_cost_total))
            tsrc = req.transport_cost_source or "configured_demo"
        else:
            tcost = Decimal("0")
            tsrc = "not_provided"
            self.warnings.append("No transport figure provided; net realization excludes logistics.")

        charges = market_charges if market_charges is not None else Decimal("0")
        loading = Decimal("0")
        net = sale - tcost - charges - loading
        per = (net / qty) if qty else Decimal("0")
        return EconomicsBreakdown(
            sale_value=sale.quantize(Decimal("0.01")),
            transport=tcost.quantize(Decimal("0.01")),
            transport_source=tsrc,
            market_charges=charges.quantize(Decimal("0.01")),
            loading_handling=loading,
            estimated_net=net.quantize(Decimal("0.01")),
            estimated_net_per_quintal=per.quantize(Decimal("0.01")),
            labels={
                "sale_value": "Gross at offered price × this lot quantity — not a guaranteed receipt",
                "transport": f"Transport is {tsrc} — not a live quote unless source is a provider",
                "net": "Estimated realization, not profit",
            },
        )

    def _is_recoverable(self) -> bool:
        if self.unrecoverable_hard:
            return False
        feasible = [m for m in self.minimum_viable_changes if m.feasible]
        return bool(feasible)

    def _build_result(
        self,
        decision: str,
        lot: FarmerLotData,
        economics: Optional[EconomicsBreakdown] = None,
    ) -> FeasibilityResult:
        return FeasibilityResult(
            decision=decision,
            blocking_constraints=list(self.blocking_constraints),
            opportunity_gaps=list(self.opportunity_gaps),
            minimum_viable_changes=list(self.minimum_viable_changes),
            explanation=self._generate_explanation(decision),
            confidence=max(self.confidence, Decimal("0")),
            warnings=list(self.warnings),
            economics=economics,
            effective_quantity=lot.quantity,
        )

    def _generate_explanation(self, decision: str) -> str:
        if decision == "EXECUTABLE":
            return "This sale can go ahead with the lot as it stands. Advertised price is not a guaranteed receipt."
        if decision == "INSUFFICIENT_DATA":
            missing = [g.gap for g in self.opportunity_gaps if g.constraint_type == ConstraintType.MISSING_DATA]
            return f"Not enough information to decide: {', '.join(str(m) for m in missing)}."
        reasons = [g.explanation for g in self.opportunity_gaps]
        reason_text = " ".join(reasons) if reasons else ", ".join(self.blocking_constraints)
        if decision == "RECOVERABLE":
            changes = [m.description for m in self.minimum_viable_changes if m.feasible]
            change_text = " ".join(changes[:3])
            return f"This opportunity does not work yet. {reason_text} Smallest realistic changes: {change_text}"
        return f"This opportunity cannot be used. {reason_text}"


def evaluate_opportunity(
    farmer_lot: FarmerLotData,
    buyer_req: BuyerRequirementData,
    transport: Optional[TransportData] = None,
    market_charges: Optional[Decimal] = None,
    overlay: Optional[RecoveryOverlay] = None,
) -> FeasibilityResult:
    return FeasibilityEngine().evaluate(farmer_lot, buyer_req, transport, market_charges, overlay)
