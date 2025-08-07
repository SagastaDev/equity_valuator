# Dummy Data Providers

This directory contains test data and utilities for field mapping functionality development. **All files in this directory should be removed before production deployment.**

## 🚨 IMPORTANT: AUTOMATED INITIALIZATION SYSTEM 🚨

**AS OF 2024, THIS DIRECTORY IS NOW AUTOMATICALLY PROCESSED BY THE BACKEND ON STARTUP.**

The individual Python scripts in this directory are **LEGACY** and no longer used. The system has been simplified:

- **Initialization Location**: `backend/db/init_dummy_data.py` handles all dummy data setup
- **Automatic Execution**: Runs automatically when backend starts (Docker or local)
- **Environment Control**: Set `ENABLE_DUMMY_DATA=false` to disable in production
- **Docker Integration**: This directory is copied into the container during build

### For Future AI Maintainers

**CRITICAL DATABASE MODEL REQUIREMENTS** - These were discovered through debugging:

1. **RawDataEntry Model Requirements**:
   - Uses `fiscal_period` (Date), NOT `period` (String)
   - Uses `period_type` (PeriodType enum), NOT a string period
   - Uses `value` (JSONB) and `value_type` (ValueType enum), NOT `raw_field_value`
   - All fields are required - no nullable fields

2. **Company Model Requirements**:
   - `country` and `currency` fields are required (NOT NULL)
   - Uses UUID primary key, not integer
   - Must provide both country="US" and currency="USD" for test companies

3. **Provider Model**:
   - Only has `id` and `name` fields
   - No `description`, `api_endpoint`, or `api_key` fields exist

4. **MappedField Model**:
   - Uses `raw_field_name`, NOT `provider_field_name`  
   - Uses `canonical_id`, NOT `canonical_field_id`

**DO NOT** modify individual scripts in this directory. **DO** modify `backend/db/init_dummy_data.py` instead.

**DOCKERFILE REQUIREMENT**: DummyProviders directory must be copied into container:
```dockerfile
COPY DummyProviders/ ./DummyProviders/
```

## Files

### MockupData01.json
Sample financial data representing "Acme Technologies Ltd." from FinStack Global provider with ~100% canonical field coverage:
- Income Statement fields (standard naming)
- Balance Sheet fields (standard naming) 
- Cash Flow Statement fields (standard naming)
- Market data

### MockupData02.json
Sample financial data representing "TechCorp Industries Inc." from AlphaFinance Pro provider with ~60% canonical field coverage:
- Uses alternative field naming conventions (e.g., "revenues" vs "total_revenue")
- Simplified field structure to simulate partial data coverage
- Different market data field names

### MockupData03.json
Sample financial data representing "SoftwareDev Solutions Ltd." from MarketInsight Analytics provider with ~55% canonical field coverage:
- Uses nested JSON structure ("financials", "position", "cashflow")
- Different field naming patterns (e.g., "revenue_total", "cf_operating")
- Demonstrates complex data structure mapping scenarios

### MockupData04.json
Sample financial data representing "Innovation Dynamics Corp." from DataStream Financial provider with ~65% canonical field coverage:
- Uses deeply nested structure within "statements"
- Alternative naming conventions (e.g., "sales_net", "earnings_pretax")
- Tests hierarchical data mapping capabilities

### Initialization Scripts

#### Data Provider Scripts
- **init_dummy_provider.py**: Loads FinStack Global test data
- **init_dummy_provider02.py**: Loads AlphaFinance Pro test data  
- **init_dummy_provider03.py**: Loads MarketInsight Analytics test data
- **init_dummy_provider04.py**: Loads DataStream Financial test data
- **init_all_dummy_providers.py**: Master script to initialize all providers at once

#### Field Mapping Scripts
- **init_mappings_alphafin.py**: Creates field mappings for AlphaFinance Pro
- **init_mappings_marketinsight.py**: Creates field mappings for MarketInsight Analytics
- **init_mappings_datastream.py**: Creates field mappings for DataStream Financial
- **init_all_mappings.py**: Master script to create all field mappings at once

## Usage

### ✅ CURRENT SYSTEM (Automated)

**No manual initialization needed!** The system automatically initializes dummy data when the backend starts.

```bash
# Development - dummy data loads automatically
docker-compose up backend db

# Production - disable dummy data
ENABLE_DUMMY_DATA=false docker-compose up backend db
```

### ❌ LEGACY SYSTEM (Deprecated - DO NOT USE)

The following commands are **OBSOLETE** and should not be used:

```bash
# ❌ DEPRECATED - These scripts are no longer executed
python DummyProviders/init_all_dummy_providers.py
python DummyProviders/init_all_mappings.py
python DummyProviders/init_dummy_provider.py
# ... etc (all individual scripts are deprecated)
```

### What Gets Created

#### Test Providers (4 total)
1. **FinStack Global (Test)**: Reference provider with ~100% field coverage
2. **AlphaFinance Pro (Test)**: Alternative naming, ~60% field coverage
3. **MarketInsight Analytics (Test)**: Nested structure, ~55% field coverage  
4. **DataStream Financial (Test)**: Hierarchical data, ~65% field coverage

#### Test Companies (4 total)
1. **ACM**: Acme Technologies Ltd. (FinStack Global data)
2. **TECH**: TechCorp Industries Inc. (AlphaFinance Pro data)
3. **SOFT**: SoftwareDev Solutions Ltd. (MarketInsight Analytics data)
4. **INNV**: Innovation Dynamics Corp. (DataStream Financial data)

#### Raw Data Entries
- All financial fields from respective JSON files as raw data entries
- Different field naming patterns to test mapping scenarios  
- Varied data completeness to simulate real-world provider differences

