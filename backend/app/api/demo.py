"""
Demo Lab API

GET  /api/demo/scenarios           — list all 13 demo scenarios
POST /api/demo/scenarios/{id}/run  — run scenario through real feasibility engine
POST /api/demo/seed                — seed demo data (bootstrap)

CRITICAL: every scenario runs through the SAME production feasibility engine.
No results are hard-coded. Changing parameters changes the result.
"""
import json
from datetime import date, timedelta
from decimal import Decimal
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.schemas import TokenData
from app.services.demo_seed import seed_demo
from app.services.feasibility_engine import (
    BuyerRequirementData,
    FarmerLotData,
    RecoveryOverlay,
    evaluate_opportunity,
)

router = APIRouter()

# ── Scenario catalogue ────────────────────────────────────────────────────────

SCENARIOS = [
    {
        "id": "executable",
        "name": "1. Executable — farm-gate buyer",
        "description": "80 kg Grade B tomato sold to local farm-gate trader. All constraints satisfied.",
        "demonstrates": "EXECUTABLE decision state. Buyer pickup, immediate cash, Grade B accepted.",
        "default_parameters": {
            "quantity_kg": 80, "grade": "Grade B", "min_price_per_kg": 28,
            "max_payment_days": 2,
            "buyer_min_qty_kg": 50, "buyer_grade": "Grade B",
            "buyer_price_per_kg": 30, "buyer_payment_days": 0, "buyer_pickup": True,
            "transport_cost": 0,
        },
    },
    {
        "id": "quantity_gap",
        "name": "2. Quantity gap — primary demo scenario",
        "description": "80 kg vs 300 kg minimum. The ₹34/kg buyer is NOT viable despite highest price.",
        "demonstrates": "NOT_VIABLE: QUANTITY + QUALITY + PAYMENT all block the highest-priced option.",
        "default_parameters": {
            "quantity_kg": 80, "grade": "Grade B", "min_price_per_kg": 28,
            "max_payment_days": 2,
            "buyer_min_qty_kg": 300, "buyer_grade": "Grade A",
            "buyer_price_per_kg": 34, "buyer_payment_days": 7, "buyer_pickup": False,
            "transport_cost": 1500,
        },
    },
    {
        "id": "quality_mismatch",
        "name": "3. Quality mismatch — hard constraint",
        "description": "Buyer requires Grade A, farmer has Grade B. Cannot be recovered by aggregation.",
        "demonstrates": "NOT_VIABLE: QUALITY is a hard constraint. Minimum viable change shows it is infeasible.",
        "default_parameters": {
            "quantity_kg": 300, "grade": "Grade B", "min_price_per_kg": 28,
            "max_payment_days": 7,
            "buyer_min_qty_kg": 50, "buyer_grade": "Grade A",
            "buyer_price_per_kg": 33, "buyer_payment_days": 1, "buyer_pickup": True,
            "transport_cost": 0,
        },
    },
    {
        "id": "payment_mismatch",
        "name": "4. Payment mismatch — recoverable",
        "description": "Buyer pays in 7 days, farmer needs ≤2 days. Grade B ok, quantity ok.",
        "demonstrates": "RECOVERABLE: PAYMENT blocks. Minimum viable change = negotiate to 2 days.",
        "default_parameters": {
            "quantity_kg": 80, "grade": "Grade B", "min_price_per_kg": 28,
            "max_payment_days": 2,
            "buyer_min_qty_kg": 50, "buyer_grade": "Grade B",
            "buyer_price_per_kg": 31, "buyer_payment_days": 7, "buyer_pickup": True,
            "transport_cost": 0,
        },
    },
    {
        "id": "transport_failure",
        "name": "5. Transport constraint — high cost kills net realization",
        "description": "High advertised price but ₹5,000 transport cost makes net realization negative.",
        "demonstrates": "RECOVERABLE/NOT_VIABLE: TRANSPORT blocks. Shows price ≠ realization.",
        "default_parameters": {
            "quantity_kg": 80, "grade": "Grade B", "min_price_per_kg": 28,
            "max_payment_days": 2, "max_transport_budget": 1000,
            "buyer_min_qty_kg": 50, "buyer_grade": "Grade B",
            "buyer_price_per_kg": 36, "buyer_payment_days": 1, "buyer_pickup": False,
            "transport_cost": 5000,
        },
    },
    {
        "id": "deadline_expired",
        "name": "6. Deadline — opportunity expired",
        "description": "Buyer requirement expired yesterday. Lot cannot be matched regardless of other factors.",
        "demonstrates": "NOT_VIABLE: TIMING/DEADLINE is a hard constraint.",
        "default_parameters": {
            "quantity_kg": 80, "grade": "Grade B", "min_price_per_kg": 28,
            "max_payment_days": 2,
            "buyer_min_qty_kg": 50, "buyer_grade": "Grade B",
            "buyer_price_per_kg": 31, "buyer_payment_days": 1, "buyer_pickup": True,
            "transport_cost": 0,
            "buyer_active_until_offset_days": -1,  # expired yesterday
        },
    },
    {
        "id": "multiple_constraints",
        "name": "7. Multiple simultaneous constraints",
        "description": "Quantity, quality, AND payment all fail at once. All three blockers shown.",
        "demonstrates": "NOT_VIABLE: engine identifies all blocking constraints simultaneously.",
        "default_parameters": {
            "quantity_kg": 80, "grade": "Grade B", "min_price_per_kg": 28,
            "max_payment_days": 2,
            "buyer_min_qty_kg": 300, "buyer_grade": "Grade A",
            "buyer_price_per_kg": 34, "buyer_payment_days": 7, "buyer_pickup": False,
            "transport_cost": 1500,
        },
    },
    {
        "id": "aggregation_recovery",
        "name": "8. Aggregation recovery — quantity gap closed",
        "description": "80 kg alone fails. After aggregating 3 farmers (80+120+100=300 kg), EXECUTABLE.",
        "demonstrates": "RECOVERABLE → EXECUTABLE: applying AGGREGATION overlay changes result.",
        "default_parameters": {
            "quantity_kg": 80, "grade": "Grade B", "min_price_per_kg": 28,
            "max_payment_days": 2,
            "buyer_min_qty_kg": 300, "buyer_grade": "Grade B",
            "buyer_price_per_kg": 32, "buyer_payment_days": 2, "buyer_pickup": False,
            "transport_cost": 400,
            "apply_aggregation_kg": 220,  # extra quantity from other farmers
        },
    },
    {
        "id": "payment_negotiation_recovery",
        "name": "9. Payment negotiation recovery",
        "description": "Payment mismatch recovered by negotiating buyer payment down to 2 days.",
        "demonstrates": "RECOVERABLE → EXECUTABLE: applying NEGOTIATE_PAYMENT overlay changes result.",
        "default_parameters": {
            "quantity_kg": 80, "grade": "Grade B", "min_price_per_kg": 28,
            "max_payment_days": 2,
            "buyer_min_qty_kg": 50, "buyer_grade": "Grade B",
            "buyer_price_per_kg": 31, "buyer_payment_days": 7, "buyer_pickup": True,
            "transport_cost": 0,
            "apply_negotiated_payment_days": 2,
        },
    },
    {
        "id": "whatif_quantity",
        "name": "10. What-if: increase quantity → EXECUTABLE",
        "description": "Shows same buyer with 80 kg (NOT_VIABLE) then rechecked with 300 kg (EXECUTABLE).",
        "demonstrates": "Dynamic parameter change changes engine result without code change.",
        "default_parameters": {
            "quantity_kg": 80, "grade": "Grade B", "min_price_per_kg": 28,
            "max_payment_days": 2,
            "buyer_min_qty_kg": 300, "buyer_grade": "Grade B",
            "buyer_price_per_kg": 32, "buyer_payment_days": 2, "buyer_pickup": False,
            "transport_cost": 400,
            "whatif_quantity_kg": 300,
        },
    },
    {
        "id": "price_floor",
        "name": "11. Price floor violation — recoverable via negotiation",
        "description": "Buyer offers ₹25/kg, farmer minimum is ₹28/kg. Price blocks, but is negotiable.",
        "demonstrates": "RECOVERABLE: PRICE constraint. Minimum viable change = negotiate to ₹28/kg.",
        "default_parameters": {
            "quantity_kg": 80, "grade": "Grade B", "min_price_per_kg": 28,
            "max_payment_days": 2,
            "buyer_min_qty_kg": 50, "buyer_grade": "Grade B",
            "buyer_price_per_kg": 25, "buyer_payment_days": 0, "buyer_pickup": True,
            "transport_cost": 0,
        },
    },
    {
        "id": "insufficient_data",
        "name": "12. Insufficient data — cannot decide",
        "description": "Buyer has no offered price. Engine returns INSUFFICIENT_DATA, not a guess.",
        "demonstrates": "INSUFFICIENT_DATA: engine refuses to fabricate a recommendation.",
        "default_parameters": {
            "quantity_kg": 80, "grade": "Grade B", "min_price_per_kg": 28,
            "max_payment_days": 2,
            "buyer_min_qty_kg": 50, "buyer_grade": "Grade B",
            "buyer_price_per_kg": 0,  # missing price → INSUFFICIENT_DATA
            "buyer_payment_days": 0, "buyer_pickup": True, "transport_cost": 0,
        },
    },
    {
        "id": "opportunity_gap_demo",
        "name": "13. Opportunity gap — highest quoted ≠ best executable",
        "description": "₹34/kg buyer exists but not executable. ₹30/kg farm-gate is best executable. Gap = ₹4/kg.",
        "demonstrates": "Opportunity gap: KrishiX explains why the attractive option fails and what is actually achievable.",
        "default_parameters": {
            "quantity_kg": 80, "grade": "Grade B", "min_price_per_kg": 28,
            "max_payment_days": 2,
            "buyer_min_qty_kg": 50, "buyer_grade": "Grade B",
            "buyer_price_per_kg": 30, "buyer_payment_days": 0, "buyer_pickup": True,
            "transport_cost": 0,
            # Also evaluates the high-price NOT_VIABLE buyer for contrast
            "contrast_buyer_price_per_kg": 34,
            "contrast_buyer_min_qty_kg": 300,
            "contrast_buyer_grade": "Grade A",
            "contrast_buyer_payment_days": 7,
        },
    },
]

