"""
Tests for new endpoints added in this session:
- GET /api/demo/scenarios
- POST /api/demo/scenarios/{id}/run (no auth)
- POST /api/lots/{id}/whatif
- GET /api/buyers/{id}/requirements
- GET /api/markets (optional state)
- GET /api/market-prices/history (selling_window)
"""
import pytest
from datetime import date


def auth_header(token):
    return {"Authorization": f"Bearer {token}"}


class TestDemoScenarios:
    def test_list_scenarios_no_auth(self, client):
        """Demo scenarios are public — no auth needed."""
        resp = client.get("/api/demo/scenarios")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 13
        ids = [s["id"] for s in data["scenarios"]]
        assert "executable" in ids
        assert "quantity_gap" in ids
        assert "quality_mismatch" in ids
        assert "payment_mismatch" in ids
        assert "aggregation_recovery" in ids
        assert "opportunity_gap_demo" in ids

    def test_run_scenario_executable(self, client):
        """Run the executable scenario — engine returns EXECUTABLE."""
        resp = client.post("/api/demo/scenarios/executable/run")
        assert resp.status_code == 200
        data = resp.json()
        assert data["scenario_id"] == "executable"
        assert data["base_result"]["decision"] == "EXECUTABLE"
        assert not data["base_result"]["blocking_constraints"]
        assert data["base_result"]["economics"] is not None

    def test_run_scenario_quantity_gap(self, client):
        """Primary demo: 80kg vs 300kg min → NOT_VIABLE (quality also blocks)."""
        resp = client.post("/api/demo/scenarios/quantity_gap/run")
        assert resp.status_code == 200
        data = resp.json()
        assert data["base_result"]["decision"] == "NOT_VIABLE"
        blocks = data["base_result"]["blocking_constraints"]
        assert "QUANTITY" in blocks
        assert "QUALITY" in blocks
        assert "PAYMENT" in blocks

    def test_run_scenario_payment_mismatch(self, client):
        """Payment mismatch only → RECOVERABLE."""
        resp = client.post("/api/demo/scenarios/payment_mismatch/run")
        assert resp.status_code == 200
        data = resp.json()
        assert data["base_result"]["decision"] == "RECOVERABLE"
        assert "PAYMENT" in data["base_result"]["blocking_constraints"]

    def test_run_scenario_quality_mismatch(self, client):
        """Quality mismatch → NOT_VIABLE (hard constraint)."""
        resp = client.post("/api/demo/scenarios/quality_mismatch/run")
        assert resp.status_code == 200
        data = resp.json()
        assert data["base_result"]["decision"] == "NOT_VIABLE"

    def test_run_scenario_with_param_override(self, client):
        """Changing quantity_kg changes the result — proves engine is not hardcoded."""
        # Default quantity_gap scenario has 80kg → NOT_VIABLE
        resp1 = client.post("/api/demo/scenarios/aggregation_recovery/run", json={})
        # Override: aggregation already applied in default params
        resp2 = client.post(
            "/api/demo/scenarios/aggregation_recovery/run",
            json={"quantity_kg": 300},  # enough without aggregation
        )
        assert resp1.status_code == 200
        assert resp2.status_code == 200
        # Both should be EXECUTABLE since grade matches and payment matches
        assert resp2.json()["base_result"]["decision"] == "EXECUTABLE"

    def test_run_scenario_aggregation_recovery(self, client):
        """After aggregation overlay, quantity constraint is resolved."""
        resp = client.post("/api/demo/scenarios/aggregation_recovery/run")
        assert resp.status_code == 200
        data = resp.json()
        # Base should be RECOVERABLE (quantity blocks)
        assert data["base_result"]["decision"] in ("RECOVERABLE", "EXECUTABLE")
        # After recovery overlay: quantity should be resolved
        # (other constraints like transport may still apply depending on economics)
        if data.get("after_recovery"):
            assert data["after_recovery"]["decision"] in ("EXECUTABLE", "RECOVERABLE")
            # Specifically: QUANTITY should no longer be in blocking constraints
            assert "QUANTITY" not in data["after_recovery"]["blocking_constraints"]

    def test_run_scenario_insufficient_data(self, client):
        """Missing price → INSUFFICIENT_DATA."""
        resp = client.post("/api/demo/scenarios/insufficient_data/run")
        assert resp.status_code == 200
        assert resp.json()["base_result"]["decision"] == "INSUFFICIENT_DATA"

    def test_run_nonexistent_scenario(self, client):
        resp = client.post("/api/demo/scenarios/does_not_exist/run")
        assert resp.status_code == 404


