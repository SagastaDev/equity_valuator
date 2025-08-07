-- Initial database setup script

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Note: Initial data (providers, industries, canonical fields) is now loaded 
-- via Python during FastAPI application startup for better error handling
-- and consistency with the application's ORM models.