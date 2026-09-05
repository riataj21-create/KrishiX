"""
Feasibility engine unit tests — 12 scenarios.

These tests call the engine directly with no database or external APIs.
They verify the deterministic core of KrishiX.
"""
import pytest
from decimal import Decimal
from datetime import date, timedelta

from app.services.feasibility_engine import (
    FeasibilityEngine,
    FarmerLotData,
    BuyerRequirementData,
    TransportData,
    RecoveryOverlay,
    ConstraintType,
    evaluate_opportunity,
)

TODAY = date.today()
TOMORROW = TODAY + timedelta(days=1)
YESTERDAY = TODAY - timedelta(days=1)
IN_30 = TODAY + timedelta(days=30)


def _lot(
    quantity=Decimal("0.8"),
    grade="Grade B",
    min_price=Decimal("2800"),
    max_payment_days=2,
    sell_by=None,
    available_from=None,
    max_transport_budget=None,
    state="Andhra Pradesh",
    district="Madanapalle",
):
    return FarmerLotData(
        quantity=quantity,
        quality_grade=grade,
        minimum_price=min_price,
        max_payment_days=max_payment_days,
        sell_by=sell_by or TODAY,
        available_from=available_from or TODAY,
        max_transport_budget=max_transport_budget,
        location_state=state,
        location_district=district,
        latitude=Decimal("13.5504"),
        longitude=Decimal("78.5024"),
    )


def _buyer(
    min_qty=Decimal("3.0"),
    max_qty=None,
    grade="Grade A",
    price=Decimal("3400"),
    payment_days=7,
    pickup=False,
    active_until=None,
    transport_cost=Decimal("1500"),
):
    return BuyerRequirementData(
        minimum_quantity=min_qty,
        maximum_quantity=max_qty,
        required_grade=grade,
        offered_price=price,
        payment_days=payment_days,
        pickup_available=pickup,
        pickup_location_state="Andhra Pradesh",
        pickup_location_district="Madanapalle",
        buyer_latitude=Decimal("13.55"),
        buyer_longitude=Decimal("78.50"),
        active_until=active_until or IN_30,
        transport_cost_total=transport_cost,
        transport_cost_source="configured_demo",
    )


# ─────────────────────────────────────────────────────────────────────────────
# Scenario 1 — EXECUTABLE (farm-gate buyer, no constraints violated)
# ─────────────────────────────────────────────────────────────────────────────

def test_executable_farmgate():
    """Farm-gate buyer: Grade B, 50 kg min, immediate payment, pickup."""
    farmer = _lot(quantity=Decimal("0.8"), grade="Grade B", max_payment_days=2)
    buyer = _buyer(
        min_qty=Decimal("0.5"),
        grade="Grade B",
        price=Decimal("3000"),
        payment_days=0,
        pickup=True,
        transport_cost=Decimal("0"),
    )
    result = evaluate_opportunity(farmer, buyer)
    assert result.decision == "EXECUTABLE"
    assert not result.blocking_constraints


# ─────────────────────────────────────────────────────────────────────────────
# Scenario 2 — QUANTITY GAP (the primary demo: 80 kg vs 300 kg required)
# ─────────────────────────────────────────────────────────────────────────────

def test_quantity_gap_not_viable_with_quality_block():
    """Gulf buyer: 300 kg, Grade A, 7-day payment vs 80 kg Grade B, 2-day limit."""
    farmer = _lot()
    buyer = _buyer()
    result = evaluate_opportunity(farmer, buyer)
    # Quality is unrecoverable → NOT_VIABLE despite quantity also failing
    assert result.decision == "NOT_VIABLE"
    assert ConstraintType.QUANTITY in result.blocking_constraints
    assert ConstraintType.QUALITY in result.blocking_constraints
    assert ConstraintType.PAYMENT in result.blocking_constraints

    # Gaps must be quantified
    qty_gap = next(g for g in result.opportunity_gaps if g.constraint_type == ConstraintType.QUANTITY)
    assert qty_gap.gap == pytest.approx(2.2, abs=0.01)
    assert qty_gap.gap_unit == "quintals"

    pay_gap = next(g for g in result.opportunity_gaps if g.constraint_type == ConstraintType.PAYMENT)
    assert pay_gap.gap == 5  # 7 - 2 days


