"""
Integration tests: offer creation, acceptance, transaction lifecycle,
payment confirmation, and dispute flow.
"""
import pytest
import json
from datetime import date, timedelta
from decimal import Decimal
from uuid import uuid4


def auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_offer(db, lot, buyer_user, buyer_req, price=3000, qty=0.8, payment_days=2):
    """Directly create an Offer in DB to avoid dependency on offer endpoint."""
    from app.models import Offer
    from datetime import datetime, timedelta
    offer = Offer(
        id=uuid4(),
        lot_id=lot.id,
        buyer_id=buyer_user.id,
        buyer_requirement_id=buyer_req.id,
        offered_price_per_quintal=Decimal(str(price)),
        quantity_quintal=Decimal(str(qty)),
        payment_days=payment_days,
        payment_method="Cash",
        pickup_date=date.today(),
        quality_terms="Grade B",
        transport_responsibility="BUYER",
        status="pending",
        expires_at=datetime.utcnow() + timedelta(hours=48),
    )
    db.add(offer)
    db.commit()
    db.refresh(offer)
    return offer


# ── Offer Creation ─────────────────────────────────────────────────────────────

class TestOfferCreation:
    def test_create_offer_via_opportunity(
        self, client, farmer_token, db,
        tomato_lot_80kg, gate_buyer_requirement
    ):
        """Farm-gate buyer opportunity → farmer accepts → creates transaction."""
        # Analyze to get an executable opportunity
        analyze = client.post(
            f"/api/lots/{tomato_lot_80kg.id}/opportunities/analyze",
            headers=auth_header(farmer_token),
        )
        assert analyze.status_code == 200
        items = analyze.json()["items"]
        executable = next(
            (i for i in items if i.get("feasibility_decision") == "EXECUTABLE"),
            None,
        )
        assert executable is not None, "Expected at least one EXECUTABLE opportunity"
        opp_id = executable["id"]

        # Accept opportunity → creates offer
        offer_resp = client.post(
            f"/api/opportunities/{opp_id}/offer",
            headers=auth_header(farmer_token),
        )
        assert offer_resp.status_code == 201, offer_resp.text
        offer = offer_resp.json()
        assert offer["status"] == "pending"
        assert offer["lot_id"] == str(tomato_lot_80kg.id)
        return offer["id"]

    def test_cannot_offer_on_not_viable_opportunity(
        self, client, farmer_token, db,
        tomato_lot_80kg, gulf_buyer_requirement
    ):
        """NOT_VIABLE opportunity must reject offer creation."""
        analyze = client.post(
            f"/api/lots/{tomato_lot_80kg.id}/opportunities/analyze",
            headers=auth_header(farmer_token),
        )
        items = analyze.json()["items"]
        not_viable = next(
            (i for i in items if i.get("feasibility_decision") == "NOT_VIABLE"),
            None,
        )
        if not_viable is None:
            pytest.skip("No NOT_VIABLE opportunity found")
        resp = client.post(
            f"/api/opportunities/{not_viable['id']}/offer",
            headers=auth_header(farmer_token),
        )
        assert resp.status_code == 400


# ── Accept Offer → Transaction ─────────────────────────────────────────────────

class TestAcceptOfferCreatesTransaction:
    def test_accept_offer(
        self, client, farmer_token, db,
        tomato_lot_80kg, gate_buyer_requirement, buyer_user
    ):
        offer = _make_offer(db, tomato_lot_80kg, buyer_user, gate_buyer_requirement)

        resp = client.post(
            f"/api/offers/{offer.id}/accept",
            headers=auth_header(farmer_token),
        )
        assert resp.status_code == 200, resp.text
        txn = resp.json()
        assert txn["status"] == "accepted"
        assert txn["agreed_price_per_quintal"] == pytest.approx(3000.0, rel=0.01)
        assert txn["agreed_payment_days"] == 2
        assert "payment" in txn
        assert txn["payment"]["payment_status"] == "agreed"
        assert txn["payment"]["is_protected"] is False
        assert "disclaimer" in txn["payment"]
        return txn["id"]

    def test_accept_same_offer_twice_returns_existing_transaction(
        self, client, farmer_token, db,
        tomato_lot_80kg, gate_buyer_requirement, buyer_user
    ):
        offer = _make_offer(db, tomato_lot_80kg, buyer_user, gate_buyer_requirement)
        resp1 = client.post(f"/api/offers/{offer.id}/accept", headers=auth_header(farmer_token))
        assert resp1.status_code == 200
        txn_id1 = resp1.json()["id"]

        # Second accept — must return same transaction, not error
        resp2 = client.post(f"/api/offers/{offer.id}/accept", headers=auth_header(farmer_token))
        assert resp2.status_code == 200
        txn_id2 = resp2.json()["id"]
        assert txn_id1 == txn_id2


# ── Transaction Lifecycle ──────────────────────────────────────────────────────

