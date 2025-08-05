-- Initial database setup script

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Note: Canonical fields are now loaded from canonical_fields.json 
-- Run: python init_canonical_fields.py to populate the canonical_fields table
-- This provides a more comprehensive set of financial statement items based on your legacy analysis

-- Insert default provider
INSERT INTO providers (name) VALUES ('Yahoo Finance')
ON CONFLICT (name) DO NOTHING;

-- Insert default industries
INSERT INTO industries (code, name, description) VALUES
('TECH', 'Technology', 'Technology companies'),
('FINANCE', 'Financial Services', 'Banks, insurance, and financial services'),
('HEALTHCARE', 'Healthcare', 'Healthcare and pharmaceutical companies'),
('ENERGY', 'Energy', 'Oil, gas, and renewable energy companies'),
('CONSUMER', 'Consumer Goods', 'Consumer products and retail'),
('INDUSTRIAL', 'Industrial', 'Manufacturing and industrial companies'),
('UTILITIES', 'Utilities', 'Electric, gas, and water utilities'),
('REAL_ESTATE', 'Real Estate', 'Real estate investment and development'),
('MATERIALS', 'Materials', 'Mining, chemicals, and raw materials'),
('TELECOM', 'Telecommunications', 'Telecommunications and media')
ON CONFLICT (code) DO NOTHING;