def test_quantity_gap_recoverable_when_quality_matches():
    """Quantity gap only (Grade B buyer). Should be RECOVERABLE via aggregation."""
    farmer = _lot(quantity=Decimal("0.8"), grade="Grade B")
    buyer = _buyer(
        min_qty=Decimal("3.0"),
        grade="Grade B",      # Quality now matches
        payment_days=2,       # Payment now matches
        transport_cost=Decimal("400"),
    )
    result = evaluate_opportunity(farmer, buyer)
    assert result.decision == "RECOVERABLE"
    assert ConstraintType.QUANTITY in result.blocking_constraints
    assert ConstraintType.QUALITY not in result.blocking_constraints

    # Must propose aggregation
    agg = next(
        (m for m in result.minimum_viable_changes if m.change_type == "AGGREGATION"),
        None,
    )
    assert agg is not None
    assert agg.feasible is True
    assert agg.parameters["additional_quantity_kg"] == pytest.approx(220.0, abs=1.0)


# ─────────────────────────────────────────────────────────────────────────────
# Scenario 3 — PAYMENT MISMATCH only
# ─────────────────────────────────────────────────────────────────────────────

def test_payment_mismatch_recoverable():
    """Grade B ok, qty ok, but buyer pays in 7 days vs farmer 2-day limit."""
    farmer = _lot(quantity=Decimal("0.8"), grade="Grade B")
    buyer = _buyer(
        min_qty=Decimal("0.5"),
        grade="Grade B",
        payment_days=7,
        pickup=True,
        transport_cost=Decimal("0"),
    )
    result = evaluate_opportunity(farmer, buyer)
    assert result.decision == "RECOVERABLE"
    assert ConstraintType.PAYMENT in result.blocking_constraints
    assert ConstraintType.QUANTITY not in result.blocking_constraints
    assert ConstraintType.QUALITY not in result.blocking_constraints

    neg = next(
        (m for m in result.minimum_viable_changes if m.change_type == "NEGOTIATE_PAYMENT"),
        None,
    )
    assert neg is not None
    assert neg.parameters["reduction_needed"] == 5
    assert neg.parameters["target_payment_days"] == 2


# ─────────────────────────────────────────────────────────────────────────────
# Scenario 4 — TRANSPORT FAILURE (high transport destroys net realization)
# ─────────────────────────────────────────────────────────────────────────────

def test_transport_failure():
    """Distant buyer: Grade B ok, qty ok, payment ok, but ₹5000 transport wrecks net."""
    farmer = _lot(
        quantity=Decimal("0.8"),
        grade="Grade B",
        min_price=Decimal("2800"),
        max_payment_days=2,
        max_transport_budget=Decimal("1000"),   # Budget: ₹1,000
    )
    buyer = _buyer(
        min_qty=Decimal("0.5"),
        grade="Grade B",
        payment_days=1,
        pickup=False,
        transport_cost=Decimal("5000"),         # Cost: ₹5,000
    )
    result = evaluate_opportunity(farmer, buyer)
    assert result.decision in ("NOT_VIABLE", "RECOVERABLE")
    assert ConstraintType.TRANSPORT in result.blocking_constraints

    transport_gap = next(
        g for g in result.opportunity_gaps if g.constraint_type == ConstraintType.TRANSPORT
    )
    assert float(transport_gap.available) > float(transport_gap.required)


# ─────────────────────────────────────────────────────────────────────────────
# Scenario 5 — QUALITY MISMATCH (hard block — not recoverable)
# ─────────────────────────────────────────────────────────────────────────────

