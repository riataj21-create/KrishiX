# KrishiX — Frontend API Contract (Complete, Final)

**Base URL:** All routes are relative `/api/*`  
**Auth:** `Authorization: Bearer <access_token>` on every protected endpoint  
**Proxy:** Vite dev server proxies `/api/*` → `http://localhost:8000`  
**No API keys in frontend.** All external calls go through the backend.

---

## ── Authentication ─────────────────────────────────────────────────────────

### POST /api/auth/register
```json
// Request
{ "email": "farmer@example.com", "password": "password123", "role": "farmer" }
// role: "farmer" | "buyer" (default: "farmer"). "admin" not allowed via registration.

// Response 201
{ "id": "uuid", "email": "...", "role": "farmer", "is_active": true, "created_at": "...", "updated_at": "..." }
// 409 if email already registered
```

### POST /api/auth/login
```json
// Request
{ "email": "farmer@example.com", "password": "password123" }

// Response 200
{ "access_token": "eyJ...", "token_type": "bearer", "expires_in": 1800 }
// Store access_token in localStorage. Send as Authorization: Bearer <token>.
// 401 if credentials invalid
```

### POST /api/auth/logout
```json
// Response 200
{ "message": "Successfully logged out" }
// Frontend removes token from localStorage
```

---

## ── Current User ───────────────────────────────────────────────────────────

### GET /api/users/me *(auth)*
```json
// Response 200
{ "id": "uuid", "email": "farmer@example.com", "role": "farmer", "is_active": true, "created_at": "...", "updated_at": "..." }
```

### PUT /api/users/me *(auth)*
```json
// Request: { "email": "new@example.com" }
// Response 200 — same as GET
```

### PUT /api/users/me/password *(auth)*
```json
// Request: { "current_password": "old", "new_password": "newpass123" }
// Response 200: { "message": "Password updated successfully" }
// 400 if current password wrong
```

---

## ── Farmer Profile ─────────────────────────────────────────────────────────

### GET /api/farmer-profile *(auth)*
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

### POST /api/farmer-profile *(auth)* → 201
### PUT /api/farmer-profile *(auth)* → 200
```json
// Request (all fields optional for PUT)
{
  "full_name": "Ravi Reddy", "phone": "9876543210",
  "state": "Andhra Pradesh", "district": "Madanapalle",
  "village": "Madanapalle", "latitude": 13.5504, "longitude": 78.5024
}
```

---

## ── Farmer Lots (Produce) ──────────────────────────────────────────────────