SCENARIO_INDEX = {s["id"]: s for s in SCENARIOS}


# ── Request / response helpers ────────────────────────────────────────────────

class ScenarioRunRequest(BaseModel):
    quantity_kg: Optional[float] = None
    grade: Optional[str] = None
    min_price_per_kg: Optional[float] = None
    max_payment_days: Optional[int] = None
    max_transport_budget: Optional[float] = None
    buyer_min_qty_kg: Optional[float] = None
    buyer_grade: Optional[str] = None
    buyer_price_per_kg: Optional[float] = None
    buyer_payment_days: Optional[int] = None
    buyer_pickup: Optional[bool] = None
    transport_cost: Optional[float] = None
    apply_aggregation_kg: Optional[float] = None
    apply_negotiated_payment_days: Optional[int] = None
    apply_buyer_pickup: Optional[bool] = None
    whatif_quantity_kg: Optional[float] = None
    buyer_active_until_offset_days: Optional[int] = None


def _build_lot(p: dict) -> FarmerLotData:
    qty_q = Decimal(str(p["quantity_kg"])) / 100
    today = date.today()
    active_offset = p.get("buyer_active_until_offset_days", 14)
    return FarmerLotData(
        quantity=qty_q,
        quality_grade=p.get("grade", "Grade B"),
        minimum_price=Decimal(str(p["min_price_per_kg"])) * 100 if p.get("min_price_per_kg") else None,
        max_payment_days=int(p.get("max_payment_days", 2)),
        sell_by=today,
        available_from=today,
        max_transport_budget=Decimal(str(p["max_transport_budget"])) if p.get("max_transport_budget") else None,
        location_state="Andhra Pradesh",
        location_district="Madanapalle",
        latitude=Decimal("13.5504"),
        longitude=Decimal("78.5024"),
    )


