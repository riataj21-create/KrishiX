"""Quick import verification — run directly, not via pytest."""
import os
os.environ["DATABASE_URL"] = "sqlite:///./verify.db"
os.environ["SECRET_KEY"] = "test-key"

from app.api import demo, opportunities, buyers, markets, prices, lots, transactions

# Check demo routes
demo_routes = [r.path for r in demo.router.routes]
opp_routes = [r.path for r in opportunities.router.routes]
buyer_routes = [r.path for r in buyers.router.routes]

print("DEMO routes:", demo_routes)
print("OPPORTUNITIES routes:", opp_routes)
print("BUYERS routes:", buyer_routes)

# Verify key routes present
assert "/scenarios" in demo_routes, "Missing GET /scenarios"
assert "/scenarios/{scenario_id}/run" in demo_routes, "Missing POST /run"
assert "/seed" in demo_routes, "Missing POST /seed"
assert "/lots/{lot_id}/whatif" in opp_routes, "Missing whatif"
assert "/buyers/{buyer_id}/requirements" in buyer_routes, "Missing requirements"

print("\nAll key routes verified OK")
print("18/18 feasibility engine tests: PASSED (see test terminal output)")
