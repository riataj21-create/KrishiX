"""Initial schema - all tables

Revision ID: 0001
Revises:
Create Date: 2025-01-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── users ──────────────────────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean(), default=True),
        sa.Column("role", sa.String(20), nullable=False, server_default="farmer"),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_users_email", "users", ["email"])
    op.create_index("ix_users_role", "users", ["role"])

    # ── farmer_profiles ────────────────────────────────────────────────────
    op.create_table(
        "farmer_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("state", sa.String(100), nullable=False),
        sa.Column("district", sa.String(100), nullable=False),
        sa.Column("village", sa.String(100), nullable=True),
        sa.Column("postal_code", sa.String(10), nullable=True),
        sa.Column("latitude", sa.Numeric(10, 8), nullable=True),
        sa.Column("longitude", sa.Numeric(11, 8), nullable=True),
        sa.Column("bio", sa.String(500), nullable=True),
        sa.Column("profile_image_url", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_index("idx_profile_state_district", "farmer_profiles", ["state", "district"])
    op.create_index("idx_profile_coordinates", "farmer_profiles", ["latitude", "longitude"])

    # ── commodities ────────────────────────────────────────────────────────
    op.create_table(
        "commodities",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("category", sa.String(50), nullable=True),
        sa.Column("unit", sa.String(20), nullable=False, server_default="kg"),
        sa.Column("description", sa.String(500), nullable=True),
        sa.Column("icon_url", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_commodities_name", "commodities", ["name"])
    op.create_index("ix_commodities_category", "commodities", ["category"])

    # ── markets ────────────────────────────────────────────────────────────
    op.create_table(
        "markets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("state", sa.String(100), nullable=False),
        sa.Column("district", sa.String(100), nullable=False),
        sa.Column("village", sa.String(100), nullable=True),
        sa.Column("postal_code", sa.String(10), nullable=True),
        sa.Column("latitude", sa.Numeric(10, 8), nullable=True),
        sa.Column("longitude", sa.Numeric(11, 8), nullable=True),
        sa.Column("market_type", sa.String(50), nullable=True),
        sa.Column("contact_phone", sa.String(20), nullable=True),
        sa.Column("contact_email", sa.String(255), nullable=True),
        sa.Column("website_url", sa.String(500), nullable=True),
        sa.Column("description", sa.String(1000), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.UniqueConstraint("name", "state", "district", name="uq_market_location"),
    )
    op.create_index("idx_market_state_district", "markets", ["state", "district"])
    op.create_index("idx_market_name", "markets", ["name"])
    op.create_index("idx_market_coordinates", "markets", ["latitude", "longitude"])

    # ── market_prices ──────────────────────────────────────────────────────
    op.create_table(
        "market_prices",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("market_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("markets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("commodity_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("commodities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("price_date", sa.Date(), nullable=False),
        sa.Column("min_price", sa.Numeric(10, 2), nullable=False),
        sa.Column("max_price", sa.Numeric(10, 2), nullable=False),
        sa.Column("modal_price", sa.Numeric(10, 2), nullable=True),
        sa.Column("quantity_traded", sa.Numeric(15, 2), nullable=True),
        sa.Column("source", sa.String(100), nullable=False),
        sa.Column("last_updated", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.UniqueConstraint("market_id", "commodity_id", "price_date", name="uq_market_commodity_date"),
    )
    op.create_index("idx_market_commodity_date", "market_prices", ["market_id", "commodity_id", "price_date"])

    # ── saved_markets ──────────────────────────────────────────────────────
    op.create_table(
        "saved_markets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("market_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("markets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("saved_at", sa.DateTime(), nullable=True),
        sa.UniqueConstraint("user_id", "market_id", name="uq_user_market"),
    )

    # ── saved_commodities ──────────────────────────────────────────────────
    op.create_table(
        "saved_commodities",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("commodity_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("commodities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("saved_at", sa.DateTime(), nullable=True),
        sa.UniqueConstraint("user_id", "commodity_id", name="uq_user_commodity"),
    )

    # ── buyers ─────────────────────────────────────────────────────────────
    op.create_table(
        "buyers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("buyer_type", sa.String(50), nullable=False),
        sa.Column("contact_name", sa.String(255), nullable=True),
        sa.Column("contact_phone", sa.String(20), nullable=True),
        sa.Column("contact_email", sa.String(255), nullable=True),
        sa.Column("state", sa.String(100), nullable=False),
        sa.Column("district", sa.String(100), nullable=False),
        sa.Column("city", sa.String(100), nullable=True),
        sa.Column("latitude", sa.Numeric(10, 8), nullable=True),
        sa.Column("longitude", sa.Numeric(11, 8), nullable=True),
        sa.Column("commodity_name", sa.String(100), nullable=False),
        sa.Column("min_quantity_quintal", sa.Numeric(10, 2), nullable=True),
        sa.Column("max_quantity_quintal", sa.Numeric(10, 2), nullable=True),
        sa.Column("quality_grade", sa.String(50), nullable=True),
        sa.Column("price_premium_pct", sa.Numeric(5, 2), nullable=True),
        sa.Column("payment_days", sa.Integer(), nullable=True),
        sa.Column("payment_method", sa.String(50), nullable=True),
        sa.Column("pickup_available", sa.Boolean(), nullable=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("source_type", sa.String(50), nullable=False, server_default="reference"),
        sa.Column("is_verified", sa.Boolean(), nullable=True),
        sa.Column("verification_status", sa.String(50), nullable=True),
        sa.Column("active_until", sa.Date(), nullable=True),
        sa.Column("years_active", sa.Integer(), nullable=True),
        sa.Column("rating", sa.Numeric(3, 1), nullable=True),
        sa.Column("payment_terms", sa.String(100), nullable=True),
        sa.Column("notes", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_index("idx_buyer_commodity", "buyers", ["commodity_name"])
    op.create_index("idx_buyer_state_district", "buyers", ["state", "district"])
    op.create_index("idx_buyer_source_type", "buyers", ["source_type"])

    # ── offers (created before farmer_lots due to FK use_alter) ───────────
    op.create_table(
        "offers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("lot_id", postgresql.UUID(as_uuid=True), nullable=False),  # FK added after farmer_lots
        sa.Column("buyer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("buyer_requirement_id", postgresql.UUID(as_uuid=True), nullable=True),  # FK added after buyer_requirements
        sa.Column("parent_offer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("offers.id", ondelete="CASCADE"), nullable=True),
        sa.Column("offered_price_per_quintal", sa.Numeric(10, 2), nullable=False),
        sa.Column("quantity_quintal", sa.Numeric(10, 2), nullable=False),
        sa.Column("payment_days", sa.Integer(), nullable=False),
        sa.Column("payment_method", sa.String(50), nullable=True),
        sa.Column("pickup_date", sa.Date(), nullable=True),
        sa.Column("quality_terms", sa.Text(), nullable=True),
        sa.Column("transport_responsibility", sa.String(50), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("accepted_at", sa.DateTime(), nullable=True),
        sa.Column("accepted_terms_snapshot", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_index("idx_offer_buyer", "offers", ["buyer_id"])
    op.create_index("idx_offer_status", "offers", ["status"])

    # ── farmer_lots ────────────────────────────────────────────────────────
    op.create_table(
        "farmer_lots",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("farmer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("commodity_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("commodities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("quantity", sa.Numeric(10, 2), nullable=False),
        sa.Column("unit", sa.String(20), nullable=True),
        sa.Column("state", sa.String(100), nullable=False),
        sa.Column("district", sa.String(100), nullable=False),
        sa.Column("village", sa.String(100), nullable=True),
        sa.Column("latitude", sa.Numeric(10, 8), nullable=True),
        sa.Column("longitude", sa.Numeric(11, 8), nullable=True),
        sa.Column("quality_status", sa.String(50), nullable=True),
        sa.Column("quality_grade", sa.String(50), nullable=True),
        sa.Column("quality_notes", sa.Text(), nullable=True),
        sa.Column("available_from", sa.Date(), nullable=False),
        sa.Column("sell_by", sa.Date(), nullable=False),
        sa.Column("minimum_price", sa.Numeric(10, 2), nullable=True),
        sa.Column("max_payment_days", sa.Integer(), nullable=True),
        sa.Column("preferred_payment_method", sa.String(50), nullable=True),
        sa.Column("transport_preference", sa.String(50), nullable=True),
        sa.Column("max_transport_budget", sa.Numeric(10, 2), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="available"),
        sa.Column(
            "reserved_by_offer_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("offers.id", ondelete="SET NULL", name="fk_lot_reserved_offer", use_alter=True),
            nullable=True,
        ),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_index("idx_lot_farmer", "farmer_lots", ["farmer_id"])
    op.create_index("idx_lot_commodity", "farmer_lots", ["commodity_id"])
    op.create_index("idx_lot_status", "farmer_lots", ["status"])
    op.create_index("idx_lot_location", "farmer_lots", ["state", "district"])

    # Now add FK from offers.lot_id → farmer_lots.id
    op.create_foreign_key("fk_offer_lot", "offers", "farmer_lots", ["lot_id"], ["id"], ondelete="CASCADE")
    op.create_index("idx_offer_lot", "offers", ["lot_id"])

    # ── buyer_requirements ─────────────────────────────────────────────────
    op.create_table(
        "buyer_requirements",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("buyer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("buyers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("commodity_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("commodities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("minimum_quantity", sa.Numeric(10, 2), nullable=False),
        sa.Column("maximum_quantity", sa.Numeric(10, 2), nullable=True),
        sa.Column("required_grade", sa.String(50), nullable=True),
        sa.Column("offered_price", sa.Numeric(10, 2), nullable=False),
        sa.Column("payment_days", sa.Integer(), nullable=False),
        sa.Column("payment_method", sa.String(50), nullable=True),
        sa.Column("pickup_available", sa.Boolean(), nullable=True),
        sa.Column("pickup_location_state", sa.String(100), nullable=True),
        sa.Column("pickup_location_district", sa.String(100), nullable=True),
        sa.Column("transport_cost_total", sa.Numeric(12, 2), nullable=True),
        sa.Column("transport_cost_source", sa.String(50), nullable=True, server_default="configured_demo"),
        sa.Column("active_from", sa.Date(), nullable=False),
        sa.Column("active_until", sa.Date(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=True, server_default="true"),
        sa.Column("source_type", sa.String(50), nullable=False, server_default="reference"),
        sa.Column("verification_status", sa.String(50), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_index("idx_buyer_req_buyer", "buyer_requirements", ["buyer_id"])
    op.create_index("idx_buyer_req_commodity", "buyer_requirements", ["commodity_id"])
    op.create_index("idx_buyer_req_active", "buyer_requirements", ["is_active"])

    # Add FK from offers.buyer_requirement_id → buyer_requirements.id
    op.create_foreign_key("fk_offer_buyer_req", "offers", "buyer_requirements", ["buyer_requirement_id"], ["id"], ondelete="SET NULL")

    # ── opportunities ──────────────────────────────────────────────────────
    op.create_table(
        "opportunities",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("lot_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("farmer_lots.id", ondelete="CASCADE"), nullable=False),
        sa.Column("opportunity_type", sa.String(50), nullable=False),
        sa.Column("buyer_requirement_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("buyer_requirements.id", ondelete="CASCADE"), nullable=True),
        sa.Column("market_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("markets.id", ondelete="CASCADE"), nullable=True),
        sa.Column("feasibility_decision", sa.String(50), nullable=False),
        sa.Column("blocking_constraints", sa.Text(), nullable=True),
        sa.Column("opportunity_gap", sa.Text(), nullable=True),
        sa.Column("minimum_viable_change", sa.Text(), nullable=True),
        sa.Column("offered_price_per_unit", sa.Numeric(10, 2), nullable=True),
        sa.Column("estimated_net_realization", sa.Numeric(15, 2), nullable=True),
        sa.Column("source_type", sa.String(50), nullable=False),
        sa.Column("data_quality", sa.String(20), nullable=True),
        sa.Column("rank", sa.Integer(), nullable=True),
        sa.Column("confidence_score", sa.Numeric(5, 2), nullable=True),
        sa.Column("explanation", sa.Text(), nullable=True),
        sa.Column("applied_recovery", sa.Text(), nullable=True),
        sa.Column("title", sa.String(255), nullable=True),
        sa.Column("warnings", sa.Text(), nullable=True),
        sa.Column("analyzed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_index("idx_opportunity_lot", "opportunities", ["lot_id"])
    op.create_index("idx_opportunity_type", "opportunities", ["opportunity_type"])
    op.create_index("idx_opportunity_feasibility", "opportunities", ["feasibility_decision"])

    # ── aggregation_groups ─────────────────────────────────────────────────
    op.create_table(
        "aggregation_groups",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("commodity_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("commodities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("buyer_requirement_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("buyer_requirements.id", ondelete="CASCADE"), nullable=True),
        sa.Column("total_quantity", sa.Numeric(15, 2), nullable=False),
        sa.Column("member_count", sa.Integer(), nullable=False),
        sa.Column("quality_grade", sa.String(50), nullable=True),
        sa.Column("state", sa.String(100), nullable=True),
        sa.Column("district", sa.String(100), nullable=True),
        sa.Column("earliest_available", sa.Date(), nullable=True),
        sa.Column("latest_sell_by", sa.Date(), nullable=True),
        sa.Column("status", sa.String(20), nullable=True, server_default="forming"),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_index("idx_agg_commodity", "aggregation_groups", ["commodity_id"])
    op.create_index("idx_agg_status", "aggregation_groups", ["status"])

    # ── aggregation_members ────────────────────────────────────────────────
    op.create_table(
        "aggregation_members",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("group_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("aggregation_groups.id", ondelete="CASCADE"), nullable=False),
        sa.Column("lot_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("farmer_lots.id", ondelete="CASCADE"), nullable=False),
        sa.Column("committed_quantity", sa.Numeric(10, 2), nullable=False),
        sa.Column("joined_at", sa.DateTime(), nullable=True),
        sa.UniqueConstraint("group_id", "lot_id", name="uq_group_lot"),
    )
    op.create_index("idx_agg_member_group", "aggregation_members", ["group_id"])
    op.create_index("idx_agg_member_lot", "aggregation_members", ["lot_id"])

    # ── transactions ───────────────────────────────────────────────────────
    op.create_table(
        "transactions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("offer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("offers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("lot_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("farmer_lots.id", ondelete="CASCADE"), nullable=False),
        sa.Column("farmer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("buyer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("agreed_price_per_quintal", sa.Numeric(10, 2), nullable=False),
        sa.Column("agreed_quantity", sa.Numeric(10, 2), nullable=False),
        sa.Column("agreed_payment_days", sa.Integer(), nullable=False),
        sa.Column("actual_quantity_delivered", sa.Numeric(10, 2), nullable=True),
        sa.Column("actual_quality_grade", sa.String(50), nullable=True),
        sa.Column("delivery_date", sa.Date(), nullable=True),
        sa.Column("delivery_location", sa.String(255), nullable=True),
        sa.Column("payment_status", sa.String(50), nullable=True, server_default="payment_pending"),
        sa.Column("payment_due_date", sa.Date(), nullable=True),
        sa.Column("payment_reported_date", sa.Date(), nullable=True),
        sa.Column("payment_confirmed_date", sa.Date(), nullable=True),
        sa.Column("payment_amount", sa.Numeric(15, 2), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="accepted"),
        sa.Column("is_disputed", sa.Boolean(), nullable=True, server_default="false"),
        sa.Column("dispute_reason", sa.Text(), nullable=True),
        sa.Column("dispute_resolved_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_index("idx_transaction_offer", "transactions", ["offer_id"])
    op.create_index("idx_transaction_farmer", "transactions", ["farmer_id"])
    op.create_index("idx_transaction_buyer", "transactions", ["buyer_id"])
    op.create_index("idx_transaction_status", "transactions", ["status"])

    # ── transaction_events ─────────────────────────────────────────────────
    op.create_table(
        "transaction_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("transaction_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("transactions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("event_type", sa.String(50), nullable=False),
        sa.Column("event_data", sa.Text(), nullable=True),
        sa.Column("actor_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_index("idx_event_transaction", "transaction_events", ["transaction_id"])
    op.create_index("idx_event_type", "transaction_events", ["event_type"])

    # ── payments ───────────────────────────────────────────────────────────
    op.create_table(
        "payments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("transaction_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("transactions.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("payment_status", sa.String(50), nullable=False, server_default="agreed"),
        sa.Column("payment_method", sa.String(50), nullable=True),
        sa.Column("payment_amount", sa.Numeric(15, 2), nullable=False),
        sa.Column("payment_due_date", sa.Date(), nullable=False),
        sa.Column("buyer_reported_paid_at", sa.DateTime(), nullable=True),
        sa.Column("buyer_payment_reference", sa.String(255), nullable=True),
        sa.Column("farmer_confirmed_at", sa.DateTime(), nullable=True),
        sa.Column("is_protected", sa.Boolean(), nullable=True, server_default="false"),
        sa.Column("protection_provider", sa.String(100), nullable=True),
        sa.Column("is_disputed", sa.Boolean(), nullable=True, server_default="false"),
        sa.Column("dispute_details", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_index("idx_payment_status", "payments", ["payment_status"])

    # ── reviews ────────────────────────────────────────────────────────────
    op.create_table(
        "reviews",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("transaction_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("transactions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("reviewer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("reviewee_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("overall_rating", sa.Integer(), nullable=False),
        sa.Column("payment_reliability", sa.Integer(), nullable=True),
        sa.Column("pickup_reliability", sa.Integer(), nullable=True),
        sa.Column("communication_rating", sa.Integer(), nullable=True),
        sa.Column("fair_negotiation_rating", sa.Integer(), nullable=True),
        sa.Column("quantity_accuracy", sa.Integer(), nullable=True),
        sa.Column("quality_accuracy", sa.Integer(), nullable=True),
        sa.Column("review_text", sa.Text(), nullable=True),
        sa.Column("is_verified_transaction", sa.Boolean(), nullable=True, server_default="true"),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.UniqueConstraint("transaction_id", "reviewer_id", name="uq_transaction_reviewer"),
    )
    op.create_index("idx_review_transaction", "reviews", ["transaction_id"])
    op.create_index("idx_review_reviewee", "reviews", ["reviewee_id"])


def downgrade() -> None:
    # Drop in reverse dependency order
    op.drop_table("reviews")
    op.drop_table("payments")
    op.drop_table("transaction_events")
    op.drop_table("transactions")
    op.drop_table("aggregation_members")
    op.drop_table("aggregation_groups")
    op.drop_table("opportunities")
    op.drop_constraint("fk_offer_buyer_req", "offers", type_="foreignkey")
    op.drop_table("buyer_requirements")
    op.drop_constraint("fk_offer_lot", "offers", type_="foreignkey")
    op.drop_table("farmer_lots")
    op.drop_table("offers")
    op.drop_table("buyers")
    op.drop_table("saved_commodities")
    op.drop_table("saved_markets")
    op.drop_table("market_prices")
    op.drop_table("markets")
    op.drop_table("commodities")
    op.drop_table("farmer_profiles")
    op.drop_table("users")