### GET /api/lots *(auth)*
```
?status=available   (optional: available|offered|negotiating|reserved|sold|cancelled)
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
    "quantity": "0.80",            // quintals (string from Decimal)
    "quantity_kg": 80.0,
    "unit": "quintal",
    "state": "Andhra Pradesh", "district": "Madanapalle", "village": "Madanapalle",
    "latitude": "13.5504", "longitude": "78.5024",
    "quality_status": "Grade B", "quality_grade": "Grade B", "quality_notes": null,
    "available_from": "2025-01-15", "sell_by": "2025-01-15",
    "minimum_price": "2800.00",    // ₹/quintal. null if not set.
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

### POST /api/lots *(auth)* → 201
```json
// Request
{
  "commodity_id": "uuid",
  "quantity": 0.8,
  "unit": "quintal",
  "state": "Andhra Pradesh",
  "district": "Madanapalle",
  "village": "Madanapalle",
  "latitude": 13.5504, "longitude": 78.5024,
  "quality_grade": "Grade B",
  "quality_status": "Grade B",
  "available_from": "2025-01-15",
  "sell_by": "2025-01-15",
  "minimum_price": 2800,
  "max_payment_days": 2,
  "transport_preference": "BUYER_PICKUP"
}
// 400 if sell_by before available_from
// 404 if commodity_id not found
```

### GET /api/lots/{lot_id} *(auth, owner only)* → 200 lot item
### PUT /api/lots/{lot_id} *(auth, owner only)* → 200
### DELETE /api/lots/{lot_id} *(auth, owner only)* → `{ "deleted": true }`

---

## ── Opportunities & Feasibility ────────────────────────────────────────────

### POST /api/lots/{lot_id}/opportunities/analyze *(auth, owner only)*
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
      // ── Identity ──────────────────────────────────────────────────
      "id": "uuid",
      "lot_id": "uuid",
      "opportunity_type": "BUYER",          // BUYER | MARKET
      "buyer_requirement_id": "uuid",
      "market_id": null,
      "title": "Farm-gate Trader Demo",
      "buyer_name": "Farm-gate Trader Demo",
      "buyer_type": "Trader",
      "source_type": "demo",                // demo | reference | verified_active | observed
      "data_quality": "DEMO",
      "price_kind": "buyer_offer",          // buyer_offer | market_price

      // ── Price & terms ─────────────────────────────────────────────
      "offered_price": 3000.0,              // ₹/quintal
      "payment_days": 0,
      "required_grade": "Grade B",
      "minimum_quantity": 0.5,              // quintals
      "pickup_available": true,
      "price_note": "Demo/reference buyer offer, not a guaranteed sale price.",

      // ── THE CORE FEASIBILITY RESULT ───────────────────────────────
      "feasibility_decision": "EXECUTABLE", // EXECUTABLE | RECOVERABLE | NOT_VIABLE | INSUFFICIENT_DATA
      "blocking_constraints": [],
      "opportunity_gaps": [],
      "minimum_viable_changes": [],
      "explanation": "This sale can go ahead with the lot as it stands.",
      "confidence_score": 100.0,
      "warnings": [],

      // ── Economics ─────────────────────────────────────────────────
      "economics": {
        "sale_value": 2400.0,
        "transport": 0.0,
        "transport_source": "buyer_pickup",
        "market_charges": 0.0,
        "loading_handling": 0.0,
        "estimated_net": 2400.0,
        "estimated_net_per_quintal": 3000.0,
        "labels": {
          "sale_value": "Gross at offered price × this lot quantity — not a guaranteed receipt",
          "transport": "Transport is buyer_pickup — not a live quote unless source is a provider",
          "net": "Estimated realization, not profit"
        }
      },
      "estimated_net_realization": 2400.0,
      "rank": 1,
      "applied_recovery": null
    },
    {
      // NOT_VIABLE example (Gulf buyer)
      "title": "Rayalaseema Gulf Exports (DEMO)",
      "offered_price": 3400.0,
      "feasibility_decision": "NOT_VIABLE",
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
          "description": "Combine with other compatible lots totaling at least 220.0 kg more.",
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
      "explanation": "This opportunity cannot be used. [full text]",
      "rank": 3
    }
  ],
  "recommendation": "Best executable option: Farm-gate Trader Demo (ranked by estimated realization, not advertised price).",
  // ── NEW: Opportunity gap ─────────────────────────────────────────
  "opportunity_gap": {
    "highest_quoted_per_quintal": 3400.0,
    "highest_quoted_per_kg": 34.0,
    "best_executable_per_quintal": 3000.0,
    "best_executable_per_kg": 30.0,
    "gap_per_quintal": 400.0,
    "gap_per_kg": 4.0,
    "label": "Opportunity gap — not guaranteed lost income. The higher-quoted opportunity has unmet constraints."
  },
  // ── NEW: Summary counts ─────────────────────────────────────────
  "summary": {
    "total": 5,
    "executable": 1,
    "recoverable": 2,
    "not_viable": 2,
    "insufficient_data": 0
  },
  "data_caveat": "Buyer offers in this demo are labelled demo/reference. Market prices are observed sample data, not guaranteed receipts. Estimated net realization deducts labelled costs only."
}
```

### GET /api/lots/{lot_id}/opportunities *(auth, owner only)*
Returns previously-analyzed opportunities or auto-analyzes if none exist.
Same shape as POST analyze response (just `lot_id` + `items`).

### GET /api/opportunities/{opportunity_id} *(auth, owner only)*
Full detail for one opportunity. Same item shape as above.

