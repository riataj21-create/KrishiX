-- ============================================================================
-- KrishiX Sample Data
-- All prices are in ₹ per QUINTAL (1 quintal = 100 kg)
-- Passwords: password123 (bcrypt hash below)
-- ============================================================================

-- ============================================================================
-- 1. USERS
-- ============================================================================
INSERT INTO users (id, email, password_hash, is_active) VALUES
('550e8400-e29b-41d4-a716-446655440000', 'farmer1@krishix.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5YmMxSUmmS46m', TRUE),
('550e8400-e29b-41d4-a716-446655440001', 'farmer2@krishix.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5YmMxSUmmS46m', TRUE),
('550e8400-e29b-41d4-a716-446655440002', 'farmer3@krishix.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5YmMxSUmmS46m', TRUE);

-- ============================================================================
-- 2. FARMER PROFILES
-- ============================================================================
INSERT INTO farmer_profiles (id, user_id, full_name, phone, state, district, village, postal_code, latitude, longitude) VALUES
('650e8400-e29b-41d4-a716-446655440000', '550e8400-e29b-41d4-a716-446655440000', 'Rajesh Kumar',  '9876543210', 'Punjab',      'Ludhiana', 'Samrala',  '141121', 30.8857, 75.9064),
('650e8400-e29b-41d4-a716-446655440001', '550e8400-e29b-41d4-a716-446655440001', 'Priya Sharma',  '9876543211', 'Maharashtra', 'Nashik',   'Igatpuri', '422403', 19.7515, 73.5628),
('650e8400-e29b-41d4-a716-446655440002', '550e8400-e29b-41d4-a716-446655440002', 'Harjeet Singh', '9876543212', 'Haryana',     'Hisar',    'Barwala',  '125033', 29.1897, 75.7330);

-- ============================================================================
-- 3. COMMODITIES  (unit = quintal)
-- ============================================================================
INSERT INTO commodities (id, name, category, unit, description) VALUES
-- Cereals
('750e8400-e29b-41d4-a716-446655440000', 'Rice',      'Cereals',    'quintal', 'White rice, medium grain'),
('750e8400-e29b-41d4-a716-446655440001', 'Wheat',     'Cereals',    'quintal', 'Whole wheat grain'),
('750e8400-e29b-41d4-a716-446655440002', 'Maize',     'Cereals',    'quintal', 'Corn grain'),
-- Vegetables
('750e8400-e29b-41d4-a716-446655440010', 'Tomato',    'Vegetables', 'quintal', 'Fresh tomatoes'),
('750e8400-e29b-41d4-a716-446655440011', 'Onion',     'Vegetables', 'quintal', 'Yellow onions'),
('750e8400-e29b-41d4-a716-446655440012', 'Potato',    'Vegetables', 'quintal', 'White potatoes'),
('750e8400-e29b-41d4-a716-446655440013', 'Carrot',    'Vegetables', 'quintal', 'Fresh carrots'),
-- Fruits
('750e8400-e29b-41d4-a716-446655440020', 'Mango',     'Fruits',     'quintal', 'Fresh mangoes'),
('750e8400-e29b-41d4-a716-446655440021', 'Banana',    'Fruits',     'quintal', 'Fresh bananas'),
('750e8400-e29b-41d4-a716-446655440022', 'Apple',     'Fruits',     'quintal', 'Fresh apples'),
-- Spices
('750e8400-e29b-41d4-a716-446655440030', 'Turmeric',  'Spices',     'quintal', 'Turmeric powder'),
('750e8400-e29b-41d4-a716-446655440031', 'Chili',     'Spices',     'quintal', 'Red chili powder'),
('750e8400-e29b-41d4-a716-446655440032', 'Coriander', 'Spices',     'quintal', 'Coriander seeds');