class TestTransactionLifecycle:
    def _setup_transaction(self, client, farmer_token, db, lot, buyer_user, buyer_req):
        offer = _make_offer(db, lot, buyer_user, buyer_req)
        resp = client.post(f"/api/offers/{offer.id}/accept", headers=auth_header(farmer_token))
        assert resp.status_code == 200
        return resp.json()["id"]

    def test_full_lifecycle(
        self, client, farmer_token, db,
        tomato_lot_80kg, gate_buyer_requirement, buyer_user
    ):
        txn_id = self._setup_transaction(
            client, farmer_token, db, tomato_lot_80kg, buyer_user, gate_buyer_requirement
        )

        def advance():
            r = client.post(f"/api/transactions/{txn_id}/advance", headers=auth_header(farmer_token))
            assert r.status_code == 200, r.text
            return r.json()

        # accepted → pickup_scheduled
        t = advance()
        assert t["status"] == "pickup_scheduled"

        # pickup_scheduled → payment_pending (via delivered)
        t = advance()
        assert t["status"] == "payment_pending"

        # Report payment (demo_as_buyer = True so farmer can simulate buyer step)
        report = client.post(
            f"/api/transactions/{txn_id}/payment/report",
            json={"demo_as_buyer": True, "payment_reference": "UPI-12345"},
            headers=auth_header(farmer_token),
        )
        assert report.status_code == 200
        assert report.json()["payment"]["payment_status"] == "buyer_reported_paid"

        # Confirm payment
        confirm = client.post(
            f"/api/transactions/{txn_id}/payment/confirm",
            json={"confirmed": True},
            headers=auth_header(farmer_token),
        )
        assert confirm.status_code == 200
        final = confirm.json()
        assert final["status"] == "completed"
        assert final["payment"]["payment_status"] == "payment_confirmed"
        assert final["payment"]["is_protected"] is False

    def test_payment_dispute(
        self, client, farmer_token, db,
        tomato_lot_80kg, gate_buyer_requirement, buyer_user
    ):
        txn_id = self._setup_transaction(
            client, farmer_token, db, tomato_lot_80kg, buyer_user, gate_buyer_requirement
        )
        # Advance to payment_pending
        client.post(f"/api/transactions/{txn_id}/advance", headers=auth_header(farmer_token))
        client.post(f"/api/transactions/{txn_id}/advance", headers=auth_header(farmer_token))
        client.post(
            f"/api/transactions/{txn_id}/payment/report",
            json={"demo_as_buyer": True},
            headers=auth_header(farmer_token),
        )

        # Farmer disputes
        dispute = client.post(
            f"/api/transactions/{txn_id}/payment/confirm",
            json={"confirmed": False, "notes": "Payment not received"},
            headers=auth_header(farmer_token),
        )
        assert dispute.status_code == 200
        final = dispute.json()
        assert final["status"] == "disputed"
        assert final["payment"]["is_disputed"] is True

    def test_list_transactions(
        self, client, farmer_token, db,
        tomato_lot_80kg, gate_buyer_requirement, buyer_user
    ):
        txn_id = self._setup_transaction(
            client, farmer_token, db, tomato_lot_80kg, buyer_user, gate_buyer_requirement
        )
        resp = client.get("/api/transactions", headers=auth_header(farmer_token))
        assert resp.status_code == 200
        ids = [t["id"] for t in resp.json()["items"]]
        assert txn_id in ids

    def test_unauthorized_cannot_view_transaction(
        self, client, db,
        tomato_lot_80kg, gate_buyer_requirement, buyer_user
    ):
        from app.models import User
        from app.auth import hash_password
        # Create and log in as a different farmer
        other = User(id=uuid4(), email="stranger@test.com", password_hash=hash_password("pass1234"), role="farmer")
        db.add(other)
        db.commit()
        tok = client.post("/api/auth/login", json={"email": "stranger@test.com", "password": "pass1234"}).json()["access_token"]

        # Create a transaction as the original farmer
        offer = _make_offer(db, tomato_lot_80kg, buyer_user, gate_buyer_requirement)
        accept_resp = client.post(
            f"/api/offers/{offer.id}/accept",
            headers={"Authorization": f"Bearer {client.post('/api/auth/login', json={'email': 'farmer@test.com', 'password': 'password123'}).json()['access_token']}"},
        )
        txn_id = accept_resp.json()["id"]

        # Stranger tries to access
        resp = client.get(f"/api/transactions/{txn_id}", headers={"Authorization": f"Bearer {tok}"})
        assert resp.status_code == 403

    def test_transaction_has_event_log(
        self, client, farmer_token, db,
        tomato_lot_80kg, gate_buyer_requirement, buyer_user
    ):
        txn_id = self._setup_transaction(
            client, farmer_token, db, tomato_lot_80kg, buyer_user, gate_buyer_requirement
        )
        txn = client.get(f"/api/transactions/{txn_id}", headers=auth_header(farmer_token)).json()
        assert len(txn["events"]) >= 1
        event_types = [e["event_type"] for e in txn["events"]]
        assert "OFFER_ACCEPTED" in event_types


# ── Auth tests (existing) ──────────────────────────────────────────────────────

class TestAuth:
    def test_register_new_user(self, client):
        resp = client.post(
            "/api/auth/register",
            json={"email": "brand_new@test.com", "password": "password123"},
        )
        assert resp.status_code == 201
        assert resp.json()["email"] == "brand_new@test.com"

    def test_register_duplicate_email(self, client, farmer_user):
        resp = client.post(
            "/api/auth/register",
            json={"email": "farmer@test.com", "password": "password123"},
        )
        assert resp.status_code == 409

    def test_login_success(self, client, farmer_user):
        resp = client.post(
            "/api/auth/login",
            json={"email": "farmer@test.com", "password": "password123"},
        )
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    def test_login_wrong_password(self, client, farmer_user):
        resp = client.post(
            "/api/auth/login",
            json={"email": "farmer@test.com", "password": "wrong"},
        )
        assert resp.status_code == 401

    def test_protected_endpoint_without_token(self, client):
        resp = client.get("/api/lots")
        assert resp.status_code == 403