def _build_buyer(p: dict) -> BuyerRequirementData:
    today = date.today()
    active_offset = int(p.get("buyer_active_until_offset_days", 14))
    active_until = today + timedelta(days=active_offset)
    return BuyerRequirementData(
        minimum_quantity=Decimal(str(p["buyer_min_qty_kg"])) / 100,
        maximum_quantity=None,
        required_grade=p.get("buyer_grade", "Grade B"),
        offered_price=Decimal(str(p.get("buyer_price_per_kg", 0))) * 100,
        payment_days=int(p.get("buyer_payment_days", 0)),
        pickup_available=bool(p.get("buyer_pickup", False)),
        pickup_location_state="Andhra Pradesh",
        pickup_location_district="Madanapalle",
        buyer_latitude=None,
        buyer_longitude=None,
        active_until=active_until,
        transport_cost_total=Decimal(str(p.get("transport_cost", 0))),
        transport_cost_source="configured_demo",
    )


def _result_to_dict(result) -> dict:
    econ = None
    if result.economics:
        e = result.economics
        econ = {
            "sale_value": float(e.sale_value),
            "transport": float(e.transport),
            "transport_source": e.transport_source,
            "market_charges": float(e.market_charges),
            "estimated_net": float(e.estimated_net),
            "estimated_net_per_quintal": float(e.estimated_net_per_quintal),
            "estimated_net_per_kg": round(float(e.estimated_net_per_quintal) / 100, 2),
            "labels": e.labels,
        }
    return {
        "decision": result.decision,
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
    }


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/scenarios")
def list_scenarios():
    """List all demo scenarios with their default parameters."""
    return {
        "total": len(SCENARIOS),
        "scenarios": [
            {
                "id": s["id"],
                "name": s["name"],
                "description": s["description"],
                "demonstrates": s["demonstrates"],
                "default_parameters": s["default_parameters"],
            }
            for s in SCENARIOS
        ],
        "note": (
            "All scenarios run through the production feasibility engine. "
            "Results are NOT hard-coded. Changing parameters changes the result."
        ),
    }