-- ============================================================================
-- 4. MARKETS
-- ============================================================================
INSERT INTO markets (id, name, state, district, village, market_type, contact_phone, website_url, latitude, longitude) VALUES
('850e8400-e29b-41d4-a716-446655440000', 'Ludhiana Central Market',   'Punjab',      'Ludhiana', 'Ludhiana City', 'APMC',  '0161-2500123',  'https://ludhiana-market.gov.in', 30.9010, 75.8573),
('850e8400-e29b-41d4-a716-446655440001', 'Samrala Market',            'Punjab',      'Ludhiana', 'Samrala',       'Local', '0161-2400456',  NULL,                             30.8857, 75.9064),
('850e8400-e29b-41d4-a716-446655440010', 'Nashik Agricultural Market','Maharashtra', 'Nashik',   'Nashik City',   'APMC',  '0253-2500789',  'https://nashik-apmc.gov.in',     19.9975, 73.7898),
('850e8400-e29b-41d4-a716-446655440011', 'Igatpuri Fruit Market',     'Maharashtra', 'Nashik',   'Igatpuri',      'Local', '0253-2401011',  NULL,                             19.7515, 73.5628),
('850e8400-e29b-41d4-a716-446655440020', 'Hisar Central Market',      'Haryana',     'Hisar',    'Hisar City',    'APMC',  '01662-2501213', 'https://hisar-market.gov.in',    29.1897, 75.7330),
('850e8400-e29b-41d4-a716-446655440021', 'Barwala Market',            'Haryana',     'Hisar',    'Barwala',       'Local', '01662-2401415', NULL,                             29.2012, 75.7201);

-- ============================================================================
-- 5. MARKET PRICES  — all values in ₹ per QUINTAL
-- ============================================================================

-- Ludhiana Central Market
INSERT INTO market_prices (id, market_id, commodity_id, price_date, min_price, max_price, modal_price, quantity_traded, source) VALUES
('950e8400-e29b-41d4-a716-446655440000', '850e8400-e29b-41d4-a716-446655440000', '750e8400-e29b-41d4-a716-446655440000', CURRENT_DATE, 4500.00, 5200.00, 4850.00, 1250, 'Sample Data'),  -- Rice
('950e8400-e29b-41d4-a716-446655440001', '850e8400-e29b-41d4-a716-446655440000', '750e8400-e29b-41d4-a716-446655440001', CURRENT_DATE, 2800.00, 3500.00, 3150.00,  890, 'Sample Data'),  -- Wheat
('950e8400-e29b-41d4-a716-446655440002', '850e8400-e29b-41d4-a716-446655440000', '750e8400-e29b-41d4-a716-446655440010', CURRENT_DATE, 2000.00, 2800.00, 2400.00,  560, 'Sample Data'),  -- Tomato
('950e8400-e29b-41d4-a716-446655440003', '850e8400-e29b-41d4-a716-446655440000', '750e8400-e29b-41d4-a716-446655440011', CURRENT_DATE, 3500.00, 4500.00, 4000.00,  720, 'Sample Data'),  -- Onion
('950e8400-e29b-41d4-a716-446655440004', '850e8400-e29b-41d4-a716-446655440000', '750e8400-e29b-41d4-a716-446655440012', CURRENT_DATE, 2500.00, 3200.00, 2850.00,  450, 'Sample Data');  -- Potato

-- Samrala Market
INSERT INTO market_prices (id, market_id, commodity_id, price_date, min_price, max_price, modal_price, quantity_traded, source) VALUES
('950e8400-e29b-41d4-a716-446655440010', '850e8400-e29b-41d4-a716-446655440001', '750e8400-e29b-41d4-a716-446655440000', CURRENT_DATE, 4600.00, 5300.00, 4950.00,  890, 'Sample Data'),  -- Rice
('950e8400-e29b-41d4-a716-446655440011', '850e8400-e29b-41d4-a716-446655440001', '750e8400-e29b-41d4-a716-446655440001', CURRENT_DATE, 2900.00, 3600.00, 3250.00,  670, 'Sample Data'),  -- Wheat
('950e8400-e29b-41d4-a716-446655440012', '850e8400-e29b-41d4-a716-446655440001', '750e8400-e29b-41d4-a716-446655440010', CURRENT_DATE, 2200.00, 3000.00, 2600.00,  420, 'Sample Data');  -- Tomato

