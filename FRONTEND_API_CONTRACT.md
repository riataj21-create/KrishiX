# KrishiX — Complete Frontend API Contract

All requests use relative `/api/*` paths.  
Vite proxy routes them to the backend.  
Auth: `Authorization: Bearer <access_token>` header on all protected endpoints.

---

## Authentication

### POST /api/auth/register
```json
// Request
{ "email": "farmer@example.com", "password": "password123" }

// Response 201
{ "id": "uuid", "email": "farmer@example.com", "role": "farmer", "is_active": true, "created_at": "...", "updated_at": "..." }
```

### POST /api/auth/login
```json
// Request
{ "email": "farmer@example.com", "password": "password123" }

// Response 200
{ "access_token": "jwt...", "token_type": "bearer", "expires_in": 1800 }
```
Store `access_token` in localStorage. Send as `Authorization: Bearer <token>` on every protected request.

### POST /api/auth/logout
```json
// Response 200
{ "message": "Successfully logged out" }
```

---

## Current User

### GET /api/users/me *(auth required)*
```json
// Response 200
{ "id": "uuid", "email": "farmer@example.com", "role": "farmer", "is_active": true, "created_at": "...", "updated_at": "..." }
```

### PUT /api/users/me *(auth required)*
```json
// Request
{ "email": "newemail@example.com" }
// Response 200 — same as GET /api/users/me
```

### PUT /api/users/me/password *(auth required)*
```json
// Request
{ "current_password": "old", "new_password": "new123456" }
// Response 200
{ "message": "Password updated successfully" }
```

---

## Farmer Profile

### GET /api/farmer-profile *(auth required)*
```json
// Response 200
{
  "id": "uuid", "user_id": "uuid",
  "full_name": "Ravi Reddy", "phone": "9876543210",
  "state": "Andhra Pradesh", "district": "Madanapalle",
  "village": "Madanapalle", "postal_code": "517325",
  "latitude": "13.5504", "longitude": "78.5024",
  "bio": null, "created_at": "...", "updated_at": "..."
}
// 404 if not created yet
```

### POST /api/farmer-profile *(auth required)*
```json
// Request
{
  "full_name": "Ravi Reddy", "phone": "9876543210",
  "state": "Andhra Pradesh", "district": "Madanapalle",
  "village": "Madanapalle", "latitude": 13.5504, "longitude": 78.5024
}
// Response 201 — same shape as GET
```

### PUT /api/farmer-profile *(auth required)*
Same body as POST but all fields optional. Response 200.

---

## Farmer Lots (Produce)

### GET /api/lots *(auth required)*
```
?status=available   (optional filter: available|offered|negotiating|reserved|sold|cancelled)
?limit=50&offset=0
```
```json
// Response 200
{
  "total": 1,
  "items": [{
    "id": "uuid",
    "farmer_id": "uuid",
    "commodity_id": "uuid",
    "commodity_name": "Tomato",
    "quantity": "0.80",
    "quantity_kg": 80.0,
    "unit": "quintal",
    "state": "Andhra Pradesh",
    "district": "Madanapalle",
    "village": "Madanapalle",
    "latitude": "13.5504",
    "longitude": "78.5024",
    "quality_status": "Grade B",
    "quality_grade": "Grade B",
    "quality_notes": null,
    "available_from": "2025-01-01",
    "sell_by": "2025-01-01",
    "minimum_price": "2800.00",
    "max_payment_days": 2,
    "preferred_payment_method": null,
    "transport_preference": "BUYER_PICKUP",
    "max_transport_budget": null,
    "status": "available",
    "reserved_by_offer_id": null,
    "created_at": "...", "updated_at": "..."
  }]
}
```

### POST /api/lots *(auth required)*
```json
// Request
{
  "commodity_id": "uuid",
  "quantity": 0.8,
  "unit": "quintal",
  "state": "Andhra Pradesh",
  "district": "Madanapalle",
  "village": "Madanapalle",
  "latitude": 13.5504,
  "longitude": 78.5024,
  "quality_grade": "Grade B",
  "quality_status": "Grade B",
  "available_from": "2025-01-01",
  "sell_by": "2025-01-01",
  "minimum_price": 2800,
  "max_payment_days": 2,
  "transport_preference": "BUYER_PICKUP"
}
// Response 201 — same as lot item above
```

### GET /api/lots/{lot_id} *(auth required, owner only)*
Response 200 — single lot item.