def test_quality_mismatch_not_viable():
    """Grade A required, farmer has Grade B — hard constraint, not recoverable."""
    farmer = _lot(grade="Grade B", quantity=Decimal("5.0"))
    buyer = _buyer(
        min_qty=Decimal("0.5"),
        grade="Grade A",
        payment_days=0,
        pickup=True,
        transport_cost=Decimal("0"),
    )
    result = evaluate_opportunity(farmer, buyer)
    assert result.decision == "NOT_VIABLE"
    assert ConstraintType.QUALITY in result.blocking_constraints

    quality_gap = next(g for g in result.opportunity_gaps if g.constraint_type == ConstraintType.QUALITY)
    assert quality_gap.required == "Grade A"
    assert quality_gap.available == "Grade B"

    # Quality MVC must be marked NOT feasible
    quality_mvc = next(m for m in result.minimum_viable_changes if m.change_type == "QUALITY_UPGRADE")
    assert quality_mvc.feasible is False


# ─────────────────────────────────────────────────────────────────────────────
# Scenario 6 — DEADLINE FAILURE (lot expired)
# ─────────────────────────────────────────────────────────────────────────────

def test_deadline_expired_lot():
    """Lot sell_by is yesterday — cannot be used."""
    farmer = _lot(sell_by=YESTERDAY, available_from=YESTERDAY - timedelta(days=1))
    buyer = _buyer(min_qty=Decimal("0.5"), grade="Grade B", payment_days=0, pickup=True, transport_cost=Decimal("0"))
    result = evaluate_opportunity(farmer, buyer, today=TODAY)
    assert result.decision == "NOT_VIABLE"
    assert ConstraintType.DEADLINE in result.blocking_constraints


def test_deadline_expired_opportunity():
    """Buyer opportunity expired yesterday."""
    farmer = _lot()
    buyer = _buyer(active_until=YESTERDAY)
    result = evaluate_opportunity(farmer, buyer, today=TODAY)
    assert result.decision in ("NOT_VIABLE", "INSUFFICIENT_DATA")
    timing_or_deadline = {ConstraintType.TIMING, ConstraintType.DEADLINE}
    assert bool(timing_or_deadline & set(result.blocking_constraints))


# ─────────────────────────────────────────────────────────────────────────────
# Scenario 7 — MULTIPLE SIMULTANEOUS CONSTRAINTS
# ─────────────────────────────────────────────────────────────────────────────

def test_multiple_constraints_all_reported():
    """Quantity, quality, and payment all fail. All three must appear in result."""
    farmer = _lot(quantity=Decimal("0.8"), grade="Grade B", max_payment_days=2)
    buyer = _buyer()   # 300 kg, Grade A, 7-day — fails on all three
    result = evaluate_opportunity(farmer, buyer)
    assert ConstraintType.QUANTITY in result.blocking_constraints
    assert ConstraintType.QUALITY in result.blocking_constraints
    assert ConstraintType.PAYMENT in result.blocking_constraints
    assert len(result.opportunity_gaps) >= 3


# ─────────────────────────────────────────────────────────────────────────────
# Scenario 8 — RECOVERABLE with aggregation overlay
# ─────────────────────────────────────────────────────────────────────────────

def test_recovery_via_aggregation_overlay():
    """Apply aggregation overlay (extra 2.2 quintals). Quantity no longer blocks."""
    farmer = _lot(grade="Grade B", quantity=Decimal("0.8"))
    buyer = _buyer(
        min_qty=Decimal("3.0"),
        grade="Grade B",
        payment_days=2,   # payment already matches
        transport_cost=Decimal("400"),
    )
    # Without overlay: RECOVERABLE (quantity blocks)
    r1 = evaluate_opportunity(farmer, buyer)
    assert r1.decision == "RECOVERABLE"
    assert ConstraintType.QUANTITY in r1.blocking_constraints

    # With overlay: extra 2.2 quintals → total 3.0 → quantity constraint cleared
    overlay = RecoveryOverlay(extra_quantity=Decimal("2.2"))
    r2 = evaluate_opportunity(farmer, buyer, overlay=overlay)
    assert r2.decision == "EXECUTABLE"
    assert ConstraintType.QUANTITY not in r2.blocking_constraints


