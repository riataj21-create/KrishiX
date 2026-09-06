"""
Integration tests: lot CRUD and opportunity analysis via HTTP.
"""
import pytest
from datetime import date, timedelta


TODAY_STR = date.today().isoformat()
TOMORROW_STR = (date.today() + timedelta(days=1)).isoformat()


def auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ── Lot CRUD ──────────────────────────────────────────────────────────────────

class TestLotCRUD:
    def test_create_lot(self, client, farmer_token, tomato_commodity):
        resp = client.post(
            "/api/lots",
            json={
                "commodity_id": str(tomato_commodity.id),
                "quantity": 0.8,
                "unit": "quintal",
                "state": "Andhra Pradesh",
                "district": "Madanapalle",
                "quality_grade": "Grade B",
                "available_from": TODAY_STR,
                "sell_by": TODAY_STR,
                "minimum_price": 2800,
                "max_payment_days": 2,
            },
            headers=auth_header(farmer_token),
        )
        assert resp.status_code == 201, resp.text
        data = resp.json()
        assert float(data["quantity"]) == pytest.approx(0.8, rel=0.01)
        assert data["quality_grade"] == "Grade B"
        assert data["status"] == "available"
        assert "id" in data
        return data["id"]

    def test_list_lots(self, client, farmer_token, tomato_lot_80kg):
        resp = client.get("/api/lots", headers=auth_header(farmer_token))
        assert resp.status_code == 200
        assert resp.json()["total"] >= 1
        ids = [item["id"] for item in resp.json()["items"]]
        assert str(tomato_lot_80kg.id) in ids

    def test_get_lot(self, client, farmer_token, tomato_lot_80kg):
        resp = client.get(f"/api/lots/{tomato_lot_80kg.id}", headers=auth_header(farmer_token))
        assert resp.status_code == 200
        assert resp.json()["id"] == str(tomato_lot_80kg.id)

    def test_get_lot_requires_auth(self, client, tomato_lot_80kg):
        resp = client.get(f"/api/lots/{tomato_lot_80kg.id}")
        assert resp.status_code in (401, 403)

    def test_update_lot(self, client, farmer_token, tomato_lot_80kg):
        resp = client.put(
            f"/api/lots/{tomato_lot_80kg.id}",
            json={"quality_notes": "Fresh harvest"},
            headers=auth_header(farmer_token),
        )
        assert resp.status_code == 200
        assert resp.json()["quality_notes"] == "Fresh harvest"

    def test_delete_lot(self, client, farmer_token, tomato_lot_80kg):
        resp = client.delete(f"/api/lots/{tomato_lot_80kg.id}", headers=auth_header(farmer_token))
        assert resp.status_code == 200
        assert resp.json()["deleted"] is True
        # Should 404 now
        resp2 = client.get(f"/api/lots/{tomato_lot_80kg.id}", headers=auth_header(farmer_token))
        assert resp2.status_code == 404

    def test_farmer_cannot_access_other_farmer_lot(self, client, farmer_token, db, tomato_commodity):
        """farmer_token fixture creates farmer@test.com; we create a separate lot owned by a different user."""
        from app.models import User, FarmerLot
        from app.auth import hash_password
        from uuid import uuid4
        from decimal import Decimal

        other = User(id=uuid4(), email="other_farmer2@test.com", password_hash=hash_password("pass1234"), role="farmer")
        db.add(other)
        db.flush()
        lot = FarmerLot(
            id=uuid4(),
            farmer_id=other.id,
            commodity_id=tomato_commodity.id,
            quantity=Decimal("1.0"),
            state="Punjab",
            district="Ludhiana",
            available_from=date.today(),
            sell_by=date.today() + timedelta(days=7),
            status="available",
        )
        db.add(lot)
        db.commit()

        # Use farmer_token (farmer@test.com) to access OTHER farmer's lot → must be 403
        resp = client.get(f"/api/lots/{lot.id}", headers=auth_header(farmer_token))
        assert resp.status_code == 403

    def test_sell_by_before_available_from_rejected(self, client, farmer_token, tomato_commodity):
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        resp = client.post(
            "/api/lots",
            json={
                "commodity_id": str(tomato_commodity.id),
                "quantity": 1.0,
                "state": "Andhra Pradesh",
                "district": "Madanapalle",
                "available_from": TODAY_STR,
                "sell_by": yesterday,
                "max_payment_days": 2,
            },
            headers=auth_header(farmer_token),
        )
        assert resp.status_code == 400