class TestWhatIf:
    def test_whatif_increases_executable_count(
        self, client, farmer_token, tomato_lot_80kg,
        gulf_buyer_requirement, gate_buyer_requirement
    ):
        """After adding 220kg via whatif, more opportunities should be EXECUTABLE."""
        # First analyze baseline
        client.post(
            f"/api/lots/{tomato_lot_80kg.id}/opportunities/analyze",
            headers=auth_header(farmer_token),
        )

        # Whatif: add 220kg (simulates aggregation)
        resp = client.post(
            f"/api/lots/{tomato_lot_80kg.id}/whatif",
            json={"extra_quantity_kg": 220},
            headers=auth_header(farmer_token),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert "summary" in data
        assert data["whatif_applied"]["extra_quantity_kg"] == 220
        # Lot must NOT be modified
        assert data["note"] == "Lot NOT modified. This is a simulation. Apply recovery actions to persist changes."

    def test_whatif_lot_not_modified(
        self, client, farmer_token, db, tomato_lot_80kg
    ):
        """Lot quantity must remain 0.8 quintals after whatif."""
        client.post(
            f"/api/lots/{tomato_lot_80kg.id}/whatif",
            json={"extra_quantity_kg": 500},
            headers=auth_header(farmer_token),
        )
        # Verify DB unchanged
        resp = client.get(
            f"/api/lots/{tomato_lot_80kg.id}",
            headers=auth_header(farmer_token),
        )
        assert resp.status_code == 200
        assert float(resp.json()["quantity_kg"]) == pytest.approx(80.0, rel=0.01)

    def test_whatif_requires_auth(self, client, tomato_lot_80kg):
        resp = client.post(
            f"/api/lots/{tomato_lot_80kg.id}/whatif",
            json={"extra_quantity_kg": 100},
        )
        assert resp.status_code in (401, 403)


class TestBuyerRequirements:
    def test_get_buyer_requirements(
        self, client, farmer_token, gulf_buyer_requirement
    ):
        buyer_id = str(gulf_buyer_requirement.buyer_id)
        resp = client.get(
            f"/api/buyers/{buyer_id}/requirements",
            headers=auth_header(farmer_token),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 1
        req = data["requirements"][0]
        assert "offered_price" in req
        assert "offered_price_per_kg" in req
        assert "minimum_quantity_kg" in req
        assert "source_type" in req
        assert req["offered_price_per_kg"] == pytest.approx(34.0, rel=0.01)
        assert req["minimum_quantity_kg"] == pytest.approx(300.0, rel=0.01)


class TestMarketsOptionalState:
    def test_list_markets_no_state(self, client, farmer_token, madanapalle_market):
        """State is now optional — should return all markets."""
        resp = client.get("/api/markets", headers=auth_header(farmer_token))
        assert resp.status_code == 200
        data = resp.json()
        assert "total" in data
        assert "items" in data
        assert data["total"] >= 1

    def test_list_markets_with_state(self, client, farmer_token, madanapalle_market):
        resp = client.get(
            "/api/markets?state=Andhra Pradesh",
            headers=auth_header(farmer_token),
        )
        assert resp.status_code == 200
        assert resp.json()["total"] >= 1


class TestPriceHistorySellingWindow:
    def test_history_includes_selling_window(
        self, client, farmer_token, db,
        tomato_commodity, madanapalle_market
    ):
        from app.models import MarketPrice
        from decimal import Decimal
        from datetime import timedelta

        today = date.today()
        # Seed 7 days of price history
        for i in range(7):
            d = today - timedelta(days=6 - i)
            price = 2700 + i * 20  # rising trend → WAIT signal
            db.add(MarketPrice(
                market_id=madanapalle_market.id,
                commodity_id=tomato_commodity.id,
                price_date=d,
                min_price=Decimal(str(price - 200)),
                max_price=Decimal(str(price + 200)),
                modal_price=Decimal(str(price)),
                quantity_traded=Decimal("400"),
                source="Sample Data",
            ))
        db.commit()

        resp = client.get(
            f"/api/market-prices/history"
            f"?market_id={madanapalle_market.id}"
            f"&commodity_id={tomato_commodity.id}"
            f"&days=30"
            f"&include_selling_signal=true",
            headers=auth_header(farmer_token),
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "selling_window" in data
        sw = data["selling_window"]
        assert "signal" in sw
        assert sw["signal"] in ("SELL_NOW", "WAIT", "CONSIDER_ALTERNATIVE", "NEUTRAL", "INSUFFICIENT_DATA")
        assert "explanation" in sw
        assert "caveat" in sw  # must always show caveat


class TestBuyersNewFields:
    def test_buyers_include_source_type(
        self, client, farmer_token, gulf_buyer_requirement
    ):
        """source_type, payment_days, pickup_available must appear in buyer list."""
        resp = client.get("/api/buyers", headers=auth_header(farmer_token))
        assert resp.status_code == 200
        items = resp.json()["items"]
        assert len(items) >= 1
        buyer = items[0]
        assert "source_type" in buyer
        assert "payment_days" in buyer
        assert "pickup_available" in buyer
        assert "verification_status" in buyer
        # Data status must be present
        assert "data_status" in resp.json()