# ─────────────────────────────────────────────────────────────────────────────
# Scenario 9 — RECOVERY via payment negotiation
# ─────────────────────────────────────────────────────────────────────────────

def test_recovery_via_payment_negotiation_overlay():
    """After negotiating payment to 2 days, payment constraint clears."""
    farmer = _lot(grade="Grade B", quantity=Decimal("0.8"))
    buyer = _buyer(
        min_qty=Decimal("0.5"),
        grade="Grade B",
        payment_days=7,
        pickup=True,
        transport_cost=Decimal("0"),
    )
    r1 = evaluate_opportunity(farmer, buyer)
    assert r1.decision == "RECOVERABLE"
    assert ConstraintType.PAYMENT in r1.blocking_constraints

    overlay = RecoveryOverlay(negotiated_payment_days=2)
    r2 = evaluate_opportunity(farmer, buyer, overlay=overlay)
    assert r2.decision == "EXECUTABLE"
    assert ConstraintType.PAYMENT not in r2.blocking_constraints


# ─────────────────────────────────────────────────────────────────────────────
# Scenario 10 — INSUFFICIENT_DATA (missing offered price)
# ─────────────────────────────────────────────────────────────────────────────

def test_insufficient_data_missing_price():
    """Buyer requirement has offered_price = 0 → cannot decide."""
    farmer = _lot()
    buyer = _buyer(price=Decimal("0"))
    result = evaluate_opportunity(farmer, buyer)
    assert result.decision == "INSUFFICIENT_DATA"
    assert ConstraintType.MISSING_DATA in result.blocking_constraints


# ─────────────────────────────────────────────────────────────────────────────
# Scenario 11 — PRICE FLOOR violation
# ─────────────────────────────────────────────────────────────────────────────

def test_price_below_minimum_recoverable():
    """Buyer offers ₹2500/quintal but farmer minimum is ₹2800. RECOVERABLE via negotiation."""
    farmer = _lot(
        quantity=Decimal("0.8"),
        grade="Grade B",
        min_price=Decimal("2800"),
        max_payment_days=7,
    )
    buyer = _buyer(
        min_qty=Decimal("0.5"),
        grade="Grade B",
        price=Decimal("2500"),  # Below farmer floor
        payment_days=2,
        pickup=True,
        transport_cost=Decimal("0"),
    )
    result = evaluate_opportunity(farmer, buyer)
    assert result.decision == "RECOVERABLE"
    assert ConstraintType.PRICE in result.blocking_constraints

    price_gap = next(g for g in result.opportunity_gaps if g.constraint_type == ConstraintType.PRICE)
    assert float(price_gap.gap) == pytest.approx(300.0, abs=1.0)  # ₹2800 - ₹2500


# ─────────────────────────────────────────────────────────────────────────────
# Scenario 12 — BUYER PICKUP clears transport cost
# ─────────────────────────────────────────────────────────────────────────────

def test_buyer_pickup_overlay_clears_transport():
    """Transport blocks with ₹5000 cost. Buyer pickup overlay clears it."""
    farmer = _lot(
        quantity=Decimal("0.8"),
        grade="Grade B",
        max_payment_days=2,
        max_transport_budget=Decimal("1000"),
    )
    buyer = _buyer(
        min_qty=Decimal("0.5"),
        grade="Grade B",
        payment_days=1,
        pickup=False,
        transport_cost=Decimal("5000"),
    )
    r1 = evaluate_opportunity(farmer, buyer)
    assert ConstraintType.TRANSPORT in r1.blocking_constraints

    overlay = RecoveryOverlay(assume_buyer_pickup=True)
    r2 = evaluate_opportunity(farmer, buyer, overlay=overlay)
    assert r2.decision == "EXECUTABLE"
    assert ConstraintType.TRANSPORT not in r2.blocking_constraints
    assert r2.economics.transport == Decimal("0")


# ─────────────────────────────────────────────────────────────────────────────
# Economics correctness
# ─────────────────────────────────────────────────────────────────────────────