### PUT /api/lots/{lot_id} *(auth required, owner only)*
Any subset of lot fields. Response 200.

### DELETE /api/lots/{lot_id} *(auth required, owner only)*
```json
// Response 200
{ "deleted": true }
```

---

## Opportunities & Feasibility

### POST /api/lots/{lot_id}/opportunities/analyze *(auth required, owner only)*
Runs feasibility engine against all active buyer requirements and market prices.
```
?farmer_priority=maximize_realization   (or: fastest_payment | lower_risk)
```
```json
// Response 200
{
  "lot_id": "uuid",
  "items": [
    {
      "id": "uuid",
      "lot_id": "uuid",
      "opportunity_type": "BUYER",           // BUYER | MARKET
      "buyer_requirement_id": "uuid",
      "market_id": null,
      "buyer_name": "Rayalaseema Gulf Exports (DEMO)",
      "buyer_type": "Exporter",
      "title": "Rayalaseema Gulf Exports (DEMO)",
      "offered_price": 3400.0,               // ₹/quintal
      "payment_days": 7,
      "required_grade": "Grade A",
      "minimum_quantity": 3.0,
      "pickup_available": false,
      "source_type": "demo",                 // demo | reference | verified_active | observed
      "data_quality": "DEMO",
      "price_kind": "buyer_offer",           // buyer_offer | market_price
      "price_note": "This is a demo/reference buyer offer, not a guaranteed sale price.",
      
      // ── THE CORE FEASIBILITY RESULT ──────────────────────────────
      "feasibility_decision": "NOT_VIABLE",  // EXECUTABLE | RECOVERABLE | NOT_VIABLE | INSUFFICIENT_DATA
      "blocking_constraints": ["QUANTITY", "QUALITY", "PAYMENT"],
      "opportunity_gaps": [
        {
          "constraint_type": "QUANTITY",
          "required": 3.0,
          "available": 0.8,
          "gap": 2.2,
          "gap_unit": "quintals",
          "explanation": "Buyer needs at least 300 kg (3 quintals). This lot has 80 kg (0.8 quintals) — short by 220 kg.",
          "severity": "HARD"
        },
        {
          "constraint_type": "QUALITY",
          "required": "Grade A",
          "available": "Grade B",
          "gap": "MISMATCH",
          "gap_unit": "grade",
          "explanation": "Buyer requires Grade A. This lot is Grade B, which does not meet that requirement.",
          "severity": "HARD"
        },
        {
          "constraint_type": "PAYMENT",
          "required": 2,
          "available": 7,
          "gap": 5,
          "gap_unit": "days",
          "explanation": "You need payment within 2 day(s). This buyer pays in 7 days (5 days too slow).",
          "severity": "HARD"
        }
      ],
      "minimum_viable_changes": [
        {
          "change_type": "AGGREGATION",
          "description": "Combine with other compatible lots totaling at least 220 kg more.",
          "parameters": { "additional_quantity_quintals": 2.2, "additional_quantity_kg": 220.0 },
          "feasible": true,
          "reason": "Quantity shortfalls can be closed by aggregating compatible lots.",
          "resulting_feasibility": "RECOVERABLE"
        },
        {
          "change_type": "QUALITY_UPGRADE",
          "description": "Grade cannot be raised after harvest without sorting/processing.",
          "parameters": { "required_grade": "Grade A", "current_grade": "Grade B" },
          "feasible": false,
          "reason": "Quality is a hard constraint for already-harvested produce.",
          "resulting_feasibility": "NOT_VIABLE"
        },
        {
          "change_type": "NEGOTIATE_PAYMENT",
          "description": "Ask the buyer to pay within 2 day(s) instead of 7.",
          "parameters": { "current_payment_days": 7, "target_payment_days": 2, "reduction_needed": 5 },
          "feasible": true,
          "reason": "Payment timing can be negotiated; it is not guaranteed.",
          "resulting_feasibility": "RECOVERABLE"
        }
      ],
      "explanation": "This opportunity cannot be used. [full text reason]",
      "confidence_score": 100.0,
      "warnings": [],
      "economics": {
        "sale_value": 2720.0,
        "transport": 1500.0,
        "transport_source": "configured_demo",
        "market_charges": 0.0,
        "loading_handling": 0.0,
        "estimated_net": 1220.0,
        "estimated_net_per_quintal": 1525.0,
        "labels": {
          "sale_value": "Gross at offered price × this lot quantity — not a guaranteed receipt",
          "transport": "Transport is configured_demo — not a live quote unless source is a provider",
          "net": "Estimated realization, not profit"
        }
      },
      "estimated_net_realization": 1220.0,
      "rank": 3,
      "applied_recovery": null
    }
    // ... more opportunities ranked 1, 2, 3 ...
  ],
  "recommendation": "Best executable option: Farm-gate Trader Demo (ranked by estimated realization, not advertised price).",
  "data_caveat": "Buyer offers in this demo are labelled demo/reference. Market prices are observed sample data, not guaranteed receipts."
}
```

