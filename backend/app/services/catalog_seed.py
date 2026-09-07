"""Idempotent baseline commodity catalog for local and new installations."""

from uuid import UUID

from sqlalchemy.orm import Session

from app.models import Commodity


COMMODITIES = (
    ("750e8400-e29b-41d4-a716-446655440000", "Rice", "Cereals", "White rice, medium grain"),
    ("750e8400-e29b-41d4-a716-446655440001", "Wheat", "Cereals", "Whole wheat grain"),
    ("750e8400-e29b-41d4-a716-446655440002", "Maize", "Cereals", "Corn grain"),
    ("750e8400-e29b-41d4-a716-446655440010", "Tomato", "Vegetables", "Fresh tomatoes"),
    ("750e8400-e29b-41d4-a716-446655440011", "Onion", "Vegetables", "Yellow onions"),
    ("750e8400-e29b-41d4-a716-446655440012", "Potato", "Vegetables", "White potatoes"),
    ("750e8400-e29b-41d4-a716-446655440013", "Carrot", "Vegetables", "Fresh carrots"),
    ("750e8400-e29b-41d4-a716-446655440020", "Mango", "Fruits", "Fresh mangoes"),
    ("750e8400-e29b-41d4-a716-446655440021", "Banana", "Fruits", "Fresh bananas"),
    ("750e8400-e29b-41d4-a716-446655440022", "Apple", "Fruits", "Fresh apples"),
    ("750e8400-e29b-41d4-a716-446655440030", "Turmeric", "Spices", "Turmeric powder"),
    ("750e8400-e29b-41d4-a716-446655440031", "Chili", "Spices", "Red chili powder"),
    ("750e8400-e29b-41d4-a716-446655440032", "Coriander", "Spices", "Coriander seeds"),
)


def seed_catalog(db: Session) -> int:
    """Insert missing baseline commodities without changing existing records."""
    inserted = 0
    for raw_id, name, category, description in COMMODITIES:
        commodity = db.query(Commodity).filter(Commodity.name == name).first()
        if commodity:
            continue
        db.add(
            Commodity(
                id=UUID(raw_id),
                name=name,
                category=category,
                unit="quintal",
                description=description,
            )
        )
        inserted += 1
    if inserted:
        db.commit()
    return inserted