### POST /api/opportunities/{opportunity_id}/recovery *(auth, owner only)*
```json
// Request
{ "change_types": ["AGGREGATION", "NEGOTIATE_PAYMENT"] }
// Valid: AGGREGATION | NEGOTIATE_PAYMENT | NEGOTIATE_PRICE | TRANSPORT_OPTIMIZATION

// Response 200 — re-evaluated opportunity + aggregation plan
{
  // ... full opportunity item with updated feasibility_decision ...
  "aggregation": {
    "needed_quintals": 2.2,
    "needed_kg": 220.0,
    "can_aggregate": true,
    "members": [
      {
        "lot_id": "uuid", "farmer_id": "uuid",
        "quantity_quintals": 1.2, "quantity_kg": 120.0,
        "quality_grade": "Grade B", "district": "Madanapalle",
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

### POST /api/lots/{lot_id}/whatif *(auth, owner only)* — **NEW**
Re-evaluate with modified constraints. Lot is NOT changed in DB.
```json
// Request
{
  "extra_quantity_kg": 220,         // simulate aggregation
  "negotiated_payment_days": 2,     // simulate payment negotiation
  "negotiated_price_per_kg": null,  // simulate price negotiation
  "assume_buyer_pickup": null,      // simulate buyer pickup
  "transport_cost_override": null   // override transport cost
}
// All fields optional. Only provided fields are applied.