### GET /api/lots/{lot_id}/opportunities *(auth required, owner only)*
Returns previously-analyzed opportunities (or auto-analyzes if none exist).
Same response shape as POST analyze.

### GET /api/opportunities/{opportunity_id} *(auth required, owner only)*
```json
// Response 200 — single opportunity with full detail (same shape as items above)
```

### POST /api/opportunities/{opportunity_id}/recovery *(auth required, owner only)*
Apply recovery actions and re-run feasibility.
```json
// Request
{
  "change_types": ["AGGREGATION", "NEGOTIATE_PAYMENT"]
  // Valid values: AGGREGATION | NEGOTIATE_PAYMENT | NEGOTIATE_PRICE | TRANSPORT_OPTIMIZATION
}

// Response 200 — re-evaluated opportunity (same shape as opportunity item)
// + extra field:
{
  "aggregation": {
    "needed_quintals": 2.2,
    "needed_kg": 220.0,
    "can_aggregate": true,
    "members": [
      {
        "lot_id": "uuid",
        "farmer_id": "uuid",
        "quantity_quintals": 1.2,
        "quantity_kg": 120.0,
        "quality_grade": "Grade B",
        "district": "Madanapalle",
        "participant_type": "demo_simulated",
        "label": "Demo / simulated participant — not a live nationwide farmer network"
      }
    ],
    "combined_quintals": 3.0,
    "combined_kg": 300.0,
    "reason": "Compatible demo lots can supply 300 kg together."
  },
  "applied_recovery": {
    "extra_quantity": 2.2,
    "negotiated_payment_days": 2,
    "negotiated_price": null,
    "transport_cost_override": null,
    "assume_buyer_pickup": false
  }
}
```

---

## Offers & Transactions

### POST /api/opportunities/{opportunity_id}/offer *(auth required, owner only)*
Accept an EXECUTABLE opportunity → creates an offer.
**Note: Only works if `feasibility_decision == "EXECUTABLE"`.**
```json
// Response 201
{
  "id": "uuid",
  "lot_id": "uuid",
  "buyer_id": "uuid",
  "buyer_requirement_id": "uuid",
  "offered_price_per_quintal": 3000.0,
  "quantity_quintal": 0.8,
  "payment_days": 0,
  "payment_method": "UPI",
  "pickup_date": "2025-01-01",
  "quality_terms": "Grade B",
  "transport_responsibility": "BUYER",
  "status": "pending",
  "expires_at": "...",
  "accepted_at": null,
  "accepted_terms_snapshot": null,
  "created_at": "..."
}
```

### GET /api/lots/{lot_id}/offers *(auth required, owner only)*
```json
// Response 200
{ "items": [ /* offer objects */ ] }
```

### POST /api/offers/{offer_id}/accept *(auth required)*
Accept offer → creates transaction.
```json
// Response 200
{
  "id": "uuid",
  "offer_id": "uuid",
  "lot_id": "uuid",
  "farmer_id": "uuid",
  "buyer_id": "uuid",
  "agreed_price_per_quintal": 3000.0,
  "agreed_quantity": 0.8,
  "agreed_payment_days": 0,
  "payment_status": "agreed",
  "status": "accepted",
  "is_disputed": false,
  "created_at": "...",
  "updated_at": "...",
  "events": [
    { "id": "uuid", "event_type": "OFFER_ACCEPTED", "event_data": "{...}", "created_at": "..." }
  ],
  "payment": {
    "id": "uuid",
    "payment_status": "agreed",
    "payment_method": "Cash",
    "payment_amount": 2400.0,
    "payment_due_date": "2025-01-01",
    "buyer_reported_paid_at": null,
    "buyer_payment_reference": null,
    "farmer_confirmed_at": null,
    "is_protected": false,
    "protection_provider": null,
    "is_disputed": false,
    "disclaimer": "KrishiX does not move money. Status is reported by the parties. Nothing here is protected, escrowed, or guaranteed."
  },
  "disclaimer": "KrishiX does not move money. ..."
}
```

