# Database Schema Reference

This document details the PostgreSQL database schema used by the Equity Valuation System.

## Overview

The database uses PostgreSQL with the following key design principles:
- **UUID primary keys** for all business entities to enable distributed scaling
- **JSONB columns** for flexible storage of financial data and configuration
- **Comprehensive indexing** for query performance optimization
- **Foreign key constraints** to maintain data integrity
- **Extensible schema** to accommodate new data providers and fields

## Core Tables

### users
Stores user account information and authentication data.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO INCREMENT | Unique user identifier |
| username | VARCHAR | UNIQUE, NOT NULL | User login name |
| email | VARCHAR | UNIQUE, NOT NULL | User email address |
| hashed_password | VARCHAR | NOT NULL | Bcrypt hashed password |
| is_active | BOOLEAN | DEFAULT true | Whether account is active |
| created_at | TIMESTAMP | DEFAULT NOW() | Account creation timestamp |
| updated_at | TIMESTAMP | DEFAULT NOW() | Last update timestamp |

**Relationships:**
- One-to-many with `valuation_results`

**Indexes:**
- Primary key on `id`
- Unique index on `username`
- Unique index on `email`

### companies
Central registry of all companies in the system.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique company identifier |
| ticker | VARCHAR | UNIQUE, NOT NULL | Stock ticker symbol |
| name | VARCHAR | NOT NULL | Company display name |
| country | VARCHAR | NOT NULL | Country code (ISO 3166-1) |
| currency | VARCHAR | NOT NULL | Currency code (ISO 4217) |
| industry_id | INTEGER | FOREIGN KEY | Reference to industries table |

**Relationships:**
- Many-to-one with `industries`
- One-to-many with `price_data`
- One-to-many with `raw_data_entries`
- One-to-many with `mapped_fields`
- One-to-many with `valuation_results`

**Indexes:**
- Primary key on `id`
- Unique index on `ticker`
- Index on `industry_id`

### industries
Industry classification for companies.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO INCREMENT | Unique industry identifier |
| code | VARCHAR | UNIQUE | Industry code (e.g., "TECH") |
| name | VARCHAR | NOT NULL | Industry display name |
| description | TEXT | | Detailed industry description |

**Relationships:**
- One-to-many with `companies`

**Indexes:**
- Primary key on `id`
- Unique index on `code`

### providers
Configuration for data providers (Kaggle, Yahoo Finance, etc.).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO INCREMENT | Unique provider identifier |
| name | VARCHAR | UNIQUE, NOT NULL | Provider display name |
| provider_type | VARCHAR | NOT NULL | Type enum (kaggle, yahoo_finance, etc.) |
| data_quality | VARCHAR | NOT NULL | Quality enum (high, medium, low, test) |
| enabled | BOOLEAN | DEFAULT true | Whether provider is active |
| configuration | JSONB | | Provider-specific configuration |
| created_at | TIMESTAMP | DEFAULT NOW() | Provider creation timestamp |
| updated_at | TIMESTAMP | DEFAULT NOW() | Last update timestamp |

**Relationships:**
- One-to-many with `price_data`
- One-to-many with `raw_data_entries`
- One-to-many with `mapped_fields`

**Indexes:**
- Primary key on `id`
- Unique index on `name`
- Index on `provider_type`

## Financial Data Tables

### price_data
Historical price and volume data for companies.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique price record identifier |
| company_id | UUID | FOREIGN KEY, NOT NULL | Reference to companies table |
| provider_id | INTEGER | FOREIGN KEY, NOT NULL | Reference to providers table |
| date | DATE | NOT NULL | Trading date |
| period_type | ENUM | NOT NULL, DEFAULT 'daily' | daily, weekly, monthly, minute, second |
| open | FLOAT | | Opening price |
| close | FLOAT | | Closing price |
| adj_close | FLOAT | | Adjusted closing price |
| volume | INTEGER | | Trading volume |

**Relationships:**
- Many-to-one with `companies`
- Many-to-one with `providers`

**Indexes:**
- Primary key on `id`
- Composite index on `(company_id, date)` - most common query pattern
- Composite index on `(company_id, provider_id, date)`
- Index on `date` for date range queries
- Index on `(provider_id, date)`
- **Unique constraint** on `(company_id, provider_id, date, period_type)`

### canonical_fields
Standardized field definitions for financial data.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO INCREMENT | Unique field identifier |
| name | VARCHAR | UNIQUE, NOT NULL | Canonical field name |
| display_name | VARCHAR | NOT NULL | Human-readable field name |
| data_type | VARCHAR | NOT NULL | Expected data type (number, string, date) |
| category | VARCHAR | NOT NULL | Field category (income_statement, balance_sheet) |
| description | TEXT | | Field description and usage |
| validation_rules | JSONB | | Validation constraints and rules |
| created_at | TIMESTAMP | DEFAULT NOW() | Field creation timestamp |

**Relationships:**
- One-to-many with `mapped_fields`

**Indexes:**
- Primary key on `id`
- Unique index on `name`
- Index on `category`

