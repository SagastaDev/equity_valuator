# Dummy Data Providers

This directory contains test data and utilities for field mapping functionality development. **All files in this directory should be removed before production deployment.**

## Files

### MockupData01.json
Sample financial data representing a fictional company "Acme Technologies Ltd." with two years of financial statements:
- Income Statement fields
- Balance Sheet fields  
- Cash Flow Statement fields
- Market data

### init_dummy_provider.py
Python script to load the mockup data into the database as a test provider for development purposes.

## Usage

### Initialize Dummy Data

```bash
# With SQLite (development)
python DummyProviders/init_dummy_provider.py

# With PostgreSQL (Docker)
python DummyProviders/init_dummy_provider.py "postgresql://postgres:postgres@localhost:5433/equity_valuation"
```

### What Gets Created

1. **Test Provider**: "FinStack Global (Test)" with clear marking as test data
2. **Test Company**: "Acme Technologies Ltd." (ACM) in Technology industry
3. **Raw Data Entries**: All financial fields from MockupData01.json as raw data entries
4. **Field Examples**: Available raw field names for mapping interface testing

### Available Raw Field Names

The script creates raw data entries with field names like:
- **Income Statement**: Total_Revenue, Cost_Of_Revenue, Net_Income, etc.
- **Balance Sheet**: Cash, Total_Assets, Total_Liab, etc.
- **Cash Flow**: Cash_From_Operating, Capital_Expenditures, etc.

## Integration with Field Mapping UI

The dummy provider enables testing of:
- Canonical field to raw field mapping
- Provider-specific field name suggestions
- Mapping backup/export functionality
- Field transformation expressions

## Cleanup for Production

To remove all test data before production:

1. Delete this entire `DummyProviders/` directory
2. Remove dummy provider from database:
   ```sql
   DELETE FROM raw_data_entries WHERE provider_id IN (SELECT id FROM providers WHERE name LIKE '%Test%');
   DELETE FROM mapped_fields WHERE provider_id IN (SELECT id FROM providers WHERE name LIKE '%Test%');
   DELETE FROM providers WHERE name LIKE '%Test%';
   DELETE FROM companies WHERE symbol = 'ACM';
   ```

## Notes

- The dummy provider is clearly marked with "(Test)" suffix and warning descriptions
- All test data uses fictional company information
- Raw field names are based on common financial data provider formats
- Script is idempotent - safe to run multiple times