---

## Transaction Lifecycle

### GET /api/transactions *(auth required)*
```json
// Response 200
{ "items": [ /* transaction objects */ ], "disclaimer": "..." }
```

### GET /api/transactions/{transaction_id} *(auth required, party only)*
Response 200 — single transaction (same shape as accept response).

### POST /api/transactions/{transaction_id}/advance *(auth required, party only)*
Advance: `accepted → pickup_scheduled → payment_pending`
```json
// Response 200 — updated transaction
```

### POST /api/transactions/{transaction_id}/payment/report
Buyer reports payment made.
```json
// Request
{
  "demo_as_buyer": true,       // For demo: farmer can simulate buyer step
  "payment_reference": "UPI-12345"
}
// Response 200 — updated transaction
// payment.payment_status → "buyer_reported_paid"
```

### POST /api/transactions/{transaction_id}/payment/confirm
Farmer confirms payment received (or disputes).
```json
// Request (confirm)
{ "confirmed": true }

// Request (dispute)
{ "confirmed": false, "notes": "Payment not received" }

// Response 200 — updated transaction
// Confirm: status → "completed", payment_status → "payment_confirmed"
// Dispute: status → "disputed", payment.is_disputed → true
```

---

## Markets & Prices

### GET /api/markets *(auth required)*
```
?state=Andhra Pradesh&district=Madanapalle&limit=20&offset=0
```
```json
// Response 200
{ "total": 6, "items": [{ "id": "uuid", "name": "...", "state": "...", ... }] }
```

### GET /api/markets/{market_id} *(auth required)*

### GET /api/market-prices *(auth required)*
```
?state=Andhra Pradesh
?commodity_id=uuid
?market_id=uuid
?limit=20&offset=0
```
```json
// Response 200
{
  "total": 10,
  "items": [{
    "id": "uuid",
    "market_id": "uuid", "commodity_id": "uuid",
    "price_date": "2025-01-01",
    "min_price": "2400.00", "max_price": "3200.00", "modal_price": "2800.00",
    "quantity_traded": "400.00",
    "source": "Sample Data",
    "market_name": "Madanapalle Tomato Market",
    "commodity_name": "Tomato",
    "state": "Andhra Pradesh", "district": "Madanapalle"
  }]
}
```

### GET /api/market-prices/compare *(auth required)*
```
?commodity_id=uuid&state=Andhra Pradesh
```

### GET /api/market-prices/history *(auth required)*
```
?market_id=uuid&commodity_id=uuid&days=30
```

---

## Commodities

### GET /api/commodities *(auth required)*
```
?category=Vegetables&limit=20&offset=0
```
```json
// Response 200
{ "total": 13, "items": [{ "id": "uuid", "name": "Tomato", "category": "Vegetables", "unit": "quintal" }] }
```

### GET /api/commodities/{id} *(auth required)*

---

## Buyers

### GET /api/buyers *(auth required)*
```
?commodity=Tomato&state=Andhra Pradesh&buyer_type=Exporter&limit=20
```
```json
// Response 200
{
  "total": 7,
  "items": [{
    "id": "uuid",
    "name": "Rayalaseema Gulf Exports (DEMO)",
    "buyer_type": "Exporter",
    "state": "Andhra Pradesh",
    "district": "Madanapalle",
    "commodity_name": "Tomato",
    "min_quantity_quintal": "0.50",
    "max_quantity_quintal": "50.00",
    "quality_grade": "Grade B",
    "source_type": "demo",      // ALWAYS show this — never hide that buyers are demo
    "is_verified": false,
    "payment_days": 7,
    "pickup_available": false,
    "rating": null,
    "notes": "DEMO. High advertised price with Grade A requirement..."
  }]
}
```

---

## Saved Markets / Commodities

### GET /api/saved-markets *(auth required)*
```json
{ "total": 2, "items": [{ "id": "uuid", "market_id": "uuid", "market_name": "...", "state": "...", "district": "...", "saved_at": "..." }] }
```

### POST /api/saved-markets/{market_id} *(auth required)*  → 201
### DELETE /api/saved-markets/{market_id} *(auth required)* → 200

