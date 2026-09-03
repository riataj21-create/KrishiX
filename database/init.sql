-- This runs before schema.sql and sample_data.sql
-- The user and database are already created by the POSTGRES_USER/POSTGRES_DB env vars
-- This script adds any extra setup needed

-- Ensure uuid extension is available
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
