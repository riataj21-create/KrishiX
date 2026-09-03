-- ============================================================================
-- KrishiX Database Schema
-- PostgreSQL 15+
-- ============================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- 1. USERS
-- ============================================================================
CREATE TABLE users (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email         VARCHAR(255) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  is_active     BOOLEAN DEFAULT TRUE,
  created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email      ON users (email);
CREATE INDEX idx_users_created_at ON users (created_at);

-- ============================================================================
-- 2. FARMER PROFILES
-- ============================================================================
CREATE TABLE farmer_profiles (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id           UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
  full_name         VARCHAR(255) NOT NULL,
  phone             VARCHAR(20),
  state             VARCHAR(100) NOT NULL,
  district          VARCHAR(100) NOT NULL,
  village           VARCHAR(100),
  postal_code       VARCHAR(10),
  latitude          DECIMAL(10, 8),
  longitude         DECIMAL(11, 8),
  bio               TEXT,
  profile_image_url VARCHAR(500),
  created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_farmer_profiles_user_id        ON farmer_profiles (user_id);
CREATE INDEX idx_farmer_profiles_state_district ON farmer_profiles (state, district);
CREATE INDEX idx_farmer_profiles_coordinates    ON farmer_profiles (latitude, longitude);

-- ============================================================================
-- 3. COMMODITIES
-- ============================================================================
CREATE TABLE commodities (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name        VARCHAR(100) NOT NULL UNIQUE,
  category    VARCHAR(50),
  unit        VARCHAR(20) NOT NULL DEFAULT 'quintal',
  description TEXT,
  icon_url    VARCHAR(500),
  created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_commodities_name     ON commodities (name);
CREATE INDEX idx_commodities_category ON commodities (category);

-- ============================================================================
-- 4. MARKETS
-- ============================================================================
CREATE TABLE markets (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name          VARCHAR(255) NOT NULL,
  state         VARCHAR(100) NOT NULL,
  district      VARCHAR(100) NOT NULL,
  village       VARCHAR(100),
  postal_code   VARCHAR(10),
  latitude      DECIMAL(10, 8),
  longitude     DECIMAL(11, 8),
  market_type   VARCHAR(50),
  contact_phone VARCHAR(20),
  contact_email VARCHAR(255),
  website_url   VARCHAR(500),
  description   TEXT,
  created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE (name, state, district)
);

CREATE INDEX idx_markets_state_district ON markets (state, district);
CREATE INDEX idx_markets_name           ON markets (name);
CREATE INDEX idx_markets_coordinates    ON markets (latitude, longitude);

-- ============================================================================
-- 5. MARKET PRICES
-- ============================================================================
CREATE TABLE market_prices (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  market_id        UUID NOT NULL REFERENCES markets(id) ON DELETE CASCADE,
  commodity_id     UUID NOT NULL REFERENCES commodities(id) ON DELETE CASCADE,
  price_date       DATE NOT NULL,
  min_price        DECIMAL(10, 2) NOT NULL,
  max_price        DECIMAL(10, 2) NOT NULL,
  modal_price      DECIMAL(10, 2),
  quantity_traded  DECIMAL(15, 2),
  source           VARCHAR(100) NOT NULL,
  last_updated     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE (market_id, commodity_id, price_date)
);

CREATE INDEX idx_market_prices_market_id            ON market_prices (market_id);
CREATE INDEX idx_market_prices_commodity_id         ON market_prices (commodity_id);
CREATE INDEX idx_market_prices_price_date           ON market_prices (price_date);
CREATE INDEX idx_market_prices_market_commodity_date ON market_prices (market_id, commodity_id, price_date DESC);

-- ============================================================================
-- 6. SAVED MARKETS
-- ============================================================================
CREATE TABLE saved_markets (
  id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id    UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  market_id  UUID NOT NULL REFERENCES markets(id) ON DELETE CASCADE,
  saved_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE (user_id, market_id)
);

CREATE INDEX idx_saved_markets_user_id   ON saved_markets (user_id);
CREATE INDEX idx_saved_markets_market_id ON saved_markets (market_id);

-- ============================================================================
-- 7. SAVED COMMODITIES
-- ============================================================================
CREATE TABLE saved_commodities (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id      UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  commodity_id UUID NOT NULL REFERENCES commodities(id) ON DELETE CASCADE,
  saved_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE (user_id, commodity_id)
);

CREATE INDEX idx_saved_commodities_user_id      ON saved_commodities (user_id);
CREATE INDEX idx_saved_commodities_commodity_id ON saved_commodities (commodity_id);

-- ============================================================================
-- CONVENIENCE VIEW: latest prices
-- ============================================================================
CREATE VIEW latest_prices AS
SELECT
  mp.id,
  m.id          AS market_id,
  m.name        AS market_name,
  m.state,
  m.district,
  c.id          AS commodity_id,
  c.name        AS commodity_name,
  mp.price_date,
  mp.min_price,
  mp.max_price,
  mp.modal_price,
  mp.source
FROM market_prices mp
JOIN markets     m ON mp.market_id     = m.id
JOIN commodities c ON mp.commodity_id  = c.id
WHERE mp.price_date = (SELECT MAX(price_date) FROM market_prices);