-- Nashik Agricultural Market
INSERT INTO market_prices (id, market_id, commodity_id, price_date, min_price, max_price, modal_price, quantity_traded, source) VALUES
('950e8400-e29b-41d4-a716-446655440020', '850e8400-e29b-41d4-a716-446655440010', '750e8400-e29b-41d4-a716-446655440000', CURRENT_DATE, 4700.00, 5400.00, 5050.00, 1100, 'Sample Data'),  -- Rice
('950e8400-e29b-41d4-a716-446655440021', '850e8400-e29b-41d4-a716-446655440010', '750e8400-e29b-41d4-a716-446655440010', CURRENT_DATE, 1800.00, 2600.00, 2200.00,  680, 'Sample Data'),  -- Tomato
('950e8400-e29b-41d4-a716-446655440022', '850e8400-e29b-41d4-a716-446655440010', '750e8400-e29b-41d4-a716-446655440020', CURRENT_DATE, 6000.00, 8000.00, 7000.00,  340, 'Sample Data');  -- Mango

-- Igatpuri Fruit Market
INSERT INTO market_prices (id, market_id, commodity_id, price_date, min_price, max_price, modal_price, quantity_traded, source) VALUES
('950e8400-e29b-41d4-a716-446655440030', '850e8400-e29b-41d4-a716-446655440011', '750e8400-e29b-41d4-a716-446655440020', CURRENT_DATE, 5800.00, 7800.00, 6800.00,  520, 'Sample Data'),  -- Mango
('950e8400-e29b-41d4-a716-446655440031', '850e8400-e29b-41d4-a716-446655440011', '750e8400-e29b-41d4-a716-446655440021', CURRENT_DATE, 3500.00, 4500.00, 4000.00,  780, 'Sample Data');  -- Banana

-- Hisar Central Market
INSERT INTO market_prices (id, market_id, commodity_id, price_date, min_price, max_price, modal_price, quantity_traded, source) VALUES
('950e8400-e29b-41d4-a716-446655440040', '850e8400-e29b-41d4-a716-446655440020', '750e8400-e29b-41d4-a716-446655440002', CURRENT_DATE, 2200.00, 2800.00, 2500.00,  650, 'Sample Data'),  -- Maize
('950e8400-e29b-41d4-a716-446655440041', '850e8400-e29b-41d4-a716-446655440020', '750e8400-e29b-41d4-a716-446655440011', CURRENT_DATE, 3600.00, 4600.00, 4100.00,  890, 'Sample Data');  -- Onion

-- Barwala Market
INSERT INTO market_prices (id, market_id, commodity_id, price_date, min_price, max_price, modal_price, quantity_traded, source) VALUES
('950e8400-e29b-41d4-a716-446655440050', '850e8400-e29b-41d4-a716-446655440021', '750e8400-e29b-41d4-a716-446655440002', CURRENT_DATE, 2300.00, 2900.00, 2600.00,  450, 'Sample Data');  -- Maize

