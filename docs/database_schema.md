# Database Schema

## Overview

AgriMandi uses PostgreSQL with a normalized relational schema. This document describes all tables, columns, relationships, and indexing strategy.

## Entity Relationship Diagram

```
┌──────────────────┐
│     users        │ (authentication)
├──────────────────┤
│ id (PK)          │
│ email (UNIQUE)   │
│ password_hash    │
│ created_at       │
│ updated_at       │
└──────┬───────────┘
       │ 1:N
       │
    ┌──┴────────────┬──────────────────┬──────────────────┐
    │               │                  │                  │
    │               │                  │                  │
┌───▼──────────┐ ┌─▼──────────┐ ┌────▼──────┐ ┌────▼──────┐
│farmer_       │ │saved_      │ │saved_      │ │price_     │
│profiles      │ │markets     │ │commodities │ │alerts(v2) │
└──────────────┘ └────────────┘ └────────────┘ └───────────┘
       │                │              │             │
       │ 1:N            │ N:1          │ N:1         │ N:1
       │                │              │             │
    ┌──┴──────────────────────────────────────────────┘
    │
    ▼
┌──────────────────┐
│    markets       │ (APMC & local markets)
├──────────────────┤
│ id (PK)          │
│ name             │
│ state            │
│ district         │
│ village          │
│ latitude         │
│ longitude        │
│ created_at       │
└──────┬───────────┘
       │ 1:N
       │
       └──────────────────┬──────────────────────┐
                          │                      │
                    ┌─────▼──────────┐    ┌──────▼──────────┐
                    │ market_prices  │    │commodities      │
                    └────────────────┘    └─────────────────┘
                          ▲                       ▲
                          │ N:1                   │ N:1
                          └───────────┬───────────┘
                                      │
                                market_prices
                                (junction table
                                with pricing data)
```

## Tables

### 1. users

Stores user account information for authentication.

```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  INDEX idx_email (email),
  INDEX idx_created_at (created_at)
);
```

| Column | Type | Constraint | Description |
|--------|------|-----------|-------------|
| `id` | UUID | PRIMARY KEY | Unique user identifier |
| `email` | VARCHAR | NOT NULL, UNIQUE | User email (login credential) |
| `password_hash` | VARCHAR | NOT NULL | Bcrypt hashed password |
| `is_active` | BOOLEAN | DEFAULT TRUE | Soft delete flag |
| `created_at` | TIMESTAMP | DEFAULT NOW | Account creation time |
| `updated_at` | TIMESTAMP | DEFAULT NOW | Last profile update |

**Notes:**
- Passwords are **never stored as plain text**, only hashed with bcrypt
- Email is indexed for fast login lookups
- UUIDs provide better security than sequential IDs

---

### 2. farmer_profiles

Extends user account with farmer-specific information and location.

```sql
CREATE TABLE farmer_profiles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
  full_name VARCHAR(255) NOT NULL,
  phone VARCHAR(20),
  state VARCHAR(100) NOT NULL,
  district VARCHAR(100) NOT NULL,
  village VARCHAR(100),
  postal_code VARCHAR(10),
  latitude DECIMAL(10, 8),
  longitude DECIMAL(11, 8),
  bio TEXT,
  profile_image_url VARCHAR(500),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  INDEX idx_user_id (user_id),
  INDEX idx_state_district (state, district),
  INDEX idx_coordinates (latitude, longitude)
);
```

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Unique profile identifier |
| `user_id` | UUID | FK to users (1:1 relationship) |
| `full_name` | VARCHAR | Farmer's name |
| `phone` | VARCHAR | Contact number |
| `state` | VARCHAR | State (e.g., "Punjab", "Maharashtra") |
| `district` | VARCHAR | District within state |
| `village` | VARCHAR | Village/town name |
| `postal_code` | VARCHAR | Postal/PIN code |
| `latitude`, `longitude` | DECIMAL | GPS coordinates (future: PostGIS) |
| `bio` | TEXT | Farmer's bio/description |
| `profile_image_url` | VARCHAR | Profile picture URL |

**Notes:**
- One farmer profile per user (UNIQUE user_id)
- Location fields indexed for geographic queries
- Coordinates prepared for PostGIS upgrade

---

### 3. commodities

Master list of agricultural commodities.

```sql
CREATE TABLE commodities (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(100) NOT NULL UNIQUE,
  category VARCHAR(50), -- Cereals, Vegetables, Fruits, Spices, etc.
  unit VARCHAR(20) NOT NULL DEFAULT 'kg', -- kg, quintal, ton, liter, etc.
  description TEXT,
  icon_url VARCHAR(500),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  INDEX idx_name (name),
  INDEX idx_category (category)
);
```

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Unique commodity ID |
| `name` | VARCHAR | Commodity name (e.g., "Rice", "Tomato") |
| `category` | VARCHAR | Category (Cereal, Vegetable, Fruit, Spice) |
| `unit` | VARCHAR | Standard unit for pricing (kg, quintal, ton) |
| `description` | TEXT | Additional info |
| `icon_url` | VARCHAR | Icon for UI display |