// Response 200
{
  "lot_id": "uuid",
  "whatif_applied": {
    "extra_quantity_kg": 220,
    "negotiated_payment_days": 2,
    "negotiated_price_per_kg": null,
    "assume_buyer_pickup": null,
    "transport_cost_override": null
  },
  "items": [ /* full opportunity list with UPDATED feasibility */ ],
  "summary": { "total": 5, "executable": 3, "recoverable": 1, "not_viable": 1 },
  "note": "Lot NOT modified. This is a simulation. Apply recovery actions to persist changes."
}
```

---

## ── Offers & Transactions ───────────────────────────────────────────────────

### POST /api/opportunities/{opportunity_id}/offer *(auth, owner only)*
Create offer from an EXECUTABLE opportunity.
**Only works when `feasibility_decision == "EXECUTABLE"`.**
```json
// Response 201
{
  "id": "uuid", "lot_id": "uuid", "buyer_id": "uuid",
  "buyer_requirement_id": "uuid",
  "offered_price_per_quintal": 3000.0, "quantity_quintal": 0.8,
  "payment_days": 0, "payment_method": "Cash",
  "pickup_date": "2025-01-15", "quality_terms": "Grade B",
  "transport_responsibility": "BUYER",
  "status": "pending",
  "expires_at": "2025-01-17T10:00:00",
  "accepted_at": null, "accepted_terms_snapshot": null,
  "created_at": "..."
}
// 400 if opportunity is NOT EXECUTABLE
```

### GET /api/lots/{lot_id}/offers *(auth, owner only)*
```json
{ "items": [ /* offer objects */ ] }
```

### POST /api/offers/{offer_id}/accept *(auth)*
Accept → creates transaction.
```json
// Response 200
{
  "id": "uuid", "offer_id": "uuid", "lot_id": "uuid",
  "farmer_id": "uuid", "buyer_id": "uuid",
  "agreed_price_per_quintal": 3000.0,
  "agreed_quantity": 0.8,
  "agreed_payment_days": 0,
  "payment_status": "agreed",
  "status": "accepted",
  "is_disputed": false,
  "created_at": "...", "updated_at": "...",
  "events": [
    { "id": "uuid", "event_type": "OFFER_ACCEPTED", "event_data": "{...}", "created_at": "..." }
  ],
  "payment": {
    "id": "uuid",
    "payment_status": "agreed",
    "payment_method": "Cash",
    "payment_amount": 2400.0,
    "payment_due_date": "2025-01-15",
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
// 409 if transaction already exists for this offer
```

---

## ── Transaction Lifecycle ───────────────────────────────────────────────────

### GET /api/transactions *(auth)*
```json
{ "items": [ /* transaction objects */ ], "disclaimer": "..." }
```

### GET /api/transactions/{transaction_id} *(auth, party only)*
Single transaction with full events + payment.

### POST /api/transactions/{transaction_id}/advance *(auth, party only)*
Advance lifecycle: `accepted → pickup_scheduled → payment_pending`
```json
// Response 200 — updated transaction
// Status flow: accepted → pickup_scheduled → payment_pending
// Cannot advance beyond payment_pending here — use payment endpoints
```

### POST /api/transactions/{transaction_id}/payment/report
Buyer reports payment made.
```json
// Request
{ "demo_as_buyer": true, "payment_reference": "UPI-12345" }
// demo_as_buyer: allows farmer to simulate buyer step in demo

// Response 200 — payment.payment_status → "buyer_reported_paid"
```

### POST /api/transactions/{transaction_id}/payment/confirm
Farmer confirms or disputes.
```json
// Confirm: { "confirmed": true }
// Dispute: { "confirmed": false, "notes": "Payment not received" }

// Confirm → status: "completed", payment_status: "payment_confirmed"
// Dispute → status: "disputed", payment.is_disputed: true
```

---

## ── Markets ────────────────────────────────────────────────────────────────

### GET /api/markets *(auth)* — **FIXED: state now optional**
```
?state=Andhra Pradesh   (optional — omit for all markets)
?district=Madanapalle   (optional)
?limit=50&offset=0
```
```json
// Response 200
{
  "total": 7,
  "items": [{
    "id": "uuid", "name": "Madanapalle Tomato Market",
    "state": "Andhra Pradesh", "district": "Madanapalle",
    "village": "Madanapalle", "market_type": "APMC",
    "latitude": 13.5504, "longitude": 78.5024,
    "contact_phone": null, "website_url": null,
    "created_at": "...", "updated_at": "..."
  }],
  "retrieved_at": "..."
}
```

### GET /api/markets/{market_id} *(auth)*

---

## ── Market Prices ───────────────────────────────────────────────────────────

### GET /api/market-prices *(no auth required)*
```
?state=Andhra Pradesh&district=Madanapalle
?commodity_id=uuid&market_id=uuid
?date=2025-01-15   (optional — defaults to latest available)
?limit=20&offset=0
```
```json
// Response 200
{
  "total": 10,
  "items": [{
    "id": "uuid",
    "market_id": "uuid", "market_name": "Madanapalle Tomato Market",
    "commodity_id": "uuid", "commodity_name": "Tomato",
    "state": "Andhra Pradesh", "district": "Madanapalle",
    "price_date": "2025-01-15",
    "min_price": 2400.0, "max_price": 3200.0, "modal_price": 2800.0,
    "quantity_traded": 400.0,
    "source": "Sample Data",
    "data_freshness": "DEMO",   // DEMO | LATEST_AVAILABLE | RECENT | STALE | STALE (Nd old)
    "last_updated": "...", "created_at": "..."
  }]
}
```

### GET /api/market-prices/compare
```
?commodity_id=uuid&state=AP&district=Madanapalle&date=2025-01-15
```
```json
{
  "commodity_id": "uuid", "commodity_name": "Tomato",
  "date": "2025-01-15",
  "prices": [{
    "market_id": "uuid", "market_name": "...", "state": "...", "district": "...",
    "modal_price": 2800.0, "min_price": 2400.0, "max_price": 3200.0,
    "data_freshness": "DEMO", "source": "Sample Data"
  }],
  "data_note": "Market price ≠ guaranteed farmer realization. Deduct transport and market charges."
}
```

### GET /api/market-prices/history — **ENHANCED: selling window signal**
```
?market_id=uuid&commodity_id=uuid&days=30
?include_selling_signal=true   (default: true)
```
```json
{
  "market_id": "uuid", "market_name": "...",
  "commodity_id": "uuid", "commodity_name": "Tomato",
  "days_requested": 30, "data_points": 7,
  "trend": [
    { "date": "2025-01-09", "min_price": 2300.0, "max_price": 3100.0, "modal_price": 2700.0,
      "quantity_traded": 380.0, "data_freshness": "DEMO", "source": "Sample Data" }
    // ... more entries ...
  ],
  // ── NEW: selling window signal ───────────────────────────────────
  "selling_window": {
    "signal": "SELL_NOW",          // SELL_NOW | WAIT | CONSIDER_ALTERNATIVE | NEUTRAL
    "basis": "OBSERVED_PRICE_TREND",
    "explanation": "Current price (₹2800/quintal) is at or above the 7-day average (₹2720/quintal). Conditions are favourable for selling.",
    "latest_modal_price": 2800.0,
    "three_day_change_pct": 1.2,
    "seven_day_average": 2720.0,
    "data_points_used": 7,
    "caveat": "Signal based on observed historical data only. Not a price prediction. Not financial advice. Always consider your sell-by deadline before waiting."
  },
  "data_note": "Prices are OBSERVED historical data. Not predictions."
}
```

---

## ── Commodities ────────────────────────────────────────────────────────────

### GET /api/commodities *(no auth required)*
```
?category=Vegetables&limit=20&offset=0
```
```json
{ "total": 13, "items": [{ "id": "uuid", "name": "Tomato", "category": "Vegetables", "unit": "quintal" }] }
```

### GET /api/commodities/{id} *(no auth required)*

---

## ── Buyers ─────────────────────────────────────────────────────────────────

### GET /api/buyers *(auth)* — **ENHANCED: full fields including source_type**
```
?commodity=Tomato&state=AP&buyer_type=Exporter&quantity=0.8
?source_type=demo   (filter by: demo | reference | verified_active)
?limit=20&offset=0
```
```json
{
  "total": 7,
  "data_status": "DEMO",   // DEMO | MIXED — never hide this
  "data_note": "Buyers marked DEMO are seed data for demonstration. Not real registered marketplace users.",
  "items": [{
    "id": "uuid",
    "name": "Rayalaseema Gulf Exports (DEMO)",
    "buyer_type": "Exporter",
    "state": "Andhra Pradesh", "district": "Madanapalle",
    "commodity_name": "Tomato",
    // ── Fields now included (were missing before) ──────────────────
    "source_type": "demo",          // ALWAYS SHOW THIS — never hide demo status
    "payment_days": 7,
    "payment_method": "Bank Transfer",
    "pickup_available": false,
    "verification_status": "UNVERIFIED",
    "active_until": "2025-01-29",
    "active_requirements_count": 1,
    "active_requirements": null,    // null in list view, populated in detail view
    // ── Existing fields ────────────────────────────────────────────
    "min_quantity_quintal": 0.5,
    "max_quantity_quintal": 50.0,
    "quality_grade": "Grade B",
    "is_verified": false,
    "rating": null,
    "notes": "DEMO. High advertised price with Grade A requirement...",
    "whatsapp_link": null
  }],
  "retrieved_at": "..."
}
```

### GET /api/buyers/{buyer_id} *(auth)* — includes `active_requirements`
Same shape but `active_requirements` is populated with full requirement objects.

### GET /api/buyers/{buyer_id}/requirements *(auth)* — **NEW**
```
?active_only=true   (default: true)
```
```json
{
  "buyer_id": "uuid",
  "buyer_name": "Rayalaseema Gulf Exports (DEMO)",
  "source_type": "demo",
  "total": 1,
  "active_only": true,
  "requirements": [{
    "id": "uuid",
    "commodity_id": "uuid",
    "minimum_quantity": 3.0,          // quintals
    "minimum_quantity_kg": 300.0,
    "maximum_quantity": 50.0,
    "required_grade": "Grade A",
    "offered_price": 3400.0,          // ₹/quintal
    "offered_price_per_kg": 34.0,
    "payment_days": 7,
    "payment_method": "Bank Transfer",
    "pickup_available": false,
    "pickup_location_state": "Andhra Pradesh",
    "pickup_location_district": "Madanapalle",
    "transport_cost_total": 1500.0,
    "transport_cost_source": "configured_demo",
    "active_from": "2025-01-15",
    "active_until": "2025-01-29",
    "is_active": true,
    "source_type": "demo",
    "notes": "₹34/kg advertised. 300 kg min. Grade A. 7-day pay. ₹1,500 configured/demo transport."
  }]
}
```

---

## ── Saved ───────────────────────────────────────────────────────────────────

### GET /api/saved-markets *(auth)*
```json
{ "total": 2, "items": [{ "id": "uuid", "market_id": "uuid", "market_name": "...", "state": "...", "district": "...", "saved_at": "..." }] }
```
### POST /api/saved-markets/{market_id} *(auth)* → 201
### DELETE /api/saved-markets/{market_id} *(auth)* → 200

### GET /api/saved-commodities *(auth)*
### POST /api/saved-commodities/{commodity_id} *(auth)* → 201
### DELETE /api/saved-commodities/{commodity_id} *(auth)* → 200

---

## ── Weather ─────────────────────────────────────────────────────────────────

### GET /api/weather *(no auth required)*
```
?lat=13.5504&lon=78.5024
```
```json
{
  "data_status": "RECENT",   // RECENT | UNAVAILABLE
  "data_source": "Open-Meteo (https://open-meteo.com/)",
  "data_note": "Open-Meteo updates hourly. Not real-time streaming data.",
  "retrieved_at": "...",
  "current": {
    "temperature_c": 28.5, "humidity_pct": 65.0,
    "precipitation_mm": 0.0, "wind_speed_kmh": 12.0,
    "condition": "Partly cloudy", "weather_code": 2
  },
  "forecast_24h": { "total_precipitation_mm": 2.5, "rain_expected": false },
  "transport_risk": {
    "risk_level": "LOW",   // LOW | MEDIUM | HIGH | UNKNOWN
    "risk_factors": ["Weather conditions are within normal range for transport"],
    "sell_signal": "CONDITIONS NORMAL"
  }
}
// Returns degraded UNAVAILABLE response (not error) if Open-Meteo is down
```

---

## ── MSP ─────────────────────────────────────────────────────────────────────

### GET /api/msp *(no auth required)*
### GET /api/msp/{commodity_name} *(no auth required)*
```json
{
  "commodity": "Tomato",
  "msp_per_quintal": null,
  "note": "Tomato does not have a central government MSP.",
  "source": "CCEA, Government of India"
}
```

---

## ── Demo Lab ────────────────────────────────────────────────────────────────

### GET /api/demo/scenarios *(no auth required)*
```json
{
  "total": 13,
  "scenarios": [
    {
      "id": "executable",
      "name": "1. Executable — farm-gate buyer",
      "description": "80 kg Grade B tomato sold to local farm-gate trader. All constraints satisfied.",
      "demonstrates": "EXECUTABLE decision state.",
      "default_parameters": { "quantity_kg": 80, "grade": "Grade B", ... }
    },
    { "id": "quantity_gap", "name": "2. Quantity gap — primary demo scenario", ... },
    { "id": "quality_mismatch", ... },
    { "id": "payment_mismatch", ... },
    { "id": "transport_failure", ... },
    { "id": "deadline_expired", ... },
    { "id": "multiple_constraints", ... },
    { "id": "aggregation_recovery", ... },
    { "id": "payment_negotiation_recovery", ... },
    { "id": "whatif_quantity", ... },
    { "id": "price_floor", ... },
    { "id": "insufficient_data", ... },
    { "id": "opportunity_gap_demo", ... }
  ],
  "note": "All scenarios run through the production feasibility engine. Results are NOT hard-coded."
}
```

### POST /api/demo/scenarios/{scenario_id}/run *(no auth required)*
```json
// Optional request body — override any default parameter
{
  "quantity_kg": 150,
  "max_payment_days": 3
}

// Response 200
{
  "scenario_id": "quantity_gap",
  "scenario_name": "2. Quantity gap — primary demo scenario",
  "demonstrates": "NOT_VIABLE: QUANTITY + QUALITY + PAYMENT all block the highest-priced option.",
  "parameters_used": { "quantity_kg": 150, ... },
  "farmer_lot": { "quantity_kg": 150, "grade": "Grade B", "min_price_per_kg": 28, ... },
  "buyer": { "min_quantity_kg": 300, "required_grade": "Grade A", "offered_price_per_kg": 34, ... },
  "base_result": {
    "decision": "NOT_VIABLE",
    "blocking_constraints": ["QUANTITY", "QUALITY", "PAYMENT"],
    "opportunity_gaps": [ ... ],
    "minimum_viable_changes": [ ... ],
    "explanation": "This opportunity cannot be used. ...",
    "economics": { ... }
  },
  "after_recovery": null,
  "overlay_applied": null,
  "whatif_result": null,
  "contrast_buyer_result": null,
  "opportunity_gap": null,
  "engine_note": "Result produced by the deterministic feasibility engine — not hard-coded."
}
```

### POST /api/demo/seed *(auth required)*
Seeds demo data (tomato scenario, 7 buyers). Idempotent.
```json
// Response 200
{
  "tomato_lot_id": "uuid",
  "farmer_login": "farmer1@krishix.com",
  "password": "password123",
  "note": "80 kg Grade B Madanapalle tomato lot is ready. Demo buyers are labelled DEMO."
}
```

---

## ── Selling Decision (Legacy) ───────────────────────────────────────────────

### GET /api/selling-decision *(auth)*
Legacy net-realization endpoint. Preserved for backward compatibility.
```
?commodity_id=uuid&quantity_quintal=0.8&farmer_lat=13.55&farmer_lon=78.50
?state=Andhra Pradesh&district=Madanapalle
```
Returns ranked market options by estimated net realization (not feasibility engine).
Use `/api/lots/{lot_id}/opportunities/analyze` for the full feasibility result.

---

## ── UI Display Rules ────────────────────────────────────────────────────────

### feasibility_decision display

| Decision | Color | Icon | Label |
|---|---|---|---|
| `EXECUTABLE` | `#16a34a` green | ✓ | Can sell |
| `RECOVERABLE` | `#d97706` amber | ⟳ | Possible with changes |
| `NOT_VIABLE` | `#dc2626` red | ✗ | Cannot sell here |
| `INSUFFICIENT_DATA` | `#6b7280` gray | ? | Missing information |

### source_type badges (NEVER hide these)

| source_type | Display |
|---|---|
| `demo` | 🔵 **DEMO DATA** |
| `reference` | 🟡 **REFERENCE** |
| `observed` | 🟢 **MARKET PRICE** |
| `verified_active` | ✅ **VERIFIED** |

### selling_window signal display

| Signal | Color | Label |
|---|---|---|
| `SELL_NOW` | green | 📈 Conditions favourable |
| `WAIT` | amber | ⏳ Price trending up |
| `CONSIDER_ALTERNATIVE` | red | 📉 Price falling |
| `NEUTRAL` | gray | ➡ No clear signal |
| `INSUFFICIENT_DATA` | gray | ? Not enough data |

Always show the `caveat` field below the signal.

### Payment status flow
```
agreed → payment_pending → buyer_reported_paid → payment_confirmed
                                              ↘ disputed
```

### Economics disclaimer
Always show below any realization figure:
> "Estimated realization — not a guaranteed receipt. Transport cost is a configured/demo estimate, not a live quote."

### Opportunity gap display
Show only when `opportunity_gap` is non-null in analyze response:
> "Opportunity gap: ₹4/kg between highest quoted (₹34) and best executable (₹30). Higher-quoted buyer has unmet constraints."
> _(Not: "You lost ₹4/kg")_

---

## ── Demo Accounts ───────────────────────────────────────────────────────────

After running `POST /api/demo/seed`:

| Email | Password | Role | Notes |
|---|---|---|---|
| `farmer1@krishix.com` | `password123` | farmer | 80 kg tomato lot, Madanapalle |
| `farmer2@krishix.com` | `password123` | farmer | Aggregation participant (120 kg) |
| `farmer3@krishix.com` | `password123` | farmer | Aggregation participant (100 kg) |
| `buyer1@krishix.com` | `password123` | buyer | Linked to demo buyer requirements |

---

## ── Files Modified This Session ────────────────────────────────────────────

| File | Change |
|---|---|
| `backend/app/api/markets.py` | state/district now optional |
| `backend/app/api/buyers.py` | source_type, payment_days, pickup_available, buyer_requirements endpoint |
| `backend/app/api/opportunities.py` | opportunity_gap, summary counts, whatif endpoint |
| `backend/app/api/prices.py` | selling_window signal on history endpoint |
| `backend/app/api/demo.py` | 13 scenarios + parameterized run through real engine |
| `backend/app/main.py` | CORS updated |
| `backend/tests/conftest.py` | OSRM mock, zombie process fix |
| `backend/pytest.ini` | Warning suppression, default options |
| `docker-compose.yml` | CORS includes :5173, :5174, :8080 |