# ── Opportunity Analysis ───────────────────────────────────────────────────────

class TestOpportunityAnalysis:
    def test_analyze_returns_opportunities(
        self, client, farmer_token, tomato_lot_80kg, gulf_buyer_requirement, gate_buyer_requirement
    ):
        resp = client.post(
            f"/api/lots/{tomato_lot_80kg.id}/opportunities/analyze",
            headers=auth_header(farmer_token),
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert "items" in data
        assert len(data["items"]) >= 2

    def test_executable_ranked_first(
        self, client, farmer_token, tomato_lot_80kg, gulf_buyer_requirement, gate_buyer_requirement
    ):
        resp = client.post(
            f"/api/lots/{tomato_lot_80kg.id}/opportunities/analyze",
            headers=auth_header(farmer_token),
        )
        items = resp.json()["items"]
        # Sort by rank
        items_sorted = sorted(items, key=lambda x: x.get("rank", 999))
        top = items_sorted[0]
        # The farm-gate buyer (executable) should beat the gulf buyer (not viable)
        assert top["feasibility_decision"] == "EXECUTABLE"

    def test_gulf_buyer_not_viable(
        self, client, farmer_token, tomato_lot_80kg, gulf_buyer_requirement
    ):
        resp = client.post(
            f"/api/lots/{tomato_lot_80kg.id}/opportunities/analyze",
            headers=auth_header(farmer_token),
        )
        items = resp.json()["items"]
        gulf_item = next(
            (i for i in items if i.get("buyer_requirement_id") == str(gulf_buyer_requirement.id)),
            None,
        )
        assert gulf_item is not None
        assert gulf_item["feasibility_decision"] == "NOT_VIABLE"
        blocks = gulf_item["blocking_constraints"]
        assert "QUANTITY" in blocks
        assert "QUALITY" in blocks
        assert "PAYMENT" in blocks

    def test_opportunities_persist_and_list(
        self, client, farmer_token, tomato_lot_80kg, gulf_buyer_requirement
    ):
        # Analyze first
        client.post(
            f"/api/lots/{tomato_lot_80kg.id}/opportunities/analyze",
            headers=auth_header(farmer_token),
        )
        # Then list
        resp = client.get(
            f"/api/lots/{tomato_lot_80kg.id}/opportunities",
            headers=auth_header(farmer_token),
        )
        assert resp.status_code == 200
        assert len(resp.json()["items"]) >= 1

    def test_recovery_apply(
        self, client, farmer_token, tomato_lot_80kg, gulf_buyer_requirement, gate_buyer_requirement
    ):
        # Analyze to create opportunities
        analyze_resp = client.post(
            f"/api/lots/{tomato_lot_80kg.id}/opportunities/analyze",
            headers=auth_header(farmer_token),
        )
        items = analyze_resp.json()["items"]
        # Find a recoverable opportunity (if any)
        recoverable = next(
            (i for i in items if i.get("feasibility_decision") == "RECOVERABLE"),
            None,
        )
        if recoverable is None:
            pytest.skip("No recoverable opportunity in this fixture set")
        opp_id = recoverable["id"]
        resp = client.post(
            f"/api/opportunities/{opp_id}/recovery",
            json={"change_types": ["NEGOTIATE_PAYMENT"]},
            headers=auth_header(farmer_token),
        )
        assert resp.status_code == 200
        data = resp.json()
        # After negotiating payment, constraint should be cleared or decision improved
        assert data["feasibility_decision"] in ("EXECUTABLE", "RECOVERABLE")

    def test_unauthorized_opportunity_access(
        self, client, tomato_lot_80kg, gulf_buyer_requirement
    ):
        resp = client.post(
            f"/api/lots/{tomato_lot_80kg.id}/opportunities/analyze",
        )
        assert resp.status_code in (401, 403)