### raw_data_entries
Raw financial data from data providers before transformation.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique raw data identifier |
| provider_id | INTEGER | FOREIGN KEY, NOT NULL | Reference to providers table |
| company_id | UUID | FOREIGN KEY, NOT NULL | Reference to companies table |
| fiscal_period | DATE | NOT NULL | Fiscal period date |
| period_type | ENUM | NOT NULL | annual, quarterly |
| raw_field_name | VARCHAR | NOT NULL | Original field name from provider |
| value_type | ENUM | NOT NULL | number, string, list, object |
| value | JSONB | | Raw field value |
| upload_id | UUID | | Batch upload tracking identifier |

**Relationships:**
- Many-to-one with `providers`
- Many-to-one with `companies`

**Indexes:**
- Primary key on `id`
- Composite index on `(company_id, fiscal_period)`
- Index on `provider_id`
- Index on `upload_id`

### mapped_fields
Mapping configuration between raw provider fields and canonical fields.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique mapping identifier |
| provider_id | INTEGER | FOREIGN KEY, NOT NULL | Reference to providers table |
| canonical_id | INTEGER | FOREIGN KEY, NOT NULL | Reference to canonical_fields table |
| raw_field_name | VARCHAR | NOT NULL | Raw field name from provider |
| company_id | UUID | FOREIGN KEY | Optional company-specific mapping |
| start_date | DATE | | Optional mapping validity start date |
| end_date | DATE | | Optional mapping validity end date |
| transform_expression | JSON | | Structured transformation formula |

**Relationships:**
- Many-to-one with `providers`
- Many-to-one with `canonical_fields`
- Many-to-one with `companies` (optional)
- One-to-many with `change_logs`

**Indexes:**
- Primary key on `id`
- Composite index on `(provider_id, raw_field_name)`
- Index on `canonical_id`
- Index on `company_id`

## Valuation Tables

### valuation_results
Results from financial valuation calculations.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique valuation identifier |
| company_id | UUID | FOREIGN KEY, NOT NULL | Reference to companies table |
| as_of | DATE | NOT NULL | Valuation calculation date |
| user_id | INTEGER | FOREIGN KEY, NOT NULL | Reference to users table |
| results | JSONB | | Valuation results and metrics |

**Relationships:**
- Many-to-one with `companies`
- Many-to-one with `users`

**Indexes:**
- Primary key on `id`
- Composite index on `(company_id, as_of)`
- Index on `user_id`

## Audit Tables

### change_logs
Audit trail for field mapping changes.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique change log identifier |
| mapped_field_id | UUID | FOREIGN KEY, NOT NULL | Reference to mapped_fields table |
| user_id | INTEGER | FOREIGN KEY, NOT NULL | User who made the change |
| timestamp | TIMESTAMP | NOT NULL, DEFAULT NOW() | When change was made |
| change_type | VARCHAR | NOT NULL | create, update, delete |
| old_value | JSONB | | Previous field configuration |
| new_value | JSONB | | New field configuration |
| reason | TEXT | | Reason for the change |

**Relationships:**
- Many-to-one with `mapped_fields`
- Many-to-one with `users`

**Indexes:**
- Primary key on `id`
- Index on `mapped_field_id`
- Index on `user_id`
- Index on `timestamp`

## Database Enums

### PeriodType
- `annual`: Annual financial periods
- `quarterly`: Quarterly financial periods

### ValueType  
- `number`: Numeric values (integer or decimal)
- `string`: Text values
- `list`: Array of values
- `object`: Complex structured data

### PricePeriodType
- `daily`: Daily price data (most common)
- `weekly`: Weekly aggregated data
- `monthly`: Monthly aggregated data  
- `minute`: Minute-by-minute data
- `second`: Second-by-second data

### DataQuality
- `high`: Real-time, premium data sources
- `medium`: Daily updates, reliable sources
- `low`: Historical data only
- `test`: Test/development data

## Performance Considerations

### Indexing Strategy
- **Primary indexes** on all UUID and auto-increment fields
- **Composite indexes** on common query patterns (company+date, provider+date)
- **Partial indexes** on filtered queries (e.g., active providers only)
- **JSONB indexes** using GIN for complex JSON queries

### Query Optimization
- Use **prepared statements** for repeated queries
- **Batch inserts** for bulk data loading
- **Connection pooling** to manage database connections efficiently
- **Read replicas** for heavy analytical workloads (future enhancement)

### Storage Optimization
- **JSONB compression** for large financial datasets
- **Partitioning** of price_data table by date (future enhancement)
- **Archive strategy** for old valuation results

## Backup Strategy

### Full Backups
- **Daily** full database backups retained for 30 days
- **Weekly** backups retained for 12 weeks
- **Monthly** backups retained for 12 months

### Incremental Backups
- **Transaction log backups** every 15 minutes
- **Point-in-time recovery** capability up to 30 days

### Disaster Recovery
- **Geo-replicated** backups in different regions
- **Recovery time objective (RTO)**: 4 hours
- **Recovery point objective (RPO)**: 15 minutes