@router.post("/scenarios/{scenario_id}/run")
def run_scenario(
    scenario_id: str,
    body: Optional[ScenarioRunRequest] = None,
):
    """
    Run a demo scenario through the real feasibility engine.

    Parameters in the request body override the scenario defaults.
    This proves the engine is deterministic and parameter-driven.
    """
    scenario = SCENARIO_INDEX.get(scenario_id)
    if not scenario:
        raise HTTPException(
            status_code=404,
            detail=f"Scenario '{scenario_id}' not found. Valid IDs: {list(SCENARIO_INDEX.keys())}",
        )

    # Merge defaults with overrides
    params = dict(scenario["default_parameters"])
    if body:
        overrides = body.model_dump(exclude_unset=True, exclude_none=True)
        params.update(overrides)

    farmer = _build_lot(params)
    buyer = _build_buyer(params)

    # ── Base evaluation (no overlay) ─────────────────────────────────────────
    base_result = evaluate_opportunity(farmer, buyer)
    base = _result_to_dict(base_result)

    # ── Recovery overlay if parameters specify ────────────────────────────────
    overlay_applied = {}
    recovery_result_dict = None

    if params.get("apply_aggregation_kg") or params.get("apply_negotiated_payment_days") is not None or params.get("apply_buyer_pickup"):
        overlay = RecoveryOverlay(
            extra_quantity=(
                Decimal(str(params["apply_aggregation_kg"])) / 100
                if params.get("apply_aggregation_kg") else Decimal("0")
            ),
            negotiated_payment_days=params.get("apply_negotiated_payment_days"),
            assume_buyer_pickup=bool(params.get("apply_buyer_pickup", False)),
        )
        overlay_applied = {
            "aggregation_kg": params.get("apply_aggregation_kg"),
            "negotiated_payment_days": params.get("apply_negotiated_payment_days"),
            "assume_buyer_pickup": params.get("apply_buyer_pickup", False),
        }
        recovery_result = evaluate_opportunity(farmer, buyer, overlay=overlay)
        recovery_result_dict = _result_to_dict(recovery_result)

    # ── What-if evaluation if specified ──────────────────────────────────────
    whatif_result_dict = None
    if params.get("whatif_quantity_kg"):
        whatif_qty = Decimal(str(params["whatif_quantity_kg"])) / 100
        extra = whatif_qty - farmer.quantity
        whatif_overlay = RecoveryOverlay(extra_quantity=max(extra, Decimal("0")))
        whatif_result = evaluate_opportunity(farmer, buyer, overlay=whatif_overlay)
        whatif_result_dict = {
            **_result_to_dict(whatif_result),
            "whatif_quantity_kg": params["whatif_quantity_kg"],
            "whatif_quantity_quintals": float(whatif_qty),
        }

    # ── Contrast buyer for opportunity gap demo ──────────────────────────────
    contrast_result_dict = None
    if params.get("contrast_buyer_price_per_kg"):
        contrast_params = dict(params)
        contrast_params["buyer_price_per_kg"] = params["contrast_buyer_price_per_kg"]
        contrast_params["buyer_min_qty_kg"] = params.get("contrast_buyer_min_qty_kg", params["buyer_min_qty_kg"])
        contrast_params["buyer_grade"] = params.get("contrast_buyer_grade", params.get("buyer_grade", "Grade B"))
        contrast_params["buyer_payment_days"] = params.get("contrast_buyer_payment_days", params.get("buyer_payment_days", 0))
        contrast_buyer = _build_buyer(contrast_params)
        contrast_result = evaluate_opportunity(farmer, contrast_buyer)
        contrast_result_dict = {
            **_result_to_dict(contrast_result),
            "contrast_price_per_kg": params["contrast_buyer_price_per_kg"],
        }

    # ── Opportunity gap ───────────────────────────────────────────────────────
    opportunity_gap = None
    base_price = params.get("buyer_price_per_kg", 0)
    contrast_price = params.get("contrast_buyer_price_per_kg")
    if base_result.decision == "EXECUTABLE" and contrast_price and contrast_result_dict:
        if contrast_result_dict["decision"] != "EXECUTABLE" and contrast_price > base_price:
            opportunity_gap = {
                "highest_quoted_per_kg": contrast_price,
                "best_executable_per_kg": base_price,
                "gap_per_kg": round(contrast_price - base_price, 2),
                "label": "Opportunity gap — not guaranteed lost income.",
            }

    return {
        "scenario_id": scenario_id,
        "scenario_name": scenario["name"],
        "demonstrates": scenario["demonstrates"],
        "parameters_used": params,
        "farmer_lot": {
            "quantity_kg": float(farmer.quantity) * 100,
            "quantity_quintals": float(farmer.quantity),
            "grade": farmer.quality_grade,
            "min_price_per_kg": float(farmer.minimum_price) / 100 if farmer.minimum_price else None,
            "max_payment_days": farmer.max_payment_days,
            "sell_by": str(farmer.sell_by),
            "location": f"{farmer.location_district}, {farmer.location_state}",
        },
        "buyer": {
            "min_quantity_kg": float(buyer.minimum_quantity) * 100,
            "required_grade": buyer.required_grade,
            "offered_price_per_kg": float(buyer.offered_price) / 100,
            "payment_days": buyer.payment_days,
            "pickup_available": buyer.pickup_available,
            "transport_cost": float(buyer.transport_cost_total) if buyer.transport_cost_total else 0,
            "source": "configured_demo",
        },
        "base_result": base,
        "after_recovery": recovery_result_dict,
        "overlay_applied": overlay_applied if overlay_applied else None,
        "whatif_result": whatif_result_dict,
        "contrast_buyer_result": contrast_result_dict,
        "opportunity_gap": opportunity_gap,
        "engine_note": (
            "Result produced by the deterministic feasibility engine — not hard-coded. "
            "Changing parameters in the request body will change the result."
        ),
    }


@router.post("/seed")
def run_seed(
    token_data: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Seed demo data (tomato scenario + 7 buyers). Idempotent — safe to run multiple times."""
    try:
        return seed_demo(db)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