-- ============================================================================
-- 6. HISTORICAL DATA — last 7 days at Ludhiana Central (₹/quintal)
-- ============================================================================
INSERT INTO market_prices (market_id, commodity_id, price_date, min_price, max_price, modal_price, quantity_traded, source) VALUES
-- Rice history
('850e8400-e29b-41d4-a716-446655440000', '750e8400-e29b-41d4-a716-446655440000', CURRENT_DATE - INTERVAL '1 day', 4450.00, 5150.00, 4800.00, 1200, 'Sample Data'),
('850e8400-e29b-41d4-a716-446655440000', '750e8400-e29b-41d4-a716-446655440000', CURRENT_DATE - INTERVAL '2 day', 4400.00, 5100.00, 4750.00, 1180, 'Sample Data'),
('850e8400-e29b-41d4-a716-446655440000', '750e8400-e29b-41d4-a716-446655440000', CURRENT_DATE - INTERVAL '3 day', 4350.00, 5050.00, 4700.00, 1150, 'Sample Data'),
('850e8400-e29b-41d4-a716-446655440000', '750e8400-e29b-41d4-a716-446655440000', CURRENT_DATE - INTERVAL '4 day', 4300.00, 5000.00, 4650.00, 1100, 'Sample Data'),
('850e8400-e29b-41d4-a716-446655440000', '750e8400-e29b-41d4-a716-446655440000', CURRENT_DATE - INTERVAL '5 day', 4250.00, 4950.00, 4600.00, 1050, 'Sample Data'),
('850e8400-e29b-41d4-a716-446655440000', '750e8400-e29b-41d4-a716-446655440000', CURRENT_DATE - INTERVAL '6 day', 4200.00, 4900.00, 4550.00, 1000, 'Sample Data'),
('850e8400-e29b-41d4-a716-446655440000', '750e8400-e29b-41d4-a716-446655440000', CURRENT_DATE - INTERVAL '7 day', 4150.00, 4850.00, 4500.00,  950, 'Sample Data'),
-- Tomato history
('850e8400-e29b-41d4-a716-446655440000', '750e8400-e29b-41d4-a716-446655440010', CURRENT_DATE - INTERVAL '1 day', 1950.00, 2750.00, 2350.00, 550, 'Sample Data'),
('850e8400-e29b-41d4-a716-446655440000', '750e8400-e29b-41d4-a716-446655440010', CURRENT_DATE - INTERVAL '2 day', 1900.00, 2700.00, 2300.00, 540, 'Sample Data'),
('850e8400-e29b-41d4-a716-446655440000', '750e8400-e29b-41d4-a716-446655440010', CURRENT_DATE - INTERVAL '3 day', 1850.00, 2650.00, 2250.00, 520, 'Sample Data'),
('850e8400-e29b-41d4-a716-446655440000', '750e8400-e29b-41d4-a716-446655440010', CURRENT_DATE - INTERVAL '4 day', 1800.00, 2600.00, 2200.00, 500, 'Sample Data'),
('850e8400-e29b-41d4-a716-446655440000', '750e8400-e29b-41d4-a716-446655440010', CURRENT_DATE - INTERVAL '5 day', 2100.00, 2900.00, 2500.00, 480, 'Sample Data'),
('850e8400-e29b-41d4-a716-446655440000', '750e8400-e29b-41d4-a716-446655440010', CURRENT_DATE - INTERVAL '6 day', 2200.00, 3000.00, 2600.00, 460, 'Sample Data'),
('850e8400-e29b-41d4-a716-446655440000', '750e8400-e29b-41d4-a716-446655440010', CURRENT_DATE - INTERVAL '7 day', 2300.00, 3100.00, 2700.00, 440, 'Sample Data');

-- ============================================================================
-- 7. SAVED PREFERENCES
-- ============================================================================
INSERT INTO saved_markets (user_id, market_id) VALUES
('550e8400-e29b-41d4-a716-446655440000', '850e8400-e29b-41d4-a716-446655440000'),
('550e8400-e29b-41d4-a716-446655440000', '850e8400-e29b-41d4-a716-446655440001'),
('550e8400-e29b-41d4-a716-446655440001', '850e8400-e29b-41d4-a716-446655440010'),
('550e8400-e29b-41d4-a716-446655440002', '850e8400-e29b-41d4-a716-446655440020');

INSERT INTO saved_commodities (user_id, commodity_id) VALUES
('550e8400-e29b-41d4-a716-446655440000', '750e8400-e29b-41d4-a716-446655440000'),  -- Rice
('550e8400-e29b-41d4-a716-446655440000', '750e8400-e29b-41d4-a716-446655440010'),  -- Tomato
('550e8400-e29b-41d4-a716-446655440001', '750e8400-e29b-41d4-a716-446655440020'),  -- Mango
('550e8400-e29b-41d4-a716-446655440002', '750e8400-e29b-41d4-a716-446655440002');  -- Maize

-- ============================================================================
-- All prices are per quintal. Reset DB with: docker-compose down -v && docker-compose up
-- ============================================================================