### GET /api/saved-commodities *(auth required)*  
### POST /api/saved-commodities/{commodity_id}*  
### DELETE /api/saved-commodities/{commodity_id}*

---

## Weather

### GET /api/weather
```
?lat=13.5504&lon=78.5024
```
```json
{
  "data_status": "RECENT",
  "data_source": "Open-Meteo (https://open-meteo.com/)",
  "data_note": "Open-Meteo updates hourly. Not real-time streaming.",
  "current": {
    "temperature_c": 28.5, "humidity_pct": 65.0,
    "precipitation_mm": 0.0, "wind_speed_kmh": 12.0,
    "condition": "Partly cloudy", "weather_code": 2
  },
  "forecast_24h": { "total_precipitation_mm": 2.5, "rain_expected": false },
  "transport_risk": {
    "risk_level": "LOW",
    "risk_factors": ["Weather conditions are within normal range for transport"],
    "sell_signal": "CONDITIONS NORMAL"
  }
}
```
Returns degraded response (not error) if Open-Meteo unavailable.

---

## MSP (Minimum Support Price)

### GET /api/msp
```json
{
  "commodities": [
    {
      "name": "Rice",
      "msp_per_quintal": 2300.0,
      "season": "Kharif 2024-25",
      "source": "CCEA, Government of India",
      "note": null
    },
    {
      "name": "Tomato",
      "msp_per_quintal": null,
      "note": "Tomato does not have a central government MSP."
    }
  ]
}
```

### GET /api/msp/{commodity_name}

---

## Demo Lab

### GET /api/demo/scenarios
```json
{
  "scenarios": [
    { "id": "best_price_not_viable", "name": "₹34/kg buyer — NOT viable", "description": "..." },
    { "id": "executable_farm_gate", "name": "Farm-gate buyer — EXECUTABLE", "description": "..." },
    { "id": "quantity_gap", "name": "Quantity gap — RECOVERABLE", "description": "..." },
    { "id": "payment_mismatch", "name": "Payment mismatch — RECOVERABLE", "description": "..." },
    { "id": "transport_failure", "name": "Transport too expensive — NOT viable", "description": "..." },
    { "id": "quality_mismatch", "name": "Grade mismatch — NOT viable", "description": "..." },
    { "id": "deadline_failure", "name": "Expired opportunity — NOT viable", "description": "..." },
    { "id": "aggregation_recovery", "name": "Aggregate 3 farmers → EXECUTABLE", "description": "..." },
    { "id": "full_transaction", "name": "Full transaction flow", "description": "..." }
  ]
}
```

### POST /api/demo/scenarios/{scenario_id}/run
```json
// Optional request body — override parameters
{
  "quantity_kg": 80,
  "grade": "Grade B",
  "max_payment_days": 2,
  "minimum_price_per_kg": 28
}

// Response 200
{
  "scenario_id": "best_price_not_viable",
  "scenario_name": "₹34/kg buyer — NOT viable",
  "farmer_lot": { ... },
  "buyer": { "name": "...", "price_per_kg": 34, "min_quantity_kg": 300 },
  "feasibility": {
    "decision": "NOT_VIABLE",
    "blocking_constraints": ["QUANTITY", "QUALITY", "PAYMENT"],
    "opportunity_gaps": [ ... ],
    "minimum_viable_changes": [ ... ],
    "explanation": "..."
  },
  "note": "Result produced by the deterministic feasibility engine — not hard-coded."
}
```

---

## Key UI Display Rules

### feasibility_decision colors
| Decision | Color | Label |
|---|---|---|
| `EXECUTABLE` | Green | ✓ Can sell |
| `RECOVERABLE` | Amber | ⟳ Possible with changes |
| `NOT_VIABLE` | Red | ✗ Cannot sell here |
| `INSUFFICIENT_DATA` | Gray | ? Missing information |

### source_type badges
| source_type | Display |
|---|---|
| `demo` | 🔵 DEMO DATA |
| `reference` | 🟡 REFERENCE |
| `observed` | 🟢 MARKET PRICE |
| `verified_active` | ✅ VERIFIED |

**Never hide source_type.** Never show demo buyers without the DEMO label.

### payment_status flow
```
agreed → payment_pending → buyer_reported_paid → payment_confirmed
                                               ↘ disputed
```

### Economics disclaimer
Always show below any realization figure:
> "Estimated realization, not guaranteed receipt. Transport is a configured/demo estimate."