#### Field Mappings (75 total mappings created)
- **AlphaFinance Pro**: 26 field mappings to canonical fields
- **MarketInsight Analytics**: 24 field mappings to canonical fields
- **DataStream Financial**: 25 field mappings to canonical fields
- **FinStack Global**: Uses standard naming (reference provider)

### Available Raw Field Examples

Different providers use various naming conventions:

#### FinStack Global (Standard)
- **Income Statement**: Total_Revenue, Cost_Of_Revenue, Net_Income, Operating_Income
- **Balance Sheet**: Cash, Total_Assets, Total_Liab, Total_Stockholder_Equity
- **Cash Flow**: Cash_From_Operating, Capital_Expenditures, Free_Cash_Flow

#### AlphaFinance Pro (Alternative)  
- **Income Statement**: revenues, cogs, gross_margin, net_earnings, ebitda
- **Balance Sheet**: cash_and_equivalents, current_assets_total, shareholders_equity
- **Cash Flow**: operating_cash_flow, capex, free_cash_flow

#### MarketInsight Analytics (Nested)
- **Financials**: revenue_total, cost_sales, income_operating, income_net
- **Position**: cash_total, assets_current, liabilities_total, equity_total
- **Cashflow**: cf_operating, cf_investing, expenditures_capital

#### DataStream Financial (Hierarchical)
- **Income**: sales_net, cost_goods_sold, profit_operating, earnings_net
- **Balance**: cash_cash_equiv, assets_grand_total, liabilities_grand_total
- **Flows**: cash_operations, investments_capital, flow_free_cash

## Integration with Field Mapping UI

The dummy providers enable comprehensive testing of:
- **Canonical Field Mapping**: Map 98+ canonical fields to provider-specific names
- **Coverage Analysis**: Test mapping completeness with varying field availability
- **Naming Pattern Recognition**: Handle different naming conventions (snake_case, camelCase, etc.)
- **Data Structure Handling**: Process flat, nested, and hierarchical data formats
- **Provider Comparison**: Compare field availability across multiple data sources
- **Mapping Export/Import**: Test backup and restore functionality for field mappings
- **Transformation Testing**: Validate formula expressions with diverse field names

## Cleanup for Production

To remove all test data before production:

### Automated Method (Recommended)
```bash
# Set environment variable to disable dummy data initialization
ENABLE_DUMMY_DATA=false docker-compose up backend db
```

### Manual Cleanup (if needed)
1. Delete this entire `DummyProviders/` directory
2. Remove line from Dockerfile: `COPY DummyProviders/ ./DummyProviders/`
3. Remove all dummy providers from database:
   ```sql
   DELETE FROM raw_data_entries WHERE provider_id IN (SELECT id FROM providers WHERE name LIKE '%Test%');
   DELETE FROM mapped_fields WHERE provider_id IN (SELECT id FROM providers WHERE name LIKE '%Test%');
   DELETE FROM providers WHERE name LIKE '%Test%';
   DELETE FROM companies WHERE ticker IN ('ACM', 'TECH', 'SOFT', 'INNV');
   ```

## Field Coverage Summary

The four dummy providers provide varying levels of canonical field coverage to test mapping scenarios:

| Provider | Raw Fields | Mapped Fields | Coverage | Key Features |
|----------|------------|---------------|----------|-------------|
| FinStack Global | 102 | N/A | ~100% | Reference provider, standard naming |
| AlphaFinance Pro | 56 | 26 | ~46% | Alternative naming, simplified structure |
| MarketInsight Analytics | 48 | 24 | ~50% | Nested JSON, different conventions |
| DataStream Financial | 53 | 25 | ~47% | Hierarchical structure, descriptive names |

**Total Test Data**: 259 raw field entries + 75 field mappings across 4 providers

## Notes

- All dummy providers are clearly marked with "(Test)" suffix and warning descriptions
- All test data uses fictional company information to avoid real market data issues
- Raw field names are based on common financial data provider API formats
- The automated system is idempotent - safe to restart backend multiple times without duplicating data
- Field coverage percentages are approximate and designed for testing mapping scenarios

## Troubleshooting for Future AI

### Common Issues and Solutions

1. **"no such table" errors**: Database tables not created yet
   - Solution: Ensure `models.Base.metadata.create_all(bind=engine)` runs before initialization

2. **"'column' violates not-null constraint"**: Missing required fields
   - Solution: Check model definitions in `backend/db/models/` for required fields
   - Always provide `country="US"` and `currency="USD"` for test companies

3. **"'Type' object has no attribute 'field'"**: Wrong field name used
   - Solution: Check actual model field names, don't assume from old code

4. **"Canonical field 'X' not found"**: Field mapping name mismatch
   - Solution: Query existing canonical fields and use exact names
   - Example: Use `cash` not `cash_and_cash_equivalents`

5. **UUID/SQLite compatibility issues**: 
   - Solution: This system requires PostgreSQL, not SQLite for UUID fields

### Debugging Commands

```bash
# Check what was created
docker-compose exec backend python -c "
from backend.db.session import get_db
from backend.db.models.provider import Provider
from backend.db.models.company import Company
db = next(get_db())
print('Providers:', [p.name for p in db.query(Provider).all()])
print('Companies:', [f'{c.ticker}:{c.name}' for c in db.query(Company).all()])
db.close()
"

# Check canonical fields
docker-compose exec backend python -c "
from backend.db.session import get_db
from backend.db.models.field import CanonicalField
db = next(get_db())
print('Field count:', db.query(CanonicalField).count())
print('Cash fields:', [f.name for f in db.query(CanonicalField).filter(CanonicalField.name.like('%cash%')).all()])
db.close()
"
```