-- ============================================================================
-- 8. DEMO BUYERS
-- These are seed/demo accounts for hackathon demonstration purposes.
-- They are NOT real registered marketplace users.
-- data_status = DEMO
-- ============================================================================
INSERT INTO buyers (
    id, name, buyer_type, contact_name, contact_phone, contact_email,
    state, district, city, latitude, longitude,
    commodity_name, min_quantity_quintal, max_quantity_quintal,
    quality_grade, price_premium_pct, is_verified, years_active,
    rating, payment_terms, notes
) VALUES
(
    'a10e8400-e29b-41d4-a716-446655440001',
    'Punjab Grain Traders Pvt Ltd', 'Trader',
    'Amarjit Singh', '9814100001', 'trade@punjabgrain.com',
    'Punjab', 'Ludhiana', 'Ludhiana',
    30.9010, 75.8573,
    'Wheat', 50.00, 500.00, 'Grade A', 2.50,
    TRUE, 12, 4.5, 'Immediate',
    'DEMO buyer. Buys wheat directly from farmers. Immediate cash payment at farm gate.'
),
(
    'a10e8400-e29b-41d4-a716-446655440002',
    'Nashik Fresh Exports', 'Exporter',
    'Ramesh Patil', '9823200002', 'exports@nashikfresh.com',
    'Maharashtra', 'Nashik', 'Nashik',
    19.9975, 73.7898,
    'Tomato', 100.00, 2000.00, 'Grade A', 15.00,
    TRUE, 8, 4.2, '7 days',
    'DEMO buyer. Exports Grade A tomatoes to Gulf markets. Pays 15% above local mandi modal price.'
),
(
    'a10e8400-e29b-41d4-a716-446655440003',
    'Haryana FPO Collective', 'FPO',
    'Suresh Kumar', '9812300003', 'fpo@haryanafpo.org',
    'Haryana', 'Hisar', 'Hisar',
    29.1897, 75.7330,
    'Maize', 20.00, 300.00, 'Any', 0.00,
    TRUE, 5, 4.0, '14 days',
    'DEMO buyer. Farmer Producer Organisation aggregating maize from smallholders in Hisar district.'
),
(
    'a10e8400-e29b-41d4-a716-446655440004',
    'Ludhiana Rice Mills', 'Processor',
    'Gurpreet Kaur', '9815400004', 'procurement@ludhianarice.com',
    'Punjab', 'Ludhiana', 'Ludhiana',
    30.8700, 75.8400,
    'Rice', 200.00, 5000.00, 'Grade B', 0.00,
    TRUE, 20, 4.7, 'Immediate',
    'DEMO buyer. Large rice mill buying paddy/rice for processing. Volume buyer — immediate payment.'
),
(
    'a10e8400-e29b-41d4-a716-446655440005',
    'Mumbai Onion Wholesalers', 'Trader',
    'Vijay Mehta', '9820500005', 'onions@mumbaiwhale.com',
    'Maharashtra', 'Nashik', 'Nashik',
    19.8762, 75.0234,
    'Onion', 50.00, 1000.00, 'Any', 5.00,
    FALSE, 3, 3.8, '7 days',
    'DEMO buyer. Wholesaler distributing onions to Mumbai retail markets.'
),
(
    'a10e8400-e29b-41d4-a716-446655440006',
    'Hisar Cold Storage & Trading', 'Trader',
    'Rakesh Sharma', '9812600006', 'cold@hisarstore.com',
    'Haryana', 'Hisar', 'Hisar',
    29.2100, 75.7500,
    'Potato', 30.00, 400.00, 'Grade A', 3.00,
    FALSE, 7, 4.1, 'Immediate',
    'DEMO buyer. Has cold storage facility. Buys potatoes for storage and off-season resale.'
),
(
    'a10e8400-e29b-41d4-a716-446655440007',
    'Maharashtra Mango Exporters Co', 'Exporter',
    'Prashant Desai', '9823700007', 'mango@mahaexport.com',
    'Maharashtra', 'Nashik', 'Igatpuri',
    19.7515, 73.5628,
    'Mango', 50.00, 800.00, 'Grade A', 20.00,
    TRUE, 15, 4.6, '7 days',
    'DEMO buyer. Exports Alphonso and Kesar mangoes. Pays 20% premium for export-quality Grade A produce.'
),
(
    'a10e8400-e29b-41d4-a716-446655440008',
    'North India Spice Processors', 'Processor',
    'Anita Gupta', '9810800008', 'spices@northindiaspice.com',
    'Haryana', 'Hisar', 'Hisar',
    29.1500, 75.8000,
    'Turmeric', 10.00, 200.00, 'Any', 0.00,
    FALSE, 4, 3.9, '14 days',
    'DEMO buyer. Processes turmeric and chili into packaged spice products.'
);

-- ============================================================================
-- 9. UPDATE SEED USERS WITH ROLES
-- ============================================================================
UPDATE users SET role = 'farmer' WHERE id IN (
    '550e8400-e29b-41d4-a716-446655440000',
    '550e8400-e29b-41d4-a716-446655440001',
    '550e8400-e29b-41d4-a716-446655440002'
);
