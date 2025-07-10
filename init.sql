-- HAL9001 Database Initialization Script
-- This script runs when the PostgreSQL container starts for the first time

-- Create the main database (already done by POSTGRES_DB env var)
-- CREATE DATABASE hal9001_db;

-- Connect to the database
\c hal9001_db;

-- Create user (already done by POSTGRES_USER env var)
-- CREATE USER hal_user WITH PASSWORD 'supersecret';

-- Grant all privileges on the database
GRANT ALL PRIVILEGES ON DATABASE hal9001_db TO hal_user;
GRANT ALL ON SCHEMA public TO hal_user;

-- Enable Row Level Security extension if needed
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- The application will create the actual tables (users, user_table_permissions)
-- when it starts up through the setup_database() function

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO hal_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO hal_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO hal_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO hal_user;

-- Verify the setup
SELECT version();
SELECT current_database();
SELECT current_user;
