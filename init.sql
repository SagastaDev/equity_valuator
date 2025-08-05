-- Initial database setup script

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Insert default canonical fields
INSERT INTO canonical_fields (code, name, display_name, type, category, is_computed) VALUES
(1001, 'total_revenue', 'Total Revenue', 'currency', 'fundamental', false),
(1002, 'net_income', 'Net Income', 'currency', 'fundamental', false),
(1003, 'total_assets', 'Total Assets', 'currency', 'fundamental', false),
(1004, 'total_liabilities', 'Total Liabilities', 'currency', 'fundamental', false),
(1005, 'total_equity', 'Total Equity', 'currency', 'fundamental', false),
(1006, 'cash', 'Cash and Cash Equivalents', 'currency', 'fundamental', false),
(1007, 'long_term_debt', 'Long Term Debt', 'currency', 'fundamental', false),
(1008, 'current_assets', 'Current Assets', 'currency', 'fundamental', false),
(1009, 'current_liabilities', 'Current Liabilities', 'currency', 'fundamental', false),
(1010, 'operating_cash_flow', 'Operating Cash Flow', 'currency', 'fundamental', false),
(2001, 'market_cap', 'Market Capitalization', 'currency', 'market', false),
(2002, 'enterprise_value', 'Enterprise Value', 'currency', 'market', false),
(2003, 'share_price', 'Share Price', 'currency', 'market', false),
(3001, 'pe_ratio', 'Price to Earnings Ratio', 'ratio', 'ratio', true),
(3002, 'ev_ebitda', 'EV/EBITDA', 'ratio', 'ratio', true),
(3003, 'debt_to_equity', 'Debt to Equity Ratio', 'ratio', 'ratio', true),
(3004, 'current_ratio', 'Current Ratio', 'ratio', 'ratio', true),
(3005, 'return_on_equity', 'Return on Equity', 'percentage', 'ratio', true),
(3006, 'return_on_assets', 'Return on Assets', 'percentage', 'ratio', true)
ON CONFLICT (code) DO NOTHING;

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