def test_economics_calculation():
    """Verify gross, transport, and net are calculated correctly."""
    farmer = _lot(quantity=Decimal("1.0"), grade="Grade B", min_price=None)
    buyer = _buyer(
        min_qty=Decimal("0.5"),
        grade="Grade B",
        price=Decimal("3000"),   # ₹3000/quintal × 1 quintal = ₹3000 gross
        payment_days=0,
        pickup=False,
        transport_cost=Decimal("500"),
    )
    result = evaluate_opportunity(farmer, buyer)
    econ = result.economics
    assert econ is not None
    assert econ.sale_value == Decimal("3000.00")
    assert econ.transport == Decimal("500.00")
    assert econ.estimated_net == Decimal("2500.00")
    assert econ.estimated_net_per_quintal == Decimal("2500.00")


def test_economics_labels_present():
    """Every economics field must carry a provenance label."""
    farmer = _lot(quantity=Decimal("1.0"), grade="Grade B")
    buyer = _buyer(min_qty=Decimal("0.5"), grade="Grade B", payment_days=0, pickup=True, transport_cost=Decimal("0"))
    result = evaluate_opportunity(farmer, buyer)
    assert result.economics is not None
    assert "transport" in result.economics.labels
    assert "net" in result.economics.labels


# ─────────────────────────────────────────────────────────────────────────────
# Ranking: lower-price executable beats higher-price not-viable
# ─────────────────────────────────────────────────────────────────────────────

def test_engine_does_not_favor_higher_price_when_infeasible():
    """
    Verify the engine is deterministic and doesn't magically prefer price.
    Gulf buyer (₹34/kg) returns NOT_VIABLE.
    Farm-gate (₹30/kg) returns EXECUTABLE.
    EXECUTABLE must rank higher.
    """
    farmer = _lot(quantity=Decimal("0.8"), grade="Grade B", max_payment_days=2)

    gulf = _buyer()  # ₹3400, Grade A, 300 kg, 7-day — multiple blocks
    gate = _buyer(
        min_qty=Decimal("0.5"),
        grade="Grade B",
        price=Decimal("3000"),
        payment_days=0,
        pickup=True,
        transport_cost=Decimal("0"),
    )
    gulf_result = evaluate_opportunity(farmer, gulf)
    gate_result = evaluate_opportunity(farmer, gate)

    assert gulf_result.decision == "NOT_VIABLE"
    assert gate_result.decision == "EXECUTABLE"
    # Engine correctly tells them apart — KrishiX does not blindly pick highest price


def test_dynamic_param_change_changes_result():
    """
    Core acceptance test principle: changing parameters changes the result
    without changing code.
    """
    farmer = _lot(quantity=Decimal("0.8"), grade="Grade B", max_payment_days=2)
    buyer = _buyer()   # 300 kg, Grade A, 7-day

    r1 = evaluate_opportunity(farmer, buyer)
    assert r1.decision == "NOT_VIABLE"

    # Step 1: Add quantity via overlay
    r2 = evaluate_opportunity(farmer, buyer, overlay=RecoveryOverlay(extra_quantity=Decimal("2.2")))
    # Grade A still blocks
    assert ConstraintType.QUALITY in r2.blocking_constraints

    # Step 2: Also fix payment
    r3 = evaluate_opportunity(
        farmer, buyer,
        overlay=RecoveryOverlay(extra_quantity=Decimal("2.2"), negotiated_payment_days=2),
    )
    # Quality still blocks → NOT_VIABLE (quality is hard)
    assert r3.decision == "NOT_VIABLE"
    assert ConstraintType.QUALITY in r3.blocking_constraints

    # Step 3: Switch to Grade B buyer — now should be EXECUTABLE
    grade_b_buyer = _buyer(
        min_qty=Decimal("3.0"),
        grade="Grade B",
        payment_days=2,
        pickup=False,
        transport_cost=Decimal("400"),
    )
    r4 = evaluate_opportunity(
        farmer, grade_b_buyer,
        overlay=RecoveryOverlay(extra_quantity=Decimal("2.2")),
    )
    assert r4.decision == "EXECUTABLE"