**Notes:**
- Immutable reference data (rarely changes)
- Indexed by name for quick lookups
- Categories used for filtering/grouping

**Sample Data:**
```
Rice, Wheat, Maize (Cereals)
Tomato, Onion, Potato (Vegetables)
Mango, Apple, Banana (Fruits)
Turmeric, Chili, Coriander (Spices)
```

---

### 4. markets

Directory of agricultural markets (APMC, local markets).

```sql
CREATE TABLE markets (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  state VARCHAR(100) NOT NULL,
  district VARCHAR(100) NOT NULL,
  village VARCHAR(100),
  postal_code VARCHAR(10),
  latitude DECIMAL(10, 8),
  longitude DECIMAL(11, 8),
  market_type VARCHAR(50), -- APMC, Local, E-Commerce Hub, etc.
  contact_phone VARCHAR(20),
  contact_email VARCHAR(255),
  website_url VARCHAR(500),
  description TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  INDEX idx_state_district (state, district),
  INDEX idx_name (name),
  INDEX idx_coordinates (latitude, longitude),
  UNIQUE(name, state, district)
);
```

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Unique market ID |
| `name` | VARCHAR | Market name (e.g., "Bangalore Central Market") |
| `state` | VARCHAR | State name |
| `district` | VARCHAR | District name |
| `village` | VARCHAR | Village/city name |
| `postal_code` | VARCHAR | Postal code |
| `latitude`, `longitude` | DECIMAL | GPS coordinates |
| `market_type` | VARCHAR | Type (APMC, Local, Cooperative, etc.) |
| `contact_phone`, `contact_email` | VARCHAR | Contact information |
| `website_url` | VARCHAR | Market website (if available) |
| `description` | TEXT | Market info |

**Notes:**
- Compound index on (state, district, village) for location-based queries
- Unique constraint prevents duplicate markets
- Latitude/longitude for distance calculations

---

### 5. market_prices

Core pricing table—stores historical and current prices.

```sql
CREATE TABLE market_prices (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  market_id UUID NOT NULL REFERENCES markets(id) ON DELETE CASCADE,
  commodity_id UUID NOT NULL REFERENCES commodities(id) ON DELETE CASCADE,
  price_date DATE NOT NULL, -- Date of price (e.g., 2025-01-15)
  min_price DECIMAL(10, 2) NOT NULL, -- Minimum price in ₹ per unit
  max_price DECIMAL(10, 2) NOT NULL, -- Maximum price in ₹ per unit
  modal_price DECIMAL(10, 2), -- Representative/mode price
  quantity_traded DECIMAL(15, 2), -- Volume in units
  source VARCHAR(100) NOT NULL, -- "Government APMC", "Sample Data", etc.
  last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  INDEX idx_market_id (market_id),
  INDEX idx_commodity_id (commodity_id),
  INDEX idx_price_date (price_date),
  INDEX idx_market_commodity_date (market_id, commodity_id, price_date DESC),
  UNIQUE(market_id, commodity_id, price_date)
);
```

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Unique price record ID |
| `market_id` | UUID | FK to markets |
| `commodity_id` | UUID | FK to commodities |
| `price_date` | DATE | Date of the price data |
| `min_price` | DECIMAL | Minimum trading price (₹) |
| `max_price` | DECIMAL | Maximum trading price (₹) |
| `modal_price` | DECIMAL | Representative/mode price (₹) |
| `quantity_traded` | DECIMAL | Volume traded in units |
| `source` | VARCHAR | Data origin for transparency |
| `last_updated` | TIMESTAMP | When price was last updated |
| `created_at` | TIMESTAMP | When record was created |

**Notes:**
- **Time-series data:** Multiple records per market per day (one per commodity)
- **UNIQUE constraint:** One price per market-commodity-date combination
- **Compound index:** Optimizes date-range queries (`WHERE price_date BETWEEN ... AND ...`)
- **Source tracking:** Distinguishes real government data from sample data

**Indexes Explained:**
- `idx_market_commodity_date` enables efficient queries like:
  ```sql
  SELECT * FROM market_prices 
  WHERE market_id = ? AND commodity_id = ? 
  ORDER BY price_date DESC 
  LIMIT 30;  -- Last 30 days
  ```

---

### 6. saved_markets

User's bookmarked/saved markets.

```sql
CREATE TABLE saved_markets (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  market_id UUID NOT NULL REFERENCES markets(id) ON DELETE CASCADE,
  saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  INDEX idx_user_id (user_id),
  INDEX idx_market_id (market_id),
  UNIQUE(user_id, market_id)
);
```

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Record ID |
| `user_id` | UUID | FK to users |
| `market_id` | UUID | FK to markets |
| `saved_at` | TIMESTAMP | When the market was saved |

**Notes:**
- Prevent duplicates: User can't save same market twice
- Efficient user lookup: `SELECT * FROM saved_markets WHERE user_id = ?`

---

### 7. saved_commodities

User's bookmarked/watched commodities.

```sql
CREATE TABLE saved_commodities (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  commodity_id UUID NOT NULL REFERENCES commodities(id) ON DELETE CASCADE,
  saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  INDEX idx_user_id (user_id),
  INDEX idx_commodity_id (commodity_id),
  UNIQUE(user_id, commodity_id)
);
```

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Record ID |
| `user_id` | UUID | FK to users |
| `commodity_id` | UUID | FK to commodities |
| `saved_at` | TIMESTAMP | When the commodity was saved |

**Notes:**
- Similar to `saved_markets`, but for commodities
- Used for personalized price alerts (future feature)

---

### 8. price_alerts (Future)

For Phase 7+: Notify users when prices change significantly.

```sql
CREATE TABLE price_alerts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  market_id UUID NOT NULL REFERENCES markets(id) ON DELETE CASCADE,
  commodity_id UUID NOT NULL REFERENCES commodities(id) ON DELETE CASCADE,
  alert_type VARCHAR(50), -- "price_increase", "price_decrease", "threshold"
  threshold_price DECIMAL(10, 2),
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  INDEX idx_user_id (user_id),
  INDEX idx_active (is_active)
);
```

---

## Indexing Strategy

| Table | Index | Reason |
|-------|-------|--------|
| `users` | `email` | Fast login lookups |
| `farmer_profiles` | `state, district` | Geographic filtering |
| `farmer_profiles` | `coordinates` | Future PostGIS queries |
| `markets` | `state, district, village` | Location-based market search |
| `market_prices` | `market_commodity_date` | Core query optimization (most common) |
| `market_prices` | `price_date` | Historical range queries |
| `saved_markets` | `user_id` | Fetch user's saved markets |
| `saved_commodities` | `user_id` | Fetch user's saved commodities |

## Key Queries

### 1. Get Latest Prices for a Market
```sql
SELECT mp.*, c.name as commodity_name
FROM market_prices mp
JOIN commodities c ON mp.commodity_id = c.id
WHERE mp.market_id = 'market-uuid'
ORDER BY mp.price_date DESC
LIMIT 100;
```

### 2. Compare Commodity Prices Across Markets
```sql
SELECT m.name as market_name, mp.modal_price, mp.price_date
FROM market_prices mp
JOIN markets m ON mp.market_id = m.id
WHERE mp.commodity_id = 'commodity-uuid'
AND mp.price_date = CURRENT_DATE
ORDER BY mp.modal_price DESC;
```

### 3. Find Markets in a District
```sql
SELECT id, name, district, state
FROM markets
WHERE state = 'Punjab' AND district = 'Ludhiana'
ORDER BY name;
```

### 4. Historical Price Trend
```sql
SELECT price_date, modal_price
FROM market_prices
WHERE market_id = 'market-uuid'
AND commodity_id = 'commodity-uuid'
AND price_date BETWEEN DATE_SUB(CURRENT_DATE, INTERVAL 90 DAY) AND CURRENT_DATE
ORDER BY price_date ASC;
```

### 5. User's Saved Markets with Latest Prices
```sql
SELECT DISTINCT m.*, mp.modal_price, c.name as commodity_name
FROM saved_markets sm
JOIN markets m ON sm.market_id = m.id
JOIN market_prices mp ON m.id = mp.market_id
JOIN commodities c ON mp.commodity_id = c.id
WHERE sm.user_id = 'user-uuid'
AND mp.price_date = CURRENT_DATE;
```

## Future Enhancements

### PostGIS Integration
When geographic queries become complex:
```sql
ALTER TABLE markets ADD COLUMN location GEOGRAPHY(POINT, 4326);

-- Find markets within 50km of a point
SELECT * FROM markets
WHERE ST_DWithin(
  location,
  ST_GeogFromText('SRID=4326;POINT(longitude latitude)'),
  50000
);
```

### Partitioning by Date
For very large `market_prices` table (millions of rows):
```sql
CREATE TABLE market_prices_2025 PARTITION OF market_prices
FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');
```

### Full-Text Search
Enable searching commodities and markets:
```sql
ALTER TABLE commodities ADD COLUMN search_text TSVECTOR;
CREATE INDEX idx_commodity_search ON commodities USING gin(search_text);
```

## Constraints Summary

| Constraint | Purpose |
|-----------|---------|
| Foreign Keys | Maintain referential integrity |
| UNIQUE constraints | Prevent duplicate data (email, market names per location, prices per market-commodity-date) |
| NOT NULL | Ensure required fields always have values |
| DEFAULT values | Provide sensible defaults (CURRENT_TIMESTAMP, TRUE) |
| CHECK constraints | (Future) Validate price ranges (min_price <= modal_price <= max_price) |

## Migration Strategy

Using Alembic (SQLAlchemy migration tool):

1. Create schema with initial tables
2. Add sample data
3. Future changes tracked as migrations:
   ```bash
   alembic revision -m "Add price alerts table"
   ```

4. Run migrations:
   ```bash
   alembic upgrade head
   ```

This ensures:
- Version control of schema changes
- Reversible migrations (if needed)
- Clear audit trail
